"""Engpass-Diagnose eines Zyklus: was war zuletzt erfuellt (gueltige Tage / Mindestgewinn / 10 Tage)?"""
import numpy as np, eng6 as E, evl6 as V, r6, cands as K
names = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930"]
V.set_generic(K.fade_blocks(names), None)
m = V.mk()
kw = dict(r6.SAFE); kw.update(r6.C510, **r6.PAY3, gesamtbudget=0.9, idea_cap=0.9, db_on=0, r21_on=0, nz_on=0)
GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1)] * 6)
tot = np.zeros(len(E.ST))
for (a, b) in V.starts(m, 250, 9):
    r = E.run(m, E.params(**kw), a, b, seed=0, masks=E.make_masks(m, 0, 0.0), GP=GP)
    tot += r["st"]
S = E.SI
n = tot[S["lim_valid"]] + tot[S["lim_profit"]] + tot[S["lim_ten"]]
print(f"Zyklen {n:.0f}: zuletzt gueltige Tage {tot[S['lim_valid']]/n*100:.0f} %, zuletzt Mindestgewinn {tot[S['lim_profit']]/n*100:.0f} %, "
      f"zuletzt 10-Tage-Frist {tot[S['lim_ten']]/n*100:.0f} %")
print(f"Tage bis 5 gueltige Tage: {tot[S['cyc_v5']]/n:.1f}, Tage bis Mindestgewinn: {tot[S['cyc_pr']]/n:.1f}, Handelstage/J je Lauf...")
print(f"gueltige Tage {tot[S['valid_days']]:.0f} von {tot[S['trade_days']]:.0f} Handelstagen ({tot[S['valid_days']]/tot[S['trade_days']]*100:.0f} %)")
