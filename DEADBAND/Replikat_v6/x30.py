"""Feinabstimmung der Mischung RSI21 + Noise + bewachte Fades (ohne DEADBAND) auf beiden Datensaetzen."""
import numpy as np, sys, pickle, os, eng6 as E, evl6 as V, r6, gext, streams as ST, prep5 as P
F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
F8 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N1100", "X0300S", "X1000S"]
target = sys.argv[1]
if target == "ext":
    DXf = pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb"))
    Sx = pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb"))
    V._MK = E.Market(D=DXf, S=Sx)
gPF = ("pf", 30, 1.2)
B = dict(r6.C510, **r6.PAY3, db_on=0, gesamtbudget=0.9, idea_cap=0.9)
configs = [
    ("A R21 .63 NZ .45 F10", B, F10),
    ("B R21 .5 NZ .45 F10", dict(B, r21_risk=0.5), F10),
    ("C R21 .5 NZ .35 F10", dict(B, r21_risk=0.5, nz_risk=0.35), F10),
    ("D R21 .63 NZ .45 F8", B, F8),
    ("E A + Serienstopp 3", dict(B, cool_n=3), F10),
    ("F A + Serienstopp 3 +1 Tag", dict(B, cool_n=3, cool_days=1), F10),
    ("G A ohne R21-2.Platz", dict(B, r21_second=0), F10),
    ("H A Ausz 4 %", dict(B, minpayout=320.0), F10),
]
for lbl, kw, names in configs:
    blks = ST.blocks(names, target, {n: gPF for n in names})
    GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1)] * len(names))
    V.set_generic(blks, GP)
    if target == "ext":
        r = V.evaluate(E.params(**dict(r6.SAFE, **kw)), GP=GP, horizons=(250, 500, 750), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
    else:
        r = V.evaluate(E.params(**dict(r6.SAFE, **kw)), GP=GP, horizons=(250, 500, 750), step=3, seeds=tuple(range(8)))
    print(V.line(f"{target} {lbl}", r["mean"]).split(" | ")[0], flush=True)
