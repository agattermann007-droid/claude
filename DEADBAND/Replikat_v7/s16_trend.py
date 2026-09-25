"""Screening 16: Tagestrend-Staerke (D1-RSI, Abstand SMA50) und Uhrzeit als Einstiegsfilter (Basis)."""
import numpy as np
import r7kand as KD
from r7lab import srun, C
p = KD.basis(C)
d = C["dir"]; px = C["close"]
d1 = np.where(d > 0, C["d1rsi"], 100 - C["d1rsi"])
a50 = d * (px - C["ma50"]) / C["d1atr"]
srun("Basis", p)
for th in (50, 52.5, 55, 57.5):
    srun(f"D1-RSI mit > {th}", dict(p, post=d1 > th))
for th in (0.5, 1.0, 1.5, 2.0):
    srun(f"Abstand SMA50 > {th} Tages-ATR", dict(p, post=a50 > th))
for hb in (11.0, 12.0, 13.0, 15.0):
    g = C["sym"] == 0
    srun(f"Gold bis {hb}", dict(p, gold_bis=hb))
