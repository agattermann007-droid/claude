"""Validierung der Fades auf Daten VOR 2022 (nie in der Suche verwendet), gleiche Parameter."""
import numpy as np, sys
import gext, gsig as G
gext.use_ext()
import scan6 as S, cands as K
K._CACHE.clear()
names = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
tot = []
for nm in names:
    p = K.FADES[nm]
    b, (ie, d, rd, tp, ix) = K.fade(0, **p)
    if len(ie) == 0:
        print(nm, "keine Signale"); continue
    R, why, held, *_ = G.simulate(p["sym"], ie, d, rd, tp, ix)
    te = b["t_entry"]
    m = G.metrics(R, te, f"{nm} 2006-2021")
    G.show(m)
    for lo, hi, tag in ((2006, 2011, "06-10"), (2011, 2016, "11-15"), (2016, 2022, "16-21")):
        yr = (te // 1440 // 365.25 + 1970).astype(int)
        mk = (yr >= lo) & (yr < hi)
        if mk.sum() > 20:
            mm = G.metrics(R[mk], te[mk])
            print(f"     {tag}: n {mm['n']:4d} WR {mm['wr']:5.1f} PF {mm['pf']:4.2f} R/J {mm['Ry']:+5.1f} maxS {mm['maxS']}")
