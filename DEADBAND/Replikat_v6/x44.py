"""Build 6.40 (Auszahlungstakt): Konto-Screening mit eng7. Basis = 6.30 Ertrag (Grid-Regel S, N1800 ohne Grid, Waechter wie
im EA ueber 600 Tage, Einstand Noise/RSI21 ab 1 R, Fade-Teilgewinn 50 % bei 0,6 R). Ziel: eine Auszahlung alle 30 Tage im
Mittel (>= 12,2 je Jahr) ohne mehr Busts als 6.30 (GFT-Ersatz und Fremddaten 2006-21).
Stellschrauben: Mindestgewinn (minpayout = Anteil des Traders), Abschluss-Ernte (bank_*), Tag nach gueltig sichern
(valid_stop), Handelspause nach Reife-Bedingungen (stop_after_valid), Risiko je Modul.
Aufruf: python x44.py gft|ext ["Variante|..."|all] [Stoerungen] [Schritt]
Ergebnisse: ergebnisse/x44_{gft|ext}.json (Schluessel "Variante [Stoerungen sSchritt]")."""
import numpy as np, sys, json, os, time
import eng8 as E, evl6 as V, evl8 as V8, r6, x40, x42

V.E = E
ERT, SIC, H = x42.ERT, x42.SIC, x42.H
NR = dict(nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05)          # 6.30: Noise und RSI21 Einstand ab 1 R
E630 = dict(ERT, **NR)
F630 = dict(H, tp1r=0.6, tp1f=0.5)                                    # 6.30: Fade-Teilgewinn 50 % bei 0,6 R
S630 = dict(tp1r=0.6, tp1f=0.5)


def mp(pct):
    """Mindestgewinn in % vom Startsaldo -> minpayout (Anteil des Traders, 80 %); nie unter der GFT-Mindestauszahlung."""
    return max(105.0, 10000.0 * pct / 100.0 * 0.8)


VAR = {
    # Basis
    "6.30 Ertrag": (E630, F630),
    "6.30 Sicher": (SIC, S630),
    # Mindestgewinn (6.30: 3 % = 300 $)
    "MP 2.5": (dict(E630, minpayout=mp(2.5)), F630),
    "MP 2.0": (dict(E630, minpayout=mp(2.0)), F630),
    "MP 1.5": (dict(E630, minpayout=mp(1.5)), F630),
    "MP min": (dict(E630, minpayout=105.0), F630),
    # Abschluss-Ernte immer (bank_last 5) bzw. ab 4 fehlenden Tagen
    "MP min B5": (dict(E630, minpayout=105.0, bank_last=5), F630),
    "MP min B4": (dict(E630, minpayout=105.0, bank_last=4), F630),
    "MP 3 B5": (dict(E630, bank_last=5), F630),
    # Schutz gueltiger Tage (vp 1: Risiko begrenzt, vp 2: keine Einstiege mehr), Ernte ganz / Rest auf Einstand
    "MP min B5 VP1": (dict(E630, minpayout=105.0, bank_last=5, vp_on=1), F630),
    "MP min B5 VP2": (dict(E630, minpayout=105.0, bank_last=5, vp_on=2), F630),
    "MP min B5 BE": (dict(E630, minpayout=105.0, bank_last=5, bank_be=1), F630),
    "MP min B5 FULL": (dict(E630, minpayout=105.0, bank_last=5, bank_full=1), F630),
    "MP min B5 VP1 BE": (dict(E630, minpayout=105.0, bank_last=5, vp_on=1, bank_be=1), F630),
    "MP min B5 VP2 BE": (dict(E630, minpayout=105.0, bank_last=5, vp_on=2, bank_be=1), F630),
    "MP min B5 m0.1": (dict(E630, minpayout=105.0, bank_last=5, bank_minr=0.1), F630),
    "MP min B5 m0.0": (dict(E630, minpayout=105.0, bank_last=5, bank_minr=0.0), F630),
    "MP min B5 m0.5": (dict(E630, minpayout=105.0, bank_last=5, bank_minr=0.5), F630),
    # ohne Fade-Teilgewinn (wie 6.20) bzw. ganz ohne 6.30-Ausstiege
    "MP min B5 noT1": (dict(E630, minpayout=105.0, bank_last=5), H),
    "MP min B5 noT1 noNR": (dict(ERT, minpayout=105.0, bank_last=5), H),
    "MP min B5 VP2 noT1": (dict(E630, minpayout=105.0, bank_last=5, vp_on=2), H),
    "MP min B5 VP1 noT1": (dict(E630, minpayout=105.0, bank_last=5, vp_on=1), H),
    "MP min B5 T1 0.8": (dict(E630, minpayout=105.0, bank_last=5), dict(H, tp1r=0.8, tp1f=0.5)),
    "MP min B5 T1 0.6/33": (dict(E630, minpayout=105.0, bank_last=5), dict(H, tp1r=0.6, tp1f=0.33)),
}
B40 = dict(E630, minpayout=105.0, bank_last=5, vp_on=2)                # Arbeitsbasis 6.40 (Fades ohne Teilgewinn: H)
VAR.update({
    "B40": (B40, H),
    "B40 paydelay1": (dict(B40, paydelay=1), H),
    "B40 F0.80": (B40, H, 0.80),
    "B40 F0.85": (B40, H, 0.85),
    "B40 F0.90": (B40, H, 0.90),
    "B40 cool0": (dict(B40, cool_n=0), H),
    "B40 cool4": (dict(B40, cool_n=4), H),
    "B40 R0.6": (dict(B40, r21_risk=0.6), H),
    "B40 N0.45": (dict(B40, nz_risk=0.45), H),
    "B40 R1st0.5": (dict(B40, r21_first_mult=0.5), H),
    "B40 R1st1": (dict(B40, r21_first_mult=1.0), H),
    "B40 GB1.0": (dict(B40, gesamtbudget=1.0, idea_cap=1.0), H),
    "B40 W1.1": (B40, H, 0.75, "S70 W1.1"),
    "B40 W1.0": (B40, H, 0.75, "S70 W1.0"),
    "B40 W1.3": (B40, H, 0.75, "S70 W1.3"),
    "B40 Woff": (B40, H, 0.75, "S70 Woff"),
})
for _N in (60, 100, 150, 200):
    for _th in (1.1, 1.2, 1.3):
        VAR[f"B40 P{_N}/{_th}"] = (B40, H, 0.75, f"P{_N}/{_th}")
        VAR[f"6.30 P{_N}/{_th}"] = (E630, F630, 0.75, f"P{_N}/{_th}")
C40 = dict(B40, vp_on=3, nz_risk=0.45)                                  # Kandidat 6.40 (mit Portfolio-Waechter)
# zusammengesetzte Waechter: langsamer Portfolio-Waechter (Regime) UND schnelle Bremse
for _g in ("M:port200/1.2+port30/1.0", "M:port200/1.2+port50/1.0", "M:port200/1.2+sym30/1.0", "M:port200/1.2+sym50/1.0",
           "M:port200/1.2+mod30/1.0", "M:port200/1.2+mod30/0.8", "M:port200/1.2+mod20/1.0", "M:port200/1.2+port30/1.1",
           "M:port200/1.2+sym30/1.1", "M:port200/1.2+sym50/1.1", "M:sym100/1.2", "M:sym200/1.2", "M:sym100/1.2+mod30/1.0"):
    VAR[f"C40 {_g}"] = (C40, H, 0.75, _g)
# staerkere Pufferkurve (Groesse nach Abstand zum Boden; EA: DDFullPct/DDMinPct/DDMinFactor)
DDV = {"DD4-2-0.3": dict(ddfull=4.0, ddmin=2.0, ddfmin=0.3), "DD5-2-0.3": dict(ddfull=5.0, ddmin=2.0, ddfmin=0.3),
       "DD4.5-2.5-0.25": dict(ddfull=4.5, ddmin=2.5, ddfmin=0.25), "DD5-1.5-0.4": dict(ddfull=5.0, ddmin=1.5, ddfmin=0.4),
       "DD4-1.5-0.3": dict(ddfull=4.0, ddmin=1.5, ddfmin=0.3), "DD4.5-2-0.4": dict(ddfull=4.5, ddmin=2.0, ddfmin=0.4)}
for _dn, _dd in DDV.items():
    VAR[f"C40 P200/1.2 {_dn}"] = (dict(C40, **_dd), H, 0.75, "P200/1.2")
    VAR[f"C40 S70 {_dn}"] = (dict(C40, **_dd), H, 0.75, "S70")
    VAR[f"6.30 {_dn}"] = (dict(E630, **_dd), F630, 0.75, "S70")
VAR["C40 S70"] = (C40, H, 0.75, "S70")
D42 = dict(ddfull=4.0, ddmin=2.0, ddfmin=0.3)
D415 = dict(ddfull=4.0, ddmin=1.5, ddfmin=0.3)
for _g in ("P200/1.2", "P200/1.15", "P200/1.1", "P150/1.2", "P250/1.2"):
    VAR[f"D40 {_g}"] = (dict(C40, **D42), H, 0.75, _g)
    VAR[f"D40 {_g} BS1.0"] = (dict(C40, belowstart=1.0, **D42), H, 0.75, _g)
    VAR[f"D40 {_g} N0.50"] = (dict(C40, nz_risk=0.50, **D42), H, 0.75, _g)
    VAR[f"D40 {_g} BS1.0 N0.50"] = (dict(C40, belowstart=1.0, nz_risk=0.50, **D42), H, 0.75, _g)
    VAR[f"D415 {_g} BS1.0"] = (dict(C40, belowstart=1.0, **D415), H, 0.75, _g)
    VAR[f"D415 {_g}"] = (dict(C40, **D415), H, 0.75, _g)
    VAR[f"D415 {_g} N0.50"] = (dict(C40, nz_risk=0.50, **D415), H, 0.75, _g)
    VAR[f"D40 {_g} N0.50 R0.55"] = (dict(C40, nz_risk=0.50, r21_risk=0.55, **D42), H, 0.75, _g)
    VAR[f"D40 {_g} N0.55"] = (dict(C40, nz_risk=0.55, **D42), H, 0.75, _g)
    VAR[f"D40 {_g} F0.80 N0.50"] = (dict(C40, nz_risk=0.50, **D42), H, 0.80, _g)
# 6.40 Endkandidat: Portfolio-Waechter PF200 > 1,15, Pufferkurve DDMinFactor 0,3 (sonst wie 6.30: 4 % / 1,5 %)
E640 = dict(C40, **D415)
VAR["6.40 Ertrag"] = (E640, H, 0.75, "P200/1.15")
VAR["6.40 paydelay1"] = (dict(E640, paydelay=1), H, 0.75, "P200/1.15")
VAR["6.40 paydelay3"] = (dict(E640, paydelay=3), H, 0.75, "P200/1.15")
VAR["6.40 Modul-Waechter"] = (E640, H, 0.75, "S70")
VAR["6.40 DDMinFactor 0.6"] = (C40, H, 0.75, "P200/1.15")
VAR["6.40 MinProfit 3 %"] = (dict(E640, minpayout=240.0), H, 0.75, "P200/1.15")
for _p in (2.5, 2.0, 1.5):
    VAR[f"6.40 MinProfit {_p} %"] = (dict(E640, minpayout=mp(_p)), H, 0.75, "P200/1.15")
S640 = dict(SIC, minpayout=105.0, vp_on=3, **D415)
VAR["6.40 Sicher"] = (S640, {}, 0.75, "P200/1.15")
VAR["6.40 Sicher B5"] = (dict(S640, bank_on=1, bank_last=5, bank_minr=0.3, bank_mods=15), dict(harv=1), 0.75, "P200/1.15")
# Nachbarschaft des Portfolio-Waechters
for _g in ("P175/1.2", "P250/1.2", "P200/1.15", "P200/1.25", "P300/1.2", "P200/1.1", "P200/1.3"):
    VAR[f"C40 {_g}"] = (C40, H, 0.75, _g)
# Auszahlungs-Wartezeit (nicht im EA einstellbar: Bearbeitung bei GFT)
VAR["C40 P200/1.2 paydelay1"] = (dict(C40, paydelay=1), H, 0.75, "P200/1.2")
VAR["C40 P200/1.2 paydelay3"] = (dict(C40, paydelay=3), H, 0.75, "P200/1.2")
# Sicher (nur Fades) mit den 6.40-Regeln
SICB = dict(SIC, minpayout=105.0, vp_on=3)
VAR["S40 P200/1.2"] = (SICB, {}, 0.75, "P200/1.2")
VAR["S40 P200/1.2 B5"] = (dict(SICB, bank_on=1, bank_last=5, bank_minr=0.3, bank_mods=15), dict(harv=1), 0.75, "P200/1.2")
VAR["S40 P200/1.2 T1"] = (SICB, dict(tp1r=0.6, tp1f=0.5), 0.75, "P200/1.2")
VAR["S40 P200/1.2 VP0"] = (dict(SICB, vp_on=0), {}, 0.75, "P200/1.2")
VAR["S40 S70 (Modul-Waechter)"] = (SICB, {}, 0.75, "S70")
for _g in ("P200/1.2", "P150/1.2"):
    VAR[f"C40 {_g}"] = (C40, H, 0.75, _g)
    VAR[f"C40 {_g} GE0.3"] = (dict(C40, ge_minr=0.3), H, 0.75, _g)
    VAR[f"C40 {_g} GE0"] = (dict(C40, ge_minr=0.0), H, 0.75, _g)
    VAR[f"C40 {_g} F0.80"] = (C40, H, 0.80, _g)
    VAR[f"C40 {_g} F0.70"] = (C40, H, 0.70, _g)
    VAR[f"C40 {_g} R0.45"] = (dict(C40, r21_risk=0.45), H, 0.75, _g)
    VAR[f"C40 {_g} R0.55"] = (dict(C40, r21_risk=0.55), H, 0.75, _g)
    VAR[f"C40 {_g} Bm0.1"] = (dict(C40, bank_minr=0.1), H, 0.75, _g)
    VAR[f"C40 {_g} Bmarg0"] = (dict(C40, bank_margin=0.0), H, 0.75, _g)
for _g in ("P200/1.2", "P150/1.2", "P100/1.1", "P100/1.2"):
    for _bs in (0.9, 1.0):
        VAR[f"B40 {_g} VP3 N0.45 BS{_bs}"] = (dict(B40, vp_on=3, nz_risk=0.45, belowstart=_bs), H, 0.75, _g)
        VAR[f"B40 {_g} VP3 BS{_bs}"] = (dict(B40, vp_on=3, belowstart=_bs), H, 0.75, _g)
    VAR[f"B40 {_g} VP3 N0.40"] = (dict(B40, vp_on=3, nz_risk=0.40), H, 0.75, _g)
    VAR[f"B40 {_g} VP3 N0.50"] = (dict(B40, vp_on=3, nz_risk=0.50), H, 0.75, _g)
    VAR[f"B40 {_g} VP3"] = (dict(B40, vp_on=3), H, 0.75, _g)
    VAR[f"B40 {_g} VP4"] = (dict(B40, vp_on=4), H, 0.75, _g)
    VAR[f"B40 {_g} VP3 N0.45"] = (dict(B40, vp_on=3, nz_risk=0.45), H, 0.75, _g)
    VAR[f"B40 {_g} SAV"] = (dict(B40, stop_after_valid=1), H, 0.75, _g)
    VAR[f"B40 {_g} F0.80"] = (B40, H, 0.80, _g)
    VAR[f"B40 {_g} N0.45"] = (dict(B40, nz_risk=0.45), H, 0.75, _g)
    VAR[f"B40 {_g} F0.80 N0.45"] = (dict(B40, nz_risk=0.45), H, 0.80, _g)
    VAR[f"B40 {_g} VP0"] = (dict(B40, vp_on=0), H, 0.75, _g)
    VAR[f"B40 {_g} VP1"] = (dict(B40, vp_on=1), H, 0.75, _g)
    VAR[f"B40 {_g} T1"] = (B40, F630, 0.75, _g)


import x41
RULES = {
    "S70": x41.S70_OHNE,                                               # 6.20/6.30: Grid-Regel S, N1800 ohne Grid, Waechter PF > 1,2 / 30
    "S70 W1.1": dict(x41.S70_OHNE, guard=("pf", 30, 1.1)),
    "S70 W1.0": dict(x41.S70_OHNE, guard=("pf", 30, 1.0)),
    "S70 W1.3": dict(x41.S70_OHNE, guard=("pf", 30, 1.3)),
    "S70 Woff": dict(x41.S70_OHNE, guard=("off", 0, 0.0)),
}
_SET = {}


def setup(target, rule="S70"):
    """rule: Schluessel aus RULES oder Portfolio-Waechter 'P<N>/<th>' (optional '&' bzw. '|' fuer UND/ODER mit Modul PF30 > 1,2,
    z. B. 'P100/1.2', 'P150/1.2&')."""
    if rule == "S70":
        return x42.setup(target)
    key = (target, rule)
    if key not in _SET:
        if rule.startswith("M:"):
            # zusammengesetzt, z. B. "M:port200/1.2+port30/1.0" oder "M:port200/1.2+sym30/1.0" oder "M:port200/1.2+mod30/1.0"
            import pg_guard as PGd, re as _re
            conds = []
            for part in rule[2:].split("+"):
                mm = _re.match(r"(port|sym|mod)(\d+)/([\d.]+)", part)
                conds.append((mm.group(1), int(mm.group(2)), float(mm.group(3))))
            blks, info = PGd.blocks_multi(target, x41.S70_OHNE, conds, info=True)
        elif rule.startswith("P"):
            import pg_guard as PGd
            comb = "and" if rule.endswith("&") else ("or" if rule.endswith("|") else None)
            N, th = rule[1:].rstrip("&|").split("/")
            blks, info = PGd.blocks_port(target, x41.S70_OHNE, int(N), float(th), combine=comb, info=True)
        else:
            blks, info = x40.PB.blocks(target, RULES[rule], info=True)
        _SET[key] = (blks, info, x42.setup(target)[2])
    return _SET[key]


def fade_gp(gpx, risk=0.75):
    return E.gparams([dict(on=1, risk=risk, maxtrades=1, **gpx) for _ in x40.F10])


def evaluate(target, kw, gpx, seeds=8, step=2, per_seed=False, by_year=False, fade_risk=0.75, rule="S70"):
    blks, info, mk = setup(target, rule)
    V._MK = mk
    GP = fade_gp(gpx, fade_risk)
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    if target == "ext":
        m = V8.evaluate(Pv, GP, step=step, seeds=tuple(range(seeds)), skip=0.03, warm="2006-09-01", end="2021-12-31",
                        per_seed=per_seed, by_year=by_year)
    else:
        m = V8.evaluate(Pv, GP, step=step, seeds=tuple(range(seeds)), skip=0.08, per_seed=per_seed, by_year=by_year)
    m["fade_live"] = sum(x[2] for x in info)
    return m


def line(target, lbl, m):
    return V8.line(f"{target} {lbl}"[:40], m)


def run(target, names, seeds, step, var=None):
    var = var or VAR
    fn = os.path.join("ergebnisse", f"x44_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl in names:
        v = var[lbl]
        kw, gpx = v[0], v[1]
        frisk = v[2] if len(v) > 2 else 0.75
        rule = v[3] if len(v) > 3 else "S70"
        key = f"{lbl} [{seeds} s{step}]"
        if key in res:
            print(line(target, lbl, res[key]), "(Cache)", flush=True)
            continue
        t = time.time()
        m = evaluate(target, kw, gpx, seeds, step, fade_risk=frisk, rule=rule)
        res[key] = m
        json.dump(res, open(fn, "w"), indent=1, default=float)
        print(line(target, lbl, m), f"[{time.time() - t:.0f}s]", flush=True)
    return res


if __name__ == "__main__":
    target = sys.argv[1]
    which = sys.argv[2] if len(sys.argv) > 2 else "all"
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    step = int(sys.argv[4]) if len(sys.argv) > 4 else (2 if target == "gft" else 6)
    names = list(VAR) if which == "all" else which.split("|")
    run(target, names, seeds, step)
