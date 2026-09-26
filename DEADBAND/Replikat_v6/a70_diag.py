"""Build 6.70, Diagnose der Basis 6.60 (vor den Kandidaten-Tests): Woraus bestehen die Verlustserien, und wie viele Tage
scheitern knapp an der Schwelle des gueltigen Tags?
- Serien: alle Verlust-Ideen in Serien >= 5 nach Modul und danach, ob der vorige Verlust am selben Tag lag (Tages-Cluster).
- Tage: realisiertes Tagesergebnis je Konto-Tag (nach Ausstiegstag) mit Fade-Gewinn, aber unter der Schwelle (50,50 $).
- Fade-Treffer: Ergebnis in R je Modul (R = Ergebnis / Stop-Risiko beim Einstieg).
1-Jahres-Konten, jeder 2. Handelstag, ohne Stoerung (Seed 0), GFT-Ersatz.
Aufruf: python a70_diag.py [gft] -> ergebnisse/a70_diag.txt"""
import numpy as np, sys, os
from collections import Counter, defaultdict
import x70, x60, x48, r6, evl6 as V
import eng11 as E

target = sys.argv[1] if len(sys.argv) > 1 else "gft"
kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x70.VAR["6.60"])
blks, info, mk = x60.setup(target, rule)
V._MK = mk
mk.r21["reg"] = x48.r21_regime(target, mk)
GP = x70.fade_gp(gpx, frisk, per)
V.set_generic(blks, GP)
Pv = E.params(**dict(r6.SAFE, **kw))
F10N = x48.F10N
NEED = 50.5


def modname(sl):
    if sl < 2:
        return "DB"
    if sl < E.NZ0:
        return "RSI21"
    if sl < E.NZ1:
        return "Noise"
    return F10N[(sl - E.G0) // 2]


out = []
m = V.mk()
st_all = V.starts(m, 250, 2)
lossmods = Counter(); streakmods = Counter(); sameday = [0, 0]; nstreak = 0
day_sub = 0; day_valid = 0; day_sub_fadewin = 0; day_neg = 0; ndays = 0
fR = defaultdict(list)
years = 0.0
for (a, b) in st_all:
    r = E.run(m, Pv, a, b, seed=0, masks=V.masks(m, 0, 0.0), GP=GP)
    years += r["years"]
    tr = r["tr"]
    if len(tr) == 0:
        continue
    # Ideen wie evl6 (Noise-Teile zusammen), mit Tag und Modul
    items = []; nz = {}
    for i, row in enumerate(tr):
        sl = int(row[2])
        if E.NZ0 <= sl < E.NZ1:
            pid = row[3]
            s, i0, d0 = nz.get(pid, (0.0, i, row[0]))
            nz[pid] = (s + row[1], i, row[0])
        else:
            items.append((i, row[1], sl, row[0]))
    for pid, (s, i, d0) in nz.items():
        items.append((i, s, E.NZ0, d0))
    items.sort()
    cur = []
    for (i, x, sl, dday) in items + [(1e18, 1.0, -1, -1)]:
        if x < 0:
            cur.append((sl, dday)); lossmods[modname(sl)] += 1
        else:
            if len(cur) >= 5:
                nstreak += 1
                for j, (sl2, d2) in enumerate(cur):
                    streakmods[modname(sl2)] += 1
                    if j > 0:
                        sameday[0 if d2 == cur[j - 1][1] else 1] += 1
            cur = []
    # Tage (nach Ausstiegstag)
    dsum = defaultdict(float); dfw = defaultdict(bool)
    for row in tr:
        dsum[row[0]] += row[1]
        sl = int(row[2])
        if sl >= E.G0 and row[1] > 0:
            dfw[row[0]] = True
            if row[7] > 0:
                fR[modname(sl)].append(row[1] / row[7])
        elif sl >= E.G0 and row[7] > 0:
            fR[modname(sl)].append(row[1] / row[7])
    for dday, s in dsum.items():
        ndays += 1
        if s >= NEED:
            day_valid += 1
        elif s > 0:
            day_sub += 1
            day_sub_fadewin += int(dfw[dday])
        else:
            day_neg += 1

lines = []
lines.append(f"Basis 6.60 ({target}), {len(st_all)} Konten zu 1 Jahr, {years:.0f} Konto-Jahre")
lines.append(f"Serien >= 5: {nstreak / years:.2f} je Jahr; Verluste darin nach Modul (Anteil) gegen alle Verluste:")
tl = sum(lossmods.values()); ts = sum(streakmods.values())
for nm in sorted(lossmods, key=lambda k: -lossmods[k]):
    lines.append(f"  {nm:7s} alle {100 * lossmods[nm] / tl:5.1f} %   in Serien >= 5 {100 * streakmods[nm] / max(ts, 1):5.1f} %")
lines.append(f"  Verlust in Serie am selben Tag wie der vorige: {100 * sameday[0] / max(sum(sameday), 1):.1f} % ({sum(sameday)} Paare)")
lines.append(f"Handelstage (Ausstiegstag) je Jahr: {ndays / years:.1f}; gueltig {day_valid / years:.1f}, 0..50,50 $ {day_sub / years:.1f} "
             f"(davon mit Fade-Gewinn {day_sub_fadewin / years:.1f}), <= 0 {day_neg / years:.1f}")
lines.append("Fade-Ergebnis in R je Modul: Trades je Jahr, Trefferquote, Anteil Gewinner < 0,71 R, Median-Gewinn R:")
for nm in F10N:
    x = np.array(fR.get(nm, []))
    if len(x) == 0:
        continue
    w = x[x > 0]
    lines.append(f"  {nm:7s} {len(x) / years:5.1f}/J  WR {100 * np.mean(x > 0):5.1f} %  Gewinner < 0,71 R {100 * np.mean(w < 0.71) if len(w) else 0:5.1f} %  "
                 f"Median-Gewinn {np.median(w) if len(w) else 0:4.2f} R")
txt = "\n".join(lines)
print(txt)
open(os.path.join("ergebnisse", f"a70_diag_{target}.txt"), "w").write(txt + "\n")
