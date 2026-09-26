"""Abgleich EA <-> Replikat fuer Build 6.70 (Regime):
1. Voreinstellungen des EA = Replikat-Variante "6.60" (x70.VAR, = x60 "6.60b"): Pruefung 1 aus t_port_660 und die neuen Eingaben
   aus (RegimeGroesse 1 = reg_mult 1, FadeTagessperre 0 = fsym_block 0). Presets: Regimeschutz = "Z9 Regime-Groesse 0.5",
   Tagessperre = "Z10 Z9 + Z2", Sicher = 6.60 Sicher mit ausgeschalteten Optionen.
2.-5. aus t_port_650/t_port_660: Quelltext-Stellen des Schutzes je Modul, Entscheidung je Modul, Fade-Regime fuer RSI21
   (FadeRegimeLive gegen x48.r21_regime), Regime-Meldungen ohne Einfluss auf den Handel.
6. Quelltext-Stellen 6.70: RegimeKlein = !FadeRegimeLive(Open der M5-Kerze), genau zweimal in der Groessenrechnung (RSI21 mit
   sigZeit nach BelowStartMult, Noise mit chkEnd auf fak), Fade-Tagessperre in FadeLive nach dem Serien-Stopp; Replikat eng11
   gleichbedeutend (reg_mult an r_reg/z_reg, fsym_block an losses[] der Fade-Plaetze des Symbols).
7. Fade-Regime fuer Noise: FadeRegimeLive zur Zeit der Pruefung (chkEnd = Open der Einstiegskerze) gegen x70.nz_regime.
8. Fade-Tagessperre auf dem Trade-Protokoll des Replikats (fsym_block 1): kein ausgefuehrter Fade-Einstieg nach einem am selben
   Prop-Tag vorher geschlossenen Fade-Verlust im selben Symbol (EA-Regel FadeVerlusteHeute), und die Sperre greift.
9. Push-Texte der Regime-Meldungen bleiben unter 255 Zeichen.
Aufruf: python t_port_670.py   (Protokoll: ergebnisse/t_port_670.txt)"""
import re, os, numpy as np
import x60, x70, x48, x44, r6, evl6 as V
import t_port_650 as T5, t_port_660 as T6, t_port_640 as TP
import eng11 as E

LOG = T6.LOG
say = T6.say
MQ, inp = T5.MQ, T5.inp
ENG11 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "eng11.py"), encoding="utf-8").read()
HERE = os.path.dirname(os.path.abspath(__file__))


def setdict(fn):
    st = {}
    for l in open(os.path.join(HERE, "..", fn), encoding="utf-8"):
        l = l.strip()
        if l and not l.startswith(";") and "=" in l:
            k, v = l.split("=", 1); st[k] = v
    return st


def check_defaults():
    ok = T6.check_defaults()
    kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x70.VAR["6.60"])
    ok &= abs(float(inp("RegimeGroesse")) - 1.0) < 1e-12 and kw.get("reg_mult", 1.0) == 1.0
    ok &= int(inp("FadeTagessperre")) == 0 and kw.get("fsym_block", 0) == 0
    ok &= kw == x60.unpack(x60.VAR["6.60b"])[0]
    rs = setdict("DEADBAND_LIVE4_670_Regimeschutz.set"); ts = setdict("DEADBAND_LIVE4_670_Tagessperre.set")
    k9 = x60.unpack(x70.VAR["Z9 Regime-Groesse 0.5"])[0]; k10 = x60.unpack(x70.VAR["Z10 Z9 + Z2"])[0]
    ok_p = (abs(float(rs["RegimeGroesse"]) - k9["reg_mult"]) < 1e-12 and int(rs["FadeTagessperre"]) == k9.get("fsym_block", 0)
            and abs(float(ts["RegimeGroesse"]) - k10["reg_mult"]) < 1e-12 and int(ts["FadeTagessperre"]) == k10["fsym_block"])
    si = setdict("DEADBAND_LIVE4_670_Sicher.set")
    ok_p &= abs(float(si["RegimeGroesse"]) - 1.0) < 1e-12 and int(si["FadeTagessperre"]) == 0
    say(f"  neue Eingaben: RegimeGroesse {inp('RegimeGroesse')} (reg_mult {kw.get('reg_mult', 1.0)}), FadeTagessperre "
        f"{inp('FadeTagessperre')} (fsym_block {kw.get('fsym_block', 0)}); Presets Regimeschutz {rs['RegimeGroesse']}/{rs['FadeTagessperre']} "
        f"= Z9 ({k9['reg_mult']}/{k9.get('fsym_block', 0)}), Tagessperre {ts['RegimeGroesse']}/{ts['FadeTagessperre']} = Z10 "
        f"({k10['reg_mult']}/{k10['fsym_block']}), Sicher {si['RegimeGroesse']}/{si['FadeTagessperre']} -> {'GLEICH' if ok and ok_p else 'ABWEICHUNG'}")
    return ok and ok_p


def body(name):
    i = MQ.index(name)
    j = MQ.index("{", i)
    d = 0
    for k in range(j, len(MQ)):
        d += (MQ[k] == "{") - (MQ[k] == "}")
        if d == 0:
            return MQ[j:k + 1]
    raise ValueError(name)


def check_source670():
    ok = True
    bk = re.sub(r"//[^\n]*", "", body("bool RegimeKlein(const datetime t)"))
    ok &= re.sub(r"\s+", "", bk) == re.sub(r"\s+", "", """{ if(RegimeGroesse >= 1.0) return false;
        datetime t5 = (datetime)((long)t - (long)t % 300); return !FadeRegimeLive(t5); }""")
    uses = re.findall(r"RegimeKlein\((\w+)\)", re.sub(r"//[^\n]*", "", MQ))
    ok &= sorted(uses) == sorted(["sigZeit", "chkEnd", "TimeCurrent"]) or sorted(uses) == sorted(["sigZeit", "chkEnd"])
    r21 = body("void HandleR21(")
    ok &= ("if(AccountInfoDouble(ACCOUNT_EQUITY) < kStart) risk *= BelowStartMult;\n      bool r21RegKlein = RegimeKlein(sigZeit);"
           in r21 and "if(r21RegKlein) risk *= RegimeGroesse;\n      double restR" in r21)
    nz = body("void NzPruefung(")
    ok &= ("if(AccountInfoDouble(ACCOUNT_EQUITY) < kStart) fak *= BelowStartMult;\n   bool nzRegKlein = RegimeKlein(chkEnd);" in nz
           and "if(nzRegKlein) fak *= RegimeGroesse;" in nz and "kStart*NzRiskPct/100.0*vw/nzN*fak" in nz)
    fl = body("void FadeLive(")
    ok &= ('else if(SerienPause()) grund = "Serien-Stopp (Verlustserie)";\n   else if(FadeTagessperre > 0 && FadeVerlusteHeute(k) >= FadeTagessperre)'
           in fl)
    fv = re.sub(r"//[^\n]*", "", body("int FadeVerlusteHeute(const int k)"))
    ok &= all(s in fv for s in ("PropDayIndex(TimeCurrent())", "if(PropDayIndex(D[i].time) < heute) break;", "IsFadeMagic(D[i].magic)",
                                 "D[i].sym != S[k].sym", "DEAL_ENTRY_OUT", "D[i].profit + D[i].swap < 0.0"))
    # Replikat eng11: Regime-Groesse und Sperre an den entsprechenden Stellen
    ok &= "if reg_mult != 1.0 and r_reg[a] == 0:\n                r *= reg_mult" in ENG11
    ok &= "if reg_mult != 1.0 and z_reg[zcur] == 0:\n                        r *= reg_mult" in ENG11
    ok &= "nls += losses[G0 + 2 * q + sy]" in ENG11 and "if nls >= fsym_block:" in ENG11
    ok &= "if pnl < 0.0:\n                    losses[k] += 1" in ENG11                           # Verlust = Ergebnis inkl. Swap < 0 (ohne Kommission)
    say(f"  RegimeKlein = !FadeRegimeLive(M5-Open), Aufrufe {sorted(uses)}; RSI21/Noise-Groesse, Fade-Tagessperre in FadeLive, "
        f"FadeVerlusteHeute (Prop-Tag, Symbol, Ergebnis + Swap < 0); Replikat reg_mult/fsym_block -> {'OK' if ok else 'ABWEICHUNG'}")
    return ok


def check_noise_regime(N=200, th=1.15, hist_days=600):
    """wie t_port_650.check_regime, aber fuer die Noise-Pruefungen (chkEnd = Open der Einstiegskerze)."""
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
        ref = x70.nz_regime(target, mk, N, th, hist_days)
        q = mk.ev_t[mk.nz["ev"]].astype(np.int64)
        q5 = q - q % 5
        ev = [(int(kt_all[i]), 0, int(mi_all[i]), i) for i in range(len(R_all))] + [(int(q5[j]), 1, 0, j) for j in range(len(q))]
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
        say(f"  {target}: {len(q)} Noise-Pruefungen, Fade-Regime live nach Replikat {int(ref.sum())}, nach EA {int(got.sum())} -> "
            f"{'IDENTISCH' if same else 'ABWEICHUNG'}")
    return ok_all


def check_sperre_log():
    kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x70.VAR["Z10 Z9 + Z2"])
    blks, info, mk = x60.setup("gft", rule)
    V._MK = mk; mk.r21["reg"] = x48.r21_regime("gft", mk); mk.nz["reg"] = x70.nz_regime("gft", mk)
    GP = x70.fade_gp(gpx, frisk, per); V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    m = V.mk()
    n_e = 0; n_bad = 0; n_blk = 0
    for (a, b) in V.starts(m, 250, 25):
        for seed in (0, 5):
            Pv2 = Pv.copy()
            if seed:
                Pv2[E.PI["slip_frac"]] = 0.3
            r = E.run(m, Pv2, a, b, seed=seed, masks=V.masks(m, seed, 0.08 if seed else 0.0), GP=GP)
            n_blk += int(r["st"][E.SI["fsym_blk"]])
            tr = r["tr"]
            fd = tr[tr[:, 2] >= E.G0]
            for x in fd:
                n_e += 1
                sy = (int(x[2]) - E.G0) % 2
                # Zeiten im Protokoll: Prop-Tag x 1440 + NY-Minute -> Prop-Tag = t // 1440, Reihenfolge im Tag ab 17:00 NY
                pday_e = int(x[3]) // 1440; ord_e = (int(x[3]) % 1440 + 420) % 1440
                prev = fd[((fd[:, 2].astype(int) - E.G0) % 2 == sy)]
                # Verlust im Sinne der Sperre = Ergebnis inkl. Swap, ohne Kommission < 0. Spalte 1 enthaelt die Kommission (Gold
                # 5 $/Lot, NAS 0): NAS exakt (< 0), Gold nur sichere Verluste (< -15 $, mehr Kommission hat kein Fade-Trade)
                lim = 0.0 if sy == 1 else -15.0
                px_ = prev[:, 10].astype(np.int64)
                prev = prev[((px_ // 1440) == pday_e) & (((px_ % 1440 + 420) % 1440) < ord_e) & (prev[:, 1] < lim)]
                if len(prev):
                    n_bad += 1
    ok = n_bad == 0 and n_blk > 0
    say(f"  Replikat mit Tagessperre: {n_e} Fade-Trades, davon nach einem Fade-Verlust im Symbol am selben Prop-Tag eroeffnet: {n_bad}; "
        f"gesperrte Signale {n_blk} -> {'OK' if ok else 'ABWEICHUNG'}")
    return ok


def check_push_len():
    """laengste moegliche Regime-Meldung (PF-Zahlen mit 5 Stellen, n = 256) gegen die MQL5-Grenze fuer Push-Texte (255)."""
    txts = [
        "FADE-REGIME WIEDER LIVE: PF 99.99 aus den letzten 256 virtuellen Signalen > 99.99 - Fades handeln wieder, RSI21/Noise wieder volle Groesse (FRUEHWARNUNG: PF noch unter 99.99)",
        "FADE-REGIME AUS: PF 99.99 aus den letzten 256 virtuellen Signalen <= 99.99 - Fades nur noch virtuell, RSI21 an gueltigen Tagen geschuetzt, RSI21/Noise x0.50. Auszahlungen werden seltener.",
    ]
    ok = all(len("DEADBAND4: " + t) < 255 for t in txts)
    say(f"  laengste Regime-Meldung {max(len('DEADBAND4: ' + t) for t in txts)} Zeichen (Grenze 255) -> {'OK' if ok else 'ZU LANG'}")
    return ok


if __name__ == "__main__":
    say("1. Voreinstellungen EA = Replikat-Variante 6.60 (Optionen aus), Presets = Replikat-Varianten")
    ok1 = check_defaults()
    say("2. Quelltext-Stellen des Schutzes je Modul (wie 6.50)")
    ok2 = T5.check_source()
    say("3. Schutz gueltiger Tage je Modul (wie 6.50)")
    ok3 = T5.check_decisions()
    say("4. Fade-Regime fuer RSI21 (FadeRegimeLive gegen x48.r21_regime)")
    ok4 = T5.check_regime()
    say("5. Regime-Meldungen (RegimeWaechter): nur Meldungen, kein Einfluss auf den Handel")
    ok5 = T6.check_regime_msgs()
    say("6. Quelltext-Stellen 6.70 (Regime-Groesse, Fade-Tagessperre) in EA und Replikat")
    ok6 = check_source670()
    say("7. Fade-Regime fuer Noise (FadeRegimeLive zur Pruefzeit gegen x70.nz_regime)")
    ok7 = check_noise_regime()
    say("8. Fade-Tagessperre auf dem Trade-Protokoll des Replikats")
    ok8 = check_sperre_log()
    say("9. Laenge der Push-Texte")
    ok9 = check_push_len()
    say("GESAMT " + ("IDENTISCH" if all((ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8, ok9)) else "ABWEICHUNG"))
    os.makedirs("ergebnisse", exist_ok=True)
    open(os.path.join("ergebnisse", "t_port_670.txt"), "w").write("\n".join(LOG) + "\n")
