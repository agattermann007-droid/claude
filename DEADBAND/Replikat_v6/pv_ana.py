"""Build 6.50: Analyse der Trades nach gueltigem Tag (pv=1): RSI21 nach Einstiegsstunde, gleicher Tag geschlossen oder spaeter,
Tageskipp-Anteil (Tag war gueltig, Trade schliesst am selben Tag mit Verlust > Kopfraum)."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eng9 as E, evl6 as V, r6, x48, x44
from concurrent.futures import ProcessPoolExecutor

name = sys.argv[1] if len(sys.argv) > 1 else "B50 F0.7 frei N1330+N1300"
v = x48.VAR[name]
kw, gpx = v[0], v[1]; frisk = v[2]; rule = v[3]; per = v[4] if len(v) > 4 else None
blks, info, mk = x44.setup("gft", rule)
V._MK = mk
GP = x48.fade_gp(gpx, frisk, per)
V.set_generic(blks, GP)
Pv = E.params(**dict(r6.SAFE, **kw))

def job(args):
    a, b, seed = args
    m = V.mk()
    P = Pv.copy()
    if seed > 0:
        P[E.PI["slip_frac"]] = 0.3
    ms = V.masks(m, seed, 0.08 if seed > 0 else 0.0)
    r = E.run(m, P, a, b, seed=seed, masks=ms, GP=GP)
    return r["tr"], r["years"]

m = V.mk()
jobs = [(a, b, s) for (a, b) in V.starts(m, 250, 4) for s in range(8)]
with ProcessPoolExecutor(4) as ex:
    outs = list(ex.map(job, jobs, chunksize=16))
Y = sum(o[1] for o in outs)
rows = np.concatenate([o[0] for o in outs])
slot = rows[:, 2].astype(int); pv = rows[:, 4]; hd = rows[:, 5]; pnl = rows[:, 1]
eday = (rows[:, 3] // 1440).astype(int); cday = rows[:, 0].astype(int); ehr = (rows[:, 3] % 1440) / 60.0
same = eday == cday
def grp(sl):
    if sl < 2: return "db"
    if sl < E.NZ0: return "r21"
    if sl < E.NZ1: return "nz"
    return f"g{(sl - E.G0) // 2}"
g = np.array([grp(s) for s in slot])
print(name, "Konten-Jahre %.0f" % Y)
for mod in ("r21", "nz", "g1", "g7", "g6", "g9", "g2", "g0"):
    for f in (0, 1):
        sel = (g == mod) & (pv == f)
        if not sel.any():
            continue
        s1 = sel & same; s2 = sel & ~same
        flip = sel & same & (pnl < 0) & (-pnl > hd)
        print(f"{mod:4s} pv{f}: n/J {sel.sum()/Y:5.1f} Summe/J {pnl[sel].sum()/Y:6.0f} WR {100*np.mean(pnl[sel]>0):4.0f}% | "
              f"gleicher Tag n/J {s1.sum()/Y:5.1f} Summe {pnl[s1].sum()/Y:6.0f} | spaeter n/J {s2.sum()/Y:5.1f} Summe {pnl[s2].sum()/Y:6.0f} | "
              f"kippt Tag (Verlust > Kopfraum) n/J {flip.sum()/Y:4.1f}")
# RSI21 pv=1 nach Einstiegsstunde
sel = (g == "r21") & (pv == 1)
for h0, h1 in ((0, 10), (10, 11), (11, 12), (12, 13), (13, 15), (15, 24)):
    s = sel & (ehr >= h0) & (ehr < h1)
    flip = s & same & (pnl < 0) & (-pnl > hd)
    print(f"  r21 pv1 Einstieg {h0:2d}-{h1:2d} NY: n/J {s.sum()/Y:4.1f} Summe/J {pnl[s].sum()/Y:5.0f} gleicher Tag {100*np.mean(same[s]) if s.any() else 0:3.0f}% kippt n/J {flip.sum()/Y:4.2f}")
# Kopfraum-Klassen
for a0, a1 in ((0, 25), (25, 50), (50, 100), (100, 1e9)):
    s = sel & (hd >= a0) & (hd < a1)
    flip = s & same & (pnl < 0) & (-pnl > hd)
    print(f"  r21 pv1 Kopfraum {a0:4.0f}-{a1:5.0f}$: n/J {s.sum()/Y:4.1f} Summe/J {pnl[s].sum()/Y:5.0f} kippt n/J {flip.sum()/Y:4.2f}")
tf = rows[:, 6]; r0 = rows[:, 7]
for f in (0, 1):
    for t in (0, 1, 2):
        s = (g == "r21") & (pv == f) & (tf == t)
        if not s.any():
            continue
        flip = s & same & (pnl < 0) & (-pnl > hd)
        print(f"  r21 pv{f} tf {['M15','M30','H1'][t]}: n/J {s.sum()/Y:5.1f} Summe/J {pnl[s].sum()/Y:6.0f} WR {100*np.mean(pnl[s]>0):3.0f}% "
              f"gleicher Tag {100*np.mean(same[s]):3.0f}% Risiko Ø {r0[s].mean():5.1f}$ kippt n/J {flip.sum()/Y:4.2f}")
