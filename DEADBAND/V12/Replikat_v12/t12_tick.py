"""v12 / Prompt 9.5: Tick-Fades nachbessern. Gepaart gegen V10 (32 Seeds, 5 Fenster inkl. 2011-15).

Varianten: N1030+N1100 im Tick (wie V11TickFades) mit 0,75 % und 0,50 %; nur N1030 im Tick mit 0,75 % und 0,50 %.
Tick-Block ersetzt den M5-Block (nur bei live Portfolio-Waechter, wie V11). Ziel ab der 4. Minute (130 s).
"""
import x12  # noqa: F401
import pickle, sys, numpy as np
import cfg11 as C, evl11 as V, eng11 as E, gen11 as G, cand11 as K

S = C.signals()
m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
live_at = G.portfolio_guard(S["fades"])
Pv = E.params()
SEEDS = tuple(range(1, 33))
base = pickle.load(open("ergebnisse/base_v10_32.pkl", "rb"))
TB = {nm: K.tick_fade(nm, live_at=live_at) for nm in ("N1030", "N1100")}


def variant(names, risk):
    blks = [(s_, TB[C.STREAMS[s_]], 1.0) if C.STREAMS[s_] in names else (s_, b, w) for (s_, b, w) in C.blocks(S)]
    m.set_generic(blks)
    GP = C.gp_v10()
    for nm in names:
        GP[C.STREAMS.index(nm), E.GPI["tpdelay"]] = 4
        GP[C.STREAMS.index(nm), E.GPI["risk"]] = risk
    return GP


out = {}
for names, risk in ((("N1030", "N1100"), 0.75), (("N1030", "N1100"), 0.50), (("N1030",), 0.75), (("N1030",), 0.50),
                    (("N1100",), 0.75)):
    GP = variant(names, risk)
    lab = f"Tick {'+'.join(names)} {risk:.2f}%"
    r = V.evaluate_seeds(Pv, GP, seeds=SEEDS, windows=V.WIN5)
    out[lab] = r
    print(V.paired(base, r, lab), flush=True)
pickle.dump(out, open("ergebnisse/t12_tick.pkl", "wb"))

# Bust-Ursachen der besten Variante (N1030+N1100 0,75 %), alle Fenster, je Seed: Zeitpunkt und letzte Trades
GP = variant(("N1030", "N1100"), 0.75)
V.reset_seed_cache(); V._apply_seed(m, 0)
seen = set()
for sd in range(1, 17):
    V._apply_seed(m, sd)
    for w, (lo, hi) in V.WIN5.items():
        for (a, b) in V.starts(m, lo, hi):
            r = m.run(Pv, GP, a, b)
            for row in r["ev"][r["ev"][:, 0] == 2]:
                p = int(row[4]); key = (p, int(row[3]))
                if key in seen:
                    continue
                seen.add(key)
                print("seed", sd, w, "Bust", np.datetime64(int(m.ev_t[p]), "m"), "Typ", int(row[3]), "Saldo-Start",
                      round(row[2]), flush=True)
                tr = r["tr"]; day = int(row[1])
                for t in tr[(tr[:, 0] >= day - 2)][-8:]:
                    print("   tr", np.datetime64(int(t[0]), "D"), round(t[1], 1), "slot", int(t[2]), "str",
                          C.STREAMS[int(t[4])] if t[4] >= 0 else int(t[4]), np.datetime64(int(t[3]), "m"), flush=True)
