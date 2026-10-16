// DEADBAND V9 - C++-Pruefgeruest fuer den MQL5-Rechenkern des Trendwende-Berichts (TwSma, TwRegeln, TwNoise).
// tw_kern.inc wird von tw_check.py MECHANISCH aus build/tw_block.mq5 erzeugt (nur Typ-Ersetzungen: Arrays -> std::vector,
// Math* -> std::). Damit wird der MQL-Text selbst uebersetzt und gerechnet, nicht eine Nachschrift.
// Aufruf:  tw_check d1 <ein.bin> <aus.bin>   (OHLC einer Reihe; Ausgabe: dn/up ganze Historie + je Tag j das Ergebnis
//                                              von TwRegeln auf den 400 Tagen bis j, wie TwTagesbericht im EA)
//          tw_check nz <ein.bin> <aus.bin>   (M5 ny/o/l/c + Fenster [a,b); Ausgabe: gueltig/NA/TR fuer die letzte Kerze)
#include <cstdio>
#include <cstdint>
#include <cmath>
#include <vector>
#include <algorithm>
#include <string>

template <class T> static void ArrayResize(std::vector<T> &x, int n) { x.resize(n > 0 ? n : 0); }
static double MathMax(double a, double b) { return std::max(a, b); }
static double MathMin(double a, double b) { return std::min(a, b); }
static double MathLog(double a) { return std::log(a); }
static double MathSqrt(double a) { return std::sqrt(a); }
static double MathAbs(double a) { return std::fabs(a); }
static double MathFloor(double a) { return std::floor(a); }

#include "tw_kern.inc"

template <class T> static bool lies(FILE *f, std::vector<T> &v, size_t n) { v.resize(n); return n == 0 || fread(v.data(), sizeof(T), n, f) == n; }

int main(int argc, char **argv)
  {
   if(argc != 4) { fprintf(stderr, "Aufruf: tw_check d1|nz ein.bin aus.bin\n"); return 2; }
   std::string modus = argv[1];
   FILE *fi = fopen(argv[2], "rb"); FILE *fo = fopen(argv[3], "wb");
   if(!fi || !fo) { fprintf(stderr, "Datei\n"); return 2; }
   if(modus == "d1")
     {
      int64_t n64 = 0, fen64 = 0;
      if(fread(&n64, 8, 1, fi) != 1 || fread(&fen64, 8, 1, fi) != 1) return 3;
      int n = (int)n64, fen = (int)fen64;
      std::vector<double> o, h, l, c;
      if(!lies(fi, o, n) || !lies(fi, h, n) || !lies(fi, l, n) || !lies(fi, c, n)) return 3;
      std::vector<int> dn(n), up(n);
      TwRegeln(o, h, l, c, n, dn, up);
      fwrite(dn.data(), sizeof(int), n, fo); fwrite(up.data(), sizeof(int), n, fo);
      // rollierend wie im EA: je Tag j die letzten fen Tage (j-fen+1..j), Ergebnis der letzten Kerze
      std::vector<int> rdn(n, -1), rup(n, -1);
      for(int j = fen - 1; j < n; j++)
        {
         std::vector<double> o2(o.begin() + (j - fen + 1), o.begin() + j + 1), h2(h.begin() + (j - fen + 1), h.begin() + j + 1),
                             l2(l.begin() + (j - fen + 1), l.begin() + j + 1), c2(c.begin() + (j - fen + 1), c.begin() + j + 1);
         std::vector<int> d2(fen), u2(fen);
         TwRegeln(o2, h2, l2, c2, fen, d2, u2);
         rdn[j] = d2[fen - 1]; rup[j] = u2[fen - 1];
        }
      fwrite(rdn.data(), sizeof(int), n, fo); fwrite(rup.data(), sizeof(int), n, fo);
     }
   else if(modus == "nz")
     {
      int64_t n64 = 0, m64 = 0;
      if(fread(&n64, 8, 1, fi) != 1 || fread(&m64, 8, 1, fi) != 1) return 3;
      size_t n = (size_t)n64, m = (size_t)m64;
      std::vector<long> ny; std::vector<double> o, l, c; std::vector<int64_t> a, b;
      if(!lies(fi, ny, n) || !lies(fi, o, n) || !lies(fi, l, n) || !lies(fi, c, n) || !lies(fi, a, m) || !lies(fi, b, m)) return 3;
      std::vector<int> erg(m * 3, 0);
      for(size_t q = 0; q < m; q++)
        {
         int k0 = (int)a[q], k1 = (int)b[q], nn = k1 - k0;
         if(nn <= 0) continue;
         std::vector<long> ny2(ny.begin() + k0, ny.begin() + k1);
         std::vector<double> o2(o.begin() + k0, o.begin() + k1), l2(l.begin() + k0, l.begin() + k1), c2(c.begin() + k0, c.begin() + k1);
         bool na = false, tr = false;
         bool ok = TwNoise(ny2, o2, l2, c2, nn, nn - 1, na, tr);
         erg[q * 3] = ok; erg[q * 3 + 1] = na; erg[q * 3 + 2] = tr;
        }
      fwrite(erg.data(), sizeof(int), erg.size(), fo);
     }
   else return 2;
   fclose(fi); fclose(fo);
   return 0;
  }
