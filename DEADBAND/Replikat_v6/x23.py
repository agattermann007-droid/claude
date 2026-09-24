"""Portfolio aus Fades (hohe Trefferquote) + NAS-PreBreak, mit/ohne alte Module; Mindestauszahlung 3 %."""
import numpy as np, eng6 as E, evl6 as V, r6, cands as K
bA, _ = K.xau_fade(0, r0=420, r1=570, tend=660, xm=750, buf=0.3)
bB, _ = K.nas_fade(1)
bC, _ = K.nas_pre_break(2)
bD, _ = K.xau_fade(3, r0=420, r1=570, tend=660, xm=750, buf=0.6)
V.set_generic([bA, bB, bC, bD], None)
base = dict(r6.C510, **r6.PAY3)
off = dict(db_on=0, r21_on=0, nz_on=0)
def S(r): return dict(on=1, risk=r, maxtrades=1)
C = []
for r in (0.6, 0.9, 1.2):
    C.append((f"Fades A+B {r}", dict(base, **off), E.gparams([S(r), S(r)])))
    C.append((f"Fades A+B+PreBreak {r}", dict(base, **off), E.gparams([S(r), S(r), S(r)])))
C.append(("Fades D+B+PreBreak 1.0", dict(base, **off), E.gparams([{}, S(1.0), S(1.0), S(1.0)])))
C.append(("NZ+R21 + A+B+Pre 0.6", dict(base, db_on=0), E.gparams([S(0.6), S(0.6), S(0.6)])))
C.append(("NZ + A+B+Pre 0.8", dict(base, db_on=0, r21_on=0), E.gparams([S(0.8), S(0.8), S(0.8)])))
C.append(("NZ + A+B+Pre 1.0", dict(base, db_on=0, r21_on=0), E.gparams([S(1.0), S(1.0), S(1.0)])))
r6.run(C, "x23.json")
