"""v12: Grundlinie auf dem erweiterten Datensatz (5 Fenster inkl. Pruef 2011-15). Seed 0 mit Kennzahlen je Fenster und
Startjahr, dann V10 ueber 32 gepaarte Stoerungen (Basis fuer alle spaeteren Vergleiche, ergebnisse/base_v10_32.pkl)."""
import x12  # noqa: F401
import time, json, pickle, numpy as np
import cfg11 as C, evl11 as V, eng11 as E

S = C.signals()
m = V.mk()
m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
Pv = E.params()
res = {}
for lab, GP in (("V8", C.gp_v8()), ("V10", C.gp_v10())):
    t = time.time()
    r = V.evaluate(Pv, GP, windows=V.WIN5, by_year=True)
    res[lab] = {k: v for k, v in r.items() if k != "_rows"}
    for w in V.WIN5:
        print(V.line(f"{lab} {w}", r[w]), flush=True)
        print("     ", V.mods_line(r[w]), flush=True)
    for y, a in r["jahre"].items():
        print(V.line(f"{lab} Start {y}", a), flush=True)
    print(f"[{time.time()-t:.0f}s]", flush=True)
json.dump(res, open("ergebnisse/t12_base.json", "w"), indent=1, default=float)
t = time.time()
base = V.evaluate_seeds(Pv, C.gp_v10(), seeds=tuple(range(1, 33)), windows=V.WIN5)
pickle.dump(base, open("ergebnisse/base_v10_32.pkl", "wb"))
print(V.paired(base, base, "V10 (32 Seeds)"), f"[{time.time()-t:.0f}s]", flush=True)
v8 = V.evaluate_seeds(Pv, C.gp_v8(), seeds=tuple(range(1, 33)), windows=V.WIN5)
print(V.paired(base, v8, "V8 gegen V10"), flush=True)
