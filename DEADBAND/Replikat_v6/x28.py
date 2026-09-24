"""Fades + Noise v2 + Eroeffnungsmomentum, mit/ohne Waechter, GFT 2022-26 und Fremddaten 2006-21."""
import numpy as np, sys, eng6 as E, evl6 as V, r6, gext, streams as ST
F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
target = sys.argv[1]
if target == "ext":
    V._MK = E.Market(D=gext.data_ext())
base = dict(r6.C510, **r6.PAY3, gesamtbudget=0.9, idea_cap=0.9, db_on=0, r21_on=0, nz_on=0)
gPF = ("pf", 30, 1.2)
configs = [
    ("F10+NZ2 ohne Waechter", F10 + ["NZ2"], {}, [0.75] * 10 + [0.6]),
    ("F10+NZ2 Waechter", F10 + ["NZ2"], {n: gPF for n in F10 + ["NZ2"]}, [0.75] * 10 + [0.6]),
    ("F10+NZ2+ODM Waechter", F10 + ["NZ2", "ODM"], {n: gPF for n in F10 + ["NZ2", "ODM"]}, [0.75] * 10 + [0.6, 0.6]),
    ("F10+NZ2h+ODM Waechter", F10 + ["NZ2h", "ODM"], {n: gPF for n in F10 + ["NZ2h", "ODM"]}, [0.75] * 10 + [0.6, 0.6]),
    ("F10+NZ2+ODM Waechter nur Fades", F10 + ["NZ2", "ODM"], {n: gPF for n in F10}, [0.75] * 10 + [0.6, 0.6]),
]
for lbl, names, guards, risks in configs:
    blks = ST.blocks(names, target, guards)
    GP = E.gparams([dict(on=1, risk=r, maxtrades=(1 if i < 10 else 0)) for i, r in enumerate(risks)])
    V.set_generic(blks, GP)
    if target == "ext":
        r = V.evaluate(E.params(**dict(r6.SAFE, **base)), GP=GP, horizons=(250, 500, 750), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
    else:
        r = V.evaluate(E.params(**dict(r6.SAFE, **base)), GP=GP, horizons=(250, 500, 750), step=3, seeds=tuple(range(8)))
    print(V.line(f"{target} {lbl}", r["mean"]), flush=True)
