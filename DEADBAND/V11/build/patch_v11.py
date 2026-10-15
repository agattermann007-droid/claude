"""Erzeugt DEADBAND_V11.mq5 aus DEADBAND_V10.mq5 (exakte Ersetzungen, jede genau einmal, sonst Abbruch).

Build 11.00: Handel wie 10.00 (keine Aenderung hat Auswahl 2022-23 UND Pruefung 2024-26 UND 2016-21 bestanden).
Neu sind zwei Testschalter (Voreinstellung aus) und die dafuer noetige Erweiterung des SR-Moduls:
  - SR-Marken mit eigenem Symbol, Stop-Art (ATR oder Markenspanne), Ziel-Art (CRV, Mitte, Gegenseite), CRV, Risiko,
    Range-Filter und Bindung an den Portfolio-Waechter der Fades.
  - V11TickFades: N1030/N1100 als Tick-Fades (Einstieg beim Ruecklauf in die Range), M5-Versionen nur virtuell.
  - V11GoldPdf: Gold-Sweep des Vortagestiefs 18:30-2:00 NY -> Long, Ziel 3 R.
"""
import sys
from patch_lib import Patch, between

SRC = sys.argv[1] if len(sys.argv) > 1 else "DEADBAND_V10.mq5"
DST = sys.argv[2] if len(sys.argv) > 2 else "DEADBAND_V11.mq5"
P = Patch(SRC)
HEAD = open("kopf_v11.txt", encoding="ascii").read()

# ---------------------------------------------------------------- 1) Kopfblock und Version
P.rep("//+------------------------------------------------------------------+\n//|  DEADBAND V10  -  Build 10.00, 14.10.2026                        |",
      HEAD + "//+------------------------------------------------------------------+\n//|  DEADBAND V10  -  Build 10.00, 14.10.2026                        |", "Kopf")
P.rep('#property version   "10.00"', '#property version   "11.00"', "Version")

# ---------------------------------------------------------------- 2) Platz fuer drei weitere Module
P.rep("#define MAXFADE 18            // 6.00: Fade-Module (7.10: 10 Listenplaetze + Spike-Modul; 8.00: + LW + XA; 8.10: + TD; 9.00: + 4 SR-Marken)",
      "#define MAXFADE 22            // 6.00: Fade-Module (7.10: 10 Listenplaetze + Spike-Modul; 8.00: + LW + XA; 8.10: + TD; 9.00: + 4 SR-Marken; 11.00: + 3 Testmodule)",
      "MAXFADE")

# ---------------------------------------------------------------- 3) Eingaben
P.rep('input double SrMaxSpreadATR   = 0.02;       // kein Einstieg, wenn der Spread > X x ATR(D1) (0 = ohne Pruefung)\n',
      'input double SrMaxSpreadATR   = 0.02;       // kein Einstieg, wenn der Spread > X x ATR(D1) (0 = ohne Pruefung)\n'
      'input group             "=== 11.00: Testschalter neue Tick-Module (Voreinstellung aus = handelsgleich 10.00) ==="\n'
      'input bool   V11TickFades     = false;      // 11.00 TEST: N1030 und N1100 als Tick-Fades SRT1030/SRT1100 (Einstieg im Tick beim Ruecklauf in die Range statt am Open nach dem M5-Schluss; nur bei live Fade-Regime). Die M5-Module N1030/N1100 rechnen dann nur virtuell (Portfolio-Waechter). Replikat: 2022/2023/2017-20 besser, 2024-25 schlechter, 1 Bust in 16 Stoerungen - erst im Tester (Echte Ticks) pruefen\n'
      'input bool   V11GoldPdf       = false;      // 11.00 TEST: Modul SRGPDF - Gold faellt 18:30-2:00 NY unter das Tief des Vortags (18:00-17:00) und kehrt zurueck -> Long, Stop 0,15 ATR unter dem Extrem, Ziel 3 R, Ausstieg 8:00 NY. Replikat: 2023-25 besser, auf OANDA-Daten 2010-16 ohne Vorteil (Gold-Baisse 2014-15 negativ) - nur Tester\n'
      'input double V11GoldPdfRisk   = 0.25;       // 11.00: Risiko je SRGPDF-Trade in % vom Startsaldo (x Pufferkurve)\n',
      "Eingaben 11.00")

# ---------------------------------------------------------------- 4) Felder je SR-Marke
P.rep("   long     srTag;                // 9.00 SR: Tag des Zustands (= day)\n",
      "   long     srTag;                // 9.00 SR: Tag des Zustands (= day)\n"
      "   int      srSmode, srTmode;     // 11.00 SR: Stop-Puffer 0 = x ATR, 1 = x Markenspanne | Ziel 0 = CRV, 1 = Mitte, 2 = Gegenseite\n"
      "   double   srCrv, srMx;          // 11.00 SR: CRV der Marke (0 = SrCRV), Markenspanne hoechstens srMx x ATR (0 = ohne)\n"
      "   bool     srGuard;              // 11.00 SR: nur bei live Fade-Regime (Portfolio-Waechter) handeln\n",
      "FadeDef-Felder")

# ---------------------------------------------------------------- 5) SrAnlegen -> SrEintrag + SrAnlegen + V11Anlegen
alt = between(P.s, "bool SrAnlegen()\n  {\n", "// 9.00 SR: Hoch/Tief der M1-Kerzen [srLa, srLb) des Handelstags Dt")
neu = r'''// 11.00: eine SR-Marke anlegen. smode 0 = Stop sb x ATR jenseits des Sweep-Extrems (9.00), 1 = sb x Markenspanne (Fade-Stil,
//        Mindeststop nur SrMinStopSpreads). tmode 0 = Ziel crv x Stopabstand (crv 0 = SrCRV), 1 = Mitte der Marke, 2 = Gegenseite.
//        mx > 0: Markenspanne hoechstens mx x ATR(D1). guard: nur handeln, solange der Portfolio-Waechter der Fades live ist.
//        Mit smode 0, tmode 0, crv 0, risk SrRiskPct, mx 0, guard false = SR wie 9.00/10.00.
bool SrEintrag(const string nm, const int k, const int la, const int lb, const int loff, const int w0, const int w1, const int xx,
               const double sd, const double md, const double rb, const double sb, const int dir,
               const int smode, const int tmode, const double crv, const double risk, const double mx, const bool guard)
  {
   if(nFade >= MAXFADE) { PrintFormat("DEADBAND4: SR - kein Platz (schon %d Module) - Marke %s AUS", nFade, nm); return false; }
   if(k < 0 || k >= nSym) { PrintFormat("DEADBAND4: SR-Marke %s - Symbol nicht in der SymbolList - AUS", nm); return false; }
   double pt = SymbolInfoDouble(S[k].sym, SYMBOL_POINT);
   if(pt <= 0.0) { PrintFormat("DEADBAND4: SR-Marke %s - Symbol ohne Point - AUS", nm); return false; }
   if(la >= lb || la < -420 || lb > 1020 || (loff != 0 && loff != -1) || lb + loff*1440 > w0 || w0 < -360 || w1 < w0 + 5 || w1 > 990
      || xx < w1 + 5 || xx > 1000 || sd < 0.0 || md <= sd || rb < 0.0 || sb < 0.0 || (dir != 1 && dir != -1)
      || smode < 0 || smode > 1 || tmode < 0 || tmode > 2 || crv < 0.0 || risk <= 0.0 || risk > 1.0 || mx < 0.0)
     { PrintFormat("DEADBAND4: SR-Marke %s ungueltig (la < lb, -420 <= la, lb <= 1020, loff 0/-1, Marke endet vor w0, -360 <= w0, w0 + 5 <= w1 <= 990, w1 + 5 <= x <= 1000, 0 <= sd < md, rb >= 0, sb >= 0, dir 1/-1, smode 0/1, tmode 0-2, crv >= 0, 0 < Risiko <= 1, mx >= 0) - AUS", nm); return false; }
   for(int q=0;q<nFade;q++) if(F[q].name == nm) { PrintFormat("DEADBAND4: SR-Name %s doppelt - AUS", nm); return false; }
   int m = nFade;
   F[m].k = k; F[m].r0 = w0; F[m].L = w1 - w0; F[m].tlen = 5; F[m].xoff = xx - (w1 + 5); F[m].buf = sb; F[m].tgt = 0;
   F[m].dir = dir; F[m].mx = 99.0; F[m].name = nm; F[m].pt = pt;
   F[m].aus = FadeNameInListe(F[m].name, FadeAus);
   F[m].schutzFrei = FadeNameInListe(F[m].name, GueltigSchutzFrei);
   F[m].gridAus = true;
   F[m].day = -1; F[m].nbar = 0; F[m].hh = 0.0; F[m].ll = 0.0; F[m].rng = 0.0; F[m].exHi = 0.0; F[m].exLo = 0.0;
   F[m].ready = false; F[m].done = false; F[m].skip = false; F[m].vOn = false; F[m].vDir = 0;
   F[m].vEnt = 0.0; F[m].vSl = 0.0; F[m].vTp = 0.0; F[m].vRd = 0.0; F[m].vBar = 0; F[m].vX = 0;
   for(int q=0;q<FADEHIST;q++) { F[m].hist[q] = 0.0; F[m].histT[q] = 0; }
   F[m].nh = 0; F[m].ph = 0; F[m].nSig = 0; F[m].histFertig = true; F[m].histFehl = 0; F[m].histVersuch = 0; F[m].histAb = 0;   // keine Historie, kein eigener Waechter
   F[m].lastBar = 0; F[m].sigHeute = 0; F[m].einHeute = 0; F[m].liveDay = -1; F[m].liveGoal = 0.0;
   F[m].logZeit = 0; F[m].tpVersuch = 0; F[m].schlussVersuch = 0; F[m].nGrid = 0;
   F[m].t1Tk = 0; F[m].t1Chk = 0; F[m].t1Versuch = 0; F[m].nT1 = 0;
   F[m].spike = false; F[m].spP0 = 0.0; F[m].spDir = 0; F[m].spA = 0.0; F[m].spGoal = 0.0;
   F[m].typ = 5; F[m].riskPct = risk; F[m].minBuf = 0.0;
   F[m].lwPH = 0.0; F[m].lwPL = 0.0; F[m].lwCH = -DBL_MAX; F[m].lwCL = DBL_MAX; F[m].lwPN = 0; F[m].lwCN = 0;
   F[m].tdLetzt = -1; F[m].tdVor = -1; F[m].tdRefTag = -1; F[m].tdRef = 0.0;
   F[m].srLa = la; F[m].srLb = lb; F[m].srLoff = loff; F[m].srSd = sd; F[m].srMd = md; F[m].srRb = rb;
   F[m].srSt = 0; F[m].srEx = 0.0; F[m].srTag = -1;
   F[m].srSmode = smode; F[m].srTmode = tmode; F[m].srCrv = crv; F[m].srMx = mx; F[m].srGuard = guard;   // 11.00
   nFade++;
   return true;
  }

// 11.00: Symbol-Index aus einem Namensteil (wie SrSymbol), -1 = nicht in der SymbolList
int SrSymIndex(const string teil)
  {
   string sy = teil; StringTrimLeft(sy); StringTrimRight(sy); StringToUpper(sy);
   for(int q=0;q<nSym && StringLen(sy) > 0;q++) { string u = S[q].sym; StringToUpper(u); if(StringFind(u, sy) >= 0) return q; }
   return -1;
  }

bool SrAnlegen()
  {
   int k = SrSymIndex(SrSymbol);
   if(k < 0) { PrintFormat("DEADBAND4: 9.00 Modul SR - Symbol %s nicht in der SymbolList - SR AUS", SrSymbol); return true; }
   if(SrCRV <= 0.0 || SrRiskPct <= 0.0 || SrRiskPct > 1.0 || SrMinStopSpreads < 0.0 || SrMinStopATR < 0.0 || SrMaxSpreadATR < 0.0)
     { Print("DEADBAND4: 9.00 SR-Eingaben ungueltig (SrCRV > 0, 0 < SrRiskPct <= 1, SrMinStopSpreads/SrMinStopATR/SrMaxSpreadATR >= 0) - SR AUS"); return true; }
   double pt = SymbolInfoDouble(S[k].sym, SYMBOL_POINT);
   if(pt <= 0.0) { Print("DEADBAND4: 9.00 Modul SR - Symbol ohne Point - SR AUS"); return true; }
   string liste = SrListe; StringTrimLeft(liste); StringTrimRight(liste);
   if(StringLen(liste) == 0) liste = SR_STANDARD;
   string teile[]; int n = StringSplit(liste, StringGetCharacter(";",0), teile);
   for(int i=0;i<n;i++)
     {
      string x = teile[i]; StringTrimLeft(x); StringTrimRight(x);
      if(StringLen(x) == 0) continue;
      string f[]; int nf = StringSplit(x, StringGetCharacter(",",0), f);
      if(nf != 12 && nf != 19)
        { PrintFormat("DEADBAND4: SrListe Eintrag %d hat %d statt 12 bzw. 19 Felder (Name,la,lb,loff,w0,w1,x,sd,md,rb,sb,dir[,Symbol,smode,tmode,crv,Risiko,mx,Waechter]): %s - AUS", i+1, nf, x); continue; }
      for(int q=0;q<nf;q++) { StringTrimLeft(f[q]); StringTrimRight(f[q]); }
      int la = (int)StringToInteger(f[1]), lb = (int)StringToInteger(f[2]), loff = (int)StringToInteger(f[3]);
      int w0 = (int)StringToInteger(f[4]), w1 = (int)StringToInteger(f[5]), xx = (int)StringToInteger(f[6]);
      double sd = StringToDouble(f[7]), md = StringToDouble(f[8]), rb = StringToDouble(f[9]), sb = StringToDouble(f[10]);
      int dir = (int)StringToInteger(f[11]);
      int kk = k, smode = 0, tmode = 0; double crv = 0.0, risk = SrRiskPct, mx = 0.0; bool guard = false;
      if(nf == 19)                                                              // 11.00: erweitertes Format
        {
         if(StringLen(f[12]) > 0 && f[12] != "-") kk = SrSymIndex(f[12]);
         smode = (int)StringToInteger(f[13]); tmode = (int)StringToInteger(f[14]); crv = StringToDouble(f[15]);
         double rr = StringToDouble(f[16]); if(rr > 0.0) risk = rr;
         mx = StringToDouble(f[17]); guard = (StringToInteger(f[18]) != 0);
        }
      SrEintrag("SR" + f[0], kk, la, lb, loff, w0, w1, xx, sd, md, rb, sb, dir, smode, tmode, crv, risk, mx, guard);
     }
   return true;
  }

// 11.00: Testmodule (Voreinstellung aus). Parameter = Replikat v11 (cand11.py): Tick-Fades wie die Listen-Fades N1030/N1100
//        (Range, Fenster, Ausstieg, Stop-Puffer x Range, Ziel Mitte/Gegenseite, Range <= 0,6 ATR, Risiko FadeRiskPct,
//        Durchbruch ab 0,6 ATR jenseits der Range), Gold-Vortagestief GPDF.
void V11Anlegen()
  {
   if(V11TickFades)
     {
      int k = SrSymIndex("NAS");
      SrEintrag("SRT1030", k, 630, 750, 0, 750, 810, 930, 0.0, 0.6, 0.0, 0.3, 1, 1, 1, 0.0, FadeRiskPct, 0.6, true);
      SrEintrag("SRT1100", k, 660, 750, 0, 750, 810, 1000, 0.0, 0.6, 0.0, 0.6, 1, 1, 2, 0.0, FadeRiskPct, 0.6, true);
      PrintFormat("DEADBAND4: 11.00 TEST Tick-Fades SRT1030/SRT1100 AN (Risiko %.2f %%, nur bei live Fade-Regime) - N1030/N1100 rechnen nur virtuell", FadeRiskPct);
     }
   if(V11GoldPdf)
     {
      SrEintrag("SRGPDF", SrSymIndex("XAU"), -360, 1020, -1, -330, 120, 480, 0.0, 0.6, 0.0, 0.15, 1, 0, 0, 3.0, V11GoldPdfRisk, 0.0, false);
      PrintFormat("DEADBAND4: 11.00 TEST Gold-Vortagestief SRGPDF AN (Fenster 18:30-2:00 NY, Ziel 3 R, Risiko %.2f %%)", V11GoldPdfRisk);
     }
  }

'''
P.rep(alt, neu, "SrAnlegen")

# ---------------------------------------------------------------- 6) Aufruf und M5-Versionen der Tick-Fades nur virtuell
P.rep("   if(SrAktiv) SrAnlegen();                                                   // 9.00\n",
      "   if(SrAktiv) SrAnlegen();                                                   // 9.00\n"
      "   if(V11TickFades || V11GoldPdf) V11Anlegen();                               // 11.00: Testmodule (Voreinstellung aus)\n",
      "Aufruf V11Anlegen")
P.rep("      F[m].aus = FadeNameInListe(F[m].name, FadeAus);\n      F[m].schutzFrei = FadeNameInListe(F[m].name, GueltigSchutzFrei);             // 6.50\n",
      "      F[m].aus = FadeNameInListe(F[m].name, FadeAus) || (V11TickFades && FadeNameInListe(F[m].name, \"N1030;N1100\"));   // 11.00: Tick-Version handelt\n"
      "      F[m].schutzFrei = FadeNameInListe(F[m].name, GueltigSchutzFrei);             // 6.50\n",
      "Listen-Fades aus")

# ---------------------------------------------------------------- 7) SrTick: Range-Filter, Stop, Ziel
P.rep("      F[m].hh = hi; F[m].ll = lo; F[m].rng = hi - lo; F[m].spA = a; F[m].nbar = n; F[m].ready = true;\n",
      "      if(F[m].srMx > 0.0 && hi - lo > F[m].srMx*a)                             // 11.00: Range-Filter (Tick-Fades wie mx der Fade-Liste)\n"
      "        {\n"
      "         F[m].skip = true;\n"
      "         PrintFormat(\"DEADBAND4 %s SR %s: Markenspanne %.2f ATR > %.2f ATR - heute kein Signal\", s, FadeName(m), (hi - lo)/a, F[m].srMx);\n"
      "         return;\n"
      "        }\n"
      "      F[m].hh = hi; F[m].ll = lo; F[m].rng = hi - lo; F[m].spA = a; F[m].nbar = n; F[m].ready = true;\n",
      "SrTick Range-Filter")
P.rep("   double st = (d > 0 ? F[m].srEx - F[m].buf*A : F[m].srEx + sp + F[m].buf*A);\n"
      "   double minD = MathMax(SrMinStopSpreads*sp, SrMinStopATR*A) + 2.0*F[m].pt;   // + 2 Punkte: Rundung des Stops, FadeMinStopSpreads in FadeLive\n"
      "   if((ent - st)*d < minD) st = ent - d*minD;                                  // Stop mindestens minD vom Einstieg\n"
      "   double rd = (ent - st)*d;\n"
      "   double goal = ent + d*SrCRV*rd;\n",
      "   double sbuf = (F[m].srSmode == 1 ? F[m].buf*F[m].rng : F[m].buf*A);        // 11.00: Stop-Puffer x Markenspanne (Fade-Stil) oder x ATR\n"
      "   double st = (d > 0 ? F[m].srEx - sbuf : F[m].srEx + sp + sbuf);\n"
      "   double minD = MathMax(SrMinStopSpreads*sp, (F[m].srSmode == 1 ? 0.0 : SrMinStopATR)*A) + 2.0*F[m].pt;   // + 2 Punkte: Rundung des Stops, FadeMinStopSpreads in FadeLive (11.00: Fade-Stil nur Spreads)\n"
      "   if((ent - st)*d < minD) st = ent - d*minD;                                  // Stop mindestens minD vom Einstieg\n"
      "   double rd = (ent - st)*d;\n"
      "   double crv = (F[m].srCrv > 0.0 ? F[m].srCrv : SrCRV);                       // 11.00: CRV je Marke\n"
      "   double goal = (F[m].srTmode == 1 ? 0.5*(F[m].hh + F[m].ll) : (F[m].srTmode == 2 ? (d > 0 ? F[m].hh : F[m].ll) : ent + d*crv*rd));   // 11.00: Mitte/Gegenseite\n"
      "   if(rd <= 0.0 || (goal - ent)*d <= 0.0)\n"
      "     {\n"
      "      PrintFormat(\"DEADBAND4 %s SR %s: Kurs schon jenseits des Ziels %.*f - kein Einstieg\", s, FadeName(m), dg, goal);\n"
      "      return;\n"
      "     }\n",
      "SrTick Stop/Ziel")
P.rep("               (d > 0 ? \"LONG\" : \"SHORT\"), dg, st, rd/A, dg, goal, SrCRV, FadeUhr(xm));\n",
      "               (d > 0 ? \"LONG\" : \"SHORT\"), dg, st, rd/A, dg, goal, (goal - ent)*d/rd, FadeUhr(xm));   // 11.00: tatsaechliches CRV\n",
      "SrTick Meldung")

# ---------------------------------------------------------------- 8) Waechter fuer Tick-Fades
P.rep("   if(F[m].typ != 0) return true;                                               // 7.10/8.00: Sondermodule ohne Waechter (Replikat)\n",
      "   if(F[m].typ == 5 && F[m].srGuard) return FadeRegimeLive(tSig);              // 11.00: Tick-Fades nur bei live Fade-Regime (Portfolio-Waechter)\n"
      "   if(F[m].typ != 0) return true;                                               // 7.10/8.00: Sondermodule ohne Waechter (Replikat)\n",
      "FadeWaechterOk")

# ---------------------------------------------------------------- 9) Ziel nach Neustart je Marke
P.rep("      double po = PositionGetDouble(POSITION_PRICE_OPEN);\n      goal = po + d*SrCRV*MathAbs(po - slAlt);\n",
      "      double po = PositionGetDouble(POSITION_PRICE_OPEN);\n"
      "      if(F[m].srTmode == 0) goal = po + d*(F[m].srCrv > 0.0 ? F[m].srCrv : SrCRV)*MathAbs(po - slAlt);   // 11.00: CRV je Marke\n"
      "      else if(F[m].day == Dt && F[m].hh > 0.0 && F[m].ll > 0.0) goal = (F[m].srTmode == 1 ? 0.5*(F[m].hh + F[m].ll) : (d > 0 ? F[m].hh : F[m].ll));\n",
      "FadeVerwalten Ziel")

P.save(DST)
