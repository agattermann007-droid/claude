"""Replikat v11 - Price-Action-Forschung: allgemeiner Sweep-Reclaim-Generator im Tick (M1, pessimistisch).

Marke = Hoch/Tief der M1-Kerzen [la, lb) eines NY-Tages (loff -1: letzter Tag davor mit Kursen). Im Fenster [w0, w1)
sticht der Kurs mind. sd x ATR jenseits der Marke (Sweep; mehr als md x ATR = Durchbruch, Marke erledigt) und kehrt um
rb x ATR zurueck -> Einstieg im selben Tick (M1: Regeln wie gen11._sr2). Stop: smode 0 = Extrem -/+ sb x ATR,
smode 1 = Extrem -/+ sb x Markenspanne (Fade-Stil). Ziel: tmode 0 = crv x Stopabstand, 1 = Mitte der Marke,
2 = Gegenseite. Filter: Markenspanne <= mx x ATR, Mindeststop max(6 Spreads, 0,05 ATR). Zeit-Ausstieg x.
dir +1 = Sweep des Tiefs -> Long, -1 = Sweep des Hochs -> Short.
"""
import numpy as np
from numba import njit
import gen11 as G, sim11 as M


@njit(cache=True)
def _sweep(ny, o, h, l, c, sp, days, t_end, atr, la, lb, loff, w0, w1, x, sd, md, rb, smode, sb, tmode, crv, mx, dr,
           minsp, minatr):
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
        A = G._atr_at(t_end, atr, Dt * 1440 + w0)
        if not (A > 0):
            continue
        rng = hi - lo
        if rng > mx * A:
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
                    if c[j] + spr >= tr:
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
                stp = ex - (sb * A if smode == 0 else sb * rng)
            else:
                lvl = hi; tr = hi - rb * A
                if st == 0:
                    if h[j] < lvl + sd * A:
                        continue
                    if h[j] >= lvl + md * A:
                        break
                    st = 1; ex = h[j]
                    if c[j] <= tr:
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
                stp = ex + spr + (sb * A if smode == 0 else sb * rng)
            if not found:
                continue
            if ny[j] >= xm:
                break
            minD = max(minsp * spr, minatr * A) + 2.0 * pt
            if (ent - stp) * dr < minD:
                stp = ent - dr * minD
            rd = (ent - stp) * dr
            if tmode == 0:
                goal = ent + dr * crv * rd
            elif tmode == 1:
                goal = 0.5 * (hi + lo)
            else:
                goal = hi if dr > 0 else lo
            if (goal - ent) * dr <= 0.0:
                break
            T[m] = ny[j]; DD[m] = dr; EN[m] = ent; SL[m] = stp; TP[m] = goal; TX[m] = xm; m += 1
            break
    return T[:m], DD[:m], EN[:m], SL[:m], TP[:m], TX[:m]


_PREP = {}


def prep(sym):
    if sym not in _PREP:
        d = G.data()[sym]
        t_end, atr = G.daily_atr(sym)
        days = np.unique(d["ny1"] // 1440)
        days = np.r_[days, days[-1] + 1]
        _PREP[sym] = (d, t_end, atr, days)
    return _PREP[sym]


def sweep(sym, la, lb, loff, w0, w1, x, sd=0.0, md=0.5, rb=0.0, smode=0, sb=0.03, tmode=0, crv=2.0, mx=99.0, dr=1,
          minsp=6.0, minatr=0.05, name=None):
    d, t_end, atr, days = prep(sym)
    T, DD, EN, SL, TP, TX = _sweep(d["ny1"], d["o1"], d["h1m"], d["l1"], d["c1"], d["sp1"], days, t_end, atr,
                                   la, lb, loff, w0, w1, x, sd, md, rb, smode, sb, tmode, crv, mx, dr, minsp, minatr)
    k = G.SYM[sym]
    return dict(name=name or f"{sym}{la}_{lb}_{w0}_{dr}", sym=np.full(len(T), k, np.int64), t=T, dir=DD, ent=EN,
                fix=np.ones(len(T), np.int64), sl=SL, tp=TP, tx=TX)


PER = [("2016-09-01", "2022-01-01", "16-21"), ("2022-01-01", "2024-01-01", "22-23"), ("2024-01-01", "2026-03-01", "24-26")]


def evalb(b, tpdelay=4, slip=0.25):
    r = M.simulate(b, tpdelay=tpdelay, slip=slip)
    ok = r["why"] >= 0
    out = {}
    for lo, hi, lab in PER:
        out[lab] = M.stats(r["R"][ok], b["t"][ok], lo, hi)
    return out, r
