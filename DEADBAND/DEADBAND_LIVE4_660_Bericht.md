# DEADBAND LIVE 4 – Build 6.60 ZUKUNFT

Bericht vom 25.09.2026 · GFT Instant Premium 10k (Konto ab 02.09.2026)

## 1. Kurzfassung

**Auftrag:** Für 6.40 neue Wege suchen, den Gewinn zu verbessern: weniger Zeit zwischen den Auszahlungen und mehr Netto. Das
System soll auch in Zukunft funktionieren und nicht auf die Vergangenheit optimiert sein. Auf diesem Branch liegt schon 6.50
(Netto-Build vom selben Tag, baut auf 6.40 auf). 6.60 wird deshalb mit beiden verglichen.

**Vorgehen:** Die Prüfregeln wurden **vor** den Tests festgelegt und gepusht (`Replikat_v6/PROTOKOLL_660.md`). Dazu gehören
ein Walk-Forward (auswählen mit 2022–23, prüfen mit 2024–25), ein Stresstest und ein Sicherheitsvergleich. **Neu ist ein
Zukunftstest 2026**: NAS100 bis 28.08.2026 aus Dukascopy-Ticks, Gold bis 02.09.2026. Diese Daten hat keine Entscheidung seit
6.10 gesehen.

**Befund:**
- Keine der neuen Ideen hat die Prüfung bestanden (Abschnitt 4).
- Die Nachprüfung von 6.50 selbst ergab: Von dessen drei Bausteinen hält einer nicht, das **Fade-Risiko 0,70 %**. Es hätte
  schon die Auswahl mit 2022–23 nicht bestanden. Im Zukunftstest 2026 kostet es rund eine Auszahlung je Jahr (Abschnitt 5).

**Build 6.60** = Handelslogik 6.50 mit **Fade-Risiko 0,75 %** (wie 6.00–6.40), dazu **Regime-Meldungen**: Push-Meldungen,
wenn die Fades wegen nachlassender Kante nur noch virtuell laufen oder wieder live gehen, und eine Vorwarnung vorher. Die
Meldungen beeinflussen den Handel nicht.

Konto-Replikat mit allen GFT-Regeln, 16 Störungen, jeder Handelstag ein neues Konto. Zellen: breite / GFT-nahe Spreads.

| Kennzahl | 6.40 | 6.50 | **6.60** |
|---|---:|---:|---:|
| **Zukunftstest 2026** (Konten ab Januar, 100 Handelstage) | | | |
| Auszahlungen je Jahr (Tage je Auszahlung) | 12,35 (29,6) / 12,49 (29,2) | 11,20 (32,6) / 11,57 (31,6) | **12,54 (29,1) / 12,38 (29,5)** |
| Netto je Jahr (80 % Anteil, 3 % Gebühr, Neukäufe) | 2079 / 2169 $ | 1993 / 2188 $ | **2229 / 2319 $** |
| … mit 60-Tage-Konten (Starts bis Juni): Auszahlungen · Netto | 11,75 · 2032 / 11,80 · 2124 | 10,58 · 1941 / 10,75 · 2091 | **11,83 · 2169 / 11,80 · 2309** |
| Busts · kleinster Abstand zum Boden, Mittel | 0 · 337 / 334 $ | 0 · 312 / 319 $ | 0 · 325 / 319 $ |
| **GFT-Ersatz 2022–2025** (1/2/3-Jahres-Konten) | | | |
| Auszahlungen je Jahr (Tage je Auszahlung) | 11,25 (32,5) / 12,06 (30,3) | 11,66 (31,3) / 12,12 (30,1) | 11,53 (31,7) / 12,05 (30,3) |
| Netto je Jahr | 2051 / 2232 $ | 2319 / 2510 $ | 2244 / 2493 $ |
| Busts · kleinster Abstand zum Boden, Mittel | 0 · 255 / 248 $ | 0 · 262 / 261 $ | 0 · 255 / 251 $ |
| **Stress**: 20 % der Fade-Gewinner entfernt (2022–25) | | | |
| Auszahlungen · Netto | 6,08 · 1076 / 7,92 · 1394 | 5,97 · 1163 / 8,37 · 1649 | 6,29 · 1217 / 8,33 · 1654 |
| Busts · Konten < 100 $ am Boden | 0 · 3,2 / 0,0 % | 0 · 0,4 / 0,0 % | 0 · 3,2 / 0,0 % |
| **Fremddaten 2006–2021** (anderes Regime) | | | |
| Auszahlungen · Netto je Jahr | 2,16 · 364 $ | 2,14 · 361 $ | 2,15 · 363 $ |
| Busts je Jahr · Bust im 1. Jahr | 0,035 · 0,9 % | 0,034 · 0,6 % | 0,038 · 1,0 % |

- **Mehr Netto als 6.40, in jeder Prüfung.** 2022–25 +193 / +260 $ je Jahr, 2026 +151 / +149 $, unter Stress +141 /
  +260 $. Das gilt jeweils in 14–16 von 16 Störungen.
- **Takt:** Gegenüber 6.40 gleich, rund 29–32 Tage je Auszahlung. Gegenüber 6.50 im Zukunftstest 2026 rund 2–3 Tage
  kürzer (breit 29,1 statt 32,6, GFT-nah 29,5 statt 31,6 Tage; +1,35 bzw. +0,81 Auszahlungen je Jahr). Eine Verkürzung
  unter rund 29 Tage, die die Sicherheit nicht schwächt, hat sich nicht gefunden (Abschnitt 3: Engpass sind die gültigen
  Tage).
- **Gegenüber 6.50 ist das Bild gemischt:**
  - 2022–25 liegt 6.60 etwas zurück: breit −0,13 Auszahlungen und −75 $, GFT-nah gleich.
  - 2026 liegt es klar vorn: +0,8 bis +1,35 Auszahlungen und +131 bis +236 $.
  - Im schlechtesten Einzeljahr verliert 6.60 gegen 6.50 höchstens 0,34 Auszahlungen und 88 $. 6.50 verliert gegen 6.60
    bis zu 1,34 Auszahlungen und 236 $ (Abschnitt 5.2).
  - Dafür hat 6.60 den etwas kleineren Sicherheitsabstand von 6.40: Im Mittel 6–10 $ näher am Boden. Im alten Regime
    +0,004 Busts je Jahr. Unter Stress (breit) kommen 3,2 statt 0,4 % der Konten dem Boden auf unter 100 $ nahe.
- **Protokoll:** Gegen 6.40 besteht 6.60 alle vorab festgelegten Kriterien. Gegen 6.50, das im Protokoll als Basis stand,
  besteht es die Kriterien auf 2022–25 nicht (Ziel, Walk-Forward, paarweiser Vergleich) und zwei Sicherheitskriterien
  knapp nicht. Warum ich 6.60 trotzdem empfehle, steht in Abschnitt 6.7. Wer den größeren Abstand von 6.50 will, setzt
  `FadeRiskPct=0.70`.
- **Zukunftsfest heißt hier:** Kein Handelsparameter wurde auf das beste Ergebnis gesetzt. 0,75 % ist der Wert von
  6.00–6.40.
  Die Regime-Meldungen machen sichtbar, wenn die Kante der Fades nachlässt. Der Portfolio-Wächter schaltet dann
  automatisch ab, wie seit 6.40.
- **Nicht geprüft:** Kompilieren in MetaEditor, Strategietester, Demo. Das bleibt Pflicht (Abschnitt 10).

## 2. Vorgehen

### 2.1 Prüfprotokoll (vorab)

`Replikat_v6/PROTOKOLL_660.md` wurde vor den Konto-Tests der Kandidaten K2 und K3 festgelegt, committet und gepusht
(Commit `8d009f3`). Eine Änderung wird nur übernommen, wenn alle Kriterien gelten:

| | Kriterium |
|---|---|
| K-a | Screening (8 Störungen, jeder 2. Handelstag), beide Spread-Lagen: Auszahlungen ≥ Basis − 0,1 und Netto ≥ Basis + 3 %, oder Auszahlungen ≥ Basis + 0,3 und Netto ≥ Basis − 1 % |
| K-b | Walk-Forward: ausgewählt wird mit den Konten, die 2022–23 starten. Die Konten mit Start 2024–25 dürfen nicht schlechter sein |
| K-c | Sicherheit: 0 Busts; Abstand zum Boden ≥ Basis − 10 $; Konten < 100 $ höchstens + 0,5 Prozentpunkte; Fremddaten: Busts je Jahr ≤ Basis + 0,005, Bust im 1. Jahr ≤ + 0,5 Prozentpunkte |
| K-d | Paarweise über 16 Störungen: Hauptziel in ≥ 12 von 16 besser, beide Spread-Lagen |
| K-e | Plateau: Nachbarwerte eines Parameters bestehen K-a ebenfalls |
| K-f | Höchstens zwei neue Eingaben; Werte aus Regelmechanik oder Literatur, nicht aus dem besten Ergebnis |
| K-g | Stress: 20 % der Fade-Gewinner entfernt (auch für den Wächter) – Sicherheit nicht schlechter als die Basis unter demselben Abschlag |

### 2.2 Daten

- **GFT-Ersatz 2022–2025** wie bei 6.40/6.50 (Fremddaten-Quellen, auf GFT-Zeit und -Kosten gebracht): einmal mit breiten,
  einmal mit GFT-nahen Spreads (× 0,6).
- **Fremddaten 2006–2021:** anderes Marktregime, in dem die Fades überwiegend verloren (Abschnitt 7). Dort zählt vor allem,
  dass die Konten überleben.
- **Zukunftstest 2026 (neu):**
  - NAS100 ab 02.01.2025 aus Dukascopy-Ticks (127 Mio. Ticks bis 28.08.2026), Gold aus den Fremddaten bis 02.09.2026. Die
    Kosten folgen derselben Regel wie im übrigen Ersatz (`mk_proxy2026.py`).
  - Konten starten ab 02.01.2026, jeder Handelstag ein neues Konto: 100 Handelstage (73 Starttage × 16 Störungen) und
    60 Handelstage (113 Starttage). Zusätzlich ein durchgehendes Konto ab 02.01.2025.
  - Signale, Wächter und Grid-Historie laufen vorher durch. Der Wächter-Zustand am Jahresanfang ist also echt.
  - Einschränkung: Die Dukascopy-Reihe ist verrauschter als die Broker-Daten. Im gemeinsamen Jahr 2025 liegt die Korrelation
    der M5-Renditen bei 0,935, in der NY-Kassazeit bei 0,979 (Datenbericht, Abschnitt 10). Für den Vergleich von Varianten
    auf denselben Daten taugt sie. Absolute Zahlen für 2026 sind unsicherer.
- **US500** 2020–2025 (MT5-Broker-Export, gleicher Broker wie US100) für Kandidat K2.

### 2.3 Replikat und Zählung

- Motor `eng10` (= `eng9` plus Größe für den gültigen Tag, Noise short, zusätzliche Signalströme). Mit Voreinstellungen ist
  er identisch mit `eng9` (`t_eng10.py`: 45 Konten, alle Zähler und Trades gleich).
- Bewertung `evl10` (rollierende 1/2/3-Jahres-Konten, 16 Störungen: ausgelassene Signale, Schlupf).
- Geprüft wurden **25 Konto-Varianten** und **5 Studien auf Signal-Ebene**. Bei so vielen Versuchen findet man leicht eine,
  die zufällig gut aussieht. Deshalb gelten die Kriterien oben, und deshalb der Zukunftstest.

## 3. Diagnose: Was die Zeit zwischen den Auszahlungen bestimmt

Eine Auszahlung braucht 5 gültige Tage (≥ 0,5 % realisiert), 10 Tage und mindestens 131,25 $ Gewinn. Welche Bedingung als
letzte erfüllt ist (6.50, 2022–25, breit / GFT-nah):

| | 5 gültige Tage | Mindestgewinn | 10 Tage |
|---|---:|---:|---:|
| zuletzt erfüllt (Anteil der Zyklen) | 72 / 72 % | 21 / 20 % | 7 / 7 % |

- **Engpass sind die gültigen Tage.** Rund 64–66 gültige Tage je Jahr, bis zum fünften vergehen im Mittel 23–24 Tage.
  Rund 60 Handelstage im Jahr bleiben ohne Trade.
- **Ein gültiger Tag ist meist genau ein Treffer:** 90,5 % der gültigen Tage realisieren 50–106 $. Der größte Einzelgewinn
  liegt an diesen Tagen im Median bei 51 $. Nur 9,5 % der gültigen Tage bringen mehr als 106 $, also genug für zwei.
  Gewinne auf zwei Tage zu verteilen, lohnt deshalb nicht.
- **Die Schwelle ist fest (50,50 $), die Größe variabel.** Ein einzelner Fade-Treffer macht den Tag mit Kosten bei 0,75 %
  Risiko ab rund 0,71 R Zielweite gültig, bei 0,70 % erst ab 0,76 R. 4,4 % aller Fade-Signale 2022–25 haben ihr Ziel genau
  in diesem Band, vor allem X0630, N1300, N1800 und X0400. Das sind bei voller Größe rund 9 Treffer je Jahr. Dazu kommen Tage
  aus mehreren kleinen Gewinnen knapp an der Schwelle.
- **Warum 2024–25 schwächer war** (6.50; Auszahlungen, gültige Tage und Verlusttage je Jahr aus den 1-Jahres-Konten mit
  Start im Jahr, die übrigen Spalten aus den Trades im Kalenderjahr):

| Jahr | Auszahlungen | gültige Tage | Verlusttage | Trades mit voller Größe | Fades: R je Trade virtuell → im Konto |
|---|---:|---:|---:|---:|---|
| 2022 | 12,35 | 68,9 | 55,3 | 41,8 % | +0,178 → +0,175 |
| 2023 | 13,24 | 71,2 | 57,6 | 62,6 % | +0,205 → +0,181 |
| 2024 | 9,10 | 52,5 | 75,3 | 52,7 % | +0,171 → +0,177 |
| 2025 | 8,20 | 47,7 | 74,9 | 25,9 % | +0,085 → +0,072 |

  - Die Kante war 2025 kleiner. X0630, X0400 und X1000S verloren (−258 / −153 / −116 $ je Konto-Jahr), Noise verdiente
    51 statt 787 $ (2023).
  - Die Pufferkurve verkleinerte danach die meisten Trades.
  - Die Umsetzung verliert kaum etwas: R je Trade im Konto ≈ R desselben virtuellen Signals (`a60_drag.py`).
  - Die vom Konto ausgelassenen Signale (Schutz, eine Position je Modul, Serien-Stopp) waren nicht systematisch schlechter
    als die gehandelten: 2022 und 2025 besser, 2023 und 2024 schlechter (`a60_stufen2.py`). Ein zusätzlicher Filter hat
    also nichts zu holen.
- **Die Pufferkurve kostet rund 1,1 Auszahlungen je Jahr** (ohne sie 12,97 statt 11,84). Ohne sie kommen aber 26 % der
  Konten dem Boden auf unter 100 $ nahe, und es gibt Busts. Sie bleibt (Abschnitt 4.6).

**Folgerung:** Kürzere Zyklen gehen nur über mehr gültige Tage. Die gibt es nur mit größeren Positionen (weniger Abstand zum
Boden) oder mit zusätzlichen Signalen mit echter Kante. Beides wurde geprüft.

## 4. Geprüfte Ideen

### 4.1 Konto-Screening (8 Störungen, jeder 2. Handelstag, breite Spreads; Basis 6.50)

Spalten 2022–23 und 2024–25: Konten nach Startjahr (Walk-Forward).

| Idee | Variante | Auszahlungen | Netto | Abstand Ø | < 200 $ | 2022–23 | 2024–25 | Urteil |
|---|---|---:|---:|---:|---:|---|---|---|
| Basis | 6.50 Ertrag | 11,84 | 2371 $ | 262 $ | 0,0 % | 12,85 · 2716 $ | 9,07 · 1553 $ | |
| K1 Größe für den gültigen Tag | Deckel 0,80 % | 11,80 | 2384 $ | 264 $ | 0,2 % | 12,96 · 2740 $ | 8,95 · 1576 $ | K-a nein |
| | Deckel 0,85 % | 11,96 | 2377 $ | 263 $ | 0,1 % | 13,16 · 2735 $ | 9,11 · 1585 $ | K-a nein |
| | Deckel 0,90 % | 11,97 | 2354 $ | 264 $ | 0,0 % | 13,15 · 2701 $ | 9,02 · 1570 $ | K-a nein |
| | 0,85 % immer | 11,83 | 2288 $ | 245 $ | 2,0 % | 12,97 · 2631 $ | 8,93 · 1538 $ | nein |
| K6 Noise auch short | Risiko 0,30 % | 11,65 | 2179 $ | 266 $ | 0,0 % | 12,27 · 2387 $ | 9,82 · 1665 $ | K-a, K-b nein |
| | 0,45 % | 11,74 | 2150 $ | 256 $ | 0,0 % | 12,45 · 2363 $ | 10,06 · 1688 $ | nein |
| | 0,60 % | 11,40 | 2051 $ | 244 $ | 5,1 % | 12,35 · 2279 $ | 9,23 · 1561 $ | nein |
| K7 N1330/N1300 kleiner | Risiko 0,35 % | 11,38 | 2242 $ | 264 $ | 0,0 % | 12,56 · 2611 $ | 8,55 · 1434 $ | nein |
| | 0,50 % | 11,57 | 2317 $ | 265 $ | 0,0 % | 12,65 · 2676 $ | 8,86 · 1503 $ | nein |
| | ohne N1330/N1300 | 11,02 | 2109 $ | 260 $ | 0,0 % | 12,30 · 2445 $ | 8,03 · 1338 $ | nein |
| K9 DEADBAND wieder an | volle Größe | 9,80 | 1666 $ | 199 $ | 55,6 % | 9,36 · 1630 $ | 10,54 · 1734 $ | nein |
| | halbe Größe | 9,21 | 1659 $ | 233 $ | 20,6 % | 9,62 · 1797 $ | 8,28 · 1404 $ | nein |
| Regel-Lesart | Boden nur zum Tagesschluss | 11,99 | 2373 $ | 272 $ | 1,0 % | 12,92 · 2699 $ | 9,36 · 1579 $ | K-a nein |
| Pufferkurve | aus | 12,97 | 2542 $ | 176 $ | 56,8 % | 13,71 · 2850 $ | 10,79 · 1814 $ | K-c nein (26 % < 100 $, Busts) |
| | wie 6.30 (4 / 1,5 / 0,6) | 12,73 | 2506 $ | 174 $ | 68,7 % | 13,52 · 2814 $ | 10,52 · 1794 $ | K-c nein (14 % < 100 $) |
| | 5 / 2,5 / 0,4 | 11,98 | 2387 $ | 235 $ | 20,7 % | 12,89 · 2732 $ | 9,56 · 1599 $ | K-a, K-c nein |
| | 5 / 3 / 0,3 | 11,76 | 2360 $ | 272 $ | 0,6 % | 12,79 · 2705 $ | 8,91 · 1540 $ | nein |
| | 6 / 2,5 / 0,2 | 10,39 | 2078 $ | 284 $ | 0,0 % | 11,72 · 2442 $ | 7,52 · 1326 $ | nein |

K1 auch auf 6.60 (Basis 0,75 %) geprüft:

| | breit | GFT-nah |
|---|---|---|
| 6.60 ohne K1 | 11,66 · 2282 $ · < 200 $ 0,4 % | 12,04 · 2503 $ · 1,2 % |
| Deckel 0,80 % | 11,65 · 2283 $ · 0,4 % | 12,06 · 2482 $ · 3,8 % |
| Deckel 0,85 % | 11,85 · 2296 $ · 0,7 % | 12,14 · 2445 $ · 4,4 % |

- **K1 Größe für den gültigen Tag:** Der Fade-Trade wird so groß, dass sein Ziel den Tag allein gültig macht, bis zu einem
  Deckel. Das bringt höchstens +0,2 Auszahlungen, das Netto bleibt gleich oder sinkt. Mehr Konten kommen dem Boden nahe, und
  das Risiko rückt näher an die harte Grenze von −1 %. Verworfen.
- **K6 Noise short:**
  - Auf Signal-Ebene hat die Short-Seite nur eine schwache Kante: PF 1,10 (2022–23) und 1,17 (2024–25). Die Long-Seite hat
    2,05 und 1,46.
  - Die Short-Seite hängt negativ mit den NAS-Fades zusammen (Korrelation der Tagesergebnisse −0,24).
  - 2024–25 bringt sie +0,75 Auszahlungen. In der Auswahlperiode 2022–23 kostet sie aber 0,6 Auszahlungen und 330 $.
    Verworfen. Diese Idee lohnt es, im Blick zu behalten.
- **K7:** N1330/N1300 treffen ihr Ziel bei 0,3–0,5 R und machen nie allein einen Tag gültig. Ein Verlust kann aber einen
  Tag kippen. Mit kleinerem Risiko verdienen sie trotzdem weniger, als sie schützen.
- **K9 DEADBAND:** Verlustserien ≥ 6 steigen auf 4,7 je Jahr, die Trefferquote liegt bei 53 %. Verworfen.
- **Boden nur zum Tagesschluss:** Ein GFT-Artikel nennt für Instant Premium einen „6% Trailing End-of-Day Maximum
  Drawdown“. Dann zöge der Boden nur das Tagesschluss-Hoch nach. Das brächte +0,15 Auszahlungen. Der EA rechnet weiter
  streng mit dem Intraday-Hoch. Ist die Lesart falsch, wäre das Konto weg.

### 4.2 Signal-Ebene (ohne Konto-Test verworfen)

**K2: NAS-Fades unverändert auf US500** (gleiche Uhrzeiten, Puffer und Ziele; Kosten relativ wie NAS). Summe der sechs
NAS-Module, je Jahr:

| | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| US500 | +3,7 R · PF 1,06 | −1,8 R · 0,97 | +6,9 R · 1,09 | +12,7 R · 1,21 | +5,3 R · 1,10 | −6,7 R · 0,90 |
| NAS100 | −6,8 R · 0,89 | −19,7 R · 0,72 | +46,6 R · 1,81 | +28,8 R · 1,53 | +28,4 R · 1,59 | +30,1 R · 1,59 |

- Die Kante ist NAS-spezifisch. US500 liegt 2022–25 nahe PF 1.
- An gemeinsamen Signaltagen korrelieren die Ergebnisse mit 0,59. US500 würde also vor allem das NAS-Risiko verdoppeln.
- Die 113 Tage, an denen nur US500 ein Signal hatte, brachten −10,8 R.

**K3: Schocktag-Filter.** Getestet wurden drei Größen: Vortags-Spanne / ATR14, Tagesbewegung bis zum Signal / ATR14 und
ATR14 / ATR100, je Symbol und Periode. Die Vorgabe verlangte denselben Zusammenhang in 2006–13, 2014–21 und 2022–25 auf beiden
Symbolen. Das hält keine Größe. Beispiel NAS, Tagesbewegung bis zum Signal ≥ 0,75 ATR: PF 0,84 / 1,18 / 4,85 / 0,50 in den
vier Perioden. Verworfen.

**K4: Handeln, während GFT die Auszahlung bearbeitet.** Ohne Test verworfen. GFT verlangt „no open trades“ für die
Auszahlung. Ob Handel bis zur Buchung erlaubt ist, ist nicht belegt.

**K5: Trendfilter und gespiegelte Fades** (Summe der 10 Module, R je Jahr):

| | 2006–13 | 2014–21 | 2022–23 | 2024–25 |
|---|---:|---:|---:|---:|
| wie im EA | −6,8 | −26,5 | **+56,0** | **+48,5** |
| nur mit Trend (SMA50) | +1,9 | −11,5 | +26,0 | +32,3 |
| gespiegelt | −14,2 | −33,8 | −13,7 | −28,3 |
| beide Richtungen, mit Trend | −2,7 | −19,4 | +25,6 | +19,1 |

Der Trendfilter halbiert die Kante 2022–25. Im alten Regime macht er die Verluste kleiner, aber dort schaltet ohnehin der
Wächter ab. Gespiegelte Fades verlieren überall. Verworfen.

**Gold-Noise** (Noise-Area-Momentum auf XAUUSD): Long PF 1,21 / 0,83 / 0,94 / 1,26, Short PF 0,99 / 0,74 / 1,06 / 0,83 in
den vier Perioden. Keine stabile Kante. Verworfen.

## 5. Walk-Forward: 6.50 nachgeprüft

### 5.1 Die drei Bausteine von 6.50, einzeln auf 6.40

Zellen: Auszahlungen · Netto. 2022–23 und 2024–25 aus dem Screening (8 Störungen), 2026 aus dem Zukunftstest (100 Tage,
16 Störungen). „–“ = nicht gerechnet.

| Variante | 2022–23 breit | … GFT-nah | 2024–25 breit | … GFT-nah | 2026 breit | … GFT-nah |
|---|---|---|---|---|---|---|
| 6.40 | 12,33 · 2361 $ | 13,50 · 2628 $ | 8,47 · 1344 $ | 8,88 · 1457 $ | 12,35 · 2079 $ | 12,49 · 2169 $ |
| + Fade-Risiko 0,70 % | 12,21 · 2379 $ | 13,21 · 2586 $ | 8,95 · 1480 $ | 9,00 · 1518 $ | **11,20 · 1879 $** | – |
| + RSI21 ab 13:00 NY im Fade-Regime | 12,86 · 2539 $ | 13,57 · 2781 $ | 8,44 · 1367 $ | 8,89 · 1468 $ | 12,64 · 2151 $ | – |
| + N1330/N1300 an gültigen Tagen frei | 12,33 · 2472 $ | 13,23 · 2681 $ | 8,88 · 1476 $ | 8,94 · 1538 $ | 12,39 · 2195 $ | 12,26 · 2266 $ |
| 6.50 (alle drei) | 12,85 · 2716 $ | 13,21 · 2903 $ | 9,07 · 1553 $ | 9,12 · 1587 $ | 11,20 · 1993 $ | 11,57 · 2188 $ |
| **6.60** (6.50 ohne 0,70 %) | 12,84 · 2661 $ | 13,43 · 2918 $ | 8,82 · 1478 $ | 8,92 · 1571 $ | **12,54 · 2229 $** | **12,38 · 2319 $** |

- **Fade-Risiko 0,70 %:**
  - In der Auswahlperiode 2022–23 fällt K-a durch (breit −0,12 Auszahlungen, +1 % Netto; GFT-nah −0,29, −2 %). Nach dem
    Protokoll wäre 0,70 % also nie gewählt worden.
  - 2024–25 ist es besser.
  - 2026 kostet es 1,14 Auszahlungen und 199 $ (breit, paarweise: 1 von 16 Störungen besser).
- **RSI21 ab 13:00 NY im Fade-Regime:** Besteht die Auswahl (+0,53 / +0,07 Auszahlungen, +7,5 / +5,8 % Netto). 2024–25
  gleich, 2026 +0,29 Auszahlungen und +72 $ (13 bzw. 14 von 16). **Bleibt.**
- **N1330/N1300 frei:**
  - Netto ist in jeder Periode und beiden Lagen höher: +4,7 / +2,0 % (2022–23), +132 / +81 $ (2024–25), +117 / +97 $
    (2026, 14 bzw. 12 von 16).
  - Die Auszahlungen schwanken um null: GFT-nah 2022–23 −0,27, 2026 −0,23. **Bleibt** (mehr Netto, gleicher Takt).

### 5.2 0,75 gegen 0,70 % je Zeitraum

Differenz 6.60 − 6.50 (16 Störungen, jeder Handelstag; 2022–25 Konten nach Startjahr):

| | Start 2022 | Start 2023 | Start 2024 | Start 2025 ⁽*⁾ | 2026 |
|---|---:|---:|---:|---:|---:|
| Auszahlungen, breit | +0,11 | −0,16 | −0,21 | +0,40 | **+1,34** |
| … GFT-nah | +0,31 | −0,02 | −0,34 | −0,13 | **+0,81** |
| Netto, breit | −33 $ | −88 $ | −68 $ | +141 $ | **+236 $** |
| … GFT-nah | +47 $ | −32 $ | −43 $ | −2 $ | **+131 $** |

⁽*⁾ nur 128 Konten (Starts Anfang Januar 2025).

- 0,75 % lag 2022, 2025 (breit) und vor allem 2026 vorn, 0,70 % leicht in 2023 und 2024.
- Plausibel sind zwei Effekte, die gegeneinander wirken:
  - Mit größeren Positionen werden mehr Tage gültig.
  - Mit kleineren fallen die Konten nach Verlusten seltener unter den Startsaldo, wo die Pufferkurve verkleinert.
  - Welcher Effekt überwiegt, hängt von der Phase ab.
- Welche Phase kommt, weiß niemand. Das schlechteste Jahr kostet mit 0,75 % höchstens 0,34 Auszahlungen und 88 $, mit
  0,70 % bis zu 1,34 Auszahlungen und 236 $.
- Dazu kommt die Mechanik (Abschnitt 3): Die Schwelle des gültigen Tags ist fest. Mit 0,75 % reicht ein einzelner Treffer
  ab 0,71 R Zielweite, mit 0,70 % erst ab 0,76 R.

## 6. Endbewertung (16 Störungen, jeder Handelstag)

### 6.1 GFT-Ersatz 2022–2025

| Variante | Auszahlungen (Tage) | Netto | Ø Auszahlung | Busts | Abstand Ø | < 200 $ | Serien ≥ 6 | Treffer |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 6.40, breit | 11,25 (32,5) | 2051 $ | 235 $ | 0 | 255 $ | 0,1 % | 0,83 | 65,6 % |
| 6.50, breit | 11,66 (31,3) | 2319 $ | 256 $ | 0 | 262 $ | 0,0 % | 0,92 | 66,6 % |
| 6.60a (6.40 + N1330/N1300 frei), breit | 11,35 (32,2) | 2160 $ | 245 $ | 0 | 253 $ | 0,2 % | 0,87 | 66,2 % |
| **6.60, breit** | **11,53 (31,7)** | **2244 $** | 251 $ | 0 | 255 $ | 0,2 % | 0,84 | 66,2 % |
| 6.40, GFT-nah | 12,06 (30,3) | 2232 $ | 239 $ | 0 | 248 $ | 4,1 % | 0,77 | 66,1 % |
| 6.50, GFT-nah | 12,12 (30,1) | 2510 $ | 267 $ | 0 | 261 $ | 5,9 % | 0,67 | 66,9 % |
| 6.60a, GFT-nah | 11,90 (30,7) | 2327 $ | 252 $ | 0 | 249 $ | 3,3 % | 0,81 | 66,6 % |
| **6.60, GFT-nah** | **12,05 (30,3)** | **2493 $** | 266 $ | 0 | 251 $ | 1,8 % | 0,86 | 66,8 % |

Längste Verlustserie in allen Varianten höchstens 10–11. Streuung über die 16 Störungen (SD): Auszahlungen 0,5–0,8,
Netto 145–210 $.

### 6.2 Paarweise je Störung (6.60 minus Vergleich; Mittel ± Standardfehler, besser in … von 16)

| | Auszahlungen | Netto |
|---|---|---|
| gegen 6.40, 2022–25 breit | +0,28 ± 0,15 (10) | **+193 ± 32 $ (16)** |
| gegen 6.40, 2022–25 GFT-nah | ±0,00 ± 0,10 (8) | **+260 ± 25 $ (16)** |
| gegen 6.40, 2026 breit (100 / 60 Tage) | +0,19 ± 0,16 (8) / +0,08 ± 0,07 (10) | **+151 ± 29 $ (16) / +137 ± 18 $ (15)** |
| gegen 6.40, 2026 GFT-nah (100 / 60 Tage) | −0,11 ± 0,22 (10) / ±0,00 ± 0,11 (10) | **+149 ± 38 $ (14) / +185 ± 18 $ (16)** |
| gegen 6.50, 2022–25 breit | −0,13 ± 0,09 (7) | −75 ± 21 $ (3) |
| gegen 6.50, 2022–25 GFT-nah | −0,07 ± 0,08 (9) | −17 ± 25 $ (7) |
| gegen 6.50, 2026 breit (100 / 60 Tage) | **+1,35 ± 0,24 (16) / +1,25 ± 0,17 (15)** | **+236 ± 38 $ (16) / +228 ± 31 $ (16)** |
| gegen 6.50, 2026 GFT-nah (100 / 60 Tage) | **+0,81 ± 0,26 (13) / +1,05 ± 0,15 (16)** | **+131 ± 51 $ (13) / +218 ± 31 $ (16)** |

### 6.3 Nach Startjahr (1-Jahres-Konten)

Zellen: Auszahlungen (Tage je Auszahlung) · Netto. Busts überall 0.

| Variante | Start 2022 | Start 2023 | Start 2024 | Start 2025 ⁽*⁾ |
|---|---|---|---|---|
| 6.40, breit | 12,14 (30,1) · 2368 $ | 12,45 (29,3) · 2360 $ | 8,83 (41,4) · 1405 $ | 8,73 (41,8) · 1335 $ |
| 6.50, breit | 12,20 (29,9) · 2602 $ | 12,92 (28,3) · 2709 $ | 9,28 (39,4) · 1584 $ | 8,15 (44,8) · 1249 $ |
| **6.60, breit** | 12,31 (29,7) · 2569 $ | 12,76 (28,6) · 2621 $ | 9,07 (40,3) · 1516 $ | 8,55 (42,7) · 1390 $ |
| 6.40, GFT-nah | 13,02 (28,1) · 2585 $ | 13,87 (26,3) · 2650 $ | 8,78 (41,6) · 1439 $ | 9,79 (37,3) · 1709 $ |
| 6.50, GFT-nah | 12,59 (29,0) · 2651 $ | 13,84 (26,4) · 3097 $ | 9,29 (39,3) · 1622 $ | 9,63 (37,9) · 1664 $ |
| **6.60, GFT-nah** | 12,90 (28,3) · 2698 $ | 13,82 (26,4) · 3065 $ | 8,95 (40,8) · 1579 $ | 9,50 (38,4) · 1662 $ |

⁽*⁾ nur 128 Konten (Starts Anfang Januar 2025).

### 6.4 Zukunftstest 2026

| Variante | 100 Tage: Auszahlungen (Tage) · Netto | Abstand Ø · < 200 $ | 60 Tage: Auszahlungen (Tage) · Netto | Abstand Ø · < 200 $ |
|---|---|---|---|---|
| 6.40, breit | 12,35 (29,6) · 2079 $ | 337 $ · 3,0 % | 11,75 (31,1) · 2032 $ | 366 $ · 1,0 % |
| 6.50, breit | 11,20 (32,6) · 1993 $ | 312 $ · 13,2 % | 10,58 (34,5) · 1941 $ | 354 $ · 4,3 % |
| **6.60, breit** | **12,54 (29,1) · 2229 $** | 325 $ · 4,1 % | **11,83 (30,9) · 2169 $** | 358 $ · 1,3 % |
| 6.40, GFT-nah | 12,49 (29,2) · 2169 $ | 334 $ · 6,0 % | 11,80 (30,9) · 2124 $ | 367 $ · 1,7 % |
| 6.50, GFT-nah | 11,57 (31,6) · 2188 $ | 319 $ · 9,9 % | 10,75 (34,0) · 2091 $ | 358 $ · 3,7 % |
| **6.60, GFT-nah** | **12,38 (29,5) · 2319 $** | 319 $ · 7,0 % | **11,80 (31,0) · 2309 $** | 357 $ · 2,9 % |

Busts in allen Zellen 0. Im Zukunftstest liegt 6.60 beim Abstand zum Boden nicht hinter 6.50. Weniger Konten kommen dem
Boden auf unter 200 $ nahe (breit 4,1 statt 13,2 %).

Durchgehendes Konto ab 02.01.2025, je Kalenderjahr (Auszahlungen · Netto; 2026 nur Januar–August):

| | 6.40 breit | 6.50 breit | 6.60 breit | 6.40 GFT-nah | 6.50 GFT-nah | 6.60 GFT-nah |
|---|---|---|---|---|---|---|
| 2025 | 8,4 · 1441 $ | 8,8 · 1437 $ | 8,6 · 1518 $ | 9,2 · 1634 $ | 10,2 · 1848 $ | 9,4 · 1720 $ |
| 2026 | 8,4 · 1333 $ | 7,6 · 1317 $ | 8,6 · 1455 $ | 8,4 · 1449 $ | 8,6 · 1579 $ | 8,6 · 1572 $ |

Ein einzelnes Konto ist ein einzelner Pfad und streut stark. GFT-nah liegt 6.50 hier 2025 vorn und 2026 gleichauf.

### 6.5 Fremddaten 2006–2021

| Variante | Auszahlungen | Netto | Busts je Jahr | Bust im 1. Jahr | Abstand Ø | < 100 $ |
|---|---:|---:|---:|---:|---:|---:|
| 6.40 | 2,16 | 364 $ | 0,035 | 0,9 % | 207 $ | 14,6 % |
| 6.50 | 2,14 | 361 $ | 0,034 | 0,6 % | 210 $ | 14,3 % |
| 6.60a | 2,15 | 364 $ | 0,034 | 0,9 % | 208 $ | 14,6 % |
| **6.60** | 2,15 | 363 $ | 0,038 | 1,0 % | 208 $ | 14,7 % |

- Alle Busts liegen in Konten mit Start 2009. Das ist die Episode Februar–Juni 2010, nach dem Ende einer Live-Phase der
  Fades (Abschnitt 7).
- 6.60 hat dort etwas mehr Busts als 6.50: +0,0041 ± 0,0013 je Jahr, in 12 von 16 Störungen mehr. Gegenüber 6.40 sind es
  +0,0033 ± 0,0014.
- Das ist der bekannte Preis von 0,75 statt 0,70 % (Bericht 6.50, Anhang A). Er liegt innerhalb der Protokoll-Grenze
  (+0,005).

### 6.6 Stress: 20 % der Fade-Gewinner entfernt

Aus jeder Fade-Signalliste (beide Datensätze) wird zufällig, aber fest je Signal, jeder fünfte Gewinner entfernt. Wächter,
RSI21-Regime und Konto sehen dieselbe geschwächte Kante.

| Variante | Auszahlungen (Tage) · Netto, breit | Abstand Ø · < 100 $ | Auszahlungen (Tage) · Netto, GFT-nah | Abstand Ø · < 100 $ |
|---|---|---|---|---|
| 6.40 | 6,08 (60,1) · 1076 $ | 190 $ · 3,2 % | 7,92 (46,2) · 1394 $ | 221 $ · 0,0 % |
| 6.50 | 5,97 (61,2) · 1163 $ | 198 $ · 0,4 % | 8,37 (43,7) · 1649 $ | 228 $ · 0,0 % |
| 6.60a | 6,07 (60,2) · 1116 $ | 190 $ · 3,0 % | 8,00 (45,7) · 1462 $ | 223 $ · 0,0 % |
| **6.60** | **6,29 (58,2) · 1217 $** | 192 $ · 3,2 % | 8,33 (43,9) · 1654 $ | 223 $ · 0,0 % |

- Busts: 0 in allen Zellen.
- Mit einer um ein Fünftel schwächeren Kante halbieren sich die Auszahlungen bei breiten Spreads. Das Konto bleibt aber
  überall über dem Boden.
- 6.60 hat die meisten Auszahlungen: breit +0,31 gegen 6.50 (13 von 16) und +0,20 gegen 6.40 (13 von 16).
- Die Sicherheit entspricht der von 6.40.

### 6.7 Bilanz nach Protokoll und Entscheidung

| Kriterium | 6.60 gegen 6.40 | 6.60 gegen 6.50 |
|---|---|---|
| K-a Screening | **erfüllt**: breit +0,51 Auszahlungen, +12 % Netto; GFT-nah −0,07, +11 % | **nicht erfüllt**: breit −0,18, −4 %; GFT-nah +0,02, +0,2 % |
| K-b Walk-Forward | **erfüllt**: 2022–23 +0,51 / −0,07 Auszahlungen und +13 / +11 % Netto; 2024–25 +0,35 / +0,04 und +134 / +114 $ | **nicht erfüllt**: 2022–23 gleich (−0,01 / +0,22; −2 / +1 %); 2024–25 −0,25 / −0,20 und −75 / −16 $ |
| K-c Sicherheit | **erfüllt**: 0 Busts; Abstand +0 / +3 $; Fremddaten +0,003 Busts je Jahr, +0,1 Prozentpunkte im 1. Jahr | **knapp nicht**: Abstand GFT-nah −10,1 $ (Grenze −10); Fremddaten +0,004 (Grenze +0,005), +0,4 Prozentpunkte (Grenze +0,5) |
| K-d paarweise | **erfüllt**: Netto 16 von 16 in beiden Lagen | 2022–25: 3 / 7 von 16; 2026: 16 / 13 von 16 |
| K-e Plateau | 0,75 % ist kein neuer Wert (6.00–6.40); Nachbar 0,70 % = 6.50 | – |
| K-f Einfachheit | **erfüllt**: keine neue Handelseingabe | – |
| K-g Stress | **erfüllt**: 0 Busts, Abstand +2 $, < 100 $ wie 6.40 | breit **nicht erfüllt**: < 100 $ 3,2 statt 0,4 %, Abstand −6 $; GFT-nah gleich |
| Zukunftstest 2026 (zusätzlich) | Netto +137 bis +185 $, Auszahlungen gleich | **+0,8 bis +1,35 Auszahlungen, +131 bis +236 $** |

**Entscheidung:** 6.60 wird Echtbetrieb. Das weicht vom Protokoll ab, das 6.50 als Basis nannte. Die Gründe:

1. Die Änderung ist eine Rücknahme. 0,70 % hätte das Protokoll selbst nicht bestanden (Abschnitt 5.1); 6.50 hatte es auf
   ganz 2022–25 gewählt, ohne Walk-Forward. Gegen 6.40, den Stand davor, besteht 6.60 alle Kriterien.
2. Auf Daten, die keine Entscheidung gesehen haben, liegt 6.50 in beiden Spread-Lagen und bei beiden Laufzeiten klar
   hinten: −0,8 bis −1,35 Auszahlungen je Jahr, in 13–16 von 16 Störungen.
3. Im schlechtesten Jahr kostet 6.60 gegenüber 6.50 wenig (−0,34 Auszahlungen, −88 $). Umgekehrt kostet 6.50 viel
   (−1,34, −236 $).
4. Der Preis ist bekannt und klein: der Sicherheitsabstand von 6.40 statt 6.50. Busts gab es auf dem GFT-Ersatz, im
   Zukunftstest und unter Stress keine.

Der Zukunftstest 2026 ist damit **verbraucht**. Er hat eine Entscheidung mitbestimmt und ist für künftige Builds nicht mehr
unberührt. Der nächste echte Test sind der Live-Betrieb und Daten ab September 2026.

### 6.8 Sicher

Das Sicher-Set handelt nur die Fades. Dort ist 0,70 % besser:

| Variante | 2022–25 breit / GFT-nah | 2026 breit | 2026 GFT-nah |
|---|---|---|---|
| Sicher mit 0,75 % (6.40 Sicher) | 7,11 · 1225 $ / 7,91 · 1487 $ | 9,42 (38,8 T) · 1601 $ | 9,98 (36,6 T) · 1668 $ |
| **Sicher mit 0,70 % (6.50 und 6.60 Sicher)** | 7,11 · 1234 $ / 8,00 · 1516 $ | **9,75 (37,5 T) · 1704 $** | **10,21 (35,8 T) · 1757 $** |

2026 paarweise: +0,32 / +0,23 Auszahlungen und +103 / +89 $ (15 bzw. 13 von 16). Vermutlich weil ohne RSI21 und Noise jeder
Fade-Verlust das Konto schneller unter den Startsaldo drückt, wo die Pufferkurve verkleinert. Das Sicher-Set bleibt deshalb
bei 0,70 % und bekommt nur die Regime-Meldungen.

## 7. Regime-Meldungen

Die Fades verdienen seit Mitte 2022. Vorher verloren sie über 16 Jahre (Abschnitt 4.2, K5). Der Portfolio-Wächter (seit 6.40)
lässt sie nur live handeln, solange der Profitfaktor (PF) der letzten 200 virtuellen Fade-Signale über 1,15 liegt. Sonst
laufen sie nur virtuell weiter. Bisher stand das nur im Panel und im Journal. Ohne Fades zahlt der EA aber nur noch rund
alle 170 Tage aus (Fremddaten), und das sollte man wissen. 6.60 meldet deshalb per Push:

- `FADE-REGIME AUS: PF … <= 1.15 - Fades nur noch virtuell, RSI21 an gueltigen Tagen geschuetzt. Auszahlungen werden seltener.`
- `FADE-REGIME WIEDER LIVE: PF … > 1.15 - Fades handeln wieder`. Liegt der PF dabei noch unter 1,25, folgt der Zusatz
  `(FRUEHWARNUNG: PF noch unter 1.25)` in derselben Meldung.
- `FRUEHWARNUNG Fade-Regime: PF … (Abschaltung bei <= 1.15) - der Vorteil der Fades laesst nach`. Die Vorwarnung kommt,
  solange die Fades live sind und der PF unter `FadeFruehwarnPF` (1,25) liegt, höchstens alle 7 Tage. Nach einer Erholung
  über 1,30 ist sie sofort wieder möglich.

**Rückblick** (`a60_warn.py`, dieselbe Rechnung wie der Wächter; `ergebnisse/a60_warn.txt`):

| Zeitraum | PF der letzten 200 Signale (Median) | Fades live | Vorwarnungen aus einer Live-Phase | … danach abgeschaltet | Abschaltungen |
|---|---:|---:|---:|---:|---:|
| 2006–13 | 0,90 | 13 % | 5 | 3 (nach 8, 12 und 18 Tagen) | 10 |
| 2014–21 | 0,81 | 1 % | 0 | – | 4 (Okt.–Dez. 2016, je 1–5 Tage live) |
| 2022–25 | 1,48 | 88 % | 5 (08/2022, 4× Apr.–Aug. 2025) | 0 | 1 (14.06.2022, Übergang ins neue Regime) |
| 2026 (bis Aug.) | 1,70 | 100 % | 0 | – | 0 |

- **Warum 1,25:** Im heutigen Regime lag der PF 2022–25 rund 4 % der Zeit zwischen 1,15 und 1,25 und 2026 nie. Die Vorwarnung
  kommt also selten.
  - Mit 1,30 hätte sie 2022–25 in acht Phasen gewarnt, davon fünfmal 2025, und keine davon endete mit einer Abschaltung.
  - Mit 1,20 käme sie im alten Regime teils erst am Tag der Abschaltung.
  - Der Wert beeinflusst nur Meldungen, nicht den Handel.
- In den Warnphasen 2025 verdienten die Fades weiter (+0,6 bis +6,8 R). **Eine Vorwarnung ist kein Grund, von Hand
  einzugreifen.** Der Wächter entscheidet selbst.
- Im alten Regime flackerte der Wächter oft: Die Fades waren wenige Tage knapp über 1,15 live, dann wieder aus (2007, 2013,
  2016). Jeder dieser Wechsel ist echt (der EA handelt dann tatsächlich) und wird gemeldet.
- Der zuletzt gemeldete Zustand und die Zeit der letzten Vorwarnung überleben einen Neustart (Terminal-Globalvariablen
  `DEADBAND4_<Login>_REGLIVE` / `_REGWARN`). Ein Wechsel, während der EA aus war, wird beim ersten Durchlauf gemeldet.

## 8. Was 6.60 ändert

| Eingabe | 6.40 | 6.50 | **6.60** | Bedeutung |
|---|---:|---:|---:|---|
| `FadeRiskPct` | 0,75 | 0,70 | **0,75** | Risiko je Fade-Trade in % vom Startsaldo (× Pufferkurve) |
| `FadeFruehwarnPF` (neu) | – | – | **1,25** | Vorwarnung, solange die Fades live sind und der PF unter X liegt. 0 = keine Vorwarnung; die Meldungen bei jedem Wechsel bleiben |
| Sicher-Set: `FadeRiskPct` | 0,75 | 0,70 | 0,70 | unverändert wie 6.50 Sicher |

- **Handelslogik:** wie 6.50, nur mit 0,75 % Fade-Risiko. Der Schutz gültiger Tage (N1330/N1300 frei, RSI21 ab 13:00 NY
  im Fade-Regime), der Portfolio-Wächter, die Pufferkurve und die Auszahlungsregeln bleiben unverändert.
- **Regime-Meldungen:** `RegimeWaechter()` läuft alle 5 Minuten im Hauptdurchlauf. Die Funktion rechnet den PF genau wie der
  Wächter (`FadePortfolioPF`) und sendet nur Meldungen. Sie schreibt keine Variable, die der Handel liest
  (`t_port_660.py`, Punkt 5). Sie meldet nur, wenn der Portfolio-Wächter aktiv ist (`FadePortPF` > 0,
  `FadeWaechterModus` = 1) und die Historie aller Module vollständig ist.
- **Journal beim Start:** `DEADBAND4: 6.60 Zukunft | Fade-Risiko 0.75 % je Trade (6.50: 0,70) | Regime-Meldungen Push bei
  jedem Wechsel LIVE <-> nur virtuell (PF 1.15), Vorwarnung bei PF < 1.25`.
- **Panel:** Titel „DEADBAND LIVE 6.60 ZUKUNFT“. Die Fade-Zeile zeigt bei live laufenden Fades und PF unter 1,25
  `FRUEHWARNUNG (< 1.25)`.
- **Rückweg:**
  - Zur Handelslogik von 6.50 im selben EA: `FadeRiskPct=0.70`.
  - Vollständig: `rollback_6.50/` (mq5, `DEADBAND_LIVE4_Echtbetrieb.set`, `DEADBAND_LIVE4_650_Sicher.set`).
  - Ein 6.50-Set in den 6.60-EA geladen: `FadeRiskPct` kommt dann aus dem Set (0,70), die Vorwarnung steht auf 1,25.

## 9. Prüfung

- **Kursdaten neu aufgebaut** aus den Quellen des Datenberichts (byte-identisch). Neu hinzugekommen sind US500 und
  NAS100-Ticks 2025–26 (Datenbericht, Abschnitt 10), ebenfalls reproduzierbar (SHA-256 dort).
- **Baselines reproduziert:**
  - 6.40: 11,25 / 2051 $ (breit), 12,06 / 2232 $ (GFT-nah), Fremddaten 2,16 / 0,035 / 364 $.
  - 6.50: 11,66 / 2319 $, 12,12 / 2510 $, 2,14 / 0,034 / 361 $.
  - Alles wie in den Berichten 6.40 und 6.50.
- **eng10 = eng9** mit Voreinstellungen (`t_eng10.py`: 45 Konten, Trades und Ereignisse identisch).
- **Abgleich EA ↔ Replikat** (`t_port_660.py`, Protokoll `Replikat_v6/ergebnisse/t_port_660.txt`): **identisch**.
  1. Voreinstellungen des EA = Replikat-Variante „6.60b“ (Fade-Risiko 0,75, Schutz je Modul, freie Fades, Wächter,
     Modul-Reihenfolge).
  2. Die Quelltext-Stellen des Schutzes je Modul sind vorhanden.
  3. Die Entscheidung des Schutzes je Modul stimmt auf 164 640 Zuständen überein.
  4. Fade-Regime für RSI21: GFT-Ersatz 1036 Signale (1002 live), Fremddaten 3550 (182 live).
  5. `RegimeWaechter` ruft nichts auf, was handelt. Die Funktion schreibt nur eigene Variablen und eigene
     Terminal-Globalvariablen, wird genau einmal aufgerufen, und ihre Voreinstellung entspricht der Rückblick-Rechnung.
- **Presets** (`t_set.py`): `DEADBAND_LIVE4_Echtbetrieb.set` enthält alle 228 Eingaben mit den Voreinstellungen des EA.
  `DEADBAND_LIVE4_660_Sicher.set` weicht nur in `R21Aktiv`, `NzAktiv`, `SerienStopp`, `FadeRiskPct` (0,70) und
  `GueltigSchutzFrei` (leer) ab.
- **Statische Prüfung** (`t_mq5.py`): Klammern, Format-Argumente, Deklarationen vor der Verwendung – bestanden.
- **Gegenlesen** der EA-Änderungen durch einen Sub-Agenten: keine Kompilierfehler, kein Einfluss auf den Handel, alle
  Format-Aufrufe passend, Push-Texte unter 255 Zeichen. Umgesetzte Hinweise:
  1. Zustand und Vorwarnzeit überleben einen Neustart (sonst neue Vorwarnung nach jedem Neustart, Wechsel während einer
     Pause ungemeldet).
  2. Beim Wechsel auf live mit PF unter 1,25 geht nur eine Push-Meldung raus. Zwei Meldungen im selben Moment würden das
     Push-Limit von MetaTrader streifen.
  3. Die Panel-Vorwarnung erscheint nur bei aktivem Portfolio-Wächter.
  4. Der AUS-Text nennt RSI21 nur, wenn RSI21 an ist und der Regime-Schalter wirkt (im Sicher-Set nicht).
  5. Texte: die Eingabe-Kommentare zu `FadeFruehwarnPF` und `FadeRiskPct`, der Kopf und die Set-Köpfe stimmen mit dem Code
     und den Zahlen überein. Ungenutzte Variablen sind entfernt.
- **Nicht** geprüft: Kompilieren in MetaEditor, Strategietester, Demo.

## 10. Echtbetrieb

Dateien:

- `DEADBAND_LIVE4.mq5`: Die Voreinstellungen **sind** das Echtbetrieb-Set („Ertrag“ + 6.60).
- `DEADBAND_LIVE4_Echtbetrieb.set`: dieselben Werte als Datei.
- `DEADBAND_LIVE4_660_Sicher.set`: „Sicher“ (nur Fades), Fade-Risiko 0,70 %, mit Regime-Meldungen.
- Rückweg: `rollback_6.50/`; ältere Stände in `rollback_6.40/`, `rollback_6.30/`, …

Inbetriebnahme:

1. `DEADBAND_LIVE4.mq5` in MetaEditor kompilieren. Erwartet: 0 Fehler.
2. **Max. Balken im Chart = Unbegrenzt** (wie seit 6.20). Wächter, RSI21-Regime und Regime-Meldungen brauchen 200 virtuelle
   Signale in 600 Tagen M5.
3. Strategietester: „Jeder Tick anhand realer Ticks“, XAUUSD.x M15, 2024–2026. Im Journal prüfen:
   - beim Start `6.60 Zukunft | Fade-Risiko 0.75 % je Trade (6.50: 0,70) | Regime-Meldungen Push bei jedem Wechsel …`,
     und in der Fade-Zeile `Risiko 0.75 %`,
   - bei vollständiger Fade-Historie keine Regime-Meldung, solange der PF über 1,25 liegt,
   - Rest wie 6.50 (Schutz gültiger Tage, N1330/N1300 frei, RSI21 ab 13:00 NY, Auszahlungsreife, Pufferkurve).
4. Eine Woche auf einem Demokonto mit gleicher Serverzeit, dann live nur auf dem eigenen PC, EIN Chart.
5. **Auszahlung sofort beantragen,** sobald der EA „JETZT AUSZAHLUNG BEANTRAGEN“ meldet (Push). Dann
   `AuszahlungAngefordertAm` setzen, wie bisher.
6. **Bei „FADE-REGIME AUS“:** nichts von Hand ändern. Die Fades laufen virtuell weiter und gehen von selbst wieder live. Mit
   „Sicher“ kann das Konto dann wochenlang ohne Trade bleiben (GFT: 30 Tage ohne Trade = Konto weg). Der
   Inaktivitäts-Push nach 20 Tagen bleibt wie bisher.

## 11. Grenzen und Hinweise

1. **Kein GFT-Datentest.** Alle Konto-Zahlen stammen vom GFT-Ersatz aus Fremddaten. Mit den GFT-Exporten nachrechnen:
   Dateien nach `data/`, dann `python prep5.py && python sig5.py` und `python x61.py gft`.
2. **Der Zukunftstest ist kurz und verbraucht.** Acht Monate, NAS aus einer verrauschteren Quelle (Abschnitt 2.2). Er hat die
   Wahl zwischen 0,70 und 0,75 % mitbestimmt. Für künftige Entscheidungen zählt er nicht mehr als unberührt.
3. **Die Kante ist NAS-spezifisch und regimeabhängig.**
   - Auf US500 tragen dieselben Fades nicht (Abschnitt 4.2).
   - 2006–21 verloren die Fades. Der Wächter schaltet sie in so einem Regime ab. Dann zahlt der EA nur noch rund alle
     170 Tage aus, und im ersten Jahr endet rund 1 % der Konten mit Bust (Fremddaten).
   - Die Regime-Meldungen machen das sichtbar, verhindern es aber nicht.
4. **Die NAS-Nachmittags-Fades waren 2026 negativ:** N1330 −2,6 R (PF 0,74), N1300 −3,3 R (PF 0,70), Januar–August. Gold
   war stark (+18,3 R, PF 1,82). Die Summe aller Fades 2026 liegt bei +29,3 R, PF 1,46, wie 2024. Der Grid-Filter (6.20)
   hielt: ohne ihn wäre der PF 2026 1,35. Die Freigabe von N1330/N1300 an gültigen Tagen brachte 2026 trotzdem mehr Netto
   (Abschnitt 5.1). Beobachten.
5. **Mehr Auszahlungen gibt es nur mit weniger Abstand zum Boden.** Die Pufferkurve kostet rund 1,1 Auszahlungen je Jahr.
   Ohne sie oder mit größeren Positionen wäre der Takt kürzer, aber die Konten liefen dem Boden nahe (Abschnitt 4.1). Nicht
   lockern.
6. **Sicherheitsabstand wie 6.40, nicht wie 6.50** (Abschnitt 6.7). Wer ihn größer will: `FadeRiskPct=0.70`. Das kostete
   2026 rund eine Auszahlung je Jahr.
7. **Viele Versuche:** 25 Konto-Varianten und 5 Signal-Studien. Übernommen wurde keine neue Idee, nur die Rücknahme eines
   ungeprüften Werts.
8. **Regeln:**
   - Ob GFT den Boden intraday oder zum Tagesschluss nachzieht, bleibt offen. Der EA rechnet streng intraday.
   - Handel während einer laufenden Auszahlung ist nicht belegt. Der EA bleibt flach.
   - Wer mehrere GFT-Konten mit demselben EA betreiben will, prüft vorher die GFT-Regeln zu gleichgerichtetem Handel über
     mehrere Konten.
9. **Nicht kompiliert, nicht im Tester** (Abschnitt 9).
10. **Lizenz** des Grid-Konzepts unverändert (Bericht 6.20, Abschnitt 10). Die Dukascopy-Daten unterliegen deren
    Nutzungsbedingungen (Datenbericht).

## Anhang: Replikat

`Replikat_v6/README.md` (Abschnitt Build 6.60):

- Prüfprotokoll: `PROTOKOLL_660.md`
- Motor: `eng10.py` (Prüfung `t_eng10.py`), Bewertung: `evl10.py`
- Screening: `x60.py` (Varianten in `VAR`), Endbewertung: `x61.py` (`ABSCHLAG=0.2` für den Stresstest), Zukunftstest:
  `x60f.py` in einer Ordnerkopie mit `mk_proxy2026.py`
- Diagnosen: `a60_sig.py` (Signal-Ebene je Periode, Trend, Spiegel, Zielweiten), `a60_jahr.py` (Konto je Startjahr und
  Modul), `a60_drag.py` (Konto gegen Signal), `a60_stufen.py` / `a60_stufen2.py` (Signal → Filter → Wächter → Konto),
  `a60_fak.py` (Anteil verkleinerter Trades), `a60_spx.py` (K2 US500), `a60_schock.py` (K3), `a60_nzs.py` (Noise short,
  Gold-Noise), `a60_warn.py` (Regime-Meldungen rückwirkend)
- Prüfungen: `t_eng10.py`, `t_port_660.py`, `t_set.py`, `t_mq5.py`
- Ergebnisse: `ergebnisse/x60_gft.json`, `x61_gft.json`, `x61_ext.json`, `x61_gft_abschlag20.json`, `x60f_2026.json`
  (GFT-nah jeweils `…_spread06.json`), `a60_*.txt`, `t_port_660.txt`
- Kursdaten: `extdata/scripts/run_all.sh` (Fremddaten), `build_us500.py`, `build_nas_dukascopy.py`;
  `Replikat_v6/mk_proxy.py` (GFT-Ersatz), `mk_proxy2026.py` (Zukunftstest; `SPREAD_FAKTOR=0.6` für GFT-nahe Spreads, nur in
  einer Kopie des Ordners)
