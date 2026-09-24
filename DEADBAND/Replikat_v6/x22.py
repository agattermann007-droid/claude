"""Neue Kandidaten im GFT-Konto: allein und zu 5.10 dazu (Mindestauszahlung 3 %)."""
import numpy as np, eng6 as E, evl6 as V, r6, cands as K
b0, _ = K.xau_fade(0)
b1, _ = K.nas_pre_break(1)
b2, _ = K.nas_lasthour(2)
V.set_generic([b0, b1, b2], None)
base = dict(r6.C510, **r6.PAY3)
old_off = dict(db_on=0, r21_on=0, nz_on=0)
S0 = dict(on=1, risk=0.5, maxtrades=1)
C = []
C.append(("nur XAU-Fade 0.5", dict(base, **old_off), E.gparams([S0])))
C.append(("nur NAS-PreBreak 0.5", dict(base, **old_off), E.gparams([{}, S0])))
C.append(("nur NAS-LastHour 0.5", dict(base, **old_off), E.gparams([{}, {}, S0])))
C.append(("alle 3 neu je 0.5", dict(base, **old_off), E.gparams([S0, S0, S0])))
C.append(("alle 3 neu je 0.8", dict(base, **old_off), E.gparams([dict(S0, risk=0.8)] * 3)))
C.append(("5.10 + 3 neu je 0.5", base, E.gparams([S0, S0, S0])))
C.append(("R21+NZ + 3 neu je 0.5", dict(base, db_on=0), E.gparams([S0, S0, S0])))
r6.run(C, "x22.json")
