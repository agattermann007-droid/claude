"""6.00 nach dem Code-Review: Fade-Einstiege zusaetzlich ohne US-Feiertage/verkuerzte Tage (NZ_FREI + Sondertage) und nur mit
Stop >= 6 x Spread der Einstiegskerze. Waechter weiter auf ALLE virtuellen Signale. GFT 2022-26 (16 Stoerungen, wie x31, mit
Startjahren) oder Fremddaten 2006-21 (4 Stoerungen)."""
import numpy as np, sys, json, pickle, os, re, eng6 as E, evl6 as V, r6, streams as ST, prep5 as P, gsig as G
from concurrent.futures import ProcessPoolExecutor
F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
g = ("pf", 30, 1.2)
B = dict(r6.C510, **r6.PAY3)
MQ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DEADBAND_LIVE4.mq5")   # EA im Ordner darueber
src = open(MQ, encoding="utf-8").read()
frei_txt = src[src.index("string NZ_FREI[] ="):src.index("};", src.index("string NZ_FREI[] ="))]
sd_txt = re.search(r'input string WeSonderTage\s*=\s*"([^"]*)"', src).group(1)
FREI = set()
for dstr in re.findall(r"(\d{4})\.(\d{2})\.(\d{2})", frei_txt):
    FREI.add(int(np.datetime64("-".join(dstr), "D").astype(np.int64)))
for e in sd_txt.split(";"):
    e = e.strip()
    if not e: continue
    dstr, hh = e.split()
    if float(hh) * 60 < 955 + 5:
        FREI.add(int(np.datetime64(dstr.replace(".", "-"), "D").astype(np.int64)))
MINSP = 6.0
target = sys.argv[1]


def spread_at(dataset, sym, t_entry):
    D = (G._D if G._D is not None else G.data())[sym]
    i = np.searchsorted(D["ny"], t_entry)
    return D["sp"][np.minimum(i, len(D["sp"]) - 1)]


def blocks_filtered(names, target):
    out = ST.blocks(names, target, {n: g for n in names})
    ST._use(target)                                    # Kursdaten des Ziel-Datensatzes fuer den Spread
    res = []
    n0 = n1 = 0
    for blk, nm in zip(out, names):
        sym = ST.K.FADES[nm]["sym"]
        te = blk["t_entry"]; tx = blk["t_exit"]
        sp = spread_at(target, sym, te)
        keep = np.array([(int(a // 1440) not in FREI) and (int(b // 1440) not in FREI) for a, b in zip(te, tx)], bool)
        keep &= blk["rd"] >= MINSP * sp
        n0 += len(te); n1 += int(keep.sum())
        res.append({k: (v[keep] if isinstance(v, np.ndarray) and len(v) == len(keep) else v) for k, v in blk.items()})
    print(f"{target}: Fade-Einstiege nach Waechter {n0}, nach Feiertags-/Stop-Filter {n1} ({100.0 * (n0 - n1) / max(n0, 1):.1f} % weniger)", flush=True)
    return res


CFG = {
    "6.00 Sicher (Review)": (dict(B, db_on=0, r21_on=0, nz_on=0, gesamtbudget=0.9, idea_cap=0.9), [0.75] * 10),
    "6.00 Ertrag (Review)": (dict(B, db_on=0, r21_risk=0.5, nz_risk=0.35, cool_n=3, gesamtbudget=0.9, idea_cap=0.9), [0.75] * 10),
}
if target == "ext":
    V._MK = E.Market(D=pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb")), S=pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb")))
res = {}
blks = blocks_filtered(F10, target)
if target == "ext":
    V._MK = E.Market(D=pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb")), S=pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb")))
for lbl, (kw, risks) in CFG.items():
    GP = E.gparams([dict(on=1, risk=r, maxtrades=1) for r in risks])
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    if target == "ext":
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
    else:
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=3, seeds=tuple(range(16)), skip=0.08)
    res[lbl] = {k: v for k, v in r["mean"].items()}
    print(V.line(f"{target} {lbl}", r["mean"]), flush=True)
    if target != "ext":
        m = V.mk()
        jobs = [(Pv, a, b, s, 0.08, 0.3, GP) for (a, b) in V.starts(m, 250, 3) for s in range(16)]
        with ProcessPoolExecutor(4) as ex:
            outs = list(ex.map(V._job, jobs, chunksize=32))
        by = {}
        for j, o in zip(jobs, outs):
            y = str(np.datetime64(int(m.days[j[1]]), "D"))[:4]
            by.setdefault(y, []).append(o)
        res[lbl]["jahre"] = {}
        for y, rows in sorted(by.items()):
            a = V.agg(rows)
            res[lbl]["jahre"][y] = {k: a[k] for k in ("pay", "paymean", "bust", "net", "s6", "mx", "mxmax")}
            print(f"     Start {y}: Ausz {a['pay']:5.2f} Ø{a['paymean']:4.0f}$ Bust {a['bust']:5.3f} Netto {a['net']:5.0f} S6 {a['s6']:4.2f} maxS {a['mx']:4.1f}/{a['mxmax']:.0f} n={a['n']}", flush=True)
json.dump(res, open(f"x35_{target}.json", "w"), indent=1, default=float)
