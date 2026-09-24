"""Sucht in der HistData-NSXUSD-Reihe (NAS100_ext_histdata_M5.csv) je Quartalsverfall (3. Freitag Mär/Jun/Sep/Dez)
im Fenster [Verfall-10 Tage, Verfall+4 Tage] den M5-Bar mit der größten Abweichung der Rendite gegenüber einer
Referenz (OANDA NAS100_USD bis 2020-05, GFT NAS100.x ab 2022). Rollsprünge des NQ-Frontmonats zeigen sich als
große Eigenbewegung der HistData-Reihe ohne entsprechende Bewegung der Referenz."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from quality import read_mt5
x = read_mt5(f'{EXT}/NAS100_ext_histdata_M5.csv')
g = load_gft('NAS100.x').set_index('ts_server')
O = pd.read_pickle(f'{EXT}/work/oanda_nas100_m1.pkl'); O['srv'] = utc_to_server(O.ts)
o = resample_ohlc(O, 'srv'); o = o[(o.index.hour != 0) & (o.index.dayofweek < 5)]
rows = []
for y in range(2010, 2027):
    for m in [3, 6, 9, 12]:
        d = pd.Timestamp(y, m, 1); fr = d + pd.Timedelta(days=(4 - d.dayofweek) % 7 + 14)
        lo, hi = fr - pd.Timedelta(days=10), fr + pd.Timedelta(days=4)
        if hi < x.index.min() or lo > x.index.max(): continue
        if fr < pd.Timestamp('2020-05-10'): ref, refname = o.close, 'OANDA'
        elif fr > pd.Timestamp('2022-01-10'): ref, refname = g.CLOSE, 'GFT'
        else: continue
        r = np.log(x.CLOSE.loc[lo:hi]).diff(); rr = np.log(ref.loc[lo:hi]).diff()
        j = pd.concat([r.rename('h'), rr.rename('ref')], axis=1, sort=True).dropna()
        if j.empty: continue
        j['ex'] = j.h - j.ref
        t = j.ex.abs().idxmax()
        rows.append({'verfall': fr.date(), 'bar_server': t, 'bar_ny': t - pd.Timedelta(hours=7), 'referenz': refname,
                     'rendite_histdata_%': round(j.h[t]*100, 3), 'rendite_ref_%': round(j.ref[t]*100, 3),
                     'abweichung_%': round(j.ex[t]*100, 3)})
df = pd.DataFrame(rows)
# Einstufung "Rollsprung wahrscheinlich": |Abw.| >= 0,15 %, Referenz ruhig (|ref| < 0,15 %) UND Bar zu einer typischen
# Rollzeit: am Verfallstag 09:20-10:00 NY (Handelsbeginn nach Schlussabrechnung des alten Kontrakts) oder am Vortag
# 16:25-16:35 NY (Wiederaufnahme nach der CME-Pause 16:15-16:30).
ny = pd.to_datetime(df.bar_ny); vf = pd.to_datetime(df.verfall)
t = ny.dt.strftime('%H:%M')
at_roll_time = ((ny.dt.normalize() == vf) & (t >= '09:20') & (t <= '10:00')) | \
               ((ny.dt.normalize() == vf - pd.Timedelta(days=1)) & (t >= '16:25') & (t <= '16:35'))
df['rollsprung_wahrscheinlich'] = (df['abweichung_%'].abs() >= 0.15) & (df['rendite_ref_%'].abs() < 0.15) & at_roll_time
df.to_csv(f'{EXT}/NAS100_histdata_rollspruenge.csv', index=False, sep=';')
pd.set_option('display.width', 200)
print(df.to_string())
print('wahrscheinliche Rollsprünge:', int(df.rollsprung_wahrscheinlich.sum()), 'von', len(df))
