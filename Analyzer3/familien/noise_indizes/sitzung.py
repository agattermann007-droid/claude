"""Familie 'noise_indizes': Kassasitzungen je Index-CFD inkl. Mittagspausen (JPN225, HK50).

Sitzungen aus lib/noise.py SESS unveraendert, ergaenzt um HK50 (Asia/Hong_Kong 9:30-16:00, letzter Ausstieg 15:30) und
Mittagspausen. qbt.session_frame kennt keine Pause: dort gelten die Pausen-Kerzen als Sitzung, das M30-Raster erzeugt dann
Signale um 12:00/12:30 Tokio in der Pause, und Pausen-Kerzen fliessen in VWAP und Noise-Area ein. Hier werden Kerzen, deren
Zeitraum in der Pause beginnt, auf in_sess=False gesetzt, bevor die Noise-Area berechnet wird. Das Raster bleibt
uhrzeitbasiert (Minuten seit Kassaeroeffnung); Signalmarken gibt es nur fuer Signalkerzen in Handelszeit.
Offene Positionen laufen durch die Pause (qbt.simulate laeuft ueber alle Kerzen).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import noise  # noqa: E402
import qbt  # noqa: E402

INSTRUMENTS = ['NAS100', 'US500', 'US30', 'US2000', 'GER40', 'FRA40', 'ESTX50', 'UK100', 'JPN225', 'AUS200', 'HK50']

LUNCH = {'JPN225': ((11, 30), (12, 30)), 'HK50': ((12, 0), (13, 0))}
SESS = {k: v + (LUNCH.get(k),) for k, v in noise.SESS.items()}
SESS['HK50'] = ('Asia/Hong_Kong', (9, 30), (16, 0), (15, 30), LUNCH['HK50'])


def prepare(df, inst, lookback=14):
    tz, op, cl, ex, lunch = SESS[inst]
    x = qbt.session_frame(df, tz, op, cl)
    if lunch is not None:
        a = lunch[0][0] * 60 + lunch[0][1]
        b = lunch[1][0] * 60 + lunch[1][1]
        mb = x['m_bar']
        x['in_sess'] = x['in_sess'] & ~((mb >= a) & (mb < b))
    x = qbt.noise_area(x, lookback=lookback, vol_mult=1.0, prev_close='session')
    x.attrs['exit_hm'] = ex
    x.attrs['open_hm'] = op
    x.attrs['inst'] = inst
    return x
