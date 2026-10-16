"""DEADBAND V9 - DEADBAND_V9_Echtbetrieb.set aus den input-Zeilen von DEADBAND_V9.mq5 (Voreinstellungen) erzeugen.

Format wie die bisherigen Presets: Kommentarzeilen mit ';', danach Name=Wert, Zeilenende CRLF, nur ASCII.
Strings ohne Anfuehrungszeichen, bool true/false, ENUM_TIMEFRAMES als Zahl (MT5-Kennung).
Aufruf: python3 gen_set.py <DEADBAND_V9.mq5> <DEADBAND_V9_Echtbetrieb.set (neu)>
"""
import os, re, sys

TF = {"PERIOD_M1": 1, "PERIOD_M5": 5, "PERIOD_M10": 10, "PERIOD_M15": 15, "PERIOD_M20": 20, "PERIOD_M30": 30,
      "PERIOD_H1": 16385, "PERIOD_H4": 16388, "PERIOD_D1": 16408}

KOPF = """; DEADBAND V9 - Build 9.00 - ECHTBETRIEB, GFT Instant Premium 10k. NICHT KOMPILIERT ERSTELLT (vorher MetaEditor + Tester).
; Handel = 8.10: alle Werte = Voreinstellung von DEADBAND_V9.mq5 = Voreinstellung von 8.10 (Fade-Liste 10 Module + S0830 + LW + XA
;   + TD, RSI21, NAS-Noise, Portfolio-Waechter PF > 1,15 der letzten 200 virtuellen Ergebnisse, Probability Grid, Pufferkurve
;   3,5/1,25/0,1, BelowStartMult 0,95, Gesamtbudget/Idee 0,9 %, Schutz gueltiger Tage, Serien-Stopp 3, Abschluss-Ernte 0,3 R,
;   Anpasser neutral). Neu ist nur TwBericht=true: Trendwende-Bericht im Journal (Zeilen "DEADBAND9 TW ..."), ohne Einfluss auf
;   den Handel. TwBericht=false schaltet nur den Bericht ab.
; Warum keine Handelsaenderung: 37 vorab festgelegte Konfigurationen (Regime-Sperren R1-R10, Noise Area, Tagesrichtung,
;   Ziel-Varianten, LW ab 9:40, NAS-Shorts nur im Abwaertsregime, Schluss-Momentum, CPPI) - keine erfuellt alle
;   Uebernahmeregeln (A 2016-21 und B 2022-10/2026, 1 und 2 Jahre, Summe R der Sperren < 0, 5/7 Jahre, Spread x1,5/x2).
;   Replikat (freie Daten) 8.10 = V9: A 1 J 4,54 Ausz./J, 1064 $/J netto; B 1 J 13,41 Ausz./J, 3031 $/J netto; 0 Pleiten.
;   Bericht: DEADBAND_V9_Bericht.md.
; KONTOEINGABEN AUS DEM LAUFENDEN V8 UEBERNEHMEN, falls dort gesetzt (sonst leer/0 lassen): KaufdatumGFT, StartBalanceOverride,
;   FloorOverride + FloorOverrideZeit, CycleStartOverride, AuszahlungKennung, KeineAuszahlung, AuszahlungZeiten,
;   AuszahlungAngefordertAm, NurAufPcPfad. Gleiche MagicBase wie V8, damit offene Positionen erkannt werden.
; Wechsel V8 -> V9 nur ohne offene Position oder am Wochenende; EIN Chart (wie V8), eigener PC, kein VPS.
; Extras > Optionen > Charts > Max. Balken im Chart = Unbegrenzt (Waechter/Grid brauchen ~600 Tage M5, TW-Bericht 401 D1).
"""


def werte(mq5):
    out = []
    for z in open(mq5, encoding="ascii"):
        if not z.startswith("input ") or z.startswith("input group"):
            continue
        m = re.match(r"input\s+(\w+)\s+(\w+)\s*=\s*", z)
        typ, name = m.group(1), m.group(2)
        rest = z[m.end():]
        if rest.startswith('"'):
            wert = rest[1:rest.index('"', 1)]
        else:
            wert = rest[:rest.index(";")].strip()
        if typ == "ENUM_TIMEFRAMES":
            wert = str(TF[wert])
        elif typ == "bool":
            assert wert in ("true", "false"), (name, wert)
        elif typ in ("int", "long"):
            int(wert)
        elif typ == "double":
            float(wert)
        out.append((name, wert))
    return out


def main(mq5, ziel):
    assert not os.path.exists(ziel), f"{ziel} existiert schon - nur neue Dateien anlegen"
    w = werte(mq5)
    namen = [n for n, _ in w]
    assert len(namen) == len(set(namen))
    assert ("TwBericht", "true") in w
    txt = KOPF + "".join(f"{n}={v}\n" for n, v in w)
    txt.encode("ascii")
    with open(ziel, "x", encoding="ascii", newline="\r\n") as f:
        f.write(txt)
    print(f"{ziel}: {len(w)} Eingaben")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
