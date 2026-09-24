import numpy as np, pickle, os, prep5 as P, gsig as G
ext = pickle.load(open(os.path.join(P.OUT, "DXo.pkl"), "rb"))
G._D = ext
import scan6 as S, cands as K
K._CACHE.clear()
names = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
for nm in names:
    p = K.FADES[nm]
    b, (ie, d, rd, tp, ix) = K.fade(0, **p)
    R, *_ = G.simulate(p["sym"], ie, d, rd, tp, ix)
    G.show(G.metrics(R, b["t_entry"], f"{nm} FREMD 2022-26"))
