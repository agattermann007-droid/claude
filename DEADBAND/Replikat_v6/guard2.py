"""Praxistaugliche Waechter-Varianten (EA muss sie aus ~1 Jahr M5-Historie rekonstruieren)."""
import numpy as np, streams as ST
F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
LIM = ST.LIM22

def mask_days(t, R, days, pf_th, nmin):
    live = np.zeros(len(R), bool)
    for i in range(len(R)):
        m = (t < t[i]) & (t >= t[i] - days * 1440)
        w = R[m]
        if len(w) < nmin:
            continue
        pos = w[w > 0].sum(); neg = -w[w < 0].sum()
        live[i] = (pos / neg if neg > 0 else 9.9) > pf_th
    return live

def mask_n(R, N, pf_th):
    return ST.guard_mask(R, N, "pf", pf_th)

series = {}
for nm in F10:
    b1, R1 = ST.virt("ext", nm); b2, R2 = ST.virt("gft", nm)
    pre = b1["t_entry"] < LIM
    series[nm] = (np.r_[b1["t_entry"][pre], b2["t_entry"]], np.r_[R1[pre], R2])
variants = [("N30 PF1.2", lambda t, R: mask_n(R, 30, 1.2)), ("N20 PF1.2", lambda t, R: mask_n(R, 20, 1.2)),
            ("250d PF1.2 min10", lambda t, R: mask_days(t, R, 250, 1.2, 10)), ("250d PF1.2 min15", lambda t, R: mask_days(t, R, 250, 1.2, 15)),
            ("180d PF1.2 min10", lambda t, R: mask_days(t, R, 180, 1.2, 10)), ("250d PF1.0 min10", lambda t, R: mask_days(t, R, 250, 1.0, 10)),
            ("365d PF1.2 min10", lambda t, R: mask_days(t, R, 365, 1.2, 10))]
for lbl, fn in variants:
    pre_s = post_s = 0.0; npre = npost = 0
    for nm, (t, R) in series.items():
        live = fn(t, R)
        pre = t < LIM
        pre_s += R[live & pre].sum(); post_s += R[live & ~pre].sum(); npre += (live & pre).sum(); npost += (live & ~pre).sum()
    print(f"{lbl:18s}: vor 2022 {pre_s/16:+6.1f} R/J ({npre/16:.0f} Tr/J) | ab 2022 {post_s/4.67:+6.1f} R/J ({npost/4.67:.0f} Tr/J)")
