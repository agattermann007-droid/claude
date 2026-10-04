"""V7-Forschung, Stufe 4: gepaarter Vergleich Basis gegen Kandidat (gleiche Starts, gleiche Stoerungen).
Je Stoerung (Seed) Mittel ueber alle 1-Jahres-Konten (jeder 3. Tag); Differenz je Seed -> Mittel, SD, SE, Anteil Seeds besser.
Aufruf: python y7_paar.py gft|ext"""
import sys, os, pickle, numpy as np
from concurrent.futures import ProcessPoolExecutor
import eng6 as E, evl6 as V, prep5 as P, y7_konto as Q

target = sys.argv[1]
if target == "ext":
    V._MK = E.Market(D=pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb")), S=pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb")))
fb = Q.fade_blocks(target)
gpf = [dict(on=1, risk=0.75, maxtrades=1, harv=1) for _ in Q.F10]
CANDS = {
    "Basis": (fb, gpf),
    "Spike Long k0.20": (fb + [Q.spike_block(target, 10, dict(Q.SPIKE, kmin=0.20), only_dir=1)], gpf + [dict(on=1, risk=0.75, maxtrades=1, harv=1)]),
    "Spike Long k0.25": (fb + [Q.spike_block(target, 10, dict(Q.SPIKE, kmin=0.25), only_dir=1)], gpf + [dict(on=1, risk=0.75, maxtrades=1, harv=1)]),
}
Pv = E.params(**Q.BASE)
m = V.mk()
if target == "ext":
    st = V.starts(m, 250, 9, warm="2006-09-01", end="2021-12-31"); seeds = range(8)
else:
    st = V.starts(m, 250, 3, end="2025-12-31"); seeds = range(16)
res = {}
for lbl, (blks, gps) in CANDS.items():
    GP = E.gparams(gps)
    V.set_generic(blks, GP)
    jobs = [(Pv, a, b, s, 0.05, 0.3, GP) for s in seeds for (a, b) in st]
    with ProcessPoolExecutor(4) as ex:
        outs = list(ex.map(V._job, jobs, chunksize=32))
    per = {}
    for (Pv_, a, b, s, *_), o in zip(jobs, outs):
        per.setdefault(s, []).append(o)
    res[lbl] = {s: V.agg(rows) for s, rows in per.items()}
    a = np.array([[res[lbl][s][k] for k in ("pay", "net", "bust", "s6", "mx")] for s in seeds])
    print(f"{target} {lbl:<20s} Ausz {a[:,0].mean():5.2f} Netto {a[:,1].mean():6.0f} Bust {a[:,2].mean():.3f} S6 {a[:,3].mean():.2f} maxS {a[:,4].mean():.1f}", flush=True)
base = np.array([[res["Basis"][s][k] for k in ("pay", "net", "s6")] for s in seeds])
for lbl in CANDS:
    if lbl == "Basis":
        continue
    c = np.array([[res[lbl][s][k] for k in ("pay", "net", "s6")] for s in seeds])
    d = c - base
    n = len(d)
    print(f"{target} {lbl:<20s} - Basis: Ausz {d[:,0].mean():+.2f} (SD {d[:,0].std(ddof=1):.2f}, SE {d[:,0].std(ddof=1)/np.sqrt(n):.2f}, besser {int((d[:,0]>0).sum())}/{n}) | "
          f"Netto {d[:,1].mean():+.0f} (SE {d[:,1].std(ddof=1)/np.sqrt(n):.0f}, besser {int((d[:,1]>0).sum())}/{n}) | S6 {d[:,2].mean():+.2f}", flush=True)
