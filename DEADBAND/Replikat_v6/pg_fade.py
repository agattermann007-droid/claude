"""Fade-Signale mit Zusatzangaben fuer das Probability Grid (Signal-Kerze, Extrem des Fehlausbruchs, Range) und die
Grid-Merkmale je Signal. Die Signale sind identisch mit scan6.gen_fade (geprueft in pg_check)."""
import numpy as np
from numba import njit
import gsig as G, scan6 as S, cands as K, pgrid as PG


@njit(cache=True)
def gen_fade_info(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx):
    """wie scan6.gen_fade; zusaetzlich J (Signal-Kerze), EX (Extrem des Fehlausbruchs: Tief bei Long, Hoch bei Short),
    HH/LL (Range), GOAL, ST (Stop), ENT (Einstieg)."""
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); RD = np.zeros(n); TP = np.zeros(n); IX = np.zeros(n, np.int64)
    J = np.zeros(n, np.int64); EX = np.zeros(n); HH = np.zeros(n); LL = np.zeros(n); GL = np.zeros(n); STP = np.zeros(n)
    EN = np.zeros(n)
    m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + r0); e = np.searchsorted(ny, D * 1440 + r1)
        if e - s < (r1 - r0) // 5 * 0.6 or e >= ny.shape[0]:
            continue
        a = S._atr_at(t_end, atr, D * 1440 + r0)
        if not (a > 0):
            continue
        hh = h[s]; ll = l[s]
        for j in range(s, e):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        rng = hh - ll
        if rng < mn * a or rng > mx * a:
            continue
        te = np.searchsorted(ny, D * 1440 + tend); X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0]:
            continue
        ext_hi = hh; ext_lo = ll
        for j in range(e, te):
            if h[j] > ext_hi: ext_hi = h[j]
            if l[j] < ext_lo: ext_lo = l[j]
            d = 0
            if h[j] > hh and c[j] < hh and c[j] > ll:
                d = -1
            elif l[j] < ll and c[j] > ll and c[j] < hh:
                d = 1
            if d == 0:
                if c[j] > hh or c[j] < ll:
                    break
                continue
            if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                break
            B = j + 1
            if B >= X:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            st = ext_lo - buf * rng if d > 0 else ext_hi + buf * rng
            r = (ent - st) * d
            goal = 0.5 * (hh + ll) if tgt == 0 else (hh if d > 0 else ll)
            g = (goal - ent) * d
            if r > 0.0 and g > 0.0:
                IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = g / r; IX[m] = X
                J[m] = j; EX[m] = ext_lo if d > 0 else ext_hi; HH[m] = hh; LL[m] = ll; GL[m] = goal; STP[m] = st; EN[m] = ent
                m += 1
            break
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m], J[:m], EX[:m], HH[:m], LL[:m], GL[:m], STP[:m], EN[:m]


def fade_info(name):
    """Signale eines Fade-Moduls (Parameter aus cands.FADES) mit Zusatzangaben und virtuellem Ergebnis in R."""
    p = dict(K.FADES[name]); sym = p.pop("sym")
    r0, L, tlen, xoff, buf, tgt, dirs = p["r0"], p["L"], p["tlen"], p["xoff"], p["buf"], p["tgt"], p["dirs"]
    mx = p.get("mx", 0.6); mn = p.get("mn", 0.0)
    D, ny, days, t_end, atr = K._prep(sym)
    r1 = r0 + L; tend = r1 + tlen; xm = min(r1 + tlen + xoff, 16 * 60 + 40)
    if xm <= tend:
        tend = xm - 5
    out = gen_fade_info(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx)
    ie, d, rd, tp, ix, j, ex, hh, ll, goal, st, ent = out
    R, why, held, mfe, mae, iout = G.simulate(sym, ie, d, rd, tp, ix)
    return dict(name=name, sym=sym, ie=ie, d=d, rd=rd, tp=tp, ix=ix, j=j, ex=ex, hh=hh, ll=ll, goal=goal, st=st, ent=ent,
                R=R, why=why, held=held, mfe=mfe, mae=mae, iout=iout, t_entry=ny[ie], t_exit=ny[ix], xm=xm, tgt=tgt, buf=buf)


_PIV = {}


def pivots(sym, tf, length):
    """Pivot-Zustand und Schenkel je (Symbol, Zeitebene, Laenge) fuer den aktuell geladenen Datensatz (Cache je Datensatz)."""
    key = (id(G._D) if G._D is not None else 0, sym, tf, length)
    if key not in _PIV:
        D = G.data()[sym] if G._D is None else G._D[sym]
        t0, o, h, l, c, done_at = PG.tf_bars(D["ny"], D["o"], D["h"], D["l"], D["c"], tf)
        res = PG.lux_pivots(o, c, length)
        _PIV[key] = (t0, done_at, res)
    return _PIV[key]


def grid_features(fi, tf=5, length=20, maxpiv=1000, minlegs=30):
    """Grid-Merkmale je Signal (Spalten siehe pgrid.features)."""
    t0, done_at, (bias, piv_px, piv_bar, piv_bias, cur_px, cur_bar, lc, ld, ls, lb) = pivots(fi["sym"], tf, length)
    qbar = done_at[fi["j"]]
    return PG.features(qbar.astype(np.int64), fi["d"].astype(np.int64), fi["ex"], fi["goal"], fi["st"], fi["ent"],
                       bias, piv_px, piv_bar, cur_px, cur_bar, lc, ld, ls, lb, int(maxpiv), int(minlegs))
