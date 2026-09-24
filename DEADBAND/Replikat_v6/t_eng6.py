"""Pruefung: eng6 ohne generische Signale muss exakt eng5 entsprechen."""
import numpy as np, eng5 as E5, eng6 as E6, evl5 as V5, evl6 as V6, batch as B
P50 = dict(db_tp1r=1.5, db_be=0.05, db_tp1f=0.5)
C2 = dict(P50, r21_risk=0.63, nz_risk=0.45, ge_mode=1, bank_on=1, bank_last=2, bank_minr=0.5, bank_mods=1,
          cool_n=4, cool_days=0, idea_cap=1.25)
kw = dict(B.SAFE); kw.update(C2)
m5 = V5.mk(); m6 = V6.mk()
a = m5.day_index("2022-03-21"); b = len(m5.days)
for seed in (0, 3):
    ms5 = E5.make_masks(m5, seed, 0.08 if seed else 0.0)
    ms6 = E6.make_masks(m6, seed, 0.08 if seed else 0.0)
    P5 = E5.params(**kw); P6 = E6.params(**kw)
    if seed:
        P5[E5.PI["slip_frac"]] = 0.3; P6[E6.PI["slip_frac"]] = 0.3
    r5 = E5.run(m5, P5, a, b, seed=seed, masks=ms5)
    r6 = E6.run(m6, P6, a, b, seed=seed, masks=ms6)
    print("seed", seed, "st gleich:", np.allclose(r5["st"], r6["st"][:len(r5["st"])]), "tr gleich:", np.allclose(r5["tr"], r6["tr"]),
          "npay", r5["st"][E5.SI["npay"]], r6["st"][E6.SI["npay"]], "pnl", round(r5["st"][2], 2), round(r6["st"][2], 2))
