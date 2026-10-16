"""Replikat 9 - Aufbau: Daten -> Signale (RSI21/Noise wie sig5, Fades wie gen9) -> Market fuer eng9. Mit Zwischenspeicher.

Aufruf:  python3 aufbau9.py NAME [gft-ordner]
  NAME = Kennung des Datensatzes (z. B. frei, gft), gft-ordner = Ordner mit MT5-Export-ZIPs/CSVs (NAS100_x_*, XAUUSD_x_*)
"""
import glob, os, pickle, sys, time
import numpy as np
import daten9 as DA, gen9 as G, cfg9 as C, eng9 as E
import sig5 as S5


def signale(D, frei):
    S5.FREI_DAYS.clear(); S5.FREI_DAYS.update(frei)          # Noise: handelsfreie Tage nach Regel (siehe cfg9.us_freie_tage)
    db = {"XAU": S5.db_candidates(D, "XAU", 0.70, False), "NAS": S5.db_candidates(D, "NAS", 0.65, True)}
    r21 = S5.r21_signals(D)
    nz = S5.nz_days(D)
    return dict(db=db, r21=r21, nz=nz)


def baue(name, gft_dir=None, spread_mult=1.0, neu=False):
    pf = os.path.join(DA.SCRATCH, f"auf9_{name}_sp{spread_mult:g}.pkl")
    if os.path.exists(pf) and not neu:
        return pickle.load(open(pf, "rb"))
    t0 = time.time()
    m5 = {}
    for s, pat in (("XAU", "XAUUSD"), ("NAS", "NAS100")):
        gft = None
        if gft_dir:
            fs = sorted(glob.glob(os.path.join(gft_dir, f"{pat}*")))
            m1 = [f for f in fs if "_M1_" in f]; m5f = [f for f in fs if "_M5_" in f]
            if m5f:
                g5 = DA.lese_mt5_export(m5f)
                if m1:                                          # M1 dort, wo vorhanden, zu M5 zusammengefasst (gleiches Ergebnis)
                    g1 = DA.m1_zu_m5(DA.lese_mt5_export(m1))
                    g5 = g5.combine_first(g1)
                gft = g5
        m5[s] = DA.lade_m5(s, gft=gft)
    D = DA.baue_D(m5, spread_mult)
    DA.info(D)
    frei = C.us_freie_tage()
    S = signale(D, frei)
    sigs = G.waechter(G.erzeuge(D))
    out = dict(D=D, S=S, sigs=sigs, frei=frei, name=name, spread_mult=spread_mult)
    pickle.dump(out, open(pf, "wb"))
    print(f"Aufbau {name} sp x{spread_mult:g}: {time.time() - t0:.0f} s")
    return out


def market(A, module=None):
    mk = E.Market(D=A["D"], S=A["S"])
    pf, n = G.portfolio_pf(A["sigs"], mk.r21["T"])
    mk.r21["reg"] = ((n >= 200) & (pf > 1.15)).astype(np.int64)    # Fade-Regime zur RSI21-Signalzeit (GueltigSchutzR21Regime)
    return mk


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "frei"
    gdir = sys.argv[2] if len(sys.argv) > 2 else None
    A = baue(name, gdir, neu=True)
    mk = market(A)
    print("RSI21-Signale", len(mk.r21["ev"]), "davon im Fade-Regime", int(mk.r21["reg"].sum()), "| Noise-Pruefungen", len(mk.nz["ev"]))
