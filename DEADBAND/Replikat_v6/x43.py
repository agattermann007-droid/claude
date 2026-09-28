"""Endbewertung Build 6.30 (Trefferquote) mit eng7 - wie x41: 16 Stoerungen, 1/2/3 Jahre, Startjahre (1-Jahres-Konten),
Streuung je Stoerung, Waechter EA-getreu (600 Tage), Grid-Regel S wie 6.20 (N1800 ohne Grid).
Varianten: 6.20 (Basis, mit eng7 neu gerechnet), 6.30 = Stop auf Einstand fuer Noise und RSI21 ab 1 R, Fade-Teilgewinn
50 % bei 0,5 R bzw. 0,6 R, Alternativen mit hoeherer Trefferquote; Sicher mit Fade-Teilgewinn.
Aufruf: python x43.py gft|ext   (Ausgabe ergebnisse/x43_{gft|ext}.json, Ordner ueber X43_OUT)"""
import numpy as np, sys, json, os
import eng7 as E, evl6 as V, r6, x40, x42
from concurrent.futures import ProcessPoolExecutor

V.E = E
ERT, SIC, H = x42.ERT, x42.SIC, x42.H
NR = dict(nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05)          # Noise und RSI21: Einstand ab 1 R
CFG = {
    "6.20 Ertrag": (ERT, H),
    "6.30 Ertrag (N+R Einstand, F T1 0,5 R)": (dict(ERT, **NR), dict(H, tp1r=0.5, tp1f=0.5)),
    "6.30 Ertrag, F T1 0,6 R": (dict(ERT, **NR), dict(H, tp1r=0.6, tp1f=0.5)),
    "6.30 Ertrag, nur N+R Einstand": (dict(ERT, **NR), H),
    "6.30 Ertrag, F Einstand 0,75 R": (dict(ERT, **NR), dict(H, tp1r=0.75, be=0.05)),
    "Treffer: N TP 1 R, R T1+Einstand, F T1+Einstand": (dict(ERT, nz_tp=1.0, r21_tp1r=1.0, r21_tp1f=0.5, r21_be=0.05),
                                                        dict(H, tp1r=0.5, tp1f=0.5, be=0.05)),
    "6.20 Sicher": (SIC, {}),
    "6.30 Sicher (F T1 0,5 R)": (SIC, dict(tp1r=0.5, tp1f=0.5)),
    "6.30 Sicher, F T1 70 % Zielweg": (SIC, dict(tp1r=-0.7, tp1f=0.5)),
    "6.30 Sicher, F T1 0,6 R": (SIC, dict(tp1r=0.6, tp1f=0.5)),
    "Sicher Treffer: F Einstand 0,4 R": (SIC, dict(tp1r=0.4, be=0.05)),
}

if __name__ == "__main__":
    target = sys.argv[1]
    step = 1 if target == "gft" else 3
    fn = os.path.join(os.environ.get("X43_OUT", "ergebnisse"), f"x43_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    blks, info, mk = x42.setup(target)
    for lbl, (kw, gpx) in CFG.items():
        if lbl in res:
            print(V.line(f"{target} {lbl}"[:34], res[lbl]), "(Cache)", flush=True)
            continue
        V._MK = mk
        GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **gpx) for _ in x40.F10])
        V.set_generic(blks, GP)
        Pv = E.params(**dict(r6.SAFE, **kw))
        if target == "ext":
            warm, end, skip = "2006-09-01", "2021-12-31", 0.03
        else:
            warm, end, skip = V.WARM, None, 0.08
        hz = (250, 500, 750)
        jobs = []; tags = []
        for h in hz:
            for (a, b) in V.starts(mk, h, step, warm, end):
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
        print(V.line(f"{target} {lbl}"[:34], mean), f"| gueltig/J {mean['valid']:.1f}", flush=True)
        per = []
        for s in range(16):
            hs = [V.agg([o for (h, s2, a), o in zip(tags, outs) if h == hh and s2 == s]) for hh in hz]
            per.append([np.mean([x[k] for x in hs]) for k in ("pay", "bust", "net", "s5", "s6", "mx", "wr")])
        per = np.array(per); mu = per.mean(0); sd = per.std(0, ddof=1)
        mean["streuung"] = dict(mean=mu.tolist(), sd=sd.tolist(), keys=["pay", "bust", "net", "s5", "s6", "mx", "wr"])
        print(f"     Streuung: Ausz {mu[0]:.2f} (SD {sd[0]:.2f}) | Busts {mu[1]:.3f} (SD {sd[1]:.3f}) | Netto {mu[2]:.0f} (SD {sd[2]:.0f}) "
              f"| WR {mu[6]:.1f} (SD {sd[6]:.2f})", flush=True)
        by = {}
        for (h, s, a), o in zip(tags, outs):
            if h != 250:
                continue
            y = str(np.datetime64(int(mk.days[a]), "D"))[:4]
            by.setdefault(y, []).append(o)
        mean["jahre"] = {}
        for y, rows in sorted(by.items()):
            a = V.agg(rows)
            mean["jahre"][y] = {k: a[k] for k in ("pay", "paymean", "bust", "net", "s6", "mx", "mxmax", "wr")}
            print(f"     Start {y}: Ausz {a['pay']:5.2f} Bust {a['bust']:5.3f} Netto {a['net']:5.0f} S6 {a['s6']:4.2f} "
                  f"maxS {a['mx']:4.1f}/{a['mxmax']:.0f} WR {a['wr']:4.1f} n={a['n']}", flush=True)
        res[lbl] = mean
        json.dump(res, open(fn, "w"), indent=1, default=float)
