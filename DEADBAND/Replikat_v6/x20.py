"""Frueher Break-even / Teilgewinn fuer DEADBAND und RSI21: Trefferquote, Serien, Busts bei Mindestauszahlung 3 %."""
import eng6 as E, r6
GP0 = E.gparams([])
C = [("5.10 Ausz3", dict(r6.C510, **r6.PAY3), GP0)]
for t1, be, f in ((1.0, 0.1, 0.5), (0.75, 0.1, 0.5), (0.5, 0.05, 0.5), (0.75, 0.2, 0.3)):
    C.append((f"DB tp1 {t1}/{be}/{f}", dict(r6.C510, **r6.PAY3, db_tp1r=t1, db_be=be, db_tp1f=f), GP0))
for t1, be, f in ((1.0, 0.1, 0.5), (0.75, 0.1, 0.5), (0.5, 0.05, 0.5)):
    C.append((f"R21 tp1 {t1}/{be}/{f}", dict(r6.C510, **r6.PAY3, r21_tp1r=t1, r21_be=be, r21_tp1f=f), GP0))
C.append(("DB+R21 tp1 0.75/0.1/0.5", dict(r6.C510, **r6.PAY3, db_tp1r=0.75, db_be=0.1, db_tp1f=0.5, r21_tp1r=0.75, r21_be=0.1, r21_tp1f=0.5), GP0))
r6.run(C, "x20.json")
