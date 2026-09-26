"""Build 6.70: Aenderungen am EA (DEADBAND_LIVE4.mq5, Stand 6.60) als nachvollziehbare Textersetzungen. Jeder Anker muss genau
einmal vorkommen. Aufruf (einmal, auf dem 6.60-Stand): python mk_ea670.py"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MQ = os.path.join(HERE, "..", "DEADBAND_LIVE4.mq5")
src = open(MQ, encoding="utf-8").read()
assert '#property version   "6.60"' in src, "EA ist nicht auf dem 6.60-Stand"


def rep(old, new):
    global src
    n = src.count(old)
    assert n == 1, (n, old[:90])
    src = src.replace(old, new)


def box(lines):
    out = []
    for t in lines:
        assert len(t) <= 64, (len(t), t)
        out.append("//|  " + t.ljust(64) + "|")
    return "\n".join(out)


HEAD = [
    "DEADBAND LIVE 4  -  Build 6.70 REGIME, 26.09.2026",
    "BUILD 6.70: HANDEL MIT VOREINSTELLUNGEN UNVERAENDERT WIE 6.60.",
    "Auftrag: mehr Netto, mehr Auszahlungen, weniger Verlustserien.",
    "Nach vorab festgelegtem Pruefprotokoll (PROTOKOLL_670.md)",
    "wurden 12 Ideen in drei Runden geprueft. Keine erfuellt alle",
    "Kriterien fuer die drei Ziele; die beiden tragfaehigsten sind",
    "als Optionen eingebaut (Voreinstellung aus):",
    "1) RegimeGroesse (1 = aus): RSI21 und Noise mit Faktor X,",
    "   solange der Portfolio-Waechter die Fades NICHT live handeln",
    "   laesst (Signalzeit). Preset Regimeschutz (0,5): Fremddaten",
    "   2006-21 Busts 0,0065 statt 0,038 je Jahr (Bust im 1. Jahr",
    "   0,2 statt 1,0 %), 2022-25 und 2026 unveraendert; ohne",
    "   Fade-Regime aber 1,48 statt 2,15 Auszahlungen und 248 statt",
    "   363 $ je Jahr (Versicherung, kein Mehrertrag).",
    "2) FadeTagessperre (0 = aus): nach X Fade-Verlusten im Symbol",
    "   keine weiteren Fades in diesem Symbol bis 17:00 NY. Preset",
    "   Tagessperre (1, mit Regimeschutz): 2022-25 +0,36 / +0,33",
    "   Auszahlungen, +78 / +59 $ je Jahr, laengste Serie 6,4 statt",
    "   7,2 (breit / GFT-nah); Zukunftstest 2026 aber -0,07 / -0,16",
    "   Auszahlungen und -36 / -47 $. Nur nach eigenem Test im",
    "   Strategietester auf GFT-Kursen verwenden.",
    "Verworfen: Ziel fuer den gueltigen Tag verlaengern, Fade-",
    "Einstand, Serien-Stopp 2, Tages-Einstiegsstopp, Noise-Pause,",
    "Noise mit einer Position, RSI21 ab 11:00 NY (Bericht 6.70).",
    "Verlustserien je Position (MT5-Bericht) sind laenger als je",
    "Idee: ein Noise-Verlust zaehlt dort bis zu dreimal.",
    "Bericht DEADBAND_LIVE4_670_Bericht.md. Zurueck: rollback_6.60/.",
    "",
    "Build 6.60 ZUKUNFT, 25.09.2026",
]
rep("//|  DEADBAND LIVE 4  -  Build 6.60 ZUKUNFT, 25.09.2026              |\n", box(HEAD) + "\n")
rep('#property version   "6.60"', '#property version   "6.70"')

# --- Eingaben
rep('''input group             "=== Anzeige, Leiter, Test ==="''',
    '''input group             "=== 6.70: Optionen (Voreinstellung aus = Handel wie 6.60) ==="
input double RegimeGroesse    = 1.0;        // RSI21 und Noise mit Faktor X, solange der Portfolio-Waechter die Fades NICHT live handeln laesst (PF der letzten FadePortN <= FadePortPF, auch solange die Fade-Historie laedt; Signalzeit = Open der Einstiegskerze). 1 = aus (wie 6.60). Preset Regimeschutz 0,5: Fremddaten 2006-21 Busts 0,0065 statt 0,038 je Jahr, 2022-25 und 2026 unveraendert, ohne Fade-Regime aber weniger Auszahlungen und Netto
input int    FadeTagessperre  = 0;          // nach X Fade-Verlusten im Symbol am selben Prop-Tag (ab 17:00 NY) keine neuen Fade-Einstiege in diesem Symbol bis 17:00 NY (0 = aus wie 6.60). Test-Option: 2022-25 mehr Auszahlungen und kuerzere Serien, Zukunftstest 2026 nicht bestaetigt (Bericht 6.70)
input group             "=== Anzeige, Leiter, Test ==="''')

# --- Pruefung der Eingaben und Journal beim Start
rep('''     { Print("DEADBAND4: GueltigSchutzR21BisNY muss zwischen 0 und 24 (NY-Stunde) liegen"); return(INIT_PARAMETERS_INCORRECT); }''',
    '''     { Print("DEADBAND4: GueltigSchutzR21BisNY muss zwischen 0 und 24 (NY-Stunde) liegen"); return(INIT_PARAMETERS_INCORRECT); }
   if(RegimeGroesse <= 0.0 || RegimeGroesse > 1.0 || FadeTagessperre < 0)                                    // 6.70
     { Print("DEADBAND4: 6.70-Eingaben ungueltig (0 < RegimeGroesse <= 1, FadeTagessperre >= 0)"); return(INIT_PARAMETERS_INCORRECT); }''')
rep('''                                : StringFormat("Push bei jedem Wechsel LIVE <-> nur virtuell (PF %.2f), keine Vorwarnung (FadeFruehwarnPF <= FadePortPF)", FadePortPF))));''',
    '''                                : StringFormat("Push bei jedem Wechsel LIVE <-> nur virtuell (PF %.2f), keine Vorwarnung (FadeFruehwarnPF <= FadePortPF)", FadePortPF))));
   PrintFormat("DEADBAND4: 6.70 Regime | Handel wie 6.60%s | Regime-Groesse %s | Fade-Tagessperre %s",
               ((RegimeGroesse < 1.0 || FadeTagessperre > 0) ? ", dazu Optionen" : " (Voreinstellungen)"),
               (RegimeGroesse < 1.0 ? StringFormat("RSI21/Noise x%.2f, solange die Fades nicht live sind%s", RegimeGroesse,
                                                   (FadePortPF <= 0.0 ? " - WIRKUNGSLOS: Portfolio-Waechter aus (FadePortPF 0)" : "")) : "aus"),
               (FadeTagessperre > 0 ? StringFormat("nach %d Fade-Verlust(en) im Symbol keine Fades mehr bis 17:00 NY", FadeTagessperre) : "aus"));''')

# --- Regime-Groesse: RSI21
rep('''      if(AccountInfoDouble(ACCOUNT_EQUITY) < kStart) risk *= BelowStartMult;
      double restR = (R21BudgetPct > 0.0) ? BudgetRest(true) - unsicht : DBL_MAX;''',
    '''      if(AccountInfoDouble(ACCOUNT_EQUITY) < kStart) risk *= BelowStartMult;
      bool r21RegKlein = RegimeKlein(sigZeit);                     // 6.70: Regime-Groesse (Fades nicht live -> RSI21 x RegimeGroesse)
      if(r21RegKlein) risk *= RegimeGroesse;
      double restR = (R21BudgetPct > 0.0) ? BudgetRest(true) - unsicht : DBL_MAX;''')
rep('''         PrintFormat("DEADBAND4 %s RSI21: Einstieg %s M%d%s (RSI %.1f, Divergenz %d, Regime %d), %.2f Lot, Risiko %.2f (Puffer %.2f %%), Stop %.*f, Ziel %.*f (%.2f R)",
                     s, (dir > 0 ? "LONG" : "SHORT"), R21TfMin(t), (ke == k ? "" : " [2. Platz]"), sigRsi[t], div, reg, vol, vol*rd*mpp, buf, dg, sl, dg, tp, S[ke].rr);''',
    '''         PrintFormat("DEADBAND4 %s RSI21: Einstieg %s M%d%s (RSI %.1f, Divergenz %d, Regime %d), %.2f Lot, Risiko %.2f (Puffer %.2f %%%s), Stop %.*f, Ziel %.*f (%.2f R)",
                     s, (dir > 0 ? "LONG" : "SHORT"), R21TfMin(t), (ke == k ? "" : " [2. Platz]"), sigRsi[t], div, reg, vol, vol*rd*mpp, buf,
                     (r21RegKlein ? StringFormat(", Regime-Groesse x%.2f", RegimeGroesse) : ""), dg, sl, dg, tp, S[ke].rr);''')

# --- Regime-Groesse: Noise (Signalzeit = Ende der Pruefung = Open der Einstiegskerze)
rep('''   if(AccountInfoDouble(ACCOUNT_EQUITY) < kStart) fak *= BelowStartMult;
   bool   neuQ[8]; double neuR[8];                                           // eben eroeffnete Teile (die Positionsliste kann nachhinken)''',
    '''   if(AccountInfoDouble(ACCOUNT_EQUITY) < kStart) fak *= BelowStartMult;
   bool nzRegKlein = RegimeKlein(chkEnd);                                    // 6.70: Regime-Groesse (Fades nicht live -> Noise x RegimeGroesse)
   if(nzRegKlein) fak *= RegimeGroesse;
   bool   neuQ[8]; double neuR[8];                                           // eben eroeffnete Teile (die Positionsliste kann nachhinken)''')
rep('''   PrintFormat("DEADBAND4 %s NOISE: LONG %s - Schluss %.2f > UB %.2f (O %.2f, Vortag %.2f, sigma %.3f %%) | Stopfaktor %.3f, Vola-Verh. %.2f, Gewicht %.3f | Puffer %.2f %% x%.2f | %d Teil(e) eroeffnet%s",
               nzSym, NzHHMM(endMin), close, UB, nzO, nzPC, nzSig[slot]*100.0, tf, vratio, vw, buf, fak, offen, info);''',
    '''   PrintFormat("DEADBAND4 %s NOISE: LONG %s - Schluss %.2f > UB %.2f (O %.2f, Vortag %.2f, sigma %.3f %%) | Stopfaktor %.3f, Vola-Verh. %.2f, Gewicht %.3f | Puffer %.2f %% x%.2f%s | %d Teil(e) eroeffnet%s",
               nzSym, NzHHMM(endMin), close, UB, nzO, nzPC, nzSig[slot]*100.0, tf, vratio, vw, buf, fak,
               (nzRegKlein ? StringFormat(" (inkl. Regime-Groesse x%.2f)", RegimeGroesse) : ""), offen, info);''')

# --- Hilfsfunktionen: Regime-Groesse und Fade-Tagessperre (vor FadeLive)
rep('''void FadeLive(const int m, const int d, const double st, const double goal, const long xm, const datetime tSig)
  {''',
    '''// 6.70 Regime-Groesse: true = RSI21/Noise-Einstieg zur Zeit t (Open der Einstiegskerze) mit Faktor RegimeGroesse, weil der
//      Portfolio-Waechter die Fades nicht live handeln laesst (wie FadeRegimeLive, auch solange die Fade-Historie laedt).
//      Replikat: eng11 reg_mult mit r21["reg"] / nz["reg"] (x48.r21_regime, x70.nz_regime) - Abgleich t_port_670.py.
bool RegimeKlein(const datetime t)
  {
   if(RegimeGroesse >= 1.0) return false;
   datetime t5 = (datetime)((long)t - (long)t % 300);
   return !FadeRegimeLive(t5);
  }

// 6.70 Fade-Tagessperre: geschlossene Fade-Positionen mit Verlust (Ergebnis + Swap < 0, wie losses[] im Replikat) im Symbol
//      des Platzes k seit 17:00 NY (Prop-Tag) - aus der Deal-Historie (wird bei jeder Positionsaenderung neu geladen)
int FadeVerlusteHeute(const int k)
  {
   long heute = PropDayIndex(TimeCurrent());
   int n = 0;
   for(int i=nD-1;i>=0;i--)
     {
      if(PropDayIndex(D[i].time) < heute) break;
      if(!IsFadeMagic(D[i].magic) || D[i].sym != S[k].sym) continue;
      if(D[i].entry != DEAL_ENTRY_OUT && D[i].entry != DEAL_ENTRY_OUT_BY) continue;
      if(D[i].profit + D[i].swap < 0.0) n++;
     }
   return n;
  }

void FadeLive(const int m, const int d, const double st, const double goal, const long xm, const datetime tSig)
  {''')
rep('''   else if(SerienPause()) grund = "Serien-Stopp (Verlustserie)";
   else if(!FadeWaechterOk(m, tSig)) grund = FadeWaechterText(m, tSig);''',
    '''   else if(SerienPause()) grund = "Serien-Stopp (Verlustserie)";
   else if(FadeTagessperre > 0 && FadeVerlusteHeute(k) >= FadeTagessperre)                                  // 6.70
      grund = StringFormat("Fade-Tagessperre: %d Fade-Verlust(e) heute in %s (bis 17:00 NY)", FadeVerlusteHeute(k), s);
   else if(!FadeWaechterOk(m, tSig)) grund = FadeWaechterText(m, tSig);''')

# --- Regime-Meldungen: Hinweis auf die Regime-Groesse
rep('''         Meldung(StringFormat("FADE-REGIME WIEDER LIVE: PF %.2f aus den letzten %d virtuellen Signalen > %.2f - Fades handeln wieder%s", pf, n, FadePortPF,
                              (warnBereich ? StringFormat(" (FRUEHWARNUNG: PF noch unter %.2f)", FadeFruehwarnPF) : "")));''',
    '''         Meldung(StringFormat("FADE-REGIME WIEDER LIVE: PF %.2f aus den letzten %d virtuellen Signalen > %.2f - Fades handeln wieder%s%s", pf, n, FadePortPF,
                              (RegimeGroesse < 1.0 && (R21Aktiv || NzAktiv) ? ", RSI21/Noise wieder volle Groesse" : ""),
                              (warnBereich ? StringFormat(" (FRUEHWARNUNG: PF noch unter %.2f)", FadeFruehwarnPF) : "")));''')
rep('''         Meldung(StringFormat("FADE-REGIME AUS: PF %.2f aus den letzten %d virtuellen Signalen <= %.2f - Fades nur noch virtuell%s. Auszahlungen werden seltener.", pf, n, FadePortPF,
                              (R21Aktiv && GueltigSchutz && GueltigSchutzR21Regime ? ", RSI21 an gueltigen Tagen geschuetzt" : "")));''',
    '''         Meldung(StringFormat("FADE-REGIME AUS: PF %.2f aus den letzten %d virtuellen Signalen <= %.2f - Fades nur noch virtuell%s%s. Auszahlungen werden seltener.", pf, n, FadePortPF,
                              (R21Aktiv && GueltigSchutz && GueltigSchutzR21Regime ? ", RSI21 an gueltigen Tagen geschuetzt" : ""),
                              (RegimeGroesse < 1.0 && (R21Aktiv || NzAktiv) ? StringFormat(", RSI21/Noise x%.2f", RegimeGroesse) : "")));''')

# --- Panel
rep('''      "DEADBAND LIVE 6.60 ZUKUNFT   %s\\n"''', '''      "DEADBAND LIVE 6.70 REGIME   %s\\n"''')
rep('''   txt += "\\n  Auszahlungstakt   " + TaktStatusText();                   // 6.40''',
    '''   txt += "\\n  Auszahlungstakt   " + TaktStatusText();                   // 6.40
   txt += "\\n  Optionen 6.70     " + OptionenStatusText();               // 6.70''')
rep('''string TaktStatusText()
  {''', '''// 6.70: Stand der Optionen (Regime-Groesse, Fade-Tagessperre) fuer das Panel
string OptionenStatusText()
  {
   string t = "Regime-Groesse ";
   if(RegimeGroesse >= 1.0) t += "aus";
   else t += StringFormat("x%.2f (jetzt %s)", RegimeGroesse, (RegimeKlein(TimeCurrent()) ? "KLEIN - Fades nicht live" : "volle Groesse - Fades live"));
   t += " | Fade-Tagessperre ";
   if(FadeTagessperre <= 0) return t + "aus";
   t += StringFormat("ab %d Verlust(en):", FadeTagessperre);
   for(int k=0;k<nSym;k++) t += StringFormat(" %s %d", S[k].sym, FadeVerlusteHeute(k));
   return t;
  }

string TaktStatusText()
  {''')

open(MQ, "w", encoding="utf-8").write(src)
print("DEADBAND_LIVE4.mq5 auf 6.70 gesetzt,", len(src), "Zeichen")
