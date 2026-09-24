"""Externe Daten (vor 2022) im selben Format wie prep5/gsig: zur Pruefung ausserhalb des Suchzeitraums."""
import numpy as np, pandas as pd, os, pickle
import prep5 as P, gsig as G

EXT = os.environ.get("DEADBAND_EXT", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extdata"))
FILES = {"XAU": "XAUUSD_ext_M5.csv", "NAS": "NAS100_ext_M5.csv"}
REL_SPREAD = {"XAU": 0.32 / 2000.0, "NAS": 1.63 / 15000.0}      # Spread proportional zum Kurs (Stand 2022-26)
_DX = None


def load(sym, until="2022-01-01"):
    ex = pd.read_csv(os.path.join(EXT, FILES[sym]), sep="\t")
    ex.columns = [c.strip("<>").lower() for c in ex.columns]
    t = pd.to_datetime(ex["date"] + " " + ex["time"], format="%Y.%m.%d %H:%M:%S")
    ny = (t - pd.Timedelta(hours=7)).values.astype("datetime64[m]").astype(np.int64)
    o = ex["open"].to_numpy(float); h = ex["high"].to_numpy(float); l = ex["low"].to_numpy(float); c = ex["close"].to_numpy(float)
    sp = ex["spread"].to_numpy(float) * P.POINT
    rel = REL_SPREAD[sym] * c
    sp = np.where(np.isnan(sp) | (sp <= 0), rel, np.maximum(sp, rel))
    v = ex["tickvol"].to_numpy(float)
    lim = np.datetime64(until, "m").astype(np.int64)
    keep = ny < lim
    order = np.argsort(ny[keep], kind="stable")
    d = dict(ny=ny[keep][order], o=o[keep][order], h=h[keep][order], l=l[keep][order], c=c[keep][order], sp=sp[keep][order], v=v[keep][order])
    d["d1"] = P.agg(d["ny"], d["o"], d["h"], d["l"], d["c"], d["v"], 1440, offset=420)
    return d


def data_ext():
    global _DX
    if _DX is None:
        f = os.path.join(P.OUT, "DX.pkl")
        if os.path.exists(f):
            _DX = pickle.load(open(f, "rb"))
        else:
            _DX = {s: load(s) for s in ("XAU", "NAS")}
            pickle.dump(_DX, open(f, "wb"))
    return _DX


def use_ext():
    """gsig/scan6 auf die externen Daten umstellen (Prozess-global)."""
    G._D = data_ext()
