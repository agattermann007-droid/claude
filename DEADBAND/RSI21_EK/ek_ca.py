"""RSI21 Eigenkapital - Koordinatensuche auf Rendite ueber Signal-, Ausstiegs- und Platz-Parameter.

"Nur auf Rendite" heisst hier: Rendite bei GLEICHER Schwankung. Rendite laesst sich ueber den Hebel beliebig erhoehen (bis zum
Ruin); verglichen wird deshalb jede Variante bei der Groesse, bei der ihre Tagesrenditen in der Auswahlperiode VOL_ZIEL
Jahresvolatilitaet haben (Hebel 1:20, Margin-Deckel 90 % wirken mit). Das entspricht der erreichbaren Rendite bei frei
gewaehltem Hebel (Kelly: g* = Sharpe^2/2), ist aber statistisch stabiler als der Kelly-Punkt selbst. Je Kandidat:
  - Lauf mit 1 % Risiko je Trade -> Volatilitaet v der Auswahlperiode -> Risiko r* = 1 % x VOL_ZIEL / v -> Lauf mit r*,
  - Mittel ueber SEEDS Stoerungen (Seed 0 ungestoert; sonst 3 % der Signale ausgelassen, Schlupf bis 0,3 Spreads),
  - Zielwert = mittlere CAGR der Auswahlperiode bei r*; alle Perioden werden mit demselben r* gerechnet (Walk-Forward).
Auswahlperiode ZIEL: T = 2006-16, G = 2006-26, TV = 2006-21 (eine Periode, CAGR bei r*), oder regime-robust
  R:TV / R:TVZ = Mittel von log(1 + CAGR) ueber die Perioden (je Regime gleiches Gewicht; r* aus der Volatilitaet von
  2006-21 bzw. 2006-26) mit Sperre: kein Schritt, der eine dieser Perioden um mehr als GUARD Prozentpunkte CAGR
  verschlechtert. Walk-Forward: R:TV waehlt ohne 2022-26 aus, Z bleibt Pruefung.
Je Runde wird jeder Parameter ueber sein Raster variiert (andere fest); uebernommen wird der beste Wert, wenn er den
Zielwert um mehr als EPS Prozentpunkte verbessert. Ende, wenn eine Runde nichts verbessert.
Aufruf: python ek_ca.py ZIEL [SEEDS] -> ergebnisse/ek_ca_<ZIEL>.json"""
import os, sys, json, copy, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ek_opt as O                                                  # noqa: E402

VOL_ZIEL = 0.25
RISKS = [1.0]
SPACE = [
    ("be_at", "sim", [0.0, 1.0, 1.5, 2.0, 2.5, 3.0]),
    ("be_plus", "sim", [0.05, 0.25, 0.5]),
    ("rr_nas", "sim", [0.0, 1.5, 2.2, 3.0, 4.0, 5.0, 6.0]),
    ("rr_gold", "sim", [0.0, 1.8, 2.64, 3.5, 5.0, 6.0]),
    ("exitbars", "sim", [288, 576, 1152, 2304, 4608]),
    ("exitdays", "sim", [0.0, 8.0]),
    ("nslots", "sim", [1, 2, 3, 4, 5]),
    ("maxloss", "sim", [0, 1, 2, 3]),
    ("first_mult", "sim", [0.0, 0.5, 1.0]),
    ("trail", "pair", [(0.0, 0.0), (1.5, 1.0), (2.0, 1.0), (3.0, 1.5), (4.0, 2.0)]),
    ("we_close", "sim", [0.0, 16.75]),
    ("goldmult", "sim", [0.5, 0.7, 1.0, 1.3]),
    ("wts", "wts", [(1.25, 1.0, 0.75), (1.0, 1.0, 1.0), (1.5, 1.0, 0.5), (1.0, 1.25, 1.5)]),
    ("oben", "sel", [70.0, 72.5, 75.0, 77.5, 80.0]),
    ("cross", "cross", [None, 50.0, 55.0, 60.0, 65.0]),
    ("folge_min", "sel", [0, 60, 120, 240, 480]),
    ("ab", "sel", [0.0, 3.0, 8.0, 9.5, 10.0]),
    ("nas_bis", "sel", [11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 24.0]),
    ("gold_bis", "sel", [13.0, 15.0, 17.0, 24.0]),
    ("tf_gold", "sel", [(0,), (1,), (0, 1), (0, 1, 2)]),
    ("tf_nas", "sel", [(0,), (1,), (0, 1), (0, 1, 2), (1, 2)]),
    ("use_div", "sel", [True, False]),
    ("short_regime", "sel", [True, False]),
    ("nas_long_regime", "sel", [True, False]),
    ("gold_gate", "sel", [True, False]),
    ("stop_atr", "sel", [1.5, 1.75, 2.0, 2.5, 3.0]),
]
BASE_SEL = dict(gold_ohne_h1=False, tf_gold=(0, 1), tf_nas=(0, 1, 2), cross=55.0, cross_on=True)
BASE_SIMX = dict()
EPS = 0.3
GUARD = 3.0


def cur_value(sel, sim, name, kind):
    if kind == "sim":
        return sim.get(name, None)
    if kind == "pair":
        return (sim.get("trail_from", 0.0), sim.get("trail_dist", 0.0))
    if kind == "wts":
        return (sim.get("w0", 1.25), sim.get("w1", 1.0), sim.get("w2", 0.75))
    if kind == "cross":
        return sel.get("cross", 55.0) if sel.get("cross_on", True) else None
    return sel.get(name, None)


def apply(sel, sim, name, kind, v):
    sel = copy.deepcopy(sel); sim = copy.deepcopy(sim)
    if kind == "sim":
        sim[name] = v
    elif kind == "pair":
        sim["trail_from"], sim["trail_dist"] = v
    elif kind == "wts":
        sim["w0"], sim["w1"], sim["w2"] = v
    elif kind == "cross":
        if v is None:
            sel["cross_on"] = False
        else:
            sel["cross_on"] = True; sel["cross"] = v
    else:
        sel[name] = v
    return sel, sim


def seeds_of(sim, n):
    out = []
    for s in range(n):
        x = dict(sim)
        if s > 0:
            x["_seed"] = s; x["_skip"] = 0.03; x["slip"] = 0.3
        out.append(x)
    return out


def norm_per(ziel):
    if ziel.startswith("R:"):
        return "TV" if ziel == "R:TV" else "G"
    return ziel


def run_many(cands, nseeds, ziel):
    """cands: Liste (Name, sel, sim) -> je Kandidat (Zeilen bei r*, r* je Seed). Zwei Stufen: 1 % -> Volatilitaet -> r*."""
    V = []
    for nm, sel, sim in cands:
        for x in seeds_of(dict(sim, risk=1.0), nseeds):
            V.append((nm, sel, x))
    rows1 = O.evaluate(V, workers=4)
    V2 = []; rk = []
    for i, (nm, sel, sim) in enumerate(cands):
        for j, x in enumerate(seeds_of(sim, nseeds)):
            v = rows1[i * nseeds + j][norm_per(ziel)]["vol"]
            r = 1.0 * VOL_ZIEL / v if v > 1e-6 else 1.0
            r = float(min(max(r, 0.1), 20.0))
            rk.append(r)
            V2.append((nm, sel, dict(x, risk=r)))
    rows2 = O.evaluate(V2, workers=4)
    return [(rows2[i * nseeds:(i + 1) * nseeds], float(np.mean(rk[i * nseeds:(i + 1) * nseeds]))) for i in range(len(cands))]


def mean_m(rows, p, k="cagr"):
    return float(np.mean([r[p][k] for r in rows]))


def objective(rows, ziel):
    if ziel.startswith("R:"):
        return float(np.mean([100.0 * np.log(1.0 + mean_m(rows, p)) for p in ziel[2:]]))
    return 100.0 * mean_m(rows, ziel)


def guard_ok(rows, cur_rows, ziel):
    if not ziel.startswith("R:"):
        return True
    return all(100.0 * mean_m(rows, p) >= 100.0 * mean_m(cur_rows, p) - GUARD for p in ziel[2:])


def summary(rows):
    return {p: {k: mean_m(rows, p, k) for k in ("cagr", "maxdd", "tr_y", "avgR", "pf", "wr", "vol", "sharpe")} for p in ("T", "V", "Z", "G")}


def fmt(sm, rk):
    return f"r* {rk:4.2f} % | " + " | ".join(
        f"{p} {100 * sm[p]['cagr']:6.1f}% SR{sm[p]['sharpe']:4.2f} DD{100 * sm[p]['maxdd']:3.0f}% n{sm[p]['tr_y']:4.0f} R{sm[p]['avgR']:+.2f}"
        for p in ("T", "V", "Z", "G"))


if __name__ == "__main__":
    ziel = sys.argv[1] if len(sys.argv) > 1 else "G"
    nseeds = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    t0 = time.time()
    sel, sim = dict(BASE_SEL), dict(BASE_SIMX)
    rows0, rk0 = run_many([("Basis 6.60", sel, sim)], nseeds, ziel)[0]
    cur_obj = objective(rows0, ziel)
    cur_rows = rows0
    hist = [dict(step="Basis 6.60", obj=cur_obj, risk=rk0, sel=dict(sel), sim=dict(sim), sm=summary(rows0))]
    print(f"Basis: Ziel {ziel} = {cur_obj:.2f} | {fmt(summary(rows0), rk0)}", flush=True)
    for rnd in range(1, 8):
        improved = False
        for name, kind, values in SPACE:
            cv = cur_value(sel, sim, name, kind)
            cands = []
            for v in values:
                if v == cv or (isinstance(v, tuple) and cv is not None and tuple(cv) == v):
                    continue
                s2, m2 = apply(sel, sim, name, kind, v)
                cands.append((f"{name}={v}", s2, m2))
            if not cands:
                continue
            res = run_many(cands, nseeds, ziel)
            objs = [objective(r, ziel) if guard_ok(r, cur_rows, ziel) else -1e9 for r, _ in res]
            j = int(np.argmax(objs))
            if objs[j] > cur_obj + EPS:
                sel, sim = cands[j][1], cands[j][2]
                cur_obj = objs[j]
                cur_rows = res[j][0]
                improved = True
                sm = summary(res[j][0])
                hist.append(dict(step=f"R{rnd} {cands[j][0]}", obj=cur_obj, risk=res[j][1], sel=dict(sel), sim=dict(sim), sm=sm))
                print(f"R{rnd} {cands[j][0]:24s} -> {cur_obj:7.2f} | {fmt(sm, res[j][1])}  [{time.time() - t0:.0f}s]", flush=True)
        if not improved:
            break
    os.makedirs(os.path.join(HERE, "ergebnisse"), exist_ok=True)
    with open(os.path.join(HERE, "ergebnisse", f"ek_ca_{ziel.replace(':', '')}.json"), "w") as f:
        json.dump(dict(ziel=ziel, seeds=nseeds, vol_ziel=VOL_ZIEL, hist=hist, sel=sel, sim=sim), f, indent=1, default=str)
    print("Endstand sel:", sel)
    print("Endstand sim:", sim)
    print(f"fertig [{time.time() - t0:.0f}s]")
