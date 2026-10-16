"""Varianten gepaart gegen eine Referenz (gleiche Stoerungs-Seeds). Datensatz ueber das erste Argument:
  gft  = GFT-Feed (xg, Fenster xg.WING)      ext = Fremddaten wie Replikat v12 (xe, Fenster evl11.WIN5)
Aufruf: py -3 g_var.py gft REF VAR1 [VAR2 ...] [--seeds 32] [--workers 8]
Varianten-Namen siehe VAR unten (Build + Schalter fuer gsetup.configure)."""
import sys, os
DS = sys.argv[1]
if DS == "gft":
    import xg as X  # noqa: F401
else:
    import xe as X  # noqa: F401
import time, pickle

VAR = {
    "V8": ("V8", {}), "V10": ("V10", {}), "V12": ("V12", {}),
    "V8_ohneXA": ("V8", dict(off=("XA",))), "V10_ohneXA": ("V10", dict(off=("XA",))), "V12_ohneXA": ("V12", dict(off=("XA",))),
    "V8_XA1805": ("V8", dict(xa_ein=-355)), "V10_XA1805": ("V10", dict(xa_ein=-355)), "V12_XA1805": ("V12", dict(xa_ein=-355)),
    "V8_XA1810": ("V8", dict(xa_ein=-350)), "V10_XA1810": ("V10", dict(xa_ein=-350)),
    # Runde 2: Nachteil 2025-26 (Serien-Stopps durch SR) - alle ohne XA (wie live)
    "V8T_ohneXA": ("V8", dict(off=("XA",), tick=("N1030",))),                       # V8 + N1030 im Tick, ohne SR
    "V12_ohneXA_SR2": ("V12", dict(off=("XA", "SRH12", "SRPDN"))),                  # nur SRIB + SRPRE
    "V12_ohneXA_SRIB": ("V12", dict(off=("XA", "SRPRE", "SRH12", "SRPDN"))),
    "V12_ohneXA_SR005": ("V12", dict(off=("XA",), sr_risk=0.05)),
    "V12_ohneXA_SR003": ("V12", dict(off=("XA",), sr_risk=0.03)),
    "V12_ohneXA_SR0075": ("V12", dict(off=("XA",), sr_risk=0.075)),
    "V10_ohneXA_SR005": ("V10", dict(off=("XA",), sr_risk=0.05)),
    "V13a_tick": ("V12", dict(off=("XA",), sr_risk=0.05)),                            # = V12_ohneXA_SR005 (erster Kandidat, kostenempfindlich)
    "V13": ("V10", dict(off=("XA",), sr_risk=0.05)),                                  # Build 13.00 = V12-Code, V12TickN1030 aus, XA aus, SR 0,05 %
    "V10_ohneXA_SR003": ("V10", dict(off=("XA",), sr_risk=0.03)),
    "V10_ohneXA_SR0075": ("V10", dict(off=("XA",), sr_risk=0.075)),
}


def parse():
    a = sys.argv[2:]
    seeds, wk, names = 32, 8, []
    i = 0
    while i < len(a):
        if a[i] == "--seeds":
            seeds = int(a[i + 1]); i += 2
        elif a[i] == "--workers":
            wk = int(a[i + 1]); i += 2
        else:
            names.append(a[i]); i += 1
    return names, seeds, wk


if __name__ == "__main__":
    import evl11 as V, eng11 as E, gsetup as GS
    names, NS, WK = parse()
    WIN = X.WING if DS == "gft" else V.WIN5
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"erg_{DS}_{os.environ['REP_SPREAD']}")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time(); res = {}
    for nm in names:
        f = os.path.join(OUT, f"var_{nm}_{NS}.pkl")
        if os.path.exists(f):
            res[nm] = pickle.load(open(f, "rb")); print(f"{nm}: aus Zwischenspeicher", flush=True); continue
        b, kw = VAR[nm]
        GP = GS.configure(b, **kw); V.INIT = (GS.init_worker, (b, kw))
        res[nm] = V.evaluate_seeds(E.params(), GP, seeds=tuple(range(1, NS + 1)), windows=WIN, workers=WK)
        pickle.dump(res[nm], open(f, "wb"))
        print(f"{nm}: fertig nach {time.time() - t0:.0f} s  " +
              " | ".join(f"{w.split()[-1]} {res[nm][w][:, 0].mean():.2f}/{res[nm][w][:, 1].mean():.0f}$/B{int(res[nm][w][:, 2].sum())}" for w in WIN), flush=True)
    ref = names[0]
    for nm in names[1:]:
        print(V.paired(res[ref], res[nm], f"{nm} gg {ref}"), flush=True)
