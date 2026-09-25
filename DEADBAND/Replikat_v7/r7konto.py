"""RSI21-Labor: Kontobewertung (Replikat v6, eng6/evl6) mit einer beliebigen RSI21-Signalliste.

Ziel 'gft' = Ersatz-GFT-Daten 2022-01-03 .. 2025-12-31 (../data, siehe mk_ersatz_gft.py), 'ext' = Fremddaten 2006-2021.
Alles andere wie x39 (Build 6.10): 10 Fades mit Waechter, Noise, Auszahlung ab 3 %, strenge Regel-Lesart."""
import os, sys, pickle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V6 = os.path.join(os.path.dirname(HERE), "Replikat_v6")
sys.path.insert(0, V6)
os.chdir(V6)                       # x35 liest die EA relativ zu Replikat_v6
import eng6 as E, evl6 as V, r6, prep5 as P, x35 as X          # noqa: E402
import r7sig as G                                               # noqa: E402

F10 = X.F10
B = dict(r6.C510, **r6.PAY3)
RES = 0.505
ERTRAG = dict(B, validpct=RES, db_on=0, r21_risk=0.5, nz_risk=0.35, cool_n=3, gesamtbudget=0.9, idea_cap=0.9,
              bank_on=1, bank_last=3, bank_minr=0.3, bank_mods=15)
GPX = dict(harv=1)

_CACHE = {}


def dataset(target):
    """(D, S, blocks) je Ziel; S = Signale der alten Module (sig5)."""
    if target in _CACHE:
        return _CACHE[target]
    if target == "ext":
        D = pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb"))
        S = pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb"))
    else:
        import gsig
        D = gsig.data()
        S = pickle.load(open(os.path.join(P.OUT, "sig5.pkl"), "rb"))
    blks = X.blocks_filtered(F10, target)
    _CACHE[target] = (D, S, blks)
    return _CACHE[target]


def evaluate(target, r21=None, kw=None, gpx=None, quick=True, seeds=None, horizons=(250, 500, 750)):
    """r21: Signalliste (r7sig.r21_dict) oder None = sig5 (Basis). kw: Aenderungen an ERTRAG."""
    D, S, blks = dataset(target)
    S2 = dict(S)
    if r21 is not None:
        S2["r21"] = r21
    V._MK = E.Market(D=D, S=S2)
    GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **(GPX if gpx is None else gpx)) for _ in F10])
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **dict(ERTRAG, **(kw or {}))))
    if target == "ext":
        r = V.evaluate(Pv, GP=GP, horizons=horizons, step=9, seeds=seeds or (0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
    else:
        if quick:
            r = V.evaluate(Pv, GP=GP, horizons=horizons, step=3, seeds=seeds or tuple(range(8)), skip=0.08)
        else:
            r = V.evaluate(Pv, GP=GP, horizons=horizons, step=3, seeds=seeds or tuple(range(16)), skip=0.08)
    return r["mean"]
