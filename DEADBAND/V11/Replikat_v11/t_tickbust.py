import numpy as np
import cfg11 as C, evl11 as V, eng11 as E, cand11 as K, gen11 as G
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
live_at = G.portfolio_guard(S["fades"])
names = ["N1030", "N1100"]
blks = [(s_, K.tick_fade(C.STREAMS[s_], live_at=live_at), 1.0) if C.STREAMS[s_] in names else (s_, b, w) for (s_, b, w) in C.blocks(S)]
m.set_generic(blks)
GP = C.gp_v10()
for nm in names: GP[C.STREAMS.index(nm), E.GPI["tpdelay"]] = 4
Pv = E.params()
V.reset_seed_cache(); V._apply_seed(m, 0)
seen = set()
for sd in range(1, 17):
    V._apply_seed(m, sd)
    for (a, b) in V.starts(m, "2024-01-01", "2025-02-13"):
        r = m.run(Pv, GP, a, b)
        for row in r["ev"][r["ev"][:, 0] == 2]:
            p = int(row[4]); key = (p, int(row[3]))
            if key in seen: continue
            seen.add(key)
            print("seed", sd, "Bust", np.datetime64(int(m.ev_t[p]), "m"), "Typ", int(row[3]), "Saldo-Start", round(row[2]), "Verlierer-Gap", round(row[5], 1))
            tr = r["tr"]; day = int(row[1])
            for t in tr[(tr[:, 0] >= day - 1)][-6:]:
                print("   tr", np.datetime64(int(t[0]), "D"), round(t[1], 1), "slot", int(t[2]), "str", int(t[4]), np.datetime64(int(t[3]), "m"))
