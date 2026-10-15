"""Kandidat 'A_s1' (Familie 'noise_indizes'): Noise-Area-Momentum als Portfolio ueber Index-CFDs, je Instrument eigene Kassasitzung.

Einstieg wie noise-1.0 (Zarattini/Aziz/Barbon 2024, 'Beat the Market'): M30-Raster ab 30 min nach lokaler Kassaeroeffnung,
Schluss ausserhalb der Noise-Area (Lookback 14), Trendfilter Vortagesschluss gegen SMA20 der Sitzungsschluesse, Market zur
naechsten Eroeffnung, Stop Bandmitte. Ausstieg: Ziel 1,5R; Zeitausstieg zum letzten Ausstieg der Sitzung (ni_sitzung.SESS).
Regel 'A' aus ni_regeln.py. Sitzungen und Mittagspausen (JPN225 11:30-12:30 Tokio, HK50 12:00-13:00 Hongkong) in ni_sitzung.py.
Instrumente nach vorab festgelegter Regel S1 (Train R netto > 0 und > Nullmodell-R) gewaehlt, siehe REGELN.md.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import ni_sitzung as sitzung  # noqa: E402
import ni_regeln as regeln  # noqa: E402

NAME = 'noise_indizes-A_s1: noise-1.0-Einstieg je lokaler Kassasitzung, Regel A, Auswahl S1'
INSTRUMENTS = ['NAS100', 'US500', 'GER40', 'JPN225', 'HK50']
RULE = 'A'


def prepare(df, inst):
    return sitzung.prepare(df, inst)


def signals(x, inst):
    return regeln.make_signals(x, RULE)
