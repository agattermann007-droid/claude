"""GRENZFALL (kein freigegebener Kandidat): Monatswechsel + Vor-Feiertag, Long intraday US500.

Regel (Lakonishok/Smidt 1988; Ariel 1987/1990; McConnell/Xu 2008): an jedem NYSE-Handelstag, der letzter Handelstag
des Monats, einer der ersten 3 Handelstage des Monats oder letzter Handelstag vor einem regulaeren NYSE-Feiertag ist:
Market-Long zur Eroeffnung der 9:30-NY-Kerze (Signal am Schluss der 9:25-Kerze), Stop = Einstieg - 1 x sigma_F,
kein Ziel, Zeitausstieg am Schluss der 14:55-Kerze (15:00 NY; an verkuerzten Tagen 13:00).
sigma_F = Wurzel des Mittels der quadrierten 9:30->15:00-Renditen der letzten 20 Handelstage (nur Vortage).
Schnittstelle wie kandidat_*.py (NAME, INSTRUMENTS, prepare, signals); Kalender aus pandas_market_calendars ('NYSE').
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kal  # noqa: E402

NAME = 'kalender-tom-preh'
INSTRUMENTS = ['US500']


def prepare(df, inst):
    return kal.prep(df)


def signals(x, inst):
    cal = x.attrs['cal']
    return kal.build(x, cal['tom'] | cal['preh'], 570, 900, k=1.0, tgt_R=np.nan, d=1)
