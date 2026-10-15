"""Kandidat A (Familie 'ausstiege'): noise-1.0-Einstieg mit Ziel 1,5R und Zeitausstieg 15:00 NY.

Einstieg wie noise-1.0 (Zarattini/Aziz/Barbon 2024, Noise-Area Lookback 14): erstes Halbstunden-Signal des Tages
(10:00-14:30 NY, Schluss ausserhalb UB/LB), Trendfilter Vortagesschluss gegen SMA20, Market zur naechsten Eroeffnung.
Stop Bandmitte (UB+LB)/2 der Signalkerze, Ziel 1,5R, Zeitausstieg zum Schluss der letzten Kerze bis 15:00 NY.
Auswahl auf NAS100 Train 2021-23 als hoechstes R je Trade (Ausstiege mit sichtbarem Ziel, Zeitausstieg 15:00).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import noise

NAME = 'ausstiege-A: noise-1.0-Einstieg, Stop Bandmitte, Ziel 1,5R, Ausstieg 15:00 NY'
INSTRUMENTS = ['NAS100']


def prepare(df, inst):
    return noise.prepare(df, inst)


def signals(x, inst):
    return noise.signals(x, grid=30, trend='cprev', one_per_day=True, stop_mode='mid', tgt_R=1.5)
