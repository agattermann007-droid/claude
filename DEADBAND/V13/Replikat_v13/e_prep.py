"""Fremddaten-Satz aufbauen: prep_m1 (NAS HistData, Gold Dukascopy) -> prep_ext (OANDA davor) -> prep11 -> Signale."""
import os, sys, time, runpy
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(W, "fremd")
os.environ.update(XAU_DIR=os.path.join(F, "xau"), NAS_DIR=os.path.join(F, "nas", "data", "histdata", "nsxusd", "normalized"),
                  OANDA_DIR=os.path.join(F, "oanda", "pyfinancialdata", "data", "currencies", "oanda", "XAU_USD"),
                  NPZ_STD=os.path.join(F, "npz"), NPZ_EXT=os.path.join(F, "npz_ext"))
os.makedirs(os.environ["NPZ_STD"], exist_ok=True)
if __name__ == "__main__":
    t0 = time.time()
    os.environ["NPZ_DIR"] = os.environ["NPZ_STD"]
    sys.argv = ["prep_m1.py", "all"]; runpy.run_path("prep_m1.py", run_name="__main__")
    print("prep_m1", round(time.time() - t0), "s", flush=True)
    runpy.run_path("prep_ext.py", run_name="__main__")
    del os.environ["NPZ_DIR"]
    import xe  # noqa: F401
    import prep11 as P
    P.build(force=True)
    import cfg11 as C
    S = C.signals(force=True)
    print("Signale fertig", round(time.time() - t0), "s", [len(b["t"]) for b in S["fades"]], flush=True)
