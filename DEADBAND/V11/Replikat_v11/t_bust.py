import numpy as np
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk()
m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
Pv = E.params(); GP = C.gp_v10()
seen = set()
for (a, b) in V.starts(m, "2017-01-02", "2020-12-31"):
    r = m.run(Pv, GP, a, b)
    ev = r["ev"]
    for row in ev[ev[:, 0] == 2]:
        key = (int(row[1]), int(row[3]))
        if key in seen: continue
        seen.add(key)
        day = int(row[1])
        print("Bust", np.datetime64(day, "D"), "Typ", int(row[3]), "Saldo-Start", round(row[2], 1), "start", np.datetime64(int(m.days[a]), "D"))
        tr = r["tr"]
        last = tr[(tr[:, 0] >= day - 1) & (tr[:, 0] <= day)]
        for t in last[-8:]:
            print("    tr", np.datetime64(int(t[0]), "D"), round(t[1], 1), "slot", int(t[2]), "str", int(t[4]), "t", np.datetime64(int(t[3]), "m"))
