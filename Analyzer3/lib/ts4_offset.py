"""Woechentliche Uhrzeit-Pruefung der ts4-Daten gegen Pedram (UTC -> Serverzeit NY+7).
Fuer jede Woche: Korrelation der M5-Renditen bei Versatz -3..+3 h; bester Versatz = Korrektur, die auf ts4 addiert werden muss."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, qdata as Q

REF = {'US100': ('q', 'NAS100'), 'US500': ('q', 'SPX500'), 'XAUUSD': ('cc', 'XAUUSD')}


def ref_m5(kind, sym):
    if kind == 'q':
        d = pd.read_parquet(f'/home/user/data/raw/q__Pedram/decoded/{sym}_M1_UTC.parquet')
        m1 = d.rename(columns=str)
    else:
        d = pd.read_csv(f'/home/user/data/raw/cc__Pedram007z__BackTest-Platform/decoded/{sym}_M1.csv', parse_dates=['time_utc'])
        m1 = pd.DataFrame({'o': d.open.values, 'h': d.high.values, 'l': d.low.values, 'c': d.close.values}, index=d.time_utc)
    m1['v'] = 0.0
    m1.index = Q.utc_to_server(m1.index)
    return Q.to_m5(m1[~m1.index.duplicated()])


def weekly_offsets(ts4sym, ref):
    a = Q.src_ts4(ts4sym)
    ra = np.log(a.c).diff()
    rb = np.log(ref.c).diff()
    out = []
    for wk, g in ra.groupby(ra.index.to_period('W')):
        if len(g) < 500:
            continue
        best = None
        for off in range(-3, 4):
            s = g.copy(); s.index = s.index + pd.Timedelta(hours=off)
            j = pd.concat([s, rb], axis=1, join='inner').dropna()
            if len(j) < 300:
                continue
            c = j.corr().iloc[0, 1]
            if best is None or c > best[1]:
                best = (off, c)
        if best:
            out.append((wk.start_time, best[0], best[1]))
    return pd.DataFrame(out, columns=['woche', 'versatz_h', 'korr']).set_index('woche')


if __name__ == '__main__':
    for ts4sym, (kind, sym) in REF.items():
        w = weekly_offsets(ts4sym, ref_m5(kind, sym))
        w = w[w.index < '2025-01-01']
        chg = w['versatz_h'].ne(w['versatz_h'].shift())
        print(f'== {ts4sym}: Wochen {len(w)}, Median-Korrelation {w.korr.median():.3f}')
        print(w[chg].to_string())
        w.to_csv(f'/home/user/data/ts4_offset_{ts4sym}.csv')
