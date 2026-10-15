"""Kandidat C (Familie 'ausstiege'): Paper-Einstieg ohne Filter, Paper-Nachzieh-Stop, Teilziel 50 % bei 1R.

Einstieg nach Zarattini/Aziz/Barbon 2024 ('Beat the Market'): an jeder Halbstunden-Marke 10:00-14:30 NY, Schluss
ausserhalb der Noise-Area (Lookback 14), kein Trendfilter; nach einem Ausstieg ist ein neuer Einstieg an einer spaeteren
Marke erlaubt (eine Position zur Zeit). Market zur naechsten Eroeffnung.
Anfangsstop Bandmitte (R-Einheit). Ab der Kerze nach dem Einstieg Nachzieh-Stop nach dem Paper: Long max(UB, VWAP),
Short min(LB, VWAP), nur an den Halbstunden-Marken neu gesetzt (dazwischen gilt der letzte Wert, nur nachziehen).
Target (sichtbar) = 1R fuer 50 % der Position, Rest mit dem Nachzieh-Stop, Zeitausstieg 15:00 NY.
Auswahl auf NAS100 Train 2021-23 als hoechstes R je Handelstag; US500 mit derselben Regel (knapp t 2,0 auf Train).

Technik: qbt.simulate erlaubt nur eine Nachzieh-Spalte. Die Spalte 'tr_paper_dir' traegt deshalb an jeder Kerze den
Paper-Stop in Richtung des juengsten Signals des Tages (Marken-Wert von max(UB,VWAP) bzw. min(LB,VWAP)). Solange eine
Position offen ist, kann kein Gegensignal entstehen, ohne dass die Position vorher ausgestoppt wurde (Schluss unter LB
liegt unter dem Long-Stop >= UB der Vormarke), daher ist die Spalte fuer jede offene Position gleich dem Paper-Stop
ihrer Richtung. Alle Werte nutzen nur Daten bis zum Schluss der jeweiligen Kerze.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import noise

NAME = 'ausstiege-C: Paper-Einstieg ohne Filter, Stop Bandmitte + Paper-Nachzug max(UB,VWAP)/min(LB,VWAP), Teilziel 50% bei 1R, 15:00 NY'
# US500 nach der vorab festgelegten Regel (auswahl_train.json): Train R>0 mit t>=2 und 2024 R>0, ohne eigene Abstimmung.
# Erfuellt erst auf den korrigierten Kerzen (v3): US500 Train +0,024 R, t 2,01; 2024 +0,039 R. Knapp.
INSTRUMENTS = ['NAS100', 'US500']
ENTRY = dict(grid=30, trend='none', one_per_day=False)
TRAIL = 'tr_paper_dir'


def _raw(x):
    return noise.signals(x, stop_mode='mid', tgt_R=np.nan, **ENTRY)


def prepare(df, inst):
    x = noise.prepare(df, inst)
    m = x['m_close'].to_numpy()
    ins = x['in_sess'].to_numpy()
    mark = ins & (m >= 30) & (m % 30 == 0) & x['UB'].notna().to_numpy() & x['vwap'].notna().to_numpy()
    raw = _raw(x)
    dsig = np.full(len(x), np.nan)
    dsig[raw['i_sig'].to_numpy()] = raw['d'].to_numpy()
    day = x['sday'].to_numpy()
    # Richtung des juengsten Signals des Tages (nur Signale bis zur Kerze)
    dirn = pd.Series(dsig, index=x.index).groupby(day).ffill().to_numpy()
    # Paper-Werte nur an den Marken, dazwischen Wert der letzten Marke
    upv = pd.Series(np.where(mark, np.maximum(x['UB'], x['vwap']), np.nan), index=x.index).groupby(day).ffill().to_numpy()
    dnv = pd.Series(np.where(mark, np.minimum(x['LB'], x['vwap']), np.nan), index=x.index).groupby(day).ffill().to_numpy()
    col = np.where(dirn > 0, upv, np.where(dirn < 0, dnv, np.nan))
    x[TRAIL] = np.where(ins, col, np.nan)
    return x


def signals(x, inst):
    sig = _raw(x)
    sig['tgt_R'] = np.nan
    sig['trail'] = TRAIL
    sig['tp1_R'] = 1.0
    sig['tp1_frac'] = 0.5
    sig['be_after_tp1'] = False
    return sig
