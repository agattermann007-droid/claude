"""signale.h1_signale == sig5.db_candidates (Replikat) fuer Gold und NAS; einzelpfad haelt die Regeln des H1-Moduls ein.
Daten synthetisch (conftest.daten), keine Forschungsaussage."""
import numpy as np
import pytest

from engine import handel as HD
from engine import signale as SG
from engine import spec as SP


@pytest.mark.parametrize("kurz,clsmin,short,stoplvl", [("XAU", 0.70, False, 5 * 0.01), ("NAS", 0.65, True, 150 * 0.01)])
def test_h1_signale_gleich_sig5(daten, kurz, clsmin, short, stoplvl):
    import sig5
    alt = sig5.db_candidates(daten, kurz, clsmin, short)
    neu = SG.h1_signale(daten[kurz], clsmin, short, 0.01, stoplvl)
    assert len(alt["T"]) > 20
    for f in ("T", "dir", "m15", "i5"):
        assert np.array_equal(alt[f], neu[f]), f
    for f in ("rd", "f", "nyh"):
        assert np.allclose(alt[f], neu[f], rtol=0, atol=1e-12), f
    assert np.array_equal(neu["j"], neu["m15"] - 1)
    if not short:
        assert (neu["dir"] > 0).all()


def test_baue_symbol_gleich_prep5(daten):
    d = daten["XAU"]
    e = SG.baue_symbol(d["ny"], d["o"], d["h"], d["l"], d["c"], d["v"], d["sp"])
    for tf in ("m15", "h1", "d1"):
        for f in ("t", "o", "h", "l", "c", "first"):
            assert np.array_equal(e[tf][f], d[tf][f]), (tf, f)


def test_einzelpfad_regeln(daten):
    d = daten["XAU"]
    sig = SG.h1_signale(d, 0.70, False, 0.01, 0.05)
    M = HD.markt_arrays(d["ny"], d["o"], d["h"], d["l"], d["c"], d["sp"])
    idx, erg = SG.einzelpfad(sig, M, SP.XAU, 8.0)
    assert len(idx) > 5
    ein = sig["i5"][idx]
    # Session 3-13 NY, hoechstens ein Trade je Prop-Tag, nie zwei Positionen gleichzeitig
    assert ((sig["nyh"][idx] >= 3.0) & (sig["nyh"][idx] < 13.0)).all()
    assert len(np.unique(M["pday"][ein])) == len(ein)
    assert (ein[1:] > erg[:-1, 2]).all()
    # Ergebnis = derselbe Trade einzeln simuliert
    e0 = HD.handel(M, SP.XAU, [ein[0]], [sig["dir"][idx[0]]], [sig["rd"][idx[0]]], 8.0)[0]
    assert np.allclose(e0, erg[0])
