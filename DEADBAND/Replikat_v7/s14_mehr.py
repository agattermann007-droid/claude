"""Screening 14: RSI-Laenge, Gold-Long-Regel, staerkeres Folgesignal, RSI-Ausstieg (auf K1gn)."""
import numpy as np
import r7sig as G, r7sim as M, r7kand as KD, r7data
import prep5 as P
from r7lab import D, C, short, srun

p0 = KD.k1gn(C)
srun("K1gn", p0)
g = C["sym"] == 0; d = C["dir"]
# 1) Gold-Longs nur mit Gate (Kurs ueber SMA200 und SMA100), Shorts Kreuz|Gate
gate = np.where(d > 0, (C["cprev"] > C["maL"]) & (C["cprev"] > C["maS"]), (C["cprev"] < C["maL"]) & (C["cprev"] < C["maS"]))
srun("K1gn + Gold-Long nur mit Gate", dict(p0, extra=p0["extra"] & ~(g & (d > 0) & ~gate)))
srun("K1gn + Gold-Long nur ueber SMA200", dict(p0, gold_long_rule="L"))
# 2) Folgesignal mit mindestens 2 frueheren Signalen binnen 240 min
def follow2(C, m, fm, k=2):
    f = np.zeros(len(m), bool)
    for si in (0, 1):
        for dd in (1, -1):
            idx = np.nonzero(m & (C["sym"] == si) & (C["dir"] == dd))[0]
            if len(idx) == 0: continue
            u, inv = np.unique(C["T"][idx], return_inverse=True)
            ok = np.zeros(len(u), bool)
            for i in range(len(u)):
                j = np.searchsorted(u, u[i] - fm, side="left")
                ok[i] = (i - j) >= k
            f[idx] = ok[inv]
    return f
m = G.valid_mask(C, dict(G.BASE, **p0))
f2 = follow2(C, m, 240, 2)
srun("K1gn + Folgesignal >= 2 fruehere", dict(p0, post=f2))
f2b = follow2(C, m, 480, 2)
srun("K1gn + Folgesignal >= 2 fruehere (480 min)", dict(p0, post=f2b))
# 3) RSI-Ausstieg: M15-RSI(21) faellt unter X (long) bzw. steigt ueber 100-X (short), am Schluss der M15-Kerze
def xb_arr(s, lo):
    d = D[s]; B = d["m15"]
    r = P.rsi_wilder(B["c"], 21)
    arr = np.zeros(len(d["ny"]), np.int64)
    last = B["last"]
    arr[last] = np.where(r < lo, -1, np.where(r > 100 - lo, 1, 0))
    return arr
for lo in (40.0, 45.0, 50.0):
    q = dict(G.BASE, **p0)
    E = G.entries(C, q)
    A = M.merge([M.simulate(D[s], s, E[s], xb=xb_arr(s, lo)) for s in G.SYMS])
    mm = M.metrics(A); mm["rp36"] = M.risk_parity(A, 0.36)[1]; mm["rp20"] = M.risk_parity(A, 0.2)[1]
    print(short(f"K1gn + RSI-Ausstieg M15 < {lo}", mm), flush=True)
# 4) RSI-Laenge
for L in (14, 18, 24, 28):
    C2 = G.features(D, rsi_len=L)
    p2 = KD.k1gn(C2)
    q = dict(G.BASE, **p2)
    E = G.entries(C2, q)
    A = M.merge([M.simulate(D[s], s, E[s]) for s in G.SYMS])
    mm = M.metrics(A); mm["rp36"] = M.risk_parity(A, 0.36)[1]; mm["rp20"] = M.risk_parity(A, 0.2)[1]
    print(short(f"K1gn mit RSI({L})", mm), flush=True)
