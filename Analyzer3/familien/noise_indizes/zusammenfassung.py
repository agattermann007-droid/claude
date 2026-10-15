"""Tabellen fuer den Bericht aus zellen_*.csv / portfolio_*.csv; Teilziel-vor-Stop (TP1vS) fuer Regel B exakt nachgerechnet.
Aufruf: python3 -W ignore zusammenfassung.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(HIER, '..', '..', 'lib'))
import ni_sitzung as S  # noqa: E402
import ni_regeln as RG  # noqa: E402
import qbt  # noqa: E402
import qdata as Q  # noqa: E402

PH = {'train': ('Train', '2024-01-01'), 'val': ('Val 2024', '2025-01-01'), 'info25': ('info 2025', '2026-01-01')}


def tp1_counts():
    """(phase, inst) -> (TP1-Treffer, Stops) fuer Regel B."""
    out = {}
    for ph, (pn, end) in PH.items():
        for inst in S.INSTRUMENTS:
            df = Q.load(inst, Q.dev_start(inst), end)
            x = S.prepare(df, inst)
            a = {'train': Q.dev_start(inst), 'val': pd.Timestamp('2024-01-01'), 'info25': pd.Timestamp('2025-01-01')}[ph]
            tr = qbt.trades_only(qbt.simulate(x, RG.make_signals(x, 'B'), inst))
            tr = tr[(tr['t_entry'] >= a) & (tr['t_entry'] < pd.Timestamp(end))]
            comp = tr[['i_sig', 'd', 'stop', 'i_last', 'kind']].copy()
            comp['tgt_R'] = 0.5
            r = qbt.simulate(x, comp, inst, seq=False)
            out[(ph, inst)] = (int((r['code'] == 1).sum()), int((r['code'] == -1).sum()))
    return out


def f(v, p=3, pct=False, sign=False):
    if pd.isna(v):
        return '–'
    if pct:
        return f'{100 * v:.0f} %'
    return f'{v:+.{p}f}' if sign else f'{v:.{p}f}'


def main():
    tp = tp1_counts()
    json.dump({f'{k[0]}|{k[1]}': v for k, v in tp.items()}, open(os.path.join(HIER, 'tp1_counts.json'), 'w'))
    sel = json.load(open(os.path.join(HIER, 'auswahl_train.json')))
    Z = {ph: pd.read_csv(os.path.join(HIER, f'zellen_{ph}.csv')) for ph in PH}
    P = {ph: pd.read_csv(os.path.join(HIER, f'portfolio_{ph}.csv')) for ph in PH}

    def hit(ph, inst, rule, r):
        if rule == 'B':
            h, s = tp[(ph, inst)]
            return h / max(h + s, 1)
        return r['tvs']

    print('### Zellen je Instrument x Regel')
    print('| Instrument | Regel | Train n | /Tag | Treffer | Gew. | R netto | t | Null Treffer | Null R | t vs Null | '
          'Val n | /Tag | Treffer | Gew. | R netto | t | Null Treffer | Null R | 2025 n | 2025 R |')
    print('|' + '---|' * 21)
    for inst in S.INSTRUMENTS:
        for rule in RG.RULES:
            rr = {ph: Z[ph][(Z[ph].inst == inst) & (Z[ph].rule == rule)].iloc[0] for ph in PH}
            t, v, i = rr['train'], rr['val'], rr['info25']
            print(f"| {inst} | {rule} | {int(t.n)} | {t.per_day:.2f} | {f(hit('train', inst, rule, t), pct=True)} | {f(t.win, pct=True)} | "
                  f"{f(t.R, sign=True)} | {f(t.t, 2)} | {f(t.null_tvs, pct=True) if rule != 'B' else '–'} | {f(t.null_R, sign=True)} | "
                  f"{f(t.t_vs_null, 2)} | {int(v.n)} | {v.per_day:.2f} | {f(hit('val', inst, rule, v), pct=True)} | {f(v.win, pct=True)} | "
                  f"{f(v.R, sign=True)} | {f(v.t, 2)} | {f(v.null_tvs, pct=True) if rule != 'B' else '–'} | {f(v.null_R, sign=True)} | "
                  f"{int(i.n)} | {f(i.R, sign=True)} |")
    print('\nTreffer = Target vor Stop; bei Regel B Teilziel (0,5R) vor Stop.')

    print('\n### Kosten in R je Trade (Regel N10_EOD) und Brutto-R')
    print('| Instrument | COST | Stop-Abstand (Median, % Kurs) | Kosten R Train | Kosten R 2024 | Brutto R Train N10_EOD | Brutto R 2024 | Brutto R Train A | Brutto R 2024 A |')
    print('|' + '---|' * 9)
    for inst in S.INSTRUMENTS:
        t = Z['train'][(Z['train'].inst == inst) & (Z['train'].rule == 'N10_EOD')].iloc[0]
        v = Z['val'][(Z['val'].inst == inst) & (Z['val'].rule == 'N10_EOD')].iloc[0]
        ta = Z['train'][(Z['train'].inst == inst) & (Z['train'].rule == 'A')].iloc[0]
        va = Z['val'][(Z['val'].inst == inst) & (Z['val'].rule == 'A')].iloc[0]
        print(f'| {inst} | {Q.COST[inst] * 1e4:.1f} bp | {100 * t.risk_pct:.2f} % | {t.cost_R:.3f} | {v.cost_R:.3f} | '
              f'{t.R + t.cost_R:+.3f} | {v.R + v.cost_R:+.3f} | {ta.R + ta.cost_R:+.3f} | {va.R + va.cost_R:+.3f} |')

    print('\n### Portfolios')
    print('| Regel | Auswahl | Zeitraum | Instr. | n | Trades/Tag | Tage mit >=1 Trade | Treffer | Gew. | R netto | t | Tages-t | R/Tag | Null R | t vs Null | Kosten R |')
    print('|' + '---|' * 16)
    for rule in RG.RULES:
        for sname in ['alle', 'S1']:
            insts = S.INSTRUMENTS if sname == 'alle' else sel[rule]
            for ph, (pn, _) in PH.items():
                p = P[ph][(P[ph].rule == rule) & (P[ph].auswahl == sname)].iloc[0]
                if rule == 'B':
                    h = sum(tp[(ph, i)][0] for i in insts)
                    s = sum(tp[(ph, i)][1] for i in insts)
                    hr = h / max(h + s, 1)
                else:
                    hr = p.tvs
                print(f'| {rule} | {sname} | {pn} | {len(insts)} | {int(p.n)} | {p.per_day:.2f} | {f(p.days_cov, pct=True)} | {f(hr, pct=True)} | '
                      f'{f(p.win, pct=True)} | {f(p.R, sign=True)} | {f(p.t, 2)} | {f(p.t_day, 2)} | {f(p.R_day, sign=True)} | '
                      f'{f(p.null_R, sign=True)} | {f(p.t_vs_null, 2)} | {f(p.cost_R)} |')
    print('\nS1-Auswahl je Regel:', json.dumps(sel))


if __name__ == '__main__':
    main()
