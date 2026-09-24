"""Fade-Portfolio mit Regime-Waechter im GFT-Konto: GFT-Daten 2022-26 und Fremddaten 2006-21."""
import numpy as np, sys, eng6 as E, evl6 as V, r6, gext, guardblk as GB
names = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
base = dict(r6.C510, **r6.PAY3, gesamtbudget=0.9, idea_cap=0.9, db_on=0, r21_on=0, nz_on=0)
GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1)] * 10)
target = sys.argv[1]
if target == "ext":
    V._MK = E.Market(D=gext.data_ext())
for mode, N, th in (("off", 0, 0.0), ("sum", 40, 0.0), ("pf", 30, 1.2)):
    blks, info = GB.blocks(names, target, N=N, mode=mode, th=th)
    V.set_generic(blks, GP)
    lbl = f"{target} Waechter {mode} N{N}"
    if target == "ext":
        r = V.evaluate(E.params(**dict(r6.SAFE, **base)), GP=GP, horizons=(250, 500, 750), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
    else:
        r = V.evaluate(E.params(**dict(r6.SAFE, **base)), GP=GP, horizons=(250, 500, 750), step=3, seeds=tuple(range(8)))
    print(V.line(lbl, r["mean"]), " live:", sum(i[1] for i in info), "von", sum(i[2] for i in info), flush=True)
