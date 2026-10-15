import numpy as np
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk()
m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
Pv = E.params(); GP = C.gp_v10()
a = m.day_index("2018-05-08"); b = m.day_index("2019-05-08")
r = m.run(Pv, GP, a, b)
ev = r["ev"]; row = ev[ev[:, 0] == 2][0]
p = int(row[4]); print("Bust-Minute", np.datetime64(int(m.ev_t[p]), "m"), "gap_l", row[5])
for k in (0, 1):
    i = m.ev_i[k, p]
    if i >= 0:
        print(k, "o h l c", m.o1[k, i], m.h1[k, i], m.l1[k, i], m.c1[k, i], "prev c", m.c1[k, i-1], np.datetime64(int(m.ny1[k][i-1]), "m"))
tr = r["tr"]
print(tr[-6:])
# Generische Signale um diese Zeit
g = m.g; sel = (g["ev"] > p - 3000) & (g["ev"] <= p)
for j in np.nonzero(sel)[0]:
    print("gen", g["str"][j], np.datetime64(int(m.ev_t[g["ev"][j]]), "m"), g["dir"][j], g["ent"][j], g["sl"][j], g["tp"][j], np.datetime64(int(m.ev_t[min(g["xev"][j], len(m.ev_t)-1)]), "m"))
