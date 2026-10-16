"""Datensatz + Signale auf dem GFT-Feed aufbauen (Cache je Spread-Modus)."""
import xg  # noqa: F401
import os, time
if __name__ == "__main__":
    t0 = time.time()
    import prep11 as P
    P.build(force=True)
    print("Daten", round(time.time() - t0), "s", os.environ["REP_CACHE"], flush=True)
    import cfg11 as C
    S = C.signals(force=True)
    print("Signale", round(time.time() - t0), "s", flush=True)
    for i, b in enumerate(S["fades"]):
        print(C.FADE_NAMES[i], "Signale", len(b["t"]), "live", int(b["live"].sum()), flush=True)
    for k in ("spike", "lw", "xa", "td"):
        print(k, len(S[k]["t"]))
    print("SR", [len(b["t"]) for b in S["sr"]], "RSI21", len(S["r21"]["T"]), "Noise", len(S["nz"]["day"]))
