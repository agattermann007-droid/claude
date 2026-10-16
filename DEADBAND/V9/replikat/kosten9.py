"""DEADBAND V9 - Regel 4: Kosten-Stress (Spread x1,5 und x2) fuer Kandidaten aus auswertung9.py.

Spread geht in Einstieg (Ask), Short-Ausstiege, virtuelle Ergebnisse (Waechter) und Stop-Pruefung (6 Spreads) ein.
Bewertet wird 1 Jahr Laufzeit in A und B gegen BASIS unter demselben Stress.
"""
import json, os, sys
import aufbau9 as AU, tests9 as T, evl9 as V, daten9 as DA


def stress(namen, mults=(1.5, 2.0), datensatz="frei"):
    res = {}
    vs = {v["name"]: v for v in T.varianten()}
    for mu in mults:
        A = AU.baue(datensatz, spread_mult=mu)
        mk = AU.market(A)
        for n in ["BASIS"] + list(namen):
            e, ss = T.lauf(A, mk, vs[n], horizonte=(250,))
            res[f"{n}@{mu:g}"] = {k: dict(pay=g["pay"], bust=g["bust"], net=g["net"]) for k, g in e.items()}
            print(V.zeile(f"{n} Spread x{mu:g}", e), flush=True)
    ok = {}
    for n in namen:
        ok[n] = all(res[f"{n}@{mu:g}"][f]["net"] > res[f"BASIS@{mu:g}"][f]["net"] and
                    res[f"{n}@{mu:g}"][f]["bust"] <= res[f"BASIS@{mu:g}"][f]["bust"] + 1e-12
                    for mu in mults for f in ("A1J", "B1J"))
    json.dump(dict(res=res, ok=ok), open(os.path.join(DA.SCRATCH, f"kosten9_{datensatz}.json"), "w"), indent=1)
    return res, ok


if __name__ == "__main__":
    namen = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] else []
    r, ok = stress(namen, datensatz=sys.argv[2] if len(sys.argv) > 2 else "frei")
    print(ok)
