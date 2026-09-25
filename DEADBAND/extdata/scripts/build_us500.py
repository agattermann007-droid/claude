"""Build 6.60: US500 (S&P 500 CFD) aus dem MT5-Broker-Export ts4blader/market_data (gleiche Quelle wie US100/NAS100-Teil M).
  US500/M1_seed.csv (Git-LFS, Commit 5246088b258b9e94cf43300e5bd8769695c49526, SHA-256 3951499477feef3c...),
  2020-01-02 .. 2025-12-31, Serverzeit (Pruefung unten: NY + 7 h), Preise 1 Nachkommastelle, SPREAD in 0,1-Punkten.
  -> M5 wie build_mt5_sources.to_m5 (TICKVOL Summe, SPREAD Minimum der M1-Spreads, in 0,01-Punkte umgerechnet), ohne
  Serverstunde 00 und Wochenende -> ../US500_ext_M5.csv."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *


def read_seed(p):                     # wie build_mt5_sources.read_seed (dort laeuft Modulcode beim Import)
    df = pd.read_csv(p, sep='\t')
    df.columns = [c.strip('<>').strip() for c in df.columns]
    df['srv'] = pd.to_datetime(df.DATE + ' ' + df.TIME, format='%Y.%m.%d %H:%M:%S')
    return df.rename(columns={'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low', 'CLOSE': 'close', 'TICKVOL': 'tickvol',
                              'SPREAD': 'spread_raw'})


def to_m5(df, spread_factor):         # wie build_mt5_sources.to_m5
    m5 = resample_ohlc(df, 'srv', extra_sum=('tickvol',), extra_min=('spread_raw',))
    m5['spread'] = m5.spread_raw * spread_factor
    drop = (m5.index.hour == 0) | (m5.index.dayofweek >= 5)
    print('  verworfen', int(drop.sum()), 'von', len(m5))
    return m5[~drop][['open', 'high', 'low', 'close', 'tickvol', 'spread']]



u = read_seed(f'{EXT}/raw/ts4blader_market_data/US500/M1_seed.csv')
m5 = to_m5(u, 10)
n = write_mt5(m5, f'{EXT}/US500_ext_M5.csv', 2)
print('US500_ext_M5.csv', n, m5.index.min(), m5.index.max())
# Zeitpruefung: Kassa-Eroeffnung 09:30 NY = 16:30 Server -> Tickvolumen-Sprung; Vergleich mit US100 (gleicher Broker)
v = m5.tickvol.groupby([m5.index.hour, m5.index.minute]).median()
print('Median-Tickvolumen um 16:20/16:25/16:30/16:35 Server:', [float(v.loc[(16, mm)]) for mm in (20, 25, 30, 35)])
nas = pd.read_pickle(f'{EXT}/work/mt5_us100_m5.pkl')
j = pd.concat([np.log(m5.close).diff().rename('s'), np.log(nas.close).diff().rename('n')], axis=1, join='inner').dropna()
for lag in (-1, 0, 1):
    print(f'Korrelation M5-Renditen US500/US100, Versatz {lag} Kerzen: {j.s.corr(j.n.shift(lag)):.3f}')
print('Spread (0,01-Punkte) Median je Jahr:', m5.spread.groupby(m5.index.year).median().to_dict())
