"""Markdown-Tabellen fuer BERICHT.md aus out/zellen_* und out/portfolio_*."""
import os
import sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nr  # noqa: E402

ab = {'Target vor Stop': 'TvS', 'Teilziel vor Stop': 'TP1', 'Gewinnquote': 'Gew'}


def f(v, k=3, pct=False):
    if pd.isna(v):
        return '–'
    return f'{100 * v:.0f} %' if pct else f'{v:+.{k}f}' if k == 3 else f'{v:.{k}f}'


def cells():
    tr = pd.concat([pd.read_csv(os.path.join(HERE, 'out', f'zellen_train_{i}.csv')) for i in nr.INSTS + nr.CHECK])
    va = pd.concat([pd.read_csv(os.path.join(HERE, 'out', f'zellen_val_{i}.csv')) for i in nr.INSTS + nr.CHECK])
    m = tr.merge(va, on=['rule', 'inst'], suffixes=('', '_v'))
    out = ['| Regel | Instr. | n | /Tag | Tage | Treffer | Gew | R | t | Null TvS/Gew/R | Kosten R | n 24 | /Tag 24 | Treffer 24 | Gew 24 | R 24 | t 24 | Null 24 TvS/Gew/R |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for rule in nr.RULES:
        for inst in nr.INSTS + nr.CHECK:
            r = m[(m.rule == rule) & (m.inst == inst)]
            if not len(r):
                continue
            r = r.iloc[0].copy()
            if r.art != 'Target vor Stop':   # Null-TvS ohne festes Ziel nicht definiert
                r['null_tvs'] = r['null_tvs_v'] = float('nan')
            out.append(f"| {rule} | {inst} | {int(r.n)} | {f(r.per_day, 2)} | {f(r.days_cov, pct=True)} | {f(r.hit, pct=True)} {ab[r.art]} | {f(r.win, pct=True)} | {f(r.R)} | {f(r.t, 1)} | {f(r.null_tvs, pct=True)}/{f(r.null_win, pct=True)}/{f(r.null_R)} | {f(r.cost_R, 2)} | "
                       f"{int(r.n_v)} | {f(r.per_day_v, 2)} | {f(r.hit_v, pct=True)} | {f(r.win_v, pct=True)} | {f(r.R_v)} | {f(r.t_v, 1)} | {f(r.null_tvs_v, pct=True)}/{f(r.null_win_v, pct=True)}/{f(r.null_R_v)} |")
    return '\n'.join(out)


def ports():
    tr = pd.read_csv(os.path.join(HERE, 'out', 'portfolio_train.csv'))
    va = pd.read_csv(os.path.join(HERE, 'out', 'portfolio_val.csv'))
    m = tr.merge(va, on=['rule', 'portfolio'], suffixes=('', '_v'))
    out = ['| Regel | Portfolio | n | /Tag | Tage mit Trade | Treffer | R | Kosten R | R/Tag | t | t Tag | Null R | t vs Null | n 24 | /Tag 24 | Tage 24 | Treffer 24 | R 24 | R/Tag 24 | t Tag 24 | Null R 24 |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for _, r in m[m.portfolio.isin(['P_alle', 'P_sel'])].iterrows():
        if r.n == 0:
            out.append(f'| {r.rule} | {r.portfolio} | 0 (keine Auswahl) |' + ' |' * 19)
            continue
        out.append(f"| {r.rule} | {r.portfolio} | {int(r.n)} | {f(r.per_day, 2)} | {f(r.days_cov, pct=True)} | {f(r.hit, pct=True)} {ab[r.art]} | {f(r.R)} | {f(r.cost_R, 2)} | {f(r.R_day)} | {f(r.t, 1)} | {f(r.t_day, 1)} | {f(r.null_R)} | {f(r.t_vs_null, 1)} | "
                   f"{int(r.n_v)} | {f(r.per_day_v, 2)} | {f(r.days_cov_v, pct=True)} | {f(r.hit_v, pct=True)} | {f(r.R_v)} | {f(r.R_day_v)} | {f(r.t_day_v, 1)} | {f(r.null_R_v)} |")
    out2 = ['| Regel | Klasse | n | R brutto | Kosten R | R netto | t Tag | n 24 | R brutto 24 | R netto 24 |', '|---|---|---|---|---|---|---|---|---|---|']
    for _, r in m[m.portfolio.str.startswith('K_')].iterrows():
        out2.append(f"| {r.rule} | {r.portfolio[2:]} | {int(r.n)} | {f(r.R_gross)} | {f(r.cost_R, 2)} | {f(r.R)} | {f(r.t_day, 1)} | {int(r.n_v)} | {f(r.R_gross_v)} | {f(r.R_v)} |")
    return '\n'.join(out), '\n'.join(out2)


if __name__ == '__main__':
    p, k = ports()
    open(os.path.join(HERE, 'out', 'tab_zellen.md'), 'w').write(cells())
    open(os.path.join(HERE, 'out', 'tab_portfolio.md'), 'w').write(p)
    open(os.path.join(HERE, 'out', 'tab_klassen.md'), 'w').write(k)
    print(p)
    print(k)
