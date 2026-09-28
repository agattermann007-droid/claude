"""Probability Grid (Konzept: LuxAlgo "Probability Grid", CC BY-NC-SA 4.0) als Nachbau fuer das Replikat.

Schwung-Erkennung wie fetchPivot: Kerzenkoerper (max/min aus Open und Close), Richtung HOCH, sobald der Koerper-Hochpunkt
der hoechste der letzten `length` Kerzen ist, TIEF entsprechend (HOCH hat Vorrang). Wechselt die Richtung, ist der bis
dahin gelaufene Extrempunkt ein bestaetigter Pivot. Jeder Schenkel (vorheriger Pivot -> neuer Pivot) wird mit Groesse
(|Preis-Differenz| / Preis des vorherigen Pivots) und Dauer (Kerzen) gespeichert, getrennt nach steigend/fallend
(fetchData), hoechstens `maxpiv` je Richtung (die aeltesten fallen heraus).

Nur abgeschlossene Kerzen (barstate.isconfirmed). Zeitebene = M5 oder aus M5 gebildete M15/M30/H1-Kerzen
(Ausrichtung wie MT5: Serverzeit = NY + 7 h, 7 h ist ein Vielfaches jeder Zeitebene bis H1)."""
import numpy as np
from numba import njit


@njit(cache=True)
def lux_pivots(o, c, length):
    """Zustand NACH jeder Kerze i: bias (+1 Aufwaertslauf, -1 Abwaertslauf, 0 unbekannt), letzter bestaetigter Pivot
    (Preis, Kerze, Art +1 Hoch / -1 Tief), laufender Extrempunkt (Preis, Kerze) und die bis dahin gespeicherten Schenkel.
    Schenkel: Kerze der Bestaetigung, Richtung (+1 steigend, -1 fallend), Groesse (normiert), Dauer (Kerzen)."""
    n = o.shape[0]
    bias = np.zeros(n, np.int64)
    piv_px = np.full(n, np.nan); piv_bar = np.full(n, -1, np.int64); piv_bias = np.zeros(n, np.int64)
    cur_px = np.full(n, np.nan); cur_bar = np.full(n, -1, np.int64)
    leg_conf = np.zeros(n, np.int64); leg_dir = np.zeros(n, np.int64); leg_sz = np.zeros(n); leg_bars = np.zeros(n, np.int64)
    nleg = 0
    b = 0                               # bias (0 = na)
    cpx = np.nan; cbar = -1             # currentPrice / currentBar (var: Start = erste Kerze)
    ppx = np.nan; pbar = -1; pbias = 0  # currentPivot
    lpx = np.nan; lbar = -1             # lastPrice / lastBar (fetchData)
    if n > 0:
        cpx = c[0]; cbar = 0; lpx = c[0]; lbar = 0
    for i in range(n):
        mx = max(o[i], c[i]); mn = min(o[i], c[i])
        if i >= length - 1:
            up = -1e300; lo = 1e300
            for j in range(i - length + 1, i + 1):
                a = max(o[j], c[j]); z = min(o[j], c[j])
                if a > up:
                    up = a
                if z < lo:
                    lo = z
            nb = b
            if mx == up:
                nb = 1
            elif mn == lo:
                nb = -1
            newp = False
            if nb != b and nb != 0:
                if b != 0:              # erster Wechsel von na: kein Pivot (Pine: na-Vergleich)
                    newp = True
                    ppx = cpx; pbar = cbar; pbias = 1 if nb == -1 else -1
                cpx = up if nb == 1 else lo
                cbar = i
                b = nb
            elif b != 0:
                old = cpx
                cpx = max(up, cpx) if b == 1 else min(lo, cpx)
                if cpx != old:
                    cbar = i
            # fetchData
            if newp:
                bars_d = pbar - lbar
                sz = abs(ppx - lpx) / lpx
                if bars_d != 0 and not np.isnan(sz):
                    leg_conf[nleg] = i; leg_dir[nleg] = 1 if ppx > lpx else -1; leg_sz[nleg] = sz; leg_bars[nleg] = bars_d
                    nleg += 1
                    lpx = ppx; lbar = pbar
        bias[i] = b; piv_px[i] = ppx; piv_bar[i] = pbar; piv_bias[i] = pbias; cur_px[i] = cpx; cur_bar[i] = cbar
    return bias, piv_px, piv_bar, piv_bias, cur_px, cur_bar, leg_conf[:nleg], leg_dir[:nleg], leg_sz[:nleg], leg_bars[:nleg]


@njit(cache=True)
def _last_legs(leg_conf, leg_dir, i, d, maxpiv, out_idx):
    """Indizes der letzten maxpiv Schenkel der Richtung d, die bis einschliesslich Kerze i bestaetigt waren."""
    k = np.searchsorted(leg_conf, i, side="right") - 1
    m = 0
    while k >= 0 and m < maxpiv:
        if leg_dir[k] == d:
            out_idx[m] = k
            m += 1
        k -= 1
    return m


@njit(cache=True)
def _ecdf(vals, idx, m, x):
    """Anteil der Werte <= x (empirische Verteilung, wie die Perzentil-Linien des Grids)."""
    if m == 0:
        return np.nan
    cnt = 0
    for q in range(m):
        if vals[idx[q]] <= x:
            cnt += 1
    return cnt / m


@njit(cache=True)
def _pct_nearest_rank(vals, idx, m, p):
    """array.percentile_nearest_rank (Pine): Wert mit Rang ceil(p/100*m) (mind. 1) der sortierten Werte."""
    if m == 0:
        return np.nan
    tmp = np.empty(m)
    for q in range(m):
        tmp[q] = vals[idx[q]]
    tmp.sort()
    r = int(np.ceil(p / 100.0 * m))
    if r < 1:
        r = 1
    if r > m:
        r = m
    return tmp[r - 1]


@njit(cache=True)
def features(qbar, qd, qext, qgoal, qstop, qent, bias, piv_px, piv_bar, cur_px, cur_bar,
             leg_conf, leg_dir, leg_sz, leg_bars, maxpiv, minlegs):
    """Merkmale je Abfrage (Fade-Signal) auf der Grid-Zeitebene. qbar = letzte abgeschlossene Kerze der Zeitebene,
    qd = Fade-Richtung, qext = Extrem des Fehlausbruchs, qgoal/qstop/qent = Ziel/Stop/Einstieg (Preise).
    Spalten: 0 bias, 1 align (+1 Fade in Laufrichtung, -1 gegen den Lauf), 2 p_ext (Rang der bisherigen Laufgroesse unter
    den Schenkeln gleicher Richtung), 3 p_bar (Rang der Laufdauer bis jetzt), 4 beyond = (1-p_ext)(1-p_bar),
    5 p_tgt (Rang des Wegs vom Fehlausbruch-Extrem zum Ziel unter den Schenkeln in Fade-Richtung; Chance ~ 1-p_tgt),
    6 surv_stop (bedingte Chance, dass der Lauf bis zum Stop weiterlaeuft: S(stop)/S(jetzt), nur gegen den Lauf),
    7 n Schenkel gleicher Richtung, 8 n Schenkel in Fade-Richtung, 9 ext (Groesse), 10 bars (Dauer),
    11 p50 Schenkelgroesse in Fade-Richtung (normiert), 12 p_barext (Rang der Dauer bis zum Extrempunkt)."""
    nq = qbar.shape[0]
    out = np.full((nq, 13), np.nan)
    idx1 = np.empty(maxpiv, np.int64); idx2 = np.empty(maxpiv, np.int64)
    for q in range(nq):
        i = qbar[q]
        if i < 0 or bias[i] == 0 or np.isnan(piv_px[i]) or piv_bar[i] < 0:
            continue
        b = bias[i]; d = qd[q]
        m1 = _last_legs(leg_conf, leg_dir, i, b, maxpiv, idx1)
        m2 = _last_legs(leg_conf, leg_dir, i, d, maxpiv, idx2)
        out[q, 0] = b
        out[q, 1] = 1.0 if d == b else -1.0
        out[q, 7] = m1; out[q, 8] = m2
        ext = abs(cur_px[i] - piv_px[i]) / piv_px[i]
        bars = i - piv_bar[i]
        out[q, 9] = ext; out[q, 10] = bars
        if m1 >= minlegs:
            pe = _ecdf(leg_sz, idx1, m1, ext)
            pb = _ecdf(leg_bars.astype(np.float64), idx1, m1, float(bars))
            out[q, 2] = pe; out[q, 3] = pb; out[q, 4] = (1.0 - pe) * (1.0 - pb)
            out[q, 12] = _ecdf(leg_bars.astype(np.float64), idx1, m1, float(cur_bar[i] - piv_bar[i]))
            if d != b:
                # gegen den Lauf: laeuft er bis zum Stop weiter? S(x) = Anteil der Schenkel > x
                xs = abs(qstop[q] - piv_px[i]) / piv_px[i]
                s_now = 1.0 - pe
                s_stop = 1.0 - _ecdf(leg_sz, idx1, m1, xs)
                out[q, 6] = s_stop / s_now if s_now > 0.0 else 0.0
        if m2 >= minlegs:
            xt = abs(qgoal[q] - qext[q]) / qext[q]
            out[q, 5] = _ecdf(leg_sz, idx2, m2, xt)
            out[q, 11] = _pct_nearest_rank(leg_sz, idx2, m2, 50.0)
    return out


@njit(cache=True)
def grid_level(qbar, qd, qref, pct, piv_px, bias, leg_conf, leg_dir, leg_sz, maxpiv, minlegs):
    """Kurs, den ein Schenkel in Fade-Richtung ab qref mit dem Perzentil pct erreicht (Grid-Linie), NaN ohne Daten."""
    nq = qbar.shape[0]
    out = np.full(nq, np.nan)
    idx = np.empty(maxpiv, np.int64)
    for q in range(nq):
        i = qbar[q]
        if i < 0:
            continue
        m = _last_legs(leg_conf, leg_dir, i, qd[q], maxpiv, idx)
        if m < minlegs:
            continue
        v = _pct_nearest_rank(leg_sz, idx, m, pct)
        out[q] = qref[q] * (1.0 + qd[q] * v)
    return out


def tf_bars(ny, o, h, l, c, minutes):
    """M5 -> Zeitebene (NY-Minuten, Ausrichtung wie MT5). Rueckgabe: Kerzenbeginn, o, h, l, c und je M5-Kerze j der Index
    der letzten Zeitebenen-Kerze, die abgeschlossen ist, wenn die Kerze j+1 beginnt (Einstieg des Fades; im EA: Shift 1 der
    Zeitebene beim Beginn der neuen M5-Kerze). -1 = keine."""
    n = len(ny)
    if minutes == 5:
        return ny, o, h, l, c, np.arange(n)
    key = ny // minutes
    uniq, first = np.unique(key, return_index=True)
    last = np.r_[first[1:] - 1, n - 1]
    oo = o[first]; cc = c[last]
    hh = np.maximum.reduceat(h, first); ll = np.minimum.reduceat(l, first)
    t0 = uniq * minutes
    kk = np.searchsorted(t0, ny, side="right") - 1          # Zeitebenen-Kerze jeder M5-Kerze
    done_at = np.empty(n, np.int64)
    done_at[:-1] = kk[1:] - 1                                # Kerze vor der, in der die naechste M5-Kerze liegt
    done_at[-1] = kk[-1] if ny[-1] + 5 >= t0[kk[-1]] + minutes else kk[-1] - 1
    return t0, oo, hh, ll, cc, done_at
