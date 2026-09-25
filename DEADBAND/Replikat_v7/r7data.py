"""RSI21-Labor: Kursdaten 2006-2026 (Fremddaten aus ../extdata, MT5-Format, Serverzeit = NY + 7 h) im Format von prep5.

Zeit = NY-Minuten seit Epoche, Kurse = Bid, Spread in Preis-Einheiten. Spread wie gext: max(Datei-Spread, Kurs x
REL_SPREAD) - Dukascopy-/OANDA-Spreads sind breiter bzw. unbekannt, die Untergrenze ist der GFT-Stand 2022-26.
Aggregate M15/M30/H1 (NY-Uhr) und D1 (Servertag 17:00-17:00 NY) wie prep5.build()."""
import os, sys, pickle
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Replikat_v6"))
import prep5 as P          # noqa: E402

EXT = os.environ.get("DEADBAND_EXT", os.path.join(os.path.dirname(HERE), "extdata"))
FILES = {"XAU": "XAUUSD_ext_M5.csv", "NAS": "NAS100_ext_M5.csv"}
REL_SPREAD = {"XAU": 0.32 / 2000.0, "NAS": 1.63 / 15000.0}
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
END = "2026-01-01"          # NAS100_ext endet 2025-12-31; beide Symbole gleich lang


def load(sym, start="2006-01-01", end=END):
    ex = pd.read_csv(os.path.join(EXT, FILES[sym]), sep="\t")
    ex.columns = [c.strip("<>").lower() for c in ex.columns]
    t = pd.to_datetime(ex["date"] + " " + ex["time"], format="%Y.%m.%d %H:%M:%S")
    ny = (t - pd.Timedelta(hours=7)).values.astype("datetime64[m]").astype(np.int64)
    o = ex["open"].to_numpy(float); h = ex["high"].to_numpy(float); l = ex["low"].to_numpy(float); c = ex["close"].to_numpy(float)
    sp = ex["spread"].to_numpy(float) * P.POINT
    rel = REL_SPREAD[sym] * c
    sp = np.where(np.isnan(sp) | (sp <= 0), rel, np.maximum(sp, rel))
    v = ex["tickvol"].to_numpy(float)
    a = np.datetime64(start, "m").astype(np.int64); b = np.datetime64(end, "m").astype(np.int64)
    keep = (ny >= a) & (ny < b)
    order = np.argsort(ny[keep], kind="stable")
    d = {k: x[keep][order] for k, x in dict(ny=ny, o=o, h=h, l=l, c=c, sp=sp, v=v).items()}
    d["pday"] = (d["ny"] + 420) // 1440
    for key, mins in (("m15", 15), ("m30", 30), ("h1", 60)):
        d[key] = P.agg(d["ny"], d["o"], d["h"], d["l"], d["c"], d["v"], mins)
    d["d1"] = P.agg(d["ny"], d["o"], d["h"], d["l"], d["c"], d["v"], 1440, offset=420)
    return d


_D = None


def data():
    """beide Symbole 2006-2025 (Cache cache/DA.pkl)."""
    global _D
    if _D is None:
        f = os.path.join(CACHE, "DA.pkl")
        if os.path.exists(f):
            _D = pickle.load(open(f, "rb"))
        else:
            _D = {s: load(s) for s in ("XAU", "NAS")}
            pickle.dump(_D, open(f, "wb"))
    return _D


if __name__ == "__main__":
    D = data()
    for s, d in D.items():
        ny = d["ny"]
        print(s, len(ny), np.datetime64(int(ny[0]), "m"), np.datetime64(int(ny[-1]), "m"),
              "Spread-Median je Jahr:", {int(y): round(float(np.median(d["sp"][(ny // 525960 + 1970) == y])), 3)
                                         for y in range(2006, 2026, 4)})
