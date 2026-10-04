"""Stufe 8.10: Endbewertung 8.00 gegen 8.10 im Konto-Replikat (eng6, gepaart: gleiche Starts, Stoerungen, Seeds).
8.10 = 8.00 + Trend-Day TD (n9sig.gen_lastmom 14:00, >= 0,75 ATR, nur Long, Stop 0,3 ATR, Ausstieg 15:55, 0,5 %),
Anpasser neutral (kein Zustandssatz hat Auswahl, Pruefung und Fremddaten verbessert).
Teile: gesamt / IS 2022-23 / OOS 2024-25 / je Kalenderjahr (Starts im Jahr, 120 Tage) / Kostenstress (Schlupf = 100 % des
Spreads statt 30 %) / Fremddaten 2006-21 / Nachbarn des TD-Punkts auf den Fremddaten.
Aufruf: python z8_final.py gft|ext"""
import sys, json, os
import eng6 as E, evl6 as V, y7_konto as Y, z8, z8_opt as ZO

TD = [("LM", dict(risk=0.5))]
CFG = {"8.00": None, "8.10": TD}


def jahr(extra, y):
    z8.use("gft")
    gps = [dict(g) for g in z8.GPS]; blks = list(z8.BLKS)
    for nm, gp in (extra or []):
        sym, gen, args = z8.NP.LIB[nm]
        blks.append(z8.NK.block(sym, gen, args, len(blks)))
        gps.append(dict(dict(on=1, risk=0.75, maxtrades=1, harv=1), **gp))
    GP = E.gparams(gps); V.set_generic(blks, GP)
    Pv = E.params(**dict(Y.BASE, **z8.KW80))
    end = f"{y}-12-31" if y < 2025 else "2025-12-31"
    warm = f"{y}-01-03" if y > 2022 else "2022-03-21"
    return V.evaluate(Pv, GP=GP, horizons=(120,), step=2, seeds=tuple(range(8)), skip=0.05, warm=warm, end=f"{y + 1}-06-30" if y < 2025 else end)["mean"]


if __name__ == "__main__":
    ds = sys.argv[1] if len(sys.argv) > 1 else "gft"
    fn = f"ergebnisse/z8_final_{ds}.json"
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    if ds == "gft":
        for lbl, ex in CFG.items():
            if lbl not in res:
                res[lbl] = z8.evaluate("gft", extra=ex)
                z8.save(fn, res)
            print(z8.kurz(lbl, res[lbl]), flush=True)
        for lbl, ex in CFG.items():
            k = lbl + " Kostenstress"
            if k not in res:
                r = {}
                z8.use("gft")
                # Schlupf 100 % des Spreads (sonst 30 %): eigene Auswertung ueber evl6 mit slip=1.0
                gps = [dict(g) for g in z8.GPS]; blks = list(z8.BLKS)
                for nm, gp in (ex or []):
                    sym, gen, args = z8.NP.LIB[nm]
                    blks.append(z8.NK.block(sym, gen, args, len(blks)))
                    gps.append(dict(dict(on=1, risk=0.75, maxtrades=1, harv=1), **gp))
                GP = E.gparams(gps); V.set_generic(blks, GP)
                Pv = E.params(**dict(Y.BASE, **z8.KW80))
                r["all"] = V.evaluate(Pv, GP=GP, horizons=(250, 500), step=3, seeds=tuple(range(1, 9)), skip=0.05, slip=1.0, end="2025-12-31")["mean"]
                res[k] = r
                z8.save(fn, res)
            print(z8.kurz(k, res[k]), flush=True)
        for y in (2022, 2023, 2024, 2025):
            for lbl, ex in CFG.items():
                k = f"{lbl} Jahr {y}"
                if k not in res:
                    res[k] = {"all": jahr(ex, y)}
                    z8.save(fn, res)
                print(z8.kurz(k, res[k]), flush=True)
    else:
        for lbl, ex in list(CFG.items()) + [("8.00 + " + n, ZO.EXTRA["8.00 + " + n]) for n in
                                             ("LM 840 thr0.5 s0.3", "LM 840 thr0.75 s0.4", "LM 840 thr0.5 s0.2", "LM 810 thr0.75 s0.3", "LM 840 thr1.0 s0.3")]:
            if lbl not in res:
                res[lbl] = z8.evaluate("ext", extra=ex)
                z8.save(fn, res)
            print(z8.kurz(lbl, res[lbl]), flush=True)
        for lbl in ("8.00", "8.10"):
            print(f"--- {lbl} ext\n" + z8.zustandstabelle(res[lbl]["ext"]), flush=True)
