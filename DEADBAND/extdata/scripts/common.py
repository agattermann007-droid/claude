"""Gemeinsame Hilfsfunktionen: Laden, Zeitzonen, Resampling, Offset-Analyse."""
import glob, json, os
import numpy as np, pandas as pd

BASE = os.environ.get('DEADBAND_BASE', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))   # Ordner DEADBAND (data/, extdata/)
EXT = BASE + '/extdata'
NY = 'America/New_York'

def load_gft(sym):
    """GFT-MT5-Export (Serverzeit = NY+7h). Liefert DataFrame mit ts_server, ts_utc."""
    df = pd.read_csv(f'{BASE}/data/{sym}_M5.csv', sep='\t')
    df.columns = [c.strip('<>') for c in df.columns]
    df['ts_server'] = pd.to_datetime(df.DATE + ' ' + df.TIME, format='%Y.%m.%d %H:%M:%S')
    df['ts_utc'] = server_to_utc(df['ts_server'])
    return df

def utc_to_server(ts_utc):
    """UTC (naiv oder tz-aware) -> GFT-Serverzeit (naiv) = New-York-Ortszeit + 7h (US-Sommerzeitregeln)."""
    s = pd.DatetimeIndex(ts_utc)
    if s.tz is None:
        s = s.tz_localize('UTC')
    return (s.tz_convert(NY).tz_localize(None) + pd.Timedelta(hours=7))

def server_to_utc(ts_server):
    """GFT-Serverzeit (naiv) -> UTC (naiv). Server-7h = NY-Ortszeit; mehrdeutige Stunde tritt nicht auf,
    da NY 01:00-02:00 (Fall-back) = Server 08:00-09:00 -> wir nutzen ambiguous='NaT' und melden das."""
    s = pd.DatetimeIndex(ts_server) - pd.Timedelta(hours=7)
    loc = s.tz_localize(NY, ambiguous='NaT', nonexistent='NaT')
    return loc.tz_convert('UTC').tz_localize(None)

def resample_ohlc(df, ts_col, rule='5min', price_cols=('open','high','low','close'), extra_sum=(), extra_min=(), extra_first=()):
    g = df.set_index(ts_col).sort_index()
    agg = {price_cols[0]:'first', price_cols[1]:'max', price_cols[2]:'min', price_cols[3]:'last'}
    for c in extra_sum: agg[c] = 'sum'
    for c in extra_min: agg[c] = 'min'
    for c in extra_first: agg[c] = 'first'
    out = g.resample(rule, label='left', closed='left').agg(agg)
    out = out.dropna(subset=[price_cols[3]])
    return out

def weekly_offset_scan(src_close, ref_close, offsets_h, min_pairs=200):
    """src_close: pd.Series (naiver Quell-Zeitstempel, M5 close). ref_close: pd.Series (UTC, M5 close).
    Für jede Woche (nach UTC) und jeden Kandidaten-Offset h (src_ts = utc + h) wird die Korrelation der
    5-Min-Log-Renditen berechnet. Ergebnis: DataFrame je Woche mit bestem Offset und Score."""
    ref_r = np.log(ref_close).diff()
    res = {}
    for h in offsets_h:
        s = src_close.copy()
        s.index = s.index - pd.Timedelta(hours=h)   # -> UTC
        r = np.log(s).diff()
        j = pd.concat([r.rename('s'), ref_r.rename('r')], axis=1, join='inner').dropna()
        j = j[(j.s != 0) | (j.r != 0)]
        wk = j.index.to_period('W-SAT')  # Wochen So-Sa
        grp = j.groupby(wk)
        res[h] = pd.DataFrame({'corr': grp.apply(lambda x: x.s.corr(x.r) if len(x) >= min_pairs else np.nan),
                               'n': grp.size()})
    corr = pd.concat({h: res[h]['corr'] for h in offsets_h}, axis=1)
    n = pd.concat({h: res[h]['n'] for h in offsets_h}, axis=1)
    corr = corr[corr.notna().any(axis=1)]
    n = n.loc[corr.index]
    best = corr.idxmax(axis=1)
    top = corr.max(axis=1)
    second = corr.apply(lambda r: r.drop(r.idxmax()).max() if r.notna().sum() > 1 else np.nan, axis=1)
    return pd.DataFrame({'best': best, 'corr': top, 'second': second, 'n': n.max(axis=1)})

def write_mt5(m5, path, digits=2):
    """m5: DataFrame index = Serverzeit (Bar-Open), Spalten open, high, low, close, tickvol, spread.
    Schreibt MT5-Export-Format (Tab, CRLF, Kopfzeile wie GFT-Dateien)."""
    df = m5.copy()
    fmt = '{:.%df}' % digits
    out = pd.DataFrame({
        '<DATE>': df.index.strftime('%Y.%m.%d'),
        '<TIME>': df.index.strftime('%H:%M:%S'),
        '<OPEN>': df.open.round(digits).map(fmt.format),
        '<HIGH>': df.high.round(digits).map(fmt.format),
        '<LOW>': df.low.round(digits).map(fmt.format),
        '<CLOSE>': df.close.round(digits).map(fmt.format),
        '<TICKVOL>': df.tickvol.fillna(0).round().astype('int64'),
        '<VOL>': 0,
        '<SPREAD>': df.spread.fillna(0).round().astype('int64'),
    })
    out.to_csv(path, sep='\t', index=False, lineterminator='\r\n')
    return len(out)
