"""Stapel-Laeufer: Konfigurationen rollierend bewerten, Ergebnisse als JSON sichern."""
import json, sys, time, os
import eng5 as E, evl5 as V

SAFE = dict(rule_losers=1, float_losers=1, swap_guard=0.8)      # strenge Lesart der Floating-Regel in jeder Bewertung


def run(configs, outfile, horizons=(250, 500, 750), step=3, seeds=tuple(range(8)), base=SAFE, quiet=False):
    res = {}
    if os.path.exists(outfile):
        res = json.load(open(outfile))
    for lbl, kw in configs:
        if lbl in res:
            m = res[lbl]["mean"]
            if not quiet:
                print(V.line(lbl, m), "(Cache)", flush=True)
            continue
        kw2 = dict(base); kw2.update(kw)
        t = time.time()
        r = V.evaluate(E.params(**kw2), horizons=horizons, step=step, seeds=seeds)
        res[lbl] = dict(kw=kw2, mean=r["mean"], by={str(h): r[h] for h in horizons})
        json.dump(res, open(outfile, "w"), indent=1)
        m = r["mean"]
        print(V.line(lbl, m), f"Bo/Fl/Tg {m['floor_b']:.2f}/{m['float_b']:.3f}/{m['day_b']:.3f} "
              f"DB {m['db_pnl']:5.0f} R21 {m['r21_pnl']:5.0f} NZ {m['nz_pnl']:5.0f} [{time.time()-t:.0f}s]", flush=True)
    return res
