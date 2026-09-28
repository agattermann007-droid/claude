"""Build 6.70: Presets aus den 6.60-Sets ableiten (Kopf neu, neue Eingaben RegimeGroesse/FadeTagessperre nach FadeFruehwarnPF).
Aufruf (einmal): python mk_sets670.py"""
import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def body(fn):
    lines = open(os.path.join(D, fn), encoding="utf-8").read().split("\n")
    return [l for l in lines if l and not l.startswith(";")]


def with_new(b, regime, sperre):
    out = []
    for l in b:
        out.append(l)
        if l.startswith("FadeFruehwarnPF="):
            out.append(f"RegimeGroesse={regime}")
            out.append(f"FadeTagessperre={sperre}")
    assert sum(l.startswith("RegimeGroesse=") for l in out) == 1
    return out


def write(fn, head, b):
    open(os.path.join(D, fn), "w", encoding="utf-8").write("\n".join([f"; {h}" if h else ";" for h in head] + b) + "\n")
    print(fn, len(b), "Eingaben")


GEMEINSAM = [
    "Replikat, 16 Stoerungen, jeder Handelstag ein neues Konto; Auszahlungen/J / Netto/J (breite / GFT-nahe Spreads):",
    "  GFT-Ersatz 2022-25:   6.60 = 6.70 Echtbetrieb 11,53 / 2244 $  -  12,05 / 2493 $, 0 Busts",
    "                        Regimeschutz            11,53 / 2244 $  -  12,05 / 2492 $, 0 Busts",
    "                        Tagessperre             11,89 / 2322 $  -  12,39 / 2552 $, 0 Busts, laengste Serie 6,4 / 6,2 (6.60: 7,2 / 7,3)",
    "  Zukunftstest 2026 (100-Tage-Konten; seit 6.60 verbraucht, nur berichtet):",
    "                        6.60 = Regimeschutz     12,54 / 2229 $  -  12,38 / 2319 $",
    "                        Tagessperre             12,48 / 2194 $  -  12,21 / 2272 $ (schlechter, 5-7 von 16 Stoerungen besser)",
    "  Fremddaten 2006-21 (altes Regime, Fades meist nur virtuell): Auszahlungen/J / Netto/J / Busts je Jahr / Bust im 1. Jahr:",
    "                        6.60 = 6.70 Echtbetrieb 2,15 / 363 $ / 0,038 / 1,0 %",
    "                        Regimeschutz            1,48 / 248 $ / 0,0065 / 0,2 %",
    "                        Tagessperre             1,46 / 242 $ / 0,0100 / 0,2 %",
]
BETRIEB = [
    "WICHTIG: Extras > Optionen > Charts > Max. Balken im Chart = Unbegrenzt (Waechter ~600 Tage M5, Grid 300 Tage mehr).",
    "Nur auf dem eigenen PC (GFT: VPS/Server verboten), EIN Chart (XAUUSD.x M15), kein zweites Konto mit Gegenposition.",
    "Beim Laden: Journal-Zeilen 'KONTO ERKANNT' und MQL5\\Files\\DEADBAND4_Konto_<Login>.txt mit dem GFT-Dashboard vergleichen,",
    "  je Symbol 'GRID ...: Historie ab ...' (ohne WARNUNG), 'FADE Portfolio-Waechter: PF ...' und '6.70 Regime | Handel wie 6.60'.",
    "Nach dem Beantragen einer Auszahlung: AuszahlungAngefordertAm = Zeitpunkt (Serverzeit) setzen; nach der Buchung wieder leeren.",
    "Teilauszahlung (Saldo bleibt ueber dem Startsaldo): AuszahlungZeiten = Buchungszeit (Serverzeit) setzen.",
    "FloorOverride nur zusammen mit FloorOverrideZeit (Zeitpunkt der Dashboard-Ablesung), sonst startet der EA nicht.",
]

e = body("DEADBAND_LIVE4_Echtbetrieb.set")
write("DEADBAND_LIVE4_Echtbetrieb.set", [
    "DEADBAND LIVE 6.70 REGIME - ECHTBETRIEB (Auspraegung Ertrag), GFT Instant Premium 10k (Konto ab 02.09.2026).",
    "Alle Werte = Voreinstellung des EA. Der Handel ist UNVERAENDERT wie 6.60: Fade-Risiko 0,75 %, Schutz gueltiger Tage je Modul",
    "  (N1330/N1300 frei, RSI21 ab 13:00 NY im Fade-Regime), Portfolio-Waechter PF200 > 1,15, Pufferkurve 5 / 2,5 / x0,2,",
    "  Regime-Meldungen. Neu in 6.70 sind nur zwei Optionen, hier AUS: RegimeGroesse=1.0, FadeTagessperre=0.",
    "Warum keine neue Voreinstellung: Nach dem vorab festgelegten Pruefprotokoll (Replikat_v6/PROTOKOLL_670.md) hat keine der 10",
    "  gepruften Ideen mehr Netto, mehr Auszahlungen und weniger Verlustserien robust geliefert (Bericht 6.70, Abschnitt 1).",
    "Optionen als eigene Sets: DEADBAND_LIVE4_670_Regimeschutz.set (Kontoschutz bei einem Regimewechsel) und",
    "  DEADBAND_LIVE4_670_Tagessperre.set (Test-Option, nur nach eigenem Strategietester-Lauf auf GFT-Kursen).",
] + GEMEINSAM + [
    "Pufferkurve NICHT lockern (Bericht 6.40, Abschnitt 3.4). FadeRiskPct nicht ueber 0,75 (Floating-Bremse bei -0,8 %).",
    "Die ~30 Tage je Auszahlung setzen voraus: Auszahlung sofort beantragen, wenn der EA 'JETZT AUSZAHLUNG BEANTRAGEN' meldet.",
    "Regime-Meldungen: Push 'FADE-REGIME AUS' (PF der letzten 200 Fade-Signale <= 1,15) - dann zahlt der EA deutlich seltener",
    "  aus (Fremddaten 2006-21: rund alle 170 Tage). Wer dann das Konto schonen will: RegimeGroesse=0.5 (Regimeschutz-Set).",
] + BETRIEB + [
    "Zurueck auf 6.60: rollback_6.60/ (mq5 und beide Sets); mit diesem Set rechnet 6.70 genau wie 6.60. Bericht: DEADBAND_LIVE4_670_Bericht.md.",
], with_new(e, "1.0", "0"))

write("DEADBAND_LIVE4_670_Regimeschutz.set", [
    "DEADBAND LIVE 6.70 REGIME - Auspraegung REGIMESCHUTZ (Option), GFT Instant Premium 10k (Konto ab 02.09.2026).",
    "Wie das Echtbetrieb-Set, aber RegimeGroesse=0.5: RSI21 und Noise mit halber Groesse, solange der Portfolio-Waechter die",
    "  Fades NICHT live handeln laesst (PF der letzten 200 virtuellen Fade-Signale <= 1,15, auch solange die Fade-Historie laedt).",
    "Wirkung: im heutigen Regime (Fades live; 2022-25 zu 88 %, 2026 immer) keine. Nach einem Regimewechsel (Fremddaten 2006-21)",
    "  6x seltener Busts, dafuer weniger Auszahlungen und Netto - eine Versicherung, kein Mehrertrag. Unter Stress (20 % der",
    "  Fade-Gewinner entfernt, 2022-25): breit 5,94 statt 6,29 Auszahlungen, Konten < 100 $ am Boden 0,3 statt 3,2 %.",
] + GEMEINSAM + BETRIEB + ["Bericht: DEADBAND_LIVE4_670_Bericht.md (Abschnitt 5)."], with_new(e, "0.5", "0"))

write("DEADBAND_LIVE4_670_Tagessperre.set", [
    "DEADBAND LIVE 6.70 REGIME - Auspraegung TAGESSPERRE (TEST-OPTION), GFT Instant Premium 10k (Konto ab 02.09.2026).",
    "Wie das Regimeschutz-Set, dazu FadeTagessperre=1: nach einem Fade-Verlust im Symbol keine weiteren Fades in diesem Symbol",
    "  bis 17:00 NY. Auf dem GFT-Ersatz 2022-25 mehr Auszahlungen, mehr Netto und kuerzere Serien (14 bzw. 13 von 16 Stoerungen),",
    "  im Zukunftstest 2026 aber etwas schlechter, und auf Signal-Ebene waren die gesperrten Signale 2024-26 nicht schlechter als",
    "  die uebrigen. Deshalb NICHT Voreinstellung: nur nach eigenem Strategietester-Lauf (jeder Tick anhand realer Ticks, GFT-Kurse)",
    "  gegen das Echtbetrieb-Set verwenden.",
] + GEMEINSAM + BETRIEB + ["Bericht: DEADBAND_LIVE4_670_Bericht.md (Abschnitt 4 und 5)."], with_new(e, "0.5", "1"))

s = body("DEADBAND_LIVE4_660_Sicher.set")
write("DEADBAND_LIVE4_670_Sicher.set", [
    "DEADBAND LIVE 6.70 REGIME - Auspraegung SICHER (nur die 10 Fehlausbruch-Fades), GFT Instant Premium 10k (Konto ab 02.09.2026).",
    "Unveraendert wie 6.60 Sicher: R21Aktiv=false, NzAktiv=false, SerienStopp=4, GueltigSchutzFrei leer, Fade-Risiko 0,70 %,",
    "  Regime-Meldungen. Die 6.70-Optionen sind aus (RegimeGroesse wirkt hier ohnehin nicht: kein RSI21, kein Noise).",
    "Replikat GFT-Ersatz 2022-25 (Bericht 6.50): 51,4 T je Auszahlung (7,11 Ausz/J) breit, 45,7 T (8,00) GFT-nah, 0 Busts.",
    "ACHTUNG Inaktivitaet: schaltet der Portfolio-Waechter die Fades ab (anderes Marktregime), handelt 'Sicher' womoeglich",
    "  wochenlang nicht. GFT: 30 Tage ohne Trade = Konto weg. Kommt der Push nach 20 Tagen ohne Einstieg, von Hand einen",
    "  kleinen Trade setzen (0,01 Lot, > 2 min halten). Die Push-Meldung 'FADE-REGIME AUS' kuendigt das an.",
], with_new(s, "1.0", "0"))
