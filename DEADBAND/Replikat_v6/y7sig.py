"""V7-Forschung: Signal-Generatoren fuer die YouTube-Ideen (Oktober 2026).
Zeit = NY-Minuten seit Epoche (wie gsig/scan6). Einstieg am Open der Kerze B, Ausstieg am Open der Kerze X oder an
Stop/Ziel (gsig.simulate, Ziel frühestens ab der zweiten Kerze = 130-s-Regel).
Rueckgabe je Generator: ie, d, rd, tp (Ziel in R, 0 = keins), ix.

A gap_fade   NAS-Eroeffnungsluecke 9:30 gegen den Vortagesschluss 16:00 schliessen
B fade_p1    Fade-Modul mit 'Turtle Soup Plus One' (Wiedereintritt nach Schluss ausserhalb der Range)
C vwap_fade  Rueckkehr von VWAP +- k Sigma (Sitzung ab 9:30) zur Mitte
D lhm        letzte halbe Stunde in Richtung der ersten halben Stunde (Gao/Han/Li/Zhou)
E spike_fade Spitze der 8:30-Kerze (Termine) gegenlaeufig handeln
"""
import numpy as np
from numba import njit


@njit(cache=True)
def _atr_at(t_end, atr, t):
    k = np.searchsorted(t_end, t, side="right") - 1
    if k < 0:
        return np.nan
    return atr[k]


@njit(cache=True)
def rth_levels(ny, o, h, l, c, days):
    """je NY-Tag: Eroeffnung 9:30 (Open der Kerze 9:30), Schluss 16:00 (Close der Kerze 15:55), RTH-Hoch/-Tief.
    NaN, wenn die Kerze fehlt."""
    n = days.shape[0]
    op = np.full(n, np.nan); cl = np.full(n, np.nan); hi = np.full(n, np.nan); lo = np.full(n, np.nan)
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + 570); e = np.searchsorted(ny, D * 1440 + 960)
        if s >= ny.shape[0] or e <= s or ny[s] != D * 1440 + 570 or ny[e - 1] != D * 1440 + 955:
            continue
        op[q] = o[s]; cl[q] = c[e - 1]
        hh = h[s]; ll = l[s]
        for j in range(s, e):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        hi[q] = hh; lo[q] = ll
    return op, cl, hi, lo


@njit(cache=True)
def gap_fade(ny, o, h, l, c, sp, days, t_end, atr, op, cl, hi, lo,
             e0, xm, gmin, gmax, inside, stopmode, stopk, tgtfrac, dirs):
    """A: Luecke = Eroeffnung 9:30 - Schluss 16:00 des letzten Handelstags (Vortag mit RTH-Daten).
    gmin <= |Luecke|/ATR14 <= gmax; inside=1: Eroeffnung innerhalb der Vortages-RTH-Range.
    Einstieg Open der Kerze e0 (NY-Minute), Richtung zum Vortagesschluss; uebersprungen, wenn die Luecke bis dahin
    schon zu tgtfrac geschlossen ist. Stop: stopmode 0 = stopk x |Luecke| ab Einstieg, 1 = stopk x ATR, 2 = Extrem seit
    9:30 + stopk x |Luecke|. Ziel: tgtfrac der Luecke (1 = Vortagesschluss). Ausstieg xm."""
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); RD = np.zeros(n); TP = np.zeros(n); IX = np.zeros(n, np.int64); m = 0
    for q in range(1, n):
        if np.isnan(op[q]) or np.isnan(cl[q - 1]):
            continue
        if days[q] - days[q - 1] > 4:
            continue
        D = days[q]
        a = _atr_at(t_end, atr, D * 1440 + 570)
        if not (a > 0):
            continue
        g = op[q] - cl[q - 1]
        ag = abs(g)
        if ag < gmin * a or ag > gmax * a or ag <= 0.0:
            continue
        if inside == 1 and (op[q] > hi[q - 1] or op[q] < lo[q - 1]):
            continue
        d = -1 if g > 0 else 1
        if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
            continue
        s = np.searchsorted(ny, D * 1440 + 570)
        B = np.searchsorted(ny, D * 1440 + e0); X = np.searchsorted(ny, D * 1440 + xm)
        if B >= ny.shape[0] or X >= ny.shape[0] or ny[B] != D * 1440 + e0 or X <= B:
            continue
        goal = op[q] - g * tgtfrac
        # bis zum Einstieg schon geschlossen?
        filled = False
        exh = op[q]; exl = op[q]
        for j in range(s, B):
            if h[j] > exh: exh = h[j]
            if l[j] < exl: exl = l[j]
            if (d > 0 and h[j] >= goal) or (d < 0 and l[j] + sp[j] <= goal):
                filled = True
        if filled:
            continue
        ent = o[B] + (sp[B] if d > 0 else 0.0)
        if stopmode == 0:
            r = stopk * ag
        elif stopmode == 1:
            r = stopk * a
        else:
            st = (exl - stopk * ag) if d > 0 else (exh + stopk * ag)
            r = (ent - st) * d
        gg = (goal - ent) * d
        if r > 0.0 and gg > 0.0:
            IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = gg / r; IX[m] = X; m += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def fade_p1(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx, nb, only_extra):
    """B: wie scan6.gen_fade, aber nach einem Schluss ausserhalb der Range bleibt das Modul nb Kerzen lang scharf:
    schliesst eine dieser Kerzen wieder innerhalb, ist das ein Fehlausbruch (Turtle Soup Plus One) -> Fade.
    Stop hinter dem Extrem seit Range-Ende + buf x Range. only_extra=1: nur die zusaetzlichen Signale."""
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
        outside = 0          # +1 Schluss ueber der Range, -1 darunter, 0 innen
        left = 0
        for j in range(e, te):
            if h[j] > ext_hi: ext_hi = h[j]
            if l[j] < ext_lo: ext_lo = l[j]
            d = 0
            extra = False
            inside_close = c[j] < hh and c[j] > ll
            if outside == 0:
                if h[j] > hh and inside_close:
                    d = -1
                elif l[j] < ll and inside_close:
                    d = 1
                elif c[j] > hh:
                    outside = 1; left = nb
                elif c[j] < ll:
                    outside = -1; left = nb
            else:
                if inside_close:
                    d = -outside; extra = True
                else:
                    left -= 1
            if d == 0:
                if outside != 0 and left < 0:
                    break
                if outside != 0 and nb == 0:
                    break
                continue
            if only_extra == 1 and not extra:
                break
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
def vwap_fade(ny, o, h, l, c, v, sp, days, t_end, atr, t0, t1, xm, k, buf, tgtmode, dirs, conf):
    """C: VWAP ab 9:30 (typischer Preis x Tickvolumen) mit Sigma = volumengewichtete Standardabweichung.
    Im Fenster [t0, t1): conf=0 Schluss jenseits VWAP +- k Sigma -> Gegenrichtung; conf=1 erst wenn eine Kerze nach dem
    Ueberschiessen wieder innerhalb schliesst. Stop: Extrem seit Ueberschiessen + buf x ATR. Ziel: tgtmode 0 VWAP,
    1 = halber Weg zum VWAP. Ein Signal je Tag, Ausstieg xm."""
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); RD = np.zeros(n); TP = np.zeros(n); IX = np.zeros(n, np.int64); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + 570)
        e = np.searchsorted(ny, D * 1440 + t1); X = np.searchsorted(ny, D * 1440 + xm)
        if s >= ny.shape[0] or X >= ny.shape[0] or ny[s] != D * 1440 + 570:
            continue
        a = _atr_at(t_end, atr, D * 1440 + 570)
        if not (a > 0):
            continue
        pv = 0.0; vv = 0.0; pv2 = 0.0
        over = 0; exh = 0.0; exl = 0.0
        for j in range(s, e):
            tp_ = (h[j] + l[j] + c[j]) / 3.0
            w = v[j] if v[j] > 0 else 1.0
            pv += tp_ * w; vv += w; pv2 += tp_ * tp_ * w
            vw = pv / vv
            var = pv2 / vv - vw * vw
            sd = np.sqrt(var) if var > 0 else 0.0
            if ny[j] < D * 1440 + t0 or sd <= 0:
                continue
            up = vw + k * sd; dn = vw - k * sd
            d = 0
            if conf == 0:
                if c[j] > up: d = -1; exh = h[j]
                elif c[j] < dn: d = 1; exl = l[j]
            else:
                if over == 0:
                    if c[j] > up: over = 1; exh = h[j]
                    elif c[j] < dn: over = -1; exl = l[j]
                else:
                    if over == 1:
                        if h[j] > exh: exh = h[j]
                        if c[j] < up: d = -1
                    else:
                        if l[j] < exl: exl = l[j]
                        if c[j] > dn: d = 1
            if d == 0:
                continue
            if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                over = 0
                continue
            B = j + 1
            if B >= X:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            st = (exl - buf * a) if d > 0 else (exh + buf * a)
            r = (ent - st) * d
            goal = vw if tgtmode == 0 else 0.5 * (vw + ent)
            g = (goal - ent) * d
            if r > 0.0 and g > 0.0:
                IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = g / r; IX[m] = X; m += 1
            break
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def lhm(ny, o, h, l, c, sp, days, t_end, atr, cl, m0, m1, e0, xm, kmin, stopk, usegap, dirs):
    """D: Bewegung 9:30 -> m1 (usegap=1: Vortagesschluss -> m1) entscheidet die Richtung; Einstieg e0, Ausstieg xm,
    nur wenn |Bewegung| >= kmin x ATR. Stop stopk x ATR, kein Ziel."""
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); RD = np.zeros(n); TP = np.zeros(n); IX = np.zeros(n, np.int64); m = 0
    for q in range(1, n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + m0); e = np.searchsorted(ny, D * 1440 + m1)
        B = np.searchsorted(ny, D * 1440 + e0); X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0] or ny[s] != D * 1440 + m0 or ny[e] != D * 1440 + m1 or ny[B] != D * 1440 + e0 or X <= B:
            continue
        a = _atr_at(t_end, atr, D * 1440 + m0)
        if not (a > 0):
            continue
        base = o[s]
        if usegap == 1:
            if np.isnan(cl[q - 1]) or days[q] - days[q - 1] > 4:
                continue
            base = cl[q - 1]
        mv = o[e] - base
        if abs(mv) < kmin * a:
            continue
        d = 1 if mv > 0 else -1
        if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
            continue
        IE[m] = B; DD[m] = d; RD[m] = stopk * a; TP[m] = 0.0; IX[m] = X; m += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def spike_fade(ny, o, h, l, c, sp, days, t_end, atr, ts, nbars, wait, xm, kmin, buf, tgtfrac, dirs):
    """E: Spitze ab ts (NY-Minute, z. B. 8:30) ueber nbars Kerzen: Bewegung Open(ts) -> Extrem >= kmin x ATR.
    Einstieg 'wait' Kerzen nach ts gegen die Spitze, wenn der Kurs noch nicht tgtfrac zurueckgelaufen ist.
    Stop Extrem + buf x ATR, Ziel tgtfrac der Spitze zurueck (vom Extrem gemessen), Ausstieg xm."""
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); RD = np.zeros(n); TP = np.zeros(n); IX = np.zeros(n, np.int64); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + ts)
        if s + wait >= ny.shape[0] or ny[s] != D * 1440 + ts:
            continue
        X = np.searchsorted(ny, D * 1440 + xm)
        B = s + wait
        if X >= ny.shape[0] or B >= X or ny[B] - ny[s] != wait * 5:
            continue
        a = _atr_at(t_end, atr, D * 1440 + ts)
        if not (a > 0):
            continue
        p0 = o[s]; hh = h[s]; ll = l[s]
        for j in range(s, s + nbars):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        up = hh - p0; dn = p0 - ll
        if up >= dn:
            mv = up; d = -1; ex = hh
        else:
            mv = dn; d = 1; ex = ll
        if mv < kmin * a:
            continue
        if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
            continue
        for j in range(s + nbars, B):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        ex = hh if d < 0 else ll
        goal = ex + d * tgtfrac * abs(ex - p0)
        ent = o[B] + (sp[B] if d > 0 else 0.0)
        st = ex - d * buf * a
        r = (ent - st) * d
        g = (goal - ent) * d
        if r > 0.0 and g > 0.0:
            IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = g / r; IX[m] = X; m += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def week_open_fade(ny, o, h, l, c, sp, days, t_end, atr, dows, e0, xm, dmin, dmax, stopk, tgtfrac):
    """F (Weekly-Open-Magnet): Wochen-Eroeffnung = Open der ersten Kerze ab Sonntag 18:00 NY. An den NY-Wochentagen der
    Bitmaske dows (Bit 1 = Mo ... Bit 5 = Fr) um e0: Abstand Kurs - Wochen-Eroeffnung zwischen dmin und dmax x ATR ->
    Richtung Wochen-Eroeffnung, Ziel tgtfrac des Abstands, Stop stopk x ATR, Ausstieg xm."""
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); RD = np.zeros(n); TP = np.zeros(n); IX = np.zeros(n, np.int64); m = 0
    for q in range(n):
        D = days[q]
        dow = (D + 4) % 7
        if ((dows >> dow) & 1) == 0:
            continue
        sun = D - dow                       # Sonntag dieser Woche (NY-Tag)
        s = np.searchsorted(ny, sun * 1440 + 1080)
        B = np.searchsorted(ny, D * 1440 + e0); X = np.searchsorted(ny, D * 1440 + xm)
        if s >= ny.shape[0] or ny[s] > sun * 1440 + 1080 + 1440 or B >= ny.shape[0] or ny[B] != D * 1440 + e0 or X >= ny.shape[0] or X <= B:
            continue
        a = _atr_at(t_end, atr, D * 1440 + e0)
        if not (a > 0):
            continue
        wo = o[s]
        dist = o[B] - wo
        if abs(dist) < dmin * a or abs(dist) > dmax * a:
            continue
        d = -1 if dist > 0 else 1
        ent = o[B] + (sp[B] if d > 0 else 0.0)
        goal = ent + d * tgtfrac * abs(dist)
        r = stopk * a
        g = (goal - ent) * d
        if r > 0.0 and g > 0.0:
            IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = g / r; IX[m] = X; m += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]
