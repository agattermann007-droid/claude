"""Systematischer Scanner fuer Intraday-Muster mit In-/Out-of-Sample-Trennung.
Familien: B = Range-Ausbruch, F = Fehlausbruch (Fade zur Range-Mitte), M = Tageszeit-Momentum/-Umkehr.
Zeiten in NY-Minuten relativ zum NY-Kalendertag (negativ = Vortag)."""
import numpy as np, itertools, json, sys, time
from numba import njit
import gsig as G

SPLIT = np.datetime64("2024-07-01", "m").astype(np.int64)     # NY-Minute: IS davor, OOS danach


def daily_atr(sym, n=14):
    """ATR(n) der Servertag-Kerzen, je NY-Tag der Wert des letzten ABGESCHLOSSENEN Servertags (17:00 NY)."""
    D = G.data()[sym]; d1 = D["d1"]
    h, l, c = d1["h"], d1["l"], d1["c"]
    tr = np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1])
    tr = np.r_[h[0] - l[0], tr]
    atr = np.convolve(tr, np.ones(n) / n, mode="full")[:len(tr)]
    atr[:n - 1] = np.nan
    t_end = d1["t"] + 1440                      # Servertag endet 17:00 NY
    return t_end, atr


@njit(cache=True)
def _atr_at(t_end, atr, t):
    k = np.searchsorted(t_end, t, side="right") - 1
    if k < 0:
        return np.nan
    return atr[k]


@njit(cache=True)
def gen_break(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, stopmode, stopk, dirs, mn, mx):
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); RD = np.zeros(n); IX = np.zeros(n, np.int64); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + r0); e = np.searchsorted(ny, D * 1440 + r1)
        if e - s < (r1 - r0) // 5 * 0.6 or e >= ny.shape[0]:
            continue
        a = _atr_at(t_end, atr, D * 1440 + r0)
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
        for j in range(e, te):
            d = 0
            if c[j] > hh:
                d = 1
            elif c[j] < ll:
                d = -1
            if d == 0:
                continue
            if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                break
            B = j + 1
            if B >= X:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            if stopmode == 0:
                st = ll if d > 0 else hh
            elif stopmode == 1:
                st = 0.5 * (hh + ll)
            else:
                st = ent - d * stopk * a
            r = (ent - st) * d
            if r > 0.0:
                IE[m] = B; DD[m] = d; RD[m] = r; IX[m] = X; m += 1
            break
    return IE[:m], DD[:m], RD[:m], IX[:m]


@njit(cache=True)
def gen_fade(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx):
    """Fehlausbruch: Kerze handelt ausserhalb der Range, schliesst wieder innen -> Gegenrichtung; Stop Extrem + buf*Range;
    Ziel: tgt 0 = Range-Mitte, 1 = Gegenseite."""
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); RD = np.zeros(n); TP = np.zeros(n); IX = np.zeros(n, np.int64); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + r0); e = np.searchsorted(ny, D * 1440 + r1)
        if e - s < (r1 - r0) // 5 * 0.6 or e >= ny.shape[0]:
            continue
        a = _atr_at(t_end, atr, D * 1440 + r0)
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
                    break                      # echter Ausbruch: kein Fade mehr
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
                IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = g / r; IX[m] = X; m += 1
            break
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_mom(ny, o, h, l, c, sp, days, t_end, atr, t0, t1, xm, k, rev, stopk, dirs):
    """Tageszeit-Momentum: Bewegung von t0 bis t1 >= k*ATR -> Einstieg t1 in (rev=0) bzw. gegen (rev=1) die Bewegung,
    Stop stopk*ATR, Ausstieg xm."""
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); RD = np.zeros(n); IX = np.zeros(n, np.int64); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + t0); e = np.searchsorted(ny, D * 1440 + t1)
        X = np.searchsorted(ny, D * 1440 + xm)
        if s >= ny.shape[0] or e >= ny.shape[0] or X >= ny.shape[0] or e <= s or X <= e:
            continue
        if ny[s] - (D * 1440 + t0) > 30 or ny[e] - (D * 1440 + t1) > 10:
            continue
        a = _atr_at(t_end, atr, D * 1440 + t0)
        if not (a > 0):
            continue
        mv = o[e] - o[s]
        if abs(mv) < k * a:
            continue
        d = 1 if mv > 0 else -1
        if rev == 1:
            d = -d
        if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
            continue
        IE[m] = e; DD[m] = d; RD[m] = stopk * a; IX[m] = X; m += 1
    return IE[:m], DD[:m], RD[:m], IX[:m]


def split_metrics(R, te, label):
    isr = te < SPLIT
    mi = G.metrics(R[isr], te[isr], label + " IS") if isr.sum() else dict(n=0)
    mo = G.metrics(R[~isr], te[~isr], label + " OOS") if (~isr).sum() else dict(n=0)
    return mi, mo


def prep(sym):
    D = G.data()[sym]
    ny = D["ny"]
    days = np.unique(ny // 1440)
    days = days[((days + 4) % 7 >= 1) & ((days + 4) % 7 <= 5)]      # Mo-Fr (NY)
    t_end, atr = daily_atr(sym)
    return D, ny, days, t_end, atr


@njit(cache=True)
def gen_sweep(ny, o, h, l, c, sp, days, t_end, atr, lvl_hi, lvl_lo, t0, tend, xm, buf, tpr, dirs, wick):
    """Sweep & Reclaim eines vorgegebenen Niveaus je Tag (lvl_hi/lvl_lo, z. B. Vortageshoch/-tief):
    im Fenster [t0, tend) handelt eine Kerze ueber lvl_hi und schliesst darunter (Docht >= wick*ATR) -> Short
    (spiegelbildlich Long unter lvl_lo). Stop Extrem + buf*ATR, Ziel tpr R (0 = keins), Ausstieg xm."""
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); RD = np.zeros(n); IX = np.zeros(n, np.int64); m = 0
    for q in range(n):
        D = days[q]
        hi = lvl_hi[q]; lo = lvl_lo[q]
        if not (hi > 0) or not (lo > 0):
            continue
        s = np.searchsorted(ny, D * 1440 + t0); te = np.searchsorted(ny, D * 1440 + tend)
        X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0] or s >= te:
            continue
        a = _atr_at(t_end, atr, D * 1440 + t0)
        if not (a > 0):
            continue
        done = False
        for j in range(s, te):
            if c[j] > hi or c[j] < lo:
                break                                    # Schluss jenseits = echter Ausbruch
            d = 0
            if h[j] > hi and (h[j] - max(o[j], c[j])) >= wick * a:
                d = -1
            elif l[j] < lo and (min(o[j], c[j]) - l[j]) >= wick * a:
                d = 1
            if d == 0:
                continue
            if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                break
            B = j + 1
            if B >= X:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            st = (l[j] - buf * a) if d > 0 else (h[j] + buf * a)
            r = (ent - st) * d
            if r > 0.0:
                IE[m] = B; DD[m] = d; RD[m] = r; IX[m] = X; m += 1
            break
    return IE[:m], DD[:m], RD[:m], IX[:m]


def levels_prevday(sym, days, kind="nyday"):
    """Vortages-Hoch/-Tief je NY-Tag: kind nyday = NY-Kalendertag 0-24 Uhr, rth = 9:30-16:00 NY, asia = 19:00-02:00."""
    D = G.data()[sym]; ny = D["ny"]; h = D["h"]; l = D["l"]
    hi = np.full(len(days), np.nan); lo = np.full(len(days), np.nan)
    for q, dy in enumerate(days):
        if kind == "nyday":
            a0, a1 = (dy - 1) * 1440, dy * 1440
            # letzter Handelstag davor (Wochenende ueberspringen)
            k = 1
            while k < 5:
                a0, a1 = (dy - k) * 1440, (dy - k + 1) * 1440
                s = np.searchsorted(ny, a0); e = np.searchsorted(ny, a1)
                if e - s > 100:
                    break
                k += 1
        elif kind == "rth":
            k = 1
            while k < 5:
                a0, a1 = (dy - k) * 1440 + 570, (dy - k) * 1440 + 960
                s = np.searchsorted(ny, a0); e = np.searchsorted(ny, a1)
                if e - s > 60:
                    break
                k += 1
        else:
            a0, a1 = dy * 1440 - 300, dy * 1440 + 120
        s = np.searchsorted(ny, a0); e = np.searchsorted(ny, a1)
        if e - s > 20:
            hi[q] = h[s:e].max(); lo[q] = l[s:e].min()
    return hi, lo


@njit(cache=True)
def gen_rollfade(ny, o, h, l, c, sp, days, t_end, atr, t_start, t_stop, L, buf, tgt, dirs, hold, t_last, mn, mx, maxper):
    """Rollender Fade: je Kerze j in [t_start, t_stop) Range = Hoch/Tief der vorigen L Minuten (ohne j).
    Docht unter das Tief und Schluss wieder innen -> Long (spiegelbildlich Short). Stop Extrem - buf*Range,
    Ziel Mitte (tgt 0) oder Gegenseite (1), Ausstieg nach hold Minuten, spaetestens t_last. Nur eine Position je
    Strom: naechstes Signal erst nach dem Ausstieg. Hoechstens maxper Signale je Tag."""
    n = days.shape[0]
    cap = n * max(maxper, 1)
    IE = np.zeros(cap, np.int64); DD = np.zeros(cap, np.int64); RD = np.zeros(cap); TP = np.zeros(cap); IX = np.zeros(cap, np.int64); m = 0
    for q in range(n):
        D = days[q]
        a = _atr_at(t_end, atr, D * 1440 + t_start)
        if not (a > 0):
            continue
        s = np.searchsorted(ny, D * 1440 + t_start); e = np.searchsorted(ny, D * 1440 + t_stop)
        XL = np.searchsorted(ny, D * 1440 + t_last)
        if XL >= ny.shape[0]:
            continue
        busy = -1; cnt = 0
        for j in range(s, e):
            if j <= busy or cnt >= maxper:
                continue
            t = ny[j]
            k0 = np.searchsorted(ny, t - L)
            if j - k0 < L // 5 * 0.6 or k0 >= j:
                continue
            hh = h[k0]; ll = l[k0]
            for u in range(k0, j):
                if h[u] > hh: hh = h[u]
                if l[u] < ll: ll = l[u]
            rng = hh - ll
            if rng <= 0.0 or rng < mn * a or rng > mx * a:
                continue
            d = 0
            if l[j] < ll and c[j] > ll and c[j] < hh:
                d = 1
            elif h[j] > hh and c[j] < hh and c[j] > ll:
                d = -1
            if d == 0 or (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                continue
            B = j + 1
            X = np.searchsorted(ny, t + 5 + hold)
            if X > XL:
                X = XL
            if B >= X:
                continue
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            st = (l[j] - buf * rng) if d > 0 else (h[j] + buf * rng)
            r = (ent - st) * d
            goal = 0.5 * (hh + ll) if tgt == 0 else (hh if d > 0 else ll)
            g = (goal - ent) * d
            if r > 0.0 and g > 0.0:
                IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = g / r; IX[m] = X; m += 1
                busy = X; cnt += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def _first_exit(o, h, l, sp, B, X, d, st, tpx, tpdelay):
    """Erster Ausstieg eines Trades ab Kerze B: Rueckgabe (Index, Grund 1 Stop / 2 Ziel / 0 Zeit)."""
    for j in range(B, X):
        s_ = sp[j]
        if d > 0:
            if l[j] <= st:
                return j, 1
            if tpx > 0 and h[j] >= tpx and j - B >= tpdelay:
                return j, 2
        else:
            if h[j] + s_ >= st:
                return j, 1
            if tpx > 0 and l[j] + s_ <= tpx and j - B >= tpdelay:
                return j, 2
    return X, 0


@njit(cache=True)
def gen_fade_x(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx, maxper, sar, sar_tp, sar_stopfrac):
    """Fade mit (a) weiteren Fades derselben Range nach dem Ausstieg (maxper) und (b) optional Umkehr (sar=1):
    wird der Fade ausgestoppt, Einstieg in Ausbruchsrichtung an der naechsten Kerze, Stop = Range-Mitte +/- sar_stopfrac*Range
    (vom Einstieg gesehen hinter der Range-Kante), Ziel sar_tp R, Ausstieg xm. Rueckgabe mit Art (0 Fade, 1 Umkehr)."""
    n = days.shape[0]
    cap = n * (maxper + 2)
    IE = np.zeros(cap, np.int64); DD = np.zeros(cap, np.int64); RD = np.zeros(cap); TP = np.zeros(cap); IX = np.zeros(cap, np.int64)
    KD = np.zeros(cap, np.int64); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + r0); e = np.searchsorted(ny, D * 1440 + r1)
        if e - s < (r1 - r0) // 5 * 0.6 or e >= ny.shape[0]:
            continue
        a = _atr_at(t_end, atr, D * 1440 + r0)
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
        ext_hi = hh; ext_lo = ll; cnt = 0; j = e
        while j < te and cnt < maxper:
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
                j += 1
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
            if not (r > 0.0 and g > 0.0):
                break
            IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = g / r; IX[m] = X; KD[m] = 0; m += 1
            cnt += 1
            jx, why = _first_exit(o, h, l, sp, B, X, d, st, goal, 1)
            if why == 1 and sar == 1:
                B2 = jx + 1
                if B2 < X:
                    d2 = -d
                    ent2 = o[B2] + (sp[B2] if d2 > 0 else 0.0)
                    edge = hh if d2 > 0 else ll
                    st2 = edge - d2 * sar_stopfrac * rng
                    r2 = (ent2 - st2) * d2
                    if r2 > 0.0:
                        IE[m] = B2; DD[m] = d2; RD[m] = r2; TP[m] = sar_tp; IX[m] = X; KD[m] = 1; m += 1
                break                               # nach Umkehr bzw. Stop: Tag fertig
            if why == 1:
                break
            j = jx + 1                              # weitere Fades erst nach dem Ausstieg
            ext_hi = hh; ext_lo = ll
            for u in range(e, j):
                if h[u] > ext_hi: ext_hi = h[u]
                if l[u] < ext_lo: ext_lo = l[u]
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m], KD[:m]
