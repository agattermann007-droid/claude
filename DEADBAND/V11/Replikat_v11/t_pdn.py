import numpy as np
import gen11 as G, pa11 as PA, sim11 as M
b = G.sr()[3]
mins = b["t"] % 1440
r = M.simulate(b, tpdelay=4); ok = r["why"] >= 0
for lab, mm in (("alle", np.ones(len(mins), bool)), ("18:00-18:05", (mins >= 1080) & (mins < 1085)), ("18:05-18:30", (mins >= 1085) & (mins < 1110)),
                ("ab 18:30", (mins >= 1110) | (mins < 600))):
    st = {k: M.stats(r["R"][ok & mm], b["t"][ok & mm], lo, hi) for lo, hi, k in PA.PER}
    print(f"SRPDN {lab:12s}", " | ".join(f"{k}: n{v['n']:4d} E{v['er']:+.3f} S{v['sum']:+6.1f}" for k, v in st.items()))
for w0 in (-345, -330):
    c = PA.sweep("NAS", 570, 960, -1, w0, 555, 565, 0.08, 0.5, 0.0, 0, 0.03, 0, 2.0, 99.0, 1)
    res, _ = PA.evalb(c)
    print(f"SRPDN ab {(w0+1440)//60%24}:{(w0+1440)%60:02d}", " | ".join(f"{k}: n{v['n']:4d} E{v['er']:+.3f} S{v['sum']:+6.1f}" for k, v in res.items()))
