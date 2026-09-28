"""Build 6.70, Diagnose der Basis 6.60 auf den Fremddaten: Woraus bestehen die Verluste vor einem Bust? Je Konto mit Bust
(1-Jahres-Konten, jeder 3. Tag, Seed 0): Ergebnis je Modul in den 60 Kalendertagen vor dem Bust, und ob die Fades zu dem
Zeitpunkt live waren (Portfolio-Waechter). Aufruf: python a70_bustmod.py -> ergebnisse/a70_bustmod.txt"""
import numpy as np, collections, os
import x70, x60, x48, r6, evl6 as V
import eng11 as E

kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x70.VAR["6.60"])
blks, info, mk = x60.setup("ext", rule)
V._MK = mk; mk.r21["reg"] = x48.r21_regime("ext", mk)
GP = x70.fade_gp(gpx, frisk, per); V.set_generic(blks, GP)
Pv = E.params(**dict(r6.SAFE, **kw))
m = V.mk()


def mod(sl):
    sl = int(sl)
    return "RSI21" if 2 <= sl < 6 else ("Noise" if 6 <= sl < 9 else ("DB" if sl < 2 else "Fades"))


agg = collections.defaultdict(float); cnt = collections.Counter(); nb = 0; months = collections.Counter()
reg_days = {}
for (a, b) in V.starts(m, 250, 3, "2006-09-01", "2021-12-31"):
    r = E.run(m, Pv, a, b, seed=0, masks=V.masks(m, 0, 0.0), GP=GP)
    ev = r["ev"]; tr = r["tr"]
    for e in ev[ev[:, 0] == 2]:
        bd = int(e[1]); nb += 1
        months[str(np.datetime64(bd, "D"))[:7]] += 1
        sel = (tr[:, 0] > bd - 60) & (tr[:, 0] <= bd)
        for row in tr[sel]:
            agg[mod(row[2])] += row[1]; cnt[mod(row[2])] += 1
lines = [f"Basis 6.60, Fremddaten, 1-Jahres-Konten jeder 3. Tag, Seed 0: {nb} Busts",
         "Monate: " + " ".join(f"{k}:{v}" for k, v in sorted(months.items())),
         "Ergebnis je Modul in den 60 Tagen vor dem Bust (Summe ueber alle Busts, je Bust):"]
for k in sorted(agg, key=lambda x: agg[x]):
    lines.append(f"  {k:6s} {agg[k] / max(nb, 1):8.1f} $ je Bust, {cnt[k] / max(nb, 1):5.1f} Trades je Bust")
txt = "\n".join(lines); print(txt)
open(os.path.join("ergebnisse", "a70_bustmod.txt"), "w").write(txt + "\n")
