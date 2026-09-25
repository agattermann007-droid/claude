"""Gegenprobe Volumen-Filter auf anderen Gold-Feeds: MT5-Broker (2018-2024, echtes Tickvolumen) und OANDA (2006-2020,
Tickanzahl) statt Dukascopy-Proxy. NAS jeweils aus NAS100_ext. Nur Gold-Trades ausgewertet."""
import numpy as np
import r7data, r7sig as G, r7sim as M, r7kand as KD

def lauf(gold_file, start, end):
    r7data.FILES["XAU"] = gold_file
    D = {"XAU": r7data.load("XAU", start, end), "NAS": r7data.load("NAS", start, end)}
    C = G.features(D)
    out = {}
    for lbl, fn, gm in (("6.10", KD.basis, 0.7), ("Volumen 1,5", KD.KAND["Volumen 1.5"], 0.7)):
        E = G.entries(C, fn(C), gold_mult=gm)
        tr = M.simulate(D["XAU"], "XAU", E["XAU"])
        m = M.metrics(tr, weighted=False)
        print(f"{gold_file:<26s} {start[:4]}-{end[:4]} {lbl:<12s} Gold-Trades {m['n']:4d} ({m['tpy']:4.1f}/J) WR {m['wr']:4.1f} ØR {m['avgR']:+.3f} PF {m['pf']:.2f} Sharpe {m['sh']:.2f}")
lauf("XAUUSD_ext_mt5_M5.csv", "2018-01-01", "2025-01-01")
lauf("XAUUSD_ext_M5.csv", "2018-01-01", "2025-01-01")
lauf("XAUUSD_ext_oanda_M5.csv", "2006-06-01", "2020-05-01")
lauf("XAUUSD_ext_M5.csv", "2006-06-01", "2020-05-01")
