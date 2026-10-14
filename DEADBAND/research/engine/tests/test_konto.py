"""Konto-Ebene auf synthetischen Daten: Familienstrom in eng6, durchgehender Tageslauf, Tagesdatensaetze und Bootstrap.
Keine Forschungsaussage (synthetische Kurse, nur Konsistenz)."""
import numpy as np
import pytest

from engine import bootstrap as BS
from engine import familien as FA
from engine import konto as KO
from engine import signale as SG
from engine import tage as TG


@pytest.fixture(scope="module")
def lauf(daten):
    import eng6 as E
    mk = E.Market(D=daten, S=None)
    d = daten["NAS"]
    atr = SG.indikatoren_m15(d)
    sig = FA.f3_asien(d, atr, 0.65, m=1e9)
    blk = KO.familien_block(d, "NAS", sig, 0, stoplvl=1.5)
    gps = [KO.familien_gp("NAS")]
    (tag, X), r = KO.tageslauf(mk, [blk], gps, maxlosspct=0.3, ddfull=0.0)  # enger Boden: Bodenverletzungen kommen vor
    return mk, blk, tag, X, r


def test_familienblock_zeit_exit_und_ziel(daten, lauf):
    mk, blk, *_ = lauf
    assert len(blk["t_entry"]) > 20
    assert (blk["t_exit"] > blk["t_entry"]).all()
    assert blk["tp"] == 10.0
    assert (blk["t_exit"] - blk["t_entry"] >= 192 * 15).all()   # 192 M15-Kerzen (laenger ueber Pausen/Wochenenden)


def test_tageslauf_ohne_auszahlung_und_ohne_kontoende(lauf):
    import eng6 as E
    mk, blk, tag, X, r = lauf
    t = r["tage"]
    Kd = {n: i for i, n in enumerate(E.KDN)}
    assert (t[:, Kd["auszahlung"]] <= 0).all()
    assert (t[:, Kd["neukonto"]] <= 0).all()
    assert (t[:, Kd["pleite"]] > 0).sum() >= 1                 # Bodenverletzung erkannt, Konto laeuft weiter
    ev = r["ev"] if "ev" in r else None
    if ev is not None and len(ev):
        assert not (ev[:, 0] == 2).any()                       # kein Pleite-Ereignis
    assert len(r["tr"]) > 10
    # Tagesaenderungen summieren sich zur Equity-Aenderung (Faktor je Tag zurueckgerechnet)
    f = t[:, Kd["fak0"]].copy(); f[~(f > 0)] = 1.0
    assert np.isclose((X[:, TG.FI["dE"]] * f).sum(), t[-1, Kd["equity"]] - t[0, Kd["saldo0"]])
    assert (X[:, TG.FI["dmin"]] <= np.minimum(X[:, TG.FI["dE"]], 0) + 1e-9).all()
    assert (X[:, TG.FI["dmax"]] >= np.maximum(X[:, TG.FI["dE"]], 0) - 1e-9).all()


def test_bootstrap_auf_tageslauf(lauf):
    mk, blk, tag, X, r = lauf
    erg = BS.bewerte(X, bloecke=(1, 5), pfade_n=100)
    for b in (1, 5):
        k = erg[b]
        assert k["pfade"] == 100 and np.isfinite(k["netto_monat"])
        assert k["aus_jahr"] >= 0 and k["pleiten_jahr"] >= 0


def test_ausrichten_gepaart():
    tag1 = np.array([1, 2, 3, 5]); tag2 = np.array([2, 3, 4, 5])
    X1 = np.arange(4)[:, None] * np.ones((1, len(TG.FELDER))); X2 = 10 + X1
    gem, (A, B) = TG.ausrichten((tag1, X1), (tag2, X2))
    assert list(gem) == [2, 3, 5]
    assert list(A[:, 0]) == [1, 2, 3] and list(B[:, 0]) == [10, 11, 13]
