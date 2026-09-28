"""Endbewertung Build 6.50 (Netto) mit eng9 - wie x46: 16 Stoerungen, 1/2/3 Jahre, jeder Handelstag (GFT-Ersatz) bzw.
jeder dritte Tag (Fremddaten 2006-21) ein neues Konto, Startjahre, Streuung je Stoerung, Abstand zum Boden.
6.50 Ertrag = 6.40 Ertrag, aber Schutz gueltiger Tage nur fuer Noise und Fades (ohne N1330/N1300; RSI21 nur vor 13:00 NY
und ohne Fade-Regime) und Fade-Risiko 0,70 %. 6.50 Sicher = 6.40 Sicher mit Fade-Risiko 0,70 %. Mit engeren Spreads: Ordner kopieren, dort SPREAD_FAKTOR=0.6 python mk_proxy.py && python prep5.py
&& python sig5.py, dann x49.py gft in der Kopie (X49_OUT=. -> Ausgabe im aktuellen Ordner).
Aufruf: python x49.py gft|ext ["Variante|..."]   (Ausgabe ergebnisse/x49_{gft|ext}.json, Ordner per X49_OUT)"""
import numpy as np, sys, json, os, time
import evl9 as V9, x48

CFG = ["6.40 Ertrag", "6.50 Ertrag", "6.50 Ertrag ohne Regime-Schalter", "C50 R21 frei ab 11.0", "C50 R21 frei ab 11.0 + Regime",
       "6.40 F0.7 + frei N1330+N1300", "6.40 + R21 frei ab 13", "6.40 Sicher", "6.50 Sicher", "6.50 Sicher, N1330/N1300 frei"]

if __name__ == "__main__":
    target = sys.argv[1]
    which = sys.argv[2].split("|") if len(sys.argv) > 2 else CFG
    step = 1 if target == "gft" else 3
    fn = os.path.join(os.environ.get("X49_OUT", "ergebnisse"), f"x49_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl in which:
        if lbl in res:
            print(V9.line(f"{target} {lbl}"[:40], res[lbl]), "(Cache)", flush=True)
            continue
        v = x48.VAR[lbl]
        kw, gpx = v[0], v[1]
        frisk = v[2] if len(v) > 2 else 0.75
        rule = v[3] if len(v) > 3 else "P200/1.15"
        per = v[4] if len(v) > 4 else None
        t = time.time()
        m = x48.evaluate(target, kw, gpx, seeds=16, step=step, per_seed=True, by_year=True, fade_risk=frisk, rule=rule, per=per)
        m["variante"] = lbl
        print(V9.line(f"{target} {lbl}"[:40], m), f"[{time.time() - t:.0f}s]", flush=True)
        s = m["streuung"]
        print(f"     Streuung (16 Stoerungen): Ausz {s['mean'][0]:.2f} (SD {s['sd'][0]:.2f}) | Busts {s['mean'][1]:.3f} (SD {s['sd'][1]:.3f}) "
              f"| Netto {s['mean'][2]:.0f} (SD {s['sd'][2]:.0f}) | WR {s['mean'][6]:.1f} (SD {s['sd'][6]:.2f})", flush=True)
        for y, a in m["jahre"].items():
            print(f"     Start {y}: Ausz {a['pay']:5.2f} ({365.25 / max(a['pay'], 1e-9):5.1f} T) Bust {a['bust']:5.3f} Netto {a['net']:5.0f} "
                  f"S6 {a['s6']:4.2f} maxS {a['mx']:4.1f}/{a['mxmax']:.0f} WR {a['wr']:4.1f} n={a['n']}", flush=True)
        res[lbl] = m
        json.dump(res, open(fn, "w"), indent=1, default=float)
