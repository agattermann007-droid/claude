"""RSI21-Labor: Einzelsignal-Simulation (ohne Plaetze) fuer Einstiegsvarianten: Markt vs. Limit-Rueckzug.

Je Signal: Markt-Einstieg am Open der Signal-M5-Kerze ODER Limit x R unter (long) dem Open, gueltig N M5-Kerzen.
Nach der Fuellung Stop/Ziel in R vom Fuellkurs (R = Stop-Abstand des Signals), Zeit-Exit wie EA (Kerzen ab Signal).
Kein Wochenend-Schluss, kein Swap - nur zum Vergleich der Einstiege auf identischer Signalmenge."""
import numpy as np
from numba import njit


@njit(cache=True)
def sim_lim(o, h, l, c, sp, ie, d, rd, tpr, lim_off, lim_bars, exitbars, comm_px):
    n = ie.shape[0]
    R = np.full(n, np.nan); filled = np.zeros(n, np.bool_); jx = np.zeros(n, np.int64)
    for t in range(n):
        i = ie[t]; dd = d[t]; r = rd[t]
        ref = o[i] + (sp[i] if dd > 0 else 0.0)
        j = i
        ent = 0.0
        if lim_off <= 0.0:
            ent = ref
            filled[t] = True
        else:
            lim = ref - dd * lim_off * r
            while j < o.shape[0] and j - i < lim_bars:
                if dd > 0:
                    px = o[j] + sp[j]
                    if px <= lim:
                        ent = px; filled[t] = True; break
                    if l[j] + sp[j] <= lim:
                        ent = lim; filled[t] = True; break
                else:
                    if o[j] >= lim:
                        ent = o[j]; filled[t] = True; break
                    if h[j] >= lim:
                        ent = lim; filled[t] = True; break
                j += 1
        if not filled[t]:
            continue
        sl = ent - dd * r
        tp = ent + dd * tpr[t] * r
        first = True
        while True:
            if j >= o.shape[0] - 1 or j - i >= exitbars:
                jj = min(j, o.shape[0] - 1)
                px = c[jj] + (sp[jj] if dd < 0 else 0.0)
                R[t] = ((px - ent) * dd - comm_px) / r; jx[t] = jj
                break
            lo = l[j]; hi = h[j]; s_ = sp[j]
            if dd > 0:
                hit_sl = lo <= sl
                hit_tp = hi >= tp
            else:
                hit_sl = hi + s_ >= sl
                hit_tp = lo + s_ <= tp
            if first and lim_off > 0.0:
                # Fuellkerze: nur der Teil nach der Fuellung zaehlt - vorsichtig: Stop zaehlt, Ziel nicht
                hit_tp = False
            first = False
            if hit_sl:
                px = sl
                if dd > 0 and o[j] < sl:
                    px = o[j]
                if dd < 0 and o[j] + s_ > sl:
                    px = o[j] + s_
                R[t] = ((px - ent) * dd - comm_px) / r; jx[t] = j
                break
            if hit_tp:
                R[t] = ((tp - ent) * dd - comm_px) / r; jx[t] = j
                break
            j += 1
    return R, filled, jx
