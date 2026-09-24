"""Prüft, ob OANDA-Zeitstempel UTC sind: wöchentlicher Offset-Scan OANDA XAU_USD vs. Dukascopy (FX31337, UTC)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
A = pd.read_pickle(f'{EXT}/work/fx31337_xau_m1.pkl').reset_index()
ref = resample_ohlc(A, 'ts_utc', price_cols=('open_bid','high_bid','low_bid','close_bid'))['close_bid']
O = pd.read_pickle(f'{EXT}/work/oanda_xau_m1.pkl')
o5 = resample_ohlc(O, 'ts')['close']
res = weekly_offset_scan(o5, ref, [-2, -1, 0, 1, 2], min_pairs=150)
print(res.best.value_counts().to_dict()); print(res['corr'].describe().round(4).to_dict())
print(res[res.best != 0].to_string())
j = o5.to_frame('o').join(ref.rename('d'), how='inner')
print('Preisdifferenz OANDA(mid)-Dukascopy(bid) je Jahr (Median):', (j.o - j.d).groupby(j.index.year).median().round(3).to_dict())
res.to_csv(f'{EXT}/work/offset_oanda_xau_vs_dukascopy.csv')
