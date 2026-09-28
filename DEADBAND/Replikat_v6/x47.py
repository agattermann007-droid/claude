"""Build 6.40: Waechter-Formen und Pufferkurven im Vergleich, mit Abstand zum Boden (Screening wie x44: 8 Stoerungen,
jeder 2. Handelstag bzw. jeder 6. auf den Fremddaten). Basis C40 = 6.40-Regeln (Mindestgewinn GFT-Minimum, Abschluss-Ernte,
Schutz gueltiger Tage, Fades ohne Teilgewinn, Noise 0,45 %). Pufferkurve "a/b/f": volle Groesse ab a % Puffer zum Boden,
Faktor f bei <= b % (EA: DDFullPct/DDMinPct/DDMinFactor). Waechter: "Modul PF30" = je Modul wie 6.30, "Port200" = PF der
letzten 200 Signale aller Fade-Module (EA FadeWaechterModus 1), "+" = UND, "ODER" = ODER; Sym/Mod/Port = je Symbol/Modul/alle.
Ergebnis (Bericht 6.40, Abschnitt 3.4): Q5 = 6.40 (Port200 > 1,15, Kurve 5/2,5/0,2); Entscheidung mit 16 Stoerungen
(ergebnisse/x47_gft_16.json, x47_gft_spread06_16.json), weil die Beinahe-Busts von einzelnen Stoerungen abhaengen.
Aufruf (im jeweiligen Replikat-Ordner, auch in der Kopie mit engeren Spreads, siehe x46.py):
python x47.py gft|ext "Name|..."|all [seeds] [step] [out.json]
Ergebnisse: ergebnisse/x47_gft.json, x47_ext.json, x47_gft_spread06.json (GFT-Ersatz mit Spreads x0,6), *_16.json"""
import sys, os, json
sys.path.insert(0, os.getcwd())
import x44
D415 = dict(ddfull=4.0, ddmin=1.5, ddfmin=0.3)
D42 = dict(ddfull=4.0, ddmin=2.0, ddfmin=0.3)
H = x44.H
C40 = x44.C40
V = {
    "G1 Modul PF30>1.2": (dict(C40, **D415), H, 0.75, "S70"),
    "G2 Port PF200>1.15": (dict(C40, **D415), H, 0.75, "P200/1.15"),
    "G3 Port200>1.15 + Sym50>1.0": (dict(C40, **D415), H, 0.75, "M:port200/1.15+sym50/1.0"),
    "G4 Port200>1.15 + Port50>1.0": (dict(C40, **D415), H, 0.75, "M:port200/1.15+port50/1.0"),
    "G5 Port200>1.15 + Mod30>1.0": (dict(C40, **D415), H, 0.75, "M:port200/1.15+mod30/1.0"),
    "G6 Port200>1.15 + Sym30>1.0": (dict(C40, **D415), H, 0.75, "M:port200/1.15+sym30/1.0"),
    "G7 Port200>1.15, Kurve 4/2/0.3": (dict(C40, **D42), H, 0.75, "P200/1.15"),
    "G8 Modul PF30>1.2, Kurve 4/2/0.3": (dict(C40, **D42), H, 0.75, "S70"),
    "G9 Port200>1.15 + Sym50>1.0, Kurve 4/2/0.3": (dict(C40, **D42), H, 0.75, "M:port200/1.15+sym50/1.0"),
    "G10 Modul PF30>1.1": (dict(C40, **D415), H, 0.75, "S70 W1.1"),
    "G11 Port200>1.15 + Sym50>1.1": (dict(C40, **D415), H, 0.75, "M:port200/1.15+sym50/1.1"),
    "H1 Mod30>1.2 ODER (Mod30>1.0 UND Port200>1.15)": (dict(C40, **D415), H, 0.75, "M:mod30/1.2|mod30/1.0+port200/1.15"),
    "H2 Mod30>1.2 ODER (Mod30>0.9 UND Port200>1.15)": (dict(C40, **D415), H, 0.75, "M:mod30/1.2|mod30/0.9+port200/1.15"),
    "H3 Mod30>1.2 ODER (Mod30>1.1 UND Port200>1.15)": (dict(C40, **D415), H, 0.75, "M:mod30/1.2|mod30/1.1+port200/1.15"),
    "H4 Mod30>1.2 ODER (Mod30>1.0 UND Port200>1.3)": (dict(C40, **D415), H, 0.75, "M:mod30/1.2|mod30/1.0+port200/1.3"),
    "H5 Mod30>1.2 ODER (Mod30>0.8 UND Port200>1.15)": (dict(C40, **D415), H, 0.75, "M:mod30/1.2|mod30/0.8+port200/1.15"),
    "P1 Port200>1.15, Kurve 5/2/0.3": (dict(C40, ddfull=5.0, ddmin=2.0, ddfmin=0.3), H, 0.75, "P200/1.15"),
    "P2 Port200>1.15, Kurve 5/1.5/0.3": (dict(C40, ddfull=5.0, ddmin=1.5, ddfmin=0.3), H, 0.75, "P200/1.15"),
    "P3 Port200>1.15, Kurve 4.5/2/0.3": (dict(C40, ddfull=4.5, ddmin=2.0, ddfmin=0.3), H, 0.75, "P200/1.15"),
    "P4 Port200>1.15+Port50>1.0, Kurve 5/2/0.3": (dict(C40, ddfull=5.0, ddmin=2.0, ddfmin=0.3), H, 0.75, "M:port200/1.15+port50/1.0"),
    "P5 Port200>1.1, Kurve 5/2/0.3": (dict(C40, ddfull=5.0, ddmin=2.0, ddfmin=0.3), H, 0.75, "P200/1.1"),
    "P6 Port200>1.15, Kurve 5.5/2/0.3": (dict(C40, ddfull=5.5, ddmin=2.0, ddfmin=0.3), H, 0.75, "P200/1.15"),
    "M1 Modul PF30>1.2, Kurve 5/2/0.3": (dict(C40, ddfull=5.0, ddmin=2.0, ddfmin=0.3), H, 0.75, "S70"),
    "R0 6.30 Ertrag": (x44.E630, x44.F630, 0.75, "S70"),
    # tiefere Stufe nahe am Boden (Episode Maerz 2025 mit GFT-nahen Spreads)
    "Q1 Port200>1.15, Kurve 5.5/2/0.15": (dict(C40, ddfull=5.5, ddmin=2.0, ddfmin=0.15), H, 0.75, "P200/1.15"),
    "Q2 Port200>1.15, Kurve 5.5/2.5/0.3": (dict(C40, ddfull=5.5, ddmin=2.5, ddfmin=0.3), H, 0.75, "P200/1.15"),
    "Q3 Port200>1.15, Kurve 5.5/3/0.3": (dict(C40, ddfull=5.5, ddmin=3.0, ddfmin=0.3), H, 0.75, "P200/1.15"),
    "Q4 Port200>1.15, Kurve 5.5/3/0.2": (dict(C40, ddfull=5.5, ddmin=3.0, ddfmin=0.2), H, 0.75, "P200/1.15"),
    "Q5 Port200>1.15, Kurve 5/2.5/0.2": (dict(C40, ddfull=5.0, ddmin=2.5, ddfmin=0.2), H, 0.75, "P200/1.15"),
    "N1 Port200>1.15, Kurve 5/2.5/0.15": (dict(C40, ddfull=5.0, ddmin=2.5, ddfmin=0.15), H, 0.75, "P200/1.15"),
    "N2 Port200>1.15, Kurve 5/3/0.2": (dict(C40, ddfull=5.0, ddmin=3.0, ddfmin=0.2), H, 0.75, "P200/1.15"),
    "N3 Port200>1.15, Kurve 4.5/2.5/0.2": (dict(C40, ddfull=4.5, ddmin=2.5, ddfmin=0.2), H, 0.75, "P200/1.15"),
    "N4 Port200>1.15, Kurve 5/2/0.2": (dict(C40, ddfull=5.0, ddmin=2.0, ddfmin=0.2), H, 0.75, "P200/1.15"),
    "N5 Port200>1.15, Kurve 5.5/2.5/0.2": (dict(C40, ddfull=5.5, ddmin=2.5, ddfmin=0.2), H, 0.75, "P200/1.15"),
    "N6 Port200>1.15, Kurve 5/2.5/0.25": (dict(C40, ddfull=5.0, ddmin=2.5, ddfmin=0.25), H, 0.75, "P200/1.15"),
}
target = sys.argv[1]; names = sys.argv[2].split("|") if len(sys.argv) > 2 and sys.argv[2] != "all" else list(V)
seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 8
step = int(sys.argv[4]) if len(sys.argv) > 4 else (2 if target == "gft" else 6)
out = sys.argv[5] if len(sys.argv) > 5 else None
res = json.load(open(out)) if out and os.path.exists(out) else {}
for nm in names:
    if nm in res:
        m = res[nm]
    else:
        kw, gpx, fr, rule = V[nm]
        m = x44.evaluate(target, kw, gpx, seeds, step, fade_risk=fr, rule=rule)
        m = {k: m[k] for k in ("pay", "bust", "p_bust1", "net", "s6", "wr", "minbuf_mean", "near100", "near200", "valid")}
        res[nm] = m
        if out:
            json.dump(res, open(out, "w"), indent=1)
    print(f"{target} {nm:<42s} Ausz {m['pay']:5.2f} ({365.25/m['pay']:5.1f} T) Bust {m['bust']:5.3f} P1 {m['p_bust1']:5.3f} Netto {m['net']:5.0f} S6 {m['s6']:4.2f} "
          f"| Boden min Ø {m['minbuf_mean']:4.0f}$ <100$ {100*m['near100']:4.1f}% <200$ {100*m['near200']:4.1f}%", flush=True)
