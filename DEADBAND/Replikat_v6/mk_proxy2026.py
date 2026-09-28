"""Build 6.60: GFT-Ersatz bis 2026 fuer den Zukunftstest (Ordnerkopie verwenden: eigene data/ und cache/).
Gold: Fremddaten (Dukascopy) 03.01.2022 - 02.09.2026. NAS100: MT5-Broker-Export (wie mk_proxy) bis 31.12.2024, danach
Dukascopy-Ticks (extdata/scripts/build_nas_dukascopy.py) 02.01.2025 - 28.08.2026; Naht am Neujahrs-Feiertag.
Spread wie mk_proxy: max(Datei, Kurs x relativer GFT-Spread) x SPREAD_FAKTOR; im Dukascopy-Teil nur der relative Spread
(Dukascopy notiert Jan-Aug 2025 3,2 Punkte, ab Sep 2025 0,9 - beides nicht GFT-typisch; so gilt dieselbe Kostenregel wie
im Broker-Teil, wo der relative Spread fast immer greift).
Dukascopy handelt NAS100 nur bis 16:15 NY (GFT bis 17:00): Kerzen 16:15-16:55 NY werden flach zum letzten Kurs ergaenzt,
damit Zeit-Ausstiege um 16:40 NY am selben Tag stattfinden (zum 16:15-Kurs statt ueber Nacht).
Aufruf: [SPREAD_FAKTOR=0.6] python mk_proxy2026.py [NAS-Naht JJJJ-MM-TT, Vorgabe 2025-01-01]"""
import numpy as np, pandas as pd, os, sys
import gext, prep5 as P

NAHT = sys.argv[1] if len(sys.argv) > 1 else "2025-01-01"
SF = float(os.environ.get("SPREAD_FAKTOR", "1.0"))


def read(fn, a, b):
    ex = pd.read_csv(os.path.join(gext.EXT, fn), sep="\t", dtype=str)
    t = pd.to_datetime(ex["<DATE>"] + " " + ex["<TIME>"], format="%Y.%m.%d %H:%M:%S")
    return ex[((t >= pd.Timestamp(a)) & (t < pd.Timestamp(b))).values].copy()


def spread(ex, sym):
    rel = gext.REL_SPREAD[sym] * ex["<CLOSE>"].astype(float).to_numpy()
    sp = ex["<SPREAD>"].astype(float).to_numpy() * P.POINT
    sp = np.where(np.isnan(sp) | (sp <= 0), rel, np.maximum(sp, rel)) * SF
    ex["<SPREAD>"] = np.round(sp / P.POINT).astype(np.int64).astype(str)
    return ex


os.makedirs(P.DATA, exist_ok=True)
xau = spread(read(gext.FILES["XAU"], "2022-01-03", "2026-09-03"), "XAU")
def fill_close(ex):
    """flache Kerzen 23:15-23:55 Serverzeit (16:15-16:55 NY) je Handelstag, dessen letzte Kerze um 23:10 liegt."""
    t = pd.to_datetime(ex["<DATE>"] + " " + ex["<TIME>"], format="%Y.%m.%d %H:%M:%S")
    last = t.groupby(t.dt.date).transform("max")
    ends = ex[((t == last) & (t.dt.strftime("%H:%M") == "23:10")).values]
    add = []
    for _, row in ends.iterrows():
        for mm in range(15, 60, 5):
            r = row.copy(); r["<TIME>"] = f"23:{mm:02d}:00"
            r["<OPEN>"] = r["<HIGH>"] = r["<LOW>"] = r["<CLOSE>"] = row["<CLOSE>"]; r["<TICKVOL>"] = "0"; r["<SPREAD>"] = "0"
            add.append(r)
    out = pd.concat([ex, pd.DataFrame(add)], ignore_index=True)
    k = pd.to_datetime(out["<DATE>"] + " " + out["<TIME>"], format="%Y.%m.%d %H:%M:%S")
    print("  Dukascopy-NAS: flach ergaenzte Kerzen 16:15-16:55 NY:", len(add))
    return out.iloc[np.argsort(k.values, kind="stable")].reset_index(drop=True)


duka = read("NAS100_duka_M5.csv", NAHT, "2026-08-29")
duka["<SPREAD>"] = "0"                                       # nur relativer Spread (siehe oben)
nas = pd.concat([spread(read(gext.FILES["NAS"], "2022-01-03", NAHT), "NAS"),
                 spread(fill_close(duka), "NAS")], ignore_index=True)
for sym, ex in (("XAU", xau), ("NAS", nas)):
    out = os.path.join(P.DATA, P.FILES[sym])
    ex.to_csv(out, sep="\t", index=False, lineterminator="\r\n")
    print(sym, "->", out, len(ex), "Kerzen", ex["<DATE>"].iloc[0], "..", ex["<DATE>"].iloc[-1],
          "Spread-Median", float(np.median(ex["<SPREAD>"].astype(int))), "Punkte")
