"""Erzeugt DEADBAND_V12.mq5 aus DEADBAND_V11.mq5 (exakte Ersetzungen, jede genau einmal, sonst Abbruch).

Build 12.00: N1030 im Tick (Modul SRT1030, Einstieg beim Ruecklauf in die Range wie V11TickFades, aber nur N1030 und mit
eigenem Risiko 0,50 %). Das M5-Modul N1030 rechnet dann nur noch virtuell (Portfolio-Waechter unveraendert).
Voreinstellung V12TickN1030 = true (getestete Variante); false = handelsgleich 11.00/10.00.
"""
import sys
from patch_lib import Patch

SRC = sys.argv[1] if len(sys.argv) > 1 else "DEADBAND_V11.mq5"
DST = sys.argv[2] if len(sys.argv) > 2 else "DEADBAND_V12.mq5"
P = Patch(SRC)
HEAD = open("kopf_v12.txt", encoding="ascii").read()

# ---------------------------------------------------------------- 1) Kopfblock und Version
P.rep("//+------------------------------------------------------------------+\n//|  DEADBAND V11  -  Build 11.00, 15.10.2026                        |",
      HEAD + "//+------------------------------------------------------------------+\n//|  DEADBAND V11  -  Build 11.00, 15.10.2026                        |", "Kopf")
P.rep('#property version   "11.00"', '#property version   "12.00"', "Version")

# ---------------------------------------------------------------- 2) Eingaben
P.rep('input double V11GoldPdfRisk   = 0.25;       // 11.00: Risiko je SRGPDF-Trade in % vom Startsaldo (x Pufferkurve)\n',
      'input double V11GoldPdfRisk   = 0.25;       // 11.00: Risiko je SRGPDF-Trade in % vom Startsaldo (x Pufferkurve)\n'
      'input group             "=== 12.00: N1030 im Tick (Voreinstellung an = getestete Variante; aus = handelsgleich 11.00) ==="\n'
      'input bool   V12TickN1030     = true;       // 12.00: N1030 als Tick-Fade SRT1030 (Einstieg im Tick beim Ruecklauf in die Range 10:30-12:30 NY statt am Open nach dem M5-Schluss; Stop 0,3 x Range hinter dem Extrem, Ziel Range-Mitte, Ausstieg 15:30 NY; nur bei live Fade-Regime). Das M5-Modul N1030 rechnet dann nur virtuell (Portfolio-Waechter unveraendert). Replikat v12 (32 Stoerungen): 2022 +0,66, 2023 +1,30, 2017-20 +0,23 Ausz./J, 2024-25 und 2011-15 gleich, 0 Busts. Wird ignoriert, wenn V11TickFades an ist\n'
      'input double V12TickN1030Risk = 0.50;       // 12.00: Risiko je SRT1030-Trade in % vom Startsaldo (x Pufferkurve). Replikat: 0,40-0,60 Plateau, 0,75 (= FadeRiskPct) mit Busts in 2011-15\n',
      "Eingaben")

# ---------------------------------------------------------------- 3) Pruefung der Eingaben
P.rep('   if(RegimeGroesse <= 0.0 || RegimeGroesse > 1.0 + 1e-9 || FadeTagessperre < 0)                             // 6.70\n',
      '   if(V12TickN1030Risk <= 0.0 || V12TickN1030Risk > 1.0)                                                     // 12.00\n'
      '     { Print("DEADBAND4: 12.00 V12TickN1030Risk muss > 0 und <= 1 sein"); return(INIT_PARAMETERS_INCORRECT); }\n'
      '   if(RegimeGroesse <= 0.0 || RegimeGroesse > 1.0 + 1e-9 || FadeTagessperre < 0)                             // 6.70\n',
      "Pruefung")

# ---------------------------------------------------------------- 4) M5-N1030 nur virtuell, wenn die Tick-Version handelt
P.rep('      F[m].aus = FadeNameInListe(F[m].name, FadeAus) || (V11TickFades && FadeNameInListe(F[m].name, "N1030;N1100"));   // 11.00: Tick-Version handelt\n',
      '      F[m].aus = FadeNameInListe(F[m].name, FadeAus) || (V11TickFades && FadeNameInListe(F[m].name, "N1030;N1100"))   // 11.00: Tick-Version handelt\n'
      '                 || (V12TickN1030 && FadeNameInListe(F[m].name, "N1030"));                                           // 12.00: nur N1030 im Tick\n',
      "aus")

# ---------------------------------------------------------------- 5) Anlegen
P.rep('   if(V11TickFades || V11GoldPdf) V11Anlegen();                               // 11.00: Testmodule (Voreinstellung aus)\n',
      '   if(V11TickFades || V11GoldPdf || V12TickN1030) V11Anlegen();               // 11.00: Testmodule; 12.00: SRT1030\n',
      "Anlegen")
P.rep('      PrintFormat("DEADBAND4: 11.00 TEST Tick-Fades SRT1030/SRT1100 AN (Risiko %.2f %%, nur bei live Fade-Regime) - N1030/N1100 rechnen nur virtuell", FadeRiskPct);\n     }\n',
      '      PrintFormat("DEADBAND4: 11.00 TEST Tick-Fades SRT1030/SRT1100 AN (Risiko %.2f %%, nur bei live Fade-Regime) - N1030/N1100 rechnen nur virtuell", FadeRiskPct);\n'
      '      if(V12TickN1030) Print("DEADBAND4: 12.00 V12TickN1030 wird ignoriert - V11TickFades ist an (SRT1030 mit FadeRiskPct)");\n'
      '     }\n'
      '   else if(V12TickN1030)                                                       // 12.00: nur N1030 im Tick, eigenes Risiko\n'
      '     {\n'
      '      int k = SrSymIndex("NAS");\n'
      '      SrEintrag("SRT1030", k, 630, 750, 0, 750, 810, 930, 0.0, 0.6, 0.0, 0.3, 1, 1, 1, 0.0, V12TickN1030Risk, 0.6, true);\n'
      '      PrintFormat("DEADBAND4: 12.00 Tick-Fade SRT1030 AN (Risiko %.2f %%, nur bei live Fade-Regime) - N1030 rechnet nur virtuell", V12TickN1030Risk);\n'
      '     }\n',
      "V11Anlegen")

P.save(DST)
