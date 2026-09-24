# DEADBAND LIVE 4 – Build 5.10 KOMBI

Bericht vom 24.09.2026 · GFT Instant Premium 10k (Konto ab 02.09.2026)

## 1. Kurzfassung

Build 5.10 behält alle Signale der drei Module aus 5.00 (DEADBAND-Ausbruch, RSI21, NAS-Noise). Geändert
haben sich der Schutz gegen GFT-Regelbrüche, das Realisieren von Gewinnen und eine Pause nach Verlustserien.
Ziel war: mehr und regelmäßigere, dafür kleinere Auszahlungen, weit weniger Busts, kürzere Verlustserien.
Netto je Jahr war zweitrangig.

Replikat auf den M5-Kursen des GFT-Terminals (03.01.2022–02.09.2026). Alle drei Handelstage startet ein
neues 10k-Konto, Laufzeit 1, 2 und 3 Jahre. Gemittelt wird über 16 Störungen (8 % der Signale ausgelassen,
Einstiegsschlupf), die GFT-Regeln gelten in der strengen Lesart:

| Kennzahl | 5.00 | 5.10 |
|---|---:|---:|
| Auszahlungen je Jahr | 7,06 | **7,96** |
| Busts je Jahr | 1,05 ¹ | **0,05** |
| Konten mit Bust im 1. / 2. / 3. Jahr | 70 % / 95 % / 100 % | **4 % / 10 % / 16 %** |
| Auszahlung im Mittel (brutto, vor 80 % und 3 %) | 378 $ | 256 $ |
| Netto je Jahr (Anteil nach Gebühr − Neukäufe à 148,50 $) | 1911 $ | 1571 $ |
| Serien ≥ 5 Verlusttrades je Jahr | 15,6 | **11,1** |
| Serien ≥ 8 Verlusttrades je Jahr | 3,3 | **1,6** |
| längste Verlustserie (Mittel je Konto) | 11,5 Trades | **9,5 Trades** |
| Verlust der schlimmsten Serie (Mittel) | −365 $ | −277 $ |
| größter Saldo-Rückgang im Zyklus (Mittel) | 550 $ | 476 $ |
| Trefferquote (Noise-Signal = 1 Trade) | 41,8 % | 45,0 % |
| Pfad ab 03.01.2022: Auszahlungen / Busts / Netto | 34,8 / 3,8 / 9494 $ | 37,3 / 0,1 / 7247 $ |

¹ Die 1,05 gelten nur, wenn GFT die −1-%-Floating-Regel **netto** misst (Gewinner verrechnet mit Verlierern).
Zählt GFT nur die Verlustpositionen, hätte 5.00 im Replikat **3,59 Busts je Jahr** (98 % der Konten im ersten
Jahr). Die Bremse von 5.00 schaut auf den Nettowert, und ein Gewinner kann dann einen Verlierer über −1 %
verdecken. 5.10 hat unter beiden Lesarten dieselben Werte (0,05).

Streuung über die 16 Störungen (Standardfehler): 5.10 Auszahlungen 7,93 ± 0,13, Busts 0,050 ± 0,022;
5.00 7,04 ± 0,08 bzw. 1,06 ± 0,05. Die Verbesserungen liegen weit über dem Rauschen. Achtung: 5.10 liegt am
günstigen Rand der geprüften Nachbarn (Abschnitt 4.5). Realistisch sind eher **0,1–0,2 Busts je Jahr**.

Der EA wurde hier **nicht kompiliert und nicht im MT5-Tester geprüft**. Das ist vor dem Echtbetrieb Pflicht
(Abschnitt 7).

## 2. Was 5.10 ändert

### A) GFT-Regelschutz (strenge Lesart)

| Nr | Änderung | Eingabe (5.10) | Zweck |
|---|---|---|---|
| 1 | Floating-Bremse (−0,8 %) und Notbremse (−1,0 %) auf die **Summe der Verlustpositionen** inkl. Swap und Einstiegskommission; Gewinner verrechnen nicht | `FloatNurVerlierer=true` | Die −1-%-Regel ist ein harter Bruch. In der strengen Lesart verdeckt ein Gewinner keinen Verlierer. |
| 2 | **Swap-Vorsorge**: in den 10 Minuten vor dem Rollover (Mitternacht Serverzeit = 17:00 NY) Verlierer plus erwarteter Swap (am Swap-3-Tag dreifach) ≤ −0,8 % → größte Verlierer vorher schließen | `SwapVorsorgePct=0.80`, `SwapVorsorgeMin=10` | Der Swap wird in einem Schritt gebucht, oft in der Tagespause. Keine Bremse kann dann noch dazwischen greifen. |
| 3 | **Risiko je Handelsidee** (Symbol + Richtung, alle Module und Plätze) höchstens 1,25 % vom Startsaldo | `IdeeMaxRisikoPct=1.25` | DEADBAND, RSI21 und Noise können gleichzeitig NAS long sein. GFT kann ein Höchstrisiko je Idee vorschreiben (1 %) → dann `1.0` einstellen. |
| 4 | Tagesregel-Notbremse auf 3 % von **min(Startsaldo, Tagesreferenz)** | – | vorsichtige Lesart der Bezugsgröße |
| 5 | Teilverkauf bei 1,5 R und Abschluss-Ernte erst nach **130 s** Haltedauer und außerhalb des News-Fensters | `MinHalteSek=130` (wie 4.90) | Gewinne aus Trades unter 120 s streicht GFT. |
| 6 | **Start nur auf dem eigenen PC**: der Terminal-Datenpfad muss einen Text enthalten, z. B. den Windows-Benutzernamen | `NurAufPcPfad=""` (bitte setzen) | Seit 12.08.2026 ist VPS verboten. `VpsSperre` erkennt nur den MetaQuotes-VPS, nicht einen gemieteten Server. |

### B) Auszahlungstakt und Serienschutz

| Nr | Änderung | Eingabe 5.00 → 5.10 | Zweck |
|---|---|---|---|
| 7 | DEADBAND: **50 % bei 1,5 R realisieren**, Stop auf +0,05 R | `Tp1R` 2,0 → 1,5 · `Tp1F` 0 → 0,50 · `BeAfterT1R` 0,30 → 0,05 | weniger zurückgegebener Buchgewinn (Abschnitt 5), mehr kleine Gewinner |
| 8 | **Abschluss-Ernte**: fehlen nur noch ≤ 2 gültige Tage (Saldo ≥ Startsaldo), wird DEADBAND-Gewinn (bester Kurs ≥ 0,5 R) jederzeit so weit realisiert, dass der Tag gültig wird | `AbschlussLetzte=2`, `AbschlussMinR=0.5`, Fenster 0–17 NY | Engpass sind die gültigen Tage. So schließen die Zyklen schneller. |
| 9 | Gewinn-Ernte ohne Rückgang-Bedingung (fehlt nur noch der Mindestgewinn, wird realisiert) | `GeRueckgangR` 1,25 → 0 | Zyklen enden pünktlicher (1,1 → 5,7 Ernten je Jahr). |
| 10 | **Serien-Stopp**: nach 4 Verlusttrades in Folge keine neuen Einstiege bis 17:00 NY. Alle Module zählen, die Noise-Teile eines Signals gelten als ein Trade. Berechnet aus der Deal-Historie, gilt also auch nach einem Neustart. | `SerienStopp=4`, `SerienPauseTage=0` | Lange Serien brechen ab. Auf dem Pfad ab 2022 greift der Stopp etwa 22-mal je Jahr. |
| 11 | Risiko umgeschichtet: RSI21 0,70 → **0,63 %**, Noise 0,30 → **0,45 %** je Signal | `R21RiskPct`, `NzRiskPct` | gleichmäßigere Tagesergebnisse; Noise ist intraday und hält nie über Nacht |

Unverändert: alle Signale, Filter, Stops, Ziele, DEADBAND-Größe (`RiskMult` 0,9), Budgets (0,8 / 1,2 / 2,0 %),
Puffer-Kurve, Wochenend-Pause, Hedging-, News- und Margin-Regeln aus 4.90/5.00.

## 3. GFT-Regeln: so hält 5.10 sie ein

Stand der Regeln: GFT-Help-Center, geprüft am 21.–24.09.2026. GFT kann die Regeln ändern.

| Regel (Instant Premium) | Umsetzung im EA | Hinweis |
|---|---|---|
| Trailender Maximalverlust 6 % (vom Equity-Hoch; Help-Center-Text: Tagesschluss-Hoch × 0,94) | Boden aus Equity-Spitze inkl. Buchgewinn (strenger als EOD), Puffer-Kurve (Größe ×1,0 ab 4 % Puffer bis ×0,6 bei 1,5 %), unter Startsaldo ×0,8, Teilverkauf 1,5 R | kein eigener Not-Exit am Boden; Schutz über Stops, Budgets und Größe. Beide Boden-Lesarten geprüft (Abschnitt 4.1) |
| Floating-Verlust −1 % (Konten ab 02.09.2026) = harter Bruch | Bremse −0,8 % auf die Summe der Verlierer inkl. Swap und Kommission (gestuft: größter Verlierer zuerst), Notbremse −1,0 %, Basis min(Startsaldo, Saldo), Swap-Vorsorge | **neu in 5.10**: strenge Lesart und Swap-Vorsorge |
| Tagesverlust 3 % | Tagesstopp 2,4 % vom Startsaldo (schließen, keine Einstiege), Notbremse 3 % auf min(Startsaldo, Tagesreferenz), Tagesreferenz = max(Saldo, Equity) um 17:00 NY | |
| Auszahlung: 5 gültige Tage ≥ 0,5 % (50 $), 10 Tage Zyklus, Mindestauszahlung 100 $, 80 %, 3 % Gebühr, Deckel 6 % für die ersten 2 Auszahlungen, Konto flach | Mindestgewinn 131,25 $ (105 $ Anteil wegen Gebühr), Reife-Modus (keine Einstiege, RSI21/Noise schließen), Push „Auszahlung beantragen“, sobald flach | den vollen Gewinn anfordern; der EA erkennt den Saldo-Deal |
| Gewinne aus Trades < 120 s werden gestrichen | eigene Gewinnschließungen erst ab 130 s: Zeit-Exit, Ernten, **Teilverkauf 1,5 R**, **Abschluss-Ernte** | Server-Ziele liegen mehrere ATR entfernt; ein Treffer unter 120 s ist sehr unwahrscheinlich |
| News (±5 min um rote Termine) | ±6 min: keine Einstiege, keine eigenen Gewinnschließungen > 1 % (MT5-Kalender, nur live) | Server-Stop oder -Ziel kann im Fenster ausgelöst werden (siehe 6) |
| Hedging verboten, **auch über eigene Konten** | Hedging-Sperre im Konto (auch vorgemerkte Wiederaufnahmen und Orders der letzten 10 s) | **kontoübergreifend kann der EA nichts prüfen** (siehe 6) |
| Martingale/Grid (Größe nach Verlust erhöhen) | nie: Größe sinkt mit dem Puffer, Serien-Stopp pausiert | |
| Gambling (Margin > 80 %) | Margin je Idee ≤ 70 % der Equity, neue Order ≤ 80 % der freien Margin | |
| Risiko je Idee (GFT kann 1 % vorschreiben) | `IdeeMaxRisikoPct` 1,25 %; bei Vorgabe 1,0 % → Replikat 7,58 Ausz / 0,11 Busts / 1419 $ | **neu in 5.10** |
| Hebel 1:10 | Margin über `OrderCalcMargin` des Servers | |
| VPS verboten (Kauf ab 12.08.2026) | `VpsSperre` (MetaQuotes-VPS) + **`NurAufPcPfad`** | Heim-PC, der durchläuft (Energiesparen aus) |
| 30 Tage ohne Trade = Konto weg | Push ab 20 Tagen ohne Einstieg | |
| keine Konsistenzregel | – | |

## 4. Ergebnisse im Detail (Replikat)

### 4.1 Regel-Lesarten und Boden-Varianten

Mittel über 1/2/3 Jahre, 16 Störungen. „P(Bust) 1 J“ = Anteil der 1-Jahres-Konten mit mindestens einem Bust.

| Variante | Ausz/J | Busts/J | Netto/J | $/Ausz | Serien ≥ 5/J | ≥ 8/J | P(Bust) 1 J |
|---|---:|---:|---:|---:|---:|---:|---:|
| 5.00 wie ist, GFT misst netto | 7,06 | 1,05 | 1911 | 378 | 15,6 | 3,32 | 70 % |
| 5.00 wie ist, GFT zählt nur Verlierer | 6,74 | 3,59 | 1455 | 380 | 15,2 | 3,38 | 98 % |
| 5.00 nur mit Regelschutz (1 + 2) | 7,05 | 0,91 | 1843 | 362 | 15,5 | 3,34 | 63 % |
| **5.10** (beide Floating-Lesarten gleich) | **7,96** | **0,05** | 1571 | 256 | 11,1 | 1,57 | **4 %** |
| 5.00 wie ist, Boden = Tagesschluss-Hoch × 0,94 | 6,55 | 0,54 | 1749 | 360 | 15,8 | 3,43 | 41 % |
| 5.10, Boden = Tagesschluss-Hoch × 0,94 | 8,00 | 0,07 | 1591 | 258 | 11,1 | 1,63 | 4 % |

### 4.2 Nach Startjahr (1-Jahres-Konten)

5.00 in der milden Lesart (netto), 5.10 in der strengen. Ausz/J · Busts/J · Netto/J:

| Start | 5.00 | 5.10 |
|---|---|---|
| 2022 | 7,39 · 1,32 · 1923 $ | 9,59 · 0,01 · 2053 $ |
| 2023 | 7,11 · 1,49 · 2016 $ | 7,31 · 0,08 · 1449 $ |
| 2024 | 6,24 · 0,76 · 1657 $ | 6,94 · 0,06 · 1346 $ |
| 2025 | 8,58 · 0,11 · 2339 $ | 9,69 · 0,00 · 1934 $ |

In jedem Startjahr gibt es mehr Auszahlungen und weit weniger Busts. Netto liegt 5.10 in drei von vier Jahren
tiefer (kleinere Auszahlungen), 2022 höher (Busts vermieden).

### 4.3 Ein Konto ab 03.01.2022 bis 02.09.2026 (16 Störungen)

| | Auszahlungen | Busts | Netto |
|---|---|---|---|
| 5.00 | 34,8 (31–37) | 3,8 (3–6) | 9494 $ |
| 5.10 | 37,3 (32–42) | 0,1 (0–1) | 7247 $ |

### 4.4 Module (je Jahr)

| | DEADBAND | RSI21 | Noise |
|---|---:|---:|---:|
| Ergebnis 5.00 → 5.10 | 709 → 646 $ | 1201 → 932 $ | 374 → 428 $ |
| Trefferquote 5.00 → 5.10 | 37,8 → 43,1 % | 49,6 → 49,4 % | – |

Ernten je Jahr: Tagesernte 29,6 → 18,6, Gewinn-Ernte 1,1 → 5,7, Abschluss-Ernte 0 → 19,2.

### 4.5 Nachbarschaft (ist 5.10 ein Zufallstreffer?)

Varianten rund um 5.10, gleiche Bewertung (16 Störungen, strenge Lesart):

| Variante | Ausz/J | Busts/J | Netto/J | Serien ≥ 8/J |
|---|---:|---:|---:|---:|
| **5.10** | 7,96 | 0,05 | 1571 | 1,57 |
| ohne Idee-Grenze | 7,85 | 0,09 | 1630 | 1,66 |
| Idee-Grenze 1,0 % | 7,58 | 0,11 | 1419 | 1,60 |
| Teilverkauf bei 1,75 R (ohne Idee-Grenze) | 7,86 | 0,16 | 1572 | 1,96 |
| Abschluss-Ernte ab 3 fehlenden Tagen (ohne Idee-Grenze) | 7,96 | 0,08 | 1608 | 1,67 |
| Serien-Stopp nach 5 (ohne Idee-Grenze) | 7,87 | 0,13 | 1635 | 1,47 |
| Noise 0,50 % (ohne Idee-Grenze) | 7,82 | 0,15 | 1659 | 1,62 |
| Stop nach Teilverkauf +0,10 R, RSI21 0,70 % | 7,99 | 0,20 | 1628 | 1,67 |
| … und Teilverkauf bei 1,25 R | 7,79 | 0,36 | 1557 | 1,44 |
| … und Serien-Stopp nach 3 | 7,50 | 0,24 | 1543 | 1,21 |
| … und DEADBAND-Größe ×1,1 | 7,98 | 0,50 | 1629 | 1,52 |

Alle Nachbarn liefern 7,5–8,4 Auszahlungen und 0,05–0,5 Busts je Jahr, gegenüber 5.00 mit 7,06 und 1,05
(streng: 3,59). Das Ergebnis ist also ein Plateau und kein Einzeltreffer. 5.10 liegt aber an dessen günstigem
Rand, weil aus rund 270 geprüften Varianten die beste gewählt wurde. Erwartung für den Echtbetrieb: **rund 7,5–8
Auszahlungen und 0,1–0,2 Busts je Jahr**. Die DEADBAND-Größe ist der empfindlichste Hebel; `RiskMult` nicht
erhöhen.

## 5. Warum es wirkt

- **Busts sind fast alle Boden-Busts.** Der trailende Boden folgt dem Equity-Hoch einschließlich
  Buchgewinn. DEADBAND-Läufer (Ziel 8–10 R) geben oft viel Buchgewinn zurück. Der Boden ist dann schon
  nachgezogen, der Saldo aber nicht gestiegen, und der Puffer schrumpft ohne Gewinn. Der Teilverkauf von
  50 % bei 1,5 R mit Stop auf +0,05 R sichert die Hälfte und macht den Rest risikolos. In einer Zwischenrunde
  senkte er die Busts allein von 0,88 auf 0,10 je Jahr.
- **Engpass der Auszahlungen sind die gültigen Tage.** In rund 60 % der Zyklen wartet die Auszahlung
  zuletzt auf gültige Tage, in rund 37 % auf den Mindestgewinn, kaum je auf die 10-Tage-Frist.
  Abschluss-Ernte und Gewinn-Ernte ohne Rückgang-Bedingung schließen fast fertige Zyklen schneller. Weniger
  Busts bedeuten außerdem, dass weniger angefangene Zyklen verloren gehen.
- **Kürzere Serien** kommen vom Teilverkauf (mehr kleine Gewinner, DEADBAND-Trefferquote 38 → 43 %) und vom
  Serien-Stopp nach 4 Verlusten.
- **Preis:** Die Auszahlungen werden kleiner (378 → 256 $ brutto), Netto je Jahr sinkt um rund 18 %.

## 6. Grenzen, offene Punkte, Risiken

1. **Nicht kompiliert, nicht im Tester geprüft.** Die Änderungen sind eng an vorhandene, erprobte Stellen
   angelehnt (Tagesernte, gestufte Bremse). Trotzdem sind Tippfehler oder unbedachte Grenzfälle möglich.
2. **Replikat statt Tick-Test.** Es hat 4,7 Jahre M5-Daten, darin ein NAS-Datenloch 2024. Die Reihenfolge
   innerhalb einer M5-Kerze ist angenommen. News-Sperre und 130-s-Regel sind nicht abgebildet. Absolute Zahlen
   sind Schätzungen; belastbar ist der Vergleich 5.00 ↔ 5.10 unter gleichen Annahmen.
3. **Regel-Lesarten.** 5.10 nimmt überall die strengere Lesart: Verlierer-Summe inkl. Swap und Kommission,
   Boden inkl. Buchgewinn, 3 % auf die kleinere Basis. Ist GFT milder, kostet das nur wenig Ertrag.
4. **Hedging über eigene Konten.** GFT verbietet Gegenpositionen auch zwischen mehreren eigenen Konten.
   Handelt ein anderes eigenes Konto zur selben Zeit NAS100 oder XAUUSD in die Gegenrichtung (z. B. das
   NLF-25k-Konto mit NAS100), kann das als Hedging gewertet werden. Der EA sieht nur sein eigenes Konto.
5. **Mehrere GFT-Konten mit demselben EA** können als Copy- oder Gruppenhandel gelten. Vorher beim Support
   klären.
6. **News:** Server-Stops und -Ziele können im News-Fenster auslösen. Der EA verhindert nur eigene Einstiege
   und Gewinnschließungen. Ein Ziel über 1 % im Fenster könnte GFT kappen.
7. **Öffentliches Repository.** Das GitHub-Repository ist öffentlich: Strategie und Einstellungen sind für
   jeden sichtbar. Empfehlung: auf „Private“ stellen.

## 7. Inbetriebnahme

1. `DEADBAND_LIVE4.mq5` nach `MQL5/Experts/` kopieren und in MetaEditor kompilieren. Erwartet: 0 Fehler.
   Warnungen prüfen.
2. Strategietester: „Jeder Tick anhand realer Ticks“, XAUUSD.x, 2024–2026, Preset
   `DEADBAND_LIVE4_Echtbetrieb.set`. Im Journal prüfen:
   - Teilverkauf bei 1,5 R (halbe Lots) und Stop auf +0,05 R,
   - `ABSCHLUSS-ERNTE`, `SERIEN-STOPP`, `SWAP-VORSORGE` (kurz vor Mitternacht Serverzeit),
   - keine Fehlermeldungen beim Schließen.

   Danach 5.00 und 5.10 im Tester vergleichen: Auszahlungsreife, Busts und Serien sollten sich wie in
   Abschnitt 4 bewegen.
3. Live nur auf dem **eigenen PC** (kein VPS, kein Mietserver). Beim ersten Start steht im Journal
   `Terminal-Datenpfad ...`. Einen eindeutigen Teil davon (z. B. den Windows-Benutzernamen) in
   `NurAufPcPfad` eintragen.
4. Umstellen am besten, wenn das Konto **flach** ist (Wochenende). Der EA rekonstruiert Zyklus, gültige Tage,
   Boden und Serien-Stand aus der Historie.
5. Verlangt GFT ein Risiko je Idee von höchstens 1 %: `IdeeMaxRisikoPct=1.0`.
6. `RiskMult` nicht erhöhen: Mit DEADBAND ×1,1 stiegen die Busts im Replikat von 0,20 auf 0,50 je Jahr.

## 8. Zurück auf 5.00

`rollback_5.00/DEADBAND_LIVE4.mq5` mit `rollback_5.00/DEADBAND_LIVE4_Echtbetrieb.set`.

Nur den Regelschutz behalten, ohne die Handelsänderungen (Replikat 7,05 / 0,91 / 1843 $): im 5.10-Preset
`Tp1R=2.0`, `Tp1F=0.00`, `BeAfterT1R=0.30`, `GeRueckgangR=1.25`, `R21RiskPct=0.70`, `NzRiskPct=0.30`,
`AbschlussLetzte=0`, `SerienStopp=0`, `IdeeMaxRisikoPct=0` setzen.

## Anhang: Replikat

Code, Anleitung und Ergebnisdateien: `Replikat_v5/` (ohne Kursdaten). Schlussvergleich: `Replikat_v5/final.py`,
Streuung: `Replikat_v5/streuung.py`.
