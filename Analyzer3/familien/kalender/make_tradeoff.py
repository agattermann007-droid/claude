"""Fasst zellen_{train,val}_stufe*.csv zu tradeoff.csv und Markdown-Tabellen zusammen."""
import glob, os
import numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(H, 'zellen_*_stufe*.csv')))], ignore_index=True)
rows = []
for _, r in d.iterrows():
    nz = r['art_trefferquote'] == 'Gewinnquote'
    rows.append(dict(variante=r['variante'], periode=r['periode'], trefferquote=r['trefferquote'], art_trefferquote=r['art_trefferquote'],
                     R=r['R'], R_pro_tag=r['R_pro_tag'], n=int(r['n']), per_day=r['per_day']))
    rows.append(dict(variante=r['variante'], periode='Nullmodell ' + r['periode'], trefferquote=(r['null_win'] if nz else r['null_tvs']),
                     art_trefferquote=r['art_trefferquote'], R=r['null_R'], R_pro_tag=r['null_R'] * r['per_day'], n=int(r['n']), per_day=r['per_day']))
t = pd.DataFrame(rows)
order = {'Train': 0, 'Nullmodell Train': 1, 'Val 2024': 2, 'Nullmodell Val 2024': 3}
t['_o'] = t['periode'].map(order)
t['_v'] = pd.Categorical(t['variante'], categories=list(dict.fromkeys(d['variante'])))
t = t.sort_values(['_v', '_o']).drop(columns=['_o', '_v'])
t.round(4).to_csv(os.path.join(H, 'tradeoff.csv'), index=False)
print(len(t), 'Zeilen -> tradeoff.csv')

def f(v, p=2, pct=False):
    if pd.isna(v): return '–'
    return f'{100*v:.0f} %' if pct else f'{v:+.{p}f}' if p else f'{v:.0f}'
# Markdown: je Variante eine Zeile mit Train / Null Train / Val / Null Val
lines = ['| Variante | Train n | /Tag | TvS | Gew. | R netto | t | Null TvS | Null Gew. | Null R | Val n | TvS | Gew. | R netto | t | Null TvS | Null Gew. | Null R |',
         '|' + '---|' * 18]
for v in dict.fromkeys(d['variante']):
    a = d[(d.variante == v) & (d.periode == 'Train')].iloc[0]
    b = d[(d.variante == v) & (d.periode == 'Val 2024')].iloc[0]
    tv = lambda r, k: '–' if r['art_trefferquote'] == 'Gewinnquote' else f(r[k], pct=True)
    lines.append(f"| {v} | {int(a.n)} | {a.per_day:.2f} | {tv(a,'tvs')} | {f(a.win,pct=True)} | {f(a.R)} | {a.t:+.1f} | {tv(a,'null_tvs')} | {f(a.null_win,pct=True)} | {f(a.null_R)} | "
                 f"{int(b.n)} | {tv(b,'tvs')} | {f(b.win,pct=True)} | {f(b.R)} | {b.t:+.1f} | {tv(b,'null_tvs')} | {f(b.null_win,pct=True)} | {f(b.null_R)} |")
pass
print('\n'.join(lines))
