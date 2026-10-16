"""Grundlinie auf dem GFT-Feed: V8 / V10 / V12 in den Fenstern xg.WING (rollierende 1-Jahres-Konten alle 7 Tage),
Kennzahlen (16 Stoerungen) und gepaarte Vergleiche (32 Stoerungen). Aufruf: py -3 g_base.py [seeds] [workers]"""
import xg  # noqa: F401
import sys, os, json, pickle, time

if __name__ == "__main__":
    import evl11 as V, eng11 as E, gsetup as GS
    NS = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    WK = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erg_gft_" + os.environ["REP_SPREAD"])
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    res, seeds = {}, {}
    for b in ("V8", "V10", "V12"):
        GP = GS.configure(b); V.INIT = (GS.init_worker, (b, {}))
        r = V.evaluate(E.params(), GP, windows=xg.WING, by_year=True, seeds=tuple(range(1, 17)), workers=WK)
        res[b] = {k: v for k, v in r.items() if k != "_rows"}
        for w in xg.WING:
            print(V.line(f"{b} {w}", r[w]), flush=True)
            print("   ", V.mods_line(r[w]), flush=True)
        for y, a in r["jahre"].items():
            print(V.line(f"{b} Start {y}", a), flush=True)
        seeds[b] = V.evaluate_seeds(E.params(), GP, seeds=tuple(range(1, NS + 1)), windows=xg.WING, workers=WK)
        print(f"  [{b} fertig nach {time.time() - t0:.0f} s]", flush=True)
    print(V.paired(seeds["V8"], seeds["V10"], "V10 gegen V8"), flush=True)
    print(V.paired(seeds["V10"], seeds["V12"], "V12 gegen V10"), flush=True)
    print(V.paired(seeds["V8"], seeds["V12"], "V12 gegen V8"), flush=True)
    json.dump(res, open(os.path.join(OUT, "g_base.json"), "w"), indent=1, default=float)
    pickle.dump(seeds, open(os.path.join(OUT, "g_base_seeds.pkl"), "wb"))
