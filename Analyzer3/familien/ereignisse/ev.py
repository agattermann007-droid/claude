"""Familie 'ereignisse': gemeinsame Bausteine (Ereigniskalender, Fenster, Signale).

Alle Uhrzeiten New-York-Ortszeit (Serverzeit - 7 h), Minuten seit Mitternacht. Kerzen M5, Index = Kerzenbeginn.
Ein Fenster [start, end) wird so gehandelt: Signalkerze = Kerze, die um start-5 beginnt (Entscheidung an ihrem Schluss),
Market-Einstieg zur Eroeffnung der Kerze um start, Zeitausstieg am Schluss der Kerze, die um end-5 beginnt.
Stop = Einstieg -/+ k * sigma_F, sigma_F = Wurzel des Mittels der quadrierten Fensterrenditen (Eroeffnung start ->
Schluss end) der letzten 20 Handelstage VOR dem Signaltag (nur Vergangenheit, alle Tage, nicht nur Ereignistage).
Ereignistermine aus /home/user/data/cal (im Voraus bekannt, nur geplante Termine). Keine Kursdaten nach der Signalkerze.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, '/home/user/claude/Analyzer3/lib')
import qdata as Q  # noqa: E402

CAL = os.environ.get('QCAL', '/home/user/data/cal')
LOOKBACK = 20
INDEX = {'NAS100', 'US500', 'US30', 'US2000'}


def hm(s):
    h, m = str(s).split(':')
    return int(h) * 60 + int(m)


# ---------------------------------------------------------------- Kalender (vorab bekannt)

def fomc(sep_only=False):
    """Geplante FOMC-Statements (scheduled=1). Spalten: t_m (Minute NY), press_conf, sep (Projektionen Mar/Jun/Sep/Dec)."""
    f = pd.read_csv(os.path.join(CAL, 'fomc.csv'))
    f = f[f['scheduled'] == 1].copy()
    f.index = pd.DatetimeIndex(pd.to_datetime(f['date'])).normalize()
    f['t_m'] = f['time_et'].map(hm)
    f['sep'] = f.index.month.isin([3, 6, 9, 12])
    if sep_only:
        f = f[f['sep']]
    return f[['t_m', 'press_conf', 'sep']]


def macro(kind):
    """kind: 'cpi' | 'nfp' | 'cpinfp' (Vereinigung). Spalte t_m."""
    if kind == 'cpinfp':
        a, b = macro('cpi'), macro('nfp')
        return pd.concat([a, b]).groupby(level=0).first().sort_index()
    f = pd.read_csv(os.path.join(CAL, f'{kind}.csv'))
    f.index = pd.DatetimeIndex(pd.to_datetime(f['date'])).normalize()
    f['t_m'] = f['time_et'].map(hm)
    return f[['t_m']]


def eia():
    f = pd.read_csv(os.path.join(CAL, 'eia.csv'))
    f.index = pd.DatetimeIndex(pd.to_datetime(f['date'])).normalize()
    f['t_m'] = f['time_et'].map(hm)
    return f[['t_m']]


def market_cal():
    """US-Boersenkalender: Handelstage mit Schlusszeit (Minuten NY)."""
    f = pd.read_csv(os.path.join(CAL, 'us_market_calendar.csv'))
    f.index = pd.DatetimeIndex(pd.to_datetime(f['date'])).normalize()
    f['close_m'] = f['close_time_et'].map(hm)
    return f


def event_days(kind):
    if kind == 'fomc':
        return fomc().index
    if kind == 'fomc_sep':
        return fomc(sep_only=True).index
    if kind in ('cpi', 'nfp', 'cpinfp'):
        return macro(kind).index
    if kind == 'eia':
        return eia().index
    if kind == 'any':     # FOMC (geplant) oder CPI oder NFP
        return fomc().index.union(macro('cpinfp').index)
    raise ValueError(kind)


# ---------------------------------------------------------------- Kerzen, Fenster

def prep(df, inst=None):
    inst = inst or df.attrs.get('inst')
    x = df.copy()
    ny = Q.server_to_ny(x.index)
    x['nyday'] = ny.normalize()
    x['m'] = (ny.hour * 60 + ny.minute).to_numpy()
    x.attrs.update(df.attrs)
    x.attrs['inst'] = inst
    days = pd.DatetimeIndex(x['nyday'].unique())
    days = days[days.dayofweek < 5]
    if inst in INDEX:
        mc = market_cal()
        full = mc.index[mc['close_m'] >= 16 * 60]
        days = days[days.isin(mc.index)]
        x.attrs['full_days'] = days[days.isin(full)]
    else:
        x.attrs['full_days'] = days
    x.attrs['tdays'] = days
    pos = pd.Series(np.arange(len(x)), index=pd.MultiIndex.from_arrays([x['nyday'].to_numpy(), x['m'].to_numpy()]))
    x.attrs['pos'] = pos[~pos.index.duplicated()]
    return x


def bar_pos(x, minute, days=None):
    """Je Tag: Position der Kerze, die um `minute` (NY) beginnt, sonst NaN."""
    days = x.attrs['tdays'] if days is None else days
    pos = x.attrs['pos']
    key = pd.MultiIndex.from_arrays([days, np.full(len(days), int(minute))])
    return pd.Series(pos.reindex(key).to_numpy(), index=days)


def last_pos(x, lo_m, hi_m, days=None):
    """Je Tag: Position der letzten vorhandenen Kerze mit Beginn in [lo_m, hi_m] (NY), sonst NaN.
    Auf abgeschnittenen Daten ist das die letzte bis dahin vorhandene Kerze (kein Blick nach vorn)."""
    days = x.attrs['tdays'] if days is None else days
    m = x['m'].to_numpy()
    sel = (m >= lo_m) & (m <= hi_m)
    pos = np.arange(len(x))[sel]
    s = pd.Series(pos, index=x['nyday'].to_numpy()[sel]).groupby(level=0).max()
    return s.reindex(days)


def past_rms(r, days, lookback=LOOKBACK):
    """sigma je Tag D = Wurzel des Mittels von r^2 ueber die letzten `lookback` gueltigen Tage STRIKT vor D."""
    r2 = (r ** 2).dropna().sort_index()
    roll = r2.rolling(lookback, min_periods=lookback).mean()
    k = r2.index.searchsorted(pd.DatetimeIndex(days), side='left') - 1
    v = np.where(k >= 0, roll.to_numpy()[np.maximum(k, 0)], np.nan)
    return pd.Series(np.sqrt(v), index=days)


def window_frame(x, start_m, end_m):
    """Je Handelstag: Signal-, Einstiegs-, Schlusskerze des Fensters [start_m, end_m) und sigma_F (nur Vortage).
    Schlusskerze = letzte vorhandene Kerze mit Beginn in [start_m, end_m-5]."""
    days = x.attrs['tdays']
    w = pd.DataFrame(index=days)
    w['p_sig'] = bar_pos(x, start_m - 5)
    w['p_in'] = bar_pos(x, start_m)
    w['p_end'] = last_pos(x, start_m, end_m - 5)
    if x.attrs.get('inst') in INDEX and end_m > 13 * 60:
        w.loc[~w.index.isin(x.attrs['full_days']), ['p_sig', 'p_in', 'p_end']] = np.nan
    o = x['o'].to_numpy(float)
    c = x['c'].to_numpy(float)
    ok = w['p_in'].notna() & w['p_end'].notna()
    r = pd.Series(np.nan, index=days)
    r[ok] = c[w.loc[ok, 'p_end'].astype(int)] / o[w.loc[ok, 'p_in'].astype(int)] - 1
    w['sigma'] = past_rms(r, days)
    w['ret'] = r
    return w


def reaction(x, a_m, b_m):
    """Je Tag: Rendite vom Schluss der Kerze vor a_m (Kurs um a_m) bis zum Schluss der Kerze, die um b_m-5 beginnt."""
    c = x['c'].to_numpy(float)
    pa = bar_pos(x, a_m - 5)
    pb = bar_pos(x, b_m - 5)
    ok = pa.notna() & pb.notna()
    r = pd.Series(np.nan, index=pa.index)
    r[ok] = c[pb[ok].astype(int)] / c[pa[ok].astype(int)] - 1
    return r


def build(x, days, start_m, end_m, d, k=1.0, tgt_R=np.nan, w=None):
    """Signale fuer die Tage `days` im Fenster [start_m, end_m). d: +1/-1 skalar oder Series je Tag (0 = kein Trade)."""
    w = window_frame(x, start_m, end_m) if w is None else w
    w = w[w.index.isin(days)].copy()
    if np.isscalar(d):
        w['d'] = d
    else:
        w['d'] = pd.Series(d).reindex(w.index)
    # nur Daten bis zur Signalkerze: Einstiegs- und Schlusskerze duerfen (auf abgeschnittenen Daten) noch fehlen
    w = w.dropna(subset=['p_sig', 'sigma', 'd'])
    w = w[w['d'] != 0]
    w['i_last'] = w['p_end'].fillna(w['p_sig'])        # fehlt die Schlusskerze, verfaellt das Signal in qbt (-8)
    c = x['c'].to_numpy(float)
    ref = c[w['p_sig'].astype(int)]
    sig = pd.DataFrame({'i_sig': w['p_sig'].astype(np.int64).to_numpy(), 'd': w['d'].astype(np.int64).to_numpy(),
                        'i_last': w['i_last'].astype(np.int64).to_numpy(), 'kind': 'market', 'tgt_R': tgt_R,
                        'sigma': w['sigma'].to_numpy(), 'day': w.index})
    sig['stop'] = ref * (1 - sig['d'] * k * sig['sigma'])
    return sig.reset_index(drop=True)
