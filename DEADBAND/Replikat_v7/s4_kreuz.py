"""Screening 4: Kreuz-Bestaetigung und Zeitfenster genauer (je Symbol)."""
import numpy as np
import r7sim as M, r7sig as G
from s1_ablation import run, C

def per_sym(lbl, p=None, **kw):
    A, m = run(lbl, p, **kw)
    for si, s in enumerate(G.SYMS):
        print(M.line(f"    {s}", M.metrics(M.sub(A, A["sym"] == si))))
    return A

g = C["sym"] == 0
ro = C["ro"]; d = C["dir"]
cross55 = np.where(d > 0, ro > 55, ro < 45) & np.isfinite(ro)
gate = np.where(d > 0, (C["cprev"] > C["maL"]) & (C["cprev"] > C["maS"]), (C["cprev"] < C["maL"]) & (C["cprev"] < C["maS"]))
per_sym("Basis", None)
per_sym("ohne Kreuz (beide)", dict(cross=None))
# Kreuz nur fuer NAS abschalten: Gold behaelt Kreuz ODER Gate
per_sym("NAS ohne Kreuz, Gold Kreuz|Gate", dict(cross=None, extra=np.where(g, cross55 | gate, True)))
per_sym("Gold ohne Kreuz/Gate, NAS mit Kreuz", dict(cross=None, extra=np.where(g, True, cross55)))
per_sym("Gold nur Gate, NAS ohne Kreuz", dict(cross=None, extra=np.where(g, gate, True)))
for thr in (45.0, 50.0, 52.5):
    per_sym(f"Kreuz-Schwelle {thr}", dict(cross=thr))
print("--- ohne Kreuz + Zeitfenster")
for ab in (3.0, 6.0, 8.0, 9.0):
    per_sym(f"ohne Kreuz, ab {ab}", dict(cross=None, ab=ab))
