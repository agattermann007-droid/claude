"""Baut die kanonischen M5-Dateien aus den bereits vorhandenen Quellen (ts4blader MT5-Export, OANDA, HistData, Bitstamp).
Weitere Quellen ergaenzt build_extra.py."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qdata as Q

T20 = '2020-01-01'
jobs = {
    'NAS100': lambda: [('oanda', Q.src_oanda('NAS100_USD'), None, '2021-01-01'), ('ts4', Q.src_ts4('US100'), '2021-01-01', None)],
    'US500':  lambda: [('oanda', Q.src_oanda('SPX500_USD'), None, T20), ('ts4', Q.src_ts4('US500'), T20, None)],
    'XAUUSD': lambda: [('oanda', Q.src_oanda('XAU_USD'), None, T20), ('ts4', Q.src_ts4('XAUUSD'), T20, None)],
    'EURUSD': lambda: [('oanda', Q.src_oanda('EUR_USD'), None, T20), ('ts4', Q.src_ts4('EURUSD'), T20, None)],
    'GBPUSD': lambda: [('oanda', Q.src_oanda('GBP_USD'), None, T20), ('ts4', Q.src_ts4('GBPUSD'), T20, None)],
    'AUDUSD': lambda: [('oanda', Q.src_oanda('AUD_USD'), None, T20), ('ts4', Q.src_ts4('AUDUSD'), T20, None)],
    'USDCAD': lambda: [('oanda', Q.src_oanda('USD_CAD'), None, T20), ('ts4', Q.src_ts4('USDCAD'), T20, None)],
    'USDCHF': lambda: [('ts4', Q.src_ts4('USDCHF'), T20, None)],
    'JPN225': lambda: [('oanda', Q.src_oanda('JP225_USD'), None, None)],
    'UK100':  lambda: [('oanda', Q.src_oanda('UK100_GBP'), None, None)],
    'FRA40':  lambda: [('oanda', Q.src_oanda('FR40_EUR'), None, None)],
    'AUS200': lambda: [('oanda', Q.src_oanda('AU200_AUD'), None, None)],
    'US2000': lambda: [('oanda', Q.src_oanda('US2000_USD'), None, None)],
    'WTI':    lambda: [('oanda', Q.src_oanda('WTICO_USD'), None, None)],
    'ESTX50': lambda: [('histdata', Q.src_histdata_fs('ETXEUR'), None, None)],
    'GER40':  lambda: [('histdata', Q.src_histdata_fs('GRXEUR'), None, None)],
    'BTCUSD': lambda: [('bitstamp', Q.src_bitstamp_btc(), None, None)],
}
want = sys.argv[1:] or list(jobs)
for k in want:
    df = Q.build(k, jobs[k]())
    print(k, len(df), df.index[0], df.index[-1], dict(df.src.value_counts()), flush=True)
