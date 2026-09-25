"""Screening 6: Nachbarn von K2 (NAS ohne Kreuz, Gold ab 3 NY): Schwellen, Ziele, Stop, NAS-Regeln, Gewichte."""
import numpy as np
import r7sim as M, r7sig as G, r7kand as KD
from s1_ablation import run, C

def per_sym(lbl, p=None, **kw):
    A, m = run(lbl, p, **kw)
    for si, s in enumerate(G.SYMS):
        print(M.line(f"    {s}", M.metrics(M.sub(A, A["sym"] == si))))
    return A

g = C["sym"] == 0; d = C["dir"]; r = C["rsi"]
P2 = KD.k2(C)
per_sym("K2", P2)
print("--- Schwelle je Symbol")
for tg, tn in ((75, 72.5), (75, 77.5), (77.5, 75), (72.5, 75), (80, 75)):
    thr = np.where(g, tg, tn)
    ok = np.where(d > 0, r > thr, r < 100 - thr)
    per_sym(f"K2 Schwelle Gold {tg} / NAS {tn}", dict(P2, oben=70.0, extra=P2["extra"] & ok))
print("--- Ziele")
for tg, tn in ((2.64, 2.5), (2.64, 3.0), (3.0, 2.2), (2.3, 2.2), (3.0, 2.5)):
    per_sym(f"K2 Ziel Gold {tg} / NAS {tn}", P2, tp=(tg, tn))
print("--- Stop")
for sm in (0.75, 0.875, 1.125):
    per_sym(f"K2 Stop {2*sm:.2f} ATR (Ziel gleich weit)", P2, rd_mult=sm, tp=(2.64 / sm, 2.2 / sm))
print("--- NAS-Regeln")
per_sym("K2 NAS-Longs ohne SMA200", dict(P2, nas_long_rule="none"))
per_sym("K2 nur NAS-Long", dict(P2, extra=P2["extra"] & (g | (d > 0))))
per_sym("K2 ohne zweiten Platz", P2, sim=dict(second=False))
per_sym("K2 ohne Folgesignal", dict(P2, folge_min=0))
print("--- Gewichte")
for w in ((1.0, 1.0, 1.0), (1.25, 0.75, 0.5), (1.5, 1.0, 0.75)):
    per_sym(f"K2 Gewichte {w}", P2, weights=w)
for gm in (0.5, 0.85, 1.0):
    per_sym(f"K2 Gold-Faktor {gm}", P2, gold_mult=gm)
