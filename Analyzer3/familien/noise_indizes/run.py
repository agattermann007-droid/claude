"""Familie 'noise_indizes': Zellen je Instrument x Regel und Portfolios (alle / S1), mit Nullmodell und Ledger.

Aufruf: python3 -W ignore run.py train      (Train = dev-Start .. 2023-12-31, legt die Auswahl S1 fest)
        python3 -W ignore run.py val        (Val 2024, einmal; nutzt die Auswahl aus auswahl_train.json)
        python3 -W ignore run.py info25     (2025, nur Information, entscheidet nichts)
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import ni_sitzung as S  # noqa: E402
import ni_regeln as RG  # noqa: E402
import qbt  # noqa: E402
import qdata as Q  # noqa: E402
import ledger  # noqa: E402

FAMILIE = 'noise_indizes'
COLS = ['n', 'per_day', 'days_cov', 'tvs', 'win', 'R', 't', 't_day', 'time_exit', 'null_tvs', 'null_win', 'null_R', 't_vs_null']


def periods(inst, phase):
    if phase == 'train':
        return {'Train': (str(Q.dev_start(inst).date()), '2024-01-01')}
    if phase == 'info25':
        return {'info 2025': ('2025-01-01', '2026-01-01')}
    return {'Val 2024': ('2024-01-01', '2025-01-01')}


def tp1_vs_stop(x, tr, inst):
    """Teilziel vor Stop: dieselben Trades mit Ziel = tp1_R auf die ganze Position (gleicher Stop, gleiches Ende)."""
    if len(tr) == 0 or 'tp1_R' not in tr.columns:
        return np.nan
    comp = tr[['i_sig', 'd', 'stop', 'i_last', 'kind']].copy()
    comp['tgt_R'] = tr['tp1_R'].to_numpy()
    r = qbt.simulate(x, comp, inst, seq=False)
    h, s = (r['code'] == 1).sum(), (r['code'] == -1).sum()
    return h / max(h + s, 1)


def portfolio(trs, days, null_cells):
    """trs: Trades aller Instrumente (Spalte inst). days: Index der Portfolio-Handelstage (Serverdatum).
    null_cells: dict inst -> (n, null_R, null_tvs, null_win)."""
    nd = len(days)
    if len(trs) == 0:
        return dict(n=0, per_day=0.0, days_cov=0.0)
    R = trs['R'].to_numpy()
    n = len(R)
    hit, stp = (trs['code'] == 1).sum(), (trs['code'] == -1).sum()
    day = pd.DatetimeIndex(trs['t_entry']).normalize()
    dsum = pd.Series(R, index=day).groupby(level=0).sum()
    sd = R.std(ddof=1)
    nn = sum(v[0] for v in null_cells.values())
    nR = sum(v[0] * v[1] for v in null_cells.values()) / nn
    ntvs = sum(v[0] * v[2] for v in null_cells.values() if not np.isnan(v[2])) / nn
    nwin = sum(v[0] * v[3] for v in null_cells.values()) / nn
    return dict(n=n, per_day=n / nd, days_cov=len(dsum) / nd, tvs=hit / max(hit + stp, 1), win=(R > 0).mean(), R=R.mean(),
                t=R.mean() / (sd / np.sqrt(n)), t_day=dsum.mean() / (dsum.std(ddof=1) / np.sqrt(len(dsum))),
                R_day=R.sum() / nd, time_exit=(trs['code'] == 0).mean(), null_tvs=ntvs, null_win=nwin, null_R=nR,
                t_vs_null=(R.mean() - nR) / (sd / np.sqrt(n)), cost_R=(trs['R_gross'] - trs['R']).mean(),
                n_inst=trs['inst'].nunique())


K_NULL = 100   # Nullmodell der berichteten Zellen (Hinweis Koordinator: K 20 ist um etwa 0,014 R verrauscht)
NOTE = 'v2: N10_480 nach Uhrzeit (noise.last_by_clock), Null K=100'


def main(phase, K=K_NULL):
    end = {'train': '2024-01-01', 'val': '2025-01-01', 'info25': '2026-01-01'}[phase]
    pname = {'train': 'Train', 'val': 'Val 2024', 'info25': 'info 2025'}[phase]
    cells, trades, sessdays = [], [], {}
    sigdays = {r: {} for r in RG.RULES}
    for inst in S.INSTRUMENTS:
        df = Q.load(inst, Q.dev_start(inst), end)
        x = S.prepare(df, inst)
        a, b = periods(inst, phase)[pname]
        ins = x.index[x['in_sess'] & (x.index >= a) & (x.index < b)]
        sessdays[inst] = pd.DatetimeIndex(ins.normalize().unique())
        for rule in RG.RULES:
            sig = RG.make_signals(x, rule)
            st = x.index[sig['i_sig'].to_numpy()]
            sigdays[rule][inst] = pd.DatetimeIndex(st[(st >= a) & (st < b)].normalize().unique())
            tr = qbt.trades_only(qbt.simulate(x, sig, inst))
            tr = tr[(tr['t_entry'] >= a) & (tr['t_entry'] < b)].copy()
            cell = qbt.report_cell(x, tr, periods(inst, phase), K=K)
            r = cell.iloc[0].to_dict()
            if phase == 'train':   # Auswahl S1 vorab mit Nullmodell K 20, seed 7 festgelegt (REGELN.md)
                r['null_R_k20'] = qbt.report_cell(x, tr, periods(inst, phase), K=20, seed=7).iloc[0]['null_R'] if len(tr) else np.nan
            r.update(inst=inst, rule=rule, period=pname, cost_R=(tr['R_gross'] - tr['R']).mean() if len(tr) else np.nan,
                     risk_pct=tr['risk_pct'].median() if len(tr) else np.nan,
                     tp1vs=tp1_vs_stop(x, tr, inst) if rule == 'B' else np.nan)
            r['R_day'] = r['R'] * r['per_day'] if r['n'] else 0.0
            cells.append(r)
            ledger.log_variant(FAMILIE, f'{rule}|{inst}', dict(rule=rule, inst=inst, entry='noise-1.0 E0', sess=list(map(str, S.SESS[inst]))),
                               cell, note=f'{phase}; Zelle Instrument x Regel; {NOTE}')
            tr['rule'] = rule
            trades.append(tr[['inst', 'rule', 'i_sig', 't_sig', 't_entry', 't_exit', 'd', 'E', 'stop', 'X', 'risk_pct', 'R_gross', 'R', 'code']])
            print(f'{phase} {inst:7s} {rule:8s} n {int(r["n"]):4d} /Tag {r["per_day"]:.2f} TvS {r["tvs"]:.2f} R {r["R"]:+.3f} '
                  f't {r["t"]:.2f} Null {r["null_R"]:+.3f} Kosten {r["cost_R"]:.3f}R', flush=True)
    C = pd.DataFrame(cells)
    T = pd.concat(trades, ignore_index=True)
    C.to_csv(os.path.join(HIER, f'zellen_{phase}.csv'), index=False)
    T.to_csv(os.path.join(HIER, f'trades_{phase}.csv'), index=False)

    # Auswahl S1 (nur auf Train festgelegt)
    fsel = os.path.join(HIER, 'auswahl_train.json')
    if phase == 'train':
        sel = {rule: [i for i in S.INSTRUMENTS
                      if ((C.rule == rule) & (C.inst == i) & (C.R > 0) & (C.R > C.null_R_k20)).any()] for rule in RG.RULES}
        alt = {rule: [i for i in S.INSTRUMENTS
                      if ((C.rule == rule) & (C.inst == i) & (C.R > 0) & (C.R > C.null_R)).any()] for rule in RG.RULES}
        print('Auswahl S1 (Null K20, vorab):', sel)
        print('zum Vergleich mit Null K' + str(K) + ':', alt, '-> gleich' if alt == sel else '-> ABWEICHEND')
        json.dump(sel, open(fsel, 'w'), indent=1)
    sel = json.load(open(fsel))
    alldays = pd.DatetimeIndex(sorted(set().union(*[set(v) for v in sessdays.values()])))
    alldays = alldays[alldays.dayofweek < 5]
    prow = []
    for rule in RG.RULES:
        for sname, insts in [('alle', S.INSTRUMENTS), ('S1', sel[rule])]:
            sub = T[(T.rule == rule) & T.inst.isin(insts)]
            cc = C[(C.rule == rule) & C.inst.isin(insts) & (C.n > 0)]
            nulls = {r.inst: (r.n, r.null_R, r.null_tvs, r.null_win) for r in cc.itertuples()}
            p = portfolio(sub, alldays, nulls) if len(sub) else dict(n=0)
            sd = set().union(*[set(sigdays[rule][i]) for i in insts]) if insts else set()
            p.update(rule=rule, auswahl=sname, period=pname, insts=','.join(insts), n_days=len(alldays),
                     sig_days_cov=len(set(sd) & set(alldays)) / len(alldays))
            prow.append(p)
            tab = pd.DataFrame([p], index=[pname])
            ledger.log_variant(FAMILIE, f'PF_{rule}_{sname}', dict(rule=rule, auswahl=sname, insts=insts), tab,
                               note=f'{phase}; Portfolio, Tag = Serverdatum; {NOTE}')
    P = pd.DataFrame(prow)
    P.to_csv(os.path.join(HIER, f'portfolio_{phase}.csv'), index=False)
    pd.set_option('display.width', 250)
    show = ['rule', 'auswahl', 'n_inst', 'n', 'per_day', 'days_cov', 'sig_days_cov', 'tvs', 'win', 'R', 't', 't_day', 'R_day',
            'null_R', 't_vs_null', 'cost_R']
    print(P[[c for c in show if c in P.columns]].round(3).to_string(index=False))
    print(json.dumps(sel))


if __name__ == '__main__':
    main(sys.argv[1])
