"""FX31337/FX-BT-Data-XAUUSD-DS (Dukascopy-Ticks, UTC) -> M1 Bid/Ask-Kerzen.
Die Tick-CSV enthalten Preise mit falschem Skalenfaktor (/100, Downloader nutzte Punktwert 1e5 statt 1e3):
z. B. 11.9426 = 1194.26 USD. Wir multiplizieren mit 100 und runden auf 3 Nachkommastellen.
Spalten der Quelle: Zeit (UTC, ms), Bid, Ask, Vol1, Vol2 (Volumen immer 0.00)."""
import sys, os, glob, io, subprocess, time
import numpy as np, pandas as pd
year = sys.argv[1]
root = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')), 'raw', 'fx31337_dukascopy_xauusd_ticks')
repo = f'{root}/y{year}'
outdir = f'{root}/derived_M1'; os.makedirs(outdir, exist_ok=True)
t0 = time.time()
files = sorted(glob.glob(f'{repo}/XAUUSD/{year}/*/*_ticks.csv'))
buf = subprocess.run(['cat'] + files, capture_output=True, check=True).stdout
df = pd.read_csv(io.BytesIO(buf), header=None, names=['t','bid','ask','v1','v2'],
                 dtype={'t':str,'bid':np.float64,'ask':np.float64,'v1':np.float64,'v2':np.float64})
del buf
n_raw = len(df)
df['t'] = pd.to_datetime(df['t'], format='%Y.%m.%d %H:%M:%S.%f')
df['bid'] = (df['bid']*100).round(3); df['ask'] = (df['ask']*100).round(3)
stats = {'year': year, 'files': len(files), 'ticks': n_raw,
         'vol_nonzero': int(((df.v1 != 0) | (df.v2 != 0)).sum()),
         'ask_lt_bid': int((df.ask < df.bid).sum()), 'zero_price': int(((df.bid <= 0) | (df.ask <= 0)).sum()),
         'non_monotonic': int((df.t.diff().dt.total_seconds() < 0).sum()),
         'dup_ts': int(df.t.duplicated().sum())}
df = df[(df.bid > 0) & (df.ask > 0)]
df = df.sort_values('t', kind='stable')
df['spr'] = df.ask - df.bid
df['m'] = df.t.dt.floor('min')
g = df.groupby('m', sort=True)
m1 = pd.DataFrame({
    'open_bid': g.bid.first(), 'high_bid': g.bid.max(), 'low_bid': g.bid.min(), 'close_bid': g.bid.last(),
    'open_ask': g.ask.first(), 'high_ask': g.ask.max(), 'low_ask': g.ask.min(), 'close_ask': g.ask.last(),
    'ticks': g.bid.size(), 'spread_min': g.spr.min().round(3), 'spread_mean': g.spr.mean().round(4)})
m1.index.name = 'ts_utc'
out = f'{outdir}/XAUUSD_M1_bidask_dukascopy_{year}.csv.gz'
m1.to_csv(out, compression='gzip')
stats.update({'m1_bars': len(m1), 'first': str(m1.index.min()), 'last': str(m1.index.max()),
              'spread_median': float(df.spr.median()), 'secs': round(time.time()-t0, 1)})
print(stats)
with open(f'{outdir}/stats_{year}.txt', 'w') as f: f.write(repr(stats) + '\n')
