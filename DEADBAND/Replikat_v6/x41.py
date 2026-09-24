"""Endbewertung Build 6.20 (Probability Grid, Regel S: M5, Laenge 15, 1000 Schenkel, Stop-Chance >= 70 % -> kein Fade gegen
den Lauf) gegen 6.10 - wie x39: 16 Stoerungen, 1/2/3 Jahre, Startjahre (1-Jahres-Konten), Streuung je Stoerung.
gft = GFT-Daten bzw. GFT-Ersatz (mk_proxy; hier jeden Handelstag ein neues Konto), ext = Fremddaten 2006-21 (16 Stoerungen,
jeder 3. Tag). Aufruf: python x41.py gft|ext"""
import numpy as np, sys, json, os
import eng6 as E, evl6 as V, r6, x40, pg_rules as RU
from concurrent.futures import ProcessPoolExecutor

S70 = RU.fade_filter(5, 15, 1000, RU.c_stop_survival(0.70))
S70_LIVE = RU.fade_filter(5, 15, 1000, RU.c_stop_survival(0.70), guard_all=True)
H = dict(harv=1)
CFG = {
    "6.10 Ertrag": (x40.ERT, H, RU.NONE),
    "6.20 Ertrag": (x40.ERT, H, S70),
    "6.20 Ertrag GridNurLive": (x40.ERT, H, S70_LIVE),
    "6.10 Sicher": (x40.SIC, {}, RU.NONE),
    "6.20 Sicher": (x40.SIC, {}, S70),
}

if __name__ == "__main__":
    target = sys.argv[1]
    step = 1 if target == "gft" else 3
    fn = os.path.join("ergebnisse", f"x41_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl, (kw, gpx, rule) in CFG.items():
        if lbl in res:
            print(V.line(f"{target} {lbl}", res[lbl]), "(Cache)", flush=True)
            continue
        blks, info = x40.PB.blocks(target, rule, info=True)
        V._MK = x40.market(target)
        GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **gpx) for _ in x40.F10])
        V.set_generic(blks, GP)
        Pv = E.params(**dict(r6.SAFE, **kw))
        m = V.mk()
        if target == "ext":
            warm, end, skip = "2006-09-01", "2021-12-31", 0.03
        else:
            warm, end, skip = V.WARM, None, 0.08
        hz = (250, 500, 750)
        jobs = []; tags = []
        for h in hz:
            for (a, b) in V.starts(m, h, step, warm, end):
                for s in range(16):
                    jobs.append((Pv, a, b, s, skip, 0.3, GP)); tags.append((h, s, a))
        with ProcessPoolExecutor(4) as ex:
            outs = list(ex.map(V._job, jobs, chunksize=32))
        byh = {}
        for (h, s, a), o in zip(tags, outs):
            byh.setdefault(h, []).append(o)
        agg = {h: V.agg(byh[h]) for h in byh}
        keys = [k for k in agg[250].keys() if k != "mods"]
        mean = {k: float(np.mean([agg[h][k] for h in agg])) for k in keys}
        mean["mxmax"] = float(max(agg[h]["mxmax"] for h in agg)); mean["p_bust1"] = agg[250]["p_bust"]; mean["mods"] = agg[250]["mods"]
        mean["fade_live"] = sum(x[2] for x in info)
        print(V.line(f"{target} {lbl}", mean), f"| gueltig/J {mean['valid']:.1f}", flush=True)
        per = []
        for s in range(16):
            hs = [V.agg([o for (h, s2, a), o in zip(tags, outs) if h == hh and s2 == s]) for hh in hz]
            per.append([np.mean([x[k] for x in hs]) for k in ("pay", "bust", "net", "s5", "s6", "mx")])
        per = np.array(per); mu = per.mean(0); sd = per.std(0, ddof=1)
        mean["streuung"] = dict(mean=mu.tolist(), sd=sd.tolist())
        print(f"     Streuung: Ausz {mu[0]:.2f} (SD {sd[0]:.2f}, SE {sd[0] / 4:.3f}) | Busts {mu[1]:.3f} (SD {sd[1]:.3f}) | Netto {mu[2]:.0f} (SD {sd[2]:.0f})", flush=True)
        by = {}
        for (h, s, a), o in zip(tags, outs):
            if h != 250:
                continue
            y = str(np.datetime64(int(m.days[a]), "D"))[:4]
            by.setdefault(y, []).append(o)
        mean["jahre"] = {}
        for y, rows in sorted(by.items()):
            a = V.agg(rows)
            mean["jahre"][y] = {k: a[k] for k in ("pay", "paymean", "bust", "net", "s6", "mx", "mxmax")}
            print(f"     Start {y}: Ausz {a['pay']:5.2f} Ø{a['paymean']:4.0f}$ Bust {a['bust']:5.3f} Netto {a['net']:5.0f} S6 {a['s6']:4.2f} maxS {a['mx']:4.1f}/{a['mxmax']:.0f} n={a['n']}", flush=True)
        res[lbl] = mean
        json.dump(res, open(fn, "w"), indent=1, default=float)
