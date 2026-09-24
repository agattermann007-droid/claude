"""Langzeit-Scan: dasselbe Fade-Raster wie scan6_run3 auf 2006-2021 (Fremddaten), Epochen 2006-2013 und 2014-2021."""
import numpy as np, itertools, json, time, sys
import gext, gsig as G
gext.use_ext()
import scan6 as S
EP = np.datetime64("2014-01-01", "m").astype(np.int64)
res = []
t = time.time()
for sym in ("XAU", "NAS"):
    D, ny, days, t_end, atr = S.prep(sym)
    o, h, l, c, sp = D["o"], D["h"], D["l"], D["c"], D["sp"]
    for r0 in range(-360, 931, 30):
        for L in (30, 60, 90, 120, 180, 240):
            r1 = r0 + L
            if r1 > 16 * 60 + 10:
                continue
            for dirs, buf, tgt, tlen, xoff, (mn, mx) in itertools.product((1, -1), (0.3, 0.6, 1.0), (0, 1), (60, 120, 180), (120, 240),
                                                                        ((0.0, 99), (0.0, 0.6))):
                tend = r1 + tlen; xm = min(r1 + tlen + xoff, 16 * 60 + 40)
                if xm <= tend:
                    tend = xm - 5
                if tend <= r1:
                    continue
                ie, d, rd, tp, ix = S.gen_fade(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx)
                if len(ie) < 80:
                    continue
                R, *_ = G.simulate(sym, ie, d, rd, tp, ix)
                te = ny[ie]; a = te < EP
                if a.sum() < 40 or (~a).sum() < 40:
                    continue
                m1 = G.metrics(R[a], te[a]); m2 = G.metrics(R[~a], te[~a])
                res.append(dict(sym=sym, r0=r0, L=L, dirs=dirs, buf=buf, tgt=tgt, tlen=tlen, xoff=xoff, mx=mx,
                                pf_e1=m1["pf"], pf_e2=m2["pf"], wr_e1=m1["wr"], wr_e2=m2["wr"], ry_e1=m1["Ry"], ry_e2=m2["Ry"],
                                n_e1=m1["n"], n_e2=m2["n"], ms_e1=m1["maxS"], ms_e2=m2["maxS"]))
print(f"{len(res)} Varianten in {time.time()-t:.0f}s")
json.dump(res, open("scan7_long.json", "w"), default=float)
