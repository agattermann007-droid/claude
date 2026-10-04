"""Stufe 8: Portfolio-Suche - alte Stroeme (10 Fades mit Portfolio-Waechter, Spike 8:30) + neue robuste Stroeme
(Larry-Williams-Ausbruch NAS, RSI(2) NAS, Eroeffnungs-Momentum NAS, ...) und RSI21/Noise (intern), je mit
GFT-Handhabung. Bewertung im Konto-Replikat (eng6): ganzer Zeitraum 2022-03..2025-12 (250/500 Tage) sowie getrennt
Auswahl-Zeitraum (Starts 2022-03..2023, Ende 2023-12) und Pruef-Zeitraum (Starts ab 2024, Ende 2025-12), je 250 Tage.
Aufruf: python n8_port.py <satz>   (Saetze unten in SETS)"""
import sys, json, os, numpy as np
import eng6 as E, evl6 as V, y7_konto as Y, n8_konto as NK, n8sig as N

FADES = None


def fades():
    global FADES
    if FADES is None:
        FADES = Y.fade_blocks("gft")
    return FADES


# neue Stroeme: Name -> (Symbol, Generator, Argumente)
LIB = {
    "LW":    ("NAS", N.gen_lw, (570, 960, 570, 900, 960, 0.4, 0, 0.0, 0.0, 0)),
    "LWt3":  ("NAS", N.gen_lw, (570, 960, 570, 900, 960, 0.4, 0, 0.0, 3.0, 0)),
    "LWl":   ("NAS", N.gen_lw, (570, 960, 570, 900, 960, 0.4, 0, 0.0, 0.0, 1)),
    "LW6":   ("NAS", N.gen_lw, (570, 960, 570, 900, 960, 0.6, 0, 0.0, 0.0, 0)),
    "RSI2":  ("NAS", N.gen_daily, (1, 955, 570, 20.0, 200, 3, 0.6, 0.0, 0)),
    "MOM":   ("NAS", N.gen_mom, (570, 600, 900, 0.1, 0, 0.25, 0.0, 0)),
    "MOMk":  ("NAS", N.gen_mom, (570, 600, 720, 0.25, 0, 0.25, 0.0, 0)),
    "ORBM":  ("NAS", N.gen_orbmid, (120, 480, 570, 585, 735, 960, 2, 0.25, 0.0, 99.0)),
    "XASIA": ("XAU", N.gen_hold, (-360, 180, 1, 0.6, 1.0, 288, 0b111110)),
}


def build(old, new, risks, spike=True):
    """old: Fades an/aus; new: Liste Namen aus LIB; risks: dict Name -> Risiko %."""
    blks = []; gps = []
    if old:
        for b in fades():
            blks.append(b); gps.append(dict(on=1, risk=risks.get("fade", 0.75), maxtrades=1, harv=1))
    if spike:
        s_ = len(blks)
        blks.append(Y.spike_block("gft", s_, dict(Y.SPIKE, kmin=0.20), only_dir=1))
        gps.append(dict(on=1, risk=risks.get("spike", 0.75), maxtrades=1, harv=1))
    for nm in new:
        s_ = len(blks)
        sym, gen, args = LIB[nm]
        blks.append(NK.block(sym, gen, args, s_))
        rv = risks.get(nm, 0.75)
        gps.append(dict(dict(on=1, risk=0.75, maxtrades=1, harv=1), **rv) if isinstance(rv, dict) else dict(on=1, risk=rv, maxtrades=1, harv=1))
    for i, b in enumerate(blks):
        b["str"] = i
    return blks, gps


def evalset(blks, gps, kw, split=True):
    GP = E.gparams(gps)
    V.set_generic(blks, GP)
    Pv = E.params(**dict(Y.BASE, **kw))
    out = {"all": V.evaluate(Pv, GP=GP, horizons=(250, 500), step=3, seeds=tuple(range(8)), skip=0.05, end="2025-12-31")["mean"]}
    if split:
        out["IS"] = V.evaluate(Pv, GP=GP, horizons=(250,), step=2, seeds=tuple(range(8)), skip=0.05, warm="2022-03-21", end="2023-12-31")["mean"]
        out["OOS"] = V.evaluate(Pv, GP=GP, horizons=(250,), step=2, seeds=tuple(range(8)), skip=0.05, warm="2024-01-02", end="2025-12-31")["mean"]
    return out


def short(m):
    return f"{m['pay']:5.2f}/{m['net']:5.0f}/{m['bust']:.3f}"


def btype(m):
    return f"Boden {m.get('b_floor', 0):.3f} Float {m.get('b_float', 0):.3f} Tag {m.get('b_day', 0):.3f}"


DD3 = dict(ddfull=3.0, ddmin=1.0, ddfmin=0.3)
DD4 = dict(ddfull=4.0, ddmin=1.5, ddfmin=0.3)
OFFN = dict(nz_on=0)
OFFR = dict(r21_on=0)

SETS = {
    "a": [
        ("7.10", True, [], {}, {}),
        ("7.10 DD3", True, [], {}, DD3),
        ("7.10 DD4", True, [], {}, DD4),
        ("7.10+LW DD4", True, ["LW"], {}, DD4),
        ("7.10+LW DD3", True, ["LW"], {}, DD3),
        ("7.10+LW 0.5 DD3", True, ["LW"], {"LW": 0.5}, DD3),
        ("7.10+LW+RSI2 DD3", True, ["LW", "RSI2"], {}, DD3),
        ("7.10-Noise+LW DD3", True, ["LW"], {}, dict(DD3, **OFFN)),
        ("7.10+LWt3 DD3", True, ["LWt3"], {}, DD3),
        ("7.10+LWl DD3", True, ["LWl"], {}, DD3),
        ("7.10+LW6 DD3", True, ["LW6"], {}, DD3),
        ("7.10+MOM DD3", True, ["MOM"], {}, DD3),
        ("7.10+RSI2 DD3", True, ["RSI2"], {}, DD3),
        ("7.10+XASIA DD3", True, ["XASIA"], {}, DD3),
        ("7.10+ORBM DD3", True, ["ORBM"], {}, DD3),
    ],
    "b": [
        ("7.10+LW 0.5 DD4", True, ["LW"], {"LW": 0.5}, DD4),
        ("7.10+LW 0.4 DD3", True, ["LW"], {"LW": 0.4}, DD3),
        ("7.10+LW 0.5 mb3 DD3", True, ["LW"], {"LW": dict(risk=0.5, minbuf=3.0)}, DD3),
        ("7.10+LW 0.5 mb4 DD3", True, ["LW"], {"LW": dict(risk=0.5, minbuf=4.0)}, DD3),
        ("7.10+LW 0.75 mb4 DD3", True, ["LW"], {"LW": dict(minbuf=4.0)}, DD3),
        ("7.10+LW 0.75 mb5 DD3", True, ["LW"], {"LW": dict(minbuf=5.0)}, DD3),
        ("7.10+LW 0.5 mb4 DD3 fmin0.1", True, ["LW"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.1)),
        ("7.10+LW 0.5 mb4 DD3 fg1.5", True, ["LW"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD3, floorguard=1.5, floorguard_mult=0.0)),
        ("7.10+LW 0.5 mb4 DD3 mxl2", True, ["LW"], {"LW": dict(risk=0.5, minbuf=4.0, maxloss=1)}, DD3),
    ],
    "d": [
        ("7.10 DD3 fmin0.1", True, [], {}, dict(DD3, ddfmin=0.1)),
        ("7.10 DD3 fmin0.2", True, [], {}, dict(DD3, ddfmin=0.2)),
        ("7.10+LW 0.5 mb4 DD3 fmin0.2", True, ["LW"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.2)),
        ("7.10+LW 0.5 DD4 fmin0.1", True, ["LW"], {"LW": 0.5}, dict(DD4, ddfmin=0.1)),
        ("7.10+LW 0.5 mb3 DD4 fmin0.1", True, ["LW"], {"LW": dict(risk=0.5, minbuf=3.0)}, dict(DD4, ddfmin=0.1)),
        ("7.10+LWt3 0.5 mb4 DD3 fmin0.1", True, ["LWt3"], {"LWt3": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.1)),
        ("7.10+LW 0.6 mb4 DD3 fmin0.1", True, ["LW"], {"LW": dict(risk=0.6, minbuf=4.0)}, dict(DD3, ddfmin=0.1)),
        ("7.10+LW 0.5 mb4+XASIA DD3 fmin0.1", True, ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.1)),
        ("7.10+LW 0.5 mb4+RSI2+XASIA DD3 fmin0.1", True, ["LW", "RSI2", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.1)),
        ("7.10+LW 0.5 mb4 DD3/1.5 fmin0.1", True, ["LW"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(ddfull=3.0, ddmin=1.5, ddfmin=0.1)),
    ],
    "e": [
        ("7.10+LW 0.5 mb4+XASIA DD3 fmin0.2", True, ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.2)),
        ("7.10+LWt3 0.5 mb4+XASIA DD3 fmin0.1", True, ["LWt3", "XASIA"], {"LWt3": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.1)),
        ("7.10+LW 0.5 mb4+XASIA 0.5 DD3 fmin0.1", True, ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.0), "XASIA": 0.5}, dict(DD3, ddfmin=0.1)),
        ("7.10+LW 0.5 mb4+XASIA DD3 fmin0.15", True, ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.15)),
        ("7.10+LW 0.5 mb3.5+XASIA DD3 fmin0.1", True, ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=3.5)}, dict(DD3, ddfmin=0.1)),
        ("7.10+LW 0.5 mb4.5+XASIA DD3 fmin0.1", True, ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.5)}, dict(DD3, ddfmin=0.1)),
    ],
    "f": [
        ("7.10+LW 0.5 mb4+XASIA DD4 fmin0.1", True, ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD4, ddfmin=0.1)),
        ("7.10+LW 0.5 mb4+XASIA DD3.5/1.25 fmin0.1", True, ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(ddfull=3.5, ddmin=1.25, ddfmin=0.1)),
    ],
    "c": [   # nur neue Stroeme (ohne Fades, Spike, RSI21, Noise), GFT-Handhabung sicher
        ("NEU LW+MOM+RSI2+XASIA DD5", False, ["LW", "MOM", "RSI2", "XASIA"], {}, dict(r21_on=0, nz_on=0)),
        ("NEU LW+RSI2+XASIA DD5", False, ["LW", "RSI2", "XASIA"], {}, dict(r21_on=0, nz_on=0)),
        ("NEU LWt3+RSI2+XASIA DD5", False, ["LWt3", "RSI2", "XASIA"], {}, dict(r21_on=0, nz_on=0)),
        ("NEU LW 0.5+RSI2+XASIA DD5", False, ["LW", "RSI2", "XASIA"], {"LW": 0.5}, dict(r21_on=0, nz_on=0)),
        ("NEU LW mb4+RSI2+XASIA DD4", False, ["LW", "RSI2", "XASIA"], {"LW": dict(minbuf=4.0)}, dict(DD4, r21_on=0, nz_on=0)),
    ],
}

if __name__ == "__main__":
    name = sys.argv[1]
    fn = f"ergebnisse/n8_port_{name}.json"
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl, old, new, risks, kw in SETS[name]:
        if lbl in res:
            continue
        blks, gps = build(old, new, risks, spike=old)
        r = evalset(blks, gps, kw)
        res[lbl] = r
        json.dump(res, open(fn, "w"), default=float, indent=1)
        print(NK.line(lbl, r["all"]) + f" | IS {short(r['IS'])} | OOS {short(r['OOS'])} | {btype(r['all'])}", flush=True)
