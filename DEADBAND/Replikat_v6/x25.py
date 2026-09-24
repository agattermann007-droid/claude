"""10 Fade-Stroeme (+ NZ/R21), Gesamtbudget 0,9 %, Mindestauszahlung 3 %."""
import numpy as np, eng6 as E, evl6 as V, r6, cands as K
names = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
V.set_generic(K.fade_blocks(names), None)
base = dict(r6.C510, **r6.PAY3, gesamtbudget=0.9, idea_cap=0.9)
off = dict(db_on=0, r21_on=0, nz_on=0)
def S(r, **kw): return dict(on=1, risk=r, maxtrades=1, **kw)
C = []
C.append(("10 Fades je 0.75", dict(base, **off), E.gparams([S(0.75)] * 10)))
C.append(("10 Fades je 0.6", dict(base, **off), E.gparams([S(0.6)] * 10)))
C.append(("8 (ohne N1100/N1300) je 0.75", dict(base, **off), E.gparams([S(0.75)] * 6 + [{}, {}] + [S(0.75)] * 2)))
C.append(("10 Fades 0.75 + NZ", dict(base, db_on=0, r21_on=0), E.gparams([S(0.75)] * 10)))
C.append(("10 Fades 0.75 + NZ + R21", dict(base, db_on=0), E.gparams([S(0.75)] * 10)))
C.append(("10 Fades 0.75, Budget 1.2", dict(base, **off, gesamtbudget=1.2, idea_cap=1.0), E.gparams([S(0.75)] * 10)))
r6.run(C, "x25.json")
