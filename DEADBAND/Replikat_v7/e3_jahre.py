"""6.10 gegen 6.20 je Startjahr (1-Jahres-Konten) auf den Fremddaten 2006-2021 (8 Stoerungen). -> ergebnisse/e3.json"""
import os, json
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import r7konto as K, evl6 as V, eng6 as E, r6, r7sig as G, r7kand as KD
from e1_final import CFG, OUT

D, S, blks = K.dataset("ext")
C = G.features(D)
res = {}
for lbl, (cand, kw) in CFG.items():
    S2 = dict(S); S2["r21"] = G.r21_dict(C, KD.KAND[cand](C))
    V._MK = E.Market(D=D, S=S2)
    GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **K.GPX) for _ in K.F10])
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **dict(K.ERTRAG, **kw)))
    m = V.mk()
    st = V.starts(m, 250, 9, "2006-09-01", "2021-12-31")
    jobs = [(Pv, a, b, s, 0.08, 0.3, GP) for (a, b) in st for s in range(8)]
    with ProcessPoolExecutor(4) as ex:
        outs = list(ex.map(V._job, jobs, chunksize=32))
    by = {}
    for (Pv_, a, b, s, *_), o in zip(jobs, outs):
        by.setdefault(str(np.datetime64(int(m.days[a]), "D"))[:4], []).append(o)
    res[lbl] = {}
    for y, rows in sorted(by.items()):
        a = V.agg(rows)
        res[lbl][y] = {k: a[k] for k in ("pay", "bust", "net", "s6", "mx")}
        print(f"{lbl} Start {y}: Ausz {a['pay']:5.2f} Bust {a['bust']:5.3f} Netto {a['net']:5.0f}", flush=True)
json.dump(res, open(os.path.join(OUT, "e3.json"), "w"), indent=1, default=float)
a, b = res["6.10 Ertrag"], res["6.20 Ertrag"]
yrs = sorted(a)
print("Jahre mit mehr Auszahlungen:", sum(b[y]["pay"] > a[y]["pay"] for y in yrs), "von", len(yrs),
      "| weniger Busts:", sum(b[y]["bust"] < a[y]["bust"] for y in yrs), "| gleich viele Busts:", sum(b[y]["bust"] == a[y]["bust"] for y in yrs))
