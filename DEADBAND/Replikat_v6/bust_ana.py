"""Build 6.50: Busts auf den Fremddaten je Variante: Datum (Monat), Art (1 Boden, 2 Floating, 3 Tagesverlust), Anzahl Konten.
Aufruf (in Replikat_v6): python bust_ana.py "Variante|Variante" [seeds] [step]"""
import sys, os, numpy as np, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eng9 as E, evl6 as V, r6, x48, x44
from concurrent.futures import ProcessPoolExecutor
names = sys.argv[1].split("|")
seeds = int(sys.argv[2]) if len(sys.argv) > 2 else 16
step = int(sys.argv[3]) if len(sys.argv) > 3 else 3
_P = {}
def job(args):
    a, b, seed = args
    m = V.mk(); P = _P["Pv"].copy()
    if seed > 0: P[E.PI["slip_frac"]] = 0.3
    ms = V.masks(m, seed, 0.03 if seed > 0 else 0.0)
    r = E.run(m, P, a, b, seed=seed, masks=ms, GP=_P["GP"])
    ev = r["ev"]
    return [(int(e[1]), int(e[3])) for e in ev if e[0] == 2.0], r["years"]
for name in names:
    v = x48.VAR[name]
    kw, gpx = v[0], v[1]; frisk = v[2]; rule = v[3]; per = v[4] if len(v) > 4 else None
    blks, info, mk = x44.setup("ext", rule)
    V._MK = mk
    GP = x48.fade_gp(gpx, frisk, per)
    V.set_generic(blks, GP)
    _P["Pv"] = E.params(**dict(r6.SAFE, **kw)); _P["GP"] = GP
    m = V.mk()
    jobs = [(a, b, s) for h in (250, 500, 750) for (a, b) in V.starts(m, h, step, "2006-09-01", "2021-12-31") for s in range(seeds)]
    with ProcessPoolExecutor(4) as ex:
        outs = list(ex.map(job, jobs, chunksize=32))
    Y = sum(o[1] for o in outs)
    cnt = collections.Counter(); art = collections.Counter()
    for bl, _ in outs:
        for d, t in bl:
            ym = str(np.datetime64(d, "D"))[:7]
            cnt[ym] += 1; art[t] += 1
    nb = sum(cnt.values())
    print(f"{name}: Busts {nb} in {Y:.0f} Konto-Jahren = {nb / Y:.3f}/J | Art Boden/Floating/Tag {art[1]}/{art[2]}/{art[3]}")
    print("   Monate:", " ".join(f"{k}:{v}" for k, v in sorted(cnt.items())))
