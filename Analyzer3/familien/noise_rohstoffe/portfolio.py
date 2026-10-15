"""Portfolio-Kennzahlen je Regel: P_alle (10 Instrumente, ohne Auswahl) und P_sel (Auswahl nur nach Train:
R netto > 0 und R > Null-R). Aufruf: python3 portfolio.py train|val"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nr  # noqa: E402
import qdata as Q  # noqa: E402
import qbt  # noqa: E402
import ledger  # noqa: E402
from run import PER, FAMILIE  # noqa: E402

OUT = os.path.join(HERE, 'out')
KLASSEN = {'Metalle': ['XAUUSD', 'XAGUSD'], 'Oel': ['WTI', 'BRENT'], 'BTC': ['BTCUSD'],
           'FX': ['EURUSD', 'GBPUSD', 'AUDUSD', 'USDCAD', 'USDCHF']}


def trading_days(per_key, insts):
    pname, a, b = PER[per_key]
    days = set()
    for inst in insts:
        df = Q.load(inst, a, b, warmup_days=0)
        ny = Q.server_to_ny(df.index).normalize()
        days |= set(ny[ny.dayofweek < 5])
    return len(days)


def agg(tr, cells, n_days, art):
    n = len(tr)
    if n == 0:
        return dict(n=0, per_day=0.0, days_cov=0.0, hit=np.nan, R=np.nan, R_day=0.0, t=np.nan, t_day=np.nan,
                    null_R=np.nan, t_vs_null=np.nan, cost_R=np.nan)
    R = tr['R'].to_numpy()
    sd = R.std(ddof=1)
    day = Q.server_to_ny(pd.DatetimeIndex(tr['t_entry'])).normalize()
    ds = pd.Series(R, index=day).groupby(level=0).sum()
    if art == 'Target vor Stop':
        h, s = (tr['code'] == 1).sum(), (tr['code'] == -1).sum()
        hit = h / max(h + s, 1)
    elif art == 'Gewinnquote':
        hit = (R > 0).mean()
    else:   # Teilziel vor Stop: n-gewichtetes Mittel der Zellen
        hit = np.average(cells['tvs'], weights=cells['n'])
    null_R = np.average(cells['null_R'], weights=cells['n'])
    return dict(n=n, per_day=n / n_days, days_cov=len(ds) / n_days, hit=hit, R=R.mean(), R_day=R.sum() / n_days,
                t=R.mean() / (sd / np.sqrt(n)), t_day=ds.mean() / (ds.std(ddof=1) / np.sqrt(len(ds))),
                null_R=null_R, t_vs_null=(R.mean() - null_R) / (sd / np.sqrt(n)),
                cost_R=(tr['R_gross'] - tr['R']).mean(), R_gross=tr['R_gross'].mean())


def main(per_key, log=True):
    pname = PER[per_key][0]
    cells = pd.concat([pd.read_csv(os.path.join(OUT, f'zellen_{per_key}_{i}.csv')) for i in nr.INSTS + nr.CHECK])
    trades = pd.concat([pd.read_parquet(os.path.join(OUT, f'trades_{per_key}_{i}.parquet')) for i in nr.INSTS])
    n_days = trading_days(per_key, nr.INSTS)
    sel_file = os.path.join(HERE, 'auswahl_train.json')
    if per_key == 'train':
        sel = {}
        for rule, g in cells[cells['inst'].isin(nr.INSTS)].groupby('rule'):
            sel[rule] = sorted(g.loc[(g['R'] > 0) & (g['R'] > g['null_R']), 'inst'].tolist())
    else:
        sel = json.load(open(sel_file))['P_sel']
    rows = []
    for rule, (fn, art) in nr.RULES.items():
        sets = {'P_alle': nr.INSTS, 'P_sel': sel.get(rule, []), **{f'K_{k}': v for k, v in KLASSEN.items()}}
        for pn, insts in sets.items():
            tr = trades[(trades['rule'] == rule) & trades['inst'].isin(insts)]
            c = cells[(cells['rule'] == rule) & cells['inst'].isin(insts) & (cells['n'] > 0)]
            r = agg(tr, c, n_days, art)
            r.update(rule=rule, portfolio=pn, period=pname, art=art, insts=','.join(insts))
            rows.append(r)
            if log:
                tab = pd.DataFrame([{k: r.get(k) for k in ['n', 'per_day', 'R', 't', 'null_R', 't_vs_null']}
                                    | {'tvs': r['hit'], 'win': np.nan, 'null_tvs': np.nan}], index=[pname])
                ledger.log_variant(FAMILIE, f'{rule}|{pn}', {'rule': rule, 'portfolio': pn, 'insts': insts}, tab,
                                   note=f'Portfolio{" (Klasse, nur beschreibend)" if pn.startswith("K_") else ""}; Trefferquote={art}; t_day={r["t_day"]:.2f}; days_cov={r["days_cov"]:.3f}')
    port = pd.DataFrame(rows)
    port.to_csv(os.path.join(OUT, f'portfolio_{per_key}.csv'), index=False)
    return port, sel, n_days


if __name__ == '__main__':
    per_key = sys.argv[1]
    port, sel, nd = main(per_key)
    pd.set_option('display.width', 250)
    print('Handelstage', nd)
    print(port[['rule', 'portfolio', 'n', 'per_day', 'days_cov', 'hit', 'R', 'R_gross', 'cost_R', 't', 't_day',
                'null_R', 't_vs_null', 'R_day']].round(3).to_string())
    if per_key == 'train':
        print(json.dumps(sel, indent=1))
