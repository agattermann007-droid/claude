"""Screening 5: Gold-Zeitfenster/Zeitebenen bei 'NAS ohne Kreuz, Gold Kreuz|Gate' (Kandidat K1)."""
import numpy as np
import r7sim as M, r7sig as G
from s1_ablation import run, C

g = C["sym"] == 0
ro = C["ro"]; d = C["dir"]; nyh = C["nyh"]
cross55 = np.where(d > 0, ro > 55, ro < 45) & np.isfinite(ro)
gate = np.where(d > 0, (C["cprev"] > C["maL"]) & (C["cprev"] > C["maS"]), (C["cprev"] < C["maL"]) & (C["cprev"] < C["maS"]))
K1 = np.where(g, cross55 | gate, True)

def per_sym(lbl, p=None, **kw):
    A, m = run(lbl, p, **kw)
    for si, s in enumerate(G.SYMS):
        print(M.line(f"    {s}", M.metrics(M.sub(A, A["sym"] == si))))
    return A

def win(gold_ab, nas_ab=9.5):
    return np.where(g, nyh >= gold_ab, nyh >= nas_ab)

per_sym("K1 (NAS ohne Kreuz)", dict(cross=None, extra=K1))
for ga in (2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0):
    per_sym(f"K1 + Gold ab {ga}", dict(cross=None, ab=0.0, extra=K1 & win(ga)))
for ga, gb in ((3.0, 13.0), (3.0, 15.0), (3.0, 20.0)):
    per_sym(f"K1 + Gold {ga}-{gb}", dict(cross=None, ab=0.0, gold_bis=gb, extra=K1 & win(ga)))
print("--- Zeitebenen Gold (K1, Gold ab 3)")
for tfs in ((0,), (0, 1), (0, 1, 2)):
    ex = K1 & win(3.0) & (~g | np.isin(C["tf"], tfs))
    per_sym(f"K1 + Gold ab 3, Gold-TF {tfs}", dict(cross=None, ab=0.0, gold_ohne_h1=False, extra=ex))
print("--- NAS-Fenster (K1)")
for na, nb in ((9.5, 12.0), (9.5, 14.0), (9.5, 15.5), (9.0, 13.0), (8.0, 13.0), (10.0, 13.0)):
    per_sym(f"K1 + NAS {na}-{nb}", dict(cross=None, ab=0.0, nas_bis=nb, extra=K1 & win(9.5, na)))
