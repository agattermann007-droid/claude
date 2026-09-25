# RSI21 EK – Eigenkapital-Strategie aus DEADBAND 6.60, Build 1.00

Bericht vom 25.09.2026 · eigenes Kapital, ohne Prop-Firmen-Regeln, auf Rendite optimiert

## 1. Kurzfassung

**Auftrag:** Build 6.60 holen und daraus eine Eigenkapital-Strategie mit dem RSI21-Modul bauen, komplett ohne Regeln und
nur auf Rendite optimiert.

**Ergebnis:** Ein eigenständiger EA `RSI21_EK.mq5` (Preset `RSI21_EK.set`) plus Replikat und Prüfungen im Ordner
`DEADBAND/RSI21_EK/`. Das Signal ist das RSI21 aus 6.60. Alle Prop-Firmen-Regeln sind entfernt. Positionsführung, Ausstieg
und Größe sind neu auf Rendite optimiert.

Replikat 2006–2026 (Gold und NAS100 auf M5, breite Spreads, Zins-Swap, Hebel 1:20):

| | RSI21 aus 6.60, nur ohne Prop-Regeln | **RSI21 EK 1.00** |
|---|---:|---:|
| **Bei gleicher Schwankung** (25 % Jahresvolatilität, 16 Störungen): CAGR 2006–26 | 30,9 % | **45,4 %** |
| … 2006–16 / 2017–21 / 2022–26 | 10,8 / 58,6 / 58,0 % | **18,7 / 82,0 / 84,8 %** |
| … Sharpe 2006–26 · größter Rückgang | 1,10 · 36 % | **1,39 · 32 %** |
| **Bei gleichem größten Rückgang** (40 % über 2006–26): CAGR 2006–26 | 33,7 % | **61,4 %** |
| **Mit der Voreinstellung 1,0 % Risiko je Trade:** CAGR · größter Rückgang 2006–26 | – | **59,7 % · 38 %** |
| … 2006–16 / 2017–21 / 2022–26 | – | 23,5 / 107,6 / 121,6 % |
| Trades je Jahr · Trefferquote · R je Trade · Profitfaktor | 50 · 53 % · +0,31 · 1,74 | 106 · 44 % · +0,44 · 1,76 |

**Was sich gegenüber 6.60 ändert** (Signal, Stop 2 ATR, Ziele 2,2 / 2,64 R und Zeit-Ausstieg bleiben):

1. **Kein Einstand.** 6.60 zieht den Stop ab 1 R auf Einstand. Das diente den gültigen Tagen der Prop-Firma und kostet
   bei diesem Trendsignal Rendite.
2. **Jedes Signal wird gehandelt.** 6.60 handelte nur Folgesignale. **Gold nur M15** statt M15 und M30.
3. **Bis 5 Positionen je Symbol** in Richtung der ersten (6.60: 2). Nach **1 Verlust am Tag je Symbol** keine neuen
   Einstiege mehr (6.60: 2).
4. **Gewichte** M15 1,5 / M30 1,0 / H1 0,5 (6.60: 1,25 / 1,0 / 0,75), Gold ×0,7 wie 6.60.
5. **Größe 1,0 % der Equity je Trade** × Gewicht, mit Zinseszins. Begrenzt ist sie nur durch die Margin des Brokers.

**Wichtig:**
- Die Rendite hängt stark am Zeitraum. 2006–16 verdient RSI21 viel weniger als 2017–26. Das gilt schon für 6.60, dessen
  RSI21-Regeln auf 2016–26 entwickelt wurden (Abschnitt 4).
- „Nur auf Rendite“ heißt hier: die höchste Rendite bei gleichem Risiko. Die Größe steht auf dem Punkt, an dem die
  Rendite auch bei schwächerer Kante am höchsten ist (Abschnitt 7.3). **Mehr Risiko erhöht die Rendite nur, solange die
  Kante so stark bleibt wie 2017–26.** Beispiele: 2,0 % je Trade brächte 88 % CAGR bei 57 % größtem Rückgang, unter Stress
  69 % Rückgang.
- Alle Bausteine von EK 1.00 hat auch eine Walk-Forward-Suche gewählt, die 2022–26 nicht kannte. Filter und Zeitfenster
  dagegen, die nur 2006–21 verbesserten, haben 2022–26 verschlechtert und sind nicht übernommen (Abschnitt 5).
- **Nicht geprüft:** Kompilieren in MetaEditor (der Code ist nur gegengelesen), Strategietester, Demo. Das bleibt Pflicht
  (Abschnitt 9).

## 2. Was wegfällt, was bleibt

**Entfernt** sind alle Regeln, die es nur wegen GFT gab, und die übrigen Module:
- Boden und Bust-Logik, Floating-Bremse (−0,8 %) und Notbremse (−1 %), Tagesgrenze, Tagesreferenz
- gültige Tage, Mindestgewinn, Auszahlungsreife, Schluss bei Reife, Abschluss- und Gewinn-Ernte
- Schutz gültiger Tage, Pufferkurve, Faktor unter Startsaldo, Budgets (RSI21 1,2 %, gesamt 0,9 %), Risiko je Idee,
  Serien-Stopp
- News-Sperre, Hedging-Sperre, 130-s-Regel, Wochenend-Schluss mit Wiederaufnahme, VPS-Sperre, Margin-Grenze je Idee (70 %)
- die Fade-Module, Noise und DEADBAND

**Geblieben** ist das RSI21-Signal (RSI21 Continuation, Regeln aus RSI21 v3.4, wie 6.60):
- Long, wenn RSI(21) der zuletzt geschlossenen Kerze über 75 liegt, Short unter 25.
- Zeitebenen M15, M30, H1 (Gold ohne H1). Kerzenbeginn ab 9:30 NY, NAS bis 13:00, Gold bis 17:00.
- Bestätigung: RSI(21) des anderen Symbols auf derselben Zeitebene über 55 (unter 45). Gold alternativ Vortagesschluss über
  (unter) SMA200 und SMA100.
- Shorts nur unter SMA200 oder SMA100, NAS-Longs nur über SMA200, kein Einstieg gegen eine bestätigte H4-RSI-Divergenz.
- Stop 2 ATR(14) der Signal-Zeitebene (= 1 R), Ziel 2,2 R (NAS) bzw. 2,64 R (Gold), Zeit-Ausstieg nach 1152 M5-Kerzen.

| Eingabe | 6.60 (RSI21) | EK 1.00 |
|---|---:|---:|
| Risiko je Trade | 0,50 % vom **Startsaldo** × Pufferkurve, Budgets | **1,0 % der Equity** (Zinseszins), nur Margin-Grenze |
| Gewichte M15 / M30 / H1, Gold | 1,25 / 1,0 / 0,75, × 0,7 | **1,5 / 1,0 / 0,5**, × 0,7 |
| Zeitebenen Gold | M15, M30 | **M15** |
| Folgesignal | nur Folgesignale (240 min) | **jedes Signal** |
| Einstand | ab 1 R (+0,05 R) | **aus** |
| Positionen je Symbol | 2 | **5** |
| Verluste je Tag und Symbol, danach keine Einstiege | 2 | **1** |
| Wochenende | schließen, Sonntag wieder aufnehmen | **halten** |
| alle übrigen Signal- und Ausstiegswerte | | unverändert |

## 3. Daten, Kosten, Prüfung

**Daten** (`ek_data.py`; Quellen im `extdata/DATEN_BERICHT.md`):
- Gold: `XAUUSD_ext_M5.csv`, 20.03.2006 – 02.09.2026 (OANDA, Dukascopy).
- NAS100: `NAS100_ext_M5.csv` bis 31.12.2025 (OANDA, HistData, MT5-Broker US100), ab 2026 `NAS100_duka_M5.csv`
  (Dukascopy-Ticks, bis 28.08.2026).
- Die Kursdaten wurden aus den Rohdaten neu aufgebaut. Alle SHA-256-Prüfsummen stimmen mit dem Datenbericht überein
  (`NAS100_ext` `dfef735d…87ab`, `XAUUSD_ext` `8532e33b…b462`); `NAS100_duka` hat wie dort 111 490 Zeilen.
- Perioden im Bericht: **T** = 2006–16, **V** = 2017–21, **Z** = 2022 – Aug. 2026, **G** = gesamt.

**Kosten:**
- Spread wie im Replikat v6 („breit“): max(Datei-Spread, Kurs × relativer GFT-Spread). Das ist eher teurer als ein
  ECN-Konto.
- Kommission Gold 5 $/Lot.
- Swap als Zinsmodell: Long zahlt US-Leitzins + 2,5 % p. a. auf den Positionswert, Short erhält Leitzins − 2,5 %. Dreifach
  nach dem Mittwoch.
- Kein Wochenend-Schluss: Positionen laufen durch, ein Gap über den Stop wird zum Eröffnungskurs gefüllt.
- **Hebel 1:20** (EU-Privatkunden: Gold und große Indizes). Alle Positionen zusammen belegen höchstens 90 % der Equity als
  Margin. Eine neue Position wird sonst verkleinert oder ausgelassen.

**Prüfung des Replikats:**

| Prüfung | Ergebnis |
|---|---|
| `ek_sig` gegen `sig5.r21_signals` (6.60-Replikat) | identisch: 4744 Signale, 3782 Folgesignale, alle Felder |
| `ek_sim` im Abgleich-Modus gegen `eng10` mit RSI21 allein und abgeschalteten GFT-Regeln | identisch: 1047 Trades, Trade für Trade (Einstieg, Platz, Richtung, Ergebnis in $) |
| EA-Tagesregime (aus H1, Handelstag 17:00–17:00 NY) gegen Replikat (D1) | 100 % gleiche Entscheidungen auf 1,7 Mio. Kandidaten |
| EA-Bestätigung (RSI des anderen Symbols über die Zeit) gegen Replikat | gleich, wenn das andere Symbol zur Signalzeit eine Kerze hat; sonst nimmt der EA die jüngere Kerze (0,3–2 % der Kandidaten). Für EK 1.00 ohne Wirkung auf die Trades |

## 4. Ausgangslage: RSI21 aus 6.60 auf Eigenkapital

Unverändertes 6.60-RSI21, nur ohne Prop-Regeln, 0,5 % Risiko × Gewicht (`ek_base.py`):

| | 2006–16 | 2017–21 | 2022–26 | gesamt |
|---|---:|---:|---:|---:|
| CAGR · größter Rückgang | 3,3 % · 9,8 % | 13,6 % · 4,3 % | 13,6 % · 5,1 % | 8,0 % · 10,6 % |
| R je Trade · Profitfaktor | +0,13 · 1,30 | +0,51 · 2,38 | +0,46 · 2,12 | +0,31 · 1,74 |

- **Die Kante war 2006–16 etwa ein Viertel so groß wie danach.** Die RSI21-Regeln von 6.60 (Folgesignal, Stop 2 ATR,
  Ziele) wurden auf Daten 2016–26 entwickelt (Build 4.50/4.60). 2006–16 hat keine dieser Entscheidungen gesehen.
- Schwache Jahre: 2009–2011 und 2015 um null, 2016 −0,27 R je Trade.
- Trades, die den Einstand erreichten, brachten im Mittel +1,19 R, die übrigen −1,02 R. Bei 1 R Einstand werden aber viele
  spätere Ziel-Treffer vorher ausgestoppt.
- Die Größe lässt sich bei 6.60 nur begrenzt steigern: Bei Hebel 1:20 ist die Rendite 2006–16 bei 3 % Risiko am höchsten
  (13,3 % CAGR, 46 % Rückgang) und fällt danach.

## 5. Was „nur auf Rendite optimiert“ hier heißt

Über den Hebel lässt sich jede Rendite erzeugen, bis zum Ruin. Varianten müssen deshalb bei **gleichem Risiko**
verglichen werden. Zwei naheliegende Wege haben nicht funktioniert (Vorversuche mit früheren Fassungen von `ek_ca.py`,
Protokolle nicht im Repo):

| Versuch | Was passierte | verworfen, weil |
|---|---|---|
| fester Prozentsatz je Trade (1 %) | gewählt wurden 5 Plätze, alle Signale, ohne Bestätigung, Handel ab 3:00 NY: 250–270 Trades je Jahr, 65–67 % Rückgang | es gewinnt, wer mehr gleichzeitige Positionen öffnet (mehr Hebel, nicht bessere Logik) |
| Kelly-Punkt je Variante (höchste CAGR über alle Größen) | 2006–16 283 % CAGR bei 10 % Risiko je Trade; 2022–26 fiel dabei von 239 auf 87 %, Rückgänge 78–85 % | der Kelly-Punkt eines einzelnen Pfads ist extrem zufallsanfällig |

**Gewählt: Rendite bei gleicher Schwankung.** Jede Variante wird so groß gehandelt, dass ihre Tagesrenditen 25 %
Jahresvolatilität haben (Hebel 1:20 wirkt mit). Bei frei wählbarem Hebel entspricht das der erreichbaren Rendite (Kelly:
Wachstum = Sharpe²/2), ist aber statistisch stabil.
- **Zielgröße regime-robust:** Mittel von log(1 + CAGR) über die Perioden. Ein Schritt ist gesperrt, wenn er eine Periode
  um mehr als 3 Prozentpunkte verschlechtert.
- **Koordinatensuche** (`ek_ca.py`) über 26 Parameter: Schwellen, Bestätigung, Zeitfenster, Zeitebenen, Filter, Stop,
  Ziele, Einstand, Nachzug, Zeit-Ausstieg, Plätze, Verluste je Tag, erstes Signal, Gewichte, Wochenende.
- Jeder Wert wird mit 4 Störungen gerechnet: 3 % der Signale ausgelassen, Schlupf bis 0,3 Spreads.

**Walk-Forward.** Dieselbe Suche lief zweimal nur mit älteren Daten, damit neuere ungesehen bleiben:

| Auswahl mit | Ergebnis in der Auswahl | ungesehen |
|---|---|---|
| nur 2006–16 (`ek_ca_T_abgebrochen.log`) | Zeitfenster 24 h, NAS bis 16 Uhr, Gold bis 13 Uhr: Sharpe 2006–16 0,44 → 1,13 | 2022–26: Sharpe 1,59 → 0,66 (abgebrochen) |
| 2006–21 (`ek_ca_RTV.log`) | CAGR 2006–16 11 → 43 %, 2017–21 61 → 139 % | 2022–26: **60 → 53 %** |

Aufgeteilt nach Bausteinen (`ek_kand.py`; 25 % Volatilität, Größe nur aus 2006–21 bestimmt, 16 Störungen, paarweise gegen
6.60):

| Kandidat | 2006–16 | 2017–21 | 2022–26 (ungesehen) |
|---|---:|---:|---:|
| K0 6.60 | 11,0 % | 60,8 % | 60,1 % |
| K2 Ausstieg + Positionsführung (Einstand 2,5 R, NAS-Ziel 3 R, 3 Plätze, 1 Verlust/Tag, M15 ×1,5) | 18,4 % | 85,9 % | **66,1 %** (16/16 besser) |
| K4 = K2 ohne Einstand, Gold-Ziel 3,5 R, 5 Plätze, erstes Signal, Gold ×1,3 | 17,2 % | 92,4 % | **79,2 %** (16/16) |
| K5 = K4 plus die gewählten Filter und Zeitfenster | 43,4 % | 136,5 % | **53,1 %** (1/16) |

- **Ausstieg und Positionsführung tragen auch ungesehen:** 2022–26 +6 bis +19 Prozentpunkte in allen 16 Störungen.
- **Filter und Zeitfenster sind Überanpassung.** Die Bestätigung aus, Gold nur bis 13 Uhr, NAS bis 16 Uhr und das NAS-Long-
  Regime aus verbessern 2006–21 stark und verschlechtern 2022–26.

## 6. Ergebnis der Suche

**Endlauf über alle Perioden** (`ek_ca_RTVZ.log`, Sperre für 2006–16, 2017–21 und 2022–26 zugleich):

| Schritt | 2006–16 | 2017–21 | 2022–26 | gesamt | Trades/J |
|---|---:|---:|---:|---:|---:|
| 6.60 | 10,5 % | 58,2 % | 57,9 % | 30,6 % | 50 |
| Einstand erst ab 2,5 R | 16,7 % | 70,8 % | 64,7 % | 38,3 % | 50 |
| 5 Plätze je Symbol | 16,4 % | 75,4 % | 77,8 % | 41,4 % | 92 |
| 1 Verlust je Tag und Symbol | 17,6 % | 77,4 % | 80,9 % | 43,1 % | 90 |
| erstes Signal voll handeln | 16,6 % | 77,2 % | 84,6 % | 43,1 % | 120 |
| Gewichte 1,5 / 1,0 / 0,5 | 17,1 % | 78,5 % | 87,2 % | 44,1 % | 120 |
| Gold nur M15 | 17,9 % | 82,1 % | 84,9 % | 44,9 % | 106 |
| Gold ×1,3 | 19,8 % | 83,4 % | 90,2 % | 47,3 % | 106 |

Diese Bausteine hatte auch der Walk-Forward mit 2006–21 gewählt (Einstand aus, 5 Plätze, 1 Verlust je Tag, erstes Signal,
Gewichte, Gold nur M15). Die Signal-Schwellen und Filter hat der Endlauf nicht verändert.

**Plateau** (`ek_plateau.py`: jeder Parameter auf seine Nachbarwerte, Zielwert R:TVZ, Endstand 47,7):
- Die Signalwerte von 6.60 liegen an **klaren Optima**:
  - RSI-Schwelle 75 (72,5: 37,3; 77,5: 39,3)
  - Bestätigung 55 (65: 37,8)
  - Beginn 9:30 NY (0:00: 38,0), NAS bis 13:00 (24:00: 40,1), Gold bis 17:00 (24:00: 39,2)
  - Stop 2 ATR (1,5: 37,8; 3,0: 42,8)
  - Short-Regime an (aus: 34,7), Gold-Tor an (aus: 42,8)
- Flach und damit unkritisch:
  - Einstand ab 2,0 R oder aus (45,5–47,9)
  - Zeit-Ausstieg 576–4608 M5-Kerzen (46,5–47,7)
  - NAS-Ziel 2,2–6 R oder ohne Ziel (46,2–49,2)
- Der Einstand bei 2,5 R wirkt praktisch nie (NAS-Ziel 2,2 R, Gold-Ziel 2,64 R). **EK 1.00 schaltet ihn deshalb aus**
  (47,9, gleichwertig). Aus demselben Grund wird jedes Signal direkt als Signal gehandelt (`FolgeMin 0`, identisch zu
  „erstes Signal voll“).

**Randparameter bei gleichem größten Rückgang** (`ek_rand.py`): Plätze und Gold-Faktor lagen am Rand des Rasters. Bei
gleicher Volatilität stieg die Rendite dort weiter, Sharpe und Rückgang wurden aber schlechter (Gold ×2,5: Sharpe 2006–16
0,62 → 0,48, Rückgang 39 → 54 %). Der Rückenwind kam aus der Gold-Hausse 2024–26. Deshalb entscheidet hier das strengere
Maß: CAGR 2006–26 bei 40 % größtem Rückgang:

| Plätze · Gold · Verluste/Tag | CAGR bei 40 % Rückgang | Risiko je Trade dafür |
|---|---:|---:|
| 5 · 1,3 · 1 (Endlauf) | 50,2 % | 0,59 % |
| 8 · 1,3 · 1 / 10 · 1,3 · 1 | 44,3 / 40,7 % | 0,43 / 0,38 % |
| 5 · 2,0 · 1 | 42,8 % | 0,39 % |
| 5 · 1,0 · 1 | 55,4 % | 0,77 % |
| 4 · 0,7 · 1 / 6 · 0,7 · 1 | 60,8 / 59,9 % | 1,25 / 0,94 % |
| **5 · 0,7 · 1 (EK 1.00)** | **61,4 %** | **1,08 %** |
| 5 · 0,7 · 2 / 5 · 0,7 · 0 | 50,5 / 48,6 % | 0,90 / 0,88 % |
| 6.60 | 33,7 % | 2,27 % |

- **Gold ×0,7** ist der Wert von 6.60 (Risikoparität aus RSI21 v3.4) und hier zugleich der beste.
- **5 Plätze** liegen auf einem Plateau (4–6 fast gleich).
- **1 Verlust je Tag** ist klar besser als 0 oder 2. An Tagen ohne Folgebewegung verhindert die Grenze, dass weitere
  Positionen nachgelegt werden.

**Warum die Bausteine plausibel sind:**
- *Kein Einstand:* RSI21 ist ein Fortsetzungssignal. Ein Stop auf Einstand bei 1 R schneidet genau die Trades ab, die
  nach einem Rücksetzer das Ziel erreichen. Im Plateau kostet Einstand bei 1 R ein Fünftel des Zielwerts (38,2 statt 47,9).
- *Mehr Plätze:* Jede weitere Position entsteht nur in Richtung der ersten, also in einer laufenden Bewegung.
  Die späteren Plätze sind die besten Trades: 1. Platz +0,31 R, 2. Platz +0,47 R, 3.–5. Platz +0,54 R je Trade.
- *Gold nur M15:* Gold-M30 war in allen drei Perioden schwächer als Gold-M15.

## 7. Endbewertung

### 7.1 Gleiche Schwankung (25 % Jahresvolatilität 2006–26, 16 Störungen, Mittel ± Standardabweichung)

| | Risiko je Trade | 2006–16 | 2017–21 | 2022–26 | gesamt | Sharpe gesamt | Rückgang |
|---|---:|---:|---:|---:|---:|---:|---:|
| 6.60 | 1,98 % | 10,8 ± 0,7 % | 58,6 ± 1,7 % | 58,0 ± 2,1 % | 30,9 ± 0,6 % | 1,10 | 36 % |
| K4 (nur Walk-Forward-Bausteine) | 0,47 % | 16,9 ± 0,9 % | 89,2 ± 1,7 % | 76,7 ± 2,1 % | 44,1 ± 0,8 % | 1,22 | 48 % |
| **EK 1.00** | 0,76 % | **18,7 ± 0,9 %** | **82,0 ± 1,8 %** | **84,8 ± 2,3 %** | **45,4 ± 0,7 %** | **1,39** | **32 %** |

- Sharpe je Periode: 6.60 0,47 / 1,73 / 1,64, EK 1.00 0,67 / 2,15 / 2,08.
- EK 1.00 ist also in jeder Periode besser, bei kleinerem Rückgang.

### 7.2 Gleicher größter Rückgang (40 % über 2006–26)

| | Risiko je Trade | 2006–16 | 2017–21 | 2022–26 | gesamt |
|---|---:|---:|---:|---:|---:|
| 6.60 | 2,27 % | 11,1 % | 64,9 % | 65,5 % | 33,7 % |
| K4 | 0,38 % | 14,5 % | 68,7 % | 59,2 % | 35,4 % |
| **EK 1.00** | 1,08 % | **22,6 %** | **113,5 %** | **129,3 %** | **61,4 %** |

### 7.3 Positionsgröße

Risikotabelle EK 1.00 (`ek_final.py`, CAGR / größter Rückgang; die Margin kürzt bei 1:20 spürbar ab rund 0,75 %):

| Risiko je Trade | 2006–16 | 2017–21 | 2022–26 | 2006–26 | 2006–26 bei 1:30 | 2006–26 bei 1:100 |
|---:|---:|---:|---:|---:|---:|---:|
| 0,5 % | 13,8 / 22 % | 51,5 / 11 % | 52,9 / 17 % | 30,3 / 22 % | 30,6 / 23 % | 30,6 / 23 % |
| 0,75 % | 19,1 / 31 % | 81,0 / 15 % | 86,3 / 24 % | 45,7 / 31 % | 46,8 / 32 % | 47,1 / 33 % |
| **1,0 %** | **23,5 / 38 %** | **107,6 / 18 %** | **121,6 / 28 %** | **59,7 / 38 %** | 63,6 / 40 % | 64,5 / 42 % |
| 1,5 % | 26,2 / 49 % | 132,6 / 28 % | 196,1 / 31 % | 77,3 / 49 % | 93,0 / 52 % | 100,4 / 57 % |
| 2,0 % | 26,7 / 57 % | 149,5 / 33 % | 254,4 / 35 % | 88,2 / 57 % | 111,4 / 62 % | 136,8 / 68 % |
| 3,0 % | 22,6 / 67 % | 159,1 / 38 % | 325,7 / 39 % | 94,4 / 67 % | 133,7 / 76 % | 201,2 / 81 % |
| 5,0 % | 14,6 / 74 % | 180,8 / 42 % | 407,7 / 45 % | 99,0 / 74 % | 139,1 / 86 % | 242,4 / 97 % |

**Robuster Kelly-Punkt** (`ek_groesse.py`). Die Größe mit der höchsten Rendite hängt davon ab, wie stark die Kante künftig
ist. Deshalb dieselbe Rechnung unter Stress: 20 % der Gewinner-Signale entfernt, Mittel über 4 Zufallsauswahlen.

| Risiko je Trade | 2006–16 normal | 2006–16 unter Stress | 2006–26 unter Stress | Monte Carlo 5 Jahre: Rückgang Median / 95 % · P(≥ 50 %) |
|---:|---:|---:|---:|---|
| 0,5 % | 13,8 % / 22 % | 6,2 % / 28 % | 20,7 % / 28 % | 16 / 25 % · 0,0 % |
| 0,75 % | 19,1 % / 31 % | 7,5 % / 39 % | 30,3 % / 39 % | 22 / 35 % · 0,1 % |
| **1,0 %** | 23,5 % / 38 % | **8,4 % / 47 %** | 38,8 % / 47 % | 28 / 43 % · 1,3 % |
| 1,25 % | 25,4 % / 43 % | 8,1 % / 55 % | 44,4 % / 55 % | 32 / 48 % · 4,0 % |
| 1,5 % | 26,2 % / 49 % | 7,3 % / 61 % | 49,2 % / 61 % | 36 / 54 % · 9,6 % |
| 2,0 % | 26,7 % / 57 % | 6,5 % / 69 % | 57,0 % / 69 % | 42 / 61 % · 24,2 % |
| 3,0 % | 22,6 % / 67 % | 0,9 % / 78 % | 61,1 % / 78 % | 50 / 71 % · 51,3 % |

- **Die Voreinstellung ist 1,0 %.** Bei schwächerer Kante im schwachen Regime ist die Rendite dort am höchsten. Darüber
  wächst nur der Rückgang.
- Ohne Stress läge der Kelly-Punkt 2006–16 bei 1,75–2,0 %.
- Über den ganzen Zeitraum steigt die Rendite bis 5 %. Bei 1:20 ist sie dort durch die Margin gedeckelt: Die meisten
  Einstiege werden gekürzt.
- Wer mehr will, erhöht `RiskPct`. Er setzt damit darauf, dass die Kante so stark bleibt wie 2017–26.

### 7.4 Jahre (1,0 % Risiko; Rendite / größter Rückgang im Jahr)

| 2006 | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 |
|---|---|---|---|---|---|---|---|---|---|---|
| −1 / 18 % | +35 / 24 % | +40 / 25 % | **−11 / 33 %** | 0 / 18 % | +8 / 30 % | +41 / 24 % | +112 / 20 % | +91 / 16 % | +21 / 18 % | **−18 / 32 %** |

| 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (Jan–Aug) |
|---|---|---|---|---|---|---|---|---|---|
| +73 / 15 % | +112 / 14 % | +101 / 10 % | +79 / 13 % | +190 / 18 % | +242 / 10 % | +27 / 28 % | +211 / 15 % | +80 / 10 % | +68 / 11 % |

Drei Verlustjahre, alle im alten Regime. Der größte Rückgang über 20 Jahre (38 % zum Tagesschluss, 40 % zum
Kerzenschluss) fällt in 2006–16.

### 7.5 Stress (1,0 % Risiko)

| | 2006–16 | 2017–21 | 2022–26 | gesamt |
|---|---:|---:|---:|---:|
| Basis | 23,5 / 38 % | 107,6 / 18 % | 121,6 / 28 % | 59,7 / 38 % |
| 20 % der Gewinner entfernt | 9,0 / 43 % | 76,7 / 16 % | 89,8 / 28 % | 38,8 / 43 % |
| Schlupf bis 1 Spread je Einstieg | 20,7 / 40 % | 107,1 / 20 % | 119,1 / 28 % | 57,3 / 40 % |
| Swap × 2 | 20,3 / 39 % | 101,6 / 18 % | 109,6 / 29 % | 54,4 / 39 % |
| ohne Swap | 26,8 / 37 % | 113,7 / 17 % | 134,1 / 26 % | 65,2 / 37 % |
| RSI des anderen Symbols wie im EA | identisch | identisch | identisch | identisch |

**Monte Carlo** (`ek_final.py`: Block-Bootstrap der Tagesrenditen 2006–26, 20 Tage je Block, 4000 Pfade à 5 Jahre; `ek_groesse.py` rechnet mit 2000 Pfaden):
- CAGR 5 / 50 / 95 %-Quantil: 24 / 57 / 106 %.
- Größter Rückgang Median 28 %, 95 %-Quantil 42 %.
- Rückgang ≥ 30 % in 37 % der Pfade, ≥ 50 % in 1,2 %.
- Verlust nach 5 Jahren in 0,2 % der Pfade.
- Der Bootstrap mischt die Regime. Wiederholt sich nur 2006–16, sind die Zahlen schlechter (Abschnitt 7.3).

### 7.6 Trade-Kennzahlen (1,0 % Risiko, 2006–26, 2198 Trades)

| | Trades je Jahr | R je Trade | Trefferquote | Summe |
|---|---:|---:|---:|---:|
| Gold / NAS | 63 / 44 | +0,40 / +0,50 | 41 / 49 % | +521 / +451 R |
| M15 / M30 / H1 | 95 / 9 / 3 | +0,44 / +0,52 / +0,42 | 43 / 50 / 48 % | |
| Long / Short | 78 / 29 | +0,41 / +0,53 | 43 / 45 % | |
| 1. / 2. / 3.–5. Platz | 38 / 25 / 44 | +0,31 / +0,47 / +0,54 | 40 / 45 / 47 % | |
| Ausstieg Stop / Ziel / Zeit | 60 / 46 / 1 | −1,04 / +2,39 / +0,93 | | |

- Haltedauer im Median rund 10 Stunden, im Mittel rund 17 Stunden.
- Kosten je Trade in R: Swap −0,03, Kommission −0,005 (Spread im Einstiegskurs).
- Margin bei 1:20: 282 Einstiege verkleinert, 124 ausgelassen (von 2322 Versuchen).

## 8. Der EA `RSI21_EK.mq5`

- **Eigenständig, ohne Code von GFT-Regeln:** rund 1160 Zeilen statt 6577. Zwei Symbole: Gold und NAS100, Namen als
  Eingaben. Ein Chart genügt; der Timer bedient beide Symbole.
- **Signal wie 6.60** (`HandleR21`, `R21Divergenz`), mit zwei robusteren Umsetzungen, beide gegen das Replikat geprüft
  (Abschnitt 3):
  - Das Tagesregime kommt aus H1-Kerzen je Handelstag 17:00–17:00 NY. Damit ist es unabhängig von der Tagesgrenze des
    Servers.
  - Der RSI des anderen Symbols kommt aus dessen letzter Kerze vor der Signalzeit. Das funktioniert auch, wenn dort noch
    kein Tick der neuen Kerze angekommen ist.
  - Regime und Divergenz gelten für die Signalzeit (Handelstag bzw. H4-Bucket der Signalkerze) wie im Replikat;
    Indikatorwerte werden über die Kerzenzeit gelesen.
- **Neue Kerze erst verarbeiten, wenn die Indikatoren nachgerechnet sind** (`BarsCalculated`). Sonst folgt ein neuer
  Versuch im nächsten Durchlauf, nach 5 min eine Warnung.
- **Größe:** `RiskPct` % der Equity × Gewicht (× Gold-Faktor). Lots werden kaufmännisch gerundet wie im Replikat.
  Übersteigt die Margin aller Positionen zusammen `MarginMaxPct` (90 %) der Equity, wird die neue Position verkleinert
  (Journal-Zeile, Gegenprobe mit dem Endvolumen für gestaffelte Margin). Signale, bei denen schon das Mindestlot mehr als
  doppelt so viel riskiert wie vorgesehen, werden ausgelassen (kleine Konten). Die Volumen-Grenze des Brokers je Richtung
  wird beachtet; Stop und Ziel liegen auf der Tick-Größe des Symbols.
- **Plätze:** Magic = `MagicBase` + 10 × Symbol + Platz. Weitere Positionen nur in Richtung der ersten; eben eröffnete
  oder eben geschlossene Positionen zählen richtig, auch wenn die Positionsliste des Terminals noch nachhinkt. Der EA
  verlangt ein **Hedging-Konto**: Ist das Konto beim Start bekannt, startet er sonst nicht; startet er vor der Anmeldung
  (Terminal-Neustart), prüft er im Betrieb und handelt auf einem Netting-Konto nicht (Warnung).
- **Ausstieg:**
  - Stop und Ziel liegen beim Broker.
  - Zeit-Ausstieg auf Kerzenbasis wie im Replikat: Schluss der 1152. M5-Kerze nach der Einstiegskerze bzw. der ersten
    Kerze, die mindestens 8 Tage nach der Einstiegskerze beginnt.
  - Optional: Einstand, Nachzug, Teilgewinn (im Preset aus). Ausgelöst wird am besten Kurs der M5-Kerzen seit dem
    Einstieg wie im Replikat; liegt der Kurs schon jenseits des neuen Stops, schließt der EA. Den Teilgewinn nimmt er
    nur, solange der Kurs höchstens 0,25 R unter dem Level liegt (das Replikat bucht ihn zum Level).
  - Der ursprüngliche Stopabstand (1 R) steht in einer Terminal-Globalvariablen. Nach einem Neustart kommt er aus der
    Eröffnungs-Order.
- **Verluste je Tag:** aus der Deal-Historie des Handelstags, je Symbol.
- **Wochenende:** Positionen werden gehalten. `WeSchlussNY` > 0 schließt freitags.
- **Zeit:** Der NY-Versatz wird aus Server- und GMT-Zeit bestimmt (`AutoNYOffset`): die erste Messung mit Verbindung
  gilt sofort, ein späterer Wechsel erst nach zwei gleichen Messungen im Abstand von 10 min (Journal-Zeile, Hinweis bei
  Abweichung von `NYOffsetHours`). Im Strategietester gilt `NYOffsetHours` (7).
- **Betrieb:**
  - Neustart: Die zuletzt verarbeitete Kerze je Symbol und Zeitebene steht in Terminal-Globalvariablen (Name mit Login
    und `MagicBase`, sofort auf Platte). Eingestiegen wird nur bis 2 min nach Kerzenbeginn. Ein Neustart, eine geänderte
    Eingabe oder eine Verbindungslücke führen so weder zu einem zweiten noch zu einem verspäteten Einstieg.
  - Mit derselben `MagicBase` läuft der EA nur auf einem Chart des Terminals (Sperre über eine temporäre
    Globalvariable; eine verwaiste Sperre, deren Chart diesen EA nicht mehr trägt, zählt nicht). Zwischen zwei Terminals
    wirkt die Sperre nicht (Abschnitt 9).
  - Schließ- und Stop-Aufträge höchstens alle 30 bzw. 5 s je Position und nur, wenn gehandelt werden kann
    (Algo-Handel an, Verbindung, frische Kurse gemessen an der laufenden Serverzeit, also auch am Wochenende). Ein
    Einstieg wird bei Requote oder neuem Kurs einmal wiederholt. Jedes ausgelassene Signal hat eine Journal-Zeile mit
    Grund.
  - Warnungen je Symbol und Art höchstens stündlich (Journal, optional Push): fehlende Historie für Regime oder
    Divergenz (dann keine Signale), Indikatoren nicht nachgerechnet, fälliger Ausstieg nicht möglich, abgelehnte
    Aufträge, kein Hedging-Konto; der Hinweis auf kurze H1-Historie höchstens täglich.
  - Zustandsvariablen geschlossener Positionen räumt der EA frühestens 5 min nach Start bzw. neuer Verbindung weg.
- **Prüfungen:**
  - `t_ek_set.py`: 57 Eingaben, Preset = Voreinstellungen, handelsrelevante Werte = Replikat-Endstand (45 Größen).
  - `t_mq5.py`: Klammern, Format-Argumente, Deklarationen, unbekannte Funktionen – bestanden. Als „unbekannt“ nennt es
    nur MQL5-Funktionen, die nicht in seiner Liste stehen (`BarsCalculated`, `ChartFirst`, `ChartGetString`,
    `ChartNext`, `GlobalVariableName`, `GlobalVariableTemp`, `GlobalVariablesTotal`).
  - Gegengelesen von einem MQL5-Prüfer: keine Kompilierfehler; 16 Befunde zu Betrieb und Randfällen (u. a. doppelter
    Einstieg nach Neustart, ungedrosselte Aufträge, stille Signalausfälle bei fehlender Historie). Alle sind umgesetzt
    (oben unter Betrieb), bis auf die Sommerzeit-Regel des Servers (Abschnitt 10).
  - Zweite Lesung der Überarbeitung: keine Kompilierfehler; zwei Betriebsrisiken (die Hedging-Prüfung vor der Anmeldung
    hätte den EA beim Terminal-Neustart vom Chart genommen; eine verwaiste Sperre hätte andere Charts ausgesperrt) und
    kleinere Punkte (Drosseln über die Ortszeit, geschlossener Markt über die laufende Serverzeit, getrennte Warnarten,
    Teilgewinn nur nahe dem Level, bester Kurs nach Pausen lückenlos, eben geschlossene Plätze). Alle umgesetzt.
  - Nicht geprüft: Kompilieren und Strategietester.

## 9. Inbetriebnahme

1. **Kompilieren:** `RSI21_EK.mq5` in MetaEditor kompilieren. Erwartet: 0 Fehler. Der EA ist nicht kompiliert; die
   statische Prüfung ersetzt MetaEditor nicht.
2. **Konto:**
   - MT5-**Hedging**-Konto.
   - Gold- und NAS100-CFD im Market Watch. Die exakten Namen in `GoldSymbol` / `NasSymbol` eintragen (z. B. `XAUUSD`,
     `NAS100`, `USTEC`, `US100`).
   - Die Zahlen gelten für Hebel 1:20. Mit mehr Hebel wird seltener gekürzt (1:30: 63,6 % statt 59,7 % CAGR).
3. **Historie:** Extras > Optionen > Charts > Max. Balken im Chart mindestens 10 000 (besser unbegrenzt). SMA200 braucht
   rund 200 Handelstage H1, die Divergenz mindestens 2000 H1-Kerzen (Voreinstellung 6000). Fehlt Historie, meldet der EA
   stündlich `… nicht berechenbar … KEINE Signale` und handelt nicht.
4. **Strategietester:**
   - „Jeder Tick anhand realer Ticks“, beide Symbole, Zeitraum ab 2024.
   - Vor dem Startdatum braucht der EA dieselbe Historie. Fehlt sie, stehen am Anfang die Warnungen aus Punkt 3 im
     Journal, und Signale gibt es erst, wenn genug Kerzen da sind.
   - Im Journal prüfen:
     - Startzeilen `RSI21EK 1.00: … Risiko 1.00 % der Equity … Plaetze 5, Verluste/Tag 1` und `Signal RSI(21) > 75.0 …
       Folge 0 min … Einstand 0.00 R …`
     - Einstiege `RSI21EK <Symbol>: Einstieg LONG M15 Platz 1, … Risiko …`
     - ausgelassene Signale mit Grund (`… ausgelassen - …`), z. B. Margin, Mindestlot, kein freier Platz, Verlust heute
     - nach der Anlaufzeit keine Warnungen `KEINE Signale`, keine `Margin nicht berechenbar`
   - Erwartung laut Replikat: im Mittel rund 2 Trades je Handelstag, rund 44 % Treffer.
5. **Demo:** zwei bis vier Wochen mit gleicher Serverzeit. Prüfen: Einstiegszeiten (9:30–13:00 NY für NAS, bis 17:00 für
   Gold), Stopabstand (2 ATR), Lots, die Zeile `NY-Versatz` (muss zur Serverzeit passen). Einmal das Terminal mitten in
   einer Kerze neu starten: Es darf kein zweiter Einstieg auf dasselbe Signal entstehen.
6. **Live:** ein Chart, AutoTrading an. VPS ist erlaubt (keine Prop-Regel mehr). Mit derselben `MagicBase` startet der EA
   nur auf einem Chart des Terminals; läuft er zusätzlich in einem zweiten Terminal (z. B. lokal und auf dem VPS), wird
   jedes Signal doppelt gehandelt – dann eines abschalten. Der EA sollte durchgehend laufen: Signale während einer Pause
   werden nicht nachgeholt (Einstieg nur bis 2 min nach Kerzenbeginn).

## 10. Grenzen und Hinweise

1. **Nicht kompiliert, nicht im Tester, nicht auf Demo** (Abschnitt 9). Der Code ist gegengelesen, das ersetzt MetaEditor
   nicht.
2. **Replikat statt Broker-Daten.** Fremddaten mit breiten Spreads und Zinsmodell-Swap. NAS 2026 stammt aus verrauschteren
   Dukascopy-Ticks. Bei einem anderen Broker weichen Spreads, Swaps, Kontraktgrößen und Serverzeit ab.
3. **Regimeabhängig.** 2006–16 verdient die Strategie rund ein Fünftel so viel wie 2017–26 (1,0 %: 23,5 statt 108–122 %
   CAGR). Dort liegen alle drei Verlustjahre und der größte Rückgang.
4. **In-Sample.** Die Zusammenstellung von EK 1.00 wurde mit allen Perioden gewählt. Ihre Bausteine hat zwar auch der
   Walk-Forward ohne 2022–26 gewählt, und der ungesehene Teil hat sich verbessert (K2, K4). Die absoluten Zahlen bleiben
   trotzdem eine Obergrenze.
5. **Hebel und Margin.** Bei 1:20 wird schon ab 0,75 % Risiko gekürzt. Bis zu 10 Positionen gleichzeitig, beide Symbole
   laufen über die Bestätigung oft in dieselbe Richtung. Schlimmster Fall bei 1,0 %: rund 12,8 % der Equity am Stop
   (5 × 1,5 % NAS + 5 × 1,05 % Gold). Wochenend- und News-Gaps können darüber hinausgehen.
6. **Zinseszins** über 20 Jahre ergibt rechnerisch absurde Endwerte. Lot-Grenzen und Liquidität sind nicht modelliert.
   Aussagekräftig sind CAGR und Rückgang, nicht der Endwert.
7. **Mehr Risiko ist kein freies Mehr an Rendite** (Abschnitt 7.3). Über 1,0 % steigt die Rendite nur, solange die Kante
   hält. Bei schwächerer Kante sinkt sie, und der Rückgang wächst schnell.
8. **DEADBAND 6.60** (GFT) ist unverändert. RSI21 EK ist ein eigener EA mit eigener Magic (`MagicBase` 2121000). Nicht
   auf einem GFT-Konto einsetzen: Er hält keine Prop-Regel ein.
9. **Serverzeit mit anderer Sommerzeit-Regel.** Der EA rechnet alle älteren H1-Kerzen mit dem aktuellen NY-Versatz um.
   Bei Servern mit EU-Sommerzeit (GMT+2/+3) stimmt das rund drei Wochen im März und eine Woche im Oktober/November nicht,
   bei GMT+0-Servern wechselt der Versatz zweimal im Jahr. Dann verschieben sich die H4-Buckets der Divergenz und die
   Tagesgrenzen des Regimes für ältere Kerzen um eine Stunde. 6.60 hat dasselbe. Am saubersten ist ein Server mit
   NY-Schlusszeit (GMT+2/+3 mit US-Sommerzeit, Versatz immer 7 h), sonst im Demo prüfen.
10. **Handeingriffe.** Von Hand geschlossene Positionen zählen nicht als Tagesverlust (der Schluss-Deal trägt keine
    EA-Magic). Von Hand eröffnete Positionen auf Gold oder NAS100 belegen keinen Platz, zählen aber für Margin und die
    Volumen-Grenze des Brokers.

## Anhang: Dateien und Ablauf

`RSI21_EK/README.md`:
- Daten: `ek_data.py`
- Signale: `ek_sig.py`
- Konto: `ek_sim.py`
- Kennzahlen: `ek_eval.py`
- Ausgangslage: `ek_base.py` → `ergebnisse/ek_base.txt`
- Sensitivität: `ek_ofat.py`
- Suche: `ek_ca.py` (`R:TV` Walk-Forward, `R:TVZ` Endlauf)
- Kandidaten: `ek_kand.py`
- Plateau: `ek_plateau.py`
- Randparameter: `ek_rand.py`
- Größe: `ek_groesse.py`
- Endbewertung: `ek_final.py 1.0` (plus `ergebnisse/ek_final_trades.txt`)
- Prüfungen: `t_ek_sim.py`, `t_ek_port.py`, `t_ek_set.py`, `../Replikat_v6/t_mq5.py RSI21_EK.mq5`
