"""DEADBAND V9 - Testprotokoll (FESTGELEGT 16.10.2026 VOR DEN ERGEBNISSEN; keine Varianten nachschieben).

37 Konfigurationen (Grenze ~45, alle zaehlen):
  BASIS   V8 8.10
  S_R1..S_R10   Sperre NAS-Long-Fades + S0830 bei Abwaertsregime R1..R10 (regime9.py)
  H_R9, H_R10   dieselben Vola-Regeln als halbes Risiko (Nagel 2012: Gegenbeleg)
  S_NA, S_TR    Noise-Area-Veto, Tagesrichtung < -sigma (nur NAS, Signalkerze 9:30-16:00 NY)
  K_R3NA, K_R3R9, K_R6NA, K_R3R9NA   Kombinationen aus hoechstens 3 unabhaengigen Filtern (Trend / Vola / Intraday)
  G_R1..G_R10   Gold-Short-Fades (X0630, X0300S, X1000S) spiegelbildlich: Sperre bei Aufwaertsregime
  Z_06, Z_GS, Z_HH   Fade-Ziel: mindestens 0,6 R | Gegenseite | halb Mitte + Rest Gegenseite mit Einstand
  LW_940        LW erst ab 9:40 NY (Signalkerze ab 9:35)
  NS_R3         NAS-Short-Fades nur im Abwaertsregime R3 (live-Zusatz, virtuelle Historie wie V8)
  SM_L, SM_B    Schluss-Momentum NAS 15:30-15:55 NY (Rendite seit Vortagesschluss >= 0,5 ATR, Stop 0,3 ATR,
                Risiko 0,5 %): nur Long | beide Richtungen
  CPPI          Groesse linear zum Puffer: Faktor = Puffer / 6 % (voll nur an der Equity-Spitze), mindestens 0,1
Gesperrte Signale fallen nur LIVE weg; virtuelle Signale (Portfolio-Waechter) laufen weiter wie in 8.20.

Uebernahme nur, wenn ALLES zutrifft:
  1. In A UND B Netto/Jahr hoeher und Busts/Jahr nicht hoeher, fuer 1 UND 2 Jahre Laufzeit
  2. gesperrte Live-Trades: Summe R < 0 in A UND B (nur Sperr-/Halb-Varianten)
  3. Netto-Differenz je Startjahr (1-Jahres-Konten) positiv in mindestens 5/7 der Jahre
  4. Kosten-Stress: Spread x1,5 und x2 - Netto weiter hoeher in A und B (1 Jahr Laufzeit)
"""
import json, os, sys, time
import numpy as np
import aufbau9 as AU, cfg9 as C, evl9 as V, gen9 as G, regime9 as RG, eng9 as E, daten9 as DA

NAS_LONG = ("N1030", "N1330", "N1800", "N0930", "N1100", "N1300", "S0830")
GOLD_SHORT = ("X0630", "X0300S", "X1000S")
NAS_FADES = ("N1030", "N1330", "N1800", "N0930", "N1100", "N1300")
WIN = {"A": ("2016-01-01", "2022-01-01"), "B": ("2022-01-01", "2026-10-17")}


def _nymin(s):
    return int(np.datetime64(s, "m").astype(np.int64))


def varianten():
    v = [dict(name="BASIS", art="basis")]
    for r in RG.REGELN:
        v.append(dict(name=f"S_{r}", art="sperre", regeln=[r], ziel="nas"))
    for r in ("R9", "R10"):
        v.append(dict(name=f"H_{r}", art="halb", regeln=[r], ziel="nas"))
    v.append(dict(name="S_NA", art="sperre", regeln=["NA"], ziel="nas"))
    v.append(dict(name="S_TR", art="sperre", regeln=["TR"], ziel="nas"))
    for nm, rr in (("K_R3NA", ["R3", "NA"]), ("K_R3R9", ["R3", "R9"]), ("K_R6NA", ["R6", "NA"]), ("K_R3R9NA", ["R3", "R9", "NA"])):
        v.append(dict(name=nm, art="sperre", regeln=rr, ziel="nas"))
    for r in RG.REGELN:
        v.append(dict(name=f"G_{r}", art="sperre", regeln=[r], ziel="gold"))
    v.append(dict(name="Z_06", art="ziel", tgtmode=1))
    v.append(dict(name="Z_GS", art="ziel", tgtmode=2))
    v.append(dict(name="Z_HH", art="ziel", tgtmode=3))
    v.append(dict(name="LW_940", art="lw", lw_ab=575))
    v.append(dict(name="NS_R3", art="ns", regel="R3"))
    v.append(dict(name="SM_L", art="sm", dir=1))
    v.append(dict(name="SM_B", art="sm", dir=0))
    v.append(dict(name="CPPI", art="cppi", cppi=6.0))
    return v


# ------------------------------------------------------------------ Hilfen
def live_set(A, s):
    """wie cfg9.bloecke: Waechter, Feiertage, Stop >= 6 Spreads."""
    ok = s["live"].copy()
    dE = s["t_entry"] // 1440; dX = s["xm"] // 1440
    fr = list(A["frei"])
    ok &= ~np.isin(dE, fr) & ~np.isin(dX, fr)
    ok &= s["rd"] >= 6.0 * A["D"][s["sym"]]["sp"][s["i_entry"]]
    return ok


def flags(A, sigs=None):
    D = A["D"]; sigs = sigs or A["sigs"]
    FT = {s: RG.tagesregeln(D[s]["d1"]) for s in ("XAU", "NAS")}
    NA = RG.noise_area(D, "NAS")
    out = {}
    for s in sigs:
        f = RG.flags_signal(D, s["sym"], s["t_entry"], FT[s["sym"]])
        dn = {k: v[0] for k, v in f.items()}; up = {k: v[1] for k, v in f.items()}
        n = len(s["t_entry"])
        if s["sym"] == "NAS" and n:
            na, tr = RG.intraday_flags(D, s, NA)
        else:
            na = np.zeros(n, bool); tr = np.zeros(n, bool)
        dn["NA"] = na; dn["TR"] = tr; up["NA"] = np.zeros(n, bool); up["TR"] = np.zeros(n, bool)
        out[s["name"]] = dict(dn=dn, up=up)
    return out


def regel_flag(FL, name, regeln, ziel):
    key = "dn" if ziel == "nas" else "up"
    f = None
    for r in regeln:
        x = FL[name][key][r]
        f = x if f is None else (f | x)
    return f


def fenster_von(t):
    out = np.full(len(t), "", dtype=object)
    for w, (a, b) in WIN.items():
        out[(t >= _nymin(a)) & (t < _nymin(b))] = w
    return out


def signal_stats(A, sigs, betroffen, faktor=1.0):
    """Summe R der betroffenen Live-Trades je Fenster und Symbol (faktor 0,5 = halbes Risiko: wegfallende Haelfte)."""
    res = {}
    for s in sigs:
        if s["name"] not in betroffen:
            continue
        m = betroffen[s["name"]] & live_set(A, s) & np.isfinite(s["R"])
        w = fenster_von(s["t_entry"])
        for f in ("A", "B"):
            q = m & (w == f)
            k = f"{f}_{s['sym']}"
            a = res.setdefault(k, [0.0, 0])
            a[0] += float(s["R"][q].sum() * faktor); a[1] += int(q.sum())
    return res


# ------------------------------------------------------------------ eine Variante
def konfig(A, v, base_sigs=None):
    """-> (sigs, bloecke, GP, Pv, betroffen, faktor)"""
    D = A["D"]
    M = G.module_v8()
    sigs = A["sigs"] if base_sigs is None else base_sigs
    Pv = C.pv(); GP = C.gp_v8(M)
    maske = None; gewicht = None; betroffen = {}; faktor = 1.0
    extra = []
    if v["art"] in ("sperre", "halb"):
        FL = flags(A, sigs)
        ziel = v["ziel"]
        mods = NAS_LONG if ziel == "nas" else GOLD_SHORT
        maske = {}; gewicht = {}
        for s in sigs:
            if s["name"] not in mods:
                continue
            f = regel_flag(FL, s["name"], v["regeln"], ziel)
            f &= (s["dir"] > 0) if ziel == "nas" else (s["dir"] < 0)
            betroffen[s["name"]] = f
            if v["art"] == "sperre":
                maske[s["name"]] = ~f
            else:
                gewicht[s["name"]] = np.where(f, 0.5, 1.0)
        faktor = 1.0 if v["art"] == "sperre" else 0.5
    elif v["art"] == "ziel":
        sigs = G.waechter(G.erzeuge(D, M, tgtmode=v["tgtmode"]))
        GP = C.gp_v8(M, teilziel=(v["tgtmode"] == 3))
    elif v["art"] == "lw":
        sigs = G.waechter(G.erzeuge(D, M, lw_ab=v["lw_ab"]))
    elif v["art"] == "ns":
        M2 = [dict(m, dir=0) if m["name"] in NAS_FADES else m for m in M]
        s2 = G.erzeuge(D, [m for m in M2 if m["name"] in NAS_FADES])
        FT = RG.tagesregeln(D["NAS"]["d1"])
        neu = []
        for s in sigs:
            if s["name"] not in NAS_FADES:
                neu.append(s); continue
            t = [x for x in s2 if x["name"] == s["name"]][0]
            sh = t["dir"] < 0
            f = RG.flags_signal(D, "NAS", t["t_entry"], FT)[v["regel"]][0]
            pf, npf = G.portfolio_pf(sigs, t["t_entry"])
            live = (npf >= 200) & (pf > 1.15)
            t["pf"] = pf; t["npf"] = npf; t["live"] = live
            keep_s = sh & f & live
            # Longs wie V8 (gleiche Kerzen), Shorts nur im Abwaertsregime, Waechter der V8-Historie
            r = {k: (np.r_[s[k], t[k][keep_s]] if isinstance(s[k], np.ndarray) and len(s[k]) == len(s["t_entry"]) else s[k]) for k in s}
            r["live"] = np.r_[s["live"], np.ones(keep_s.sum(), bool)]
            o = np.argsort(r["t_entry"], kind="stable")
            for k in r:
                if isinstance(r[k], np.ndarray) and len(r[k]) == len(o):
                    r[k] = r[k][o]
            betroffen[s["name"]] = np.isin(np.arange(len(o)), np.nonzero(o >= len(s["t_entry"]))[0])
            neu.append(r)
        sigs = neu
        GP = C.gp_v8(M)
    elif v["art"] == "sm":
        sm = dict(name="SM", sym="NAS", typ=4, r0=930, L=5, tlen=5, xoff=955 - 930 - 10, buf=0.3, tgt=0, dir=v["dir"], mx=99.0,
                  risk=0.50, minbuf=0.0, grid=False, frei=False, schluss=960, minatr=0.5, zielr=0.0)
        x = G.waechter(G.erzeuge(D, [sm]))
        sigs = list(sigs) + x
        M = M + [sm]
        GP = C.gp_v8(M)
    elif v["art"] == "cppi":
        Pv = C.pv(cppi=v["cppi"])
    bl = C.bloecke(sigs, A["frei"], D=D, maske=maske, gewicht=gewicht)
    return sigs, bl, GP, Pv, betroffen, faktor


def lauf(A, mk, v, horizonte=(250, 500), fenster=("A", "B")):
    sigs, bl, GP, Pv, betroffen, faktor = konfig(A, v)
    mk.set_generic(bl)
    e = V.bewerte(mk, Pv, GP, fenster=fenster, horizonte=horizonte)
    ss = signal_stats(A, sigs, betroffen, faktor) if betroffen else {}
    return e, ss


def kurz(e):
    out = {}
    for k, g in e.items():
        out[k] = dict(pay=g["pay"], bust=g["bust"], net=g["net"], paymean=g["paymean"], valid=g["valid"], n=g["n"],
                      jahre={str(y): dict(pay=j["pay"], bust=j["bust"], net=j["net"], n=j["n"]) for y, j in g["jahre"].items()},
                      gs={kk: vv for kk, vv in g["gs"].items()})
    return out


def main(name="frei", nur=None):
    A = AU.baue(name)
    mk = AU.market(A)
    pf = os.path.join(DA.SCRATCH, f"tests9_{name}.json")
    res = json.load(open(pf)) if os.path.exists(pf) else {}
    for v in varianten():
        if nur and v["name"] not in nur:
            continue
        if v["name"] in res:
            continue
        t0 = time.time()
        e, ss = lauf(A, mk, v)
        res[v["name"]] = dict(v=v, konto=kurz(e), signal=ss)
        json.dump(res, open(pf, "w"), indent=1, default=float)
        print(V.zeile(v["name"], e), "|", " ".join(f"{k}:{x[0]:+.1f}R/{x[1]}" for k, x in sorted(ss.items())), f"[{time.time() - t0:.0f}s]", flush=True)
    return res


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "frei", sys.argv[2].split(",") if len(sys.argv) > 2 else None)
