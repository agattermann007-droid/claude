import numpy as np
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk()
m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
W = {"Pruef 2024-25": V.WIN["Pruef 2024-25"]}
for sl in (0.0, 0.1, 0.25):
    r = V.evaluate(E.params(slip=sl), C.gp_v8(), windows=W)["Pruef 2024-25"]
    print(sl, V.line("", r)); print("   ", V.mods_line(r))
    print("    valid/J", round(r["valid"],1), "bank/J", round(r["bank"],1), "cool/J", round(r["cool"],1), "brake/J", round(r["brake"],1), "tr/J", round(r["tr"]), "WR", round(r["wr"],1), "lim v/p/t", r["lim_v"], r["lim_p"], r["lim_t"])
