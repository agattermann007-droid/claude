"""Lauf je Zelle (Instrument x Regel). Aufruf: python3 run.py train|val [inst ...]
Train: dev-Start bis 2023-12-31. val: 2024 (einmal, nach auswahl_train.json)."""
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nr  # noqa: E402
import qdata as Q  # noqa: E402
import qbt  # noqa: E402
import ledger  # noqa: E402

FAMILIE = 'noise_rohstoffe'
PER = {'train': ('Train', '2020-01-01', '2024-01-01'), 'val': ('Val 2024', '2024-01-01', '2025-01-01'),
       'info25': ('Info 2025', '2025-01-01', '2026-01-01')}


def tp1_hit_rate(x, tr, inst):
    """Teilziel vor Stop: dieselben Trades nochmals mit Ziel = Teilziel (0,5R), ohne Teilziel, gleicher Stop."""
    s = tr[['i_sig', 'd', 'stop', 'i_last', 'kind']].copy()
    s['tgt_R'] = 0.5
    r = qbt.trades_only(qbt.simulate(x, s, inst, seq=False))
    h, st = (r['code'] == 1).sum(), (r['code'] == -1).sum()
    return h / max(h + st, 1)


def run_inst(inst, per_key, rules=None):
    pname, a, b = PER[per_key]
    end = '2026-01-01' if per_key == 'info25' else '2025-01-01'
    df = Q.load(inst, '2020-01-01', end)
    x = nr.prepare(df, inst)
    rows, trades = [], []
    for rule, (fn, art) in nr.RULES.items():
        if rules and rule not in rules:
            continue
        sig = fn(x)
        res = qbt.simulate(x, sig, inst)
        tr = qbt.trades_only(res)
        tr = tr[(tr['t_entry'] >= pd.Timestamp(a)) & (tr['t_entry'] < pd.Timestamp(b))].copy()
        tab = qbt.report_cell(x, tr, {pname: (a, b)})
        r = tab.iloc[0].to_dict()
        r.update(rule=rule, inst=inst, period=pname, art=art)
        r['cost_R'] = (tr['R_gross'] - tr['R']).mean() if len(tr) else np.nan
        r['cost_R_med'] = (tr['R_gross'] - tr['R']).median() if len(tr) else np.nan
        r['R_day'] = r['R'] * r['per_day'] if r['n'] > 0 else 0.0
        if art == 'Teilziel vor Stop' and len(tr):
            r['tvs'] = tp1_hit_rate(x, tr, inst)
        if art == 'Gewinnquote':
            r['hit'] = r['win']
        else:
            r['hit'] = r['tvs']
        rows.append(r)
        tab2 = tab.copy()
        tab2['tvs'] = r['tvs']
        ledger.log_variant(FAMILIE, f'{rule}|{inst}', {'rule': rule, 'inst': inst, 'sess': nr.SESS[inst]}, tab2,
                           note=f'Trefferquote={art}; cost_R={r["cost_R"]:.3f}')
        tr['rule'] = rule
        tr['null_R_cell'] = r.get('null_R', np.nan)
        trades.append(tr)
    return pd.DataFrame(rows), pd.concat(trades) if trades else pd.DataFrame()


if __name__ == '__main__':
    per_key = sys.argv[1]
    insts = sys.argv[2:] or (nr.INSTS + nr.CHECK)
    outdir = os.path.join(HERE, 'out')
    os.makedirs(outdir, exist_ok=True)
    for inst in insts:
        t0 = time.time()
        cells, tr = run_inst(inst, per_key)
        cells.to_csv(os.path.join(outdir, f'zellen_{per_key}_{inst}.csv'), index=False)
        keep = ['rule', 'inst', 'i_sig', 'd', 'stop', 'E', 'X', 'R_gross', 'R', 'code', 't_entry', 't_exit', 'risk_pct',
                'null_R_cell', 'tgt_R']
        tr[[k for k in keep if k in tr.columns]].to_parquet(os.path.join(outdir, f'trades_{per_key}_{inst}.parquet'))
        print(f'{inst} fertig {time.time() - t0:.0f}s', flush=True)
