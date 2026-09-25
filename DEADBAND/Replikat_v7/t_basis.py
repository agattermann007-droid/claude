"""Pruefung: vektorisierte Signale (r7sig) == sig5.r21_signals (Replikat v6) auf denselben Daten; Basis-Kennzahlen."""
import numpy as np, time
import r7data, r7sig as G, r7sim as M
import sig5 as S5

t = time.time()
D = r7data.data()
print(f"Daten {time.time()-t:.0f}s")
t = time.time()
C = G.features(D)
print(f"Merkmale {len(C['T'])} Kandidaten {time.time()-t:.0f}s")
p = dict(G.BASE)
m = G.valid_mask(C, p)
f = G.follow(C, m, p["folge_min"])
t = time.time()
ref = S5.r21_signals(D)
print(f"sig5.r21_signals {len(ref['T'])} Signale (Folge {ref['folge'].sum()}) {time.time()-t:.0f}s")
mine = sorted(zip(C["T"][m].tolist(), C["sym"][m].tolist(), C["tf"][m].tolist(), C["dir"][m].tolist(), f[m].astype(int).tolist()))
theirs = sorted(zip(ref["T"].tolist(), ref["sym"].tolist(), ref["tf"].tolist(), ref["dir"].tolist(), ref["folge"].tolist()))
print("gleich:", mine == theirs, len(mine), len(theirs))
if mine != theirs:
    a = set(mine); b = set(theirs)
    print("nur r7sig:", sorted(a - b)[:10]); print("nur sig5:", sorted(b - a)[:10])
# Basis-Simulation
E = G.entries(C, p)
trs = []
for s in G.SYMS:
    tr = M.simulate(D[s], s, E[s])
    trs.append(tr)
    print(M.line(f"Basis {s}", M.metrics(tr)))
print(M.line("Basis beide", M.metrics(M.merge(trs))))
