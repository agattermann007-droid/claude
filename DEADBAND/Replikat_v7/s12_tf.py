"""Screening 12: weitere Zeitebenen (M5, H4) als zusaetzliche RSI21-Signale."""
import numpy as np
import r7sig as G, r7sim as M, r7kand as KD
import prep5 as P
from r7lab import D, C

for s in G.SYMS:
    d = D[s]
    d["m5"] = dict(t=d["ny"], o=d["o"], h=d["h"], l=d["l"], c=d["c"], v=d["v"])
    d["h4"] = P.agg(d["ny"], d["o"], d["h"], d["l"], d["c"], d["v"], 240, offset=420)
G.TFS = (5, 240); G.KEYS = ("m5", "h4")
C2 = G.features(D)
G.TFS = (15, 30, 60); G.KEYS = ("m15", "m30", "h1")
C2["tf"] = np.where(C2["tf"] == 0, 3, 4)
CC = {k: np.concatenate([C[k], C2[k]]) for k in C}
o = np.lexsort((CC["tf"], CC["sym"], CC["T"]))
CC = {k: v[o] for k, v in CC.items()}
W = (1.25, 1.0, 0.75, 1.0, 0.75)


def run(lbl, p, sim=None, weights=W):
    q = dict(G.BASE, **p)
    E = G.entries(CC, q, weights=weights)
    A = M.merge([M.simulate(D[s], s, E[s], **(sim or {})) for s in G.SYMS])
    m = M.metrics(A)
    f, ry = M.risk_parity(A, 0.36)
    print(M.line(lbl, m) + f" | RP36 {ry:+.1f}", flush=True)
    for ti, nm in enumerate(("M15", "M30", "H1", "M5", "H4")):
        mm = A["tf"] == ti
        if mm.sum():
            print(M.line(f"    {nm}", M.metrics(M.sub(A, mm))))


g = CC["sym"] == 0
for lbl, fn in (("Basis", KD.basis), ("K1", KD.k1)):
    p = fn(CC)
    run(f"{lbl} (M15/M30/H1)", dict(p, tfs=(0, 1, 2)))
    run(f"{lbl} + M5", dict(p, tfs=(0, 1, 2, 3)))
    run(f"{lbl} + H4", dict(p, tfs=(0, 1, 2, 4)))
