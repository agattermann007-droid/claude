"""Laeufer fuer die neuen Anforderungen: 10 Ausz/J, jede >= 3 % (300 $), 0 Busts, keine Serie > 5."""
import json, os, time, numpy as np
import eng6 as E, evl6 as V, batch as B

SAFE = dict(B.SAFE)
P50 = dict(db_tp1r=1.5, db_be=0.05, db_tp1f=0.5)
C510 = dict(P50, r21_risk=0.63, nz_risk=0.45, ge_mode=1, bank_on=1, bank_last=2, bank_minr=0.5, bank_mods=1,
            cool_n=4, cool_days=0, idea_cap=1.25)
PAY3 = dict(minpayout=240.0)          # Gewinn >= 300 $ = 3 % vor der Auszahlung
OFF_OLD = dict(db_on=0, r21_on=0, nz_on=0)


def ok_line(m):
    f = []
    f.append("Ausz>=10 " + ("JA" if m["pay"] >= 10 else "nein"))
    f.append("min>=300 " + ("JA" if m["paymin"] >= 299.9 else "nein"))
    f.append("Bust0 " + ("JA" if m["bust"] == 0 else "nein"))
    f.append("Serie<=5 " + ("JA" if m["mxmax"] <= 5 else "nein"))
    return " | ".join(f)


def run(configs, outfile, seeds=tuple(range(8)), skip=0.03, horizons=(250, 500, 750), step=3, quiet=False, end=None):
    res = json.load(open(outfile)) if os.path.exists(outfile) else {}
    for lbl, kw, GP in configs:
        if lbl in res:
            if not quiet:
                print(V.line(lbl, res[lbl]["mean"]), "(Cache)", flush=True)
            continue
        kw2 = dict(SAFE); kw2.update(kw)
        t = time.time()
        r = V.evaluate(E.params(**kw2), GP=GP, horizons=horizons, step=step, seeds=seeds, skip=skip, end=end)
        res[lbl] = dict(kw=kw2, GP=GP.tolist(), mean=r["mean"], by={str(h): {k: v for k, v in r[h].items()} for h in horizons if h in r})
        json.dump(res, open(outfile, "w"), indent=1, default=float)
        print(V.line(lbl, r["mean"]), f"[{time.time()-t:.0f}s]", flush=True)
    return res
