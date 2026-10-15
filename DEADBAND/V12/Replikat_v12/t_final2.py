import numpy as np, pickle
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
Pv = E.params()
SEEDS = tuple(range(1, 33))
base = V.evaluate_seeds(Pv, C.gp_v10(sr_risk=0.10), seeds=SEEDS)
print(V.paired(base, base, "V10 SR 0.10 (32 Seeds)"), flush=True)
out = {"V10": base}
for risk in (0.15, 0.20, 0.25, 0.30, 0.35):
    r = V.evaluate_seeds(Pv, C.gp_v10(sr_risk=risk), seeds=SEEDS); lab = f"SR {risk:.2f}"
    print(V.paired(base, r, lab), flush=True); out[lab] = r
pickle.dump(out, open("ergebnisse/t_final2.pkl", "wb"))
