"""Durchgehender Datensatz fuer die Grid-Studie: Fremddaten 2006-2025 (Gold ab 2006, NAS100 ab 2005) in einem Stueck,
Spread wie gext (max(Datei, relativer GFT-Spread)). 2022-2025 ist damit derselbe Kurs wie der GFT-Ersatz (mk_proxy)."""
import numpy as np, os, pickle
import gext, gsig as G, prep5 as P, cands as K

_ALL = None


def data_all(until="2026-01-01"):
    global _ALL
    if _ALL is None:
        f = os.path.join(P.OUT, "DXall.pkl")
        if os.path.exists(f):
            _ALL = pickle.load(open(f, "rb"))
        else:
            _ALL = {s: gext.load(s, until=until) for s in ("XAU", "NAS")}
            pickle.dump(_ALL, open(f, "wb"))
    return _ALL


def use_all():
    G._D = data_all()
    K._CACHE.clear()


def year_of(t_ny):
    return (np.asarray(t_ny) // 1440 // 365.25 + 1970).astype(int)
