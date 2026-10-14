"""Baut research/patch_intrabar.mq5 (+ .diff) aus DEADBAND_V8.mq5 (Build 8.10). PLAN.md Abschnitt 7 (Stufe 3, E2-i).

EntryMode (nur das H1-Ausbruchsmodul "DEADBAND"; alle anderen Module unveraendert):
  0 A  Schluss der M15-Kerze wie 8.10 (Standard, handelsidentisch).
  1 B  erster Durchstoss: Bid >= H1-Hoch + X x aktueller Spread (Short: Bid <= H1-Tief - X x Spread).
  2 C  wie B, aber T Sekunden ununterbrochen jenseits (jede Beobachtung in OnTick und im 1-s-OnTimer).
  3 D  Teilbestaetigung: einmal je M15-Kerze ab 7,5 min, Kurs jenseits der H1-Kante und im obersten (untersten)
       Anteil ClsMin der bisherigen Kerzenspanne.
Richtungsfilter zum Entscheidungszeitpunkt: EMA50 (D1, Vortag) wie A; VWAP der abgeschlossenen Kerzen des Prop-Tags wie A
gegen den aktuellen Bid; RSI und MACD der laufenden Kerze (Schift 0). Kerzenqualitaet und Volumen beziehen sich auf eine
abgeschlossene Kerze und sind bei B/C nicht anwendbar; D prueft die Qualitaet der bisherigen Spanne und das Volumen
zeitanteilig (Volumen bisher x 900 s / verstrichene s gegen den Schnitt der letzten VolLen Kerzen).
Stop (3 x ATR14 der letzten abgeschlossenen M15-Kerze), Groesse, Ausstieg, Session, Tageslimits: identisch zu A
(gemeinsame Funktion DbOrder = unveraenderter Order-Teil von HandleSymbol). Keine Zufallselemente.
Aufruf: python werkzeuge/patch_intrabar_bauen.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patch_bauen as PB  # noqa: E402

RESEARCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KOPF = """//+------------------------------------------------------------------+
//| PATCH intrabar (research/patch_intrabar.mq5) - NUR STRATEGIETESTER|
//| = DEADBAND_V8.mq5 Build 8.10 + EntryMode fuer das H1-Modul.       |
//| EntryMode 0 = handelsidentisch zu V8.10. Testplan:                |
//| research/MT5_TESTPLAN_INTRABAR.md, Aenderungen: patch_intrabar.diff|
//+------------------------------------------------------------------+
"""

INPUTS = """input group             "=== Patch Intrabar (Stufe 3, nur Strategietester) ==="
input int    EntryMode        = 0;      // H1-Modul: 0 A M15-Schluss (wie 8.10) | 1 B erster Durchstoss | 2 C Durchstoss + Haltezeit | 3 D Teilbestaetigung nach IbTeilSek
input double IbSpreadX        = 1.0;    // B/C: Durchstoss um mindestens X x aktuellen Spread ueber/unter die H1-Kante (Testplan: 1, 2, 3)
input int    IbHalteSek       = 30;     // C: so viele Sekunden ununterbrochen jenseits der Kante (Testplan: 30, 120, 300)
input int    IbTeilSek        = 450;    // D: Pruefung einmal je M15-Kerze ab X s nach Kerzenbeginn (7,5 min)
"""

FUNKTIONEN = """// ---- Patch Intrabar: Einstieg des H1-Moduls innerhalb der laufenden M15-Kerze (EntryMode 1-3)
datetime ibH1[MAXSYM];                 // H1-Kerze, auf die sich der Zustand bezieht (neue Stunde = neue Kanten)
datetime ibSeit[MAXSYM];               // C: seit wann ununterbrochen jenseits (0 = nicht jenseits)
int      ibDir[MAXSYM];                // C: Richtung des laufenden Durchstosses
datetime ibDBar[MAXSYM];               // D: M15-Kerze, die schon geprueft wurde

double IbVolRelTeil(string s, int len, datetime bt, datetime now)
  {
   if(len<2) return(1.0);
   long v0[];
   if(CopyTickVolume(s, PERIOD_M15, 0, 1, v0) < 1) return(-1.0);
   long v[]; ArraySetAsSeries(v, true);
   int got = CopyTickVolume(s, PERIOD_M15, 1, len, v);
   if(got < len) return(-1.0);
   double sum=0.0;
   for(int i=0;i<got;i++) sum += (double)v[i];
   if(sum<=0.0) return(-1.0);
   double el = (double)(now - bt);
   if(el < 1.0) el = 1.0;
   return(((double)v0[0]*PeriodSeconds(PERIOD_M15)/el) / (sum/got));
  }

void IntrabarPruefen(int k, bool dayLocked)
  {
   string s = S[k].sym;
   datetime now = TimeCurrent();
   datetime bt = iTime(s, PERIOD_M15, 0);
   datetime ht = iTime(s, PERIOD_H1, 1);
   if(bt<=0 || ht<=0) return;
   if(ibH1[k] != ht) { ibH1[k] = ht; ibSeit[k] = 0; ibDir[k] = 0; }
   long dnow = PropDayIndex(now);
   if((datetime)dnow != S[k].curDay) { S[k].curDay=(datetime)dnow; S[k].tradesToday=0; }
   ulong tk = 0;
   if(HavePosition(k, tk)) return;
   if(dayLocked) return;
   if(kMode != 0) return;
   if(!DbAktiv) return;
   if(SerienPause()) return;
   if(WeAktiv && W[k].aktiv) return;
   if(WeAktiv && KurzVorSchluss(now)) return;
   if(NewsFenster(now)) return;
   if(S[k].tradesToday >= MaxTradesDay) return;
   if(LossesToday(k, dnow) >= MaxLossDay) return;
   if(!MQLInfoInteger(MQL_TESTER) && kBereitAb > 0 && now < kBereitAb) return;
   double nyH = NYHour(now);
   if(nyH < SessStartNY || nyH >= SessEndNY) return;
   double h1 = iHigh(s, PERIOD_H1, 1);
   double l1 = iLow (s, PERIOD_H1, 1);
   if(h1<=0.0 || l1<=0.0) return;
   double bid = SymbolInfoDouble(s, SYMBOL_BID);
   double ask = SymbolInfoDouble(s, SYMBOL_ASK);
   if(bid<=0.0 || ask<=0.0) return;
   double spr = ask - bid;
   int d = 0;
   if(EntryMode == 1 || EntryMode == 2)
     {
      int dj = (bid >= h1 + IbSpreadX*spr) ? 1 : ((bid <= l1 - IbSpreadX*spr) ? -1 : 0);
      if(EntryMode == 1) d = dj;
      else
        {
         if(dj == 0 || dj != ibDir[k]) { ibDir[k] = dj; ibSeit[k] = (dj != 0 ? now : 0); }
         if(dj != 0 && ibSeit[k] > 0 && now - ibSeit[k] >= IbHalteSek) d = dj;
        }
     }
   else if(EntryMode == 3)
     {
      if(ibDBar[k] == bt || now - bt < IbTeilSek) return;
      ibDBar[k] = bt;                                                  // genau eine Pruefung je Kerze
      double h0 = iHigh(s, PERIOD_M15, 0), l0 = iLow(s, PERIOD_M15, 0);
      double rg = h0 - l0;
      double cp = (rg > 0.0 ? (bid - l0)/rg : 0.5);
      double cm = S[k].clsMin;
      if(bid > h1 && (!UseCls || cp >= cm)) d = 1;
      else if(bid < l1 && (!UseCls || (1.0 - cp) >= cm)) d = -1;
      if(d != 0 && UseVolume)
        {
         double vr = IbVolRelTeil(s, VolLen, bt, now);
         if(vr < 0.0 || vr < VolMin) d = 0;
        }
     }
   if(d == 0) return;
   if(d < 0 && !S[k].allowShort) return;
   double emaBuf[]; if(CopyBuffer(S[k].hEma, 0, 1, 1, emaBuf)<1) return;
   double rsiBuf[]; if(CopyBuffer(S[k].hRsi, 0, 0, 1, rsiBuf)<1) return;
   double vw = UseVwap ? SessionVwap(s) : 0.0;
   if(UseVwap && vw<=0.0) return;
   bool ok = (d > 0) ? ((!UseTrend || bid > emaBuf[0]) && (!UseVwap || bid > vw) && (!UseRsi || rsiBuf[0] > RsiLvl))
                     : ((!UseTrend || bid < emaBuf[0]) && (!UseVwap || bid < vw) && (!UseRsi || rsiBuf[0] < RsiLvl));
   if(ok && UseMacd)
     {
      double mMain[], mSig[];
      if(CopyBuffer(S[k].hMacd, 0, 0, 1, mMain)<1) return;
      if(CopyBuffer(S[k].hMacd, 1, 0, 1, mSig )<1) return;
      double hist = mMain[0] - mSig[0];
      ok = (d > 0) ? (hist > 0.0) : (hist < 0.0);
     }
   if(!ok) return;
   int dg = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
   PrintFormat("DEADBAND4 %s: Intrabar-Signal Modus %d %s, Kante %.*f, Bid %.*f, Spread %.*f, %d s nach Kerzenbeginn",
               s, EntryMode, (d > 0 ? "LONG" : "SHORT"), dg, (d > 0 ? h1 : l1), dg, bid, dg, spr, (int)(now - bt));
   DbOrder(k, d > 0, nyH, bt, h1, l1);
  }

"""

AUFRUF = """   if(EntryMode != 0 && !inPos) IntrabarPruefen(k, dayLocked);          // Patch Intrabar: B/C/D in jedem Durchlauf
"""

A_AUS = ("   if(!inPos) WeAktivLoeschen(k);                      // 4.30: Merkmale der wiederaufgenommenen Position sind erledigt\n"
         "   if(dayLocked) return;\n",
         "   if(!inPos) WeAktivLoeschen(k);                      // 4.30: Merkmale der wiederaufgenommenen Position sind erledigt\n"
         "   if(dayLocked) return;\n"
         "   if(EntryMode != 0) return;                          // Patch Intrabar: Schluss-Einstieg nur in Modus 0\n")

ORDER_ALT = "   if(!HedgeFrei(k, sigL ? 1 : -1)) return;           // 4.90: GFT-Hedging-Verbot\n"
ORDER_NEU = """   DbOrder(k, sigL, nyH, bt, h1, l1);                  // Patch Intrabar: Order-Teil unveraendert ausgelagert
  }

// Patch Intrabar: Order-Teil des H1-Moduls (Text unveraendert aus HandleSymbol 8.10), gemeinsam fuer EntryMode 0-3
void DbOrder(int k, bool sigL, double nyH, datetime bt, double h1, double l1)
  {
   string s = S[k].sym;
   if(!HedgeFrei(k, sigL ? 1 : -1)) return;           // 4.90: GFT-Hedging-Verbot
"""

INIT_ANKER = """   PrintFormat("DEADBAND4: 4.90 GFT-Schutz: Hedging-Sperre %s"""
INIT_ZEILE = """   if(EntryMode < 0 || EntryMode > 3 || IbSpreadX <= 0.0 || IbHalteSek < 0 || IbTeilSek < 0 || IbTeilSek >= 900)
     { Print("DEADBAND4: Patch Intrabar: EntryMode 0-3, IbSpreadX > 0, IbHalteSek >= 0, IbTeilSek 0-899"); return(INIT_PARAMETERS_INCORRECT); }
   if(EntryMode != 0) PrintFormat("DEADBAND4: Patch Intrabar: EntryMode %d (%s), X %.1f Spreads, Haltezeit %d s, Teilbestaetigung ab %d s",
                                  EntryMode, (EntryMode == 1 ? "B Durchstoss" : (EntryMode == 2 ? "C Durchstoss + Haltezeit" : "D Teilbestaetigung")),
                                  IbSpreadX, IbHalteSek, IbTeilSek);
"""

EINGRIFFE = [
    ("input double KaufPuffer    = 2.0;\n", "nach", INPUTS),
    ("void HandleSymbol(int k, long today, bool dayLocked)\n", "vor", FUNKTIONEN),
    ("   // --- ab hier nur einmal je neuer M15-Kerze ----\n", "vor", AUFRUF),
    (A_AUS[0], "ersetze", A_AUS[1]),
    (ORDER_ALT, "ersetze", ORDER_NEU),
    (INIT_ANKER, "vor", INIT_ZEILE),
]

if __name__ == "__main__":
    aus = os.path.join(RESEARCH, "patch_intrabar.mq5")
    PB.bauen(EINGRIFFE, aus, os.path.join(RESEARCH, "patch_intrabar.diff"), KOPF)
    print("geschrieben:", aus)
