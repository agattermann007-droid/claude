"""Build 6.60 (Suche nach Takt und Netto, zukunftsfest): Konto-Screening mit eng10/evl10. Basis = 6.50 Ertrag (x48.VAR).
Prueft jede Variante nach einem vorab festgelegten Protokoll (PROTOKOLL_660.md; Bericht 6.60, Abschnitt 2):
beide Spread-Lagen, Startjahre einzeln (vor allem 2024-25), Stoerungen paarweise gegen die Basis, Fremddaten 2006-21.

Aufruf: python x60.py gft|ext ["Variante|..."|all] [Stoerungen] [Schritt] [Ausgabedatei]
Ergebnisse: ergebnisse/x60_{gft|ext}.json (Schluessel "Variante [Stoerungen sSchritt]"), Ordner per X60_OUT."""
import numpy as np, sys, json, os, time
import x48, x44, x40, r6
import eng10 as E, evl6 as V, evl10 as V10                    # evl10 zuletzt: evl6 rechnet mit eng10

H = dict(harv=1)
F10N = x48.F10N
E640 = x44.E640
E650 = x48.E650
FREI2 = x48.FREI2


def _ex(names):
    return {F10N.index(n): dict(vpx=1) for n in names}


def fade_gp(gpx, risk=0.70, per=None, extra=()):
    """GP fuer eng10: 10 Fade-Module (Reihenfolge x40.F10), danach optionale Zusatz-Stroeme (extra: Liste von dicts)."""
    out = []
    for i, _ in enumerate(x40.F10):
        kw = dict(on=1, risk=risk, maxtrades=1, **gpx)
        if per and i in per:
            kw.update(per[i])
        out.append(kw)
    for kw in extra:
        out.append(dict(kw))
    return E.gparams(out)


# Varianten: (Konto-Parameter, Fade-GP-Zusatz, Fade-Risiko, Waechter-Regel, je-Modul-Parameter, Zusatz-Bloecke-Schluessel)
VAR = {
    "6.40 Ertrag": (E640, H, 0.75, "P200/1.15", None, None),
    "6.50 Ertrag": (E650, H, 0.70, "P200/1.15", _ex(FREI2), None),
}
# K1: Groesse fuer den gueltigen Tag (nur wenn mit dem Deckel erreichbar; Deckel = Gesamtbudget 0,9 % bzw. 0,8 / 0,85)
for _c in (0.80, 0.85, 0.90):
    VAR[f"6.50 SV{_c}"] = (dict(E650, sv_on=1, sv_cap=_c), H, 0.70, "P200/1.15", _ex(FREI2), None)
VAR["6.50 SV0.85 immer"] = (dict(E650, sv_on=2, sv_cap=0.85), H, 0.70, "P200/1.15", _ex(FREI2), None)

# Pufferkurve (Diagnose: wie viel kostet die Verkleinerung im Rueckgang?)
for _k, _dd in {"DD5-2.5-0.4": (5.0, 2.5, 0.4), "DD4-1.5-0.6 (6.30)": (4.0, 1.5, 0.6), "DD aus": (0.0, 0.0, 1.0),
                "DD5-3-0.3": (5.0, 3.0, 0.3), "DD6-2.5-0.2": (6.0, 2.5, 0.2)}.items():
    VAR[f"6.50 {_k}"] = (dict(E650, ddfull=_dd[0], ddmin=_dd[1], ddfmin=_dd[2]), H, 0.70, "P200/1.15", _ex(FREI2), None)

# K6: Noise auch short (Originalstrategie zweiseitig; Ausgleich zur Long-Lastigkeit auf NAS100)
for _r in (0.30, 0.45, 0.60):
    VAR[f"6.50 NS{_r}"] = (dict(E650, nz_short=1, nz_s_risk=_r), H, 0.70, "P200/1.15", _ex(FREI2), None)

# K7: Risiko nach Zielweite - N1330/N1300 (Ziel 0,3-0,5 R) machen einen Tag nie allein gueltig; ihr Verlust kippt aber einen Tag
def _exr(names, risk):
    d = _ex(FREI2)
    for n in names:
        d.setdefault(F10N.index(n), {}).update(risk=risk)
    return d
for _r in (0.35, 0.50):
    VAR[f"6.50 N13xx R{_r}"] = (E650, H, 0.70, "P200/1.15", _exr(["N1330", "N1300"], _r), None)
VAR["6.50 ohne N1330/N1300"] = (E650, H, 0.70, "P200/1.15", {**_ex(FREI2), F10N.index("N1330"): dict(on=0), F10N.index("N1300"): dict(on=0)}, None)

# K9: DEADBAND-Ausbruch wieder an (Gegenstueck zu den Fades in Trendphasen), mit den 6.40/6.50-Schutzregeln
VAR["6.50 + DEADBAND"] = (dict(E650, db_on=1), H, 0.70, "P200/1.15", _ex(FREI2), None)
VAR["6.50 + DEADBAND x0.5"] = (dict(E650, db_on=1, db_mult=0.45), H, 0.70, "P200/1.15", _ex(FREI2), None)

# Regel-Lesart: Boden trailt nur das Tagesschluss-Hoch (GFT-Artikel Instant Premium: "6% Trailing End-of-Day Maximum Drawdown")
VAR["6.50 Boden EOD"] = (dict(E650, floor_eod=1), H, 0.70, "P200/1.15", _ex(FREI2), None)

# Zerlegung 6.50 (je ein Baustein auf 6.40) fuer den Zukunftstest
VAR["6.40 + F0.70"] = (E640, H, 0.70, "P200/1.15", None, None)
VAR["6.40 + R21 ab 13 Regime"] = (dict(E640, vp_mods=12, vp_r21_to=13.0, vp_r21_reg=1), H, 0.75, "P200/1.15", None, None)
VAR["6.40 + N1330/N1300 frei"] = (dict(E640, vp_mods=14), H, 0.75, "P200/1.15", _ex(FREI2), None)
VAR["6.40 + F0.70 + R21 ab 13 Regime"] = (dict(E640, vp_mods=12, vp_r21_to=13.0, vp_r21_reg=1), H, 0.70, "P200/1.15", None, None)

# Kandidaten 6.60 (nach Walk-Forward): Fade-Risiko zurueck auf 0,75 % (6.40), N1330/N1300 an gueltigen Tagen frei (6.50),
# wahlweise RSI21 ab 13:00 NY frei, solange das Fade-Regime live ist (6.50)
VAR["6.60a"] = VAR["6.40 + N1330/N1300 frei"]
E660 = dict(E650)                                                     # = 6.50-Kontoregeln (Schutz je Modul, RSI21 ab 13 + Regime)
VAR["6.60b"] = (E660, H, 0.75, "P200/1.15", _ex(FREI2), None)

# K1 neu: Basis 0,75 % (6.60b) + Groesse fuer den gueltigen Tag bis 0,80 / 0,85 % (nur wenn damit erreichbar)
for _c in (0.80, 0.85):
    VAR[f"6.60b SV{_c}"] = (dict(E660, sv_on=1, sv_cap=_c), H, 0.75, "P200/1.15", _ex(FREI2), None)

# 6.70: Konsistenzregel (Instant GOAT: bester Tag < 15 % des Gewinns der Auszahlungsperiode, geprueft beim Antrag)
#   K15 = passiv: Auszahlung erst, wenn die Regel mit 0,5 Prozentpunkten Reserve erfuellt ist (Handel unveraendert)
#   Deckel = aktiv: sind die gueltigen Tage erreicht, heute keine neuen Einstiege, sobald der Tag den besten Tag erreicht
#   T14 = 14-Tage-Zyklus (Instant GOAT: Auszahlung alle 14 Tage)
VAR["6.60"] = VAR["6.60b"]
VAR["6.60 T14"] = (dict(E660, cycledays=14), H, 0.75, "P200/1.15", _ex(FREI2), None)
VAR["6.60 K15"] = (dict(E660, cons_pct=15.0), H, 0.75, "P200/1.15", _ex(FREI2), None)
VAR["6.60 K15 R0"] = (dict(E660, cons_pct=15.0, cons_res=0.0), H, 0.75, "P200/1.15", _ex(FREI2), None)
VAR["6.60 K15 T14"] = (dict(E660, cons_pct=15.0, cycledays=14), H, 0.75, "P200/1.15", _ex(FREI2), None)
VAR["6.60 K15 Deckel"] = (dict(E660, cons_pct=15.0, cons_cap=1, cons_capfrac=1.0), H, 0.75, "P200/1.15", _ex(FREI2), None)
VAR["6.60 K15 Deckel 0.8"] = (dict(E660, cons_pct=15.0, cons_cap=1, cons_capfrac=0.8), H, 0.75, "P200/1.15", _ex(FREI2), None)
VAR["6.60 K15 Deckel T14"] = (dict(E660, cons_pct=15.0, cons_cap=1, cons_capfrac=1.0, cycledays=14), H, 0.75, "P200/1.15", _ex(FREI2), None)
#   Tagesdeckel = nach einem gueltigen Tag (x Faktor) heute keine neuen Einstiege, die ganze Periode (Schutz gueltiger Tage fuer alle)
for _f in (1.0, 1.5, 2.0):
    VAR[f"6.60 K15 Tagesdeckel {_f}"] = (dict(E660, cons_pct=15.0, cons_cap=2, cons_capfrac=_f), H, 0.75, "P200/1.15", _ex(FREI2), None)

# Sicher (nur Fades): 6.40 Sicher (Fade-Risiko 0,75 %) gegen 6.50 Sicher (0,70 %)
VAR["6.40 Sicher"] = tuple(x48.VAR["6.40 Sicher"]) + (None, None)
VAR["6.50 Sicher"] = tuple(x48.VAR["6.50 Sicher"]) + (None, None)

SEED0 = int(os.environ.get("X60_SEED0", "0"))
_SET = {}


def _nz_lb(target, mk):
    """6.60: untere Noise-Bandgrenze LB in den Markt uebernehmen (sig5.nz_days liefert sie seit 6.60; gleiche Reihenfolge)."""
    if "LB" in mk.nz:
        return
    import pickle, prep5 as P
    S = pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl" if target == "ext" else "sig5.pkl"), "rb"))
    z = S["nz"]
    assert len(z["UB"]) == len(mk.nz["UB"]) and np.array_equal(z["UB"], mk.nz["UB"]), "Noise-Reihenfolge weicht ab"
    mk.nz["LB"] = np.ascontiguousarray(z["LB"])


def setup(target, rule, extra_key=None):
    blks, info, mk = x44.setup(target, rule)
    _nz_lb(target, mk)
    blks = list(blks)
    if extra_key is not None:
        import a60_blocks as AB
        blks = blks + AB.extra_blocks(target, extra_key, start_stream=len(blks))
    return blks, info, mk


def evaluate(target, kw, gpx, seeds=8, step=2, per_seed=False, by_year=False, fade_risk=0.70, rule="P200/1.15", per=None,
             extra_key=None, extra_gp=(), skip_gft=0.08, drop=None):
    """drop: optional Funktion (blks) -> blks fuer Stresstests (z. B. Kanten-Abschlag)."""
    blks, info, mk = setup(target, rule, extra_key)
    if drop is not None:
        blks = drop(target, blks)
    V._MK = mk
    mk.r21["reg"] = x48.r21_regime(target, mk)
    GP = fade_gp(gpx, fade_risk, per, extra_gp)
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    sd = tuple(range(SEED0, SEED0 + seeds))
    if target == "ext":
        m = V10.evaluate(Pv, GP, step=step, seeds=sd, skip=0.03, warm="2006-09-01", end="2021-12-31",
                         per_seed=per_seed, by_year=by_year)
    else:
        m = V10.evaluate(Pv, GP, step=step, seeds=sd, skip=skip_gft, per_seed=per_seed, by_year=by_year)
    m["fade_live"] = sum(x[2] for x in info)
    return m


def unpack(v):
    kw, gpx = v[0], v[1]
    frisk = v[2] if len(v) > 2 else 0.70
    rule = v[3] if len(v) > 3 else "P200/1.15"
    per = v[4] if len(v) > 4 else None
    extra = v[5] if len(v) > 5 else None
    extra_gp = v[6] if len(v) > 6 else ()
    return kw, gpx, frisk, rule, per, extra, extra_gp


def run(target, names, seeds, step, fn=None, var=None, per_seed=False, by_year=False):
    var = var or VAR
    fn = fn or os.path.join(os.environ.get("X60_OUT", "ergebnisse"), f"x60_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl in names:
        kw, gpx, frisk, rule, per, extra, extra_gp = unpack(var[lbl])
        key = f"{lbl} [{seeds} s{step}]" + (f" ab{SEED0}" if SEED0 else "")
        if key in res:
            print(V10.line(f"{target} {lbl}"[:40], res[key]), "(Cache)", flush=True)
            continue
        t = time.time()
        m = evaluate(target, kw, gpx, seeds, step, per_seed=per_seed, by_year=by_year, fade_risk=frisk, rule=rule, per=per,
                     extra_key=extra, extra_gp=extra_gp)
        res[key] = m
        json.dump(res, open(fn, "w"), indent=1, default=float)
        print(V10.line(f"{target} {lbl}"[:40], m), f"sv {m.get('x_sv_up', 0):.1f} [{time.time() - t:.0f}s]", flush=True)
        if by_year and "jahre" in m:
            print("     " + " | ".join(f"{y}: {a['pay']:.2f} ({365.25 / max(a['pay'], 1e-9):.1f} T) {a['net']:.0f}$"
                                       for y, a in m["jahre"].items()), flush=True)
    return res


if __name__ == "__main__":
    target = sys.argv[1]
    which = sys.argv[2] if len(sys.argv) > 2 else "all"
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    step = int(sys.argv[4]) if len(sys.argv) > 4 else (2 if target == "gft" else 6)
    fn = sys.argv[5] if len(sys.argv) > 5 else None
    names = list(VAR) if which == "all" else which.split("|")
    run(target, names, seeds, step, fn, per_seed=True, by_year=True)
