"""Abgleich EA <-> Replikat fuer Build 6.30 (Trefferquote): woertliche Python-Uebertragung der Entscheidungen von
FadeTeilgewinn, EinstandSetzen und NzEinstand (DEADBAND_LIVE4.mq5) gegen die Replikat-Logik (gsig._sim = eng7-Ausstiege
auf Signal-Ebene) auf echten Signalen: Fades (10 Module, Teilgewinn 50 % ab 0,6 R), RSI21-Folgesignale und Noise-Teile
(Stop auf Einstand + 0,05 R ab 1 R). Kurse je M5-Kerze (Hoch/Tief = Kursverlauf, Stop vor Ziel vor T1 in derselben Kerze).
Geprueft: gleiche Ausloesekerze, gleiches Ergebnis je Signal (R), gleiche Teilmenge (Lots).
Aufruf: python t_port_630.py"""
import numpy as np, pickle, os
import gsig as G, prep5 as P, pg_blocks as PB, x40, nz2

FT1R, FT1F, BEAB, BEPLUS = 0.6, 0.5, 1.0, 0.05


def ea_port(sym, ie, d, rd, tpr, ix, lots, t1r, t1f, beab, beplus):
    """EA-Logik je Signal, Kerze fuer Kerze. Einstieg = Open der Kerze ie (Long zum Ask). Stop/Ziel liegen beim Broker
    (Ziel der Fades erst ab der Kerze nach der Einstiegskerze gesetzt - wie FadeVerwalten). FadeTeilgewinn/EinstandSetzen
    erst ab der Kerze nach der Einstiegskerze (NachEinstiegsKerze). Rueckgabe R (inkl. Kommission), Ausloesekerze, Teillots."""
    D = G.data()[sym]; o, h, l, sp = D["o"], D["h"], D["l"], D["sp"]
    k = G.SYM[sym]; mpp = G.MPP[k]; comm = G.COMM[k]
    n = len(ie)
    R = np.zeros(n); trig = np.full(n, -1); v1s = np.zeros(n)
    for t in range(n):
        i = int(ie[t]); dd = int(d[t])
        op = o[i] + (sp[i] if dd > 0 else 0.0)                       # POSITION_PRICE_OPEN
        sl = op - dd * rd[t]                                          # POSITION_SL beim Einstieg
        tp = op + dd * tpr[t] * rd[t] if tpr[t] > 0 else 0.0         # Ziel (gesetzt ab der naechsten Kerze)
        vol = lots[t]; acc = 0.0; t1done = t1r <= 0.0; bedone = beab <= 0.0
        j = i
        while True:
            if j >= ix[t] or j >= len(o):
                jj = min(j, len(o) - 1)
                acc += (o[jj] + (sp[jj] if dd < 0 else 0.0) - op) * dd * vol * mpp
                break
            s_ = sp[j]
            bid_hi, bid_lo = h[j], l[j]
            ask_hi, ask_lo = h[j] + s_, l[j] + s_
            # Broker-Stop (Stop vor Ziel in derselben Kerze)
            if (dd > 0 and bid_lo <= sl) or (dd < 0 and ask_hi >= sl):
                px = sl
                if dd > 0 and o[j] < sl:
                    px = o[j]
                if dd < 0 and o[j] + s_ > sl:
                    px = o[j] + s_
                acc += (px - op) * dd * vol * mpp
                break
            nach = j >= i + 1                                         # NachEinstiegsKerze
            if tp > 0 and nach and ((dd > 0 and bid_hi >= tp) or (dd < 0 and ask_lo <= tp)):
                acc += (tp - op) * dd * vol * mpp
                break
            if nach:
                bid = bid_hi if dd > 0 else None; ask = ask_lo if dd < 0 else None   # bester Kurs der Kerze
                rdp = (op - sl) * dd
                if not t1done and rdp > 0:                            # FadeTeilgewinn
                    lvl = op + dd * t1r * rdp
                    if (dd > 0 and bid >= lvl) or (dd < 0 and ask <= lvl):
                        v1 = np.floor(vol * t1f / 0.01 + 1e-9) * 0.01
                        t1done = True
                        if v1 >= 0.01 - 1e-9 and vol - v1 >= 0.01 - 1e-9:
                            acc += (lvl - op) * dd * v1 * mpp           # Teilschliessung am Niveau
                            vol = round(vol - v1, 2); trig[t] = j; v1s[t] = v1
                if not bedone:                                        # EinstandSetzen (ref = op, rd = R beim Einstieg)
                    rd0 = rd[t]
                    nsl = op + dd * beplus * rd0
                    if (sl - nsl) * dd >= 0:
                        bedone = True
                    else:
                        lvl = op + dd * beab * rd0
                        if (dd > 0 and bid >= lvl) or (dd < 0 and ask <= lvl):
                            sl = nsl; bedone = True; trig[t] = j
            j += 1
        R[t] = (acc - comm * lots[t]) / (rd[t] * lots[t] * mpp)
    return R, trig, v1s


def replica(sym, ie, d, rd, tpr, ix, lots, t1r, t1f, be):
    """Replikat: gsig._sim (Signal-Ebene der eng7-Ausstiege). Lots-Rundung des Teilgewinns wie eng7 (floor auf 0,01)."""
    R = np.zeros(len(ie)); trig = np.full(len(ie), -1)
    # Teilmenge je Signal wie eng7: v1 = floor(lots*f/0.01)*0.01, nur wenn v1 >= 0.01 und Rest >= 0.01 - sonst kein Teilgewinn
    for t in range(len(ie)):
        f_eff = 0.0
        if t1f > 0:
            v1 = np.floor(lots[t] * t1f / 0.01 + 1e-9) * 0.01
            f_eff = v1 / lots[t] if (v1 >= 0.01 - 1e-9 and lots[t] - v1 >= 0.01 - 1e-9) else 0.0
        Rt, why, held, mfe, mae, iout = G.simulate(sym, ie[t:t + 1], d[t:t + 1], rd[t:t + 1], tpr[t:t + 1], ix[t:t + 1],
                                                   tp1r=t1r, tp1f=f_eff, be=be, tpdelay=1)
        R[t] = Rt[0]
    return R


def lots_for(rd, sym, risk=75.0):
    k = G.SYM[sym]
    lt = np.floor(risk / (rd * G.MPP[k]) / 0.01 + 0.5) * 0.01
    return np.maximum(lt, 0.01)


def check(label, sym, ie, d, rd, tpr, ix, t1r, t1f, beab, beplus):
    lots = lots_for(rd, sym)
    Ra, trig, v1s = ea_port(sym, ie, d, rd, tpr, ix, lots, t1r, t1f, beab, beplus)
    be = beplus if beab > 0 else -99.0
    t1 = t1r if t1r > 0 else beab
    Rr = replica(sym, ie, d, rd, tpr, ix, lots, t1, t1f, be)
    # Kommission: gsig rechnet je Lot in R ueber rd (COMM/MPP/rd) - gleich wie ea_port (comm*lots/(rd*lots*mpp))
    diff = np.abs(Ra - Rr)
    ok = float(diff.max()) < 1e-9
    print(f"{label:34s} {len(ie):5d} Signale, ausgeloest {int((trig >= 0).sum()):5d} | max. Abweichung R {diff.max():.1e} | "
          f"Treffer EA {100 * (Ra > 0).mean():4.1f} % / Replikat {100 * (Rr > 0).mean():4.1f} % | {'GLEICH' if ok else 'ABWEICHUNG'}", flush=True)
    if not ok:
        for b in np.nonzero(diff > 1e-9)[0][:5]:
            print("   ", b, ie[b], d[b], rd[b], tpr[b], "EA", Ra[b], "Replikat", Rr[b], "Ausloesung", trig[b])
    return ok


if __name__ == "__main__":
    ok = True
    PB.ST._use("gft")
    for nm in PB.F10:                                                  # Fades: Teilgewinn 50 % ab 0,6 R
        f = PB.fi("gft", nm)
        ok &= check(f"Fade {nm}", f["sym"], f["ie"], f["d"], f["rd"], f["tp"], f["ix"], FT1R, FT1F, 0.0, 0.0)
    S = pickle.load(open(os.path.join(P.OUT, "sig5.pkl"), "rb"))      # RSI21-Folgesignale: Einstand ab 1 R
    D = G.data()
    for si, sym in enumerate(("XAU", "NAS")):
        r = S["r21"]
        m = (np.asarray(r["sym"]) == si) & (np.asarray(r["folge"]) == 1)
        ie = np.searchsorted(D[sym]["ny"], np.asarray(r["T"])[m]).astype(np.int64)
        d = np.asarray(r["dir"])[m].astype(np.int64); rd = np.asarray(r["rd"])[m].astype(float)
        ok_ = ie < len(D[sym]["ny"]) - 2
        ie, d, rd = ie[ok_], d[ok_], rd[ok_]
        rr = 2.64 if sym == "XAU" else 2.2
        ix = np.minimum(ie + 1152, len(D[sym]["o"]) - 1)
        ok &= check(f"RSI21 {sym}", sym, ie, d, rd, np.full(len(ie), rr), ix, 0.0, 0.0, BEAB, BEPLUS)
    for sm in (0.35, 0.5, 0.75):                                       # Noise-Teile: Einstand ab 1 R
        blk, (ie, d, rd, tp, ix) = nz2.nz2(0, every=60, stop_mult=sm)
        ok &= check(f"Noise Teil {sm}", "NAS", ie.astype(np.int64), d.astype(np.int64), rd.astype(float), np.zeros(len(ie)), ix.astype(np.int64), 0.0, 0.0, BEAB, BEPLUS)
    print("GESAMT", "IDENTISCH" if ok else "ABWEICHUNG")
