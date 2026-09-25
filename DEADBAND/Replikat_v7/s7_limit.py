"""Screening 7: Einstieg per Limit-Rueckzug statt Markt (Einzelsignale ohne Plaetze, gleiche Signalmenge K2)."""
import numpy as np
import r7data, r7sig as G, r7sim as M, r7lim as L, r7kand as KD
D = r7data.data(); C = G.features(D)
P2 = KD.k2(C)
E = G.entries(C, P2)
for lo, lb in ((0.0, 0), (0.25, 6), (0.25, 12), (0.5, 12), (0.5, 24), (0.75, 24), (1.0, 48)):
    Rs = []; ts = []; ws = []; fill = []
    for s in G.SYMS:
        e = E[s]; d = D[s]
        R, f, _ = L.sim_lim(d["o"], d["h"], d["l"], d["c"], d["sp"], e["i5"].astype(np.int64), e["dir"].astype(np.int64), e["rd"],
                         e["tp"], lo, lb, 1152, M.COMM[s])
        Rs.append(np.where(f, R, 0.0)); ts.append(d["ny"][e["i5"]]); ws.append(e["w"]); fill.append(f)
    R = np.concatenate(Rs); t = np.concatenate(ts); w = np.concatenate(ws); f = np.concatenate(fill)
    y = M.year_of(t)
    eps = " ".join(f"{nm}:{(R*w)[(y>=a)&(y<=b)].sum()/(b-a+1):+5.1f}" for nm, a, b in M.EPOCHS)
    Rf = R[f]
    print(f"Limit {lo:.2f} R, {lb:2d} Kerzen: gefuellt {100*f.mean():5.1f} %  ØR (gefuellt) {Rf.mean():+.3f} WR {100*(Rf>0).mean():4.1f}  "
          f"R/J(gew.) {(R*w).sum()/20:+6.2f} | {eps}")
