"""Endbewertung Build 6.20 (RSI21: Volumen-Bestaetigung 1,5 x Mittel(50), Gold-Faktor 0,5, Risiko 0,6 %) gegen 6.10.
Konto wie x39 (Ertrag): gft = Ersatz-GFT 2022-2025 (16 Stoerungen, rollierend 1/2/3 J, mit Startjahren),
ext = Fremddaten 2006-2021 (8 Stoerungen). Dazu RSI21 allein (ohne Konto) je Epoche. -> ../Replikat_v7/ergebnisse/e1.json"""
import os, sys, json
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import r7konto as K, evl6 as V, eng6 as E, r6, r7sig as G, r7kand as KD

CFG = {
    "6.10 Ertrag": ("Basis", {}),
    "6.20 Ertrag": ("Volumen 1.5", dict(r21_goldmult=0.5, r21_risk=0.6)),
}
OUT = os.path.join(K.HERE, "ergebnisse")
os.makedirs(OUT, exist_ok=True)


def konto(target):
    D, S, blks = K.dataset(target)
    C = G.features(D)
    res = {}
    for lbl, (cand, kw) in CFG.items():
        r21 = G.r21_dict(C, KD.KAND[cand](C))
        if target == "ext":
            r = K.evaluate(target, r21=r21, kw=kw, seeds=tuple(range(8)))
            res[lbl] = r
            print(V.line(f"{target} {lbl}", r), flush=True)
            continue
        # gft wie x39: 16 Stoerungen, Startjahre der 1-Jahres-Konten
        S2 = dict(S); S2["r21"] = r21
        V._MK = E.Market(D=D, S=S2)
        GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **K.GPX) for _ in K.F10])
        V.set_generic(blks, GP)
        Pv = E.params(**dict(r6.SAFE, **dict(K.ERTRAG, **kw)))
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
        print(V.line(f"{target} {lbl}", mean), flush=True)
        per = []
        for s in range(16):
            hs = [V.agg([o for (h, s2, a), o in zip(tags, outs) if h == hh and s2 == s]) for hh in (250, 500, 750)]
            per.append([np.mean([x[k] for x in hs]) for k in ("pay", "bust", "net")])
        per = np.array(per)
        mean["streuung"] = dict(mean=per.mean(0).tolist(), sd=per.std(0, ddof=1).tolist())
        print(f"     Streuung ueber 16 Stoerungen: Ausz {per[:, 0].mean():.2f} (SD {per[:, 0].std(ddof=1):.2f}) Busts {per[:, 1].mean():.3f} (SD {per[:, 1].std(ddof=1):.3f})", flush=True)
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
            print(f"     Start {y}: Ausz {a['pay']:5.2f} Bust {a['bust']:5.3f} Netto {a['net']:5.0f} S6 {a['s6']:4.2f} maxS {a['mx']:4.1f}/{a['mxmax']:.0f}", flush=True)
        res[lbl] = mean
    return res


def allein():
    """RSI21 ohne Konto (2006-2025, Fremddaten): Kennzahlen je Epoche."""
    from r7lab import run, C
    out = {}
    for lbl, (cand, kw) in CFG.items():
        gm = kw.get("r21_goldmult", 0.7)
        A, m = run(lbl, KD.KAND[cand](C), gold_mult=gm, show=True)
        out[lbl] = {k: v for k, v in m.items()}
    return out


if __name__ == "__main__":
    res = {"allein": allein(), "gft": konto("gft"), "ext": konto("ext")}
    json.dump(res, open(os.path.join(OUT, "e1.json"), "w"), indent=1, default=float)
