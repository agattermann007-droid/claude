//+------------------------------------------------------------------+
//|  RSI21 EK (Eigenkapital) - Build 1.00, 25.09.2026                |
//|  RSI21 Continuation aus DEADBAND LIVE 4 Build 6.60, als eigene   |
//|  Strategie fuer EIGENES Kapital: keine Prop-Firmen-Regeln (kein  |
//|  Boden, keine Tages-/Floating-Grenze, keine gueltigen Tage, keine|
//|  Auszahlungen, keine News-, Hedging- oder 130-s-Regel, kein      |
//|  Wochenend-Schluss, keine Budgets, keine Pufferkurve, kein       |
//|  Serien-Stopp). Groesse in % der Equity (Zinseszins), begrenzt   |
//|  nur durch die Margin des Brokers.                               |
//|  VOREINSTELLUNGEN: siehe Kopf "Build 1.00" unten und Bericht     |
//|  RSI21_EK_Bericht.md.                                            |
//|                                                                  |
//|  Signal (unveraendert wie 6.60, Schwellen als Eingaben):         |
//|   Long, wenn RSI(21) der zuletzt geschlossenen Kerze > Oben      |
//|   (Short < Unten) auf M15/M30/H1, Kerzenbeginn im NY-Zeitfenster,|
//|   Bestaetigung RSI(21) des anderen Symbols (gleiche Zeitebene)   |
//|   > KreuzSchwelle (< 100 - X); Gold alternativ Vortagesschluss   |
//|   ueber (unter) SMA200 und SMA100. Shorts nur unter SMA200 oder  |
//|   SMA100, NAS-Longs nur ueber SMA200, kein Einstieg gegen eine   |
//|   bestaetigte H4-RSI-Divergenz. Nur Folgesignale (frueheres      |
//|   Signal gleicher Richtung hoechstens FolgeMin alt). Stop        |
//|   StopATR x ATR(14) der Signal-Zeitebene.                        |
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
input double RiskPct        = 1.0;        // Risiko je Trade in % der Equity (x Gewicht der Zeitebene, x Gold-Faktor)
input bool   RisikoVomSaldo = false;      // true = % vom Saldo statt von der Equity
input double GewichtM15     = 1.25;       // Gewicht der Zeitebenen (Risiko = RiskPct x Gewicht)
input double GewichtM30     = 1.0;
input double GewichtH1      = 0.75;
input double GoldFaktor     = 0.70;       // Risiko-Faktor fuer Gold
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
input bool   GoldM30        = true;
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
input int    FolgeMin       = 240;        // nur Folgesignale: frueheres Signal gleicher Richtung hoechstens X min alt (0 = jedes Signal)
input double ErstesSignalFaktor = 0.0;    // Groesse fuer das erste Signal einer Bewegung (0 = nur merken, nicht handeln)
input double StopATR        = 2.0;        // Stop in ATR(14) der Signal-Zeitebene (= 1 R)

input group             "=== Ausstieg ==="
input double ZielNasR       = 2.2;        // Ziel NAS in R (0 = kein Ziel)
input double ZielGoldR      = 2.64;       // Ziel Gold in R (0 = kein Ziel)
input double EinstandAbR    = 1.0;        // Stop auf Einstand + EinstandPlusR, sobald der Kurs X R im Plus war (0 = aus)
input double EinstandPlusR  = 0.05;
input double NachzugAbR     = 0.0;        // Stop-Nachzug, sobald der beste Kurs X R im Plus war (0 = aus) ...
input double NachzugAbstandR = 0.0;       // ... im Abstand Y R hinter dem besten Kurs
input double TeilAbR        = 0.0;        // Teilgewinn bei X R (0 = aus) ...
input double TeilAnteil     = 0.0;        // ... Anteil der Position (0,1-0,9)
input int    ZeitExitM5     = 1152;       // Zeit-Ausstieg nach X M5-Kerzen seit der Einstiegskerze (0 = aus)
input double ZeitExitTage   = 8.0;        // ... oder nach X Kalendertagen (0 = aus)

input group             "=== Plaetze, Tag, Wochenende ==="
input int    Plaetze        = 2;          // Positionen je Symbol (weitere nur in Richtung der ersten), 1-5
input int    MaxVerlusteTag = 2;          // keine Einstiege mehr nach X Verlust-Trades am Tag je Symbol (0 = aus)
input double WeSchlussNY    = 0.0;        // Freitag ab X NY alle Positionen schliessen (0 = ueber das Wochenende halten)

input group             "=== Betrieb ==="
input int    AbweichungPkt  = 50;         // erlaubte Abweichung beim Einstieg in Punkten
input bool   PushMeldungen  = false;      // Push-Meldung bei Einstieg, Ausstieg und Fehlern

//--- Zustand
CTrade   trade;
string   gSym[NS];
int      hRsi[NS][NT], hAtr[NS][NT];
datetime lastBar[NS][NT];
datetime lastSig[NS][2];             // Kerzenzeit des letzten gueltigen Signals je Richtung ([0] long, [1] short)
bool     tfOn[NS][NT];
double   wTf[NT];
int      nyOff = 7;
datetime offZeit = 0;
long     regTag[NS];                  // Handelstag, fuer den das Regime gerechnet wurde
bool     regOk[NS];
double   regC[NS], regMaL[NS], regMaS[NS];
datetime divBucket[NS];
int      divDir[NS];
bool     divGut[NS];
datetime letzteMeldung = 0;
string   letztesSignal[NS];

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

int AutoOffset()
  {
   if(MQLInfoInteger(MQL_TESTER) || !AutoNYOffset) return NYOffsetHours;
   if(!TerminalInfoInteger(TERMINAL_CONNECTED)) return nyOff;
   datetime gmt = TimeGMT(), srv = TimeTradeServer();
   if(gmt <= 0 || srv <= 0) return nyOff;
   int srvOff = (int)MathRound((double)(srv - gmt) / 3600.0);
   int off = srvOff - (UsDst(gmt) ? -4 : -5);
   if(off < -12 || off > 14)
     {
      PrintFormat("RSI21EK: automatischer NY-Versatz %d unplausibel (Server %+d h GMT) - bleibe bei %d", off, srvOff, nyOff);
      return nyOff;
     }
   return off;
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

long MagicOf(const int s, const int q) { return MagicBase + 10*s + q; }
bool UnsereMagic(const long mg, int &s, int &q)
  {
   long o = mg - MagicBase;
   if(o < 0 || o >= 10*NS) return false;
   s = (int)(o / 10); q = (int)(o % 10);
   return (q < MAXP);
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

// Platzwahl wie im Replikat: erster Platz frei -> erster; sonst naechster freier Platz, wenn der erste in dieselbe Richtung laeuft
int PlatzWahl(const int s, const int dir)
  {
   ulong tk = 0; int dA = 0;
   if(!PlatzPosition(s, 0, tk, dA)) return 0;
   if(dA != dir) return -1;
   int np = (int)MathMax(1, MathMin(MAXP, Plaetze));
   for(int q=1;q<np;q++)
     {
      ulong t2 = 0; int d2 = 0;
      if(!PlatzPosition(s, q, t2, d2)) return q;
     }
   return -1;
  }

string PosGv(const long pid, const string was) { return GVP + "P" + IntegerToString(pid) + "_" + was; }
string SigGv(const int s, const int di) { return GVP + "SIG_" + gSym[s] + (di == 0 ? "_L" : "_S"); }

// urspruenglicher Stop-Abstand (1 R): gemerkt beim Einstieg, sonst aus der Eroeffnungs-Order
double PositionR(const ulong tk)
  {
   if(!PositionSelectByTicket(tk)) return 0.0;
   long pid = PositionGetInteger(POSITION_IDENTIFIER);
   string g = PosGv(pid, "R");
   if(GlobalVariableCheck(g)) { double r = GlobalVariableGet(g); if(r > 0.0) return r; }
   double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL);
   double rd = (sl > 0.0 ? MathAbs(op - sl) : 0.0);
   if(HistorySelectByPosition(pid))
     {
      for(int i=0;i<HistoryDealsTotal();i++)
        {
         ulong dt = HistoryDealGetTicket(i);
         if(dt == 0 || HistoryDealGetInteger(dt, DEAL_ENTRY) != DEAL_ENTRY_IN) continue;
         ulong ot = (ulong)HistoryDealGetInteger(dt, DEAL_ORDER);
         double osl = (ot > 0 && HistoryOrderSelect(ot)) ? HistoryOrderGetDouble(ot, ORDER_SL) : 0.0;
         double px = HistoryDealGetDouble(dt, DEAL_PRICE);
         if(osl > 0.0 && px > 0.0) rd = MathAbs(px - osl);
         break;
        }
     }
   PositionSelectByTicket(tk);
   if(rd > 0.0) GlobalVariableSet(g, rd);
   return rd;
  }

// erst ab der M5-Kerze nach der Einstiegskerze (wie im Replikat)
bool NachEinstiegsKerze(const string s, const datetime tOpen)
  {
   int ps = PeriodSeconds(PERIOD_M5);
   datetime b0 = iTime(s, PERIOD_M5, 0);
   datetime naechste = (datetime)((long)tOpen - (long)tOpen % ps + ps);
   return (b0 > 0 && b0 >= naechste);
  }

// bester Vorlauf in R seit der Kerze nach dem Einstieg (Nachzug): aus M5-Kerzen und dem aktuellen Kurs
double BesterVorlauf(const ulong tk, const string s, const int d, const double op, const double rd, const datetime t0)
  {
   long pid = PositionGetInteger(POSITION_IDENTIFIER);
   string g = PosGv(pid, "M");
   double mfe = GlobalVariableCheck(g) ? GlobalVariableGet(g) : -1e9;
   if(mfe < -1e8)
     {
      mfe = 0.0;
      int ps = PeriodSeconds(PERIOD_M5);
      datetime ab = (datetime)((long)t0 - (long)t0 % ps + ps);
      MqlRates r[];
      int n = CopyRates(s, PERIOD_M5, ab, TimeCurrent(), r);
      double pt = SymbolInfoDouble(s, SYMBOL_POINT);
      for(int j=0;j<n;j++)
        {
         double f = (d > 0) ? (r[j].high - op)/rd : (op - (r[j].low + r[j].spread*pt))/rd;
         if(f > mfe) mfe = f;
        }
      PositionSelectByTicket(tk);
     }
   return mfe;
  }

bool Schliesse(const ulong tk, const string grund)
  {
   if(!PositionSelectByTicket(tk)) return false;
   string s = PositionGetString(POSITION_SYMBOL);
   double p = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
   trade.SetExpertMagicNumber((ulong)PositionGetInteger(POSITION_MAGIC));
   if(trade.PositionClose(tk))
     {
      PrintFormat("RSI21EK %s: %s - geschlossen, Ergebnis %.2f", s, grund, p);
      if(PushMeldungen) SendNotification(StringFormat("RSI21EK %s: %s, %.2f", s, grund, p));
      return true;
     }
   PrintFormat("RSI21EK %s: Schliessen (%s) abgelehnt (%d %s)", s, grund, trade.ResultRetcode(), trade.ResultRetcodeDescription());
   return false;
  }

// Verlust-Trades heute (Handelstag 17:00 NY) je Symbol; Verlust = Gewinn + Swap < 0 (wie Replikat, ohne Kommission)
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

bool Wert(const int handle, const string sym, const int t, const datetime T, double &v)
  {
   int sh = BarVor(sym, TfOf(t), T);
   if(sh < 0) return false;
   double b[];
   if(CopyBuffer(handle, 0, sh, 1, b) != 1) return false;
   if(b[0] == EMPTY_VALUE || !MathIsValidNumber(b[0])) return false;
   v = b[0];
   return true;
  }

// Tagesregime aus H1: Schlusskurse je Handelstag (17:00-17:00 NY), ohne den laufenden Tag; SMA lang/schnell
bool Regime(const int s, int &regv, bool &shortOk, bool &gateL, bool &gateS)
  {
   long heute = TagIndex(TimeCurrent());
   if(!(regOk[s] && regTag[s] == heute))
     {
      regOk[s] = false;
      int nMa = (int)MathMax(MaLang, MaSchnell);
      int need = (nMa + 15)*25;
      MqlRates r[];
      ArraySetAsSeries(r, false);
      int got = CopyRates(gSym[s], PERIOD_H1, 0, need, r);
      if(got < 200) return false;
      double cl[]; ArrayResize(cl, got);
      int n = 0; long lastD = -1;
      for(int i=0;i<got;i++)
        {
         long dI = TagIndex(r[i].time);
         if(dI >= heute) break;
         if(dI != lastD) { cl[n] = r[i].close; n++; lastD = dI; }
         else cl[n-1] = r[i].close;
        }
      if(n < 50) return false;
      int nl = (int)MathMin(n, MaLang), nf = (int)MathMin(n, MaSchnell);
      double sl = 0.0, sf = 0.0;
      for(int i=n-nl;i<n;i++) sl += cl[i];
      for(int i=n-nf;i<n;i++) sf += cl[i];
      regC[s] = cl[n-1]; regMaL[s] = sl/nl; regMaS[s] = sf/nf;
      regTag[s] = heute; regOk[s] = true;
      if(n < nMa) PrintFormat("RSI21EK %s: nur %d Handelstage H1-Historie (SMA %d/%d mit weniger Tagen) - Max. Balken im Chart erhoehen", gSym[s], n, MaLang, MaSchnell);
     }
   double c = regC[s], mL = regMaL[s], mS = regMaS[s];
   if(c <= 0.0 || mL <= 0.0 || mS <= 0.0) return false;
   shortOk = (c < mL || c < mS);
   gateL   = (c > mL && c > mS);
   gateS   = (c < mL && c < mS);
   regv    = (c > mL) ? 1 : -1;
   return true;
  }

// bestaetigte RSI-Divergenz auf UTC-H4 (aus H1 wie RSI21 v3.4 / DEADBAND 6.60): +1 bullisch, -1 baerisch, 0 keine/beide
bool Divergenz(const int s, int &direction)
  {
   long sek = 14400;
   string sym = gSym[s];
   datetime current = (datetime)(((long)SrvZuUTC(TimeCurrent())/sek)*sek);
   if(divBucket[s] == current && current > 0) { direction = divDir[s]; return divGut[s]; }
   MqlRates rates[];
   ArraySetAsSeries(rates, false);
   int got = CopyRates(sym, PERIOD_H1, 1, DivHistoryH1, rates);
   if(got < 2000) return false;
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
   if(n < 500) return false;
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
   double mpp = MoneyPerPricePerLot(sym);
   double pt  = SymbolInfoDouble(sym, SYMBOL_POINT);
   long   stl = SymbolInfoInteger(sym, SYMBOL_TRADE_STOPS_LEVEL);
   if(rd <= 0.0 || mpp <= 0.0) return false;
   if(stl > 0 && rd < stl*pt*1.2) { PrintFormat("RSI21EK %s: Stop %.5f unter dem Mindestabstand des Brokers - ausgelassen", sym, rd); return false; }
   double w = wTf[t]*(s == 0 ? GoldFaktor : 1.0)*fak;
   double basis = RisikoVomSaldo ? AccountInfoDouble(ACCOUNT_BALANCE) : AccountInfoDouble(ACCOUNT_EQUITY);
   double risk = basis*RiskPct/100.0*w;
   if(risk <= 0.0) return false;
   double mnv = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN), mxv = SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX);
   double stp = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP);
   if(stp <= 0.0) stp = 0.01;
   if(mnv <= 0.0) mnv = stp;
   if(mnv*rd*mpp > risk*MinLotToleranz)
     {
      PrintFormat("RSI21EK %s: Mindestlot %.2f traegt %.2f Risiko, Soll %.2f - ausgelassen (Konto zu klein fuer diesen Stop)", sym, mnv, mnv*rd*mpp, risk);
      return false;
     }
   double lots = MathFloor(risk/(rd*mpp)/stp + 0.5)*stp;                 // kaufmaennisch gerundet (wie Replikat)
   if(lots < mnv) lots = mnv;
   if(MaxLotsJePos > 0.0 && lots > MaxLotsJePos) lots = MathFloor(MaxLotsJePos/stp + 1e-9)*stp;
   if(mxv > 0.0 && lots > mxv) lots = MathFloor(mxv/stp + 1e-9)*stp;
   double ask = SymbolInfoDouble(sym, SYMBOL_ASK), bid = SymbolInfoDouble(sym, SYMBOL_BID);
   if(ask <= 0.0 || bid <= 0.0) return false;
   double ent = (dir > 0 ? ask : bid);
   // Margin: alle Positionen zusammen hoechstens MarginMaxPct % der Equity - sonst kleiner
   double m1 = 0.0;
   if(!OrderCalcMargin(dir > 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, sym, 1.0, ent, m1) || m1 <= 0.0)
     { PrintFormat("RSI21EK %s: Margin nicht berechenbar (%d) - ausgelassen", sym, GetLastError()); return false; }
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double frei = MathMin(eq*MarginMaxPct/100.0 - AccountInfoDouble(ACCOUNT_MARGIN), AccountInfoDouble(ACCOUNT_MARGIN_FREE));
   if(lots*m1 > frei)
     {
      double lmax = MathFloor(frei/m1/stp + 1e-9)*stp;
      if(lmax < mnv) { PrintFormat("RSI21EK %s: Margin reicht nicht (frei %.2f, je Lot %.2f) - ausgelassen", sym, frei, m1); return false; }
      PrintFormat("RSI21EK %s: Groesse wegen Margin %.2f -> %.2f Lot", sym, lots, lmax);
      lots = lmax;
     }
   lots = NormalizeDouble(lots, LotStellen(stp));
   int dg = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
   double sl = NormalizeDouble(ent - dir*rd, dg);
   double rr = (s == 0 ? ZielGoldR : ZielNasR);
   double tp = (rr > 0.0 ? NormalizeDouble(ent + dir*rr*rd, dg) : 0.0);
   double minD = (stl > 0 ? stl*pt : 0.0);
   if(dir > 0 && (bid - sl < minD || (tp > 0.0 && tp - bid < minD))) return false;
   if(dir < 0 && (sl - ask < minD || (tp > 0.0 && ask - tp < minD))) return false;
   trade.SetExpertMagicNumber((ulong)MagicOf(s, q));
   trade.SetDeviationInPoints(AbweichungPkt);
   string kom = StringFormat("RSI21EK %s M%d P%d%s", (dir > 0 ? "L" : "S"), TfMin(t), q + 1, (fak < 1.0 ? " erst" : ""));
   bool ok = (dir > 0) ? trade.Buy(lots, sym, 0.0, sl, tp, kom) : trade.Sell(lots, sym, 0.0, sl, tp, kom);
   uint rc = trade.ResultRetcode();
   if(!ok || (rc != TRADE_RETCODE_DONE && rc != TRADE_RETCODE_DONE_PARTIAL && rc != TRADE_RETCODE_PLACED))
     {
      PrintFormat("RSI21EK %s: Einstieg abgelehnt (%d %s) %.2f Lot, SL %.*f, TP %.*f", sym, rc, trade.ResultRetcodeDescription(), lots, dg, sl, dg, tp);
      if(PushMeldungen) SendNotification(StringFormat("RSI21EK %s: Einstieg abgelehnt (%d)", sym, rc));
      return false;
     }
   long pid = (long)trade.ResultOrder();                                  // Hedging-Konto: Positions-Kennung = Eroeffnungs-Order
   GlobalVariableSet(PosGv(pid, "R"), rd);
   GlobalVariableSet(PosGv(pid, "L"), lots);
   PrintFormat("RSI21EK %s: Einstieg %s M%d Platz %d, %.2f Lot, Risiko %.2f (%.2f %% x %.2f), Stop %.*f, Ziel %s",
               sym, (dir > 0 ? "LONG" : "SHORT"), TfMin(t), q + 1, lots, lots*rd*mpp, RiskPct, w, dg, sl,
               (tp > 0.0 ? DoubleToString(tp, dg) : "keins"));
   if(PushMeldungen) SendNotification(StringFormat("RSI21EK %s %s M%d, %.2f Lot", sym, (dir > 0 ? "LONG" : "SHORT"), TfMin(t), lots));
   return true;
  }

//+------------------------------------------------------------------+
//| Signale je Symbol (bei neuer Kerze einer Zeitebene)              |
//+------------------------------------------------------------------+
// Indikatoren der Zeitebene nachgerechnet (nach einer neuen Kerze rechnet MT5 die Handles asynchron nach)
bool Bereit(const int s, const int t)
  {
   int nb = Bars(gSym[s], TfOf(t));
   return (nb > 0 && BarsCalculated(hRsi[s][t]) >= nb && BarsCalculated(hAtr[s][t]) >= nb);
  }

void Signale(const int s)
  {
   string sym = gSym[s];
   datetime jetzt = TimeCurrent();
   bool neu[NT]; bool jede = false;
   datetime nb[NT];
   for(int t=0;t<NT;t++)
     {
      neu[t] = false; nb[t] = 0;
      datetime bt = iTime(sym, TfOf(t), 0);
      if(bt <= 0 || bt == lastBar[s][t]) continue;
      if(tfOn[s][t] && !Bereit(s, t)) return;                 // noch nicht nachgerechnet: im naechsten Durchlauf erneut
      nb[t] = bt;
     }
   for(int t=0;t<NT;t++)
     {
      if(nb[t] == 0) continue;
      bool start = (lastBar[s][t] == 0);
      lastBar[s][t] = nb[t];
      if(start && jetzt - nb[t] > 120) continue;               // Start mitten in einer Kerze: nicht nachtraeglich einsteigen
      neu[t] = true; jede = true;
     }
   if(!jede) return;

   int regv = 0; bool shortOk = false, gateL = false, gateS = false;
   if(!Regime(s, regv, shortOk, gateL, gateS))              // Regime unbekannt: kein Signal, kein Gedaechtnis (wie Replikat)
     {
      static datetime warn = 0;
      if(jetzt - warn >= 3600) { PrintFormat("RSI21EK %s: Tagesregime nicht berechenbar (zu wenig H1-Historie) - keine Signale", sym); warn = jetzt; }
      return;
     }
   int div = 0; bool divOk = true;
   if(DivH4) divOk = Divergenz(s, div);
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
   for(int di=0;di<2;di++)
     {
      datetime vor = lastSig[s][di];
      folge[di] = (FolgeMin <= 0) || (vor > 0 && vor < T && (long)(T - vor) <= (long)FolgeMin*60);
      if(hat[di] && T > vor)
        {
         lastSig[s][di] = T;
         GlobalVariableSet(SigGv(s, di), (double)(long)T);
        }
     }
   // Einstiege
   if(WeSchlussNY > 0.0 && NYWeekday(jetzt) == 5 && NYHour(jetzt) >= WeSchlussNY - 5.0/60.0) return;
   if(SymbolInfoInteger(sym, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_FULL) return;
   int verl = (MaxVerlusteTag > 0 ? VerlusteHeute(s) : 0);
   for(int t=0;t<NT;t++)
     {
      int dir = sigDir[t];
      if(dir == 0) continue;
      double fak = 1.0;
      if(!folge[dir > 0 ? 0 : 1])
        {
         if(ErstesSignalFaktor <= 0.0) { PrintFormat("RSI21EK %s: erstes %s-Signal M%d gemerkt (Einstieg erst beim Folgesignal)", sym, (dir > 0 ? "LONG" : "SHORT"), TfMin(t)); continue; }
         fak = ErstesSignalFaktor;
        }
      if(MaxVerlusteTag > 0 && verl >= MaxVerlusteTag) { PrintFormat("RSI21EK %s: %d Verluste heute - keine Einstiege mehr", sym, verl); return; }
      int q = PlatzWahl(s, dir);
      if(q < 0) continue;
      Einstieg(s, t, dir, sigRd[t], fak, q);
     }
  }

//+------------------------------------------------------------------+
//| Verwaltung offener Positionen                                    |
//+------------------------------------------------------------------+
void Verwalten()
  {
   datetime now = TimeCurrent();
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
      datetime t0 = (datetime)PositionGetInteger(POSITION_TIME);
      long pid = PositionGetInteger(POSITION_IDENTIFIER);
      double bid = SymbolInfoDouble(sym, SYMBOL_BID), ask = SymbolInfoDouble(sym, SYMBOL_ASK);
      if(bid <= 0.0 || ask <= 0.0) continue;
      if(SymbolInfoInteger(sym, SYMBOL_TRADE_MODE) == SYMBOL_TRADE_MODE_DISABLED) continue;
      // Wochenende (optional)
      if(WeSchlussNY > 0.0 && NYWeekday(now) == 5 && NYHour(now) >= WeSchlussNY) { Schliesse(tk, "Wochenend-Schluss"); continue; }
      // Zeit-Ausstieg: Schluss der Kerze Einstieg + ZeitExitM5 (wie Replikat), bzw. nach ZeitExitTage
      int sh = iBarShift(sym, PERIOD_M5, t0, false);
      bool zeit = (ZeitExitM5 > 0 && sh >= ZeitExitM5 + 1) || (ZeitExitTage > 0.0 && (double)(now - t0) >= ZeitExitTage*86400.0);
      if(zeit) { Schliesse(tk, StringFormat("Zeit-Ausstieg (%d M5-Kerzen)", sh)); continue; }
      double rd = PositionR(tk);
      if(rd <= 0.0 || !PositionSelectByTicket(tk)) continue;
      if(!NachEinstiegsKerze(sym, t0)) continue;
      double fav = (d > 0) ? (bid - op)/rd : (op - ask)/rd;
      // Teilgewinn (einmal)
      if(TeilAbR > 0.0 && TeilAnteil > 0.0 && fav >= TeilAbR && !GlobalVariableCheck(PosGv(pid, "T")))
        {
         double vol = PositionGetDouble(POSITION_VOLUME);
         double l0 = GlobalVariableCheck(PosGv(pid, "L")) ? GlobalVariableGet(PosGv(pid, "L")) : vol;
         double stp = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP); if(stp <= 0.0) stp = 0.01;
         double mnv = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
         double v1 = NormalizeDouble(MathFloor(l0*TeilAnteil/stp + 1e-9)*stp, LotStellen(stp));
         if(v1 >= mnv && vol - v1 >= mnv - 1e-9)
           {
            trade.SetExpertMagicNumber((ulong)PositionGetInteger(POSITION_MAGIC));
            if(trade.PositionClosePartial(tk, v1)) { GlobalVariableSet(PosGv(pid, "T"), 1.0); PrintFormat("RSI21EK %s: Teilgewinn %.2f Lot bei %.2f R", sym, v1, fav); }
           }
         else GlobalVariableSet(PosGv(pid, "T"), 1.0);
         if(!PositionSelectByTicket(tk)) continue;
         sl = PositionGetDouble(POSITION_SL); tp = PositionGetDouble(POSITION_TP);
        }
      double nsl = sl;
      if(EinstandAbR > 0.0 && fav >= EinstandAbR)
        {
         double c = op + d*EinstandPlusR*rd;
         if(nsl <= 0.0 || (c - nsl)*d > 0.0) nsl = c;
        }
      if(NachzugAbR > 0.0)
        {
         double mfe = BesterVorlauf(tk, sym, d, op, rd, t0);
         if(fav > mfe) mfe = fav;
         GlobalVariableSet(PosGv(pid, "M"), mfe);
         if(mfe >= NachzugAbR)
           {
            double c = op + d*(mfe - NachzugAbstandR)*rd;
            if(nsl <= 0.0 || (c - nsl)*d > 0.0) nsl = c;
           }
        }
      int dg = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
      nsl = NormalizeDouble(nsl, dg);
      double pt = SymbolInfoDouble(sym, SYMBOL_POINT);
      if(nsl > 0.0 && (sl <= 0.0 || (nsl - sl)*d > 0.5*pt))
        {
         long stl = SymbolInfoInteger(sym, SYMBOL_TRADE_STOPS_LEVEL), frz = SymbolInfoInteger(sym, SYMBOL_TRADE_FREEZE_LEVEL);
         double minD = (double)MathMax(stl, frz)*pt;
         if((d > 0 && bid - nsl >= minD) || (d < 0 && nsl - ask >= minD))
           {
            trade.SetExpertMagicNumber((ulong)PositionGetInteger(POSITION_MAGIC));
            if(trade.PositionModify(tk, nsl, tp)) PrintFormat("RSI21EK %s: Stop %.*f -> %.*f (Vorlauf %.2f R)", sym, dg, sl, dg, nsl, fav);
            else PrintFormat("RSI21EK %s: Stop-Aenderung abgelehnt (%d %s)", sym, trade.ResultRetcode(), trade.ResultRetcodeDescription());
           }
        }
     }
  }

// Zustands-Variablen geschlossener Positionen loeschen
void Aufraeumen()
  {
   for(int i=GlobalVariablesTotal()-1;i>=0;i--)
     {
      string g = GlobalVariableName(i);
      if(StringFind(g, GVP + "P") != 0) continue;
      int us = StringFind(g, "_", StringLen(GVP) + 1);
      if(us < 0) continue;
      long pid = StringToInteger(StringSubstr(g, StringLen(GVP) + 1, us - StringLen(GVP) - 1));
      bool offen = false;
      for(int k=PositionsTotal()-1;k>=0 && !offen;k--)
        {
         ulong tk = PositionGetTicket(k);
         if(tk > 0 && PositionGetInteger(POSITION_IDENTIFIER) == pid) offen = true;
        }
      if(!offen) GlobalVariableDel(g);
     }
  }

void Anzeige()
  {
   string t = StringFormat("RSI21 EK 1.00 | Equity %.2f | Risiko %.2f %% je Trade | NY %s (Versatz %d h)\n",
                           AccountInfoDouble(ACCOUNT_EQUITY), RiskPct, TimeToString(TimeCurrent() - nyOff*3600, TIME_MINUTES), nyOff);
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
   datetime now = TimeCurrent();
   if(now - offZeit >= 600) { int o = AutoOffset(); if(o != nyOff) { PrintFormat("RSI21EK: NY-Versatz %d -> %d h", nyOff, o); nyOff = o; } offZeit = now; }
   Verwalten();
   for(int s=0;s<NS;s++) Signale(s);
   static datetime auf = 0;
   if(now - auf >= 3600) { Aufraeumen(); auf = now; }
   static datetime anz = 0;
   if(!MQLInfoInteger(MQL_TESTER) && now - anz >= 2) { Anzeige(); anz = now; }
  }

int OnInit()
  {
   if(RiskPct <= 0.0 || StopATR <= 0.0 || Oben <= 50.0 || Unten >= 50.0 || RsiLen < 2 || MaLang < 1 || MaSchnell < 1)
     { Print("RSI21EK: Eingaben ungueltig (RiskPct > 0, StopATR > 0, Oben > 50 > Unten, RsiLen >= 2, SMA >= 1)"); return(INIT_PARAMETERS_INCORRECT); }
   if(Plaetze < 1 || Plaetze > MAXP || MaxVerlusteTag < 0 || ZielNasR < 0.0 || ZielGoldR < 0.0 || EinstandAbR < 0.0 || NachzugAbR < 0.0 || TeilAbR < 0.0)
     { Print("RSI21EK: Eingaben ungueltig (Plaetze 1-5, Ziele/Einstand/Nachzug/Teilgewinn >= 0)"); return(INIT_PARAMETERS_INCORRECT); }
   if(EinstandAbR > 0.0 && EinstandPlusR >= EinstandAbR) { Print("RSI21EK: EinstandPlusR muss unter EinstandAbR liegen"); return(INIT_PARAMETERS_INCORRECT); }
   if(NachzugAbR > 0.0 && (NachzugAbstandR <= 0.0 || NachzugAbstandR > NachzugAbR + 5.0)) { Print("RSI21EK: NachzugAbstandR muss > 0 sein"); return(INIT_PARAMETERS_INCORRECT); }
   if(TeilAbR > 0.0 && (TeilAnteil < 0.1 || TeilAnteil > 0.9)) { Print("RSI21EK: TeilAnteil 0,1-0,9"); return(INIT_PARAMETERS_INCORRECT); }
   if(MarginMaxPct <= 0.0 || MarginMaxPct > 100.0) { Print("RSI21EK: MarginMaxPct 1-100"); return(INIT_PARAMETERS_INCORRECT); }
   if(Plaetze > 1 && AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
     { Print("RSI21EK: Konto ist kein Hedging-Konto - mehrere Positionen je Symbol wuerden verschmelzen. Hedging-Konto verwenden oder Plaetze=1."); return(INIT_FAILED); }
   gSym[0] = GoldSymbol; gSym[1] = NasSymbol;
   wTf[0] = GewichtM15; wTf[1] = GewichtM30; wTf[2] = GewichtH1;
   tfOn[0][0] = GoldM15; tfOn[0][1] = GoldM30; tfOn[0][2] = GoldH1;
   tfOn[1][0] = NasM15;  tfOn[1][1] = NasM30;  tfOn[1][2] = NasH1;
   nyOff = NYOffsetHours;
   nyOff = AutoOffset(); offZeit = TimeCurrent();
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
      regOk[s] = false; regTag[s] = -1; divBucket[s] = 0; divDir[s] = 0; divGut[s] = false; letztesSignal[s] = "";
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
     }
   trade.SetDeviationInPoints(AbweichungPkt);
   PrintFormat("RSI21EK 1.00: %s + %s, NY-Versatz %d h | Risiko %.2f %% der %s je Trade x Gewicht (M15 %.2f, M30 %.2f, H1 %.2f), Gold x%.2f, Margin bis %.0f %% | Plaetze %d, Verluste/Tag %d",
               gSym[0], gSym[1], nyOff, RiskPct, (RisikoVomSaldo ? "Saldo" : "Equity"), GewichtM15, GewichtM30, GewichtH1, GoldFaktor, MarginMaxPct, Plaetze, MaxVerlusteTag);
   PrintFormat("RSI21EK 1.00: Signal RSI(%d) > %.1f / < %.1f, Kreuz %s, NY %.2f-%.2f (NAS) / -%.2f (Gold), Folge %d min, Div %s | Stop %.2f ATR, Ziel NAS %.2f R / Gold %.2f R, Einstand %.2f R, Nachzug %.2f/%.2f R, Zeit %d M5 / %.1f Tage, Wochenende %s",
               RsiLen, Oben, Unten, (KreuzAn ? DoubleToString(KreuzSchwelle, 1) : "aus"), AbNY, NasBisNY, GoldBisNY, FolgeMin, (DivH4 ? "an" : "aus"),
               StopATR, ZielNasR, ZielGoldR, EinstandAbR, NachzugAbR, NachzugAbstandR, ZeitExitM5, ZeitExitTage, (WeSchlussNY > 0.0 ? "schliessen" : "halten"));
   EventSetTimer(1);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   for(int s=0;s<NS;s++)
      for(int t=0;t<NT;t++) { IndicatorRelease(hRsi[s][t]); IndicatorRelease(hAtr[s][t]); }
   Comment("");
  }

void OnTick()  { Durchlauf(); }
void OnTimer() { Durchlauf(); }
//+------------------------------------------------------------------+
