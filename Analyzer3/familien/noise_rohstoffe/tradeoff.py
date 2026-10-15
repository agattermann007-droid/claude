"""Schreibt tradeoff.csv (variante, periode, trefferquote, art_trefferquote, R, R_pro_tag, n, per_day)
aus out/zellen_*.csv und out/portfolio_*.csv (Train und, falls vorhanden, Val 2024)."""
import glob
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
rows = []
for per_key in ('train', 'val'):
    fs = sorted(glob.glob(os.path.join(OUT, f'zellen_{per_key}_*.csv')))
    if not fs:
        continue
    c = pd.concat([pd.read_csv(f) for f in fs])
    for _, r in c.iterrows():
        rows.append(dict(variante=f"{r['rule']}|{r['inst']}", periode=r['period'], trefferquote=r['hit'],
                         art_trefferquote=r['art'], R=r['R'], R_pro_tag=r['R_day'], n=int(r['n']), per_day=r['per_day']))
    pf = os.path.join(OUT, f'portfolio_{per_key}.csv')
    if os.path.exists(pf):
        p = pd.read_csv(pf)
        for _, r in p.iterrows():
            rows.append(dict(variante=f"{r['rule']}|{r['portfolio']}", periode=r['period'], trefferquote=r['hit'],
                             art_trefferquote=r['art'], R=r['R'], R_pro_tag=r['R_day'], n=int(r['n']), per_day=r['per_day']))
t = pd.DataFrame(rows)
for k in ('trefferquote', 'R', 'R_pro_tag', 'per_day'):
    t[k] = t[k].astype(float).round(4)
t.to_csv(os.path.join(HERE, 'tradeoff.csv'), index=False)
print(len(t), 'Zeilen')
