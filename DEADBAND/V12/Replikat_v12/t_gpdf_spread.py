"""GPDF-Stresstest Eroeffnung 18:00: Einstiegszeiten, Spread x3 bis 18:30, keine Einstiege 18:00-18:05 bzw. vor 18:15."""
import numpy as np
import pa11 as PA, sim11 as M, gen11 as G
D = G.data(); d = D["XAU"]
b = PA.sweep("XAU", -360, 1020, -1, -360, 120, 480, 0.0, 0.6, 0.0, 0, 0.10, 0, 3.0, 99.0, 1, name="GPDF")
mins = b["t"] % 1440
print("Einstiege je Uhrzeit:", {lab: int(((mins >= a) & (mins < z)).sum()) for lab, a, z in
      (("18:00-18:05", 1080, 1085), ("18:05-18:30", 1085, 1110), ("18:30-20:00", 1110, 1200), ("20:00-02:00", 1200, 1440)) }, "nach Mitternacht", int((mins < 120).sum()))
res, r = PA.evalb(b)
print("Basis          ", " | ".join(f"{k}: n{v['n']:4d} E{v['er']:+.3f} S{v['sum']:+6.1f}" for k, v in res.items()))
for lab, a, z in (("18:00-18:05", 1080, 1085), ("18:05-18:30", 1085, 1110), ("ab 18:30", 1110, 2000)):
    mm = (mins >= a) & (mins < z) if z < 2000 else ((mins >= 1110) | (mins < 120))
    ok = r["why"] >= 0
    st = {k: M.stats(r["R"][ok & mm], b["t"][ok & mm], lo, hi) for lo, hi, k in PA.PER}
    print(f"  nur {lab:12s}", " | ".join(f"{k}: n{v['n']:4d} E{v['er']:+.3f} S{v['sum']:+6.1f}" for k, v in st.items()))
# Spread-Stress: Kopie der Gold-M1 mit Spread x3 von 18:00 bis 18:30
sp_orig = d["sp1"].copy()
m1 = d["ny1"] % 1440
d["sp1"] = np.where((m1 >= 1080) & (m1 < 1110), sp_orig * 3.0, sp_orig)
res2, _ = PA.evalb(b)
print("Spread x3 18:00-18:30", " | ".join(f"{k}: n{v['n']:4d} E{v['er']:+.3f} S{v['sum']:+6.1f}" for k, v in res2.items()))
d["sp1"] = sp_orig
for w0 in (-355, -345):
    b2 = PA.sweep("XAU", -360, 1020, -1, w0, 120, 480, 0.0, 0.6, 0.0, 0, 0.10, 0, 3.0, 99.0, 1)
    res3, _ = PA.evalb(b2)
    print(f"Fenster ab {(w0+1440)//60%24:02d}:{(w0+1440)%60:02d}", " | ".join(f"{k}: n{v['n']:4d} E{v['er']:+.3f} S{v['sum']:+6.1f}" for k, v in res3.items()))
