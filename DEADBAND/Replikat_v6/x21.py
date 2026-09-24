"""Konflikt-Test: DEADBAND aus (viele Trades, wenig Ertrag), RSI21/Noise hoeher gewichtet."""
import eng6 as E, r6
GP0 = E.gparams([])
base = dict(r6.C510, **r6.PAY3)
C = []
for r21, nz, bud in ((0.63, 0.45, 1.2), (0.9, 0.6, 1.8), (1.1, 0.75, 2.2), (1.3, 0.9, 2.6)):
    kw = dict(base, db_on=0, r21_risk=r21, nz_risk=nz, r21_budget=bud, gesamtbudget=max(2.0, bud + 0.8))
    C.append((f"ohne DB R21 {r21} NZ {nz}", kw, GP0))
C.append(("ohne DB, ohne NZ, R21 1.1", dict(base, db_on=0, nz_on=0, r21_risk=1.1, r21_budget=2.2, gesamtbudget=2.6), GP0))
C.append(("ohne R21 (DB+NZ)", dict(base, r21_on=0), GP0))
C.append(("nur NZ 0.9", dict(base, db_on=0, r21_on=0, nz_risk=0.9), GP0))
r6.run(C, "x21.json")
