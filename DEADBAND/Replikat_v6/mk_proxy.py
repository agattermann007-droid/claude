"""Ersatz fuer die GFT-Exporte (../data/*.csv), wenn diese nicht vorliegen: Fremddaten 03.01.2022 - 31.12.2025 im
MT5-Format (Gold Dukascopy, NAS100 MT5-Broker US100; siehe extdata/DATEN_BERICHT.md). Spread wie gext.load:
max(Datei-Spread, Kurs x relativer GFT-Spread 2022-26), in Punkten. Ende 31.12.2025, weil die NAS-Reihe dort endet.
Die Zahlen auf diesem Ersatz sind nicht mit den GFT-Zahlen frueherer Berichte gleichzusetzen (breitere Spreads, keine
GFT-Datenloecher); verglichen werden Varianten untereinander auf denselben Daten.
SPREAD_FAKTOR (Umgebung, Vorgabe 1,0) skaliert die Spreads; 0,6 bringt sie in den Bereich der GFT-Exporte (Gold Median
36 -> 22 Punkte, GFT 7-32; NAS 195 -> 117, GFT 100-163). Nur in einer Kopie des Ordners verwenden (eigene data/ und cache/)."""
import numpy as np, pandas as pd, os, sys
import gext, prep5 as P

A = sys.argv[1] if len(sys.argv) > 1 else "2022-01-03"
B = sys.argv[2] if len(sys.argv) > 2 else "2026-01-01"
os.makedirs(P.DATA, exist_ok=True)
for sym, fn in P.FILES.items():
    src = os.path.join(gext.EXT, gext.FILES[sym])
    ex = pd.read_csv(src, sep="\t", dtype=str)
    t = pd.to_datetime(ex["<DATE>"] + " " + ex["<TIME>"], format="%Y.%m.%d %H:%M:%S")
    keep = (t >= pd.Timestamp(A)) & (t < pd.Timestamp(B))
    ex = ex[keep.values].copy()
    rel = gext.REL_SPREAD[sym] * ex["<CLOSE>"].astype(float).to_numpy()
    sp = ex["<SPREAD>"].astype(float).to_numpy() * P.POINT
    sp = np.where(np.isnan(sp) | (sp <= 0), rel, np.maximum(sp, rel)) * float(os.environ.get("SPREAD_FAKTOR", "1.0"))  # 6.40: x0,6 = GFT-nahe Spreads
    ex["<SPREAD>"] = np.round(sp / P.POINT).astype(np.int64).astype(str)
    out = os.path.join(P.DATA, fn)
    ex.to_csv(out, sep="\t", index=False, lineterminator="\r\n")
    print(sym, "->", out, len(ex), "Kerzen", ex["<DATE>"].iloc[0], "..", ex["<DATE>"].iloc[-1],
          "Spread-Median", float(np.median(ex["<SPREAD>"].astype(int))), "Punkte")
