"""Busts im Einzelpfad (gft): Tag, und Modul-Ergebnisse der 15 Tage davor. Basis vs K1 (NAS ohne Kreuz)."""
import numpy as np
import r7konto as K, evl6 as V, eng6 as E, r6, r7sig as G, r7kand as KD
target = "gft"
D, S, blks = K.dataset(target)
C = G.features(D)
for nm, risk in (("Basis", 0.5), ("K1 NAS ohne Kreuz", 0.5), ("K1 NAS ohne Kreuz", 0.25)):
    S2 = dict(S); S2["r21"] = G.r21_dict(C, KD.KAND[nm](C))
    m = E.Market(D=D, S=S2)
    GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **K.GPX) for _ in K.F10])
    m.set_generic(blks)
    Pv = E.params(**dict(r6.SAFE, **dict(K.ERTRAG, r21_risk=risk)))
    tot_b = 0
    for start in range(m.day_index("2022-03-21"), len(m.days) - 250, 20):
        r = E.run(m, Pv, start, start + 250, seed=0, masks=E.make_masks(m, 0, 0.0), GP=GP)
        ev = r["ev"]; tr = r["tr"]
        for e in ev[ev[:, 0] == 2]:
            tot_b += 1
            day = e[1]
            w = tr[(tr[:, 0] > day - 15) & (tr[:, 0] <= day)]
            mods = {}
            for row in w:
                nmx = V.modname(int(row[2]))
                a = mods.setdefault(nmx, [0.0, 0]); a[0] += row[1]; a[1] += 1
            print(f"{nm} r{risk} Start {np.datetime64(int(m.days[start]), 'D')} Bust {np.datetime64(int(day), 'D')} "
                  + " ".join(f"{k}:{v[0]:+.0f}/{v[1]}" for k, v in sorted(mods.items())))
    print(nm, risk, "Busts gesamt", tot_b)
