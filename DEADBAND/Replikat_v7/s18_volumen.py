"""Screening 18: Volumen-Bestaetigung (Tick-Volumen der Signalkerze relativ zum Mittel der letzten 50 Kerzen)."""
import numpy as np
import r7sig as G, r7kand as KD
import prep5 as P
from r7lab import D, C, srun
vrel = np.full(len(C["T"]), np.nan)
for si, s in enumerate(G.SYMS):
    for ti, kk in enumerate(G.KEYS):
        B = D[s][kk]
        v = B["v"].astype(float)
        vr = v / P.sma(v, 50)
        m = (C["sym"] == si) & (C["tf"] == ti)
        vrel[m] = vr[C["kbar"][m] - 1]
ok = np.isfinite(vrel) & (vrel > 0)
print("Anteil mit Volumen:", ok.mean().round(3))
p = KD.basis(C)
srun("Basis", p)
for th in (0.8, 1.0, 1.2, 1.5):
    srun(f"Volumen >= {th} x Mittel", dict(p, post=~ok | (vrel >= th)))
    srun(f"Volumen <  {th} x Mittel", dict(p, post=~ok | (vrel < th)))
