"""Noise-Area-Momentum (Zarattini/Aziz/Barbon 2024) als Signalgenerator fuer die gemeinsame Bibliothek.
noise-1.0 (laufend bei Alex): NAS100, SMA20-Trendfilter, Sitzung 9:30-15:00 NY, Stop in der Bandmitte, Ziel 1R."""
import numpy as np
import pandas as pd

import qbt

SESS = {   # Ortszeit-Sitzung je Instrument: (tz, Eroeffnung, Schluss der Kassasitzung, letzter Ausstieg)
    'NAS100': ('America/New_York', (9, 30), (16, 0), (15, 0)),
    'US500': ('America/New_York', (9, 30), (16, 0), (15, 0)),
    'US30': ('America/New_York', (9, 30), (16, 0), (15, 0)),
    'US2000': ('America/New_York', (9, 30), (16, 0), (15, 0)),
    'GER40': ('Europe/Berlin', (9, 0), (17, 30), (17, 0)),
    'FRA40': ('Europe/Paris', (9, 0), (17, 30), (17, 0)),
    'ESTX50': ('Europe/Berlin', (9, 0), (17, 30), (17, 0)),
    'UK100': ('Europe/London', (8, 0), (16, 30), (16, 0)),
    'JPN225': ('Asia/Tokyo', (9, 0), (15, 0), (14, 30)),
    'AUS200': ('Australia/Sydney', (10, 0), (16, 0), (15, 30)),
}


def prepare(df, inst, lookback=14, vol_mult=1.0, sess=None, prev_close='session'):
    tz, op, cl, ex = sess or SESS[inst]
    x = qbt.session_frame(df, tz, op, cl)
    x = qbt.noise_area(x, lookback=lookback, vol_mult=vol_mult, prev_close=prev_close)
    x.attrs['exit_hm'] = ex
    x.attrs['open_hm'] = op
    return x


def last_bar_index(x, exit_hm):
    """Je Sitzungstag: Index der letzten Kerze mit Schluss <= Ausstiegszeit (Ortszeit)."""
    em = exit_hm[0] * 60 + exit_hm[1]
    pos = np.arange(len(x))
    ok = x['in_sess'].to_numpy() & (x['m_bar'].to_numpy() + 5 <= em)
    s = pd.Series(np.where(ok, pos, -1), index=x.index)
    last = s[ok].groupby(x.loc[ok, 'sday']).max()
    return x['sday'].map(last)


def signals(x, grid=30, first_min=30, entry_end_hm=None, trend='cprev', stop_mode='mid', tgt_R=1.0,
            one_per_day=False, exit_hm=None, side='both'):
    """Signale am Schluss jeder grid-Minuten-Kerze (Minuten seit Sitzungsbeginn, ab first_min).
    trend: 'cprev' (Vortagesschluss gegen SMA20 bis Vortag), 'close' (aktueller Kurs gegen SMA20), 'none'."""
    exit_hm = exit_hm or x.attrs['exit_hm']
    entry_end_hm = entry_end_hm or exit_hm
    op = x.attrs['open_hm']
    eem = entry_end_hm[0] * 60 + entry_end_hm[1] - (op[0] * 60 + op[1])
    ilast = last_bar_index(x, exit_hm)
    m = x['m_close']
    cand = x['in_sess'] & (m >= first_min) & (m % grid == 0) & (m < eem) & x['sigma'].notna() & x['Cprev'].notna()
    s = x[cand]
    up = s['c'] > s['UB']
    dn = s['c'] < s['LB']
    if trend == 'cprev':
        tl, ts = s['Cprev'] > s['sma20_prev'], s['Cprev'] < s['sma20_prev']
    elif trend == 'close':
        tl, ts = s['c'] > s['sma20_prev'], s['c'] < s['sma20_prev']
    else:
        tl = ts = pd.Series(True, index=s.index)
    d = np.where(up & tl, 1, np.where(dn & ts, -1, 0))
    if side == 'long':
        d = np.where(d > 0, 1, 0)
    elif side == 'short':
        d = np.where(d < 0, -1, 0)
    pos = pd.Series(np.arange(len(x)), index=x.index)
    out = pd.DataFrame({'i_sig': pos[s.index].to_numpy(), 'd': d, 'sday': s['sday'].to_numpy(),
                        'UB': s['UB'].to_numpy(), 'LB': s['LB'].to_numpy(), 'c': s['c'].to_numpy(),
                        'vwap': s['vwap'].to_numpy(), 'i_last': ilast[s.index].to_numpy()})
    out = out[(out['d'] != 0) & out['i_last'].notna()].copy()
    out['i_last'] = out['i_last'].astype(np.int64)
    if stop_mode == 'mid':
        out['stop'] = (out['UB'] + out['LB']) / 2
    elif stop_mode == 'band':
        out['stop'] = np.where(out['d'] > 0, out['LB'], out['UB'])
    elif stop_mode == 'vwap':
        out['stop'] = out['vwap']
    out['tgt_R'] = tgt_R
    out['kind'] = 'market'
    if one_per_day:
        out = out.groupby('sday').head(1)
    return out.reset_index(drop=True)


def noise10_signals(x):
    """Referenz noise-1.0 (Rekonstruktion, Abweichung zum Original <= 3 Prozentpunkte / 0,03 R):
    M30-Raster ab 10:00 bis vor 15:00 NY, Schluss ausserhalb der Noise-Area, Trendfilter Vortagesschluss gegen SMA20,
    erster Trade des Tages, Stop Bandmitte, Ziel 1R, Bewertung nach 480 min (wie bewerte() in Alex' Harness)."""
    sig = signals(x, grid=30, trend='cprev', one_per_day=True, stop_mode='mid', tgt_R=1.0)
    sig['i_last'] = last_by_clock(x, sig['i_sig'], 480)
    return sig


def last_by_clock(x, i_sig, minutes):
    """Letzte Kerze, deren Schluss <= Signalzeit + minutes (Uhrzeit, nicht Kerzenzahl: kein Halten uebers Wochenende)."""
    idx = x.index.values
    t_end = idx[np.asarray(i_sig)] + np.timedelta64(5 + minutes - 5, 'm')   # Kerzenbeginn <= Signalschluss + minutes - 5
    return np.searchsorted(idx, t_end, side='right') - 1
