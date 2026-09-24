"""Bewertung v6: wie evl5, zusaetzlich generische Stroeme (GP), Serien >= 6, kleinste Auszahlung, Modul-Ergebnisse.
Rollierende Starts (jeder step-te Handelstag ein frisches 10k-Konto, Laufzeit 1/2/3 Jahre), Stoerungen (Seeds)."""
import numpy as np, os
from concurrent.futures import ProcessPoolExecutor
import eng6 as E

WARM = "2022-03-21"
_MK = None
_MASKS = {}
_GP = None


def mk():
    global _MK
    if _MK is None:
        _MK = E.Market(os.environ.get("SIG5", "sig5.pkl"))
    return _MK


def set_generic(sigs, GP):
    """Signale der neuen Strategien setzen (vor dem Start der Prozesse aufrufen; fork uebernimmt den Zustand)."""
    global _GP
    m = mk()
    m.set_generic(sigs)
    _MASKS.clear()
    _GP = GP


def masks(m, seed, skip):
    key = (seed, skip)
    if key not in _MASKS:
        _MASKS[key] = E.make_masks(m, seed, skip)
    return _MASKS[key]


def streaks(pnls):
    cur = 0; mx = 0; n5 = 0; n6 = 0; n8 = 0; s = 0.0; worst = 0.0
    for x in pnls:
        if x < 0:
            cur += 1; s += x
            if cur == 5:
                n5 += 1
            if cur == 6:
                n6 += 1
            if cur == 8:
                n8 += 1
            mx = max(mx, cur)
            worst = min(worst, s)
        else:
            cur = 0; s = 0.0
    return n5, n6, n8, mx, worst


def ideas(tr):
    """Trade-Folge je Idee: Noise-Teile (Plaetze 6..8) mit gleicher Einstiegszeit = ein Trade."""
    if len(tr) == 0:
        return np.zeros(0), np.zeros(0, np.int64)
    items = []; nz = {}
    for i, row in enumerate(tr):
        sl = int(row[2])
        if E.NZ0 <= sl < E.NZ1:
            pid = row[3]
            s, _ = nz.get(pid, (0.0, i))
            nz[pid] = (s + row[1], i)
        else:
            items.append((i, row[1], sl))
    for pid, (s, i) in nz.items():
        items.append((i, s, E.NZ0))
    items.sort()
    return np.array([x[1] for x in items]), np.array([x[2] for x in items], np.int64)


def modname(sl):
    if sl < 2:
        return "db"
    if sl < E.NZ0:
        return "r21"
    if sl < E.NZ1:
        return "nz"
    return f"g{(sl - E.G0) // 2}"


def one(Pv, d0, d1, seed, skip, slip, GP):
    m = mk()
    Pv = Pv.copy()
    if seed > 0:
        Pv[E.PI["slip_frac"]] = slip
    ms = masks(m, seed, skip if seed > 0 else 0.0)
    r = E.run(m, Pv, d0, d1, seed=seed, masks=ms, GP=GP)
    st = r["st"]; S = E.SI; tr = r["tr"]; ev = r["ev"]
    pnls, slots = ideas(tr)
    n5, n6, n8, mx, worst = streaks(pnls)
    pays = ev[ev[:, 0] == 1, 2] if len(ev) else np.zeros(0)
    mods = {}
    for x, sl in zip(pnls, slots):
        nm = modname(int(sl))
        a = mods.setdefault(nm, [0.0, 0, 0])
        a[0] += x; a[1] += 1; a[2] += int(x > 0)
    return dict(years=r["years"], npay=float(st[S["npay"]]), sumpay=float(st[S["sumpay"]]), nbust=int(st[S["nbust"]]),
                floor_b=float(st[S["floor_b"]]), float_b=float(st[S["float_b"]]), day_b=float(st[S["day_b"]]),
                ntr=float(len(pnls)), wins=float((pnls > 0).sum()), n5=n5, n6=n6, n8=n8, mx=mx, worst=worst,
                gapmax=float(st[S["gaps_max"]]), maxdd=float(st[S["maxdd"]]), valid=float(st[S["valid_days"]]),
                cool=float(st[S["cool"]]), bank=float(st[S["bank"]]), ge=float(st[S["ge"]]), harv=float(st[S["harv"]]),
                cyc=float(st[S["cyc_days"]]), paymin=float(pays.min()) if len(pays) else 0.0, mods=mods)


def _job(args):
    return one(*args)


def starts(m, horizon, step, warm=WARM, end=None):
    a = m.day_index(warm)
    last = (len(m.days) - 1) if end is None else m.day_index(end)
    return [(s, s + horizon) for s in range(a, last - horizon + 1, step)]


def agg(rows):
    Y = sum(r["years"] for r in rows)
    npay = sum(r["npay"] for r in rows); nb = sum(r["nbust"] for r in rows); sp = sum(r["sumpay"] for r in rows)
    ntr = sum(r["ntr"] for r in rows); wins = sum(r["wins"] for r in rows)
    out = dict(pay=npay / Y, bust=nb / Y, net=(0.8 * 0.97 * sp - 148.5 * nb) / Y, gross=sp / Y, paymean=sp / max(npay, 1),
               paymin=float(np.min([r["paymin"] for r in rows if r["npay"] > 0])) if any(r["npay"] > 0 for r in rows) else 0.0,
               tr=ntr / Y, wr=100.0 * wins / max(ntr, 1),
               s5=sum(r["n5"] for r in rows) / Y, s6=sum(r["n6"] for r in rows) / Y, s8=sum(r["n8"] for r in rows) / Y,
               mx=float(np.mean([r["mx"] for r in rows])), mxmax=float(np.max([r["mx"] for r in rows])),
               p_s6=float(np.mean([r["n6"] > 0 for r in rows])),
               worst=float(np.mean([r["worst"] for r in rows])), gapmax=float(np.mean([r["gapmax"] for r in rows])),
               maxdd=float(np.mean([r["maxdd"] for r in rows])), valid=sum(r["valid"] for r in rows) / Y,
               cool=sum(r["cool"] for r in rows) / Y, bank=sum(r["bank"] for r in rows) / Y, ge=sum(r["ge"] for r in rows) / Y,
               cyc=sum(r["cyc"] for r in rows) / max(npay, 1),
               p_bust=float(np.mean([r["nbust"] > 0 for r in rows])), n=len(rows))
    mods = {}
    for r in rows:
        for nm, (x, n, w) in r["mods"].items():
            a = mods.setdefault(nm, [0.0, 0, 0])
            a[0] += x; a[1] += n; a[2] += w
    out["mods"] = {nm: dict(pnl=a[0] / Y, tr=a[1] / Y, wr=100.0 * a[2] / max(a[1], 1)) for nm, a in mods.items()}
    return out


def evaluate(Pv, GP=None, horizons=(250, 500, 750), step=3, seeds=tuple(range(8)), skip=0.03, slip=0.3, workers=4,
             warm=WARM, end=None):
    m = mk()
    if GP is None:
        GP = _GP if _GP is not None else E.gparams([])
    jobs = []
    for h in horizons:
        for (a, b) in starts(m, h, step, warm, end):
            for s in seeds:
                jobs.append((h, (Pv, a, b, s, skip, slip, GP)))
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            outs = list(ex.map(_job, [j[1] for j in jobs], chunksize=32))
    else:
        outs = [_job(j[1]) for j in jobs]
    byh = {}
    for (h, _), o in zip(jobs, outs):
        byh.setdefault(h, []).append(o)
    res = {h: agg(byh[h]) for h in horizons if h in byh}
    hs = [h for h in horizons if h in res]
    keys = [k for k in res[hs[0]].keys() if k != "mods"]
    res["mean"] = {k: float(np.mean([res[h][k] for h in hs])) for k in keys}
    res["mean"]["mxmax"] = float(np.max([res[h]["mxmax"] for h in hs]))
    res["mean"]["p_bust1"] = res[hs[0]]["p_bust"]
    res["mean"]["mods"] = res[hs[0]]["mods"]
    return res


def line(label, r):
    mods = " ".join(f"{k}:{v['pnl']:.0f}/{v['tr']:.0f}/{v['wr']:.0f}%" for k, v in sorted(r.get("mods", {}).items()))
    return (f"{label:<34s} Ausz {r['pay']:5.2f} Ø{r['paymean']:4.0f}$ min{r['paymin']:4.0f} Bust {r['bust']:5.3f} "
            f"P(B)1J {r.get('p_bust1', r['p_bust']):5.3f} Netto {r['net']:5.0f} S5 {r['s5']:5.2f} S6 {r['s6']:5.2f} "
            f"maxS {r['mx']:4.1f}/{r['mxmax']:.0f} Tr {r['tr']:4.0f} WR {r['wr']:4.1f} | {mods}")
