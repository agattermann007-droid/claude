"""Konto: K1gn mit schwaecher gewichteten NAS-Signalen ohne Kreuz (r21_first_mult) und weitere Varianten.
Aufruf: python a3_konto.py gft|ext faktor [schluessel=wert ...]"""
import sys, os, json, time
import r7konto as K, evl6 as V, r7sig as G, r7kand as KD
target = sys.argv[1]; fak = float(sys.argv[2])
kw = {}
for a in sys.argv[3:]:
    k, v = a.split("="); kw[k] = float(v)
D, S, blks = K.dataset(target)
C = G.features(D)
p = KD.k1gn(C)
r21 = G.r21_dict_weak(C, p, KD.weak_nas_nocross(C))
t = time.time()
r = K.evaluate(target, r21=r21, kw=dict(kw, r21_first_mult=fak), quick=os.environ.get("VOLL") is None)
print(V.line(f"{target} K1gn NAS-ohne-Kreuz x{fak} " + " ".join(f"{k}={v:g}" for k, v in kw.items()), r), f"| r21 {r['mods']['r21']} [{time.time()-t:.0f}s]", flush=True)
