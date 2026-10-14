"""Zufallsvergleich: Mechanik, Seeds, Trennschaerfe (ein Signal mit Blick in die Zukunft muss bestehen).
Daten synthetisch (conftest.daten), keine Forschungsaussage."""
import numpy as np

from engine import familien as FA
from engine import signale as SG
from engine import spec as SP
from engine import zufall as ZF


def test_ohne_ueberlappung():
    ein = np.array([10, 5, 20, 30, 31]); aus = np.array([25, 8, 22, 40, 33])
    assert list(ZF.ohne_ueberlappung(ein, aus)) == [1, 0, 3]


def test_vergleich_mechanik_und_seed(daten):
    d = daten["NAS"]
    atr = SG.indikatoren_m15(d)
    sig = FA.f3_asien(d, atr, 0.65, m=1e9)
    a = ZF.vergleich(d, SP.NAS, sig, 10.0, familie=3, symbolindex=1, laeufe=40)
    b = ZF.vergleich(d, SP.NAS, sig, 10.0, familie=3, symbolindex=1, laeufe=40)
    assert np.array_equal(a["zufall_r"], b["zufall_r"])
    assert len(a["zufall_r"]) == 40 and 0.0 <= a["quantil"] <= 1.0
    assert a["fenster"][0] >= 3 * 60 + 15 and a["fenster"][1] <= 5 * 60   # Einstiegskerzen 03:15-05:00
    assert a["seed"] == 7000 + 300 + 1


def test_blick_in_die_zukunft_besteht(daten):
    d = daten["NAS"]
    atr = SG.indikatoren_m15(d)
    B = d["m15"]
    pool = ZF.kandidaten(d, atr, 4 * 60, 6 * 60)
    pool = pool[(pool + 40 < len(B["t"])) & (np.arange(len(pool)) % 7 == 0)]
    zukunft = B["c"][pool + 32] - B["o"][pool]                              # Kurs 8 h spaeter
    sig = dict(i5=B["first"][pool], dir=np.where(zukunft > 0, 1, -1), rd=3.0 * atr[pool - 1], j=pool - 1)
    r = ZF.vergleich(d, SP.NAS, sig, 10.0, familie=9, symbolindex=1, laeufe=60)
    assert r["bestanden"] and r["quantil"] == 1.0


def test_gleiche_termine_zufallsrichtung(daten):
    d = daten["NAS"]
    atr = SG.indikatoren_m15(d)
    sig = FA.f3_asien(d, atr, 0.65, m=1e9)
    r = ZF.gleiche_termine_zufallsrichtung(d, SP.NAS, sig, 10.0, familie=1, symbolindex=1, laeufe=30)
    assert len(r["zufall_r"]) == 30 and np.isfinite(r["netto_r"])
