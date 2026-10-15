import time, numpy as np, sys
import cfg11 as C, evl11 as V, eng11 as E
t0 = time.time()
S = C.signals()
print(f"Signale {time.time()-t0:.0f}s", flush=True)
m = V.mk()
m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
m.set_generic(C.blocks(S))
print(f"Markt {time.time()-t0:.0f}s, Ereignisse {len(m.ev_t)}, R21 {len(m.r['ev'])}, NZ {len(m.z['ev'])}, generisch {len(m.g['ev'])}", flush=True)
Pv = E.params()
a = m.day_index("2022-03-07"); b = m.day_index("2023-03-07")
r = m.run(Pv, C.gp_v10(), a, b)
print(f"Testlauf {time.time()-t0:.0f}s", r["st"][:10], r["ev"][:5])
