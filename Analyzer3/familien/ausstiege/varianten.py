"""Variantenliste der Familie 'ausstiege' (vor dem ersten Lauf festgelegt).

Einstiege (lib/noise.py): N10 = noise-1.0 (erstes Halbstunden-Signal des Tages, SMA20-Filter),
PAPS / PAP0 = Paper-Einstieg Zarattini/Aziz/Barbon 2024 (alle Halbstunden-Signale, Wiedereinstieg) mit / ohne SMA20.
Ausstiege: Stop (Bandmitte, VWAP, Gegenband), festes Ziel in R, Zeitausstieg 15:00 NY (T15) oder 480 min (M480),
Nachzieh-Stop (paper = max(UB,VWAP)/min(LB,VWAP); vwap = VWAP allein, Maroy 2025 'VWAP exit'), Teilziel 50 %.
"""
import numpy as np

NAN = np.nan

EXITS_N10 = {
    # feste Ziele, Stop Bandmitte, 15:00 NY bzw. 480 min (wie noise-1.0)
    'ref_t10_480': dict(stop='mid', tgt=1.0, time='M480'),          # = noise-1.0 Referenz
    't05_480': dict(stop='mid', tgt=0.5, time='M480'),
    't15_480': dict(stop='mid', tgt=1.5, time='M480'),
    't20_480': dict(stop='mid', tgt=2.0, time='M480'),
    't05_15': dict(stop='mid', tgt=0.5),
    't10_15': dict(stop='mid', tgt=1.0),
    't15_15': dict(stop='mid', tgt=1.5),
    't20_15': dict(stop='mid', tgt=2.0),
    # Paper-Ausstieg (Zarattini/Aziz/Barbon 2024): Nachzug max(UB,VWAP)/min(LB,VWAP), kein Ziel, 15:00
    'paper': dict(stop='mid', tgt=NAN, trail='paper'),
    # Maroy 2025 'VWAP exit': Nachzug VWAP allein, kein Ziel, 15:00
    'vwaptrail': dict(stop='mid', tgt=NAN, trail='vwap'),
    # Teilziel 50 % bei 1R / 0,5R, Rest: Break-even bis 15:00, VWAP-Nachzug oder Paper-Nachzug
    'tp10_be': dict(stop='mid', tgt=NAN, tp1=1.0, be=True),
    'tp05_be': dict(stop='mid', tgt=NAN, tp1=0.5, be=True),
    'tp10_vwap': dict(stop='mid', tgt=NAN, tp1=1.0, trail='vwap'),
    'tp05_vwap': dict(stop='mid', tgt=NAN, tp1=0.5, trail='vwap'),
    'tp10_paper': dict(stop='mid', tgt=NAN, tp1=1.0, trail='paper'),
    'tp05_paper': dict(stop='mid', tgt=NAN, tp1=0.5, trail='paper'),
    # Stop-Varianten bei Ziel 1R, 15:00
    'stopvwap_t10': dict(stop='vwap', tgt=1.0),
    'stopband_t10': dict(stop='band', tgt=1.0),
}

EXITS_PAP = {k: EXITS_N10[k] for k in ['t05_15', 't10_15', 't15_15', 't20_15', 'paper', 'vwaptrail',
                                       'tp10_be', 'tp05_be', 'tp10_paper', 'tp05_paper']}

VARIANTS = [('N10', k, v) for k, v in EXITS_N10.items()] + \
           [(e, k, v) for e in ('PAPS', 'PAP0') for k, v in EXITS_PAP.items()]


def label(entry, ex_name):
    return f'{entry}_{ex_name}'


def has_target(ex):
    """Sichtbares Ziel fuer Alex: festes Ziel oder Teilziel."""
    return not np.isnan(ex.get('tgt', NAN)) or ex.get('tp1') is not None
