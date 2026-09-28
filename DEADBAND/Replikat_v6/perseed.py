"""Build 6.50: 6.40 und 6.50 paarweise je Stoerung (16 Stoerungen, jeder Handelstag): Auszahlungen und Netto je Stoerung,
Anteil der Stoerungen mit mehr Netto bzw. mindestens gleich vielen Auszahlungen. Aufruf in Replikat_v6 (bzw. in der Kopie mit
GFT-nahen Spreads): python perseed.py"""
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import x48
out = {}
for lbl in ("6.40 Ertrag", "6.50 Ertrag"):
    v = x48.VAR[lbl]
    m = x48.evaluate("gft", v[0], v[1], seeds=16, step=1, per_seed=True, fade_risk=v[2], rule=v[3], per=v[4] if len(v) > 4 else None)
    out[lbl] = np.array(m["streuung"]["per"])
a, b = out["6.40 Ertrag"], out["6.50 Ertrag"]
print("Stoerung  Ausz 6.40 -> 6.50   Netto 6.40 -> 6.50")
for i in range(len(a)):
    print(f"{i:3d}  {a[i,0]:6.2f} -> {b[i,0]:6.2f}   {a[i,2]:6.0f} -> {b[i,2]:6.0f}")
print(f"Netto hoeher in {int((b[:,2] > a[:,2]).sum())}/16, Auszahlungen >= in {int((b[:,0] >= a[:,0]).sum())}/16, "
      f"Differenz Ausz Mittel {np.mean(b[:,0]-a[:,0]):+.2f} (SD {np.std(b[:,0]-a[:,0], ddof=1):.2f}), Netto {np.mean(b[:,2]-a[:,2]):+.0f} (SD {np.std(b[:,2]-a[:,2], ddof=1):.0f})")
