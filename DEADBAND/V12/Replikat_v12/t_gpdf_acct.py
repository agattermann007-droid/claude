import numpy as np, pickle
import cfg11 as C, evl11 as V, eng11 as E, cand11 as K
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
Pv = E.params(); base_blocks = C.blocks(S)
m.set_generic(base_blocks)
base = V.evaluate_seeds(Pv, C.gp_v10())
print(V.paired(base, base, "V10"), flush=True)
out = {"V10": base}
for w0, sb in ((-360, 0.15), (-345, 0.10), (-330, 0.10), (-330, 0.15)):
    b = K.cand_block("GPDF", w0=w0, sb=sb)
    m.set_generic(base_blocks + [(18, b, 1.0)])
    for risk in (0.15, 0.20, 0.25):
        GP = C.gp_v10(extra=[dict(on=1, risk=risk, maxtrades=1, harv=1, tpdelay=4, minsprd=6)])
        r = V.evaluate_seeds(Pv, GP); lab = f"GPDF w0{w0} sb{sb} r{risk:.2f}"
        print(V.paired(base, r, lab), flush=True); out[lab] = r
pickle.dump(out, open("ergebnisse/t_gpdf_acct.pkl", "wb"))
