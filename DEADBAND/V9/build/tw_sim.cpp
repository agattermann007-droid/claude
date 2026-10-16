// DEADBAND V9 - C++-Geruest fuer den GESAMTEN neuen MQL5-Block (tw_block.mq5): MQL-Funktionen als Attrappen
// (CopyRates aus Replikat-Kursen, PrintFormat -> stdout, TimeCurrent gesetzt). tw_alles.inc erzeugt tw_sim.py
// mechanisch aus build/tw_block.mq5 (Globale + alle Funktionen). Ablauf aus einer Ereignisdatei:
//   T <servertime>               TimeCurrent setzen und TwBerichteAusgeben() (Ende eines Durchlaufs)
//   S <servertime> <m> <d>       TimeCurrent setzen, TwSignalMerken(m, d, tSig = servertime), dann TwBerichteAusgeben()
// Aufruf: tw_sim <daten.bin> <ereignisse.txt> <module.txt>
#include <cstdio>
#include <cstdint>
#include <cmath>
#include <cstring>
#include <ctime>
#include <vector>
#include <string>
#include <algorithm>

typedef long datetime;
typedef std::string string;
#define MAXSYM 8
#define PERIOD_D1 1440
#define PERIOD_M5 5
#define TIME_DATE 1
#define TIME_MINUTES 2
static const int NYOffsetHours = 7;

struct MqlRates { datetime time; double open, high, low, close; long tick_volume; int spread; long real_volume; };
struct SymState { string sym; };
struct FadeDef  { int k; string name; };
SymState S[MAXSYM];
FadeDef  F[32];
int      nSym = 0;
static datetime simJetzt = 0;
static int      simFehler = 0;
static std::vector<MqlRates> simD1[MAXSYM], simM5[MAXSYM];

template <class T> static void ArrayResize(std::vector<T> &x, int n) { x.resize(n > 0 ? n : 0); }
template <class T> static void ArraySetAsSeries(std::vector<T> &, bool) {}
static double MathMax(double a, double b) { return std::max(a, b); }
static double MathMin(double a, double b) { return std::min(a, b); }
static double MathLog(double a) { return std::log(a); }
static double MathSqrt(double a) { return std::sqrt(a); }
static double MathAbs(double a) { return std::fabs(a); }
static double MathFloor(double a) { return std::floor(a); }
static datetime TimeCurrent() { return simJetzt; }
static int GetLastError() { return simFehler; }
static int StringLen(const string &s) { return (int)s.size(); }
static string IntegerToString(long v) { return std::to_string(v); }
static bool StringToUpper(string &s) { for(auto &ch : s) ch = (char)toupper((unsigned char)ch); return true; }
static int StringFind(const string &s, const string &w) { size_t p = s.find(w); return p == string::npos ? -1 : (int)p; }
static string TimeToString(datetime t, int) { time_t x = (time_t)t; struct tm g; gmtime_r(&x, &g); char b[32]; strftime(b, sizeof b, "%Y.%m.%d", &g); return b; }
template <class T> static T conv(const T &x) { return x; }
static const char *conv(const string &s) { return s.c_str(); }
template <class... A> static void PrintFormat(const char *f, const A &...a) { printf(f, conv(a)...); printf("\n"); }
template <class... A> static string StringFormat(const char *f, const A &...a) { char b[4096]; snprintf(b, sizeof b, f, conv(a)...); return b; }
static int symIdx(const string &s) { for(int k = 0; k < nSym; k++) if(S[k].sym == s) return k; return -1; }
// CopyRates nach Position (0 = juengste Kerze, auch die laufende) - Ergebnis chronologisch
static int CopyRates(const string &s, int tf, int start, int count, std::vector<MqlRates> &r)
  {
   int k = symIdx(s); simFehler = 0;
   if(k < 0 || tf != PERIOD_D1) { simFehler = 4301; return -1; }
   std::vector<MqlRates> &q = simD1[k];
   int n = 0;                                                   // Kerzen mit Beginn <= jetzt
   while(n < (int)q.size() && q[n].time <= simJetzt) n++;
   int b = n - start, a = std::max(0, b - count);
   if(b <= 0) { simFehler = 4401; return -1; }
   r.assign(q.begin() + a, q.begin() + b);
   return (int)r.size();
  }
// CopyRates nach Zeitraum [von, bis] (Kerzenbeginn)
static int CopyRates(const string &s, int tf, datetime von, datetime bis, std::vector<MqlRates> &r)
  {
   int k = symIdx(s); simFehler = 0;
   if(k < 0 || tf != PERIOD_M5) { simFehler = 4301; return -1; }
   std::vector<MqlRates> &q = simM5[k];
   auto a = std::lower_bound(q.begin(), q.end(), von, [](const MqlRates &x, datetime t) { return x.time < t; });
   auto b = std::upper_bound(q.begin(), q.end(), bis, [](datetime t, const MqlRates &x) { return t < x.time; });
   r.assign(a, b);
   if(r.empty()) { simFehler = 4401; return -1; }
   return (int)r.size();
  }
static long FadeNyMin(const datetime t) { return (long)MathFloor((double)((long)t - (long)NYOffsetHours * 3600) / 60.0); }  // wie V8
static string FadeName(const int m) { return (F[m].name.size() > 0 ? F[m].name : StringFormat("F%d", m)); }

#include "tw_alles.inc"

int main(int argc, char **argv)
  {
   if(argc != 4) { fprintf(stderr, "Aufruf: tw_sim daten.bin ereignisse.txt module.txt\n"); return 2; }
   FILE *f = fopen(argv[1], "rb");
   if(!f) return 2;
   int64_t ns = 0;
   if(fread(&ns, 8, 1, f) != 1) return 3;
   nSym = (int)ns;
   for(int k = 0; k < nSym; k++)
     {
      char name[32] = {0};
      if(fread(name, 1, 32, f) != 32) return 3;
      S[k].sym = name;
      for(int t = 0; t < 2; t++)
        {
         int64_t n = 0;
         if(fread(&n, 8, 1, f) != 1) return 3;
         std::vector<int64_t> tm(n); std::vector<double> x(4 * n);
         if(n > 0 && (fread(tm.data(), 8, n, f) != (size_t)n || fread(x.data(), 8, 4 * n, f) != (size_t)(4 * n))) return 3;
         std::vector<MqlRates> &q = (t == 0 ? simD1[k] : simM5[k]);
         q.resize(n);
         for(int64_t i = 0; i < n; i++) { q[i] = MqlRates(); q[i].time = tm[i]; q[i].open = x[i]; q[i].high = x[n + i]; q[i].low = x[2 * n + i]; q[i].close = x[3 * n + i]; }
        }
     }
   fclose(f);
   FILE *fm = fopen(argv[3], "r");
   int m, k; char nm[64];
   while(fm && fscanf(fm, "%d %d %63s", &m, &k, nm) == 3) { F[m].k = k; F[m].name = nm; }
   if(fm) fclose(fm);
   FILE *fe = fopen(argv[2], "r");
   if(!fe) return 2;
   char typ[4]; long t; int mm, d;
   while(fscanf(fe, "%3s %ld", typ, &t) == 2)
     {
      simJetzt = t;
      if(typ[0] == 'S')
        {
         if(fscanf(fe, "%d %d", &mm, &d) != 2) return 3;
         TwSignalMerken(mm, d, t);
        }
      TwBerichteAusgeben();
     }
   fclose(fe);
   return 0;
  }
