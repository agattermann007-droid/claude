"""Replikat v11 - Einzel-Simulator fuer Signal-Bloecke auf M1 (ohne Konto).

Konventionen (pessimistisch, wie Bericht V10 / Prompt Abschnitt 6):
  - Einstieg am Open der Minute t (Long zum Ask = Bid + Spread) bzw. zum festen Preis (fix = 1, Tick-Einstieg SR)
  - Schlupf: Markt-Einstiege, Stop- und Zeit-Ausstiege je slip x Spread schlechter (Ziel = Limit, ohne Schlupf)
  - in derselben Minute zaehlt der Stop VOR dem Ziel; Ziel erst ab der Minute tpdelay nach dem Einstieg
  - Zeit-Ausstieg am Open der ersten Minute ab tx
  - R = Ergebnis / Stop-Abstand beim Einstieg, inkl. Spread, Schlupf und Kommission (Gold 5 $/Lot)
"""
import numpy as np
from numba import njit
import gen11 as G

MPP = G.MPP; COMM = G.COMM


@njit(cache=True)
def _sim(ny, o, h, l, sp, t, d, ent0, fix, sl0, tp0, tx, tpdelay, slip, comm_px, be_r, be_plus):
    n = t.shape[0]
    R = np.zeros(n); why = np.zeros(n, np.int64); mfe = np.zeros(n); mae = np.zeros(n); tout = np.zeros(n, np.int64)
    for q in range(n):
        i = np.searchsorted(ny, t[q])
        if i >= ny.shape[0] or ny[i] - t[q] > 10:
            why[q] = -1
            continue
        dd = d[q]
        if fix[q] == 1:
            ent = ent0[q] + dd * slip * sp[i]
        else:
            ent = o[i] + (sp[i] if dd > 0 else 0.0) + dd * slip * sp[i]
        sl = sl0[q]; tp = tp0[q]
        r = (ent - sl) * dd
        if r <= 0.0:
            why[q] = -2
            continue
        bmfe = 0.0; bmae = 0.0; j = i; px = 0.0; w = 0; be = False
        while True:
            if j >= ny.shape[0]:
                px = o[ny.shape[0] - 1]; w = 3; j = ny.shape[0] - 1; break
            s_ = sp[j]
            if ny[j] >= tx[q] and j > i:
                px = o[j] + (s_ if dd < 0 else 0.0) - dd * slip * s_; w = 0; break
            if dd > 0:
                fav = (h[j] - ent) / r; adv = (ent - l[j]) / r
                hs = l[j] <= sl; ht = tp > 0.0 and h[j] >= tp
            else:
                fav = (ent - (l[j] + s_)) / r; adv = ((h[j] + s_) - ent) / r
                hs = h[j] + s_ >= sl; ht = tp > 0.0 and l[j] + s_ <= tp
            if hs:
                px = sl
                if dd > 0 and o[j] < sl:
                    px = o[j]
                if dd < 0 and o[j] + s_ > sl:
                    px = o[j] + s_
                px -= dd * slip * s_
                w = 1
                if adv > bmae:
                    bmae = adv
                break
            if ht and j - i >= tpdelay:
                px = tp
                if dd > 0 and o[j] > tp:
                    px = o[j]
                if dd < 0 and o[j] + s_ < tp:
                    px = o[j] + s_
                w = 2
                if fav > bmfe:
                    bmfe = fav
                break
            if fav > bmfe:
                bmfe = fav
            if adv > bmae:
                bmae = adv
            if be_r > 0.0 and not be and bmfe >= be_r:
                cand = ent + dd * be_plus * r
                if (cand - sl) * dd > 0.0:
                    sl = cand
                be = True
            j += 1
        R[q] = ((px - ent) * dd - comm_px) / r
        why[q] = w; mfe[q] = bmfe; mae[q] = bmae; tout[q] = ny[min(j, ny.shape[0] - 1)]
    return R, why, mfe, mae, tout


def simulate(blk, tpdelay=5, slip=0.25, be_r=0.0, be_plus=0.05):
    D = G.data()
    if len(blk["t"]) == 0:
        return dict(R=np.zeros(0), why=np.zeros(0, np.int64), mfe=np.zeros(0), mae=np.zeros(0), tout=np.zeros(0, np.int64))
    k = int(blk["sym"][0])
    s = "XAU" if k == 0 else "NAS"
    d = D[s]
    R, why, mfe, mae, tout = _sim(d["ny1"], d["o1"], d["h1m"], d["l1"], d["sp1"], blk["t"], blk["dir"], blk["ent"],
                                  blk["fix"], blk["sl"], blk["tp"], blk["tx"], tpdelay, slip, COMM[k] / MPP[k], be_r, be_plus)
    return dict(R=R, why=why, mfe=mfe, mae=mae, tout=tout)


def stats(R, t=None, lo=None, hi=None):
    m = np.ones(len(R), bool)
    if t is not None and lo is not None:
        m &= t >= np.datetime64(lo, "m").astype(np.int64)
    if t is not None and hi is not None:
        m &= t < np.datetime64(hi, "m").astype(np.int64)
    x = R[m]
    if len(x) == 0:
        return dict(n=0, wr=0.0, pf=0.0, er=0.0, sum=0.0)
    pos = x[x > 0].sum(); neg = -x[x < 0].sum()
    return dict(n=int(len(x)), wr=100.0 * (x > 0).mean(), pf=pos / neg if neg > 0 else 99.0, er=float(x.mean()), sum=float(x.sum()))


def fmt(st):
    return f"n {st['n']:5d}  WR {st['wr']:5.1f}%  PF {st['pf']:5.2f}  E {st['er']:+.3f} R  Summe {st['sum']:+7.1f} R"


@njit(cache=True)
def _sim_conf(ny, o, h, l, sp, t, d, ent0, fix, sl0, tp0, tx, tpdelay, slip, comm_px, xr, wmin):
    """Bestaetigungs-Einstieg: nach dem Signal (Zeit t, geplanter Einstieg ent0) erst kaufen/verkaufen, wenn der Kurs
    xr x Stop-Abstand in Signalrichtung gelaufen ist (Stop-Order, Fuellung am Ausloeser + Schlupf), hoechstens wmin Minuten
    lang (0 = bis zum Zeit-Ausstieg). Erreicht der Kurs vorher den Stop: Signal verfaellt. Beruehrt die Ausloese-Minute
    auch den Stop: Einstieg und Stop in derselben Minute (schlechterer Fall). Stop und Ziel bleiben die des Signals."""
    n = t.shape[0]
    R = np.zeros(n); why = np.full(n, -1, np.int64); tin = np.zeros(n, np.int64)
    for q in range(n):
        i = np.searchsorted(ny, t[q])
        if i >= ny.shape[0] or ny[i] - t[q] > 10:
            continue
        dd = d[q]; sl = sl0[q]; tp = tp0[q]
        r0 = (ent0[q] - sl) * dd
        if r0 <= 0.0:
            continue
        trig = ent0[q] + dd * xr * r0
        j = i + 1 if fix[q] == 1 else i          # Tick-Signal: Open und Extreme der Signalminute liegen teils davor
        ent = 0.0; found = False
        while j < ny.shape[0]:
            if ny[j] >= tx[q] or (wmin > 0 and ny[j] - t[q] >= wmin):
                break
            s_ = sp[j]
            if dd > 0:
                hit_t = h[j] + s_ >= trig; hit_s = l[j] <= sl
            else:
                hit_t = l[j] <= trig; hit_s = h[j] + s_ >= sl
            if hit_t:
                ent = trig + dd * slip * s_
                if dd > 0 and o[j] + s_ > trig:
                    ent = o[j] + s_ + slip * s_
                if dd < 0 and o[j] < trig:
                    ent = o[j] - slip * s_
                found = True
                break
            if hit_s:
                break
            j += 1
        if not found:
            why[q] = -3
            continue
        r = (ent - sl) * dd
        if r <= 0.0 or (tp > 0.0 and (tp - ent) * dd <= 0.0):
            why[q] = -4
            continue
        i0 = j; px = 0.0; w = 0
        while True:
            if j >= ny.shape[0]:
                px = o[ny.shape[0] - 1]; w = 3; break
            s_ = sp[j]
            if ny[j] >= tx[q] and j > i0:
                px = o[j] + (s_ if dd < 0 else 0.0) - dd * slip * s_; w = 0; break
            if dd > 0:
                hs = l[j] <= sl; ht = tp > 0.0 and h[j] >= tp
            else:
                hs = h[j] + s_ >= sl; ht = tp > 0.0 and l[j] + s_ <= tp
            if hs:
                px = sl
                if j > i0 and dd > 0 and o[j] < sl:
                    px = o[j]
                if j > i0 and dd < 0 and o[j] + s_ > sl:
                    px = o[j] + s_
                px -= dd * slip * s_
                w = 1
                break
            if ht and j - i0 >= tpdelay:
                px = tp; w = 2; break
            j += 1
        R[q] = ((px - ent) * dd - comm_px) / r
        why[q] = w; tin[q] = ny[i0]
    return R, why, tin


def simulate_conf(blk, xr, wmin, tpdelay=5, slip=0.25):
    D = G.data()
    if len(blk["t"]) == 0:
        return dict(R=np.zeros(0), why=np.zeros(0, np.int64), tin=np.zeros(0, np.int64))
    k = int(blk["sym"][0]); s = "XAU" if k == 0 else "NAS"; d = D[s]
    R, why, tin = _sim_conf(d["ny1"], d["o1"], d["h1m"], d["l1"], d["sp1"], blk["t"], blk["dir"], blk["ent"], blk["fix"],
                            blk["sl"], blk["tp"], blk["tx"], tpdelay, slip, COMM[k] / MPP[k], xr, wmin)
    return dict(R=R, why=why, tin=tin)
