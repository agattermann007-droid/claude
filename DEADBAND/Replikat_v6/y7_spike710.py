"""V7-Forschung: 7.10-Spezifikation des Spike-Moduls S0830 je Jahr (Long = Voreinstellung, Short zum Vergleich).
Aufruf: python y7_spike710.py  (braucht ../data und DEADBAND_EXT)"""
import numpy as np
import gsig as G, gext, cands as K
from y7_spike import trades, show

SPEC = (510, 2, 6, 660, 0.20, 0.25, 0.5)   # 7.10: SpikeStartNY, MessKerzen, WarteKerzen, AusstiegNY, KMin, StopATR, Ziel
for ds in ("ext", "gft"):
    if ds == "ext":
        G._D = gext.data_ext()
    else:
        G._D = None; G.data()
    K._CACHE.clear()
    print(f"\n######## {ds}")
    for k in (0.15, 0.20, 0.25):
        c = SPEC[:4] + (k,) + SPEC[5:]
        t, R, d = trades("NAS", c)
        show(f"k{k:.2f} Long", t[d > 0], R[d > 0])
        show(f"k{k:.2f} Short", t[d < 0], R[d < 0])
