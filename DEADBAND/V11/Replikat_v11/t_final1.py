import numpy as np, pickle
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
Pv = E.params()
v8 = V.evaluate_seeds(Pv, C.gp_v8())
print(V.paired(v8, v8, "V8 (8.10)"), flush=True)
out = {"V8": v8}
for risk in (0.05, 0.10, 0.15, 0.20):
    r = V.evaluate_seeds(Pv, C.gp_v10(sr_risk=risk)); lab = f"V10 SR {risk:.2f}"
    print(V.paired(v8, r, lab), flush=True); out[lab] = r
pickle.dump(out, open("ergebnisse/t_final1.pkl", "wb"))
