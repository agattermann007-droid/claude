"""Endbewertung Build 6.60 (nach PROTOKOLL_660.md): 6.40, 6.50, 6.60a, 6.60b mit 16 Stoerungen, jeder Handelstag (GFT-Ersatz)
bzw. jeder 3. Tag (Fremddaten), Startjahre, Streuung und Werte je Stoerung (fuer den paarweisen Vergleich), Abstand zum Boden.
Stresstest (Kriterium K-g): ABSCHLAG=0.2 entfernt 20 % der Fade-Gewinner (zufaellig, fest je Signal) aus allen virtuellen
Signalen - Waechter, RSI21-Regime und Konto sehen dieselbe geschwaechte Kante.
Aufruf: [ABSCHLAG=0.2] python x61.py gft|ext ["Variante|..."]   (Ausgabe ergebnisse/x61_{gft|ext}[_abschlag].json, Ordner per X61_OUT)"""
import numpy as np, sys, json, os, time
import x60, x48, x44, r6, pg_blocks as PB, pg_guard as PGd
import eng10 as E, evl6 as V, evl10 as V10

CFG = ["6.40 Ertrag", "6.50 Ertrag", "6.60a", "6.60b"]
ABSCHLAG = float(os.environ.get("ABSCHLAG", "0"))


def abschlag(frac):
    """Kanten-Abschlag: aus jeder Fade-Signalliste (beide Datensaetze) einen festen Anteil der Gewinner entfernen."""
    for s_, nm in enumerate(PB.F10):
        for ds in ("ext", "gft"):
            f = PB.fi(ds, nm)
            n = len(f["R"])
            rng = np.random.default_rng(1000 + 17 * s_ + (0 if ds == "ext" else 1))
            drop = (f["R"] > 0) & (rng.random(n) < frac)
            keep = ~drop
            g = {k: (v[keep] if isinstance(v, np.ndarray) and v.shape[:1] == (n,) else v) for k, v in f.items()}
            PB._FI[(ds, nm)] = g
    PGd._KT.clear(); x44._SET.clear(); x48._REG.clear()


if __name__ == "__main__":
    target = sys.argv[1]
    which = sys.argv[2].split("|") if len(sys.argv) > 2 else CFG
    step = 1 if target == "gft" else 3
    suf = f"_abschlag{int(round(100 * ABSCHLAG))}" if ABSCHLAG > 0 else ""
    fn = os.path.join(os.environ.get("X61_OUT", "ergebnisse"), f"x61_{target}{suf}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    if ABSCHLAG > 0:
        abschlag(ABSCHLAG)
    for lbl in which:
        if lbl in res:
            print(V10.line(f"{target} {lbl}"[:40], res[lbl]), "(Cache)", flush=True)
            continue
        kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x60.VAR[lbl])
        t = time.time()
        m = x60.evaluate(target, kw, gpx, seeds=16, step=step, per_seed=True, by_year=True, fade_risk=frisk, rule=rule, per=per,
                         extra_key=extra, extra_gp=extra_gp)
        m["variante"] = lbl
        res[lbl] = m
        json.dump(res, open(fn, "w"), indent=1, default=float)
        print(V10.line(f"{target} {lbl}"[:40], m), f"[{time.time() - t:.0f}s]", flush=True)
        s = m["streuung"]
        print(f"     Streuung (16): Ausz {s['mean'][0]:.2f} (SD {s['sd'][0]:.2f}) | Busts {s['mean'][1]:.3f} | Netto {s['mean'][2]:.0f} "
              f"(SD {s['sd'][2]:.0f})", flush=True)
        for y, a in m["jahre"].items():
            print(f"     Start {y}: Ausz {a['pay']:5.2f} ({365.25 / max(a['pay'], 1e-9):5.1f} T) Bust {a['bust']:5.3f} Netto {a['net']:5.0f} "
                  f"S6 {a['s6']:4.2f} WR {a['wr']:4.1f} n={a['n']}", flush=True)
