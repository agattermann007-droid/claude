"""Welche Regel beendet die Konten (Boden, Floating, Tagesverlust)? Basis vs. K1, beide Datensaetze."""
import sys, numpy as np
import r7konto as K, evl6 as V, eng6 as E, r6, r7sig as G, r7kand as KD
from concurrent.futures import ProcessPoolExecutor
for target in ("gft", "ext"):
    D, S, blks = K.dataset(target)
    C = G.features(D)
    for nm in ("Basis", "K1 NAS ohne Kreuz"):
        r21 = G.r21_dict(C, KD.KAND[nm](C))
        S2 = dict(S); S2["r21"] = r21
        V._MK = E.Market(D=D, S=S2)
        GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **K.GPX) for _ in K.F10])
        V.set_generic(blks, GP)
        Pv = E.params(**dict(r6.SAFE, **K.ERTRAG))
        m = V.mk()
        if target == "ext":
            st = V.starts(m, 250, 9, "2006-09-01", "2021-12-31"); seeds = (0, 1, 2, 3)
        else:
            st = V.starts(m, 250, 3); seeds = tuple(range(8))
        jobs = [(Pv, a, b, s, 0.08, 0.3, GP) for (a, b) in st for s in seeds]
        with ProcessPoolExecutor(4) as ex:
            outs = list(ex.map(V._job, jobs, chunksize=32))
        Y = sum(o["years"] for o in outs)
        nb = sum(o["nbust"] for o in outs)
        print(f"{target} {nm:<20s} Busts/J {nb/Y:.3f} | Boden {sum(o['floor_b'] for o in outs)/Y:.3f} Floating {sum(o['float_b'] for o in outs)/Y:.3f} Tag {sum(o['day_b'] for o in outs)/Y:.3f} | Konten {len(outs)}")
