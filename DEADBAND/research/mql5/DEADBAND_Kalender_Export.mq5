//+------------------------------------------------------------------+
//| DEADBAND_Kalender_Export.mq5  (Skript, nur lesend)               |
//| Forschung DEADBAND V8.10 (research/PLAN.md, Abschnitt 9.1)      |
//| Der Strategietester hat keinen Wirtschaftskalender. Dieses       |
//| Skript schreibt die Kalenderhistorie eines Landes einmalig nach  |
//| MQL5\Files\DEADBAND_Export\kalender_<Land>.csv (UTF-8, Tabs).    |
//| Zeiten = Serverzeit (wie CalendarValueHistory sie liefert).      |
//| Werte: Ist/Prognose/Vorwert/korrigiert als Zahl, leer = fehlt.   |
//+------------------------------------------------------------------+
#property copyright "DEADBAND Forschung"
#property version   "1.00"
#property script_show_inputs

input string   Land     = "US";              // ISO-Laendercode
input datetime Von      = D'2019.01.01';     // Beginn
input int      TageVoraus = 35;              // auch kommende Termine bis heute + X Tage

string OUT = "DEADBAND_Export\\";

string Wert(const long v)
  {
   if(v == LONG_MIN) return "";
   return DoubleToString((double)v/1000000.0, 6);
  }

string Bereinigt(const string s)
  {
   string r = s;
   StringReplace(r, "\t", " ");
   StringReplace(r, "\r", " ");
   StringReplace(r, "\n", " ");
   return r;
  }

void OnStart()
  {
   FolderCreate("DEADBAND_Export");
   // 1) Ereignisliste des Landes
   MqlCalendarEvent ev[];
   int ne = CalendarEventByCountry(Land, ev);
   int eh = FileOpen(OUT + "kalender_" + Land + "_ereignisse.csv", FILE_WRITE|FILE_TXT|FILE_ANSI, '\t', CP_UTF8);
   if(eh == INVALID_HANDLE) { Print("DEADBAND-KALENDER: Datei nicht schreibbar, Code ", GetLastError()); return; }
   FileWriteString(eh, "event_id\tcode\tname\timportance\tsector\tfrequency\ttime_mode\tunit\tmultiplier\tdigits\r\n");
   for(int i=0;i<ne;i++)
     {
      string z = IntegerToString((long)ev[i].id) + "\t" + Bereinigt(ev[i].event_code) + "\t" + Bereinigt(ev[i].name) + "\t"
                 + IntegerToString((int)ev[i].importance) + "\t" + IntegerToString((int)ev[i].sector) + "\t"
                 + IntegerToString((int)ev[i].frequency) + "\t" + IntegerToString((int)ev[i].time_mode) + "\t"
                 + IntegerToString((int)ev[i].unit) + "\t" + IntegerToString((int)ev[i].multiplier) + "\t"
                 + IntegerToString((int)ev[i].digits) + "\r\n";
      FileWriteString(eh, z);
     }
   FileClose(eh);
   if(ne <= 0) Print("DEADBAND-KALENDER: keine Ereignisse fuer ", Land, " (Code ", GetLastError(), ") - Kalender im Terminal geladen? (Werkzeuge > Wirtschaftskalender)");
   // 2) Werte monatsweise (grosse Zeitraeume liefert der Kalender nicht vollstaendig in einem Aufruf)
   int vh = FileOpen(OUT + "kalender_" + Land + ".csv", FILE_WRITE|FILE_TXT|FILE_ANSI, '\t', CP_UTF8);
   if(vh == INVALID_HANDLE) { Print("DEADBAND-KALENDER: Datei nicht schreibbar, Code ", GetLastError()); return; }
   FileWriteString(vh, "server_time\tvalue_id\tevent_id\tcode\tname\timportance\ttime_mode\tactual\tforecast\tprev\trevised_prev\timpact\r\n");
   datetime bis = TimeTradeServer() + (datetime)TageVoraus*86400;
   datetime t = Von;
   int n = 0, leer = 0;
   while(t < bis && !IsStopped())
     {
      MqlDateTime st; TimeToStruct(t, st);
      st.mon += 1; if(st.mon > 12) { st.mon = 1; st.year += 1; }
      st.day = 1; st.hour = 0; st.min = 0; st.sec = 0;
      datetime t1 = StructToTime(st);
      if(t1 > bis) t1 = bis;
      MqlCalendarValue v[];
      int k = -1;
      for(int r=0; r<10 && k < 0; r++) { k = CalendarValueHistory(v, t, t1 - 1, Land, NULL); if(k < 0) Sleep(500); }
      if(k <= 0) leer++;
      for(int i=0;i<k;i++)
        {
         MqlCalendarEvent e;
         string code = "", name = ""; int imp = -1, tm = -1;
         if(CalendarEventById(v[i].event_id, e)) { code = Bereinigt(e.event_code); name = Bereinigt(e.name); imp = (int)e.importance; tm = (int)e.time_mode; }
         string z = TimeToString(v[i].time, TIME_DATE|TIME_SECONDS) + "\t" + IntegerToString((long)v[i].id) + "\t"
                    + IntegerToString((long)v[i].event_id) + "\t" + code + "\t" + name + "\t" + IntegerToString(imp) + "\t"
                    + IntegerToString(tm) + "\t" + Wert(v[i].actual_value) + "\t" + Wert(v[i].forecast_value) + "\t"
                    + Wert(v[i].prev_value) + "\t" + Wert(v[i].revised_prev_value) + "\t" + IntegerToString((int)v[i].impact_type) + "\r\n";
         FileWriteString(vh, z);
         n++;
        }
      t = t1;
     }
   FileClose(vh);
   Print("DEADBAND-KALENDER: ", n, " Termine (", Land, ") ab ", TimeToString(Von, TIME_DATE), ", Monate ohne Werte: ", leer,
         " | Serverzeit ", TimeToString(TimeTradeServer(), TIME_DATE|TIME_SECONDS), " | Ordner MQL5\\Files\\DEADBAND_Export");
   Alert("DEADBAND-Kalender fertig: ", n, " Termine");
  }
//+------------------------------------------------------------------+
