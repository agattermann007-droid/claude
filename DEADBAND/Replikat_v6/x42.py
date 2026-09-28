"""Build 6.30 (Trefferquote): Konto-Screening mit eng7. Basis = 6.20 (Grid-Regel S, N1800 ohne Grid, Waechter wie im EA
ueber 600 Tage). Varianten: Teilgewinn (T1), Stop auf Einstand (BE) und Ziele fuer Fades, RSI21 und Noise.
Aufruf: python x42.py gft|ext ["Variante|..."|all] [Stoerungen] [Schritt]
Ergebnisse: ergebnisse/x42_{gft|ext}.json (Schluessel "Variante [Stoerungen sSchritt]")."""
import numpy as np, sys, json, os, time
import eng7 as E, evl6 as V, r6, x40, x41

V.E = E                                                     # Bewertung mit eng7 (Noise-Ausstiege, Fade-T1 relativ)
H = dict(harv=1)
ERT = dict(x40.ERT)
SIC = dict(x40.SIC)

VAR = {
    # Basis
    "6.20 Ertrag": (ERT, H),
    "6.20 Sicher": (SIC, {}),
    # Fades: Stop auf Einstand (+0,05 R) ab x R, Teilgewinn 50 % ab x R bzw. ab 70 % des Wegs zum Ziel
    "F BE 0.4": (ERT, dict(H, tp1r=0.4, be=0.05)),
    "F BE 0.5": (ERT, dict(H, tp1r=0.5, be=0.05)),
    "F BE 0.75": (ERT, dict(H, tp1r=0.75, be=0.05)),
    "F T1 0.5/50": (ERT, dict(H, tp1r=0.5, tp1f=0.5)),
    "F T1 0.5/50 BE": (ERT, dict(H, tp1r=0.5, tp1f=0.5, be=0.05)),
    "F T1 70%Z/50": (ERT, dict(H, tp1r=-0.7, tp1f=0.5)),
    "F T1 70%Z/50 BE": (ERT, dict(H, tp1r=-0.7, tp1f=0.5, be=0.05)),
    # RSI21 (R = Stop-Abstand 2 ATR, Ziel 2,2 / 2,64 R)
    "R BE 0.5": (dict(ERT, r21_tp1r=0.5, r21_be=0.05), H),
    "R BE 1.0": (dict(ERT, r21_tp1r=1.0, r21_be=0.05), H),
    "R T1 0.5/50 BE": (dict(ERT, r21_tp1r=0.5, r21_tp1f=0.5, r21_be=0.05), H),
    "R T1 1.0/50 BE": (dict(ERT, r21_tp1r=1.0, r21_tp1f=0.5, r21_be=0.05), H),
    "R T1 1.0/50": (dict(ERT, r21_tp1r=1.0, r21_tp1f=0.5, r21_be=-99.0), H),
    # Noise (R = Stop-Abstand des Teils: 0,35 / 0,5 / 0,75 Tages-Sigma x Zeitfaktor)
    "N BE 0.5": (dict(ERT, nz_tp1r=0.5, nz_be=0.05), H),
    "N BE 1.0": (dict(ERT, nz_tp1r=1.0, nz_be=0.05), H),
    "N T1 0.5/50 BE": (dict(ERT, nz_tp1r=0.5, nz_tp1f=0.5, nz_be=0.05), H),
    "N T1 1.0/50 BE": (dict(ERT, nz_tp1r=1.0, nz_tp1f=0.5, nz_be=0.05), H),
    "N T1 1.0/50": (dict(ERT, nz_tp1r=1.0, nz_tp1f=0.5), H),
    "N TP 1.0": (dict(ERT, nz_tp=1.0), H),
    "N TP 1.5": (dict(ERT, nz_tp=1.5), H),
    # Kombinationen (Ertrag)
    "K1 N BE1 R BE1": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), H),
    "K2 N BE1 R BE1 F T1": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), dict(H, tp1r=0.5, tp1f=0.5)),
    "K3 N TP1 R BE1 F T1": (dict(ERT, nz_tp=1.0, r21_tp1r=1.0, r21_be=0.05), dict(H, tp1r=0.5, tp1f=0.5)),
    "K4 N BE1 R T1BE F T1": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_tp1f=0.5, r21_be=0.05), dict(H, tp1r=0.5, tp1f=0.5)),
    "K5 N TP1 R T1BE F T1BE": (dict(ERT, nz_tp=1.0, r21_tp1r=1.0, r21_tp1f=0.5, r21_be=0.05), dict(H, tp1r=0.5, tp1f=0.5, be=0.05)),
    "K6 N BE.5 R T1.5BE F BE.4": (dict(ERT, nz_tp1r=0.5, nz_be=0.05, r21_tp1r=0.5, r21_tp1f=0.5, r21_be=0.05), dict(H, tp1r=0.4, be=0.05)),
    "K7 N BE1 R T1BE F BE.75": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_tp1f=0.5, r21_be=0.05), dict(H, tp1r=0.75, be=0.05)),
    # Runde 2: um K1/K2
    "K1b N BE.75 R BE1": (dict(ERT, nz_tp1r=0.75, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), H),
    "K1c N BE1 R BE.75": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=0.75, r21_be=0.05), H),
    "K1d N BE1 R BE1.5": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.5, r21_be=0.05), H),
    "K1e N BE1.5 R BE1": (dict(ERT, nz_tp1r=1.5, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), H),
    "K2b K1 F T1 0.5/33": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), dict(H, tp1r=0.5, tp1f=0.33)),
    "K2c K1 F T1 0.4/50": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), dict(H, tp1r=0.4, tp1f=0.5)),
    "K2d K1 F T1 0.6/50": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), dict(H, tp1r=0.6, tp1f=0.5)),
    "K2e K1 F T1 70%Z/50": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), dict(H, tp1r=-0.7, tp1f=0.5)),
    "K2f K1 F BE.75": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), dict(H, tp1r=0.75, be=0.05)),
    "K2g K1 F T1 50%Z/50": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), dict(H, tp1r=-0.5, tp1f=0.5)),
    "K8 N BE1 R T1.5BE F T1": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.5, r21_tp1f=0.5, r21_be=0.05), dict(H, tp1r=0.5, tp1f=0.5)),
    "K9 N TP1.5 R BE1 F T1": (dict(ERT, nz_tp=1.5, r21_tp1r=1.0, r21_be=0.05), dict(H, tp1r=0.5, tp1f=0.5)),
    # Runde 3: mehr Treffer, nur mit den Regeln, die der EA 6.30 hat (Einstand fuer Noise/RSI21, Fade-Teilgewinn)
    "T+ N BE.5 R BE.5 F T1 .4": (dict(ERT, nz_tp1r=0.5, nz_be=0.05, r21_tp1r=0.5, r21_be=0.05), dict(H, tp1r=0.4, tp1f=0.5)),
    "T+ N BE.5 R BE.5 F T1 .3/70": (dict(ERT, nz_tp1r=0.5, nz_be=0.05, r21_tp1r=0.5, r21_be=0.05), dict(H, tp1r=0.3, tp1f=0.7)),
    "T+ N BE.75 R BE.75 F T1 .4": (dict(ERT, nz_tp1r=0.75, nz_be=0.05, r21_tp1r=0.75, r21_be=0.05), dict(H, tp1r=0.4, tp1f=0.5)),
    "T+ N BE1 R BE1 F T1 .3/70": (dict(ERT, nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05), dict(H, tp1r=0.3, tp1f=0.7)),
    "S+ F T1 .4": (SIC, dict(tp1r=0.4, tp1f=0.5)),
    "S+ F T1 .3/70": (SIC, dict(tp1r=0.3, tp1f=0.7)),
    # Sicher (nur Fades)
    "S F T1 0.5/50": (SIC, dict(tp1r=0.5, tp1f=0.5)),
    "S F T1 0.5/50 BE": (SIC, dict(tp1r=0.5, tp1f=0.5, be=0.05)),
    "S F BE 0.4": (SIC, dict(tp1r=0.4, be=0.05)),
    "S F BE 0.75": (SIC, dict(tp1r=0.75, be=0.05)),
    "S F T1 70%Z/50": (SIC, dict(tp1r=-0.7, tp1f=0.5)),
}
_SET = {}


def setup(target):
    if target not in _SET:
        blks, info = x40.PB.blocks(target, x41.S70_OHNE, info=True)
        _SET[target] = (blks, info, x40.market(target))
    return _SET[target]


def evaluate(target, kw, gpx, seeds=8, step=2):
    blks, info, mk = setup(target)
    V._MK = mk
    GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **gpx) for _ in x40.F10])
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    if target == "ext":
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=step, seeds=tuple(range(seeds)), warm="2006-09-01", end="2021-12-31")
    else:
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=step, seeds=tuple(range(seeds)), skip=0.08)
    m = r["mean"]; m["fade_live"] = sum(x[2] for x in info)
    return m


def run(target, names, seeds, step, var=None):
    var = var or VAR
    fn = os.path.join("ergebnisse", f"x42_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl in names:
        kw, gpx = var[lbl]
        key = f"{lbl} [{seeds} s{step}]"
        if key in res:
            print(V.line(f"{target} {lbl}", res[key]), "(Cache)", flush=True)
            continue
        t = time.time()
        m = evaluate(target, kw, gpx, seeds, step)
        res[key] = m
        json.dump(res, open(fn, "w"), indent=1, default=float)
        print(V.line(f"{target} {lbl}", m), f"| gueltig/J {m['valid']:.1f} [{time.time() - t:.0f}s]", flush=True)
    return res


if __name__ == "__main__":
    target = sys.argv[1]
    which = sys.argv[2] if len(sys.argv) > 2 else "all"
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    step = int(sys.argv[4]) if len(sys.argv) > 4 else (2 if target == "gft" else 6)
    names = list(VAR) if which == "all" else which.split("|")
    run(target, names, seeds, step)
