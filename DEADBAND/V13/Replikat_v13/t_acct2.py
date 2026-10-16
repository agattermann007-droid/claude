"""Kontoebene, gepaart ueber 16 Stoerungs-Seeds: V10 + Kandidaten. Differenz zu V10 +- Standardfehler."""
import numpy as np, json, pickle
import cfg11 as C, evl11 as V, eng11 as E, cand11 as K, gen11 as G
S = C.signals(); m = V.mk()
m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
Pv = E.params()
base_blocks = C.blocks(S)
m.set_generic(base_blocks)
base = V.evaluate_seeds(Pv, C.gp_v10())
print(V.paired(base, base, "V10"), flush=True)
out = {"V10": base}
live_at = G.portfolio_guard(S["fades"])
for names in (["N1030"], ["N1100"], ["N1800"], ["N1030", "N1100"], ["N1030", "N1100", "N1800"]):
    blks = [(s_, K.tick_fade(C.STREAMS[s_], live_at=live_at), 1.0) if C.STREAMS[s_] in names else (s_, b, w) for (s_, b, w) in base_blocks]
    m.set_generic(blks)
    GP = C.gp_v10()
    for nm in names:
        GP[C.STREAMS.index(nm), E.GPI["tpdelay"]] = 4
    r = V.evaluate_seeds(Pv, GP); lab = "Tick " + "+".join(names)
    print(V.paired(base, r, lab), flush=True); out[lab] = r
for nm in K.CANDS:
    b = K.cand_block(nm)
    m.set_generic(base_blocks + [(18, b, 1.0)])
    for risk in (0.10, 0.20):
        GP = C.gp_v10(extra=[dict(on=1, risk=risk, maxtrades=1, harv=1, tpdelay=4, minsprd=6)])
        r = V.evaluate_seeds(Pv, GP); lab = f"+{nm} {risk:.2f}"
        print(V.paired(base, r, lab), flush=True); out[lab] = r
pickle.dump(out, open("ergebnisse/t_acct2.pkl", "wb"))
