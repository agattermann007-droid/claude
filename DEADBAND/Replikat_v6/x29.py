"""5.10 gegen Kombinationen mit bewachten Fades, auf GFT 2022-26 und Fremddaten 2006-21 (gleiche Regeln)."""
import numpy as np, sys, pickle, os, eng6 as E, evl6 as V, r6, gext, streams as ST, prep5 as P
F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
target = sys.argv[1]
if target == "ext":
    DXf = pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb"))
    Sx = pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb"))
    V._MK = E.Market(D=DXf, S=Sx)
gPF = ("pf", 30, 1.2)
C510 = dict(r6.C510, **r6.PAY3)
OFF = dict(db_on=0, r21_on=0, nz_on=0)
configs = [
    ("5.10 (Budget 2,0)", C510, [], {}, []),
    ("5.10 Budget 0,9", dict(C510, gesamtbudget=0.9, idea_cap=0.9), [], {}, []),
    ("F10 bewacht", dict(C510, **OFF, gesamtbudget=0.9, idea_cap=0.9), F10, {n: gPF for n in F10}, [0.75] * 10),
    ("5.10 B0,9 + F10 bewacht", dict(C510, gesamtbudget=0.9, idea_cap=0.9), F10, {n: gPF for n in F10}, [0.75] * 10),
    ("NZ+R21 B0,9 + F10 bewacht", dict(C510, db_on=0, gesamtbudget=0.9, idea_cap=0.9), F10, {n: gPF for n in F10}, [0.75] * 10),
    ("NZ B0,9 + F10 bewacht", dict(C510, db_on=0, r21_on=0, gesamtbudget=0.9, idea_cap=0.9), F10, {n: gPF for n in F10}, [0.75] * 10),
]
for lbl, kw, names, guards, risks in configs:
    blks = ST.blocks(names, target, guards) if names else []
    GP = E.gparams([dict(on=1, risk=r, maxtrades=1) for r in risks])
    V.set_generic(blks, GP)
    if target == "ext":
        r = V.evaluate(E.params(**dict(r6.SAFE, **kw)), GP=GP, horizons=(250, 500, 750), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
    else:
        r = V.evaluate(E.params(**dict(r6.SAFE, **kw)), GP=GP, horizons=(250, 500, 750), step=3, seeds=tuple(range(8)))
    print(V.line(f"{target} {lbl}", r["mean"]), flush=True)
