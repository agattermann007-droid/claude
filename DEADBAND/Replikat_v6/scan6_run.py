"""Grober Scan aller Familien auf beiden Symbolen; Auswahl nur mit guter IS- UND OOS-Leistung."""
import numpy as np, itertools, json, time
import gsig as G, scan6 as S

res = []
t = time.time()
for sym in ("XAU", "NAS"):
    D, ny, days, t_end, atr = S.prep(sym)
    o, h, l, c, sp = D["o"], D["h"], D["l"], D["c"], D["sp"]
    # --- B: Range-Ausbruch
    ranges = [(-300, 120), (-420, 180), (0, 180), (120, 180), (180, 240), (240, 330), (330, 570), (570, 600), (570, 630), (570, 660), (480, 570)]
    for (r0, r1), dirs, (sm, sk), tp, xoff, (mn, mx) in itertools.product(
            ranges, (1, -1), ((0, 0), (1, 0), (2, 0.5)), (1.0, 2.0, 0.0), (240, 600), ((0.0, 99), (0.0, 0.5))):
        tend = r1 + 180; xm = min(r1 + xoff, 16 * 60 + 40)
        if xm <= tend:
            tend = xm - 5
        ie, d, rd, ix = S.gen_break(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, sm, sk, dirs, mn, mx)
        if len(ie) < 60:
            continue
        R, *_ = G.simulate(sym, ie, d, rd, tp, ix)
        lbl = f"{sym} B r{r0}-{r1} d{dirs} st{sm}/{sk} tp{tp} x{xm} rg{mn}-{mx}"
        mi, mo = S.split_metrics(R, ny[ie], lbl)
        res.append((lbl, mi, mo))
    # --- F: Fehlausbruch
    for (r0, r1), dirs, buf, tgt, xoff, (mn, mx) in itertools.product(
            ranges, (1, -1), (0.1, 0.3), (0, 1), (180, 480), ((0.0, 99), (0.0, 0.6))):
        tend = r1 + 180; xm = min(r1 + xoff, 16 * 60 + 40)
        if xm <= tend:
            tend = xm - 5
        ie, d, rd, tp, ix = S.gen_fade(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx)
        if len(ie) < 60:
            continue
        R, *_ = G.simulate(sym, ie, d, rd, tp, ix)
        lbl = f"{sym} F r{r0}-{r1} d{dirs} buf{buf} tgt{tgt} x{xm} rg{mn}-{mx}"
        mi, mo = S.split_metrics(R, ny[ie], lbl)
        res.append((lbl, mi, mo))
    # --- M: Tageszeit-Momentum / -Umkehr
    moms = [(-420, 180), (-420, 570), (-60, 180), (180, 300), (570, 600), (570, 630), (570, 660), (600, 720), (720, 840), (840, 900), (900, 930)]
    for (t0, t1), rev, k, stopk, xoff, dirs in itertools.product(moms, (0, 1), (0.1, 0.25, 0.5), (0.3, 0.6), (30, 120, 360), (1, -1)):
        xm = min(t1 + xoff, 16 * 60 + 40)
        if xm <= t1:
            continue
        ie, d, rd, ix = S.gen_mom(ny, o, h, l, c, sp, days, t_end, atr, t0, t1, xm, k, rev, stopk, dirs)
        if len(ie) < 60:
            continue
        R, *_ = G.simulate(sym, ie, d, rd, 0.0, ix)
        lbl = f"{sym} M t{t0}-{t1} rev{rev} k{k} st{stopk} x{xm} d{dirs}"
        mi, mo = S.split_metrics(R, ny[ie], lbl)
        res.append((lbl, mi, mo))
print(f"{len(res)} Varianten in {time.time()-t:.0f}s")
json.dump([(a, b, c) for a, b, c in res], open("scan6_res.json", "w"), default=float)
good = [(a, b, c) for a, b, c in res if b.get("n", 0) >= 40 and c.get("n", 0) >= 40 and b["pf"] >= 1.25 and c["pf"] >= 1.25]
good.sort(key=lambda x: -min(x[1]["sharpe"], x[2]["sharpe"]))
print(f"IS und OOS PF >= 1,25: {len(good)}")
for a, b, c in good[:60]:
    print(f"{a:<58s} IS n{b['n']:4d} WR{b['wr']:5.1f} PF{b['pf']:5.2f} Sh{b['sharpe']:5.2f} R/J{b['Ry']:+6.1f} | OOS n{c['n']:4d} WR{c['wr']:5.1f} PF{c['pf']:5.2f} Sh{c['sharpe']:5.2f} R/J{c['Ry']:+6.1f} maxS{max(b['maxS'],c['maxS'])}")
