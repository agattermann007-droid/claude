# DEADBAND LIVE 4 – Build 6.40 TAKT

Bericht vom 25.09.2026 · GFT Instant Premium 10k (Konto ab 02.09.2026)

## 1. Kurzfassung

Auftrag: 6.30 verbessern und auf eine Auszahlung **alle 30 Tage im Durchschnitt** bringen, **ohne mehr Bust-Risiko**.

**Build 6.40** ändert, *wann* ausgezahlt wird, *welche Tage* gültig bleiben, *wann* die Fades handeln und *wie stark* die
Größe im Rückgang sinkt. Die Einstiegssignale bleiben die von 6.30:

1. **Auszahlung ab dem GFT-Minimum** statt ab 3 %: 131,25 $ Gewinn (`MinProfitPct` 3 → 0).
2. **Abschluss-Ernte immer** (`AbschlussLetzte` 3 → 5): Offener Gewinn macht den Tag gültig, sobald er dafür reicht.
3. **Schutz gültiger Tage** (neu, `GueltigSchutz`): Ist der Tag schon gültig und fehlen dem Zyklus noch gültige Tage, öffnet
   der EA bis 17:00 NY keine neue Position. Ein Verlust hätte den Tag sonst wieder ungültig gemacht.
4. **Regime-Wächter über das ganze Fade-Portfolio** (neu, `FadeWaechterModus` 1): Fades handeln live, solange der
   Profitfaktor der letzten 200 virtuellen Signale **aller** 10 Module über 1,15 liegt. Bisher galt der PF der letzten 30
   Signale **je Modul** über 1,2.
5. **Pufferkurve** (`DDFullPct` 4 → 5, `DDMinPct` 1,5 → 2,5, `DDMinFactor` 0,6 → 0,2): volle Größe nur bis 1 % Rückgang
   von der Equity-Spitze, danach kleiner bis ×0,2 bei 3,5 % Rückgang. Bisher: volle Größe bis 2 % Rückgang, ×0,6 ab 4,5 %.
6. **Fades ohne Teilgewinn** (`FadeT1R` 0,6 → 0) und **Noise 0,45 %** statt 0,35 % je Signal.

**Ergebnis** im Konto-Replikat mit allen GFT-Regeln (16 Störungen, rollierende Konten über 1/2/3 Jahre, Wächter wie im EA).
Die GFT-Exporte fehlten. Gerechnet ist deshalb auf dem GFT-Ersatz aus Fremddaten 2022–2025, und zwar zweimal: mit
**GFT-nahen Spreads** und mit den **breiten Spreads** der Berichte 6.20/6.30. Die breiten Spreads sind härter als bei GFT:

| Kennzahl | 6.30 Ertrag | **6.40 Ertrag** (Echtbetrieb) |
|---|---:|---:|
| **Tage je Auszahlung** (365,25 / Auszahlungen je Jahr), GFT-nahe Spreads | 44,1 | **30,3** |
| … breite Spreads | 49,9 | **32,5** |
| Auszahlungen je Jahr, GFT-nah / breit | 8,29 / 7,33 | **12,06 / 11,25** |
| Lücke zwischen zwei Auszahlungen, GFT-nah: Mittel / 90 % der Lücken kürzer als | 41 / 76 Tage | 29 / 46 Tage |
| Auszahlung im Mittel (Gewinn vor 80 % und 3 %), GFT-nah | 391 $ | 239 $ |
| **Busts je Jahr**, GFT-nah / breit | 0 / 0 | **0 / 0** |
| **Kleinster Abstand zum Boden je Konto**, Mittel, GFT-nah / breit | 248 / 215 $ | **248 / 255 $** |
| Konten, die dem Boden auf < 100 $ nahekamen, GFT-nah / breit | 0,0 / 0,5 % | **0,0 / 0,0 %** |
| Konten, die dem Boden auf < 200 $ nahekamen, GFT-nah / breit | 7,5 / 41,6 % | **4,1 / 0,1 %** |
| Netto je Jahr (80 % Anteil, 3 % Gebühr, Neukäufe), GFT-nah / breit | 2516 / 2171 $ | 2232 / 2051 $ |
| Serien ≥ 6 Verluste je Jahr, GFT-nah / breit | 0,61 / 0,96 | 0,77 / 0,83 |
| Trefferquote, GFT-nah / breit | 66,3 / 65,0 % | 66,1 / 65,6 % |
| **Fremddaten 2006–21** (anderes Regime): Busts je Jahr | 0,347 | **0,035** |
| … Konten mit Bust im 1. Jahr | 29,2 % | **0,9 %** |
| … kleinster Abstand zum Boden, Mittel | 38 $ | **207 $** |
| … Auszahlungen / Netto je Jahr | 1,83 / 481 $ | 2,16 / 364 $ |

- **Ziel erreicht mit GFT-nahen Spreads:**
  - Im Mittel kommt alle **30,3 Tage** eine Auszahlung, gegenüber 44,1 Tagen bei 6.30.
  - Mit den breiten Spreads sind es 32,5 Tage (6.30: 49,9).
  - Die GFT-nahe Rechnung liegt mit ihren Spreads im Bereich der GFT-Exporte (Bericht 6.20): Gold Median 22 Punkte
    (GFT 7–32), NAS 117 (GFT 100–163). Die breite Rechnung nimmt 36 bzw. 195 Punkte an.
- **Nicht mehr Bust-Risiko:**
  - Busts gibt es in beiden Rechnungen keine, wie bei 6.30.
  - Den Boden halten die Konten mindestens so weit entfernt wie bei 6.30: mit GFT-nahen Spreads gleich weit (248 $ im
    Mittel), mit breiten Spreads weiter (255 statt 215 $).
  - Kein Konto kam dem Boden näher als 100 $.
  - Im alten Regime 2006–21 hat 6.40 ein Zehntel der Busts von 6.30 (0,035 statt 0,347 je Jahr).
- **Der Preis:**
  - Die Auszahlungen sind kleiner: im Mittel 239 $ statt 391 $ Gewinn, dafür 12 statt 8 im Jahr.
  - Netto je Jahr ist es etwas weniger: −11 % mit GFT-nahen, −6 % mit breiten Spreads. Der Schutz gültiger Tage lässt
    Trades aus, und die Pufferkurve holt Rückgänge langsamer auf.
  - Die frühere Vorgabe „jede Auszahlung ≥ 3 %“ (Build 6.00) gilt nicht mehr. Mit `MinProfitPct=3` zahlte 6.40 alle
    47 Tage aus (breite Spreads, Abschnitt 3.5).
- **Nach Startjahr** (1-Jahres-Konten, GFT-nah):
  - Start 2022: alle 28,1 Tage, 2023: 26,3 Tage.
  - Start 2024: 41,6 Tage, 2025: 37,3 Tage (6.30: 64,7 / 68,6 Tage).
  - Die 30 Tage sind ein Mittel über die Jahre 2022–2025, keine Garantie für jedes Jahr.
- **Schneller ginge es nur näher am Boden** (Abschnitt 3.4):
  - Die Pufferkurve des ersten Entwurfs (4/1,5/×0,3) zahlte alle 29,2 Tage aus (GFT-nah).
  - Damit kamen aber 6 % der Konten dem Boden auf < 100 $ nahe, im Mittel 65 $ näher als bei 6.30 – fast alle im März 2025.
  - Das verletzt die Vorgabe. Deshalb ist diese Kurve nicht voreingestellt.
- **Die 30 Tage setzen voraus,** dass die Auszahlung sofort beantragt wird, sobald der EA „JETZT AUSZAHLUNG BEANTRAGEN“
  meldet, und dass GFT sie binnen etwa eines Tages bucht. Bucht GFT einen Tag später, dauert jede Runde rund einen Tag
  länger (breite Spreads: 33,5 statt 32,5 Tage).

**Nicht geprüft:** Kompilieren in MetaEditor, Strategietester, Demo. Das bleibt Pflicht (Abschnitt 6).

## 2. Was die Auszahlung bremst

Eine Auszahlung braucht 5 gültige Tage (je ≥ 0,5 % = 50,50 $ realisiert), 10 Tage Zyklus und den Mindestgewinn. Danach
muss das Konto flach sein, bis GFT bucht. Die Diagnose von 6.30 (Replikat, breite Spreads, je Jahr):

| | 6.30 Ertrag | 6.40 Ertrag |
|---|---:|---:|
| gültige Tage | 48,8 | **63,2** |
| … davon schon gültig gewesen und durch einen späteren Verlust wieder ungültig | 8,3 | **3,1** |
| Handelstage mit 25–50 $ (knapp ungültig) / 0–25 $ | 31,8 / 29,8 | 26,4 / 30,2 |
| Handelstage mit Verlust | 59,5 | 63,6 |
| Handelstage ohne jeden Trade | 80,3 | **62,2** |
| Tage im Reife-/Auszahlungsmodus (flach) | 14,7 | 22,5 |
| zuletzt erfüllt: gültige Tage / Mindestgewinn / 10-Tage-Frist | 52 / 48 / 1 % | 64 / 29 / 7 % |
| Tage vom Zyklusbeginn bis 5 gültige Tage / bis Mindestgewinn | 32,5 / 40,4 | 23,5 / 24,2 |

Drei Bremsen, drei Hebel:

1. **Mindestgewinn 300 $:** In fast der Hälfte der Zyklen waren die 5 gültigen Tage längst da, der Gewinn aber noch nicht.
   → Auszahlung ab dem GFT-Minimum.
2. **Zu wenige gültige Tage:** Viele Tage enden knapp unter 50,50 $ oder kippen nach einem gültigen Stand durch einen
   späteren Verlust zurück. Der Fade-Teilgewinn von 6.30 hat das verschärft: Er macht aus vollen Gewinnen halbe
   (6.30: 48,8 gültige Tage, 6.20: 52,0). → Abschluss-Ernte immer, Schutz gültiger Tage, kein Fade-Teilgewinn.
3. **Zu wenige Handelstage:** An 80 Handelstagen im Jahr gab es keinen Trade. Rund 20 davon gehen auf den Wächter je
   Modul zurück, der auch im heutigen Regime viele gute Fade-Signale sperrt (ohne Wächter: 60 Tage ohne Trade).
   → Portfolio-Wächter.

Der vierte Hebel kam erst am Ende dazu: Der Portfolio-Wächter lässt mehr Fades handeln, und damit wurden Rückgänge
tiefer. Die neue Pufferkurve nimmt das zurück (Abschnitt 3.4).

## 3. Was gesucht und geprüft wurde

Replikat `eng8` = `eng7` plus Schutz gültiger Tage, Ernte-Varianten, Tages-Diagnose und Abstand zum Boden (`t_eng8.py`:
mit Voreinstellungen identisch mit eng7). Screening `x44.py`: 8 Störungen, jeder 2. Handelstag (GFT-Ersatz) bzw. jeder 6.
(Fremddaten). Wächter-Formen und Pufferkurven `x47.py`: wie das Screening, die Endauswahl mit 16 Störungen, jeweils mit
breiten und mit GFT-nahen Spreads. Endbewertung `x46.py`: 16 Störungen, jeder Handelstag bzw. jeder 3.

### 3.1 Schritt für Schritt (Screening, breite Spreads)

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
| … PF200 > 1,15, Pufferkurve 4/1,5/×0,3 (erster Entwurf) | 12,18 (30,0) · 0 · 2225 $ | 2,57 · 0,118 · 424 $ |
| **… PF200 > 1,15, Pufferkurve 5/2,5/×0,2 (= 6.40)** | **11,15 (32,7) · 0 · 2030 $** | **2,19 · 0,034 · 369 $** |

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

Nachbarn (Endbewertung mit der 6.40-Pufferkurve, breite Spreads): PF200 > 1,1 und > 1,2 liefern je 11,1 Auszahlungen
(6.40 mit 1,15: 11,25) und 0 Busts, im alten Regime 0,039 bzw. 0,023 Busts (1,15: 0,035). Die Wahl 1,15 liegt in der Mitte
dieses Plateaus.

Mit dem Wächter je Modul statt Portfolio wäre 6.40 deutlich langsamer: 33,7 Tage je Auszahlung mit GFT-nahen, 37,9 Tage
mit breiten Spreads (Abschnitt 3.5). Zusammen mit der 6.40-Pufferkurve wäre er noch sicherer: im alten Regime 0,004 statt
0,035 Busts je Jahr, heute im Mittel 20–40 $ weiter vom Boden. Das Ziel von 30 Tagen verfehlt er aber.

### 3.4 Abstand zum Boden: warum die Pufferkurve früher greift

Busts sind selten, deshalb wurde zusätzlich je Konto der **kleinste Abstand zwischen Equity und Boden** gemessen
(schlechtester Kurs; Boden = Equity-Spitze − 6 %, nach jeder Auszahlung neu). Er ist empfindlicher als die Zahl der Busts.

**Das Problem.** Der Portfolio-Wächter lässt mehr Fades handeln, und die Rückgänge werden tiefer:

- Mit der Pufferkurve von 6.30 (volle Größe bis 2 % Rückgang, ×0,6 ab 4,5 %) kamen 12 % der Konten dem Boden auf < 100 $
  nahe (6.30: 0,5 %; breite Spreads).
- Fast alle diese Konten erreichten ihren tiefsten Stand im **März 2025** (NAS-Abverkauf). Der langsame Portfolio-Wächter
  ließ die NAS-Long-Fades dort länger handeln als der schnelle Wächter je Modul.
- Der erste Entwurf von 6.40 senkte nur den Faktor am Boden (×0,3 statt ×0,6). Mit breiten Spreads kam dann kein Konto
  unter 100 $, im Mittel lagen die Konten aber 20 $ näher am Boden als bei 6.30.
- Mit **GFT-nahen Spreads** war es deutlicher: 6 % der Konten unter 100 $, im Mittel 65 $ näher am Boden. Auch hier lag
  der tiefste Stand dieser Konten im Februar/März 2025.

Die Pufferkurve heißt hier „a/b/×f“: volle Größe ab a % Puffer zum Boden, Faktor f ab b % Puffer und darunter,
dazwischen linear. An der Equity-Spitze ist der Puffer 6 %.

| Pufferkurve (`DDFullPct`/`DDMinPct`/`DDMinFactor`) | volle Größe bis Rückgang | kleinste Größe ab Rückgang |
|---|---:|---:|
| 6.30: 4/1,5/×0,6 | 2 % | ×0,6 ab 4,5 % |
| erster Entwurf 6.40: 4/1,5/×0,3 | 2 % | ×0,3 ab 4,5 % |
| **6.40: 5/2,5/×0,2** | **1 %** | **×0,2 ab 3,5 %** |

**Andere Wächter-Formen helfen nicht verlässlich.** Screening, 8 Störungen, alle mit Pufferkurve 4/1,5/×0,3. Zellen: GFT-nah /
breit; rechts Fremddaten.

| Wächter | Tage je Auszahlung | kleinster Abstand, Mittel | Konten < 100 $ | Busts/J 2006–21 |
|---|---:|---:|---:|---:|
| 6.30 Ertrag (je Modul, Kurve 4/1,5/×0,6) | 44,1 / 49,2 | 248 / 212 $ | 0,0 / 0,5 % | 0,326 |
| je Modul PF30 > 1,2 | 30,7 / 34,7 | 248 / 230 $ | 0,0 / 0,7 % | 0,148 |
| Portfolio PF200 > 1,15 (erster Entwurf) | 29,3 / 30,0 | 187 / 190 $ | 4,3 / 0,0 % | 0,118 |
| … UND Portfolio PF50 > 1,0 | 29,3 / 31,8 | 176 / 207 $ | 3,3 / 0,0 % | 0,029 |
| … UND je Symbol PF50 > 1,0 | 29,8 / 31,5 | 183 / 206 $ | 7,0 / 0,8 % | 0,088 |
| … UND je Symbol PF30 > 1,0 | 32,4 / 35,7 | 200 / 180 $ | 0,0 / 20,5 % | 0,044 |
| je Modul PF30 > 1,2 ODER (PF30 > 1,1 UND Portfolio) | 31,3 / 33,5 | 220 / 224 $ | 7,4 / 0,0 % | – |
| je Modul PF30 > 1,2 ODER (PF30 > 0,8 UND Portfolio) | 28,4 / 30,1 | 201 / 205 $ | 11,5 / 0,6 % | – |

- Die zusammengesetzten Wächter liegen je nach Datenlage mal besser, mal schlechter.
- Beispiel „UND je Symbol PF30“: Mit breiten Spreads kamen 20,5 % der Konten unter 100 $, mit GFT-nahen keines.
- Welche Form die März-Episode übersteht, ist Zufall. Danach wurde bewusst **nicht** ausgewählt.
- Der Wächter je Modul hält mit dieser Kurve und GFT-nahen Spreads zwar Abstand, im alten Regime aber kaum (76 $ im Mittel).

**Die Pufferkurve wirkt dagegen in allen Datenlagen gleich:** Je früher und tiefer sie die Größe senkt, desto weiter
bleiben die Konten vom Boden weg, und desto langsamer wird der Takt. Das hängt nicht an einer Episode.

**Auswahl der Kurve mit 16 Störungen.** Mit 8 Störungen fielen die Beinahe-Busts teils nicht auf:

- Mit Kurve 5,5/2/×0,3 und GFT-nahen Spreads kamen 3,4 % der Konten dem Boden auf < 100 $ nahe.
- Fast alle stammen aus 2 der 16 Störungen (Nr. 11 und 15), alle mit dem tiefsten Stand im Februar/März 2025.
- Unter den ersten 8 Störungen ist keine davon, das Screening zeigte 0 %.

Portfolio-Wächter PF200 > 1,15, 16 Störungen, jeder 2. Handelstag (`x47.py`); Fremddaten: 8 Störungen, jeder 6. Tag.
Zellen: GFT-nah / breit:

| Pufferkurve | Tage je Auszahlung | kleinster Abstand, Mittel | Konten < 100 $ | Konten < 200 $ | Busts/J 2006–21 |
|---|---:|---:|---:|---:|---:|
| 6.30 Ertrag | 44,1 / 49,9 | 248 / 215 $ | 0,0 / 0,5 % | 7,4 / 41,6 % | 0,326 |
| 5/2/×0,2 | 29,9 / 31,5 | 231 / 238 $ | 0,0 / 0,0 % | 25,9 / 17,4 % | 0,054 |
| 5,5/2/×0,3 | 30,1 / 31,3 | 233 / 245 $ | **3,4** / 0,0 % | 24,9 / 19,3 % | 0,072 |
| 5/2,5/×0,25 | 30,2 / 32,1 | 239 / 245 $ | 0,0 / 0,0 % | 12,9 / 3,8 % | 0,060 |
| **5/2,5/×0,2 (6.40)** | **30,3 / 32,5** | **248 / 255 $** | **0,0 / 0,0 %** | **4,0 / 0,1 %** | **0,034** |
| 4,5/2,5/×0,2 | 30,5 / 31,9 | 233 / 240 $ | 0,0 / 0,0 % | 18,6 / 3,6 % | 0,035 |
| 5,5/2,5/×0,3 | 30,5 / 31,8 | 243 / 258 $ | 0,9 / 0,0 % | 15,7 / 5,0 % | 0,066 |
| 5/2,5/×0,15 | 30,8 / 33,4 | 251 / 257 $ | 0,0 / 0,0 % | 9,2 / 1,2 % | 0,009 |
| 5,5/2,5/×0,2 | 31,2 / 33,8 | 262 / 267 $ | 0,0 / 0,0 % | 0,2 / 0,0 % | 0,031 |
| 5/3/×0,2 | 31,6 / 34,2 | 268 / 275 $ | 0,0 / 0,0 % | 0,0 / 0,0 % | 0,025 |

- **5/2,5/×0,2 ist die schnellste geprüfte Kurve, die in beiden Spread-Lagen mindestens den Abstand von 6.30 hält.**
  Mit GFT-nahen Spreads zahlt sie trotzdem alle 30 Tage aus.
- Die Nachbarn liegen auf beiden Seiten:
  - lockerer (Faktor 0,25, Grenze 2 %, volle Größe bis 1,5 % Rückgang): mit breiten Spreads 0,4–1,0 Tage schneller, aber
    mit GFT-nahen Spreads näher am Boden als 6.30 (231–239 statt 248 $);
  - strenger (Faktor 0,15, Grenze 3 %, volle Größe nur bis 0,5 % Rückgang): noch weiter vom Boden weg, aber 0,5–1,3 Tage
    (GFT-nah) bzw. 0,9–1,7 Tage (breit) langsamer.
- Es ist also kein einzelner Glückspunkt, sondern ein Abwägungspunkt auf einer glatten Kurve.

Endbewertung mit derselben Auswahl (`x46.py`, 16 Störungen, jeder Handelstag):

| | 6.30 | **6.40** | Kurve 5,5/2/×0,3 | Kurve 5/2/×0,3 | erster Entwurf 4/1,5/×0,3 | Kurve wie 6.30 |
|---|---:|---:|---:|---:|---:|---:|
| Tage je Auszahlung, GFT-nah | 44,1 | **30,3** | 30,1 | 29,5 | 29,2 | – |
| … breit | 49,9 | **32,5** | 31,3 | 30,8 | 29,7 | 29,3 |
| kleinster Abstand, Mittel, GFT-nah | 248 $ | **248 $** | 233 $ | 221 $ | 183 $ | – |
| … breit | 215 $ | **255 $** | 245 $ | 229 $ | 195 $ | 173 $ |
| Konten < 100 $, GFT-nah / breit | 0,0 / 0,5 % | **0,0 / 0,0 %** | 3,3 / 0,0 % | 0,5 / 0,0 % | 6,0 / 0,0 % | – / 12,2 % |
| Fremddaten: Busts je Jahr | 0,347 | **0,035** | 0,075 | 0,080 | 0,121 | 0,274 |
| … kleinster Abstand, Mittel | 38 $ | **207 $** | 178 $ | 167 $ | 139 $ | 114 $ |

Die neue Kurve kostet gegenüber dem ersten Entwurf 1,1 Tage je Auszahlung mit GFT-nahen und 2,8 Tage mit breiten
Spreads. Dafür bleibt kein Konto näher am Boden als bei 6.30, und im alten Regime sinken die Busts von 0,121 auf 0,035.

### 3.5 Endbewertung (`x46.py`, 16 Störungen, Wächter wie im EA)

**GFT-Ersatz 2022–2025 mit GFT-nahen Spreads** (Spreads ×0,6; jeder Handelstag ein neues Konto, 1/2/3 Jahre):

| Variante | Ausz./J (Tage) | Ø Ausz. | Busts | Netto | Serien ≥ 6 | längste Ø/max | Treffer | kleinster Abstand Ø | < 100 $ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6.30 Ertrag | 8,29 (44,1) | 391 $ | 0 | 2516 $ | 0,61 | 6,7 / 10 | 66,3 % | 248 $ | 0,0 % |
| **6.40 Ertrag** | **12,06 (30,3)** | 239 $ | **0** | 2232 $ | 0,77 | 7,1 / 10 | 66,1 % | **248 $** | **0,0 %** |
| 6.40 mit Wächter je Modul (wie 6.30) | 10,84 (33,7) | 242 $ | 0 | 2038 $ | 0,69 | 6,4 / 10 | 65,3 % | 285 $ | 0,0 % |
| 6.30 Sicher | 5,57 (65,7) | 353 $ | 0 | 1526 $ | 0,00 | 4,1 / 6 | 71,7 % | 258 $ | 0,0 % |
| **6.40 Sicher** (mit Abschluss-Ernte) | **7,91 (46,2)** | 242 $ | 0 | 1487 $ | 0,00 | 4,5 / 5 | 69,7 % | 264 $ | 0,0 % |

**GFT-Ersatz 2022–2025 mit breiten Spreads** (wie in den Berichten 6.20/6.30):

| Variante | Ausz./J (Tage) | Ø Ausz. | Busts | Netto | Serien ≥ 6 | längste Ø/max | Treffer | kleinster Abstand Ø | < 100 $ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6.30 Ertrag | 7,33 (49,9) | 382 $ | 0 | 2171 $ | 0,96 | 7,0 / 11 | 65,0 % | 215 $ | 0,5 % |
| **6.40 Ertrag** | **11,25 (32,5)** | 235 $ | **0** | 2051 $ | **0,83** | 7,0 / 10 | **65,6 %** | **255 $** | **0,0 %** |
| 6.40, Wächter PF200 > 1,1 | 11,08 (33,0) | 234 $ | 0 | 2011 $ | 0,81 | 7,2 / 10 | 65,4 % | 253 $ | 0,0 % |
| 6.40, Wächter PF200 > 1,2 | 11,07 (33,0) | 232 $ | 0 | 1993 $ | 0,84 | 7,0 / 10 | 65,2 % | 254 $ | 0,0 % |
| 6.40 mit Wächter je Modul (wie 6.30) | 9,65 (37,9) | 238 $ | 0 | 1780 $ | 1,04 | 7,2 / 12 | 64,4 % | 273 $ | 0,0 % |
| 6.40 mit Mindestgewinn 3 % | 7,77 (47,0) | 339 $ | 0 | 2045 $ | 0,93 | 7,2 / 12 | 65,4 % | 245 $ | 0,0 % |
| 6.40, GFT bucht 1 Tag schneller | 11,47 (31,8) | 233 $ | 0 | 2075 $ | 0,95 | 7,4 / 10 | 65,3 % | 252 $ | 0,0 % |
| 6.40, GFT bucht 1 Tag später | 10,91 (33,5) | 232 $ | 0 | 1967 $ | 0,75 | 6,6 / 10 | 65,7 % | 261 $ | 0,0 % |
| 6.30 Sicher | 4,13 (88,4) | 350 $ | 0 | 1123 $ | 0,05 | 4,8 / 9 | 70,4 % | 209 $ | 0,6 % |
| **6.40 Sicher** (mit Abschluss-Ernte) | **7,11 (51,4)** | 222 $ | 0 | 1225 $ | **0,02** | 4,8 / 6 | 69,3 % | 253 $ | 0,0 % |
| 6.40 Sicher ohne Abschluss-Ernte | 6,50 (56,2) | 246 $ | 0 | 1239 $ | 0,04 | 4,8 / 6 | 68,5 % | 246 $ | 0,0 % |

Streuung über die 16 Störungen: 6.40 Ertrag 12,06 ± 0,62 Auszahlungen mit GFT-nahen, 11,25 ± 0,73 mit breiten Spreads
(6.30: 7,33 ± 0,32). Der Abstand liegt weit über der Streuung. Die Störungen bilden nur Ausführung und Kosten ab, nicht
einen anderen Marktverlauf.

**Fremddaten 2006–2021** (anderes Regime; jeder dritte Tag):

| Variante | Ausz./J | Busts/J | Bust im 1. Jahr | Netto | Serien ≥ 6 | Treffer | kleinster Abstand zum Boden Ø |
|---|---:|---:|---:|---:|---:|---:|---:|
| 6.30 Ertrag | 1,83 | 0,347 | 29,2 % | 481 $ | 2,47 | 51,1 % | 38 $ |
| **6.40 Ertrag** | **2,16** | **0,035** | **0,9 %** | 364 $ | **2,21** | 48,2 % | **207 $** |
| 6.40, PF200 > 1,1 | 2,12 | 0,039 | 1,3 % | 358 $ | 2,41 | 48,3 % | 184 $ |
| 6.40, PF200 > 1,2 | 2,14 | 0,023 | 0,1 % | 364 $ | 2,16 | 48,0 % | 218 $ |
| 6.40 mit Wächter je Modul (wie 6.30) | 1,82 | 0,004 | 0,0 % | 307 $ | 2,43 | 50,1 % | 170 $ |
| 6.40 mit Mindestgewinn 3 % | 1,30 | 0,045 | 1,8 % | 343 $ | 2,30 | 48,4 % | 199 $ |
| 6.30 Sicher | 0,48 | 0,228 | 16,3 % | 97 $ | 0,31 | 59,2 % | 79 $ |
| **6.40 Sicher** (mit Abschluss-Ernte) | 0,25 | **0,000** | 0,0 % | 49 $ | 0,21 | 54,8 % | 377 $ |

- Im alten Regime verdienen die Fades nichts. 6.40 lässt sie dort seltener handeln als 6.30.
- Den größten Teil des Rückgangs bringt die Pufferkurve: Mit der Kurve von 6.30 hätte 6.40 dort 0,274 Busts je Jahr, mit
  dem ersten Entwurf 0,121, mit der 6.40-Kurve 0,035 (Abschnitt 3.4).
- Die Trefferquote sinkt dort, weil die treffsicheren Fades seltener handeln (48,2 statt 51,1 %).

### 3.6 Mindestgewinn: Größe gegen Takt

Mit 6.40 lässt sich über `MinProfitPct` wählen, ob größere oder häufigere Auszahlungen wichtiger sind. Screening
(breite Spreads, 8 Störungen), Busts in allen Stufen 0:

| `MinProfitPct` | 0 (GFT-Minimum 131 $) | 1,5 | 2,0 | 2,5 | 3,0 |
|---|---:|---:|---:|---:|---:|
| Auszahlungen je Jahr | 11,15 | 10,79 | 9,74 | 8,82 | 7,64 |
| Tage je Auszahlung | 32,8 | 33,9 | 37,5 | 41,4 | 47,8 |
| Auszahlung im Mittel | 235 $ | 242 $ | 265 $ | 300 $ | 339 $ |
| Netto je Jahr | 2030 $ | 2025 $ | 2005 $ | 2054 $ | 2009 $ |

Netto je Jahr bleibt in allen Stufen gleich. Mit GFT-nahen Spreads sind die Tage je Auszahlung jeweils etwa 2 Tage kürzer
(Stufe 0: 30,3 statt 32,5 Tage in der Endbewertung).

### 3.7 Nach Startjahr (1-Jahres-Konten)

Zellen: Auszahlungen je Jahr (Tage je Auszahlung) · Netto · Serien ≥ 6 · Trefferquote. Busts in allen Zellen 0.

| Variante | Start 2022 | Start 2023 | Start 2024 | Start 2025 ⁽*⁾ |
|---|---|---|---|---|
| 6.30 Ertrag, GFT-nah | 9,35 (39,1) · 3144 $ · 0,56 · 69,6 % | 9,55 (38,3) · 2851 $ · 1,08 · 66,8 % | 5,64 (64,7) · 1561 $ · 0,10 · 63,4 % | 5,32 (68,6) · 1438 $ · 0,00 · 65,5 % |
| **6.40 Ertrag, GFT-nah** | **13,02 (28,1)** · 2585 $ · 1,00 · 68,4 % | **13,87 (26,3)** · 2650 $ · 0,53 · 68,5 % | **8,78 (41,6)** · 1439 $ · 0,86 · 61,9 % | **9,79 (37,3)** · 1709 $ · 0,70 · 65,1 % |
| 6.30 Ertrag, breit | 8,46 (43,2) · 2743 $ · 0,77 · 68,3 % | 8,20 (44,6) · 2393 $ · 1,66 · 64,9 % | 5,10 (71,6) · 1399 $ · 0,30 · 62,7 % | 4,42 (82,6) · 1216 $ · 0,29 · 64,2 % |
| **6.40 Ertrag, breit** | **12,14 (30,1)** · 2368 $ · 1,08 · 67,4 % | **12,45 (29,3)** · 2360 $ · 0,48 · 67,3 % | **8,83 (41,4)** · 1405 $ · 1,02 · 62,2 % | **8,73 (41,8)** · 1335 $ · 1,63 · 64,0 % |
| 6.40 Sicher, GFT-nah | 7,77 (47,0) · 1578 $ | 8,92 (40,9) · 1760 $ | 6,46 (56,5) · 1049 $ | 7,50 (48,7) · 1418 $ |

⁽*⁾ Die Ersatzdaten enden am 31.12.2025, deshalb gibt es für Start 2025 nur wenige Konten.

Seit 2024 verdienen die Fades auf dem Ersatz weniger (schwächerer Vorteil). 6.40 zahlt dann etwa alle 6 Wochen aus, 6.30
alle 9–12 Wochen. 2022–23 sind es etwa 4 Wochen.

## 4. Was 6.40 ändert

| Eingabe | 6.30 | **6.40** | Bedeutung |
|---|---:|---:|---|
| `MinProfitPct` | 3,0 | **0,0** | Mindestgewinn in % (0 = nur GFT-Mindestauszahlung: 105 $ Anteil = 131,25 $ Gewinn) |
| `AbschlussLetzte` | 3 | **5** | Abschluss-Ernte, sobald höchstens X gültige Tage fehlen (≥ 5 = immer) |
| `FadeT1R` | 0,6 | **0,0** | Fade-Teilgewinn aus (wie 6.20) |
| `NzRiskPct` | 0,35 | **0,45** | Risiko je Noise-Signal |
| `DDFullPct` | 4,0 | **5,0** | volle Größe ab X % Puffer zum Boden (Puffer an der Spitze: 6 %) |
| `DDMinPct` | 1,5 | **2,5** | bei X % Puffer und darunter gilt `DDMinFactor` |
| `DDMinFactor` | 0,6 | **0,2** | kleinster Größenfaktor |
| `PeakUnsicherFaktor` (neu) | – | **0,6** | Größenfaktor, solange die Equity-Spitze nicht sicher rekonstruiert ist (bis 6.30: `DDMinFactor` 0,6) |
| `GueltigSchutz` (neu) | – | **true** | heute gültig und dem Zyklus fehlen (ohne heute) gültige Tage: keine neuen Einstiege bis 17:00 NY |
| `FadeWaechterModus` (neu) | – | **1** | 1 = Portfolio-Wächter, 0 = je Modul (`FadeWaechterN/PF/Min` wie 6.00–6.30) |
| `FadePortN` (neu) | – | **200** | Zahl der letzten virtuellen Fade-Signale (alle Module, innerhalb `FadeHistTage`) |
| `FadePortPF` (neu) | – | **1,15** | Fades live nur bei Profitfaktor > X (0 = Wächter aus) |

Verhalten:

- **Pufferkurve:**
  - Gilt wie bisher für alle Module (DEADBAND, RSI21, Noise, Fades), bezogen auf den Puffer zwischen Equity und Boden.
  - Nach einer Auszahlung beginnt der Puffer wieder bei 6 %, die Größe also bei ×1,0.
  - Größenfaktor bis 1 % Rückgang ×1,0, bei 2 % Rückgang ×0,68, bei 3 % ×0,36, ab 3,5 % ×0,2.
  - Liegt das Mindestlot dann über dem Doppelten des Sollrisikos, lässt der EA den Einstieg wie bisher aus
    (`MinLotRiskTol` 2), sonst handelt er das Mindestlot. Das Replikat rechnet genauso.
- **Schutz gültiger Tage:**
  - Gilt für neue Einstiege von RSI21, Noise, Fades und DEADBAND.
  - Offene Positionen, Stops, Ziele, Ernten, Ausstiege und Wochenend-Wiederaufnahmen laufen weiter. RSI21-Signale werden
    weiter als Erstsignal gemerkt.
  - „Heute gültig“ heißt: realisiert heute ≥ 50,50 $, in beiden Kommissions-Lesarten wie bei der Reife. Eine eigene Ernte
    zählt schon, bevor ihre Deals in der Historie stehen (30 s).
  - Der EA prüft den Schutz vor jedem Modul neu. Hat sich seit dem letzten Laden eine Position geändert (eigener Ausstieg,
    Stop, Ziel), lädt er die Deals vorher neu.
  - Journal: `SCHUTZ GUELTIGER TAG - heute realisiert … keine neuen Einstiege bis 17:00 NY`.
  - Bei ausgelassenen Signalen steht der Grund im Journal: `Tag schon gueltig (…), noch n gueltige Tage bis zur Auszahlung`.
- **Portfolio-Wächter:**
  - Jedes virtuelle Fade-Ergebnis bekommt den Zeitpunkt, ab dem es feststeht (Ende der Kerze).
  - Bei einem Signal zählen die letzten 200 Ergebnisse aller Module, die vor der Einstiegskerze feststanden. Sie dürfen
    nicht älter als `FadeHistTage` (600 Tage) sein und nicht vor dem Historienbeginn eines Moduls liegen.
  - Fehlen Signale oder ist die Historie eines Moduls noch nicht geladen, handeln die Fades nur virtuell.
  - Beim Start meldet das Journal `FADE Portfolio-Waechter: PF … aus den letzten 200 virtuellen Signalen aller 10 Module
    -> Fades LIVE / nur virtuell`.
  - Das Panel zeigt den Wert in der Zeile „Fade-Module“ (der PF je Modul steht dort nur zur Information).
  - `FADEHIST` ist jetzt 256 (bisher 64), damit der Ringpuffer jedes Moduls das ganze Fenster fassen kann.
- **Panel:** Zeile „Auszahlungstakt“ (Mindestgewinn, Ernte, Schutz, Wächter, Pufferkurve). Im Status steht
  „TAG GUELTIG - keine neuen Einstiege bis 17:00 NY“, solange der Schutz greift.
- **Rückweg zu 6.30** im selben EA:
  - `MinProfitPct=3`, `AbschlussLetzte=3`, `FadeT1R=0.6`, `NzRiskPct=0.35`, `DDFullPct=4`, `DDMinPct=1.5`,
    `DDMinFactor=0.6`, `GueltigSchutz=false`, `FadeWaechterModus=0` (`PeakUnsicherFaktor` 0,6 entspricht 6.30).
  - Oder `rollback_6.30/` (mq5 und beide Sets).
  - Achtung: Ein 6.30-Set in den 6.40-EA geladen lässt die fünf neuen Eingaben auf den 6.40-Werten.

## 5. Prüfung

- **Replikat eng8 = eng7** mit ausgeschalteten 6.40-Regeln (`t_eng8.py`): alle Zähler, Trades und Ereignisse identisch
  (6.30 Ertrag, 6.30 Sicher, je 15 Konten).
- **Baseline reproduziert:** Die Kursdaten wurden aus den Quellen neu aufgebaut. Alle fünf Dateien sind byte-identisch mit
  dem Datenbericht. Das Replikat rechnet 6.30 exakt wie im 6.30-Bericht: 7,33 / 0 / 2171 $ / 0,96 / 65,0 % und
  1,83 / 0,347 / 481 $.
- **GFT-nahe Spreads:** `mk_proxy.py` mit `SPREAD_FAKTOR=0.6` in einer Kopie des Ordners (eigene `data/` und `cache/`),
  sonst dieselben Daten und Regeln.
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
  - Die Pufferkurve (`DDFaktor`) ist dieselbe Formel wie im Replikat (`_ddf`, auch für die Fades) und unverändert; neu sind
    nur die Werte.
- **Presets** (`t_set.py`): `DEADBAND_LIVE4_Echtbetrieb.set` enthält alle 224 Eingaben mit genau den Voreinstellungen des
  EA. Das Sicher-Set weicht nur in `R21Aktiv`, `NzAktiv` und `SerienStopp` ab.
- **Statische Prüfung** (`t_mq5.py`): Klammern, Format-Argumente, Deklarationen vor der Verwendung – bestanden.
- **Gegenlesen** der EA-Änderungen durch einen Sub-Agenten. Keine Kompilierfehler gefunden; Portfolio-Wächter gleich
  `pg_guard.port_live_ea`. Sieben Befunde, alle behoben:
  1. *Mittel:* Der Schutz gültiger Tage wurde nur einmal je Durchlauf bestimmt, auf Deals, die nur alle 5 s neu geladen
     werden. Ein Ausstieg, der den Tag eben gültig macht, hätte Einstiege anderer Module im selben Durchlauf und einige
     Sekunden danach nicht gesperrt. → Prüfung vor jedem Modul, Deals neu laden nach jeder Positionsänderung.
  2. `DDMinFactor` hätte auch den Faktor bei unsicherer Equity-Spitze gesenkt (nach einem Neustart unter Umständen
     tagelang). → eigene Eingabe `PeakUnsicherFaktor` 0,6 wie bis 6.30.
  3. Mit `KontoAb20260730=false` hätte `MinProfitPct` 0 den Mindestgewinn auf 0 $ gesetzt. → Untergrenze
     `MinPayoutUSD`/`ProfitSplit` in jedem Fall (`MinGewinnAuszahlung`).
  4. Ist die M5-Historie eines Symbols kürzer als `FadeHistTage`, hätten alte Ergebnisse der anderen Module den PF
     verzerrt. → Das Fenster beginnt frühestens einen Tag nach dem spätesten Historienbeginn.
  5. `FadePortPF` 0 schaltet den Wächter ganz aus (auch vor dem Laden der Historie). → dokumentiert.
  6. Texte im Panel und Journal (PF je Modul im Portfolio-Modus, „bei <=“). → angepasst.
  7. Das Panel rechnete den Portfolio-PF je Modul neu. → einmal je Aufruf.
  - **Offen, bewusst:** Im selben Durchlauf handelt der EA RSI21 vor Noise. Macht ein Noise-Ausstieg zur vollen Stunde den
    Tag gültig und kommt in derselben Sekunde ein RSI21-Signal, öffnet der EA es noch, das Replikat nicht. Ab dem nächsten
    Tick greift der Schutz. Das Umstellen der Reihenfolge hätte die Noise-Verwaltung aufgetrennt; der Fall ist selten.
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
   - beim Start `6.40 Auszahlungstakt | Mindestgewinn 131.25 $ … | Pufferkurve voll ab 5.0 %, x0.20 bei <= 2.5 % Puffer`
     und `FADE Portfolio-Waechter: PF … -> Fades LIVE`,
   - Fade-Einstiege ohne `Teilgewinn`,
   - nach einem gültigen Tag `SCHUTZ GUELTIGER TAG …`, danach keine neuen Einstiege bis 17:00 NY (Ausstiege laufen),
   - `ABSCHLUSS-ERNTE …` auch dann, wenn noch 4–5 gültige Tage fehlen,
   - nach einem Rückgang von mehr als 1 % kleinere Einstiege (Fade und Noise: `Puffer … % x…` in der Einstiegszeile),
   - `AUSZAHLUNGSREIF`, sobald 5 gültige Tage, 10 Tage und 131,25 $ Gewinn erreicht sind.
4. Eine Woche auf einem Demokonto mit gleicher Serverzeit, dann live nur auf dem eigenen PC, EIN Chart.
5. **Auszahlung sofort beantragen,** sobald der EA „JETZT AUSZAHLUNG BEANTRAGEN“ meldet (Push). Danach
   `AuszahlungAngefordertAm` setzen. Jeder Tag Verzögerung verlängert den Takt um rund einen Tag (Replikat, breite
   Spreads: 33,5 statt 32,5 Tage bei einer Buchung einen Tag später).

## 7. Grenzen und Hinweise

1. **Kein GFT-Datentest.** Alle Konto-Zahlen stammen vom GFT-Ersatz aus Fremddaten (Daten bis 31.12.2025), einmal mit
   GFT-nahen, einmal mit breiten Spreads. Welche Rechnung GFT näher kommt, klären erst die GFT-Exporte: Dateien nach
   `data/`, dann `python prep5.py && python sig5.py` und `python x46.py gft`. Liegen die echten Kosten näher an den breiten
   Spreads, sind es rund 32,5 statt 30,3 Tage.
2. **Takt nach Marktphase:** Die 30,3 Tage sind ein Mittel über 2022–2025. Bei Start 2024/2025 waren es 37–42 Tage
   (Abschnitt 3.7). In einem Regime wie 2006–21 wären es rund 170 Tage (6.30: 200).
3. **Kleinere Auszahlungen, etwas weniger Netto:** im Mittel 239 $ statt 391 $ Gewinn und 6–11 % weniger Netto je Jahr.
   Wer größere Auszahlungen will, setzt `MinProfitPct` (Abschnitt 3.6). Ab 2 % liegt der Takt bei etwa 37 Tagen
   (breite Spreads).
4. **Noch sicherer, aber langsamer:** `FadeWaechterModus=0` (Wächter je Modul wie 6.30) mit sonst allen 6.40-Regeln.
   Im alten Regime 0,004 Busts je Jahr, heute weiter vom Boden weg, aber alle 33,7 Tage (GFT-nah) bzw. 37,9 Tage (breit)
   eine Auszahlung.
5. **Bust-Risiko:**
   - Auf dem GFT-Ersatz 0 Busts wie 6.30. Kein Konto kam dem Boden näher als 100 $; im Mittel so weit wie bei 6.30
     (GFT-nah) bzw. 40 $ weiter weg (breit).
   - Auf den Fremddaten ein Zehntel der Busts von 6.30.
   - Die Pufferkurve trägt das. Sie nicht lockern: Mit der Kurve des ersten Entwurfs oder der von 6.30 kamen im März 2025
     6–12 % der Konten dem Boden auf < 100 $ nahe.
   - Die Kurve senkt die Größe schon ab 1 % Rückgang. Nach einer Verlustserie dauert es deshalb länger, bis das Konto
     wieder voll handelt. Das ist gewollt.
6. **Wächter-Wahl:** PF200 > 1,15 liegt zwischen den geprüften Nachbarn > 1,1 und > 1,2. Beide liefern ebenfalls rund 11
   Auszahlungen ohne Busts (breite Spreads). Aus mehreren Varianten gewählte Punkte sind eher etwas optimistisch; die
   Pufferkurve wurde deshalb mit 16 Störungen in beiden Spread-Lagen gewählt, nicht nach einem einzelnen Ergebnis.
7. **Schwächstes Modul:** X1000S verliert auf dem Ersatz mit Portfolio-Wächter rund 70 $ je Jahr (6.30: +14 $). Es wurde
   nicht abgeschaltet, weil das eine Auswahl nach dem Ergebnis wäre. Wer es abschalten will: `FadeAus=X1000S`.
8. **Inaktivität bei „Sicher“:** Schaltet der Portfolio-Wächter die Fades ab (anderes Regime), handelt „Sicher“ womöglich
   wochenlang nicht. GFT: 30 Tage ohne Trade = Konto weg. Kommt der Push nach 20 Tagen ohne Einstieg, von Hand einen kleinen
   Trade setzen.
9. **Tick gegen Kerze:** Das Replikat prüft den Schutz gültiger Tage und die Abschluss-Ernte je M5-Kerze, der EA laufend.
   Der EA kann einen Tag deshalb etwas früher gültig machen und schützen. Umgekehrt der seltene Fall aus Abschnitt 5
   (RSI21 und Noise in derselben Sekunde).
10. **Nicht kompiliert, nicht im Tester** (Abschnitt 5).
11. **Lizenz** des Grid-Konzepts unverändert (Bericht 6.20, Abschnitt 10).

## Anhang: Replikat

`Replikat_v6/README.md` (Abschnitt Build 6.40):

- Motor: `eng8.py`, Bewertung: `evl8.py`
- Wächter-Studie und Portfolio-Wächter: `pg_guard.py`
- Screening: `x44.py`, Zwischenbewertung: `x45.py`, Wächter-Formen und Pufferkurven: `x47.py`, Endbewertung: `x46.py`
- Beinahe-Busts je Störung und Monat: `nb_diag.py`
- Prüfungen: `t_eng8.py`, `t_port_640.py`, `t_set.py`, `t_mq5.py`
- Ergebnisse: `ergebnisse/x44_*.json`, `x45_*.json`, `x46_*.json` (GFT-nah: `x46_gft_spread06.json`), `x47_*.json`,
  `pg_guard.txt`, `t_port_640.txt`
- Kursdaten: `extdata/scripts/run_all.sh` baut die Fremddaten neu, `Replikat_v6/mk_proxy.py` den GFT-Ersatz
  (`SPREAD_FAKTOR=0.6` für GFT-nahe Spreads).
