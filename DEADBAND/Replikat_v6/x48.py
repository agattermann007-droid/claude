"""Build 6.50 (Netto): Konto-Screening mit eng9/evl9. Basis = 6.40 Ertrag (x44.VAR["6.40 Ertrag"]). Ziel: mehr Netto je Jahr,
ohne weniger Auszahlungen je Jahr und ohne mehr Bust-Risiko (Busts, kleinster Abstand zum Boden, Fremddaten 2006-21).
Aufruf: python x48.py gft|ext ["Variante|..."|all] [Stoerungen] [Schritt] [Ausgabedatei]
Ergebnisse: ergebnisse/x48_{gft|ext}.json (Schluessel "Variante [Stoerungen sSchritt]")."""
import numpy as np, sys, json, os, time
import eng9 as E, evl6 as V, evl9 as V9, r6, x40, x44

H = dict(harv=1)
E640 = x44.E640                                                       # 6.40 Ertrag (Konto-Parameter)


def fade_gp(gpx, risk=0.75, per=None):
    """per: optional {Strom-Index: dict} mit abweichenden Parametern je Fade-Modul (Reihenfolge x40.F10)."""
    out = []
    for i, _ in enumerate(x40.F10):
        kw = dict(on=1, risk=risk, maxtrades=1, **gpx)
        if per and i in per:
            kw.update(per[i])
        out.append(kw)
    return E.gparams(out)


VAR = {
    "6.40 Ertrag": (E640, H, 0.75, "P200/1.15"),
    "6.40 VP0": (dict(E640, vp_on=0), H, 0.75, "P200/1.15"),
}
# Schutz gueltiger Tage nur fuer einzelne Module (Bits: 2 RSI21, 4 Noise, 8 Fades; DEADBAND ist aus)
for _m, _n in ((2, "R21"), (4, "NZ"), (8, "F"), (6, "R21+NZ"), (12, "NZ+F"), (10, "R21+F")):
    VAR[f"VPM {_n}"] = (dict(E640, vp_mods=_m), H, 0.75, "P200/1.15")
# andere Schutzformen: 6 = Einstieg nur mit Kopfraum >= k x Risiko, 7 = Groesse x k, 5 = enger Stop (mind. Anteil)
for _k in (1.0, 0.75, 0.5, 0.25):
    VAR[f"VP6 k{_k}"] = (dict(E640, vp_on=6, vp_k=_k), H, 0.75, "P200/1.15")
for _k in (0.5, 0.33):
    VAR[f"VP7 k{_k}"] = (dict(E640, vp_on=7, vp_k=_k), H, 0.75, "P200/1.15")
for _f in (0.0, 0.3, 0.5):
    VAR[f"VP5 f{_f}"] = (dict(E640, vp_on=5, vp_minfrac=_f), H, 0.75, "P200/1.15")

# Arbeitsbasis 6.50: Schutz gueltiger Tage nur fuer Noise und Fades (RSI21 handelt weiter; vp_mods 4 + 8)
B50 = dict(E640, vp_mods=12)
VAR["B50"] = (B50, H, 0.75, "P200/1.15")
F10N = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]


def _ex(names):
    return {F10N.index(n): dict(vpx=1) for n in names}


for _g in (["N1330"], ["N1300"], ["N1330", "N1300"], ["X1000S"], ["N1100"], ["X0630"], ["N1030"]):
    VAR["B50 frei " + "+".join(_g)] = (B50, H, 0.75, "P200/1.15", _ex(_g))
for _r in (0.45, 0.55, 0.60, 0.70):
    VAR[f"B50 R{_r}"] = (dict(B50, r21_risk=_r), H, 0.75, "P200/1.15")
for _n in (0.40, 0.50):
    VAR[f"B50 N{_n}"] = (dict(B50, nz_risk=_n), H, 0.75, "P200/1.15")
for _fr in (0.70, 0.80):
    VAR[f"B50 F{_fr}"] = (B50, H, _fr, "P200/1.15")
VAR["B50 cool4"] = (dict(B50, cool_n=4), H, 0.75, "P200/1.15")
VAR["B50 BS1.0"] = (dict(B50, belowstart=1.0), H, 0.75, "P200/1.15")
VAR["B50 R21maxloss3"] = (dict(B50, r21_maxloss=3), H, 0.75, "P200/1.15")
VAR["B50 ohne X1000S"] = (B50, H, 0.75, "P200/1.15", {9: dict(on=0)})
for _fr in (0.60, 0.65):
    VAR[f"B50 F{_fr}"] = (B50, H, _fr, "P200/1.15")
FREI2 = ["N1330", "N1300"]
for _fr in (0.65, 0.70):
    VAR[f"B50 F{_fr} frei N1330+N1300"] = (B50, H, _fr, "P200/1.15", _ex(FREI2))
VAR["B50 F0.7 frei N1330+N1300+N1100"] = (B50, H, 0.70, "P200/1.15", _ex(FREI2 + ["N1100"]))
VAR["B50 F0.7 frei N1330+N1300+N1100+X1000S"] = (B50, H, 0.70, "P200/1.15", _ex(FREI2 + ["N1100", "X1000S"]))
VAR["B50 F0.7 frei alle Fades"] = (dict(E640, vp_mods=4), H, 0.70, "P200/1.15")
VAR["B50 F0.7 frei N1330+N1300 R21maxloss3"] = (dict(B50, r21_maxloss=3), H, 0.70, "P200/1.15", _ex(FREI2))
VAR["B50 F0.7 frei N1330+N1300 N0.5"] = (dict(B50, nz_risk=0.5), H, 0.70, "P200/1.15", _ex(FREI2))
VAR["6.40 F0.7"] = (E640, H, 0.70, "P200/1.15")
# Kandidat C = Schutz ohne RSI21, Fade-Risiko 0,70 %, N1330/N1300 frei; darauf Hebel fuer die Auszahlungen
C50 = (B50, H, 0.70, "P200/1.15", _ex(FREI2))
VAR["C50"] = C50
for _bs in (0.9, 1.0):
    VAR[f"C50 BS{_bs}"] = (dict(B50, belowstart=_bs), H, 0.70, "P200/1.15", _ex(FREI2))
VAR["C50 R21maxloss3"] = (dict(B50, r21_maxloss=3), H, 0.70, "P200/1.15", _ex(FREI2))
VAR["C50 F0.65"] = (B50, H, 0.65, "P200/1.15", _ex(FREI2))
VAR["C50 N0.40"] = (dict(B50, nz_risk=0.40), H, 0.70, "P200/1.15", _ex(FREI2))
for _h in (10.5, 11.0, 11.5, 12.0, 13.0, 14.0):
    VAR[f"C50 R21 frei ab {_h}"] = (dict(B50, vp_r21_to=_h), H, 0.70, "P200/1.15", _ex(FREI2))

# 6.50 NETTO (Auswahl): Schutz gueltiger Tage fuer Noise und Fades (ohne N1330/N1300); RSI21 geschuetzt vor 13:00 NY und
# immer dann, wenn der Portfolio-Waechter die Fades nicht live handeln laesst (altes Regime); Fade-Risiko 0,70 %.
# Ohne den Regime-Schalter gleiche Zahlen auf dem GFT-Ersatz, aber auf den Fremddaten 2006-21 weniger Auszahlungen.
# RSI21 schon ab 11:00 NY frei (C50 R21 frei ab 11.0) bringt mehr, aber auf den Fremddaten mehr Busts (Episode 2010).
E650 = dict(B50, vp_r21_to=13.0, vp_r21_reg=1)
VAR["6.50 Ertrag"] = (E650, H, 0.70, "P200/1.15", _ex(FREI2))
VAR["6.50 Ertrag ohne Regime-Schalter"] = (dict(B50, vp_r21_to=13.0), H, 0.70, "P200/1.15", _ex(FREI2))
VAR["C50 R21 frei ab 11.0 + Regime"] = (dict(B50, vp_r21_to=11.0, vp_r21_reg=1), H, 0.70, "P200/1.15", _ex(FREI2))
VAR["C50 R21 frei + Regime"] = (dict(B50, vp_r21_reg=1), H, 0.70, "P200/1.15", _ex(FREI2))
S640B5 = x44.VAR["6.40 Sicher B5"]
VAR["6.40 Sicher"] = S640B5
VAR["6.50 Sicher, N1330/N1300 frei"] = (dict(S640B5[0], vp_mods=12), S640B5[1], 0.70, "P200/1.15", _ex(FREI2))
VAR["6.40 Sicher F0.7"] = (S640B5[0], S640B5[1], 0.70, "P200/1.15")
VAR["6.50 Sicher"] = VAR["6.40 Sicher F0.7"]                             # Sicher: nur Fade-Risiko 0,70 % (Serien wie 6.40)
VAR["6.40 Sicher frei N1330+N1300"] = (dict(S640B5[0], vp_mods=12), S640B5[1], 0.75, "P200/1.15", _ex(FREI2))
# Zerlegung (je ein Baustein auf 6.40)
VAR["6.40 + frei N1330+N1300"] = (dict(E640, vp_mods=14), H, 0.75, "P200/1.15", _ex(FREI2))
VAR["6.40 + R21 frei"] = (dict(E640, vp_mods=12), H, 0.75, "P200/1.15")
VAR["6.40 + R21 frei ab 11"] = (dict(E640, vp_mods=12, vp_r21_to=11.0), H, 0.75, "P200/1.15")
VAR["6.40 + R21 frei ab 13"] = (dict(E640, vp_mods=12, vp_r21_to=13.0), H, 0.75, "P200/1.15")
VAR["6.40 F0.7 + frei N1330+N1300"] = (dict(E640, vp_mods=14), H, 0.70, "P200/1.15", _ex(FREI2))
# RSI21 nach gueltigem Tag nur ohne Rueckgang: dd 1 = volle Groesse laut Pufferkurve, 2 = Equity >= Startsaldo, 3 = beides
for _h in (0.0, 11.0):
    for _dd in (1, 2, 3):
        VAR[f"C50 R21 frei ab {_h} dd{_dd}"] = (dict(B50, vp_r21_to=_h, vp_r21_dd=_dd), H, 0.70, "P200/1.15", _ex(FREI2))


SEED0 = int(os.environ.get("X48_SEED0", "0"))                         # Stoerungen SEED0 .. SEED0+seeds-1 (Rausch-Pruefung)
_REG = {}


def r21_regime(target, mk, N=200, th=1.15, window_days=600):
    """Je RSI21-Signal des Markts: 1 = Portfolio-Waechter der Fades beim Einstieg live (PF der letzten N virtuellen Ergebnisse,
    die vor dem Einstieg feststanden, > th; wie blocks_port / FadeWaechterOk im Portfolio-Modus), sonst 0."""
    key = (target, N, th, window_days)
    if key not in _REG:
        import pg_guard as PGd, pg_blocks as PB, x41
        rule = x41.S70_OHNE
        exempt = set(rule.get("exempt", ()))
        te_l, kt_l, mi_l, R_l = [], [], [], []
        for i, nm in enumerate(PB.F10):
            fk = {}
            for ds in ("ext", "gft"):
                f = PB.fi(ds, nm)
                keep, live, tp, w = PB.apply_rule(f, rule if nm not in exempt else dict(kind="none"))
                fk[ds] = (f, keep)
            (f1, k1), (f2, k2) = fk["ext"], fk["gft"]
            v1 = (f1["t_entry"] < PGd.LIM22) & k1
            kt1 = PGd.known_time("ext", f1); kt2 = PGd.known_time("gft", f2)
            te_l.append(np.r_[f1["t_entry"][v1], f2["t_entry"][k2]]); kt_l.append(np.r_[kt1[v1], kt2[k2]])
            R_l.append(np.r_[f1["R"][v1], f2["R"][k2]]); mi_l.append(np.full(len(te_l[-1]), i))
        kt_all = np.concatenate(kt_l); R_all = np.concatenate(R_l); mi_all = np.concatenate(mi_l)
        q = mk.ev_t[mk.r21["ev"]]
        _REG[key] = PGd.port_live_ea(q, kt_all, mi_all, R_all, N, th, window_days).astype(np.int64)
    return _REG[key]


def evaluate(target, kw, gpx, seeds=8, step=2, per_seed=False, by_year=False, fade_risk=0.75, rule="P200/1.15", per=None):
    blks, info, mk = x44.setup(target, rule)
    V._MK = mk
    mk.r21["reg"] = r21_regime(target, mk)                            # 6.50: Regime fuer RSI21 (nur mit vp_r21_reg wirksam)
    GP = fade_gp(gpx, fade_risk, per)
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    sd = tuple(range(SEED0, SEED0 + seeds))
    if target == "ext":
        m = V9.evaluate(Pv, GP, step=step, seeds=sd, skip=0.03, warm="2006-09-01", end="2021-12-31",
                        per_seed=per_seed, by_year=by_year)
    else:
        m = V9.evaluate(Pv, GP, step=step, seeds=sd, skip=0.08, per_seed=per_seed, by_year=by_year)
    m["fade_live"] = sum(x[2] for x in info)
    return m


def pvline(m):
    return " ".join(f"{k}:{v['pnl']:.0f}/{v['tr']:.1f}/{v['wr']:.0f}%" for k, v in sorted(m.get("pv", {}).items()))


def run(target, names, seeds, step, fn=None, var=None):
    var = var or VAR
    fn = fn or os.path.join("ergebnisse", f"x48_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl in names:
        v = var[lbl]
        kw, gpx = v[0], v[1]
        frisk = v[2] if len(v) > 2 else 0.75
        rule = v[3] if len(v) > 3 else "P200/1.15"
        per = v[4] if len(v) > 4 else None
        key = f"{lbl} [{seeds} s{step}]" + (f" ab{SEED0}" if SEED0 else "")
        if key in res:
            print(V9.line(f"{target} {lbl}"[:40], res[key]), "(Cache)", flush=True)
            continue
        t = time.time()
        m = evaluate(target, kw, gpx, seeds, step, fade_risk=frisk, rule=rule, per=per)
        res[key] = m
        json.dump(res, open(fn, "w"), indent=1, default=float)
        print(V9.line(f"{target} {lbl}"[:40], m), f"[{time.time() - t:.0f}s]", flush=True)
        print("     pv:", pvline(m), "| Module:", " ".join(f"{k}:{a['pnl']:.0f}/{a['tr']:.0f}" for k, a in sorted(m["mods"].items())), flush=True)
    return res


if __name__ == "__main__":
    target = sys.argv[1]
    which = sys.argv[2] if len(sys.argv) > 2 else "all"
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    step = int(sys.argv[4]) if len(sys.argv) > 4 else (2 if target == "gft" else 6)
    fn = sys.argv[5] if len(sys.argv) > 5 else None
    names = list(VAR) if which == "all" else which.split("|")
    run(target, names, seeds, step, fn)
