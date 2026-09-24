"""Endzahlen 6.00 (Waechter: PF der letzten 30 virtuellen Signale > 1,2, volles Fenster) auf GFT 2022-26 (16 Stoerungen) und Fremddaten 2006-21 (4 Stoerungen)."""
import numpy as np, sys, json, pickle, os, eng6 as E, evl6 as V, r6, streams as ST, prep5 as P
F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
g = ("pf", 30, 1.2)
B = dict(r6.C510, **r6.PAY3)
CFG = {
    "5.10": (B, [], []),
    "6.00 Sicher": (dict(B, db_on=0, r21_on=0, nz_on=0, gesamtbudget=0.9, idea_cap=0.9), F10, [0.75] * 10),
    "6.00 Ertrag": (dict(B, db_on=0, r21_risk=0.5, nz_risk=0.35, cool_n=3, gesamtbudget=0.9, idea_cap=0.9), F10, [0.75] * 10),
}
target = sys.argv[1]
if target == "ext":
    V._MK = E.Market(D=pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb")), S=pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb")))
res = {}
for lbl, (kw, names, risks) in CFG.items():
    blks = ST.blocks(names, target, {n: g for n in names}) if names else []
    GP = E.gparams([dict(on=1, risk=r, maxtrades=1) for r in risks])
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    if target == "ext":
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
    else:
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=3, seeds=tuple(range(16)), skip=0.08)
    res[lbl] = {k: v for k, v in r["mean"].items()}
    res[lbl]["by"] = {str(h): {k: v for k, v in r[h].items() if k != "mods"} for h in (250, 500, 750)}
    print(V.line(f"{target} {lbl}", r["mean"]), flush=True)
json.dump(res, open(f"x33_{target}.json", "w"), indent=1, default=float)
