"""Build 6.60: Wo geht die Signal-Kante der Fades im Konto verloren? Jeder Fade-Trade im Konto wird seinem virtuellen Signal
(gleiches Modul, gleiche Einstiegskerze) zugeordnet: R im Konto (Ergebnis inkl. Teilschliessungen / Stop-Risiko beim Einstieg)
gegen R des Signals (Stop, Ziel, Zeit-Ausstieg ohne Konto). Ausgabe je Kalenderjahr und Modul: Trades, Summe R virtuell,
Summe R im Konto, Differenz, dazu Verteilung der Differenz (Konto-Trade besser / schlechter / gleich).
Aufruf: python a60_drag.py [Variante aus x60.VAR] [gft|ext] [Schritt] [Stoerungen]"""
import numpy as np, sys
import x60, x48, r6
import eng10 as E, evl6 as V, evl10 as V10

lbl = sys.argv[1] if len(sys.argv) > 1 else "6.50 Ertrag"
target = sys.argv[2] if len(sys.argv) > 2 else "gft"
step = int(sys.argv[3]) if len(sys.argv) > 3 else 4
nseed = int(sys.argv[4]) if len(sys.argv) > 4 else 4
kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x60.VAR[lbl])
blks, info, mk = x60.setup(target, rule, extra)
V._MK = mk
mk.r21["reg"] = x48.r21_regime(target, mk)
GP = x60.fade_gp(gpx, frisk, per, extra_gp)
V.set_generic(blks, GP)
Pv = E.params(**dict(r6.SAFE, **kw))
# virtuelles R je Signal (Strom, Einstiegszeit)
import pg_blocks as PB
vR = {}
for s_, nm in enumerate(PB.F10):
    f = PB.fi(target, nm)
    for te, R in zip(f["t_entry"], f["R"]):
        vR[(s_, int(te))] = float(R)
warm, end = ("2006-09-01", "2021-12-31") if target == "ext" else (V.WARM, None)
yr_of = lambda d: int(str(np.datetime64(int(d), "D"))[:4])
acc = {}
miss = 0
for (a, b) in V.starts(mk, 250, step, warm, end):
    for seed in range(nseed):
        ms = V.masks(mk, seed, 0.08 if seed > 0 else 0.0)
        P2 = Pv.copy()
        if seed > 0:
            P2[E.PI["slip_frac"]] = 0.3
        r = E.run(mk, P2, a, b, seed=seed, masks=ms, GP=GP)
        for row in r["tr"]:
            sl = int(row[2])
            if sl < E.G0 or row[7] <= 0:
                continue
            s_ = (sl - E.G0) // 2
            if s_ >= len(PB.F10):
                continue
            tmin = int(row[3])
            v = vR.get((s_, tmin))
            if v is None:
                v = vR.get((s_, tmin - 1440))
            if v is None:
                miss += 1
                continue
            ra = row[1] / row[7]
            y = yr_of(row[0])
            a_ = acc.setdefault((y, PB.F10[s_]), [0, 0.0, 0.0, 0, 0])
            a_[0] += 1; a_[1] += v; a_[2] += ra
            if ra < v - 0.05:
                a_[3] += 1
            elif ra > v + 0.05:
                a_[4] += 1
years = sorted({k[0] for k in acc})
print(f"{target} {lbl}: Fade-Trades im Konto gegen ihr virtuelles Signal (R je Trade), nicht zugeordnet: {miss}")
print("Zellen: Trades | R/Trade virtuell -> Konto | Anteil Konto schlechter / besser (Abweichung > 0,05 R)")
for nm in PB.F10 + ["SUMME"]:
    cells = []
    for y in years:
        if nm == "SUMME":
            parts = [acc[k] for k in acc if k[0] == y]
            a_ = [sum(p[i] for p in parts) for i in range(5)] if parts else None
        else:
            a_ = acc.get((y, nm))
        if not a_ or a_[0] == 0:
            cells.append(" " * 40); continue
        n = a_[0]
        cells.append(f"{n:6d} | {a_[1] / n:+.3f} -> {a_[2] / n:+.3f} | {100 * a_[3] / n:3.0f}/{100 * a_[4] / n:3.0f}%")
    print(f"{nm:7s} " + "  ".join(cells))
print("Jahre:", years)
