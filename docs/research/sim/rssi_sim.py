#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enkaz altindaki bir telefonun BLE RSSI ile yatay konum + derinlik kestirimi
Monte Carlo fizibilite simulasyonu.

Calistirma:
    python rssi_sim.py              # tam kosu (varsayilan 500 deneme / senaryo)
    python rssi_sim.py --trials 80  # hizli duman testi

GERCEK (simulasyondaki "dunya") olcum modeli, cihaz i / nokta i icin:
    RSSI_i = P0 + v - 10*n*log10(r_i) - A_i + S_i + o_i + mean_j(F_ij)
      P0   = -59 dBm (1 m'de hava ortaminda RSSI; kestiricinin bildigi varsayilan)
      v    ~ N(0, 3 dB)   kurban telefonu ofseti (cep/vucut/yonelim/model), deneme basina ortak
      n    ~ U(2.0, 3.5)  gercek yol kaybi ussu, deneme basina ortak
      A_i  = alpha*d*(1 + 0.2*g_i)  enkaz zayiflamasi; alpha ~ U(5,20) dB/m deneme basina,
             g_i ~ N(0,1) link basina (farkli yol -> linkler arasi bagimsiz +/- bilesen)
      S_i  ~ N(0, sigma)  YAVAS golgeleme (uzamsal; ayni noktada 20 ornek ortalamasiyla DUSMEZ)
      o_i  ~ N(0, 4 dB)   alici (kurtarici) telefon ofseti, telefon basina sabit
      F_ij ~ N(0, 5 dB)   HIZLI sonumleme, ornek basina bagimsiz; N=20 ortalama -> 5/sqrt(20)
    Yuruyerek taramada S ve A'nin link bileseni 1.5 m korelasyon mesafeli ustel kovaryansli
    Gauss rastgele alanidir (komsu noktalar benzer hata alir).
    Algilama: bir link/nokta, 20 ornegin en az 3'u >= -100 dBm ise "algilandi" sayilir.
    KESTIRIM ALGILAMA ESIGINI YOK SAYAR (iyimser): esigin altindaki linkler de kullanilir.

KESTIRICI (bildigi tek sey P0=-59 ve n=2.5; malzeme zayiflamasini bilmez):
    A : (x, y, z<0)          en kucuk kareler, RSSI alaninda
    B : (x, y, z<0, c)       c = ortak bilinmeyen zayiflama/ofset (tanimlanabilirlik testi)
    A|z, B|z : z barometreden sabitlenir, yalniz (x, y) [ve c] kestirilir
    Hepsi: kaba izgara aramasi + scipy least_squares (trf, sinirli) inceltme.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.optimize import least_squares

# --------------------------------------------------------------------------- sabitler
SEED = 20260927
P0 = -59.0            # dBm @ 1 m (varsayilan, kestiricinin bildigi)
N_EST = 2.5           # kestiricinin varsaydigi yol kaybi ussu
N_LO, N_HI = 2.0, 3.5
ALPHA_LO, ALPHA_HI = 5.0, 20.0   # dB / m enkaz
KAPPA = 0.20          # link basina malzeme yolu farki (A'nin goreli std'si)
VIC_SD = 3.0          # kurban telefonu ofseti
DEV_SD = 4.0          # kurtarici telefon ofseti (telefon basina sabit)
SIG_FAST = 5.0        # hizli sonumleme (ornek basina)
N_SAMP = 20           # nokta basina ornek
SENS = -100.0         # tipik telefon BLE tarama duyarliligi (1M PHY)
ROUGH = 0.5           # yuzey puruzlulugu, U(-0.5, 0.5) m
DCORR = 1.5           # uzamsal golgeleme korelasyon mesafesi (m)
ZMAX = 20.0           # kestiricinin derinlik siniri (m)
GPS_SD = 4.0
AR_SD = 0.2
BARO_SD = 0.8         # kalibre barometre (goreli) derinlik hatasi
BARO_UNCAL_SD = 4.0   # kalibresiz cihazlar arasi mutlak ofset (~0.5 hPa)

ZG = np.concatenate([np.arange(0.10, 2.0, 0.15),
                     np.arange(2.0, 8.0, 0.3),
                     np.arange(8.0, ZMAX + 1e-9, 1.0)])   # derinlik izgarasi (m)


# --------------------------------------------------------------------------- yardimcilar
def pl(r, n=N_EST):
    """Kestiricinin modeli: RSSI = P0 - 10 n log10 r."""
    return P0 - 10.0 * n * np.log10(np.maximum(r, 0.1))


def make_grid(lo, hi, step=0.5):
    xs = np.arange(lo, hi + 1e-9, step)
    X, Y = np.meshgrid(xs, xs)
    xy = np.column_stack([X.ravel(), Y.ravel()])
    nxy, nz = len(xy), len(ZG)
    G = np.empty((nz * nxy, 3))
    G[:, :2] = np.tile(xy, (nz, 1))
    G[:, 2] = np.repeat(-ZG, nxy)
    return dict(G=G, xy=xy, nz=nz, nxy=nxy, lo=lo, hi=hi)


def dist(G, anc):
    d2 = (G * G).sum(1)[:, None] + (anc * anc).sum(1)[None, :] - 2.0 * G @ anc.T
    return np.sqrt(np.maximum(d2, 1e-6))


def estimate_3d(anc, rssi, gp, sig_eff, d_true):
    """A: (x,y,z); B: (x,y,z,c). Ayrica B icin derinlik profil-olabilirlik %95 guven araligi."""
    G, lo, hi = gp["G"], gp["lo"], gp["hi"]
    E = rssi[None, :] - pl(dist(G, anc))
    out = {}
    # --- A
    cA = (E * E).sum(1)
    i = int(np.argmin(cA))
    fA = lambda th: rssi - pl(np.linalg.norm(anc - th, axis=1))
    s = least_squares(fA, G[i], bounds=([lo, lo, -ZMAX], [hi, hi, -0.05]), method="trf")
    out["A"] = s.x
    # --- B (c kapali formda: c* = ortalama artik)
    Em = E.mean(1)
    cB = ((E - Em[:, None]) ** 2).sum(1)
    j = int(np.argmin(cB))
    fB = lambda th: rssi - pl(np.linalg.norm(anc - th[:3], axis=1)) - th[3]
    x0 = np.r_[G[j], np.clip(Em[j], -249.0, 49.0)]
    s = least_squares(fB, x0, bounds=([lo, lo, -ZMAX, -250.0], [hi, hi, -0.05, 50.0]), method="trf")
    out["B"] = s.x
    # --- profil olabilirlik: her derinlik icin (x,y,c) uzerinden min maliyet
    J = cB.reshape(gp["nz"], gp["nxy"]).min(1)
    ok = (J - J.min()) / sig_eff ** 2 <= 3.84
    zs = ZG[ok]
    out["ci_w"] = float(zs.max() - zs.min())
    out["ci_in"] = bool(zs.min() - 0.15 <= d_true <= zs.max() + 0.15)
    return out


def estimate_fixed_z(anc, rssi, xy, z, lo, hi):
    """Derinlik barometreden sabit; A|z: (x,y); B|z: (x,y,c)."""
    G2 = np.column_stack([xy, np.full(len(xy), z)])
    E = rssi[None, :] - pl(dist(G2, anc))
    cA = (E * E).sum(1)
    i = int(np.argmin(cA))
    fA = lambda th: rssi - pl(np.linalg.norm(anc - np.r_[th, z], axis=1))
    sA = least_squares(fA, xy[i], bounds=([lo, lo], [hi, hi]), method="trf")
    Em = E.mean(1)
    cB = ((E - Em[:, None]) ** 2).sum(1)
    j = int(np.argmin(cB))
    fB = lambda th: rssi - pl(np.linalg.norm(anc - np.r_[th[:2], z], axis=1)) - th[2]
    sB = least_squares(fB, np.r_[xy[j], np.clip(Em[j], -249.0, 49.0)],
                       bounds=([lo, lo, -250.0], [hi, hi, 50.0]), method="trf")
    return sA.x, sB.x


def q(a):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return dict(med=float("nan"), p90=float("nan"))
    return dict(med=float(np.median(a)), p90=float(np.percentile(a, 90)))


def alpha_class(a, lo, hi):
    """Onsel araligini esit uc sinifa boler: 0 gozenekli/bosluklu, 1 orta, 2 yogun."""
    w = (hi - lo) / 3.0
    return np.digitize(a, [lo + w, lo + 2 * w])


# --------------------------------------------------------------------------- 4 capa isi
def job_4anchor(args):
    jid, L, d, sigma, pos_name, pos_sd, jitter, alo, ahi, n_trials = args
    rng = np.random.default_rng([SEED, jid])
    gp = make_grid(-3.0, L + 3.0, 0.5)
    corners = np.array([[0, 0], [L, 0], [L, L], [0, L]], float)
    keys = ["hA", "dA", "sA", "hB", "dB", "sB", "hC", "ci_w", "ci_in", "A_bound", "B_surf",
            "det_all", "det_any", "rssi_mean", "hAz", "hBz", "dz", "hBz_u", "dz_u", "a_err", "a_ok",
            "a_ok_det", "a_err_det", "hBz_det", "cls_det"]
    R = {k: [] for k in keys}
    for _ in range(n_trials):
        tgt = np.array([rng.uniform(0, L), rng.uniform(0, L), -d])
        cxy = corners + (rng.uniform(-jitter, jitter, (4, 2)) if jitter > 0 else 0.0)
        anc_true = np.column_stack([cxy, rng.uniform(-ROUGH, ROUGH, 4)])
        anc_known = anc_true.copy()
        anc_known[:, :2] += rng.normal(0, pos_sd, (4, 2))
        if pos_name == "GPS":
            anc_known[:, 2] = 0.0          # GPS yuksekligi isesiz; yuzey z=0 varsayilir
        else:
            anc_known[:, 2] += rng.normal(0, pos_sd, 4)
        n_true = rng.uniform(N_LO, N_HI)
        alpha = rng.uniform(alo, ahi)
        A = np.maximum(alpha * d * (1 + KAPPA * rng.normal(size=4)), 0.0)
        r = np.linalg.norm(anc_true - tgt, axis=1)
        mu = (P0 + rng.normal(0, VIC_SD) - 10 * n_true * np.log10(r) - A
              + rng.normal(0, sigma, 4) + rng.normal(0, DEV_SD, 4))
        smp = mu[:, None] + rng.normal(0, SIG_FAST, (4, N_SAMP))
        rssi = smp.mean(1)                       # IYIMSER: esik alti ornekler de kullanilir
        det = (smp >= SENS).sum(1) >= 3
        sig_eff = math.sqrt(sigma ** 2 + (KAPPA * alpha * d) ** 2 + DEV_SD ** 2 + SIG_FAST ** 2 / N_SAMP)

        e = estimate_3d(anc_known, rssi, gp, sig_eff, d)
        R["hA"].append(np.hypot(*(e["A"][:2] - tgt[:2])))
        R["dA"].append(abs(-e["A"][2] - d))
        R["sA"].append(-e["A"][2] - d)
        R["A_bound"].append(bool(-e["A"][2] >= ZMAX - 0.5))
        R["hB"].append(np.hypot(*(e["B"][:2] - tgt[:2])))
        R["dB"].append(abs(-e["B"][2] - d))
        R["sB"].append(-e["B"][2] - d)
        R["B_surf"].append(bool(-e["B"][2] <= 0.2))
        R["hC"].append(np.hypot(tgt[0] - L / 2, tgt[1] - L / 2))
        R["ci_w"].append(e["ci_w"])
        R["ci_in"].append(e["ci_in"])
        R["det_all"].append(bool(det.all()))
        R["det_any"].append(bool(det.any()))
        R["rssi_mean"].append(float(rssi.mean()))

        # (iv) barometre: kalibre (goreli) ve kalibresiz
        db = max(d + rng.normal(0, BARO_SD), 0.05)
        thA, thB = estimate_fixed_z(anc_known, rssi, gp["xy"], -db, gp["lo"], gp["hi"])
        R["hAz"].append(np.hypot(*(thA - tgt[:2])))
        R["hBz"].append(np.hypot(*(thB[:2] - tgt[:2])))
        R["dz"].append(abs(db - d))
        a_hat = -thB[2] / db                           # malzeme cikarimi: c ~ -alpha*d
        R["a_err"].append(abs(a_hat - alpha))
        R["a_ok"].append(bool(alpha_class(a_hat, alo, ahi) == alpha_class(alpha, alo, ahi)))
        if det.all():
            R["a_ok_det"].append(bool(alpha_class(a_hat, alo, ahi) == alpha_class(alpha, alo, ahi)))
            R["a_err_det"].append(abs(a_hat - alpha))
            R["hBz_det"].append(np.hypot(*(thB[:2] - tgt[:2])))
            R["cls_det"].append(int(alpha_class(alpha, alo, ahi)))
        dbu = max(d + rng.normal(0, BARO_UNCAL_SD), 0.05)
        _, thBu = estimate_fixed_z(anc_known, rssi, gp["xy"], -dbu, gp["lo"], gp["hi"])
        R["hBz_u"].append(np.hypot(*(thBu[:2] - tgt[:2])))
        R["dz_u"].append(abs(dbu - d))

    out = dict(kind="4capa", L=L, d=d, sigma=sigma, pos=pos_name, jitter=jitter, alpha=[alo, ahi], n=n_trials)
    for k in ["hA", "dA", "sA", "hB", "dB", "sB", "hC", "ci_w", "hAz", "hBz", "dz", "hBz_u", "dz_u",
              "a_err", "rssi_mean", "a_err_det", "hBz_det"]:
        out[k] = q(R[k])
    for k in ["ci_in", "det_all", "det_any", "a_ok", "A_bound", "B_surf", "a_ok_det"]:
        out[k] = float(np.mean(R[k])) if R[k] else float("nan")
    out["n_det_all"] = int(np.sum(R["det_all"]))
    # secilim etkisi: algilanan denemelerde gercek sinif dagilimi zaten tek sinifa yigilabilir
    out["a_base_det"] = (float(np.bincount(R["cls_det"], minlength=3).max() / len(R["cls_det"]))
                         if R["cls_det"] else float("nan"))
    return out


# --------------------------------------------------------------------------- yuruyerek tarama isi
def fine_window(lat, bx, by, L, exclude):
    x0 = min(max(bx - 2, 0), L - 4)
    y0 = min(max(by - 2, 0), L - 4)
    fine = np.where((lat[:, 0] >= x0) & (lat[:, 0] <= x0 + 4) &
                    (lat[:, 1] >= y0) & (lat[:, 1] <= y0 + 4))[0]
    return np.setdiff1d(fine, exclude)


def job_walk(args):
    jid, L, d, sigma, alo, ahi, n_trials = args
    rng = np.random.default_rng([SEED, jid])
    g = np.arange(0.0, L + 1e-9, 1.0)
    X, Y = np.meshgrid(g, g)
    lat = np.column_stack([X.ravel(), Y.ravel()])
    nlat = len(lat)
    Dm = np.sqrt(((lat[:, None, :] - lat[None, :, :]) ** 2).sum(-1))
    Lc = np.linalg.cholesky(np.exp(-Dm / DCORR) + 1e-9 * np.eye(nlat))
    coarse = np.where((lat[:, 0] % 3 == 0) & (lat[:, 1] % 3 == 0))[0]
    gp = make_grid(-1.0, L + 1.0, 0.5)
    keys = ["hH", "hA", "dA", "sA", "hB", "dB", "sB", "hC", "ci_w", "ci_in", "B_surf",
            "det_frac", "det_any", "npts", "hAz", "hBz", "dz",
            "real_ok", "real_hH", "real_hB", "real_dB", "real_hBz"]
    R = {k: [] for k in keys}
    for _ in range(n_trials):
        tgt = np.array([rng.uniform(0, L), rng.uniform(0, L), -d])
        n_true = rng.uniform(N_LO, N_HI)
        alpha = rng.uniform(alo, ahi)
        v = rng.normal(0, VIC_SD)
        o = rng.normal(0, DEV_SD)                 # TEK telefon: ofset tum noktalarda ortak
        sd_field = math.sqrt(sigma ** 2 + (KAPPA * alpha * d) ** 2)
        field = (Lc @ rng.normal(size=nlat)) * sd_field
        zs = rng.uniform(-ROUGH, ROUGH, nlat)
        pts = np.column_stack([lat, zs])
        r = np.linalg.norm(pts - tgt, axis=1)
        mu = P0 + v + o - 10 * n_true * np.log10(r) - alpha * d + field
        # her kafes noktasi icin 20 ornek (ayni ornekler ideal ve gercekci kosulda kullanilir)
        smp = mu[:, None] + rng.normal(0, SIG_FAST, (nlat, N_SAMP))
        ideal = smp.mean(1)
        rec = smp >= SENS
        cnt = rec.sum(1)
        det_pt = cnt >= 3
        trunc = np.where(det_pt, (smp * rec).sum(1) / np.maximum(cnt, 1), np.nan)   # yalniz alinan paketler
        known_all = pts + rng.normal(0, AR_SD, (nlat, 3))

        if L <= 6:
            idx = np.arange(nlat)
            idx_r = idx
        else:   # kaba (3 m) -> ince (1 m, 5x5) uyarlamali tarama
            bx, by = lat[coarse[int(np.argmax(ideal[coarse]))]]
            idx = np.r_[coarse, fine_window(lat, bx, by, L, coarse)]
            dc = det_pt[coarse]
            if dc.any():
                cc = coarse[dc]
                bx, by = lat[cc[int(np.nanargmax(trunc[cc]))]]
            else:
                bx, by = L / 2, L / 2
            idx_r = np.r_[coarse, fine_window(lat, bx, by, L, coarse)]
        rssi = ideal[idx]
        known = known_all[idx]
        sig_eff = math.sqrt(sd_field ** 2 + SIG_FAST ** 2 / N_SAMP)

        k = int(np.argmax(rssi))
        R["hH"].append(np.hypot(*(known[k, :2] - tgt[:2])))
        e = estimate_3d(known, rssi, gp, sig_eff, d)
        R["hA"].append(np.hypot(*(e["A"][:2] - tgt[:2])))
        R["dA"].append(abs(-e["A"][2] - d))
        R["sA"].append(-e["A"][2] - d)
        R["hB"].append(np.hypot(*(e["B"][:2] - tgt[:2])))
        R["dB"].append(abs(-e["B"][2] - d))
        R["sB"].append(-e["B"][2] - d)
        R["B_surf"].append(bool(-e["B"][2] <= 0.2))
        R["hC"].append(np.hypot(tgt[0] - L / 2, tgt[1] - L / 2))
        R["ci_w"].append(e["ci_w"])
        R["ci_in"].append(e["ci_in"])
        R["det_frac"].append(float(det_pt[idx].mean()))
        R["det_any"].append(bool(det_pt[idx].any()))
        R["npts"].append(len(idx))
        db = max(d + rng.normal(0, BARO_SD), 0.05)
        thA, thB = estimate_fixed_z(known, rssi, gp["xy"], -db, gp["lo"], gp["hi"])
        R["hAz"].append(np.hypot(*(thA - tgt[:2])))
        R["hBz"].append(np.hypot(*(thB[:2] - tgt[:2])))
        R["dz"].append(abs(db - d))

        # GERCEKCI: yalniz -100 dBm ustunde alinan paketler; algilanmayan nokta veri vermez
        ok_pts = idx_r[det_pt[idx_r]]
        R["real_ok"].append(len(ok_pts) >= 6)
        if len(ok_pts) >= 1:
            kk = ok_pts[int(np.argmax(trunc[ok_pts]))]
            R["real_hH"].append(np.hypot(*(known_all[kk, :2] - tgt[:2])))
        if len(ok_pts) >= 6:
            er = estimate_3d(known_all[ok_pts], trunc[ok_pts], gp, sig_eff, d)
            R["real_hB"].append(np.hypot(*(er["B"][:2] - tgt[:2])))
            R["real_dB"].append(abs(-er["B"][2] - d))
            _, thBr = estimate_fixed_z(known_all[ok_pts], trunc[ok_pts], gp["xy"], -db, gp["lo"], gp["hi"])
            R["real_hBz"].append(np.hypot(*(thBr[:2] - tgt[:2])))

    out = dict(kind="yuruyus", L=L, d=d, sigma=sigma, alpha=[alo, ahi], n=n_trials)
    for kk in ["hH", "hA", "dA", "sA", "hB", "dB", "sB", "hC", "ci_w", "hAz", "hBz", "dz", "npts",
               "real_hH", "real_hB", "real_dB", "real_hBz"]:
        out[kk] = q(R[kk])
    for kk in ["ci_in", "det_frac", "det_any", "B_surf", "real_ok"]:
        out[kk] = float(np.mean(R[kk]))
    return out


# --------------------------------------------------------------------------- analitik bolumler
def crlb(anc, tgt, sig, which):
    """Cramer-Rao alt siniri: yatay ve derinlik std (m). Tekilse inf."""
    def f(th):
        c = th[3] if which in ("B", "C") else 0.0
        n = th[4] if which == "C" else N_EST
        r = np.linalg.norm(anc - th[:3], axis=1)
        return P0 + c - 10 * n * np.log10(r)
    th0 = np.array(list(tgt) + ([0.0] if which in ("B", "C") else []) + ([N_EST] if which == "C" else []))
    J = np.empty((len(anc), len(th0)))
    for k in range(len(th0)):
        h = 1e-5
        tp, tm = th0.copy(), th0.copy()
        tp[k] += h
        tm[k] -= h
        J[:, k] = (f(tp) - f(tm)) / (2 * h)
    F = J.T @ J / sig ** 2
    sv = np.linalg.svd(F, compute_uv=False)
    cond = sv[0] / max(sv[-1], 1e-300)
    if cond > 1e10:
        return float("inf"), float("inf"), cond
    C = np.linalg.inv(F)
    return math.sqrt(C[0, 0] + C[1, 1]), math.sqrt(C[2, 2]), cond


def section_crlb():
    print("\n" + "=" * 100)
    print("5) CRAMER-RAO ALT SINIRI (en iyi yansiz kestiricinin ulasabilecegi std; sigma=6, alpha=12.5 dB/m)")
    print("   A: (x,y,z) bilinen P0,n,zayiflama | B: +ortak ofset c | C: +c +n (yol kaybi ussu de bilinmiyor)")
    print("=" * 100)
    rows = []
    for setup in ["4capa_L12", "4capa_L6", "4capa_L12_duzensiz", "yuruyus_L6_49nokta"]:
        if setup.startswith("4capa"):
            L = 12.0 if "L12" in setup else 6.0
            if "duzensiz" in setup:   # ayni cember uzerinde OLMAYAN dortgen
                anc = np.array([[0, 0, 0], [L, 0.15 * L, 0], [0.85 * L, L, 0], [0.1 * L, 0.8 * L, 0]], float)
            else:                      # kare: 4 kose ayni cember uzerinde
                anc = np.array([[0, 0, 0], [L, 0, 0], [L, L, 0], [0, L, 0]], float)
            dev = DEV_SD
        else:
            L = 6.0
            g = np.arange(0.0, 7.0, 1.0)
            X, Y = np.meshgrid(g, g)
            anc = np.column_stack([X.ravel(), Y.ravel(), np.zeros(49)])
            dev = 0.0
        for where, (fx, fy) in [("merkez", (0.5, 0.5)), ("merkez-disi", (0.25, 0.35))]:
            for d in (1.0, 3.0, 6.0):
                sig = math.sqrt(36 + (KAPPA * 12.5 * d) ** 2 + dev ** 2 + SIG_FAST ** 2 / N_SAMP)
                tgt = (fx * L, fy * L, -d)
                res = {w: crlb(anc, tgt, sig, w) for w in ("A", "B", "C")}
                rows.append(dict(setup=setup, where=where, d=d, sig=sig,
                                 **{f"{w}_h": res[w][0] for w in res}, **{f"{w}_z": res[w][1] for w in res}))
                fmt = lambda v: "  tekil" if not np.isfinite(v) else f"{v:7.2f}"
                print(f"  {setup:20s} {where:11s} d={d:3.0f}m sig_eff={sig:5.1f}dB | "
                      f"A: yatay {fmt(res['A'][0])} der {fmt(res['A'][1])} | "
                      f"B: yatay {fmt(res['B'][0])} der {fmt(res['B'][1])} | "
                      f"C: yatay {fmt(res['C'][0])} der {fmt(res['C'][1])}")
    print("  Not: A satiri zayiflamanin BILINDIGI hayali durumdur; gercekte zayiflama bilinmedigi icin A yanlidir (bkz. tablo 1).")
    print("  Not: kare (ve her dikdortgen) koseleri ayni cember uzerindedir -> |a_i|^2 capa koordinatlarinin afin fonksiyonu olur ->")
    print("       4 capali B'nin Fisher matrisi HER hedef konumunda tekildir: (x,y,z,c) icin tek parametreli bir cozum egrisi vardir.")
    return rows


def section_tradeoff():
    print("\n" + "=" * 100)
    print("6) DERINLIK <-> MALZEME ODUNLESIMI (yalniz RSSI'dan katman/malzeme cikarilabilir mi?)")
    print("=" * 100)
    out = {}
    # 6a: link butcesi tablosu
    print("6a) En iyi durum (telefon tam ustte, n=2.5) beklenen RSSI [dBm]; '<' = -100 dBm altinda (algilanamaz)")
    ds = [0.5, 1, 2, 3, 4, 6]
    als = [5, 10, 15, 20]
    print("      d(m) " + "".join(f"  a={a:>2}dB/m" for a in als))
    lb = {}
    for dd in ds:
        vals = [P0 - 25 * math.log10(dd) - a * dd for a in als]
        lb[dd] = vals
        print(f"    {dd:5.1f}  " + "".join(f"  {v:8.1f}{'<' if v < SENS else ' '}" for v in vals))
    out["link_budget"] = lb
    # 6b: ayni RSSI'yi veren (d, alpha) ciftleri
    print("\n6b) Ayni RSSI'yi ureten (derinlik, zayiflama) ciftleri: alpha = (P0 - 10 n log10 d - RSSI)/d  [dB/m]")
    pairs = {}
    for obs in (-80.0, -90.0, -98.0):
        print(f"   Gozlenen RSSI = {obs:.0f} dBm")
        pairs[obs] = []
        for dd in (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0):
            row = []
            for n in (2.0, 2.5, 3.5):
                a = (P0 - 10 * n * math.log10(dd) - obs) / dd
                row.append(a)
            pairs[obs].append((dd, row))
            txt = "  ".join(f"n={n}: {a:6.1f}" for n, a in zip((2.0, 2.5, 3.5), row))
            print(f"     d={dd:3.1f} m -> alpha  {txt}")
    out["pairs"] = {str(k): v for k, v in pairs.items()}
    # 6c: katman kombinasyonlari
    print("\n6c) Katman kombinasyonlari: nominal 2.4 GHz kayiplari (varsayim): betonarme doseme 20 dB, "
          "tugla/briket duvar 8 dB, ahsap/mobilya/alcipan 3 dB, bosluk 0 dB")
    comb = {}
    for D, tol in ((20.0, 7.0), (40.0, 7.0), (60.0, 7.0)):
        found = []
        for ks in range(0, 5):
            for kb in range(0, 9):
                for kw in range(0, 9):
                    tot = 20 * ks + 8 * kb + 3 * kw
                    if abs(tot - D) <= tol:
                        found.append((ks, kb, kw, tot))
        comb[D] = found
        ex = sorted(found, key=lambda t: (t[0], t[1]))
        exs = "; ".join(f"{a}doseme+{b}duvar+{c}ahsap={t}dB" for a, b, c, t in ex[:: max(1, len(ex) // 6)][:6])
        print(f"   Olculen fazla kayip {D:.0f}+/-{tol:.0f} dB -> {len(found)} farkli katman kombinasyonu uyumlu. Ornek: {exs}")
    out["layer_combos"] = {str(k): len(v) for k, v in comb.items()}
    return out


def section_bayes(rng):
    """Tek bir ust-nokta RSSI okumasindan derinlik ve malzeme sinifinin Bayes-optimal cikarimi."""
    print("\n" + "=" * 100)
    print("7) TEK RSSI OKUMASINDAN (tarama tepe noktasi) DERINLIK ve MALZEME SINIFI: Bayes-optimal sonsal dagilim")
    print("   Onsel: d~U(0.5,6) m, n~U(2,3.5), ofset v~N(0,3)+o~N(0,4), golgeleme N(0,6), hizli/20; yatay kacik h<=0.71 m")
    print("=" * 100)
    res = {}
    for prior_name, alo, ahi in (("alpha~U(5,20)", 5.0, 20.0), ("alpha~U(2,40) (bosluklu..som beton)", 2.0, 40.0)):
        M = 600_000
        d = rng.uniform(0.5, 6.0, M)
        a = rng.uniform(alo, ahi, M)
        n = rng.uniform(N_LO, N_HI, M)
        hx, hy = rng.uniform(-0.5, 0.5, (2, M))
        r = np.sqrt(hx ** 2 + hy ** 2 + d ** 2)
        noise = rng.normal(0, math.sqrt(6 ** 2 + VIC_SD ** 2 + DEV_SD ** 2 + SIG_FAST ** 2 / N_SAMP), M)
        A = a * d * (1 + KAPPA * rng.normal(size=M))
        rs = P0 - 10 * n * np.log10(r) - A + noise
        detm = rs >= SENS
        print(f"\n   Onsel {prior_name}: algilanabilir okuma orani = {detm.mean()*100:.1f}%")
        print("     RSSI araligi    | derinlik p10/p50/p90 (m) | alpha p10/p50/p90 (dB/m) | toplam kayip alpha*d p10/p90 (dB)")
        bins = np.arange(-100, -54, 5)
        rows = []
        for lo in bins:
            m = detm & (rs >= lo) & (rs < lo + 5)
            if m.sum() < 200:
                continue
            dq = np.percentile(d[m], [10, 50, 90])
            aq = np.percentile(a[m], [10, 50, 90])
            tq = np.percentile((a * d)[m], [10, 90])
            rows.append(dict(lo=float(lo), d=dq.tolist(), a=aq.tolist(), t=tq.tolist(), n=int(m.sum())))
            print(f"     [{lo:4.0f},{lo+5:4.0f}) dBm | {dq[0]:4.1f} / {dq[1]:4.1f} / {dq[2]:4.1f}       | "
                  f"{aq[0]:5.1f} / {aq[1]:5.1f} / {aq[2]:5.1f}       | {tq[0]:5.1f} / {tq[1]:5.1f}")
        # MAP siniflandirma dogrulugu (algilananlar icinde), 1 dB kutular
        edges = np.arange(-100, -40, 1.0)
        bi = np.digitize(rs[detm], edges)
        acls = np.digitize(a[detm], np.linspace(alo, ahi, 4)[1:-1])
        dcls = np.digitize(d[detm], [2.0, 4.0])

        def map_acc(cls, k):
            tab = np.zeros((len(edges) + 1, k))
            np.add.at(tab, (bi, cls), 1)
            return tab.max(1).sum() / tab.sum(), np.bincount(cls, minlength=k).max() / len(cls)
        acc_a, base_a = map_acc(acls, 3)
        acc_d, base_d = map_acc(dcls, 3)
        # derinlik barometreden (N(0,0.8)) biliniyorsa: 2 boyutlu kutu (RSSI 2 dB x d_baro 0.5 m)
        dbar = d[detm] + rng.normal(0, BARO_SD, detm.sum())
        b2 = np.digitize(rs[detm], np.arange(-100, -40, 2.0)) * 100 + np.digitize(dbar, np.arange(-2, 9, 0.5))
        _, inv = np.unique(b2, return_inverse=True)
        tab2 = np.zeros((inv.max() + 1, 3))
        np.add.at(tab2, (inv, acls), 1)
        acc_a_baro = tab2.max(1).sum() / tab2.sum()
        print(f"     MAP dogrulugu (3 malzeme sinifi, alpha esit genislikte): {acc_a*100:.1f}%  (sans/cogunluk: {base_a*100:.1f}%)")
        print(f"     MAP dogrulugu (3 derinlik sinifi 0.5-2/2-4/4-6 m):         {acc_d*100:.1f}%  (sans/cogunluk: {base_d*100:.1f}%)")
        print(f"     MAP dogrulugu (3 malzeme sinifi) derinlik barometreden +/-0.8 m BILINIRSE: {acc_a_baro*100:.1f}%")
        res[prior_name] = dict(det_rate=float(detm.mean()), rows=rows, acc_alpha=float(acc_a), base_alpha=float(base_a),
                               acc_depth=float(acc_d), base_depth=float(base_d), acc_alpha_baro=float(acc_a_baro))
    return res


# --------------------------------------------------------------------------- raporlama
def f2(x):
    return f"{x['med']:5.2f}/{x['p90']:5.2f}"


def tag4(r):
    g = "kare" if r["jitter"] == 0 else f"duz{r['jitter']:.1f}"
    return f"{r['pos']:3s} {g:6s} a{r['alpha'][0]:.0f}-{r['alpha'][1]:.0f}"


def print_4anchor(rs, title):
    print("\n" + "=" * 100)
    print(title)
    print("   A = (x,y,z) kestirici; B = (x,y,z,c) ortak ofsetli; Merkez = hep karenin ortasini soyleyen naif tahmin")
    print("   det4/det1 = 4 linkin hepsi / en az 1'i -100 dBm ustunde algilanir (KESTIRIM ESIGI YOK SAYAR: iyimser)")
    print("   A@20m = A'nin derinlik sinirina (20 m) yapistigi oran; B@yuzey = B'nin z~0'a yapistigi oran; GA95 = B derinlik %95 profil guven araligi genisligi")
    print("=" * 100)
    print(" L  d sig senaryo           | det4 det1 | A yatay     A derin     A@20m | B yatay     B derin     B biasMed B@yuzey | Merkez yatay | GA95gen kapsar")
    for r in rs:
        print(f"{r['L']:2.0f} {r['d']:2.0f} {r['sigma']:2.0f} {tag4(r):18s}| {r['det_all']*100:3.0f}% {r['det_any']*100:3.0f}% | "
              f"{f2(r['hA'])} {f2(r['dA'])} {r['A_bound']*100:4.0f}% | {f2(r['hB'])} {f2(r['dB'])} {r['sB']['med']:+7.2f}  {r['B_surf']*100:4.0f}%  | "
              f"{f2(r['hC'])}  | {r['ci_w']['med']:6.2f} {r['ci_in']*100:4.0f}%")


def print_baro(rs):
    print("\n" + "=" * 100)
    print("2) BAROMETRE ILE DERINLIK (kurban telefonu basinci advertisement'ta) + yatay konum RSSI'dan (4 capa)")
    print("   baro kalibre: N(0,0.8 m) | kalibresiz: N(0,4 m) (~0.5 hPa cihazlar arasi mutlak ofset)")
    print("   alpha: B|z'nin ofsetinden alpha_hat=-c/d_baro ile malzeme cikarimi; 3 sinif (esit genislik), sans ~%33")
    print("   'det4 icinde' = yalniz 4 linkin de gercekten algilandigi denemeler (n = o deneme sayisi)")
    print("=" * 100)
    print("   'cogunluk' = algilanan denemelerde en sik gercek sinifin orani (hep o sinifi soyleyen naif tahminin dogrulugu)")
    print(" L  d sig senaryo           | A|z yatay   B|z yatay   derin(kal)  | B|z yatay(kalsiz) derin(kalsiz) | alpha hata med sinif | det4 icinde: n  sinif cogunluk B|z yatay")
    for r in rs:
        adet = (f"{r['a_ok_det']*100:4.0f}%  {r['a_base_det']*100:4.0f}%  " if r["n_det_all"] > 0 else "   -      -    ")
        hdet = f2(r["hBz_det"]) if r["n_det_all"] > 0 else "     -     "
        print(f"{r['L']:2.0f} {r['d']:2.0f} {r['sigma']:2.0f} {tag4(r):18s}| {f2(r['hAz'])} {f2(r['hBz'])} {f2(r['dz'])} | "
              f"{f2(r['hBz_u'])}       {f2(r['dz_u'])}  | {r['a_err']['med']:5.1f} dB/m {r['a_ok']*100:4.0f}% | "
              f"{r['n_det_all']:4d} {adet} {hdet}")


def print_walk(rs, title):
    print("\n" + "=" * 100)
    print(title)
    print("   L=6: 7x7=49 nokta; L=12: kaba 5x5 (3 m) + ince 5x5 (1 m) uyarlamali = ~49 nokta")
    print("   IDEAL: esik alti ornekler de kullanilir. GERCEKCI: yalniz >=-100 dBm paketler; >=6 algilanan nokta yoksa kestirim YOK")
    print("   Sezgisel = en guclu RSSI noktasi (derinlik vermez); B|baro = B, z barometreden (0.8 m)")
    print("=" * 100)
    print(" L  d sig alfa  | det%nokta det1 | IDEAL: Sezgisel  A yatay     A derin     | B yatay     B derin     B@yuzey | B|baro yatay | Merkez     "
          "| GERCEKCI: basari Sezgisel    B yatay     B derin     B|baro yatay | GA95gen kapsar")
    for r in rs:
        print(f"{r['L']:2.0f} {r['d']:2.0f} {r['sigma']:2.0f} {r['alpha'][0]:.0f}-{r['alpha'][1]:<3.0f}| {r['det_frac']*100:6.0f}% {r['det_any']*100:5.0f}% | "
              f"{f2(r['hH'])}  {f2(r['hA'])} {f2(r['dA'])} | {f2(r['hB'])} {f2(r['dB'])} {r['B_surf']*100:4.0f}%  | "
              f"{f2(r['hBz'])}  | {f2(r['hC'])} | {r['real_ok']*100:5.0f}%  {f2(r['real_hH'])} {f2(r['real_hB'])} {f2(r['real_dB'])} {f2(r['real_hBz'])}  | "
              f"{r['ci_w']['med']:6.2f} {r['ci_in']*100:4.0f}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=500)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"))
    args = ap.parse_args()
    T = args.trials
    t0 = time.time()
    print(f"Enkaz BLE RSSI Monte Carlo | seed={SEED} | deneme/senaryo={T} | P0={P0} n_est={N_EST} | "
          f"alpha~U({ALPHA_LO},{ALPHA_HI}) dB/m | n~U({N_LO},{N_HI}) | duyarlilik={SENS} dBm")

    jobs4, jid = [], 0
    for L in (6.0, 12.0):                        # temel: kare, GPS vs AR, alpha U(5,20)
        for d in (1.0, 3.0, 6.0):
            for s in (3.0, 6.0, 9.0):
                for pn, psd in (("GPS", GPS_SD), ("AR", AR_SD)):
                    jobs4.append((jid, L, d, s, pn, psd, 0.0, ALPHA_LO, ALPHA_HI, T))
                    jid += 1
    extra4 = []
    for L in (6.0, 12.0):
        for d in (1.0, 3.0, 6.0):
            extra4.append((jid, L, d, 6.0, "AR", AR_SD, 1.5, ALPHA_LO, ALPHA_HI, T)); jid += 1   # duzensiz dortgen
            extra4.append((jid, L, d, 6.0, "AR", AR_SD, 0.0, 1.0, 5.0, T)); jid += 1             # dusuk zayiflama
    jobsw = []
    for L in (6.0, 12.0):
        for d in (1.0, 3.0, 6.0):
            for s in (3.0, 6.0, 9.0):
                jobsw.append((1000 + jid, L, d, s, ALPHA_LO, ALPHA_HI, T)); jid += 1
    extraw = []
    for L in (6.0, 12.0):
        for d in (1.0, 3.0, 6.0):
            extraw.append((1000 + jid, L, d, 6.0, 1.0, 5.0, T)); jid += 1
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        fw = [ex.submit(job_walk, j) for j in jobsw + extraw]
        f4 = [ex.submit(job_4anchor, j) for j in jobs4 + extra4]
        r4all = [f.result() for f in f4]
        rwall = [f.result() for f in fw]
    r4, r4x = r4all[:len(jobs4)], r4all[len(jobs4):]
    rw, rwx = rwall[:len(jobsw)], rwall[len(jobsw):]

    print_4anchor(r4, "1) 4 KURTARICI TELEFON, KARE KOSELER, alpha~U(5,20) dB/m — hatalar medyan/p90 (m)")
    print_4anchor(r4x, "1b) 4 CAPA DUYARLILIK: duzensiz dortgen (koseler +/-1.5 m) ve DUSUK zayiflama alpha~U(1,5) (bosluklu enkaz), sigma=6, AR")
    print_baro([r for r in r4 if r["sigma"] == 6.0] + [r for r in r4x if r["alpha"][0] == 1.0])
    print_walk(rw, "3) TEK KURTARICI YURUYEREK TARAMA (1 m izgara, AR 0.2 m), alpha~U(5,20) — hatalar medyan/p90 (m)")
    print_walk(rwx, "3b) YURUYEREK TARAMA, DUSUK zayiflama alpha~U(1,5) (bosluklu enkaz), sigma=6")
    crl = section_crlb()
    to = section_tradeoff()
    by = section_bayes(np.random.default_rng([SEED, 99999]))

    with open(args.out, "w") as fh:
        json.dump(dict(anchors4=r4, anchors4_extra=r4x, walk=rw, walk_extra=rwx, crlb=crl, tradeoff=to, bayes=by,
                       config=dict(seed=SEED, trials=T)), fh, indent=1, default=float)
    print(f"\nSonuclar JSON: {args.out} | sure {time.time()-t0:.0f} s")


if __name__ == "__main__":
    main()
