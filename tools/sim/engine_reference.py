"""
Reference for locator_engine (CLAUDE.md §7): the Bayesian probability map of
docs/research/sim/circle_prob_sim.py (`bayes`), generalised from a rectangle to any rubble outline,
and the golden fixtures the Dart engine must match.

Model per grid cell (0.25 m, centres inside the outline), victim height z in {0.25 H, 0.6 H}:
  mu  = P0 + c - 10 n log10(r) - alpha * r_in          r_in = path length inside the rubble footprint
  sig = sqrt(slow² + fast² + (linkVariation * alpha * r_in)²)
  heard point:     log N(rssi; mu, sig)
  not heard point: log Phi((threshold - mu) / sig)      (a point with no signal is data — rule 3)
Unknowns marginalised: z, n, alpha (uniform), common offset c (normal, sd = offset).

Run: tools/sim/.venv/bin/python tools/sim/engine_reference.py <out_dir>
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

PROFILES = {
    "voided_pancake@1": {
        "id": "voided_pancake@1",
        "txPowerAt1mDbm": -59.0,
        "thresholdDbm": -100.0,
        "slowFadingDb": 6.0,
        "fastFadingDb": 5.0 / np.sqrt(20),
        "offsetSdDb": 5.0,
        "offsetsDb": list(np.linspace(-12, 12, 9)),
        "linkVariation": 0.3,
        "pathLossExponents": [2.0, 2.5, 3.0],
        "attenuationDbPerM": list(np.linspace(2, 6, 5)),
        "rubbleHeightM": 4.0,
        "victimHeightFractions": [0.25, 0.6],
        "cellM": 0.25,
    },
    "dense@1": {
        "id": "dense@1",
        "txPowerAt1mDbm": -59.0,
        "thresholdDbm": -100.0,
        "slowFadingDb": 6.0,
        "fastFadingDb": 5.0 / np.sqrt(20),
        "offsetSdDb": 5.0,
        "offsetsDb": list(np.linspace(-12, 12, 9)),
        "linkVariation": 0.3,
        "pathLossExponents": [2.0, 2.5, 3.0],
        "attenuationDbPerM": list(np.linspace(5, 15, 5)),
        "rubbleHeightM": 4.0,
        "victimHeightFractions": [0.25, 0.6],
        "cellM": 0.25,
    },
}


def inside(px, py, corners):
    """Points inside the polygon (ray casting); points on a side count as inside."""
    px = np.asarray(px, float)
    py = np.asarray(py, float)
    result = np.zeros(px.shape, bool)
    on_edge = np.zeros(px.shape, bool)
    n = len(corners)
    for i in range(n):
        ax, ay = corners[i]
        bx, by = corners[(i + 1) % n]
        cross = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
        within = (
            (px >= min(ax, bx) - 1e-9) & (px <= max(ax, bx) + 1e-9)
            & (py >= min(ay, by) - 1e-9) & (py <= max(ay, by) + 1e-9)
        )
        on_edge |= (np.abs(cross) <= 1e-9) & within
        crosses = (ay > py) != (by > py)
        with np.errstate(divide="ignore", invalid="ignore"):
            x = ax + (py - ay) * (bx - ax) / (by - ay)
        result ^= crosses & (px < x)
    return result | on_edge


def grid(corners, cell):
    xs = np.array([c[0] for c in corners])
    ys = np.array([c[1] for c in corners])
    x0, y0 = xs.min(), ys.min()
    cols = int(np.ceil((xs.max() - x0) / cell - 1e-9))
    rows = int(np.ceil((ys.max() - y0) / cell - 1e-9))
    gx = x0 + cell / 2 + cell * np.arange(cols)
    gy = y0 + cell / 2 + cell * np.arange(rows)
    GX, GY = np.meshgrid(gx, gy, indexing="xy")  # (rows, cols)
    mask = inside(GX, GY, corners)
    return x0, y0, cols, rows, GX, GY, mask


def rubble_path(anchor, GX, GY, z, H, corners, samples=21):
    t = np.linspace(0, 1, samples)
    ax, ay = anchor
    PX = ax + t[None, None, :] * (GX[..., None] - ax)
    PY = ay + t[None, None, :] * (GY[..., None] - ay)
    PZ = t * z  # anchors stand on the ground (z = 0)
    ins = inside(PX, PY, corners) & (PZ[None, None, :] <= H)
    length = np.sqrt((GX - ax) ** 2 + (GY - ay) ** 2 + z ** 2)
    return ins.mean(-1) * length


def posterior(corners, points, profile):
    cell = profile["cellM"]
    x0, y0, cols, rows, GX, GY, mask = grid(corners, cell)
    H = profile["rubbleHeightM"]
    offsets = np.array(profile["offsetsDb"])
    weights = norm.pdf(offsets, 0, profile["offsetSdDb"])
    weights /= weights.sum()
    heard = np.array([p["heard"] for p in points])
    rssi = np.array([p["medianDbm"] if p["heard"] else 0.0 for p in points])
    terms = []
    for frac in profile["victimHeightFractions"]:
        z = frac * H
        R = np.stack(
            [np.sqrt((GX - p["x"]) ** 2 + (GY - p["y"]) ** 2 + z ** 2).clip(0.3) for p in points], -1
        )
        RIN = np.stack([rubble_path((p["x"], p["y"]), GX, GY, z, H, corners) for p in points], -1)
        logR = np.log10(R)
        for n in profile["pathLossExponents"]:
            for alpha in profile["attenuationDbPerM"]:
                mu0 = profile["txPowerAt1mDbm"] - 10 * n * logR - alpha * RIN
                sig = np.sqrt(
                    profile["slowFadingDb"] ** 2 + profile["fastFadingDb"] ** 2
                    + (profile["linkVariation"] * alpha * RIN) ** 2
                )
                for c, w in zip(offsets, weights):
                    mu = mu0 + c
                    ll = np.where(
                        heard, norm.logpdf(rssi, mu, sig),
                        norm.logcdf((profile["thresholdDbm"] - mu) / sig),
                    )
                    terms.append(ll.sum(-1) + np.log(w))
    L = np.stack(terms, 0)
    m = L.max(0)
    logpost = m + np.log(np.exp(L - m).sum(0))
    logpost = np.where(mask, logpost, -np.inf)
    logpost -= logpost[mask].max()
    post = np.where(mask, np.exp(logpost), 0.0)
    post /= post.sum()
    return x0, y0, cols, rows, post


def hpd_area(post, mass, cell):
    p = np.sort(post.ravel())[::-1]
    k = int(np.searchsorted(np.cumsum(p), mass) + 1)
    return k * cell * cell


def scenario(name, corners, victim, anchors, profile_id, seed, n=2.5, alpha=None):
    """Readings simulated like circle_prob_sim.simulate, with a fixed seed, then the posterior."""
    profile = PROFILES[profile_id]
    rng = np.random.default_rng(seed)
    alpha = alpha if alpha is not None else float(np.mean(profile["attenuationDbPerM"]))
    H = profile["rubbleHeightM"]
    vx, vy, vz = victim
    points = []
    for ax, ay in anchors:
        r = max(np.sqrt((vx - ax) ** 2 + (vy - ay) ** 2 + vz ** 2), 0.3)
        rin = rubble_path((ax, ay), np.array([[vx]]), np.array([[vy]]), vz, H, corners)[0, 0]
        loss = alpha * rin * (1 + profile["linkVariation"] * rng.standard_normal())
        value = (profile["txPowerAt1mDbm"] - 10 * n * np.log10(r) - loss
                 + profile["slowFadingDb"] * rng.standard_normal())
        heard = bool(value >= profile["thresholdDbm"])
        points.append({"x": ax, "y": ay, "heard": heard,
                       "medianDbm": round(float(value), 1) if heard else None})
    x0, y0, cols, rows, post = posterior(corners, points, profile)
    cell = profile["cellM"]
    return {
        "name": name,
        "profile": profile_id,
        "outline": [{"x": x, "y": y} for x, y in corners],
        "points": points,
        "victim": {"x": vx, "y": vy},
        "grid": {"originX": x0, "originY": y0, "cols": cols, "rows": rows, "cellM": cell},
        "probabilities": [round(float(v), 12) for v in post.ravel()],
        "area50": hpd_area(post, 0.5, cell),
        "area90": hpd_area(post, 0.9, cell),
    }


def perimeter(w, d, off=1.0):
    return [(-off, -off), (w / 2, -off), (w + off, -off), (w + off, d / 2),
            (w + off, d + off), (w / 2, d + off), (-off, d + off), (-off, d / 2)]


def main(out):
    out.mkdir(parents=True, exist_ok=True)
    rect = [(0.0, 0.0), (12.0, 0.0), (12.0, 10.0), (0.0, 10.0)]
    ell = [(0.0, 0.0), (12.0, 0.0), (12.0, 5.0), (6.0, 5.0), (6.0, 10.0), (0.0, 10.0)]
    fixtures = [
        scenario("voided_rect_8", rect, (3.0, 7.5, 1.0), perimeter(12, 10), "voided_pancake@1", 1),
        scenario("dense_rect_8", rect, (10.5, 1.5, 0.5), perimeter(12, 10), "dense@1", 2, alpha=5.0),
        scenario("voided_l_shape", ell, (2.5, 8.0, 1.5),
                 [(-1, -1), (13, -1), (13, 6), (7, 6), (7, 11), (-1, 11)], "voided_pancake@1", 3),
        scenario("all_silent", rect, (6.0, 5.0, 2.0), perimeter(12, 10), "dense@1", 4, alpha=40.0),
    ]
    for f in fixtures:
        (out / f"{f['name']}.json").write_text(json.dumps(f, indent=1) + "\n")
    (out / "profiles.json").write_text(json.dumps(PROFILES, indent=1) + "\n")
    for f in fixtures:
        heard = sum(p["heard"] for p in f["points"])
        print(f"{f['name']}: heard {heard}/{len(f['points'])}, area50 {f['area50']:.2f} m², "
              f"area90 {f['area90']:.2f} m², cells {f['grid']['cols']}x{f['grid']['rows']}")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "fixtures"))
