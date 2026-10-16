"""Endauswertung Live-Runde: Kennzahlen je Fenster/Startjahr (16 Stoerungen) und gepaart (32) gegen die erste Variante.
Aufruf: py -3 g_final.py gft|ext [--slip 0.25] VAR1 VAR2 ...   (REP_SPREAD=modell fuer das alte Spread-Modell auf GFT)"""
import sys
DS = sys.argv[1]
if DS == "gft":
    import xg as X  # noqa: F401
else:
    import xe as X  # noqa: F401
import os, json

if __name__ == "__main__":
    import evl11 as V, eng11 as E, gsetup as GS
    from g_var import VAR
    a = sys.argv[2:]
    slip = 0.25
    if a and a[0] == "--slip":
        slip = float(a[1]); a = a[2:]
    WIN = X.WING if DS == "gft" else V.WIN5
    P = E.params(slip=slip)
    tag = f"{DS}_{os.environ['REP_SPREAD']}_slip{slip}"
    print(f"=== Datensatz {tag} ===", flush=True)
    res, sd = {}, {}
    for nm in a:
        b, kw = VAR[nm]
        GP = GS.configure(b, **kw); V.INIT = (GS.init_worker, (b, kw))
        r = V.evaluate(P, GP, windows=WIN, by_year=True, seeds=tuple(range(1, 17)), workers=10)
        res[nm] = {k: v for k, v in r.items() if k != "_rows"}
        for w in WIN:
            print(V.line(f"{nm} {w}", r[w]), flush=True)
        for y, x in r["jahre"].items():
            print(V.line(f"{nm} Start {y}", x), flush=True)
        sd[nm] = V.evaluate_seeds(P, GP, seeds=tuple(range(1, 33)), windows=WIN, workers=10)
    for nm in a[1:]:
        print(V.paired(sd[a[0]], sd[nm], f"{nm} gg {a[0]}"), flush=True)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"final_{tag}.json")
    json.dump(res, open(out, "w"), indent=1, default=float)
