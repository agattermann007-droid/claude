"""Robustheit: Kennzahlen je Startjahr (1-Jahres-Laeufe) und je Teilzeitraum (vor/nach dem NAS-Datenloch 2024)."""
import numpy as np, json, os
from concurrent.futures import ProcessPoolExecutor
import eng5 as E, evl5 as V, batch as B


def per_start_year(kw, seeds=tuple(range(16)), skip=0.08, slip=0.3, horizon=250, step=3):
    m = V.mk()
    kw2 = dict(B.SAFE); kw2.update(kw)
    Pv = E.params(**kw2)
    jobs = []
    for (a, b) in V.starts(m, horizon, step):
        for s in seeds:
            jobs.append((Pv, a, b, s, skip, slip))
    with ProcessPoolExecutor(4) as ex:
        outs = list(ex.map(V._job, jobs, chunksize=64))
    by = {}
    for j, o in zip(jobs, outs):
        y = str(np.datetime64(int(m.days[j[1]]), "D"))[:4]
        by.setdefault(y, []).append(o)
    return {y: V.agg(rows) for y, rows in sorted(by.items())}


def show(label, res):
    print(f"== {label}")
    for y, r in res.items():
        print(f"   Start {y}: Ausz/J {r['pay']:5.2f}  Busts/J {r['bust']:4.2f}  Netto/J {r['net']:6.0f}  S5/J {r['s5']:4.1f}  S8/J {r['s8']:4.2f}  "
              f"maxS {r['mx']:4.1f}  Luecke {r['gapmax']:5.1f}  P(Bust) {r['p_bust']:4.2f}  n={r['n']}")
