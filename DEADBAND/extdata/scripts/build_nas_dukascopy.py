"""Build 6.60: NAS100 aus Dukascopy-Ticks (USATECHIDXUSD, Bid/Ask, UTC) fuer den Zukunftstest 2026.
Quelle: github.com/esmaeil999/dukascopy-tick-data, Release-Tag usatechidxusd-ticks-2025-01-01-to-2026-08-29 (Commit 4121bdc0),
Datei usatechidxusd-ticks-2025-01-01-to-2026-08-29.zip (SHA-256 65634bfe...), 2025-01-01 23:00 .. 2026-08-28 20:14 UTC.
Aufbereitung wie Gold-Segment A/B (build_xauusd): Ticks -> M1 Bid-OHLC, Spread je M1 = min(Open-Spread, Close-Spread);
M5 = Bid-OHLC, TICKVOL = Tickzahl, SPREAD = Minimum der M1-Spreads (MT5-Konvention) in 0,01-Punkten; UTC -> Serverzeit
(New York + 7 h), ohne Serverstunde 00 und Wochenende -> ../NAS100_duka_M5.csv.
Download: curl -L -o raw/dukascopy_usatech/usatechidxusd-ticks-2025-01-01-to-2026-08-29.zip \\
  https://github.com/esmaeil999/dukascopy-tick-data/releases/download/usatechidxusd-ticks-2025-01-01-to-2026-08-29/usatechidxusd-ticks-2025-01-01-to-2026-08-29.zip"""
import sys, os, subprocess, io, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

ZIP = f'{EXT}/raw/dukascopy_usatech/usatechidxusd-ticks-2025-01-01-to-2026-08-29.zip'
t0 = time.time()
proc = subprocess.Popen(['unzip', '-p', ZIP], stdout=subprocess.PIPE, bufsize=1 << 24)
parts = []
carry = None
n_ticks = 0
for ch in pd.read_csv(proc.stdout, usecols=[0, 1, 2], names=['t', 'bid', 'ask'], header=0, chunksize=5_000_000,
                      dtype={'bid': np.float64, 'ask': np.float64}):
    n_ticks += len(ch)
    ch['t'] = pd.to_datetime(ch['t'], format='%Y-%m-%d %H:%M:%S.%f')
    if carry is not None:
        ch = pd.concat([carry, ch], ignore_index=True)
    ch['m'] = ch['t'].dt.floor('min')
    last = ch['m'].iloc[-1]
    carry = ch[ch['m'] == last][['t', 'bid', 'ask']]
    ch = ch[ch['m'] < last]
    ch['spr'] = ch['ask'] - ch['bid']
    g = ch.groupby('m', sort=True)
    m1 = pd.DataFrame({'open': g.bid.first(), 'high': g.bid.max(), 'low': g.bid.min(), 'close': g.bid.last(),
                       'sp_o': g.spr.first(), 'sp_c': g.spr.last(), 'ticks': g.bid.size()})
    parts.append(m1)
    print(f'  {n_ticks / 1e6:.0f} Mio. Ticks, bis {last}  [{time.time() - t0:.0f}s]', flush=True)
if carry is not None and len(carry):
    carry = carry.copy(); carry['m'] = carry['t'].dt.floor('min'); carry['spr'] = carry['ask'] - carry['bid']
    g = carry.groupby('m')
    parts.append(pd.DataFrame({'open': g.bid.first(), 'high': g.bid.max(), 'low': g.bid.min(), 'close': g.bid.last(),
                               'sp_o': g.spr.first(), 'sp_c': g.spr.last(), 'ticks': g.bid.size()}))
M1 = pd.concat(parts).sort_index()
M1 = M1[~M1.index.duplicated(keep='first')]
M1['spread_raw'] = np.minimum(M1.sp_o, M1.sp_c)
M1.index.name = 'ts_utc'
M1.to_pickle(f'{EXT}/work/duka_nas_m1.pkl')
print('M1', len(M1), M1.index.min(), M1.index.max(), 'Ticks', n_ticks)
srv = utc_to_server(M1.index)
df = M1.reset_index(drop=True)
df['srv'] = srv
df = df.rename(columns={'ticks': 'tickvol'})
m5 = resample_ohlc(df, 'srv', extra_sum=('tickvol',), extra_min=('spread_raw',))
m5['spread'] = m5.spread_raw * 100.0                     # Punkte -> 0,01-Punkte
drop = (m5.index.hour == 0) | (m5.index.dayofweek >= 5)
print('  verworfen', int(drop.sum()), 'von', len(m5))
m5 = m5[~drop][['open', 'high', 'low', 'close', 'tickvol', 'spread']]
n = write_mt5(m5, f'{EXT}/NAS100_duka_M5.csv', 2)
print('NAS100_duka_M5.csv', n, m5.index.min(), m5.index.max(), f'[{time.time() - t0:.0f}s]')
print('Spread-Median (Punkte) je Monat:', (m5.spread.groupby(m5.index.to_period('M')).median() / 100).round(2).to_dict())
