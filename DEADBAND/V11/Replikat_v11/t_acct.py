"""Kontoebene: V10 + Kandidat (je Strom einzeln, Risiko 0,10/0,15/0,25 %) und Tick-Fades."""
import numpy as np, json, sys, time
import cfg11 as C, evl11 as V, eng11 as E, cand11 as K, gen11 as G
S = C.signals(); m = V.mk()
m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
Pv = E.params()
W = V.WIN
def show(lab, r):
    print(f"{lab:<26s} " + " | ".join(f"{w.split()[-1]} {r[w]['pay']:5.2f} {r[w]['net']:5.0f}$ B{r[w]['bust']}" for w in W), flush=True)
base_blocks = C.blocks(S)
m.set_generic(base_blocks)
ref = V.evaluate(Pv, C.gp_v10()); show("V10", ref)
res = {"V10": {w: ref[w] for w in W}}
live_at = G.portfolio_guard(S["fades"])
# --- Tick-Fades (ersetzen die M5-Version im selben Strom)
for names in (["N1030"], ["N1100"], ["N1800"], ["N1030", "N1100", "N1800"]):
    blks = []
    for (s_, b, w) in base_blocks:
        nm = C.STREAMS[s_]
        if nm in names:
            blks.append((s_, K.tick_fade(nm, live_at=live_at), 1.0))
        else:
            blks.append((s_, b, w))
    m.set_generic(blks)
    GP = C.gp_v10()
    for nm in names:
        GP[C.STREAMS.index(nm), E.GPI["tpdelay"]] = 4
    r = V.evaluate(Pv, GP); show("Tick " + "+".join(names), r)
    res["Tick " + "+".join(names)] = {w: r[w] for w in W}
# --- neue Stroeme einzeln
for nm in K.CANDS:
    b = K.cand_block(nm)
    m.set_generic(base_blocks + [(18, b, 1.0)])
    for risk in (0.10, 0.15, 0.25):
        GP = C.gp_v10(extra=[dict(on=1, risk=risk, maxtrades=1, harv=1, tpdelay=4, minsprd=6)])
        r = V.evaluate(Pv, GP); show(f"+{nm} {risk:.2f}", r)
        res[f"+{nm} {risk:.2f}"] = {w: r[w] for w in W}
json.dump(res, open("ergebnisse/t_acct.json", "w"), indent=1, default=float)
