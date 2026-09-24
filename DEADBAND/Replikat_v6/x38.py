"""Build 6.10 wie x37, aber gueltiger Tag erst ab 52 $ (0,5 % + 2 $ Reserve wie der EA, ValidDayReserveUSD)."""
import numpy as np, sys, json, os, pickle, eng6 as E, evl6 as V, r6, x35 as X, prep5 as P
from concurrent.futures import ProcessPoolExecutor
F10 = X.F10
B = dict(r6.C510, **r6.PAY3)
RES = 0.52
CFG = {
    "6.10 Ertrag": (dict(B, validpct=RES, db_on=0, r21_risk=0.5, nz_risk=0.35, cool_n=3, gesamtbudget=0.9, idea_cap=0.9,
                         bank_on=1, bank_last=3, bank_minr=0.3, bank_mods=15), dict(harv=1)),
    "6.10 Sicher": (dict(B, validpct=RES, db_on=0, r21_on=0, nz_on=0, gesamtbudget=0.9, idea_cap=0.9), {}),
}
if __name__ == "__main__":
    target = sys.argv[1]
    blks = X.blocks_filtered(F10, target)
    if target == "ext":
        V._MK = E.Market(D=pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb")), S=pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb")))
    res = {}
    for lbl, (kw, gpx) in CFG.items():
        GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **gpx) for _ in F10])
        V.set_generic(blks, GP)
        Pv = E.params(**dict(r6.SAFE, **kw))
        if target == "ext":
            r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
            res[lbl] = r["mean"]
            print(V.line(f"{target} {lbl}", r["mean"]), flush=True)
            continue
        m = V.mk()
        jobs = [(Pv, a, b, s, 0.08, 0.3, GP) for h in (250, 500, 750) for (a, b) in V.starts(m, h, 3) for s in range(16)]
        tags = [(h, s, a) for h in (250, 500, 750) for (a, b) in V.starts(m, h, 3) for s in range(16)]
        with ProcessPoolExecutor(4) as ex:
            outs = list(ex.map(V._job, jobs, chunksize=32))
        byh = {}
        for (h, s, a), o in zip(tags, outs):
            byh.setdefault(h, []).append(o)
        agg = {h: V.agg(byh[h]) for h in byh}
        keys = [k for k in agg[250].keys() if k != "mods"]
        mean = {k: float(np.mean([agg[h][k] for h in agg])) for k in keys}
        mean["mxmax"] = float(max(agg[h]["mxmax"] for h in agg)); mean["p_bust1"] = agg[250]["p_bust"]; mean["mods"] = agg[250]["mods"]
        res[lbl] = mean
        print(V.line(f"{target} {lbl}", mean), flush=True)
        # Streuung je Stoerung (alle Laufzeiten gemittelt)
        per = []
        for s in range(16):
            hs = [V.agg([o for (h, s2, a), o in zip(tags, outs) if h == hh and s2 == s]) for hh in (250, 500, 750)]
            per.append([np.mean([x[k] for x in hs]) for k in ("pay", "bust", "net", "s5", "s6", "mx")])
        per = np.array(per); mu = per.mean(0); sd = per.std(0, ddof=1)
        res[lbl]["streuung"] = dict(mean=mu.tolist(), sd=sd.tolist())
        print(f"     Streuung: Ausz {mu[0]:.2f} (SD {sd[0]:.2f}, SE {sd[0]/4:.3f}) | Busts {mu[1]:.3f} (SD {sd[1]:.3f}) | Netto {mu[2]:.0f} (SD {sd[2]:.0f})", flush=True)
        # Startjahre (1-Jahres-Konten)
        by = {}
        for (h, s, a), o in zip(tags, outs):
            if h != 250: continue
            y = str(np.datetime64(int(m.days[a]), "D"))[:4]
            by.setdefault(y, []).append(o)
        res[lbl]["jahre"] = {}
        for y, rows in sorted(by.items()):
            a = V.agg(rows)
            res[lbl]["jahre"][y] = {k: a[k] for k in ("pay", "paymean", "bust", "net", "s6", "mx", "mxmax")}
            print(f"     Start {y}: Ausz {a['pay']:5.2f} Ø{a['paymean']:4.0f}$ Bust {a['bust']:5.3f} Netto {a['net']:5.0f} S6 {a['s6']:4.2f} maxS {a['mx']:4.1f}/{a['mxmax']:.0f} n={a['n']}", flush=True)
    json.dump(res, open(f"x38_{target}.json", "w"), indent=1, default=float)
