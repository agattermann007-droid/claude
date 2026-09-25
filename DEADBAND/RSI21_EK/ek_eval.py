"""RSI21 Eigenkapital - Kennzahlen aus einem ek_sim.run-Ergebnis (Tages-Equity und Trades)."""
import numpy as np

SYMN = ("Gold", "NAS")


def day_dates(res):
    return res["day"][:, 0].astype(np.int64).astype("datetime64[D]")


def metrics(res, a=None, b=None):
    """CAGR, Endwert, groesster Rueckgang (Tagesschluss), Trades, Trefferquote, R je Trade, PF - optional nur [a, b)."""
    day = res["day"]
    if len(day) < 2:
        return dict(cagr=0.0, final=res["start"], maxdd=0.0, years=0.0, ntr=0, wr=0.0, avgR=0.0, pf=0.0)
    dd_ = day[:, 0].astype(np.int64)
    m = np.ones(len(day), bool)
    if a is not None:
        m &= dd_ >= np.datetime64(a, "D").astype(np.int64)
    if b is not None:
        m &= dd_ < np.datetime64(b, "D").astype(np.int64)
    eq = day[m, 1]
    if len(eq) < 2 or eq[0] <= 0:
        return dict(cagr=0.0, final=eq[-1] if len(eq) else res["start"], maxdd=0.0, years=0.0, ntr=0, wr=0.0, avgR=0.0, pf=0.0)
    years = (dd_[m][-1] - dd_[m][0]) / 365.25
    ratio = max(eq[-1], 1e-9) / eq[0]
    cagr = ratio ** (1.0 / years) - 1.0 if years > 0 else 0.0
    peak = np.maximum.accumulate(eq)
    maxdd = float(np.max(1.0 - eq / peak))
    r = np.diff(np.log(np.maximum(eq, 1e-9)))
    sharpe = float(np.mean(r) / np.std(r) * np.sqrt(252)) if np.std(r) > 0 else 0.0
    vol = float(np.std(r) * np.sqrt(252))
    tr = res["tr"]
    if len(tr):
        tin = tr[:, 16]
        tm = np.ones(len(tr), bool)
        if a is not None or b is not None:
            # Trade-Zuordnung ueber den Einstieg (NY-Minute; bei clock_eng10 Servertag*1440 + NY-Minute)
            t_day = (tin // 1440).astype(np.int64)
            if a is not None:
                tm &= t_day >= np.datetime64(a, "D").astype(np.int64) - 1
            if b is not None:
                tm &= t_day < np.datetime64(b, "D").astype(np.int64)
        tr = tr[tm]
    R = (tr[:, 9] - tr[:, 10]) / np.maximum(tr[:, 12], 1e-9) if len(tr) else np.zeros(0)
    gp = R[R > 0].sum(); gl = -R[R < 0].sum()
    return dict(cagr=float(cagr), final=float(eq[-1]), start=float(eq[0]), maxdd=maxdd, years=float(years), sharpe=sharpe, vol=vol,
                ntr=int(len(tr)), tr_y=float(len(tr) / years) if years > 0 else 0.0,
                wr=float((R > 0).mean()) if len(R) else 0.0, avgR=float(R.mean()) if len(R) else 0.0,
                pf=float(gp / gl) if gl > 0 else float("inf"), sumR=float(R.sum()),
                calmar=float(cagr / maxdd) if maxdd > 0 else float("inf"))


def by_year(res):
    day = res["day"]
    d = day[:, 0].astype(np.int64).astype("datetime64[D]")
    y = d.astype("datetime64[Y]").astype(int) + 1970
    out = {}
    prev = None
    for yy in np.unique(y):
        m = y == yy
        eq = day[m, 1]
        first = prev if prev is not None else eq[0]
        pk = np.maximum.accumulate(np.r_[first, eq])
        out[int(yy)] = dict(ret=float(eq[-1] / first - 1.0), maxdd=float(np.max(1.0 - np.r_[first, eq] / pk)))
        prev = eq[-1]
    return out


def trades_R(res):
    tr = res["tr"]
    return (tr[:, 9] - tr[:, 10]) / np.maximum(tr[:, 12], 1e-9)


def fmt(m):
    return (f"CAGR {100 * m['cagr']:6.1f} %  maxDD {100 * m['maxdd']:5.1f} %  Endwert {m['final']:14,.0f}  "
            f"Trades/J {m.get('tr_y', 0):5.1f}  Treffer {100 * m['wr']:4.1f} %  R/Trade {m['avgR']:+.3f}  PF {m['pf']:.2f}")
