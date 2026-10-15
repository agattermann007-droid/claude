"""Gemeinsame Backtest-Bibliothek fuer Analyzer 3.

Regeln (Protokoll):
  - Entscheidung am Schluss der Signalkerze i, Einstieg zur Eroeffnung der naechsten Kerze (Market) oder per Pending-Order.
  - Stop vor Ziel in derselben Kerze. Kurs oeffnet jenseits des Stops -> Ausstieg zur Eroeffnung (schlechter).
  - Ziel wird exakt zum Zielkurs gefuellt (nie besser). Zeitablauf zum Schlusskurs der letzten erlaubten Kerze.
  - Kosten: Roundtrip-Anteil am Preis (qdata.COST) in R umgerechnet und von jedem Trade abgezogen.
  - Eine Position je Instrument und Regel: Signale waehrend einer offenen Position verfallen.

Signal-Tabelle (DataFrame), eine Zeile je Signal:
  i_sig    int    Index der Signalkerze (Entscheidung an ihrem Schluss)
  d        +1/-1
  stop     float  Anfangsstop (absoluter Kurs)
  tgt_R    float  Ziel als Vielfaches des Risikos ab tatsaechlichem Einstieg (NaN = kein festes Ziel)
  tgt_abs  float  optional absolutes Ziel (hat Vorrang vor tgt_R)
  i_last   int    letzte Kerze, deren Schluss noch gehalten wird (Zeitausstieg an ihrem Schluss)
  kind     str    'market' (Standard), 'stop' oder 'limit'
  level    float  Einstiegskurs fuer Pending-Orders
  i_exp    int    letzte Kerze, in der die Pending-Order fuellen darf
  trail    str    optional Spaltenname im Kerzen-DataFrame mit einem Nachzieh-Stop (Wert der Vorkerze wird benutzt)
  tp1_R, tp1_frac, be_after_tp1  optional Teilziel
"""
import numpy as np
import pandas as pd
from numba import njit

import qdata as Q

MARKET, STOPO, LIMITO = 0, 1, 2
KIND = {'market': MARKET, 'stop': STOPO, 'limit': LIMITO}


@njit(cache=True)
def _sim(o, h, l, c, i_sig, d, kind, level, i_exp, stop0, tgtR, tgtA, i_last, trail, use_trail,
         tp1R, tp1f, be1, cost, seq):
    n = len(i_sig)
    out_fill = np.full(n, -1, np.int64)
    out_exit = np.full(n, -1, np.int64)
    out_E = np.full(n, np.nan)
    out_X = np.full(n, np.nan)
    out_R = np.full(n, np.nan)
    out_Rg = np.full(n, np.nan)
    out_code = np.full(n, -9, np.int64)   # 1 Ziel, -1 Stop, 0 Zeit, -7 nicht gefuellt, -8 ungueltig, -9 uebersprungen
    busy_until = -1
    nb = len(o)
    for k in range(n):
        s = i_sig[k]
        if seq and s < busy_until:
            continue
        dd = d[k]
        j = s + 1
        if j >= nb:
            continue
        f = -1
        E = np.nan
        if kind[k] == 0:
            f = j
            E = o[j]
        else:
            lev = level[k]
            for q in range(j, min(i_exp[k], nb - 1) + 1):
                if kind[k] == 1:   # Stop-Einstieg
                    if (dd > 0 and h[q] >= lev) or (dd < 0 and l[q] <= lev):
                        f = q
                        E = max(o[q], lev) if dd > 0 else min(o[q], lev)
                        break
                else:              # Limit-Einstieg
                    if (dd > 0 and l[q] <= lev) or (dd < 0 and h[q] >= lev):
                        f = q
                        E = min(o[q], lev) if dd > 0 else max(o[q], lev)
                        break
            if f < 0:
                out_code[k] = -7
                if seq:
                    busy_until = min(i_exp[k], nb - 1) + 1
                continue
        risk = dd * (E - stop0[k])
        T = tgtA[k] if not np.isnan(tgtA[k]) else (E + dd * tgtR[k] * risk if not np.isnan(tgtR[k]) else np.nan)
        if risk <= 0 or (not np.isnan(T) and dd * (T - E) <= 0) or f > i_last[k]:
            out_code[k] = -8
            if seq:
                busy_until = f + 1
            continue
        P1 = E + dd * tp1R[k] * risk if not np.isnan(tp1R[k]) else np.nan
        frac_open = 1.0
        realized = 0.0
        cur = stop0[k]
        code = 0
        X = np.nan
        ex = -1
        for i in range(f, nb):
            if i > i_last[k]:
                break
            if use_trail[k] and i > f:
                tv = trail[i - 1]
                if not np.isnan(tv):
                    cur = max(cur, tv) if dd > 0 else min(cur, tv)
            # Stop zuerst
            if (dd > 0 and l[i] <= cur) or (dd < 0 and h[i] >= cur):
                px = cur
                if i > f:
                    px = min(o[i], cur) if dd > 0 else max(o[i], cur)
                X = px
                ex = i
                code = -1
                break
            if i == f and kind[k] != 0:
                # Fuellkerze einer Pending-Order: Ziel nur, wenn der Schluss jenseits liegt (konservativ)
                if not np.isnan(T) and ((dd > 0 and c[i] >= T) or (dd < 0 and c[i] <= T)):
                    X = T
                    ex = i
                    code = 1
                    break
                continue
            if not np.isnan(P1) and frac_open == 1.0 and ((dd > 0 and h[i] >= P1) or (dd < 0 and l[i] <= P1)):
                realized += tp1f[k] * dd * (P1 - E)
                frac_open = 1.0 - tp1f[k]
                if be1[k]:
                    cur = max(cur, E) if dd > 0 else min(cur, E)
            if not np.isnan(T) and ((dd > 0 and h[i] >= T) or (dd < 0 and l[i] <= T)):
                X = T
                ex = i
                code = 1
                break
        if ex < 0:
            ex = min(i_last[k], nb - 1)
            X = c[ex]
            code = 0
        rg = (realized + frac_open * dd * (X - E)) / risk
        out_fill[k] = f
        out_exit[k] = ex
        out_E[k] = E
        out_X[k] = X
        out_Rg[k] = rg
        out_R[k] = rg - cost * E / risk
        out_code[k] = code
        if seq:
            busy_until = ex + 1
    return out_fill, out_exit, out_E, out_X, out_Rg, out_R, out_code


def _arr(sig, col, default, dtype=float):
    if col in sig.columns:
        return sig[col].fillna(default).to_numpy(dtype)
    return np.full(len(sig), default, dtype)


def simulate(df, sig, inst=None, seq=True, cost=None):
    """Simuliert Signale auf dem Kerzen-DataFrame df (Index Serverzeit, Spalten o h l c ...).
    Gibt sig mit Ergebnisspalten zurueck (nur gefuellte und auswertbare Trades haben R)."""
    inst = inst or df.attrs.get('inst')
    cost = Q.COST[inst] if cost is None else cost
    sig = sig.sort_values('i_sig').reset_index(drop=True).copy()
    if len(sig) == 0:
        return sig.assign(R=[], code=[])
    o, h, l, c = (df[x].to_numpy(float) for x in 'ohlc')
    kind = np.array([KIND[x] for x in (sig['kind'] if 'kind' in sig.columns else ['market'] * len(sig))], np.int64)
    trail_name = sig['trail'].dropna().unique() if 'trail' in sig.columns else []
    if len(trail_name) > 1:
        raise ValueError('nur eine Nachzieh-Spalte je Lauf')
    trail = df[trail_name[0]].to_numpy(float) if len(trail_name) == 1 else np.full(len(df), np.nan)
    use_trail = (sig['trail'].notna().to_numpy() if 'trail' in sig.columns else np.zeros(len(sig), bool))
    res = _sim(o, h, l, c, sig['i_sig'].to_numpy(np.int64), sig['d'].to_numpy(np.int64), kind,
               _arr(sig, 'level', np.nan), _arr(sig, 'i_exp', -1, np.int64), sig['stop'].to_numpy(float),
               _arr(sig, 'tgt_R', np.nan), _arr(sig, 'tgt_abs', np.nan), sig['i_last'].to_numpy(np.int64),
               trail, use_trail, _arr(sig, 'tp1_R', np.nan), _arr(sig, 'tp1_frac', 0.0),
               _arr(sig, 'be_after_tp1', False, bool), float(cost), bool(seq))
    for name, v in zip(['i_fill', 'i_exit', 'E', 'X', 'R_gross', 'R', 'code'], res):
        sig[name] = v
    idx = df.index
    ok = sig['i_fill'] >= 0
    sig['t_entry'] = pd.NaT
    sig.loc[ok, 't_entry'] = idx[sig.loc[ok, 'i_fill'].to_numpy()]
    sig['t_exit'] = pd.NaT
    sig.loc[ok, 't_exit'] = idx[sig.loc[ok, 'i_exit'].to_numpy()] + pd.Timedelta(minutes=5)
    sig['t_sig'] = idx[sig['i_sig'].to_numpy()] + pd.Timedelta(minutes=5)
    sig['risk_pct'] = (sig['E'] - sig['stop']).abs() / sig['E']
    sig['inst'] = inst
    return sig


def trades_only(res):
    return res[res['code'].isin([1, -1, 0])].copy()


# ---------------------------------------------------------------- Kennzahlen

def n_trading_days(df):
    a, b = df.attrs.get('eval_start'), df.attrs.get('eval_end')
    x = df.index
    if a is not None:
        x = x[(x >= a) & (x < b)]
    ny = Q.server_to_ny(x)
    return int(pd.Series(ny.normalize()).loc[lambda s: s.dt.dayofweek < 5].nunique())


def summarize(tr, n_days=None):
    tr = trades_only(tr)
    n = len(tr)
    if n == 0:
        return dict(n=0, per_day=0.0, days_cov=0.0, tvs=np.nan, win=np.nan, R=np.nan, t=np.nan, t_day=np.nan, time_exit=np.nan)
    R = tr['R'].to_numpy()
    hit = (tr['code'] == 1).sum()
    stp = (tr['code'] == -1).sum()
    sd = R.std(ddof=1) if n > 1 else np.nan
    day = Q.server_to_ny(pd.DatetimeIndex(tr['t_entry'])).normalize()
    dsum = pd.Series(R, index=day).groupby(level=0).sum()
    t_day = dsum.mean() / (dsum.std(ddof=1) / np.sqrt(len(dsum))) * 1.0 if len(dsum) > 1 else np.nan
    out = dict(n=n, per_day=(n / n_days if n_days else np.nan), days_cov=(len(dsum) / n_days if n_days else np.nan),
               tvs=hit / max(hit + stp, 1), win=(R > 0).mean(),
               R=R.mean(), t=R.mean() / (sd / np.sqrt(n)) if n > 1 and sd > 0 else np.nan,
               t_day=t_day, time_exit=(tr['code'] == 0).mean(), R_gross=tr['R_gross'].mean())
    return out


def by_period(tr, df, periods):
    """periods: dict name -> (start, end). Kennzahlen je Zeitraum (nach Einstiegszeit, Serverzeit)."""
    rows = {}
    for name, (a, b) in periods.items():
        a, b = pd.Timestamp(a), pd.Timestamp(b)
        x = tr[(tr['t_entry'] >= a) & (tr['t_entry'] < b)]
        sub = df[(df.index >= a) & (df.index < b)]
        sub.attrs.update(df.attrs)
        sub.attrs['eval_start'], sub.attrs['eval_end'] = a, b
        rows[name] = summarize(x, n_trading_days(sub))
    return pd.DataFrame(rows).T


# ---------------------------------------------------------------- Nullmodell

def null_model(df, tr, K=20, seed=7, a=None, b=None, extra_cols=()):
    """Gleiche Geometrie, Richtung und Uhrzeit; Tag gleichverteilt ueber den Zeitraum [a, b).
    Jeder Trade wird K-mal an zufaelligen Handelstagen zur selben NY-Uhrzeit nachgestellt:
    Market-Einstieg zur Eroeffnung derselben Kerzenzeit, Stop im selben Prozentabstand, gleiches Ziel in R,
    Zeitausstieg zur selben Uhrzeit, gleiche Nachzieh-Spalte. Pending-Orders: gleicher Prozentabstand zum
    Schluss der Signalkerze, gleiche Gueltigkeitsdauer."""
    tr = trades_only(tr)
    if len(tr) == 0:
        return dict(n=0)
    a = pd.Timestamp(a) if a is not None else df.attrs.get('eval_start', df.index[0])
    b = pd.Timestamp(b) if b is not None else df.attrs.get('eval_end', df.index[-1])
    idx = df.index
    ny = Q.server_to_ny(idx)
    day = ny.normalize()
    tod = (ny - day).total_seconds().astype(np.int64) // 60
    pos = pd.Series(np.arange(len(idx)), index=pd.MultiIndex.from_arrays([day, tod]))
    pos = pos[~pos.index.duplicated()]
    days = pd.Index(day[(idx >= a) & (idx < b)].unique())
    days = days[days.dayofweek < 5]
    rng = np.random.default_rng(seed)
    c = df['c'].to_numpy(float)
    rows = []
    for _, t in tr.iterrows():
        sig_ny = Q.server_to_ny(pd.DatetimeIndex([idx[t['i_sig']]]))[0]
        sig_tod = int((sig_ny - sig_ny.normalize()).total_seconds() // 60)
        last_ny = Q.server_to_ny(pd.DatetimeIndex([idx[min(int(t['i_last']), len(idx) - 1)]]))[0]
        span_days = (last_ny.normalize() - sig_ny.normalize()).days
        last_tod = int((last_ny - last_ny.normalize()).total_seconds() // 60)
        exp_bars = int(t['i_exp'] - t['i_sig']) if t.get('kind', 'market') != 'market' else 0
        stop_pct = abs(t['E'] - t['stop']) / t['E']
        for dday in rng.choice(days, size=K, replace=True):
            dday = pd.Timestamp(dday)
            j = pos.get((dday, sig_tod))
            jl = pos.get((dday + pd.Timedelta(days=span_days), last_tod))
            if j is None or jl is None or jl <= j:
                continue
            r = dict(i_sig=int(j), d=int(t['d']), i_last=int(jl), kind=t.get('kind', 'market'))
            ref = c[j]
            if r['kind'] == 'market':
                ref = df['o'].iat[j + 1] if j + 1 < len(idx) else np.nan
                r['stop'] = ref * (1 - t['d'] * stop_pct)
            else:
                lev_pct = (t['level'] - c[int(t['i_sig'])]) / c[int(t['i_sig'])]
                r['level'] = ref * (1 + lev_pct)
                r['i_exp'] = int(j + exp_bars)
                r['stop'] = r['level'] * (1 - t['d'] * abs(t['level'] - t['stop']) / t['level'])
            for col in ('tgt_R', 'trail', 'tp1_R', 'tp1_frac', 'be_after_tp1') + tuple(extra_cols):
                if col in tr.columns:
                    r[col] = t[col]
            if 'tgt_abs' in tr.columns and not pd.isna(t.get('tgt_abs', np.nan)):
                r['tgt_R'] = abs(t['tgt_abs'] - t['E']) / abs(t['E'] - t['stop'])
            rows.append(r)
    ns = pd.DataFrame(rows)
    res = simulate(df, ns, seq=False)
    s = summarize(res)
    return s


def report_cell(df, tr, periods, K=20, seed=7):
    """Tabelle je Zeitraum: Kennzahlen und Nullmodell (jeweils im eigenen Zeitraum)."""
    rows = []
    for name, (a, b) in periods.items():
        a, b = pd.Timestamp(a), pd.Timestamp(b)
        x = tr[(tr['t_entry'] >= a) & (tr['t_entry'] < b)]
        sub = df[(df.index >= a) & (df.index < b)]
        nd = n_trading_days(sub.assign()) if len(sub) else 0
        s = summarize(x, nd)
        nm = null_model(df, x, K=K, seed=seed, a=a, b=b) if s['n'] > 0 else dict(n=0)
        s.update({'null_tvs': nm.get('tvs', np.nan), 'null_win': nm.get('win', np.nan), 'null_R': nm.get('R', np.nan)})
        if s['n'] > 1:
            sd = trades_only(x)['R'].std(ddof=1)
            s['t_vs_null'] = (s['R'] - s['null_R']) / (sd / np.sqrt(s['n']))
        rows.append(pd.Series(s, name=name))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- Sitzungen, Noise-Area, VWAP

def session_frame(df, tz='America/New_York', open_hm=(9, 30), close_hm=(16, 0)):
    """Ergaenzt Ortszeit, Sitzungstag und Minute seit Sitzungsbeginn (Kerzenschluss).
    Nur Kerzen, deren Zeitraum in [open, close) liegt, bekommen in_sess=True."""
    loc = Q.server_to_tz(df.index, tz) if tz != 'America/New_York' else Q.server_to_ny(df.index)
    x = df.copy()
    x['loc'] = loc
    x['sday'] = loc.normalize()
    m_open = (loc - loc.normalize()).total_seconds() // 60     # Kerzenbeginn in Minuten
    o_m = open_hm[0] * 60 + open_hm[1]
    c_m = close_hm[0] * 60 + close_hm[1]
    x['m_bar'] = m_open.astype(int)
    x['in_sess'] = (m_open >= o_m) & (m_open + 5 <= c_m) & (loc.dayofweek < 5)
    x['m_close'] = (m_open + 5 - o_m).astype(int)              # Minuten seit Sitzungsbeginn am Kerzenschluss
    x.attrs.update(df.attrs)
    return x


def noise_area(x, lookback=14, vol_mult=1.0, prev_close='session'):
    """Noise-Area nach Zarattini/Aziz/Barbon (2024) auf Kerzenbasis.
    sigma(m) = Mittel der letzten `lookback` Sitzungen von |close(m)/open_tag - 1| (ohne heute).
    UB = max(O, C_vortag) * (1 + vol_mult*sigma), LB = min(O, C_vortag) * (1 - vol_mult*sigma).
    Zusaetzlich: sitzungsverankerter VWAP (Tickvolumen, sonst gleichgewichtet) und Tages-SMA20 der Schlusskurse."""
    s = x[x['in_sess']].copy()
    g = s.groupby('sday')
    O = g['o'].first()
    if prev_close == 'session':
        C = g['c'].last()
    else:   # (h, m): Schluss der letzten Kerze mit Kerzenende <= h:m Ortszeit
        cm = prev_close[0] * 60 + prev_close[1]
        C = s[s['m_bar'] + 5 <= cm].groupby('sday')['c'].last()
    first_m = g['m_bar'].first()
    s['O'] = s['sday'].map(O)
    Cprev = C.shift(1)
    s['Cprev'] = s['sday'].map(Cprev)
    s['move'] = (s['c'] / s['O'] - 1).abs()
    piv = s.pivot_table(index='sday', columns='m_close', values='move', aggfunc='first')
    sig = piv.rolling(lookback, min_periods=max(5, lookback * 2 // 3)).mean().shift(1)
    st = sig.stack(future_stack=True).rename('sigma')
    s = s.join(st, on=['sday', 'm_close'])
    s['UB'] = np.maximum(s['O'], s['Cprev']) * (1 + vol_mult * s['sigma'])
    s['LB'] = np.minimum(s['O'], s['Cprev']) * (1 - vol_mult * s['sigma'])
    v = s['v'].where(s['v'] > 0, 1.0)
    tp = (s['h'] + s['l'] + s['c']) / 3
    s['vwap'] = (tp * v).groupby(s['sday']).cumsum() / v.groupby(s['sday']).cumsum()
    sma20 = C.rolling(20).mean()
    s['sma20_prev'] = s['sday'].map(sma20.shift(1))       # SMA20 bis einschliesslich Vortag
    s['cprev_sess'] = s['sday'].map(Cprev)
    s['day_ok'] = s['sday'].map(first_m) <= s['m_bar'].min() + 30
    out = x.join(s[['O', 'Cprev', 'sigma', 'UB', 'LB', 'vwap', 'sma20_prev', 'day_ok']])
    out.attrs.update(x.attrs)
    return out
