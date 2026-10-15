"""Zusatzpruefungen nur auf Train (vor dem Blick auf 2024):
a) Jahre: R je Trade je Jahr fuer Portfolios 'alle' und 'S1' sowie je Instrument (Regel N10_EOD).
b) Auswahlverzerrung: Regel S1 auf Train-Haelfte 1 (bis 2021) anwenden, Portfolio auf Haelfte 2 (2022-23) messen, und umgekehrt.
c) JPN225: Pausenbehandlung von noise.prepare (Pause = Sitzung, Signale 12:00/12:30) gegen sitzung.prepare.
Aufruf: python3 -W ignore extra_train.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(HIER, '..', '..', 'lib'))
import sitzung as S  # noqa: E402
import regeln as RG  # noqa: E402
import qbt  # noqa: E402
import qdata as Q  # noqa: E402
import noise  # noqa: E402
import ledger  # noqa: E402

FAMILIE = 'noise_indizes'


def main():
    pd.set_option('display.width', 250)
    T = pd.read_csv(os.path.join(HIER, 'trades_train.csv'), parse_dates=['t_entry'])
    sel = json.load(open(os.path.join(HIER, 'auswahl_train.json')))
    T['jahr'] = T['t_entry'].dt.year
    # a) Jahre
    rows = []
    for rule in RG.DAYTRADE:
        for sname, insts in [('alle', S.INSTRUMENTS), ('S1', sel[rule])]:
            sub = T[(T.rule == rule) & T.inst.isin(insts)]
            g = sub.groupby('jahr')['R']
            rows.append(pd.Series({f'{y}': f'{m:+.3f} ({n})' for y, m, n in zip(g.mean().index, g.mean(), g.size())},
                                  name=f'{rule} {sname}'))
    for inst in S.INSTRUMENTS:
        sub = T[(T.rule == 'N10_EOD') & (T.inst == inst)]
        g = sub.groupby('jahr')['R']
        rows.append(pd.Series({f'{y}': f'{m:+.3f} ({n})' for y, m, n in zip(g.mean().index, g.mean(), g.size())},
                              name=f'N10_EOD {inst}'))
    print('a) R netto je Trade (n) nach Jahr\n', pd.DataFrame(rows).fillna('').to_string())

    # b) Auswahl auf einer Haelfte, Messung auf der anderen
    H = {'H1': ('2020-01-01', '2022-01-01'), 'H2': ('2022-01-01', '2024-01-01')}
    cells = {}
    for inst in S.INSTRUMENTS:
        df = Q.load(inst, Q.dev_start(inst), '2024-01-01')
        x = S.prepare(df, inst)
        for rule in RG.DAYTRADE:
            tr = T[(T.rule == rule) & (T.inst == inst)]
            per = {h: (max(pd.Timestamp(a), Q.dev_start(inst)), b) for h, (a, b) in H.items()}
            res = qbt.simulate(x, RG.make_signals(x, rule), inst)
            tr = qbt.trades_only(res)
            tr = tr[tr['t_entry'] < pd.Timestamp('2024-01-01')]
            c = qbt.report_cell(x, tr, per)
            for h in H:
                cells[(rule, inst, h)] = c.loc[h]
    out = []
    for rule in RG.DAYTRADE:
        for hs, hm in [('H1', 'H2'), ('H2', 'H1')]:
            pick = [i for i in S.INSTRUMENTS if cells[(rule, i, hs)]['n'] > 0 and cells[(rule, i, hs)]['R'] > 0
                    and cells[(rule, i, hs)]['R'] > cells[(rule, i, hs)]['null_R']]
            a, b = H[hm]
            m = (T.rule == rule) & (T.t_entry >= a) & (T.t_entry < b)
            R_sel = T[m & T.inst.isin(pick)]['R']
            R_all = T[m]['R']
            R_rest = T[m & ~T.inst.isin(pick)]['R']
            r = dict(rule=rule, auswahl_auf=hs, messung_auf=hm, auswahl=','.join(pick),
                     n_sel=len(R_sel), R_sel=R_sel.mean(), t_sel=R_sel.mean() / (R_sel.std() / np.sqrt(len(R_sel))),
                     n_rest=len(R_rest), R_rest=R_rest.mean(), n_alle=len(R_all), R_alle=R_all.mean())
            out.append(r)
            tab = pd.DataFrame([dict(n=r['n_sel'], R=r['R_sel'], t=r['t_sel'])], index=[f'{hm} (Auswahl {hs})'])
            ledger.log_variant(FAMILIE, f'PF_{rule}_S1halb_{hs}', dict(rule=rule, auswahl='S1 auf ' + hs, insts=pick), tab,
                               note='train; Pruefung Auswahlverzerrung (Auswahl auf einer Train-Haelfte, Messung auf der anderen)')
    print('\nb) Auswahl S1 auf einer Train-Haelfte, gemessen auf der anderen\n', pd.DataFrame(out).round(3).to_string(index=False))

    # c) JPN225 Pausenbehandlung
    df = Q.load('JPN225', Q.dev_start('JPN225'), '2024-01-01')
    x0 = noise.prepare(df, 'JPN225')
    sig = noise.signals(x0, grid=30, trend='cprev', one_per_day=True, stop_mode='mid', tgt_R=1.0)
    tr = qbt.trades_only(qbt.simulate(x0, sig, 'JPN225'))
    per = {'Train': (str(Q.dev_start('JPN225').date()), '2024-01-01')}
    c = qbt.report_cell(x0, tr, per)
    ledger.log_variant(FAMILIE, 'N10_EOD|JPN225|noise.prepare', dict(rule='N10_EOD', inst='JPN225', sess='noise.SESS ohne Pause'), c,
                       note='train; Vergleich Pausenbehandlung')
    loc = x0['loc'].iloc[tr['i_sig'].to_numpy()] + pd.Timedelta(minutes=5)
    lunch = ((loc.dt.hour * 60 + loc.dt.minute) > 690) & ((loc.dt.hour * 60 + loc.dt.minute) <= 750)
    print('\nc) JPN225 N10_EOD mit noise.prepare (Pause als Sitzung):',
          c[['n', 'tvs', 'win', 'R', 't', 'null_R']].round(3).to_dict('records'), f'Trades mit Signal in der Pause: {int(lunch.sum())}')


if __name__ == '__main__':
    main()
