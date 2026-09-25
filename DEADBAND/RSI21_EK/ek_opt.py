"""RSI21 Eigenkapital - Varianten rechnen (parallel) und Kennzahlen je Periode speichern.

Eine Variante = (Name, Signal-Parameter fuer ek_sig.select, Konto-Parameter fuer ek_sim.params). Jede Variante laeuft als
EIN durchgehendes Konto 2006-2026 (Groesse in % der Equity, daher sind die Renditen je Periode unabhaengig vom Kontostand);
die Kennzahlen werden je Periode aus der Tages-Equity gerechnet:
  T  = Auswahl   2006-03 .. 2016-12
  V  = Pruefung  2017-01 .. 2021-12
  Z  = heute     2022-01 .. 2026-08   (von frueheren RSI21-Entscheidungen gesehen, siehe Bericht)
  G  = gesamt
Aufruf als Modul: rows = evaluate(variants, workers=4)."""
import os, sys, json, time
import numpy as np
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ek_data, ek_sig, ek_sim, ek_eval as V                        # noqa: E402

PER = {"T": ("2006-01-01", "2017-01-01"), "V": ("2017-01-01", "2022-01-01"), "Z": ("2022-01-01", "2026-09-01"),
       "G": ("2006-01-01", "2026-09-01"), "VZ": ("2017-01-01", "2026-09-01"), "TV": ("2006-01-01", "2022-01-01")}
BASE_SIM = dict(risk=1.0, size_mode=1, swap_mode=1, lev_gold=20.0, lev_nas=20.0, margin_cap=0.9)
_W = {}


def _init(dname):
    D = ek_data.load(dname)
    _W["F"] = ek_sig.features(D)
    _W["mk"] = ek_sim.Market(D)
    _W["cache"] = {}


def signals(sel, feat=None, fkw=None):
    key = json.dumps(sel, sort_keys=True) + "|" + json.dumps(fkw or {}, sort_keys=True)
    c = _W["cache"]
    if key not in c:
        if len(c) > 64:
            c.clear()
        F = _W["F"] if feat is None else feat
        c[key] = _W["mk"].signals(ek_sig.select(F, **sel))
    return c[key]


def _feat(fkw):
    key = "F:" + json.dumps(fkw, sort_keys=True)
    if key not in _W:
        _W[key] = ek_sig.features(_W["mk"].D, **fkw)
    return _W[key]


def _job(v):
    name, sel, sim = v[0], v[1], dict(v[2])
    fkw = v[3] if len(v) > 3 else {}
    seed = int(sim.pop("_seed", 0)) if "_seed" in sim else 0
    skipf = float(sim.pop("_skip", 0.0)) if "_skip" in sim else 0.0
    feat = _feat(fkw) if fkw else None
    R = signals(sel, feat, fkw)
    Pv = ek_sim.params(**dict(BASE_SIM, **sim))
    skip = None
    if skipf > 0:
        skip = np.random.default_rng(seed).random(len(R["ev"])) < skipf
    res = ek_sim.run(_W["mk"], R, Pv, seed=seed, skip=skip)
    out = dict(name=name, sel=sel, sim=sim, fkw=fkw, st=res["st"].tolist())
    for p, (a, b) in PER.items():
        out[p] = V.metrics(res, a, b)
    out["years"] = {str(k): v for k, v in V.by_year(res).items()}
    return out


def evaluate(variants, workers=4, dname="D.pkl"):
    t0 = time.time()
    if workers <= 1:
        _init(dname)
        rows = [_job(v) for v in variants]
    else:
        with ProcessPoolExecutor(workers, initializer=_init, initargs=(dname,)) as ex:
            rows = list(ex.map(_job, variants, chunksize=max(1, len(variants) // (workers * 4))))
    print(f"  {len(variants)} Varianten in {time.time() - t0:.0f}s", flush=True)
    return rows


def line(r, per=("T", "V", "Z")):
    s = f"{r['name'][:44]:44s}"
    for p in per:
        m = r[p]
        s += f" | {p} {100 * m['cagr']:6.1f}% DD {100 * m['maxdd']:4.0f}% n{m['tr_y']:5.0f} R{m['avgR']:+.2f}"
    return s


def save(rows, fn):
    os.makedirs(os.path.join(HERE, "ergebnisse"), exist_ok=True)
    with open(os.path.join(HERE, "ergebnisse", fn), "w") as f:
        json.dump(rows, f, indent=1, default=float)
