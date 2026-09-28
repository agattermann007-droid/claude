"""Build 6.50: Alle RSI21-Trades (auch vor gueltigem Tag) nach Einstiegsstunde: Anteil am selben Tag geschlossen, Anteil am selben Tag
mit Verlust geschlossen, Ergebnis gleicher Tag / spaeter. Grundlage fuer die RSI21-Schutzgrenze (gewaehlt: 13:00 NY)."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eng9 as E, evl6 as V, r6, x48, x44
from concurrent.futures import ProcessPoolExecutor
name = sys.argv[1] if len(sys.argv) > 1 else "C50"
v = x48.VAR[name]
kw, gpx = v[0], v[1]; frisk = v[2]; rule = v[3]; per = v[4] if len(v) > 4 else None
blks, info, mk = x44.setup("gft", rule)
V._MK = mk
GP = x48.fade_gp(gpx, frisk, per)
V.set_generic(blks, GP)
Pv = E.params(**dict(r6.SAFE, **kw))
def job(args):
    a, b, seed = args
    m = V.mk(); P = Pv.copy()
    if seed > 0: P[E.PI["slip_frac"]] = 0.3
    ms = V.masks(m, seed, 0.08 if seed > 0 else 0.0)
    r = E.run(m, P, a, b, seed=seed, masks=ms, GP=GP)
    return r["tr"], r["years"]
m = V.mk()
jobs = [(a, b, s) for (a, b) in V.starts(m, 250, 2) for s in range(16)]
with ProcessPoolExecutor(4) as ex:
    outs = list(ex.map(job, jobs, chunksize=16))
Y = sum(o[1] for o in outs)
rows = np.concatenate([o[0] for o in outs])
slot = rows[:, 2].astype(int); pnl = rows[:, 1]; pv = rows[:, 4]; hd = rows[:, 5]; r0 = rows[:, 7]
eday = (rows[:, 3] // 1440).astype(int); cday = rows[:, 0].astype(int); ehr = (rows[:, 3] % 1440) / 60.0
same = eday == cday
r21 = (slot >= 2) & (slot < E.NZ0)
print(name, "Konten-Jahre %.0f, RSI21-Trades %d" % (Y, r21.sum()))
for h0, h1 in ((9.5, 10), (10, 10.5), (10.5, 11), (11, 11.5), (11.5, 12), (12, 13), (13, 15), (15, 17), (17, 24), (0, 9.5)):
    s = r21 & (ehr >= h0) & (ehr < h1)
    if s.sum() < 5: continue
    sl = s & same & (pnl < 0)
    print(f"  Einstieg {h0:5.1f}-{h1:5.1f} NY: n/J {s.sum()/Y:5.1f} WR {100*np.mean(pnl[s]>0):3.0f}% | gleicher Tag {100*np.mean(same[s]):3.0f}%, "
          f"davon Verlust {100*sl.sum()/max(s.sum(),1):3.0f}% aller | Ergebnis/Trade {pnl[s].mean():6.1f}$ (gleicher Tag {pnl[s & same].mean() if (s&same).any() else 0:6.1f}, spaeter {pnl[s & ~same].mean() if (s&~same).any() else 0:6.1f}) | Risiko {r0[s].mean():4.1f}$ | davon pv1 n/J {(s & (pv==1)).sum()/Y:4.1f}")
