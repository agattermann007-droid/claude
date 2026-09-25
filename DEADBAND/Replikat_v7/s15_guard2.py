"""Screening 15: Waechter (Basis) nach Sharpe/Risiko-Paritaet; Groesse nach Verlusten."""
import numpy as np
import r7kand as KD, r7sim as M, r7sig as G
from r7lab import srun, C, D, short
import s8_guard as SG

p = KD.basis(C)
srun("Basis", p)
use, Rv, tx = SG.virtual(p)
for N, th, ps in ((15, 1.0, True), (20, 1.0, True), (20, 0.8, True), (25, 1.0, True), (30, 1.0, True), (20, 1.0, False), (30, 1.0, False), (40, 1.0, False)):
    live = SG.guard(use, Rv, tx, N, th, "pf", per_sym=ps)
    srun(f"Waechter PF {N} > {th} {'je Symbol' if ps else 'gesamt'}", dict(p, post=live))
