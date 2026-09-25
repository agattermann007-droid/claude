"""Screening 9: zweiter Platz nur bei Gewinn der ersten Position (Pyramidieren), Verlustgrenze je Tag, Risiko-Paritaet."""
import numpy as np
import r7sim as M, r7kand as KD
from s1_ablation import run, C

def rp(lbl, p, **kw):
    A, m = run(lbl, p, show=False, **kw)
    f, ry = M.risk_parity(A, 0.36)
    f2, ry2 = M.risk_parity(A, 0.2)
    print(M.line(lbl, m) + f" | RP36 {ry:+.2f} (x{f:.2f}) RP20 {ry2:+.2f}", flush=True)
    return A

for nm in ("Basis", "K1 NAS ohne Kreuz"):
    p = KD.KAND[nm](C)
    rp(nm, p)
    rp(f"{nm} ohne Platz B", p, sim=dict(second=False))
    for am in (0.0, 0.5, 1.0, 1.5):
        rp(f"{nm} Platz B ab A >= {am} R", p, sim=dict(add_min=am))
    for am, be in ((0.5, 0.0), (1.0, 0.0), (1.0, 0.3)):
        rp(f"{nm} Platz B ab A >= {am} R, A-Stop auf {be} R", p, sim=dict(add_min=am, add_be=be))
    rp(f"{nm} max 1 Verlust/Tag", p, sim=dict(maxloss=1))
