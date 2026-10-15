"""Datenpruefung (nur Train-Daten, keine Strategie): Zeitlage der Kassaeroeffnung, Mittagspausen, Luecken.
1) Mittlere |Rendite| je 5-min-Kerze nach Ortszeit: Spitze sollte an der Kassaeroeffnung liegen (prueft UTC->Serverzeit).
2) JPN225/HK50: Kerzen und Bewegung in der Mittagspause.
3) Monate mit wenigen Sitzungskerzen (Datenluecken).
Aufruf: python3 -W ignore qa_daten.py
"""
import os
import sys

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import sitzung as S  # noqa: E402
import qdata as Q  # noqa: E402


def main():
    pd.set_option('display.width', 220)
    for inst in S.INSTRUMENTS:
        df = Q.load(inst, Q.dev_start(inst), '2024-01-01', warmup_days=0)
        tz, op, cl, ex, lunch = S.SESS[inst]
        loc = Q.server_to_tz(df.index, tz)
        r = np.log(df['c']).diff().abs()
        r[pd.Series(loc.normalize(), index=df.index).diff().dt.days.fillna(1).to_numpy() != 0] = np.nan
        hm = pd.Series(loc.hour * 100 + loc.minute, index=df.index)
        prof = r.groupby(hm.to_numpy()).mean()
        cnt = r.groupby(hm.to_numpy()).size()
        top = prof.sort_values(ascending=False).head(4)
        print(f'\n{inst} ({tz}, Kasse {op}-{cl}): Spitzen |Rendite| bei Ortszeit {[f"{k:04d}" for k in top.index]} '
              f'(x Median {np.round(top.values / prof.median(), 1).tolist()})')
        o_hm = op[0] * 100 + op[1]
        pre = [k for k in prof.index if k < o_hm][-3:]
        post = [k for k in prof.index if k >= o_hm][:3]
        print('   um die Eroeffnung:', {f'{k:04d}': round(prof[k] * 1e4, 2) for k in pre + post}, '(bp)')
        if lunch:
            a, b = lunch[0][0] * 100 + lunch[0][1], lunch[1][0] * 100 + lunch[1][1]
            mid = prof[(prof.index >= a) & (prof.index < b)]
            mc = cnt[(cnt.index >= a) & (cnt.index < b)]
            morn = prof[(prof.index >= o_hm) & (prof.index < a)]
            print(f'   Mittag {a}-{b}: Kerzen je Slot {mc.min()}..{mc.max()}, |Rendite| {mid.mean() * 1e4:.2f} bp '
                  f'vs Vormittag {morn.mean() * 1e4:.2f} bp')
        x = S.prepare(df, inst)
        ins = x[x['in_sess']]
        per_day = ins.groupby('sday').size()
        exp = per_day.median()
        mon = per_day.groupby(per_day.index.to_period('M')).agg(['size', 'median'])
        bad = mon[(mon['size'] < 15) | (mon['median'] < 0.9 * exp)]
        print(f'   Sitzungstage {len(per_day)}, Kerzen je Sitzung Median {exp:.0f}; Monate mit Luecken:',
              {str(k): (int(v['size']), int(v['median'])) for k, v in bad.iterrows()})


if __name__ == '__main__':
    main()
