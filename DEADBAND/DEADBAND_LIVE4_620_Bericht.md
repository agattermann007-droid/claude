# DEADBAND LIVE 4 – Build 6.20 GRID

Bericht vom 24.09.2026 · GFT Instant Premium 10k (Konto ab 02.09.2026)

## 1. Kurzfassung

Auftrag: die Strategie mit dem Konzept des TradingView-Indikators **„Probability Grid“ (LuxAlgo)** verbessern und
mit den Parametern experimentieren.

Das Konzept: Aus den bisherigen Schwüngen (Pivot → Pivot) eine Statistik bilden, wie weit und wie lange ein
Schwung üblicherweise läuft, und daraus ablesen, **mit welcher Wahrscheinlichkeit der laufende Schwung noch über
ein bestimmtes Niveau hinausgeht**. Für DEADBAND passt das genau zu den Fehlausbruch-Fades: Ein Fade setzt darauf,
dass der Schwung, der gerade über die Range-Kante gelaufen ist, umkehrt – und sein Stop liegt hinter dem Extrem.

**Build 6.20** nutzt das Grid als Filter für die Fades (Regel S):

> Läuft ein Fade **gegen** den laufenden M5-Schwung und liegt die Grid-Chance, dass dieser Schwung noch **bis zum
> Stop** weiterläuft, bei **70 % oder mehr**, entfällt das Signal – auch virtuell für den Regime-Wächter.

Alles andere bleibt wie 6.10 (RSI21, Noise, Budget, Kontoerkennung, Auszahlungslogik). Ausnahme vom Filter: N1800
(Abschnitt 5.3).

**Ergebnis** im Konto-Replikat mit allen GFT-Regeln (Abschnitt 5). Gerechnet auf einem GFT-Ersatz aus Fremddaten
2022–2025, weil die GFT-Exporte fehlten; der Wächter arbeitet wie im EA:

| Kennzahl je Jahr | 6.10 Ertrag | **6.20 Ertrag** (Echtbetrieb) | 6.20 Ertrag `GridNurLive` | 6.10 Sicher | **6.20 Sicher** |
|---|---:|---:|---:|---:|---:|
| Auszahlungen | 6,42 | **7,34** | 6,78 | 3,02 | **4,12** |
| Busts | 0,195 | **0,032** | 0,130 | 0,001 | **0,000** |
| Netto | 1877 $ | **2152 $** | 1979 $ | 835 $ | **1162 $** |
| Serien ≥ 6 Verluste | 0,75 | **1,45** | 0,86 | 0,27 | **0,24** |
| längste Serie Ø / max | 7,2 / 10 | 7,6 / **13** | 7,3 / 10 | 5,2 / 7 | 5,5 / **10** |
| Fremddaten 2006–21: Ausz. · Busts · Netto | 1,99 · 0,360 · 511 $ | 1,97 · 0,395 · 497 $ | 1,96 · 0,355 · 499 $ | 0,49 · 0,261 · 98 $ | 0,43 · 0,246 · 82 $ |

1. **Mehr Auszahlungen, weniger Busts auf 2022–25.** „Ertrag“ bringt +0,9 Auszahlungen je Jahr, „Sicher“ +1,1, und
   zwar in jedem Startjahr von 2022 bis 2025. Die Busts in „Ertrag“ fallen von 0,20 auf 0,03 je Jahr. Der Abstand
   liegt weit über der Streuung der 16 Störungen. Auch die Nachbar-Einstellungen (65/75 %, Swing Length 10/20,
   500 Schenkel) schlagen 6.10.
2. **Der Preis: mehr lange Verlustserien in „Ertrag“.** Serien ≥ 6 kommen 1,45-mal statt 0,75-mal je Jahr vor, die
   längste Serie erreicht 13. Ursache: Der Wächter sieht den gefilterten Strom und lässt die schwächeren Gold-Module
   (X0300S, X0400) öfter live. Mit **`GridNurLive=true`** bleiben die Serien wie in 6.10 (0,86). Dann bleibt gut ein
   Drittel des Zusatz-Ertrags (+0,36 Auszahlungen, Busts 0,13).
3. **Altes Regime (2006–21): neutral.** Dort verdienen die Fades nichts. 6.20 Ertrag hat 0,035 Busts je Jahr mehr
   (etwa 2 Standardfehler), `GridNurLive` liegt gleichauf mit 6.10. „Sicher“ hat weniger Busts, aber auch etwas
   weniger Ertrag.
4. **N1800 läuft ohne Grid** (`GridOhne`). Mit Grid bliebe N1800 unter der Mindestzahl des Wächters und liefe im EA
   nie live. Das hat erst das Gegenlesen gezeigt (Abschnitte 5.3 und 7.1).
5. **Was fehlt:** der Test auf den echten GFT-Kursen, das Kompilieren in MetaEditor, der Strategietester und die Demo.
   Bei den engeren GFT-Spreads ist ein kleinerer Vorteil zu erwarten (Abschnitt 4.4).

**Die Anforderungen ehrlich bewertet:**

- 10 Auszahlungen je Jahr erreicht auch 6.20 im Mittel nicht: 7,3, im Startjahr 2022 8,6.
- Busts: 0,03 je Jahr auf 2022–25, aber nicht 0 auf 2006–21.
- Serien über 5 Verluste: in „Ertrag“ häufiger als in 6.10. Wer das stärker gewichtet, nimmt `GridNurLive=true`
  oder „Sicher“ (0,24 je Jahr, längste Serie bis 10).

## 2. Datenlage

Die GFT-Exporte (`data/XAUUSD.x_M5.csv`, `data/NAS100.x_M5.csv`) liegen nicht im Repository und waren in dieser
Sitzung nicht verfügbar. Deshalb:

- **Fremddaten neu aufgebaut** mit `extdata/scripts` (Dukascopy, OANDA, HistData, MT5-Broker-Exporte). Alle fünf
  Dateien sind **byte-identisch** mit dem Datenbericht (SHA-256 `8532e33b…`, `dfef735d…`, `1dad5a98…`, `ab243548…`,
  `dd403ce3…`).
- **GFT-Ersatz 2022–2025** (`Replikat_v6/mk_proxy.py`): dieselben Fremddaten ab 03.01.2022 bis 31.12.2025 (dort
  endet die NAS-Reihe), Spread = max(Datei, GFT-typischer relativer Spread). Die Spreads liegen damit **über**
  denen der GFT-Exporte (Gold Median 36 statt 7–32 Punkte, NAS 195 statt 100–163) – der Ersatz ist härter. Auch die
  Basis 6.10 hat auf ihm Busts (0,20 je Jahr statt 0,00 auf den GFT-Daten).
- **Kontrollrechnung:** 6.10 auf den Fremddaten 2006–21 ergibt 1,99 Auszahlungen / 0,34 Busts / 511 $ je Jahr
  (Bericht 6.10: 2,02 / 0,40 / 503 $). Nicht bitgenau (andere numpy/numba-Versionen im neuen Container), aber im
  Rahmen der Streuung. **Alle Vergleiche unten laufen gegen die hier neu gerechnete Basis 6.10.**

Absolute Zahlen auf dem Ersatz sind daher **nicht** mit den GFT-Zahlen früherer Berichte vergleichbar; belastbar ist
der Vergleich 6.10 ↔ 6.20 auf denselben Daten.

## 3. Das Konzept und seine Übertragung

### 3.1 Probability Grid (LuxAlgo)

- **Schwung-Erkennung:** Kerzenkörper (Maximum/Minimum aus Open und Close). Ist der Körper-Hochpunkt der höchste der
  letzten *Swing Length* Kerzen, läuft der Markt aufwärts, ist der Körper-Tiefpunkt der tiefste, abwärts (aufwärts
  hat Vorrang). Wechselt die Richtung, ist der bis dahin erreichte Extrempunkt ein bestätigter Pivot.
- **Schenkel:** vom vorigen zum neuen Pivot, mit Größe (|Differenz| / Preis des vorigen Pivots) und Dauer (Kerzen),
  getrennt nach steigend und fallend, je Richtung die letzten *Maximum Reversals* (1000).
- **Grid:** Perzentile von Größe und Dauer ab dem letzten Pivot; „Beyond“-Wahrscheinlichkeit einer Zelle =
  (1 − Perzentil Größe) × (1 − Perzentil Dauer).

Der Nachbau (`Replikat_v6/pgrid.py`) ist gegen eine wörtliche Übertragung der Pine-Funktionen `fetchPivot` und
`fetchData` geprüft (`t_pgrid.py`, Zufallskurse mit vielen Gleichständen): **identische Pivots und Schenkel.**

### 3.2 Was an einem Fade-Signal gemessen wird

Zum Einstieg (Beginn der Kerze nach der Signalkerze, nur abgeschlossene Kerzen):

| Merkmal | Bedeutung |
|---|---|
| Ausrichtung | Fade in Richtung des laufenden Schwungs oder dagegen (auf M5 laufen je nach Swing Length 91–97 % der Fades dagegen) |
| Reife `p_ext` | Anteil der Schenkel gleicher Richtung, die kleiner sind als der Lauf bisher (Perzentil) |
| Reife `p_bar` | dasselbe für die Dauer |
| `beyond` | (1 − p_ext)(1 − p_bar) – die Grid-Wahrscheinlichkeit des Indikators |
| Zielweg | Perzentil des Wegs vom Extrem zum Fade-Ziel unter den Schenkeln in Fade-Richtung |
| **Stop-Chance** | Anteil der Schenkel, die über die Größe **bis zum Stop** hinausgehen, geteilt durch den Anteil über der bisherigen Größe = Grid-Chance, dass der Lauf bis zum Stop weiterläuft (bedingte Wahrscheinlichkeit) |

## 4. Vorstudie: alle Fade-Signale 2006–2025

Alle virtuellen Signale der 10 Fade-Module (6 856 Signale; ohne Wächter), Fremddaten durchgehend, vier Perioden.
Zellen: Signale · Trefferquote · R je Signal · Profitfaktor (`pg_study.py`).

### 4.1 Zeitebene und Reife

Fades gegen den laufenden Schwung, nach Reife des Schwungs (Grid auf M5, Swing Length 20):

| Reife des Laufs (p_ext) | 2006–13 | 2014–21 | 2022–23 | 2024–25 |
|---|---|---|---|---|
| jung (< 33 %) | 365 · 49 % · −0,20 · PF 0,58 | 495 · 51 % · −0,19 · PF 0,59 | 106 · 63 % · −0,05 · PF 0,86 | 107 · 56 % · −0,04 · PF 0,91 |
| mittel | 783 · 57 % · −0,04 · PF 0,90 | 979 · 54 % · −0,06 · PF 0,86 | 275 · 61 % · +0,06 · PF 1,18 | 281 · 67 % · +0,12 · PF 1,39 |
| reif (≥ 67 %) | 1028 · 58 % · +0,01 · PF 1,03 | 976 · 53 % · −0,09 · PF 0,78 | 357 · 66 % · +0,19 · PF 1,67 | 339 · 62 % · +0,12 · PF 1,41 |
| alle Signale | 2389 · 57 % · −0,04 · PF 0,89 | 2689 · 54 % · −0,10 · PF 0,76 | 815 · 65 % · +0,11 · PF 1,36 | 792 · 65 % · +0,10 · PF 1,34 |

Einen **jungen** Schwung zu faden ist in **allen vier Perioden** das Schlechteste: Der „Fehlausbruch“ ist dann oft
der Beginn eines echten Laufs. Auf M15 ist das Muster schwächer, auf H1 verschwindet es. Die Stop-Chance zeigt
dasselbe noch deutlicher (Stop-Chance ≥ 75 %: PF 0,56 / 0,64 / 0,75 / 0,99).

### 4.2 Parameter-Raster

`pg_scan.py`: Zeitebene M5/M10/M15, Swing Length 10–40, Maximum Reversals 200/500/1000, je drei Regeln mit fünf
Schwellen. Gemessen als Änderung der Summe R je Jahr gegenüber allen Signalen:

| Regel (Grid M5) | 2006–13 | 2014–21 | 2022–23 | 2024–25 | R je Signal 2022–25 |
|---|---:|---:|---:|---:|---:|
| A: kein Fade gegen jungen Lauf (p_ext < 33 %), Länge 20 | +9,3 | +11,6 | +2,5 | +2,0 | 0,104 → 0,126 |
| **S: kein Fade bei Stop-Chance ≥ 70 %, Länge 15** | **+7,1** | **+6,7** | **+7,6** | **+6,9** | **0,104 → 0,138** |
| S: Stop-Chance ≥ 70 %, Länge 20 | +8,8 | +9,9 | +2,5 | +0,3 | 0,104 → 0,130 |
| B: beyond > 0,3 (Wahrscheinlichkeit des Indikators) | +8,1 | +12,6 | −3,8 | −5,8 | – |

Die „Beyond“-Wahrscheinlichkeit des Indikators selbst filtert zu grob (kostet 2022–25 Ertrag). Die bedingte
**Stop-Chance** trifft den Kern: Sie fragt nicht „wie weit läuft ein Schwung üblicherweise“, sondern „wie oft läuft
ein Schwung, der **schon so weit** gekommen ist, noch **bis zu meinem Stop**“.

### 4.3 Grid-Ziele, RSI21, Noise

- **Grid als Ziel** statt Range-Mitte (Perzentil 20–70 des Umkehr-Schenkels, „nur näher“ oder „immer“): 2022–25
  durchweg schlechter (PF 1,09–1,33 statt 1,36) → verworfen.
- **RSI21 und Noise** (Trendfolge): RSI21-Signale entstehen per Definition in reifen Läufen (fast alle im obersten
  Drittel), Noise zeigt kein über die Perioden stabiles Muster (`pg_study_old.py`) → unverändert.

### 4.4 Kostenabhängigkeit

Die von Regel S ausgelassenen Signale sind bei **jedem** Spread-Niveau Verlierer (`pg_spread.py`):

| Spread × | ausgelassene Signale: PF 2006–13 / 2014–21 / 2022–23 / 2024–25 | alle → Regel S, PF 2022–25 |
|---|---|---|
| 0,3 (enger als GFT) | 0,77 / 0,89 / 0,94 / 0,93 | 1,55 → 1,67 · 1,51 → 1,65 |
| 0,6 | 0,71 / 0,77 / 0,78 / 0,78 | 1,46 → 1,60 · 1,41 → 1,58 |
| 1,0 (Ersatz) | 0,60 / 0,67 / 0,63 / 0,73 | 1,36 → 1,51 · 1,34 → 1,51 |

Der Filter ist also kein Kosten-Artefakt. Bei den engeren GFT-Spreads fällt der Vorteil aber **kleiner** aus.

### 4.5 Wirkung je Modul (Regel S, virtuelle Signale)

| Modul | ausgelassen 2022–25 | PF 2022–25 vorher → nachher | R/J 2022–25 | R/J 2006–21 |
|---|---:|---|---|---|
| N1030 | 15 % | 1,84 → 2,13 | +8,1 → +8,4 | −1,7 → −1,9 |
| N1330 | 1 % | 1,68 → 1,80 | +4,8 → +5,3 | −1,6 → −1,6 |
| X0630 | 0 % | 1,24 → 1,24 | +4,1 → +4,1 | +0,3 → +0,4 |
| X0400 | 11 % | 1,15 → 1,27 | +2,4 → +3,6 | −6,4 → −5,1 |
| N1800 | 60 % | 1,31 → 1,78 | +2,4 → +2,0 | −1,5 → −0,5 |
| N0930 | 5 % | 1,57 → 1,73 | +4,7 → +5,5 | −1,1 → −1,2 |
| N1100 | 1 % | 1,51 → 1,47 | +7,1 → +6,4 | +0,3 → +0,4 |
| N1300 | 2 % | 1,60 → 1,75 | +5,4 → +6,2 | −1,0 → −1,1 |
| X0300S | 32 % | 1,02 → 1,38 | +0,4 → +4,7 | −8,3 → −3,6 |
| X1000S | 6 % | 1,26 → 1,35 | +2,2 → +2,8 | −1,7 → −1,5 |

Der Filter wirkt vor allem dort, wo der Stop eng am Extrem liegt (Puffer 0,3 × Range: N1800, X0300S, X0400, N1030).
Module mit weitem Stop (X0630, N1330, N1100) bleiben fast unberührt.

## 5. Konto-Replikat (alle GFT-Regeln)

Kontomotor wie in 6.10 (`eng6`/`evl6`): alle GFT-Regeln (Auszahlung ab 3 % = 300 $, gültiger Tag ab 50,50 $,
Floating-Verlust −1 %, Trailing-Drawdown 6 %), rollierende Konten über 1, 2 und 3 Jahre, 16 Störungen (Ausführung und
Kosten), Kennzahlen je Konto und Jahr. GFT-Ersatz 2022–2025: an jedem Handelstag startet ein neues Konto; Fremddaten
2006–21: an jedem dritten. Ein vom Grid gesperrtes Signal entfällt ganz, auch für den Regime-Wächter. Der Wächter
bewertet damit den gefilterten Strom.

### 5.1 Screening der Varianten (`x40.py`)

Zuerst gut 20 Varianten gegen 6.10. Im Screening rechnete der Wächter noch über die ganze Historie (dazu 5.2).
Zellen: Auszahlungen · Busts · Netto · Serien ≥ 6 Verluste, je Jahr.

| Variante | GFT-Ersatz 2022–25 | Fremddaten 2006–21 |
|---|---|---|
| ***Ertrag*** | | |
| 6.10 (Basis) | 6,42 · 0,195 · 1877 $ · 0,75 | 1,95 · 0,376 · 493 $ · 2,69 |
| A: kein Fade gegen jungen Lauf (p_ext < 33 %), Länge 20 | 6,86 · 0,032 · 1984 $ · 1,37 | 1,88 · 0,426 · 461 $ · 2,72 |
| A, nur 500 Schenkel | 7,39 · 0,092 · 2144 $ · 1,08 | 1,72 · 0,406 · 424 $ · 2,92 ⁽⁴⁾ |
| **S: Stop-Chance ≥ 70 %, Länge 15** | **7,58 · 0,052 · 2199 $ · 1,26** | **1,90 · 0,347 · 475 $ · 2,89** |
| S ≥ 65 %, Länge 15 | 7,21 · 0,073 · 2078 $ · 1,40 | 1,89 · 0,399 · 462 $ · 2,82 |
| S ≥ 75 %, Länge 15 | 6,99 · 0,111 · 2005 $ · 1,00 | 1,92 · 0,429 · 469 $ · 2,80 |
| S ≥ 75 %, Länge 20 | 7,13 · 0,094 · 2045 $ · 1,40 | 1,83 · 0,356 · 458 $ · 2,91 ⁽⁴⁾ |
| S ≥ 70 %, Länge 10 | 6,69 · 0,095 · 1923 $ · 0,98 | 1,92 · 0,307 · 494 $ · 2,82 ⁽⁴⁾ |
| S ≥ 70 %, nur 500 Schenkel | 6,51 · 0,011 · 1884 $ · 1,35 | 2,05 · 0,410 · 500 $ · 2,79 ⁽⁴⁾ |
| S, Wächter sieht alle Signale (= `GridNurLive`) | 6,68 · 0,130 · 1975 $ · 0,86 | 1,90 · 0,343 · 487 $ · 2,82 ⁽⁴⁾ |
| S, Wächter PF > 1,3 | 6,71 · 0,061 · 1874 $ · 0,89 | 1,76 · 0,277 · 447 $ · 2,48 |
| S, Wächter PF > 1,4 | 6,40 · 0,140 · 1750 $ · 1,28 | 1,82 · 0,231 · 489 $ · 2,53 ⁽⁴⁾ |
| ohne Grid, Wächter PF > 1,3 | 6,22 · 0,296 · 1779 $ · 0,75 | 1,90 · 0,221 · 503 $ · 2,45 |
| ***Sicher*** | | |
| 6.10 (Basis) | 3,02 · 0,001 · 835 $ · 0,27 | 0,58 · 0,324 · 111 $ · 0,40 |
| A: p_ext < 33 %, Länge 20 | 3,50 · 0,003 · 976 $ · 0,66 | 0,53 · 0,393 · 86 $ · 0,38 ⁽⁴⁾ |
| **S: Stop-Chance ≥ 70 %, Länge 15** | **4,20 · 0,000 · 1173 $ · 0,21** | **0,47 · 0,231 · 96 $ · 0,30** |
| S ≥ 65 % | 3,49 · 0,000 · 961 $ · 0,15 | 0,47 · 0,297 · 82 $ · 0,41 |
| S ≥ 75 % | 3,52 · 0,005 · 959 $ · 0,09 | 0,53 · 0,339 · 95 $ · 0,39 |
| S ≥ 75 %, Länge 20 | 4,15 · 0,039 · 1160 $ · 0,11 | 0,47 · 0,334 · 83 $ · 0,27 ⁽⁴⁾ |
| S ≥ 70 %, Länge 10 | 3,15 · 0,010 · 887 $ · 0,33 | 0,58 · 0,299 · 110 $ · 0,34 ⁽⁴⁾ |
| S ≥ 70 %, nur 500 Schenkel | 3,71 · 0,092 · 1014 $ · 0,26 | 0,43 · 0,285 · 71 $ · 0,41 ⁽⁴⁾ |
| S, Wächter PF > 1,3 | 3,24 · 0,000 · 916 $ · 0,04 | 0,37 · 0,204 · 69 $ · 0,15 |

16 Störungen (GFT-Ersatz: jeder Handelstag, Fremddaten: jeder dritte Tag); ⁽⁴⁾ = Vorauswahl mit 4 Störungen.
Ergebnisse: `Replikat_v6/ergebnisse/x40_gft.json`, `x40_ext.json`.

- Auf dem GFT-Ersatz schlägt **jede** Grid-Variante 6.10 bei Auszahlungen und Busts, auch die Nachbarn der gewählten
  Einstellung (65/75 %, Länge 10/20, 500 Schenkel). Der Effekt hängt also nicht an einem einzelnen Parameterpunkt.
  Länge 15 / 70 % ist aber das Beste dieses Rasters; die Zahlen des gewählten Punkts sind deshalb eher etwas
  optimistisch.
- Auf den Fremddaten 2006–21 (anderes Regime, die Fades verdienen dort nichts) ist Regel S **neutral**: etwas
  weniger Ertrag, eher weniger Busts. Regel A hat dort mehr Busts als 6.10 und ist deshalb verworfen.
- Ein strengerer Wächter (PF > 1,3 / 1,4) kostet auf dem Ersatz Auszahlungen. Ohne Grid bringt er dort mehr Busts.
- **Der Preis:** Weil der Wächter den gefilterten Strom sieht, handeln die schwächeren Gold-Module öfter (5.4). In
  „Ertrag“ steigen die Serien ≥ 6 Verluste. `GridNurLive` lässt die Serien auf dem Stand von 6.10, bringt aber nur
  einen Teil des Zusatz-Ertrags.

### 5.2 Endbewertung mit dem Wächter wie im EA (`x41.py`)

Das Gegenlesen (7.1, Befund A) zeigte: Der EA rekonstruiert den Wächter beim Start nur aus den letzten
`FadeHistTage` = 600 Tagen. Ein Modul geht erst live, wenn darin mindestens 30 virtuelle Signale liegen. Das Replikat
rechnet das jetzt genauso: nach jedem Start, also im ungünstigsten Fall. Für 6.10 ändert das auf dem GFT-Ersatz
nichts (dieselben Zahlen wie mit ganzer Historie) und auf den Fremddaten wenig. Für N1800 mit Grid ändert es viel,
siehe 5.3.

**GFT-Ersatz 2022–2025** (16 Störungen, jeder Handelstag):

| Variante | Ausz./J | Busts/J | Netto/J | Serien ≥ 5 | Serien ≥ 6 | längste Serie Ø / max | gültige Tage/J |
|---|---:|---:|---:|---:|---:|---:|---:|
| 6.10 Ertrag | 6,42 | 0,195 | 1877 $ | 2,80 | 0,75 | 7,2 / 10 | 48,2 |
| **6.20 Ertrag** (Echtbetrieb) | **7,34** | **0,032** | **2152 $** | 2,72 | **1,45** | 7,6 / **13** | 52,0 |
| 6.20 Ertrag, Grid auch für N1800 | 7,26 | 0,052 | 2105 $ | 2,29 | 1,10 | 7,2 / 12 | 51,1 |
| 6.20 Ertrag, `GridNurLive` | 6,78 | 0,130 | 1979 $ | 2,24 | 0,86 | 7,3 / 10 | 48,4 |
| 6.10 Sicher | 3,02 | 0,001 | 835 $ | 0,61 | 0,27 | 5,2 / 7 | 26,7 |
| **6.20 Sicher** | **4,12** | **0,000** | **1162 $** | 0,80 | 0,24 | 5,5 / **10** | 32,0 |
| 6.20 Sicher, Grid auch für N1800 | 4,00 | 0,000 | 1123 $ | 0,64 | 0,26 | 5,4 / 10 | 31,7 |

Streuung über die 16 Störungen: 6.20 Ertrag 7,34 ± 0,46 Auszahlungen (6.10: 6,42 ± 0,36), 6.20 Sicher 4,12 ± 0,35
(6.10: 3,02 ± 0,24). Der Abstand liegt weit über der Streuung. Die Störungen bilden aber nur Ausführung und Kosten
ab, nicht einen anderen Marktverlauf.

**Fremddaten 2006–2021** (anderes Regime; 16 Störungen, jeder dritte Tag):

| Variante | Ausz./J | Busts/J | Netto/J | Serien ≥ 5 | Serien ≥ 6 | längste Serie Ø / max |
|---|---:|---:|---:|---:|---:|---:|
| 6.10 Ertrag | 1,99 | 0,360 | 511 $ | 4,62 | 2,63 | 10,0 / 20 |
| **6.20 Ertrag** (Echtbetrieb) | **1,97** | **0,395** | **497 $** | 4,58 | 2,81 | 9,8 / 18 |
| 6.20 Ertrag, Grid auch für N1800 | 1,96 | 0,385 | 498 $ | 4,52 | 2,76 | 9,9 / 18 |
| 6.20 Ertrag, `GridNurLive` | 1,96 | 0,355 | 499 $ | 4,75 | 2,67 | 10,0 / 20 |
| 6.10 Sicher | 0,49 | 0,261 | 98 $ | 0,83 | 0,37 | 5,6 / 10 |
| **6.20 Sicher** | **0,43** | **0,246** | **82 $** | 0,76 | 0,31 | 5,6 / 10 |
| 6.20 Sicher, Grid auch für N1800 | 0,46 | 0,228 | 94 $ | 0,75 | 0,30 | 5,4 / 10 |

Im alten Regime verdienen die Fades nichts: Zusammen verlieren sie rund 120–140 $ je Jahr, den Ertrag bringen dort
RSI21 und Noise. Das Grid ändert daran wenig.

- 6.20 Ertrag hat 0,035 Busts je Jahr mehr als 6.10. Die Streuung über die Störungen beträgt ±0,06, das sind etwa
  2 Standardfehler.
- Im Screening (Wächter über die ganze Historie, 5.1) war es umgekehrt: 0,347 statt 0,376 Busts. Der Unterschied
  liegt also im Bereich dessen, was allein die Wächter-Rechnung verschiebt.
- `GridNurLive` liegt gleichauf mit 6.10.
- 6.20 Sicher hat weniger Busts und Serien, aber auch etwas weniger Ertrag.
- Nach Startjahr (2006–2021) liegt 6.20 Ertrag in 7 von 16 Jahren vorn (`ergebnisse/x41_ext.json`).

### 5.3 N1800 ohne Grid

Das Grid sperrt 60 % der N1800-Signale (Stop nur 0,3 Range hinter dem Extrem, siehe 4.5). Vor einem N1800-Signal
2022–25 liegen dann im 600-Tage-Fenster im Median nur 20 Signale, mindestens 12 (6.10: Median 49, mindestens 35;
`t_window.py`). Der EA bräuchte 30 und ließe N1800 deshalb nach jedem Start nur virtuell laufen. Alle anderen Module
bleiben über 30. Nur N1030 und N0930 fallen bei gut 5 % ihrer Signale kurz darunter, N0930 auch in 6.10. Das
rechnet das Replikat mit. Mit `GridOhne = N1800` läuft N1800 wie in 6.10. Ohne diese Ausnahme wäre N1800 praktisch
abgeschaltet:

- GFT-Ersatz, Ertrag: 7,34 statt 7,26 Auszahlungen, 0,032 statt 0,052 Busts, aber 1,45 statt 1,10 Serien ≥ 6.
- GFT-Ersatz, Sicher: 4,12 statt 4,00 Auszahlungen.
- Fremddaten: Ertrag 1,97 statt 1,96 Auszahlungen, aber 0,395 statt 0,385 Busts. Sicher: 0,43 statt 0,46
  Auszahlungen und 0,246 statt 0,228 Busts. Im alten Regime verliert N1800 (−15 $ je Jahr).

Die Unterschiede sind klein und zeigen nicht in eine Richtung. 6.20 lässt N1800 unverändert, weil das Grid ein Filter
sein soll und kein Abschalter für ein Modul. Wer die Serien drücken will, kann `GridOhne` leeren. Das Journal meldet dann beim Start, dass N1800
zu wenige Signale hat.

### 5.4 Woher der Zusatz-Ertrag kommt

Netto je Jahr und Trades je Jahr je Modul, GFT-Ersatz:

| Modul | 6.10 Ertrag | 6.20 Ertrag | `GridNurLive` | 6.10 Sicher | 6.20 Sicher |
|---|---:|---:|---:|---:|---:|
| N1030 | 399 $ · 26 | 494 $ · 23 | 449 $ · 22 | 349 $ · 28 | 501 $ · 25 |
| N1330 | 168 $ · 34 | 206 $ · 33 | 191 $ · 33 | 175 $ · 37 | 209 $ · 36 |
| X0630 | 188 $ · 35 | 212 $ · 34 | 203 $ · 35 | 142 $ · 36 | 143 $ · 36 |
| X0400 | −54 $ · 7 | 60 $ · 13 | −60 $ · 7 | −48 $ · 8 | 83 $ · 14 |
| N1800 (ohne Grid) | 55 $ · 6 | 74 $ · 6 | 47 $ · 6 | 62 $ · 6 | 68 $ · 6 |
| N0930 | 164 $ · 18 | 122 $ · 18 | 164 $ · 18 | 153 $ · 20 | 146 $ · 19 |
| N1100 | 141 $ · 16 | 152 $ · 17 | 132 $ · 17 | 162 $ · 19 | 140 $ · 21 |
| N1300 | 143 $ · 26 | 129 $ · 27 | 152 $ · 26 | 150 $ · 31 | 135 $ · 32 |
| X0300S | 0 $ · 3 | 113 $ · 15 | 16 $ · 2 | 15 $ · 4 | 135 $ · 16 |
| X1000S | −71 $ · 9 | 11 $ · 12 | −57 $ · 8 | −118 $ · 11 | −34 $ · 14 |
| RSI21 | 861 $ · 65 | 777 $ · 65 | 904 $ · 66 | – | – |
| Noise | 406 $ · 77 | 442 $ · 76 | 399 $ · 77 | – | – |

Zwei Wirkungen:

1. **Bessere Trades** bei den Modulen mit engem Stop: Das Grid lässt die Fades weg, deren Stop der laufende Schwung
   wahrscheinlich noch erreicht. N1030 verdient mit weniger Trades mehr (494 statt 399 $), X1000S verliert kaum
   noch.
2. **Mehr Trades der schwachen Gold-Module:** X0300S und X0400 lagen in 6.10 meist unter der Wächter-Schwelle (PF der
   letzten 30 > 1,2) und liefen nur virtuell. Gefiltert erreichen sie die Schwelle öfter: X0300S handelt 15-mal statt
   3-mal im Jahr und verdient 113 $. Diese Module haben aber die niedrigsten Trefferquoten (58–63 %). Daher kommen
   die zusätzlichen Verlustserien. Mit `GridNurLive` bleibt ihr Wächter wie in 6.10 und damit auch die Serien.

RSI21 verdient in 6.20 Ertrag etwas weniger (777 statt 861 $) bei gleicher Trade-Zahl. Das ist eine Wechselwirkung über
Budget, Serien-Stopp und Abschluss-Ernte; einzeln zerlegt ist sie nicht.

### 5.5 Startjahre (1-Jahres-Konten, GFT-Ersatz)

Zellen: Auszahlungen · Busts · Netto · Serien ≥ 6, je Jahr.

| Variante | Start 2022 | Start 2023 | Start 2024 | Start 2025 ⁽*⁾ |
|---|---|---|---|---|
| 6.10 Ertrag | 8,00 · 0,33 · 2509 $ · 0,89 | 7,47 · 0,25 · 2135 $ · 1,11 | 3,80 · 0,00 · 1053 $ · 0,30 | 3,44 · 0,00 · 877 $ · 0,40 |
| **6.20 Ertrag** | **8,56 · 0,05 · 2815 $ · 1,16** | **8,26 · 0,05 · 2333 $ · 2,05** | **5,07 · 0,00 · 1376 $ · 0,94** | **4,60 · 0,00 · 1254 $ · 0,75** |
| 6.20 Ertrag, `GridNurLive` | 8,16 · 0,20 · 2593 $ · 0,80 | 7,91 · 0,20 · 2241 $ · 1,33 | 4,03 · 0,00 · 1125 $ · 0,42 | 4,28 · 0,00 · 1123 $ · 0,29 |
| 6.10 Sicher | 3,23 · 0,00 · 989 $ · 0,00 | 3,52 · 0,00 · 948 $ · 0,35 | 2,15 · 0,00 · 558 $ · 0,37 | 1,66 · 0,01 · 422 $ · 0,00 |
| **6.20 Sicher** | **4,30 · 0,00 · 1414 $ · 0,00** | **4,42 · 0,00 · 1180 $ · 0,05** | **3,44 · 0,00 · 899 $ · 0,62** | **3,43 · 0,00 · 1004 $ · 0,78** |

⁽*⁾ Die Ersatzdaten enden am 31.12.2025, deshalb gibt es für Start 2025 nur wenige 1-Jahres-Konten.

6.20 bringt in **jedem** Startjahr mehr Auszahlungen als 6.10, in „Ertrag“ auch deutlich weniger Busts (2022/23).
Die Serien ≥ 6 steigen in „Ertrag“ in jedem Startjahr, in „Sicher“ in den Startjahren 2024/25.

## 6. Was 6.20 ändert

| Eingabe | Wert | Bedeutung |
|---|---:|---|
| `GridAktiv` | true | Grid-Filter für Fades an (false = Fades wie 6.10) |
| `GridTF` | M5 | Zeitebene der Schwünge (aus M5 gebildet: M5, M10, M15, M20, M30, H1) |
| `GridLaenge` | 15 | Swing Length (LuxAlgo: 20) |
| `GridMaxSchenkel` | 1000 | Maximum Reversals je Richtung |
| `GridMinSchenkel` | 30 | darunter filtert das Grid nicht |
| `GridMaxStopChance` | 0,70 | Regel S: ab dieser Stop-Chance kein Fade gegen den Lauf (0 = aus) |
| `GridMinReife` | 0 (aus) | Regel A: kein Fade gegen einen Lauf unter diesem Perzentil (getestet 0,33) |
| `GridVorlaufTage` | 300 | M5-Historie vor der Fade-Historie für die Schenkel-Statistik (1000 Schenkel je Richtung brauchen 225–259 Tage) |
| `GridOhne` | N1800 | Fade-Module ohne Grid (Liste mit `;`) – Begründung siehe Abschnitt 5.3 |
| `GridNurLive` | false | true = Grid sperrt nur den Live-Einstieg, der Wächter zählt alle Signale wie 6.10 |

Verhalten:

- Die Schwung-Statistik wird je Symbol aus den M5-Kerzen gebildet – dieselben Kerzen, die die Fade-Module nutzen.
  Beim Start lädt der EA `FadeHistTage + GridVorlaufTage` Tage M5 (900 Tage; **Max. Balken im Chart = Unbegrenzt**),
  danach rechnet er jede abgeschlossene Kerze fort. Sind die Kurse noch nicht vollständig geladen, wartet er (bis zu
  20 Versuche) und warnt im Journal, wenn die Historie kürzer bleibt. Die Fade-Historie des Wächters wird erst
  rekonstruiert, wenn das Grid steht; Fade-Kerzen werden live erst verarbeitet, wenn das Grid die Kerze davor kennt.
- Ein vom Grid gesperrtes Signal beendet den Tag des Moduls wie jedes Signal in 6.10 (kein zweiter Versuch am selben
  Tag – so rechnet auch das Replikat).
- Journal: `FADE X0300S: SHORT-Signal ausgelassen (auch virtuell) - Probability Grid: Lauf aufwaerts (62. Perzentil),
  Chance 81 %, dass er bis zum Stop weiterlaeuft (Regel S: ab 70 % kein Fade)`; beim Laden je Symbol
  `GRID XAUUSD.x: Historie ab …, n steigende / n fallende Schenkel`.
- Panel: Zeile „Probability Grid“ mit Laufrichtung und Perzentil je Symbol und der Zahl gesperrter Signale.
- Ohne genug Kurse oder Schenkel filtert das Grid nicht (Verhalten wie 6.10).
- Nach Verbindungslücken schreibt der EA das Grid erst mit synchronen Kursen fort (neue Fade-Kerzen warten mit,
  Ausstiege nicht).
- Ungültige Grid-Eingaben (z. B. `GridTF` nicht M5 … H1) verhindern den Start des EA mit einer Meldung im Journal.

## 7. Prüfung

- **Abgleich EA ↔ Replikat** (`t_port_grid.py`): Die Funktionen `GridM5`, `GridKerze`, `GridIndex`, `GridRang`
  und `GridFadeOk` wurden wörtlich nach Python übertragen und für **alle 6 856 Fade-Signale 2006–2025** gegen den
  Nachbau gerechnet: **gleiche Entscheidung bei jedem Signal**, Stop-Chance ohne Abweichung – auch nach den Korrekturen
  aus dem Gegenlesen (Protokoll: `Replikat_v6/ergebnisse/t_port_grid_5_15_1000_070.txt`).
- **Statische Prüfung** (`t_mq5.py`, neu im Repository): Klammern, Anzahl der Format-Argumente, Makros und globale
  Variablen vor der ersten Verwendung, unbekannte Funktionen. Die Prüfung findet den Fehler, an dem 0704e96
  scheiterte (`MAXFADE`), und fand im 6.20-Entwurf eine vor der Verwendung fehlende Deklaration (`gridOk`) – behoben.
- **Gegenlesen** durch einen Sub-Agenten (Kompilierbarkeit, Logik gegen das Replikat, Neustart, Datenlücken): keine
  Kompilier-Hindernisse gefunden (Struktur mit dynamischen Arrays, Format-Argumente, Deklarationen, Indizes), Logik
  deckungsgleich mit dem Replikat, auch `GridNurLive`. Die Befunde stehen in 7.1 – alle sind behoben.
- **Nicht** geprüft: Kompilieren in MetaEditor, Strategietester, Demo. Das bleibt Pflicht.

### 7.1 Befunde des Gegenlesens

| | Befund | Behebung |
|---|---|---|
| **A** (hoch) | N1800 behält mit Grid nur rund 20 Signale je 600 Tage (Median, mindestens 12; 6.10: 49). Der EA rekonstruiert den Wächter nur über `FadeHistTage` = 600 Tage und braucht 30 Signale – N1800 wäre nach jedem Start nur virtuell gelaufen. Das Replikat hatte den Wächter über die ganze Historie gerechnet und 35 Live-Trades von N1800 mitgezählt. | Replikat rechnet den Wächter jetzt **wie der EA** (Mindestzahl aus den letzten 600 Tagen). N1800 läuft ohne Grid (`GridOhne`). Die Endbewertung (5.2) ist damit neu gerechnet. |
| **B** (hoch) | `GridHistorie` nahm auch unvollständig geladene Kurse an (typisch direkt nach „Max. Balken = Unbegrenzt“ und Neustart). Das Grid wäre einmal aus zu wenigen Schenkeln gebaut worden. | Vollständigkeitsprüfung wie in `FadeHistorie`, bis zu 20 Versuche, danach Warnung im Journal |
| C | Das Warten auf das Grid verbrauchte den Wiederholungszähler der Fade-Historie. | Die Fade-Historie wartet ohne zu zählen, nur das Grid zählt seine Versuche. |
| D | Mit der Voreinstellung „Max. Balken“ 100 000 (~520 Tage M5) fehlt der Grid-Vorlauf. | Warnung im Journal (`GRID …: WARNUNG - M5-Historie erst ab …`) |
| E | `GridVorlaufTage` 240 war knapp: 1000 Schenkel je Richtung brauchen 225–259 Tage. | 300 |
| F | `gridOk` behielt nach einem Re-Init den alten Wert (Panel und Journal zeigten Veraltetes). | Der Grid-Zustand wird bei jedem Init zurückgesetzt. |
| G | Ungültige Grid-Eingaben stoppen den ganzen EA, die Meldung sagte aber nur „Fade-Module AUS“. `GridTF = PERIOD_CURRENT` folgte still dem Chart. | Die Meldung ist korrigiert, `PERIOD_CURRENT` wird abgewiesen. |
| H | Nach Verbindungslücken konnte das Grid Kerzen überspringen oder eine Zeitebenen-Kerze doppelt zählen. | Fortschreibung nur mit synchronen Kursen, keine doppelten oder rückwärts laufenden Kerzen |
| I, J | Panel und Kontozustand zeigten „6.10“. Bei `GridNurLive` hieß es „ausgelassen“ statt „nur virtuell“. | behoben |

## 8. Echtbetrieb: Dateien

- `DEADBAND_LIVE4.mq5`: Die Voreinstellungen **sind** das Echtbetrieb-Set („Ertrag“ + Grid).
- `DEADBAND_LIVE4_Echtbetrieb.set`: dieselben Werte als Datei.
- `DEADBAND_LIVE4_620_Sicher.set`: Ausprägung „Sicher“ (nur Fades) + Grid.
- Die 6.10-Sets liegen nur noch in `rollback_6.10/` (dort auch `DEADBAND_LIVE4_610_Sicher.set`).
- Rückweg: `GridAktiv=false` (Handelslogik wie 6.10) oder `rollback_6.10/` (mq5 + beide Sets), ältere Stände in
  `rollback_6.00/`, `rollback_5.10/`, `rollback_5.00/`.

## 9. Inbetriebnahme

1. `DEADBAND_LIVE4.mq5` nach `MQL5\Experts\` kopieren und in MetaEditor kompilieren. Erwartet: 0 Fehler.
2. Extras → Optionen → Charts → **Max. Balken im Chart = Unbegrenzt**, Terminal neu starten (Wächter ~600 Tage M5,
   Grid 300 Tage mehr, zusammen rund 180 000 M5-Kerzen je Symbol).
3. Strategietester: „Jeder Tick anhand realer Ticks“, XAUUSD.x M15, 2024–2026. Im Journal prüfen:
   - `GRID XAUUSD.x: Historie ab …` und `GRID NAS100.x: …` mit je einigen tausend Schenkeln,
   - je Fade-Modul `FADE … Historie ab …` (weniger Signale als in 6.10 vor allem bei X0300S, X0400 und N1030; N1800 unverändert),
   - keine Zeile `GRID …: WARNUNG - M5-Historie erst ab …` (sonst Max. Balken prüfen),
   - `… ausgelassen (auch virtuell) - Probability Grid: …` bei einzelnen Signalen,
   - sonst wie 6.10 (Ziel erst in der Kerze nach dem Einstieg, Abschluss-Ernte, Serien-Stopp, keine DEADBAND-Einstiege).
4. Eine Woche auf einem Demokonto mit gleicher Serverzeit, dann live nur auf dem eigenen PC, EIN Chart.
5. Kontoerkennung, Auszahlung, Overrides: unverändert, siehe Bericht 6.10, Abschnitte 4 und 6.

## 10. Grenzen und Hinweise

1. **Kein GFT-Datentest.** Alle Konto-Zahlen stammen vom Ersatz aus Fremddaten (breitere Spreads, 2022–2025).
   Mit den GFT-Exporten lässt sich alles wiederholen: Dateien nach `data/`, dann `python prep5.py && python sig5.py`
   und `python x41.py gft` (ohne `mk_proxy.py`). Bei den engeren GFT-Spreads ist ein **kleinerer** Vorteil zu
   erwarten (Abschnitt 4.4).
2. **Regime:** Im alten Regime (2006–21) verdienen die Fades nicht. Das Grid ändert daran wenig: 6.20 Ertrag hat dort
   etwas mehr Busts (0,395 statt 0,360 je Jahr), `GridNurLive` nicht (Abschnitt 5.2).
3. **Verlustserien:** Mit gefiltertem Wächter handeln die schwächeren Gold-Module (X0300S, X0400, X1000S) öfter. Das
   bringt mehr Auszahlungen, aber in „Ertrag“ fast doppelt so viele Serien ≥ 6 Verluste (1,45 statt 0,75 je Jahr,
   längste bis 13 statt 10). Wer das nicht will, setzt `GridNurLive=true` (Serien wie 6.10, gut ein Drittel des
   Zusatz-Ertrags, Abschnitt 5.2).
4. **Nicht kompiliert, nicht im Tester** (Abschnitt 7).
5. **Lizenz:** Das Konzept stammt aus dem LuxAlgo-Indikator „Probability Grid“ (CC BY-NC-SA 4.0, nicht kommerziell).
   EA und Replikat enthalten eigene Umsetzungen des Schwung-/Perzentil-Verfahrens mit Quellenangabe;
   `Replikat_v6/t_pgrid.py` enthält zu Prüfzwecken eine wörtliche Übertragung der Pine-Funktionen. Ob der Einsatz auf
   einem Prop-Firm-Konto als kommerzielle Nutzung gilt, bitte selbst prüfen.
6. **Öffentliches Repository:** Empfehlung „Private“.

## Anhang: Replikat

Code und Anleitung: `Replikat_v6/README.md` (Abschnitt Build 6.20). Endbewertung: `Replikat_v6/x41.py gft|ext`,
Screening: `x40.py`, Vorstudie: `pg_study.py`, `pg_scan.py`, `pg_spread.py`, `pg_module.py`, Abgleich:
`t_port_grid.py`, Wächter-Fenster: `t_window.py`, statische Prüfung: `t_mq5.py`. Ergebnisse: `Replikat_v6/ergebnisse/x40_*.json`, `x41_*.json`.
