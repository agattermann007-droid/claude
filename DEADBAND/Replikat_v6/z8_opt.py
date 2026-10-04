"""Stufe 8.10: Parametersaetze je Kontozustand. Vorher festgelegte, kleine Raster (Saetze in SETS).
Auswahl NUR auf IS (Starts 2022-03..2023, Ende 2023-12, 250 Tage, 8 Stoerungen); Pruefung OOS (2024-25) und Fremddaten
(2006-21) nur fuer die Finalisten (python z8_opt.py <satz> oos|ext). Gepaart: gleiche Starts, Stoerungen, Seeds.
Ergebnis: ergebnisse/z8_opt_<satz>_<teil>.json"""
import sys, os, json
import z8

ST = dict(st_on=1)
SETS = {
    # 1) je Zustand ein Faktor auf ALLE Stroeme (Richtung finden)
    "zall": [(f"{z} x{f}", ST, {z: {"all": f}}) for z in ("NACH_AUSZ", "REIFENAH", "LEICHT", "TIEF", "SERIE")
             for f in (0.5, 1.5)],
    # 2) einzelne Stroeme je Zustand aus (Zustand, in dem ein Strom Geld kostet oder nichts bringt)
    "zoff": [(f"{z} {g} aus", ST, {z: {g: 0.0}}) for z, g in (("SERIE", "lw"), ("SERIE", "xa"), ("LEICHT", "xa"), ("TIEF", "xa"),
                                                               ("REIFENAH", "r21"), ("REIFENAH", "xa"), ("NACH_AUSZ", "xa"),
                                                               ("LEICHT", "nz"), ("TIEF", "nz"), ("SERIE", "all"))],
    # 3) Plateau LEICHT, Schwellen, Gruppen, Kombination mit SERIE-XA
    "z2": [("LEICHT x1.25", ST, {"LEICHT": {"all": 1.25}}),
           ("LEICHT x2", ST, {"LEICHT": {"all": 2.0}}),
           ("LEICHT x1.5 nur fade", ST, {"LEICHT": {"fade": 1.5}}),
           ("LEICHT x1.5 nur r21+nz", ST, {"LEICHT": {"r21": 1.5, "nz": 1.5}}),
           ("LEICHT x1.5 Schwelle 3.5", dict(ST, st_light=3.5), {"LEICHT": {"all": 1.5}}),
           ("LEICHT x1.5 Schwelle 4.5", dict(ST, st_light=4.5), {"LEICHT": {"all": 1.5}}),
           ("LEICHT+TIEF x1.5", ST, {"LEICHT": {"all": 1.5}, "TIEF": {"all": 1.5}}),
           ("SERIE xa aus, Serie 4", dict(ST, st_streak=4), {"SERIE": {"xa": 0.0}}),
           ("SERIE xa aus, Serie 2", dict(ST, st_streak=2), {"SERIE": {"xa": 0.0}}),
           ("LEICHT x1.5 + SERIE xa aus", ST, {"LEICHT": {"all": 1.5}, "SERIE": {"xa": 0.0}}),
           ("LEICHT x1.5 + SERIE xa aus + REIFENAH x1.25", ST, {"LEICHT": {"all": 1.5}, "SERIE": {"xa": 0.0}, "REIFENAH": {"all": 1.25}}),
           ],
    # 4) Finalisten (nach IS gewaehlt) fuer OOS und Fremddaten
    "fin": [("LEICHT x1.5", ST, {"LEICHT": {"all": 1.5}}),
            ("LEICHT+TIEF x1.5", ST, {"LEICHT": {"all": 1.5}, "TIEF": {"all": 1.5}}),
            ("LEICHT x1.5 Schwelle 3.5", dict(ST, st_light=3.5), {"LEICHT": {"all": 1.5}}),
            ("REIFENAH x1.5", ST, {"REIFENAH": {"all": 1.5}}),
            ("LEICHT x1.5 + SERIE xa aus + REIFENAH x1.25", ST, {"LEICHT": {"all": 1.5}, "SERIE": {"xa": 0.0}, "REIFENAH": {"all": 1.25}}),
            ],
    # 5) Rauschmessung: fast neutrale Faktoren (Pfad-Chaos bei gleichen Starts/Stoerungen)
    "rausch": [(f"{z} x{f}", ST, {z: {"all": f}}) for z in ("LEICHT", "NACH_AUSZ") for f in (0.99, 1.01)],
}


import n9sig as N9, n8_port as NP
NP.LIB["LM"] = ("NAS", N9.gen_lastmom, (840, 955, 0, 0.75, 0, 0.3, 0.0, 1, 960))
# 6) robuste, bisher nicht uebernommene Stroeme nur mit Luft zum Boden (zustandsabhaengig ueber minbuf)
EXTRA = {
    "8.00 + RSI2 0,5 % ab 4 %": [("RSI2", dict(risk=0.5, minbuf=4.0))],
    "8.00 + RSI2 0,5 % ab 5 %": [("RSI2", dict(risk=0.5, minbuf=5.0))],
    "8.00 + MOM 0,5 % ab 4 %": [("MOM", dict(risk=0.5, minbuf=4.0))],
    "8.00 + MOM 0,5 % ab 5 %": [("MOM", dict(risk=0.5, minbuf=5.0))],
    "8.00 + LM 0,5 % ab 4 %": [("LM", dict(risk=0.5, minbuf=4.0))],
}
SETS["neu"] = [(k, {}, {}) for k in EXTRA]
# 7) Plateau des Trend-Day-Stroms LM (Schwelle, Uhrzeit, Stop) - alle 0,5 %, ohne Puffer-Schwelle
for t1 in (810, 840, 870):
    for thr in (0.5, 0.75, 1.0):
        for sk in (0.2, 0.3, 0.4):
            nm = f"LM {t1} thr{thr} s{sk}"
            NP.LIB[nm] = ("NAS", N9.gen_lastmom, (t1, 955, 0, thr, 0, sk, 0.0, 1, 960))
            EXTRA["8.00 + " + nm] = [(nm, dict(risk=0.5))]
SETS["lmp"] = [(k, {}, {}) for k in EXTRA if k.startswith("8.00 + LM ") and " thr" in k]


def run(name, part):
    fn = f"ergebnisse/z8_opt_{name}_{part}.json"
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    ds = "ext" if part == "ext" else "gft"
    cfgs = [("8.00 (Anpasser aus)", {}, {})] + SETS[name]
    for lbl, kw, rows in cfgs:
        if lbl in res:
            continue
        r = z8.evaluate(ds, kw=kw, rows=rows, parts=(part,), extra=EXTRA.get(lbl))
        res[lbl] = dict(kw=kw, rows=rows, r=r)
        z8.save(fn, res)
        print(z8.kurz(lbl, r), flush=True)
    return res


if __name__ == "__main__":
    name = sys.argv[1]
    for part in (sys.argv[2:] or ["IS"]):
        run(name, part)
