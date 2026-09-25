"""Build 6.60: Welche Fade-Signale (nach Filter und Waechter, S2) laesst das Konto aus, und sind das die besseren? Je Signal:
Abdeckung c = Zahl der Konten x Stoerungen, die an seinem Tag laufen; gehandelt t = Zahl davon, die es handeln. Je Jahr und
Modul: Anteil gehandelt, R je Signal gehandelt / ausgelassen (abdeckungsgewichtet, dadurch ohne Verzerrung durch die
ungleiche Abdeckung der Jahre). Aufruf: python a60_stufen2.py [Variante] [gft|ext] [Schritt] [Stoerungen]"""
import numpy as np, sys
import x60, x48, r6, pg_blocks as PB
import eng10 as E, evl6 as V, evl10 as V10

lbl = sys.argv[1] if len(sys.argv) > 1 else "6.50 Ertrag"
target = sys.argv[2] if len(sys.argv) > 2 else "gft"
step = int(sys.argv[3]) if len(sys.argv) > 3 else 4
nseed = int(sys.argv[4]) if len(sys.argv) > 4 else 4
kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x60.VAR[lbl])
blks, info, mk = x60.setup(target, rule, extra)
V._MK = mk
mk.r21["reg"] = x48.r21_regime(target, mk)
GP = x60.fade_gp(gpx, frisk, per, extra_gp)
V.set_generic(blks, GP)
Pv = E.params(**dict(r6.SAFE, **kw))
# S2-Signale mit virtuellem R
sig = {}
for s_, nm in enumerate(PB.F10):
    f = PB.fi(target, nm)
    Rmap = {int(t): float(R) for t, R in zip(f["t_entry"], f["R"])}
    for te in blks[s_]["t_entry"]:
        sig[(s_, int(te))] = [Rmap[int(te)], 0, 0]
day_of_sig = {}
for (s_, te) in sig:
    # Servertag der Einstiegskerze
    ev = np.searchsorted(mk.ev_t, te)
    day_of_sig[(s_, te)] = int(mk.ev_day[min(ev, len(mk.ev_day) - 1)])
warm, end = (V.WARM, None) if target == "gft" else ("2006-09-01", "2021-12-31")
starts = V.starts(mk, 250, step, warm, end)
cov = np.zeros(len(mk.days) + 1)
for (a, b) in starts:
    cov[a:min(b, len(mk.days))] += nseed
for k, d in day_of_sig.items():
    sig[k][1] = cov[d]
for (a, b) in starts:
    for seed in range(nseed):
        ms = V.masks(mk, seed, 0.08 if seed > 0 else 0.0)
        P2 = Pv.copy()
        if seed > 0:
            P2[E.PI["slip_frac"]] = 0.3
        r = E.run(mk, P2, a, b, seed=seed, masks=ms, GP=GP)
        for row in r["tr"]:
            sl = int(row[2])
            if sl < E.G0 or row[7] <= 0:
                continue
            s_ = (sl - E.G0) // 2
            tmin = int(row[3])
            k = (s_, tmin) if (s_, tmin) in sig else (s_, tmin - 1440)
            if k in sig:
                sig[k][2] += 1
yr = lambda te: int(str(np.datetime64(int(te), "m"))[:4])
years = sorted({yr(k[1]) for k in sig})
print(f"{target} {lbl}: Fade-Signale nach Waechter (S2): Anteil im Konto gehandelt | R je Signal gehandelt / ausgelassen (abdeckungsgewichtet)")
for nm in PB.F10 + ["SUMME"]:
    cells = []
    for y in years:
        ks = [k for k in sig if yr(k[1]) == y and (nm == "SUMME" or PB.F10[k[0]] == nm) and sig[k][1] > 0]
        if not ks:
            cells.append(" " * 30); continue
        c = np.array([sig[k][1] for k in ks]); t = np.array([sig[k][2] for k in ks]); R = np.array([sig[k][0] for k in ks])
        t = np.minimum(t, c)
        sk = c - t
        rt = (t * R).sum() / max(t.sum(), 1e-9); rs = (sk * R).sum() / max(sk.sum(), 1e-9)
        cells.append(f"{100 * t.sum() / c.sum():3.0f}% | {rt:+.3f} / {rs:+.3f}")
    print(f"{nm:7s} " + "   ".join(f"{c:30s}" for c in cells))
print("Jahre:", years)
