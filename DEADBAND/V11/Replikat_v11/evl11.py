"""Replikat v11 - Bewertung auf Kontoebene: rollierende Starts (alle 7 Tage ein frisches 10k-Konto, 1 Jahr Laufzeit).

Kennzahlen je Fenster (Startdatum im Fenster):
  pay      Auszahlungen je Konto-Jahr
  net      $ je Jahr (Anteil 80 %, minus 3 % Auszahlungsgebuehr, minus 148,50 $ je Bust)
  net_open wie net, zusaetzlich der am Ende noch nicht ausgezahlte Gewinn (Saldo - Start, auch negativ)
  avg      Durchschnittliche Auszahlung (Brutto-Gewinn je Auszahlung)
  first    Median der Tage bis zur ersten Auszahlung (nur Konten mit Auszahlung)
  zero     Anteil der Konto-Jahre ohne Auszahlung
  bust     Busts (Summe)
"""
import numpy as np, os, json
from concurrent.futures import ProcessPoolExecutor
import mk11, eng11 as E

_MK = None
WIN = {"Auswahl 2022": ("2022-01-03", "2022-12-31"), "2023": ("2023-01-01", "2023-12-31"),
       "Pruef 2024-25": ("2024-01-01", "2025-02-13"), "Pruef 2017-20": ("2017-01-02", "2020-12-31")}


def mk():
    global _MK
    if _MK is None:
        _MK = mk11.Market()
    return _MK


def starts(m, lo, hi, step=7, horizon=365):
    a = m.day_index(lo); b = m.day_index(hi)
    out = []
    d = int(m.days[a])
    while d <= int(m.days[min(b, len(m.days) - 1)]):
        i0 = m.day_index(str(np.datetime64(d, "D")))
        i1 = m.day_index(str(np.datetime64(d + horizon, "D")))
        if i1 < len(m.days) and m.days[i1] - d >= horizon - 3:
            out.append((i0, i1))
        d += step
    return out


def _hash(*cols, seed=0):
    x = np.zeros(len(cols[0]))
    for i, c in enumerate(cols):
        x = x + np.asarray(c, float) * (12.9898 + 7.233 * i)
    x = np.sin(x + seed * 37.719) * 43758.5453
    return x - np.floor(x)


_ORIG = {}


def _apply_seed(m, seed, frac=0.03):
    """Gepaarte Stoerung: je Seed faellt ein fester Anteil der Signale weg (Auswahl ueber die Signal-Identitaet, also in
    Basis und Variante dieselben Signale). Seed 0 = alle Signale."""
    if "r" not in _ORIG:
        _ORIG.update(r=m.r, z=m.z, g=m.g, ev=None)
    r0, z0, g0 = _ORIG["r"], _ORIG["z"], _ORIG["g"]
    if seed == 0:
        m.r, m.z, m.g = r0, z0, g0
        return
    key = ("seed", seed, frac)
    if key not in _ORIG:
        for k_ in [k_ for k_ in _ORIG if isinstance(k_, tuple)]:
            del _ORIG[k_]                       # nur die Maske des aktuellen Seeds behalten (Speicher)
        def sub(d, keep):
            out = {k: (v[keep] if isinstance(v, np.ndarray) and k != "next" and len(v) == len(keep) else v) for k, v in d.items()}
            out["next"] = m._next(out["ev"])
            return out
        _ORIG[key] = (sub(r0, _hash(r0["ev"], r0["sym"], r0["tf"], seed=seed) >= frac),
                      sub(z0, _hash(z0["ev"], seed=seed) >= frac),
                      sub(g0, _hash(m.ev_t[g0["ev"]], g0["str"], g0["sym"], seed=seed) >= frac))
    m.r, m.z, m.g = _ORIG[key]


def reset_seed_cache():
    _ORIG.clear()


def _one(args):
    Pv, GP, a, b = args[:4]
    seed = args[4] if len(args) > 4 else 0
    m = mk()
    _apply_seed(m, seed)
    r = m.run(Pv, GP, a, b)
    st = r["st"]; S = E.SI
    pays = r["ev"][r["ev"][:, 0] == 1, 2] if len(r["ev"]) else np.zeros(0)
    tr = r["tr"]
    mods = {}
    for row in tr:
        s_ = int(row[4]); sl = int(row[2])
        key = "r21" if sl < E.NZ0 else ("nz" if sl < E.NZ1 else f"g{s_}")
        a_ = mods.setdefault(key, [0.0, 0, 0])
        a_[0] += row[1]; a_[1] += 1; a_[2] += int(row[1] > 0)
    return dict(years=r["years"], npay=st[S["npay"]], sumpay=st[S["sumpay"]], nbust=st[S["nbust"]], first=st[S["first_pay"]],
                end_bal=st[S["end_bal"]], start=float(m.days[a]), valid=st[S["valid_days"]], bank=st[S["bank"]],
                ge=st[S["ge"]], cool=st[S["cool"]], gs=st[S["gs_block"]], brake_f=st[S["brake_f"]], brake_d=st[S["brake_d"]],
                floor_b=st[S["floor_b"]], float_b=st[S["float_b"]], day_b=st[S["day_b"]], maxstreak=st[S["maxstreak"]],
                lim_valid=st[S["lim_valid"]], lim_profit=st[S["lim_profit"]], lim_ten=st[S["lim_ten"]],
                ntr=st[S["ntr"]], wins=st[S["wins"]], paymin=float(pays.min()) if len(pays) else 0.0, mods=mods)


def agg(rows, start=10000.0):
    Y = sum(r["years"] for r in rows)
    npay = sum(r["npay"] for r in rows); sp = sum(r["sumpay"] for r in rows); nb = sum(r["nbust"] for r in rows)
    openp = sum(r["end_bal"] - start for r in rows)
    firsts = [r["first"] for r in rows if r["npay"] > 0]
    out = dict(n=len(rows), pay=npay / Y, net=(0.8 * 0.97 * sp - 148.5 * nb) / Y, net_open=(0.8 * 0.97 * (sp + openp) - 148.5 * nb) / Y,
               avg=sp / max(npay, 1), first=float(np.median(firsts)) if firsts else float("nan"),
               zero=float(np.mean([r["npay"] == 0 for r in rows])), bust=int(nb),
               valid=sum(r["valid"] for r in rows) / Y, bank=sum(r["bank"] for r in rows) / Y, ge=sum(r["ge"] for r in rows) / Y,
               cool=sum(r["cool"] for r in rows) / Y, brake=sum(r["brake_f"] + r["brake_d"] for r in rows) / Y,
               tr=sum(r["ntr"] for r in rows) / Y, wr=100.0 * sum(r["wins"] for r in rows) / max(sum(r["ntr"] for r in rows), 1),
               mxs=float(np.max([r["maxstreak"] for r in rows])),
               lim_v=sum(r["lim_valid"] for r in rows), lim_p=sum(r["lim_profit"] for r in rows), lim_t=sum(r["lim_ten"] for r in rows))
    mods = {}
    for r in rows:
        for k, (x, n, w) in r["mods"].items():
            a = mods.setdefault(k, [0.0, 0, 0])
            a[0] += x; a[1] += n; a[2] += w
    out["mods"] = {k: dict(pnl=a[0] / Y, tr=a[1] / Y, wr=100.0 * a[2] / max(a[1], 1)) for k, a in sorted(mods.items())}
    return out


def evaluate(Pv, GP, windows=WIN, step=7, workers=4, by_year=False, seeds=(0,)):
    m = mk()
    reset_seed_cache()
    _apply_seed(m, 0)
    jobs = []; tags = []
    for name, (lo, hi) in windows.items():
        for (a, b) in starts(m, lo, hi, step):
            for sd in seeds:
                jobs.append((Pv, GP, a, b, sd)); tags.append((name, a))
    order = sorted(range(len(jobs)), key=lambda i: jobs[i][4])      # nach Seed: jede Stoerungsmaske einmal je Prozess
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            o2 = list(ex.map(_one, [jobs[i] for i in order], chunksize=16))
    else:
        o2 = [_one(jobs[i]) for i in order]
    outs = [None] * len(jobs)
    for i, o in zip(order, o2):
        outs[i] = o
    res = {}
    for name in windows:
        rows = [o for (nm, a), o in zip(tags, outs) if nm == name]
        if rows:
            res[name] = agg(rows)
    if by_year:
        byy = {}
        for (nm, a), o in zip(tags, outs):
            y = str(np.datetime64(int(m.days[a]), "D"))[:4]
            byy.setdefault(y, []).append(o)
        res["jahre"] = {y: agg(v) for y, v in sorted(byy.items())}
    res["_rows"] = [(nm, int(m.days[a]), o["npay"], o["sumpay"], o["end_bal"], o["nbust"]) for (nm, a), o in zip(tags, outs)]
    return res


def line(lab, r):
    return (f"{lab:<22s} Ausz/J {r['pay']:5.2f}  $/J {r['net']:5.0f} (+offen {r['net_open']:5.0f})  Ø {r['avg']:4.0f}$  "
            f"1.Ausz {r['first']:5.0f} T  ohne {100*r['zero']:4.1f}%  Bust {r['bust']}  n={r['n']}")


def mods_line(r):
    return "  ".join(f"{k}:{v['pnl']:.0f}$/{v['tr']:.0f}tr/{v['wr']:.0f}%" for k, v in r["mods"].items())


def evaluate_seeds(Pv, GP, seeds=tuple(range(1, 17)), windows=WIN, step=7, workers=4):
    """Je Seed und Fenster (Ausz/J, $/J, Busts) - fuer gepaarte Vergleiche. Rueckgabe {fenster: array (nseed, 3)}."""
    m = mk()
    reset_seed_cache()
    _apply_seed(m, 0)
    jobs = []; tags = []
    for name, (lo, hi) in windows.items():
        for (a, b) in starts(m, lo, hi, step):
            for sd in seeds:
                jobs.append((Pv, GP, a, b, sd)); tags.append((name, sd))
    order = sorted(range(len(jobs)), key=lambda i: jobs[i][4])
    with ProcessPoolExecutor(workers) as ex:
        o2 = list(ex.map(_one, [jobs[i] for i in order], chunksize=64))
    outs = [None] * len(jobs)
    for i, o in zip(order, o2):
        outs[i] = o
    res = {}
    for name in windows:
        arr = []
        for sd in seeds:
            rows = [o for (nm, s2), o in zip(tags, outs) if nm == name and s2 == sd]
            a = agg(rows)
            arr.append((a["pay"], a["net"], a["bust"], a["net_open"]))
        res[name] = np.array(arr)
    return res


def paired(base, var, lab):
    out = []
    for w in base:
        d = var[w] - base[w]
        n = len(d)
        out.append(f"{w.split()[-1]} {var[w][:,0].mean():5.2f}({d[:,0].mean():+.2f}±{d[:,0].std(ddof=1)/np.sqrt(n):.2f}) "
                   f"{var[w][:,1].mean():5.0f}$({d[:,1].mean():+4.0f}±{d[:,1].std(ddof=1)/np.sqrt(n):3.0f}) B{int(var[w][:,2].sum())}")
    return f"{lab:<24s} " + " | ".join(out)
