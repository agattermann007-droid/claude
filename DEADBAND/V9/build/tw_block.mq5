//+------------------------------------------------------------------+
//| 9.00 TRENDWENDE-BERICHT (TW) - NUR JOURNAL, KEIN EINFLUSS AUF DEN |
//|  HANDEL. Die Regeln wurden fuer V9 als Sperre bzw. halbes Risiko |
//|  der NAS-Long-Fades (+S0830) und gespiegelt der Gold-Short-Fades |
//|  geprueft und haben die Uebernahmeregeln NICHT bestanden (Bericht|
//|  DEADBAND_V9_Bericht.md). Der Bericht zeigt ihren Stand, damit   |
//|  der Live-Verlauf weiter beobachtet werden kann.                 |
//|  Tagesregeln (nur abgeschlossene Servertage, 17:00-17:00 NY):    |
//|   R1  Schluss < EMA20 und EMA20 faellt                           |
//|   R2  Schluss - Schluss vor 5 Tagen <= -1,5 ATR14                |
//|   R3  Schluss < EMA20 und 5-Tage-Aenderung <= -1,0 ATR14         |
//|   R4  Aenderung des letzten Tages <= -0,75 ATR14                 |
//|   R5  Schluss unter dem Tief der 10 Tage davor, an bis ein       |
//|       Schluss ueber EMA10 liegt                                  |
//|   R6  Rendite 21 Tage < 0 und 252 Tage < 0 (Baer)                |
//|   R7  Rendite 21 Tage < 0 und 252 Tage > 0 (Korrektur)           |
//|   R8  Schluss <= Hoch der letzten 20 Tage - 2 ATR14              |
//|   R9  Tagesspanne 5 Tage / 50 Tage > 1,3 (Vola-Sprung)           |
//|   R10 Rang der 10-Tage-Vola unter 252 Tagen > 0,8                |
//|  Aufwaertsregime spiegelbildlich (R9/R10 symmetrisch).           |
//|  Intraday je NAS-Signal (Noise Area nach Zarattini/Aziz/Barbon   |
//|  2024; O = Open 9:30 NY, PC = Vortagesschluss, sigma = Mittel    |
//|  der letzten 14 Tage von |Schluss/O - 1| je 5-min-Block):        |
//|   NA  Tief der Signalkerze < min(O,PC)*(1-sigma) - 0,25 sigma    |
//|   TR  Schluss/O - 1 < -sigma                                     |
//|  Ablauf: FadeLive merkt sich nur das Signal (TwSignalMerken,     |
//|  keine Kursabfrage vor der Order). Ausgabe am Ende von Durchlauf |
//|  (TwBerichteAusgeben): einmal je Servertag der Tagesstand, dann  |
//|  die gemerkten Signale.                                          |
//|  TwRegeln/TwNoise: Rechenkern wie regime9.py (Replikat 9),       |
//|  mechanisch nach C++ uebersetzt und dagegen geprueft             |
//|  (build/tw_check.py + tw_check.cpp, Ergebnis im Bericht).        |
//+------------------------------------------------------------------+
#define TW_NR 10
#define TW_Q  16
int      twDn[MAXSYM];               // Bitmaske Abwaertsregime (Bit r-1 = Regel r) des letzten abgeschlossenen Servertags
int      twUp[MAXSYM];               // Bitmaske Aufwaertsregime
datetime twTag[MAXSYM];              // Servertag (D1-Kerze) des Stands, 0 = noch keiner
datetime twStand[MAXSYM];            // Beginn des Servertags, fuer den der Tagesbericht lief (0 = noch nicht)
datetime twVersuch = 0;              // letzter Versuch des Tagesberichts (fehlen Kerzen: hoechstens alle 60 s)
int      twQn = 0, twQweg = 0;       // gemerkte Signale dieses Durchlaufs / verworfen (Ueberlauf)
int      twQm[TW_Q], twQd[TW_Q];
datetime twQt[TW_Q];

// gleitender Mittelwert ueber Praefixsummen (wie regime9._sma); ok[i] = false fuer i < len-1
void TwSma(const double &x[], const int n, const int len, double &out[], bool &ok[])
  {
   double cs[];
   ArrayResize(cs, n + 1);
   cs[0] = 0.0;
   for(int i = 0; i < n; i++) cs[i + 1] = cs[i] + x[i];
   for(int i = 0; i < n; i++)
     {
      ok[i] = (i >= len - 1);
      out[i] = ok[i] ? (cs[i + 1] - cs[i + 1 - len]) / len : 0.0;
     }
  }

// Kern: Regel-Flags je Tag (Arrays chronologisch, aeltester zuerst). dn/up = Bitmasken, Bit r-1 = Regel r.
void TwRegeln(const double &o[], const double &h[], const double &l[], const double &c[], const int n, int &dn[], int &up[])
  {
   double ema20[], ema10[], tr[], atr[], rng[], v5[], v50[], lr[], rv10[], rk[];
   bool   okA[], ok5[], ok50[], okRv[], okRk[];
   ArrayResize(ema20, n); ArrayResize(ema10, n); ArrayResize(tr, n); ArrayResize(atr, n); ArrayResize(rng, n);
   ArrayResize(v5, n); ArrayResize(v50, n); ArrayResize(lr, n); ArrayResize(rv10, n); ArrayResize(rk, n);
   ArrayResize(okA, n); ArrayResize(ok5, n); ArrayResize(ok50, n); ArrayResize(okRv, n); ArrayResize(okRk, n);
   if(n <= 0) return;
   double a20 = 2.0 / 21.0, a10 = 2.0 / 11.0;
   ema20[0] = c[0]; ema10[0] = c[0];
   for(int i = 1; i < n; i++)
     {
      ema20[i] = ema20[i - 1] + a20 * (c[i] - ema20[i - 1]);
      ema10[i] = ema10[i - 1] + a10 * (c[i] - ema10[i - 1]);
     }
   tr[0] = h[0] - l[0];
   for(int i = 1; i < n; i++) tr[i] = MathMax(h[i], c[i - 1]) - MathMin(l[i], c[i - 1]);
   TwSma(tr, n, 14, atr, okA);
   for(int i = 0; i < n; i++) rng[i] = h[i] - l[i];
   TwSma(rng, n, 5, v5, ok5);
   TwSma(rng, n, 50, v50, ok50);
   lr[0] = 0.0;
   for(int i = 1; i < n; i++) lr[i] = MathLog(c[i] / c[i - 1]);
   for(int i = 0; i < n; i++)                                      // Std. (ddof 0) von lr[i-9..i], gueltig ab i = 10
     {
      okRv[i] = (i >= 10);
      rv10[i] = 0.0;
      if(!okRv[i]) continue;
      double s = 0.0;
      for(int q = i - 9; q <= i; q++) s += lr[q];
      double mu = s / 10.0, v = 0.0;
      for(int q = i - 9; q <= i; q++) v += (lr[q] - mu) * (lr[q] - mu);
      rv10[i] = MathSqrt(v / 10.0);
     }
   for(int j = 0; j < n; j++)                                      // Rang unter den 252 Tagen davor, ab j = 262
     {
      okRk[j] = (j >= 262);
      rk[j] = 0.0;
      if(!okRk[j]) continue;
      int cnt = 0;
      for(int q = j - 252; q < j; q++) if(rv10[q] < rv10[j]) cnt++;
      rk[j] = cnt / 252.0;
     }
   bool sd = false, su = false;
   for(int j = 0; j < n; j++)
     {
      int bd = 0, bu = 0;
      // R5 Struktur (Zustand)
      if(j >= 10)
        {
         double lo10 = l[j - 10], hi10 = h[j - 10];
         for(int q = j - 9; q < j; q++) { lo10 = MathMin(lo10, l[q]); hi10 = MathMax(hi10, h[q]); }
         if(c[j] < lo10) sd = true; else if(sd && c[j] > ema10[j]) sd = false;
         if(c[j] > hi10) su = true; else if(su && c[j] < ema10[j]) su = false;
        }
      else
        {
         if(sd && c[j] > ema10[j]) sd = false;
         if(su && c[j] < ema10[j]) su = false;
        }
      if(j >= 1)
        {
         if(c[j] < ema20[j] && ema20[j] < ema20[j - 1]) bd |= 1;
         if(c[j] > ema20[j] && ema20[j] > ema20[j - 1]) bu |= 1;
        }
      if(okA[j] && j >= 5)
        {
         double r5 = c[j] - c[j - 5];
         if(r5 <= -1.5 * atr[j]) bd |= 2;
         if(r5 >= 1.5 * atr[j]) bu |= 2;
         if(c[j] < ema20[j] && r5 <= -1.0 * atr[j]) bd |= 4;
         if(c[j] > ema20[j] && r5 >= 1.0 * atr[j]) bu |= 4;
        }
      if(okA[j] && j >= 1)
        {
         double r1 = c[j] - c[j - 1];
         if(r1 <= -0.75 * atr[j]) bd |= 8;
         if(r1 >= 0.75 * atr[j]) bu |= 8;
        }
      if(sd) bd |= 16;
      if(su) bu |= 16;
      if(j >= 252)
        {
         double fast = c[j] / c[j - 21] - 1.0, slow = c[j] / c[j - 252] - 1.0;
         if(fast < 0.0 && slow < 0.0) bd |= 32;
         if(fast > 0.0 && slow > 0.0) bu |= 32;
         if(fast < 0.0 && slow > 0.0) bd |= 64;
         if(fast > 0.0 && slow < 0.0) bu |= 64;
        }
      if(okA[j] && j >= 19)
        {
         double hi20 = h[j], lo20 = l[j];
         for(int q = j - 19; q < j; q++) { hi20 = MathMax(hi20, h[q]); lo20 = MathMin(lo20, l[q]); }
         if(c[j] <= hi20 - 2.0 * atr[j]) bd |= 128;
         if(c[j] >= lo20 + 2.0 * atr[j]) bu |= 128;
        }
      if(ok5[j] && ok50[j] && v50[j] > 0.0 && v5[j] / v50[j] > 1.3) { bd |= 256; bu |= 256; }
      if(okRk[j] && rk[j] > 0.8) { bd |= 512; bu |= 512; }
      dn[j] = bd; up[j] = bu;
     }
  }

// Kern: Noise Area fuer M5-Kerze k (Arrays chronologisch, ny = NY-Minuten des Kerzenbeginns). false = kein Wert
// (Kerze ausserhalb 9:30-16:00 NY, Tag ohne 9:30-Kerze oder weniger als 15 vollstaendige Vortage in den Daten).
bool TwNoise(const long &ny[], const double &o[], const double &l[], const double &c[], const int n, const int k, bool &na, bool &tr)
  {
   na = false; tr = false;
   if(k < 0 || k >= n) return false;
   long dk = (long)MathFloor((double)ny[k] / 1440.0);
   int mk = (int)(ny[k] - dk * 1440);
   if(mk < 570 || mk >= 960) return false;
   // Tagestabelle: je NY-Tag O, letzter Schluss 9:30-16:00, |Schluss/O - 1| je 5-min-Block (-1 = kein Wert)
   double tO[], tLast[], tBl[];
   int    nt = 0, qk = -1;
   int    i = 0;
   while(i < n)
     {
      long d = (long)MathFloor((double)ny[i] / 1440.0);
      int j = i;
      while(j < n && (long)MathFloor((double)ny[j] / 1440.0) == d) j++;
      int f = -1, la = -1;
      for(int q = i; q < j; q++)
        {
         int m = (int)(ny[q] - d * 1440);
         if(m >= 570 && m < 960) { if(f < 0) f = q; la = q; }
        }
      if(f >= 0 && (int)(ny[f] - d * 1440) <= 575)
        {
         ArrayResize(tO, nt + 1); ArrayResize(tLast, nt + 1); ArrayResize(tBl, (nt + 1) * 78);
         tO[nt] = o[f]; tLast[nt] = c[la];
         for(int b = 0; b < 78; b++) tBl[nt * 78 + b] = -1.0;
         for(int q = f; q <= la; q++)
           {
            int m = (int)(ny[q] - d * 1440);
            if(m >= 570 && m < 960) tBl[nt * 78 + (m - 570) / 5] = MathAbs(c[q] / o[f] - 1.0);
           }
         if(d == dk) qk = nt;
         nt++;
        }
      i = j;
     }
   if(qk < 15) return false;
   int bk = (mk - 570) / 5;
   double s = 0.0; int cnt = 0;
   for(int q = qk - 14; q < qk; q++) { double v = tBl[q * 78 + bk]; if(v >= 0.0) { s += v; cnt++; } }
   if(cnt == 0) return false;
   double sig = s / cnt;
   double O = tO[qk], pc = tLast[qk - 1];
   double ref = MathMin(O, pc);
   na = (l[k] < ref * (1.0 - sig) - 0.25 * sig * ref);
   tr = (c[k] / O - 1.0 < -sig);
   return true;
  }

string TwListe(const int maske)
  {
   string t = "";
   for(int r = 1; r <= TW_NR; r++)
     {
      if(((maske >> (r - 1)) & 1) != 1) continue;
      if(StringLen(t) > 0) t += ",";
      t += "R" + IntegerToString(r);
     }
   if(StringLen(t) == 0) t = "-";
   return t;
  }

// Stand der Tagesregeln je Symbol aus den abgeschlossenen Servertagen (D1-Kerzen vor dem heutigen Servertag).
// Je Symbol einmal je Servertag; fehlen D1-Kerzen, neuer Versuch in einem spaeteren Durchlauf (fruehestens nach 60 s).
void TwTagesbericht(const datetime heute0)
  {
   for(int k = 0; k < nSym; k++)
     {
      if(twStand[k] == heute0) continue;
      MqlRates r[];
      ArraySetAsSeries(r, false);
      int n0 = CopyRates(S[k].sym, PERIOD_D1, 0, 401, r);
      if(n0 <= 0) { PrintFormat("DEADBAND9 TW %s: keine D1-Kerzen (Fehler %d) - neuer Versuch spaeter", S[k].sym, GetLastError()); continue; }
      twStand[k] = heute0;
      int n = n0;
      while(n > 0 && r[n - 1].time >= heute0) n--;                      // nur abgeschlossene Servertage
      if(n < 30) { PrintFormat("DEADBAND9 TW %s: nur %d abgeschlossene D1-Kerzen - kein Tagesstand", S[k].sym, n); continue; }
      double o[], h[], l[], c[];
      int dn[], up[];
      ArrayResize(o, n); ArrayResize(h, n); ArrayResize(l, n); ArrayResize(c, n); ArrayResize(dn, n); ArrayResize(up, n);
      for(int i = 0; i < n; i++) { o[i] = r[i].open; h[i] = r[i].high; l[i] = r[i].low; c[i] = r[i].close; }
      TwRegeln(o, h, l, c, n, dn, up);
      twDn[k] = dn[n - 1]; twUp[k] = up[n - 1]; twTag[k] = r[n - 1].time;
      PrintFormat("DEADBAND9 TW %s Servertag %s: Abwaertsregime [%s] | Aufwaertsregime [%s] | %d D1-Kerzen%s | nur Bericht, kein Einfluss auf den Handel",
                  S[k].sym, TimeToString(r[n - 1].time, TIME_DATE), TwListe(dn[n - 1]), TwListe(up[n - 1]), n,
                  (n < 263 ? " (R6/R7/R10 brauchen 253/263 Tage)" : ""));
     }
  }

// je Live-Signal eines Fade-artigen Moduls: Tagesregeln in Gegenrichtung und (NAS) Noise Area der Signalkerze.
// tSig = Zeit der Einstiegskerze; die letzte M5-Kerze vor tSig ist die Signalkerze.
void TwSignalBericht(const int m, const int d, const datetime tSig)
  {
   int k = F[m].k;
   if(k < 0 || k >= nSym) return;
   string intra = "-";
   string su = S[k].sym;
   StringToUpper(su);
   if(StringFind(su, "NAS") >= 0)
     {
      MqlRates r[];
      ArraySetAsSeries(r, false);
      int n = CopyRates(S[k].sym, PERIOD_M5, tSig - 45 * 86400, tSig - 1, r);   // bis einschliesslich Signalkerze
      if(n > 0 && tSig - r[n - 1].time > 3600)                                 // Luecke: letzte Kerze ist nicht die Signalkerze
         intra = StringFormat("M5-Historie endet %s vor der Signalkerze", TimeToString(r[n - 1].time, TIME_DATE|TIME_MINUTES));
      else if(n > 0)
        {
         long ny[]; double o[], l[], c[];
         ArrayResize(ny, n); ArrayResize(o, n); ArrayResize(l, n); ArrayResize(c, n);
         for(int i = 0; i < n; i++) { ny[i] = FadeNyMin(r[i].time); o[i] = r[i].open; l[i] = r[i].low; c[i] = r[i].close; }
         bool na = false, tr = false;
         if(TwNoise(ny, o, l, c, n, n - 1, na, tr)) intra = StringFormat("NA %s, TR %s", (na ? "JA" : "nein"), (tr ? "JA" : "nein"));
         else intra = "Noise Area ohne Wert (ausserhalb 9:30-16:00 NY oder zu wenig Historie)";
        }
      else intra = StringFormat("keine M5-Kerzen (Fehler %d)", GetLastError());
     }
   int maske = (d > 0 ? twDn[k] : twUp[k]);
   PrintFormat("DEADBAND9 TW Signal %s %s %s: Tagesregeln %s [%s] (Stand %s) | Intraday %s | nur Bericht, V9 handelt wie 8.10",
               FadeName(m), S[k].sym, (d > 0 ? "LONG" : "SHORT"), (d > 0 ? "abwaerts" : "aufwaerts"), TwListe(maske),
               (twTag[k] > 0 ? TimeToString(twTag[k], TIME_DATE) : "-"), intra);
  }

// aus FadeLive: Signal nur merken (keine Kursabfrage vor der Order)
void TwSignalMerken(const int m, const int d, const datetime tSig)
  {
   if(twQn >= TW_Q) { twQweg++; return; }
   twQm[twQn] = m; twQd[twQn] = d; twQt[twQn] = tSig; twQn++;
  }

// am Ende von Durchlauf: Tagesstand (einmal je Servertag), dann die gemerkten Signale
void TwBerichteAusgeben()
  {
   datetime jetzt = TimeCurrent();
   if(jetzt <= 0) return;
   datetime heute0 = jetzt - jetzt % 86400;                         // Beginn des heutigen Servertags (GFT: 17:00 NY)
   bool offen = false;
   for(int k = 0; k < nSym; k++) if(twStand[k] != heute0) offen = true;
   if(offen && (twQn > 0 || jetzt - twVersuch >= 60)) { twVersuch = jetzt; TwTagesbericht(heute0); }
   for(int q = 0; q < twQn; q++) TwSignalBericht(twQm[q], twQd[q], twQt[q]);
   if(twQweg > 0) PrintFormat("DEADBAND9 TW: %d Signal-Berichte ausgelassen (mehr als %d in einem Durchlauf)", twQweg, TW_Q);
   twQn = 0; twQweg = 0;
  }
