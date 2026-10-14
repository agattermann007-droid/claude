"""GFT-Bootstrap: Kontoregeln mit konstruierten Tagesdatensaetzen und Gleichheit mit einer Python-Referenz."""
import numpy as np
import pytest

from engine import bootstrap as BS
from engine import konfig as K
from engine.tage import FELDER, FI


def _tage(n, **spalten):
    X = np.zeros((n, len(FELDER)))
    X[:, FI["gap"]] = 1.0
    X[:, FI["akt"]] = 1.0
    for k, v in spalten.items():
        X[:, FI[k]] = v
    return X


def _lauf(X):
    idx = np.arange(len(X), dtype=np.int64)[None, :]
    return BS.pfade(X, idx)[0]


def test_indizes_kreisbloecke():
    idx = BS.indizes(100, 5, pfade=50, tage=252, seed=3)
    assert idx.shape == (50, 252)
    d = np.diff(idx.reshape(50, -1)[:, :250].reshape(50, 50, 5), axis=2) % 100
    assert (d == 1).all()                                     # innerhalb eines Blocks aufeinanderfolgend (umlaufend)
    assert np.array_equal(idx, BS.indizes(100, 5, pfade=50, tage=252, seed=3))


def test_auszahlung_reife_deckel_und_wartetage():
    X = _tage(40, dE=60.0, real=60.0, dmax=60.0)
    r = _lauf(X)
    # Tag 1 Zyklusbeginn; Tag 11 reif (5 gueltige Tage, 10 Kalendertage, 660 $ >= 131,25 $); Tag 12 flach;
    # Tag 13 Auszahlung 600 $ (Deckel 6 %), dann wird an Tag 13 wieder gehandelt
    assert r[0] >= 1 and r[1] >= 600.0
    X2 = _tage(13, dE=60.0, real=60.0, dmax=60.0)
    r2 = _lauf(X2)
    assert r2[0] == 1 and r2[1] == pytest.approx(600.0)
    assert r2[5] == pytest.approx(660.0 - 600.0 + 60.0)      # Rest nach dem Deckel + Tag 13
    X3 = _tage(12, dE=60.0, real=60.0, dmax=60.0)
    assert _lauf(X3)[0] == 0                                  # Tag 12: noch keine Auszahlung


def test_gueltiger_tag_schwelle():
    X = _tage(30, dE=50.0, real=50.0, dmax=50.0)              # 50 $ < 50,50 $ -> nie gueltig
    r = _lauf(X)
    assert r[0] == 0 and r[4] == 0


@pytest.mark.parametrize("spalte,wert,pleite", [("dmin", -599.0, False), ("dmin", -601.0, True),
                                                 ("flt", -99.0, False), ("flt", -101.0, True)])
def test_boden_und_floating(spalte, wert, pleite):
    X = _tage(3, dE=0.0)
    X[1, FI[spalte]] = wert
    if spalte == "dmin":
        X[1, FI["ref"]] = -1e9                                # Tagesregel hier ausschalten
    assert _lauf(X)[2] == (1 if pleite else 0)


def test_tagesregel_gegen_referenz():
    X = _tage(3, dE=0.0)
    X[1, FI["dmin"]] = -250.0
    X[1, FI["ref"]] = 60.0                                    # offener Gewinn zu Tagesbeginn hebt die Referenz
    assert _lauf(X)[2] == 1                                   # 9750 - 10060 = -310 <= -301,8
    X[1, FI["ref"]] = 0.0
    assert _lauf(X)[2] == 0


def test_boden_steigt_zuerst_mit_dem_hoch():
    X = _tage(3, dE=0.0)
    X[1, FI["dmax"]] = 300.0; X[1, FI["dmin"]] = -301.0; X[1, FI["ref"]] = -1e9
    assert _lauf(X)[2] == 1                                   # Hoch 10300 -> Boden 9700; Tief 9699


def test_pufferkurve_und_unter_start():
    X = _tage(3, dE=0.0)
    X[0, FI["dE"]] = -400.0; X[0, FI["dmin"]] = -400.0; X[0, FI["ref"]] = -1e9
    X[1, FI["dE"]] = 100.0; X[1, FI["dmax"]] = 100.0
    r = _lauf(X)
    f = (0.1 + 0.9 * (2.0 - 1.25) / (3.5 - 1.25)) * 0.95       # Puffer 2 %, unter Start
    assert r[5] == pytest.approx(-400.0 + 100.0 * f)


def test_neues_konto_nach_pause():
    X = _tage(5, dE=10.0, dmax=10.0)
    X[1, FI["dmin"]] = -700.0
    r = _lauf(X)
    assert r[2] == 1
    assert r[5] == pytest.approx(3 * 10.0)                    # Tag 2 Pleite (Rest flach), ab Tag 3 neues Konto


# ---------------------------------------------------------------- Referenz in reinem Python
def _referenz(X, idx, cfg):
    start, boden, fpct, tpct, needday, needvalid, zyklus, minprofit, deckel_pct, deckel_n, w_aus, w_neu, voll, mi, ff, un = cfg
    abstand = start * boden / 100; deckel = start * deckel_pct / 100
    out = []
    for pf in idx:
        eq = peak = start; modus = 0; warte = 0; g = 0; zyk = None; n_acc = 0; kal = 0.0
        n_aus = s_aus = n_pl = n_g = 0.0
        for d in pf:
            x = dict(zip(FELDER, X[d]))
            kal += x["gap"]
            if modus == 2:
                warte -= 1
                if warte > 0:
                    continue
                a = max(0.0, min(eq - start, deckel) if n_acc < deckel_n else eq - start)
                eq -= a; peak = eq; n_aus += 1; s_aus += a; n_acc += 1; g = 0; zyk = None; modus = 0
            elif modus == 3:
                warte -= 1
                if warte > 0:
                    continue
                eq = peak = start; n_acc = 0; g = 0; zyk = None; modus = 0
            buf = (eq - (peak - abstand)) / start * 100
            f = 1.0 if buf >= voll else (ff if buf <= mi else ff + (1 - ff) * (buf - mi) / (voll - mi))
            if eq < start:
                f *= un
            e0 = eq
            peak = max(peak, e0 + x["dmax"] * f)
            tief = e0 + x["dmin"] * f
            sal = e0 + x["bal"] * f
            fb = start if sal >= start else sal
            ref = e0 + x["ref"] * f
            if tief <= peak - abstand or x["flt"] * f <= -fb * fpct / 100 or tief - ref <= -ref * tpct / 100:
                n_pl += 1; modus = 3; warte = w_neu
                continue
            eq = e0 + x["dE"] * f
            if x["akt"] > 0.5 and zyk is None:
                zyk = kal
            if x["real"] * f >= needday:
                g += 1; n_g += 1
            if g >= needvalid and zyk is not None and kal - zyk >= zyklus and eq - start >= minprofit:
                modus = 2; warte = w_aus
        out.append((n_aus, s_aus, n_pl, kal, n_g))
    return np.array(out)


def test_gleich_referenz_zufallsdaten():
    rng = np.random.default_rng(5)
    n = 400
    dE = rng.normal(25.0, 140.0, n)
    X = _tage(n, dE=dE, real=dE * rng.uniform(0.5, 1.0, n), dmin=np.minimum(dE, 0) - rng.exponential(60.0, n),
              dmax=np.maximum(dE, 0) + rng.exponential(60.0, n), flt=-rng.exponential(30.0, n),
              ref=np.maximum(rng.normal(0, 20, n), 0), bal=rng.normal(0, 20, n))
    X[:, FI["gap"]] = np.where(rng.random(n) < 0.2, 3.0, 1.0)
    X[:, FI["akt"]] = (rng.random(n) < 0.9).astype(float)
    idx = BS.indizes(n, 5, pfade=60, tage=252, seed=9)
    a = BS.pfade(X, idx)
    b = _referenz(X, idx, BS.cfg_vektor())
    assert np.allclose(a[:, :5], b)
    assert a[:, 0].sum() > 20 and a[:, 2].sum() > 5          # Auszahlungen und Pleiten kommen vor


def test_kennzahlen_und_gepaarter_vergleich():
    rng = np.random.default_rng(6)
    n = 300
    dE = rng.normal(30.0, 120.0, n)
    Xb = _tage(n, dE=dE, real=dE, dmin=np.minimum(dE, 0) - 30, dmax=np.maximum(dE, 0) + 30)
    erg = BS.vergleich(Xb, Xb.copy(), bloecke=(1, 5), pfade_n=200)
    for b in (1, 5):
        assert erg[b]["diff_netto_monat"] == 0.0 and erg[b]["anteil_besser"] == 0.0
        k = erg[b]["baseline"]
        assert k["aus_jahr"] > 0 and np.isfinite(k["netto_monat"])
        assert k["bpp"] == pytest.approx(k["pleiten_jahr"] / k["aus_jahr"])
    Xk = Xb.copy(); Xk[:, FI["dE"]] += 5.0; Xk[:, FI["real"]] += 5.0; Xk[:, FI["dmax"]] += 5.0
    erg2 = BS.vergleich(Xb, Xk, bloecke=(5,), pfade_n=200)
    assert erg2[5]["diff_netto_monat"] > 0
