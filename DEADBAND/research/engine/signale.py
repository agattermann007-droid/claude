"""Signale: H1-Ausbruch (DEADBAND-Modul) fuer beliebige Symbole und der Einzelpfad je Symbol.

h1_signale() ist sig5.db_candidates (Replikat_v6) mit Parametern statt fester Gold/NAS-Werte; Test:
tests/test_signale.py prueft Gleichheit mit sig5 fuer XAU und NAS. Regeln wie EA HandleSymbol:
  Schluss der M15-Signalkerze jenseits Hoch/Tief der letzten abgeschlossenen H1-Kerze, EMA50 (D1, Vortag), Session-VWAP,
  RSI14 > / < 50, MACD-Histogramm, Kerzenqualitaet >= ClsMin, Tick-Volumen >= Schnitt 50; Stop 3 x ATR14 (M15);
  dynamischer Faktor (ATR-Perzentil 500, Stochastik); Einstieg am Open der naechsten M15-Kerze.
einzelpfad() waehlt daraus die Trades eines Symbols wie das H1-Modul: Session 3-13 NY, hoechstens 1 Trade je Prop-Tag,
nach 2 Verlusten am Tag Schluss, eine Position je Symbol, kein Einstieg in den 5 min vor dem Freitags-Schluss.
"""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

import prep5 as P

from . import handel as HD


def baue_symbol(ny, o, h, l, c, v, sp):
    """Struktur wie prep5.build()[sym] (sp in Preis-Einheiten)."""
    d = dict(ny=np.asarray(ny, np.int64), o=np.asarray(o, float), h=np.asarray(h, float), l=np.asarray(l, float),
             c=np.asarray(c, float), v=np.asarray(v, float), sp=np.asarray(sp, float))
    ny = d["ny"]
    d["pday"] = (ny + 420) // 1440
    d["m15"] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 15)
    d["m30"] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 30)
    d["h1"] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 60)
    d["d1"] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 1440, offset=420)
    return d


def indikatoren_m15(d):
    """ATR14 (SMA des TR wie iATR) auf M15 - Stop-Abstand der Familien = 3 x ATR der Signalkerze."""
    B = d["m15"]
    return P.atr_sma(B["h"], B["l"], B["c"], 14)


def h1_signale(d, clsmin, allow_short, punkt=0.01, stoplvl=0.0):
    """Alle H1-Ausbruchssignale (ohne Session/Tageslimits). Rueckgabe wie sig5.db_candidates + 'j' (Signalkerze M15)."""
    B = d["m15"]; H1 = d["h1"]; D1 = d["d1"]
    c = B["c"]; h = B["h"]; l = B["l"]; v = B["v"]; t = B["t"]
    n = len(c)
    rsi = P.rsi_wilder(c, 14)
    atr = P.atr_sma(h, l, c, 14)
    stoK, stoD = P.stoch_mt5(h, l, c, 14, 3, 3)
    macd = P.ema_mt5(c, 12) - P.ema_mt5(c, 26)
    hist = macd - P.sma(macd, 9)
    vrel = v / P.sma(v, 50)
    ratio = atr / c
    pz = np.full(n, np.nan)
    L = 500
    r2 = np.where(np.isfinite(ratio), ratio, np.inf)
    if n >= L:
        win = sliding_window_view(r2, L)
        pz[L - 1:] = (win < r2[L - 1:, None]).sum(axis=1) / float(L)
    emaD = P.ema_mt5(D1["c"], 50)
    pday = (t + 420) // 1440
    di = np.searchsorted(D1["key"], pday)
    ema_prev = np.where(di >= 1, emaD[np.clip(di - 1, 0, len(emaD) - 1)], np.nan)
    ema_prev[di < 50] = np.nan
    hk = t // 60
    pos = np.searchsorted(H1["key"], hk)
    prev = pos - 1
    okh = prev >= 0
    hH1 = np.where(okh, H1["h"][np.clip(prev, 0, None)], np.nan)
    lH1 = np.where(okh, H1["l"][np.clip(prev, 0, None)], np.nan)
    tp = (h + l + c) / 3.0
    w = np.where(v > 0, v, 1.0)
    cpv = np.cumsum(tp * w); cw = np.cumsum(w)
    ds = np.r_[0, np.nonzero(np.diff(pday))[0] + 1]
    dstart = np.repeat(ds, np.diff(np.r_[ds, n]))
    pv0 = np.where(dstart > 0, cpv[np.maximum(dstart - 1, 0)], 0.0)
    w0 = np.where(dstart > 0, cw[np.maximum(dstart - 1, 0)], 0.0)
    vwap = (cpv - pv0) / np.maximum(cw - w0, 1e-12)
    k = np.arange(1, n); j = k - 1
    T = t[k]
    nyh = (T % 1440) / 60.0
    rng = h[j] - l[j]
    clsP = np.where(rng > 0, (c[j] - l[j]) / np.where(rng > 0, rng, 1.0), 0.5)
    base = np.isfinite(hH1[k]) & np.isfinite(ema_prev[k]) & np.isfinite(rsi[j]) & np.isfinite(atr[j]) \
        & np.isfinite(pz[j]) & np.isfinite(stoK[j]) & np.isfinite(stoD[j]) & np.isfinite(hist[j]) \
        & np.isfinite(vrel[j]) & (vwap[j] > 0)
    volok = vrel[j] >= 1.0
    Lg = base & volok & (c[j] > hH1[k]) & (c[j] > ema_prev[k]) & (c[j] > vwap[j]) & (rsi[j] > 50) & (clsP >= clsmin) & (hist[j] > 0)
    Sg = base & volok & (c[j] < lH1[k]) & (c[j] < ema_prev[k]) & (c[j] < vwap[j]) & (rsi[j] < 50) & ((1 - clsP) >= clsmin) & (hist[j] < 0)
    if not allow_short:
        Sg[:] = False
    sel = np.nonzero(Lg | Sg)[0]
    dirs = np.where(Lg[sel], 1, -1)
    rd = 3.0 * atr[j[sel]]
    f = np.clip(1.40 - 0.80 * pz[j[sel]], 0.35, 2.00)
    passt = np.where(dirs > 0, stoK[j[sel]] > stoD[j[sel]], stoK[j[sel]] < stoD[j[sel]])
    f = f * np.where(passt, 1.2, 0.8)
    good = (rd > 50 * punkt) & (rd >= stoplvl)
    sel, dirs, rd, f = sel[good], dirs[good], rd[good], f[good]
    kk = k[sel]
    return dict(T=t[kk], dir=dirs, rd=rd, f=f, m15=kk, i5=B["first"][kk], nyh=nyh[sel], j=kk - 1,
                hH1=hH1[kk], lH1=lH1[kk])


def einzelpfad(sig, M, sym, ziel_r, sess=(3.0, 13.0), max_trades=1, max_verluste=2, we_schluss=16.75):
    """Trades des H1-Moduls auf einem Symbol (eine Position, Tageslimits). Rueckgabe: Index der genommenen Signale und
    Handelsergebnisse (handel.ERG)."""
    order = np.argsort(sig["i5"], kind="stable")
    genommen = []
    ergebnisse = []
    frei_ab = -1
    tag = -1; n_tag = 0; v_tag = 0
    for a in order:
        i5 = int(sig["i5"][a])
        if sig["nyh"][a] < sess[0] or sig["nyh"][a] >= sess[1]:
            continue
        if i5 <= frei_ab:
            continue
        pt = int(M["pday"][i5])
        if pt != tag:
            tag = pt; n_tag = 0; v_tag = 0
        if n_tag >= max_trades or v_tag >= max_verluste:
            continue
        if M["dow"][i5] == 5 and M["nyh"][i5] >= we_schluss - 5.0 / 60.0:
            continue
        e = HD.handel(M, sym, [i5], [int(sig["dir"][a])], [float(sig["rd"][a])], ziel_r)[0]
        genommen.append(a); ergebnisse.append(e)
        n_tag += 1
        aus = int(e[2])
        if int(M["pday"][aus]) == tag and e[1] < 0:
            v_tag += 1
        frei_ab = aus
    return np.array(genommen, np.int64), (np.array(ergebnisse) if ergebnisse else np.zeros((0, 7)))
