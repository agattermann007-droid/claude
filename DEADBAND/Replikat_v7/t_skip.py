"""Warum werden RSI21-Signale im Konto nicht gehandelt? (Zaehler r_seen .. r_taken aus eng6)"""
import numpy as np
import r7konto as K, evl6 as V, eng6 as E, r6, r7sig as G, r7kand as KD
names = ["r_seen", "r_mode", "r_loss", "r_slot", "r_hedge", "r_budget", "r_minlot", "r_margin", "r_taken"]
for target in ("gft", "ext"):
    D, S, blks = K.dataset(target)
    C = G.features(D)
    for nm in ("Basis", "K1gn"):
        S2 = dict(S); S2["r21"] = G.r21_dict(C, KD.KAND[nm](C))
        m = E.Market(D=D, S=S2)
        GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **K.GPX) for _ in K.F10])
        m.set_generic(blks)
        Pv = E.params(**dict(r6.SAFE, **K.ERTRAG))
        a = m.day_index("2022-03-21" if target == "gft" else "2006-09-01")
        b = len(m.days) - 1 if target == "gft" else m.day_index("2021-12-31")
        r = E.run(m, Pv, a, b, seed=0, masks=E.make_masks(m, 0, 0.0), GP=GP)
        st = r["st"]
        print(target, nm, " ".join(f"{n}={int(st[E.SI[n]])}" for n in names), f"Jahre {r['years']:.1f} Busts {int(st[E.SI['nbust']])} Ausz {int(st[E.SI['npay']])}")
