"""
Kullanıcının kurgusu: enkaz alanı çizilir, kullanıcı ölçüm noktalarını haritada elle işaretler (GPS yok),
her noktada RSSI -> metre -> çember; çemberlerin kesişimi hedef. Sonuç olasılık haritası olarak yorumlanır.

Senaryo: Türkiye tipik 4-5 katlı apartman, taban 12x10 m, pankek çökme sonrası enkaz yüksekliği H~U(3,5) m.
Kurbanın telefonu enkaz içinde rastgele (x,y), zeminden yükseklik z~U(0, H-0.5).
Ölçümler: TEK telefonla sırayla alınır (cihaz ofseti ortak), her noktada 20 örnek ortalaması.

Karşılaştırılan yöntemler:
  naive  : RSSI -> r = 10^((P0-RSSI)/(10n)) serbest uzay çemberi, en küçük kareler kesişim (kullanıcının literal yöntemi)
  calib  : malzeme kaybını ortalama alfa ile hesaba katan çember (r çözülür), en küçük kareler kesişim
  bayes  : olasılık haritası; n, alfa, ortak ofset bilinmiyor (marjinalize), algılanmayan nokta da bilgi (sansür)
Çalıştırma: venv/bin/python circle_prob_sim.py
"""
import numpy as np
from scipy.stats import norm
from scipy.optimize import least_squares

rng = np.random.default_rng(20260927)
W, D = 12.0, 10.0          # bina tabanı (m)
P0 = -59.0                 # 1 m'de RSSI (Android TX HIGH, havada)
THR = -100.0               # algılama eşiği (dBm)
SIG_S = 6.0                # yavaş gölgeleme (dB), ortalamayla düşmez
SIG_F = 5.0 / np.sqrt(20)  # hızlı sönümleme, 20 örnek ortalaması
SIG_V = 5.0                # kurban tarafı ofset (vücut, yönelim, model)
LINKVAR = 0.3              # link başına malzeme kaybı değişkenliği (+-%30)
TRIALS = 250
GRID = 0.25

xs = np.arange(GRID / 2, W, GRID); ys = np.arange(GRID / 2, D, GRID)
GX, GY = np.meshgrid(xs, ys, indexing="xy")
CELL_A = GRID * GRID
TOTAL_A = W * D

def corners(off=1.0):
    return np.array([[-off, -off, 0], [W + off, -off, 0], [W + off, D + off, 0], [-off, D + off, 0]], float)

def perim8(off=1.0):
    c = corners(off)
    mids = np.array([[W / 2, -off, 0], [W + off, D / 2, 0], [W / 2, D + off, 0], [-off, D / 2, 0]], float)
    return np.vstack([c, mids])

def perim12(off=1.0):
    pts = []
    for t in (0.0, 1/3, 2/3):
        pts += [[-off + t * (W + 2*off), -off, 0], [W + off, -off + t * (D + 2*off), 0],
                [W + off - t * (W + 2*off), D + off, 0], [-off, D + off - t * (D + 2*off), 0]]
    return np.array(pts, float)

def top5(H):  # enkaz üstünde 5 nokta (güvenliyse)
    return np.array([[W/4, D/4, H], [3*W/4, D/4, H], [3*W/4, 3*D/4, H], [W/4, 3*D/4, H], [W/2, D/2, H]], float)

def rubble_path(anc, vic, H):
    """Enkaz içinde kalan yol uzunluğu (yaklaşık): segmenti örnekle, taban içinde ve z<H olan kısım."""
    t = np.linspace(0, 1, 41)[:, None]
    p = anc[None, :] + t * (vic - anc)[None, :]
    inside = (p[:, 0] >= 0) & (p[:, 0] <= W) & (p[:, 1] >= 0) & (p[:, 1] <= D) & (p[:, 2] <= H)
    return inside.mean() * np.linalg.norm(vic - anc)

def simulate(anchors, vic, H, n, alpha, v):
    r = np.linalg.norm(anchors - vic, axis=1).clip(0.3)
    rin = np.array([rubble_path(a, vic, H) for a in anchors])
    loss = alpha * rin * (1 + LINKVAR * rng.standard_normal(len(r)))
    rssi = P0 + v - 10 * n * np.log10(r) - loss + SIG_S * rng.standard_normal(len(r)) + SIG_F * rng.standard_normal(len(r))
    return rssi, rssi >= THR

# ---------- kestiriciler ----------
def lsq_circles(anchors2d, radii):
    def f(p): return np.linalg.norm(anchors2d - p, axis=1) - radii
    best = None
    for x0 in ([W/2, D/2], [W/4, D/4], [3*W/4, 3*D/4]):
        s = least_squares(f, x0, bounds=([0, 0], [W, D]))
        if best is None or s.cost < best.cost: best = s
    return best.x

def naive(anchors, rssi, det):
    if det.sum() < 3: return None
    r = 10 ** ((P0 - rssi[det]) / (10 * 2.5))
    return lsq_circles(anchors[det, :2], r)

def calib(anchors, rssi, det, alpha_mid):
    if det.sum() < 3: return None
    rr = np.linspace(0.3, 40, 4000)
    model = P0 - 25 * np.log10(rr) - alpha_mid * np.maximum(rr - 1, 0) * 0.8
    radii = np.array([rr[np.argmin(np.abs(model - x))] for x in rssi[det]])
    return lsq_circles(anchors[det, :2], radii)

N_GRID = [2.0, 2.5, 3.0]
C_GRID = np.linspace(-12, 12, 9); C_W = norm.pdf(C_GRID, 0, SIG_V); C_W /= C_W.sum()

def bayes(anchors, rssi, det, H_guess, alpha_grid):
    """Olasılık haritası (log alanında). n, alfa, ortak ofset c ve kurbanın yüksekliği z bilinmiyor -> marjinalize.
    Algılanmayan nokta da bilgi taşır: P(RSSI < eşik)."""
    terms = []
    for zv in (0.25 * H_guess, 0.6 * H_guess):
        V = np.stack([GX, GY, np.full_like(GX, zv)], -1)
        R = np.stack([np.linalg.norm(V - a, axis=-1).clip(0.3) for a in anchors], -1)          # (ny,nx,K)
        RIN = np.stack([_rin_grid(a, V, H_guess) for a in anchors], -1)
        logR = np.log10(R)
        for n in N_GRID:
            for al in alpha_grid:
                mu0 = P0 - 10 * n * logR - al * RIN
                sig = np.sqrt(SIG_S**2 + SIG_F**2 + (LINKVAR * al * RIN) ** 2)
                for c, w in zip(C_GRID, C_W):
                    mu = mu0 + c
                    ll = np.where(det, norm.logpdf(rssi, mu, sig), norm.logcdf((THR - mu) / sig))
                    terms.append(ll.sum(-1) + np.log(w))
    L = np.stack(terms, 0)
    m = L.max(0)
    logpost = m + np.log(np.exp(L - m).sum(0))
    logpost -= logpost.max()
    post = np.exp(logpost)
    return post / post.sum()

_rin_cache = {}
def _rin_grid(a, V, H):
    key = (tuple(np.round(a, 2)), round(float(V[0, 0, 2]), 2), round(H, 2))
    if key in _rin_cache: return _rin_cache[key]
    t = np.linspace(0, 1, 21)
    P = a[None, None, None, :] + t[None, None, :, None] * (V[:, :, None, :] - a[None, None, None, :])
    inside = (P[..., 0] >= 0) & (P[..., 0] <= W) & (P[..., 1] >= 0) & (P[..., 1] <= D) & (P[..., 2] <= H)
    out = inside.mean(-1) * np.linalg.norm(V - a, axis=-1)
    _rin_cache[key] = out
    return out

def hpd_area(post, mass):
    p = np.sort(post.ravel())[::-1]; k = np.searchsorted(np.cumsum(p), mass) + 1
    return k * CELL_A, p[min(k - 1, len(p) - 1)]

def quadrant(x, y): return int(x > W / 2) + 2 * int(y > D / 2)

def run(name, anchor_fn, alpha_rng, use_top=False):
    alpha_grid = np.linspace(alpha_rng[0], alpha_rng[1], 5)
    e_naive, e_cal, e_map = [], [], []
    a50, a90, cov90, quad_ok, top30 = [], [], [], [], []
    ndet_all = []
    for _ in range(TRIALS):
        H = rng.uniform(3, 5)
        vic = np.array([rng.uniform(0.5, W - 0.5), rng.uniform(0.5, D - 0.5), rng.uniform(0, H - 0.5)])
        anchors = anchor_fn()
        if use_top: anchors = np.vstack([anchors, top5(H)])
        n = rng.uniform(2, 3); alpha = rng.uniform(*alpha_rng); v = SIG_V * rng.standard_normal()
        rssi, det = simulate(anchors, vic, H, n, alpha, v)
        # kullanıcı noktaları haritada elle işaretliyor: 0.5 m hata
        anc_est = anchors + np.c_[0.5 * rng.standard_normal((len(anchors), 2)), np.zeros(len(anchors))]
        ndet_all.append(det.sum())
        p = naive(anc_est, rssi, det); e_naive.append(np.nan if p is None else np.hypot(*(p - vic[:2])))
        p = calib(anc_est, rssi, det, np.mean(alpha_rng)); e_cal.append(np.nan if p is None else np.hypot(*(p - vic[:2])))
        post = bayes(anc_est, rssi, det, 4.0, alpha_grid)
        iy, ix = np.unravel_index(post.argmax(), post.shape)
        e_map.append(np.hypot(GX[iy, ix] - vic[0], GY[iy, ix] - vic[1]))
        A50, _ = hpd_area(post, 0.5); A90, th90 = hpd_area(post, 0.9)
        a50.append(A50); a90.append(A90)
        jx = min(int(vic[0] / GRID), GX.shape[1] - 1); jy = min(int(vic[1] / GRID), GX.shape[0] - 1)
        cov90.append(post[jy, jx] >= th90)
        qpost = [post[((GX > W/2) == bool(q % 2)) & ((GY > D/2) == bool(q // 2))].sum() for q in range(4)]
        quad_ok.append(int(np.argmax(qpost)) == quadrant(*vic[:2]))
        # en olası 30 m² (binanın %25'i) içinde mi?
        p_sorted = np.sort(post.ravel())[::-1]; k = int(30 / CELL_A); th = p_sorted[k - 1]
        top30.append(post[jy, jx] >= th)
    ndet_all = np.array(ndet_all); K = len(anchors)
    f = lambda a: f"{np.nanmedian(a):5.2f}/{np.nanpercentile(a, 90):5.2f}"
    ok = ~np.isnan(e_naive)
    print(f"\n### {name}  (alfa {alpha_rng} dB/m, {K} nokta)")
    print(f"  algılanan nokta sayısı: medyan {np.median(ndet_all):.0f}/{K}; >=3 nokta algılanan deneme %{100*np.mean(ndet_all>=3):.0f}; hiç yok %{100*np.mean(ndet_all==0):.0f}")
    print(f"  naif çember (serbest uzay) hata med/p90 m : {f(e_naive)}   (>=3 algılamada)")
    print(f"  kalibre çember hata med/p90 m            : {f(e_cal)}")
    print(f"  olasılık haritası MAP hata med/p90 m     : {f(e_map)}")
    print(f"  %50 bölge alanı medyan: {np.median(a50):5.1f} m² (binanın %{100*np.median(a50)/TOTAL_A:.0f}) | %90 bölge: {np.median(a90):5.1f} m² (%{100*np.median(a90)/TOTAL_A:.0f}) | %90 bölge gerçeği kapsıyor: %{100*np.mean(cov90):.0f}")
    print(f"  doğru çeyrek (4'te 1) seçimi: %{100*np.mean(quad_ok):.0f}  (şans %25)")
    print(f"  en olası 30 m² (binanın %25'i) kurbanı içeriyor: %{100*np.mean(top30):.0f}  (şans %25)")
    print(f"  referans: hep bina merkezini söylemek hata medyanı ~{np.median(np.hypot(rng.uniform(0.5,W-0.5,4000)-W/2, rng.uniform(0.5,D-0.5,4000)-D/2)):.2f} m")

SCENARIOS = []
for label, ar in (("BOŞLUKLU pankek", (2, 6)), ("YOĞUN enkaz", (5, 15))):
    SCENARIOS += [(f"{label} — 4 köşe (kullanıcının kurgusu)", "corners", ar, False),
                  (f"{label} — 8 çevre noktası", "perim8", ar, False),
                  (f"{label} — 12 çevre noktası", "perim12", ar, False),
                  (f"{label} — 4 köşe + 5 enkaz üstü nokta", "corners", ar, True)]

def _job(i):
    global rng
    rng = np.random.default_rng(20260927 + i)
    import io, contextlib
    buf = io.StringIO()
    name, fn, ar, top = SCENARIOS[i]
    with contextlib.redirect_stdout(buf):
        run(name, {"corners": corners, "perim8": perim8, "perim12": perim12}[fn], ar, use_top=top)
    return buf.getvalue()

if __name__ == "__main__":
    from multiprocessing import Pool
    print(f"Bina {W}x{D} m, enkaz yüksekliği U(3,5) m, tek telefon, {TRIALS} deneme/senaryo, eşik {THR} dBm, sigma {SIG_S} dB")
    with Pool(8) as pool:
        for out in pool.map(_job, range(len(SCENARIOS))):
            print(out, end="", flush=True)
