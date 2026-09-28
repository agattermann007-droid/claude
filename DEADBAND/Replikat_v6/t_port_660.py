"""Abgleich EA <-> Replikat fuer Build 6.60 (Zukunft):
1. Voreinstellungen des EA = Replikat-Variante "6.60b" (x60.VAR): Fade-Risiko 0,75 %, Schutz gueltiger Tage wie 6.50
   (vp_r21_to, vp_r21_reg, vp_mods, freie Fades), Portfolio-Waechter P200/1,15, Modul-Reihenfolge.
2.-4. unveraendert aus t_port_650 (Quelltext-Stellen des Schutzes, Entscheidung je Modul auf dem Zustandsraster,
   Fade-Regime fuer RSI21 gegen x48.r21_regime). Die Handelslogik von 6.60 ist die von 6.50.
5. Regime-Meldungen (RegimeWaechter): nur Meldungen - im Funktionsrumpf keine Handelsaufrufe, Zuweisungen nur an die
   eigenen reg*-Variablen und lokale Namen, Terminal-Globalvariablen nur die eigenen (REGLIVE, REGWARN, sonst nirgends
   gelesen); Aufruf genau einmal nach InaktivWaechter(); Rueckstellung beim Anlegen der Fades;
   Voreinstellung FadeFruehwarnPF = Vorgabe von a60_warn.py (rueckwirkende Auswertung im Bericht, Abschnitt 7).
Aufruf: python t_port_660.py   (Protokoll: ergebnisse/t_port_660.txt)"""
import re, os
import x60, x48
import t_port_650 as T5

LOG = T5.LOG
say = T5.say
MQ, inp = T5.MQ, T5.inp


def check_defaults():
    kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x60.VAR["6.60b"])
    names = T5.fade_names()
    frei_ea = [n.strip().upper() for n in inp("GueltigSchutzFrei").split(";") if n.strip()]
    frei_rep = [x48.F10N[i].upper() for i, d in (per or {}).items() if d.get("vpx", 0) > 0.5]
    ok = True
    ok &= abs(float(inp("FadeRiskPct")) - frisk) < 1e-12 and abs(frisk - 0.75) < 1e-12
    ok &= abs(float(inp("GueltigSchutzR21BisNY")) - kw["vp_r21_to"]) < 1e-12
    ok &= (inp("GueltigSchutzR21Regime") == "true") == (kw.get("vp_r21_reg", 0) == 1)
    ok &= inp("GueltigSchutz") == "true" and kw["vp_on"] == 3
    ok &= kw["vp_mods"] == 12
    ok &= sorted(frei_ea) == sorted(frei_rep)
    ok &= names == x48.F10N
    ok &= rule == "P200/1.15" and abs(float(inp("FadePortPF")) - 1.15) < 1e-12 and int(inp("FadePortN")) == 200
    ok &= extra is None and not extra_gp and not kw.get("sv_on", 0) and not kw.get("nz_short", 0) and not kw.get("db_on", 0)
    say(f"  EA: FadeRiskPct {inp('FadeRiskPct')}, GueltigSchutzR21BisNY {inp('GueltigSchutzR21BisNY')}, GueltigSchutzR21Regime "
        f"{inp('GueltigSchutzR21Regime')}, GueltigSchutzFrei {frei_ea} | Replikat 6.60b: Fade-Risiko {frisk}, vp_r21_to "
        f"{kw['vp_r21_to']}, vp_r21_reg {kw.get('vp_r21_reg', 0)}, vp_mods {kw['vp_mods']}, frei {frei_rep} -> "
        f"{'GLEICH' if ok else 'ABWEICHUNG'}")
    return ok


def body(name):
    i = MQ.index(f"void {name}()")
    j = MQ.index("{", i)
    d = 0
    for k in range(j, len(MQ)):
        d += (MQ[k] == "{") - (MQ[k] == "}")
        if d == 0:
            return MQ[j:k + 1]
    raise ValueError(name)


def check_regime_msgs():
    ok = True
    b_txt = re.sub(r"//[^\n]*", "", body("RegimeWaechter"))                     # ohne Kommentare
    b = re.sub(r'"[^"\n]*"', '""', b_txt)                                           # ... und ohne Texte
    verboten = ["OrderSend", "trade.", "Trade.", "PositionClose", "PositionOpen", "OrderDelete", "OrderModify", "Buy(", "Sell(",
                "Close(", "Schliess", "Oeffne", "FadeLive", "Einstieg"]
    treffer = [v for v in verboten if v in b]
    ok &= not treffer
    erlaubt = {"regPruefZeit", "regMeldLive", "regWarnZeit", "now", "n", "alle", "pf", "live", "warnBereich", "warnVorher"}
    ziele = set(re.findall(r"\b([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*(?<![=!<>])=(?!=)", b))
    fremd = sorted(ziele - erlaubt)
    ok &= not fremd
    aufrufe = set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", b)) - {"if", "return", "StringFormat"}
    ok &= aufrufe <= {"TimeCurrent", "FadePortfolioPF", "Meldung", "KontoGv", "GlobalVariableCheck", "GlobalVariableGet",
                      "GlobalVariableSet"}
    gv = set(re.findall(r'KontoGv\("(\w+)"\)', b_txt))
    ok &= gv == {"REGLIVE", "REGWARN"} and all(MQ.count(f'KontoGv("{g}")') == b_txt.count(f'KontoGv("{g}")') for g in gv)
    n_call = MQ.count("RegimeWaechter();")
    ok &= n_call == 1 and re.search(r"InaktivWaechter\(\);[^\n]*\n\s*RegimeWaechter\(\);", MQ) is not None
    ok &= MQ.count("regMeldLive = -1; regWarnZeit = 0; regPruefZeit = 0;") == 1
    src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "a60_warn.py"), encoding="utf-8").read()
    warn_default = float(re.search(r'WARN = float\(sys.argv\[1\]\) if len\(sys.argv\) > 1 else ([0-9.]+)', src).group(1))
    ok &= abs(float(inp("FadeFruehwarnPF")) - warn_default) < 1e-12 and float(inp("FadeFruehwarnPF")) > float(inp("FadePortPF"))
    say(f"  RegimeWaechter: Handelsaufrufe {treffer or 'keine'}, Zuweisungen ausserhalb reg*/lokal {fremd or 'keine'}, "
        f"Aufrufe {sorted(aufrufe)}, eigene Terminal-Globalvariablen {sorted(gv)} (sonst nirgends benutzt), Aufrufstellen {n_call}, "
        f"FadeFruehwarnPF {inp('FadeFruehwarnPF')} (a60_warn {warn_default}) -> "
        f"{'OK' if ok else 'ABWEICHUNG'}")
    return ok


if __name__ == "__main__":
    say("1. Voreinstellungen EA = Replikat-Variante 6.60b")
    ok1 = check_defaults()
    say("2. Quelltext-Stellen des Schutzes je Modul (wie 6.50)")
    ok2 = T5.check_source()
    say("3. Schutz gueltiger Tage je Modul (wie 6.50)")
    ok3 = T5.check_decisions()
    say("4. Fade-Regime fuer RSI21 (FadeRegimeLive gegen x48.r21_regime)")
    ok4 = T5.check_regime()
    say("5. Regime-Meldungen (RegimeWaechter): nur Meldungen, kein Einfluss auf den Handel")
    ok5 = check_regime_msgs()
    say("GESAMT " + ("IDENTISCH" if (ok1 and ok2 and ok3 and ok4 and ok5) else "ABWEICHUNG"))
    os.makedirs("ergebnisse", exist_ok=True)
    open(os.path.join("ergebnisse", "t_port_660.txt"), "w").write("\n".join(LOG) + "\n")
