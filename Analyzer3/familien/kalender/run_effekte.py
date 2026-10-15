"""Familie 'kalender': Literaturregeln als Daytrades, Train (Phase 1) bzw. Val 2024 (Phase 2).

Aufruf:  python3 -W ignore run_effekte.py train      -> nur Train, Ledger-Zeilen 'Train'
         python3 -W ignore run_effekte.py val        -> nur Val 2024 (einmal), Ledger-Zeilen 'Val 2024'
Geometrie: Stop = 1 x sigma_F (RMS der Fensterrendite, 20 Tage), Ziele 0,5 / 1 / 2 R / kein Ziel (Zeitausstieg).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import kal  # noqa: E402
import qdata as Q  # noqa: E402
import qbt  # noqa: E402
import ledger  # noqa: E402

FAM = 'kalender'
TARGETS = [0.5, 1.0, 2.0, np.nan]
RULESET = os.environ.get('KAL_RULES', 'stufe1')
INSTS = ['NAS100', 'US500']


def tname(t):
    return 'none' if np.isnan(t) else f'{t:g}R'


def rules(x):
    """Literaturregeln -> (Tagesmaske, Fensterstart, Fensterende, Quelle)."""
    cal = x.attrs['cal']
    ref = kal.ref_close(x)
    prev_ret = ref.shift(1) / ref.shift(2) - 1          # Vortag (15:00 -> 15:00 NY), bekannt vor 2:00 ET
    alle = pd.Series(True, index=cal.index)
    if RULESET == 'stufe2':
        return {
            'ONbig': (prev_ret <= -0.01, 120, 180, 'BLW 2023: Umkehr nach Ausverkauf; Vortag <= -1 %'),
            'TOM+PREH': (cal['tom'] | cal['preh'], 570, 900, 'Lakonishok/Smidt 1988: Monatswechsel und Vor-Feiertag gebuendelt'),
        }
    if RULESET == 'stufe3':
        hw = pd.Series(np.isin(cal.index.month, [11, 12, 1, 2, 3, 4]), index=cal.index)
        return {
            'TOM+PREH_hw': ((cal['tom'] | cal['preh']) & hw, 570, 900,
                            'wie TOM+PREH, nur Nov-Apr (Halloween-Filter, Bouman/Jacobsen 2002)'),
        }
    return {
        'ON': (alle, 120, 180, 'Boyarchenko/Larsen/Whelan 2023 RFS: Long 2:00-3:00 ET (Europa-Eroeffnung)'),
        'ONneg': (prev_ret < 0, 120, 180, 'BLW 2023: Drift staerker nach Ausverkauf; nur nach negativem Vortag'),
        'TOM': (cal['tom'], 570, 900, 'Ariel 1987, Lakonishok/Smidt 1988, McConnell/Xu 2008: Tag -1..+3, intraday'),
        'PREH': (cal['preh'], 570, 900, 'Ariel 1990, Lakonishok/Smidt 1988: Vor-Feiertag, intraday'),
        'OPEXW': (cal['opex_week'], 570, 900, 'Stivers/Sun 2010/2013: OE-Woche (3. Freitag) hoch, intraday Mo..Verfall'),
    }


def main(phase):
    rows = []
    for inst in INSTS:
        df = Q.load(inst, None, '2025-01-01', warmup_days=0)
        x = kal.prep(df)
        per = {'Train': (str(Q.dev_start(inst).date()), '2024-01-01')} if phase == 'train' else \
              {'Val 2024': ('2024-01-01', '2025-01-01')}
        for rn, (mask, a, b, src) in rules(x).items():
            for tg in TARGETS:
                sig = kal.build(x, mask, a, b, k=1.0, tgt_R=tg)
                res = qbt.simulate(x, sig, inst)
                tr = qbt.trades_only(res)
                cell = qbt.report_cell(x, tr, per)
                name = f'{rn}|{inst}|{tname(tg)}'
                params = dict(rule=rn, inst=inst, win=f'{a // 60}:{a % 60:02d}-{b // 60}:{b % 60:02d} NY', stop='1*sigmaF20',
                              tgt_R=None if np.isnan(tg) else tg, src=src)
                ledger.log_variant(FAM, name, params, cell, note='v2')
                for p, r in cell.iterrows():
                    art = 'Gewinnquote' if np.isnan(tg) else 'Target vor Stop'
                    rows.append(dict(variante=name, periode=p, trefferquote=(r['win'] if np.isnan(tg) else r['tvs']),
                                     art_trefferquote=art, R=r['R'], R_pro_tag=r['R'] * r['per_day'], n=r['n'],
                                     per_day=r['per_day'], win=r['win'], tvs=r['tvs'], t=r['t'], t_day=r['t_day'],
                                     null_tvs=r['null_tvs'], null_win=r['null_win'], null_R=r['null_R'],
                                     t_vs_null=r.get('t_vs_null', np.nan), R_gross=r.get('R_gross', np.nan)))
                print(name, {k: round(float(v), 3) for k, v in rows[-1].items() if k not in ('variante', 'periode', 'art_trefferquote')}, flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(HIER, f'zellen_{phase}_{RULESET}.csv'), index=False)


if __name__ == '__main__':
    main(sys.argv[1])
