"""Abgleich EA (RSI21_EK.mq5) <-> Replikat (ek_sig) an den Stellen, an denen der EA anders rechnet als DEADBAND 6.60:
  1. Tagesregime: EA aus H1-Kerzen je Handelstag (TagIndex, 17:00-17:00 NY), Replikat aus Servertagen (D1 aus M5).
     Woertlich uebertragen: Regime() mit CopyRates(H1) -> Schlusskurse je Tag ohne den laufenden Tag -> SMA lang/schnell
     (mit weniger Tagen, wenn die Historie kuerzer ist - wie sma_partial ab 50 Tagen).
  2. RSI des anderen Symbols: EA BarVor(T) = letzte Kerze, die vor T begann; Replikat po - 1 (Kerze vor der Kerze mit t <= T).
Geprueft fuer jeden Signal-Kandidaten (jede Kerze M15/M30/H1 beider Symbole) 2006-2026: Anteil gleicher Entscheidungen
(shortOk, gateL, gateS, regv) und gleicher Kreuz-Werte. Aufruf: python t_ek_port.py -> ergebnisse/t_ek_port.txt"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Replikat_v6"))
import ek_data, ek_sig                                              # noqa: E402
import prep5 as P                                                   # noqa: E402

OUT = []


def log(s):
    print(s, flush=True)
    OUT.append(s)


D = ek_data.load()
F = ek_sig.features(D)
NYOFF = 7
for si, s in enumerate(ek_sig.SYMS):
    # ---- 1. Regime wie im EA: H1-Kerzen (Serverzeit = NY + 7), TagIndex = floor((t_srv - (nyOff-7)*3600) / 86400)
    H1 = D[s]["h1"]
    t_srv_min = H1["t"] + NYOFF * 60                      # NY-Minuten -> Server-Minuten
    tag = (t_srv_min - (NYOFF - 7) * 60) // 1440
    # letzter H1-Schluss je Tag
    ut, first = np.unique(tag, return_index=True)
    last = np.r_[first[1:] - 1, len(tag) - 1]
    cl = H1["c"][last]
    maL = P.sma_partial(cl, 200, 50); maS = P.sma_partial(cl, 100, 50)
    m = F["sym"] == si
    T = F["T"][m]
    heute = (T + NYOFF * 60 - (NYOFF - 7) * 60) // 1440
    di = np.searchsorted(ut, heute)                        # Index des heutigen Tages (bzw. Einfuegeposition)
    ok = di >= 1
    j = np.clip(di - 1, 0, len(ut) - 1)
    c = cl[j]; mL = maL[j]; mS = maS[j]
    ok &= np.isfinite(mL) & np.isfinite(mS)
    # Replikat-Werte
    cR = F["cprev"][m]; mLR = F["maL"][m]; mSR = F["maS"][m]; okR = F["regok"][m]
    both = ok & okR
    def dec(c_, l_, s_):
        return np.stack([(c_ < l_) | (c_ < s_), (c_ > l_) & (c_ > s_), (c_ < l_) & (c_ < s_), c_ > l_], 1)
    same = np.all(dec(c[both], mL[both], mS[both]) == dec(cR[both], mLR[both], mSR[both]), 1)
    log(f"{s}: Regime bekannt EA {ok.mean():.4f} / Replikat {okR.mean():.4f}; Entscheidungen gleich in "
        f"{same.mean() * 100:.3f} % von {both.sum()} Kandidaten; Schlusskurs gleich {np.mean(np.isclose(c[both], cR[both])) * 100:.3f} %")
    # ---- 2. RSI des anderen Symbols: EA = letzte Kerze mit Beginn < T; Replikat = Kerze vor der letzten mit Beginn <= T
    o = ek_sig.SYMS[1 - si]
    for ti, kk in enumerate(ek_sig.KEYS):
        mm = m & (F["tf"] == ti)
        Tm = F["T"][mm]
        ob = D[o][kk]
        rsi_o = P.rsi_wilder(ob["c"], 21)
        pe = np.searchsorted(ob["t"], Tm, side="left") - 1          # letzte Kerze mit Beginn < T
        roE = np.where(pe >= 0, rsi_o[np.clip(pe, 0, None)], np.nan)
        roR = F["ro"][mm]
        f = np.isfinite(roE) & np.isfinite(roR)
        eq = np.isclose(roE[f], roR[f])
        # Unterschiede nur dort, wo das andere Symbol zur Zeit T keine Kerze hat (Luecke/Handelspause)
        has_T = np.isin(Tm, ob["t"])
        log(f"   Kreuz {s}<-{o} {kk}: gleich {eq.mean() * 100:.3f} % von {f.sum()}; Abweichungen ohne Kerze des anderen "
            f"Symbols bei T: {np.sum(~eq & ~has_T[f])}, mit Kerze: {np.sum(~eq & has_T[f])}")
os.makedirs(os.path.join(HERE, "ergebnisse"), exist_ok=True)
with open(os.path.join(HERE, "ergebnisse", "t_ek_port.txt"), "w") as fh:
    fh.write("\n".join(OUT) + "\n")
