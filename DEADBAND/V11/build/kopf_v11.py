"""Erzeugt kopf_v11.txt (Kopfblock, Breite 70 wie die bisherigen Bloecke)."""
L = """DEADBAND V11  -  Build 11.00, 15.10.2026
BUILD 11.00: HANDEL WIE 10.00 + TESTSCHALTER NEUE TICK-MODULE
Kein neuer Strom, keine Einstellung hat die Pruefung bestanden
(Auswahl 2022-23, dann besser in 2024-26 UND 2016-21, 0 Busts).
Voreinstellung = handelsgleich 10.00. Neu im Code:
1) SR-Marken erweitert (SrEintrag): Symbol je Marke, Stop-Puffer
   x ATR oder x Markenspanne, Ziel CRV/Range-Mitte/Gegenseite,
   CRV und Risiko je Marke, Range-Filter, Bindung an den
   Portfolio-Waechter. SrListe: 12 Felder (wie 9.00) oder 19.
2) V11TickFades (aus): N1030/N1100 als Tick-Fades SRT1030/1100,
   M5-Versionen nur virtuell. Replikat (16 Stoerungen, Ausz./J):
   2022 +1,2, 2023 +1,9, 2017-20 +0,6, aber 2024-25 -0,6 und
   1 Bust -> verworfen, nur fuer den Tester (Echte Ticks).
3) V11GoldPdf (aus): Gold 18:30-2:00 NY unter Vortagstief und
   zurueck -> Long, Ziel 3 R, 0,25 %. Replikat: 2023 +2,2 und
   2024-25 +1,0 Ausz./J, 2022 und 2017-20 beim Geld neutral;
   OANDA-Gold 2010-16 ohne Vorteil (2014-15 negativ) = Drift.
Replikat v11 (neu gebaut: M1, Schlupf 1/4 Spread, rollierende
1-Jahres-Konten alle 7 Tage, 16 gepaarte Stoerungen), Ausz./J
und $/J (Anteil nach Gebuehr), V8 -> V10/V11:
  Start 2022    9,2 -> 12,0  |  1531 -> 2288 $
  Start 2023   11,4 -> 13,1  |  2354 -> 2542 $
  2024-25       8,4 ->  7,9  |  1759 -> 1670 $ (SR nicht besser)
  2017-20       5,0 ->  5,5  |   939 -> 1025 $  0 Busts ueberall
GETESTET UND VERWORFEN (Bericht DEADBAND_V11_Bericht.md):
  Bestaetigungs-Einstieg (+0,1..0,3 R, Hypothese "Move vorbei"),
  Tick-Fades, 4.608 Sweep-Varianten Gold/NAS (8 Kandidaten auf
  Kontoebene), Gold-Vortagestief GPDF, SR-Risiko 0,15-0,35
  (kein Plateau, ab 0,30 Busts), Abschluss-Ernte 0,2/0,5 R und
  10 % Reserve, Serien-Stopp 2/4, ohne Schutz gueltiger Tage,
  RSI21-Schutz bis 12/14 Uhr, Gewinn-Ernte ab 0,5 R.
RUECKFALL = 10.00: V11TickFades=false, V11GoldPdf=false (Vorein-
  stellung). DEADBAND_V10.mq5 bleibt unveraendert.
NICHT KOMPILIERT ERSTELLT - vor dem Einsatz im MetaEditor
kompilieren und im Strategietester (Echte Ticks) pruefen."""
bad = False
out = ["//+------------------------------------------------------------------+"]
for line in L.split("\n"):
    if len(line) > 64:
        print(f"zu lang ({len(line)}): {line}"); bad = True; continue
    out.append("//|  " + line.ljust(64) + "|")
out.append("//+------------------------------------------------------------------+")
if bad: raise SystemExit(1)
txt = "\n".join(out) + "\n"
txt.encode("ascii")
assert all(len(x) == 70 for x in txt.splitlines())
import os
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "kopf_v11.txt"), "w", encoding="ascii").write(txt)
print("kopf_v11.txt geschrieben")
