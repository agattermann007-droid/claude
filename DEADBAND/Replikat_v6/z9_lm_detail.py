"""Stufe 8.10: Trend-Day LM - Signalebene je Jahr (GFT 2022-25, Fremddaten 2005-21) und Kostenstress (Schlupf je Seite)."""
import json, numpy as np
import gsig as G, gext, cands as K, scan6 as S, n9sig as N9

ARGS = (840, 955, 0, 0.75, 0, 0.3, 0.0, 1, 960)
out = {}
for ds in ("gft", "ext"):
    G._D = gext.data_ext() if ds == "ext" else None
    if ds == "gft":
        G.data()
    K._CACHE.clear()
    D, ny, days, t_end, atr = S.prep("NAS")
    ie, d, rd, tp, ix = N9.gen_lastmom(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, *ARGS)
    R, why, held, mfe, mae, iout = G.simulate("NAS", ie, d, rd, tp, ix)
    yr = (ny[ie] // 1440).astype("datetime64[D]").astype("datetime64[Y]").astype(int) + 1970
    rows = {}
    for y in np.unique(yr):
        r = R[yr == y]
        pos = r[r > 0].sum(); neg = -r[r < 0].sum()
        rows[int(y)] = dict(n=int(len(r)), wr=float((r > 0).mean() * 100), pf=float(pos / neg) if neg > 0 else 9.9, sumR=float(r.sum()))
    stress = {}
    px = D["o"][ie]
    for slip in (0.0, 1.0, 2.0, 4.0):              # NAS-Punkte je Seite bei Kurs 20 000 (proportional zum Kursniveau)
        r = R - 2.0 * slip * (px / 20000.0) / rd
        pos = r[r > 0].sum(); neg = -r[r < 0].sum()
        stress[slip] = dict(pf=float(pos / neg), avgR=float(r.mean()), wr=float((r > 0).mean() * 100))
    out[ds] = dict(jahre=rows, stress=stress, stop_median=float(np.median(rd)))
    print(f"=== {ds}: {len(R)} Trades, Stop Median {np.median(rd):.1f} Pkt")
    for y, v in rows.items():
        print(f"  {y}: n{v['n']:3d} WR{v['wr']:4.0f} PF{v['pf']:5.2f} R{v['sumR']:+6.1f}")
    for k, v in stress.items():
        print(f"  Schlupf {k:.0f} Pkt/Seite (bei 20000): PF {v['pf']:.2f}, R/Trade {v['avgR']:+.3f}, WR {v['wr']:.0f}")
json.dump(out, open("ergebnisse/z9_lm_detail.json", "w"), indent=1)
