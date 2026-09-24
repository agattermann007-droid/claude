"""Bewertung: rollierende Starts (jeder step-te Handelstag ein frisches 10k-Konto, Laufzeit 1/2/3 Jahre),
gemittelt ueber Stoerungen (Seeds: zufaelliges Auslassen von Signalen + Einstiegsschlupf).
Kennzahlen je Jahr = Summe ueber alle Starts / Summe der Laufzeiten.
Serien werden aus dem Trade-Protokoll berechnet (Reihenfolge der Schliessungen)."""
import numpy as np, time, json, os
from concurrent.futures import ProcessPoolExecutor
import eng5 as E

WARM = "2022-03-21"            # EMA50/SMA-Vorlauf
_MK = None


def mk():
    global _MK
    if _MK is None:
        _MK = E.Market(os.environ.get("SIG5", "sig5.pkl"))
    return _MK


_MASKS = {}


def masks(m, seed, skip):
    key = (seed, skip)
    if key not in _MASKS:
        _MASKS[key] = E.make_masks(m, seed, skip)
    return _MASKS[key]


def streaks(pnls):
    """Serien aufeinanderfolgender Verlusttrades: Anzahl >=5, >=8, Maximum, Summe der Verluste der schlimmsten Serie."""
    cur = 0; mx = 0; n5 = 0; n8 = 0; s = 0.0; worst = 0.0
    for x in pnls:
        if x < 0:
            cur += 1; s += x
            if cur == 5:
                n5 += 1
            if cur == 8:
                n8 += 1
            if cur > mx:
                mx = cur
            if s < worst:
                worst = s
        else:
            cur = 0; s = 0.0
    return n5, n8, mx, worst


def ideas(tr):
    """Trade-Folge je Idee: Noise-Teile (Plaetze 6..8) mit gleicher Einstiegs-ID = ein Trade,
    einsortiert an der Stelle der letzten Teilschliessung."""
    if len(tr) == 0:
        return np.zeros(0)
    items = []
    nz = {}
    for i, row in enumerate(tr):
        if int(row[2]) >= 6:
            pid = row[3]
            s, _ = nz.get(pid, (0.0, i))
            nz[pid] = (s + row[1], i)
        else:
            items.append((i, row[1]))
    for pid, (s, i) in nz.items():
        items.append((i, s))
    items.sort()
    return np.array([x[1] for x in items])


def day_streaks(tr):
    """Verlusttage in Folge (Tage mit Schliessungen)."""
    if len(tr) == 0:
        return 0, 0
    days = tr[:, 0]; pnl = tr[:, 1]
    ud, inv = np.unique(days, return_inverse=True)
    dsum = np.zeros(len(ud)); np.add.at(dsum, inv, pnl)
    cur = 0; mx = 0; n3 = 0
    for x in dsum:
        if x < 0:
            cur += 1
            if cur == 3:
                n3 += 1
            mx = max(mx, cur)
        else:
            cur = 0
    return mx, n3


def one(Pv, d0, d1, seed, skip, slip):
    m = mk()
    Pv = Pv.copy()
    if seed > 0:
        Pv[E.PI["slip_frac"]] = slip
    ms = masks(m, seed, skip if seed > 0 else 0.0)
    r = E.run(m, Pv, d0, d1, seed=seed, masks=ms)
    st = r["st"]; S = E.SI; tr = r["tr"]; ev = r["ev"]
    pnls = ideas(tr)
    n5, n8, mx, worst = streaks(pnls)
    dmx, d3 = day_streaks(tr) if len(tr) else (0, 0)
    pays = ev[ev[:, 0] == 1, 2] if len(ev) else np.zeros(0)
    if len(tr):
        slot = tr[:, 2]
        mdb = slot < 2; mr = (slot >= 2) & (slot < 6); mz = slot >= 6
        db_p, r_p, z_p = tr[mdb, 1].sum(), tr[mr, 1].sum(), tr[mz, 1].sum()
        db_n, r_n = float(mdb.sum()), float(mr.sum())
        db_w, r_w = float((tr[mdb, 1] > 0).sum()), float((tr[mr, 1] > 0).sum())
    else:
        db_p = r_p = z_p = db_n = r_n = db_w = r_w = 0.0
    busts = int(st[S["nbust"]])
    return dict(years=r["years"], npay=float(st[S["npay"]]), sumpay=float(st[S["sumpay"]]), nbust=busts,
                floor_b=float(st[S["floor_b"]]), float_b=float(st[S["float_b"]]), day_b=float(st[S["day_b"]]),
                ntr=float(len(pnls)), wins=float((pnls > 0).sum()), n5=n5, n8=n8, mx=mx, worst=worst,
                dmx=dmx, d3=d3, gapmax=float(st[S["gaps_max"]]), maxdd=float(st[S["maxdd"]]),
                valid=float(st[S["valid_days"]]), tdays=float(st[S["trade_days"]]), ldays=float(st[S["loss_days"]]),
                db_tr=db_n, db_pnl=float(db_p), r21_tr=r_n, db_w=db_w, r21_w=r_w,
                r21_pnl=float(r_p), nz_tr=float(st[S["nz_tr"]]), nz_pnl=float(z_p),
                harv=float(st[S["harv"]]), bank=float(st[S["bank"]]), ge=float(st[S["ge"]]), cool=float(st[S["cool"]]),
                ripe_lost=float(st[S["ripe_lost"]]), cyc=float(st[S["cyc_days"]]), brake_f=float(st[S["brake_f"]]),
                paymin=float(pays.min()) if len(pays) else 0.0)


def _job(args):
    Pv, d0, d1, seed, skip, slip = args
    return one(Pv, d0, d1, seed, skip, slip)


def starts(m, horizon, step, warm=WARM):
    a = m.day_index(warm)
    last = len(m.days) - 1
    return [(s, s + horizon) for s in range(a, last - horizon + 1, step)]


def agg(rows):
    Y = sum(r["years"] for r in rows)
    npay = sum(r["npay"] for r in rows); nb = sum(r["nbust"] for r in rows); sp = sum(r["sumpay"] for r in rows)
    ntr = sum(r["ntr"] for r in rows); wins = sum(r["wins"] for r in rows)
    out = dict(pay=npay / Y, bust=nb / Y, net=(0.8 * 0.97 * sp - 148.5 * nb) / Y, net_old=(0.8 * sp - 148.5 * nb) / Y,
               gross=sp / Y, paymean=sp / max(npay, 1), tr=ntr / Y, wr=100.0 * wins / max(ntr, 1),
               s5=sum(r["n5"] for r in rows) / Y, s8=sum(r["n8"] for r in rows) / Y,
               d3=sum(r["d3"] for r in rows) / Y,
               mx=float(np.mean([r["mx"] for r in rows])), worst=float(np.mean([r["worst"] for r in rows])),
               dmx=float(np.mean([r["dmx"] for r in rows])),
               gapmax=float(np.mean([r["gapmax"] for r in rows])), maxdd=float(np.mean([r["maxdd"] for r in rows])),
               floor_b=sum(r["floor_b"] for r in rows) / Y, float_b=sum(r["float_b"] for r in rows) / Y,
               day_b=sum(r["day_b"] for r in rows) / Y,
               valid=sum(r["valid"] for r in rows) / Y, ldays=sum(r["ldays"] for r in rows) / Y,
               tdays=sum(r["tdays"] for r in rows) / Y,
               db_pnl=sum(r["db_pnl"] for r in rows) / Y, r21_pnl=sum(r["r21_pnl"] for r in rows) / Y,
               nz_pnl=sum(r["nz_pnl"] for r in rows) / Y,
               db_tr=sum(r["db_tr"] for r in rows) / Y, r21_tr=sum(r["r21_tr"] for r in rows) / Y,
               nz_tr=sum(r["nz_tr"] for r in rows) / Y, harv=sum(r["harv"] for r in rows) / Y,
               db_wr=100.0 * sum(r["db_w"] for r in rows) / max(sum(r["db_tr"] for r in rows), 1),
               r21_wr=100.0 * sum(r["r21_w"] for r in rows) / max(sum(r["r21_tr"] for r in rows), 1),
               bank=sum(r["bank"] for r in rows) / Y, ge=sum(r["ge"] for r in rows) / Y,
               cyc=sum(r["cyc"] for r in rows) / max(npay, 1), ripe_lost=sum(r["ripe_lost"] for r in rows) / Y,
               p_nopay=float(np.mean([r["npay"] == 0 for r in rows])),
               p_bust=float(np.mean([r["nbust"] > 0 for r in rows])), n=len(rows))
    return out


def evaluate(Pv, horizons=(250, 500, 750), step=3, seeds=tuple(range(8)), skip=0.03, slip=0.3, workers=4, warm=WARM):
    m = mk()
    res = {}
    jobs = []
    for h in horizons:
        for (a, b) in starts(m, h, step, warm):
            for s in seeds:
                jobs.append((h, (Pv, a, b, s, skip, slip)))
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            outs = list(ex.map(_job, [j[1] for j in jobs], chunksize=64))
    else:
        outs = [_job(j[1]) for j in jobs]
    byh = {}
    for (h, _), o in zip(jobs, outs):
        byh.setdefault(h, []).append(o)
    for h in horizons:
        res[h] = agg(byh[h])
    # Mittel ueber die Laufzeiten (gleich gewichtet)
    keys = res[horizons[0]].keys()
    res["mean"] = {k: float(np.mean([res[h][k] for h in horizons])) for k in keys}
    return res


def path(Pv, d0="2022-01-03", seeds=tuple(range(8)), skip=0.03, slip=0.3):
    m = mk()
    a = m.day_index(d0); b = len(m.days)
    rows = [one(Pv, a, b, s, skip, slip) for s in seeds]
    return agg(rows), rows


def line(label, r):
    return (f"{label:<38s} Ausz/J {r['pay']:5.2f}  Busts/J {r['bust']:4.2f}  Netto/J {r['net']:6.0f}  "
            f"$/Ausz {r['paymean']:4.0f}  Luecke {r['gapmax']:5.1f}d  S5/J {r['s5']:4.1f} S8/J {r['s8']:4.2f} "
            f"maxS {r['mx']:4.1f}  VTage3/J {r['d3']:4.1f}  Tr/J {r['tr']:5.0f} WR {r['wr']:4.1f}  "
            f"DD {r['maxdd']:4.0f}  ohneAusz {100*r['p_nopay']:4.1f}%")
