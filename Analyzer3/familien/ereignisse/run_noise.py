"""Effekt 5: noise-1.0 (Referenz-Rekonstruktion) getrennt nach Ereignistagen und Nicht-Ereignistagen.
Kein neues Setup, nur ein moeglicher Tagesfilter. Ereignistag = geplantes FOMC-Statement, CPI- oder NFP-Termin (NY-Datum).

Aufruf: python3 -W ignore run_noise.py train|val
"""
import os
import sys

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import ev  # noqa: E402
import qdata as Q  # noqa: E402
import qbt  # noqa: E402
import ledger  # noqa: E402
import noise  # noqa: E402

FAM = 'ereignisse'


def main(phase, insts=('NAS100', 'US500')):
    rows = []
    sets = {'fomc': ev.event_days('fomc'), 'cpinfp': ev.event_days('cpinfp'), 'any': ev.event_days('any')}
    for inst in insts:
        end = '2024-01-01' if phase == 'train' else '2025-01-01'
        df = Q.load(inst, None, end, warmup_days=0)
        x = noise.prepare(df, inst)
        sig = noise.noise10_signals(x)
        res = qbt.simulate(x, sig, inst)
        tr = qbt.trades_only(res)
        day = Q.server_to_ny(pd.DatetimeIndex(tr['t_entry'])).normalize()
        per = {'Train': (str(Q.dev_start(inst).date()), '2024-01-01')} if phase == 'train' else \
              {'Val 2024': ('2024-01-01', '2025-01-01')}
        subsets = {'alle': np.ones(len(tr), bool),
                   'ereignis': day.isin(sets['any']), 'kein_ereignis': ~day.isin(sets['any']),
                   'fomc': day.isin(sets['fomc']), 'cpinfp': day.isin(sets['cpinfp'])}
        for sn, m in subsets.items():
            cell = qbt.report_cell(x, tr[np.asarray(m)], per)
            name = f'N10_{sn}|{inst}|1R'
            ledger.log_variant(FAM, name, dict(rule='noise10', subset=sn, inst=inst, src='noise-1.0 Rekonstruktion; Filter Ereignistag'),
                               cell, note='v2')
            for p, r in cell.iterrows():
                rows.append(dict(variante=name, periode=p, trefferquote=r['tvs'], art_trefferquote='Target vor Stop',
                                 R=r['R'], R_pro_tag=r['R'] * r['per_day'], n=r['n'], per_day=r['per_day'], win=r['win'],
                                 tvs=r['tvs'], t=r['t'], t_day=r['t_day'], null_tvs=r['null_tvs'], null_win=r['null_win'],
                                 null_R=r['null_R'], t_vs_null=r.get('t_vs_null', np.nan),
                                 R_gross=r.get('R_gross', np.nan), time_exit=r['time_exit']))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(HIER, f'noise_{phase}.csv'), index=False)
    return out


if __name__ == '__main__':
    out = main(sys.argv[1])
    cols = ['variante', 'periode', 'n', 'per_day', 'tvs', 'win', 'R', 't', 't_day', 'null_tvs', 'null_R', 't_vs_null']
    pd.set_option('display.width', 250)
    print(out[cols].round(3).to_string(index=False))
