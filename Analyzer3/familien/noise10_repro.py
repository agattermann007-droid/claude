"""Nachbau noise-1.0 und Abgleich mit den bekannten Kennzahlen (54/60/57 %, +0,10/+0,17/+0,15 R)."""
import sys, os, itertools
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import pandas as pd, numpy as np
import qdata as Q, qbt, noise

df = Q.load('NAS100', '2021-01-01', '2026-01-01')
x = noise.prepare(df, 'NAS100')
P = {'2021-23': ('2021-01-01', '2024-01-01'), '2024': ('2024-01-01', '2025-01-01'), '2025': ('2025-01-01', '2026-01-01')}
rows = []
for grid, trend, opd, stop in itertools.product([30, 5], ['cprev', 'close', 'none'], [False, True], ['mid']):
    sig = noise.signals(x, grid=grid, first_min=30 if grid == 30 else 5, trend=trend, one_per_day=opd, stop_mode=stop)
    res = qbt.simulate(x, sig, 'NAS100')
    tr = qbt.trades_only(res)
    t = qbt.by_period(tr, x, P)
    r = {'grid': grid, 'trend': trend, 'one_per_day': opd}
    for p in P:
        r[f'n_{p}'] = int(t.loc[p, 'n']); r[f'tvs_{p}'] = round(100 * t.loc[p, 'tvs'], 1); r[f'R_{p}'] = round(t.loc[p, 'R'], 3)
    r['dist'] = sum(abs(r[f'tvs_{p}'] - v) for p, v in zip(P, [54, 60, 57])) / 3 + 100 * sum(abs(r[f'R_{p}'] - v) for p, v in zip(P, [0.10, 0.17, 0.15])) / 3
    rows.append(r)
out = pd.DataFrame(rows).sort_values('dist')
pd.set_option('display.width', 250)
print(out.to_string(index=False))
