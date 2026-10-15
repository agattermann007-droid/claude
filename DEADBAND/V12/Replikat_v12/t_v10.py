"""Abgleich: V8 (8.10) gegen V10 (SR 0,10 %) - rollierende 1-Jahres-Konten, Premium-Regeln."""
import time, json, numpy as np
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals()
m = V.mk()
m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
Pv = E.params()
res = {}
for lab, GP in (("V8", C.gp_v8()), ("V10", C.gp_v10())):
    t = time.time()
    r = V.evaluate(Pv, GP, by_year=True)
    res[lab] = {k: v for k, v in r.items() if k != "_rows"}
    for w in V.WIN:
        print(V.line(f"{lab} {w}", r[w]), flush=True)
        print("     ", V.mods_line(r[w]), flush=True)
    for y, a in r["jahre"].items():
        print(V.line(f"{lab} Start {y}", a), flush=True)
    print(f"[{time.time()-t:.0f}s]", flush=True)
json.dump(res, open("ergebnisse/t_v10.json", "w"), indent=1, default=float)
