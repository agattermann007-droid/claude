"""Build 6.70: Konsistenzregel (15 %) - was kostet sie? 6.60 ohne Regel gegen passive (nur spaeter auszahlen) und aktive
(Tagesdeckel) Umsetzung, dazu der 14-Tage-Zyklus von Instant GOAT. Zusatzkennzahlen: Netto inkl. am Ende noch nicht
ausgezahltem Gewinn (net_open), Anteil der Auszahlungen, die zuletzt auf die Konsistenz warteten, Wartetage je Jahr.
Aufruf: python x62.py gft|ext ["Variante|..."] [Stoerungen] [Schritt]   (Ausgabe ergebnisse/x62_{gft|ext}.json, Ordner per X62_OUT)"""
import numpy as np, sys, json, os, time
import x60, evl10 as V10

CFG = ["6.60", "6.60 K15", "6.60 K15 Deckel", "6.60 K15 T14", "6.60 T14"]

if __name__ == "__main__":
    target = sys.argv[1]
    which = sys.argv[2].split("|") if len(sys.argv) > 2 and sys.argv[2] else CFG
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    step = int(sys.argv[4]) if len(sys.argv) > 4 else (1 if target == "gft" else 3)
    fn = os.path.join(os.environ.get("X62_OUT", "ergebnisse"), f"x62_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl in which:
        key = f"{lbl} [{seeds} s{step}]"
        if key in res:
            m = res[key]; t = None
        else:
            kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x60.VAR[lbl])
            t = time.time()
            m = x60.evaluate(target, kw, gpx, seeds=seeds, step=step, per_seed=True, by_year=True, fade_risk=frisk, rule=rule,
                             per=per, extra_key=extra, extra_gp=extra_gp)
            m["variante"] = lbl
            res[key] = m
            json.dump(res, open(fn, "w"), indent=1, default=float)
        print(V10.line(f"{target} {lbl}"[:40], m).split(" | zuletzt")[0], f"[{time.time() - t:.0f}s]" if t else "(Cache)", flush=True)
        print(f"     Netto inkl. offen {m['net_open']:5.0f} (offen am Ende {m['x_open_end']:4.0f} $/J) | Ø Auszahlung {m['paymean']:4.0f} $ | "
              f"zuletzt Konsistenz {m.get('lim_cons_pct', 0):4.0f} % | Wartetage Konsistenz {m['x_cons_wait']:5.1f}/J | Deckel-Tage "
              f"{m['x_cons_block']:4.1f}/J | Boden Ø {m['minbuf_mean']:4.0f} $ <1% {100 * m['near100']:.1f} % <2% {100 * m['near200']:.1f} %",
              flush=True)
        for y, a in m.get("jahre", {}).items():
            print(f"     Start {y}: Ausz {a['pay']:5.2f} ({365.25 / max(a['pay'], 1e-9):5.1f} T) Bust {a['bust']:5.3f} Netto {a['net']:5.0f} "
                  f"inkl. offen {a.get('net_open', a['net']):5.0f} n={a['n']}", flush=True)
