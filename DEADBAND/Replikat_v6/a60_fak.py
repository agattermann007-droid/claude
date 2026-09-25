"""Build 6.60: Wie oft handeln die Konten mit verkleinerter Groesse (Pufferkurve x Faktor unter Startsaldo), und wie viel
tragen diese Trades bei? Je Kalenderjahr: Anteil der Einstiege mit Groessenfaktor 1 / 0,6-1 / < 0,6, Ergebnis je Gruppe.
Aufruf: python a60_fak.py [Variante] [gft|ext]"""
import numpy as np, sys
import x60, x48, r6
import eng10 as E, evl6 as V, evl10 as V10

lbl = sys.argv[1] if len(sys.argv) > 1 else "6.50 Ertrag"
target = sys.argv[2] if len(sys.argv) > 2 else "gft"
kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x60.VAR[lbl])
blks, info, mk = x60.setup(target, rule, extra)
V._MK = mk
mk.r21["reg"] = x48.r21_regime(target, mk)
GP = x60.fade_gp(gpx, frisk, per, extra_gp)
V.set_generic(blks, GP)
Pv = E.params(**dict(r6.SAFE, **kw))
yr_of = lambda d: int(str(np.datetime64(int(d), "D"))[:4])
warm, end = (V.WARM, None) if target == "gft" else ("2006-09-01", "2021-12-31")
acc = {}
for (a, b) in V.starts(mk, 250, 4, warm, end):
    for seed in range(4):
        ms = V.masks(mk, seed, 0.08 if seed > 0 else 0.0)
        P2 = Pv.copy()
        if seed > 0:
            P2[E.PI["slip_frac"]] = 0.3
        r = E.run(mk, P2, a, b, seed=seed, masks=ms, GP=GP)
        for row in r["tr"]:
            fk = row[8]
            if fk < 0:
                continue
            g = 0 if fk >= 0.999 else (1 if fk >= 0.6 else 2)
            y = yr_of(row[0])
            x = acc.setdefault(y, np.zeros((3, 3)))
            x[g, 0] += 1; x[g, 1] += row[1]; x[g, 2] += fk
for y, x in sorted(acc.items()):
    n = x[:, 0].sum()
    print(f"{target} {lbl} {y}: " + " | ".join(
        f"{nm}: {100 * x[g, 0] / n:4.1f}% der Trades, Ø Faktor {x[g, 2] / max(x[g, 0], 1):.2f}, {x[g, 1] / max(x[g, 0], 1):+6.1f} $/Trade"
        for g, nm in enumerate(("voll", "0,6-1", "<0,6"))))
