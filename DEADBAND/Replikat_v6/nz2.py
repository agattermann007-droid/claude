"""Noise-Area-Momentum v2 als generischer Strom: Pruefungen alle X Minuten, optional VWAP-Ausstieg."""
import numpy as np, gsig as G, sig5 as S5


def nz2(stream, every=30, first=600, last_entry=930, schluss=955, stop_mult=0.5, vwap_exit=False, k=1.0, tp=0.0):
    D = G.data()
    checks = tuple(range(first, last_entry + 1, every))
    z = S5.nz_days(D, "NAS", checks=checks, last_entry=last_entry, schluss=schluss, stops=(stop_mult,), k=k)
    d = D["NAS"]; ny = d["ny"]; c = d["c"]; h = d["h"]; l = d["l"]; v = d["v"]
    day = z["day"]; em = z["em"]; i5 = z["i5"]; close = z["close"]; UB = z["UB"]; dist = z["dist"][:, 0]
    # VWAP je Tag ab 9:30 bis zur Pruefung (typischer Preis, Tick-Volumen)
    vw_at = np.full(len(day), np.nan)
    if vwap_exit:
        for q in range(len(day)):
            dd = day[q]; e = np.searchsorted(ny, dd * 1440 + em[q]); s = np.searchsorted(ny, dd * 1440 + 570)
            if e > s:
                tpx = (h[s:e] + l[s:e] + c[s:e]) / 3.0; w = np.maximum(v[s:e], 1.0)
                vw_at[q] = float((tpx * w).sum() / w.sum())
    import scan6 as SC
    o = d["o"]; sp = d["sp"]
    ie, dd_, rd, ix, te = [], [], [], [], []
    ud = np.unique(day)
    for dy in ud:
        rows = np.nonzero(day == dy)[0]
        eod = np.searchsorted(ny, dy * 1440 + schluss)
        busy = -1
        for a_ in range(len(rows)):
            q = rows[a_]
            if i5[q] <= busy:
                continue
            if em[q] > last_entry or not (close[q] > UB[q]) or dist[q] <= 0:
                continue
            X = eod
            for b_ in range(a_ + 1, len(rows)):
                r = rows[b_]
                lvl = max(UB[r], vw_at[r]) if vwap_exit and np.isfinite(vw_at[r]) else UB[r]
                if close[r] < lvl:
                    X = i5[r]; break
            if X <= i5[q]:
                continue
            ent = o[i5[q]] + sp[i5[q]]
            jx, why = SC._first_exit(o, h, l, sp, i5[q], X, 1, ent - dist[q], ent + tp * dist[q] if tp > 0 else 0.0, 1)
            busy = jx
            ie.append(i5[q]); dd_.append(1); rd.append(dist[q]); ix.append(X); te.append(ny[i5[q]])
    ie = np.array(ie); dd_ = np.array(dd_); rd = np.array(rd); ix = np.array(ix)
    blk = dict(str=stream, sym=np.full(len(ie), 1), dir=dd_, t_entry=ny[ie], rd=rd, tp=np.full(len(ie), tp), t_exit=ny[ix], w=1.0)
    return blk, (ie, dd_, rd, tp, ix)


if __name__ == "__main__":
    import scan6 as SC
    for every in (60, 30):
        for vx in (False, True):
            for sm in (0.35, 0.5, 0.75):
                b, (ie, d, rd, tp, ix) = nz2(0, every=every, vwap_exit=vx, stop_mult=sm)
                R, *_ = G.simulate("NAS", ie, d, rd, tp, ix)
                te = b["t_entry"]; isr = te < SC.SPLIT
                mi = G.metrics(R[isr], te[isr]); mo = G.metrics(R[~isr], te[~isr])
                print(f"alle {every} min VWAP {vx!s:5s} Stop {sm}: n {len(R)} ({mi['tpy']:.0f}+{mo['tpy']:.0f}/J) | IS WR{mi['wr']:.0f} PF{mi['pf']:.2f} R/J{mi['Ry']:+.1f} "
                      f"mS{mi['maxS']} | OOS WR{mo['wr']:.0f} PF{mo['pf']:.2f} R/J{mo['Ry']:+.1f} mS{mo['maxS']}")
