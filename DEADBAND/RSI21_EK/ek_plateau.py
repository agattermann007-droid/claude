"""RSI21 Eigenkapital - Plateau: jeder Parameter des Endstands (ergebnisse/ek_ca_RTVZ.json) auf seine Rasterwerte gesetzt,
die anderen fest; Bewertung wie ek_ca (Rendite bei 25 % Jahresvolatilitaet 2006-26, 4 Stoerungen). Ausgabe je Wert:
CAGR T / V / Z und Zielwert R:TVZ. Ein breites Plateau (Nachbarn fast gleich gut) spricht gegen eine Zufallsauswahl.
Aufruf: python ek_plateau.py -> ergebnisse/ek_plateau.json"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ek_ca as C                                                   # noqa: E402

if __name__ == "__main__":
    fn = sys.argv[1] if len(sys.argv) > 1 else "ek_ca_RTVZ.json"
    d = json.load(open(os.path.join(HERE, "ergebnisse", fn)))
    sel = dict(d["sel"]); sim = dict(d["sim"])
    for k in ("tf_gold", "tf_nas"):
        if k in sel:
            sel[k] = tuple(sel[k])
    ziel = "R:TVZ"
    base_rows, base_rk = C.run_many([("Endstand", sel, sim)], 4, ziel)[0]
    base = C.objective(base_rows, ziel)
    out = dict(base=base, rows=[])
    print(f"Endstand: Ziel {base:.2f} | {C.fmt(C.summary(base_rows), base_rk)}")
    for name, kind, values in C.SPACE:
        cv = C.cur_value(sel, sim, name, kind)
        cands = []
        for v in values:
            s2, m2 = C.apply(sel, sim, name, kind, v)
            cands.append((f"{name}={v}", s2, m2))
        res = C.run_many(cands, 4, ziel)
        parts = []
        for (nm, _, _), (rows, rk) in zip(cands, res):
            ob = C.objective(rows, ziel)
            sm = C.summary(rows)
            is_cur = nm.split("=", 1)[1] == str(cv) or (isinstance(cv, (list, tuple)) and nm.split("=", 1)[1] == str(tuple(cv)))
            out["rows"].append(dict(param=name, value=nm.split("=", 1)[1], cur=is_cur, obj=ob, r=rk,
                                    T=sm["T"]["cagr"], V=sm["V"]["cagr"], Z=sm["Z"]["cagr"]))
            parts.append(f"{nm.split('=', 1)[1]}{'*' if is_cur else ''}: {ob:5.1f} ({100 * sm['T']['cagr']:.0f}/{100 * sm['V']['cagr']:.0f}/{100 * sm['Z']['cagr']:.0f})")
        print(f"{name:16s} " + "  ".join(parts), flush=True)
    with open(os.path.join(HERE, "ergebnisse", "ek_plateau.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
