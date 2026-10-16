"""Erzeugt DEADBAND_V13.mq5 aus DEADBAND_V12.mq5 (exakte Ersetzungen, jede genau einmal, sonst Abbruch).

Build 13.00 (Live-Runde 16.10.2026, Nachbau auf dem echten GFT-Feed und Abgleich mit den Live-Trades):
  - V12TickN1030 = false  (N1030 wieder auf M5; der Tick-Einstieg ist auf dem GFT-Feed 2025-26 kostenempfindlich)
  - AsiaAktiv    = false  (XA kann live nie handeln: das Signal kommt an der ersten Kerze nach der Tagespause,
                           FadeDurchlauf wertet nur Kerzen ohne Luecke davor live aus - Nachbau, Tester und Echtbetrieb
                           stimmen damit ueberein; am Live-Handel aendert das nichts)
  - SrRiskPct    = 0.05   (statt 0,10; Plateau-Mitte 0,03-0,075 auf GFT-Feed und Fremddaten)
Sonst unveraendert. Aufruf: py -3 patch_v13.py DEADBAND_V12.mq5 DEADBAND_V13.mq5
"""
import sys, os
_H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_H, "..", "..", "V12", "build"))                          # Repo: DEADBAND/V12/build
sys.path.insert(0, os.path.join(_H, "..", "repo", "DEADBAND", "V12", "build"))            # lokale Arbeitskopie
from patch_lib import Patch

SRC = sys.argv[1] if len(sys.argv) > 1 else "DEADBAND_V12.mq5"
DST = sys.argv[2] if len(sys.argv) > 2 else "DEADBAND_V13.mq5"
P = Patch(SRC)

KOPF = [
    "DEADBAND V13  -  Build 13.00, 17.10.2026",
    "BUILD 13.00: V12-CODE, 3 VOREINSTELLUNGEN AUS DEM LIVE-ABGLEICH",
    "Grundlage: Abgleich der 29 Live-Trades 28.09.-16.10.2026 mit dem",
    "  Nachbau auf dem GFT-Feed (M1-Export, echte Spreads): Einstieg,",
    "  Stop und R stimmen Trade fuer Trade (meist < 0,5 Punkte).",
    "FUND: XA (Gold-Asien) handelt live NIE. Das Signal kommt an der",
    "  ersten Kerze nach der Tagespause 17-18 NY; FadeDurchlauf",
    "  wertet nur Kerzen ohne Luecke davor live aus ('frisch').",
    "  Gilt fuer alle Builds ab 8.00 und den Tester. Der Nachbau",
    "  rechnete XA mit.",
    "Neu (Voreinstellung = getestete Variante):",
    "  AsiaAktiv    = false (am Live-Handel aendert das nichts)",
    "  SrRiskPct    = 0,05  (statt 0,10)",
    "  V12TickN1030 = false (N1030 wieder auf M5)",
    "Nachbau, 32 gepaarte Stoerungen, gegen den ECHTEN Live-Stand",
    "  (V8 ohne XA), Differenz Ausz./J (Kontostart):",
    "  GFT-Feed  2022 +0,20  2023 +1,72  2024-25 +1,09  2025-26 +0,22",
    "  Schlupf x2         +0,09       +0,83          +1,39      +0,68",
    "  Spread x2          +1,42       +2,38          +0,88      +0,07",
    "  Fremddaten 2022 +1,32 2023 +2,75 2024-25 +0,79 2017-20 +0,29",
    "    2011-15 +0,53. 0 Busts in allen Rechnungen.",
    "VERWORFEN: V12 wie geliefert (Tick-N1030 2025-26 -0,89, mit",
    "  Spread x2 -3,66 Ausz./J), XA reparieren (Einstieg 18:05 bzw.",
    "  18:10 NY: nicht robust), SR 0,03/0,075/0,10, nur SRIB(+SRPRE).",
    "RUECKFALL = 12.00: V12TickN1030 = true, SrRiskPct = 0,10,",
    "  AsiaAktiv = true. Rueckfall = Live-Handel 8.10:",
    "  SrAktiv = false, V12TickN1030 = false (AsiaAktiv egal).",
    "KOMPILIERT (MetaEditor GFT-Terminal, 0 Fehler) - vor dem Einsatz",
    "  im Strategietester (Echte Ticks) pruefen.",
]
W = 64
for z in KOPF:
    if len(z) > W:
        sys.exit(f"ABBRUCH: Kopfzeile zu lang ({len(z)}): {z}")
HEAD = "//+------------------------------------------------------------------+\n" + \
       "".join(f"//|  {z:<{W}}|\n" for z in KOPF) + \
       "//+------------------------------------------------------------------+\n"

# ---------------------------------------------------------------- 1) Kopfblock und Version
P.rep("//+------------------------------------------------------------------+\n//|  DEADBAND V12  -  Build 12.00, 16.10.2026                        |",
      HEAD + "//+------------------------------------------------------------------+\n//|  DEADBAND V12  -  Build 12.00, 16.10.2026                        |", "Kopf")
P.rep('#property version   "12.00"', '#property version   "13.00"', "Version")

# ---------------------------------------------------------------- 2) Voreinstellungen
P.rep('input bool   AsiaAktiv        = true ;       // 8.00: Modul XA anlegen\n',
      'input bool   AsiaAktiv        = false;       // 8.00: Modul XA anlegen. 13.00: AUS - XA handelt live nie (Signal an der ersten Kerze nach der Tagespause, FadeDurchlauf wertet nur luecklose Kerzen live aus); aus = Nachbau/Tester wie Echtbetrieb\n',
      "AsiaAktiv")
P.rep('input double SrRiskPct        = 0.10;       // 10.00: 0,10',
      'input double SrRiskPct        = 0.05;       // 13.00: 0,05 (GFT-Feed: Plateau 0,03-0,075, 0,10 im Fenster 2025-26 -0,46 Ausz./J). 10.00: 0,10',
      "SrRiskPct")
P.rep('input bool   V12TickN1030     = true;       // 12.00: N1030 als Tick-Fade SRT1030',
      'input bool   V12TickN1030     = false;      // 13.00: AUS (GFT-Feed 2025-26 -0,9 Ausz./J, mit doppelten Kosten -3,7). 12.00: N1030 als Tick-Fade SRT1030',
      "V12TickN1030")
P.save(DST)
