"""Gegenprobe: pa11.sweep mit den SR-Standardmarken muss gen11.sr reproduzieren."""
import numpy as np, gen11 as G, pa11 as PA
for b, mk in zip(G.sr(), G.SR_STANDARD):
    nm, la, lb, loff, w0, w1, x, sd, md, rb, sb, dr = mk
    c = PA.sweep("NAS", la, lb, loff, w0, w1, x, sd, md, rb, 0, sb, 0, 2.0, 99.0, dr)
    same = len(b["t"]) == len(c["t"]) and np.all(b["t"] == c["t"]) and np.allclose(b["sl"], c["sl"])
    print(nm, len(b["t"]), len(c["t"]), "gleich" if same else "ABWEICHUNG")
