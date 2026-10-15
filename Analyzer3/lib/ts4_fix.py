"""Bestimmt je ts4-Symbol die Zeitraeume, in denen die ts4-Uhr 1 h hinter NY+7 liegt (Broker fest UTC+2),
tageweise per Korrelation der M5-Renditen gegen Pedram (UTC -> Serverzeit), Umstellungstage in 4-h-Bloecken.
Ergebnis: /home/user/data/ts4_korrektur.json  {sym: [[von, bis], ...]}  (Serverzeit-Labels von ts4, +1 h addieren)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd, qdata as Q

PAIR = {'US100': 'NAS100', 'US500': 'SPX500', 'XAUUSD': 'XAUUSD', 'EURUSD': 'EURUSD', 'GBPUSD': 'GBPUSD',
        'AUDUSD': 'AUDUSD', 'USDCAD': 'USDCAD', 'USDCHF': 'USDCHF'}


def ped(sym):
    d = pd.read_parquet(f'/home/user/data/raw/q__Pedram/decoded/{sym}_M1_UTC.parquet')
    d['v'] = 0.0
    d.index = Q.utc_to_server(d.index)
    return Q.to_m5(d[~d.index.duplicated()])


def corr_off(g, rb, off):
    s = g.copy(); s.index = s.index + pd.Timedelta(hours=off)
    j = pd.concat([s, rb], axis=1, join='inner').dropna()
    return j.corr().iloc[0, 1] if len(j) > 20 else np.nan


def blocks(sym):
    a = Q.src_ts4(sym); ra = np.log(a.c).diff()
    rb = np.log(ped(PAIR[sym]).c).diff()
    rows = []
    for day, g in ra.groupby(ra.index.normalize()):
        if len(g) < 100:
            continue
        c0, c1 = corr_off(g, rb, 0), corr_off(g, rb, 1)
        rows.append((day, c0, c1))
    d = pd.DataFrame(rows, columns=['tag', 'k0', 'k1']).set_index('tag')
    d['plus1'] = d.k1 > d.k0
    # Umstellungstage (Wechsel zum Vortag) in 4-h-Bloecken aufloesen
    iv, cur = [], None
    for day, r in d.iterrows():
        if r.plus1 and cur is None:
            cur = day
        if not r.plus1 and cur is not None:
            iv.append([cur, day]); cur = None
    if cur is not None:
        iv.append([cur, d.index[-1] + pd.Timedelta(days=1)])
    fine = []
    for a0, b0 in iv:
        # Ende genauer: 4-h-Bloecke am letzten +1-Tag und am ersten 0-Tag
        end = b0
        for t0 in pd.date_range(b0 - pd.Timedelta(days=1), b0 + pd.Timedelta(days=1), freq='4h'):
            g = ra[(ra.index >= t0) & (ra.index < t0 + pd.Timedelta(hours=4))]
            if len(g) > 20 and corr_off(g, rb, 0) > corr_off(g, rb, 1):
                end = t0; break
        fine.append([str(a0), str(end)])
    return d, fine


if __name__ == '__main__':
    out = {}
    for sym in PAIR:
        d, fine = blocks(sym)
        n1 = int(d.plus1.sum())
        print(f'{sym}: Tage {len(d)}, Tage mit +1h {n1}, Median-Korr. richtig {np.nanmedian(np.maximum(d.k0, d.k1)):.3f}, Intervalle {fine}', flush=True)
        out[sym] = fine
    json.dump(out, open('/home/user/data/ts4_korrektur.json', 'w'), indent=1)
