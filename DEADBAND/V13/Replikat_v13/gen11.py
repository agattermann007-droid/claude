"""Replikat v11 - Signal-Generatoren aller V10-Stroeme (ohne Kontozustand).

Jede Funktion liefert einen Block (dict) mit Arrays je Signal:
  t   NY-Minute des Einstiegs (Open dieser Minute; bei SR die Minute, in der der Einstieg im Tick liegt)
  sym 0 = XAU, 1 = NAS;  dir +1/-1
  ent geschaetzter Einstieg (Long = Ask), fix = 1: Einstieg genau zu diesem Preis (Tick-Einstieg SR), 0: Markt am Open
  sl, tp absolute Preise (tp 0 = kein Ziel); tx NY-Minute des Zeit-Ausstiegs (Open der ersten Minute ab tx)
Die Logik folgt Zeile fuer Zeile den MQL5-Funktionen FadeKerze, SpikeKerze, LwKerze, AsiaKerze, TdKerze, SrTick,
GridKerze/GridFadeOk und FadePortfolioPF aus DEADBAND_V10.mq5.
"""
import numpy as np, datetime as dt
from numba import njit
import prep11 as P
import sig5 as S5

SYM = {"XAU": 0, "NAS": 1}
MPP = np.array([100.0, 10.0])
COMM = np.array([5.0, 0.0])           # $ je Lot (Gold), wie Replikat v5/v6
_D = None


def data():
    global _D
    if _D is None:
        _D = P.build()
    return _D


# ------------------------------------------------------------------ Feiertage (NzFreierTag)
def _nth_weekday(y, m, wd, n):          # wd: 0 = Montag
    d = dt.date(y, m, 1)
    d += dt.timedelta(days=(wd - d.weekday()) % 7)
    return d + dt.timedelta(days=7 * (n - 1))


def _last_weekday(y, m, wd):
    d = dt.date(y, m + 1, 1) - dt.timedelta(days=1) if m < 12 else dt.date(y, 12, 31)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)


def _easter(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; mon = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(y, mon, day)


def _observed(d):
    if d.weekday() == 5:
        return d - dt.timedelta(days=1)
    if d.weekday() == 6:
        return d + dt.timedelta(days=1)
    return d


def us_frei(y0=2010, y1=2018):
    """US-Boersenfeiertage und verkuerzte Tage wie die eingebaute EA-Liste (die EA-Liste beginnt 2019)."""
    out = set()
    for y in range(y0, y1 + 1):
        ds = [_observed(dt.date(y, 1, 1)), _nth_weekday(y, 1, 0, 3), _nth_weekday(y, 2, 0, 3),
              _easter(y) - dt.timedelta(days=2), _last_weekday(y, 5, 0), _observed(dt.date(y, 7, 4)),
              _nth_weekday(y, 9, 0, 1), _nth_weekday(y, 11, 3, 4), _nth_weekday(y, 11, 3, 4) + dt.timedelta(days=1),
              _observed(dt.date(y, 12, 25))]
        j3 = dt.date(y, 7, 3)
        if j3.weekday() < 5 and dt.date(y, 7, 4).weekday() not in (0, 5, 6):
            ds.append(j3)
        d24 = dt.date(y, 12, 24)
        if d24.weekday() < 5:
            ds.append(d24)
        for d in ds:
            out.add((d - dt.date(1970, 1, 1)).days)
    for extra in ("2012-10-29", "2012-10-30", "2018-12-05"):
        out.add(int(np.datetime64(extra, "D").astype(np.int64)))
    return out


FREI = set(S5.FREI_DAYS) | us_frei()
FREI_ARR = np.array(sorted(FREI), np.int64)


def bad_days(sym):
    """NY-Tage ohne neue Einstiege im Symbol (nur Replikat): NAS-Datenluecken (< 330 M1-Kerzen 9:30-16:00) und die
    Quartalsverfalltage 2011-2018 (Rollspruenge der HistData-Reihe)."""
    d = data()[sym]
    out = set()
    if sym != "NAS":
        return np.zeros(0, np.int64)
    ny = d["ny1"]; day = ny // 1440; m = ny % 1440
    rth = (m >= 570) & (m < 960)
    u, cnt = np.unique(day[rth], return_counts=True)
    for x, c in zip(u, cnt):
        if c < 330 and int(x) not in FREI:
            out.add(int(x))
    for y in range(2011, 2019):
        for mo in (3, 6, 9, 12):
            f3 = _nth_weekday(y, mo, 4, 3)
            out.add((f3 - dt.date(1970, 1, 1)).days)
    return np.array(sorted(out), np.int64)


# ------------------------------------------------------------------ ATR(D1,14) wie FadeAtr
def daily_atr(sym, n=14):
    d1 = data()[sym]["d1"]
    h, l, c = d1["h"], d1["l"], d1["c"]
    tr = np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1])
    tr = np.r_[h[0] - l[0], tr]
    atr = np.convolve(tr, np.ones(n) / n, mode="full")[:len(tr)]
    atr[:n] = np.nan                    # FadeAtr braucht 15 Tageskerzen (14 TR mit Vortagesschluss)
    t_end = d1["t"] + 1440
    return t_end, atr


@njit(cache=True)
def _atr_at(t_end, atr, t):
    k = np.searchsorted(t_end, t, side="right") - 1
    if k < 0:
        return np.nan
    return atr[k]


# ------------------------------------------------------------------ Probability Grid (6.20, GridTF = M5)
@njit(cache=True)
def grid_build(o, c, L):
    n = o.shape[0]
    bias = np.zeros(n, np.int64); pivBar = np.full(n, -1, np.int64); pivPx = np.zeros(n); curPx = np.zeros(n)
    legConf = np.zeros(n, np.int64); legDir = np.zeros(n, np.int64); legSz = np.zeros(n); nLeg = 0
    b = 0; cbar = -1; pbar = -1; lbar = -1; cpx = 0.0; ppx = 0.0; lpx = 0.0
    for i in range(n):
        if i == 0:
            cpx = c[0]; cbar = 0; lpx = c[0]; lbar = 0
        if i >= L - 1:
            up = -1e300; lo = 1e300
            for j in range(i - L + 1, i + 1):
                a = max(o[j], c[j]); z = min(o[j], c[j])
                if a > up: up = a
                if z < lo: lo = z
            mx = max(o[i], c[i]); mn = min(o[i], c[i])
            nb = b
            if mx == up:
                nb = 1
            elif mn == lo:
                nb = -1
            neu = False
            if nb != b and nb != 0:
                if b != 0:
                    neu = True; ppx = cpx; pbar = cbar
                cpx = up if nb == 1 else lo
                cbar = i; b = nb
            elif b != 0:
                alt = cpx
                cpx = max(up, cpx) if b == 1 else min(lo, cpx)
                if cpx != alt:
                    cbar = i
            if neu and lpx > 0.0:
                bd = pbar - lbar
                if bd != 0:
                    legConf[nLeg] = i; legDir[nLeg] = 1 if ppx > lpx else -1
                    legSz[nLeg] = abs(ppx - lpx) / lpx; nLeg += 1
                    lpx = ppx; lbar = pbar
        bias[i] = b; pivPx[i] = ppx; pivBar[i] = pbar; curPx[i] = cpx
    return bias, pivBar, pivPx, curPx, legConf[:nLeg], legDir[:nLeg], legSz[:nLeg]


@njit(cache=True)
def _grid_rang(legConf, legDir, legSz, i, d, x, maxn):
    lo = 0; hi = legConf.shape[0] - 1; q0 = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if legConf[mid] <= i:
            q0 = mid; lo = mid + 1
        else:
            hi = mid - 1
    n = 0; cnt = 0
    q = q0
    while q >= 0 and n < maxn:
        if legDir[q] == d:
            n += 1
            if legSz[q] <= x:
                cnt += 1
        q -= 1
    return (cnt / n if n > 0 else 0.0), n


@njit(cache=True)
def grid_ok(bias, pivBar, pivPx, curPx, legConf, legDir, legSz, i, d, st, maxn, minn, maxstop):
    """i = Index der letzten abgeschlossenen M5-Kerze vor der Einstiegskerze."""
    if i < 0 or bias[i] == 0 or pivBar[i] < 0 or pivPx[i] <= 0.0:
        return True
    b = bias[i]
    if d == b:
        return True
    ext = abs(curPx[i] - pivPx[i]) / pivPx[i]
    pe, n = _grid_rang(legConf, legDir, legSz, i, b, ext, maxn)
    if n < minn:
        return True
    if maxstop > 0.0:
        xs = abs(st - pivPx[i]) / pivPx[i]
        sJ = 1.0 - pe
        p2, n2 = _grid_rang(legConf, legDir, legSz, i, b, xs, maxn)
        sS = 1.0 - p2
        ch = sS / sJ if sJ > 0.0 else 0.0
        if ch >= maxstop:
            return False
    return True


# ------------------------------------------------------------------ Listen-Fades (FadeKerze)
FADE_STANDARD = [
    ("N1030", "NAS", 630, 120, 60, 120, 0.3, 0, 1, 0.6), ("N1330", "NAS", 810, 60, 120, 120, 1.0, 0, 1, 0.6),
    ("X0630", "XAU", 390, 120, 180, 240, 1.0, 1, -1, 0.6), ("X0400", "XAU", 240, 180, 60, 240, 0.3, 0, 1, 0.6),
    ("N1800", "NAS", -360, 180, 60, 120, 0.3, 0, 1, 0.6), ("N0930", "NAS", 570, 180, 60, 120, 0.3, 0, 1, 99.0),
    ("N1100", "NAS", 660, 90, 60, 240, 0.6, 1, 1, 0.6), ("N1300", "NAS", 780, 90, 60, 120, 0.6, 0, 1, 0.6),
    ("X0300S", "XAU", 180, 90, 60, 120, 0.3, 0, -1, 0.6), ("X1000S", "XAU", 600, 180, 60, 240, 0.3, 0, -1, 0.6)]


def fade_times(r0, L, tlen, xoff):
    r1 = r0 + L; te = r1 + tlen; xm = min(r1 + tlen + xoff, 1000)
    if xm <= te:
        te = xm - 5
    return r1, te, xm


@njit(cache=True)
def _gen_fade(ny, o, h, l, c, sp, days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mx):
    n = days.shape[0]
    IE = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); SL = np.zeros(n); TP = np.zeros(n); EN = np.zeros(n)
    IX = np.zeros(n, np.int64); m = 0
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
        if rng <= 0.0 or rng > mx * a:
            continue
        te = np.searchsorted(ny, D * 1440 + tend)
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
                    break
                continue
            if dirs != 0 and d != dirs:
                break
            B = j + 1
            if B >= ny.shape[0] or ny[B] >= D * 1440 + xm:
                break
            ent = o[B] + (sp[B] if d > 0 else 0.0)
            st = ext_lo - buf * rng if d > 0 else ext_hi + buf * rng
            goal = 0.5 * (hh + ll) if tgt == 0 else (hh if d > 0 else ll)
            if (ent - st) * d > 0.0 and (goal - ent) * d > 0.0:
                IE[m] = B; DD[m] = d; SL[m] = st; TP[m] = goal; EN[m] = ent; IX[m] = D * 1440 + xm; m += 1
            break
    return IE[:m], DD[:m], SL[:m], TP[:m], EN[:m], IX[:m]


@njit(cache=True)
def virt_m5(ny, o, h, l, sp, ie, d, en, sl, tp, tx, comm_px):
    """Virtueller Trade wie FadeKerze: M5, Stop vor Ziel, Ziel nicht in der Einstiegskerze, Zeit-Ausstieg am Open der
    ersten Kerze ab tx. Rueckgabe R (inkl. Kommission) und der Zeitpunkt, ab dem das Ergebnis feststeht."""
    n = ie.shape[0]
    R = np.zeros(n); tk = np.zeros(n, np.int64)
    for t in range(n):
        i = ie[t]; dd = d[t]; r = (en[t] - sl[t]) * dd
        j = i; px = 0.0; known = 0
        while True:
            if j >= ny.shape[0]:
                px = o[ny.shape[0] - 1]; known = ny[ny.shape[0] - 1]; break
            if ny[j] >= tx[t] and j > i:
                px = o[j] + (sp[j] if dd < 0 else 0.0); known = ny[j]; break
            s_ = sp[j]
            if dd > 0:
                hs = l[j] <= sl[t]; ht = tp[t] > 0.0 and h[j] >= tp[t]
            else:
                hs = h[j] + s_ >= sl[t]; ht = tp[t] > 0.0 and l[j] + s_ <= tp[t]
            if hs:
                px = sl[t]
                if dd > 0 and o[j] < sl[t]:
                    px = o[j]
                if dd < 0 and o[j] + s_ > sl[t]:
                    px = o[j] + s_
                known = ny[j + 1] if j + 1 < ny.shape[0] else ny[j] + 5
                break
            if ht and j > i:
                px = tp[t]
                known = ny[j + 1] if j + 1 < ny.shape[0] else ny[j] + 5
                break
            j += 1
        R[t] = ((px - en[t]) * dd - comm_px) / r
        tk[t] = known
    return R, tk


def list_fades(grid=True, gmaxn=1000, gminn=30, gmaxstop=0.70, glen=15, grid_ohne=("N1800",), names=None):
    D = data()
    out = []
    gr = {}
    for s in ("XAU", "NAS"):
        d = D[s]
        gr[s] = grid_build(d["o"], d["c"], glen)
    for (nm, s, r0, L, tlen, xoff, buf, tgt, dirs, mx) in FADE_STANDARD:
        if names is not None and nm not in names:
            continue
        d = D[s]; ny = d["ny"]
        days = np.unique(ny // 1440)
        days = days[((days + 4) % 7 >= 1) & ((days + 4) % 7 <= 5)]
        t_end, atr = daily_atr(s)
        r1, te, xm = fade_times(r0, L, tlen, xoff)
        ie, dd, sl, tp, en, tx = _gen_fade(ny, d["o"], d["h"], d["l"], d["c"], d["sp"], days, t_end, atr, r0, r1, te, xm,
                                           buf, tgt, dirs, mx)
        keep = np.ones(len(ie), bool)
        if grid and nm not in grid_ohne:
            g = gr[s]
            for q in range(len(ie)):
                keep[q] = grid_ok(*g, ie[q] - 1, dd[q], sl[q], gmaxn, gminn, gmaxstop)
        ie, dd, sl, tp, en, tx = ie[keep], dd[keep], sl[keep], tp[keep], en[keep], tx[keep]
        k = SYM[s]
        R, tk = virt_m5(ny, d["o"], d["h"], d["l"], d["sp"], ie, dd, en, sl, tp, tx, COMM[k] / MPP[k])
        out.append(dict(name=nm, sym=np.full(len(ie), k), t=ny[ie], dir=dd, ent=en, fix=np.zeros(len(ie), np.int64),
                        sl=sl, tp=tp, tx=tx, R=R, tknown=tk))
    return out


def portfolio_guard(blocks, N=200, pf=1.15, hist_days=600, t_start=None):
    """FadePortfolioPF: live, wenn der PF der letzten N virtuellen Ergebnisse ALLER Listen-Fades, die vor der
    Signalzeit feststanden (innerhalb hist_days), > pf ist und N erreicht sind. Zusaetzlich Zustand als Zeitreihe."""
    T = np.concatenate([b["tknown"] for b in blocks]); R = np.concatenate([b["R"] for b in blocks])
    M = np.concatenate([np.full(len(b["R"]), i) for i, b in enumerate(blocks)])
    o = np.lexsort((M, T)); T = T[o]; R = R[o]
    if t_start is None:
        t_start = max(int(b["t"][0]) for b in blocks if len(b["t"]))
    t_start += 1440

    def live_at(t):
        k = np.searchsorted(T, t, side="left")          # Ergebnisse mit T < t
        lo = max(0, k - N)
        w = R[lo:k]; tw = T[lo:k]
        w = w[tw >= max(t - hist_days * 1440, t_start)]
        if len(w) < N:
            return False, len(w), 0.0
        pos = w[w > 0].sum(); neg = -w[w < 0].sum()
        p = pos / neg if neg > 0 else 9.9
        return p > pf, len(w), p
    for b in blocks:
        b["live"] = np.array([live_at(int(t))[0] for t in b["t"]], bool)
    return live_at


# ------------------------------------------------------------------ Spike S0830 (SpikeKerze)
def spike(start=510, mess=2, warte=6, kmin=0.20, stop_atr=0.25, ziel=0.5, aus=660, richtung=1):
    D = data(); d = D["NAS"]; ny = d["ny"]; o, h, l, sp = d["o"], d["h"], d["l"], d["sp"]
    t_end, atr = daily_atr("NAS")
    days = np.unique(ny // 1440)
    rows = []
    for Dt in days:
        dow = (Dt + 4) % 7
        if dow < 1 or dow > 5:
            continue
        rs = Dt * 1440 + start; re = rs + warte * 5
        i0 = np.searchsorted(ny, rs)
        if i0 + warte >= len(ny) or ny[i0] != rs:
            continue
        ok = True
        for q in range(warte):
            if ny[i0 + q] != rs + 5 * q:
                ok = False; break
        if not ok or ny[i0 + warte] != re:
            continue
        p0 = o[i0]
        hh = h[i0:i0 + mess].max(); ll = l[i0:i0 + mess].min()
        a = _atr_at(t_end, atr, rs)
        up = hh - p0; dn = p0 - ll
        dd = -1 if up >= dn else 1
        mv = up if up >= dn else dn
        if not (a > 0) or mv < kmin * a or (richtung != 0 and dd != richtung):
            continue
        hh = h[i0:i0 + warte].max(); ll = l[i0:i0 + warte].min()
        B = i0 + warte
        xm = Dt * 1440 + aus
        ex = ll if dd > 0 else hh
        goal = ex + dd * ziel * abs(ex - p0)
        ent = o[B] + (sp[B] if dd > 0 else 0.0)
        st = ex - dd * stop_atr * a
        if (ent - st) * dd <= 0 or (goal - ent) * dd <= 0:
            continue
        rows.append((ny[B], 1, dd, ent, 0, st, goal, xm))
    return _blk("S0830", rows)


# ------------------------------------------------------------------ Larry-Williams-Ausbruch LW (LwKerze)
def lw(start=570, sitzung=390, k=0.4, ende=900, aus=960, ziel_r=0.0, richtung=0):
    D = data(); d = D["NAS"]; ny = d["ny"]; o, h, l, c, sp = d["o"], d["h"], d["l"], d["c"], d["sp"]
    t_end, atr = daily_atr("NAS")
    rows = []
    days = np.unique((ny - start) // 1440)
    pH = pL = 0.0; pN = 0
    for Dt in days:
        a0 = np.searchsorted(ny, Dt * 1440 + start); a1 = np.searchsorted(ny, (Dt + 1) * 1440 + start)
        sess = (ny[a0:a1] >= Dt * 1440 + start) & (ny[a0:a1] < Dt * 1440 + start + sitzung)
        cN = int(sess.sum())
        cH = h[a0:a1][sess].max() if cN else -np.inf; cL = l[a0:a1][sess].min() if cN else np.inf
        dow = (Dt + 4) % 7
        if 1 <= dow <= 5 and a0 < len(ny) and ny[a0] == Dt * 1440 + start:
            A = _atr_at(t_end, atr, Dt * 1440 + start)
            if pN >= 12 and A > 0 and pH - pL > 0:
                p0 = o[a0]; rng = pH - pL
                upv = p0 + k * rng; dnv = p0 - k * rng
                re = Dt * 1440 + ende; xm = Dt * 1440 + aus
                for j in range(a0, a1):
                    if ny[j] >= re:
                        break
                    dd = 1 if c[j] > upv else (-1 if c[j] < dnv else 0)
                    if dd == 0:
                        continue
                    if richtung != 0 and dd != richtung:
                        break
                    B = j + 1
                    if B >= len(ny) or ny[B] >= xm:
                        break
                    ent = o[B] + (sp[B] if dd > 0 else 0.0)
                    st = 0.5 * (p0 + ent)
                    r = (ent - st) * dd
                    if r <= 0.05 * A:
                        break
                    goal = ent + dd * ziel_r * r if ziel_r > 0 else 0.0
                    rows.append((ny[B], 1, dd, ent, 0, st, goal, xm))
                    break
        if cN >= 12:
            pH, pL, pN = cH, cL, cN
    return _blk("LW", rows)


# ------------------------------------------------------------------ Gold-Asien XA (AsiaKerze)
def xa(ein=-360, aus=180, trend=288, stop_atr=0.6, ziel_r=1.0):
    D = data(); d = D["XAU"]; ny = d["ny"]; o, c, sp = d["o"], d["c"], d["sp"]
    t_end, atr = daily_atr("XAU")
    cs = np.r_[0.0, np.cumsum(c)]
    rows = []
    days = np.unique((ny - ein) // 1440)
    for Dn in days:
        dow = (Dn + 4) % 7
        if dow < 1 or dow > 5:
            continue
        tgt = Dn * 1440 + ein
        B = np.searchsorted(ny, tgt)
        if B >= len(ny) or B == 0 or ny[B] - tgt > 10:
            continue
        b = B - 1
        if trend > 0:
            if b + 1 < trend:
                continue
            ma = (cs[b + 1] - cs[b + 1 - trend]) / trend
            if c[b] <= ma:
                continue
        a = _atr_at(t_end, atr, tgt)
        if not (a > 0):
            continue
        ent = o[B] + sp[B]
        r = stop_atr * a
        rows.append((ny[B], 0, 1, ent, 0, ent - r, ent + ziel_r * r if ziel_r > 0 else 0.0, Dn * 1440 + aus))
    return _blk("XA", rows)


# ------------------------------------------------------------------ Trend-Day TD (TdKerze)
def td(ein=840, aus=955, schluss=960, min_atr=0.75, stop_atr=0.3, ziel_r=0.0, richtung=1):
    D = data(); d = D["NAS"]; ny = d["ny"]; o, c, sp = d["o"], d["c"], d["sp"]
    t_end, atr = daily_atr("NAS")
    day = ny // 1440; mins = ny % 1440
    wk = ((day + 4) % 7 >= 1) & ((day + 4) % 7 <= 5)
    wdays = np.unique(day[wk])
    ref = {}
    sel = (mins >= schluss - 60) & (mins < schluss)
    for i in np.nonzero(sel)[0]:
        ref[int(day[i])] = c[i]                       # spaeteste Kerze vor 16:00 gewinnt
    rows = []
    for q in range(1, len(wdays)):
        Dn = int(wdays[q]); vor = int(wdays[q - 1])
        B = np.searchsorted(ny, Dn * 1440 + ein)
        if B >= len(ny) or ny[B] != Dn * 1440 + ein or B == 0:
            continue
        if vor not in ref:
            continue
        a = _atr_at(t_end, atr, Dn * 1440 + ein)
        if not (a > 0):
            continue
        r = c[B - 1] - ref[vor]
        if abs(r) < min_atr * a or r == 0:
            continue
        dd = 1 if r > 0 else -1
        if richtung != 0 and dd != richtung:
            continue
        ent = o[B] + (sp[B] if dd > 0 else 0.0)
        rd = stop_atr * a
        rows.append((ny[B], 1, dd, ent, 0, ent - dd * rd, ent + dd * ziel_r * rd if ziel_r > 0 else 0.0, Dn * 1440 + aus))
    return _blk("TD", rows)


# ------------------------------------------------------------------ SR Liquidity-Sweep-Reclaim im Tick (SrTick)
SR_STANDARD = [("IB", 570, 630, 0, 630, 900, 955, 0.0, 0.5, 0.0, 0.03, 1),
               ("PRE", 480, 570, 0, 570, 630, 955, 0.0, 0.5, 0.0, 0.03, -1),
               ("H12", 720, 780, 0, 780, 900, 955, 0.0, 0.5, 0.0, 0.03, 1),
               ("PDN", 570, 960, -1, -360, 555, 565, 0.08, 0.5, 0.0, 0.03, 1)]


def sr(marks=None, crv=2.0, minsp=6.0, minatr=0.05, maxspatr=0.02, same_minute=True):
    D = data(); d = D["NAS"]
    ny, o, h, l, c, sp = d["ny1"], d["o1"], d["h1m"], d["l1"], d["c1"], d["sp1"]
    t_end, atr = daily_atr("NAS")
    days = np.unique(ny // 1440)
    days = np.r_[days, days[-1] + 1]
    out = []
    for mk in (marks or SR_STANDARD):
        nm, la, lb, loff, w0, w1, x, sd, md, rb, sb, dr = mk
        T, DD, EN, SL, TP, TX = _sr2(ny, o, h, l, c, sp, days, t_end, atr, la, lb, loff, w0, w1, x, sd, md, rb, sb, dr,
                                     crv, minsp, minatr, maxspatr, same_minute)
        out.append(dict(name="SR" + nm, sym=np.ones(len(T), np.int64), t=T, dir=DD, ent=EN, fix=np.ones(len(T), np.int64),
                        sl=SL, tp=TP, tx=TX))
    return out


@njit(cache=True)
def _sr2(ny, o, h, l, c, sp, days, t_end, atr, la, lb, loff, w0, w1, x, sd, md, rb, sb, dr, crv, minsp, minatr, maxspatr,
         same_minute):
    """SrTick auf M1 (pessimistisch): Sweep-Minute = Tief <= Marke - sd*ATR (Durchbruch, wenn <= Marke - md*ATR).
    Rueckkehr in derselben Minute nur, wenn deren Schluss (Ask) schon ueber der Marke liegt; Extrem = Tief dieser Minute.
    Spaetere Minuten: Ask-Hoch >= Marke -> Einstieg zur Marke (oder zum Open, wenn darueber eroeffnet); das Extrem
    stammt aus den Minuten davor - faellt die Einstiegsminute bis zum Stop, rechnet der Motor den Stop in derselben
    Minute (Reihenfolge unbekannt = schlechterer Fall). Durchbruch in einer Minute ohne Rueckkehr: Marke erledigt."""
    n = days.shape[0]
    T = np.zeros(n, np.int64); DD = np.zeros(n, np.int64); EN = np.zeros(n); SL = np.zeros(n); TP = np.zeros(n)
    TX = np.zeros(n, np.int64); m = 0
    pt = 0.01
    for q in range(n):
        Dt = days[q]
        dow = (Dt + 4) % 7
        if dow < 1 or dow > 5:
            continue
        hi = -1e300; lo = 1e300; cnt = 0
        nv = 7 if loff < 0 else 1
        for v in range(nv):
            tag = Dt - 1 - v if loff < 0 else Dt
            s = np.searchsorted(ny, tag * 1440 + la); e = np.searchsorted(ny, tag * 1440 + lb)
            if e - s >= 10:
                for j in range(s, e):
                    if h[j] > hi: hi = h[j]
                    if l[j] < lo: lo = l[j]
                cnt = e - s
                break
        if cnt < 10 or hi <= lo:
            continue
        A = _atr_at(t_end, atr, Dt * 1440 + w0)
        if not (A > 0):
            continue
        s = np.searchsorted(ny, Dt * 1440 + w0); e = np.searchsorted(ny, Dt * 1440 + w1)
        xm = Dt * 1440 + x
        st = 0; ex = 0.0; ent = 0.0; found = False
        for j in range(s, e):
            spr = sp[j]
            if dr > 0:
                lvl = lo; tr = lo + rb * A
                if st == 0:
                    if l[j] > lvl - sd * A:
                        continue
                    if l[j] <= lvl - md * A:
                        break
                    st = 1; ex = l[j]
                    if same_minute and c[j] + spr >= tr:
                        ent = tr; found = True
                    else:
                        continue
                else:
                    if h[j] + spr >= tr:
                        ent = max(tr, o[j] + spr); found = True
                    else:
                        if l[j] <= lvl - md * A:
                            break
                        if l[j] < ex:
                            ex = l[j]
                        continue
                stp = ex - sb * A
            else:
                lvl = hi; tr = hi - rb * A
                if st == 0:
                    if h[j] < lvl + sd * A:
                        continue
                    if h[j] >= lvl + md * A:
                        break
                    st = 1; ex = h[j]
                    if same_minute and c[j] <= tr:
                        ent = tr; found = True
                    else:
                        continue
                else:
                    if l[j] <= tr:
                        ent = min(tr, o[j]); found = True
                    else:
                        if h[j] >= lvl + md * A:
                            break
                        if h[j] > ex:
                            ex = h[j]
                        continue
                stp = ex + spr + sb * A
            if not found:
                continue
            if ny[j] >= xm:
                break
            if maxspatr > 0.0 and spr > maxspatr * A:
                break
            minD = max(minsp * spr, minatr * A) + 2.0 * pt
            if (ent - stp) * dr < minD:
                stp = ent - dr * minD
            rd = (ent - stp) * dr
            T[m] = ny[j]; DD[m] = dr; EN[m] = ent; SL[m] = stp; TP[m] = ent + dr * crv * rd; TX[m] = xm; m += 1
            break
    return T[:m], DD[:m], EN[:m], SL[:m], TP[:m], TX[:m]


def _blk(name, rows):
    if not rows:
        z = np.zeros(0)
        return dict(name=name, t=z.astype(np.int64), sym=z.astype(np.int64), dir=z.astype(np.int64), ent=z,
                    fix=z.astype(np.int64), sl=z, tp=z, tx=z.astype(np.int64))
    A = np.array(rows, dtype=np.float64)
    return dict(name=name, t=A[:, 0].astype(np.int64), sym=A[:, 1].astype(np.int64), dir=A[:, 2].astype(np.int64),
                ent=A[:, 3], fix=A[:, 4].astype(np.int64), sl=A[:, 5], tp=A[:, 6], tx=A[:, 7].astype(np.int64))


# ------------------------------------------------------------------ RSI21 / Noise (alte Generatoren, sig5)
def r21_and_nz():
    D = data()
    r21 = S5.r21_signals(D)
    nz = S5.nz_days(D)
    return r21, nz


def regime_flags(live_at, T):
    """6.50: Regime der Fades zur Zeit T (Open der M5-Kerze) fuer den Schutz gueltiger Tage bei RSI21."""
    return np.array([live_at(int(t))[0] for t in T], bool)
