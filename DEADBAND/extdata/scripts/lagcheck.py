"""Tagesweise Lead/Lag-Prüfung zwischen zwei Kursreihen gleicher Frequenz (Index = gleiche Zeitbasis).
Für jeden Tag: Korrelation der Renditen bei Verschiebung um -L..+L Bars; bester Lag.
Markiert Tage mit bestem Lag != 0 und Verbesserung > delta gegenüber Lag 0."""
import numpy as np, pandas as pd

def daily_lag(x_close, y_close, L=6, min_n=100, delta=0.10, freq='5min'):
    idx = pd.date_range(min(x_close.index.min(), y_close.index.min()).floor('D'),
                        max(x_close.index.max(), y_close.index.max()).ceil('D'), freq=freq)
    x = np.log(x_close.reindex(idx).ffill(limit=3)).diff()
    y = np.log(y_close.reindex(idx).ffill(limit=3)).diff()
    df = pd.DataFrame({'x': x, 'y': y})
    rows = []
    for day, g in df.groupby(df.index.date):
        g = g.dropna()
        if len(g) < min_n: continue
        cs = {}
        for l in range(-L, L + 1):
            xs = g.x.shift(l)
            m = xs.notna() & g.y.notna()
            if m.sum() < min_n: continue
            cs[l] = np.corrcoef(xs[m], g.y[m])[0, 1]
        if 0 not in cs: continue
        best = max(cs, key=lambda k: cs[k])
        rows.append((pd.Timestamp(day), best, cs[best], cs[0]))
    r = pd.DataFrame(rows, columns=['day', 'best_lag', 'corr_best', 'corr0']).set_index('day')
    r['flag'] = (r.best_lag != 0) & (r.corr_best - r.corr0 > delta)
    return r
