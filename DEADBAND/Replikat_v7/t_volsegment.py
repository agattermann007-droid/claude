"""Volumen-Effekt je Datenquelle (Segment): Ø R der 6.10-Trades mit Volumen >= 1,5 x Mittel gegen < 1,5 x Mittel."""
import numpy as np
import r7sig as G, r7sim as M, r7kand as KD
from r7lab import D, C

p = KD.basis(C)
E = G.entries(C, p)
seg = {"XAU": [("OANDA 2006-11", "2006-01-01", "2011-05-14"), ("Dukascopy-Ticks 2011-16", "2011-05-14", "2016-09-03"),
               ("Dukascopy-Proxy 2016-25", "2016-09-03", "2026-01-01")],
       "NAS": [("OANDA 2006-20", "2006-01-01", "2020-05-09"), ("HistData 2020", "2020-05-09", "2021-01-02"), ("MT5-Broker 2021-25", "2021-01-02", "2026-01-01")]}
for si, s in enumerate(G.SYMS):
    tr = M.simulate(D[s], s, E[s])
    key = {(int(a), int(b)): int(ix) for a, b, ix in zip(E[s]["i5"], E[s]["tf"], E[s]["idx"])}
    idx = np.array([key[(int(a), int(b))] for a, b in zip(tr["ie"], tr["tf"])])
    v = C["vrel"][idx]; R = tr["R"]; t = tr["t"]
    for nm, a, b in seg[s]:
        m = (t >= np.datetime64(a, "m").astype(np.int64)) & (t < np.datetime64(b, "m").astype(np.int64))
        hi = m & np.isfinite(v) & (v >= 1.5); lo = m & np.isfinite(v) & (v > 0) & (v < 1.5); na = m & ~(np.isfinite(v) & (v > 0))
        f = lambda x: f"n{x.sum():4d} ØR {R[x].mean():+.3f}" if x.sum() else "n   0"
        print(f"{s} {nm:<26s} Volumen >= 1,5: {f(hi)} | < 1,5: {f(lo)} | ohne Volumen: {f(na)}")
