"""DEADBAND V9 - erzeugt DEADBAND_V9.mq5 (Build 9.00) aus DEADBAND_V8.mq5 (Build 8.10). Die V8-Datei wird nur gelesen.

Aenderungen (jede Einfuegung an genau einer, gepruefter Stelle):
  1. Kopfblock Build 9.00 vor dem 8.10-Block
  2. #property version "9.00"
  3. Eingabegruppe 9.00 mit TwBericht nach KaufPuffer
  4. TW-Globale nach "int nSym = 0;"
  5. OnInit: TW-Zustand zuruecksetzen + Startmeldung (vor "anpOk = AnpLesen();")
  6. FadeLive: TwSignalMerken (nur merken, keine Rechnung vor der Order)
  7. Durchlauf: TwBerichteAusgeben am Ende (nach allen Einstiegen und Ernten)
  8. TW-Funktionen am Dateiende
Mit TwBericht = false laufen nur zwei zusaetzliche if-Abfragen und das Zuruecksetzen in OnInit: Handel wie 8.10.
Aufruf: python3 patch_v9.py <DEADBAND_V8.mq5> <DEADBAND_V9.mq5 (neu)>
"""
import hashlib, os, sys

HIER = os.path.dirname(os.path.abspath(__file__))
BREITE = 66                                   # Zeichen zwischen "//|" und "|" (wie im V8-Kopf)


def box(zeilen):
    out = ["//+" + "-" * BREITE + "+"]
    for z in zeilen:
        assert len(z) <= BREITE, (len(z), z)
        out.append("//|" + z.ljust(BREITE) + "|")
    out.append("//+" + "-" * BREITE + "+")
    return "\n".join(out) + "\n"


KOPF = [
    "  DEADBAND V9  -  Build 9.00, 16.10.2026",
    "  BUILD 9.00: TRENDWENDE-PRUEFUNG - HANDEL UNVERAENDERT (= 8.10)",
    "  Anlass: Live 01.-16.10.2026 - 11 NAS-Long-Fades + S0830 mit",
    "  -3,55 R (-218 $) in einen Abwaertsschub hinein.",
    "  Geprueft nach vorab festgelegtem Protokoll (37 Konfigurationen,",
    "  freie M5-Daten 2010-2026, Replikat 9 = eng6-Konto + V8-Signale):",
    "  Sperre/halbes Risiko der NAS-Long-Fades + S0830 nach 10 Tages-",
    "  regeln R1-R10, Noise-Area-Veto, Tagesrichtung < -1 sigma und",
    "  Kombinationen; Gold-Shorts gespiegelt; Fade-Ziel 0,6R/Gegen-",
    "  seite/halb an der Mitte + Rest mit BE; LW erst ab 9:40; NAS-",
    "  Short-Fades nur im Abwaertsregime; Schluss-Momentum 15:30-15:55",
    "  (nur Long / beide); CPPI.",
    "  Uebernahme nur, wenn A (2016-21) UND B (2022-10/2026), 1 UND 2",
    "  Jahre: netto hoeher und Pleiten nicht hoeher; gesperrte Trades",
    "  Summe R < 0 in A und B; >= 5/7 der Startjahre positiv; besteht",
    "  Spread x1,5 und x2.",
    "  ERGEBNIS: KEINE Aenderung besteht. Basis netto/J: A 1 J 1064 $,",
    "  B 1 J 3031 $, 0 Pleiten. Am knappsten: LW ab 9:40 (B 2 J -4 $),",
    "  R9 Vola-Sprung (B-Sperren -3,0 R, aber nur 4/9 Startjahre),",
    "  NAS-Short nur bei R3 (A nicht hoeher). Im Oktober haette die",
    "  beste Regel R2 2,4 R gespart, 2022-26 aber +24,5 R Gewinner",
    "  gesperrt (R1 +50 R, R8 +58 R).",
    "  NEU NUR: Trendwende-Bericht im Journal (TwBericht): Tagesstand",
    "  R1-R10 je Symbol einmal je Servertag, je Fade-Signal die Regeln",
    "  der Gegenrichtung und (NAS) Noise Area NA/TR. Kein Einfluss auf",
    "  Orders, Groessen, Panel oder Kontologik. Ausgabe am Ende von",
    "  Durchlauf, nach allen Einstiegen.",
    "  Rechenkern TwRegeln/TwNoise mechanisch nach C++ uebersetzt und",
    "  gegen regime9.py geprueft: 0 Abweichungen (8672 D1-Tage, auch",
    "  rollierend 400 Tage wie im EA; 6515 NAS-Signale).",
    "  RUECKFALL: TwBericht = false (Handel in beiden Faellen = 8.10).",
    "  Bericht: DEADBAND_V9_Bericht.md, Set: DEADBAND_V9_Echtbetrieb.",
    "  NICHT KOMPILIERT ERSTELLT - vor dem Einsatz im MetaEditor",
    "  kompilieren und im Strategietester (Echte Ticks) pruefen.",
]

EINGABE = """input group             "=== 9.00: Trendwende-Bericht (nur Journal, kein Einfluss auf den Handel) ==="
input bool   TwBericht        = true;       // 9.00: Tagesregeln R1-R10 je Servertag und je Fade-Signal (NAS: Noise Area) ins Journal (false = ohne Bericht; Handel in beiden Faellen wie 8.10)
"""

INIT = """   for(int q=0;q<MAXSYM;q++) { twDn[q] = 0; twUp[q] = 0; twTag[q] = 0; twStand[q] = 0; }       // 9.00: Trendwende-Bericht neu aufsetzen
   twQn = 0; twQweg = 0; twVersuch = 0;
   PrintFormat("DEADBAND9: Build 9.00 - Handel wie 8.10 | Trendwende-Bericht %s (nur Journal, Regeln R1-R10, NA/TR; Bericht DEADBAND_V9_Bericht.md)", (TwBericht ? "AN" : "AUS"));
"""

FADELIVE_ALT = """   int k = F[m].k; string s = S[k].sym;
   string grund = "";
   if(!FadeAktiv) grund = "Modul aus";"""
FADELIVE_NEU = """   int k = F[m].k; string s = S[k].sym;
   if(TwBericht) TwSignalMerken(m, d, tSig);                                   // 9.00: nur merken, Bericht am Ende von Durchlauf
   string grund = "";
   if(!FadeAktiv) grund = "Modul aus";"""

DURCH_ALT = """   if(GeAktiv && kMode==0) GewinnErntePruefen();
   ZyklusPanel();
  }"""
DURCH_NEU = """   if(GeAktiv && kMode==0) GewinnErntePruefen();
   if(TwBericht) TwBerichteAusgeben();                                 // 9.00: Trendwende-Bericht (nur Journal), nach allen Einstiegen dieses Durchlaufs
   ZyklusPanel();
  }"""


def ersetze(t, alt, neu, was):
    n = t.count(alt)
    assert n == 1, f"{was}: Anker {n}-mal gefunden"
    return t.replace(alt, neu)


def block_teilen():
    b = open(os.path.join(HIER, "tw_block.mq5")).read()
    a = b.index("#define TW_NR")
    e = b.index("// gleitender Mittelwert")
    kopf = b[:a]
    glob = b[a:e].rstrip() + "\n"
    funk = b[e:]
    # Kasten des Blocks auf die V8-Breite bringen
    zz = []
    for z in kopf.splitlines():
        if z.startswith("//|"):
            inhalt = z[3:].rstrip()
            inhalt = inhalt[:-1].rstrip() if inhalt.endswith("|") else inhalt
            zz.append(inhalt)
    return box(zz), glob, funk


def main(v8, v9):
    assert os.path.abspath(v8) != os.path.abspath(v9)
    assert not os.path.exists(v9), f"{v9} existiert schon - nur neue Dateien anlegen"
    t = open(v8, encoding="ascii").read()
    sha8 = hashlib.sha256(t.encode()).hexdigest()
    tw_box, tw_glob, tw_funk = block_teilen()
    t = box(KOPF) + t                                                                      # 1
    t = ersetze(t, '#property version   "8.10"', '#property version   "9.00"', "version")   # 2
    t = ersetze(t, "input double KaufPuffer    = 2.0;\n", "input double KaufPuffer    = 2.0;\n" + EINGABE, "Eingabe")  # 3
    t = ersetze(t, "int      nSym = 0;\n", "int      nSym = 0;\n// 9.00: Trendwende-Bericht (Funktionen am Dateiende)\n" + tw_glob, "Globale")  # 4
    t = ersetze(t, "   anpOk = AnpLesen();", INIT + "   anpOk = AnpLesen();", "OnInit")  # 5
    t = ersetze(t, FADELIVE_ALT, FADELIVE_NEU, "FadeLive")                                 # 6
    t = ersetze(t, DURCH_ALT, DURCH_NEU, "Durchlauf")                                      # 7
    t = t.rstrip("\n") + "\n\n" + tw_box + tw_funk                                         # 8
    t.encode("ascii")                                                                      # nur ASCII wie V8
    with open(v9, "x", encoding="ascii", newline="\n") as f:
        f.write(t)
    print(f"V8 {v8} sha256 {sha8}")
    print(f"V9 {v9} {len(t.splitlines())} Zeilen sha256 {hashlib.sha256(t.encode()).hexdigest()}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
