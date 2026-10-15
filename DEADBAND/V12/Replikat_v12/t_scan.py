"""Scan Sweep-Reclaim je Symbol: Auswahl 2022-23, Pruefung 2024-26 und 2016-21. Ergebnis: ergebnisse/scan_<sym>.pkl"""
import numpy as np, itertools, time, pickle, sys
import pa11 as PA, sim11 as M
sym = sys.argv[1]
if sym == "XAU":
    MARKS = {  # name: (la, lb, loff, [(w0, w1, [x...])])
        "ASIA":  (-360, 120, 0, [(120, 360, [480, 720]), (480, 660, [720, 955])]),
        "ASIA2": (-360, 180, 0, [(180, 480, [600, 720]), (480, 660, [720, 955])]),
        "LON":   (120, 480, 0, [(480, 720, [720, 955])]),
        "PRE":   (360, 500, 0, [(510, 630, [720, 955])]),
        "NYAM":  (500, 570, 0, [(570, 720, [720, 955])]),
        "IBG":   (500, 600, 0, [(600, 840, [900, 955])]),
        "NOON":  (720, 810, 0, [(810, 930, [955])]),
        "PD":    (500, 810, -1, [(-360, 120, [300, 480]), (120, 480, [600, 720]), (480, 720, [720, 955])]),
        "PDF":   (-360, 1020, -1, [(-360, 120, [300, 480]), (120, 480, [600, 720]), (480, 720, [720, 955])]),
    }
else:
    MARKS = {
        "ASIA":  (-360, 180, 0, [(180, 570, [630, 955]), (570, 690, [720, 955])]),
        "LON":   (180, 570, 0, [(570, 690, [720, 955])]),
        "ORB":   (570, 585, 0, [(585, 720, [720, 955])]),
        "ORB30": (570, 600, 0, [(600, 780, [780, 955])]),
        "IB":    (570, 630, 0, [(630, 900, [955])]),
        "PRE":   (480, 570, 0, [(570, 630, [955]), (630, 780, [955])]),
        "H12":   (720, 780, 0, [(780, 900, [955])]),
        "PM":    (780, 870, 0, [(870, 945, [955])]),
        "PD":    (570, 960, -1, [(-360, 555, [565]), (570, 720, [955])]),
        "PDC":   (900, 960, -1, [(-360, 555, [565]), (570, 690, [955])]),
    }
GRID = dict(dr=(1, -1), sd=(0.0, 0.05), md=(0.3, 0.6), sb=(0.03, 0.10),
            tgt=((0, 1.0), (0, 1.5), (0, 2.0), (0, 3.0), (1, 0.0), (2, 0.0)))
rows = []
t0 = time.time()
for nm, (la, lb, loff, wins) in MARKS.items():
    for (w0, w1, xs) in wins:
        for x in xs:
            for dr, sd, md, sb, (tm, crv) in itertools.product(GRID["dr"], GRID["sd"], GRID["md"], GRID["sb"], GRID["tgt"]):
                b = PA.sweep(sym, la, lb, loff, w0, w1, x, sd, md, 0.0, 0, sb, tm, crv, 99.0, dr)
                if len(b["t"]) < 30:
                    continue
                res, r = PA.evalb(b)
                rows.append(dict(mark=nm, la=la, lb=lb, loff=loff, w0=w0, w1=w1, x=x, dr=dr, sd=sd, md=md, sb=sb, tm=tm, crv=crv,
                                 **{f"{p}_{k}": v[k] for p, v in res.items() for k in ("n", "wr", "pf", "er", "sum")}))
print(f"{len(rows)} Varianten in {time.time()-t0:.0f}s")
pickle.dump(rows, open(f"ergebnisse/scan_{sym}.pkl", "wb"))
