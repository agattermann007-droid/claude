# DEADBAND LIVE 4 – Build 6.70 REGIME

Bericht vom 26.09.2026 · GFT Instant Premium 10k (Konto ab 02.09.2026) · Ausgangspunkt: hochgeladene Datei
`DEADBAND_FINAL1.mq5` = Build 6.60 ZUKUNFT (identisch mit dem Stand `6af75df`)

## 1. Kurzfassung

**Auftrag:** 6.60 verbessern – mehr Nettogewinn, mehr Auszahlungen, weniger Verlustserien. Wie bei allen Builds seit 6.00
gilt zusätzlich: nicht mehr Bust-Risiko.

**Ergebnis:** Eine Änderung, die alle drei Ziele **robust** verbessert, gibt es in dem geprüften Raum nicht. Geprüft wurden
10 Kandidaten in 28 Konto-Varianten, nach einem Prüfprotokoll, das **vor** den Tests festgelegt und gepusht wurde
(`Replikat_v6/PROTOKOLL_670.md`, zwei Nachträge vor Runde 2 und 3). Keiner hat alle Kriterien erfüllt.

**Build 6.70 handelt deshalb mit den Voreinstellungen genau wie 6.60.** Neu sind zwei geprüfte Optionen, beide ab Werk
**aus**, jeweils mit eigenem Preset:

| Kennzahl (Replikat, 16 Störungen) | 6.60 = 6.70 Echtbetrieb | Option **Regimeschutz** (`RegimeGroesse=0.5`) | Option **Tagessperre** (Regimeschutz + `FadeTagessperre=1`) |
|---|---:|---:|---:|
| **GFT-Ersatz 2022–25**, breite / GFT-nahe Spreads | | | |
| Auszahlungen je Jahr | 11,53 / 12,05 | 11,53 / 12,05 | **11,89 / 12,39** |
| Netto je Jahr | 2244 / 2493 $ | 2244 / 2492 $ | **2322 / 2552 $** |
| Serien ≥ 5 · ≥ 6 Verluste je Jahr | 1,93 · 0,84 / 1,73 · 0,86 | gleich | **1,71 · 0,79 / 1,57 · 0,63** |
| längste Serie, Mittel / schlimmste | 7,2 / 10 · 7,3 / 10 | gleich | **6,4 / 9 · 6,2 / 10** |
| Busts · kleinster Abstand zum Boden | 0 · 255 / 251 $ | 0 · 255 / 251 $ | 0 · 270 / 264 $ |
| **Zukunftstest 2026** (100-Tage-Konten; seit 6.60 verbraucht, nur berichtet) | | | |
| Auszahlungen · Netto, breit / GFT-nah | 12,54 · 2229 $ / 12,38 · 2319 $ | gleich | 12,48 · 2194 $ / 12,21 · 2272 $ |
| **Fremddaten 2006–21** (altes Regime, Fades meist nur virtuell) | | | |
| Auszahlungen · Netto je Jahr | 2,15 · 363 $ | 1,48 · 248 $ | 1,46 · 242 $ |
| Busts je Jahr · Bust im 1. Jahr | 0,038 · 1,0 % | **0,0065 · 0,2 %** | 0,010 · 0,2 % |
| **Stress** (20 % der Fade-Gewinner entfernt, 2022–25), breit / GFT-nah | | | |
| Auszahlungen | 6,29 / 8,33 | 5,94 / 8,14 | 6,11 / 8,67 |
| Konten nahe am Boden: breit < 100 $ / GFT-nah < 200 $ | 3,2 % / 30,1 % | 0,3 % / 33,0 % | 0,5 % / 11,5 % |

- **Regimeschutz** ist eine Versicherung, kein Mehrertrag: Solange die Fades live handeln (2022–25 zu 88 % der Zeit, 2026
  immer), ändert sich nichts. Endet das Fade-Regime, handeln RSI21 und Noise mit halber Größe: sechsmal seltener Busts, aber
  weniger Auszahlungen und weniger Netto (auch unter Stress). Da Netto die Neukäufe schon abzieht, ist 6.60 selbst im alten
  Regime im Mittel ertragreicher. Wer das Konto bei einem Regimewechsel lieber schont, nimmt das Preset.
- **Tagessperre** hätte auf 2022–25 alle drei Ziele verbessert (Auszahlungen besser in 14 bzw. 13 von 16 Störungen). Der
  Vorteil schrumpft aber von Jahr zu Jahr (Start 2022: +0,74, 2025: ±0,00 bzw. +0,16 Auszahlungen) und ist im Zukunftstest 2026
  weg (−0,07 / −0,16 Auszahlungen). Auf Signal-Ebene waren die gesperrten Fades 2024–26 sogar besser als die übrigen. Deshalb
  nur als Test-Option: erst nach einem eigenen Lauf im Strategietester auf GFT-Kursen (siehe Abschnitt 10).
- **Warum nicht mehr geht** (Abschnitt 3–6):
  1. Engpass sind die gültigen Tage. Das Ziel eines Fades zu verlängern, damit ein kleiner Treffer den Tag gültig macht (meine
     Hauptidee Z1), kostet in allen neun Varianten Auszahlungen und Netto: Nach der Range-Mitte läuft der Kurs meist zurück.
  2. Was Verlustserien direkt verkürzt (Fade-Einstand, Serien-Stopp 2, Tages-Einstiegsstopp, Noise-Pause, Noise mit einer
     Position), kostet gültige Tage und damit Auszahlungen.
  3. Mehr RSI21 an gültigen Tagen (ab 11:00 NY) bringt Netto, aber 2024–25 weniger Auszahlungen.
- **Verlustserien im MT5-Bericht:** MT5 und das GFT-Dashboard zählen jede Position. Ein Noise-Verlust zählt dort bis zu dreimal
  (drei Teilpositionen). Je Position gibt es deshalb 7,8 Serien ≥ 5 im Jahr und eine längste Serie von 9,0 im Mittel (höchstens
  11–15), je Idee 2,4 und 6,8 (Abschnitt 3.4). Das ist kein Fehler des EA; die Zahlen in diesem Bericht zählen je Idee wie
  der Serien-Stopp.
- **Nicht geprüft:** Kompilieren in MetaEditor, Strategietester, Demo. Das bleibt Pflicht (Abschnitt 10).

## 2. Vorgehen

### 2.1 Daten und Replikat

- **Kursdaten neu aufgebaut** aus den Quellen des Datenberichts (`extdata/DATEN_BERICHT.md`): alle Rohdaten mit den dort
  genannten Commits und SHA-256 geladen, `run_all.sh` und `build_nas_dukascopy.py` ausgeführt. Die fünf Hauptdateien und
  `NAS100_duka_M5.csv` sind **byte-identisch** mit dem 6.60-Stand.
- **Basis reproduziert:** 6.60 auf dem GFT-Ersatz breit 11,53 Auszahlungen / 2244 $ je Jahr, GFT-nah 12,05 / 2493 $,
  Fremddaten 2,15 / 0,038 Busts / 363 $, Stress 6,29 / 1217 $ bzw. 8,33 / 1654 $, Zukunftstest 2026 12,54 / 2229 $ bzw.
  12,38 / 2319 $ – alles exakt wie im Bericht 6.60.
- **Motor `eng11`** = `eng10` plus die Schalter der Kandidaten (Ziel für den gültigen Tag, Tagessperre der Fades je Symbol,
  Noise-Tagespause, Regime-Größe, Noise mit einer Position) und die Ausstiegszeit im Trade-Protokoll. Mit Voreinstellungen
  rechnet er exakt wie `eng10` (`t_eng11.py`: 45 Konten, alle Zähler, Trades und Ereignisse identisch; jeder Schalter wirkt).
- **Bewertung `evl11`** = `evl10`, zusätzlich Verlustserien je Position (MT5-Zählung). Screening `x70.py`, Zukunftstest
  `x70f.py`.

### 2.2 Prüfprotokoll (vorab)

`Replikat_v6/PROTOKOLL_670.md` wurde vor den Konto-Tests festgelegt und gepusht (Commit `13eb71e`; Nachtrag 1 vor Runde 2
in `c520e53`, Nachtrag 2 vor Runde 3 in `067da17`). Eine Änderung wird nur übernommen, wenn alle Kriterien gelten:

| | Kriterium |
|---|---|
| K-a | Screening (8 Störungen, jeder 2. Handelstag), beide Spread-Lagen: ein Ziel deutlich besser (Auszahlungen ≥ +0,2 oder Netto ≥ +3 % oder Serien ≥ 6 ≤ −20 % bei Serien ≥ 5 nicht schlechter), keines schlechter (Auszahlungen ≥ −0,1, Netto ≥ −1 %, Serien ≤ +5 %) |
| K-b | Walk-Forward: gewählt wird mit den Konten, die 2022–23 starten; die Konten mit Start 2024–25 dürfen bei Auszahlungen und Netto nicht schlechter sein |
| K-c | Sicherheit: 0 Busts; Abstand zum Boden ≥ Basis − 10 $; Konten < 100 $ höchstens +0,5 Prozentpunkte; Fremddaten: Busts je Jahr ≤ Basis + 0,005, Bust im 1. Jahr ≤ +0,5 Prozentpunkte |
| K-d | Paarweise über 16 Störungen: Hauptziel in ≥ 12 von 16 besser, beide Spread-Lagen |
| K-e | Plateau: Nachbarwerte bestehen K-a ebenfalls |
| K-f | Höchstens zwei neue Eingaben; Werte aus der Regelmechanik |
| K-g | Stress: Sicherheit nicht schlechter als die Basis unter demselben Abschlag |

Der Zukunftstest 2026 ist seit 6.60 verbraucht. Er wird berichtet; ab Runde 2 gilt ein paarweise um mehr als einen
Standardfehler schlechteres Ergebnis als Warnsignal.

## 3. Diagnose der Basis 6.60

### 3.1 Verlustserien (`a70_diag.py`)

1-Jahres-Konten 2022–25, jeder 2. Handelstag: 2,36 Serien ≥ 5 je Jahr.

| Modul | Anteil an allen Verlusten | Anteil an den Verlusten in Serien ≥ 5 |
|---|---:|---:|
| Noise | 24,0 % | **33,4 %** |
| RSI21 | 17,0 % | **21,6 %** |
| X0630 / X0300S / X0400 (Gold-Fades) | 10,7 / 7,3 / 6,3 % | 9,6 / 9,4 / 6,6 % |
| N1330 / N1300 (NAS nachmittags) | 7,3 / 5,3 % | 2,2 / 4,3 % |

**65 %** der Verluste in einer Serie liegen am selben Tag wie der vorige Verlust.

### 3.2 Knapp verfehlte gültige Tage

- 55,8 Handelstage je Jahr enden mit 0–50,50 $ realisiert, **48,7 davon mit einem Fade-Gewinn**.
- N1330 (46 Trades je Jahr, 80 % Treffer) trifft sein Ziel immer unter 0,71 R (Median 0,28 R), N1300 (33, 80 %) zu 95 %
  (Median 0,45 R), X0630 und X1000S in 68 % der Treffer.

### 3.3 Verlorene gültige Tage und Gewinne an schon gültigen Tagen (`a70_verl.py`)

- 71,4 Tage je Jahr sind zwischendurch gültig, 3,5 davon am Ende nicht mehr. Die Verluste danach stammen überwiegend von
  Positionen, die **nach** dem Gültigwerden eröffnet wurden (die 6.50 bewusst freigab): Fades 2,43 (vorher 0,87), RSI21 0,89
  (0,75), Noise 0,34 (0,36) je Jahr.
- Gewinne am selben Tag nach dem Gültigwerden (für den Takt überzählig): Fades 26 je Jahr (435 $), Noise 10,5 (161 $), RSI21
  6,6 (323 $); RSI21-Ziele darunter 3,3 je Jahr.
- **Abschätzung ohne Konto-Test:** Die Positionen, die beim Gültigwerden schon offen waren, per Stop-Nachzug zu sichern, könnte
  höchstens rund 1,5 gültige Tage je Jahr retten; ein RSI21-Ziel an einem schon gültigen Tag auf den Folgetag zu verschieben
  höchstens rund 1,9 (der Folgetag war in 43 % der Fälle ohnehin gültig). Beides zusammen weniger als +0,7 Auszahlungen als
  Obergrenze, vor Kosten und mit Übernacht-Risiko. Nicht weiter verfolgt.

### 3.4 Verlustserien je Position (MT5-Zählung)

Basis 6.60, 1-Jahres-Konten, ohne Störung (`evl11`, Spalten `s5p`/`s6p`/`mxp`):

| Zählung | Serien ≥ 5 je Jahr | Serien ≥ 6 je Jahr | längste Serie Mittel / höchstens |
|---|---:|---:|---:|
| je Idee (Bericht, Serien-Stopp) | 2,36 | 0,98 | 6,8 / 10 |
| je Position (MT5-Bericht, GFT-Dashboard) | **7,79** | **4,82** | **9,0 / 11** |

Im Screening (8 Störungen) je Position breit 7,66 / 4,49 / 9,4 (höchstens 15), GFT-nah 6,40 / 3,71 / 9,1 (13).

### 3.5 Busts im alten Regime (`a70_bust.py`)

Alle Busts der Fremddaten 2006–21 liegen in zwei Episoden: Februar–Juni 2010 und April 2011. Die Fades waren von August 2009
bis Februar 2010 live und ab März 2010 nur virtuell. Rund **70 %** der Busts (März–Juni 2010) fallen in die Zeit **nach** dem
Abschalten der Fades, wenn nur RSI21 und Noise handeln. (Der Nachtrag 1 nannte grob 60 %.)

## 4. Runde 1: Kandidaten Z1–Z6

### 4.1 Screening (8 Störungen, jeder 2. Handelstag)

Zellen: Auszahlungen · Netto · Serien ≥ 6 · längste Serie im Mittel. WF = Start 2024–25 (Auszahlungen · Netto).

| Idee | Variante | breit | GFT-nah | WF breit / GFT-nah | Urteil |
|---|---|---|---|---|---|
| Basis | 6.60 | 11,66 · 2282 $ · 0,88 · 7,4 | 12,04 · 2503 $ · 0,82 · 7,3 | 8,82 · 1478 / 8,92 · 1571 | |
| Z1 Ziel für den gültigen Tag | L 0,5 / M 1,0 (Mitte) | 11,26 · 2062 $ · 0,92 · 7,2 | 11,84 · 2215 $ · 0,75 · 7,1 | 8,61 · 1391 / 8,60 · 1422 | nein |
| | beste der 9 (L 0,7 / M 0,8) | 11,47 · 2155 $ · 0,96 · 7,3 | 11,75 · 2337 $ · 0,78 · 7,2 | 8,77 · 1446 / 8,42 · 1419 | nein |
| Z2 Tagessperre je Symbol | 1 Verlust | **11,92 · 2326 $** · 0,90 · **6,5** | **12,35 · 2551 $ · 0,59 · 5,9** | 9,04 · 1540 / 9,13 · 1556 | weiter (Endbewertung) |
| | 2 Verluste (Nachbar) | 11,72 · 2291 $ · 0,85 · 7,3 | 12,10 · 2511 $ · 0,87 · 7,3 | 8,95 · 1497 / 9,02 · 1581 | K-a nein |
| Z3 Fade-Einstand | ab 0,5 R | 9,68 · 1851 $ · 0,70 · 6,9 | 11,06 · 2233 $ · 0,43 · 7,0 | 8,64 · 1436 / 9,17 · 1628 | nein |
| | ab 0,6 R | 10,98 · 2219 $ · 0,70 · 6,8 | 11,72 · 2471 $ · 0,31 · 6,2 | 9,09 · 1522 / 9,38 · 1624 | nein |
| | ab 0,75 R | 11,40 · 2233 $ · 0,67 · 6,8 | 11,78 · 2392 $ · 0,46 · 6,6 | 9,63 · 1608 / 9,55 · 1629 | nein |
| Z4 Serien-Stopp 2 | | 11,79 · 2322 $ · **0,60** · 6,9 | 11,83 · 2419 $ · **0,41** · 6,6 | 9,23 · 1606 / 9,04 · 1615 | nein (GFT-nah) |
| Z5 Tages-Einstiegsstopp | 0,5 % | 10,78 · 2010 $ · 0,98 · 7,8 | 11,46 · 2243 $ · 0,84 · 7,1 | 8,34 · 1415 / 8,49 · 1474 | nein |
| | 0,75 % (Mitte) | 11,66 · 2202 $ · 0,58 · 6,2 | 11,97 · 2348 $ · 0,58 · 6,2 | 8,98 · 1532 / 8,77 · 1549 | nein (Netto) |
| | 1,0 % | 11,77 · 2314 $ · 0,84 · 6,6 | 12,10 · 2521 $ · 0,56 · 6,6 | 8,88 · 1506 / 8,87 · 1568 | nein (breit nicht deutlich) |
| Z6 Noise-Tagespause | nach 1 Teil | 11,02 · 2164 $ · 0,73 · 7,0 | 11,57 · 2299 $ · 0,76 · 7,3 | 8,45 · 1388 / 8,64 · 1463 | nein |
| | nach 2 Teilen | 11,21 · 2187 $ · 0,87 · 7,3 | 11,65 · 2360 $ · 0,78 · 7,4 | 8,69 · 1449 / 8,68 · 1518 | nein |

- **Z1 Ziel für den gültigen Tag mit Gewinnsicherung:** Erreicht ein Fade sein Ziel, ohne dass das Schließen den Tag gültig
  macht, bleibt er offen (Stop auf Einstieg + L × Zielweite, neues Ziel dort, wo der Tag gültig wird, höchstens M R).
  Verlängert wurden 22–40 Ziele je Jahr, erreicht nur 1,5–10,8. Meist endete der Trade am gesicherten Stop mit weniger Gewinn
  als am alten Ziel: Tage mit 25–50 $ wurden zu Tagen mit 0–25 $, gültige Tage kamen keine hinzu. Die Range-Mitte wirkt wie ein
  Magnet. **Verworfen**, und zwar in allen neun Varianten.
- **Z3 Fade-Einstand:** Serien ≥ 6 um 20–60 % seltener, aber viele Ziel-Treffer enden am Einstand: weniger gültige Tage,
  −0,26 bis −2 Auszahlungen.
- **Z4, Z5, Z6:** kürzere Serien, aber in mindestens einer Spread-Lage weniger Auszahlungen oder Netto.

### 4.2 Z2 in der Endbewertung (16 Störungen, jeder Handelstag)

| | breit | GFT-nah |
|---|---|---|
| Auszahlungen (paarweise, besser in … von 16) | 11,88 statt 11,53: **+0,35 ± 0,11 (14)** | 12,39 statt 12,05: **+0,33 ± 0,10 (14)** |
| Netto | 2322 statt 2244 $: +77 ± 22 $ (14) | 2552 statt 2493 $: +59 ± 22 $ (12) |
| Serien ≥ 5 · ≥ 6 · längste Serie | 1,71 · 0,79 · 6,4 statt 1,93 · 0,84 · 7,2 | 1,57 · 0,63 · 6,2 statt 1,73 · 0,86 · 7,3 |
| Start 2024–25 (WF) | 9,22 · 1551 $ statt 9,05 · 1512 $ | 9,08 · 1579 $ statt 8,97 · 1581 $ (Netto −2 $) |
| Stress: Auszahlungen · Abstand · Konten < 100 $ | 6,32 · 196 $ · 2,9 % (Basis 6,29 · 192 $ · 3,2 %) | 8,75 · 243 $ · 0 % (8,33 · 223 $ · 0 %) |
| Fremddaten: Busts je Jahr · Bust im 1. Jahr | **0,0442 · 1,55 %** (Basis 0,0381 · 1,02 %) | – |
| Zukunftstest 2026 | 12,48 · 2194 $ statt 12,54 · 2229 $ (5 von 16 besser) | 12,21 · 2272 $ statt 12,38 · 2319 $ (6 von 16) |

- **K-c nicht erfüllt:** Fremddaten +0,0062 ± 0,0013 Busts je Jahr (Grenze +0,005), Bust im 1. Jahr +0,53 Prozentpunkte (Grenze
  +0,5). **K-e nicht erfüllt:** Nachbar „nach 2 Verlusten“ ohne deutliche Verbesserung.
- **Signal-Ebene** (`a70_sig.py`, live gehandelte Fade-Signale nach einem Fade-Verlust im Symbol am selben Prop-Tag):

| Zeitraum | gesperrte Signale je Jahr | deren Treffer · R je Signal | übrige live-Signale: Treffer · R |
|---|---:|---|---|
| 2006–13 | 2,1 | 47 % · −0,17 | 55 % · −0,06 |
| 2022–23 | 9,5 | 53 % · −0,07 | 70 % · +0,18 |
| 2024–25 | 21,5 | **74 % · +0,15** | 67 % · +0,13 |
| 2026 (bis Aug.) | 19,4 | **77 % · +0,20** | 63 % · +0,12 |

  Die Annahme „an einem Trendtag scheitern weitere Fades“ trifft nur 2022–23 zu. Seit 2024 waren die gesperrten Fades sogar
  besser als die übrigen. Der Kontovorteil 2024–25 kommt also nicht aus der Signalauswahl. **Nicht angenommen.**

## 5. Runde 2: Regime-Größe (Z9) und Kombinationen

Nach Abschnitt 3.5 entsteht das Bust-Risiko im alten Regime vor allem, wenn die Fades schon abgeschaltet sind.

| Variante | 2022–25 breit (8 Störungen) | GFT-nah | WF 2024–25 breit / GFT-nah | Fremddaten: Ausz. · Netto · Busts · Bust 1. J. | Urteil |
|---|---|---|---|---|---|
| 6.60 | 11,66 · 2282 $ | 12,04 · 2503 $ | 8,82 · 1478 / 8,92 · 1571 | 2,15 · 363 $ · 0,038 · 1,0 % | |
| Z9 F 0,3 | 11,63 · 2277 $ | 12,00 · 2493 $ | gleich | 0,98 · 185 $ · 0,008 · 0,2 % | |
| **Z9 F 0,5** | 11,65 · 2280 $ | 12,03 · 2498 $ | gleich | **1,48 · 248 $ · 0,0065 · 0,2 %** | Sicherheit ja, K-a nein |
| Z9 F 0,7 | 11,65 · 2281 $ | 12,04 · 2499 $ | gleich | 1,84 · 312 $ · 0,012 · 0,2 % | |
| Z10 = Z9 + Z2 | **11,93 · 2327 $** | **12,35 · 2551 $** | 9,04 · 1540 / 9,13 · 1556 | 1,46 · 242 $ · 0,010 · 0,2 % | K-e nein, 2026 Warnsignal |
| Z11 = Z9 + RSI21 ab 11:00 NY | 11,67 · **2466 $** | 12,14 · **2605 $** | **8,18** · 1514 / **8,65** · 1612 | 1,47 · 244 $ · 0,021 · 1,2 % | K-b nein |
| RSI21 ab 11:00 NY allein (6.50-Option) | 11,69 · 2470 $ | 12,14 · 2607 $ | 8,18 · 1514 / 8,65 · 1612 | 2,14 · 360 $ · 0,052 · 2,9 % | K-b, K-c nein |

- **Z9 Regime-Größe:** Im heutigen Regime praktisch ohne Wirkung (16 Störungen: breit 11,53 · 2244 $, GFT-nah 12,05 · 2492 $;
  2026 identisch). Im alten Regime sechsmal seltener Busts, der kleinste Abstand zum Boden steigt von 208 auf 272 $. Der
  Preis: weniger Auszahlungen und Netto ohne Fade-Regime, auch unter Stress (breit 5,94 statt 6,29 Auszahlungen, dafür 0,3 statt
  3,2 % der Konten unter 100 $ am Boden). Alle drei Werte (0,3 / 0,5 / 0,7) wirken gleichgerichtet. Z9 verbessert keines der
  drei Ziele (K-a) und wird deshalb **nicht** Voreinstellung, sondern Option.
- **Z10:** 2022–25 wie Z2 und im alten Regime sicherer als 6.60. Paarweise über 16 Störungen: Auszahlungen breit
  +0,36 ± 0,11 (14 von 16), GFT-nah +0,33 ± 0,10 (13); Serien ≥ 6 GFT-nah −0,24 ± 0,07 (14); längste Serie −0,8 bzw. −1,1 (13
  bzw. 15 von 16). Nach Startjahr schrumpft der Vorteil aber (Auszahlungen breit / GFT-nah: 2022 +0,74 / +0,74, 2023
  +0,22 / +0,24, 2024 +0,17 / +0,11, 2025 ±0,00 / +0,16), und **2026** liegt er darunter: breit −0,07 ± 0,12 Auszahlungen und
  −36 ± 35 $, GFT-nah −0,16 ± 0,14 und −47 ± 31 $ – ein Warnsignal im Sinne des Nachtrags. Dazu K-e (Nachbar von Z2) nicht
  erfüllt. **Nicht Voreinstellung, Test-Option.**
- **Z11:** mehr Netto (+8 % / +4 %), aber mit Start 2024–25 deutlich weniger Auszahlungen. Verworfen.
- **Serien-Stopp 2 als Option** (vorhandene Eingabe `SerienStopp`): 16 Störungen breit 11,77 · 2282 $ · Serien ≥ 6 0,53,
  GFT-nah 11,92 · 2436 $ · 0,41 (Basis 0,84 / 0,86); 2026 breit −0,34 ± 0,13 Auszahlungen, GFT-nah ohne kürzere Serien;
  Fremddaten 0,047 Busts je Jahr (mit Regimeschutz 0,014). Wer Serien stärker gewichtet als Auszahlungen, kann `SerienStopp=2`
  setzen; empfohlen wird es nicht.

## 6. Runde 3: Noise mit einer Position (Z12)

Nach Abschnitt 3.4: Noise mit einer einzigen Position am 0,5-Sigma-Stop (im EA `NzStops="0.5"`) statt drei Teilen.

| (8 Störungen) | Auszahlungen · Netto | Serien je Idee ≥ 5 · ≥ 6 · längste | Serien je Position ≥ 5 · ≥ 6 · längste |
|---|---|---|---|
| 6.60 breit | 11,66 · 2282 $ | 1,88 · 0,88 · 7,4 | 7,66 · 4,49 · 9,4 (höchstens 15) |
| Z12 breit | 10,98 · 2075 $ | 1,53 · 0,78 · 7,0 | **1,53 · 0,78 · 7,0 (10)** |
| 6.60 GFT-nah | 12,04 · 2503 $ | 1,67 · 0,82 · 7,3 | 6,40 · 3,71 · 9,1 (13) |
| Z12 GFT-nah | 11,16 · 2219 $ | 1,35 · 0,71 · 7,1 | **1,35 · 0,71 · 7,1 (9)** |

Die sichtbaren Serien im MT5-Bericht würden um vier Fünftel kürzer, aber es kostet 0,7–0,9 Auszahlungen und 9–11 % Netto: Die
Teile des Ensembles steigen einzeln wieder ein, und genau diese Wiedereinstiege tragen. **Verworfen.**

## 7. Entscheidung

| Kriterium | Z2 | Z9 | Z10 (Z9 + Z2) | Z11 | Z4 (Option) |
|---|---|---|---|---|---|
| K-a Ziel | erfüllt | **nicht** (kein Ziel besser) | erfüllt | erfüllt (Netto) | nicht (GFT-nah) |
| K-b Walk-Forward | erfüllt (GFT-nah Netto −2 $) | erfüllt | erfüllt (GFT-nah Netto −2 $) | **nicht** | erfüllt |
| K-c Sicherheit | **nicht** (Fremddaten) | erfüllt, deutlich besser | erfüllt, besser | erfüllt | nicht (Fremddaten) |
| K-d paarweise | erfüllt (14 / 14) | – | erfüllt (14 / 13) | – | – |
| K-e Plateau | **nicht** | erfüllt | **nicht** (Z2-Teil) | – | – |
| K-g Stress | erfüllt | erfüllt | erfüllt | – | – |
| Zukunftstest 2026 | schlechter | gleich | **Warnsignal** | – | breit schlechter |

**Übernommen als Voreinstellung: nichts.** 6.70 handelt ab Werk wie 6.60. Die Optionen stehen bereit:

1. `RegimeGroesse` (Preset `DEADBAND_LIVE4_670_Regimeschutz.set`) für alle, denen ein Bust nach einem Regimewechsel mehr weh
   tut als etwas weniger Ertrag in dieser Phase.
2. `FadeTagessperre` (Preset `DEADBAND_LIVE4_670_Tagessperre.set`, mit Regimeschutz) als Test-Option. Der EA läuft auf GFT-Kursen
   im Strategietester, das Replikat nur auf einem Ersatz aus Fremddaten: Zeigt der eigene Tester-Lauf 2024–2026 mit dem Preset
   mehr Auszahlungen und Netto als mit dem Echtbetrieb-Set, spricht das für die Option, sonst dagegen.

Geprüft wurden 28 Konto-Varianten und 4 Studien (Signal-Ebene und Abschätzungen). Bei so vielen Versuchen findet man leicht eine
Variante, die zufällig gut aussieht – deshalb die strengen Kriterien und der Blick auf 2026.

## 8. Was 6.70 ändert

| Eingabe | Voreinstellung | Bedeutung |
|---|---:|---|
| `RegimeGroesse` (neu) | **1,0 = aus** | RSI21 und Noise mit Faktor X, solange der Portfolio-Wächter die Fades nicht live handeln lässt (PF der letzten 200 virtuellen Fade-Signale ≤ 1,15). Zeitpunkt wie beim RSI21-Schutz seit 6.50: Open der Einstiegskerze (RSI21 `sigZeit`, Noise Ende der Prüfung `chkEnd`). Gilt auch, solange die Fade-Historie nach dem Start noch lädt. Wirkt nur auf neue Einstiege, nie vergrößernd. Erlaubt: 0 < X ≤ 1 |
| `FadeTagessperre` (neu) | **0 = aus** | nach X Fade-Verlusten im Symbol seit 17:00 NY keine neuen Fade-Einstiege in diesem Symbol bis 17:00 NY. Als Verlust zählt eine voll geschlossene Fade-Position, deren letztes Schließen (der Rest nach Teilschließungen, Ergebnis + Swap) im Minus lag – wie im Replikat; Teilschließungen der Abschluss-Ernte zählen nie. Die virtuellen Signale für den Wächter laufen weiter |

- **Mit den Voreinstellungen** rechnet der EA wie 6.60: `RegimeKlein()` kehrt sofort zurück, die Sperre wird nicht geprüft.
- **Journal beim Start:** `DEADBAND4: 6.70 Regime | Handel wie 6.60 (Voreinstellungen) | Regime-Groesse aus | Fade-Tagessperre aus`
  (mit Optionen: `, dazu Optionen | Regime-Groesse RSI21/Noise x0.50, solange die Fades nicht live sind | ...`). Kann die
  Regime-Größe nicht wie gedacht wirken, steht es gleich dabei: `WIRKUNGSLOS: Portfolio-Waechter aus (FadePortPF 0)` bzw.
  `WARNUNG Regime-Groesse: Fade-Module nicht angelegt - RSI21 und Noise bleiben DAUERHAFT bei x0.50`; bei
  `FadeWaechterModus=0` ein Hinweis, dass die Option trotzdem dem Portfolio-PF folgt.
- **Einstiegs-Journal:** RSI21 und Noise vermerken `Regime-Groesse x0.50`, wenn sie verkleinert wurden; die Fade-Sperre erscheint
  als Auslass-Grund `Fade-Tagessperre: 1 Fade-Verlust(e) heute in NAS100.x`.
- **Push-Meldungen des Regime-Wächters:** bei aktiver Regime-Größe mit dem Zusatz `RSI21/Noise x0.50` bzw.
  `RSI21/Noise wieder volle Groesse` (höchstens 198 Zeichen).
- **Panel:** Titel „DEADBAND LIVE 6.70 REGIME“. Die Zeile `Optionen 6.70` (Regime-Größe jetzt klein oder voll, Fade-Verluste
  heute je Symbol) erscheint nur, wenn eine Option an ist, und steht ganz unten: MT5 zeigt im Chart-Kommentar nur rund 2045
  Zeichen, die Statuszeilen darüber sollen nicht weiter nach hinten rutschen.
- **Nebenwirkung der Regime-Größe:** Die Mindestlot-Prüfung (`MinLotRiskTol`) vergleicht mit dem verkleinerten Risiko. Ist das
  kleinste Lot dafür zu groß, lässt der EA einen Noise-Teil bzw. einen RSI21-Zeitrahmen aus, statt ihn größer zu handeln. Größer
  als in 6.60 wird ein Trade nie.
- **Presets:** `DEADBAND_LIVE4_Echtbetrieb.set` (= Voreinstellungen), `DEADBAND_LIVE4_670_Regimeschutz.set`,
  `DEADBAND_LIVE4_670_Tagessperre.set`, `DEADBAND_LIVE4_670_Sicher.set` (= 6.60 Sicher, Optionen aus).
- **Rückweg:** `rollback_6.60/` (mq5 und beide 6.60-Sets). Mit dem Echtbetrieb-Set rechnet 6.70 ohnehin wie 6.60.

## 9. Prüfung

- **eng11 = eng10** mit Voreinstellungen (`t_eng11.py`, 45 Konten identisch; jeder neue Schalter ändert die Rechnung).
- **Abgleich EA ↔ Replikat** (`t_port_670.py`, Protokoll `Replikat_v6/ergebnisse/t_port_670.txt`): **identisch**.
  1. Voreinstellungen des EA = Replikat „6.60“, neue Eingaben aus; Presets Regimeschutz = Z9, Tagessperre = Z10, Sicher mit
     ausgeschalteten Optionen.
  2.–5. wie 6.60: Quelltext-Stellen und Entscheidung des Schutzes je Modul (164 640 Zustände), Fade-Regime für RSI21 (1036
     bzw. 3550 Signale), Regime-Meldungen ohne Einfluss auf den Handel.
  6. `RegimeKlein` = `!FadeRegimeLive(Open der M5-Kerze)`, genau an den zwei Stellen der Größenrechnung (RSI21 nach
     `BelowStartMult`, Noise auf `fak`); die Sperre in `FadeLive` nach dem Serien-Stopp; im Replikat an den gleichen Stellen.
  7. Fade-Regime zur Noise-Prüfzeit gegen `x70.nz_regime`: GFT-Ersatz 5838 Prüfungen (5265 live), Fremddaten 24 761 (1646 live),
     identisch.
  8. Tagessperre auf dem Trade-Protokoll des Replikats: kein Fade-Einstieg nach einem vorher am selben Prop-Tag geschlossenen
     Fade-Verlust im Symbol (14 392 Trades), 518 gesperrte Signale.
  9. Längste Push-Meldung 198 Zeichen mit dem Vorsatz `DEADBAND4: ` (Grenze 255).
  10. Zählung der Fade-Verluste im EA (`FadeVerlusteHeute`, Wort für Wort nachgebaut) gegen die Replikat-Regel: 5 Fälle
      (Abschluss-Ernte mit Gewinn und Rest am Stop, Stop in zwei Teil-Ausführungen derselben Sekunde, Ziel erreicht, nur
      Teilschließung bei offener Position, Zeit-Ausstieg durch Swap knapp im Minus) einzeln und zusammen: gleich (3 Verluste).
- **Presets** (`t_set.py`): Echtbetrieb-Set = alle 230 Voreinstellungen; die anderen weichen nur in den genannten Eingaben ab.
- **Statische Prüfung** (`t_mq5.py`): Klammern, Format-Argumente, Deklarationen vor der Verwendung, unbekannte Funktionen –
  bestanden.
- **Gegenlesen** der EA-Änderungen durch einen Sub-Agenten: siehe Abschnitt 9.1.
- **Nicht** geprüft: Kompilieren in MetaEditor, Strategietester, Demo.

### 9.1 Gegenlesen

Ein Sub-Agent hat die Änderungen 6.60 → 6.70 im EA unabhängig gelesen (Unterschied beider Dateien: genau die beabsichtigten
108 Zeilen, sonst nichts geändert).

- **Kompilierfehler: keine gefunden.** Format-Zeichenketten passen zu ihren Argumenten, keine neuen globalen Namen, keine
  Namenskollisionen, `DEAL_ENTRY_OUT_BY` und die Felder von `D[]` werden wie im übrigen Code benutzt.
- **Voreinstellungen (1,0 und 0): kein Unterschied zu 6.60.** `RegimeKlein()` kehrt zurück, bevor es den Zwischenspeicher von
  `FadeRegimeLive` berührt; Sperre und Panel-Zeile werden gar nicht erst geprüft; Journal- und Push-Texte bleiben Zeichen für
  Zeichen wie in 6.60.
- **Als richtig bestätigt:** Zeitpunkt der Regime-Größe (RSI21 `sigZeit`, Noise `chkEnd`, beide auf M5 ausgerichtet), Faktor auf
  jedem Noise-Teil, Verkleinerung vor allen Obergrenzen (nie vergrößernd, keine Division durch 0), der virtuelle Fade-Trade wird
  vor der Sperre verbucht (der Wächter sieht die Sperre nicht), Prop-Tag-Grenze 17:00 NY (Fades sind um 16:40 NY aus dem Markt).

| Befund | Gewicht | Umsetzung in 6.70 |
|---|---|---|
| `FadeVerlusteHeute` zählte verlustreiche **Ausstiegs-Deals** statt Positionen: Abschluss-Ernte mit Gewinn und Rest am Stop = ein Verlust, obwohl die Position im Plus lag; ein Stop in zwei Teil-Ausführungen zählte doppelt | beheben | Zählung **je Position**: nur das letzte Schließen einer voll geschlossenen Position (Deals derselben Sekunde zusammen, Ergebnis + Swap) – genau die Regel des Replikats (`losses[k]`), damit dessen Zahlen gelten. Der Vorschlag des Gegenlesens (Summe aller Ausstiege) wäre vom Replikat abgewichen. Prüfung 10 in `t_port_670.py` |
| Die Regime-Größe kann **dauerhaft** klein bleiben (Fade-Module nicht angelegt), ohne Warnung | beheben (gering) | Warnung beim Start (Abschnitt 8); bei `FadeWaechterModus=0` ein Hinweis, dass die Option dem Portfolio-PF folgt |
| Das Panel schrieb in den Ein-Platz-Zwischenspeicher von `FadeRegimeLive`; ein späteres Signal derselben M5-Kerze hätte selten einen veralteten Wert lesen können | Kleinigkeit | Panel rechnet den PF direkt, ohne Zwischenspeicher – der Speicher verhält sich wieder genau wie in 6.60 |
| Die neue Panel-Zeile stand vor den GFT-Schutz-Zeilen und schob sie über die Grenze des Chart-Kommentars (~2045 Zeichen) | Kleinigkeit | Zeile nur bei aktiver Option, ganz unten |
| Eingabe-Kommentar von `RegimeGroesse` 396 Zeichen (bisher höchstens 323) | Kleinigkeit | gekürzt auf 261 (`FadeTagessperre` 188) |
| `RegimeGroesse > 1.0` hätte im Optimierer Werte wie 1,0000000000000002 abgelehnt | Kleinigkeit | Prüfung mit Toleranz (> 1 + 10⁻⁹) |
| Überschrift `// 6.40: Auszahlungstakt (Panel)` war verrutscht | Kleinigkeit | wiederhergestellt |

Bewusst **nicht** geändert:

- `D[]` (Deal-Historie) wird mit `GueltigSchutz` (Voreinstellung) sofort nach jeder Positionsänderung neu geladen, ohne ihn
  spätestens nach 5 s. Ohne Schutz gültiger Tage könnte die Sperre einen Fade-Verlust übersehen, der in den letzten 5 Sekunden
  vor dem nächsten Fade-Einstieg im selben Symbol geschlossen wurde – selten, und nur mit ausgeschaltetem Schutz. Der Kommentar
  im Code sagt das jetzt so.
- Der Zwischenspeicher von `FadeRegimeLive` wird nicht geleert, wenn in derselben M5-Kerze neue virtuelle Fade-Ergebnisse
  eintreffen. Das gab es schon in 6.60 (RSI21-Schutz), ist sehr selten und bleibt, damit der geprüfte 6.60-Handel unverändert
  bleibt.
- Push-Längen (höchstens 198 Zeichen) und Rechenzeit (`FadeVerlusteHeute` liest nur die Deals des Tages) sind unkritisch.

Nach den Änderungen: `t_mq5.py` bestanden, `t_port_670.py` alle 10 Prüfungen identisch, `t_set.py` für alle vier Presets
bestanden.

## 10. Echtbetrieb

1. `DEADBAND_LIVE4.mq5` in MetaEditor kompilieren. Erwartet: 0 Fehler.
2. **Max. Balken im Chart = Unbegrenzt** (wie seit 6.20).
3. Echtbetrieb-Set laden (oder den EA ohne Set: die Voreinstellungen sind das Echtbetrieb-Set). Im Journal:
   `6.70 Regime | Handel wie 6.60 (Voreinstellungen)`. Alles Weitere wie 6.60 (Bericht 6.60, Abschnitt 10).
4. **Optionen prüfen, bevor man sie nutzt** – im Strategietester („Jeder Tick anhand realer Ticks“, XAUUSD.x M15, Zeitraum
   2024-01 bis 2026-09, Einzahlung 10 000 $):
   - drei Läufe mit Echtbetrieb-, Regimeschutz- und Tagessperre-Set;
   - vergleichen: Zahl der Auszahlungsreifen (Journal `JETZT AUSZAHLUNG BEANTRAGEN`), Netto, längste Verlustserie. Der
     MT5-Bericht zählt Positionen; die drei Noise-Teile eines Signals zählen dort einzeln (Abschnitt 3.4);
   - Regimeschutz sollte sich im Tester kaum unterscheiden (die Fades waren 2024–26 live). Unterschiede zeigen sich nur, wenn der
     Journal-Eintrag `Regime-Groesse x0.50` bei RSI21/Noise auftaucht.
5. Auf die Push-Meldung `FADE-REGIME AUS` hin kann man jederzeit auf das Regimeschutz-Set wechseln (EA neu laden; der Zustand wird
   aus der Historie rekonstruiert).

## 11. Grenzen und Hinweise

1. **Kein GFT-Datentest.** Alle Konto-Zahlen stammen vom GFT-Ersatz aus Fremddaten (wie seit 6.20). Wer die GFT-Exporte hat:
   Dateien nach `data/`, dann `python prep5.py && python sig5.py` und `python x70.py gft "6.60|Z9 Regime-Groesse 0.5|Z10 Z9 + Z2" 16 1`.
2. **Der Zukunftstest 2026 ist verbraucht** (seit 6.60) und kurz; hier hat er eine Entscheidung gegen Z2/Z10 mitbestimmt.
3. **Die Fades sind 2022–26 gesucht worden.** Verbesserungen, die an den Fades ansetzen (Z1–Z3, Z2), sind auf 2022–25 teilweise
   In-Sample. Deshalb zählen Signal-Ebene, Startjahre und 2026 hier so viel.
4. **Regimeschutz ist eine Wette auf das eigene Risikoprofil:** Sie senkt das Bust-Risiko nach einem Regimewechsel stark, kostet
   dann aber Ertrag. Im Mittel (Netto inklusive Neukäufe) ist 6.60 auch im alten Regime vorn.
5. **Serien im MT5-Bericht** sind länger als hier angegeben (Abschnitt 3.4). Der Serien-Stopp des EA zählt wie dieser Bericht
   (ein Noise-Signal = ein Trade).
6. **Viele Versuche:** 28 Konto-Varianten, 4 Studien. Übernommen wurde keine neue Handelsregel als Voreinstellung.
7. **Nicht kompiliert, nicht im Tester** (Abschnitt 9).
8. **Panel-Länge:** Nach grober Schätzung des Gegenlesens ist das Panel schon in 6.60 länger als die rund 2045 Zeichen, die MT5
   im Chart-Kommentar zeigt – die letzten Zeilen (GFT-Schutz, Leiter) können abgeschnitten sein. Nicht nachgemessen, unverändert
   wie 6.60. Die 6.70-Zeile steht deshalb ganz unten und nur bei aktiver Option; fällt sie selbst weg, steht der Stand der
   Optionen auch im Journal (Startzeile, Vermerk `Regime-Groesse x0.50` je Einstieg, Auslass-Grund der Sperre) und in den
   Push-Meldungen.

## Anhang: Replikat

`Replikat_v6/README.md` (Abschnitt Build 6.70):

- Prüfprotokoll: `PROTOKOLL_670.md` (mit Nachtrag 1 und 2)
- Motor `eng11.py` (erzeugt aus `eng10.py` mit `mk_eng11.py`; Prüfung `t_eng11.py`), Bewertung `evl11.py`
- Screening und Endbewertung `x70.py` (Varianten in `VAR`; `ABSCHLAG=0.2` = Stresstest; GFT-nah in einer Ordnerkopie mit
  `SPREAD_FAKTOR=0.6`), Zukunftstest `x70f.py` (Ordnerkopie mit `mk_proxy2026.py` wie 6.60)
- Diagnosen: `a70_diag.py` (Serien nach Modul, knapp verfehlte Tage), `a70_verl.py` (verlorene gültige Tage), `a70_sig.py`
  (Z2 auf Signal-Ebene), `a70_bust.py` / `a70_bustmod.py` (Busts der Fremddaten)
- EA und Presets: `mk_ea670.py` (Änderungen am EA als Textersetzungen), `mk_sets670.py`, Prüfungen `t_port_670.py`, `t_set.py`,
  `t_mq5.py`
- Ergebnisse: `ergebnisse/x70_gft.json`, `x70_gft_spread06.json`, `x70_ext.json`, `x70_gft_abschlag20.json`,
  `x70_gft_abschlag20_spread06.json`, `x70r3_gft.json`, `x70r3_gft_spread06.json`, `x70f_2026.json`, `x70f_2026_spread06.json`,
  `a70_*.txt`, `t_port_670.txt`
