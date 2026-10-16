"""v12: Endauswertung V10 (= V11 Voreinstellung) gegen V12 (N1030 im Tick, 0,50 %, M5-N1030 nur virtuell).

1) Kennzahlen je Fenster und je Startjahr, gemittelt ueber 16 Stoerungen (Seeds 1-16)
2) gepaart, 32 Stoerungen, 5 Fenster
3) Sensitivitaet ohne Schlupf (slip 0), gepaart, 16 Stoerungen
Ausgabe: ergebnisse/t12_final.log / .json
"""
import x12  # noqa: F401
import json, pickle
import cfg11 as C, evl11 as V, eng11 as E, gen11 as G, cand11 as K

S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
live_at = G.portfolio_guard(S["fades"])
I = C.STREAMS.index("N1030")
TB = K.tick_fade("N1030", live_at=live_at)


def setup(v12):
    if v12:
        m.set_generic([(s_, TB, 1.0) if s_ == I else (s_, b, w) for (s_, b, w) in C.blocks(S)])
        GP = C.gp_v10(); GP[I, E.GPI["risk"]] = 0.50; GP[I, E.GPI["tpdelay"]] = 4
    else:
        m.set_generic(C.blocks(S)); GP = C.gp_v10()
    return GP


res = {}
for lab, v12 in (("V10", False), ("V12", True)):
    GP = setup(v12)
    r = V.evaluate(E.params(), GP, windows=V.WIN5, by_year=True, seeds=tuple(range(1, 17)))
    res[lab] = {k: v for k, v in r.items() if k != "_rows"}
    for w in V.WIN5:
        print(V.line(f"{lab} {w}", r[w]), flush=True)
    for y, a in r["jahre"].items():
        print(V.line(f"{lab} Start {y}", a), flush=True)
json.dump(res, open("ergebnisse/t12_final.json", "w"), indent=1, default=float)

base = pickle.load(open("ergebnisse/base_v10_32.pkl", "rb"))
GP = setup(True)
r32 = V.evaluate_seeds(E.params(), GP, seeds=tuple(range(1, 33)), windows=V.WIN5)
print(V.paired(base, r32, "V12 gegen V10 (32 Seeds)"), flush=True)
pickle.dump(r32, open("ergebnisse/v12_32.pkl", "wb"))

P0 = E.params(slip=0.0)
S16 = tuple(range(1, 17))
b0 = V.evaluate_seeds(P0, setup(False), seeds=S16, windows=V.WIN5)
v0 = V.evaluate_seeds(P0, setup(True), seeds=S16, windows=V.WIN5)
print(V.paired(b0, b0, "V10 ohne Schlupf"), flush=True)
print(V.paired(b0, v0, "V12 ohne Schlupf"), flush=True)
