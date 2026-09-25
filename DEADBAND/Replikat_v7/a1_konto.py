"""Konto-Screening der RSI21-Kandidaten (Build 6.10 Ertrag, nur die RSI21-Signale getauscht).
Aufruf: python a1_konto.py gft|ext [Kandidat|Kandidat...] [schluessel=wert ...]  -> cache/a1_<ziel>.json"""
import sys, json, os, time
import numpy as np
import r7konto as K, evl6 as V, r7sig as G, r7kand as KD

target = sys.argv[1]
names = sys.argv[2].split("|") if len(sys.argv) > 2 and sys.argv[2] != "alle" else list(KD.KAND)
kw = {}
for a in sys.argv[3:]:
    k, v = a.split("=")
    kw[k] = float(v)
out_f = os.path.join(K.HERE, "cache", f"a1_{target}{os.environ.get('VOLL', '')}.json")
res = json.load(open(out_f)) if os.path.exists(out_f) else {}
D, S, blks = K.dataset(target)
C = G.features(D)
for nm in names:
    lbl = nm + ("" if not kw else " " + " ".join(f"{k}={v:g}" for k, v in kw.items()))
    t = time.time()
    p = KD.KAND[nm](C)
    r21 = G.r21_dict(C, p)
    r = K.evaluate(target, r21=r21, kw=kw, quick=os.environ.get("VOLL") is None)
    res[lbl] = r
    json.dump(res, open(out_f, "w"), indent=1, default=float)
    print(V.line(f"{target} {lbl}", r), f"| gueltig/J {r['valid']:.1f} [{time.time()-t:.0f}s]", flush=True)
