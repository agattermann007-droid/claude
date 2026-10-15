"""Kandidat B (Familie 'ausstiege'): Paper-Einstieg mit SMA20-Filter, Teilziel 50 % bei 0,5R, danach Break-even.

Einstieg nach Zarattini/Aziz/Barbon 2024 ('Beat the Market'): an jeder Halbstunden-Marke 10:00-14:30 NY, Schluss
ausserhalb der Noise-Area (Lookback 14), Trendfilter Vortagesschluss gegen SMA20 (wie noise-1.0); nach einem Ausstieg
ist ein neuer Einstieg an einer spaeteren Marke erlaubt (eine Position zur Zeit). Market zur naechsten Eroeffnung.
Stop Bandmitte (UB+LB)/2 der Signalkerze. Target (sichtbar) = 0,5R fuer 50 % der Position; danach Stop auf Einstieg
(Break-even), Rest ohne Ziel bis 15:00 NY. Auswahl auf NAS100 Train 2021-23 als beste Trefferquote >= 60 % mit R > 0.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import noise

NAME = 'ausstiege-B: Paper-Einstieg+SMA20, Stop Bandmitte, Teilziel 50% bei 0,5R, dann Break-even, Rest bis 15:00 NY'
INSTRUMENTS = ['NAS100']


def prepare(df, inst):
    return noise.prepare(df, inst)


def signals(x, inst):
    sig = noise.signals(x, grid=30, trend='cprev', one_per_day=False, stop_mode='mid', tgt_R=np.nan)
    sig['tgt_R'] = np.nan
    sig['tp1_R'] = 0.5
    sig['tp1_frac'] = 0.5
    sig['be_after_tp1'] = True
    return sig
