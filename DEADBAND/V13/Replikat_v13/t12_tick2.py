"""v12: Bestaetigung N1030 im Tick mit 0,50 % - Nachbarn (Risiko 0,40/0,60 %, Stop-Puffer 0,2/0,4 x Range) und
Gegenprobe N1030 auf M5 mit 0,50 % (kommt der Vorteil vom Tick-Einstieg oder nur vom kleineren Risiko?). 32 Seeds."""
import x12  # noqa: F401
import pickle
import cfg11 as C, evl11 as V, eng11 as E, gen11 as G, cand11 as K
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
live_at = G.portfolio_guard(S["fades"])
Pv = E.params()
base = pickle.load(open("ergebnisse/base_v10_32.pkl", "rb"))
I = C.STREAMS.index("N1030")


def run(lab, tick=True, risk=0.5, buf=None):
    blks = C.blocks(S)
    if tick:
        tb = K.tick_fade("N1030", live_at=live_at, buf_over=buf)
        blks = [(s_, tb, 1.0) if s_ == I else (s_, b, w) for (s_, b, w) in blks]
    m.set_generic(blks)
    GP = C.gp_v10()
    GP[I, E.GPI["risk"]] = risk
    if tick:
        GP[I, E.GPI["tpdelay"]] = 4
    r = V.evaluate_seeds(Pv, GP, seeds=tuple(range(1, 33)), windows=V.WIN5)
    print(V.paired(base, r, lab), flush=True)
    return r


out = {}
out["M5 0.50"] = run("N1030 M5 0.50% (Gegenprobe)", tick=False, risk=0.5)
for rk in (0.40, 0.60):
    out[f"Tick {rk}"] = run(f"N1030 Tick {rk:.2f}%", risk=rk)
for bf in (0.2, 0.4):
    out[f"Tick 0.50 buf{bf}"] = run(f"N1030 Tick 0.50% Puffer {bf}", buf=bf)
pickle.dump(out, open("ergebnisse/t12_tick2.pkl", "wb"))
