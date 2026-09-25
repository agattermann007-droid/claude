"""Screening 11: Kandidaten nach Sharpe (Wochen) und Risiko-Paritaet."""
import numpy as np
import r7kand as KD, r7sig as G
from r7lab import run, C
g = C["sym"] == 0; d = C["dir"]; nyh = C["nyh"]
for nm, fn in KD.KAND.items():
    run(nm, fn(C))
P1 = KD.k1(C)
run("K1 + NAS bis 14", dict(P1, nas_bis=14.0))
run("K1 + NAS-Longs ohne SMA200", dict(P1, nas_long_rule="none"))
run("K1 + NAS-Ziel 2,5 R", P1, tp=(2.64, 2.5))
run("K1 + NAS-Ziel 3,0 R", P1, tp=(2.64, 3.0))
run("K1 + Gold nur M15", dict(P1, extra=P1["extra"] & (~g | (C["tf"] == 0))))
run("K1 + max 1 Verlust/Tag", P1, sim=dict(maxloss=1))
run("K1 + Zeit-Stop 36/0,5", P1, sim=dict(ts_bars=36, ts_mfe=0.5))
for ga in (5.0, 7.0, 8.0):
    q = KD.k2(C, gold_ab=ga)
    run(f"K2 Gold ab {ga}", q)
