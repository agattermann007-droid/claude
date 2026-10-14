//+------------------------------------------------------------------+
//| DEADBAND_Daten_Export.mq5  (Skript, nur lesend)                  |
//| Forschung DEADBAND V8.10, Stufe 0 (research/PLAN.md, Abschn. 10)|
//| Exportiert Kerzen M5/M15 (und M1 fuer Gold/NAS) mit Spread im    |
//| Format "Balken exportieren" von MT5 sowie je Symbol eine         |
//| Spezifikation nach MQL5\Files\DEADBAND_Export\.                  |
//| Keine Orders, keine Kontonummer, kein Servername in den Dateien. |
//| Start: im GFT-Terminal einen leeren Chart oeffnen (z. B. EURUSD) |
//| und das Skript darauf ziehen. Nicht auf den Chart des EA.        |
//+------------------------------------------------------------------+
#property copyright "DEADBAND Forschung"
#property version   "1.00"
#property script_show_inputs

input string   Gruppen      = "XAUUSD;NAS100;XAGUSD;USOIL|WTI|XTI|CRUDE;BTCUSD;DXY|USDX|DOLLAR"; // Gruppen mit ; getrennt, Alternativen mit |
input string   M1Gruppen    = "XAUUSD;NAS100";   // Gruppen, die zusaetzlich M1 bekommen
input datetime VonM5M15     = D'2019.01.01';     // Beginn M5/M15 (so frueh wie der Server liefert)
input datetime VonM1        = D'2025.06.01';     // Beginn M1
input int      MaxJeGruppe  = 3;                 // hoechstens so viele Symbole je Gruppe
input int      LadeSekunden = 180;               // Wartezeit auf das Nachladen der Historie je Symbol und Zeitrahmen

string OUT = "DEADBAND_Export\\";
int    logH = INVALID_HANDLE;

void Log(const string txt)
  {
   Print("DEADBAND-EXPORT: ", txt);
   if(logH != INVALID_HANDLE) FileWriteString(logH, txt + "\r\n");
  }

string Sauber(const string s)
  {
   string r = s;
   for(int i=0;i<StringLen(r);i++)
     {
      ushort c = StringGetCharacter(r, i);
      bool ok = (c >= '0' && c <= '9') || (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || c == '.' || c == '_' || c == '-';
      if(!ok) StringSetCharacter(r, i, '_');
     }
   return r;
  }

// Alle Symbole des Servers (nicht nur Marktuebersicht), deren Name eine der Alternativen enthaelt
int SymboleSuchen(const string gruppe, string &treffer[])
  {
   ArrayResize(treffer, 0);
   string alt[];
   int na = StringSplit(gruppe, StringGetCharacter("|", 0), alt);
   int n = SymbolsTotal(false);
   for(int i=0;i<n;i++)
     {
      string s = SymbolName(i, false);
      string u = s; StringToUpper(u);
      bool passt = false;
      for(int a=0;a<na;a++)
        {
         string x = alt[a]; StringTrimLeft(x); StringTrimRight(x); StringToUpper(x);
         if(StringLen(x) > 0 && StringFind(u, x) >= 0) { passt = true; break; }
        }
      if(!passt) continue;
      int m = ArraySize(treffer);
      if(m >= MaxJeGruppe) { Log("Gruppe " + gruppe + ": weiteres Symbol " + s + " nicht exportiert (MaxJeGruppe)"); continue; }
      ArrayResize(treffer, m + 1);
      treffer[m] = s;
     }
   return ArraySize(treffer);
  }

// Historie anstossen und warten, bis sie ab 'von' (oder ab dem ersten Datum des Servers) im Terminal liegt
bool HistorieLaden(const string sym, const ENUM_TIMEFRAMES tf, const datetime von)
  {
   uint t0 = GetTickCount();
   while(!IsStopped() && GetTickCount() - t0 < (uint)LadeSekunden*1000)
     {
      datetime tt[];
      CopyTime(sym, tf, von, TimeCurrent(), tt);
      datetime erst = (datetime)SeriesInfoInteger(sym, tf, SERIES_FIRSTDATE);
      datetime srv  = (datetime)SeriesInfoInteger(sym, tf, SERIES_SERVER_FIRSTDATE);
      bool sync = (bool)SeriesInfoInteger(sym, tf, SERIES_SYNCHRONIZED);
      if(erst > 0 && erst <= von + 3*86400 && sync) return true;
      if(srv > 0 && erst > 0 && erst <= srv + 3*86400 && sync) return true;
      Sleep(500);
     }
   return false;
  }

string TfName(const ENUM_TIMEFRAMES tf)
  {
   if(tf == PERIOD_M1) return "M1";
   if(tf == PERIOD_M5) return "M5";
   return "M15";
  }

// Kerzen in 60-Tage-Bloecken schreiben (Bloecke ueberlappen, doppelte Kerzen werden ueber die Zeit ausgelassen)
int Exportieren(const string sym, const ENUM_TIMEFRAMES tf, const datetime von)
  {
   bool voll = HistorieLaden(sym, tf, von);
   string fn = OUT + Sauber(sym) + "_" + TfName(tf) + ".csv";
   int fh = FileOpen(fn, FILE_WRITE|FILE_TXT|FILE_ANSI);
   if(fh == INVALID_HANDLE) { Log("FEHLER: Datei " + fn + " nicht schreibbar, Code " + IntegerToString(GetLastError())); return -1; }
   FileWriteString(fh, "<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\r\n");
   int dg = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
   datetime bis = TimeCurrent();
   datetime t = von, letzte = 0, erste = 0;
   int n = 0;
   while(t < bis && !IsStopped())
     {
      datetime t1 = t + 60*86400;
      if(t1 > bis) t1 = bis;
      MqlRates r[];
      int k = -1;
      for(int v=0; v<20 && k < 0; v++) { k = CopyRates(sym, tf, t, t1, r); if(k < 0) Sleep(300); }
      for(int i=0;i<k;i++)
        {
         if(r[i].time <= letzte) continue;
         string z = TimeToString(r[i].time, TIME_DATE) + "\t" + TimeToString(r[i].time, TIME_SECONDS) + "\t"
                    + DoubleToString(r[i].open, dg) + "\t" + DoubleToString(r[i].high, dg) + "\t"
                    + DoubleToString(r[i].low, dg) + "\t" + DoubleToString(r[i].close, dg) + "\t"
                    + IntegerToString(r[i].tick_volume) + "\t" + IntegerToString(r[i].real_volume) + "\t"
                    + IntegerToString(r[i].spread) + "\r\n";
         FileWriteString(fh, z);
         if(erste == 0) erste = r[i].time;
         letzte = r[i].time; n++;
        }
      t = t1;
     }
   FileClose(fh);
   Log(sym + " " + TfName(tf) + ": " + IntegerToString(n) + " Kerzen " + (n > 0 ? TimeToString(erste) + " bis " + TimeToString(letzte) : "-")
       + (voll ? "" : " (WARNUNG: Historie nicht vollstaendig nachgeladen - Max. Balken im Chart = Unbegrenzt? erneut starten)"));
   return n;
  }

string SwapModeText(const long m)
  {
   return EnumToString((ENUM_SYMBOL_SWAP_MODE)m);
  }

// Spezifikation und gebuchte Kommission je Lot (aus der eigenen Deal-Historie, ohne Kontonummer)
void Spezifikation(const string sym)
  {
   string fn = OUT + Sauber(sym) + "_spec.txt";
   int fh = FileOpen(fn, FILE_WRITE|FILE_TXT|FILE_ANSI);
   if(fh == INVALID_HANDLE) { Log("FEHLER: Datei " + fn + " nicht schreibbar"); return; }
   string z = "";
   z += "name=" + sym + "\r\n";
   z += "description=" + SymbolInfoString(sym, SYMBOL_DESCRIPTION) + "\r\n";
   z += "path=" + SymbolInfoString(sym, SYMBOL_PATH) + "\r\n";
   z += "currency_base=" + SymbolInfoString(sym, SYMBOL_CURRENCY_BASE) + "\r\n";
   z += "currency_profit=" + SymbolInfoString(sym, SYMBOL_CURRENCY_PROFIT) + "\r\n";
   z += "currency_margin=" + SymbolInfoString(sym, SYMBOL_CURRENCY_MARGIN) + "\r\n";
   z += "digits=" + IntegerToString(SymbolInfoInteger(sym, SYMBOL_DIGITS)) + "\r\n";
   z += "point=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_POINT), 10) + "\r\n";
   z += "contract_size=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_TRADE_CONTRACT_SIZE), 6) + "\r\n";
   z += "tick_size=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_SIZE), 10) + "\r\n";
   z += "tick_value=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE), 10) + "\r\n";
   z += "volume_min=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN), 4) + "\r\n";
   z += "volume_step=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP), 4) + "\r\n";
   z += "volume_max=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX), 4) + "\r\n";
   long sm = SymbolInfoInteger(sym, SYMBOL_SWAP_MODE);
   z += "swap_mode=" + IntegerToString(sm) + " " + SwapModeText(sm) + "\r\n";
   z += "swap_long=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_SWAP_LONG), 6) + "\r\n";
   z += "swap_short=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_SWAP_SHORT), 6) + "\r\n";
   long r3 = SymbolInfoInteger(sym, SYMBOL_SWAP_ROLLOVER3DAYS);
   z += "swap_rollover3days=" + IntegerToString(r3) + " " + EnumToString((ENUM_DAY_OF_WEEK)r3) + "\r\n";
   long cm = SymbolInfoInteger(sym, SYMBOL_TRADE_CALC_MODE);
   z += "calc_mode=" + IntegerToString(cm) + " " + EnumToString((ENUM_SYMBOL_CALC_MODE)cm) + "\r\n";
   z += "stops_level=" + IntegerToString(SymbolInfoInteger(sym, SYMBOL_TRADE_STOPS_LEVEL)) + "\r\n";
   z += "freeze_level=" + IntegerToString(SymbolInfoInteger(sym, SYMBOL_TRADE_FREEZE_LEVEL)) + "\r\n";
   z += "spread_now=" + IntegerToString(SymbolInfoInteger(sym, SYMBOL_SPREAD)) + "\r\n";
   z += "margin_initial=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_MARGIN_INITIAL), 4) + "\r\n";
   z += "margin_hedged=" + DoubleToString(SymbolInfoDouble(sym, SYMBOL_MARGIN_HEDGED), 4) + "\r\n";
   double m1 = 0.0;
   double bid = SymbolInfoDouble(sym, SYMBOL_BID);
   if(bid > 0.0 && OrderCalcMargin(ORDER_TYPE_BUY, sym, 1.0, bid, m1)) z += "margin_1lot_now=" + DoubleToString(m1, 2) + "\r\n";
   // Handelszeiten je Wochentag (Serverzeit)
   for(int d=0; d<7; d++)
     {
      string s = "";
      datetime a = 0, b = 0;
      for(uint q=0; q<10; q++)
        {
         if(!SymbolInfoSessionTrade(sym, (ENUM_DAY_OF_WEEK)d, q, a, b)) break;
         s += (StringLen(s) > 0 ? "," : "") + TimeToString(a, TIME_MINUTES) + "-" + TimeToString(b, TIME_MINUTES);
        }
      z += "session_" + IntegerToString(d) + "=" + s + "\r\n";
     }
   // gebuchte Kommission je Lot (Einstieg / Ausstieg getrennt)
   double ci = 0.0, vi = 0.0, co = 0.0, vo = 0.0;
   int ni = 0, no = 0;
   if(HistorySelect(0, TimeCurrent() + 86400))
     {
      int nd = HistoryDealsTotal();
      for(int i=0;i<nd;i++)
        {
         ulong tk = HistoryDealGetTicket(i);
         if(tk == 0 || HistoryDealGetString(tk, DEAL_SYMBOL) != sym) continue;
         long ty = HistoryDealGetInteger(tk, DEAL_TYPE);
         if(ty != DEAL_TYPE_BUY && ty != DEAL_TYPE_SELL) continue;
         double v = HistoryDealGetDouble(tk, DEAL_VOLUME);
         double c = HistoryDealGetDouble(tk, DEAL_COMMISSION);
         if(HistoryDealGetInteger(tk, DEAL_ENTRY) == DEAL_ENTRY_IN) { ci += c; vi += v; ni++; }
         else { co += c; vo += v; no++; }
        }
     }
   z += "commission_in_per_lot=" + (vi > 0.0 ? DoubleToString(ci/vi, 4) : "unbekannt") + " (" + IntegerToString(ni) + " Deals)\r\n";
   z += "commission_out_per_lot=" + (vo > 0.0 ? DoubleToString(co/vo, 4) : "unbekannt") + " (" + IntegerToString(no) + " Deals)\r\n";
   ENUM_TIMEFRAMES tfs[3] = {PERIOD_M1, PERIOD_M5, PERIOD_M15};
   for(int i=0;i<3;i++)
     {
      z += "server_firstdate_" + TfName(tfs[i]) + "=" + TimeToString((datetime)SeriesInfoInteger(sym, tfs[i], SERIES_SERVER_FIRSTDATE)) + "\r\n";
      z += "terminal_firstdate_" + TfName(tfs[i]) + "=" + TimeToString((datetime)SeriesInfoInteger(sym, tfs[i], SERIES_FIRSTDATE)) + "\r\n";
     }
   FileWriteString(fh, z);
   FileClose(fh);
  }

void OnStart()
  {
   FolderCreate("DEADBAND_Export");
   logH = FileOpen(OUT + "export_log.txt", FILE_WRITE|FILE_TXT|FILE_ANSI);
   Log("Start " + TimeToString(TimeLocal(), TIME_DATE|TIME_SECONDS) + " (PC-Zeit), Serverzeit " + TimeToString(TimeTradeServer(), TIME_DATE|TIME_SECONDS));
   Log("Server minus GMT in Stunden: " + DoubleToString((double)(TimeTradeServer() - TimeGMT())/3600.0, 2));
   Log("Max. Balken im Chart: " + IntegerToString(TerminalInfoInteger(TERMINAL_MAXBARS)) + " | Kontowaehrung " + AccountInfoString(ACCOUNT_CURRENCY)
       + " | Hebel 1:" + IntegerToString(AccountInfoInteger(ACCOUNT_LEVERAGE)));
   // Symbolliste des Servers (fuer die Namenssuche)
   int sh = FileOpen(OUT + "symbole.txt", FILE_WRITE|FILE_TXT|FILE_ANSI);
   if(sh != INVALID_HANDLE)
     {
      int n = SymbolsTotal(false);
      for(int i=0;i<n;i++)
        {
         string s = SymbolName(i, false);
         FileWriteString(sh, s + "\t" + SymbolInfoString(s, SYMBOL_DESCRIPTION) + "\t" + SymbolInfoString(s, SYMBOL_PATH) + "\r\n");
        }
      FileClose(sh);
     }
   string gr[];
   int ng = StringSplit(Gruppen, StringGetCharacter(";", 0), gr);
   string m1g[];
   int nm1 = StringSplit(M1Gruppen, StringGetCharacter(";", 0), m1g);
   for(int g=0; g<ng && !IsStopped(); g++)
     {
      string grp = gr[g]; StringTrimLeft(grp); StringTrimRight(grp);
      if(StringLen(grp) == 0) continue;
      string tr[];
      if(SymboleSuchen(grp, tr) == 0) { Log("Gruppe " + grp + ": kein Symbol gefunden"); continue; }
      bool mitM1 = false;
      for(int q=0;q<nm1;q++) { string x = m1g[q]; StringTrimLeft(x); StringTrimRight(x); if(x == grp) mitM1 = true; }
      for(int i=0; i<ArraySize(tr) && !IsStopped(); i++)
        {
         string s = tr[i];
         if(!SymbolSelect(s, true)) { Log("FEHLER: " + s + " nicht auswaehlbar"); continue; }
         Log("Gruppe " + grp + ": exportiere " + s);
         Exportieren(s, PERIOD_M5, VonM5M15);
         Exportieren(s, PERIOD_M15, VonM5M15);
         if(mitM1) Exportieren(s, PERIOD_M1, VonM1);
         Spezifikation(s);
        }
     }
   Log("Ende " + TimeToString(TimeLocal(), TIME_DATE|TIME_SECONDS) + " - Ordner MQL5\\Files\\DEADBAND_Export");
   if(logH != INVALID_HANDLE) FileClose(logH);
   logH = INVALID_HANDLE;
   Alert("DEADBAND-Export fertig: MQL5\\Files\\DEADBAND_Export (Protokoll export_log.txt)");
  }
//+------------------------------------------------------------------+
