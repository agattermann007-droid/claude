"""v12 / Prompt 9.3: Regime-Groesse nach oben - bestehende Stroeme mit Faktor f, solange die Fades NICHT live sind.

EA: RegimeGroesse (6.70) gibt es schon, aber nur <= 1 (RSI21 und Noise). Hier f > 1 fuer
  A) RSI21 + Noise (= RegimeGroesse > 1)
  B) A + LW, XA, TD, S0830, SR (alle Nicht-Fade-Stroeme)
Gepaart gegen V10 (32 Seeds, 5 Fenster).
"""
import x12  # noqa: F401
import pickle, numpy as np
import cfg11 as C, evl11 as V, eng11 as E, gen11 as G

S = C.signals()
m = V.mk(); m.set_r21(S["r21"], S["reg"])
live_at = G.portfolio_guard(S["fades"])
Pv0 = E.params()
SEEDS = tuple(range(1, 33))
base = pickle.load(open("ergebnisse/base_v10_32.pkl", "rb"))

m.set_nz(S["nz"])
z_vw0 = m.z["vw"].copy()
z_live = np.array([live_at(int(m.ev_t[e]))[0] for e in m.z["ev"]], bool)
NONFADE = set(range(10, 18))


def blocks_scaled(f):
    out = []
    for (s_, b, w) in C.blocks(S):
        if s_ in NONFADE and len(b["t"]):
            lv = np.array([live_at(int(t))[0] for t in b["t"]], bool)
            out.append((s_, b, np.where(lv, 1.0, f)))
        else:
            out.append((s_, b, w))
    return out


out = {}
for f in (1.25, 1.5, 2.0):
    for mode in ("A", "B"):
        m.z["vw"] = np.where(z_live, z_vw0, z_vw0 * f)
        m.set_generic(blocks_scaled(f) if mode == "B" else C.blocks(S))
        Pv = E.params(r21_regfak=f)
        r = V.evaluate_seeds(Pv, C.gp_v10(), seeds=SEEDS, windows=V.WIN5)
        lab = f"Regime x{f:.2f} {mode}"
        out[lab] = r
        print(V.paired(base, r, lab), flush=True)
m.z["vw"] = z_vw0
pickle.dump(out, open("ergebnisse/t12_regsize.pkl", "wb"))
