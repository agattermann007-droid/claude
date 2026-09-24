"""Fade-Portfolio im GFT-Konto: 6 Stroeme, Gesamtbudget 0,9 %, Mindestauszahlung 3 %."""
import numpy as np, eng6 as E, evl6 as V, r6, cands as K
names = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930"]
V.set_generic(K.fade_blocks(names), None)
base = dict(r6.C510, **r6.PAY3, gesamtbudget=0.9, idea_cap=0.9)
off = dict(db_on=0, r21_on=0, nz_on=0)
def S(r, **kw): return dict(on=1, risk=r, maxtrades=1, **kw)
C = []
for r in (0.45, 0.6, 0.75, 0.9):
    C.append((f"6 Fades je {r}", dict(base, **off), E.gparams([S(r)] * 6)))
C.append(("6 Fades je 0.75 + NZ 0.45", dict(base, db_on=0, r21_on=0), E.gparams([S(0.75)] * 6)))
C.append(("6 Fades je 0.75 + NZ + R21", dict(base, db_on=0), E.gparams([S(0.75)] * 6)))
C.append(("6 Fades je 0.75 + 5.10 alt", dict(base), E.gparams([S(0.75)] * 6)))
C.append(("6 Fades 0.75, Budget 1.5", dict(base, **off, gesamtbudget=1.5, idea_cap=1.25), E.gparams([S(0.75)] * 6)))
r6.run(C, "x24.json")
