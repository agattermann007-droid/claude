"""Schritt 1: Rohdaten (extdata/raw/...) -> Zwischendateien (extdata/work/*.pkl).
Voraussetzung: raw/ wie im Bericht beschrieben befüllt (git-Klone bzw. derived_M1 aus fx31337_ticks_to_m1.py)."""
import sys, glob, json, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import os
os.makedirs(f'{EXT}/work', exist_ok=True)

# 1) HistData NSXUSD (JSON aus hizawye/better-backtest). timestamp = Date.UTC(Quell-Wanduhr) -> naive Quellzeit
rows = []
for f in sorted(glob.glob(f'{EXT}/raw/histdata_nsxusd_better-backtest/data/histdata/nsxusd/normalized/*.json')):
    rows.extend(json.load(open(f)))
h = pd.DataFrame(rows); h['ts'] = pd.to_datetime(h.timestamp, unit='ms'); h = h.drop(columns=['timestamp'])
h = h.sort_values('ts').reset_index(drop=True)
h.to_pickle(f'{EXT}/work/nsx_histdata_m1.pkl')
# Quellzeit -> UTC (empirisch bestimmt, siehe Bericht):
#   bis 2018-12-31: New-York-Ortszeit (US-Sommerzeit)
#   ab 2019-01-01 : UTC-5h, +1h während EU-Sommerzeit (= Europe/Athens-Ortszeit - 7h)
ts = pd.DatetimeIndex(h.ts)
early = ts < pd.Timestamp('2019-01-01')
utc = pd.Series(pd.NaT, index=h.index, dtype='datetime64[ns]')
utc[early] = ts[early].tz_localize('America/New_York', ambiguous='NaT', nonexistent='NaT').tz_convert('UTC').tz_localize(None)
utc[~early] = (ts[~early] + pd.Timedelta(hours=7)).tz_localize('Europe/Athens', ambiguous='NaT', nonexistent='NaT').tz_convert('UTC').tz_localize(None)
assert utc.notna().all()
h['ts_utc'] = utc.values
h.to_pickle(f'{EXT}/work/nsx_histdata_m1_utc.pkl')
print('HistData NSXUSD', len(h), h.ts.min(), h.ts.max())

# 2) OANDA (FutureSharks/financial-data), Mid-Kerzen, UTC
def load_oanda(instr):
    fs = sorted(glob.glob(f'{EXT}/raw/oanda_futuresharks/pyfinancialdata/data/currencies/oanda/{instr}/*/*.csv'))
    df = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    df['ts'] = pd.to_datetime(df['time']); df = df.drop(columns=['time']).sort_values('ts').drop_duplicates('ts')
    return df.reset_index(drop=True)
for instr, nm in [('NAS100_USD', 'oanda_nas100_m1'), ('XAU_USD', 'oanda_xau_m1')]:
    d = load_oanda(instr); d.to_pickle(f'{EXT}/work/{nm}.pkl'); print('OANDA', instr, len(d), d.ts.min(), d.ts.max())

# 3) Dypoi (Dukascopy M1 bid/ask, UTC); Dateien überlappen am 1.9. jeden Jahres (identische Zeilen)
fs = sorted(glob.glob(f'{EXT}/raw/dypoi_dukascopy_xauusd_m1/XAUUSD_M1_*.csv'))
d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
d['ts'] = pd.to_datetime(d['timestamp']); d = d.drop(columns=['timestamp']).sort_values('ts').drop_duplicates('ts')
d.reset_index(drop=True).to_pickle(f'{EXT}/work/dypoi_xau_m1.pkl'); print('Dypoi', len(d), d.ts.min(), d.ts.max())

# 4) FX31337 Dukascopy-Ticks -> M1 (bereits durch fx31337_ticks_to_m1.py je Jahr erzeugt)
A = pd.concat([pd.read_csv(f, parse_dates=['ts_utc']) for f in sorted(glob.glob(f'{EXT}/raw/fx31337_dukascopy_xauusd_ticks/derived_M1/*.csv.gz'))])
A = A.set_index('ts_utc').sort_index(); A.to_pickle(f'{EXT}/work/fx31337_xau_m1.pkl'); print('FX31337 M1', len(A), A.index.min(), A.index.max())

# 5) EPSOFT (Dukascopy JForex-Export M5 Bid, 'Local time' = New York mit GMT-Offset)
fs = sorted(glob.glob(f'{EXT}/raw/epsoft_dukascopy_xauusd_m5/5M/*.csv'))
E = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
offh = E['Local time'].str[-5:].astype(int) // 100
E['ts_utc'] = pd.to_datetime(E['Local time'].str[:19], format='%d.%m.%Y %H:%M:%S') - pd.to_timedelta(offh, unit='h')
E = E.drop_duplicates('ts_utc').set_index('ts_utc').sort_index(); E.to_pickle(f'{EXT}/work/epsoft_xau_m5.pkl'); print('EPSOFT', len(E))

# 6) Kalibrierfaktor k für den TICKVOL-Proxy (Dukascopy-Bid-Volumen -> Tickanzahl), Überlappung A/B
a5 = resample_ohlc(A.reset_index(), 'ts_utc', price_cols=('open_bid','high_bid','low_bid','close_bid'), extra_sum=('ticks',))
b5 = resample_ohlc(d, 'ts', price_cols=('open_bid','high_bid','low_bid','close_bid'), extra_sum=('volume_bid',))
k5 = a5[['ticks']].join(b5[['volume_bid']], how='inner')
day = k5.groupby(k5.index.date).agg(t=('ticks','sum'), vb=('volume_bid','sum'))
k = {'k_bid_med': float((day.t / day.vb).median()), 'k_bid_sum': float(k5.ticks.sum() / k5.volume_bid.sum()),
     'corr_m5': float(k5.ticks.corr(k5.volume_bid * 1.0)), 'n_m5': int(len(k5))}
pd.to_pickle(k, f'{EXT}/work/gold_k.pkl'); print('k', k)
