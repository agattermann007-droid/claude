"""Scan 2: Fades in allen Sitzungen + Sweeps von Vortages-/Asia-Niveaus, beide Symbole, beide Richtungen."""
import numpy as np, itertools, json, time
import gsig as G, scan6 as S

res = []
t = time.time()
for sym in ("XAU", "NAS"):
    D, ny, days, t_end, atr = S.prep(sym)
    o, h, l, c, sp = D["o"], D["h"], D["l"], D["c"], D["sp"]
    ranges = [(-300, 120), (-300, 180), (0, 180), (120, 240), (180, 330), (240, 480), (330, 570), (420, 570), (480, 570),
              (510, 570), (540, 570), (570, 600), (570, 630), (600, 690), (720, 840), (780, 870)]
    for (r0, r1), dirs, buf, tgt, tlen, xoff, (mn, mx) in itertools.product(
            ranges, (1, -1), (0.1, 0.3, 0.6), (0, 1), (90, 180), (180, 360), ((0.0, 99), (0.0, 0.6), (0.2, 1.0))):
        tend = r1 + tlen; xm = min(r1 + xoff, 16 * 60 + 40)
        if xm <= tend:
            tend = xm - 5
        ie, d, rd, tp, ix = S.gen_fade(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx)
        if len(ie) < 60:
            continue
        R, *_ = G.simulate(sym, ie, d, rd, tp, ix)
        lbl = f"{sym} F r{r0}-{r1} d{dirs} buf{buf} tgt{tgt} te{tend} x{xm} rg{mn}-{mx}"
        mi, mo = S.split_metrics(R, ny[ie], lbl)
        res.append((lbl, mi, mo))
    for kind in ("nyday", "rth", "asia"):
        hi, lo = S.levels_prevday(sym, days, kind)
        wins = [(120, 330), (180, 480), (330, 570), (570, 690), (570, 840), (690, 900)] if kind != "asia" else [(120, 330), (180, 480), (330, 570), (570, 690)]
        for (t0, tend), dirs, buf, tpr, xoff, wick in itertools.product(wins, (1, -1), (0.05, 0.15), (1.0, 2.0, 0.0), (120, 360), (0.0, 0.05)):
            xm = min(tend + xoff, 16 * 60 + 40)
            ie, d, rd, ix = S.gen_sweep(ny, o, h, l, c, sp, days, t_end, atr, hi, lo, t0, tend, xm, buf, tpr, dirs, wick)
            if len(ie) < 60:
                continue
            R, *_ = G.simulate(sym, ie, d, rd, tpr, ix)
            lbl = f"{sym} S {kind} w{t0}-{tend} d{dirs} buf{buf} tp{tpr} x{xm} wk{wick}"
            mi, mo = S.split_metrics(R, ny[ie], lbl)
            res.append((lbl, mi, mo))
print(f"{len(res)} Varianten in {time.time()-t:.0f}s")
json.dump(res, open("scan6_res2.json", "w"), default=float)
good = [(a, b, c) for a, b, c in res if b.get("n", 0) >= 40 and c.get("n", 0) >= 40 and b["pf"] >= 1.3 and c["pf"] >= 1.3]
good.sort(key=lambda x: -min(x[1]["sharpe"], x[2]["sharpe"]))
print(f"IS und OOS PF >= 1,3: {len(good)}")
for a, b, c in good[:70]:
    print(f"{a:<62s} IS n{b['n']:4d} WR{b['wr']:5.1f} PF{b['pf']:5.2f} Sh{b['sharpe']:5.2f} R/J{b['Ry']:+6.1f} | OOS n{c['n']:4d} WR{c['wr']:5.1f} PF{c['pf']:5.2f} Sh{c['sharpe']:5.2f} R/J{c['Ry']:+6.1f} maxS{max(b['maxS'],c['maxS'])}")
