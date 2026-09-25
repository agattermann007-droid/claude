"""RSI21 Eigenkapital - Signale (RSI21 Continuation wie DEADBAND 6.60, Replikat_v6/sig5.r21_signals), parametrisierbar.

Zweistufig, damit Parameter-Raster schnell laufen:
  features(D)  je Symbol, Zeitebene (M15/M30/H1) und Kerze k >= 1 alle Groessen zum Signalzeitpunkt T = Beginn der Kerze k
               (RSI und ATR der geschlossenen Kerze k-1, RSI des anderen Symbols auf derselben Zeitebene, Tagesregime aus
               Vortagesschluss gegen SMA200/SMA100, H4-Divergenz) - unabhaengig von Schwellen und Zeitfenstern.
  select(F, ...) Schwellen, Filter und Folgesignal-Logik -> Signalliste wie sig5.r21_signals
               (T, sym 0 = Gold / 1 = NAS, tf 0/1/2 = M15/M30/H1, dir, rd = Stop-Abstand, folge).

Mit den Voreinstellungen ist select(features(D)) identisch mit sig5.r21_signals(D) (Pruefung t_ek_sig.py).
Zusaetzliche Schalter (alle Voreinstellungen = 6.60): Zeitebenen je Symbol, Richtungen, Regime-/Gate-/Bestaetigungs-Filter,
Folgesignal-Fenster, erstes Signal einer Bewegung.
"""
import os, sys
import numpy as np
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Replikat_v6"))
import prep5 as P                                                   # noqa: E402
import sig5 as S5                                                   # noqa: E402

TFS = (15, 30, 60)
KEYS = ("m15", "m30", "h1")
SYMS = ("XAU", "NAS")


def features(D, rsi_len=21, atr_len=14, sma_min=50, sma_long=200, sma_fast=100, div_radius=2, div_gap=2.0, cross_ea=False):
    """cross_ea: RSI des anderen Symbols wie im EA RSI21_EK (letzte Kerze, die vor T begann); sonst wie sig5/6.60 (Kerze
    vor der letzten Kerze mit Beginn <= T - unterscheidet sich nur, wenn das andere Symbol bei T keine Kerze hat)."""
    rsiT = {}; atrT = {}
    for s in SYMS:
        for tf, kk in zip(TFS, KEYS):
            B = D[s][kk]
            rsiT[(s, tf)] = P.rsi_wilder(B["c"], rsi_len)
            atrT[(s, tf)] = P.atr_sma(B["h"], B["l"], B["c"], atr_len)
    cols = {k: [] for k in ("T", "sym", "tf", "rsi", "atr", "ro", "regok", "cprev", "maL", "maS", "divok", "divv")}
    for si, s in enumerate(SYMS):
        o = SYMS[1 - si]
        D1 = D[s]["d1"]
        maL = P.sma_partial(D1["c"], sma_long, sma_min)
        maS = P.sma_partial(D1["c"], sma_fast, sma_min)
        # H4-Divergenz (UTC-Buckets aus H1, wie sig5.r21_h4_div, mit waehlbarem Radius/Abstand)
        H1 = D[s]["h1"]
        nyh1 = H1["t"]
        utc = nyh1 + np.where(S5.us_dst_ny(nyh1), 240, 300)
        bucket = utc // 240
        ub, first = np.unique(bucket, return_index=True)
        last = np.r_[first[1:] - 1, len(bucket) - 1]
        closes = H1["c"][last]
        rsi4 = P.rsi_wilder(closes, rsi_len)
        rsi4 = np.where(np.isfinite(rsi4), rsi4, 50.0)
        dv = S5._divergence_series(closes, rsi4, div_radius, float(div_gap), rsi_len, 150)
        for ti, (tf, kk) in enumerate(zip(TFS, KEYS)):
            B = D[s][kk]
            n = len(B["t"])
            k = np.arange(1, n)
            T = B["t"][k].astype(np.int64)
            r = rsiT[(s, tf)][k - 1]
            a = atrT[(s, tf)][k - 1]
            ob = D[o][kk]
            rov = rsiT[(o, tf)]
            if cross_ea:
                pe = np.searchsorted(ob["t"], T, side="left") - 1
                ro = np.where(pe >= 0, rov[np.clip(pe, 0, len(rov) - 1)], np.nan)
            else:
                po = np.searchsorted(ob["t"], T, side="right") - 1
                ro = np.where(po - 1 >= 0, rov[np.clip(po - 1, 0, len(rov) - 1)], np.nan)
            pday = (T + 420) // 1440
            di = np.searchsorted(D1["key"], pday)
            dm1 = np.clip(di - 1, 0, len(D1["key"]) - 1)
            regok = (di >= 1) & np.isfinite(maL[dm1]) & np.isfinite(maS[dm1])
            u = T + np.where(S5.us_dst_ny(T), 240, 300)
            bi = np.minimum(np.searchsorted(ub, u // 240), len(dv) - 1)
            dval = dv[bi]
            cols["T"].append(T); cols["sym"].append(np.full(len(T), si, np.int64)); cols["tf"].append(np.full(len(T), ti, np.int64))
            cols["rsi"].append(r); cols["atr"].append(a); cols["ro"].append(ro)
            cols["regok"].append(regok); cols["cprev"].append(D1["c"][dm1]); cols["maL"].append(maL[dm1]); cols["maS"].append(maS[dm1])
            cols["divok"].append(dval != -9); cols["divv"].append(np.where(dval == -9, 0, dval).astype(np.int64))
    F = {k: np.concatenate(v) for k, v in cols.items()}
    order = np.lexsort((F["tf"], F["T"], F["sym"]))                  # je Symbol zeitlich, dann Zeitebene
    F = {k: v[order] for k, v in F.items()}
    F["nyh"] = (F["T"] % 1440) / 60.0
    F["rsi_len"] = rsi_len
    return F


@njit(cache=True)
def _folge(sym, T, dr, folge_min):
    """Folgesignal wie sig5/EA: je Symbol und Richtung Zeit des letzten gueltigen Signals (beliebige Zeitebene); ein Signal
    ist Folgesignal, wenn ein frueheres (kleinere Kerzenzeit) hoechstens folge_min Minuten alt ist. Zeilen sind nach
    (sym, T) sortiert."""
    n = len(T)
    out = np.zeros(n, np.int64)
    i = 0
    last0 = 0; last1 = 0; cur = -1
    while i < n:
        if sym[i] != cur:
            cur = sym[i]; last0 = 0; last1 = 0
        j = i
        has0 = False; has1 = False
        while j < n and sym[j] == cur and T[j] == T[i]:
            if dr[j] > 0:
                has0 = True
            else:
                has1 = True
            j += 1
        tt = T[i]
        f0 = (folge_min <= 0) or (last0 > 0 and last0 < tt and tt - last0 <= folge_min)
        f1 = (folge_min <= 0) or (last1 > 0 and last1 < tt and tt - last1 <= folge_min)
        for q in range(i, j):
            out[q] = 1 if ((dr[q] > 0 and f0) or (dr[q] < 0 and f1)) else 0
        if has0 and tt > last0:
            last0 = tt
        if has1 and tt > last1:
            last1 = tt
        i = j
    return out


def select(F, oben=75.0, unten=None, cross=55.0, ab=9.5, nas_bis=13.0, gold_bis=17.0, gold_ohne_h1=True, use_div=True,
           stop_atr=2.0, folge_min=240, tf_gold=(0, 1, 2), tf_nas=(0, 1, 2), longs=True, shorts=True,
           short_regime=True, nas_long_regime=True, gold_gate=True, cross_on=True, nas_ab=None, gold_ab=None):
    """Signalliste wie sig5.r21_signals. unten=None -> 100 - oben. nas_ab/gold_ab: eigener Beginn je Symbol (NY-Stunde)."""
    if unten is None:
        unten = 100.0 - oben
    r = F["rsi"]; sym = F["sym"]; tf = F["tf"]; nyh = F["nyh"]
    isg = sym == 0
    a0 = np.where(isg, ab if gold_ab is None else gold_ab, ab if nas_ab is None else nas_ab)
    bis = np.where(isg, gold_bis, nas_bis)
    ok = F["regok"] & np.isfinite(r) & (nyh >= a0) & (nyh < bis)
    tfok = np.zeros(len(r), bool)
    for t in tf_gold:
        tfok |= isg & (tf == t)
    for t in tf_nas:
        tfok |= (~isg) & (tf == t)
    if gold_ohne_h1:
        tfok &= ~(isg & (tf == 2))
    ok &= tfok
    dr = np.where(r > oben, 1, np.where(r < unten, -1, 0))
    if not longs:
        dr[dr > 0] = 0
    if not shorts:
        dr[dr < 0] = 0
    ok &= dr != 0
    c = F["cprev"]; mL = F["maL"]; mS = F["maS"]
    shortOk = (c < mL) | (c < mS)
    gateL = (c > mL) & (c > mS)
    gateS = (c < mL) & (c < mS)
    regv = np.where(c > mL, 1, -1)
    if short_regime:
        ok &= ~((dr < 0) & ~shortOk)
    if nas_long_regime:
        ok &= ~((dr > 0) & (~isg) & (regv < 0))
    ro = F["ro"]
    if cross_on:
        crossOk = np.where(dr > 0, ro > cross, ro < 100.0 - cross) & np.isfinite(ro)
    else:
        crossOk = np.ones(len(r), bool)
    gate = np.where(dr > 0, gateL, gateS) if gold_gate else np.zeros(len(r), bool)
    ok &= np.where(isg, crossOk | gate, crossOk)
    if use_div:
        ok &= F["divok"] & ~(dr * F["divv"] < 0)
    a = F["atr"]
    ok &= np.isfinite(a) & (a > 0)
    idx = np.nonzero(ok)[0]
    fo = _folge(sym[idx], F["T"][idx], dr[idx], int(folge_min))
    out = dict(T=F["T"][idx], sym=sym[idx], tf=tf[idx], dir=dr[idx].astype(np.int64), rd=stop_atr * a[idx], folge=fo)
    order = np.lexsort((out["tf"], out["sym"], out["T"]))
    return {k: v[order] for k, v in out.items()}
