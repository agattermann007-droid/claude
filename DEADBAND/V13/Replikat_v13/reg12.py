"""Replikat v12 - Kandidaten fuer das Regime "Fades aus" (Portfolio-Waechter nicht live), Prompt 9.3.

Alle Generatoren liefern Bloecke im Format von gen11 (t, sym, dir, ent, fix, sl, tp, tx). Einstieg am Open der
Einstiegsminute (Markt, fix = 0; Long zum Ask), Stop/Ziel absolut, Zeit-Ausstieg tx (NY-Minute).
  orb      NAS Opening-Range-Breakout: Richtung der ersten n Minuten ab 9:30, Einstieg 9:30+n
  imom     NAS Intraday-Momentum: Richtung (Vortagsschluss -> t_sig), Einstieg t_in, Ausstieg x
  brk      Ausbruch statt Fade: M5-Schluss ausserhalb einer Fade-Range -> Einstieg in Ausbruchsrichtung
  gbrk     Gold: Ausbruch aus einer Range in Richtung des Trends (Schluss D1 gegen SMA)
gate(block, live_at, want)  behaelt nur Signale, bei denen der Portfolio-Waechter == want ist (False = Fades aus).
"""
import numpy as np
from numba import njit
import gen11 as G


@njit(cache=True)
def _orb(ny, o, h, l, c, sp, days, t_end, atr, n, dirs, smode, s, crv, x, t0):
    nd = days.shape[0]
    T = np.zeros(nd, np.int64); DD = np.zeros(nd, np.int64); EN = np.zeros(nd); SL = np.zeros(nd); TP = np.zeros(nd)
    TX = np.zeros(nd, np.int64); m = 0
    for q in range(nd):
        D = days[q]
        dow = (D + 4) % 7
        if dow < 1 or dow > 5:
            continue
        a = np.searchsorted(ny, D * 1440 + t0)
        b = np.searchsorted(ny, D * 1440 + t0 + n)
        if a >= ny.shape[0] or ny[a] != D * 1440 + t0 or b - a < max(1, int(0.8 * n)) or b >= ny.shape[0]:
            continue
        if ny[b] - (D * 1440 + t0 + n) > 2:
            continue
        hh = h[a]; ll = l[a]
        for j in range(a, b):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        mv = c[b - 1] - o[a]
        if mv == 0.0:
            continue
        d = 1 if mv > 0 else -1
        if dirs != 0 and d != dirs:
            continue
        A = G._atr_at(t_end, atr, D * 1440 + t0)
        if not (A > 0):
            continue
        spr = sp[b]
        ent = o[b] + (spr if d > 0 else 0.0)
        if smode == 0:
            st = ent - d * s * A
        else:
            st = (ll - s * A) if d > 0 else (hh + spr + s * A)
        rd = (ent - st) * d
        if rd <= max(6.0 * spr, 0.03 * A):
            continue
        T[m] = ny[b]; DD[m] = d; EN[m] = ent; SL[m] = st
        TP[m] = ent + d * crv * rd if crv > 0 else 0.0
        TX[m] = D * 1440 + x; m += 1
    return T[:m], DD[:m], EN[:m], SL[:m], TP[:m], TX[:m]


def _days(ny):
    d = np.unique(ny // 1440)
    return d[((d + 4) % 7 >= 1) & ((d + 4) % 7 <= 5)]


def _mk(name, k, T, DD, EN, SL, TP, TX):
    return dict(name=name, sym=np.full(len(T), k, np.int64), t=T, dir=DD, ent=EN, fix=np.zeros(len(T), np.int64),
                sl=SL, tp=TP, tx=TX)


def orb(n=5, dirs=0, smode=0, s=0.10, crv=0.0, x=955, t0=570, sym="NAS", name=None):
    d = G.data()[sym]; t_end, atr = G.daily_atr(sym)
    r = _orb(d["ny1"], d["o1"], d["h1m"], d["l1"], d["c1"], d["sp1"], _days(d["ny1"]), t_end, atr, n, dirs, smode, s, crv,
             x, t0)
    return _mk(name or f"ORB{n}_{dirs}_{smode}_{s}_{crv}", G.SYM[sym], *r)


@njit(cache=True)
def _imom(ny, o, h, l, c, sp, days, t_end, atr, t_ref, t_sig, t_in, x, s, minr, dirs, crv):
    nd = days.shape[0]
    T = np.zeros(nd, np.int64); DD = np.zeros(nd, np.int64); EN = np.zeros(nd); SL = np.zeros(nd); TP = np.zeros(nd)
    TX = np.zeros(nd, np.int64); m = 0
    for q in range(1, nd):
        D = days[q]
        P0 = days[q - 1]
        # Referenz: letzter Schluss vor t_ref des Vortags (Handelstag davor)
        r = np.searchsorted(ny, P0 * 1440 + t_ref) - 1
        if r < 0 or ny[r] < P0 * 1440 + t_ref - 30:
            continue
        sg = np.searchsorted(ny, D * 1440 + t_sig) - 1
        if sg < 0 or ny[sg] < D * 1440 + t_sig - 5:
            continue
        b = np.searchsorted(ny, D * 1440 + t_in)
        if b >= ny.shape[0] or ny[b] - (D * 1440 + t_in) > 2:
            continue
        A = G._atr_at(t_end, atr, D * 1440 + t_in)
        if not (A > 0):
            continue
        mv = c[sg] - c[r]
        if abs(mv) < minr * A or mv == 0.0:
            continue
        d = 1 if mv > 0 else -1
        if dirs != 0 and d != dirs:
            continue
        spr = sp[b]
        ent = o[b] + (spr if d > 0 else 0.0)
        st = ent - d * s * A
        T[m] = ny[b]; DD[m] = d; EN[m] = ent; SL[m] = st
        TP[m] = ent + d * crv * s * A if crv > 0 else 0.0
        TX[m] = D * 1440 + x; m += 1
    return T[:m], DD[:m], EN[:m], SL[:m], TP[:m], TX[:m]


def imom(t_sig=600, t_in=930, x=955, s=0.3, minr=0.0, dirs=0, crv=0.0, t_ref=960, sym="NAS", name=None):
    d = G.data()[sym]; t_end, atr = G.daily_atr(sym)
    r = _imom(d["ny1"], d["o1"], d["h1m"], d["l1"], d["c1"], d["sp1"], _days(d["ny1"]), t_end, atr, t_ref, t_sig, t_in,
              x, s, minr, dirs, crv)
    return _mk(name or f"IM{t_sig}_{t_in}_{x}_{s}_{minr}_{dirs}", G.SYM[sym], *r)


@njit(cache=True)
def _brk(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, smode, sb, crv, dirs, mx, minr):
    """M5: erste Kerze, die ausserhalb der Range [r0, r1) schliesst, im Fenster [r1, tend) -> Einstieg am Open der
    naechsten M5-Kerze in Ausbruchsrichtung. Stop smode 0 = Range-Mitte, 1 = Gegenseite, 2 = sb x ATR."""
    n = days.shape[0]
    T = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); EN = np.zeros(n); SL = np.zeros(n); TP = np.zeros(n)
    TX = np.zeros(n, np.int64); m = 0
    for q in range(n):
        D = days[q]
        s = np.searchsorted(ny, D * 1440 + r0); e = np.searchsorted(ny, D * 1440 + r1)
        if e - s < (r1 - r0) // 5 * 0.6 or e >= ny.shape[0]:
            continue
        a = G._atr_at(t_end, atr, D * 1440 + r0)
        if not (a > 0):
            continue
        hh = h[s]; ll = l[s]
        for j in range(s, e):
            if h[j] > hh: hh = h[j]
            if l[j] < ll: ll = l[j]
        rng = hh - ll
        if rng <= 0.0 or rng > mx * a or rng < minr * a:
            continue
        te = np.searchsorted(ny, D * 1440 + tend)
        for j in range(e, te):
            d = 0
            if c[j] > hh:
                d = 1
            elif c[j] < ll:
                d = -1
            if d == 0:
                continue
            if dirs != 0 and d != dirs:
                break
            B = j + 1
            if B >= ny.shape[0] or ny[B] >= D * 1440 + xm or ny[B] - ny[j] > 10:
                break
            spr = sp[B]
            ent = o[B] + (spr if d > 0 else 0.0)
            if smode == 0:
                st = 0.5 * (hh + ll)
            elif smode == 1:
                st = ll if d > 0 else hh + spr
            else:
                st = ent - d * sb * a
            rd = (ent - st) * d
            if rd <= max(6.0 * spr, 0.03 * a):
                break
            T[m] = ny[B]; DD[m] = d; EN[m] = ent; SL[m] = st
            TP[m] = ent + d * crv * rd if crv > 0 else 0.0
            TX[m] = D * 1440 + xm; m += 1
            break
    return T[:m], DD[:m], EN[:m], SL[:m], TP[:m], TX[:m]


def brk(sym, r0, L, tlen, xoff, smode=0, sb=0.3, crv=1.0, dirs=0, mx=0.6, minr=0.0, name=None):
    d = G.data()[sym]; t_end, atr = G.daily_atr(sym)
    r1, te, xm = G.fade_times(r0, L, tlen, xoff)
    r = _brk(d["ny"], d["o"], d["h"], d["l"], d["c"], d["sp"], _days(d["ny"]), t_end, atr, r0, r1, te, xm, smode, sb,
             crv, dirs, mx, minr)
    return _mk(name or f"BRK{sym}{r0}_{L}_{smode}_{crv}_{dirs}", G.SYM[sym], *r)


def brk_fade(name, **kw):
    """Ausbruch auf der Range eines Listen-Fades (gleiche Zeiten, Range-Filter mx)."""
    for (nm, s, r0, L, tlen, xoff, buf, tgt, dirs, mx) in G.FADE_STANDARD:
        if nm == name:
            kw.setdefault("mx", mx)
            return brk(s, r0, L, tlen, xoff, name="B" + nm, **kw)
    raise KeyError(name)


def d1_trend(sym, n=50):
    """+1/-1 je Tag: Schluss D1 des Vortags ueber/unter SMA(n) der D1-Schluesse (bis zum Vortag)."""
    d1 = G.data()[sym]["d1"]
    c = d1["c"]
    cs = np.r_[0.0, np.cumsum(c)]
    sma = np.full(len(c), np.nan)
    sma[n - 1:] = (cs[n:] - cs[:-n]) / n
    tr = np.where(c > sma, 1, np.where(c < sma, -1, 0))
    return d1["t"] + 1440, tr          # gueltig ab Ende der Tageskerze


def gbrk(r0=-360, L=480, tlen=300, xoff=60, smode=0, sb=0.3, crv=1.5, n=50, mx=1.0, minr=0.0, sym="XAU", name=None):
    """Ausbruch in Trendrichtung: Signal nur, wenn die Richtung zum D1-Trend passt."""
    b = brk(sym, r0, L, tlen, xoff, smode=smode, sb=sb, crv=crv, dirs=0, mx=mx, minr=minr)
    t_end, tr = d1_trend(sym, n)
    k = np.searchsorted(t_end, b["t"], side="right") - 1
    ok = (k >= 0) & (tr[np.maximum(k, 0)] == b["dir"])
    out = {kk: (v[ok] if isinstance(v, np.ndarray) and len(v) == len(ok) else v) for kk, v in b.items()}
    out["name"] = name or f"GBRK{r0}_{L}_{smode}_{crv}_{n}"
    return out


def gate(b, live_at, want=False):
    m = np.array([live_at(int(t))[0] == want for t in b["t"]], bool)
    out = {k: (v[m] if isinstance(v, np.ndarray) and len(v) == len(m) else v) for k, v in b.items()}
    return out


def sub(b, m):
    return {k: (v[m] if isinstance(v, np.ndarray) and len(v) == len(m) else v) for k, v in b.items()}
