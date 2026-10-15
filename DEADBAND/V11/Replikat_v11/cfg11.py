"""Replikat v11 - Signalsaetze und Stromparameter der Builds (V8 = 8.10, V10 = 10.00) + Zwischenspeicher."""
import os, pickle, numpy as np
import prep11 as P, gen11 as G, eng11 as E

CACHE = P.CACHE
FADE_NAMES = [f[0] for f in G.FADE_STANDARD]
GS_FREI = ("N1330", "N1300")
SPECIAL = ["S0830", "LW", "XA", "TD"]
SR_NAMES = ["SRIB", "SRPRE", "SRH12", "SRPDN"]
STREAMS = FADE_NAMES + SPECIAL + SR_NAMES          # Stromnummer = Index


def signals(force=False):
    f = os.path.join(CACHE, "sig11.pkl")
    if os.path.exists(f) and not force:
        return pickle.load(open(f, "rb"))
    fades = G.list_fades()
    live_at = G.portfolio_guard(fades)
    r21, nz = G.r21_and_nz()
    reg = G.regime_flags(live_at, r21["T"])
    # Regime-Zeitreihe (fuer Auswertungen): Zustand je Tag 12:00 NY
    S = dict(fades=fades, spike=G.spike(), lw=G.lw(), xa=G.xa(), td=G.td(), sr=G.sr(), r21=r21, nz=nz, reg=reg)
    pickle.dump(S, open(f, "wb"), protocol=4)
    return S


def blocks(S, which=("fades", "special", "sr"), extra=()):
    """Liste (Stromnummer, Block, Gewicht). Listen-Fades nur mit Waechter 'live' (FadeWaechterOk)."""
    out = []
    if "fades" in which:
        for i, b in enumerate(S["fades"]):
            m = b["live"]
            out.append((i, {k: (v[m] if isinstance(v, np.ndarray) and len(v) == len(m) else v) for k, v in b.items()}, 1.0))
    if "special" in which:
        for j, key in enumerate(("spike", "lw", "xa", "td")):
            out.append((10 + j, S[key], 1.0))
    if "sr" in which:
        for j, b in enumerate(S["sr"]):
            out.append((14 + j, b, 1.0))
    for s_, b in extra:
        out.append((s_, b, 1.0))
    return out


def gp_v10(sr_risk=0.10, sr_on=True, extra=()):
    st = []
    for nm in FADE_NAMES:
        st.append(dict(on=1, risk=0.75, maxtrades=1, harv=1, tpdelay=5, minsprd=6, gsfree=1 if nm in GS_FREI else 0))
    st.append(dict(on=1, risk=0.75, maxtrades=1, harv=1, tpdelay=5, minsprd=6))            # S0830
    st.append(dict(on=1, risk=0.50, maxtrades=1, harv=1, tpdelay=5, minsprd=6, minbuf=4.0))  # LW
    st.append(dict(on=1, risk=0.75, maxtrades=1, harv=1, tpdelay=5, minsprd=6))            # XA
    st.append(dict(on=1, risk=0.50, maxtrades=1, harv=1, tpdelay=5, minsprd=6))            # TD
    for nm in SR_NAMES:
        st.append(dict(on=1 if sr_on else 0, risk=sr_risk, maxtrades=1, harv=1, tpdelay=4, minsprd=6))
    for kw in extra:
        st.append(kw)
    return E.gparams(st)


def gp_v8():
    return gp_v10(sr_on=False)
