"""Familie 'noise_indizes': die vier vorab festgelegten Regeln (siehe REGELN.md) als Signaltabellen fuer qbt.simulate."""
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(HIER, '..', '..', 'lib'))
import noise  # noqa: E402

RULES = ['N10_480', 'N10_EOD', 'A', 'B']
DAYTRADE = ['N10_EOD', 'A', 'B']


def make_signals(x, rule):
    """x aus sitzung.prepare. Einstieg E0 = noise-1.0 (M30 ab Eroeffnung+30 min, Noise-Area 14, SMA20-Filter, Stop Bandmitte)."""
    if rule == 'N10_480':
        sig = noise.signals(x, grid=30, trend='cprev', one_per_day=True, stop_mode='mid', tgt_R=1.0)
        sig['i_last'] = noise.last_by_clock(x, sig['i_sig'], 480)   # 480 min nach Uhrzeit (nicht 96 Kerzen)
    elif rule == 'N10_EOD':
        sig = noise.signals(x, grid=30, trend='cprev', one_per_day=True, stop_mode='mid', tgt_R=1.0)
    elif rule == 'A':
        sig = noise.signals(x, grid=30, trend='cprev', one_per_day=True, stop_mode='mid', tgt_R=1.5)
    elif rule == 'B':
        sig = noise.signals(x, grid=30, trend='cprev', one_per_day=False, stop_mode='mid', tgt_R=np.nan)
        sig['tgt_R'] = np.nan
        sig['tp1_R'] = 0.5
        sig['tp1_frac'] = 0.5
        sig['be_after_tp1'] = True
    else:
        raise ValueError(rule)
    return sig
