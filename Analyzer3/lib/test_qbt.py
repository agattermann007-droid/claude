"""Selbsttest des Simulators an konstruierten Kerzen."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import qbt

def mk(bars):
    idx = pd.date_range('2023-03-01 17:00', periods=len(bars), freq='5min')
    df = pd.DataFrame(bars, columns=list('ohlc'), index=idx, dtype=float); df['v'] = 1.0
    df.attrs['inst'] = 'NAS100'; return df

def run(df, **kw):
    sig = pd.DataFrame([dict(i_sig=0, d=1, stop=95.0, tgt_R=1.0, i_last=len(df) - 1, kind='market', **kw)])
    return qbt.simulate(df, sig, cost=0.0).iloc[0]

ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print(('OK  ' if cond else 'FAIL'), name)

# 1 Einstieg zur naechsten Eroeffnung, Ziel 1R
r = run(mk([[100,100,100,100],[100,101,99,100],[100,106,99,105]]))
check('Ziel bei 105 (E=100, Stop 95)', r.code == 1 and r.E == 100 and r.X == 105 and abs(r.R - 1) < 1e-9)
# 2 Stop und Ziel in derselben Kerze -> Stop
r = run(mk([[100,100,100,100],[100,106,94,100]]))
check('gleiche Kerze -> Stop', r.code == -1 and abs(r.R + 1) < 1e-9)
# 3 Gap unter Stop -> Ausstieg zur Eroeffnung
r = run(mk([[100,100,100,100],[100,101,99,100],[90,91,89,90]]))
check('Gap unter Stop -> X=90, R=-2', r.code == -1 and r.X == 90 and abs(r.R + 2) < 1e-9)
# 4 Zeitausstieg
r = run(mk([[100,100,100,100],[100,101,99,100],[100,102,98,101]]))
check('Zeitausstieg zum Schluss 101', r.code == 0 and r.X == 101 and abs(r.R - 0.2) < 1e-9)
# 5 Einstieg ungueltig, wenn Eroeffnung schon unter Stop
r = run(mk([[100,100,100,100],[94,95,93,94],[100,106,99,105]]))
check('Eroeffnung unter Stop -> ungueltig', r.code == -8)
# 6 Kosten: 0,01 % von 100 bei Risiko 5 -> 0,002 R
sig = pd.DataFrame([dict(i_sig=0, d=1, stop=95.0, tgt_R=1.0, i_last=2, kind='market')])
r = qbt.simulate(mk([[100,100,100,100],[100,101,99,100],[100,106,99,105]]), sig, cost=0.0001).iloc[0]
check('Kosten 0,002 R', abs(r.R - (1 - 0.002)) < 1e-9)
# 7 Stop-Einstieg Long bei 102, Fuellung mit Gap zur Eroeffnung 103
sig = pd.DataFrame([dict(i_sig=0, d=1, stop=98.0, tgt_R=1.0, i_last=4, kind='stop', level=102.0, i_exp=3)])
r = qbt.simulate(mk([[100,100,100,100],[100,101,99,100],[103,104,102.5,103.5],[103.5,109,103,108],[108,108,108,108]]), sig, cost=0).iloc[0]
check('Stop-Order: Fuellung 103 (Gap), Ziel 108', r.E == 103 and r.code == 1 and r.X == 108)
# 8 Limit-Order nicht gefuellt
sig = pd.DataFrame([dict(i_sig=0, d=1, stop=95.0, tgt_R=1.0, i_last=3, kind='limit', level=97.0, i_exp=2)])
r = qbt.simulate(mk([[100,100,100,100],[100,101,99,100],[100,101,98,100],[96,96,96,96]]), sig, cost=0).iloc[0]
check('Limit nicht gefuellt bis i_exp', r.code == -7)
# 9 Nachzieh-Stop: Wert der Vorkerze
df = mk([[100,100,100,100],[100,103,99.5,102],[102,104,101.5,103],[103,103,100.5,101]])
df['tr'] = [np.nan, 101.0, 101.0, 101.0]
sig = pd.DataFrame([dict(i_sig=0, d=1, stop=95.0, tgt_R=np.nan, i_last=3, kind='market', trail='tr')])
r = qbt.simulate(df, sig, cost=0).iloc[0]
check('Nachzieh-Stop 101 greift in Kerze 3', r.code == -1 and r.X == 101 and r.i_exit == 3)
# 10 Teilziel 0,5R zur Haelfte, Rest Ziel 1R
sig = pd.DataFrame([dict(i_sig=0, d=1, stop=95.0, tgt_R=1.0, i_last=3, kind='market', tp1_R=0.5, tp1_frac=0.5, be_after_tp1=True)])
r = qbt.simulate(mk([[100,100,100,100],[100,103,99,102],[102,102.5,99.9,100],[100,100,100,100]]), sig, cost=0).iloc[0]
check('Teilziel 0,5R, danach Break-even -> R=0,25', r.code == -1 and abs(r.R - 0.25) < 1e-9)
# 11 sequenziell: zweites Signal waehrend offener Position verfaellt
df = mk([[100,100,100,100]] + [[100,101,99,100]] * 5 + [[100,106,99,105]])
sig = pd.DataFrame([dict(i_sig=0, d=1, stop=95.0, tgt_R=1.0, i_last=6, kind='market'), dict(i_sig=2, d=1, stop=95.0, tgt_R=1.0, i_last=6, kind='market')])
r = qbt.simulate(df, sig, cost=0)
check('zweites Signal verfaellt', (r.code.values == [1, -9]).all())
print('ALLE OK' if ok else 'FEHLER')
