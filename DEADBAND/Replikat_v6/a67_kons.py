"""Build 6.70: Wie weit ist 6.60 heute von einer 15-%-Konsistenzregel entfernt? Durchgehendes Konto 2022-2025 (16 Stoerungen):
je Auszahlungszyklus Gewinn der Periode (Summe der Tagesergebnisse), bester Tag und dessen Anteil; dazu die Zahl der Tage,
die der Zyklus mindestens haette, wenn der beste Tag bleibt (Gewinn >= bester Tag / 0,145).
Aufruf: python a67_kons.py ["Variante"] [Start] [Ende]"""
import numpy as np, sys
import x60, x48, r6
import eng10 as E, evl6 as V

lbl = sys.argv[1] if len(sys.argv) > 1 else "6.60"
A = sys.argv[2] if len(sys.argv) > 2 else "2022-01-03"
B = sys.argv[3] if len(sys.argv) > 3 else None
kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x60.VAR[lbl])
blks, info, mk = x60.setup("gft", rule, extra)
V._MK = mk
mk.r21["reg"] = x48.r21_regime("gft", mk)
GP = x60.fade_gp(gpx, frisk, per, extra_gp)
V.set_generic(blks, GP)
Pv = E.params(**dict(r6.SAFE, **kw))
a = mk.day_index(A); b = mk.day_index(B) if B else len(mk.days) - 1
rat, tot_l, best_l, share_l, gross_d = [], [], [], [], []
for seed in range(16):
    ms = V.masks(mk, seed, 0.08 if seed > 0 else 0.0)
    P2 = Pv.copy()
    if seed > 0:
        P2[E.PI["slip_frac"]] = 0.3
    r = E.run(mk, P2, a, b, seed=seed, masks=ms, GP=GP)
    tr, ev = r["tr"], r["ev"]
    pays = ev[ev[:, 0] == 1, 1] if len(ev) else np.zeros(0)
    busts = ev[ev[:, 0] == 3, 1] if len(ev) else np.zeros(0)
    cuts = np.sort(np.r_[pays, busts])
    d_all = {}
    for row in tr:
        d_all[int(row[0])] = d_all.get(int(row[0]), 0.0) + row[1]
    gross_d.append(sum(v for v in d_all.values()) / max(r["years"], 1e-9))
    lo = -10 ** 9
    for c in pays:
        days_c = {d: v for d, v in d_all.items() if lo < d <= c}
        lo = c
        if not days_c:
            continue
        tot = sum(days_c.values()); best = max(days_c.values())
        if tot <= 0:
            continue
        tot_l.append(tot); best_l.append(best); rat.append(best / tot)
        share_l.append(np.mean(np.array(list(days_c.values())) >= 0.5 * best))
rat = np.array(rat); tot_l = np.array(tot_l); best_l = np.array(best_l)
print(f"{lbl}: {len(rat)} Auszahlungen (16 Stoerungen, {A}..{str(np.datetime64(int(mk.days[b]), 'D'))}), Gewinn je Jahr (Summe Tagesergebnisse) {np.mean(gross_d):.0f} $")
print(f"  Gewinn der Periode: Median {np.median(tot_l):.0f} $ (p25 {np.percentile(tot_l, 25):.0f}, p75 {np.percentile(tot_l, 75):.0f})")
print(f"  bester Tag der Periode: Median {np.median(best_l):.0f} $ (p25 {np.percentile(best_l, 25):.0f}, p75 {np.percentile(best_l, 75):.0f})")
print(f"  Anteil bester Tag / Gewinn: Median {100 * np.median(rat):.0f} % (p10 {100 * np.percentile(rat, 10):.0f} %, p90 {100 * np.percentile(rat, 90):.0f} %)"
      f" | Auszahlungen, die 15 % erfuellen: {100 * np.mean(rat < 0.15):.1f} %, 25 %: {100 * np.mean(rat < 0.25):.1f} %, 40 %: {100 * np.mean(rat < 0.40):.1f} %")
need = best_l / 0.145
print(f"  noetiger Gewinn bei 15 % (Reserve 0,5): Median {np.median(need):.0f} $ = {np.median(need) / (np.mean(gross_d) / 12):.1f} Monatsgewinne")
