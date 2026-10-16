"""v12: Bust-Ursachen Tick-Fades N1030+N1100 (0,5 %) im Fenster 2011-15: Zeitpunkt, Typ, letzte Trades."""
import x12  # noqa: F401
import collections, numpy as np
import cfg11 as C, evl11 as V, eng11 as E, gen11 as G, cand11 as K
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
live_at = G.portfolio_guard(S["fades"])
Pv = E.params()
TB = {nm: K.tick_fade(nm, live_at=live_at) for nm in ("N1030", "N1100")}
blks = [(s_, TB[C.STREAMS[s_]], 1.0) if C.STREAMS[s_] in TB else (s_, b, w) for (s_, b, w) in C.blocks(S)]
m.set_generic(blks)
GP = C.gp_v10()
for nm in TB:
    GP[C.STREAMS.index(nm), E.GPI["tpdelay"]] = 4; GP[C.STREAMS.index(nm), E.GPI["risk"]] = 0.5
V.reset_seed_cache(); V._apply_seed(m, 0)
cnt = collections.Counter(); shown = 0
for sd in range(1, 9):
    V._apply_seed(m, sd)
    for (a, b) in V.starts(m, "2011-03-01", "2015-12-31"):
        r = m.run(Pv, GP, a, b)
        for row in r["ev"][r["ev"][:, 0] == 2]:
            p = int(row[4]); t = np.datetime64(int(m.ev_t[p]), "m")
            cnt[(str(t)[:16], int(row[3]))] += 1
            if shown < 3:
                shown += 1
                print("seed", sd, "Start", np.datetime64(int(m.days[a]), "D"), "Bust", t, "Typ", int(row[3]), "Saldo-Start", round(row[2]), "gap_l", round(row[5], 1))
                tr = r["tr"]; day = int(row[1])
                for x in tr[(tr[:, 0] >= day - 2) & (tr[:, 0] <= day)][-10:]:
                    print("   tr", np.datetime64(int(x[0]), "D"), round(x[1], 1), "slot", int(x[2]),
                          "str", C.STREAMS[int(x[4])] if x[4] >= 0 else int(x[4]), np.datetime64(int(x[3]), "m"))
print("Busts je Zeitpunkt/Typ (8 Seeds):")
for k, v in cnt.most_common(15):
    print("  ", k, v)
