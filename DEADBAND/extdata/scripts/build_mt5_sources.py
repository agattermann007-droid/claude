"""MT5-Broker-Exporte (Serverzeit bereits = New York + 7 h, geprüft):
  - ts4blader/market_data  US100/M1_seed.csv  (2021-01-04 .. 2025-12-31, Preise 1 Nachkommastelle, SPREAD in 0,1-Punkten)
  - AntonDonev/Tiamat      TiamatOffline/XAUUSD_M1_RAW.csv (2018-01-02 .. 2024-12-31, Preise 2 Nachkommastellen, SPREAD in 0,01)
  -> M5: OHLC, TICKVOL = Summe, SPREAD = Minimum der M1-Spreads (MT5-Konvention), umgerechnet in 0,01-Punkte.
  Schreibt work/mt5_us100_m5.pkl und XAUUSD_ext_mt5_M5.csv."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

def read_seed(p):
    df = pd.read_csv(p, sep='\t')
    df.columns = [c.strip('<>').strip() for c in df.columns]
    df['srv'] = pd.to_datetime(df.DATE + ' ' + df.TIME, format='%Y.%m.%d %H:%M:%S')
    return df.rename(columns={'OPEN':'open','HIGH':'high','LOW':'low','CLOSE':'close','TICKVOL':'tickvol','SPREAD':'spread_raw'})

def to_m5(df, spread_factor):
    m5 = resample_ohlc(df, 'srv', extra_sum=('tickvol',), extra_min=('spread_raw',))
    m5['spread'] = m5.spread_raw * spread_factor
    drop = (m5.index.hour == 0) | (m5.index.dayofweek >= 5)
    print('  verworfen', int(drop.sum()), 'von', len(m5))
    return m5[~drop][['open','high','low','close','tickvol','spread']]

u = read_seed(f'{EXT}/raw/ts4blader_market_data/US100/M1_seed.csv')
um5 = to_m5(u, 10)          # 0,1-Punkte -> 0,01-Punkte
um5['src'] = 'M'
um5.to_pickle(f'{EXT}/work/mt5_us100_m5.pkl')
print('US100 M5', len(um5), um5.index.min(), um5.index.max())

a = read_seed(f'{EXT}/raw/antondonev_tiamat/XAUUSD_M1_RAW.csv')
am5 = to_m5(a, 1)
am5.to_pickle(f'{EXT}/work/mt5_xau_m5.pkl')
n = write_mt5(am5, f'{EXT}/XAUUSD_ext_mt5_M5.csv', 2)
print('XAUUSD_ext_mt5_M5.csv', n, am5.index.min(), am5.index.max())
