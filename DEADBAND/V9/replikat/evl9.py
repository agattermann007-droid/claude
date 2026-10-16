"""Replikat 9 - Bewertung nach dem Testprotokoll V9 (vorab festgelegt).

Konto-Ebene: jeden 3. Handelstag ein frisches 10k-Konto, Laufzeit 1 Jahr (250 Handelstage) und 2 Jahre (500), Starts so,
dass die Laufzeit im Fenster liegt. Kennzahlen je Jahr Laufzeit: Auszahlungen, Busts, Netto = 0,8 x Auszahlungen
- 148,50 $ je Neukauf nach Bust (Formel aus dem Auftrag). Dazu die Netto-Werte je Startjahr (Robustheit 5 von 7).
"""
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import eng9 as E

FENSTER = {"A": ("2016-01-01", "2021-12-31"), "B": ("2022-01-01", "2026-10-16")}
_MK = None
_GP = None


def setze(mk, GP):
    """vor dem Start der Prozesse aufrufen (fork uebernimmt den Zustand)."""
    global _MK, _GP
    _MK = mk; _GP = GP


def _job(args):
    Pv, d0, d1 = args
    r = E.run(_MK, Pv, d0, d1, seed=0, masks=None, GP=_GP)
    st = r["st"]; S = E.SI; tr = r["tr"]
    gs = {}
    for row in tr:                                   # Ergebnis je Strom (Trade-Protokoll: Platz -> Strom)
        sl = int(row[2])
        key = "r21" if 2 <= sl < E.NZ0 else ("nz" if E.NZ0 <= sl < E.NZ1 else (f"g{(sl - E.G0) // 2}" if sl >= E.G0 else "db"))
        a = gs.setdefault(key, [0.0, 0, 0])
        a[0] += row[1]; a[1] += 1; a[2] += int(row[1] > 0)
    return dict(d0=d0, years=r["years"], npay=float(st[S["npay"]]), sumpay=float(st[S["sumpay"]]), nbust=int(st[S["nbust"]]),
                floor_b=float(st[S["floor_b"]]), float_b=float(st[S["float_b"]]), day_b=float(st[S["day_b"]]),
                valid=float(st[S["valid_days"]]), ntr=float(st[S["entries"]]), gs=gs)


def starts(mk, fenster, h, step=3):
    a = mk.day_index(fenster[0]); b = mk.day_index(fenster[1])
    b = min(b, len(mk.days) - 1)
    return [(s, s + h) for s in range(a, b - h + 1, step)]


def agg(rows):
    Y = sum(r["years"] for r in rows)
    npay = sum(r["npay"] for r in rows); nb = sum(r["nbust"] for r in rows); sp = sum(r["sumpay"] for r in rows)
    out = dict(pay=npay / Y, bust=nb / Y, net=(0.8 * sp - 148.5 * nb) / Y, gross=sp / Y, paymean=sp / max(npay, 1),
               valid=sum(r["valid"] for r in rows) / Y, p_bust=float(np.mean([r["nbust"] > 0 for r in rows])), n=len(rows),
               floor_b=sum(r["floor_b"] for r in rows) / Y, float_b=sum(r["float_b"] for r in rows) / Y,
               day_b=sum(r["day_b"] for r in rows) / Y)
    gs = {}
    for r in rows:
        for k, (x, n, w) in r["gs"].items():
            a = gs.setdefault(k, [0.0, 0, 0]); a[0] += x; a[1] += n; a[2] += w
    out["gs"] = {k: dict(pnl=a[0] / Y, tr=a[1] / Y, wr=100.0 * a[2] / max(a[1], 1)) for k, a in gs.items()}
    return out


def bewerte(mk, Pv, GP, fenster=("A", "B"), horizonte=(250, 500), step=3, workers=4):
    setze(mk, GP)
    jobs, tags = [], []
    for f in fenster:
        for h in horizonte:
            for (a, b) in starts(mk, FENSTER[f], h, step):
                jobs.append((Pv, a, b)); tags.append((f, h, a))
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            outs = list(ex.map(_job, jobs, chunksize=8))
    else:
        outs = [_job(j) for j in jobs]
    res = {}
    for (f, h, a), o in zip(tags, outs):
        res.setdefault((f, h), []).append(o)
    erg = {}
    for (f, h), rows in res.items():
        g = agg(rows)
        jahre = {}
        for r in rows:
            y = int(str(np.datetime64(int(mk.days[r["d0"]]), "D"))[:4])
            jahre.setdefault(y, []).append(r)
        g["jahre"] = {y: agg(v) for y, v in sorted(jahre.items())}
        erg[f"{f}{h // 250}J"] = g
    return erg


def zeile(lbl, e):
    t = []
    for k in sorted(e):
        g = e[k]
        t.append(f"{k}: {g['pay']:5.2f}/{g['bust']:5.3f}/{g['net']:6.0f}")
    return f"{lbl:<34s} " + " | ".join(t)
