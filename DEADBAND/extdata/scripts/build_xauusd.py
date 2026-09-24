"""Baut XAUUSD_ext_M5.csv: bis Fr 2011-05-13 OANDA XAU_USD M1 (Mid, UTC; TICKVOL = OANDA-Tickanzahl, SPREAD 0 = unbekannt),
ab Mo 2011-05-16 Dukascopy-Daten (alle drei Dukascopy-Quellen = derselbe Feed, geprüft):
  Teil A (Server < SEAM): FX31337/FX-BT-Data-XAUUSD-DS Ticks -> M1 (bid/ask) -> M5.
        TICKVOL = echte Dukascopy-Tickanzahl. Der Quelle fehlt systematisch die Stunde 00:00-00:59 UTC
        (Downloader-Fehler); diese Bars werden, soweit vorhanden, aus EPSOFT (Dukascopy-JForex-Export M5 Bid,
        nicht-flache Bars) ergänzt, dort TICKVOL=0 und SPREAD=0 (unbekannt; dient zugleich als Markierung).
  Teil B (Server >= SEAM): Dypoi/XAUUSD_Dataset M1 bid/ask -> M5. TICKVOL = Proxy = round(k * Bid-Volumen),
        k aus Überlappung 2016-09..2018-06 mit echten Tickzahlen kalibriert.
  SPREAD (beide Teile gleich definiert) = Minimum über die M1-Bars des M5-Bars von min(Open-Spread, Close-Spread),
        in Punkten (0,01 USD) - Näherung an die MT5-Konvention (minimaler Spread im Bar).
  Zeit: UTC -> New-York-Ortszeit + 7 h. Bars 00:00-00:59 Server (Tagespause bei GFT) und Wochenend-Bars werden verworfen.
  Zusätzlich XAUUSD_ext_oanda_M5.csv (OANDA XAU_USD Mid, 2006-2020, TICKVOL = OANDA-Tickvolumen, SPREAD 0)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
SEAM = pd.Timestamp(sys.argv[1] if len(sys.argv) > 1 else '2016-09-03 00:00')   # Serverzeit (Samstag): Teil A -> Teil B
SEAM0 = pd.Timestamp('2011-05-14 00:00')   # Serverzeit (Samstag): OANDA -> Dukascopy Teil A
k = pd.read_pickle(f'{EXT}/work/gold_k.pkl')['k_bid_med']

def spread_oc(df):
    return np.minimum(df.open_ask - df.open_bid, df.close_ask - df.close_bid)

# Teil A
A = pd.read_pickle(f'{EXT}/work/fx31337_xau_m1.pkl').reset_index()
A['srv'] = utc_to_server(A.ts_utc); A['spr_oc'] = spread_oc(A)
a5 = resample_ohlc(A, 'srv', price_cols=('open_bid','high_bid','low_bid','close_bid'), extra_sum=('ticks',), extra_min=('spr_oc',))
a5 = a5.rename(columns={'open_bid':'open','high_bid':'high','low_bid':'low','close_bid':'close','ticks':'tickvol'})
a5['spread'] = (a5.spr_oc * 100).round(); a5['src'] = 'A'
a5 = a5[a5.index < SEAM]
# EPSOFT-Füllung der fehlenden UTC-Stunde 0 im Zeitraum von Teil A
E = pd.read_pickle(f'{EXT}/work/epsoft_xau_m5.pkl')
E = E[~((E.High == E.Low) & (E.Volume == 0))]
E = E[E.index.hour == 0]
E = E.loc[A.ts_utc.min():A.ts_utc.max()]
e5 = pd.DataFrame({'open': E.Open, 'high': E.High, 'low': E.Low, 'close': E.Close, 'tickvol': 0, 'spread': 0, 'src': 'E'})
e5.index = utc_to_server(E.index)
e5 = e5[(e5.index < SEAM) & ~e5.index.isin(a5.index)]
print('EPSOFT-Füllbars:', len(e5))
# Teil B
B = pd.read_pickle(f'{EXT}/work/dypoi_xau_m1.pkl').drop_duplicates('ts')
B['srv'] = utc_to_server(B.ts); B['spr_oc'] = spread_oc(B)
b5 = resample_ohlc(B, 'srv', price_cols=('open_bid','high_bid','low_bid','close_bid'), extra_sum=('volume_bid',), extra_min=('spr_oc',))
b5 = b5.rename(columns={'open_bid':'open','high_bid':'high','low_bid':'low','close_bid':'close'})
b5['tickvol'] = (b5.volume_bid * k).round().clip(lower=1); b5['spread'] = (b5.spr_oc * 100).round(); b5['src'] = 'B'
b5 = b5[b5.index >= SEAM]

O = pd.read_pickle(f'{EXT}/work/oanda_xau_m1.pkl')
O['srv'] = utc_to_server(O.ts)
o5 = resample_ohlc(O, 'srv', extra_sum=('volume',)).rename(columns={'volume': 'tickvol'})
o5['spread'] = 0; o5['src'] = 'O'

cols = ['open','high','low','close','tickvol','spread','src']
a5 = a5[a5.index >= SEAM0]; e5 = e5[e5.index >= SEAM0]
m5 = pd.concat([o5.loc[o5.index < SEAM0, cols], a5[cols], e5[cols], b5[cols]]).sort_index()
assert not m5.index.duplicated().any()
drop = (m5.index.hour == 0) | (m5.index.dayofweek >= 5)
print('verworfen (Stunde 0 oder Wochenende):', int(drop.sum()), 'von', len(m5),
      ' Stunde0:', int((m5.index.hour == 0).sum()), ' Wochenende:', int((m5.index.dayofweek >= 5).sum()))
m5 = m5[~drop]
print('Bars je Quelle:', m5.src.value_counts().to_dict())
m5.to_pickle(f'{EXT}/work/xauusd_ext_m5.pkl')
n = write_mt5(m5, f'{EXT}/XAUUSD_ext_M5.csv', 2)
print('XAUUSD_ext_M5.csv', n, m5.index.min(), m5.index.max(), 'SEAM0', SEAM0, 'SEAM', SEAM, 'k', round(k, 1))
print(m5.loc['2011-05-13 23:30':'2011-05-16 01:20', cols].to_string())
print(m5.loc['2016-09-02 23:30':'2016-09-05 01:20', cols].to_string())

o5 = o5.drop(columns=['src'])
drop = (o5.index.hour == 0) | (o5.index.dayofweek >= 5)
print('OANDA XAU verworfen:', int(drop.sum()), 'von', len(o5), ' Stunde0:', int((o5.index.hour == 0).sum()))
o5 = o5[~drop]
o5.to_pickle(f'{EXT}/work/xauusd_oanda_m5.pkl')
n = write_mt5(o5, f'{EXT}/XAUUSD_ext_oanda_M5.csv', 2)
print('XAUUSD_ext_oanda_M5.csv', n, o5.index.min(), o5.index.max())
