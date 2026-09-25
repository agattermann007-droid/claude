"""Build 6.50 auf einem 400k-Konto (statt 10k): dieselben Regeln, alle Groessen und Grenzen in % vom Startsaldo wie im EA.
Fest in Dollar bleiben wie im EA die GFT-Mindestauszahlung (MinPayoutUSD 105 $ Anteil = 131,25 $ Gewinn) und die Reserve
des gueltigen Tags (0,50 $); Mindestlot 0,01 und Lot-Schritt 0,01 wie bei GFT (auf 400k fast ohne Rundung).
Varianten: EA-Voreinstellung (MinProfitPct 0 -> Mindestgewinn 131,25 $ = 0,03 % vom Startsaldo) und MinProfitPct 1,3125
(= 5250 $, derselbe Anteil wie 131,25 $ auf 10k). Netto hier OHNE Neukauf (Preis eines 400k-Kontos unbekannt):
0,8 x 0,97 x Auszahlungen; Busts werden getrennt ausgewiesen. Abstand zum Boden: Schwellen 1 % / 2 % = 4000 / 8000 $.
Aufruf: python x50.py gft|ext ["Variante|..."] [Stoerungen] [Schritt]   -> ergebnisse/x50_{gft|ext}.json (X50_OUT)"""
import numpy as np, sys, json, os, time
import evl9 as V9, x48

START = 400000.0
VPCT = 0.5 + 0.5 / START * 100.0                                      # 0,5 % + 0,50 $ Reserve (wie der EA)
MP_EA = 105.0                                                         # MinPayoutUSD (Anteil des Traders), fest in $
MP_1313 = START * 1.3125 / 100.0 * 0.8                                # 5250 $ Gewinn = 1,3125 % (wie 131,25 $ auf 10k)


def v400(lbl, mp=MP_EA):
    v = x48.VAR[lbl]
    kw = dict(v[0], start=START, validpct=VPCT, minpayout=mp)
    return (kw,) + tuple(v[1:])


VAR = {
    "6.40 Ertrag 400k": v400("6.40 Ertrag"),
    "6.50 Ertrag 400k": v400("6.50 Ertrag"),
    "6.40 Ertrag 400k, Mindestgewinn 1,3125 %": v400("6.40 Ertrag", MP_1313),
    "6.50 Ertrag 400k, Mindestgewinn 1,3125 %": v400("6.50 Ertrag", MP_1313),
    "6.50 Sicher 400k": v400("6.50 Sicher"),
}
# 400k: RSI21 an gueltigen Tagen immer geschuetzt (GueltigSchutzR21BisNY=24) - nur die Fade-Bausteine von 6.50
_v = x48.VAR["6.50 Ertrag"]
VAR["6.50 Ertrag 400k, RSI21 immer geschuetzt"] = (dict(_v[0], vp_r21_to=24.0, start=START, validpct=VPCT, minpayout=MP_EA),) + tuple(_v[1:])
# 400k: 6.50-Schutz, aber Fade-Risiko 0,75 % wie 6.40
VAR["6.50 Ertrag 400k, Fade-Risiko 0,75 %"] = (dict(_v[0], start=START, validpct=VPCT, minpayout=MP_EA), _v[1], 0.75) + tuple(_v[3:])
VAR["6.50 Ertrag 400k, Fade-Risiko 0,75 %, Mindestgewinn 1,3125 %"] = (dict(_v[0], start=START, validpct=VPCT, minpayout=MP_1313), _v[1], 0.75) + tuple(_v[3:])


def line(lbl, m):
    return (f"{lbl:<44s} Ausz {m['pay']:5.2f} ({m['days_per_pay']:4.1f} T) Ø {m['paymean']:7.0f}$ Bust {m['bust']:5.3f} "
            f"Netto o. Neukauf {0.8 * 0.97 * m['gross']:8.0f}$ S6 {m['s6']:4.2f} WR {m['wr']:4.1f} | gueltig {m['valid']:4.1f} "
            f"| Boden Ø {m['minbuf_mean']:6.0f}$ ({100 * m['minbuf_mean'] / START:4.2f} %) <1% {100 * m['near100']:4.1f}% <2% {100 * m['near200']:4.1f}%")


if __name__ == "__main__":
    target = sys.argv[1]
    which = sys.argv[2].split("|") if len(sys.argv) > 2 and sys.argv[2] != "all" else list(VAR)
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    step = int(sys.argv[4]) if len(sys.argv) > 4 else (1 if target == "gft" else 3)
    V9.NEAR_SCALE = START / 10000.0
    fn = os.path.join(os.environ.get("X50_OUT", "ergebnisse"), f"x50_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl in which:
        key = f"{lbl} [{seeds} s{step}]"
        if key in res:
            print(line(lbl, res[key]), "(Cache)", flush=True)
            continue
        v = VAR[lbl]
        t = time.time()
        m = x48.evaluate(target, v[0], v[1], seeds=seeds, step=step, per_seed=True, by_year=True, fade_risk=v[2], rule=v[3],
                         per=v[4] if len(v) > 4 else None)
        m["netto_ohne_neukauf"] = 0.8 * 0.97 * m["gross"]
        res[key] = m
        json.dump(res, open(fn, "w"), indent=1, default=float)
        print(line(lbl, m), f"[{time.time() - t:.0f}s]", flush=True)
        for y, a in m["jahre"].items():
            print(f"     Start {y}: Ausz {a['pay']:5.2f} ({365.25 / max(a['pay'], 1e-9):5.1f} T) Bust {a['bust']:5.3f} n={a['n']}", flush=True)
