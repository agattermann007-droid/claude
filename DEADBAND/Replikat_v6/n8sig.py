"""Neues Konzept (Stufe 8): Signal-Generatoren fuer eigenstaendige Strategien aus den YouTube-Quellen.
Zeit = NY-Minuten seit Epoche; Rueckgabe je Generator (ie, d, rd, tpR, ix): Einstiegs-Index (Open der Kerze), Richtung,
Stop-Abstand (Preis), Ziel in R (0 = keins), Ausstiegs-Index (Open dieser Kerze). Alle Entscheidungen nur mit Kerzen,
die vor dem Einstieg abgeschlossen sind. Long-Einstieg zum Ask (Open + Spread)."""
import numpy as np
from numba import njit
from scan6 import _atr_at


@njit(cache=True)
def _out(n):
    return np.zeros(n, np.int64), np.zeros(n, np.int64), np.zeros(n), np.zeros(n), np.zeros(n, np.int64)


@njit(cache=True)
def gen_orb(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, stopmode, stopk, tpr, dirs, mn, mx, maxn):
    """Opening-Range-Breakout (ORB, London-/Asia-Breakout, Initial Balance, erste Kerze):
    Range [r0, r1), im Fenster [r1, tend) schliesst eine Kerze ausserhalb -> Einstieg am Open der naechsten Kerze.
    stopmode 0 = Gegenseite der Range, 1 = Range-Mitte, 2 = stopk x ATR, 3 = Extrem der Ausbruchskerze + stopk x ATR.
    Ziel tpr R (0 = keins), Ausstieg xm. maxn = Einstiege je Tag (2 = nach Stop einmal in Gegenrichtung)."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(2 * n); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + r0); e = np.searchsorted(ny, D * 1440 + r1)
        if e - s < max(1, int((r1 - r0) // 5 * 0.6)) or e >= ny.shape[0]:
            continue
        a = _atr_at(t_end, atr, D * 1440 + r0)
        if not (a > 0):
            continue
        hh = h[s]; ll = l[s]
        for j in range(s, e):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        rng = hh - ll
        if rng < mn * a or rng > mx * a or rng <= 0.0:
            continue
        te = np.searchsorted(ny, D * 1440 + tend); X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0]:
            continue
        cnt = 0; lastd = 0; j = e; busy_until = -1
        while j < te and cnt < maxn:
            if j < busy_until:
                j += 1; continue
            d = 0
            if c[j] > hh and lastd != 1:
                d = 1
            elif c[j] < ll and lastd != -1:
                d = -1
            if d == 0 or (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                j += 1; continue
            B = j + 1
            if B >= X:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            if stopmode == 0:
                st = ll if d > 0 else hh
            elif stopmode == 1:
                st = 0.5 * (hh + ll)
            elif stopmode == 2:
                st = ent - d * stopk * a
            else:
                st = (l[j] if d > 0 else h[j]) - d * stopk * a
            r = (ent - st) * d
            if r > 0.0:
                IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = tpr; IX[m] = X; m += 1; cnt += 1; lastd = d
                # naechster Einstieg erst, wenn dieser Trade sicher vorbei ist (Stop beruehrt)
                k = B; done = False
                while k < X:
                    if (d > 0 and l[k] <= st) or (d < 0 and h[k] + sp[k] >= st):
                        done = True; break
                    if tpr > 0.0 and ((d > 0 and h[k] >= ent + tpr * r) or (d < 0 and l[k] + sp[k] <= ent - tpr * r)):
                        break
                    k += 1
                if not done:
                    break
                busy_until = k + 1
            j += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_sb(ny, o, h, l, c, sp, days, t_end, atr, ref0, ref1, w0, w1, xm, buf, tpr, dirs, minsw, tgtopp):
    """ICT Silver Bullet / Judas: Referenz-Range [ref0, ref1). Im Fenster [w0, w1) wird ein Extrem der Range
    ueberschritten (Sweep, mind. minsw x ATR); danach entsteht eine Fair-Value-Gap in Gegenrichtung (Kerze j: Hoch unter
    dem Tief von j-2 = baerisch) -> Einstieg am Open von j+1. Stop: Extrem seit dem Sweep + buf x ATR. Ziel tpr R, oder
    tgtopp = 1: Gegenseite der Referenz-Range (mind. 1 R, sonst kein Trade). Ein Trade je Tag."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + ref0); e = np.searchsorted(ny, D * 1440 + ref1)
        if e - s < max(1, int((ref1 - ref0) // 5 * 0.6)) or e >= ny.shape[0]:
            continue
        a = _atr_at(t_end, atr, D * 1440 + ref0)
        if not (a > 0):
            continue
        hh = h[s]; ll = l[s]
        for j in range(s, e):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        ws = np.searchsorted(ny, D * 1440 + w0); we = np.searchsorted(ny, D * 1440 + w1)
        X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0] or ws < 2:
            continue
        swH = False; swL = False; exH = -1e18; exL = 1e18
        for j in range(max(e, ws - 6), we):
            if h[j] > hh + minsw * a:
                swH = True
            if l[j] < ll - minsw * a:
                swL = True
            if swH and h[j] > exH: exH = h[j]
            if swL and l[j] < exL: exL = l[j]
            if j < ws:
                continue
            d = 0
            if swH and h[j] < l[j - 2] and c[j] < hh:
                d = -1
            elif swL and l[j] > h[j - 2] and c[j] > ll:
                d = 1
            if d == 0 or (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                continue
            B = j + 1
            if B >= X:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            st = (exL - buf * a) if d > 0 else (exH + buf * a)
            r = (ent - st) * d
            if r <= 0.0:
                break
            t = tpr
            if tgtopp == 1:
                tg = hh if d > 0 else ll
                t = (tg - ent) * d / r
                if t < 1.0:
                    break
            IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = t; IX[m] = X; m += 1
            break
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def _bands(c, n):
    L = c.shape[0]
    mid = np.full(L, np.nan); sd = np.full(L, np.nan)
    s = 0.0; s2 = 0.0
    for i in range(L):
        s += c[i]; s2 += c[i] * c[i]
        if i >= n:
            s -= c[i - n]; s2 -= c[i - n] * c[i - n]
        if i >= n - 1:
            mu = s / n
            mid[i] = mu
            v = s2 / n - mu * mu
            sd[i] = np.sqrt(v) if v > 0 else 0.0
    return mid, sd


@njit(cache=True)
def _rsi(c, n):
    L = c.shape[0]
    r = np.full(L, 50.0)
    ag = 0.0; al = 0.0
    for i in range(1, L):
        ch = c[i] - c[i - 1]
        g = ch if ch > 0 else 0.0; lo = -ch if ch < 0 else 0.0
        if i <= n:
            ag += g / n; al += lo / n
        else:
            ag = (ag * (n - 1) + g) / n; al = (al * (n - 1) + lo) / n
        if i >= n:
            r[i] = 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    return r


@njit(cache=True)
def _ema(c, n):
    L = c.shape[0]
    e = np.empty(L); k = 2.0 / (n + 1.0)
    e[0] = c[0]
    for i in range(1, L):
        e[i] = c[i] * k + e[i - 1] * (1.0 - k)
    return e


@njit(cache=True)
def gen_bb(ny, o, h, l, c, sp, days, t_end, atr, bn, bk, rn, rlo, w0, w1, xm, stopk, dirs, mintp, maxn):
    """Bollinger-Rueckkehr (M5): Schluss ausserhalb des Bandes (bn, bk) und RSI(rn) extrem (< rlo bzw. > 100-rlo)
    im Fenster [w0, w1) -> Einstieg Gegenrichtung am naechsten Open. Ziel = Mittellinie zum Signalzeitpunkt (in R,
    mind. mintp R, sonst kein Trade), Stop stopk x ATR. Ausstieg xm. Bis maxn Trades je Tag (nach Ende des vorigen)."""
    mid, sd = _bands(c, bn)
    rs = _rsi(c, rn)
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n * max(maxn, 1)); m = 0
    for q in range(n):
        D = days[q]
        a = _atr_at(t_end, atr, D * 1440 + w0)
        if not (a > 0):
            continue
        ws = np.searchsorted(ny, D * 1440 + w0); we = np.searchsorted(ny, D * 1440 + w1)
        X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0]:
            continue
        cnt = 0; j = max(ws, bn)
        while j < we and cnt < maxn:
            if np.isnan(mid[j]):
                j += 1; continue
            d = 0
            if c[j] < mid[j] - bk * sd[j] and rs[j] < rlo:
                d = 1
            elif c[j] > mid[j] + bk * sd[j] and rs[j] > 100.0 - rlo:
                d = -1
            if d == 0 or (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                j += 1; continue
            B = j + 1
            if B >= X:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            r = stopk * a
            t = (mid[j] - ent) * d / r
            if t < mintp:
                j += 1; continue
            IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = t; IX[m] = X; m += 1; cnt += 1
            st = ent - d * r; tg = ent + d * t * r
            k = B
            while k < X:
                if (d > 0 and (l[k] <= st or h[k] >= tg)) or (d < 0 and (h[k] + sp[k] >= st or l[k] + sp[k] <= tg)):
                    break
                k += 1
            j = k + 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_pull(ny, o, h, l, c, sp, days, t_end, atr, ef, es, w0, w1, xm, swing, buf, tpr, dirs, maxn):
    """Trend-Pullback (EMA ef/es auf M5): Trend = EMAf ueber EMAs und beide steigend (bzw. umgekehrt); eine Kerze
    beruehrt die EMAf und schliesst wieder in Trendrichtung ueber ihr -> Einstieg naechstes Open. Stop: Tief/Hoch der
    letzten swing Kerzen -/+ buf x ATR. Ziel tpr R. Fenster [w0, w1), Ausstieg xm, bis maxn Trades je Tag."""
    F = _ema(c, ef); S = _ema(c, es)
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n * max(maxn, 1)); m = 0
    for q in range(n):
        D = days[q]
        a = _atr_at(t_end, atr, D * 1440 + w0)
        if not (a > 0):
            continue
        ws = np.searchsorted(ny, D * 1440 + w0); we = np.searchsorted(ny, D * 1440 + w1)
        X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0] or ws < es + 5:
            continue
        cnt = 0; j = ws
        while j < we and cnt < maxn:
            d = 0
            if F[j] > S[j] and F[j] > F[j - 3] and S[j] > S[j - 3] and l[j] <= F[j] and c[j] > F[j] and c[j] > o[j]:
                d = 1
            elif F[j] < S[j] and F[j] < F[j - 3] and S[j] < S[j - 3] and h[j] >= F[j] and c[j] < F[j] and c[j] < o[j]:
                d = -1
            if d == 0 or (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                j += 1; continue
            B = j + 1
            if B >= X:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            ex = l[j]; eh = h[j]
            for k in range(max(0, j - swing + 1), j + 1):
                if l[k] < ex: ex = l[k]
                if h[k] > eh: eh = h[k]
            st = (ex - buf * a) if d > 0 else (eh + buf * a)
            r = (ent - st) * d
            if r <= 0.05 * a:
                j += 1; continue
            IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = tpr; IX[m] = X; m += 1; cnt += 1
            k = B
            while k < X:
                if (d > 0 and (l[k] <= st or (tpr > 0 and h[k] >= ent + tpr * r))) or \
                   (d < 0 and (h[k] + sp[k] >= st or (tpr > 0 and l[k] + sp[k] <= ent - tpr * r))):
                    break
                k += 1
            j = k + 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_mom(ny, o, h, l, c, sp, days, t_end, atr, t0, t1, xm, k, rev, stopk, tpr, dirs):
    """Zeit-Momentum: Bewegung vom Open der Kerze t0 bis zum Schluss vor t1 >= k x ATR -> Einstieg am Open von t1 in
    Richtung (rev = 1: dagegen). Stop stopk x ATR, Ziel tpr R, Ausstieg xm."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + t0); B = np.searchsorted(ny, D * 1440 + t1)
        X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0] or B <= s or ny[s] != D * 1440 + t0 or ny[B] != D * 1440 + t1 or B >= X:
            continue
        a = _atr_at(t_end, atr, D * 1440 + t0)
        if not (a > 0):
            continue
        mv = c[B - 1] - o[s]
        if abs(mv) < k * a:
            continue
        d = 1 if mv > 0 else -1
        if rev == 1:
            d = -d
        if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
            continue
        IE[m] = B; DD[m] = d; RD[m] = stopk * a; TP[m] = tpr; IX[m] = X; m += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_pdl(ny, o, h, l, c, sp, days, t_end, atr, w0, w1, xm, mode, buf, tpr, dirs):
    """Vortageshoch/-tief (NY-Tag 0:00-16:00 der Vortages-Sitzung = [prev 570, prev 960)): mode 0 = Ausbruch
    (Schluss jenseits -> mit), mode 1 = Sweep & Rueckkehr (Docht jenseits, Schluss innen -> dagegen). Fenster [w0, w1),
    Stop: mode 0 Gegenseite der Ausbruchskerze - buf x ATR, mode 1 Extrem + buf x ATR. Ziel tpr R."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n); m = 0
    for q in range(1, n):
        D = days[q]; P = days[q - 1]
        s = np.searchsorted(ny, P * 1440 + 570); e = np.searchsorted(ny, P * 1440 + 960)
        if e - s < 40:
            continue
        hh = h[s]; ll = l[s]
        for j in range(s, e):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        a = _atr_at(t_end, atr, D * 1440 + w0)
        if not (a > 0):
            continue
        ws = np.searchsorted(ny, D * 1440 + w0); we = np.searchsorted(ny, D * 1440 + w1)
        X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0]:
            continue
        if ws < we and (o[ws] > hh or o[ws] < ll):
            continue                                                       # Eroeffnung schon ausserhalb
        for j in range(ws, we):
            d = 0
            if mode == 0:
                if c[j] > hh: d = 1
                elif c[j] < ll: d = -1
            else:
                if h[j] > hh and c[j] < hh: d = -1
                elif l[j] < ll and c[j] > ll: d = 1
            if d == 0:
                if mode == 1 and (c[j] > hh or c[j] < ll):
                    break
                continue
            if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                break
            B = j + 1
            if B >= X:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            if mode == 0:
                st = (l[j] - buf * a) if d > 0 else (h[j] + buf * a)
            else:
                st = (l[j] - buf * a) if d > 0 else (h[j] + buf * a)
            r = (ent - st) * d
            if r > 0.0:
                IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = tpr; IX[m] = X; m += 1
            break
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_mom2(ny, o, h, l, c, sp, days, t_end, atr, t0, t1, te, xm, k, rev, stopk, tpr, dirs, same):
    """Intraday-Momentum nach Gao/Han/Li/Zhou: Bewegung vom Open der Kerze t0 bis zum Schluss vor t1 (>= k x ATR)
    bestimmt die Richtung; Einstieg erst am Open der Kerze te (z. B. 15:30), Ausstieg xm. same = 1: nur wenn auch die
    Bewegung t1 -> te in dieselbe Richtung zeigt. Stop stopk x ATR, Ziel tpr R."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + t0); B1 = np.searchsorted(ny, D * 1440 + t1)
        B = np.searchsorted(ny, D * 1440 + te); X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0] or B1 <= s or B <= B1 or B >= X or ny[B] != D * 1440 + te:
            continue
        a = _atr_at(t_end, atr, D * 1440 + t0)
        if not (a > 0):
            continue
        mv = c[B1 - 1] - o[s]
        if abs(mv) < k * a:
            continue
        d = 1 if mv > 0 else -1
        if same == 1 and (c[B - 1] - c[B1 - 1]) * d <= 0:
            continue
        if rev == 1:
            d = -d
        if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
            continue
        IE[m] = B; DD[m] = d; RD[m] = stopk * a; TP[m] = tpr; IX[m] = X; m += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_hold(ny, o, h, l, c, sp, days, t_end, atr, t_in, t_out, d0, stopk, tpr, trend, dowmask):
    """Zeit-Halten (Saisonalitaet im Tag): Einstieg am Open der Kerze t_in (negativ = Vorabend), Ausstieg t_out,
    Richtung d0 (+1/-1). trend > 0: nur wenn der Schluss vor dem Einstieg ueber (Long) bzw. unter (Short) dem
    Durchschnitt der letzten trend M5-Schluesse liegt. dowmask: Bit w (1 = Mo .. 5 = Fr, NY-Tag des Ausstiegs)."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n); m = 0
    for q in range(n):
        D = days[q]
        w = int((D + 4) % 7)
        if ((dowmask >> w) & 1) == 0:
            continue
        B = np.searchsorted(ny, D * 1440 + t_in); X = np.searchsorted(ny, D * 1440 + t_out)
        if X >= ny.shape[0] or B >= X or B < 1 or abs(ny[B] - (D * 1440 + t_in)) > 10:
            continue
        a = _atr_at(t_end, atr, D * 1440 + t_in)
        if not (a > 0):
            continue
        d = d0
        if trend > 0:
            if B < trend:
                continue
            s = 0.0
            for j in range(B - trend, B):
                s += c[j]
            if (c[B - 1] - s / trend) * d <= 0:
                continue
        IE[m] = B; DD[m] = d; RD[m] = stopk * a; TP[m] = tpr; IX[m] = X; m += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_ibret(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, fin, sin, tout, dirs, mn, mx):
    """Initial-Balance-Ausbruch mit Ruecklauf (Trade That Swing / edgeful, Gold): IB = [r0, r1), Breite W. Nach dem ersten
    Ueberschreiten (Hoch > IBH bzw. Tief < IBL) im Fenster [r1, tend) wartet eine Limit-Marke fin x W innerhalb des
    gebrochenen Randes. Beruehrt eine SPAETERE Kerze die Marke, Einstieg am Open der naechsten Kerze (Marktorder - so
    rechnet auch der EA). Stop sin x W innerhalb des Randes, Ziel tout x W jenseits des Randes. Erreicht der Kurs das
    Ziel vor dem Ruecklauf: kein Trade. Ausstieg xm."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + r0); e = np.searchsorted(ny, D * 1440 + r1)
        if e - s < max(1, int((r1 - r0) // 5 * 0.6)) or e >= ny.shape[0]:
            continue
        a = _atr_at(t_end, atr, D * 1440 + r0)
        if not (a > 0):
            continue
        hh = h[s]; ll = l[s]
        for j in range(s, e):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        W = hh - ll
        if W <= 0.0 or W < mn * a or W > mx * a:
            continue
        te = np.searchsorted(ny, D * 1440 + tend); X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0]:
            continue
        d = 0; jb = -1
        for j in range(e, te):
            if h[j] > hh and l[j] < ll:
                break
            if h[j] > hh:
                d = 1; jb = j; break
            if l[j] < ll:
                d = -1; jb = j; break
        if d == 0 or (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
            continue
        edge = hh if d > 0 else ll
        lim = edge - d * fin * W; st = edge - d * sin * W; tg = edge + d * tout * W
        for j in range(jb + 1, te):
            if (d > 0 and h[j] + sp[j] >= tg) or (d < 0 and l[j] <= tg):
                break
            if (d > 0 and l[j] <= lim) or (d < 0 and h[j] + sp[j] >= lim):
                if (d > 0 and l[j] <= st) or (d < 0 and h[j] + sp[j] >= st):
                    break
                B = j + 1
                if B >= X:
                    break
                ent = o[B] + (sp[B] if d > 0 else 0.0)
                r = (ent - st) * d
                g = (tg - ent) * d
                if r > 0.0 and g > 0.0:
                    IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = g / r; IX[m] = X; m += 1
                break
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_orbmid(ny, o, h, l, c, sp, days, t_end, atr, m0, m1, r0, r1, tend, xm, stopmode, stopk, tpr, mx):
    """ORB mit Mittelpunkt-Filter (tradingstats): Referenz-Range [m0, m1) (Nacht/London), Mittelpunkt M. Oeffnet der
    Markt um r0 ueber M: nur Long-Ausbruch der Range [r0, r1), darunter nur Short. Sonst wie gen_orb (1 Trade)."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n); m = 0
    for q in range(n):
        D = days[q]
        a0 = np.searchsorted(ny, D * 1440 + m0); a1 = np.searchsorted(ny, D * 1440 + m1)
        s = np.searchsorted(ny, D * 1440 + r0); e = np.searchsorted(ny, D * 1440 + r1)
        if a1 - a0 < 6 or e - s < max(1, int((r1 - r0) // 5 * 0.6)) or e >= ny.shape[0]:
            continue
        a = _atr_at(t_end, atr, D * 1440 + r0)
        if not (a > 0):
            continue
        H = h[a0]; L = l[a0]
        for j in range(a0, a1):
            if h[j] > H: H = h[j]
            if l[j] < L: L = l[j]
        want = 1 if o[s] > 0.5 * (H + L) else -1
        hh = h[s]; ll = l[s]
        for j in range(s, e):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        if hh - ll <= 0.0 or hh - ll > mx * a:
            continue
        te = np.searchsorted(ny, D * 1440 + tend); X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0]:
            continue
        for j in range(e, te):
            d = 1 if c[j] > hh else (-1 if c[j] < ll else 0)
            if d == 0:
                continue
            if d != want:
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
                IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = tpr; IX[m] = X; m += 1
            break
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_lw(ny, o, h, l, c, sp, days, t_end, atr, p0, p1, t0, tend, xm, k, stopmode, stopk, tpr, dirs):
    """Larry-Williams-Volatilitaetsausbruch: Vortages-Range R aus [p0, p1) des Vortags; Marke = Open um t0 +/- k x R.
    Schluss einer Kerze jenseits der Marke im Fenster [t0, tend) -> Einstieg naechstes Open in Ausbruchsrichtung.
    stopmode 0: Mitte zwischen Open(t0) und Einstieg (Williams), 1: stopk x ATR. Ziel tpr R, Ausstieg xm."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n); m = 0
    for q in range(1, n):
        D = days[q]; P = days[q - 1]
        a0 = np.searchsorted(ny, P * 1440 + p0); a1 = np.searchsorted(ny, P * 1440 + p1)
        s = np.searchsorted(ny, D * 1440 + t0)
        if a1 - a0 < 12 or s >= ny.shape[0] or ny[s] != D * 1440 + t0:
            continue
        a = _atr_at(t_end, atr, D * 1440 + t0)
        if not (a > 0):
            continue
        H = h[a0]; L = l[a0]
        for j in range(a0, a1):
            if h[j] > H: H = h[j]
            if l[j] < L: L = l[j]
        R = H - L; op = o[s]
        up = op + k * R; dn = op - k * R
        te = np.searchsorted(ny, D * 1440 + tend); X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0]:
            continue
        for j in range(s, te):
            d = 1 if c[j] > up else (-1 if c[j] < dn else 0)
            if d == 0:
                continue
            if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
                break
            B = j + 1
            if B >= X:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            st = 0.5 * (op + ent) if stopmode == 0 else ent - d * stopk * a
            r = (ent - st) * d
            if r > 0.05 * a:
                IE[m] = B; DD[m] = d; RD[m] = r; TP[m] = tpr; IX[m] = X; m += 1
            break
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_daily(ny, o, h, l, c, sp, days, t_end, atr, kind, t_sig, rs0, thr, ma, maxhold, stopk, tpr, dirs):
    """Kurz-Swing aus Tagesdaten der Sitzung [rs0, t_sig) (NAS: 9:30-15:55). Einstieg am Open der Kerze t_sig (= kurz vor
    Schluss). kind 0 = IBS: (C-L)/(H-L) < thr -> Long (> 1-thr -> Short); Ausstieg sobald ein Sitzungsschluss ueber dem
    Vortageshoch liegt (Long) bzw. unter dem Vortagestief, spaetestens nach maxhold Tagen (am Open der t_sig-Kerze).
    kind 1 = RSI(2) der Sitzungsschluesse < thr -> Long (> 100-thr -> Short); Ausstieg wenn Schluss > SMA5 (Long).
    ma > 0: Long nur ueber, Short nur unter dem SMA(ma) der Sitzungsschluesse. Stop stopk x ATR, Ziel tpr R (0 = keins)."""
    n = days.shape[0]
    SH = np.zeros(n); SL = np.zeros(n); SC = np.zeros(n); SI = np.full(n, -1, np.int64)
    for q in range(n):
        D = days[q]
        a0 = np.searchsorted(ny, D * 1440 + rs0); B = np.searchsorted(ny, D * 1440 + t_sig)
        if B >= ny.shape[0] or B - a0 < 12 or ny[B] != D * 1440 + t_sig:
            continue
        H = h[a0]; L = l[a0]
        for j in range(a0, B):
            if h[j] > H: H = h[j]
            if l[j] < L: L = l[j]
        SH[q] = H; SL[q] = L; SC[q] = c[B - 1]; SI[q] = B
    IE, DD, RD, TP, IX = _out(n); m = 0
    q = 1
    while q < n:
        if SI[q] < 0 or SI[q - 1] < 0:
            q += 1; continue
        d = 0
        if kind == 0:
            rg = SH[q] - SL[q]
            if rg <= 0:
                q += 1; continue
            ibs = (SC[q] - SL[q]) / rg
            if ibs < thr: d = 1
            elif ibs > 1.0 - thr: d = -1
        else:
            if q < 3:
                q += 1; continue
            ag = 0.0; al = 0.0
            for k2 in range(q - 1, q + 1):
                ch = SC[k2] - SC[k2 - 1]
                if ch > 0: ag += ch
                else: al -= ch
            rsi = 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
            if rsi < thr: d = 1
            elif rsi > 100.0 - thr: d = -1
        if d != 0 and ma > 0:
            if q < ma:
                d = 0
            else:
                s = 0.0
                for k2 in range(q - ma + 1, q + 1):
                    s += SC[k2]
                if (SC[q] - s / ma) * d <= 0:
                    d = 0
        if d == 0 or (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
            q += 1; continue
        a = _atr_at(t_end, atr, ny[SI[q]])
        if not (a > 0):
            q += 1; continue
        x = -1
        for k2 in range(q + 1, min(n, q + 1 + maxhold)):
            if SI[k2] < 0:
                continue
            x = k2
            if kind == 0:
                if (d > 0 and SC[k2] > SH[k2 - 1]) or (d < 0 and SC[k2] < SL[k2 - 1]):
                    break
            else:
                s5 = 0.0
                for k3 in range(k2 - 4, k2 + 1):
                    s5 += SC[k3]
                if (SC[k2] - s5 / 5.0) * d > 0:
                    break
        if x < 0:
            q += 1; continue
        IE[m] = SI[q]; DD[m] = d; RD[m] = stopk * a; TP[m] = tpr; IX[m] = SI[x]; m += 1
        q = x
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]


@njit(cache=True)
def gen_tom(ny, o, h, l, c, sp, days, t_end, atr, t_sig, before, after, stopk, tpr):
    """Turn of the Month: Long am Open der Kerze t_sig des before-letzten Handelstags des Monats, Ausstieg am Open der
    t_sig-Kerze des after-ten Handelstags des neuen Monats. Stop stopk x ATR."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n); m = 0
    mon = np.zeros(n, np.int64)
    for q in range(n):
        # Monat aus Tagen seit Epoche (proleptischer Kalender, Civil-from-days nach H. Hinnant)
        z = days[q] + 719468; era = (z if z >= 0 else z - 146096) // 146097; doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365; doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153; mm = mp + 3 if mp < 10 else mp - 9
        mon[q] = (yoe + era * 400 + (1 if mm <= 2 else 0)) * 12 + mm
    for q in range(n - 1):
        if mon[q + 1] == mon[q]:
            continue                                                  # q = letzter Handelstag des Monats
        qi = q - (before - 1); qx = q + after
        if qi < 0 or qx >= n or mon[qx] != mon[q + 1]:
            continue
        B = np.searchsorted(ny, days[qi] * 1440 + t_sig); X = np.searchsorted(ny, days[qx] * 1440 + t_sig)
        if X >= ny.shape[0] or B >= X:
            continue
        a = _atr_at(t_end, atr, ny[B])
        if not (a > 0):
            continue
        IE[m] = B; DD[m] = 1; RD[m] = stopk * a; TP[m] = tpr; IX[m] = X; m += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]
