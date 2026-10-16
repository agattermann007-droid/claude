"""v12: IMOM im Konto - Ergebnis je Modul (Seed 0) mit und ohne Abschluss-Ernte / Serienzaehler fuer den neuen Strom."""
import x12  # noqa: F401
import numpy as np
import cfg11 as C, evl11 as V, eng11 as E, gen11 as G, reg12 as R
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
live_at = G.portfolio_guard(S["fades"])
Pv = E.params()
b = R.gate(R.imom(600, 600, 955, 0.2, 0.3, 0), live_at, False)
m.set_generic(C.blocks(S, extra=[(18, b)]))
W = {k: V.WIN5[k] for k in ("Auswahl 2022", "Pruef 2017-20", "Pruef 2011-15")}
for lab, kw in (("harv1", dict(harv=1)), ("harv0", dict(harv=0)), ("harv0 noser", dict(harv=0, noser=1)),
                ("harv0 ripe0", dict(harv=0, ripeclose=0))):
    st = dict(on=1, risk=0.5, maxtrades=1, tpdelay=5, minsprd=6, **kw)
    r = V.evaluate(Pv, C.gp_v10(extra=[st]), windows=W)
    for w in W:
        g = r[w]["mods"].get("g18", dict(pnl=0, tr=0, wr=0))
        print(f"{lab:12s} {w:14s} Ausz/J {r[w]['pay']:5.2f} $/J {r[w]['net']:5.0f} Bust {r[w]['bust']:3d} | IMOM {g['pnl']:6.0f}$/J {g['tr']:5.1f} tr {g['wr']:4.1f}% | Serien {r[w]['cool']:5.1f}", flush=True)
