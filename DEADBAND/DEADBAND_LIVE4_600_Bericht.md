# DEADBAND LIVE 4 – Build 6.00 FADE

Bericht vom 24.09.2026 · GFT Instant Premium 10k (Konto ab 02.09.2026)

## 1. Kurzfassung

Auftrag: mehr Ertrag, jede Auszahlung mindestens 3 % (Wunsch 4 %) der Kontogröße, dabei nicht mehr Busts,
10 Auszahlungen im Jahr, keine Verlustserie über 5 und die GFT-Regeln mit absoluter Sicherheit einhalten.
Gesucht wurde in jede Richtung: Web- und YouTube-Recherche, Studien, eigene Scans über tausende Varianten,
Gegenproben auf Kursdaten von 2006 bis 2021 und Abschalt-Tests der alten Module.

Das Ergebnis ist **Build 6.00** mit einem neuen Modul-Typ: **Fehlausbruch-Fades**. Eine Sitzungs-Range wird
kurz über- oder unterschritten, die Kerze schließt aber wieder innen. Dann handelt der EA zurück zur
Range-Mitte bzw. zur Gegenseite. Zehn solche Module (6 × NAS100, 4 × Gold) haben im Replikat 57–78 %
Trefferquote. Ein **Regime-Wächter** je Modul lässt es nur handeln, solange seine letzten 30 Signale
(virtuell mitgerechnet) einen Profitfaktor über 1,2 haben. Der **DEADBAND-Ausbruch ist aus**: Er erzeugte
die langen Verlustserien und vertrug sich nicht mit den Fades (Abschnitt 2.4).

Replikat auf den M5-Kursen des GFT-Terminals (03.01.2022–02.09.2026): alle drei Handelstage ein neues
10k-Konto, Laufzeit 1, 2 und 3 Jahre, 16 Störungen (8 % der Signale ausgelassen, Einstiegsschlupf),
strenge Regel-Lesart. Alle drei Varianten zahlen erst ab 3 % Gewinn (300 $) aus:

| Kennzahl | 5.10 (Ausz. ab 3 %) | **6.00 Sicher** | **6.00 Ertrag** (Echtbetrieb-Set) |
|---|---:|---:|---:|
| Auszahlungen je Jahr | 5,51 | **6,08** | **7,46** |
| Auszahlung im Mittel (brutto) | 361 $ | 350 $ | 388 $ |
| kleinste Auszahlung | 300 $ | 300 $ | 300 $ |
| Busts je Jahr | 0,17 | **0,00** | **0,02** |
| Konten mit Bust im 1. Jahr | 13,7 % | **0 %** | **2,1 %** |
| Netto je Jahr (80 % Anteil, 3 % Gebühr, Neukäufe) | 1517 $ | 1653 $ | **2243 $** |
| Serien ≥ 5 Verluste je Jahr | 11,8 | **0,65** | 2,26 |
| Serien ≥ 6 Verluste je Jahr | 6,15 | **0,04** | 0,62 |
| längste Serie: Mittel je Konto / schlimmste | 9,4 / 13 | **4,8 / 7** | 6,0 / 11 |
| Trades je Jahr / Trefferquote | 424 / 45 % | 216 / 68 % | 315 / 61 % |

Gegenüber 5.10 mit derselben 3-%-Schwelle bringt „Ertrag“ **+35 % Auszahlungen, +48 % Netto, 90 % weniger
Busts und 80 % weniger lange Serien**. „Sicher“ hat im Replikat keinen einzigen Bust und fast nie mehr als
5 Verluste in Folge, verdient aber weniger.

**Anforderungen – ehrlich bewertet:**

| Anforderung | Sicher | Ertrag | Bewertung |
|---|---|---|---|
| Auszahlung ≥ 3 % | ja (Minimum 300 $) | ja (Minimum 300 $) | erfüllt (`MinProfitPct=3`) |
| 10 Auszahlungen je Jahr | 6,1 | 7,5 (Startjahr 2022: 9,7) | **nicht erfüllt** |
| keine Busts | 0,00 | 0,02 | im Replikat erfüllt bzw. fast |
| keine Serie über 5 | Mittel 4,8, schlimmste 7 | Mittel 6,0, schlimmste 11 | **nur „Sicher“ annähernd** |
| mehr Ertrag, nicht mehr Busts | +9 % Netto, Busts 0 | +48 % Netto, Busts −90 % | erfüllt |
| GFT-Regeln mit absoluter Sicherheit | | | so weit ein EA es kann (Abschnitt 5); absolut geht nicht |

Alle Ziele **zugleich** erreicht keine geprüfte Variante robust. Die Rechnung dazu (Abschnitt 2.1):
10 × 3 % ohne Bust und mit kurzen Serien verlangt eine Kante, wie sie öffentlich nirgends belegt ist
(≈ 70 % Treffer bei Chance/Risiko 1 nach Kosten, Jahres-Sharpe 4–5). Die einzige Mischung mit knapp
10 Auszahlungen (Fades plus Noise v2 **ohne** Wächter: 9,6 je Jahr, 0 Busts auf 2022–26) hätte auf den
Kursen von 2006–2021 **3,2 Busts je Jahr**. Sie ist deshalb verworfen.

**Die wichtigste Einschränkung:** Die Fades verdienen auf 2022–2026 in beiden Hälften (In- und
Out-of-Sample), aber **nicht** auf 2006–2021. Der Vorteil hängt vom heutigen Marktregime ab. Kippt es,
schaltet der Wächter die Module ab, aber erst nach einigen Verlusten (Abschnitt 6.3).

Der EA wurde hier **nicht kompiliert und nicht im MT5-Tester geprüft**. Ein Gegenleser (Sub-Agent) hat den
neuen Code geprüft (Abschnitt 7). Kompilieren und Tester sind vor dem Echtbetrieb Pflicht (Abschnitt 8).

## 2. Was gesucht und geprüft wurde

### 2.1 Machbarkeit: was 10 × 3 % verlangt

Jeder Auszahlungszyklus ist ein Rennen: +3 % erreichen, bevor ein Rückgang von 6 % vom Hoch kommt. Dazu
müssen 5 gültige Tage à ≥ 0,5 % realisiert sein, der Zyklus dauert mindestens 10 Tage, und die −1-%-
Floating-Regel begrenzt das Risiko je Trade auf rund 0,75 %. Monte-Carlo-Rechnung mit allen GFT-Regeln:

- 10 Auszahlungen à ≥ 3 % bei ≤ 2 % Bust-Wahrscheinlichkeit brauchen eine Jahres-Sharpe der Trade-Reihe
  von ≈ 4,2–5. 5.10 liegt bei ≈ 2,45 (Faktor 3 zu tief). Keine Größen- oder Auszahlungsregel schließt die
  Lücke.
- Verlustserien ≤ 5 bei 200–400 Trades je Jahr brauchen ≈ 70 % Trefferquote. Bei 55 % Treffern und
  200 Trades tritt mit 60 % Wahrscheinlichkeit mindestens eine Serie ≥ 6 auf.
- Alle Ziele zugleich: ≈ 70 % Treffer bei Chance/Risiko ≈ 1 nach Kosten (Profitfaktor ≈ 2,3), 175–190
  Trades je Jahr.

5.10 selbst mit höherer Schwelle (Replikat): ab 3 % → 5,51 Auszahlungen à 361 $, ab 4 % → 4,40 à 452 $.
Eine höhere Schwelle allein kostet Auszahlungen und bringt kein Netto.

### 2.2 Recherche (Web, YouTube, Studien)

Drei Recherche-Agenten, je einer für Gold, NAS100 und Risiko/Auszahlung, dazu die GFT-Regeln:

- **Keine öffentlich belegte Intraday-Strategie** für Gold oder Nasdaq verbindet ≥ 70 % Trefferquote mit
  positivem Erwartungswert nach Kosten. „75–93 % Trefferquote“ in Blogs und Videos sind fast immer
  Berührungsquoten ohne Stop oder Ziel ≪ Stop. Nachgerechnet: Berührungsquoten stimmen, der Erwartungswert
  mit Stop und Kosten ist negativ (Gap-Fill, „Magic Hour“, Weekly Open).
- ICT Silver Bullet und SMC: 0 von 162 Einstellungen positiv (unabhängiger Test, XAUUSD 2020–2026).
- Opening-Range-Breakout und Noise-Area-Momentum sind belegt, haben seit 2023–2025 aber deutlich an Stärke
  verloren (Sharpe außerhalb der Stichprobe ≈ 0–0,4).
- RSI(2)-Rückkehr (Connors) hat 74–80 % Treffer, hält aber über Nacht mit −3,4 % Buchverlust im
  90-%-Perzentil: mit der −1-%-Floating-Regel nicht regelkonform.
- Stärkste Risikoregel: Größe proportional zum Puffer bis zum Boden (Grossman/Zhou 1993). Der EA hat sie
  seit 4.x (Pufferkurve).

### 2.3 Eigene Scans

Ein Scanner prüfte vier Familien auf beiden Symbolen und in beiden Richtungen: Range-Ausbruch, Fehlausbruch-
Fade, Tageszeit-Momentum und Sweep von Vortages- bzw. Asia-Niveaus. Ausgewählt wurde nur, was **vor und nach
dem 01.07.2024** (In-/Out-of-Sample) gut war und auch mit benachbarten Parametern trägt. Danach dieselben
Raster auf Fremddaten 2006–2021 (Gold ab 2006, NAS100 ab 2005; Zeitabgleich mit den GFT-Daten geprüft,
Korrelation 0,99 bzw. 0,96).

- **Fehlausbruch-Fades** bestimmter Sitzungs-Ranges: robust auf 2022–26, hohe Trefferquote. Aus den
  stabilen Clustern wurden die 10 Module gewählt (jeweils zentrale, nicht beste Parameter).
- Ausbruch, Momentum, Sweep: keine Variante trägt über alle vier Epochen (2006–13, 2014–21, 2022–24H1,
  2024H2–26).
- Rollende Fades (mehrere Signale je Tag, beliebige Range): keine Variante besteht.
- Früher Break-even oder Teilgewinn für DEADBAND und RSI21: hebt die Trefferquote, zerstört aber den
  Erwartungswert (DEADBAND lebt von wenigen Läufern).
- Fades mit mehr als 0,75 % Risiko: schlechter, weil die Floating-Bremse bei −0,8 % dann Verlierer vor dem
  Stop schließt.

### 2.4 Beißen sich die Bestätigungen? (Abschalt-Tests)

Die Frage war: Läuft ein neuer Ansatz **ohne** einen alten besser? Replikat GFT 2022–26, Auszahlung ab 3 %:

| Variante | Ausz./J | Busts/J | Netto/J | Serien ≥ 5 /J | Trades/J |
|---|---:|---:|---:|---:|---:|
| 5.10 (DEADBAND + RSI21 + Noise) | 5,51 | 0,17 | 1517 $ | 11,8 | 424 |
| 5.10 ohne DEADBAND | 3,69 | 0,03 | 1196 $ | 2,0 | 124 |
| 5.10 + 10 Fades (Budget 0,9 %) | 8,06 | **0,41** | 2248 $ | 8,7 | 579 |
| 10 Fades allein (bewacht) | 6,46 | 0,00 | 1758 $ | 0,8 | 226 |
| 10 Fades + RSI21 + Noise, **ohne DEADBAND** | 7,71 | 0,06 | 2394 $ | 2,6 | 325 |
| dasselbe, RSI21 0,50 %, Noise 0,35 %, Serien-Stopp 3 (= Ertrag) | 7,46 | 0,02 | 2243 $ | 2,3 | 315 |

Zeilen 2–5: Einzelversuche mit 8 Störungen und 3 % ausgelassenen Signalen. Zeilen 1 und 6: Endbewertung
mit 16 Störungen und 8 % ausgelassenen Signalen. Die Einzelversuche liegen dadurch etwas höher
(„10 Fades allein“ in der Endbewertung: 6,08 statt 6,46).

- **DEADBAND ist der Störfaktor.** Ohne ihn fallen die Serien ≥ 5 von 11,8 auf 2,0 je Jahr. Er bringt
  Auszahlungen, aber mit ~300 Trades je Jahr bei 43 % Treffern und auf 2006–21 ohne Gewinn.
- **Fades plus DEADBAND** haben mehr als doppelt so viele Busts wie 5.10 (0,41 statt 0,17). Beide teilen
  sich das Risikobudget, und DEADBAND-Verlustphasen treffen auf Fade-Positionen.
- **Fades plus RSI21 und Noise, ohne DEADBAND** ist die beste Mischung. Kleinere RSI21-/Noise-Risiken und
  der Serien-Stopp nach 3 Verlusten drücken die Busts von 0,06 auf 0,02.
- Die Noise-Variante v2 (Prüfung alle 30 min) plus ein Eröffnungsmomentum brachten zu den Fades kaum mehr
  Auszahlungen (7,8), auf 2006–21 aber doppelt so viele Busts wie die Fades allein (0,65 statt 0,31 je
  Jahr). Sie sind nicht in 6.00.

### 2.5 Regime-Problem und Wächter

Dieselben 10 Fades allein (= „Sicher“) auf beiden Datensätzen:

| Wächter | GFT 2022–26: Ausz. / Busts / Netto | Fremddaten 2006–21: Ausz. / Busts / Netto |
|---|---|---|
| keiner ¹ | 7,89 / 0,00 / 2226 $ | 1,19 / **2,70** / −83 $ |
| Summe der letzten 40 > 0 R ¹ | 7,52 / 0,00 / 2092 $ | 0,54 / 0,62 / 49 $ |
| PF der letzten 30 > 1,2 ¹ | 6,46 / 0,00 / 1758 $ | 0,61 / 0,31 / 121 $ |
| **PF der letzten 30 > 1,2 (6.00)** ² | 6,08 / 0,00 / 1653 $ | 0,55 / **0,31** / 104 $ |
| PF der letzten 180 Tage > 1,2 ² | 5,63 / 0,00 / 1554 $ | 0,55 / 0,37 / 95 $ |

¹ Einzelversuch: GFT 8 Störungen, 3 % ausgelassen. ² Endbewertung: GFT 16 Störungen, 8 % ausgelassen.
Fremddaten jeweils 4 Störungen.

Ohne Wächter verlieren die Fades 2006–21 rund 23 R je Jahr. Der Wächter drückt das auf 2–4 R und behält
70–83 % des Gewinns von 2022–26. Gewählt wurde „PF der letzten 30 > 1,2“: die wenigsten Busts im alten
Regime, und der EA kann ihn beim Start aus rund 600 Tagen M5-Historie rekonstruieren.

Warum die Fades erst seit 2022 funktionieren, ist nicht belegt. Eine naheliegende Erklärung ist der
Siegeszug der täglich verfallenden Optionen (0DTE) seit 2022: Deren Absicherung drückt den Index intraday
eher zurück in die Spanne. Das ist eine Vermutung. Genau deshalb gibt es den Wächter.

## 3. Was 6.00 ändert

| Eingabe | 5.10 | **6.00** | Zweck |
|---|---:|---:|---|
| `FadeAktiv` (neu) | – | true | 10 Fade-Module (Abschnitt 4) |
| `FadeRiskPct` (neu) | – | 0,75 % | Risiko je Fade-Trade × Pufferkurve |
| `FadeWaechterN` / `FadeWaechterPF` / `FadeWaechterMin` (neu) | – | 30 / 1,20 / 30 | Regime-Wächter je Modul |
| `FadeHistTage` (neu) | – | 600 | Historie für den Wächter beim Start |
| `FadeZielAbSek` (neu) | – | 130 | Ziel erst nach 130 s setzen (120-s-Regel) |
| `FadeListe` / `FadeAus` (neu) | – | leer / leer | leer = Standard-Liste im Code; `FadeAus` schaltet einzelne Module ab (z. B. `N1800;X0300S`) |
| `DbAktiv` (neu) | (an) | **false** | DEADBAND-Einstiege aus; offene Positionen werden weiter verwaltet |
| `MinProfitPct` | 0 | **3,0** | Auszahlung erst ab 300 $ Gewinn |
| `GesamtBudgetPct` | 2,00 % | **0,90 %** | Summe aller offenen Stop-Risiken unter der −1-%-Grenze |
| `IdeeMaxRisikoPct` | 1,25 % | **0,90 %** | Risiko je Symbol + Richtung |
| `R21RiskPct` | 0,63 % | **0,50 %** | |
| `NzRiskPct` | 0,45 % | **0,35 %** | |
| `SerienStopp` | 4 | **3** | nach 3 Verlusten in Folge Pause bis 17:00 NY |

Preset **Sicher** (`DEADBAND_LIVE4_600_Sicher.set`): wie oben, aber `R21Aktiv=false`, `NzAktiv=false`,
`SerienStopp=4` – nur die Fades.

## 4. Die 10 Fade-Module

Uhrzeiten New York. Range = Hoch/Tief der M5-Kerzen im Range-Fenster. Handelsfenster: die erste Kerze, die
über das Hoch (unter das Tief) handelt und wieder innen schließt, gibt das Signal. Schließt vorher eine Kerze
außerhalb, ist der Tag für das Modul vorbei. Einstieg zur nächsten Kerze, Stop hinter dem Extrem plus
Puffer × Range, Ziel Range-Mitte bzw. Gegenseite, Zeit-Ausstieg spätestens 16:40. Nur Tage mit Range
≤ 0,6 × Tages-ATR(14) (außer N0930). Höchstens ein Signal je Modul und Tag.

| Modul | Symbol | Richtung | Range | Handelsfenster | Ausstieg | Puffer | Ziel | Signale/J | Treffer | PF |
|---|---|---|---|---|---|---:|---|---:|---:|---:|
| N1030 | NAS100 | long | 10:30–12:30 | 12:30–13:30 | 15:30 | 0,3 | Mitte | 30 | 67 % | 1,92 |
| N1330 | NAS100 | long | 13:30–14:30 | 14:30–16:30 | 16:40 | 1,0 | Mitte | 54 | 78 % | 1,59 |
| X0630 | Gold | short | 06:30–08:30 | 08:30–11:30 | 15:30 | 1,0 | Gegenseite | 55 | 69 % | 1,52 |
| X0400 | Gold | long | 04:00–07:00 | 07:00–08:00 | 12:00 | 0,3 | Mitte | 38 | 63 % | 1,43 |
| N1800 | NAS100 | long | 18:00–21:00 (Vorabend) | 21:00–22:00 | 00:00 | 0,3 | Mitte | 26 | 66 % | 1,61 |
| N0930 | NAS100 | long | 09:30–12:30 | 12:30–13:30 | 15:30 | 0,3 | Mitte | 25 | 59 % | 1,63 |
| N1100 | NAS100 | long | 11:00–12:30 | 12:30–13:30 | 16:40 | 0,6 | Gegenseite | 39 | 57 % | 1,59 |
| N1300 | NAS100 | long | 13:00–14:30 | 14:30–15:30 | 16:40 | 0,6 | Mitte | 43 | 72 % | 1,53 |
| X0300S | Gold | short | 03:00–04:30 | 04:30–05:30 | 07:30 | 0,3 | Mitte | 48 | 61 % | 1,45 |
| X1000S | Gold | short | 10:00–13:00 | 13:00–14:00 | 16:40 | 0,3 | Mitte | 26 | 63 % | 1,63 |

Signale, Trefferquote und Profitfaktor: alle Signale virtuell, GFT-Daten 2022–26, inkl. Spread und Kommission.
Im Konto handelt jedes Modul seltener (Wächter, Budget, Auszahlungsreife, Serien-Stopp, Hedging-Sperre).

Beitrag im Konto „Sicher“ (Replikat, je Jahr: Ergebnis / Trades / Treffer): N1030 302 $ / 20 / 65 %,
N1330 191 $ / 36 / 77 %, X0630 278 $ / 35 / 70 %, X0400 219 $ / 17 / 67 %, N1800 112 $ / 9 / 70 %,
N0930 118 $ / 16 / 58 %, N1100 263 $ / 23 / 58 %, N1300 96 $ / 30 / 72 %, X0300S 368 $ / 19 / 68 %,
X1000S 263 $ / 17 / 67 %. Kein Modul trägt das Ergebnis allein. In „Ertrag“ kommen RSI21 (800 $ / 51 / 50 %)
und Noise (380 $ / 63 / 51 %) dazu.

## 5. GFT-Regeln: so hält 6.00 sie ein

Stand der Regeln: GFT-Help-Center (Suchauszüge), GFT-Website; geprüft am 21.–24.09.2026. Die
GFT-Seiten selbst ließen sich aus dieser Umgebung nicht öffnen. GFT kann die Regeln ändern.

| Regel (Instant Premium) | Umsetzung in 6.00 |
|---|---|
| Floating-Verlust −1 % = harter Bruch (Kauf ab 02.09.2026, inkl. Swap und Kommission) | Summe aller offenen Stop-Risiken ≤ **0,9 %** (Gesamtbudget, jedes Modul), je Idee ≤ 0,9 %; eben eröffnete, noch nicht sichtbare Fade-Positionen zählen mit. Bremse bei −0,8 % auf die Summe der **Verlierer**, Notbremse −1,0 %, Swap-Vorsorge vor dem Rollover. Fades sind intraday (kein Swap). |
| Trailender Maximalverlust 6 % | Boden vom Equity-Hoch inkl. Buchgewinn (strengste Lesart), Pufferkurve verkleinert alle Module nahe am Boden |
| Tagesverlust 3 % | Tagesstopp 2,4 %, Notbremse 3 % auf min(Startsaldo, Tagesreferenz) |
| Gewinne aus Trades < 120 s gestrichen | Fade-Ziel erst nach **130 s** gesetzt; eigene Gewinnschließungen (Zeit-Ausstieg, Reife) erst ab 130 s |
| News ±5 min (Gewinne > 1 % gekappt) | ±6 min keine Einstiege, keine eigenen Gewinnschließungen > 1 %. Ein Server-Ziel kann im Fenster auslösen; bei den Zielen „Gegenseite“ (X0630, N1100) kann der Gewinn 1 % übersteigen – dann kappt GFT den Überschuss, das Konto bleibt |
| Hedging verboten (auch über eigene Konten) | Hedging-Sperre im Konto: kein Fade gegen eine offene oder eben gesendete Position im selben Symbol, egal welches Modul |
| Martingale/Grid | nie: feste Prozent-Größe × Pufferkurve, nach Verlusten kleiner, nie größer |
| Gambling (Margin > 80 %) | Margin je Idee ≤ 70 % der Equity, neue Order ≤ 80 % der freien Margin |
| Auszahlung: 5 gültige Tage, 10 Tage, flach, keine offenen Orders | Reife-Modus: keine Einstiege, Fade-, RSI21- und Noise-Positionen schließen (Gewinner nach 130 s), Push „Auszahlung beantragen“, sobald flach. Keine Pending Orders im EA |
| VPS verboten | `VpsSperre` + `NurAufPcPfad` (bitte setzen) |
| 30 Tage ohne Trade = Konto weg | Push ab 20 Tagen ohne Einstieg. **Achtung:** Schaltet der Wächter viele Module ab (altes Regime), kann besonders „Sicher“ wochenlang nicht handeln. Kommt der Push, von Hand einen kleinen Trade (0,01 Lot, > 2 min halten) setzen |

**Absolute Sicherheit kann kein EA geben.** Ein Kurssprung über den Stop (Gap, Datenausfall), ein
Verbindungsabbruch, eine andere Lesart von GFT oder eine Regeländerung liegen außerhalb seiner Kontrolle.
6.00 nimmt überall die strengste bekannte Lesart und hält das Stop-Risiko strukturell unter der −1-%-Grenze.

## 6. Ergebnisse im Detail

### 6.1 Nach Startjahr (1-Jahres-Konten, GFT-Daten, 16 Störungen)

| Startjahr | 5.10 (ab 3 %): Ausz. / Busts / Netto / längste Serie | **Sicher** | **Ertrag** |
|---|---|---|---|
| 2022 | 7,49 / 0,14 / 2114 $ / 9,4 | 5,81 / 0,00 / 1622 $ / 4,7 | 9,74 / 0,00 / 3101 $ / 5,2 |
| 2023 | 5,26 / 0,23 / 1446 $ / 9,2 | 6,40 / 0,00 / 1743 $ / 4,1 | 7,69 / 0,00 / 2325 $ / 5,8 |
| 2024 | 4,52 / 0,18 / 1274 $ / 8,5 | 5,27 / 0,00 / 1382 $ / 4,4 | 5,62 / 0,03 / 1634 $ / 5,5 |
| 2025 | 6,32 / 0,01 / 1732 $ / 8,1 | 6,62 / 0,00 / 1897 $ / 4,9 | 7,92 / 0,06 / 2359 $ / 6,1 |

„Ertrag“ ist in jedem Startjahr besser als 5.10. „Sicher“ hat in keinem Startjahr einen Bust; 2022 liegt
es bei den Auszahlungen unter 5.10.

### 6.2 Auszahlung ab 4 % (`MinProfitPct=4`)

| | Ausz./J | Ø Auszahlung | Busts/J | Netto/J |
|---|---:|---:|---:|---:|
| Sicher, ab 3 % | 6,08 | 350 $ | 0,00 | 1653 $ |
| Sicher, ab 4 % | 4,92 | 432 $ | 0,00 | 1650 $ |
| Ertrag, ab 3 % | 7,46 | 388 $ | 0,02 | 2243 $ |
| Ertrag, ab 4 % | 6,52 | 456 $ | 0,04 | 2300 $ |

Netto ändert sich kaum; ab 4 % gibt es weniger, dafür größere Auszahlungen. Voreinstellung bleibt 3 %.

### 6.3 Fremddaten 2006–2021 (anderes Regime, 4 Störungen)

| | Ausz./J | Busts/J | Netto/J | Konten mit Bust im 1. Jahr |
|---|---:|---:|---:|---:|
| 5.10 (ab 3 %) | 3,18 | 1,30 | 765 $ | 72 % |
| 6.00 Sicher | 0,55 | 0,31 | 104 $ | 22 % |
| 6.00 Ertrag | 1,89 | 0,39 | 502 $ | 31 % |

In diesem Regime verdienen die Fades nichts; der Wächter hält sie meist still. Auch 5.10 wäre dort
schlecht gelaufen (1,3 Busts je Jahr). Kommt so ein Regime zurück, wird 6.00 **seltener auszahlen** und kann
einzelne Konten verlieren. Warnzeichen: Im Panel stehen viele Module mit „−“ (nur virtuell), und seit
Wochen reift kein Zyklus.

### 6.4 Streuung

Über die 16 Störungen (Standardabweichung / Standardfehler des Mittels):

| | Auszahlungen/J | Busts/J | Netto/J |
|---|---|---|---|
| Sicher | 6,09 ± 0,31 / ± 0,08 | 0,000 ± 0 | 1653 $ ± 97 / ± 24 |
| Ertrag | 7,44 ± 0,30 / ± 0,08 | 0,017 ± 0,057 / ± 0,014 | 2236 $ ± 107 / ± 27 |

Die Abstände zwischen 5.10, Sicher und Ertrag liegen weit über diesem Rauschen. Die Unsicherheit aus dem
Regime (6.3) ist viel größer als die statistische.

## 7. Umsetzung im EA und Prüfung

- Neues Modul am Ende von `DEADBAND_LIVE4.mq5` (Abschnitt „6.00 Fade-Module“). Jede abgeschlossene M5-Kerze
  läuft durch denselben Zustandsautomaten wie im Replikat: Range, Signal, virtueller Trade (Stop vor Ziel,
  Ziel nicht in der Einstiegskerze, Zeit-Ausstieg). Live gehandelt wird nur die eben abgeschlossene Kerze.
  Verpasste Kerzen nach einem Neustart werden nur virtuell nachgerechnet.
- Beim Start rekonstruiert der EA die virtuellen Signale der letzten 600 Tage aus der M5-Historie. Erst dann
  kennt der Wächter den Stand. Das Journal zeigt je Modul eine Zeile `FADE N1030 (...): Historie ab ...,
  n Signale, PF der letzten 30 = x -> LIVE / nur virtuell`.
- Magic-Nummern: `MagicBase + 50 … + 59` (DEADBAND +0/+1, RSI21 +10…+25, Noise +30…+37).
- Fade-Positionen zählen im Serien-Stopp, in den Bremsen, im Gesamtbudget, in der Flach-Prüfung und in der
  Hedging-Sperre mit. Positionen ohne passendes Modul (Liste geändert) schließt der EA spätestens nach 8 h,
  ab 16:40 NY oder zum Freitagsschluss.
- Die Standard-Liste steht im Code (`FADE_STANDARD`), weil MT5 lange Text-Eingaben kürzen kann.
- **Abgleich mit dem Replikat:** Die Kerzenlogik `FadeKerze` wurde Zeile für Zeile nach Python übertragen
  (`Replikat_v6/t_port.py`) und auf den GFT-Daten gegen den Nachbau gerechnet: **1 750 von 1 753 Signalen
  identisch** (Einstiegskerze, Richtung, Stop-Abstand, Ergebnis in R). Die 3 Abweichungen liegen alle am
  21.01.2022, dem ersten Tag mit Tages-ATR am Datenbeginn; live hat MT5 genug D1-Historie.
- Dazu ein unabhängiger Code-Review auf Kompilierfehler und Regelverstöße durch einen Sub-Agenten.
  **Nicht** geprüft: Kompilieren in MetaEditor, Strategietester, Demo.

## 8. Grenzen, Risiken, Hinweise

1. **Regime-Abhängigkeit** (Abschnitt 6.3). Die Fades wurden auf 2022–26 unter vielen Varianten gefunden.
   Trotz In-/Out-of-Sample-Trennung und Nachbar-Prüfung kann ein Teil davon Zufall sein. Der Wächter
   begrenzt den Schaden, braucht nach einem Regimewechsel aber einige Verlust-Signale, bis er abschaltet.
2. **Nicht kompiliert, nicht im Tester.** Kleine Fehler sind möglich.
3. **Replikat statt Tick-Test:** M5-Kerzen, Reihenfolge in der Kerze angenommen, News-Sperre nicht
   abgebildet, NAS-Datenloch 2024. Absolute Zahlen sind Schätzungen, belastbar ist der Vergleich.
4. **M5-Historie:** Der Wächter braucht ~600 Tage M5-Kurse. Mit „Max. Balken im Chart“ = 100 000
   (MT5-Standard) reicht es knapp; besser „Unbegrenzt“. Hat ein Modul zu wenige Signale, bleibt es virtuell
   und meldet das im Journal.
5. **Hedging über eigene Konten:** GFT verbietet Gegenpositionen auch zwischen mehreren eigenen Konten.
   Handelt ein anderes eigenes Konto zur selben Zeit NAS100 oder Gold in die Gegenrichtung, kann
   das als Hedging gewertet werden. Der EA sieht nur sein eigenes Konto. Die Fades handeln NAS100 nur long
   und Gold fast nur short (X0400 long).
6. **Mehrere GFT-Konten mit demselben EA** können als Copy- oder Gruppenhandel gelten. Vorher beim Support
   klären.
7. **VPS/Server:** Für Instant Premium (Kauf ab 12.08.2026) ist VPS verboten; Trustpilot-Berichte nennen
   Kontosperren bei der Auszahlung wegen VPS-Nutzung. Ein gemieteter Windows-Server zählt vermutlich genauso.
   Nur auf dem eigenen PC betreiben und `NurAufPcPfad` setzen.
8. **Nachtmodul N1800** (NAS 21:00–00:00 NY = 04:00–07:00 Serverzeit) handelt in der ruhigsten Zeit mit
   breiterem Spread. Wer das nicht will: `FadeAus=N1800`.
9. **Öffentliches Repository:** Strategie und Einstellungen sind für jeden sichtbar. Empfehlung: auf
   „Private“ stellen.

## 9. Inbetriebnahme

1. `DEADBAND_LIVE4.mq5` nach `MQL5/Experts/` kopieren, in MetaEditor kompilieren. Erwartet: 0 Fehler.
2. Extras → Optionen → Charts → **Max. Balken im Chart = Unbegrenzt**, Terminal neu starten.
3. Strategietester: „Jeder Tick anhand realer Ticks“, XAUUSD.x M15, 2024–2026, Preset
   `DEADBAND_LIVE4_Echtbetrieb.set`. Im Journal prüfen:
   - je Modul die Zeile `FADE ... Historie ab ...` mit plausibler Signalzahl (≈ 25–55 je Jahr),
   - Einstiege `FADE N1330 14:35 LONG ... Ziel ... ab 130 s, Ausstieg 16:40 NY`, danach `Ziel ... gesetzt`
     und `Zeit-Ausstieg` bzw. Stop/Ziel,
   - keine Einstiege von `DEADBAND`, `SERIEN-STOPP` nach 3 Verlusten, Schließen bei Auszahlungsreife.
4. Eine Woche auf einem Demokonto (gleiche Serverzeit), dann live.
5. Live nur auf dem **eigenen PC**, EIN Chart (XAUUSD.x M15), `NurAufPcPfad` setzen. Umstellen, wenn das
   Konto flach ist (Wochenende).
6. Wahl der Ausprägung: **Ertrag** (Echtbetrieb-Set) für mehr Auszahlungen und Netto, **Sicher** für null
   Busts im Replikat und die kürzesten Serien.
7. `FadeRiskPct` nicht über 0,75 % erhöhen (Floating-Bremse bei −0,8 %).

## 10. Zurück auf 5.10

`rollback_5.10/DEADBAND_LIVE4.mq5` mit `rollback_5.10/DEADBAND_LIVE4_Echtbetrieb.set`. Nur die Fades
abschalten, sonst 6.00: `FadeAktiv=false` (rechnet virtuell weiter), für das Verhalten von 5.10 zusätzlich
`DbAktiv=true` und die Werte aus Abschnitt 3.

## Anhang: Replikat

Code, Anleitung und Ergebnisse: `Replikat_v6/` (ohne Kursdaten), Fremddaten-Aufbau: `extdata/`.
Endbewertung: `Replikat_v6/x31.py` (GFT) und `Replikat_v6/x33.py ext` (Fremddaten).
