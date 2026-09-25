"""Endbewertung Build 6.40 (Auszahlungstakt) mit eng8 - wie x43/x45: 16 Stoerungen, 1/2/3 Jahre, jeder Handelstag
(GFT-Ersatz) bzw. jeder dritte Tag (Fremddaten 2006-21) ein neues Konto, Startjahre, Streuung je Stoerung, zusaetzlich
Abstand zum Boden (kleinster Abstand je Konto; Anteil der Konten, die dem Boden auf < 100 $ / < 200 $ nahekamen).
6.40 Ertrag: Mindestgewinn = GFT-Minimum (131,25 $), Abschluss-Ernte immer, Schutz gueltiger Tage (vp_on 3), Fades ohne
Teilgewinn, Noise 0,45 %, Portfolio-Waechter PF der letzten 200 Fade-Signale > 1,15, Pufferkurve DDMinFactor 0,3.
Aufruf: python x46.py gft|ext ["Variante|..."]   (Ausgabe ergebnisse/x46_{gft|ext}.json)"""
import numpy as np, sys, json, os, time
import eng8 as E, evl6 as V, evl8 as V8, x44

CFG = {
    "6.30 Ertrag": "6.30 Ertrag",
    "6.40 Ertrag": "6.40 Ertrag",
    "6.40, Waechter PF200 > 1,1, Noise 0,50 %, Kurve 4/2/0,3": "D40 P200/1.1 N0.50",
    "6.40, Waechter PF200 > 1,2, Kurve 4/2/0,3": "D40 P200/1.2",
    "6.40 mit DDMinFactor 0,6 (wie 6.30)": "6.40 DDMinFactor 0.6",
    "6.40 mit Modul-Waechter (wie 6.30)": "6.40 Modul-Waechter",
    "6.40 mit Mindestgewinn 3 %": "6.40 MinProfit 3 %",
    "6.40, Auszahlung 1 Tag schneller gebucht": "6.40 paydelay1",
    "6.40, Auszahlung 1 Tag spaeter gebucht": "6.40 paydelay3",
    "6.30 Sicher": "6.30 Sicher",
    "6.40 Sicher": "6.40 Sicher",
    "6.40 Sicher mit Abschluss-Ernte": "6.40 Sicher B5",
}

if __name__ == "__main__":
    target = sys.argv[1]
    which = sys.argv[2].split("|") if len(sys.argv) > 2 else list(CFG)
    step = 1 if target == "gft" else 3
    fn = os.path.join(os.environ.get("X46_OUT", "ergebnisse"), f"x46_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl in which:
        if lbl in res:
            print(V8.line(f"{target} {lbl}"[:40], res[lbl]), "(Cache)", flush=True)
            continue
        v = x44.VAR[CFG[lbl]]
        kw, gpx = v[0], v[1]
        frisk = v[2] if len(v) > 2 else 0.75
        rule = v[3] if len(v) > 3 else "S70"
        t = time.time()
        m = x44.evaluate(target, kw, gpx, seeds=16, step=step, per_seed=True, by_year=True, fade_risk=frisk, rule=rule)
        m["variante"] = CFG[lbl]
        print(V8.line(f"{target} {lbl}"[:40], m), f"[{time.time() - t:.0f}s]", flush=True)
        s = m["streuung"]
        print(f"     Streuung (16 Stoerungen): Ausz {s['mean'][0]:.2f} (SD {s['sd'][0]:.2f}) | Busts {s['mean'][1]:.3f} (SD {s['sd'][1]:.3f}) "
              f"| Netto {s['mean'][2]:.0f} (SD {s['sd'][2]:.0f}) | WR {s['mean'][6]:.1f} (SD {s['sd'][6]:.2f})", flush=True)
        for y, a in m["jahre"].items():
            print(f"     Start {y}: Ausz {a['pay']:5.2f} ({365.25 / max(a['pay'], 1e-9):5.1f} T) Bust {a['bust']:5.3f} Netto {a['net']:5.0f} "
                  f"S6 {a['s6']:4.2f} maxS {a['mx']:4.1f}/{a['mxmax']:.0f} WR {a['wr']:4.1f} n={a['n']}", flush=True)
        res[lbl] = m
        json.dump(res, open(fn, "w"), indent=1, default=float)
