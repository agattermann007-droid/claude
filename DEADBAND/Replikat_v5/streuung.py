"""Streuung ueber die 16 Stoerungen (Seeds) fuer die Schlussvergleiche."""
import numpy as np, json, eng5 as E, evl5 as V, batch as B
from concurrent.futures import ProcessPoolExecutor
m = V.mk()
P50 = dict(db_tp1r=1.5, db_be=0.05, db_tp1f=0.5)
C2 = dict(P50, r21_risk=0.63, nz_risk=0.45, ge_mode=1, bank_on=1, bank_last=2, bank_minr=0.5, bank_mods=1,
          cool_n=4, cool_days=0, idea_cap=1.25)
AS_IS = dict(rule_losers=0, float_losers=0, swap_guard=0.0)
out = {}
for lbl, kw in (("5.00 wie ist | GFT zaehlt netto", AS_IS), ("5.00 wie ist | GFT zaehlt nur Verlierer", dict(AS_IS, rule_losers=1)),
                ("5.00 regelsicher", {}), ("5.10 (C2)", C2)):
    kw2 = dict(B.SAFE); kw2.update(kw); Pv = E.params(**kw2)
    per = []
    for s in range(16):
        jobs = [(Pv, a, b, s, 0.08, 0.3) for h in (250, 500, 750) for (a, b) in V.starts(m, h, 3)]
        with ProcessPoolExecutor(4) as ex:
            outs = list(ex.map(V._job, jobs, chunksize=64))
        r = V.agg(outs)
        per.append((r["pay"], r["bust"], r["net"], r["s5"], r["s8"], r["mx"]))
    per = np.array(per)
    mu = per.mean(0); sd = per.std(0, ddof=1)
    out[lbl] = dict(mean=mu.tolist(), sd=sd.tolist())
    print(f"{lbl}: Ausz {mu[0]:.2f} (SD {sd[0]:.2f}, SE {sd[0]/4:.3f}) | Busts {mu[1]:.3f} (SD {sd[1]:.3f}, SE {sd[1]/4:.3f}) | Netto {mu[2]:.0f} (SD {sd[2]:.0f}) | S5 {mu[3]:.2f} (SD {sd[3]:.2f}) | S8 {mu[4]:.2f} (SD {sd[4]:.2f}) | maxS {mu[5]:.2f}", flush=True)
json.dump(out, open("streuung.json", "w"), indent=1)
