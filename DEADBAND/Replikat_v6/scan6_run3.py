"""Scan 3: feines Fade-Raster ueber den ganzen Tag, beide Symbole/Richtungen; Robustheit ueber Nachbarn."""
import numpy as np, itertools, json, time
import gsig as G, scan6 as S

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
                isr = ny[ie] < S.SPLIT
                if isr.sum() < 40 or (~isr).sum() < 40:
                    continue
                mi = G.metrics(R[isr], ny[ie][isr]); mo = G.metrics(R[~isr], ny[ie][~isr])
                res.append(dict(sym=sym, r0=r0, L=L, dirs=dirs, buf=buf, tgt=tgt, tlen=tlen, xoff=xoff, mx=mx,
                                n_is=mi["n"], n_oos=mo["n"], wr_is=mi["wr"], wr_oos=mo["wr"], pf_is=mi["pf"], pf_oos=mo["pf"],
                                sh_is=mi["sharpe"], sh_oos=mo["sharpe"], ry_is=mi["Ry"], ry_oos=mo["Ry"], maxS=max(mi["maxS"], mo["maxS"])))
print(f"{len(res)} Varianten in {time.time()-t:.0f}s")
json.dump(res, open("scan6_res3b.json", "w"), default=float)
good = [r for r in res if r["pf_is"] >= 1.3 and r["pf_oos"] >= 1.3]
print("IS+OOS PF>=1.3:", len(good))
# Cluster: gleiche (sym, dirs, r0, L) -> Anzahl bestandener Varianten
from collections import Counter
cl = Counter((r["sym"], r["dirs"], r["r0"], r["L"]) for r in good)
tot = Counter((r["sym"], r["dirs"], r["r0"], r["L"]) for r in res)
rows = sorted(cl.items(), key=lambda x: -x[1])
print("Cluster (sym, dir, Rangebeginn, Laenge): bestanden / geprueft, bestes Paar")
for key, nb in rows[:40]:
    best = max((r for r in good if (r["sym"], r["dirs"], r["r0"], r["L"]) == key), key=lambda r: min(r["sh_is"], r["sh_oos"]))
    print(f"  {key}: {nb}/{tot[key]}  best: buf{best['buf']} tgt{best['tgt']} tlen{best['tlen']} xoff{best['xoff']} mx{best['mx']} "
          f"IS WR{best['wr_is']:.0f} PF{best['pf_is']:.2f} n{best['n_is']} | OOS WR{best['wr_oos']:.0f} PF{best['pf_oos']:.2f} n{best['n_oos']} maxS{best['maxS']}")
