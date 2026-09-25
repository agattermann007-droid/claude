//+------------------------------------------------------------------+
//|  RSI21 EK (Eigenkapital) - Build 1.00, 25.09.2026                |
//|  RSI21 Continuation aus DEADBAND LIVE 4 Build 6.60, als eigene   |
//|  Strategie fuer EIGENES Kapital: keine Prop-Firmen-Regeln (kein  |
//|  Boden, keine Tages-/Floating-Grenze, keine gueltigen Tage, keine|
//|  Auszahlungen, keine News-, Hedging- oder 130-s-Regel, kein      |
//|  Wochenend-Schluss, keine Budgets, keine Pufferkurve, kein       |
//|  Serien-Stopp). Groesse in % der Equity (Zinseszins), begrenzt   |
//|  nur durch die Margin des Brokers.                               |
//|                                                                  |
//|  BUILD 1.00 - AUF RENDITE OPTIMIERT (Replikat RSI21_EK/, Bericht |
//|  RSI21_EK_Bericht.md). Signale wie 6.60, geaendert nur:          |
//|   1) jedes Signal wird gehandelt (FolgeMin 0; 6.60: nur Folge-   |
//|      signale), Gold nur M15 (6.60: M15 + M30),                   |
//|   2) kein Einstand (6.60: Stop auf Einstand ab 1 R - fuer die    |
//|      gueltigen Tage der Prop-Firma, kostet Rendite),             |
//|   3) bis 5 Positionen je Symbol in Richtung der ersten (6.60: 2),|
//|      keine Einstiege mehr nach 1 Verlust am Tag je Symbol,       |
//|   4) Gewichte M15 1,5 / M30 1,0 / H1 0,5 (6.60: 1,25/1,0/0,75),  |
//|   5) Risiko 1,0 % der Equity je Trade x Gewicht (x0,7 Gold).     |
//|  Ziele 2,2 R (NAS) / 2,64 R (Gold), Stop 2 ATR und Zeit-Ausstieg |
//|  1152 M5-Kerzen wie 6.60.                                        |
//|  Replikat 2006-26 (Gold/NAS M5, breite Spreads, Zins-Swap, Hebel |
//|  1:20), bei gleicher Schwankung (25 % Vol., 16 Stoerungen):      |
//|  CAGR 6.60 -> EK 30,9 -> 45,4 %, Sharpe 1,10 -> 1,39, besser in  |
//|  2006-16, 2017-21 und 2022-26. Bei gleichem groessten Rueckgang  |
//|  (40 %): 33,7 -> 61,4 % CAGR. Walk-Forward: die Bausteine, mit   |
//|  2006-21 gewaehlt, verbesserten 2022-26 in 16 von 16 Stoerungen. |
//|  Mit 1,0 % Risiko: CAGR 2006-26 60 %, groesster Rueckgang 38 %   |
//|  (2006-16: 24 % / 38 %, 2017-21: 108 % / 18 %, 2022-26: 122 % /  |
//|  28 %), ~106 Trades je Jahr. Warum 1,0 %: bei 20 % weniger       |
//|  Gewinnern hat 2006-16 hier die hoechste Rendite; mehr Risiko    |
//|  erhoeht nur den Rueckgang (2,0 %: 57 %, unter Stress 69 %).     |
//|  Gegengelesen (Review, alle Befunde umgesetzt); NICHT kompiliert,|
//|  nicht im Strategietester, nicht auf Demo geprueft (Pflicht).    |
//|                                                                  |
//|  Betrieb: zuletzt verarbeitete Kerze je Zeitebene dauerhaft      |
//|  gespeichert, Einstieg nur bis 2 min nach Kerzenbeginn (kein     |
//|  Doppel-Einstieg nach Neustart), Sperre gegen eine zweite        |
//|  Instanz mit derselben MagicBase, nur Hedging-Konten, Schliess-  |
//|  und Aenderungsversuche gedrosselt, Warnung, wenn Historie fuer  |
//|  Regime oder Divergenz fehlt (dann keine Signale).               |
//|                                                                  |
//|  Signal (unveraendert wie 6.60, Schwellen als Eingaben):         |
//|   Long, wenn RSI(21) der zuletzt geschlossenen Kerze > Oben      |
//|   (Short < Unten) auf M15/M30/H1, Kerzenbeginn im NY-Zeitfenster,|
//|   Bestaetigung RSI(21) des anderen Symbols (gleiche Zeitebene)   |
//|   > KreuzSchwelle (< 100 - X); Gold alternativ Vortagesschluss   |
//|   ueber (unter) SMA200 und SMA100. Shorts nur unter SMA200 oder  |
//|   SMA100, NAS-Longs nur ueber SMA200, kein Einstieg gegen eine   |
//|   bestaetigte H4-RSI-Divergenz. Mit FolgeMin > 0 nur Folge-      |
//|   signale (frueheres Signal gleicher Richtung hoechstens FolgeMin|
//|   alt). Stop StopATR x ATR(14) der Signal-Zeitebene.             |
//|  Tagesregime aus H1-Kerzen je Handelstag 17:00-17:00 NY (damit   |
//|  unabhaengig von der Tagesgrenze des Servers).                   |
//+------------------------------------------------------------------+
#property copyright   "RSI21 EK"
#property version     "1.00"
#property description "RSI21 Continuation (aus DEADBAND 6.60) fuer eigenes Kapital: ohne Prop-Regeln, auf Rendite optimiert"

#include <Trade/Trade.mqh>

#define NS    2            // Symbole: 0 = Gold, 1 = NAS100
#define NT    3            // Zeitebenen: 0 = M15, 1 = M30, 2 = H1
#define MAXP  5            // Plaetze je Symbol
#define GVP   "RSI21EK_"   // Praefix der Terminal-Globalvariablen

input group             "=== Symbole und Zeit ==="
input string GoldSymbol     = "XAUUSD";   // Gold beim Broker (exakter Name im Market Watch)
input string NasSymbol      = "NAS100";   // Nasdaq-100-CFD beim Broker (z. B. NAS100, USTEC, US100)
input bool   AutoNYOffset   = true;       // NY-Versatz aus Server- und GMT-Zeit bestimmen (im Tester gilt NYOffsetHours)
input int    NYOffsetHours  = 7;          // Serverzeit minus X Stunden = New-York-Zeit (viele MT5-Broker: 7)
input long   MagicBase      = 2121000;    // Magic = MagicBase + 10 x Symbol (0 Gold, 1 NAS) + Platz (0..4)

input group             "=== Groesse (Zinseszins) ==="
input double RiskPct        = 1.0;        // Risiko je Trade in % der Equity (x Gewicht der Zeitebene, x Gold-Faktor); 1,0 = robuster Kelly-Punkt (Bericht Abschnitt 6)
input bool   RisikoVomSaldo = false;      // true = % vom Saldo statt von der Equity
input double GewichtM15     = 1.5;        // Gewicht der Zeitebenen (Risiko = RiskPct x Gewicht; 6.60: 1,25 / 1,0 / 0,75)
input double GewichtM30     = 1.0;
input double GewichtH1      = 0.5;
input double GoldFaktor     = 0.70;       // Risiko-Faktor fuer Gold (Risikoparitaet RSI21 v3.4; bei gleichem Rueckgang besser als 0,85-1,6)
input double MarginMaxPct   = 90.0;       // alle Positionen zusammen hoechstens X % der Equity als Margin (neue Position sonst kleiner)
input double MaxLotsJePos   = 0.0;        // Obergrenze je Position in Lots (0 = Broker-Maximum)
input double MinLotToleranz = 2.0;        // Signal auslassen, wenn schon das Mindestlot mehr als X-mal das Soll-Risiko traegt

input group             "=== Signal (RSI21 Continuation) ==="
input int    RsiLen         = 21;         // RSI-Laenge (Wilder)
input double Oben           = 75.0;       // Long, wenn RSI der zuletzt geschlossenen Kerze > X
input double Unten          = 25.0;       // Short, wenn RSI < X
input bool   Longs          = true;
input bool   Shorts         = true;
input bool   KreuzAn        = true;       // Bestaetigung durch das andere Symbol (gleiche Zeitebene)
input double KreuzSchwelle  = 55.0;       // RSI des anderen Symbols > X (Long) bzw. < 100 - X (Short)
input double AbNY           = 9.5;        // Signal-Kerzen ab dieser NY-Stunde (Beginn der neuen Kerze; 9.5 = 9:30)
input double NasBisNY       = 13.0;       // NAS: Signal-Kerzen bis (NY-Stunde, exklusiv; 24 = bis Mitternacht)
input double GoldBisNY      = 17.0;       // Gold: Signal-Kerzen bis (NY-Stunde)
input bool   NasM15         = true;       // Zeitebenen je Symbol
input bool   NasM30         = true;
input bool   NasH1          = true;
input bool   GoldM15        = true;
input bool   GoldM30        = false;      // EK 1.00: Gold nur M15 (6.60: M15 + M30)
input bool   GoldH1         = false;
input int    MaLang         = 200;        // Tages-SMA (Handelstage 17:00-17:00 NY) fuer Regime, NAS-Longs, Gold-Tor
input int    MaSchnell      = 100;        // Tages-SMA schnell fuer Short-Regime und Gold-Tor
input bool   ShortRegime    = true;       // Shorts nur, wenn Vortagesschluss unter SMA lang ODER schnell
input bool   NasLongRegime  = true;       // NAS-Longs nur, wenn Vortagesschluss ueber SMA lang
input bool   GoldTor        = true;       // Gold auch ohne Bestaetigung, wenn Vortagesschluss ueber (unter) beiden SMA
input bool   DivH4          = true;       // kein Einstieg gegen eine bestaetigte H4-RSI-Divergenz (UTC-H4 aus H1)
input int    DivRadius      = 2;
input double DivAbstand     = 2.0;
input int    DivHistoryH1   = 6000;
input int    FolgeMin       = 0;          // 0 = jedes Signal handeln (EK 1.00); > 0 = nur Folgesignale: frueheres Signal gleicher Richtung hoechstens X min alt (6.60: 240)
input double ErstesSignalFaktor = 0.0;    // nur mit FolgeMin > 0: Groesse fuer das erste Signal einer Bewegung (0 = nur merken, nicht handeln)
input double StopATR        = 2.0;        // Stop in ATR(14) der Signal-Zeitebene (= 1 R)

input group             "=== Ausstieg ==="
input double ZielNasR       = 2.2;        // Ziel NAS in R (0 = kein Ziel)
input double ZielGoldR      = 2.64;       // Ziel Gold in R (0 = kein Ziel)
input double EinstandAbR    = 0.0;        // Stop auf Einstand + EinstandPlusR, sobald der Kurs X R im Plus war (0 = aus; EK 1.00 aus, 6.60: 1,0)
input double EinstandPlusR  = 0.05;
input double NachzugAbR     = 0.0;        // Stop-Nachzug, sobald der beste Kurs X R im Plus war (0 = aus) ...
input double NachzugAbstandR = 0.0;       // ... im Abstand Y R hinter dem besten Kurs
input double TeilAbR        = 0.0;        // Teilgewinn bei X R (0 = aus) ...
input double TeilAnteil     = 0.0;        // ... Anteil der Position (0,1-0,9)
input int    ZeitExitM5     = 1152;       // Zeit-Ausstieg nach X M5-Kerzen seit der Einstiegskerze (0 = aus)
input double ZeitExitTage   = 8.0;        // ... oder nach X Kalendertagen (0 = aus)

input group             "=== Plaetze, Tag, Wochenende ==="
input int    Plaetze        = 5;          // Positionen je Symbol (weitere nur in Richtung der ersten), 1-5 (6.60: 2)
input int    MaxVerlusteTag = 1;          // keine Einstiege mehr nach X Verlust-Trades am Tag je Symbol (0 = aus; 6.60: 2)
input double WeSchlussNY    = 0.0;        // Freitag ab X NY alle Positionen schliessen (0 = ueber das Wochenende halten)

input group             "=== Betrieb ==="
input int    AbweichungPkt  = 50;         // erlaubte Abweichung beim Einstieg in Punkten
input bool   PushMeldungen  = false;      // Push-Meldung bei Einstieg, Ausstieg und Fehlern

//--- Zustand (wird in OnInit vollstaendig zurueckgesetzt: bei Re-Init behalten Globale sonst ihre Werte)
CTrade   trade;
string   gSym[NS];
int      hRsi[NS][NT], hAtr[NS][NT];
datetime lastBar[NS][NT];             // zuletzt verarbeitete Kerze je Zeitebene (dauerhaft in Globalvariablen)
datetime lastSig[NS][2];              // Kerzenzeit des letzten gueltigen Signals je Richtung ([0] long, [1] short)
bool     geladen[NS];                 // Kerzen und Signal-Gedaechtnis aus den Globalvariablen geladen
bool     tfOn[NS][NT];
double   wTf[NT];
int      nyOff = 7;
bool     offGemessen = false;         // NY-Versatz schon einmal mit Verbindung gemessen
int      offKand = -99;               // abweichende Messung, die noch bestaetigt werden muss
datetime offLokal = 0;                // Ortszeit der letzten Messung
long     regTag[NS];                  // Handelstag, fuer den das Regime gerechnet wurde (-1 = neu rechnen)
bool     regOk[NS];
double   regC[NS], regMaL[NS], regMaS[NS];
datetime divBucket[NS];
int      divDir[NS];
bool     divGut[NS];
string   letztesSignal[NS];
datetime wartet[NS];                  // seit wann auf nachgerechnete Indikatoren gewartet wird (0 = nicht)
datetime warnZeit[NS][5];             // letzte Warnung je Art: 0 Regime, 1 Divergenz, 2 Indikatoren, 3 Handel, 4 NY-Versatz
datetime versuchZu[NS][MAXP];         // letzter Schliessversuch je Platz (hoechstens alle 30 s)
datetime versuchSl[NS][MAXP];         // letzte Stop-Aenderung / Teilschluss je Platz (hoechstens alle 5 s)
datetime startLokal = 0, anzLokal = 0, aufLokal = 0;
string   gLock = "";                  // Sperre gegen eine zweite Instanz (temporaere Globalvariable)

//+------------------------------------------------------------------+
//| Zeit                                                             |
//+------------------------------------------------------------------+
ENUM_TIMEFRAMES TfOf(const int t) { return (t == 0 ? PERIOD_M15 : (t == 1 ? PERIOD_M30 : PERIOD_H1)); }
int    TfMin(const int t) { return (t == 0 ? 15 : (t == 1 ? 30 : 60)); }
double NYHour(const datetime t) { MqlDateTime st; TimeToStruct(t - nyOff*3600, st); return st.hour + st.min/60.0; }
int    NYWeekday(const datetime t) { MqlDateTime st; TimeToStruct(t - nyOff*3600, st); return st.day_of_week; }
// Handelstag 17:00 NY bis 17:00 NY (bei Serverzeit = NY + 7 h genau der Servertag)
long   TagIndex(const datetime t) { return (long)MathFloor((double)((long)t - (long)(nyOff - 7)*3600) / 86400.0); }
datetime TagBeginn(const long idx) { return (datetime)(idx*86400 + (long)(nyOff - 7)*3600); }

// US-Sommerzeit: zweiter Sonntag im Maerz 2:00 bis erster Sonntag im November 2:00 (Ortszeit), gmt in UTC
bool UsDst(const datetime gmt)
  {
   MqlDateTime st; TimeToStruct(gmt, st);
   MqlDateTime m; ZeroMemory(m); m.year = st.year; m.mon = 3; m.day = 1;
   datetime mar1 = StructToTime(m); TimeToStruct(mar1, m);
   int secondSun = 1 + ((7 - m.day_of_week) % 7) + 7;
   MqlDateTime n; ZeroMemory(n); n.year = st.year; n.mon = 11; n.day = 1;
   datetime nov1 = StructToTime(n); TimeToStruct(nov1, n);
   int firstSun = 1 + ((7 - n.day_of_week) % 7);
   m.day = secondSun; m.hour = 7; m.min = 0; m.sec = 0;               // 2:00 EST = 7:00 UTC
   n.day = firstSun;  n.hour = 6; n.min = 0; n.sec = 0;               // 2:00 EDT = 6:00 UTC
   return (gmt >= StructToTime(m) && gmt < StructToTime(n));
  }

// Serverzeit -> UTC (fuer die H4-Buckets der Divergenz; US-Sommerzeit aus dem NY-Datum wie RSI21 v3.4)
int SonntagImMonat(const int jahr, const int monat, const int nr)
  {
   MqlDateTime d; ZeroMemory(d); d.year = jahr; d.mon = monat; d.day = 1;
   datetime first = StructToTime(d); TimeToStruct(first, d);
   return 1 + (7 - d.day_of_week) % 7 + 7*(nr - 1);
  }
datetime SrvZuUTC(const datetime srv)
  {
   datetime ny = (datetime)((long)srv - (long)nyOff*3600);
   MqlDateTime d; TimeToStruct(ny, d);
   bool dst = (d.mon > 3 && d.mon < 11);
   if(d.mon == 3)  { int st = SonntagImMonat(d.year, 3, 2);  dst = (d.day > st || (d.day == st && d.hour >= 2)); }
   if(d.mon == 11) { int en = SonntagImMonat(d.year, 11, 1); dst = (d.day < en || (d.day == en && d.hour < 2)); }
   return (datetime)((long)ny + (dst ? 4 : 5)*3600);
  }

//+------------------------------------------------------------------+
//| Meldungen, Globalvariablen                                       |
//+------------------------------------------------------------------+
// Warnung je Symbol und Art hoechstens einmal je Stunde (Journal und Push)
void Warnung(const int s, const int art, const string text)
  {
   datetime lok = TimeLocal();
   if(warnZeit[s][art] > 0 && lok - warnZeit[s][art] < 3600) return;
   warnZeit[s][art] = lok;
   Print("RSI21EK ", text);
   if(PushMeldungen) SendNotification("RSI21EK " + text);
  }

// Praefix mit Login und MagicBase: Konten und Instanzen im selben Terminal bleiben getrennt
string Pfx() { return GVP + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + "_" + IntegerToString(MagicBase) + "_"; }
string SymKey(const int s) { return (StringLen(gSym[s]) <= 16 ? gSym[s] : "S" + IntegerToString(s)); }
string PosGv(const long pid, const string was) { return Pfx() + "P" + IntegerToString(pid) + "_" + was; }
string SigGv(const int s, const int di) { return Pfx() + "SIG_" + SymKey(s) + (di == 0 ? "_L" : "_S"); }
string BarGv(const int s, const int t) { return Pfx() + "BAR_" + SymKey(s) + "_" + IntegerToString(t); }
void   Sichern() { if(!MQLInfoInteger(MQL_TESTER)) GlobalVariablesFlush(); }        // sofort auf Platte (Absturz, Stromausfall)

// Kerzen und Signal-Gedaechtnis je Symbol laden (erst mit bekanntem Konto, das Praefix enthaelt den Login)
bool LadeZustand(const int s)
  {
   if(AccountInfoInteger(ACCOUNT_LOGIN) == 0) return false;
   for(int t=0;t<NT;t++)
     {
      string g = BarGv(s, t);
      lastBar[s][t] = GlobalVariableCheck(g) ? (datetime)(long)GlobalVariableGet(g) : 0;
     }
   for(int di=0;di<2;di++)
     {
      lastSig[s][di] = 0;
      string g = SigGv(s, di);
      if(GlobalVariableCheck(g))
        {
         datetime v = (datetime)(long)GlobalVariableGet(g);
         if(v > 0 && TimeCurrent() - v <= 86400) lastSig[s][di] = v;
        }
     }
   geladen[s] = true;
   return true;
  }

//+------------------------------------------------------------------+
//| NY-Versatz                                                       |
//+------------------------------------------------------------------+
// aus Server- und GMT-Zeit; false = keine Verbindung oder unplausibel
bool OffsetMessen(int &off)
  {
   if(!TerminalInfoInteger(TERMINAL_CONNECTED)) return false;
   datetime gmt = TimeGMT(), srv = TimeTradeServer();
   if(gmt <= 0 || srv <= 0) return false;
   int srvOff = (int)MathRound((double)(srv - gmt) / 3600.0);
   int m = srvOff - (UsDst(gmt) ? -4 : -5);
   if(m < -12 || m > 14)
     {
      Warnung(0, 4, StringFormat("automatischer NY-Versatz %d unplausibel (Server %+d h GMT) - bleibe bei %d h", m, srvOff, nyOff));
      return false;
     }
   off = m;
   return true;
  }

void OffsetSetzen(const int off, const string grund)
  {
   PrintFormat("RSI21EK: NY-Versatz %d -> %d h (%s)%s", nyOff, off, grund,
               (off != NYOffsetHours ? " - weicht von NYOffsetHours ab: PC-Uhr, Zeitzone und Broker-Serverzeit pruefen" : ""));
   nyOff = off;
   for(int s=0;s<NS;s++) { regTag[s] = -1; regOk[s] = false; divBucket[s] = 0; }   // Tagesgrenzen und H4-Buckets neu
  }

// erste Messung mit Verbindung sofort, danach alle 600 s; ein Wechsel erst nach zwei gleichen Messungen
void OffsetPflegen()
  {
   if(MQLInfoInteger(MQL_TESTER) || !AutoNYOffset) return;
   datetime lok = TimeLocal();
   if(offGemessen && lok - offLokal < 600) return;
   int m = 0;
   if(!OffsetMessen(m)) return;
   offLokal = lok;
   if(!offGemessen)
     {
      offGemessen = true;
      if(m != nyOff) OffsetSetzen(m, "erste Messung");
      return;
     }
   if(m == nyOff) { offKand = -99; return; }
   if(m != offKand) { offKand = m; return; }
   OffsetSetzen(m, "zweimal gemessen");
   offKand = -99;
  }

//+------------------------------------------------------------------+
//| Hilfsfunktionen                                                  |
//+------------------------------------------------------------------+
double MoneyPerPricePerLot(const string s)
  {
   double ts = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE), tv = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE);
   if(ts > 0.0 && tv > 0.0) return tv/ts;
   double cs = SymbolInfoDouble(s, SYMBOL_TRADE_CONTRACT_SIZE);
   return (cs > 0.0 ? cs : 1.0);
  }

int LotStellen(const double stp)
  {
   int d = 0; double x = stp;
   while(d < 8 && MathAbs(x - MathRound(x)) > 1e-9) { x *= 10.0; d++; }
   return d;
  }

// Preis auf die Tick-Groesse des Symbols (Index-CFDs: 0,25 / 0,5 ...)
double AufTick(const string sym, const double px)
  {
   double ts = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_SIZE);
   int dg = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
   return NormalizeDouble(ts > 0.0 ? MathRound(px/ts)*ts : px, dg);
  }

long MagicOf(const int s, const int q) { return MagicBase + 10*s + q; }
bool UnsereMagic(const long mg, int &s, int &q)
  {
   long o = mg - MagicBase;
   if(o < 0 || o >= 10*NS) return false;
   s = (int)(o / 10); q = (int)(o % 10);
   return (q < MAXP);
  }

// Handel moeglich? Algo-Handel erlaubt, Symbol handelbar (Eroeffnen: in dieser Richtung), frische Kurse (Markt offen)
bool HandelMoeglich(const int s, const bool eroeffnen, const int dir, string &grund)
  {
   string sym = gSym[s];
   long tm = SymbolInfoInteger(sym, SYMBOL_TRADE_MODE);
   if(tm == SYMBOL_TRADE_MODE_DISABLED) { grund = "Symbol fuer den Handel gesperrt"; return false; }
   if(eroeffnen && !(tm == SYMBOL_TRADE_MODE_FULL || (dir > 0 && tm == SYMBOL_TRADE_MODE_LONGONLY) || (dir < 0 && tm == SYMBOL_TRADE_MODE_SHORTONLY)))
     { grund = "Symbol nur eingeschraenkt handelbar (Handelsmodus des Brokers)"; return false; }
   if(MQLInfoInteger(MQL_TESTER)) return true;
   if(!TerminalInfoInteger(TERMINAL_CONNECTED)) { grund = "keine Verbindung"; return false; }
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !MQLInfoInteger(MQL_TRADE_ALLOWED)) { grund = "Algo-Handel ausgeschaltet"; return false; }
   if(TimeCurrent() - (datetime)SymbolInfoInteger(sym, SYMBOL_TIME) > 60) { grund = "keine frischen Kurse (Markt geschlossen?)"; return false; }
   return true;
  }

// Position eines Platzes (Symbol + Magic); Richtung +1/-1
bool PlatzPosition(const int s, const int q, ulong &tk, int &dir)
  {
   long mg = MagicOf(s, q);
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong t = PositionGetTicket(i);
      if(t == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == gSym[s] && PositionGetInteger(POSITION_MAGIC) == mg)
        {
         tk = t; dir = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1);
         return true;
        }
     }
   return false;
  }

// Platzwahl wie im Replikat: erster Platz frei -> erster; sonst naechster freier Platz, wenn der erste in dieselbe Richtung laeuft.
// neuP/dirNeu: in diesem Durchlauf eroeffnet (die Positionsliste kann kurz nachhinken)
int PlatzWahl(const int s, const int dir, const bool &neuP[], const int dirNeu)
  {
   ulong tk = 0; int dA = 0;
   if(!PlatzPosition(s, 0, tk, dA))
     {
      if(!neuP[0]) return 0;
      dA = dirNeu;
     }
   if(dA != dir) return -1;
   int np = (int)MathMax(1, MathMin(MAXP, Plaetze));
   for(int q=1;q<np;q++)
     {
      if(neuP[q]) continue;
      ulong t2 = 0; int d2 = 0;
      if(!PlatzPosition(s, q, t2, d2)) return q;
     }
   return -1;
  }

// urspruenglicher Stop-Abstand (1 R): gemerkt beim Einstieg, sonst aus der Eroeffnungs-Order (nur dieser Wert wird gespeichert).
// Aufrufer waehlt die Position danach neu (HistorySelectByPosition)
double PositionR(const ulong tk)
  {
   if(!PositionSelectByTicket(tk)) return 0.0;
   long pid = PositionGetInteger(POSITION_IDENTIFIER);
   string g = PosGv(pid, "R");
   if(GlobalVariableCheck(g)) { double r = GlobalVariableGet(g); if(r > 0.0) return r; }
   int d = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1);
   double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL);
   double rd = 0.0;
   bool ausHist = false;
   if(HistorySelectByPosition(pid))
     {
      for(int i=0;i<HistoryDealsTotal();i++)
        {
         ulong dt = HistoryDealGetTicket(i);
         if(dt == 0 || HistoryDealGetInteger(dt, DEAL_ENTRY) != DEAL_ENTRY_IN) continue;
         ulong ot = (ulong)HistoryDealGetInteger(dt, DEAL_ORDER);
         double osl = (ot > 0 && HistoryOrderSelect(ot)) ? HistoryOrderGetDouble(ot, ORDER_SL) : 0.0;
         double px = HistoryDealGetDouble(dt, DEAL_PRICE);
         if(osl > 0.0 && px > 0.0 && (px - osl)*d > 0.0) { rd = (px - osl)*d; ausHist = true; }
         break;
        }
     }
   if(ausHist) { GlobalVariableSet(g, rd); Sichern(); return rd; }
   return (sl > 0.0 && (op - sl)*d > 0.0) ? (op - sl)*d : 0.0;      // Ersatz nur fuer diesen Durchlauf (Stop auf Verlustseite)
  }

// erst ab der M5-Kerze nach der Einstiegskerze (wie im Replikat)
bool NachEinstiegsKerze(const string s, const datetime tOpen)
  {
   int ps = PeriodSeconds(PERIOD_M5);
   datetime b0 = iTime(s, PERIOD_M5, 0);
   datetime naechste = (datetime)((long)tOpen - (long)tOpen % ps + ps);
   return (b0 > 0 && b0 >= naechste);
  }

// bester Vorlauf in R ab der M5-Kerze nach dem Einstieg: Hoch (Long) bzw. Tief + Spread (Short) wie im Replikat.
// Beim ersten Aufruf aus der Historie, danach Globalvariable M + die letzten zwei Kerzen. -1e9 = Historie noch nicht da
double BesterVorlauf(const long pid, const string sym, const int d, const double op, const double rd, const datetime t0)
  {
   string g = PosGv(pid, "M");
   bool erst = !GlobalVariableCheck(g);
   double mfe = erst ? 0.0 : GlobalVariableGet(g);
   int ps = PeriodSeconds(PERIOD_M5);
   datetime ab = (datetime)((long)t0 - (long)t0 % ps + ps);
   MqlRates r[];
   int n = erst ? CopyRates(sym, PERIOD_M5, ab, TimeCurrent(), r) : CopyRates(sym, PERIOD_M5, 0, 2, r);
   if(erst && n <= 0) return -1e9;
   double pt = SymbolInfoDouble(sym, SYMBOL_POINT);
   for(int j=0;j<n;j++)
     {
      if(r[j].time < ab) continue;
      double f = (d > 0) ? (r[j].high - op)/rd : (op - (r[j].low + r[j].spread*pt))/rd;
      if(f > mfe) mfe = f;
     }
   return mfe;
  }

// Teilgewinn schon genommen? (Deal-Historie: ein Ausstiegs-Deal der Position; Aufrufer waehlt die Position danach neu)
bool TeilSchonZu(const long pid)
  {
   bool ja = false;
   if(HistorySelectByPosition(pid))
      for(int i=HistoryDealsTotal()-1;i>=0 && !ja;i--)
        {
         ulong dt = HistoryDealGetTicket(i);
         ja = (dt > 0 && HistoryDealGetInteger(dt, DEAL_ENTRY) == DEAL_ENTRY_OUT);
        }
   return ja;
  }

bool Schliesse(const int s, const ulong tk, const string grund)
  {
   if(!PositionSelectByTicket(tk)) return false;
   string sym = PositionGetString(POSITION_SYMBOL);
   double p = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
   trade.SetExpertMagicNumber((ulong)PositionGetInteger(POSITION_MAGIC));
   bool ok = trade.PositionClose(tk);
   uint rc = trade.ResultRetcode();
   if(ok && (rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_DONE_PARTIAL || rc == TRADE_RETCODE_PLACED))
     {
      PrintFormat("RSI21EK %s: %s - geschlossen, Ergebnis %.2f", sym, grund, p);
      if(PushMeldungen) SendNotification(StringFormat("RSI21EK %s: %s, %.2f", sym, grund, p));
      return true;
     }
   Warnung(s, 3, StringFormat("%s: Schliessen (%s) abgelehnt (%d %s) - neuer Versuch alle 30 s", sym, grund, rc, trade.ResultRetcodeDescription()));
   return false;
  }

// Verlust-Trades heute (Handelstag 17:00 NY) je Symbol; Verlust = Gewinn + Swap < 0 (wie Replikat, ohne Kommission).
// Von Hand geschlossene Positionen (Deal-Magic 0) zaehlen nicht.
int VerlusteHeute(const int s)
  {
   datetime von = TagBeginn(TagIndex(TimeCurrent()));
   if(!HistorySelect(von, TimeCurrent() + 60)) return 0;
   int n = 0;
   for(int i=0;i<HistoryDealsTotal();i++)
     {
      ulong dt = HistoryDealGetTicket(i);
      if(dt == 0) continue;
      long e = HistoryDealGetInteger(dt, DEAL_ENTRY);
      if(e != DEAL_ENTRY_OUT && e != DEAL_ENTRY_OUT_BY) continue;
      int ss = -1, qq = -1;
      if(!UnsereMagic(HistoryDealGetInteger(dt, DEAL_MAGIC), ss, qq) || ss != s) continue;
      if(HistoryDealGetString(dt, DEAL_SYMBOL) != gSym[s]) continue;
      if(HistoryDealGetDouble(dt, DEAL_PROFIT) + HistoryDealGetDouble(dt, DEAL_SWAP) < 0.0) n++;
     }
   return n;
  }

//+------------------------------------------------------------------+
//| Indikatorwerte zur Signalzeit                                    |
//+------------------------------------------------------------------+
// Index der letzten Kerze, die vor T begann (= zur Zeit T zuletzt geschlossene Kerze)
int BarVor(const string sym, const ENUM_TIMEFRAMES tf, const datetime T)
  {
   int sh = iBarShift(sym, tf, (datetime)((long)T - 1), false);
   if(sh < 0) return -1;
   datetime bt = iTime(sym, tf, sh);
   int guard = 0;
   while(bt > 0 && bt >= T && guard < 5) { sh++; bt = iTime(sym, tf, sh); guard++; }
   return (bt > 0 && bt < T) ? sh : -1;
  }

// Indikatorwert der zur Zeit T zuletzt geschlossenen Kerze, ueber die Kerzenzeit gelesen (nicht ueber den Index)
bool Wert(const int handle, const string sym, const int t, const datetime T, double &v)
  {
   ENUM_TIMEFRAMES tf = TfOf(t);
   int sh = BarVor(sym, tf, T);
   if(sh < 0) return false;
   datetime bt = iTime(sym, tf, sh);
   if(bt <= 0) return false;
   double b[];
   if(CopyBuffer(handle, 0, bt, 1, b) != 1) return false;
   if(b[0] == EMPTY_VALUE || !MathIsValidNumber(b[0])) return false;
   v = b[0];
   return true;
  }

// Tagesregime aus H1: Schlusskurse je Handelstag (17:00-17:00 NY) vor dem Handelstag der Signalzeit T; SMA lang/schnell.
// Gilt fuer den ganzen Handelstag nur mit voller Historie (sonst beim naechsten Mal neu laden)
bool Regime(const int s, const datetime T, int &regv, bool &shortOk, bool &gateL, bool &gateS)
  {
   long tag = TagIndex(T);
   if(!(regOk[s] && regTag[s] == tag))
     {
      regOk[s] = false;
      int nMa = (int)MathMax(MaLang, MaSchnell);
      int need = (nMa + 15)*25;
      MqlRates r[];
      ArraySetAsSeries(r, false);
      int got = CopyRates(gSym[s], PERIOD_H1, 0, need, r);
      if(got < 200)
        {
         Warnung(s, 0, StringFormat("%s: Tagesregime nicht berechenbar (%d H1-Kerzen) - KEINE Signale; Historie / Max. Balken im Chart pruefen", gSym[s], got));
         return false;
        }
      double cl[]; ArrayResize(cl, got);
      int n = 0; long lastD = -1;
      for(int i=0;i<got;i++)
        {
         long dI = TagIndex(r[i].time);
         if(dI >= tag) break;
         if(dI != lastD) { cl[n] = r[i].close; n++; lastD = dI; }
         else cl[n-1] = r[i].close;
        }
      if(n < 50)
        {
         Warnung(s, 0, StringFormat("%s: Tagesregime nicht berechenbar (%d Handelstage H1-Historie) - KEINE Signale", gSym[s], n));
         return false;
        }
      int nl = (int)MathMin(n, MaLang), nf = (int)MathMin(n, MaSchnell);
      double sl = 0.0, sf = 0.0;
      for(int i=n-nl;i<n;i++) sl += cl[i];
      for(int i=n-nf;i<n;i++) sf += cl[i];
      regC[s] = cl[n-1]; regMaL[s] = sl/nl; regMaS[s] = sf/nf; regOk[s] = true;
      regTag[s] = (n >= nMa ? tag : -1);
      if(n < nMa)
         Warnung(s, 0, StringFormat("%s: nur %d Handelstage H1-Historie (SMA %d/%d mit weniger Tagen) - Max. Balken im Chart erhoehen", gSym[s], n, MaLang, MaSchnell));
     }
   double c = regC[s], mL = regMaL[s], mS = regMaS[s];
   if(c <= 0.0 || mL <= 0.0 || mS <= 0.0) return false;
   shortOk = (c < mL || c < mS);
   gateL   = (c > mL && c > mS);
   gateS   = (c < mL && c < mS);
   regv    = (c > mL) ? 1 : -1;
   return true;
  }

// bestaetigte RSI-Divergenz auf UTC-H4 (aus H1 wie RSI21 v3.4 / DEADBAND 6.60), nur H4-Buckets vor dem Bucket der Signalzeit T:
// +1 bullisch, -1 baerisch, 0 keine/beide; false = nicht berechenbar (sperrt alle Signale, mit Warnung)
bool Divergenz(const int s, const datetime T, int &direction)
  {
   long sek = 14400;
   string sym = gSym[s];
   datetime current = (datetime)(((long)SrvZuUTC(T)/sek)*sek);
   if(divBucket[s] == current && current > 0) { direction = divDir[s]; return divGut[s]; }
   MqlRates rates[];
   ArraySetAsSeries(rates, false);
   int got = CopyRates(sym, PERIOD_H1, 0, DivHistoryH1, rates);
   if(got < 2000)
     {
      Warnung(s, 1, StringFormat("%s: H4-Divergenz nicht berechenbar (%d H1-Kerzen, noetig 2000) - KEINE Signale; Historie / Max. Balken im Chart pruefen", sym, got));
      return false;
     }
   double closes[]; ArrayResize(closes, got);
   int n = 0; datetime last = 0;
   for(int i=0;i<got;i++)
     {
      datetime utc = SrvZuUTC(rates[i].time);
      datetime bucket = (datetime)(((long)utc/sek)*sek);
      if(bucket >= current) continue;
      if(n == 0 || bucket != last) { closes[n] = rates[i].close; n++; last = bucket; }
      else closes[n-1] = rates[i].close;
     }
   if(n < 500)
     {
      Warnung(s, 1, StringFormat("%s: H4-Divergenz nicht berechenbar (%d H4-Kerzen, noetig 500) - KEINE Signale", sym, n));
      return false;
     }
   double rsi[]; ArrayResize(rsi, n); ArrayInitialize(rsi, 50.0);
   int period = RsiLen;
   double gain = 0.0, loss = 0.0;
   for(int i=1;i<=period;i++) { double delta = closes[i]-closes[i-1]; gain += MathMax(delta, 0.0); loss += MathMax(-delta, 0.0); }
   gain /= period; loss /= period;
   for(int i=period;i<n;i++)
     {
      if(i > period)
        {
         double delta = closes[i]-closes[i-1];
         gain = (gain*(period-1) + MathMax(delta, 0.0))/period;
         loss = (loss*(period-1) + MathMax(-delta, 0.0))/period;
        }
      rsi[i] = (loss == 0.0) ? (gain == 0.0 ? 50.0 : 100.0) : 100.0 - 100.0/(1.0 + gain/loss);
     }
   double high=0, prevHigh=0, highRsi=0, prevHighRsi=0, low=0, prevLow=0, lowRsi=0, prevLowRsi=0;
   int highs=0, lows=0, radius=DivRadius;
   for(int j=MathMax(radius, period); j+radius<n; j++)
     {
      bool isHigh=true, isLow=true;
      for(int q=j-radius;q<=j+radius;q++) { if(closes[q] > closes[j]) isHigh=false; if(closes[q] < closes[j]) isLow=false; }
      if(isHigh) { prevHigh=high; prevHighRsi=highRsi; high=closes[j]; highRsi=rsi[j]; highs++; }
      if(isLow)  { prevLow=low;   prevLowRsi=lowRsi;   low=closes[j];  lowRsi=rsi[j];  lows++; }
     }
   bool ok = (highs >= 2 && lows >= 2);
   bool bearish = ok && (high > prevHigh && highRsi < prevHighRsi - DivAbstand);
   bool bullish = ok && (low < prevLow && lowRsi > prevLowRsi + DivAbstand);
   direction = (bullish ? 1 : 0) - (bearish ? 1 : 0);
   divBucket[s] = current; divDir[s] = direction; divGut[s] = ok;
   return ok;
  }

//+------------------------------------------------------------------+
//| Einstieg                                                         |
//+------------------------------------------------------------------+
bool Einstieg(const int s, const int t, const int dir, const double rd, const double fak, const int q)
  {
   string sym = gSym[s];
   string was = StringFormat("%s M%d Platz %d", (dir > 0 ? "LONG" : "SHORT"), TfMin(t), q + 1);
   double mpp = MoneyPerPricePerLot(sym);
   double pt  = SymbolInfoDouble(sym, SYMBOL_POINT);
   long   stl = SymbolInfoInteger(sym, SYMBOL_TRADE_STOPS_LEVEL);
   if(rd <= 0.0 || mpp <= 0.0) { PrintFormat("RSI21EK %s: %s ausgelassen - Stop %.5f oder Geld je Preis-Einheit %.5f ungueltig", sym, was, rd, mpp); return false; }
   if(stl > 0 && rd < stl*pt*1.2) { PrintFormat("RSI21EK %s: %s ausgelassen - Stop %.5f unter dem Mindestabstand des Brokers (%d Punkte)", sym, was, rd, (int)stl); return false; }
   double w = wTf[t]*(s == 0 ? GoldFaktor : 1.0)*fak;
   double basis = RisikoVomSaldo ? AccountInfoDouble(ACCOUNT_BALANCE) : AccountInfoDouble(ACCOUNT_EQUITY);
   double risk = basis*RiskPct/100.0*w;
   if(risk <= 0.0) { PrintFormat("RSI21EK %s: %s ausgelassen - Risiko %.2f (Basis %.2f, Gewicht %.2f)", sym, was, risk, basis, w); return false; }
   double mnv = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN), mxv = SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX);
   double stp = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP);
   if(stp <= 0.0) stp = 0.01;
   if(mnv <= 0.0) mnv = stp;
   if(mnv*rd*mpp > risk*MinLotToleranz)
     {
      PrintFormat("RSI21EK %s: %s ausgelassen - Mindestlot %.2f traegt %.2f Risiko, Soll %.2f (Konto zu klein fuer diesen Stop)", sym, was, mnv, mnv*rd*mpp, risk);
      return false;
     }
   double lots = MathFloor(risk/(rd*mpp)/stp + 0.5)*stp;                 // kaufmaennisch gerundet (wie Replikat)
   if(lots < mnv) lots = mnv;
   if(MaxLotsJePos > 0.0 && lots > MaxLotsJePos) lots = MathFloor(MaxLotsJePos/stp + 1e-9)*stp;
   if(mxv > 0.0 && lots > mxv) lots = MathFloor(mxv/stp + 1e-9)*stp;
   // Volumen-Grenze des Brokers je Richtung (alle Positionen des Symbols)
   double lim = SymbolInfoDouble(sym, SYMBOL_VOLUME_LIMIT);
   if(lim > 0.0)
     {
      double offen = 0.0;
      for(int i=PositionsTotal()-1;i>=0;i--)
        {
         ulong pk = PositionGetTicket(i);
         if(pk == 0 || PositionGetString(POSITION_SYMBOL) != sym) continue;
         if((PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1) == dir) offen += PositionGetDouble(POSITION_VOLUME);
        }
      double rest = MathFloor((lim - offen)/stp + 1e-9)*stp;
      if(rest < mnv) { PrintFormat("RSI21EK %s: %s ausgelassen - Volumen-Grenze %.2f Lot je Richtung erreicht (offen %.2f)", sym, was, lim, offen); return false; }
      if(lots > rest) { PrintFormat("RSI21EK %s: Groesse wegen Volumen-Grenze %.2f -> %.2f Lot", sym, lots, rest); lots = rest; }
     }
   MqlTick tick;
   if(!SymbolInfoTick(sym, tick) || tick.ask <= 0.0 || tick.bid <= 0.0) { PrintFormat("RSI21EK %s: %s ausgelassen - kein Kurs", sym, was); return false; }
   double ent = (dir > 0 ? tick.ask : tick.bid);
   // Margin: alle Positionen zusammen hoechstens MarginMaxPct % der Equity - sonst kleiner
   ENUM_ORDER_TYPE ot = (dir > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
   double m1 = 0.0;
   if(!OrderCalcMargin(ot, sym, 1.0, ent, m1) || m1 <= 0.0)
     { PrintFormat("RSI21EK %s: %s ausgelassen - Margin nicht berechenbar (%d)", sym, was, GetLastError()); return false; }
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double frei = MathMin(eq*MarginMaxPct/100.0 - AccountInfoDouble(ACCOUNT_MARGIN), AccountInfoDouble(ACCOUNT_MARGIN_FREE));
   if(lots*m1 > frei)
     {
      double lmax = MathFloor(frei/m1/stp + 1e-9)*stp;
      if(lmax < mnv) { PrintFormat("RSI21EK %s: %s ausgelassen - Margin reicht nicht (frei %.2f, je Lot %.2f)", sym, was, frei, m1); return false; }
      PrintFormat("RSI21EK %s: Groesse wegen Margin %.2f -> %.2f Lot", sym, lots, lmax);
      lots = lmax;
     }
   for(int k=0;k<3;k++)                                                   // Gegenprobe mit dem Endvolumen (gestaffelte Margin)
     {
      double mE = 0.0;
      if(!OrderCalcMargin(ot, sym, lots, ent, mE) || mE <= frei) break;
      double l2 = MathFloor(lots*frei/mE/stp + 1e-9)*stp;
      if(l2 >= lots) l2 = lots - stp;
      if(l2 < mnv) { PrintFormat("RSI21EK %s: %s ausgelassen - Margin reicht nicht (frei %.2f, fuer %.2f Lot %.2f)", sym, was, frei, lots, mE); return false; }
      PrintFormat("RSI21EK %s: Groesse wegen Margin (gestaffelt) %.2f -> %.2f Lot", sym, lots, l2);
      lots = l2;
     }
   lots = NormalizeDouble(lots, LotStellen(stp));
   int dg = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
   double rr = (s == 0 ? ZielGoldR : ZielNasR);
   double minD = (stl > 0 ? stl*pt : 0.0);
   trade.SetExpertMagicNumber((ulong)MagicOf(s, q));
   trade.SetDeviationInPoints((ulong)AbweichungPkt);
   string kom = StringFormat("RSI21EK %s M%d P%d%s", (dir > 0 ? "L" : "S"), TfMin(t), q + 1, (fak < 1.0 ? " erst" : ""));
   uint rc = 0;
   double sl = 0.0, tp = 0.0;
   for(int nr=0;nr<2;nr++)                                                // einmal wiederholen bei Requote / neuem Kurs
     {
      if(nr > 0)
        {
         if(!SymbolInfoTick(sym, tick) || tick.ask <= 0.0 || tick.bid <= 0.0) break;
         ent = (dir > 0 ? tick.ask : tick.bid);
        }
      sl = AufTick(sym, ent - dir*rd);
      tp = (rr > 0.0 ? AufTick(sym, ent + dir*rr*rd) : 0.0);
      if((dir > 0 && (tick.bid - sl < minD || (tp > 0.0 && tp - tick.bid < minD))) || (dir < 0 && (sl - tick.ask < minD || (tp > 0.0 && tick.ask - tp < minD))))
        { PrintFormat("RSI21EK %s: %s ausgelassen - Stop oder Ziel naeher als der Mindestabstand des Brokers (%d Punkte)", sym, was, (int)stl); return false; }
      bool ok = (dir > 0) ? trade.Buy(lots, sym, 0.0, sl, tp, kom) : trade.Sell(lots, sym, 0.0, sl, tp, kom);
      rc = trade.ResultRetcode();
      if(ok && (rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_DONE_PARTIAL || rc == TRADE_RETCODE_PLACED))
        {
         long pid = (long)trade.ResultOrder();                               // Hedging-Konto: Positions-Kennung = Eroeffnungs-Order
         GlobalVariableSet(PosGv(pid, "R"), rd);
         GlobalVariableSet(PosGv(pid, "L"), lots);
         Sichern();
         PrintFormat("RSI21EK %s: Einstieg %s, %.2f Lot, Risiko %.2f (%.2f %% x %.2f), Stop %.*f, Ziel %s",
                     sym, was, lots, lots*rd*mpp, RiskPct, w, dg, sl, (tp > 0.0 ? DoubleToString(tp, dg) : "keins"));
         if(PushMeldungen) SendNotification(StringFormat("RSI21EK %s %s, %.2f Lot", sym, was, lots));
         return true;
        }
      if(!(rc == TRADE_RETCODE_REQUOTE || rc == TRADE_RETCODE_PRICE_CHANGED || rc == TRADE_RETCODE_PRICE_OFF)) break;
      PrintFormat("RSI21EK %s: %s - %d %s, zweiter Versuch mit neuem Kurs", sym, was, rc, trade.ResultRetcodeDescription());
     }
   PrintFormat("RSI21EK %s: Einstieg %s abgelehnt (%d %s) %.2f Lot, SL %.*f, TP %.*f", sym, was, rc, trade.ResultRetcodeDescription(), lots, dg, sl, dg, tp);
   if(PushMeldungen) SendNotification(StringFormat("RSI21EK %s: Einstieg %s abgelehnt (%d)", sym, was, rc));
   return false;
  }

//+------------------------------------------------------------------+
//| Signale je Symbol (bei neuer Kerze einer Zeitebene)              |
//+------------------------------------------------------------------+
// Indikatoren der Zeitebene nachgerechnet (nach einer neuen Kerze rechnet MT5 die Handles asynchron nach)
bool Bereit(const int s, const int t)
  {
   int nb = Bars(gSym[s], TfOf(t));
   if(!(nb > 0 && BarsCalculated(hRsi[s][t]) >= nb && BarsCalculated(hAtr[s][t]) >= nb)) return false;
   if(!KreuzAn) return true;
   int no = Bars(gSym[1-s], TfOf(t));                         // RSI des anderen Symbols (Bestaetigung)
   return (no > 0 && BarsCalculated(hRsi[1-s][t]) >= no);
  }

void Signale(const int s)
  {
   string sym = gSym[s];
   if(!geladen[s] && !LadeZustand(s)) return;
   datetime jetzt = TimeCurrent();
   bool neu[NT]; bool jede = false;
   datetime nb[NT];
   for(int t=0;t<NT;t++)
     {
      neu[t] = false; nb[t] = 0;
      datetime bt = iTime(sym, TfOf(t), 0);
      if(bt <= 0 || bt <= lastBar[s][t]) continue;
      if(tfOn[s][t] && !Bereit(s, t))                         // noch nicht nachgerechnet: im naechsten Durchlauf erneut
        {
         if(wartet[s] == 0) wartet[s] = jetzt;
         else if(jetzt - wartet[s] >= 300)
            Warnung(s, 2, StringFormat("%s: Indikatoren M%d seit %d s nicht nachgerechnet - keine Signale (Historie beider Symbole pruefen)", sym, TfMin(t), (int)(jetzt - wartet[s])));
         return;
        }
      nb[t] = bt;
     }
   wartet[s] = 0;
   datetime T0 = 0;
   bool gs = false;
   for(int t=0;t<NT;t++)
     {
      if(nb[t] == 0) continue;
      lastBar[s][t] = nb[t];                                  // dauerhaft: nach Neustart wird diese Kerze nicht noch einmal gehandelt
      GlobalVariableSet(BarGv(s, t), (double)(long)nb[t]);
      gs = true;
      if(jetzt - nb[t] > 120) continue;                        // nie verspaetet einsteigen (Start, Neustart, Verbindungsluecke)
      neu[t] = true; jede = true;
      if(nb[t] > T0) T0 = nb[t];
     }
   if(gs) Sichern();
   if(!jede) return;

   int regv = 0; bool shortOk = false, gateL = false, gateS = false;
   if(!Regime(s, T0, regv, shortOk, gateL, gateS)) return;    // Regime unbekannt: kein Signal, kein Gedaechtnis (wie Replikat)
   int div = 0; bool divOk = true;
   if(DivH4) divOk = Divergenz(s, T0, div);
   int sigDir[NT]; double sigRd[NT];
   bool hat[2]; hat[0] = false; hat[1] = false;
   datetime T = 0;
   for(int t=0;t<NT;t++)
     {
      sigDir[t] = 0; sigRd[t] = 0.0;
      if(!neu[t] || !tfOn[s][t]) continue;
      datetime bt = lastBar[s][t];
      double nyh = NYHour(bt);
      double bis = (s == 0 ? GoldBisNY : NasBisNY);
      if(nyh < AbNY || nyh >= bis) continue;
      double r = 0.0;
      if(!Wert(hRsi[s][t], sym, t, bt, r)) continue;
      int dir = (r > Oben ? 1 : (r < Unten ? -1 : 0));
      if(dir == 0) continue;
      if((dir > 0 && !Longs) || (dir < 0 && !Shorts)) continue;
      if(ShortRegime && dir < 0 && !shortOk) continue;
      if(NasLongRegime && dir > 0 && s == 1 && regv < 0) continue;
      bool kreuz = true;
      if(KreuzAn)
        {
         double ro = 0.0;
         kreuz = Wert(hRsi[1-s][t], gSym[1-s], t, bt, ro) && (dir > 0 ? ro > KreuzSchwelle : ro < 100.0 - KreuzSchwelle);
        }
      if(s == 0) { bool tor = GoldTor && (dir > 0 ? gateL : gateS); if(!kreuz && !tor) continue; }
      else if(!kreuz) continue;
      if(DivH4) { if(!divOk) continue; if(dir*div < 0) continue; }
      double a = 0.0;
      if(!Wert(hAtr[s][t], sym, t, bt, a) || a <= 0.0) continue;
      sigDir[t] = dir; sigRd[t] = StopATR*a;
      hat[dir > 0 ? 0 : 1] = true;
      if(bt > T) T = bt;
      letztesSignal[s] = StringFormat("%s M%d %s (RSI %.1f)", TimeToString(bt, TIME_DATE|TIME_MINUTES), TfMin(t), (dir > 0 ? "LONG" : "SHORT"), r);
     }
   if(!hat[0] && !hat[1]) return;
   bool folge[2];
   bool gm = false;
   for(int di=0;di<2;di++)
     {
      datetime vor = lastSig[s][di];
      folge[di] = (FolgeMin <= 0) || (vor > 0 && vor < T && (long)(T - vor) <= (long)FolgeMin*60);
      if(hat[di] && T > vor)
        {
         lastSig[s][di] = T;
         GlobalVariableSet(SigGv(s, di), (double)(long)T);
         gm = true;
        }
     }
   if(gm) Sichern();
   // Einstiege
   if(WeSchlussNY > 0.0 && NYWeekday(jetzt) == 5 && NYHour(jetzt) >= WeSchlussNY - 5.0/60.0) return;
   int verl = (MaxVerlusteTag > 0 ? VerlusteHeute(s) : 0);
   bool neuP[MAXP];
   for(int k=0;k<MAXP;k++) neuP[k] = false;
   int dirNeu = 0;
   for(int t=0;t<NT;t++)
     {
      int dir = sigDir[t];
      if(dir == 0) continue;
      string was = StringFormat("%s-Signal M%d", (dir > 0 ? "LONG" : "SHORT"), TfMin(t));
      double fak = 1.0;
      if(!folge[dir > 0 ? 0 : 1])
        {
         if(ErstesSignalFaktor <= 0.0) { PrintFormat("RSI21EK %s: erstes %s gemerkt (Einstieg erst beim Folgesignal)", sym, was); continue; }
         fak = ErstesSignalFaktor;
        }
      if(MaxVerlusteTag > 0 && verl >= MaxVerlusteTag) { PrintFormat("RSI21EK %s: %s ausgelassen - %d Verlust(e) heute, keine Einstiege mehr bis 17:00 NY", sym, was, verl); return; }
      int q = PlatzWahl(s, dir, neuP, dirNeu);
      if(q < 0) { PrintFormat("RSI21EK %s: %s ausgelassen - kein freier Platz (erste Position in Gegenrichtung oder %d Plaetze belegt)", sym, was, Plaetze); continue; }
      string grund = "";
      if(!HandelMoeglich(s, true, dir, grund)) { PrintFormat("RSI21EK %s: %s ausgelassen - %s", sym, was, grund); continue; }
      if(Einstieg(s, t, dir, sigRd[t], fak, q)) { neuP[q] = true; if(q == 0) dirNeu = dir; }
     }
  }

//+------------------------------------------------------------------+
//| Verwaltung offener Positionen                                    |
//+------------------------------------------------------------------+
void Verwalten()
  {
   datetime now = TimeCurrent();
   bool optionen = (EinstandAbR > 0.0 || NachzugAbR > 0.0 || (TeilAbR > 0.0 && TeilAnteil > 0.0));
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk == 0 || !PositionSelectByTicket(tk)) continue;
      int s = -1, q = -1;
      if(!UnsereMagic(PositionGetInteger(POSITION_MAGIC), s, q)) continue;
      string sym = PositionGetString(POSITION_SYMBOL);
      if(sym != gSym[s]) continue;
      int d = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1);
      double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL), tp = PositionGetDouble(POSITION_TP);
      double vol = PositionGetDouble(POSITION_VOLUME);
      datetime t0 = (datetime)PositionGetInteger(POSITION_TIME);
      long pid = PositionGetInteger(POSITION_IDENTIFIER);
      long mg = PositionGetInteger(POSITION_MAGIC);
      double bid = SymbolInfoDouble(sym, SYMBOL_BID), ask = SymbolInfoDouble(sym, SYMBOL_ASK);
      if(bid <= 0.0 || ask <= 0.0) continue;
      string grund = "";
      // Wochenende (optional) und Zeit-Ausstieg auf Kerzenbasis wie im Replikat: Schluss der Kerze Einstieg + ZeitExitM5,
      // bzw. Schluss der ersten Kerze, die mindestens ZeitExitTage nach Beginn der Einstiegskerze beginnt
      bool we = (WeSchlussNY > 0.0 && NYWeekday(now) == 5 && NYHour(now) >= WeSchlussNY);
      int sh = iBarShift(sym, PERIOD_M5, t0, false);
      bool zeit = false;
      if(sh >= 1)
        {
         datetime tE = iTime(sym, PERIOD_M5, sh), t1 = iTime(sym, PERIOD_M5, 1);
         zeit = (ZeitExitM5 > 0 && sh >= ZeitExitM5 + 1) || (ZeitExitTage > 0.0 && tE > 0 && t1 > 0 && (double)(t1 - tE) >= ZeitExitTage*86400.0);
        }
      if(we || zeit)
        {
         if(now - versuchZu[s][q] < 30) continue;
         if(!HandelMoeglich(s, false, d, grund)) { Warnung(s, 3, StringFormat("%s: Ausstieg faellig, aber nicht moeglich - %s", sym, grund)); continue; }
         versuchZu[s][q] = now;
         Schliesse(s, tk, we ? "Wochenend-Schluss" : StringFormat("Zeit-Ausstieg (%d M5-Kerzen)", sh - 1));
         continue;
        }
      if(!optionen || !NachEinstiegsKerze(sym, t0)) continue;
      // Einstand / Nachzug / Teilgewinn (im Preset aus): ab der M5-Kerze nach dem Einstieg, ausgeloest am besten Kurs (Kerzenextrem)
      double rd = PositionR(tk);
      if(!PositionSelectByTicket(tk) || rd <= 0.0) continue;
      double fav = (d > 0) ? (bid - op)/rd : (op - ask)/rd;
      double mfe = BesterVorlauf(pid, sym, d, op, rd, t0);
      if(mfe < -1e8) continue;
      if(fav > mfe) mfe = fav;
      GlobalVariableSet(PosGv(pid, "M"), mfe);
      if(now - versuchSl[s][q] < 5) continue;
      if(TeilAbR > 0.0 && TeilAnteil > 0.0 && mfe >= TeilAbR && !GlobalVariableCheck(PosGv(pid, "T")))
        {
         bool schon = TeilSchonZu(pid);
         if(!PositionSelectByTicket(tk)) continue;
         double l0 = GlobalVariableCheck(PosGv(pid, "L")) ? GlobalVariableGet(PosGv(pid, "L")) : vol;
         double stp = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP); if(stp <= 0.0) stp = 0.01;
         double mnv = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
         double v1 = NormalizeDouble(MathFloor(l0*TeilAnteil/stp + 1e-9)*stp, LotStellen(stp));
         if(!schon && v1 >= mnv && vol - v1 >= mnv - 1e-9)
           {
            if(!HandelMoeglich(s, false, d, grund)) { Warnung(s, 3, StringFormat("%s: Teilgewinn faellig, aber nicht moeglich - %s", sym, grund)); continue; }
            versuchSl[s][q] = now;
            trade.SetExpertMagicNumber((ulong)mg);
            bool ok = trade.PositionClosePartial(tk, v1);
            uint rc = trade.ResultRetcode();
            if(ok && (rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_DONE_PARTIAL || rc == TRADE_RETCODE_PLACED))
              {
               GlobalVariableSet(PosGv(pid, "T"), 1.0); Sichern();
               PrintFormat("RSI21EK %s: Teilgewinn %.2f Lot (Vorlauf %.2f R, jetzt %.2f R)", sym, v1, mfe, fav);
              }
            else Warnung(s, 3, StringFormat("%s: Teilgewinn abgelehnt (%d %s)", sym, rc, trade.ResultRetcodeDescription()));
            continue;                                             // Stop im naechsten Durchlauf (Position hat neue Werte)
           }
         GlobalVariableSet(PosGv(pid, "T"), 1.0); Sichern();       // schon genommen oder zu klein (wie Replikat: dann ohne Teil)
        }
      double nsl = sl;
      if(EinstandAbR > 0.0 && mfe >= EinstandAbR)
        {
         double c = op + d*EinstandPlusR*rd;
         if(nsl <= 0.0 || (c - nsl)*d > 0.0) nsl = c;
        }
      if(NachzugAbR > 0.0 && mfe >= NachzugAbR)
        {
         double c = op + d*(mfe - NachzugAbstandR)*rd;
         if(nsl <= 0.0 || (c - nsl)*d > 0.0) nsl = c;
        }
      if(nsl <= 0.0) continue;
      nsl = AufTick(sym, nsl);
      double pt = SymbolInfoDouble(sym, SYMBOL_POINT);
      int dg = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
      if(!(sl <= 0.0 || (nsl - sl)*d > 0.5*pt)) continue;
      if(!HandelMoeglich(s, false, d, grund)) { Warnung(s, 3, StringFormat("%s: Stop-Aenderung faellig, aber nicht moeglich - %s", sym, grund)); continue; }
      double px = (d > 0 ? bid : ask);
      if((px - nsl)*d <= 0.0)                                     // Kurs schon jenseits des neuen Stops: schliessen (Replikat: Stop in der naechsten Kerze)
        {
         versuchSl[s][q] = now;
         Schliesse(s, tk, StringFormat("Stop %.*f schon erreicht (Vorlauf %.2f R)", dg, nsl, mfe));
         continue;
        }
      long stl = SymbolInfoInteger(sym, SYMBOL_TRADE_STOPS_LEVEL), frz = SymbolInfoInteger(sym, SYMBOL_TRADE_FREEZE_LEVEL);
      if((px - nsl)*d < (double)MathMax(stl, frz)*pt) continue;   // naeher als der Mindestabstand: spaeter erneut
      versuchSl[s][q] = now;
      trade.SetExpertMagicNumber((ulong)mg);
      bool okm = trade.PositionModify(tk, nsl, tp);
      uint rcm = trade.ResultRetcode();
      if(okm && (rcm == TRADE_RETCODE_DONE || rcm == TRADE_RETCODE_NO_CHANGES)) PrintFormat("RSI21EK %s: Stop %.*f -> %.*f (Vorlauf %.2f R)", sym, dg, sl, dg, nsl, mfe);
      else Warnung(s, 3, StringFormat("%s: Stop-Aenderung abgelehnt (%d %s)", sym, rcm, trade.ResultRetcodeDescription()));
     }
  }

// Zustands-Variablen geschlossener Positionen dieses Kontos und dieser MagicBase loeschen
void Aufraeumen()
  {
   string pp = Pfx() + "P";
   int lp = StringLen(pp);
   for(int i=GlobalVariablesTotal()-1;i>=0;i--)
     {
      string g = GlobalVariableName(i);
      if(StringFind(g, pp) != 0) continue;
      int us = StringFind(g, "_", lp);
      if(us < 0) continue;
      long pid = StringToInteger(StringSubstr(g, lp, us - lp));
      bool offen = false;
      for(int k=PositionsTotal()-1;k>=0 && !offen;k--)
        {
         ulong tk = PositionGetTicket(k);
         if(tk > 0 && PositionGetInteger(POSITION_IDENTIFIER) == pid) offen = true;
        }
      if(!offen) GlobalVariableDel(g);
     }
   Sichern();
  }

void Anzeige()
  {
   string t = StringFormat("RSI21 EK 1.00 | Equity %.2f | Risiko %.2f %% je Trade | NY %s (Versatz %d h, %s)\n",
                           AccountInfoDouble(ACCOUNT_EQUITY), RiskPct, TimeToString(TimeCurrent() - nyOff*3600, TIME_MINUTES), nyOff,
                           (AutoNYOffset ? (offGemessen ? "gemessen" : "noch nicht gemessen") : "Eingabe"));
   for(int s=0;s<NS;s++)
     {
      t += StringFormat("%s: Regime %s", gSym[s], (regOk[s] ? StringFormat("Schluss %.2f / SMA%d %.2f / SMA%d %.2f", regC[s], MaLang, regMaL[s], MaSchnell, regMaS[s]) : "unbekannt"));
      int np = (int)MathMax(1, MathMin(MAXP, Plaetze));
      for(int q=0;q<np;q++)
        {
         ulong tk = 0; int d = 0;
         if(PlatzPosition(s, q, tk, d) && PositionSelectByTicket(tk))
            t += StringFormat(" | P%d %s %.2f Lot %.2f", q + 1, (d > 0 ? "L" : "S"), PositionGetDouble(POSITION_VOLUME), PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP));
        }
      if(StringLen(letztesSignal[s]) > 0) t += " | letztes Signal " + letztesSignal[s];
      t += "\n";
     }
   Comment(t);
  }

//+------------------------------------------------------------------+
//| Ablauf                                                           |
//+------------------------------------------------------------------+
void Durchlauf()
  {
   OffsetPflegen();
   Verwalten();
   for(int s=0;s<NS;s++) Signale(s);
   datetime lok = TimeLocal();
   bool verb = (MQLInfoInteger(MQL_TESTER) || TerminalInfoInteger(TERMINAL_CONNECTED));
   // Aufraeumen erst 5 min nach dem Start und mit Verbindung (vorher kann die Positionsliste noch leer sein)
   if(verb && AccountInfoInteger(ACCOUNT_LOGIN) != 0 && lok - startLokal >= 300 && lok - aufLokal >= 3600) { Aufraeumen(); aufLokal = lok; }
   if(!MQLInfoInteger(MQL_TESTER) && lok - anzLokal >= 2) { Anzeige(); anzLokal = lok; }
  }

int OnInit()
  {
   gLock = "";
   for(int s=0;s<NS;s++)
      for(int t=0;t<NT;t++) { hRsi[s][t] = INVALID_HANDLE; hAtr[s][t] = INVALID_HANDLE; }
   if(RiskPct <= 0.0 || StopATR <= 0.0 || Oben <= 50.0 || Unten >= 50.0 || RsiLen < 2 || RsiLen > 100 || MaLang < 1 || MaSchnell < 1)
     { Print("RSI21EK: Eingaben ungueltig (RiskPct > 0, StopATR > 0, Oben > 50 > Unten, RsiLen 2-100, SMA >= 1)"); return(INIT_PARAMETERS_INCORRECT); }
   if(GewichtM15 < 0.0 || GewichtM30 < 0.0 || GewichtH1 < 0.0 || GoldFaktor <= 0.0 || MinLotToleranz <= 0.0 || MaxLotsJePos < 0.0 || KreuzSchwelle < 0.0 || KreuzSchwelle > 100.0)
     { Print("RSI21EK: Eingaben ungueltig (Gewichte >= 0, GoldFaktor > 0, MinLotToleranz > 0, MaxLotsJePos >= 0, KreuzSchwelle 0-100)"); return(INIT_PARAMETERS_INCORRECT); }
   if(DivH4 && (DivRadius < 1 || DivAbstand < 0.0 || DivHistoryH1 < 2000))
     { Print("RSI21EK: Eingaben ungueltig (DivRadius >= 1, DivAbstand >= 0, DivHistoryH1 >= 2000)"); return(INIT_PARAMETERS_INCORRECT); }
   if(Plaetze < 1 || Plaetze > MAXP || MaxVerlusteTag < 0 || FolgeMin < 0 || ErstesSignalFaktor < 0.0 || ZeitExitM5 < 0 || ZeitExitTage < 0.0 || AbweichungPkt < 0)
     { Print("RSI21EK: Eingaben ungueltig (Plaetze 1-5, MaxVerlusteTag/FolgeMin/ErstesSignalFaktor/Zeit-Ausstieg/AbweichungPkt >= 0)"); return(INIT_PARAMETERS_INCORRECT); }
   if(ZielNasR < 0.0 || ZielGoldR < 0.0 || EinstandAbR < 0.0 || NachzugAbR < 0.0 || TeilAbR < 0.0)
     { Print("RSI21EK: Eingaben ungueltig (Ziele, Einstand, Nachzug, Teilgewinn >= 0)"); return(INIT_PARAMETERS_INCORRECT); }
   if(EinstandAbR > 0.0 && EinstandPlusR >= EinstandAbR) { Print("RSI21EK: EinstandPlusR muss unter EinstandAbR liegen"); return(INIT_PARAMETERS_INCORRECT); }
   if(NachzugAbR > 0.0 && (NachzugAbstandR <= 0.0 || NachzugAbstandR > NachzugAbR + 5.0)) { Print("RSI21EK: NachzugAbstandR muss > 0 und hoechstens NachzugAbR + 5 sein"); return(INIT_PARAMETERS_INCORRECT); }
   if(TeilAbR > 0.0 && (TeilAnteil < 0.1 || TeilAnteil > 0.9)) { Print("RSI21EK: TeilAnteil 0,1-0,9"); return(INIT_PARAMETERS_INCORRECT); }
   if(MarginMaxPct <= 0.0 || MarginMaxPct > 100.0) { Print("RSI21EK: MarginMaxPct 1-100"); return(INIT_PARAMETERS_INCORRECT); }
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
     { Print("RSI21EK: nur fuer Hedging-Konten (auf Netting-Konten verschmelzen die Positionen mit fremden oder manuellen)"); return(INIT_FAILED); }
   gSym[0] = GoldSymbol; gSym[1] = NasSymbol;
   wTf[0] = GewichtM15; wTf[1] = GewichtM30; wTf[2] = GewichtH1;
   tfOn[0][0] = GoldM15; tfOn[0][1] = GoldM30; tfOn[0][2] = GoldH1;
   tfOn[1][0] = NasM15;  tfOn[1][1] = NasM30;  tfOn[1][2] = NasH1;
   nyOff = NYOffsetHours; offGemessen = false; offKand = -99; offLokal = 0;
   startLokal = TimeLocal(); anzLokal = 0; aufLokal = 0;
   for(int s=0;s<NS;s++)
     {
      if(!SymbolSelect(gSym[s], true)) { PrintFormat("RSI21EK: Symbol %s nicht vorhanden - exakten Namen aus dem Market Watch eintragen", gSym[s]); return(INIT_FAILED); }
      for(int t=0;t<NT;t++)
        {
         hRsi[s][t] = iRSI(gSym[s], TfOf(t), RsiLen, PRICE_CLOSE);
         hAtr[s][t] = iATR(gSym[s], TfOf(t), 14);
         if(hRsi[s][t] == INVALID_HANDLE || hAtr[s][t] == INVALID_HANDLE) { PrintFormat("RSI21EK: Indikator fuer %s fehlgeschlagen", gSym[s]); return(INIT_FAILED); }
         lastBar[s][t] = 0;
        }
      geladen[s] = false;
      regOk[s] = false; regTag[s] = -1; divBucket[s] = 0; divDir[s] = 0; divGut[s] = false; letztesSignal[s] = ""; wartet[s] = 0;
      lastSig[s][0] = 0; lastSig[s][1] = 0;
      for(int k=0;k<5;k++) warnZeit[s][k] = 0;
      for(int q=0;q<MAXP;q++) { versuchZu[s][q] = 0; versuchSl[s][q] = 0; }
     }
   // Sperre: dieselbe MagicBase darf nur auf einem Chart laufen (sonst wuerde jedes Signal doppelt gehandelt)
   if(!MQLInfoInteger(MQL_TESTER))
     {
      string lp = GVP + "LOCK_" + IntegerToString(MagicBase) + "_";
      for(int i=GlobalVariablesTotal()-1;i>=0;i--)
        {
         string g = GlobalVariableName(i);
         if(StringFind(g, lp) != 0) continue;
         long cid = StringToInteger(StringSubstr(g, StringLen(lp)));
         if(cid == ChartID()) continue;
         bool da = false;
         for(long c=ChartFirst(); c>=0; c=ChartNext(c)) if(c == cid) { da = true; break; }
         if(da) { Print("RSI21EK: laeuft mit MagicBase ", MagicBase, " schon auf einem anderen Chart (ID ", cid, ") - zweite Instanz abgelehnt"); return(INIT_FAILED); }
         GlobalVariableDel(g);                                      // verwaist
        }
      gLock = lp + IntegerToString(ChartID());
      if(!GlobalVariableCheck(gLock) && !GlobalVariableTemp(gLock)) Print("RSI21EK: Sperre gegen eine zweite Instanz nicht gesetzt");
     }
   OffsetPflegen();
   trade.SetDeviationInPoints((ulong)AbweichungPkt);
   PrintFormat("RSI21EK 1.00: %s + %s, NY-Versatz %d h | Risiko %.2f %% der %s je Trade x Gewicht (M15 %.2f, M30 %.2f, H1 %.2f), Gold x%.2f, Margin bis %.0f %% | Plaetze %d, Verluste/Tag %d",
               gSym[0], gSym[1], nyOff, RiskPct, (RisikoVomSaldo ? "Saldo" : "Equity"), GewichtM15, GewichtM30, GewichtH1, GoldFaktor, MarginMaxPct, Plaetze, MaxVerlusteTag);
   PrintFormat("RSI21EK 1.00: Signal RSI(%d) > %.1f / < %.1f, Kreuz %s, NY %.2f-%.2f (NAS) / -%.2f (Gold), Folge %d min, Div %s | Stop %.2f ATR, Ziel NAS %.2f R / Gold %.2f R, Einstand %.2f R, Nachzug %.2f/%.2f R, Zeit %d M5 / %.1f Tage, Wochenende %s",
               RsiLen, Oben, Unten, (KreuzAn ? DoubleToString(KreuzSchwelle, 1) : "aus"), AbNY, NasBisNY, GoldBisNY, FolgeMin, (DivH4 ? "an" : "aus"),
               StopATR, ZielNasR, ZielGoldR, EinstandAbR, NachzugAbR, NachzugAbstandR, ZeitExitM5, ZeitExitTage, (WeSchlussNY > 0.0 ? "schliessen" : "halten"));
   if(!EventSetTimer(1)) { Print("RSI21EK: Timer nicht gesetzt - ohne Timer wird das zweite Symbol nur mit den Ticks des Chart-Symbols bedient"); return(INIT_FAILED); }
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   for(int s=0;s<NS;s++)
      for(int t=0;t<NT;t++)
        {
         if(hRsi[s][t] != INVALID_HANDLE) IndicatorRelease(hRsi[s][t]);
         if(hAtr[s][t] != INVALID_HANDLE) IndicatorRelease(hAtr[s][t]);
        }
   if(StringLen(gLock) > 0) GlobalVariableDel(gLock);
   Sichern();
   Comment("");
  }

void OnTick()  { Durchlauf(); }
void OnTimer() { Durchlauf(); }
//+------------------------------------------------------------------+
