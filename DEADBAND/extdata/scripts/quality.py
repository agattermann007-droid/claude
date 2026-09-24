"""Qualitätsprüfung der erzeugten M5-Dateien (liest die fertigen MT5-CSV) + Vergleich mit GFT-Dateien."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

def read_mt5(path):
    df = pd.read_csv(path, sep='\t')
    df.columns = [c.strip('<>') for c in df.columns]
    df.index = pd.to_datetime(df.DATE + ' ' + df.TIME, format='%Y.%m.%d %H:%M:%S')
    return df

def gaps(df, min_gap_min=30):
    """Lücken innerhalb eines Handelstages (gleicher Server-Kalendertag, Mo-Fr, zwischen 01:00 und 23:10)."""
    t = df.index.to_series()
    prev = t.shift(1)
    same_day = t.dt.date == prev.dt.date
    dur = (t - prev).dt.total_seconds() / 60
    g = pd.DataFrame({'start': prev + pd.Timedelta(minutes=5), 'end': t, 'min': dur - 5})
    g = g[same_day & (dur > min_gap_min + 5)]
    # Tagespause/Session-Ende ignorieren: Lücken, die bis zum Tagesende reichen, erkennt man hier nicht (nur intra-day)
    return g

def summary(path, name, gft_sym=None, price_tol=None):
    df = read_mt5(path)
    out = {}
    out['name'] = name
    out['rows'] = len(df); out['first'] = str(df.index.min()); out['last'] = str(df.index.max())
    out['ohlc_bad'] = int(((df.HIGH < df[['OPEN','CLOSE']].max(axis=1)) | (df.LOW > df[['OPEN','CLOSE']].min(axis=1))).sum())
    out['dup_ts'] = int(df.index.duplicated().sum())
    out['weekend_bars'] = int((df.index.dayofweek >= 5).sum())
    days = df.groupby(df.index.date).size()
    yr = pd.DataFrame({'bars': df.groupby(df.index.year).size(),
                       'days': pd.Series(days.index, index=pd.to_datetime(days.index)).groupby(lambda x: x.year).size(),
                       'bars_per_day_med': pd.Series(days.values, index=pd.to_datetime(days.index)).groupby(lambda x: x.year).median(),
                       'tickvol_zero_share': df.groupby(df.index.year).TICKVOL.apply(lambda s: round((s == 0).mean(), 3)),
                       'spread_med_pts': df.groupby(df.index.year).SPREAD.median()})
    g = gaps(df)
    yr['gaps_gt30min'] = g.groupby(g.end.dt.year).size()
    yr['gap_hours_sum'] = (g.groupby(g.end.dt.year)['min'].sum() / 60).round(1)
    # Ausreißer: Range > 15x Median-Range des Tages oder |Rendite| > 2 % in 5 Min
    rng = df.HIGH - df.LOW
    med_day = rng.groupby(df.index.date).transform('median')
    ret = np.log(df.CLOSE).diff().abs()
    same_day = pd.Series(df.index.date, index=df.index) == pd.Series(df.index.date, index=df.index).shift(1)
    spikes = df[((rng > 15 * med_day) & (med_day > 0)) | ((ret > 0.02) & same_day)]
    yr['spike_bars'] = spikes.groupby(spikes.index.year).size()
    yr = yr.fillna(0)
    out['yearly'] = yr
    out['gaps'] = g.sort_values('min', ascending=False)
    out['spikes'] = spikes
    if gft_sym:
        gft = load_gft(gft_sym).set_index('ts_server')
        j = df[['OPEN','HIGH','LOW','CLOSE','SPREAD','TICKVOL']].join(gft[['OPEN','HIGH','LOW','CLOSE','SPREAD','TICKVOL']], how='inner', lsuffix='_x', rsuffix='_g')
        j['r_x'] = np.log(j.CLOSE_x).diff(); j['r_g'] = np.log(j.CLOSE_g).diff()
        cont = (j.index.to_series().diff() == pd.Timedelta(minutes=5))
        jj = j[cont]
        ov = pd.DataFrame({
            'bars_both': j.groupby(j.index.year).size(),
            'ret_corr': jj.groupby(jj.index.year).apply(lambda x: round(x.r_x.corr(x.r_g), 4)),
            'close_diff_med': j.groupby(j.index.year).apply(lambda x: round((x.CLOSE_x - x.CLOSE_g).median(), 3)),
            'close_absdiff_med': j.groupby(j.index.year).apply(lambda x: round((x.CLOSE_x - x.CLOSE_g).abs().median(), 3)),
            'range_ratio_med': j.groupby(j.index.year).apply(lambda x: round(((x.HIGH_x - x.LOW_x) / (x.HIGH_g - x.LOW_g)).replace([np.inf, -np.inf], np.nan).median(), 3)),
            'tickvol_corr': j.groupby(j.index.year).apply(lambda x: round(x.TICKVOL_x.corr(x.TICKVOL_g), 3)),
            'spread_med_x': j.groupby(j.index.year).SPREAD_x.median(),
            'spread_med_gft': j.groupby(j.index.year).SPREAD_g.median(),
        })
        # Abdeckung: GFT-Bars ohne ext-Bar und umgekehrt (im Überlappungszeitraum)
        lo, hi = max(df.index.min(), gft.index.min()), min(df.index.max(), gft.index.max())
        gi = gft.index[(gft.index >= lo) & (gft.index <= hi)]; xi = df.index[(df.index >= lo) & (df.index <= hi)]
        miss_in_ext = gi.difference(xi); extra_in_ext = xi.difference(gi)
        out['overlap'] = ov
        out['overlap_cov'] = {'period': f'{lo} .. {hi}', 'gft_bars': len(gi), 'ext_bars': len(xi),
                              'gft_bars_missing_in_ext': len(miss_in_ext), 'ext_bars_not_in_gft': len(extra_in_ext),
                              'missing_by_server_hour': pd.Series(miss_in_ext.hour).value_counts().sort_index().to_dict(),
                              'extra_by_server_hour': pd.Series(extra_in_ext.hour).value_counts().sort_index().to_dict()}
        # Wochenweise Rendite-Korrelation (Verteilung)
        wk = jj.groupby(jj.index.to_period('W')).apply(lambda x: x.r_x.corr(x.r_g) if len(x) > 200 else np.nan).dropna()
        out['weekly_corr'] = wk.describe().round(4).to_dict()
        out['weekly_corr_low'] = wk[wk < 0.9]
    return out

if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 200); pd.set_option('display.max_columns', 30)
    path, name = sys.argv[1], sys.argv[2]
    gsym = sys.argv[3] if len(sys.argv) > 3 else None
    s = summary(path, name, gsym)
    for k in ['name','rows','first','last','ohlc_bad','dup_ts','weekend_bars']: print(k, ':', s[k])
    print(s['yearly'].to_string())
    print('Top-Lücken:'); print(s['gaps'].head(15).to_string())
    print('Spikes:', len(s['spikes'])); print(s['spikes'].head(15).to_string())
    if gsym:
        print(s['overlap'].to_string()); print(s['overlap_cov']); print('weekly corr:', s['weekly_corr'])
        print('Wochen mit corr<0.9:'); print(s['weekly_corr_low'].to_string())
    pd.to_pickle(s, f'{EXT}/work/quality_{name}.pkl')
