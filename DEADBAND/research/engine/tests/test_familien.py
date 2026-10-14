"""Familien-Generatoren: nur abgeschlossene Kerzen, Einstieg am Open der Folgekerze, Regeln laut PLAN.md 6.1-6.4.
Daten synthetisch (conftest.daten), keine Forschungsaussage."""
import numpy as np
import pandas as pd
import pytest

from engine import familien as FA
from engine import signale as SG


@pytest.fixture(scope="module")
def nas(daten):
    d = daten["NAS"]
    return d, SG.indikatoren_m15(d)


def _einstieg_nach_signal(d, s):
    B = d["m15"]
    assert np.array_equal(s["i5"], B["first"][s["j"] + 1])               # erste M5 der Folgekerze
    assert (d["ny"][s["i5"]] >= s["t_sig"] + 15).all()                   # Signalkerze ist abgeschlossen
    assert np.allclose(s["rd"], 3.0 * SG.indikatoren_m15(d)[s["j"]])


# ---------------------------------------------------------------- F1
def _kalender(pfad, zeilen):
    kopf = "server_time\tvalue_id\tevent_id\tcode\tname\timportance\ttime_mode\tactual\tforecast\tprev\trevised_prev\timpact\n"
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(kopf)
        for i, (ny, code, imp, mode) in enumerate(zeilen):
            server = (pd.Timestamp(ny) + pd.Timedelta(hours=7)).strftime("%Y.%m.%d %H:%M:%S")
            f.write(f"{server}\t{i}\t{i}\t{code}\t{code}\t{imp}\t{mode}\t1\t1\t1\t\t0\n")


def test_f1_kalender_und_signal(nas, tmp_path):
    d, atr = nas
    p = tmp_path / "kal.csv"
    _kalender(p, [("2021-05-12 08:30", "cpi-mm", 3, 0), ("2021-05-12 08:30", "core-cpi-mm", 3, 0),   # gleiche Uhrzeit
                  ("2021-05-13 08:30", "ppi-mm", 3, 0),                                              # PPI zaehlt nicht
                  ("2021-06-04 08:30", "nonfarm-payrolls", 3, 0), ("2021-06-16 14:00", "fed-interest-rate-decision", 3, 0),
                  ("2021-06-25 08:30", "pce-price-index-mm", 3, 0),
                  ("2021-07-02 08:30", "nonfarm-payrolls", 2, 0),                                    # Bedeutung mittel
                  ("2021-07-13 08:30", "cpi-mm", 3, 1)])                                             # ohne Uhrzeit
    ny, kl = FA.kalender_termine(str(p))
    assert list(kl) == ["CPI", "NFP", "FOMC", "PCE"]
    erw = [pd.Timestamp(x).to_datetime64().astype("datetime64[m]").astype(np.int64)
           for x in ("2021-05-12 08:30", "2021-06-04 08:30", "2021-06-16 14:00", "2021-06-25 08:30")]
    assert list(ny) == erw
    s0 = FA.f1_ereignis(d, atr, ny, k=0.0)
    B = d["m15"]
    assert list(s0["t_sig"]) == erw                                      # Kerze, die zur Veroeffentlichung beginnt
    assert np.array_equal(s0["dir"], np.sign(B["c"][s0["j"]] - B["o"][s0["j"]]).astype(int))
    _einstieg_nach_signal(d, s0)
    assert (d["ny"][s0["i5"]] % 1440 == np.array(erw) % 1440 + 15).all()  # 8:45 bzw. 14:15
    assert len(FA.f1_ereignis(d, atr, ny, k=1e9)["j"]) == 0
    s1 = FA.f1_ereignis(d, atr, ny, k=0.5)
    koerper = np.abs(B["c"][s1["j"]] - B["o"][s1["j"]])
    assert (koerper >= 0.5 * atr[s1["j"] - 1]).all()


# ---------------------------------------------------------------- F2
def test_f2_retest(nas):
    d, atr = nas
    h1 = SG.h1_signale(d, 0.65, True, 0.01, 1.5)
    s = FA.f2_retest(d, atr, h1, 0.65)
    assert len(s["j"]) > 0
    _einstieg_nach_signal(d, s)
    B = d["m15"]
    for j, dd in zip(s["j"], s["dir"]):
        a = np.nonzero((h1["j"] < j) & (h1["j"] >= j - 8) & (h1["dir"] == dd))[0]
        assert len(a) > 0                                                # Ausbruchssignal hoechstens W Kerzen davor
        kante = h1["hH1"][a] if dd > 0 else h1["lH1"][a]
        assert np.any(B["c"][j] > kante) if dd > 0 else np.any(B["c"][j] < kante)
    assert len(FA.f2_retest(d, atr, h1, 0.65, W=0)["j"]) == 0


# ---------------------------------------------------------------- F3
def test_f3_asien(nas):
    d, atr = nas
    s = FA.f3_asien(d, atr, 0.65, m=0.6)
    gross = FA.f3_asien(d, atr, 0.65, m=1e9)
    assert len(gross["j"]) > len(s["j"]) > 0
    assert len(FA.f3_asien(d, atr, 0.65, m=0.0)["j"]) == 0
    _einstieg_nach_signal(d, s)
    t = s["t_sig"] % 1440
    assert ((t >= 180) & (t < 300)).all()                                # Signalkerze 03:00-05:00 NY
    assert len(np.unique(s["t_sig"] // 1440)) == len(s["j"])              # ein Signal je NY-Tag
    B = d["m15"]
    for j, dd in zip(s["j"], s["dir"]):
        D = B["t"][j] // 1440
        m = (B["t"] >= D * 1440 - 360) & (B["t"] < D * 1440 + 180)
        assert (B["c"][j] > B["h"][m].max()) if dd > 0 else (B["c"][j] < B["l"][m].min())


# ---------------------------------------------------------------- F4
def test_f4_donchian(nas):
    d, atr = nas
    s = FA.f4_donchian(d, atr, N=20)
    assert len(s["j"]) > 0
    _einstieg_nach_signal(d, s)
    d1 = d["d1"]
    t_ein = d["ny"][s["i5"]]
    assert (t_ein % 1440 >= 180).all() and (t_ein % 1440 < 13 * 60).all()
    assert (((t_ein // 1440) + 4) % 7 != 0).all()                        # nie die Sonntags-Wiedereroeffnung
    for te, dd in zip(t_ein, s["dir"]):
        i = int(np.searchsorted(d1["key"], (te + 420) // 1440)) - 1      # letzter abgeschlossener Servertag
        while i >= 20:
            hoch, tief = d1["h"][i - 20:i].max(), d1["l"][i - 20:i].min()
            if (d1["c"][i] > hoch and dd > 0) or (d1["c"][i] < tief and dd < 0):
                break
            i -= 1                                                       # Freitag/Feiertag: Signal liegt weiter zurueck
        assert i >= 20
        assert d1["key"][i] * 1440 + 17 * 60 <= te                       # Tagesschluss liegt vor dem Einstieg
        assert te - (d1["key"][i] * 1440 + 17 * 60) < 4 * 1440
