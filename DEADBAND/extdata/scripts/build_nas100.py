"""NAS100-Dateien:
  NAS100_ext_M5.csv (Haupt), drei Segmente (Nahtstellen jeweils am Wochenende):
      O: OANDA NAS100_USD M1 (Mid, UTC, Tickvolumen)            2005-01-03 .. Fr 2020-05-08
      H: HistData NSXUSD M1 (via hizawye/better-backtest)       Mo 2020-05-11 .. Do 2020-12-31
      M: MT5-Broker-Export US100 M1 (ts4blader/market_data)     Mo 2021-01-04 .. 2025-12-31
      TICKVOL = OANDA- bzw. MT5-Tickanzahl; im HistData-Segment 0 (unbekannt).
      SPREAD  = 0 (unbekannt) in O und H; in M Minimum der M1-Spreads des Brokers, in 0,01-Punkte umgerechnet.
  NAS100_ext_histdata_M5.csv (Alternative): reine HistData-Reihe 2010-11-15 .. 2026-02-13, TICKVOL 0, SPREAD 0.
      Achtung: enthält 2011-2018 Rollsprünge des NQ-Frontmonats (siehe Bericht).
  Zeit: Quelle -> UTC -> New-York-Ortszeit + 7 h; Bars 00:00-00:59 Server und Wochenende verworfen."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
SEAM = pd.Timestamp('2020-05-09 00:00')   # Serverzeit (Samstag): OANDA -> HistData
SEAM2 = pd.Timestamp('2021-01-02 00:00')  # Serverzeit (Samstag): HistData -> MT5 US100

def session_filter(m5, name):
    drop = (m5.index.hour == 0) | (m5.index.dayofweek >= 5)
    h0 = m5[m5.index.hour == 0]
    print(f'{name}: verworfen {int(drop.sum())} von {len(m5)} (Stunde0 {len(h0)}, Wochenende {int((m5.index.dayofweek >= 5).sum())});',
          'Stunde0 je Jahr', h0.groupby(h0.index.year).size().to_dict())
    return m5[~drop]

# HistData
h = pd.read_pickle(f'{EXT}/work/nsx_histdata_m1_utc.pkl')     # ts (Quelle), ts_utc (umgerechnet)
h['srv'] = utc_to_server(h.ts_utc)
early = h.ts < pd.Timestamp('2019-01-01')
assert ((h.srv[early] - h.ts[early]) == pd.Timedelta(hours=7)).all()
print('Offset Server-Quelle ab 2019 (h):', (h.srv - h.ts)[~early].dt.total_seconds().div(3600).value_counts().to_dict())
hm5 = resample_ohlc(h, 'srv'); hm5['tickvol'] = 0; hm5['spread'] = 0; hm5['src'] = 'H'
hm5 = session_filter(hm5, 'HistData')
n = write_mt5(hm5, f'{EXT}/NAS100_ext_histdata_M5.csv', 2)
print('NAS100_ext_histdata_M5.csv', n, hm5.index.min(), hm5.index.max())

# OANDA
o = pd.read_pickle(f'{EXT}/work/oanda_nas100_m1.pkl')
o['srv'] = utc_to_server(o.ts)
om5 = resample_ohlc(o, 'srv', extra_sum=('volume',)).rename(columns={'volume': 'tickvol'})
om5['spread'] = 0; om5['src'] = 'O'
om5 = session_filter(om5, 'OANDA')

cols = ['open','high','low','close','tickvol','spread','src']
mm5 = pd.read_pickle(f'{EXT}/work/mt5_us100_m5.pkl')   # aus build_mt5_sources.py (Serverzeit = NY+7, geprüft)
m5 = pd.concat([om5.loc[om5.index < SEAM, cols], hm5.loc[(hm5.index >= SEAM) & (hm5.index < SEAM2), cols],
                mm5.loc[mm5.index >= SEAM2, cols]]).sort_index()
assert not m5.index.duplicated().any()
print('Bars je Quelle:', m5.src.value_counts().to_dict())
m5.to_pickle(f'{EXT}/work/nas100_ext_m5.pkl')
n = write_mt5(m5, f'{EXT}/NAS100_ext_M5.csv', 2)
print('NAS100_ext_M5.csv', n, m5.index.min(), m5.index.max(), 'SEAM', SEAM, 'SEAM2', SEAM2)
print(m5.loc['2020-12-31 22:30':'2021-01-04 01:30', ['open','high','low','close','tickvol','spread','src']].to_string())
# Nahtstelle
print(m5.loc['2020-05-08 22:30':'2020-05-11 01:30', ['open','high','low','close','tickvol','src']].to_string())
