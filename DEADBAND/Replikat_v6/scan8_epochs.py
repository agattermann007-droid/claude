"""Familien B (Ausbruch), M (Tageszeit-Momentum), S (Sweep) ueber 4 Epochen: 2006-13, 2014-21 (Fremddaten),
2022-24H1, 2024H2-26 (GFT). Ausgabe: Varianten mit PF >= Schwelle in allen Epochen."""
import numpy as np, itertools, json, time, os, pickle, sys
import gsig as G, gext, prep5 as P
import scan6 as S

def epochs_for(dataset):
    if dataset == "ext":
        return [(None, np.datetime64("2014-01-01", "m").astype(np.int64)), (np.datetime64("2014-01-01", "m").astype(np.int64), None)]
    return [(None, S.SPLIT), (S.SPLIT, None)]

def run_dataset(dataset):
    if dataset == "ext":
        G._D = gext.data_ext()
    else:
        G._D = None; G.data()
    out = {}
    for sym in ("XAU", "NAS"):
        D, ny, days, t_end, atr = S.prep(sym)
        o, h, l, c, sp = D["o"], D["h"], D["l"], D["c"], D["sp"]
        eps = epochs_for(dataset)
        def rec(key, ie, d, rd, tp, ix):
            if len(ie) < 60:
                return
            R, *_ = G.simulate(sym, ie, d, rd, tp, ix)
            te = ny[ie]; ms = []
            for lo, hi in eps:
                mk = np.ones(len(te), bool)
                if lo is not None: mk &= te >= lo
                if hi is not None: mk &= te < hi
                if mk.sum() < 30:
                    return
                m = G.metrics(R[mk], te[mk]); ms.append((m["pf"], m["wr"], m["Ry"], m["maxS"], m["n"]))
            out[key] = ms
        ranges = [(-300, 120), (-420, 180), (0, 180), (120, 180), (180, 240), (240, 330), (330, 570), (570, 600), (570, 630), (570, 660), (480, 570)]
        for (r0, r1), dirs, (sm, sk), tp, xoff, (mn, mx) in itertools.product(ranges, (1, -1), ((0, 0), (1, 0), (2, 0.5)), (1.0, 2.0, 0.0), (240, 600), ((0.0, 99), (0.0, 0.5))):
            tend = r1 + 180; xm = min(r1 + xoff, 16 * 60 + 40)
            if xm <= tend:
                tend = xm - 5
            ie, d, rd, ix = S.gen_break(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, sm, sk, dirs, mn, mx)
            rec(("B", sym, r0, r1, dirs, sm, sk, tp, xm, mx), ie, d, rd, np.full(len(ie), tp), ix)
        moms = [(-420, 180), (-420, 570), (-60, 180), (180, 300), (570, 600), (570, 630), (570, 660), (600, 720), (720, 840), (840, 900), (900, 930)]
        for (t0, t1), rev, k, stopk, xoff, dirs in itertools.product(moms, (0, 1), (0.1, 0.25, 0.5), (0.3, 0.6), (30, 120, 360), (1, -1)):
            xm = min(t1 + xoff, 16 * 60 + 40)
            if xm <= t1:
                continue
            ie, d, rd, ix = S.gen_mom(ny, o, h, l, c, sp, days, t_end, atr, t0, t1, xm, k, rev, stopk, dirs)
            rec(("M", sym, t0, t1, rev, k, stopk, xm, dirs), ie, d, rd, np.zeros(len(ie)), ix)
        for kind in ("nyday", "rth", "asia"):
            hi_, lo_ = S.levels_prevday(sym, days, kind)
            wins = [(120, 330), (180, 480), (330, 570), (570, 690), (570, 840), (690, 900)] if kind != "asia" else [(120, 330), (180, 480), (330, 570), (570, 690)]
            for (t0, tend), dirs, buf, tpr, xoff, wick in itertools.product(wins, (1, -1), (0.05, 0.15), (1.0, 2.0, 0.0), (120, 360), (0.0, 0.05)):
                xm = min(tend + xoff, 16 * 60 + 40)
                ie, d, rd, ix = S.gen_sweep(ny, o, h, l, c, sp, days, t_end, atr, hi_, lo_, t0, tend, xm, buf, tpr, dirs, wick)
                rec(("S", sym, kind, t0, tend, dirs, buf, tpr, xm, wick), ie, d, rd, np.full(len(ie), tpr), ix)
    return out

t = time.time()
A = run_dataset("ext"); B = run_dataset("gft")
print(f"fertig in {time.time()-t:.0f}s: ext {len(A)}, gft {len(B)}")
rows = []
for k, ms in A.items():
    if k in B:
        allm = ms + B[k]
        rows.append((min(m[0] for m in allm), k, allm))
rows.sort(key=lambda x: -x[0])
json.dump([(a, list(map(str, b)), c) for a, b, c in rows], open("scan8_epochs.json", "w"), default=float)
for th in (1.0, 1.1, 1.2, 1.3):
    print(f"min PF >= {th}: {sum(1 for r in rows if r[0] >= th)} von {len(rows)}")
for mn, k, allm in rows[:40]:
    s = " | ".join(f"PF{m[0]:.2f} WR{m[1]:.0f} R/J{m[2]:+.1f}" for m in allm)
    print(f"{str(k):<70s} {s} maxS {max(m[3] for m in allm)}")
