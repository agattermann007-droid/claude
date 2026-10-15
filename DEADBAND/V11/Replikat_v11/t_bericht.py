"""Kennzahlen fuer den Bericht: V8, V10 (= V11 Voreinstellung) und die beiden V11-Testschalter, 16 Stoerungs-Seeds, je Fenster und Startjahr."""
import numpy as np, json
import cfg11 as C, evl11 as V, eng11 as E, cand11 as K, gen11 as G
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
Pv = E.params(); SEEDS = tuple(range(1, 17))
base_blocks = C.blocks(S)
live_at = G.portfolio_guard(S["fades"])
res = {}
def run(lab, blocks, GP, P=Pv):
    m.set_generic(blocks)
    r = V.evaluate(P, GP, seeds=SEEDS, by_year=True)
    res[lab] = {k: v for k, v in r.items() if k != "_rows"}
    for w in V.WIN:
        print(V.line(f"{lab} {w}", r[w]), flush=True)
    for y, a in r["jahre"].items():
        print(V.line(f"{lab} Start {y}", a), flush=True)
run("V8", base_blocks, C.gp_v8())
run("V10", base_blocks, C.gp_v10())
names = ["N1030", "N1100"]
tb = [(s_, K.tick_fade(C.STREAMS[s_], live_at=live_at), 1.0) if C.STREAMS[s_] in names else (s_, b, w) for (s_, b, w) in base_blocks]
GP = C.gp_v10()
for nm in names: GP[C.STREAMS.index(nm), E.GPI["tpdelay"]] = 4
run("V11 TickFades", tb, GP)
run("V11 GoldPdf", base_blocks + [(18, K.cand_block("GPDF", w0=-330, sb=0.15), 1.0)],
    C.gp_v10(extra=[dict(on=1, risk=0.25, maxtrades=1, harv=1, tpdelay=4, minsprd=6)]))
run("V10 ohne Schlupf", base_blocks, C.gp_v10(), E.params(slip=0.0))
run("V8 ohne Schlupf", base_blocks, C.gp_v8(), E.params(slip=0.0))
json.dump(res, open("ergebnisse/t_bericht.json", "w"), indent=1, default=float)
