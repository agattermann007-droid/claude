"""Rauschen der Kontoebene: V10 mit 8 gepaarten Stoerungs-Seeds (je 3 % Signale weg) - Streuung je Seed."""
import numpy as np
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk()
m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
Pv = E.params()
for sd in range(9):
    r = V.evaluate(Pv, C.gp_v10(), seeds=(sd,))
    print(f"seed {sd}: " + " | ".join(f"{w.split()[-1]} {r[w]['pay']:5.2f} {r[w]['net']:5.0f}$" for w in V.WIN), flush=True)
r = V.evaluate(Pv, C.gp_v10(), seeds=tuple(range(1, 9)))
print("Mittel 1-8: " + " | ".join(f"{w.split()[-1]} {r[w]['pay']:5.2f} {r[w]['net']:5.0f}$" for w in V.WIN))
