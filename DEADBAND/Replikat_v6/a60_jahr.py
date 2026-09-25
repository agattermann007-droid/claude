"""Build 6.60: Warum zahlen die Konten 2024-25 seltener aus als 2022-23, obwohl die Fades auf Signal-Ebene kaum schwaecher
sind? Konto-Diagnose je Kalenderjahr: 1-Jahres-Konten (jeder 2. Handelstag, 8 Stoerungen), Trades nach Kalenderjahr des
Ausstiegs: Ergebnis, Zahl und Trefferquote je Modul, dazu Tageskennzahlen je Startjahr (gueltige Tage, Tage ohne Trade,
Verlusttage, Wartetage) und der Anteil der Fade-Signale, die der Portfolio-Waechter live liess.
Aufruf: python a60_jahr.py [Variante aus x60.VAR] [gft|ext]"""
import numpy as np, sys, os
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
warm, end = ("2006-09-01", "2021-12-31") if target == "ext" else (V.WARM, None)
st_list = V.starts(mk, 250, 2, warm, end)
names = x48.F10N
yr_of = lambda d: int(str(np.datetime64(int(d), "D"))[:4])
agg = {}
days_agg = {}
for (a, b) in st_list:
    for seed in range(8):
        ms = V.masks(mk, seed, 0.08 if seed > 0 else 0.0)
        P2 = Pv.copy()
        if seed > 0:
            P2[E.PI["slip_frac"]] = 0.3
        r = E.run(mk, P2, a, b, seed=seed, masks=ms, GP=GP)
        sy = yr_of(mk.days[a])
        st = r["st"]; S = E.SI
        dd = days_agg.setdefault(sy, np.zeros(9))
        dd += [r["years"], st[S["npay"]], st[S["valid_days"]], st[S["d_notrade"]], st[S["d_neg"]], st[S["d_wait"]],
               st[S["d_25_50"]] + st[S["d_0_25"]], st[S["cool"]], st[S["sumpay"]]]
        for row in r["tr"]:
            y = yr_of(row[0]); sl = int(row[2])
            nm = "RSI21" if 2 <= sl < E.NZ0 else ("Noise" if E.NZ0 <= sl < E.NZ1 else ("DB" if sl < 2 else names[(sl - E.G0) // 2]))
            a_ = agg.setdefault((y, nm), [0.0, 0, 0])
            a_[0] += row[1]; a_[1] += 1; a_[2] += int(row[1] > 0)
print(f"{target} {lbl}: je Startjahr (1-Jahres-Konten): Ausz/J, gueltige Tage/J, Tage ohne Trade, Verlusttage, 0-50$-Tage, Wartetage, Serien-Stopps/J, Netto/J")
for y, v in sorted(days_agg.items()):
    Y = v[0]
    print(f"  Start {y}: Ausz {v[1] / Y:5.2f} gueltig {v[2] / Y:5.1f} leer {v[3] / Y:5.1f} neg {v[4] / Y:5.1f} 0-50 {v[6] / Y:5.1f} "
          f"warte {v[5] / Y:5.1f} Stopps {v[7] / Y:4.1f} Netto {0.776 * v[8] / Y:5.0f}")
years = sorted({k[0] for k in agg})
mods = ["RSI21", "Noise"] + names
# Trades je Kalenderjahr: Summe ueber alle Konten / Zahl der Konto-Jahre, die das Kalenderjahr abdecken (Naeherung: Anteil)
cover = {}
for (a, b) in st_list:
    for d in range(a, min(b, len(mk.days) - 1)):
        y = yr_of(mk.days[d]); cover[y] = cover.get(y, 0) + 1
tdays = {}
for d in range(len(mk.days)):
    y = yr_of(mk.days[d]); tdays[y] = tdays.get(y, 0) + 1
print("Ergebnis je Kalenderjahr und Modul ($ je Konto-Jahr / Trades / Treffer %):")
print("  " + "Modul".ljust(8) + "".join(f"{y:>22d}" for y in years))
for nm in mods:
    cells = []
    for y in years:
        a_ = agg.get((y, nm))
        kj = cover.get(y, 0) * 8 / max(tdays.get(y, 1), 1)            # Konto-Jahre in diesem Kalenderjahr
        if a_ is None or kj == 0:
            cells.append(" " * 22); continue
        cells.append(f"{a_[0] / kj:8.0f}$ {a_[1] / kj:5.1f} {100 * a_[2] / max(a_[1], 1):4.0f}%")
    print("  " + nm.ljust(8) + "".join(f"{c:>22s}" for c in cells))
tot = {y: sum(agg.get((y, nm), [0, 0, 0])[0] for nm in mods) / max(cover.get(y, 0) * 8 / max(tdays.get(y, 1), 1), 1e-9) for y in years}
print("  Summe   " + "".join(f"{tot[y]:21.0f}$" for y in years))
live = [(nm, n0, n1) for nm, n0, n1 in info]
print("Fade-Signale gesamt / live (Waechter + Filter):", " ".join(f"{nm} {n1}/{n0}" for nm, n0, n1 in live))
