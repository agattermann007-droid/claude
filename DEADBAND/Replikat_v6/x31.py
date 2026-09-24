"""Robuste Endbewertung (16 Stoerungen, 8 % ausgelassen) der beiden 6.00-Auspraegungen + 5.10 zum Vergleich, GFT 2022-26,
dazu Kennzahlen je Startjahr."""
import numpy as np, json, eng6 as E, evl6 as V, r6, streams as ST
from concurrent.futures import ProcessPoolExecutor
F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
gPF = ("pf", 30, 1.2)
B = dict(r6.C510, **r6.PAY3)
CFG = {
    "5.10 (Ausz >= 3 %)": (B, [], []),
    "6.00 Sicher": (dict(B, db_on=0, r21_on=0, nz_on=0, gesamtbudget=0.9, idea_cap=0.9), F10, [0.75] * 10),
    "6.00 Ertrag": (dict(B, db_on=0, r21_risk=0.5, nz_risk=0.35, cool_n=3, gesamtbudget=0.9, idea_cap=0.9), F10, [0.75] * 10),
}
out = {}
for lbl, (kw, names, risks) in CFG.items():
    blks = ST.blocks(names, "gft", {n: gPF for n in names}) if names else []
    GP = E.gparams([dict(on=1, risk=r, maxtrades=1) for r in risks])
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=3, seeds=tuple(range(16)), skip=0.08)
    print(V.line(lbl, r["mean"]), flush=True)
    m = V.mk()
    jobs = [(Pv, a, b, s, 0.08, 0.3, GP) for (a, b) in V.starts(m, 250, 3) for s in range(16)]
    with ProcessPoolExecutor(4) as ex:
        outs = list(ex.map(V._job, jobs, chunksize=32))
    by = {}
    for j, o in zip(jobs, outs):
        y = str(np.datetime64(int(m.days[j[1]]), "D"))[:4]
        by.setdefault(y, []).append(o)
    for y, rows in sorted(by.items()):
        a = V.agg(rows)
        print(f"     Start {y}: Ausz {a['pay']:5.2f} Ø{a['paymean']:4.0f}$ Bust {a['bust']:5.3f} Netto {a['net']:5.0f} S6 {a['s6']:4.2f} maxS {a['mx']:4.1f}/{a['mxmax']:.0f} n={a['n']}")
    out[lbl] = r["mean"]
json.dump(out, open("x31.json", "w"), indent=1, default=float)
