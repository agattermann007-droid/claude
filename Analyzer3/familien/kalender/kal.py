"""Familie 'kalender': gemeinsame Bausteine (NYSE-Kalender, Fenster-Volatilitaet, Signale).

Alle Uhrzeiten in New-York-Ortszeit (Serverzeit - 7 h). Ein Fenster [start, end) wird so gehandelt:
Signalkerze = Kerze, die um start-5 min beginnt (Entscheidung an ihrem Schluss), Market-Einstieg zur Eroeffnung
der Kerze um start, Zeitausstieg am Schluss der letzten Kerze mit Ende <= end.
Stop = Einstieg -/+ k * sigma_F, sigma_F = Wurzel des Mittels der quadrierten Fensterrenditen
(Eroeffnung start -> Schluss end) der letzten 20 NYSE-Handelstage vor dem Signaltag (nur Vergangenheit).
Feiertage/Handelstage kommen aus pandas_market_calendars ('NYSE'); nur regulaere, im Voraus bekannte Feiertage.
"""
import os
import sys

import numpy as np
import pandas as pd
import pandas_market_calendars as mcal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import qdata as Q  # noqa: E402

LOOKBACK = 20
_NYSE = mcal.get_calendar('NYSE')


# ---------------------------------------------------------------- Kalender

def nyse_table(d0, d1):
    """Je NYSE-Handelstag in [d0, d1]: Schlusszeit (Minuten NY), Monatswechsel, Vor-Feiertag, OPEX.
    Der Kalender ist regelbasiert (vorab bekannt), daher keine Vorschau auf Kursdaten."""
    d0 = pd.Timestamp(d0).normalize() - pd.Timedelta(days=45)
    d1 = pd.Timestamp(d1).normalize() + pd.Timedelta(days=45)
    s = _NYSE.schedule(d0, d1)
    t = pd.DataFrame(index=pd.DatetimeIndex(s.index).tz_localize(None).normalize())
    cl = s['market_close'].dt.tz_convert('America/New_York')
    t['close_m'] = (cl.dt.hour * 60 + cl.dt.minute).to_numpy()
    days = t.index
    # Monatswechsel: letzter Handelstag des Monats (-1) und erste 3 Handelstage (+1..+3)
    ym = days.year * 12 + days.month
    pos_in_m = pd.Series(1, index=days).groupby(ym).cumsum().to_numpy()
    n_in_m = pd.Series(1, index=days).groupby(ym).transform('sum').to_numpy()
    t['tom_last'] = pos_in_m == n_in_m
    t['tom_first'] = pos_in_m <= 3
    t['tom'] = t['tom_last'] | t['tom_first']
    # Vor-Feiertag: der naechste Wochentag ist ein regulaerer NYSE-Feiertag
    hol = set(pd.DatetimeIndex(_NYSE.regular_holidays.holidays(d0, d1)).normalize())
    nxt_wd = days + pd.offsets.BDay(1)
    t['preh'] = [x in hol for x in nxt_wd]
    # OPEX: dritter Freitag; ist er kein Handelstag, der Handelstag davor. OPEX-Woche: Mo..Verfallstag derselben Woche
    tf = []
    for y, m in sorted(set(zip(days.year, days.month))):
        fr = pd.date_range(pd.Timestamp(y, m, 1), periods=31, freq='D')
        fr = fr[(fr.month == m) & (fr.dayofweek == 4)][2]
        tf.append(fr)
    exp_days, weeks = set(), set()
    dayset = set(days)
    for fr in tf:
        e = fr
        while e not in dayset and e > fr - pd.Timedelta(days=4):
            e -= pd.Timedelta(days=1)
        if e in dayset:
            exp_days.add(e)
        mon = fr - pd.Timedelta(days=4)
        for k in range(5):
            dd = mon + pd.Timedelta(days=k)
            if dd in dayset and dd <= e:
                weeks.add(dd)
    t['opex_day'] = [x in exp_days for x in days]
    t['opex_week'] = [x in weeks for x in days]
    return t


# ---------------------------------------------------------------- Kerzen, Fenster

def prep(df):
    x = df.copy()
    ny = Q.server_to_ny(x.index)
    x['nyday'] = ny.normalize()
    x['m'] = (ny.hour * 60 + ny.minute).to_numpy()          # Kerzenbeginn, Minuten NY
    x.attrs.update(df.attrs)
    x.attrs['cal'] = nyse_table(x['nyday'].min(), x['nyday'].max())
    g = pd.Series(np.arange(len(x))).groupby(x['nyday'].to_numpy()).agg(['min', 'max'])
    x.attrs['daypos'] = g
    return x


def _bar_pos(x, minute):
    """Je NY-Tag: Position der Kerze, die um `minute` beginnt (falls vorhanden)."""
    pos = np.arange(len(x))
    sel = x['m'].to_numpy() == minute
    return pd.Series(pos[sel], index=x['nyday'].to_numpy()[sel]).groupby(level=0).first()


def _last_pos(x, end_m):
    """Je NY-Tag: Position der letzten Kerze mit Ende <= end_m (und Beginn >= 0)."""
    pos = np.arange(len(x))
    sel = (x['m'].to_numpy() + 5) <= end_m
    return pd.Series(pos[sel], index=x['nyday'].to_numpy()[sel]).groupby(level=0).last()


def window_frame(x, start_m, end_m):
    """Je NYSE-Handelstag: Signal-, Einstiegs- und Schlusskerze des Fensters sowie sigma_F (nur Vortage)."""
    cal = x.attrs['cal']
    tdays = cal.index
    p_sig = _bar_pos(x, start_m - 5)
    p_in = _bar_pos(x, start_m)
    p_end = _bar_pos(x, end_m - 5)
    w = pd.DataFrame(index=tdays)
    w['p_sig'] = p_sig.reindex(tdays)
    w['p_in'] = p_in.reindex(tdays)
    w['p_end'] = p_end.reindex(tdays)
    o = x['o'].to_numpy(float)
    c = x['c'].to_numpy(float)
    ok = w['p_in'].notna() & w['p_end'].notna()
    r = pd.Series(np.nan, index=tdays)
    r[ok] = c[w.loc[ok, 'p_end'].astype(int)] / o[w.loc[ok, 'p_in'].astype(int)] - 1
    r2 = (r ** 2).dropna()
    roll = r2.rolling(LOOKBACK, min_periods=LOOKBACK).mean()
    # sigma fuer Tag D: letzter Wert strikt vor D (auch wenn D selbst noch keine Fensterrendite hat -> kausal)
    sig = np.sqrt(roll.reindex(tdays, method='ffill').shift(1))
    w['sigma'] = sig
    w['ret'] = r
    return w


def ref_close(x, end_m=15 * 60):
    """Je NYSE-Handelstag: Schluss der letzten Kerze mit Ende <= min(15:00, Boersenschluss)."""
    cal = x.attrs['cal']
    out = pd.Series(np.nan, index=cal.index)
    c = x['c'].to_numpy(float)
    for cm in sorted(set(cal['close_m'])):
        lp = _last_pos(x, min(end_m, cm))
        days = cal.index[cal['close_m'] == cm]
        lp = lp.reindex(days).dropna().astype(int)
        out[lp.index] = c[lp.to_numpy()]
    return out


def build(x, day_mask, start_m=570, end_m=900, k=1.0, tgt_R=np.nan, d=1, early_close=True):
    """Signale fuer alle NYSE-Handelstage mit day_mask (bool-Series auf cal.index).
    early_close: an verkuerzten Tagen endet das Fenster mit dem Boersenschluss (eigene sigma-Reihe)."""
    cal = x.attrs['cal']
    c = x['c'].to_numpy(float)
    rows = []
    ends = {end_m}
    if early_close:
        ends |= {min(end_m, cm) for cm in set(cal['close_m'])}
    frames = {e: window_frame(x, start_m, e) for e in ends if e > start_m}
    sel_days = cal.index[day_mask.reindex(cal.index).fillna(False).to_numpy(bool)]
    xm = x['m'].to_numpy()
    for day in sel_days:
        e = min(end_m, cal.at[day, 'close_m']) if early_close else end_m
        if e not in frames:
            continue
        w = frames[e]
        ps, sg = w.at[day, 'p_sig'], w.at[day, 'sigma']
        if np.isnan(ps) or np.isnan(sg):
            continue
        ps = int(ps)
        pe = _last_in_day(x, day, e, xm)
        if pe is None or pe <= ps:
            if ps == len(x) - 1:      # Daten enden an der Signalkerze (Live/abgeschnitten): Ausstieg liegt in der Zukunft
                pe = ps + 1
            else:
                continue
        rows.append(dict(i_sig=ps, d=d, stop=c[ps] * (1 - d * k * sg), tgt_R=tgt_R, i_last=pe, kind='market',
                         sday=day, sigma=sg))
    out = pd.DataFrame(rows)
    if len(out) == 0:
        out = pd.DataFrame(columns=['i_sig', 'd', 'stop', 'tgt_R', 'i_last', 'kind', 'sday', 'sigma'])
    return out


def _last_in_day(x, day, end_m, xm):
    g = x.attrs['daypos']
    if day not in g.index:
        return None
    a, b = int(g.at[day, 'min']), int(g.at[day, 'max'])
    sel = np.nonzero(xm[a:b + 1] + 5 <= end_m)[0]
    return a + int(sel[-1]) if len(sel) else None
