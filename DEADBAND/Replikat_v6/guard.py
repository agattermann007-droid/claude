"""Regime-Waechter je Modul: live nur, wenn die letzten N virtuellen Trades (alle Signale) eine Summe > 0 R bzw. PF > x haben.
Test ueber 2006-2026 (Fremddaten bis 2021, GFT-Daten ab 2022)."""
import numpy as np, gsig as G, gext, cands as K, scan6 as S

def trades(dataset, nm):
    G._D = gext.data_ext() if dataset == "ext" else None
    if dataset != "ext":
        G.data()
    K._CACHE.clear()
    p = K.FADES[nm]
    b, (ie, d, rd, tp, ix) = K.fade(0, **p)
    R, *_ = G.simulate(p["sym"], ie, d, rd, tp, ix)
    return b["t_entry"], R

def guard_apply(t, R, N, mode, th):
    live = np.zeros(len(R), bool)
    for i in range(len(R)):
        if i < N:
            continue
        w = R[i - N:i]
        if mode == "sum":
            live[i] = w.sum() > th
        else:
            pos = w[w > 0].sum(); neg = -w[w < 0].sum()
            live[i] = (pos / neg if neg > 0 else 9.9) > th
    return live

names = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
data = {}
for nm in names:
    t1, R1 = trades("ext", nm); t2, R2 = trades("gft", nm)
    data[nm] = (np.r_[t1, t2], np.r_[R1, R2])
lim22 = np.datetime64("2022-01-01", "m").astype(np.int64)
for N, mode, th in ((20, "sum", 0.0), (30, "sum", 0.0), (40, "sum", 0.0), (30, "pf", 1.2), (40, "pf", 1.2), (60, "pf", 1.2)):
    tot_pre = 0.0; tot_post = 0.0; n_pre = 0; n_post = 0; base_pre = 0.0; base_post = 0.0; yrs_pre = 16.0; yrs_post = 4.67
    per = []
    for nm in names:
        t, R = data[nm]
        live = guard_apply(t, R, N, mode, th)
        pre = t < lim22
        tot_pre += R[live & pre].sum(); tot_post += R[live & ~pre].sum()
        base_pre += R[pre].sum(); base_post += R[~pre].sum()
        n_pre += (live & pre).sum(); n_post += (live & ~pre).sum()
        per.append(f"{nm}:{R[live & pre].sum()/yrs_pre:+.1f}/{R[live & ~pre].sum()/yrs_post:+.1f}")
    print(f"N{N} {mode}>{th}: vor 2022 {tot_pre/yrs_pre:+6.1f} R/J ({n_pre/yrs_pre:.0f} Tr/J, ohne Waechter {base_pre/yrs_pre:+.1f}) | "
          f"ab 2022 {tot_post/yrs_post:+6.1f} R/J ({n_post/yrs_post:.0f} Tr/J, ohne {base_post/yrs_post:+.1f})")
    print("     ", " ".join(per))
