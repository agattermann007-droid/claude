"""GPDF: Nachbarparameter auf Stromebene (Plateau?)."""
import numpy as np, itertools
import pa11 as PA
base = dict(la=-360, lb=1020, loff=-1, w0=-360, w1=120, x=480, sd=0.0, md=0.6, sb=0.10, tm=0, crv=3.0)
def run(**kw):
    p = dict(base); p.update(kw)
    b = PA.sweep("XAU", p["la"], p["lb"], p["loff"], p["w0"], p["w1"], p["x"], p["sd"], p["md"], 0.0, 0, p["sb"], p["tm"], p["crv"], 99.0, 1)
    res, _ = PA.evalb(b)
    return " | ".join(f"{k}: n{v['n']:4d} WR{v['wr']:3.0f}% E{v['er']:+.3f} PF{v['pf']:4.2f}" for k, v in res.items())
print("Basis        ", run())
for k, vals in dict(crv=(2.0, 2.5, 3.5, 4.0), sb=(0.03, 0.05, 0.15, 0.2), md=(0.3, 0.45, 0.8, 1.2), w1=(60, 90, 180, 240),
                    x=(300, 420, 540, 600), w0=(-300, -240), sd=(0.03, 0.05)).items():
    for v in vals:
        print(f"{k}={v:<8}", run(**{k: v}))
print("Ziel Gegenseite", run(tm=2)); print("Ziel Mitte", run(tm=1))
