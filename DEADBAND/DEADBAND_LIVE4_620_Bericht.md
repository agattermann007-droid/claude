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

Alles andere bleibt wie 6.10 (RSI21, Noise, Budget, Kontoerkennung, Auszahlungslogik).

ERGEBNIS_KURZ

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

KONTO_TEIL

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
| `GridVorlaufTage` | 240 | M5-Historie vor der Fade-Historie für die Schenkel-Statistik |
| `GridNurLive` | false | true = Grid sperrt nur den Live-Einstieg, der Wächter zählt alle Signale wie 6.10 |

Verhalten:

- Die Schwung-Statistik wird je Symbol aus den M5-Kerzen gebildet – dieselben Kerzen, die die Fade-Module nutzen.
  Beim Start lädt der EA `FadeHistTage + GridVorlaufTage` Tage M5 (840 Tage; **Max. Balken im Chart = Unbegrenzt**),
  danach rechnet er jede abgeschlossene Kerze fort. Die Fade-Historie des Wächters wird erst rekonstruiert, wenn das
  Grid steht; Fade-Kerzen werden live erst verarbeitet, wenn das Grid die Kerze davor kennt.
- Ein vom Grid gesperrtes Signal beendet den Tag des Moduls wie jedes Signal in 6.10 (kein zweiter Versuch am selben
  Tag – so rechnet auch das Replikat).
- Journal: `FADE X0300S: SHORT-Signal ausgelassen (auch virtuell) - Probability Grid: Lauf aufwaerts (62. Perzentil),
  Chance 81 %, dass er bis zum Stop weiterlaeuft (Regel S: ab 70 % kein Fade)`; beim Laden je Symbol
  `GRID XAUUSD.x: Historie ab …, n steigende / n fallende Schenkel`.
- Panel: Zeile „Probability Grid“ mit Laufrichtung und Perzentil je Symbol und der Zahl gesperrter Signale.
- Ohne genug Kurse oder Schenkel filtert das Grid nicht (Verhalten wie 6.10).

## 7. Prüfung

- **Abgleich EA ↔ Replikat** (`t_port_grid.py`): Die Funktionen `GridM5`, `GridKerze`, `GridIndex`, `GridRang`
  und `GridFadeOk` wurden wörtlich nach Python übertragen und für **alle 6 856 Fade-Signale 2006–2025** gegen den
  Nachbau gerechnet: **gleiche Entscheidung bei jedem Signal**, Stop-Chance ohne Abweichung.
- **Statische Prüfung** (`t_mq5.py`, neu im Repository): Klammern, Anzahl der Format-Argumente, Makros und globale
  Variablen vor der ersten Verwendung, unbekannte Funktionen. Die Prüfung findet den Fehler, an dem 0704e96
  scheiterte (`MAXFADE`), und fand im 6.20-Entwurf eine vor der Verwendung fehlende Deklaration (`gridOk`) – behoben.
- **Gegenlesen** durch einen Sub-Agenten (Kompilierbarkeit, Logik gegen das Replikat, Neustart, Datenlücken).
  REVIEW_TEIL
- **Nicht** geprüft: Kompilieren in MetaEditor, Strategietester, Demo. Das bleibt Pflicht.

## 8. Echtbetrieb: Dateien

- `DEADBAND_LIVE4.mq5`: Die Voreinstellungen **sind** das Echtbetrieb-Set („Ertrag“ + Grid).
- `DEADBAND_LIVE4_Echtbetrieb.set`: dieselben Werte als Datei.
- `DEADBAND_LIVE4_620_Sicher.set`: Ausprägung „Sicher“ (nur Fades) + Grid.
- Rückweg: `GridAktiv=false` (Handelslogik wie 6.10) oder `rollback_6.10/` (mq5 + beide Sets), ältere Stände in
  `rollback_6.00/`, `rollback_5.10/`, `rollback_5.00/`.

## 9. Inbetriebnahme

1. `DEADBAND_LIVE4.mq5` nach `MQL5\Experts\` kopieren und in MetaEditor kompilieren. Erwartet: 0 Fehler.
2. Extras → Optionen → Charts → **Max. Balken im Chart = Unbegrenzt**, Terminal neu starten (Wächter ~600 Tage M5,
   Grid 240 Tage mehr).
3. Strategietester: „Jeder Tick anhand realer Ticks“, XAUUSD.x M15, 2024–2026. Im Journal prüfen:
   - `GRID XAUUSD.x: Historie ab …` und `GRID NAS100.x: …` mit je einigen tausend Schenkeln,
   - je Fade-Modul `FADE … Historie ab …` (die Signalzahl liegt bei N1800 und X0300S deutlich unter 6.10),
   - `… ausgelassen (auch virtuell) - Probability Grid: …` bei einzelnen Signalen,
   - sonst wie 6.10 (Ziel erst in der Kerze nach dem Einstieg, Abschluss-Ernte, Serien-Stopp, keine DEADBAND-Einstiege).
4. Eine Woche auf einem Demokonto mit gleicher Serverzeit, dann live nur auf dem eigenen PC, EIN Chart.
5. Kontoerkennung, Auszahlung, Overrides: unverändert, siehe Bericht 6.10, Abschnitte 4 und 6.

## 10. Grenzen und Hinweise

1. **Kein GFT-Datentest.** Alle Konto-Zahlen stammen vom Ersatz aus Fremddaten (breitere Spreads, 2022–2025).
   Mit den GFT-Exporten lässt sich alles wiederholen: Dateien nach `data/`, dann `python prep5.py && python sig5.py`
   und `python x41.py gft` (ohne `mk_proxy.py`). Bei den engeren GFT-Spreads ist ein **kleinerer** Vorteil zu
   erwarten (Abschnitt 4.4).
2. **Regime:** Im alten Regime (2006–21) verdienen die Fades nicht; das Grid ändert daran wenig (Abschnitt 5).
3. **Verlustserien:** Mit gefiltertem Wächter handeln schwächere Gold-Module (X0300S, X0400, X1000S) öfter – mehr
   Auszahlungen, aber etwas mehr Serien ≥ 6 in „Ertrag“. Wer das nicht will: `GridNurLive=true`.
4. **Nicht kompiliert, nicht im Tester** (Abschnitt 7).
5. **Lizenz:** Das Konzept stammt aus dem LuxAlgo-Indikator „Probability Grid“ (CC BY-NC-SA 4.0, nicht kommerziell).
   EA und Replikat enthalten eigene Umsetzungen des Schwung-/Perzentil-Verfahrens mit Quellenangabe;
   `Replikat_v6/t_pgrid.py` enthält zu Prüfzwecken eine wörtliche Übertragung der Pine-Funktionen. Ob der Einsatz auf
   einem Prop-Firm-Konto als kommerzielle Nutzung gilt, bitte selbst prüfen.
6. **Öffentliches Repository:** Empfehlung „Private“.

## Anhang: Replikat

Code und Anleitung: `Replikat_v6/README.md` (Abschnitt Build 6.20). Endbewertung: `Replikat_v6/x41.py gft|ext`,
Screening: `x40.py`, Vorstudie: `pg_study.py`, `pg_scan.py`, `pg_spread.py`, `pg_module.py`, Abgleich:
`t_port_grid.py`, statische Prüfung: `t_mq5.py`. Ergebnisse: `Replikat_v6/ergebnisse/x40_*.json`, `x41_*.json`.
