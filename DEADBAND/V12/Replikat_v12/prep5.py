"""DEADBAND 5.00 KOMBI Replikat - Datenaufbereitung (GFT-M5-Exporte 2022-01 .. 2026-09).

Zeitachse: NY-Minuten seit Epoche (int64). Serverzeit = NY + 7 h (GFT, 17:00 NY = 00:00 Server).
Kurse = Bid, Spread in Preis-Einheiten (Punkte * 0.01).

Indikatoren wie MT5:
  RSI  = Wilder (erstes Mittel = SMA), ATR = SMA des True Range (iATR), EMA-Start = erster Wert,
  Stochastik(14,3,3,SMA,LowHigh) = 100*Summe(C-LL)/Summe(HH-LL) ueber 3, Signal = SMA 3,
  MACD 12/26 EMA, Signal = SMA 9.
Tagesbalken = Servertag (17:00 NY bis 17:00 NY).
"""
import numpy as np, pandas as pd, os
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
OUT = os.path.join(HERE, "cache")
os.makedirs(OUT, exist_ok=True)

SYMS = ("XAU", "NAS")
FILES = {"XAU": "XAUUSD.x_M5.csv", "NAS": "NAS100.x_M5.csv"}
POINT = 0.01
DEFSPREAD = {"XAU": 0.32, "NAS": 1.63}


# ------------------------------------------------------------------ Grundfunktionen
@njit(cache=True)
def ema_mt5(x, n):
    out = np.empty_like(x)
    a = 2.0 / (n + 1.0)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = out[i - 1] + a * (x[i] - out[i - 1])
    return out


@njit(cache=True)
def sma(x, n):
    out = np.full(len(x), np.nan)
    s = 0.0
    for i in range(len(x)):
        s += x[i]
        if i >= n:
            s -= x[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


@njit(cache=True)
def sma_partial(x, n, nmin):
    """SMA, am Anfang mit weniger Werten (mindestens nmin) - Ersatz fuer fehlende Vorlaufdaten."""
    out = np.full(len(x), np.nan)
    s = 0.0
    for i in range(len(x)):
        s += x[i]
        if i >= n:
            s -= x[i - n]
        m = i + 1 if i < n else n
        if m >= nmin:
            out[i] = s / m
    return out


@njit(cache=True)
def rsi_wilder(c, n):
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    g = 0.0; l = 0.0
    for i in range(1, n + 1):
        d = c[i] - c[i - 1]
        if d > 0:
            g += d
        else:
            l -= d
    g /= n; l /= n
    out[n] = 100.0 if l == 0.0 else 100.0 - 100.0 / (1.0 + g / l)
    for i in range(n + 1, len(c)):
        d = c[i] - c[i - 1]
        up = d if d > 0 else 0.0
        dn = -d if d < 0 else 0.0
        g = (g * (n - 1) + up) / n
        l = (l * (n - 1) + dn) / n
        if l == 0.0:
            out[i] = 50.0 if g == 0.0 else 100.0
        else:
            out[i] = 100.0 - 100.0 / (1.0 + g / l)
    return out


@njit(cache=True)
def atr_sma(h, l, c, n):
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    for i in range(1, len(c)):
        a = h[i] - l[i]
        b = abs(h[i] - c[i - 1])
        d = abs(l[i] - c[i - 1])
        tr[i] = max(a, max(b, d))
    return sma(tr, n)


@njit(cache=True)
def stoch_mt5(h, l, c, kp, slowing, dp):
    n = len(c)
    hh = np.full(n, np.nan); ll = np.full(n, np.nan)
    for i in range(kp - 1, n):
        mx = -1e18; mn = 1e18
        for j in range(i - kp + 1, i + 1):
            if h[j] > mx:
                mx = h[j]
            if l[j] < mn:
                mn = l[j]
        hh[i] = mx; ll[i] = mn
    main = np.full(n, np.nan)
    for i in range(kp - 1 + slowing - 1, n):
        num = 0.0; den = 0.0
        for j in range(i - slowing + 1, i + 1):
            num += c[j] - ll[j]
            den += hh[j] - ll[j]
        main[i] = 100.0 if den == 0.0 else 100.0 * num / den
    sig = np.full(n, np.nan)
    for i in range(n):
        if i >= dp - 1:
            ok = True; s = 0.0
            for j in range(i - dp + 1, i + 1):
                if np.isnan(main[j]):
                    ok = False
                    break
                s += main[j]
            if ok:
                sig[i] = s / dp
    return main, sig


def load(sym):
    ex = pd.read_csv(os.path.join(DATA, FILES[sym]), sep="\t")
    ex.columns = [c.strip("<>").lower() for c in ex.columns]
    t = pd.to_datetime(ex["date"] + " " + ex["time"], format="%Y.%m.%d %H:%M:%S")
    ny = (t - pd.Timedelta(hours=7)).values.astype("datetime64[m]").astype(np.int64)
    o = ex["open"].to_numpy(float); h = ex["high"].to_numpy(float)
    l = ex["low"].to_numpy(float); c = ex["close"].to_numpy(float)
    sp = ex["spread"].to_numpy(float) * POINT
    sp = np.where(np.isnan(sp) | (sp <= 0), DEFSPREAD[sym], sp)
    v = ex["tickvol"].to_numpy(float)
    order = np.argsort(ny, kind="stable")
    return dict(ny=ny[order], o=o[order], h=h[order], l=l[order], c=c[order], sp=sp[order], v=v[order])


def agg(ny, o, h, l, c, v, minutes, offset=0):
    """Balken aus M5 gruppieren: Schluessel = floor((ny+offset)/minutes). Rueckgabe je Balken + first/last M5-Index."""
    key = (ny + offset) // minutes
    uniq, first = np.unique(key, return_index=True)
    last = np.r_[first[1:] - 1, len(ny) - 1]
    oo = o[first]; cc = c[last]
    hh = np.maximum.reduceat(h, first); ll = np.minimum.reduceat(l, first)
    vv = np.add.reduceat(v, first)
    t0 = uniq * minutes - offset          # Balkenbeginn in NY-Minuten
    return dict(t=t0, o=oo, h=hh, l=ll, c=cc, v=vv, first=first, last=last, key=uniq)


def build():
    D = {}
    for s in SYMS:
        d = load(s)
        ny = d["ny"]
        # Servertag (Prop-Tag): (ny + 7 h) // 1440
        pday = (ny + 420) // 1440
        d["pday"] = pday
        m15 = agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 15)
        m30 = agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 30)
        h1 = agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 60)
        d1 = agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 1440, offset=420)   # Servertag
        d["m15"], d["m30"], d["h1"], d["d1"] = m15, m30, h1, d1
        D[s] = d
        print(f"{s}: {len(ny)} M5, {len(m15['t'])} M15, {len(h1['t'])} H1, {len(d1['t'])} D1 "
              f"{np.datetime64(int(ny[0]), 'm')} .. {np.datetime64(int(ny[-1]), 'm')}")
    return D


if __name__ == "__main__":
    build()
