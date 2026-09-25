"""RSI21 Eigenkapital - durchgehender Kursdatensatz XAUUSD + NAS100 (M5, NY-Zeit), 2006-03 bis 2026-08.

Quellen (extdata/DATEN_BERICHT.md, alle CSV im MT5-Format, Serverzeit = New York + 7 h):
  Gold    XAUUSD_ext_M5.csv          2006-03-20 .. 2026-09-02 (OANDA / Dukascopy)
  NAS100  NAS100_ext_M5.csv          2005-01-03 .. NAHT       (OANDA / HistData / MT5-Broker US100)
          NAS100_duka_M5.csv         NAHT .. 2026-08-28       (Dukascopy-Ticks; Kerzen 16:15-16:55 NY flach ergaenzt,
                                                               wie Replikat_v6/mk_proxy2026.py)
NAHT = 2026-01-01 (Neujahr): 2025 kommt aus dem Broker-Export (naeher an GFT als Dukascopy, Datenbericht Abschnitt 10),
2026 aus Dukascopy.

Spread wie Replikat_v6/gext.load: max(Datei-Spread, Kurs x relativer GFT-Spread 2022-26) ("breit"); im Dukascopy-Teil nur
der relative Spread (wie mk_proxy2026). SPREAD_FAKTOR (Umgebung) skaliert alle Spreads (0,6 = GFT-nah).

Zeitachse wie prep5: NY-Minuten seit Epoche (int64), Kurse = Bid, Spread in Preis-Einheiten. Balken M15/M30/H1 aus M5
(prep5.agg), Tagesbalken = Servertag (17:00 NY bis 17:00 NY).

Aufruf: python ek_data.py   -> cache/D.pkl (wird von ek_sig/ek_sim geladen)
"""
import os, sys, pickle
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Replikat_v6"))
import prep5 as P                                                   # noqa: E402

EXT = os.environ.get("DEADBAND_EXT", os.path.join(os.path.dirname(HERE), "extdata"))
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
REL_SPREAD = {"XAU": 0.32 / 2000.0, "NAS": 1.63 / 15000.0}        # wie gext.REL_SPREAD
NAHT = os.environ.get("EK_NAHT", "2026-01-01")
BIS = "2026-09-03"
SF = float(os.environ.get("SPREAD_FAKTOR", "1.0"))


def _read(fn, a=None, b=None):
    ex = pd.read_csv(os.path.join(EXT, fn), sep="\t", dtype=str)
    t = pd.to_datetime(ex["<DATE>"] + " " + ex["<TIME>"], format="%Y.%m.%d %H:%M:%S")
    keep = np.ones(len(ex), bool)
    if a is not None:
        keep &= (t >= pd.Timestamp(a)).values
    if b is not None:
        keep &= (t < pd.Timestamp(b)).values
    return ex[keep].reset_index(drop=True)


def _fill_close(ex):
    """wie mk_proxy2026.fill_close: flache Kerzen 23:15-23:55 Server (16:15-16:55 NY) an Tagen, deren letzte Kerze 23:10 ist."""
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
    return out.iloc[np.argsort(k.values, kind="stable")].reset_index(drop=True), len(add)


def _to_arrays(ex, sym):
    t = pd.to_datetime(ex["<DATE>"] + " " + ex["<TIME>"], format="%Y.%m.%d %H:%M:%S")
    ny = (t - pd.Timedelta(hours=7)).values.astype("datetime64[m]").astype(np.int64)
    o = ex["<OPEN>"].astype(float).to_numpy(); h = ex["<HIGH>"].astype(float).to_numpy()
    l = ex["<LOW>"].astype(float).to_numpy(); c = ex["<CLOSE>"].astype(float).to_numpy()
    sp = ex["<SPREAD>"].astype(float).to_numpy() * P.POINT
    rel = REL_SPREAD[sym] * c
    sp = np.where(np.isnan(sp) | (sp <= 0), rel, np.maximum(sp, rel)) * SF
    v = ex["<TICKVOL>"].astype(float).to_numpy()
    order = np.argsort(ny, kind="stable")
    return dict(ny=ny[order], o=o[order], h=h[order], l=l[order], c=c[order], sp=sp[order], v=v[order])


def build():
    xau = _read("XAUUSD_ext_M5.csv", None, BIS)
    nas_a = _read("NAS100_ext_M5.csv", None, NAHT)                     # ab 2005: volle SMA200-Historie ab 2006
    duka, nfill = _fill_close(_read("NAS100_duka_M5.csv", NAHT, BIS))
    duka["<SPREAD>"] = "0"                                              # nur relativer Spread (wie mk_proxy2026)
    nas = pd.concat([nas_a, duka], ignore_index=True)
    D = {}
    for s, ex in (("XAU", xau), ("NAS", nas)):
        d = _to_arrays(ex, s)
        ny = d["ny"]
        d["pday"] = (ny + 420) // 1440
        for key, mins in (("m15", 15), ("m30", 30), ("h1", 60)):
            d[key] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], mins)
        d["d1"] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 1440, offset=420)
        D[s] = d
        print(f"{s}: {len(ny)} M5  {np.datetime64(int(ny[0]), 'm')} .. {np.datetime64(int(ny[-1]), 'm')} NY, "
              f"Spread-Median {np.median(d['sp']):.3f}")
    print(f"NAS: Naht {NAHT}, Dukascopy flach ergaenzt {nfill} Kerzen")
    D["meta"] = dict(naht=NAHT, bis=BIS, spread_faktor=SF)
    return D


def load(name="D.pkl"):
    f = os.path.join(CACHE, name)
    if not os.path.exists(f):
        D = build()
        with open(f, "wb") as fh:
            pickle.dump(D, fh)
    with open(f, "rb") as fh:
        return pickle.load(fh)


if __name__ == "__main__":
    f = os.path.join(CACHE, "D.pkl")
    if os.path.exists(f):
        os.remove(f)
    load()
