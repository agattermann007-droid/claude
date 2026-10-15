"""Trade-off-Kurve (Trefferquote gegen R) je Effekt aus den v2-Laeufen -> tradeoff.csv."""
import os
import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
COLS = ['variante', 'periode', 'trefferquote', 'art_trefferquote', 'R', 'R_pro_tag', 'n', 'per_day']
z = pd.concat([pd.read_csv(os.path.join(HIER, f)) for f in
               ['zellen_train.csv', 'zellen_val.csv', 'noise_train.csv', 'noise_val.csv']], ignore_index=True)
rows = []
for _, r in z.iterrows():
    rows.append({c: r[c] for c in COLS})
    gw = r['art_trefferquote'] == 'Gewinnquote'
    rows.append(dict(variante=r['variante'], periode='Nullmodell ' + r['periode'],
                     trefferquote=r['null_win'] if gw else r['null_tvs'], art_trefferquote=r['art_trefferquote'],
                     R=r['null_R'], R_pro_tag=r['null_R'] * r['per_day'], n=r['n'], per_day=r['per_day']))
out = pd.DataFrame(rows)
order = {'Train': 0, 'Nullmodell Train': 1, 'Val 2024': 2, 'Nullmodell Val 2024': 3}
out['_o'] = out['periode'].map(order)
out['_v'] = pd.Categorical(out['variante'], categories=list(dict.fromkeys(z['variante'])), ordered=True)
out = out.sort_values(['_v', '_o']).drop(columns=['_o', '_v'])
for c in ['trefferquote', 'R', 'R_pro_tag', 'per_day']:
    out[c] = out[c].astype(float).round(4)
out['n'] = out['n'].astype(int)
out.to_csv(os.path.join(HIER, 'tradeoff.csv'), index=False)
print(len(out), 'Zeilen')
