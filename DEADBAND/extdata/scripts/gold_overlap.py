"""Überlappungsanalyse FX31337-Ticks (A) vs. Dypoi-M1 (B), beide Dukascopy, UTC. Liefert Kennzahlen und
Kalibrierfaktor k für den TICKVOL-Proxy (B-Volumen -> Tickanzahl-Äquivalent)."""
import sys, glob, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
A = pd.concat([pd.read_csv(f, parse_dates=['ts_utc']) for f in sorted(glob.glob(f'{EXT}/raw/fx31337_dukascopy_xauusd_ticks/derived_M1/*.csv.gz'))])
A = A.set_index('ts_utc').sort_index()
B = pd.read_pickle(f'{EXT}/work/dypoi_xau_m1.pkl').drop_duplicates('ts').set_index('ts').sort_index()
print('A', A.index.min(), A.index.max(), len(A)); print('B', B.index.min(), B.index.max(), len(B))
lo, hi = B.index.min(), A.index.max()
a = A.loc[lo:hi]; b = B.loc[lo:hi]
j = a.join(b, how='inner', lsuffix='_a', rsuffix='_b')
print('M1 overlap bars A', len(a), 'B', len(b), 'both', len(j))
for c in ['open_bid','high_bid','low_bid','close_bid','close_ask']:
    d = (j[c+'_a'] - j[c+'_b']).abs()
    print(f'{c}: |A-B| median {d.median():.4f}  p99 {d.quantile(.99):.4f}  max {d.max():.3f}  share==0 {(d<0.0005).mean():.4f}')
only_a = a.index.difference(b.index); only_b = b.index.difference(a.index)
print('M1 only in A', len(only_a), ' only in B', len(only_b))
# M5 in UTC
a5 = resample_ohlc(a.reset_index(), 'ts_utc', price_cols=('open_bid','high_bid','low_bid','close_bid'), extra_sum=('ticks',), extra_min=('spread_min',))
bb = b.reset_index(); bb['vol'] = bb.volume_bid + bb.volume_ask; bb['vb'] = bb.volume_bid
bb['spr_oc'] = np.minimum(bb.open_ask - bb.open_bid, bb.close_ask - bb.close_bid)
bb['spr_c'] = bb.close_ask - bb.close_bid
b5 = resample_ohlc(bb, 'ts', price_cols=('open_bid','high_bid','low_bid','close_bid'), extra_sum=('vol','vb'), extra_min=('spr_oc',))
b5['spr_c_med'] = bb.set_index('ts').spr_c.resample('5min').median()
k5 = a5.join(b5, how='inner', lsuffix='_a', rsuffix='_b')
print('M5 both', len(k5))
print('corr ticks vs vol(bid+ask):', round(k5.ticks.corr(k5.vol), 4), ' vs vol_bid:', round(k5.ticks.corr(k5.vb), 4))
print('corr log:', round(np.log1p(k5.ticks).corr(np.log1p(k5.vol*1000)), 4))
# Kalibrierfaktor: Verhältnis der Summen (robust: Median der Tagesverhältnisse)
day = k5.groupby(k5.index.date).agg(t=('ticks','sum'), v=('vol','sum'))
k_sum = k5.ticks.sum() / k5.vol.sum(); k_med = (day.t / day.v).median()
print('k (Summenverhältnis)', round(k_sum, 2), ' k (Median Tagesverhältnis)', round(k_med, 2))
# Zeitliche Stabilität des Verhältnisses (Monat)
mon = k5.groupby(k5.index.to_period('M')).agg(t=('ticks','sum'), v=('vol','sum'))
print((mon.t / mon.v).round(1).to_string())
# Spread: exaktes Minimum (A) vs Näherung (B, Minimum aus Open/Close-Spreads der M1)
d = (k5.spr_oc - k5.spread_min)
print('Spread-Min A (exakt) median', k5.spread_min.median(), ' B-Näherung median', k5.spr_oc.median(), ' B close-median', k5.spr_c_med.median())
print('B-Näherung minus A: median', round(d.median(), 4), ' mean', round(d.mean(), 4), ' p90', round(d.quantile(.9), 4))
pd.to_pickle({'k_sum_bidask': k_sum, 'k_med_bidask': k_med}, f'{EXT}/work/gold_overlap_k_bidask.pkl')   # nur Analyse; massgeblich ist gold_k.pkl aus prepare_sources.py
