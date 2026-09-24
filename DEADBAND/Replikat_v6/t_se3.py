"""Streuung ueber die 16 Stoerungen (Seeds) fuer 6.00 Sicher / Ertrag (GFT 2022-26, wie x31)."""
import numpy as np, json, eng6 as E, evl6 as V, r6, streams as ST
from concurrent.futures import ProcessPoolExecutor
F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
gPF = ("pf", 30, 1.2)
B = dict(r6.C510, **r6.PAY3)
CFG = {
    "6.00 Sicher": (dict(B, db_on=0, r21_on=0, nz_on=0, gesamtbudget=0.9, idea_cap=0.9), F10, [0.75] * 10),
    "6.00 Ertrag": (dict(B, db_on=0, r21_risk=0.5, nz_risk=0.35, cool_n=3, gesamtbudget=0.9, idea_cap=0.9), F10, [0.75] * 10),
}
out = {}
for lbl, (kw, names, risks) in CFG.items():
    blks = ST.blocks(names, "gft", {n: gPF for n in names})
    GP = E.gparams([dict(on=1, risk=r, maxtrades=1) for r in risks])
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    m = V.mk()
    per = []
    for s in range(16):
        jobs = [(Pv, a, b, s, 0.08, 0.3, GP) for h in (250, 500, 750) for (a, b) in V.starts(m, h, 3)]
        with ProcessPoolExecutor(4) as ex:
            outs = list(ex.map(V._job, jobs, chunksize=32))
        r = V.agg(outs)
        per.append((r["pay"], r["bust"], r["net"], r["s5"], r["s6"], r["mx"]))
    per = np.array(per); mu = per.mean(0); sd = per.std(0, ddof=1)
    out[lbl] = dict(mean=mu.tolist(), sd=sd.tolist())
    print(f"{lbl}: Ausz {mu[0]:.2f} (SD {sd[0]:.2f}, SE {sd[0]/4:.3f}) | Busts {mu[1]:.3f} (SD {sd[1]:.3f}, SE {sd[1]/4:.3f}) | Netto {mu[2]:.0f} (SD {sd[2]:.0f}, SE {sd[2]/4:.0f}) | S5 {mu[3]:.2f} | S6 {mu[4]:.2f} (SD {sd[4]:.2f}) | maxS {mu[5]:.2f}", flush=True)
json.dump(out, open("se3.json", "w"), indent=1)
