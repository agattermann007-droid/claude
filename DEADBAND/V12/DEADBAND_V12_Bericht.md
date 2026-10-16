# DEADBAND V12 – Bericht (Build 12.00, 16.10.2026)

## 1. Kurzfassung

**Ergebnis dieser Runde: Eine Änderung hat alle Prüfungen bestanden – N1030 handelt im Tick (Modul `SRT1030`) mit
0,50 % Risiko.** Alles andere bleibt wie in 11.00 (= 10.00). Dazu kommt eine wichtige Korrektur des Nachbaus, die
einen Befund aus V11 umdreht.

Methode wie in V11: alle 7 Tage startet ein frisches 10k-Konto mit 1 Jahr Laufzeit, GFT-Premium-Regeln, Schlupf
¼ Spread. Neu ist ein fünftes Fenster mit Kontostart 2011–2015 (Gold aus OANDA-Daten, siehe 3.2). Vergleiche sind
gepaart über 32 Störungen (je 3 % andere Signale); angegeben ist Mittelwert ± Standardfehler der Differenz.
„$/J“ ist dein Anteil nach Split und 3 % Gebühr.

| Fenster (Kontostart) | V11 Ausz./J | V12 Ausz./J | Differenz | V11 $/J | V12 $/J | Differenz | Busts |
|---|---|---|---|---|---|---|---|
| 2022 (Auswahl) | 12,27 | 12,93 | +0,66 ± 0,12 | 2.409 | 2.522 | +112 ± 35 | 0 → 0 |
| 2023 | 13,20 | 14,49 | +1,30 ± 0,14 | 2.576 | 2.811 | +235 ± 44 | 0 → 0 |
| 2024–25 | 7,68 | 7,61 | −0,07 ± 0,17 | 1.656 | 1.676 | +21 ± 41 | 0 → 0 |
| 2017–20 | 5,57 | 5,79 | +0,23 ± 0,03 | 1.054 | 1.116 | +61 ± 8 | 0 → 0 |
| 2011–15 (neu) | 3,71 | 3,71 | −0,01 ± 0,00 | 681 | 681 | −1 ± 1 | 0 → 0 |

Was du daraus mitnehmen solltest:
1. **V12 bringt im Auswahlfenster 2022 +0,66 Ausz./J, 2023 +1,30 und 2017–20 +0,23.** 2024–25 und 2011–15 bleiben
   gleich (Differenz im Rauschen), 0 Busts in allen 5 × 32 Rechnungen. Der Vorteil kommt vom Einstieg im Tick, nicht
   vom kleineren Risiko: N1030 auf M5 mit 0,50 % ändert nichts (Gegenprobe). **Einschränkung:** Ohne Schlupf ist der
   Vorteil etwa halb so groß, und 2024–25 ist in allen Rechnungen leicht negativ (−0,07 bis −0,38 Ausz./J, nicht
   signifikant). Deshalb bitte im Tester prüfen (Abschnitt 7) – der Rückfall ist ein Schalter.
2. **Der Nachbau hatte einen Fehler, der alle Kontozahlen aus V11 verzerrt hat** (Abschnitt 2). Korrigiert gilt:
   **SR hilft auch 2024–25** – V10/V11 ist in allen fünf Fenstern mindestens so gut wie V8. Der V11-Befund
   „SR 2024–25 nicht besser“ war ein Artefakt.
3. **Für das Regime „Fades aus“ (2011–21) gibt es keinen neuen Strom.** 208 Kandidaten auf Stromebene, 44 auf
   Kontoebene: Ströme mit positivem Erwartungswert, aber niedriger Trefferquote und engem Stop machen das Konto unter
   den GFT-Regeln schlechter (weniger gültige Tage, mehr Serien-Stopps, Busts am trailenden Boden). In diesem
   Regime bleibt es bei ~3,7 (2011–15) bzw. ~5,6 (2017–20) Ausz./J.

## 2. Diagnose: Fehler im Nachbau und was er verändert

### 2.1 Der Fehler

Im EA wird jeder Tick bearbeitet. Der Nachbau springt bei flachem Konto von einer Signal-Minute zur nächsten. Dabei
gingen zwei Dinge verloren:

1. **Noise-Prüfungen fielen aus.** Nach einer Noise-Prüfung (stündlich 10–15 Uhr NY) zeigte der interne Zeiger noch
   auf die gerade bearbeitete Minute; die *folgende* Prüfung wurde beim Sprung übersehen, wenn keine anderen Signale
   dazwischen lagen. Noise handelte dadurch zu selten und zu spät.
2. **Die RSI21-Wiederaufnahme nach dem Wochenende** erfolgte erst in der nächsten besuchten Minute.

Die Folge war schlimmer als „Noise etwas zu schwach“: **Jeder zusätzliche Strom veränderte nebenbei den
Noise-Strom**, weil seine Signal-Minuten weitere Noise-Prüfungen „besuchbar“ machten. Ein Vergleich „mit/ohne
Strom X“ maß also X plus eine zufällige Noise-Änderung. Gefunden habe ich das, weil „SR nur bei Fades aus“ 2024–25
(dort sind die Fades immer live, SR handelt also nie) nicht dasselbe ergab wie V8.

### 2.2 Prüfung der Korrektur

Ein abgeschalteter Dummy-Strom mit Signalen in jeder 7. Minute verändert jetzt **kein einziges von 521 Konten**
(`t12_engine_check.py`). Vorher waren es bei Seed 0 bis zu ±1,7 Ausz./J.

### 2.3 Neue Grundlinie (32 Störungen)

| Fenster | V8 Ausz./J | V10 = V11 Ausz./J | V8 − V10 | V8 $/J | V10 $/J | V8 − V10 $/J |
|---|---|---|---|---|---|---|
| 2022 (Auswahl) | 9,70 | 12,27 | −2,56 ± 0,17 | 1.697 | 2.409 | −713 ± 32 |
| 2023 | 11,63 | 13,20 | −1,57 ± 0,23 | 2.383 | 2.576 | −193 ± 63 |
| 2024–25 | 7,54 | 7,68 | −0,14 ± 0,21 | 1.563 | 1.656 | −92 ± 43 |
| 2017–20 | 4,85 | 5,57 | −0,71 ± 0,07 | 926 | 1.054 | −128 ± 18 |
| 2011–15 (neu) | 3,09 | 3,71 | −0,62 ± 0,06 | 597 | 681 | −84 ± 11 |

Gegenüber dem V11-Bericht verschieben sich die Zahlen spürbar, am stärksten bei V8 (2024–25: V8 7,5 statt 8,4,
V10 7,7 statt 7,9 Ausz./J). Im alten Nachbau war V8 dort vorn, jetzt ist V10 überall mindestens gleich.
**Alle Kontozahlen aus dem V11-Bericht sind überholt.** Die Stromebene (R je Trade) war nicht betroffen.

## 3. Daten

### 3.1 Abgleich

Mit dem unveränderten Nachbau v11 reproduziert: V10 Start 2022 11,58, 2024–25 7,17; V8 9,46 / 7,02 Ausz./J (Seed 0) –
genau wie im Prompt. Danach die Korrektur aus Abschnitt 2.

### 3.2 Erweiterter Datensatz 2010–2026, Prüffenster 2011–15

- Gold 2010-01 bis 2016-08 aus OANDA M1 (Mid), danach Dukascopy wie bisher; NAS (HistData) ab 2010-11.
- Ab 2016-09 sind die Kurse identisch zum Standardsatz; die Kennzahlen 2022–25 stimmen exakt, 2017–20 bis auf
  ±0,01 Ausz./J (längere Historie des Portfolio-Wächters).
- Damit lassen sich ganze Konten mit Start 2011–2015 rechnen. Der Portfolio-Wächter ließ die Fades dort fast nie
  live (2011–12, 2014–18, 2020–21: 0 %; 2013: 44 %; 2019: 42 %; 2022: 53 %; ab 2023: 98–100 %). Das Fenster ist also
  ein zweites, unabhängiges Beispiel für das Regime „Fades aus“ – und es ist härter als 2017–20: V10 nur 3,7 Ausz./J,
  16 % der Konto-Jahre ohne Auszahlung.
- Die GFT-M5-Daten konnte ich nicht nutzen: Im Drive liegen nur die ganzen CSVs (~30 MB), keine ZIPs < 10 MB.

## 4. Tests

Zahl der geprüften Varianten (Zufallsgefahr): 208 Stromkandidaten, 44 Regime-Kandidaten auf Kontoebene, 10
SR-Varianten, 5 SR-Risikostufen, 1 Regime-Größe, 5 Tick-Fade-Varianten, 5 Nachbarn/Gegenproben, 4 IMOM-Mechanik-
Varianten. Bestanden hat eine Variante; ihre sechs Nachbarn sind ebenfalls besser bzw. gleich.

### 4.1 N1030 im Tick (Prompt 9.5) – übernommen

Tick-Fade = dieselbe Range wie N1030 (10:30–12:30 NY), Einstieg aber im Tick, sobald der Kurs nach dem Docht unter
das Range-Tief wieder in die Range zurückkehrt (statt am Open nach dem M5-Schluss). Stop 0,3 × Range unter dem
Extrem, Ziel Range-Mitte, Ausstieg 15:30 NY, nur bei live Portfolio-Wächter.

Gepaart gegen V10, 32 Störungen, Differenz Ausz./J (Busts in Klammern, nur wenn > 0):

| Variante | 2022 | 2023 | 2024–25 | 2017–20 | 2011–15 |
|---|---|---|---|---|---|
| N1030+N1100 Tick 0,75 % (= V11TickFades) | +0,94 | +1,48 | −0,58 (7) | +0,41 | +0,13 (**333**) |
| N1030+N1100 Tick 0,50 % | +0,55 | +1,16 | −0,20 | +0,35 | +0,06 (**133**) |
| N1100 Tick 0,75 % | +0,94 | +0,50 | **−0,47** | +0,33 | +0,03 |
| N1030 Tick 0,75 % | +0,68 | +1,34 | −0,15 | +0,25 | +0,01 (**12**) |
| **N1030 Tick 0,50 % (V12)** | **+0,66 ± 0,12** | **+1,30 ± 0,14** | **−0,07 ± 0,17** | **+0,23 ± 0,03** | **−0,01 ± 0,00** |
| N1030 Tick 0,40 % | +0,16 | +0,98 | −0,03 | +0,22 | −0,01 |
| N1030 Tick 0,60 % | +0,74 | +1,49 | −0,24 | +0,25 | +0,01 |
| N1030 Tick 0,50 %, Puffer 0,2 | +0,33 | +0,21 | +0,02 | +0,32 | −0,00 |
| N1030 Tick 0,50 %, Puffer 0,4 | +0,72 | +1,30 | −0,18 | +0,16 | +0,01 |
| Gegenprobe: N1030 **M5** 0,50 % | −0,02 | +0,04 | +0,20 | +0,04 | +0,00 |

In $/J (V12): 2022 +112 ± 35, 2023 +235 ± 44, 2024–25 +21 ± 41, 2017–20 +61 ± 8, 2011–15 −1 ± 1.

- **Busts der Tick-Fades** liegen in genau zwei Episoden: 10.10.2013 (Fades 2013 zeitweise live, dann Verluste) und
  21.07.2025 (der Rückgang aus dem V11-Bericht). Viele Konten mit ähnlichem Start laufen gemeinsam in denselben
  Rückgang. Mit N1030 allein und 0,50 % erreicht keine der 32 Störungen den Boden; 0,75 % schon.
- **Plateau:** Risiko 0,40–0,60 % und Stop-Puffer 0,2–0,4 × Range sind alle besser in 2022, 2023, 2017–20 und gleich
  in 2024–25 und 2011–15. 0,50 % / 0,3 liegt in der Mitte; Abstand zu 0,75 %, wo Busts beginnen.
- 2024–25 ist bei allen Tick-Varianten im Mittel leicht negativ bei den Auszahlungen (−0,03 bis −0,24), beim Geld
  aber ±0. Das ist innerhalb des Rauschens; ich weise es trotzdem aus.

### 4.2 SR 2024–25 verstehen (Prompt 9.4)

- **Stromebene:** Die SR-Marken sind 2024–26 nicht schwächer, eher stärker: SRIB +0,11, SRPRE +0,19, SRH12 +0,09,
  SRPDN +0,17 R je Trade.
- **Kontoebene (korrigierter Nachbau, 16 Störungen, 2024–25):** SR selbst bringt +239 $/J; die NAS-Long-Module
  verlieren zusammen ~280 $/J (N0930 −63, N1100 −48, N1300 −44, N1030 −41, N1330 −35, Noise −44). Mechanismus:
  **Mit SR gibt es doppelt so viele Serien-Stopps** (61 statt 31 je Konto-Jahr; 2011–15 67 statt 25), weil SR mit
  39 % Treffern viele kleine Verluste liefert. Netto bleibt V10 vorn (+84 $/J).
- **Varianten** (32 Störungen, Differenz zu V10, Ausz./J):

| Variante | 2022 | 2023 | 2024–25 | 2017–20 | 2011–15 |
|---|---|---|---|---|---|
| SR zählt nicht für den Serien-Stopp | −1,38 | −1,13 | +0,21 | −0,78 | −0,15 (1 Bust) |
| Serien-Stopp aus | −0,96 | −0,06 | +1,47 | −0,59 | −0,06 (1 Bust) |
| Serien-Stopp nach 4 | −1,33 | +0,15 | +0,60 | −0,43 | +0,06 (1 Bust) |
| SR nur bei Fades aus | −1,72 | −1,75 | −0,14 | −0,20 | +0,03 |
| SR nur bei Fades live | −0,94 | +0,06 | ±0 | −0,69 | −0,68 |
| nur SRPRE (Short) | −1,21 | −1,21 | +0,06 | −1,00 | −0,28 |
| ohne SRIB | −0,60 | −0,05 | −0,02 | −0,34 | −0,07 |
| ohne SRPRE | −0,32 | −0,63 | +1,81 | −1,07 | −0,08 |
| ohne SRH12 | −0,09 | +0,36 | −0,01 | −0,29 | −0,01 |
| ohne SRPDN | −0,54 | −0,32 | −0,14 | −0,22 | −0,10 |

  Die Serien-Stopps, die SR auslöst, **schützen** – ohne sie wird es deutlich schlechter. Jede Marke trägt bei.
- **SR-Risiko** (neu gerechnet; in V11 mit dem fehlerhaften Nachbau):

| SR-Risiko | 2022 | 2023 | 2024–25 | 2017–20 | 2011–15 |
|---|---|---|---|---|---|
| 0,05 % | −1,10 | −0,11 | −0,29 | −0,25 | −0,41 |
| **0,10 % (V10)** | 0 | 0 | 0 | 0 | 0 |
| 0,15 % | −0,14 | +0,30 | −1,10 (16 Busts) | +0,37 | +0,22 (14 Busts) |
| 0,20 % | +0,06 | +0,47 | −0,13 (5 Busts) | +1,01 | +0,41 (198 Busts) |
| 0,25 % | −0,38 | +0,25 | +0,31 | +0,54 | +0,40 (252 Busts) |
| 0,30 % | −2,03 | +0,91 | +1,17 | +0,48 (5 Busts) | +0,88 (364 Busts) |

  Über 0,10 % kommen im schwachen Regime 2011–15 Busts dazu → **SR bleibt bei 0,10 %.**

→ SR bleibt unverändert. Deine Tester-Prüfung `SrAktiv` false gegen true bleibt sinnvoll; der Nachbau sagt jetzt:
SR hilft auch 2024–26 (beim Geld deutlich, bei der Zahl der Auszahlungen im Rauschen).

### 4.3 Regime „Fades aus“ (Prompt 9.3)

**Stromebene** (`t12_regime_scan.py`, Regel vor dem Lauf: im Regime „Fades aus“ E ≥ +0,05 R und PF ≥ 1,10 in
2016–21 und E > 0 in 2011–16): 208 Varianten (ORB 5/15/30 min, Intraday-Momentum, Ausbruch statt Fade auf allen
10 Fade-Ranges, Gold-Ausbruch mit D1-Trend, Tick-Fades). 13 bestehen, alle aus zwei Familien:

- **Intraday-Momentum NAS (IMOM)**: Bewegung Vortagsschluss → 10:00/10:30 ≥ 0,3 ATR → in Richtung der Bewegung,
  Stop 0,2 ATR, Ausstieg 15:55. Beste Variante 2011–16 +0,17 R, 2016–21 +0,17 R, 2022–23 +0,13 R, 2024–26 −0,06 R –
  genau das Gegenstück zu den Fades. (Logisch dasselbe wie das TD-Modul mit anderen Parametern.)
- **ORB 5 min** (Richtung der ersten 5 Minuten, Stop 0,1 ATR, Ausstieg 15:55): +0,08 / +0,14 / −0,02 / +0,11 R.
- Ausbruch statt Fade, Gold-Trend-Ausbruch und Tick-Fades: in 2011–16 ohne Vorteil.

**Kontoebene** (nur bei Fades aus, 0,50 %, 16 Störungen, 3 Fenster): **0 von 44 bestehen.**

| Familie | typisches Ergebnis (Ausz./J 2022 / 2017–20 / 2011–15) | Busts |
|---|---|---|
| IMOM 10:00, Stop 0,2–0,4, beide Richtungen | +0,4 bis +0,7 / −0,5 bis 0 / −0,2 bis −0,7 | 0–105 |
| IMOM 10:00, nur Long | −0,1 bis −0,4 / −0,2 bis −0,7 / 0 bis +0,6 | 0–1 |
| IMOM 10:30 | meist −0,3 bis −1,8 in 2017–20 | 34–190 |
| ORB 5/10 min | −0,1 bis −2,0 überall | 741–2.982 |

Warum ein Strom mit +0,2 R je Trade das Konto schlechter macht (IMOM, Seed 0): IMOM verdient im Konto +140 bis
+234 $/J, aber die Auszahlungen sinken (2017–20 4,9 statt 5,8). Ursachen: 35 % Treffer → viele Verlusttage und
mehr Serien-Stopps; in diesem Regime ist der Engpass die Zahl der gültigen Tage (2011–15 nur ~25 je Jahr). Lange
Verlustserien mit 0,5 % (10 Verluste = 5 %) treiben Konten unter 1,25 % Puffer, wo sie mit Faktor 0,1 handeln und
kaum herauskommen. ORB mit Stop 0,1 ATR ist eine Position von mehreren Konten-Werten: der Boden trailt mit den
Kursspitzen innerhalb der Minute mit (GFT: trailend am Equity-Hoch), normale Rückläufe reichen dann für 6 %.

Weitere Versuche für dieses Regime:
- **Regime-Größe ×1,25** (RSI21 und Noise größer, solange die Fades nicht live sind; im EA gibt es `RegimeGroesse`,
  bisher nur ≤ 1): 2017–20 −0,28, 2011–15 −0,27 Ausz./J, 45 Busts → verworfen, stärkere Stufen nicht mehr gerechnet.
- IMOM ohne Abschluss-Ernte bzw. ohne Serienzähler: nicht besser.

→ Für 2011–21 bleibt der Hebel offen. Mein Schluss: Unter den GFT-Regeln (trailender Boden, 5 gültige Tage) helfen
nur Ströme mit hoher Trefferquote und mäßiger Positionsgröße – genau das, was die Fades in ihrem Regime liefern.

### 4.4 Nicht erneut geprüft

- `V11GoldPdf`: verworfen wegen Gold-Drift (OANDA 2010–16), daran ändert der Nachbau-Fehler nichts.
- Die übrigen Konto-Mechaniken aus V11 (Abschluss-Ernte 0,2/0,5 R, Reserve, Gewinn-Ernte, RSI21-Schutzzeit) habe ich
  nicht neu gerechnet; die Serien-Stopp-Varianten schon (4.2).

## 5. Kennzahlen V11 → V12 (Mittel über 16 Störungen)

| Fenster | Ausz./J V11 → V12 | $/J V11 → V12 | $/J inkl. offen | Ø Auszahlung | 1. Ausz. (Median, Tage) | ohne Ausz. | Busts |
|---|---|---|---|---|---|---|---|
| 2022 (Auswahl) | 12,13 → 13,09 | 2.336 → 2.542 | 2.314 → 2.529 | 248 → 250 $ | 16 → 16 | 0,0 → 0,0 % | 0 → 0 |
| 2023 | 13,14 → 14,48 | 2.558 → 2.768 | 2.533 → 2.750 | 251 → 246 $ | 22 → 21 | 0,0 → 0,0 % | 0 → 0 |
| 2024–25 | 7,86 → 7,62 | 1.693 → 1.653 | 1.563 → 1.501 | 278 → 279 $ | 15 → 15 | 0,0 → 0,2 % | 0 → 0 |
| 2017–20 | 5,49 → 5,69 | 1.018 → 1.082 | 898 → 966 | 239 → 245 $ | 30 → 30 | 0,7 → 1,1 % | 0 → 0 |
| 2011–15 (neu) | 3,72 → 3,71 | 684 → 684 | 506 → 503 | 237 → 237 $ | 27 → 27 | 13,7 → 13,8 % | 0 → 0 |

Je Startjahr:

| Start | Ausz./J V11 → V12 | $/J V11 → V12 | $/J inkl. offen | Ø Auszahlung | 1. Ausz. (Median, Tage) | ohne Ausz. | Busts |
|---|---|---|---|---|---|---|---|
| 2011 | 3,02 → 3,02 | 556 → 556 | 381 → 381 | 237 → 237 $ | 34 → 34 | 14,5 → 14,5 % | 0 → 0 |
| 2012 | 5,99 → 5,98 | 1.143 → 1.142 | 990 → 983 | 246 → 246 $ | 29 → 29 | 0,0 → 0,0 % | 0 → 0 |
| 2013 | 1,57 → 1,54 | 326 → 324 | 70 → 63 | 268 → 271 $ | 20 → 20 | 34,3 → 34,4 % | 0 → 0 |
| 2014 | 3,31 → 3,31 | 566 → 566 | 460 → 460 | 220 → 220 $ | 24 → 24 | 17,1 → 17,1 % | 0 → 0 |
| 2015 | 4,64 → 4,64 | 818 → 818 | 619 → 620 | 227 → 227 $ | 28 → 28 | 2,5 → 2,5 % | 0 → 0 |
| 2017 | 5,00 → 5,00 | 826 → 826 | 698 → 698 | 213 → 213 $ | 35 → 35 | 0,7 → 0,7 % | 0 → 0 |
| 2018 | 6,73 → 7,32 | 1.347 → 1.510 | 1.246 → 1.414 | 258 → 266 $ | 24 → 24 | 0,7 → 0,6 % | 0 → 0 |
| 2019 | 3,69 → 3,90 | 703 → 797 | 528 → 631 | 245 → 263 $ | 28 → 23 | 1,5 → 3,2 % | 0 → 0 |
| 2020 | 6,59 → 6,59 | 1.201 → 1.201 | 1.127 → 1.127 | 235 → 235 $ | 48 → 48 | 0,0 → 0,0 % | 0 → 0 |
| 2022 | 12,18 → 13,13 | 2.352 → 2.554 | 2.331 → 2.542 | 249 → 251 $ | 16 → 16 | 0,0 → 0,0 % | 0 → 0 |
| 2023 | 13,09 → 14,44 | 2.535 → 2.748 | 2.514 → 2.736 | 250 → 245 $ | 22 → 21 | 0,0 → 0,0 % | 0 → 0 |
| 2024 | 7,74 → 7,57 | 1.669 → 1.665 | 1.530 → 1.502 | 278 → 284 $ | 15 → 15 | 0,0 → 0,2 % | 0 → 0 |
| 2025* | 9,59 → 9,08 | 2.084 → 1.764 | 2.017 → 1.689 | 280 → 250 $ | 15 → 15 | 0,0 → 0,0 % | 0 → 0 |

\* 2025: nur 6 Starts (NAS-Daten enden 13.02.2026).

Sensitivität ohne Schlupf (16 Störungen, gepaart, Differenz V12 − V11):

| Fenster | V11 Ausz./J | V12 Ausz./J | Differenz | V11 $/J | V12 $/J | Differenz |
|---|---|---|---|---|---|---|
| 2022 | 14,39 | 14,72 | +0,33 ± 0,17 | 2.704 | 2.872 | +168 ± 54 |
| 2023 | 16,31 | 16,74 | +0,44 ± 0,17 | 3.274 | 3.332 | +58 ± 79 |
| 2024–25 | 9,91 | 9,53 | −0,38 ± 0,24 | 2.229 | 2.210 | −19 ± 59 |
| 2017–20 | 6,94 | 7,14 | +0,20 ± 0,02 | 1.351 | 1.409 | +58 ± 6 |
| 2011–15 | 4,76 | 4,77 | +0,00 ± 0,01 | 913 | 913 | +0 ± 2 |

Einordnung:
- **Ohne Schlupf ist der Vorteil kleiner** (2022 +0,33 statt +0,66, 2023 +0,44 statt +1,30). Ein Teil des Vorteils
  kommt also daher, dass der Tick-Einstieg zum festen Preis weniger unter dem Markt-Schlupf am M5-Open leidet. Wie
  groß der Schlupf bei GFT wirklich ist, kann nur der Tester (Echte Ticks) bzw. das Live-Konto zeigen.
- **2024–25 ist die Schwachstelle:** mit Schlupf −0,07 ± 0,17 (32 Störungen) bzw. −0,24 (Störungen 1–16), ohne
  Schlupf −0,38 ± 0,24 Ausz./J; beim Geld jeweils ±0. Keine dieser Zahlen ist vom Zufall zu unterscheiden, aber die
  Richtung ist überall leicht negativ. Das Startjahr 2025 (nur 6 Starts) zeigt 9,6 → 9,1 Ausz./J.
- Je Startjahr ist V12 besser 2018, 2019, 2022, 2023, gleich 2011–2017 und 2020 (dort sind die Fades meist nicht live,
  also handelt auch SRT1030 nicht), leicht schlechter 2024–25.

## 6. Einstellungen V12

| Eingabe | Voreinstellung | Wirkung |
|---|---|---|
| `V12TickN1030` | **true** | N1030 handelt als Tick-Fade `SRT1030` (Range 10:30–12:30, Fenster bis 13:30, Stop 0,3 × Range, Ziel Range-Mitte, Ausstieg 15:30 NY, Range ≤ 0,6 ATR, Durchbruch ab 0,6 ATR, nur bei live Portfolio-Wächter). Das M5-Modul N1030 rechnet nur virtuell (Wächter unverändert). Wird ignoriert, wenn `V11TickFades` an ist. |
| `V12TickN1030Risk` | **0,50** | Risiko je `SRT1030`-Trade in % vom Startsaldo (× Pufferkurve). Plateau 0,40–0,60; 0,75 mit Busts. |
| `V11TickFades`, `V11GoldPdf` | false | unverändert (Testschalter aus V11) |

- **Rückfall auf 11.00:** `V12TickN1030 = false` – dann ist jeder geänderte Codepfad identisch zu 11.00 (= 10.00).
  `DEADBAND_V11.mq5` liegt unverändert daneben.
- `SRT1030` ist ein Modul vom SR-Typ: Es handelt auch bei `SrAktiv = false` (der Schalter betrifft nur die vier
  SR-Marken). Die SR-Statuszeile zeigt dann „aus“, obwohl `SRT1030` aktiv ist.
- Modulzahl: 18 + 1 = 19 von `MAXFADE` 22.

## 7. Checkliste für den Tester

1. V12 im MetaEditor kompilieren. **NICHT KOMPILIERT ERSTELLT.** Statisch geprüft: ASCII, Klammerbilanz,
   389 Format-Strings gegen die Argumentzahl, Diff gegen V11 (7 Ersetzungen, `V11_V12.diff`). Reproduzierbar mit
   `python patch_v12.py ../DEADBAND_V11.mq5 ../DEADBAND_V12.mq5`.
2. Strategietester, Echte Ticks, NAS100.x + XAUUSD.x, 01.01.2024 bis heute:
   - a) `V12TickN1030 = false` muss V11 handelsgleich sein (gleiche Trades).
   - b) **V12 Voreinstellung gegen a)**: Im Journal „12.00 Tick-Fade SRT1030 AN“; Einstiege `SRT1030` mitten in
     der M5-Kerze, wenn der Kurs nach einem Docht unter das 10:30–12:30-Tief zurückkehrt; Ziel erst nach 130 s.
     Vergleiche Auszahlungen, $ und **Kleinster Abstand zum Boden** (OnTester). Erwartung aus dem Nachbau für 2024–25:
     etwa gleich (±0,2 Ausz./J), beim Geld leicht besser. Der eigentliche Vorteil zeigte sich 2022–23.
   - c) Wenn möglich zusätzlich 2022–2023 testen (dort +0,7 / +1,3 Ausz./J im Nachbau).
   - d) `SrAktiv` false gegen true (wie bisher offen) – der Nachbau sagt jetzt: SR hilft.
3. Einzelne Tester-Läufe schwanken um ±1 Ausz./J. Bitte mehrere Startdaten (z. B. 01.01., 01.04., 01.07.2024).
4. Unverändert: kein VPS, News-Fenster, 130-s-Regel, Hedging-Sperre, Budgets, Pufferkurve.

## 8. Grenzen

- **Fremddaten statt GFT-Feed** (NAS HistData mit Lücken und Rollsprüngen vor 2019; Gold Dukascopy bzw. OANDA mit
  Spread-Modell). Die GFT-M5-Daten fehlen weiter – bitte als ZIPs < 10 MB (z. B. je Jahr) in den Drive legen.
- **Tick-Einstieg nur auf M1 geschätzt** (pessimistisch: Rückkehr in der Docht-Minute nur, wenn deren Schluss schon
  zurück ist; Ziel erst ab der 4. Minute). Echte Ticks können besser oder schlechter sein – deshalb Tester-Punkt 2b.
- 2024–25 ist das kürzeste Fenster (59 Konten) und das empfindlichste; dort ist V12 gleich, nicht besser, mit leicht
  negativer Tendenz (ohne Schlupf −0,38 ± 0,24).
- Der Vorteil von V12 hängt teilweise am Schlupf-Modell (¼ Spread auf Markt-Einstiege): ohne Schlupf etwa halb so groß.
- Das Fenster 2011–15 nutzt Gold von OANDA (Mid) und NAS-Daten mit Rollsprüngen (Verfallstage ausgeschlossen).
- Nicht nachgebildet: News-Sperre, Kontoerkenner/Anpasser (neutral), Peak-Unsicherheit, Margin nur grob (1:20).
- Rund 290 geprüfte Varianten; bestanden hat eine (mit Plateau und Gegenprobe). Die V12-Zahlen sind eher etwas zu
  optimistisch als zu pessimistisch.

## 9. Dateien (Repo `agattermann007-droid/claude`, Branch `claude/deadband-v11`, Ordner `DEADBAND/V12/`)

| Datei | Inhalt |
|---|---|
| `DEADBAND_V12.mq5` | Build 12.00 (nicht kompiliert) |
| `DEADBAND_V12_Bericht.md` | dieser Bericht |
| `build/` | `patch_v12.py` (7 exakte Ersetzungen), `patch_lib.py`, `kopf_v12.py`/`.txt`, `check_mq5.py`, `V11_V12.diff` |
| `Replikat_v12/` | Nachbau v12 mit README (Korrekturen, erweiterter Datensatz, neue Skripte), alle Versuche `t12_*.py`, Ausgaben in `ergebnisse/` (alte, fehlerhafte Läufe in `ergebnisse/alt_vor_fix/`) |
| `PROMPT_DEADBAND_V13.md` | Prompt für die nächste Sitzung |
