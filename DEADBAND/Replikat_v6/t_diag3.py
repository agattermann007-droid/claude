"""Engpass-Diagnose fuer 6.00 Sicher/Ertrag (mit Review-Filtern wie x35): was war zuletzt erfuellt?"""
import numpy as np, eng6 as E, evl6 as V, r6, x35 as X
F10 = X.F10
blks = X.blocks_filtered(F10, "gft")
for lbl, (kw0, risks) in X.CFG.items():
    GP = E.gparams([dict(on=1, risk=r, maxtrades=1) for r in risks])
    V.set_generic(blks, GP)
    m = V.mk()
    kw = dict(r6.SAFE); kw.update(kw0)
    tot = np.zeros(len(E.ST))
    for (a, b) in V.starts(m, 250, 3):
        r = E.run(m, E.params(**kw), a, b, seed=0, masks=E.make_masks(m, 0, 0.0), GP=GP)
        tot += r["st"]
    S = E.SI
    n = tot[S["lim_valid"]] + tot[S["lim_profit"]] + tot[S["lim_ten"]]
    print(f"{lbl}: Zyklen {n:.0f}: zuletzt gueltige Tage {tot[S['lim_valid']]/n*100:.0f} %, zuletzt Mindestgewinn {tot[S['lim_profit']]/n*100:.0f} %, zuletzt 10-Tage-Frist {tot[S['lim_ten']]/n*100:.0f} %")
    print(f"   Tage bis 5 gueltige Tage: {tot[S['cyc_v5']]/n:.1f}, Tage bis Mindestgewinn: {tot[S['cyc_pr']]/n:.1f}")
    print(f"   gueltige Tage {tot[S['valid_days']]:.0f} von {tot[S['trade_days']]:.0f} Handelstagen ({tot[S['valid_days']]/max(tot[S['trade_days']],1)*100:.0f} %)", flush=True)
