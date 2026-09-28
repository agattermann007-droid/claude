"""Build 6.70, Diagnose der Basis 6.60 (Runde 2): verlorene gueltige Tage und Gewinne an schon gueltigen Tagen.
Aus dem Trade-Protokoll (Spalte 10 = Ausstiegszeit) je Konto-Tag das realisierte Tagesergebnis in Ausstiegsreihenfolge
(Naeherung: Teilernten zaehlen erst beim Schliessen der Position):
- verlorene gueltige Tage: zwischendurch >= 50,50 $, am Ende darunter. Welche Verluste kamen danach (Modul, Einstieg vor oder
  nach dem Gueltigwerden)?
- Gewinne nach dem Gueltigwerden (gleicher Tag, fuer den Takt ueberzaehlig), je Modul.
1-Jahres-Konten, jeder 2. Handelstag, Seed 0. Aufruf: python a70_verl.py [gft|ext] -> ergebnisse/a70_verl_{ziel}.txt"""
import numpy as np, sys, os, collections
import x70, x60, x48, r6, evl6 as V
import eng11 as E

target = sys.argv[1] if len(sys.argv) > 1 else "gft"
kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x70.VAR["6.60"])
blks, info, mk = x60.setup(target, rule)
V._MK = mk; mk.r21["reg"] = x48.r21_regime(target, mk)
GP = x70.fade_gp(gpx, frisk, per); V.set_generic(blks, GP)
Pv = E.params(**dict(r6.SAFE, **kw))
NEED = 50.5
m = V.mk()
warm, end = (("2006-09-01", "2021-12-31") if target == "ext" else (V.WARM, None))


def mod(sl):
    sl = int(sl)
    return "RSI21" if 2 <= sl < E.NZ0 else ("Noise" if E.NZ0 <= sl < E.NZ1 else ("DB" if sl < 2 else "Fade"))


def key(t):                       # Reihenfolge im Prop-Tag (17:00 NY = 0)
    return (int(t) % 1440 + 420) % 1440


years = 0.0; nlost = 0; lost_by = collections.Counter(); lost_pre = collections.Counter(); lost_post = collections.Counter()
after_win = collections.defaultdict(lambda: [0, 0.0]); nvalid = 0
for (a, b) in V.starts(m, 250, 2, warm, end):
    r = E.run(m, Pv, a, b, seed=0, masks=V.masks(m, 0, 0.0), GP=GP)
    years += r["years"]; tr = r["tr"]
    if len(tr) == 0:
        continue
    for dday in np.unique(tr[:, 0]):
        rows = tr[tr[:, 0] == dday]
        rows = rows[np.argsort([key(x) for x in rows[:, 10]], kind="stable")]
        cum = 0.0; tval = None
        for x in rows:
            if tval is not None and x[1] > 0:
                a_ = after_win[mod(x[2])]; a_[0] += 1; a_[1] += x[1]
            cum += x[1]
            if tval is None and cum >= NEED:
                tval = key(x[10])
        if tval is not None:
            nvalid += 1
            if cum < NEED:
                nlost += 1
                for x in rows:
                    if key(x[10]) >= tval and x[1] < 0:
                        md = mod(x[2]); lost_by[md] += 1
                        pre = (int(x[3]) // 1440 < int(dday)) or key(x[3]) < tval
                        (lost_pre if pre else lost_post)[md] += 1
lines = [f"Basis 6.60 ({target}), 1-Jahres-Konten jeder 2. Tag, Seed 0, {years:.0f} Konto-Jahre (Naeherung ueber Ausstiegsreihenfolge)",
         f"zwischendurch gueltige Tage je Jahr {nvalid / years:.1f}, davon am Ende verloren {nlost / years:.2f}",
         "Verluste nach dem Gueltigwerden an verlorenen Tagen (je Jahr): Modul, davon Einstieg vorher / nachher:"]
for md in sorted(lost_by, key=lambda k: -lost_by[k]):
    lines.append(f"  {md:6s} {lost_by[md] / years:5.2f}  vorher {lost_pre[md] / years:5.2f}  nachher {lost_post[md] / years:5.2f}")
lines.append("Gewinne nach dem Gueltigwerden am selben Tag (je Jahr: Anzahl, Summe):")
for md, (n, s) in sorted(after_win.items(), key=lambda kv: -kv[1][1]):
    lines.append(f"  {md:6s} {n / years:5.1f}  {s / years:7.0f} $")
txt = "\n".join(lines); print(txt)
open(os.path.join("ergebnisse", f"a70_verl_{target}.txt"), "w").write(txt + "\n")
