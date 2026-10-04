"""Stufe 8.10: neue Kandidaten aus der Recherche (Konventionen wie n8sig: NY-Minuten, Einstieg am Open, nur
abgeschlossene Kerzen vor dem Einstieg, Rueckgabe ie, d, rd, tpR, ix).
- gen_lastmom: Intraday-Momentum zum Schluss (Baltussen/Da/Lammers/Martens, JFE 2021 "Hedging demand and market
  intraday momentum"; Variante "Trend Day" nach E. Chan, Einstieg 14:00 mit Mindestbewegung).
- Gold-PM-Fix (Caminschi & Heaney 2014) laeuft ueber n8sig.gen_hold mit d0 = -1."""
import numpy as np
from numba import njit
from scan6 import _atr_at
from n8sig import _out


@njit(cache=True)
def gen_lastmom(ny, o, h, l, c, sp, days, t_end, atr, t1, xm, refmode, thr, rev, stopk, tpr, dirs, pclose):
    """Einstieg am Open der Kerze t1 in Richtung der bisherigen Tagesrendite (rev 1: dagegen).
    refmode 0: Rendite seit dem Vortagesschluss (letzter Schluss vor pclose des Vortags, NAS 960 = 16:00),
    refmode 1: seit dem Open um 9:30 (Kerze 570). Nur wenn |Rendite| >= thr x ATR(D1). Stop stopk x ATR,
    Ziel tpr R (0 = keins), Ausstieg am Open der Kerze xm. dirs 1 nur Long, -1 nur Short, 0 beide."""
    n = days.shape[0]
    IE, DD, RD, TP, IX = _out(n); m = 0
    for q in range(1, n):
        D = days[q]; P = days[q - 1]
        B = np.searchsorted(ny, D * 1440 + t1); X = np.searchsorted(ny, D * 1440 + xm)
        if X >= ny.shape[0] or B >= X or B < 1 or ny[B] != D * 1440 + t1:
            continue
        if refmode == 0:
            k = np.searchsorted(ny, P * 1440 + pclose) - 1
            if k < 0 or ny[k] < P * 1440 + pclose - 60:
                continue
            ref = c[k]
        else:
            k = np.searchsorted(ny, D * 1440 + 570)
            if k >= B or ny[k] != D * 1440 + 570:
                continue
            ref = o[k]
        a = _atr_at(t_end, atr, D * 1440 + t1)
        if not (a > 0):
            continue
        r = c[B - 1] - ref
        if abs(r) < thr * a or r == 0.0:
            continue
        d = 1 if r > 0 else -1
        if rev == 1:
            d = -d
        if (dirs == 1 and d < 0) or (dirs == -1 and d > 0):
            continue
        IE[m] = B; DD[m] = d; RD[m] = stopk * a; TP[m] = tpr; IX[m] = X; m += 1
    return IE[:m], DD[:m], RD[:m], TP[:m], IX[:m]
