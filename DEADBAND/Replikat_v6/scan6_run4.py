"""Scan 4: rollender Fade (mehrere Signale je Tag) je Sitzung, beide Symbole/Richtungen."""
import numpy as np, itertools, json, time
from collections import Counter
import gsig as G, scan6 as S
res = []
t = time.time()
sess = {"asia": (-300, 120, 180), "london": (180, 480, 540), "ny": (570, 930, 1000), "nyam": (570, 720, 1000), "nypm": (720, 930, 1000)}
for sym in ("XAU", "NAS"):
    D, ny, days, t_end, atr = S.prep(sym)
    o, h, l, c, sp = D["o"], D["h"], D["l"], D["c"], D["sp"]
    for (sn, (ts, tst, tl)), L, dirs, buf, tgt, hold, mx, maxper in itertools.product(
            sess.items(), (30, 60, 90, 120), (1, -1), (0.3, 0.6, 1.0), (0, 1), (60, 120, 240), (0.3, 0.6, 99.0), (1, 2, 3)):
        ie, d, rd, tp, ix = S.gen_rollfade(ny, o, h, l, c, sp, days, t_end, atr, ts, tst, L, buf, tgt, dirs, hold, tl, 0.0, mx, maxper)
        if len(ie) < 80:
            continue
        R, *_ = G.simulate(sym, ie, d, rd, tp, ix)
        isr = ny[ie] < S.SPLIT
        if isr.sum() < 40 or (~isr).sum() < 40:
            continue
        mi = G.metrics(R[isr], ny[ie][isr]); mo = G.metrics(R[~isr], ny[ie][~isr])
        res.append(dict(sym=sym, sess=sn, L=L, dirs=dirs, buf=buf, tgt=tgt, hold=hold, mx=mx, maxper=maxper,
                        n_is=mi["n"], n_oos=mo["n"], tpy=(mi["tpy"] + mo["tpy"]) / 2, wr_is=mi["wr"], wr_oos=mo["wr"],
                        pf_is=mi["pf"], pf_oos=mo["pf"], sh_is=mi["sharpe"], sh_oos=mo["sharpe"], ry_is=mi["Ry"], ry_oos=mo["Ry"],
                        maxS=max(mi["maxS"], mo["maxS"])))
print(f"{len(res)} Varianten in {time.time()-t:.0f}s")
json.dump(res, open("scan6_res4.json", "w"), default=float)
good = [r for r in res if r["pf_is"] >= 1.25 and r["pf_oos"] >= 1.25]
print("IS+OOS PF>=1.25:", len(good))
cl = Counter((r["sym"], r["sess"], r["dirs"], r["L"]) for r in good)
tot = Counter((r["sym"], r["sess"], r["dirs"], r["L"]) for r in res)
for key, nb in sorted(cl.items(), key=lambda x: -x[1])[:25]:
    cands = [r for r in good if (r["sym"], r["sess"], r["dirs"], r["L"]) == key]
    best = max(cands, key=lambda r: min(r["ry_is"], r["ry_oos"]))
    print(f"{key}: {nb}/{tot[key]} best buf{best['buf']} tgt{best['tgt']} hold{best['hold']} mx{best['mx']} per{best['maxper']} "
          f"{best['tpy']:.0f}/J | IS WR{best['wr_is']:.0f} PF{best['pf_is']:.2f} R/J{best['ry_is']:.1f} | OOS WR{best['wr_oos']:.0f} "
          f"PF{best['pf_oos']:.2f} R/J{best['ry_oos']:.1f} maxS{best['maxS']}")
