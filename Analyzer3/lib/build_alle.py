"""Baut alle kanonischen M5-Dateien (Serverzeit NY+7). Quellenplan:
  dev 2020-2024 und info 2025: ts4 (MT5-Broker, Uhr korrigiert) fuer NAS100/US500/XAU/FX, sonst Pedram.
  gesperrt vor dev_start: OANDA (2005-) bzw. Pedram 2015-2019; gesperrt 2026: Pedram (bis 07.10.2026, Oel bis 01.10.)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import qdata as Q

T15, T20, T21, T26 = '2015-01-01', '2020-01-01', '2021-01-01', '2026-01-01'
DEFEKT = ('2023-02-01', '2023-08-01')     # HistData-Loecher bei XAG/USOIL/UKOIL (jede 2. Stunde fehlt)


def ohne_defekt(df):
    return df[(df.index < DEFEKT[0]) | (df.index >= DEFEKT[1])]


jobs = {
    'NAS100': lambda: [('oanda', Q.src_oanda('NAS100_USD'), None, T21), ('ts4', Q.src_ts4('US100'), T21, T26), ('q', Q.src_q('NAS100', '2025-12-01'), T26, None)],
    'US500':  lambda: [('oanda', Q.src_oanda('SPX500_USD'), None, T20), ('ts4', Q.src_ts4('US500'), T20, T26), ('q', Q.src_q('SPX500', '2025-12-01'), T26, None)],
    'XAUUSD': lambda: [('oanda', Q.src_oanda('XAU_USD'), None, T20), ('q', Q.src_q('XAUUSD', '2021-04-19', '2021-05-22'), '2021-04-20', '2021-05-21'),
                       ('ts4', Q.src_ts4('XAUUSD'), T20, T26), ('q', Q.src_q('XAUUSD', '2025-12-01'), T26, None)],
    'US30':   lambda: [('q', Q.src_q('US30'), None, None)],
    'US2000': lambda: [('oanda', Q.src_oanda('US2000_USD'), None, T15), ('q', Q.src_q('US2000'), T15, None)],
    'GER40':  lambda: [('histdata', Q.src_histdata_fs('GRXEUR'), None, T15), ('q', Q.src_q('GER40'), T15, None)],
    'FRA40':  lambda: [('oanda', Q.src_oanda('FR40_EUR'), None, T15), ('q', Q.src_q('FRA40'), T15, None)],
    'ESTX50': lambda: [('histdata', Q.src_histdata_fs('ETXEUR'), None, T15), ('q', Q.src_q('EU50'), T15, None)],
    'UK100':  lambda: [('oanda', Q.src_oanda('UK100_GBP'), None, T15), ('q', Q.src_q('UK100'), T15, None)],
    'JPN225': lambda: [('oanda', Q.src_oanda('JP225_USD'), None, T15), ('q', Q.src_q('JPN225'), T15, None)],
    'AUS200': lambda: [('oanda', Q.src_oanda('AU200_AUD'), None, T15), ('q', Q.src_q('AUS200'), T15, None)],
    'HK50':   lambda: [('q', Q.src_q('HK50'), None, None)],
    'XAGUSD': lambda: [('q', ohne_defekt(Q.src_q('XAGUSD')), None, None)],
    'WTI':    lambda: [('oanda', Q.src_oanda('WTICO_USD'), None, T15), ('q', ohne_defekt(Q.src_q('USOIL')), T15, None)],
    'BRENT':  lambda: [('q', ohne_defekt(Q.src_q('UKOIL')), None, None)],
    'BTCUSD': lambda: [('bitstamp', Q.src_bitstamp_btc(), None, '2017-08-18'), ('q', Q.src_q('BTCUSD'), '2017-08-18', None)],
    'ETHUSD': lambda: [('q', Q.src_q('ETHUSD'), None, None)],
    **{fx: (lambda fx=fx, oa=oa: ([('oanda', Q.src_oanda(oa), None, T20)] if oa else []) +
            [('ts4', Q.src_ts4(fx), T20, T26), ('q', Q.src_q(fx, '2025-12-01'), T26, None)])
       for fx, oa in [('EURUSD', 'EUR_USD'), ('GBPUSD', 'GBP_USD'), ('AUDUSD', 'AUD_USD'), ('USDCAD', 'USD_CAD'), ('USDCHF', None)]},
}

if __name__ == '__main__':
    want = sys.argv[1:] or list(jobs)
    for k in want:
        df = Q.build(k, jobs[k]())
        yrs = df.groupby(df.index.year).size()
        print(f'{k:7s} {len(df):8d} {df.index[0]} .. {df.index[-1]} Quellen {dict(df.src.value_counts())}', flush=True)
