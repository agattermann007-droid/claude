"""Neue Strategien: Datenzugriff, schneller Trade-Simulator (ohne Konto) und Kennzahlen.
Zeit = NY-Minuten seit Epoche. Einstieg am Open einer M5-Kerze (Long zum Ask = Bid + Spread), Ausstieg am Open der
Ausstiegskerze oder an Stop/Ziel (Stop vor Ziel in derselben Kerze). R = Ergebnis / Stop-Abstand, inkl. Spread und Kommission."""
import numpy as np, os, pickle
from numba import njit
import prep5 as P

SYM = {"XAU": 0, "NAS": 1}
MPP = np.array([100.0, 10.0]); COMM = np.array([5.0, 0.0])
_D = None


def data():
    global _D
    if _D is None:
        f = os.path.join(P.OUT, "D5.pkl")
        if os.path.exists(f):
            _D = pickle.load(open(f, "rb"))
        else:
            _D = P.build()
            pickle.dump(_D, open(f, "wb"))
    return _D


@njit(cache=True)
def _sim(o, h, l, c, sp, ie, d, rd, tpr, ix, tp1r, tp1f, be, trf, trd, comm_px, tpdelay):
    n = ie.shape[0]
    R = np.zeros(n); why = np.zeros(n, np.int64); held = np.zeros(n, np.int64)
    mfe = np.zeros(n); mae = np.zeros(n); iout = np.zeros(n, np.int64)
    for t in range(n):
        i = ie[t]; dd = d[t]; r = rd[t]
        ent = o[i] + (sp[i] if dd > 0 else 0.0)
        sl = ent - dd * r
        tp = ent + dd * tpr[t] * r if tpr[t] > 0.0 else 0.0
        frac_left = 1.0; acc = 0.0; t1 = tp1r <= 0.0; bmfe = 0.0; bmae = 0.0
        j = i; res = -1
        while True:
            if j >= ix[t] or j >= o.shape[0]:
                jj = min(j, o.shape[0] - 1)
                px = o[jj] + (sp[jj] if dd < 0 else 0.0)
                acc += frac_left * (px - ent) * dd; res = 0; break
            lo = l[j]; hi = h[j]; s_ = sp[j]
            if dd > 0:
                fav = (hi - ent) / r; adv = (ent - lo) / r
                hit_sl = lo <= sl; hit_tp = tp > 0.0 and hi >= tp
            else:
                fav = (ent - (lo + s_)) / r; adv = ((hi + s_) - ent) / r
                hit_sl = hi + s_ >= sl; hit_tp = tp > 0.0 and lo + s_ <= tp
            if hit_sl:
                px = sl
                if dd > 0 and o[j] < sl:
                    px = o[j]
                if dd < 0 and o[j] + s_ > sl:
                    px = o[j] + s_
                acc += frac_left * (px - ent) * dd; res = 1
                if adv > bmae:
                    bmae = adv
                break
            if hit_tp and j - i >= tpdelay:
                acc += frac_left * (tp - ent) * dd; res = 2
                if fav > bmfe:
                    bmfe = fav
                break
            if fav > bmfe:
                bmfe = fav
            if adv > bmae:
                bmae = adv
            if not t1 and j - i >= tpdelay:
                lvl = ent + dd * tp1r * r
                if (dd > 0 and hi >= lvl) or (dd < 0 and lo + s_ <= lvl):
                    t1 = True
                    if tp1f > 0.0:
                        acc += tp1f * (lvl - ent) * dd; frac_left -= tp1f
                    if be > -9.0:
                        cand = ent + dd * be * r
                        if (cand - sl) * dd > 0.0:
                            sl = cand
            if trf > 0.0 and bmfe >= trf:
                cand = ent + dd * (bmfe - trd) * r
                if (cand - sl) * dd > 0.0:
                    sl = cand
            j += 1
        R[t] = (acc - comm_px) / r; why[t] = res; held[t] = j - i; mfe[t] = bmfe; mae[t] = bmae; iout[t] = j
    return R, why, held, mfe, mae, iout


def simulate(sym, ie, d, rd, tpr, ix, tp1r=0.0, tp1f=0.0, be=-99.0, trf=0.0, trd=0.0, tpdelay=1):
    D = data()[sym]
    k = SYM[sym]
    n = len(ie)
    tpr = np.broadcast_to(np.asarray(tpr, float), (n,)).copy()
    return _sim(D["o"], D["h"], D["l"], D["c"], D["sp"], np.asarray(ie, np.int64), np.asarray(d, np.int64),
                np.asarray(rd, float), tpr, np.asarray(ix, np.int64), float(tp1r), float(tp1f), float(be),
                float(trf), float(trd), COMM[k] / MPP[k], int(tpdelay))


def metrics(R, t_ny, label=""):
    R = np.asarray(R, float); t_ny = np.asarray(t_ny)
    n = len(R)
    if n == 0:
        return dict(n=0)
    yrs = max((t_ny.max() - t_ny.min()) / 1440 / 365.25, 1e-9)
    order = np.argsort(t_ny, kind="stable")
    Rs = R[order]
    cur = 0; mx = 0; n6 = 0
    for x in Rs:
        if x < 0:
            cur += 1
            mx = max(mx, cur)
            if cur == 6:
                n6 += 1
        else:
            cur = 0
    cum = np.cumsum(Rs); dd = np.max(np.maximum.accumulate(np.r_[0.0, cum])[1:] - cum) if n else 0.0
    wins = Rs[Rs > 0].sum(); loss = -Rs[Rs < 0].sum()
    yr = (t_ny[order] // 1440 // 365.25 + 1970).astype(int)
    per_year = {int(y): float(Rs[yr == y].sum()) for y in np.unique(yr)}
    day = t_ny[order] // 1440
    ud, inv = np.unique(day, return_inverse=True)
    dsum = np.zeros(len(ud)); np.add.at(dsum, inv, Rs)
    sh = float(dsum.mean() / dsum.std() * np.sqrt(252)) if len(dsum) > 2 and dsum.std() > 0 else 0.0
    return dict(label=label, n=n, tpy=n / yrs, wr=float((Rs > 0).mean() * 100), avgR=float(Rs.mean()),
                pf=float(wins / loss) if loss > 0 else np.inf, Ry=float(Rs.sum() / yrs), maxS=mx, s6y=n6 / yrs,
                ddR=float(dd), sharpe=sh, years=per_year)


def show(m):
    if m.get("n", 0) == 0:
        print(f"{m.get('label',''):<40s} keine Trades"); return
    ys = " ".join(f"{y}:{v:+.1f}" for y, v in m["years"].items())
    print(f"{m['label']:<40s} n {m['n']:5d} ({m['tpy']:5.1f}/J) WR {m['wr']:5.1f}% ØR {m['avgR']:+.3f} PF {m['pf']:4.2f} "
          f"R/J {m['Ry']:+6.1f} maxS {m['maxS']:2d} S6/J {m['s6y']:4.2f} DD {m['ddR']:5.1f}R Sh {m['sharpe']:4.2f} | {ys}")


# ------------------------------------------------------------------ Hilfen fuer Signal-Generatoren
def day_index(ny):
    return ny // 1440


def idx_at(ny, t):
    """erster M5-Index mit ny >= t (t: Array)."""
    return np.searchsorted(ny, t, side="left")
