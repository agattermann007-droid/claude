"""Gold MT5-Broker-Feed 2018-2024 (echtes Tickvolumen) gegen Dukascopy-Proxy: Ø R der Gold-Trades nach Volumen-Klasse."""
import numpy as np
import r7data, r7sig as G, r7sim as M, r7kand as KD
for f in ("XAUUSD_ext_mt5_M5.csv", "XAUUSD_ext_M5.csv"):
    r7data.FILES["XAU"] = f
    D = {"XAU": r7data.load("XAU", "2018-01-01", "2025-01-01"), "NAS": r7data.load("NAS", "2018-01-01", "2025-01-01")}
    C = G.features(D)
    E = G.entries(C, KD.basis(C))
    tr = M.simulate(D["XAU"], "XAU", E["XAU"])
    key = {(int(a), int(b)): int(ix) for a, b, ix in zip(E["XAU"]["i5"], E["XAU"]["tf"], E["XAU"]["idx"])}
    idx = np.array([key[(int(a), int(b))] for a, b in zip(tr["ie"], tr["tf"])])
    v = C["vrel"][idx]; R = tr["R"]
    for lo_, hi_ in ((0, 1.0), (1.0, 1.5), (1.5, 2.0), (2.0, 3.0), (3.0, 99)):
        m = np.isfinite(v) & (v >= lo_) & (v < hi_)
        print(f"{f:<24s} Volumen {lo_:.1f}-{hi_:.1f}: n {m.sum():4d} ØR {R[m].mean():+.3f}")
    print(f"{f:<24s} Median Volumen-Verhaeltnis der Trades {np.nanmedian(v):.2f}")
