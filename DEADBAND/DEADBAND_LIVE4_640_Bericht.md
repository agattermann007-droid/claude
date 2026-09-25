# DEADBAND LIVE 4 – Build 6.40 TAKT

Bericht vom 25.09.2026 · GFT Instant Premium 10k (Konto ab 02.09.2026)

## 1. Kurzfassung

Auftrag: 6.30 verbessern und auf eine Auszahlung **alle 30 Tage im Durchschnitt** bringen, **ohne mehr Bust-Risiko**.

**Build 6.40** ändert, *wann* ausgezahlt wird, *welche Tage* gültig bleiben und *wann* die Fades handeln. Die Einstiegssignale
bleiben die von 6.30:

1. **Auszahlung ab dem GFT-Minimum** statt ab 3 %: 131,25 $ Gewinn (`MinProfitPct` 3 → 0).
2. **Abschluss-Ernte immer** (`AbschlussLetzte` 3 → 5): Offener Gewinn macht den Tag gültig, sobald er dafür reicht.
3. **Schutz gültiger Tage** (neu, `GueltigSchutz`): Ist der Tag schon gültig und fehlen dem Zyklus noch gültige Tage, öffnet
   der EA bis 17:00 NY keine neue Position. Ein Verlust hätte den Tag sonst wieder ungültig gemacht.
4. **Regime-Wächter über das ganze Fade-Portfolio** (neu, `FadeWaechterModus` 1): Fades handeln live, solange der
   Profitfaktor der letzten 200 virtuellen Signale **aller** 10 Module über 1,15 liegt. Bisher galt der PF der letzten 30
   Signale **je Modul** über 1,2.
5. **Pufferkurve:** Nahe am Boden wird die Größe mit 0,3 statt 0,6 multipliziert (`DDMinFactor`).
6. **Fades ohne Teilgewinn** (`FadeT1R` 0,6 → 0) und **Noise 0,45 %** statt 0,35 % je Signal.

**Ergebnis** im Konto-Replikat mit allen GFT-Regeln (16 Störungen, rollierende Konten über 1/2/3 Jahre, Wächter wie im EA).
Gerechnet ist wie in 6.20/6.30 auf dem GFT-Ersatz aus Fremddaten 2022–2025, weil die GFT-Exporte fehlten:

| Kennzahl | 6.30 Ertrag | **6.40 Ertrag** (Echtbetrieb) |
|---|---:|---:|
| **Auszahlungen je Jahr** | 7,33 | **12,31** |
| **Tage je Auszahlung** (365,25 / Auszahlungen) | 49,9 | **29,7** |
| Lücke zwischen zwei Auszahlungen: Mittel / 90 % der Lücken kürzer als | 46 / 82 Tage | 28 / 45 Tage |
| Auszahlung im Mittel (Gewinn vor 80 % und 3 %) | 382 $ | 234 $ |
| **Busts je Jahr** | 0,000 | **0,000** |
| Konten, die dem Boden auf < 100 $ nahekamen | 0,5 % | **0,0 %** |
| kleinster Abstand zum Boden je Konto (Mittel) | 215 $ | 195 $ |
| Netto je Jahr (80 % Anteil, 3 % Gebühr, Neukäufe) | 2171 $ | **2234 $** |
| Serien ≥ 6 Verluste je Jahr | 0,96 | **0,70** |
| Trefferquote | 65,0 % | **65,7 %** |
| **Fremddaten 2006–21** (anderes Regime): Busts je Jahr | 0,347 | **0,121** |
| … Konten mit Bust im 1. Jahr | 29,2 % | **7,2 %** |
| … Auszahlungen / Netto je Jahr | 1,83 / 481 $ | 2,56 / 418 $ |

- **Ziel erreicht:** Im Mittel kommt alle **29,7 Tage** eine Auszahlung, gegenüber 49,9 Tagen bei 6.30. Busts gibt es wie
  bei 6.30 keine.
- **Nicht mehr Bust-Risiko, im alten Regime deutlich weniger:** Auf dem GFT-Ersatz kam kein Konto dem Boden auf weniger als
  100 $ nahe (6.30: 0,5 %). Im Mittel liegt der kleinste Abstand zum Boden 20 $ tiefer (195 statt 215 $). Auf den
  Fremddaten 2006–21 hat 6.40 ein Drittel der Busts von 6.30 (0,121 statt 0,347 je Jahr).
- **Der Preis:** kleinere Auszahlungen, im Mittel 234 $ statt 382 $ Gewinn, dafür 12 statt 7 im Jahr. Netto je Jahr bleibt
  gleich. Die frühere Vorgabe „jede Auszahlung ≥ 3 %“ (Build 6.00) gilt damit nicht mehr.
  - Mit `MinProfitPct=3` hätte 6.40 alle 42,6 Tage eine Auszahlung (Abschnitt 3.6).
  - Dazwischen: 2 % → etwa alle 34 Tage, 1,5 % → alle 31 Tage.
- **Nach Startjahr** (1-Jahres-Konten):
  - Start 2022: alle 28,6 Tage, 2023: 27,0 Tage.
  - Start 2024: 36,5 Tage, 2025: 39,6 Tage (6.30: 71,6 / 82,6 Tage).
  - Die 30 Tage sind ein Mittel über die Jahre 2022–2025, keine Garantie für jedes Jahr.
- **Die 30 Tage setzen voraus,** dass die Auszahlung sofort beantragt wird, sobald der EA „JETZT AUSZAHLUNG BEANTRAGEN“
  meldet, und dass GFT sie binnen etwa eines Tages bucht. Bucht GFT einen Tag später, sind es 31,1 Tage.

**Nicht geprüft:** Kompilieren in MetaEditor, Strategietester, Demo. Das bleibt Pflicht (Abschnitt 6).

## 2. Was die Auszahlung bremst

Eine Auszahlung braucht 5 gültige Tage (je ≥ 0,5 % = 50,50 $ realisiert), 10 Tage Zyklus und den Mindestgewinn. Danach
muss das Konto flach sein, bis GFT bucht. Die Diagnose von 6.30 (Replikat, je Jahr):

| | 6.30 Ertrag | 6.40 Ertrag |
|---|---:|---:|
| gültige Tage | 48,8 | **69,8** |
| … davon schon gültig gewesen und durch einen späteren Verlust wieder ungültig | 8,3 | **3,1** |
| Handelstage mit 25–50 $ (knapp ungültig) / 0–25 $ | 31,8 / 29,8 | 25,9 / 25,0 |
| Handelstage mit Verlust | 59,5 | 62,5 |
| Handelstage ohne jeden Trade | 80,3 | **61,3** |
| Tage im Reife-/Auszahlungsmodus (flach) | 14,7 | 24,6 |
| zuletzt erfüllt: gültige Tage / Mindestgewinn / 10-Tage-Frist | 52 / 48 / 1 % | 64 / 30 / 7 % |
| Tage vom Zyklusbeginn bis 5 gültige Tage / bis Mindestgewinn | 32,5 / 40,4 | 21,6 / 21,7 |

Drei Bremsen, drei Hebel:

1. **Mindestgewinn 300 $:** In fast der Hälfte der Zyklen waren die 5 gültigen Tage längst da, der Gewinn aber noch nicht.
   → Auszahlung ab dem GFT-Minimum.
2. **Zu wenige gültige Tage:** Viele Tage enden knapp unter 50,50 $ oder kippen nach einem gültigen Stand durch einen
   späteren Verlust zurück. Der Fade-Teilgewinn von 6.30 hat das verschärft: Er macht aus vollen Gewinnen halbe
   (6.30: 48,8 gültige Tage, 6.20: 52,0). → Abschluss-Ernte immer, Schutz gültiger Tage, kein Fade-Teilgewinn.
3. **Zu wenige Handelstage:** An 80 Handelstagen im Jahr gab es keinen Trade. Rund 20 davon gehen auf den Wächter je
   Modul zurück, der auch im heutigen Regime viele gute Fade-Signale sperrt (ohne Wächter: 60 Tage ohne Trade).
   → Portfolio-Wächter.

## 3. Was gesucht und geprüft wurde

Replikat `eng8` = `eng7` plus Schutz gültiger Tage, Ernte-Varianten, Tages-Diagnose und Abstand zum Boden (`t_eng8.py`:
mit Voreinstellungen identisch mit eng7). Screening `x44.py`: 8 Störungen, jeder 2. Handelstag (GFT-Ersatz) bzw. jeder 6.
(Fremddaten). Endbewertung `x46.py`: 16 Störungen, jeder Handelstag bzw. jeder 3.

### 3.1 Schritt für Schritt (Screening)

Zellen: Auszahlungen je Jahr (Tage je Auszahlung) · Busts · Netto · gültige Tage · wieder verlorene gültige Tage; rechts
Fremddaten 2006–21: Auszahlungen · Busts · Netto.

| Variante | GFT-Ersatz 2022–25 | Fremddaten 2006–21 |
|---|---|---|
| 6.30 Ertrag | 7,43 (49,2) · 0 · 2195 $ · 49,3 · 8,1 | 1,83 · 0,326 · 485 $ |
| Mindestgewinn 2 % / 1,5 % | 8,75 (41,8) / 9,18 (39,8) · 0 | – |
| **Mindestgewinn = GFT-Minimum (131 $)** | 9,31 (39,2) · 0 · 2242 $ · 49,1 · 6,3 | 2,54 · 0,308 · 489 $ |
| + Abschluss-Ernte immer | 9,71 (37,6) · 0 · 2297 $ · 51,3 · 8,0 | 2,56 · 0,277 · 467 $ |
| + ohne Fade-Teilgewinn | 10,02 (36,4) · 0 · 2409 $ · 53,6 · 10,1 | 2,70 · 0,314 · 453 $ |
| + keine Einstiege nach gültigem Tag | 10,39 (35,1) · 0 · 1899 $ · 59,3 · 1,7 | 2,68 · 0,280 · 398 $ |
| + Wächter PF30 je Modul > 1,1 / > 1,0 | 10,57 / 10,78 · 0 | 3,07 · **0,461** / 3,20 · **0,678** |
| + ohne Wächter | 11,84 (30,8) · 0 | 3,84 · **1,822** · 348 $ |
| + Portfolio-Wächter PF100 > 1,2 | 11,04 (33,1) · 0 | 2,52 · 0,145 · 403 $ |
| + Portfolio-Wächter PF200 > 1,2 | 11,86 (30,8) · 0 | 2,68 · 0,178 · 448 $ |
| + Portfolio-Wächter PF150 > 1,1 | 12,27 (29,8) · 0 | 2,81 · **0,387** · 417 $ |
| … PF200 > 1,2, Schutz nur solange gültige Tage fehlen, Noise 0,45 % | 12,15 (30,1) · 0 · 2202 $ | 2,97 · 0,215 · 470 $ |
| **… PF200 > 1,15, dazu Pufferkurve x0,3 (= 6.40)** | **12,18 (30,0) · 0 · 2225 $** | **2,57 · 0,118 · 424 $** |

Einzelne Hebel ohne Wirkung über das Rauschen hinaus (±0,3 Auszahlungen): Fade-Risiko 0,70–0,90 %, RSI21 0,45–0,60 %,
Gesamtbudget 1,0 %, Serien-Stopp 0 oder 4, RSI21-Erstsignale, Vorlauf der Abschluss-Ernte 0–0,5 R, Ernte ganz oder mit Rest
auf Einstand, Teilgewinn bei 0,8 R.

### 3.2 Schutz gültiger Tage

Nach einem gültigen Tag kann jeder weitere Trade den Tag wieder ungültig machen. Ein Fade-Verlust von 75 $ genügt, wenn der
Tag bei 60 $ steht. Geprüft wurden vier Formen:

Basis: Mindestgewinn = GFT-Minimum, Abschluss-Ernte immer, ohne Fade-Teilgewinn, Wächter je Modul (Screening):

| Form | Ausz./J | gültige Tage | wieder verloren | Netto |
|---|---:|---:|---:|---:|
| ohne Schutz | 10,02 | 53,6 | 10,1 | 2409 $ |
| Risiko neuer Trades so begrenzt, dass der Tag gültig bleibt | 10,32 | 59,1 | 1,8 | 1918 $ |
| keine Einstiege nach gültigem Tag | 10,39 | 59,3 | 1,7 | 1899 $ |

Mit Portfolio-Wächter (PF200 > 1,2): „keine Einstiege nach gültigem Tag“ 11,86 Auszahlungen; **dieselbe Sperre, aber nur
solange dem Zyklus gültige Tage fehlen** (6.40), 12,02. Diese Form sperrt nur, wenn der Tag noch gebraucht wird. Fehlt nur
noch der Mindestgewinn oder die 10-Tage-Frist, wird normal gehandelt. Der Schutz kostet Netto (weniger Trades an gültigen
Tagen), bringt aber Auszahlungen und weniger Busts im alten Regime.

### 3.3 Regime-Wächter: Portfolio statt je Modul

Die Fades verdienen seit 2022, vorher nicht (Bericht 6.00). Der Wächter soll sie im alten Regime abschalten, im heutigen aber
handeln lassen. Das tut der Wächter je Modul nur mäßig: Aus 30 Signalen ist der Profitfaktor eines Moduls stark verrauscht.
Gute Module fallen zufällig darunter, schwache zufällig darüber. Das Regime trifft aber alle Fades zugleich. Ein Wächter über
alle 200 letzten Signale des Portfolios misst es mit viel weniger Rauschen.

Signal-Ebene (`pg_guard.py`, alle virtuellen Signale mit Grid-Regel S; R je Jahr · Signale je Jahr · größter Rückgang):

| Wächter | 2006–13 | 2014–21 | 2022–25 |
|---|---|---|---|
| keiner | −6,8 R · 273 · 79 R | −26,5 R · 311 · 212 R | +52,2 R · 366 · 11 R |
| je Modul PF30 > 1,2 (6.00–6.30) | +1,0 R · 73 · 23 R | −5,1 R · 59 · 41 R | +35,4 R · 238 · 9 R |
| **Portfolio PF200 > 1,15** (6.40, wie im EA) | −2,4 R · 35 · 28 R | **−0,7 R · 2 · 6 R** | **+48,1 R · 320 · 8 R** |

Im heutigen Regime lässt der Portfolio-Wächter ein Drittel mehr Signale durch (320 statt 238 je Jahr) und holt 92 % dessen,
was die Fades ohne Wächter verdienen. Im alten Regime ist er über 2006–21 zusammen etwas besser (−1,6 statt −2,1 R je Jahr,
größter Rückgang 28 statt 41 R), 2006–13 für sich aber schlechter.

Konto (Screening, Tabelle 3.1): Ein lockerer Wächter je Modul (PF > 1,1 / 1,0) bringt kaum mehr Auszahlungen, aber im alten
Regime 40–100 % mehr Busts. Ohne Wächter wären es 11,8 Auszahlungen, aber 1,8 Busts je Jahr im alten Regime. Der
Portfolio-Wächter bringt die Auszahlungen fast so weit wie „ohne Wächter“ und hält die Busts im alten Regime unter 6.30.
Nachbarn (Endbewertung, mit Pufferkurve 4/2/0,3; bei > 1,1 zusätzlich Noise 0,50 %): PF200 > 1,1 und > 1,2 liefern je
12,0 Auszahlungen und 0 Busts, im alten Regime 0,171 bzw. 0,069 Busts. Die Wahl 1,15 liegt in der Mitte dieses Plateaus.

### 3.4 Abstand zum Boden: warum die Pufferkurve strenger ist

Busts sind selten, deshalb wurde zusätzlich je Konto der **kleinste Abstand zwischen Equity und Boden** gemessen. Er ist
empfindlicher als die Zahl der Busts.

- **Ohne strengere Pufferkurve** kamen mit Portfolio-Wächter **15 % der Konten** dem Boden auf < 100 $ nahe (6.30: 0,5 %),
  fast alle im **März 2025** (NAS-Abverkauf).
  - Der langsame Portfolio-Wächter ließ die NAS-Long-Fades dort länger handeln als der schnelle Wächter je Modul.
  - Die Nachbar-Einstellung PF175 > 1,2 hatte in dieser Episode 0,025 Busts je Jahr.
  - Welche Wächter-Einstellung die Episode zufällig übersteht, ist Glück. Danach wurde bewusst **nicht** ausgewählt.
- **Stattdessen: Größe nahe am Boden kleiner** (`DDMinFactor` 0,6 → 0,3).
  - Die Pufferkurve beginnt wie bisher bei 4 % Puffer (volle Größe).
  - Bei 1,5 % Puffer ist die Größe jetzt ×0,3 statt ×0,6.
  - Das wirkt unabhängig vom Wächter und von der Episode.

| | 6.30 | 6.40 mit `DDMinFactor` 0,6 | **6.40** |
|---|---:|---:|---:|
| GFT-Ersatz: Auszahlungen je Jahr | 7,33 | 12,45 | **12,31** |
| … Konten < 100 $ vor dem Boden | 0,5 % | 12,2 % | **0,0 %** |
| … kleinster Abstand zum Boden (Mittel) | 215 $ | 173 $ | **195 $** |
| Fremddaten: Busts je Jahr | 0,347 | 0,274 | **0,121** |
| … kleinster Abstand zum Boden (Mittel) | 38 $ | 114 $ | **139 $** |

Die strengere Kurve kostet 0,14 Auszahlungen je Jahr und nimmt die Beinahe-Busts heraus. Im Mittel bleiben die Konten 20 $
näher am Boden als bei 6.30, weil mehr gehandelt wird. Kein Konto kommt aber näher als 100 $ heran.

### 3.5 Endbewertung (`x46.py`, 16 Störungen, Wächter wie im EA)

**GFT-Ersatz 2022–2025** (jeder Handelstag ein neues Konto, 1/2/3 Jahre):

| Variante | Ausz./J (Tage) | Ø Ausz. | Busts | Netto | Serien ≥ 6 | längste Ø/max | Treffer | < 100 $ am Boden |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 6.30 Ertrag | 7,33 (49,9) | 382 $ | 0 | 2171 $ | 0,96 | 7,0 / 11 | 65,0 % | 0,5 % |
| **6.40 Ertrag** | **12,31 (29,7)** | 234 $ | **0** | **2234 $** | **0,70** | 6,8 / 10 | **65,7 %** | **0,0 %** |
| 6.40, Wächter PF200 > 1,1, Noise 0,50 %, Kurve 4/2/0,3 | 11,99 (30,5) | 232 $ | 0 | 2159 $ | 0,72 | 7,0 / 10 | 65,3 % | 0,0 % |
| 6.40, Wächter PF200 > 1,2, Kurve 4/2/0,3 | 12,03 (30,4) | 231 $ | 0 | 2161 $ | 0,68 | 6,7 / 10 | 65,5 % | 0,0 % |
| 6.40 mit `DDMinFactor` 0,6 | 12,45 (29,3) | 233 $ | 0 | 2256 $ | 0,69 | 6,8 / 9 | 65,6 % | 12,2 % |
| 6.40 mit Wächter je Modul (wie 6.30) | 10,63 (34,4) | 233 $ | 0 | 1921 $ | 1,01 | 6,9 / 13 | 64,6 % | 0,4 % |
| 6.40 mit Mindestgewinn 3 % | 8,57 (42,6) | 340 $ | 0 | 2259 $ | 0,78 | 7,0 / 10 | 65,4 % | 2,2 % |
| 6.40, GFT bucht 1 Tag schneller | 12,60 (29,0) | 231 $ | 0 | 2263 $ | 0,91 | 7,2 / 10 | 65,3 % | 0,2 % |
| 6.40, GFT bucht 1 Tag später | 11,76 (31,1) | 231 $ | 0 | 2113 $ | 0,71 | 6,5 / 10 | 65,7 % | 0,0 % |
| 6.30 Sicher | 4,13 (88,4) | 350 $ | 0 | 1123 $ | 0,05 | 4,8 / 9 | 70,4 % | 0,6 % |
| **6.40 Sicher** (mit Abschluss-Ernte) | **7,95 (45,9)** | 222 $ | 0 | 1370 $ | **0,02** | 4,8 / 6 | 69,5 % | 0,0 % |
| 6.40 Sicher ohne Abschluss-Ernte | 7,66 (47,7) | 241 $ | 0 | 1430 $ | 0,05 | 4,8 / 6 | 68,6 % | 0,0 % |

Streuung über die 16 Störungen: 6.40 Ertrag 12,31 ± 0,61 Auszahlungen (6.30: 7,33 ± 0,32). Der Abstand liegt weit über der
Streuung. Die Störungen bilden nur Ausführung und Kosten ab, nicht einen anderen Marktverlauf.

**Fremddaten 2006–2021** (anderes Regime; jeder dritte Tag):

| Variante | Ausz./J | Busts/J | Bust im 1. Jahr | Netto | Serien ≥ 6 | Treffer | kleinster Abstand zum Boden Ø |
|---|---:|---:|---:|---:|---:|---:|---:|
| 6.30 Ertrag | 1,83 | 0,347 | 29,2 % | 481 $ | 2,47 | 51,1 % | 38 $ |
| **6.40 Ertrag** | **2,56** | **0,121** | **7,2 %** | 418 $ | **2,20** | 48,3 % | **139 $** |
| 6.40, PF200 > 1,1, Noise 0,50 %, Kurve 4/2/0,3 | 2,64 | 0,171 | 9,6 % | 428 $ | 2,39 | 48,6 % | 115 $ |
| 6.40, PF200 > 1,2, Kurve 4/2/0,3 | 2,44 | 0,069 | 5,5 % | 408 $ | 2,19 | 48,2 % | 165 $ |
| 6.40 mit `DDMinFactor` 0,6 | 3,04 | 0,274 | 16,5 % | 472 $ | 2,12 | 48,6 % | 114 $ |
| 6.40 mit Wächter je Modul | 2,52 | 0,156 | 10,7 % | 397 $ | 2,49 | 50,4 % | 75 $ |
| 6.40 mit Mindestgewinn 3 % | 1,67 | 0,139 | 7,6 % | 426 $ | 2,26 | 48,7 % | 133 $ |
| 6.30 Sicher | 0,48 | 0,228 | 16,3 % | 97 $ | 0,31 | 59,2 % | 79 $ |
| **6.40 Sicher** | 0,31 | **0,063** | 4,7 % | 47 $ | 0,20 | 55,7 % | 359 $ |

- Im alten Regime verdienen die Fades nichts. 6.40 lässt sie dort seltener handeln als 6.30.
- Mit dem Wächter je Modul läge 6.40 dort bei 0,156 Busts. Der größere Teil des Rückgangs kommt also von den anderen
  Änderungen: Pufferkurve, häufigere Auszahlungen und Schutz gültiger Tage.
- Die Trefferquote sinkt dort, weil die treffsicheren Fades seltener handeln (48,3 statt 51,1 %).

### 3.6 Mindestgewinn: Größe gegen Takt

Mit 6.40 lässt sich über `MinProfitPct` wählen, ob größere oder häufigere Auszahlungen wichtiger sind. Screening
(GFT-Ersatz, 8 Störungen), Netto je Jahr in allen Stufen 2200–2275 $:

| `MinProfitPct` | 0 (GFT-Minimum 131 $) | 1,5 | 2,0 | 2,5 | 3,0 |
|---|---:|---:|---:|---:|---:|
| Auszahlungen je Jahr | 12,18 | 11,77 | 10,75 | 9,76 | 8,49 |
| Tage je Auszahlung | 30,0 | 31,0 | 34,0 | 37,5 | 43,1 |
| Auszahlung im Mittel | 235 $ | 241 $ | 265 $ | 300 $ | 340 $ |

### 3.7 Nach Startjahr (1-Jahres-Konten, GFT-Ersatz)

Zellen: Auszahlungen je Jahr (Tage je Auszahlung) · Netto · Serien ≥ 6 · Trefferquote. Busts in allen Zellen 0.

| Variante | Start 2022 | Start 2023 | Start 2024 | Start 2025 ⁽*⁾ |
|---|---|---|---|---|
| 6.30 Ertrag | 8,46 (43,2) · 2743 $ · 0,77 · 68,3 % | 8,20 (44,6) · 2393 $ · 1,66 · 64,9 % | 5,10 (71,6) · 1399 $ · 0,30 · 62,7 % | 4,42 (82,6) · 1216 $ · 0,29 · 64,2 % |
| **6.40 Ertrag** | **12,76 (28,6)** · 2515 $ · 1,05 · 67,3 % | **13,54 (27,0)** · 2535 $ · 0,42 · 67,6 % | **10,01 (36,5)** · 1598 $ · 0,76 · 62,3 % | **9,22 (39,6)** · 1413 $ · 1,34 · 63,6 % |
| 6.40 Sicher | 8,01 (45,6) · 1593 $ | 8,25 (44,3) · 1440 $ | 7,29 (50,1) · 1118 $ | 7,40 (49,4) · 1293 $ |

⁽*⁾ Die Ersatzdaten enden am 31.12.2025, deshalb gibt es für Start 2025 nur wenige Konten.

Seit 2024 verdienen die Fades auf dem Ersatz weniger (breitere Spreads, schwächerer Vorteil). 6.40 zahlt dann etwa alle
5–6 Wochen aus, 6.30 alle 10–12 Wochen. 2022–23 sind es knapp 4 Wochen.

## 4. Was 6.40 ändert

| Eingabe | 6.30 | **6.40** | Bedeutung |
|---|---:|---:|---|
| `MinProfitPct` | 3,0 | **0,0** | Mindestgewinn in % (0 = nur GFT-Mindestauszahlung: 105 $ Anteil = 131,25 $ Gewinn) |
| `AbschlussLetzte` | 3 | **5** | Abschluss-Ernte, sobald höchstens X gültige Tage fehlen (≥ 5 = immer) |
| `FadeT1R` | 0,6 | **0,0** | Fade-Teilgewinn aus (wie 6.20) |
| `NzRiskPct` | 0,35 | **0,45** | Risiko je Noise-Signal |
| `DDMinFactor` | 0,6 | **0,3** | Größenfaktor bei `DDMinPct` (1,5 %) Puffer; auch Faktor bei unsicherer Equity-Spitze |
| `GueltigSchutz` (neu) | – | **true** | heute gültig und dem Zyklus fehlen (ohne heute) gültige Tage: keine neuen Einstiege bis 17:00 NY |
| `FadeWaechterModus` (neu) | – | **1** | 1 = Portfolio-Wächter, 0 = je Modul (`FadeWaechterN/PF/Min` wie 6.00–6.30) |
| `FadePortN` (neu) | – | **200** | Zahl der letzten virtuellen Fade-Signale (alle Module, innerhalb `FadeHistTage`) |
| `FadePortPF` (neu) | – | **1,15** | Fades live nur bei Profitfaktor > X |

Verhalten:

- **Schutz gültiger Tage:**
  - Gilt für neue Einstiege von RSI21, Noise, Fades und DEADBAND.
  - Offene Positionen, Stops, Ziele, Ernten, Ausstiege und Wochenend-Wiederaufnahmen laufen weiter. RSI21-Signale werden
    weiter als Erstsignal gemerkt.
  - „Heute gültig“ heißt: realisiert heute ≥ 50,50 $, in beiden Kommissions-Lesarten wie bei der Reife. Eine eigene Ernte
    zählt schon, bevor ihre Deals in der Historie stehen (30 s).
  - Journal: `SCHUTZ GUELTIGER TAG - heute realisiert … keine neuen Einstiege bis 17:00 NY`.
  - Bei ausgelassenen Signalen steht der Grund im Journal: `Tag schon gueltig (…), noch n gueltige Tage bis zur Auszahlung`.
- **Portfolio-Wächter:**
  - Jedes virtuelle Fade-Ergebnis bekommt den Zeitpunkt, ab dem es feststeht (Ende der Kerze).
  - Bei einem Signal zählen die letzten 200 Ergebnisse aller Module, die vor der Einstiegskerze feststanden und nicht
    älter als `FadeHistTage` (600 Tage) sind.
  - Fehlen Signale oder ist die Historie eines Moduls noch nicht geladen, handeln die Fades nur virtuell.
  - Beim Start meldet das Journal `FADE Portfolio-Waechter: PF … aus den letzten 200 virtuellen Signalen aller 10 Module
    -> Fades LIVE / nur virtuell`.
  - Das Panel zeigt den Wert in der Zeile „Fade-Module“.
  - `FADEHIST` ist jetzt 256 (bisher 64), damit der Ringpuffer jedes Moduls das ganze Fenster fassen kann.
- **Panel:** Zeile „Auszahlungstakt“ (Mindestgewinn, Ernte, Schutz, Wächter, Größe nahe am Boden). Im Status steht
  „TAG GUELTIG - keine neuen Einstiege bis 17:00 NY“, solange der Schutz greift.
- **Rückweg zu 6.30** im selben EA:
  - `MinProfitPct=3`, `AbschlussLetzte=3`, `FadeT1R=0.6`, `NzRiskPct=0.35`, `DDMinFactor=0.6`, `GueltigSchutz=false`,
    `FadeWaechterModus=0`.
  - Oder `rollback_6.30/` (mq5 und beide Sets).
  - Achtung: Ein 6.30-Set in den 6.40-EA geladen lässt die vier neuen Eingaben auf den 6.40-Werten.

## 5. Prüfung

- **Replikat eng8 = eng7** mit ausgeschalteten 6.40-Regeln (`t_eng8.py`): alle Zähler, Trades und Ereignisse identisch
  (6.30 Ertrag, 6.30 Sicher, je 15 Konten).
- **Baseline reproduziert:** Die Kursdaten wurden aus den Quellen neu aufgebaut. Alle fünf Dateien sind byte-identisch mit
  dem Datenbericht. Das Replikat rechnet 6.30 exakt wie im 6.30-Bericht: 7,33 / 0 / 2171 $ / 0,96 / 65,0 % und
  1,83 / 0,347 / 481 $.
- **Abgleich EA ↔ Replikat** (`t_port_640.py`, Protokoll `Replikat_v6/ergebnisse/t_port_640.txt`):
  - Die virtuelle Trade-Führung aus `FadeKerze` mit dem neuen Zeitstempel ist wörtlich nach Python übertragen. Gerechnet
    wurden alle Signale der 10 Module auf GFT-Ersatz und Fremddaten. Einstieg, Ergebnis und Zeitpunkt sind identisch mit
    dem Replikat.
  - Ausnahme sind je 1 Signal bei 3 Modulen am 21.01.2022. Das ist der erste Tag mit Tages-ATR am Datenbeginn und schon
    im 6.00-Bericht beschrieben. Live hat MT5 genug Tageskerzen.
  - `FadePortfolioPF`/`FadeWaechterOk` sind wörtlich übertragen (Ringpuffer, Schlüssel, Sortierung, Fenster) und auf allen
    6309 Signalen der Kette gerechnet. Ergebnis: **identische Entscheidung bei jedem Signal**, für PF200 > 1,15, PF200 > 1,2
    und PF100 > 1,1.
  - Schutz gültiger Tage: EA-Bedingung = Replikat-Bedingung auf 112 Zuständen.
- **Presets** (`t_set.py`): `DEADBAND_LIVE4_Echtbetrieb.set` enthält alle 223 Eingaben mit genau den Voreinstellungen des
  EA. Das Sicher-Set weicht nur in `R21Aktiv`, `NzAktiv` und `SerienStopp` ab.
- **Statische Prüfung** (`t_mq5.py`): Klammern, Format-Argumente, Deklarationen vor der Verwendung – bestanden.
- **Gegenlesen** durch einen Sub-Agenten: REVIEW_640
- **Nicht** geprüft: Kompilieren in MetaEditor, Strategietester, Demo.

## 6. Echtbetrieb

Dateien:

- `DEADBAND_LIVE4.mq5`: Die Voreinstellungen **sind** das Echtbetrieb-Set („Ertrag“ + 6.40).
- `DEADBAND_LIVE4_Echtbetrieb.set`: dieselben Werte als Datei.
- `DEADBAND_LIVE4_640_Sicher.set`: „Sicher“ (nur Fades) mit den 6.40-Regeln.
- Rückweg: `rollback_6.30/` (mq5, `DEADBAND_LIVE4_Echtbetrieb.set`, `DEADBAND_LIVE4_630_Sicher.set`); ältere Stände in
  `rollback_6.20/`, `rollback_6.10/`, …

Inbetriebnahme:

1. `DEADBAND_LIVE4.mq5` in MetaEditor kompilieren. Erwartet: 0 Fehler.
2. **Max. Balken im Chart = Unbegrenzt** (wie 6.20). Der Portfolio-Wächter braucht 200 virtuelle Signale in 600 Tagen M5.
3. Strategietester: „Jeder Tick anhand realer Ticks“, XAUUSD.x M15, 2024–2026. Im Journal prüfen:
   - beim Start `6.40 Auszahlungstakt | Mindestgewinn 131.25 $ …` und `FADE Portfolio-Waechter: PF … -> Fades LIVE`,
   - Fade-Einstiege ohne `Teilgewinn`,
   - nach einem gültigen Tag `SCHUTZ GUELTIGER TAG …`, danach keine neuen Einstiege bis 17:00 NY (Ausstiege laufen),
   - `ABSCHLUSS-ERNTE …` auch dann, wenn noch 4–5 gültige Tage fehlen,
   - `AUSZAHLUNGSREIF`, sobald 5 gültige Tage, 10 Tage und 131,25 $ Gewinn erreicht sind.
4. Eine Woche auf einem Demokonto mit gleicher Serverzeit, dann live nur auf dem eigenen PC, EIN Chart.
5. **Auszahlung sofort beantragen,** sobald der EA „JETZT AUSZAHLUNG BEANTRAGEN“ meldet (Push). Danach
   `AuszahlungAngefordertAm` setzen. Jeder Tag Verzögerung verlängert den Takt: Bei einer Buchung einen Tag später
   sind es im Replikat 31,1 statt 29,7 Tage.

## 7. Grenzen und Hinweise

1. **Kein GFT-Datentest.** Alle Konto-Zahlen stammen vom GFT-Ersatz aus Fremddaten (breitere Spreads als GFT, Daten bis
   31.12.2025). Nachrechnen mit den GFT-Exporten: Dateien nach `data/`, dann `python prep5.py && python sig5.py` und
   `python x46.py gft`. Mit den engeren GFT-Spreads verdienen die Fades mehr. Der Portfolio-Wächter ließe sie dann eher
   öfter handeln.
2. **Takt nach Marktphase:** Die 29,7 Tage sind ein Mittel über 2022–2025. Bei Start 2024/2025 waren es 36–40 Tage
   (Abschnitt 3.7). In einem Regime wie 2006–21 wären es rund 140 Tage (6.30: 200).
3. **Kleinere Auszahlungen:** im Mittel 234 $ statt 382 $ Gewinn. Wer größere will, setzt `MinProfitPct` (Abschnitt 3.6).
   Ab 2 % liegt der Takt bei etwa 34 Tagen.
4. **Bust-Risiko:**
   - Auf dem GFT-Ersatz 0 Busts wie 6.30. Kein Konto kam dem Boden näher als 100 $, im Mittel aber 20 $ näher als bei 6.30.
   - Auf den Fremddaten ein Drittel der Busts von 6.30.
   - Die März-Episode 2025 zeigt, dass es ohne die strengere Pufferkurve knapp geworden wäre.
   - `DDMinFactor` deshalb nicht erhöhen.
5. **Wächter-Wahl:** PF200 > 1,15 liegt zwischen den geprüften Nachbarn > 1,1 und > 1,2. Beide liefern ebenfalls rund 12
   Auszahlungen ohne Busts. Die Zahlen des gewählten Punkts sind trotzdem eher etwas optimistisch, weil aus mehreren
   Varianten gewählt wurde.
6. **Schwächstes Modul:** X1000S verliert auf dem Ersatz mit Portfolio-Wächter rund 70 $ je Jahr (6.30: +14 $). Es wurde
   nicht abgeschaltet, weil das eine Auswahl nach dem Ergebnis wäre. Wer es abschalten will: `FadeAus=X1000S`.
7. **Inaktivität bei „Sicher“:** Schaltet der Portfolio-Wächter die Fades ab (anderes Regime), handelt „Sicher“ womöglich
   wochenlang nicht. GFT: 30 Tage ohne Trade = Konto weg. Kommt der Push nach 20 Tagen ohne Einstieg, von Hand einen kleinen
   Trade setzen.
8. **Tick gegen Kerze:** Das Replikat prüft den Schutz gültiger Tage und die Abschluss-Ernte je M5-Kerze, der EA laufend.
   Der EA kann einen Tag deshalb etwas früher gültig machen und schützen.
9. **Nicht kompiliert, nicht im Tester** (Abschnitt 5).
10. **Lizenz** des Grid-Konzepts unverändert (Bericht 6.20, Abschnitt 10).

## Anhang: Replikat

`Replikat_v6/README.md` (Abschnitt Build 6.40):

- Motor: `eng8.py`, Bewertung: `evl8.py`
- Wächter-Studie und Portfolio-Wächter: `pg_guard.py`
- Screening: `x44.py`, Zwischenbewertung: `x45.py`, Endbewertung: `x46.py`
- Prüfungen: `t_eng8.py`, `t_port_640.py`, `t_set.py`, `t_mq5.py`
- Ergebnisse: `ergebnisse/x44_*.json`, `x45_*.json`, `x46_*.json`, `pg_guard.txt`, `t_port_640.txt`
- Kursdaten: `extdata/scripts/run_all.sh` baut die Fremddaten neu, `Replikat_v6/mk_proxy.py` den GFT-Ersatz.
