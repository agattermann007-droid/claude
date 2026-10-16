"""Replikat 9 - Regime-Regeln (Trendwende-Waechter TW) und Intraday-Filter fuer die V9-Tests.

FESTGELEGT VOR DEN TESTS (16.10.2026). Der Code von Build 8.20 und patch900.py lag nicht vor; die Regeln sind aus den
Kurzbeschreibungen im Auftrag rekonstruiert. Alle Tagesregeln nutzen nur ABGESCHLOSSENE Servertage (17:00-17:00 NY):
Signal am Servertag S -> Werte des letzten D1-Balkens vor S.

Abwaertsregime (sperrt NAS-Long-Fades und S0830); Gold-Shorts: spiegelbildlich (Aufwaertsregime sperrt Shorts).
  R1  EMA20 + Steigung        Schluss < EMA20 und EMA20 faellt (EMA20 heute < gestern)
  R2  Momentum 5 Tage          Schluss - Schluss vor 5 Tagen <= -1,5 ATR14
  R3  Kombi (8.20 aktiv)       Schluss < EMA20 und 5-Tage-Aenderung <= -1,0 ATR14
  R4  Tagestrend               Aenderung des letzten Tages <= -0,75 ATR14
  R5  Struktur                 Schluss unter dem Tief der 10 Tage davor -> an, bis ein Schluss ueber EMA10 liegt
  R6  Fast/Slow Baer           Rendite 21 Tage < 0 und 252 Tage < 0 (Goulding/Harvey/Mazzoleni 2023)
  R7  Fast/Slow Korrektur      Rendite 21 Tage < 0 und 252 Tage > 0
  R8  Donchian 20 / 2 ATR      Schluss <= Hoch der letzten 20 Tage - 2 ATR14
  R9  Vola-Sprung              mittlere Tagesspanne 5 Tage / 50 Tage > 1,3   (symmetrisch, kein Spiegel)
  R10 Vola-Rang                Rang der 10-Tage-Vola (Std. Log-Renditen) unter den letzten 252 Tagen > 0,8 (symmetrisch)
Intraday (nur NAS, Signalkerze 9:30-16:00 NY; Noise Area wie Zarattini/Aziz/Barbon 2024: O = Open 9:30, PC = Vortagesschluss,
sigma(T) = Mittel der letzten 14 Tage von |Schluss(T)/O - 1|):
  NA  Noise-Area-Veto          Tief der Signalkerze < min(O, PC) x (1 - sigma) - 0,25 sigma x min(O, PC)
  TR  Tagesrichtung            Schluss der Signalkerze / O - 1 < -sigma(T)
"""
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Replikat_v6"))
import prep5 as P

REGELN = ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10")


def _sma(x, n):
    out = np.full(len(x), np.nan)
    cs = np.r_[0.0, np.cumsum(x)]
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def _rmax(x, n):
    from numpy.lib.stride_tricks import sliding_window_view
    out = np.full(len(x), np.nan)
    out[n - 1:] = sliding_window_view(x, n).max(axis=1)
    return out


def _rmin(x, n):
    from numpy.lib.stride_tricks import sliding_window_view
    out = np.full(len(x), np.nan)
    out[n - 1:] = sliding_window_view(x, n).min(axis=1)
    return out


def tagesregeln(D1):
    """Flags je D1-Balken j (Stand nach Schluss von j). Rueckgabe dict: Regel -> (abwaerts, aufwaerts) bool-Arrays."""
    o, h, l, c = D1["o"], D1["h"], D1["l"], D1["c"]
    n = len(c)
    ema20 = P.ema_mt5(c, 20); ema10 = P.ema_mt5(c, 10)
    tr = np.r_[h[0] - l[0], np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1])]
    atr = _sma(tr, 14)
    sh = lambda x, k: np.r_[np.full(k, np.nan), x[:-k]]
    r5 = c - sh(c, 5); r1 = c - sh(c, 1)
    ema20v = sh(ema20, 1)
    lo10 = sh(_rmin(l, 10), 1); hi10 = sh(_rmax(h, 10), 1)
    hi20 = _rmax(h, 20); lo20 = _rmin(l, 20)
    rng = h - l
    v5 = _sma(rng, 5); v50 = _sma(rng, 50)
    lr = np.r_[np.nan, np.log(c[1:] / c[:-1])]
    from numpy.lib.stride_tricks import sliding_window_view
    rv10 = np.full(n, np.nan)
    w = sliding_window_view(np.nan_to_num(lr), 10)
    rv10[9:] = w.std(axis=1)
    rv10[:10] = np.nan
    rk = np.full(n, np.nan)
    for j in range(262, n):
        hist = rv10[j - 252:j]
        rk[j] = np.mean(hist < rv10[j])
    fast = c / sh(c, 21) - 1.0; slow = c / sh(c, 252) - 1.0
    # R5 Struktur mit Zustand
    r5d = np.zeros(n, bool); r5u = np.zeros(n, bool)
    sd = False; su = False
    for j in range(n):
        if np.isfinite(lo10[j]) and c[j] < lo10[j]:
            sd = True
        elif sd and c[j] > ema10[j]:
            sd = False
        if np.isfinite(hi10[j]) and c[j] > hi10[j]:
            su = True
        elif su and c[j] < ema10[j]:
            su = False
        r5d[j] = sd; r5u[j] = su
    with np.errstate(invalid="ignore"):
        F = {
            "R1": ((c < ema20) & (ema20 < ema20v), (c > ema20) & (ema20 > ema20v)),
            "R2": (r5 <= -1.5 * atr, r5 >= 1.5 * atr),
            "R3": ((c < ema20) & (r5 <= -1.0 * atr), (c > ema20) & (r5 >= 1.0 * atr)),
            "R4": (r1 <= -0.75 * atr, r1 >= 0.75 * atr),
            "R5": (r5d, r5u),
            "R6": ((fast < 0) & (slow < 0), (fast > 0) & (slow > 0)),
            "R7": ((fast < 0) & (slow > 0), (fast > 0) & (slow < 0)),
            "R8": (c <= hi20 - 2.0 * atr, c >= lo20 + 2.0 * atr),
            "R9": (v5 / v50 > 1.3, v5 / v50 > 1.3),
            "R10": (rk > 0.8, rk > 0.8),
        }
    F = {k: (np.nan_to_num(a, nan=0).astype(bool), np.nan_to_num(b, nan=0).astype(bool)) for k, (a, b) in F.items()}
    return F


def flags_signal(D, sym, t_entry, F=None):
    """Regel-Flags (abwaerts, aufwaerts) zum Einstieg t_entry (NY-Minuten) aus dem letzten abgeschlossenen Servertag."""
    D1 = D[sym]["d1"]
    if F is None:
        F = tagesregeln(D1)
    key = D1["key"]
    sd = (np.asarray(t_entry) + 420) // 1440
    j = np.searchsorted(key, sd, side="left") - 1
    ok = j >= 0
    jj = np.clip(j, 0, len(key) - 1)
    return {k: (a[jj] & ok, b[jj] & ok) for k, (a, b) in F.items()}


def noise_area(D, sym="NAS", ntage=14):
    """Je M5-Kerze im Fenster 9:30-16:00 NY: O, PC, sigma der Kerze (Schluss am Ende der Kerze). NaN ausserhalb."""
    d = D[sym]
    ny = d["ny"]; o = d["o"]; c = d["c"]
    day = ny // 1440; m = ny % 1440
    n = len(ny)
    O = np.full(n, np.nan); PC = np.full(n, np.nan); SIG = np.full(n, np.nan)
    days, first = np.unique(day, return_index=True)
    last = np.r_[first[1:], n]
    tab = {}                                    # Tag -> (O, Schluss vor 16:00, Bloecke |cl/O-1|)
    for dd, a, b in zip(days, first, last):
        mm = m[a:b]
        sel = np.nonzero((mm >= 570) & (mm < 960))[0] + a
        if len(sel) == 0 or m[sel[0]] > 575:
            continue
        O0 = o[sel[0]]
        bl = np.full(78, np.nan)
        bl[(m[sel] - 570) // 5] = np.abs(c[sel] / O0 - 1.0)
        tab[int(dd)] = (O0, c[sel[-1]], bl, sel)
    keys = sorted(tab)
    for q, dd in enumerate(keys):
        if q < ntage + 1:
            continue
        O0, _, _, sel = tab[dd]
        pc = tab[keys[q - 1]][1]
        hist = np.array([tab[keys[q - k]][2] for k in range(1, ntage + 1)])
        sig = np.nanmean(hist, axis=0)
        b = (m[sel] - 570) // 5
        O[sel] = O0; PC[sel] = pc; SIG[sel] = sig[b]
    return O, PC, SIG


def intraday_flags(D, sigs_mod, NA):
    """NA-Veto und Tagesrichtung je Signal (Signalkerze i_sig). NA = Ergebnis von noise_area()."""
    O, PC, SIG = NA
    i = sigs_mod["i_sig"]
    d = D["NAS"]
    lo = d["l"][i]; cl = d["c"][i]
    ref = np.minimum(O[i], PC[i])
    s = SIG[i]
    with np.errstate(invalid="ignore"):
        na = lo < ref * (1.0 - s) - 0.25 * s * ref
        tr_ = (cl / O[i] - 1.0) < -s
    gueltig = np.isfinite(s)
    return na & gueltig, tr_ & gueltig
