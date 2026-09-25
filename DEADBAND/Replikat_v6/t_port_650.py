"""Abgleich EA <-> Replikat fuer Build 6.50 (Netto):
1. Voreinstellungen des EA (FadeRiskPct, GueltigSchutzR21BisNY, GueltigSchutzFrei, GueltigSchutzR21Regime, GueltigSchutz) =
   Replikat-Variante "6.50 Ertrag" (x48.VAR: Fade-Risiko, vp_r21_to, vp_r21_reg, vp_mods, vpx je Fade-Modul).
2. Die Stellen im Quelltext, die den Schutz je Modul entscheiden (EA: HandleR21-Aufruf, FadeLive, NzBar, HandleSymbol;
   Replikat: eng9 RSI21/Noise/Fades/DEADBAND), sind vorhanden und unveraendert.
3. Entscheidung je Modul (sperrt der Schutz einen neuen Einstieg?) auf einem Raster von Zustaenden: EA-Logik (woertlich
   uebertragen) gegen Replikat-Logik (woertlich aus eng9), mit und ohne Fade-Regime.
4. Fade-Regime fuer RSI21 (FadeRegimeLive = FadePortfolioPF zur M5-Kerze des Einstiegs, woertlich wie in t_port_640) gegen
   x48.r21_regime (pg_guard.port_live_ea zur Einstiegszeit) fuer alle RSI21-Signale auf GFT-Ersatz und Fremddaten.
Aufruf: python t_port_650.py   (Protokoll: ergebnisse/t_port_650.txt)"""
import re, os, numpy as np
import x48, x44, t_port_640 as TP

HERE = os.path.dirname(os.path.abspath(__file__))
MQ = open(os.path.join(HERE, "..", "DEADBAND_LIVE4.mq5"), encoding="utf-8").read()
ENG = open(os.path.join(HERE, "eng9.py"), encoding="utf-8").read()
LOG = []


def say(s):
    print(s, flush=True); LOG.append(s)


def inp(name):
    m = re.search(r'^input\s+\w+\s+' + name + r'\s*=\s*("[^"]*"|[^;]+);', MQ, re.M)
    v = m.group(1).strip()
    return v[1:-1] if v.startswith('"') else v


def fade_names():
    s = MQ[MQ.index('const string FADE_STANDARD = "') + len('const string FADE_STANDARD = "'):]
    s = s[:s.index('"')]
    return [e.split(",")[9] for e in s.split(";") if e.strip()]


# ------------------------------------------------------------------ 1. Voreinstellungen
def check_defaults():
    kw, gpx, frisk, rule, per = x48.VAR["6.50 Ertrag"]
    names = fade_names()
    frei_ea = [n.strip().upper() for n in inp("GueltigSchutzFrei").split(";") if n.strip()]
    frei_rep = [x48.F10N[i].upper() for i, d in (per or {}).items() if d.get("vpx", 0) > 0.5]
    ok = True
    ok &= abs(float(inp("FadeRiskPct")) - frisk) < 1e-12
    ok &= abs(float(inp("GueltigSchutzR21BisNY")) - kw["vp_r21_to"]) < 1e-12
    ok &= (inp("GueltigSchutzR21Regime") == "true") == (kw.get("vp_r21_reg", 0) == 1)
    ok &= inp("GueltigSchutz") == "true" and kw["vp_on"] == 3
    ok &= kw["vp_mods"] == 12                                  # Replikat: Noise (4) + Fades (8); RSI21 ueber vp_r21_to; DEADBAND aus
    ok &= sorted(frei_ea) == sorted(frei_rep)
    ok &= names == x48.F10N                                    # gleiche Modul-Reihenfolge (Strom-Index = Modul)
    ok &= rule == "P200/1.15" and abs(float(inp("FadePortPF")) - 1.15) < 1e-12 and int(inp("FadePortN")) == 200
    say(f"  EA: FadeRiskPct {inp('FadeRiskPct')}, GueltigSchutzR21BisNY {inp('GueltigSchutzR21BisNY')}, GueltigSchutzR21Regime {inp('GueltigSchutzR21Regime')}, "
        f"GueltigSchutzFrei {frei_ea} | Replikat: Fade-Risiko {frisk}, vp_r21_to {kw['vp_r21_to']}, vp_r21_reg {kw.get('vp_r21_reg', 0)}, "
        f"vp_mods {kw['vp_mods']}, frei {frei_rep} -> {'GLEICH' if ok else 'ABWEICHUNG'}")
    return ok


# ------------------------------------------------------------------ 2. Quelltext-Stellen
EA_STELLEN = [
    "HandleR21(k, today, keineEinstiege);",
    "if(gGueltigSchutz && R21GueltigSchutzJetzt(sigZeit))",
    "datetime t5 = (datetime)((long)t - (long)t % 300);                     // Open der M5-Kerze des Einstiegs",
    "if(NYHour(t5) < GueltigSchutzR21BisNY) return true;",
    "return (GueltigSchutzR21Regime && !FadeRegimeLive(t5));",
    "if(t == fadeRegZeit) return fadeRegLive;",
    "fadeRegZeit = t; fadeRegLive = (alle && n >= FadePortN && pf > FadePortPF);",
    "else if(gGueltigSchutz && !F[m].schutzFrei) grund = GueltigSchutzText();",
    "F[m].schutzFrei = FadeNameInListe(F[m].name, GueltigSchutzFrei);",
    "else if(gGueltigSchutz) grund = GueltigSchutzText();                                    // 6.40",       # Noise (NzBar)
    "HandleSymbol(k, today, keineEinstiege || gGueltigSchutz);",                                             # DEADBAND
    "gGueltigSchutz = GueltigSchutz && kBereit && kCycleStart > 0 && kValidDays < NeedValidDays && GueltigHeuteReal() >= GueltigSchwelle();",
]
REP_STELLEN = [
    "if not r21_on or not entries_ok or (vp_blk and ((vp_mods & 2) or nyh < vp_r21_to or r21_dd or (vp_r21_reg > 0 and r_reg[a] == 0))):",
    "if zcur >= 0 and nz_on and entries_ok and not (vp_blk and (vp_mods & 4))",
    "if vp_blk and (vp_mods & 8) and GP[s_, 16] <= 0.5:",
    "if (vp_blk and (vp_mods & 1)) or vp_tight:",
]


def check_source():
    ok = True
    for s_ in EA_STELLEN:
        n = MQ.count(s_)
        ok &= n == 1
        if n != 1:
            say(f"    EA-Stelle {n}x gefunden: {s_}")
    for s_ in REP_STELLEN:
        n = ENG.count(s_)
        ok &= n == 1
        if n != 1:
            say(f"    Replikat-Stelle {n}x gefunden: {s_}")
    say(f"  {len(EA_STELLEN)} EA-Stellen, {len(REP_STELLEN)} Replikat-Stellen: {'VORHANDEN' if ok else 'ABWEICHUNG'}")
    return ok


# ------------------------------------------------------------------ 3. Entscheidung je Modul
def ea_sperrt(modul, schutz, nyh, frei_liste, r21_bis, regime_live, r21_regime=True):
    """EA 6.50: schutz = gGueltigSchutz (GueltigSchutzPruefen); DEADBAND/RSI21 ueber den Aufruf, Noise in NzBar, Fades in FadeLive."""
    if modul == "db":
        return schutz
    if modul == "r21":
        return schutz and ((nyh < r21_bis) or (r21_regime and not regime_live))
    if modul == "nz":
        return schutz
    return schutz and not (modul.upper() in frei_liste)


def rep_sperrt(modul, vp_act, nyh, kw, per, r_reg_a):
    """eng9: vp_blk = Schutz aktiv (vp_on 3, vp_mods != 15); Sperre je Modul wie in run_path."""
    vp_mods = kw["vp_mods"]; vp_r21_to = kw["vp_r21_to"]; vp_r21_reg = kw.get("vp_r21_reg", 0); r21_dd = False
    vp_blk = vp_act and vp_mods != 15
    if vp_act and vp_mods == 15:
        return True
    if modul == "db":
        return bool(vp_blk and (vp_mods & 1)) or (vp_act and vp_mods == 15)
    if modul == "r21":
        return bool(vp_blk and ((vp_mods & 2) or nyh < vp_r21_to or r21_dd or (vp_r21_reg > 0 and r_reg_a == 0)))
    if modul == "nz":
        return bool(vp_blk and (vp_mods & 4))
    s_ = x48.F10N.index(modul)
    vpx = (per or {}).get(s_, {}).get("vpx", 0.0)
    return bool(vp_blk and (vp_mods & 8) and vpx <= 0.5)


def check_decisions():
    kw0, gpx, frisk, rule, per = x48.VAR["6.50 Ertrag"]
    frei = [n.strip().upper() for n in inp("GueltigSchutzFrei").split(";") if n.strip()]
    schwelle = 10000 * 0.005 + 0.5
    ok = True; n = 0; diff = []
    # Voreinstellung (13 NY, Regime an) und die Eckwerte der Eingaben: Uhrzeit 0 / 11 / 24, Regime an / aus
    for r21_bis, regime in ((float(inp("GueltigSchutzR21BisNY")), inp("GueltigSchutzR21Regime") == "true"),
                            (0.0, True), (0.0, False), (11.0, True), (13.0, False), (24.0, True), (24.0, False)):
        kw = dict(kw0, vp_r21_to=r21_bis, vp_r21_reg=1 if regime else 0)
        for valid in range(0, 7):
            for real in (-80.0, 0.0, 30.0, 50.49, 50.5, 75.0, 200.0):
                for cyc in (0, 1):
                    ea_schutz = bool(cyc > 0 and valid < 5 and real >= schwelle)
                    rep_schutz = bool(cyc > 0 and real != 0.0 and real >= 50.5 and valid < 5)
                    for nyh in (3.0, 9.5, 10.0, 10.95, 11.0, 12.95, 13.0, 13.05, 15.5, 16.9):
                        for live in (False, True):
                            for modul in ["nz", "r21"] + x48.F10N:
                                a = ea_sperrt(modul, ea_schutz, nyh, frei, r21_bis, live, regime)
                                b = rep_sperrt(modul, rep_schutz, nyh, kw, per, 1 if live else 0)
                                n += 1
                                if a != b:
                                    ok = False; diff.append((r21_bis, regime, valid, real, cyc, nyh, live, modul, a, b))
    say(f"  Entscheidung je Modul: {n} Zustaende (RSI21-Uhrzeit 0/11/13/24 und Regime an/aus, gueltige Tage, Tagesergebnis, "
        f"Zyklus, NY-Stunde, Fade-Regime, Modul), EA = Replikat: {'IDENTISCH' if ok else 'ABWEICHUNG'}")
    for d in diff[:5]:
        say(f"    {d}")
    return ok


# ------------------------------------------------------------------ 4. Fade-Regime fuer RSI21
def check_regime(N=200, th=1.15, hist_days=600):
    """Ergebnisse der virtuellen Fades (Kette wie blocks_port) in die Ringpuffer des EA, dazwischen die RSI21-Einstiege:
    EA-Entscheidung FadeRegimeLive(t5) = FadePortfolioPF (t_port_640.ea_port_pf) gegen x48.r21_regime."""
    import pg_blocks as PB, pg_guard as PGd, x41, streams as ST
    rule = x41.S70_OHNE
    exempt = set(rule.get("exempt", ()))
    kt_l, R_l, mi_l = [], [], []
    for i, nm in enumerate(PB.F10):
        fk = {}
        for ds in ("ext", "gft"):
            f = PB.fi(ds, nm)
            keep, live, tp, w = PB.apply_rule(f, rule if nm not in exempt else dict(kind="none"))
            fk[ds] = (f, keep)
        (f1, k1), (f2, k2) = fk["ext"], fk["gft"]
        v1 = (f1["t_entry"] < ST.LIM22) & k1
        kt_l.append(np.r_[PGd.known_time("ext", f1)[v1], PGd.known_time("gft", f2)[k2]])
        R_l.append(np.r_[f1["R"][v1], f2["R"][k2]]); mi_l.append(np.full(len(kt_l[-1]), i))
    kt_all = np.concatenate(kt_l); R_all = np.concatenate(R_l); mi_all = np.concatenate(mi_l)
    ok_all = True
    for target in ("gft", "ext"):
        blks, info, mk = x44.setup(target, "P200/1.15")
        ref = x48.r21_regime(target, mk, N, th, hist_days)
        q = mk.ev_t[mk.r21["ev"]].astype(np.int64)
        ev = [(int(kt_all[i]), 0, int(mi_all[i]), i) for i in range(len(R_all))] + [(int(q[j]), 1, 0, j) for j in range(len(q))]
        ev.sort(key=lambda x: (x[0], x[1], x[2]))
        bufs = [[] for _ in PB.F10]
        got = np.zeros(len(q), bool)
        for t, kind, m, i in ev:
            if kind == 0:
                bufs[m].append((t, float(R_all[i])))
                if len(bufs[m]) > TP.FADEHIST:
                    bufs[m].pop(0)
            else:
                pf, n = TP.ea_port_pf(bufs, t, N, hist_days)
                got[i] = (n >= N and pf > th)
        same = np.array_equal(ref.astype(bool), got)
        ok_all &= same
        say(f"  {target}: {len(q)} RSI21-Signale, Fade-Regime live nach Replikat {int(ref.sum())}, nach EA {int(got.sum())} -> "
            f"{'IDENTISCH' if same else 'ABWEICHUNG'}")
    return ok_all


if __name__ == "__main__":
    say("1. Voreinstellungen EA = Replikat-Variante 6.50 Ertrag")
    ok1 = check_defaults()
    say("2. Quelltext-Stellen des Schutzes je Modul")
    ok2 = check_source()
    say("3. Schutz gueltiger Tage je Modul")
    ok3 = check_decisions()
    say("4. Fade-Regime fuer RSI21 (FadeRegimeLive gegen x48.r21_regime)")
    ok4 = check_regime()
    say("GESAMT " + ("IDENTISCH" if (ok1 and ok2 and ok3 and ok4) else "ABWEICHUNG"))
    os.makedirs("ergebnisse", exist_ok=True)
    open(os.path.join("ergebnisse", "t_port_650.txt"), "w").write("\n".join(LOG) + "\n")
