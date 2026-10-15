# Familie „noise_indizes“ – Bericht (15.10.2026)

Auftrag: Noise-Area-Momentum (Zarattini/Aziz/Barbon 2024) als Portfolio über 11 Index-CFDs, jeweils mit der lokalen Kassasitzung. Ziel: mehr Setups je Tag (Ziel 4) bei positiver Erwartung.
Alle Zahlen sind netto (Kosten aus `qdata.COST`, Annahmen) und mit `qbt.simulate` gerechnet. Nullmodell aus `qbt.report_cell` (K 20). Train = dev-Start bis 2023 (NAS100 ab 2021), Val = 2024 (einmal angesehen), 2025 nur als Information.
Die Regeln, die Auswahlregel und die Kandidatenregel standen vor der ersten Rechnung fest (`REGELN.md`).

## Kurzfazit
- **„Alle 11 Indizes“ ohne Auswahl ist negativ:** Train −0,037 R je Trade (N10_EOD, t −2,8), 2024 −0,025 R. Es gibt rund 3,1–4,0 Trades je Handelstag und an 87–92 % der Tage mindestens einen Trade, aber der Vorteil fehlt. 2025 (nur Info) liegt das Portfolio leicht im Plus (+0,03 R).
- **Der Effekt ist auf wenige Märkte begrenzt.** Brutto (vor Kosten) positiv auf Train sind nur NAS100, JPN225, US500 und HK50. Auf UK100, AUS200, US30, US2000 und FRA40 ist das Ergebnis schon vor Kosten negativ, auf UK100 deutlich (−0,13 R brutto, also eher Umkehr als Momentum). Bei GER40 und ESTX50 liegt es vor Kosten bei etwa null.
- **Auswahlportfolio S1** (vorab festgelegt: Train R > 0 und R > Null-R). Gewählt wurden NAS100, US500, JPN225 und HK50, bei Regel A und B zusätzlich GER40. Ergebnis: Train +0,04 bis +0,07 R (Tages-t 2,4–2,9), 2024 +0,04 bis +0,08 R (Tages-t 1,0–1,6), 2025 +0,05 bis +0,09 R. Das sind 1,0–1,7 Trades je Handelstag, an 63–75 % der Tage gibt es mindestens einen Trade.
- **Vom Zielprofil weit entfernt:** R je Trade liegt bei rund 0,04–0,09, gefordert sind 0,5 R. Ziel 4 ist im Mittel erreicht (≥ 1 Trade je Tag), aber nicht an jedem Tag (höchstens 75 %). Target vor Stop ≥ 60 % schafft nur Regel B mit dem Teilziel (73–77 % Teilziel vor Stop).
- **Die Auswahl der Instrumente ist auf Instrumentenebene instabil.** JPN225 war auf Train stark (+0,10 R, t 2,4), 2024 und 2025 ist es negativ. GER40 war auf Train bei null und 2024 stark (+0,14 R). Nur NAS100 ist durchgehend positiv. Ein Teil des Train-Vorteils von S1 ist Auswahlverzerrung (siehe Prüfung unten).

## Umsetzung
- **Sitzungen** (`ni_sitzung.py`): `noise.SESS` unverändert, ergänzt um HK50 (Asia/Hong_Kong 9:30–16:00, letzter Ausstieg 15:30) und Mittagspausen (JPN225 11:30–12:30 Tokio, HK50 12:00–13:00 Hongkong).
- **Befund `noise.prepare`/`qbt.session_frame`:** Die Funktionen kennen keine Mittagspause. Bei JPN225 gelten die Pausen-Kerzen als Sitzung (der CFD folgt dem Nikkei-Future und läuft durch). Das M30-Raster erzeugt dann Signale um 12:00 und 12:30 Tokio mitten in der Pause (Train, Paper-Einstieg: 146 + 145 Signale), und die Pausen-Kerzen fließen in VWAP und Noise-Area ein. HK50 fehlt in `SESS` ganz.
  - Nachbau: Kerzen, deren Zeitraum in der Pause beginnt, bekommen `in_sess = False`, bevor die Noise-Area berechnet wird. Das Raster bleibt uhrzeitbasiert. Signalmarken: JPN225 9:30–11:30 und 13:00–14:00, HK50 10:00–12:00 und 13:30–15:00 (geprüft). Offene Positionen laufen durch die Pause.
  - Auswirkung bei JPN225 N10_EOD Train: Nur 9 von 245 Trades hatten ihr Signal in der Pause. Das Ergebnis ist praktisch gleich (+0,100 R mit `noise.prepare`, +0,100 R mit `ni_sitzung.prepare`).
- **Regeln** (`ni_regeln.py`, je Instrument gleich): Einstieg E0 = noise-1.0 (M30 ab Kassaeröffnung + 30 min, Noise-Area Lookback 14, Trendfilter Vortagesschluss gegen SMA20, Stop Bandmitte, Market).
  - `N10_480`: erster Trade des Tages, 1R, 480 min (nur Vergleich).
  - `N10_EOD`: wie N10_480, aber Ausstieg zum letzten Ausstieg der Sitzung (für Alex maßgeblich).
  - `A`: wie N10_EOD mit Ziel 1,5R.
  - `B`: Paper-Einstieg (alle Halbstunden-Signale, Wiedereinstieg), 50 % bei 0,5R, danach Break-even, Rest bis Fensterende.
- **VWAP** wird ohne Volumen gleichgewichtet (Pedram und ts4 ohne echtes Volumen). Keine der vier Regeln nutzt VWAP.
- **Portfolio:** Ein Tag ist das Serverdatum (NY+7). Asien-, Europa- und US-Sitzung desselben Kalendertags liegen auf demselben Serverdatum. Handelstage sind Werktage mit Sitzungskerzen bei mindestens einem Instrument (Train 1035, 2024 259). Das Tages-Cluster-t rechnet mit der Summe R je Tag (wie `qbt`). Das Portfolio-Nullmodell ist das trade-gewichtete Mittel der Instrument-Nullmodelle.

## Datenprüfung (`qa_daten.py`, nur Train)
- **Zeitlage:** Die größte mittlere 5-min-Bewegung liegt bei allen 11 Instrumenten an der lokalen Kassaeröffnung. Die Umrechnung UTC → Serverzeit stimmt also. Bei HK50 gibt es zusätzlich eine Spitze an der Futures-Eröffnung 9:15, bei AUS200 am SPI-Start 9:50.
- **Mittagspause:** HK50 hat in der Pause praktisch keine Kerzen, weil die HSI-Futures pausieren. JPN225 hat dort Kerzen mit geringer Bewegung (4,5 bp gegen 7,7 bp am Vormittag).
- **Lücken:**
  - FRA40 und UK100: Von 2023-03 bis 2023-07 fehlt am Nachmittag etwa die Hälfte der Kerzen (113 bzw. 115 Tage).
  - AUS200: An 29 Tagen fehlt die erste Stunde. Dort ist die Tageseröffnung O falsch, weil die erste vorhandene Kerze genommen wird.
  - Die Regeln bleiben trotzdem unverändert (wie im gesperrten Lauf), die Lücken sind hier nur dokumentiert. `qbt.noise_area` liefert `day_ok`, aber `noise.signals` nutzt es nicht.
- Pedram hat in 2023 bei mehreren Instrumenten weniger Kerzen als in anderen Jahren (siehe `qdata.coverage`).

## Literatur (Schritt 3)
WebSearch funktionierte. WebFetch scheiterte an allen Fachseiten (DNS-Fehler: nd.edu, eprints, worktribe, ideas.repec, efmaefm, alphaarchitect). Die Angaben stammen deshalb aus Suchtreffern und Abstracts, nicht aus Volltexten.
- **Zarattini/Aziz/Barbon 2024/2025** („Beat the Market“, SSRN): nur SPY. Eine Folgearbeit, die die Noise-Area auf Nicht-US-Indizes (DAX, Nikkei, FTSE, HSI) testet, habe ich nicht gefunden.
- **Gao/Han/Li/Zhou 2018** (JFE, „Market intraday momentum“): Die erste Halbstunde sagt die letzte Halbstunde voraus (SPY 1993–2013). Der Effekt ist laut Abstract auch stark bei 10 weiteren ETFs und 2 internationalen Index-Futures (ohne Namen im Abstract).
- **Baltussen/Da/Lammers/Martens 2021** (JFE 142, 377–403): über 60 Futures 1974–2020, darunter Aktienindex-Futures aus 17 entwickelten Märkten (Nordamerika, 8 aus Europa, Australasien). Der Rest des Tages (ab Vortagesschluss) sagt die letzten 30 min vorher. Am stärksten bei Nasdaq-100. Die Länderergebnisse waren nicht zugänglich.
- **Li/Sakkas/Urquhart 2022** (JFM 57, 100619): Intraday-Momentum in 16 entwickelten Märkten, in den meisten signifikant (laut Zitat 12 von 16). Stärker bei geringer Liquidität und hoher Volatilität.
- **Limkriangkrai/Chai/Zheng 2023** (Pacific-Basin Finance Journal, APAC-ETFs): Der Effekt zeigt sich vor allem in China und Japan, in Hongkong und Singapur nicht.
- **Liu/Tse 2017** (12 internationale Index-Futures): Die erste Halbstunde sagt nichts vorher, der Übernacht-Ertrag schon.
- Eine Arbeit zu Interday-Cross-Sectional-Momentum findet in Europa kein signifikantes Intraday-Momentum.
- **Übernommen: keine neue Regel.**
  - Der belegte Effekt ist ein anderes Setup: Halten nur in den letzten 30 min. Das wäre eher ein Scalp und passt nicht zu Alex' Profil.
  - Ein Länderfilter aus der Literatur ist nicht klar und widerspruchsfrei definiert.
  - Der Übernacht-Ertrag (Liu/Tse, Baltussen) steckt in der Noise-Area schon über max(O, Vortagesschluss).
  - Die Literatur stützt aber die Vorab-Erwartung: Außerhalb der USA ist der Effekt schwächer und uneinheitlich, in Japan eher vorhanden, in Hongkong und Europa eher nicht. Die Ergebnisse passen dazu, mit Ausnahme von HK50.

## Ergebnisse
### Zellen je Instrument × Regel (Train / Val 2024 mit Nullmodell; 2025 nur Info)
| Instrument | Regel | Train n | /Tag | Treffer | Gew. | R netto | t | Null Treffer | Null R | t vs Null | Val n | /Tag | Treffer | Gew. | R netto | t | Null Treffer | Null R | 2025 n | 2025 R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NAS100 | N10_480 | 226 | 0.29 | 57 % | 60 % | +0.113 | 2.04 | 48 % | -0.040 | 2.76 | 68 | 0.26 | 57 % | 59 % | +0.138 | 1.41 | 53 % | +0.042 | 62 | +0.120 |
| NAS100 | N10_EOD | 225 | 0.29 | 53 % | 58 % | +0.105 | 2.04 | 48 % | -0.032 | 2.67 | 68 | 0.26 | 58 % | 65 % | +0.150 | 1.61 | 49 % | -0.001 | 62 | +0.084 |
| NAS100 | A | 225 | 0.29 | 35 % | 56 % | +0.139 | 2.39 | 32 % | -0.028 | 2.87 | 68 | 0.26 | 35 % | 62 % | +0.164 | 1.54 | 33 % | +0.026 | 62 | +0.091 |
| NAS100 | B | 255 | 0.33 | 77 % | 67 % | +0.110 | 2.76 | – | -0.026 | 3.41 | 78 | 0.30 | 75 % | 67 % | +0.125 | 1.68 | – | +0.001 | 74 | +0.054 |
| US500 | N10_480 | 304 | 0.29 | 53 % | 54 % | +0.025 | 0.50 | 49 % | -0.028 | 1.08 | 80 | 0.31 | 48 % | 52 % | +0.002 | 0.02 | 50 % | -0.033 | 66 | +0.045 |
| US500 | N10_EOD | 304 | 0.29 | 48 % | 55 % | +0.028 | 0.64 | 49 % | -0.028 | 1.27 | 80 | 0.31 | 47 % | 54 % | +0.013 | 0.14 | 50 % | -0.015 | 66 | +0.081 |
| US500 | A | 304 | 0.29 | 32 % | 52 % | +0.051 | 1.03 | 34 % | -0.019 | 1.42 | 80 | 0.31 | 24 % | 46 % | -0.083 | -0.82 | 35 % | +0.001 | 66 | +0.045 |
| US500 | B | 345 | 0.33 | 71 % | 62 % | +0.024 | 0.68 | – | -0.016 | 1.12 | 96 | 0.37 | 62 % | 59 % | -0.054 | -0.72 | – | -0.010 | 78 | +0.063 |
| US30 | N10_480 | 305 | 0.29 | 47 % | 50 % | -0.049 | -1.03 | 49 % | -0.027 | -0.47 | 91 | 0.35 | 47 % | 44 % | -0.109 | -1.23 | 50 % | -0.020 | 89 | -0.007 |
| US30 | N10_EOD | 305 | 0.29 | 42 % | 49 % | -0.067 | -1.57 | 50 % | -0.019 | -1.12 | 91 | 0.35 | 40 % | 44 % | -0.138 | -1.69 | 49 % | -0.014 | 89 | +0.069 |
| US30 | A | 305 | 0.29 | 21 % | 47 % | -0.081 | -1.82 | 34 % | -0.017 | -1.44 | 91 | 0.35 | 24 % | 44 % | -0.094 | -1.05 | 33 % | +0.004 | 89 | +0.101 |
| US30 | B | 351 | 0.34 | 67 % | 58 % | -0.054 | -1.59 | – | -0.019 | -1.02 | 102 | 0.39 | 59 % | 50 % | -0.133 | -1.91 | – | -0.021 | 96 | +0.059 |
| US2000 | N10_480 | 307 | 0.30 | 43 % | 45 % | -0.096 | -2.11 | 50 % | -0.040 | -1.22 | 80 | 0.31 | 40 % | 41 % | -0.141 | -1.65 | 50 % | -0.039 | 79 | -0.010 |
| US2000 | N10_EOD | 307 | 0.30 | 40 % | 48 % | -0.078 | -1.92 | 51 % | -0.026 | -1.27 | 80 | 0.31 | 42 % | 38 % | -0.135 | -1.77 | 51 % | -0.033 | 79 | -0.029 |
| US2000 | A | 307 | 0.30 | 20 % | 45 % | -0.088 | -2.06 | 33 % | -0.024 | -1.50 | 80 | 0.31 | 23 % | 34 % | -0.175 | -2.15 | 35 % | -0.026 | 79 | -0.046 |
| US2000 | B | 361 | 0.35 | 67 % | 55 % | -0.078 | -2.39 | – | -0.038 | -1.22 | 89 | 0.34 | 66 % | 46 % | -0.162 | -2.86 | – | -0.042 | 89 | -0.057 |
| GER40 | N10_480 | 304 | 0.29 | 49 % | 51 % | -0.002 | -0.04 | 51 % | -0.008 | 0.12 | 101 | 0.39 | 63 % | 58 % | +0.150 | 1.81 | 51 % | -0.007 | 78 | +0.117 |
| GER40 | N10_EOD | 304 | 0.29 | 48 % | 51 % | -0.029 | -0.64 | 51 % | -0.012 | -0.38 | 101 | 0.39 | 67 % | 55 % | +0.140 | 1.76 | 50 % | -0.009 | 78 | +0.146 |
| GER40 | A | 304 | 0.29 | 37 % | 49 % | +0.010 | 0.20 | 37 % | -0.004 | 0.26 | 101 | 0.39 | 53 % | 50 % | +0.153 | 1.64 | 37 % | +0.000 | 78 | +0.212 |
| GER40 | B | 358 | 0.35 | 72 % | 63 % | +0.022 | 0.60 | – | -0.022 | 1.21 | 127 | 0.49 | 81 % | 65 % | +0.065 | 1.15 | – | -0.011 | 96 | +0.149 |
| FRA40 | N10_480 | 331 | 0.32 | 47 % | 47 % | -0.082 | -1.73 | 50 % | -0.047 | -0.74 | 94 | 0.37 | 47 % | 45 % | -0.121 | -1.38 | 51 % | -0.042 | 83 | -0.058 |
| FRA40 | N10_EOD | 334 | 0.33 | 47 % | 46 % | -0.075 | -1.72 | 49 % | -0.049 | -0.58 | 94 | 0.37 | 50 % | 45 % | -0.073 | -0.90 | 50 % | -0.042 | 83 | +0.013 |
| FRA40 | A | 334 | 0.33 | 34 % | 46 % | -0.035 | -0.72 | 35 % | -0.041 | 0.12 | 94 | 0.37 | 35 % | 41 % | -0.061 | -0.68 | 33 % | -0.053 | 83 | -0.001 |
| FRA40 | B | 408 | 0.40 | 69 % | 57 % | -0.066 | -2.02 | – | -0.047 | -0.56 | 110 | 0.43 | 72 % | 57 % | -0.043 | -0.68 | – | -0.037 | 99 | -0.019 |
| ESTX50 | N10_480 | 312 | 0.30 | 49 % | 50 % | -0.038 | -0.81 | 51 % | -0.042 | 0.08 | 96 | 0.37 | 48 % | 51 % | -0.051 | -0.59 | 51 % | -0.071 | 92 | -0.106 |
| ESTX50 | N10_EOD | 313 | 0.30 | 48 % | 47 % | -0.064 | -1.42 | 52 % | -0.035 | -0.64 | 96 | 0.37 | 51 % | 47 % | -0.061 | -0.76 | 51 % | -0.070 | 92 | -0.079 |
| ESTX50 | A | 313 | 0.30 | 32 % | 44 % | -0.056 | -1.11 | 37 % | -0.026 | -0.58 | 96 | 0.37 | 36 % | 42 % | -0.091 | -1.00 | 38 % | -0.051 | 92 | -0.042 |
| ESTX50 | B | 382 | 0.37 | 66 % | 57 % | -0.070 | -1.95 | – | -0.043 | -0.76 | 119 | 0.46 | 72 % | 60 % | -0.026 | -0.37 | – | -0.080 | 103 | -0.064 |
| UK100 | N10_480 | 287 | 0.28 | 40 % | 41 % | -0.176 | -3.58 | 49 % | -0.048 | -2.59 | 86 | 0.33 | 48 % | 48 % | -0.089 | -0.92 | 49 % | -0.085 | 90 | -0.019 |
| UK100 | N10_EOD | 287 | 0.28 | 42 % | 41 % | -0.163 | -3.50 | 49 % | -0.044 | -2.55 | 86 | 0.33 | 47 % | 48 % | -0.094 | -1.00 | 47 % | -0.089 | 90 | -0.026 |
| UK100 | A | 287 | 0.28 | 29 % | 39 % | -0.152 | -2.95 | 34 % | -0.046 | -2.05 | 86 | 0.33 | 24 % | 41 % | -0.181 | -1.81 | 34 % | -0.076 | 90 | -0.004 |
| UK100 | B | 348 | 0.34 | 66 % | 55 % | -0.087 | -2.30 | – | -0.050 | -0.97 | 100 | 0.38 | 67 % | 58 % | -0.118 | -1.78 | – | -0.086 | 103 | -0.026 |
| JPN225 | N10_480 | 244 | 0.24 | 64 % | 53 % | +0.101 | 2.08 | 51 % | -0.038 | 2.86 | 66 | 0.25 | 55 % | 50 % | +0.029 | 0.27 | 53 % | -0.003 | 70 | -0.093 |
| JPN225 | N10_EOD | 244 | 0.24 | 64 % | 59 % | +0.100 | 2.38 | 49 % | -0.036 | 3.23 | 66 | 0.25 | 51 % | 47 % | -0.055 | -0.57 | 52 % | -0.015 | 70 | -0.108 |
| JPN225 | A | 244 | 0.24 | 47 % | 58 % | +0.123 | 2.60 | 31 % | -0.029 | 3.21 | 66 | 0.25 | 39 % | 45 % | +0.000 | 0.00 | 37 % | +0.010 | 70 | -0.112 |
| JPN225 | B | 274 | 0.26 | 83 % | 64 % | +0.068 | 2.09 | – | -0.050 | 3.64 | 71 | 0.27 | 70 % | 55 % | -0.027 | -0.32 | – | -0.056 | 74 | -0.118 |
| AUS200 | N10_480 | 269 | 0.26 | 49 % | 43 % | -0.121 | -2.48 | 48 % | -0.075 | -0.94 | 61 | 0.24 | 48 % | 43 % | -0.146 | -1.42 | 49 % | -0.088 | 70 | +0.061 |
| AUS200 | N10_EOD | 270 | 0.26 | 44 % | 41 % | -0.141 | -3.32 | 48 % | -0.067 | -1.73 | 61 | 0.24 | 48 % | 41 % | -0.115 | -1.34 | 49 % | -0.068 | 69 | +0.062 |
| AUS200 | A | 270 | 0.26 | 31 % | 39 % | -0.131 | -2.84 | 31 % | -0.066 | -1.41 | 61 | 0.24 | 27 % | 41 % | -0.096 | -1.04 | 24 % | -0.082 | 69 | +0.081 |
| AUS200 | B | 299 | 0.29 | 66 % | 49 % | -0.138 | -3.73 | – | -0.052 | -2.32 | 67 | 0.26 | 67 % | 49 % | -0.100 | -1.37 | – | -0.076 | 77 | +0.070 |
| HK50 | N10_480 | 278 | 0.28 | 56 % | 53 % | +0.035 | 0.76 | 50 % | -0.028 | 1.37 | 59 | 0.23 | 61 % | 58 % | +0.123 | 1.27 | 48 % | -0.047 | 68 | +0.132 |
| HK50 | N10_EOD | 280 | 0.28 | 52 % | 54 % | +0.028 | 0.68 | 50 % | -0.033 | 1.48 | 59 | 0.23 | 61 % | 63 % | +0.125 | 1.42 | 47 % | -0.071 | 68 | +0.138 |
| HK50 | A | 280 | 0.28 | 34 % | 53 % | +0.048 | 1.07 | 30 % | -0.036 | 1.87 | 59 | 0.23 | 44 % | 63 % | +0.167 | 1.70 | 30 % | -0.066 | 68 | +0.183 |
| HK50 | B | 315 | 0.31 | 74 % | 58 % | +0.002 | 0.07 | – | -0.024 | 0.81 | 63 | 0.25 | 79 % | 65 % | +0.105 | 1.41 | – | -0.012 | 75 | +0.078 |

Treffer = Target vor Stop; bei Regel B Teilziel (0,5R) vor Stop.


### Kosten in R je Trade (Regel N10_EOD) und Brutto-R
| Instrument | COST | Stop-Abstand (Median, % Kurs) | Kosten R Train | Kosten R 2024 | Brutto R Train N10_EOD | Brutto R 2024 | Brutto R Train A | Brutto R 2024 A |
|---|---|---|---|---|---|---|---|---|
| NAS100 | 1.0 bp | 0.83 % | 0.013 | 0.016 | +0.118 | +0.166 | +0.152 | +0.180 |
| US500 | 1.0 bp | 0.61 % | 0.019 | 0.027 | +0.047 | +0.040 | +0.070 | -0.056 |
| US30 | 1.2 bp | 0.61 % | 0.022 | 0.028 | -0.045 | -0.111 | -0.060 | -0.066 |
| US2000 | 3.0 bp | 1.07 % | 0.031 | 0.037 | -0.047 | -0.099 | -0.058 | -0.138 |
| GER40 | 1.0 bp | 0.69 % | 0.017 | 0.027 | -0.012 | +0.167 | +0.027 | +0.180 |
| FRA40 | 2.0 bp | 0.64 % | 0.035 | 0.043 | -0.040 | -0.030 | +0.000 | -0.018 |
| ESTX50 | 3.0 bp | 0.70 % | 0.052 | 0.072 | -0.012 | +0.011 | -0.004 | -0.019 |
| UK100 | 2.0 bp | 0.59 % | 0.038 | 0.057 | -0.126 | -0.036 | -0.114 | -0.124 |
| JPN225 | 3.0 bp | 0.77 % | 0.044 | 0.045 | +0.144 | -0.010 | +0.166 | +0.045 |
| AUS200 | 3.0 bp | 0.53 % | 0.063 | 0.072 | -0.078 | -0.043 | -0.068 | -0.024 |
| HK50 | 3.0 bp | 1.03 % | 0.031 | 0.029 | +0.059 | +0.155 | +0.079 | +0.197 |


### Portfolios (Tag = Serverdatum; Treffer bei B = Teilziel vor Stop; Null R = trade-gewichtet)
| Regel | Auswahl | Zeitraum | Instr. | n | Trades/Tag | Tage mit >=1 Trade | Treffer | Gew. | R netto | t | Tages-t | R/Tag | Null R | t vs Null | Kosten R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N10_480 | alle | Train | 11 | 3167 | 3.06 | 87 % | 50 % | 49 % | -0.031 | -2.15 | -1.54 | -0.096 | -0.038 | 0.45 | 0.033 |
| N10_480 | alle | Val 2024 | 11 | 882 | 3.41 | 92 % | 51 % | 50 % | -0.023 | -0.81 | -0.66 | -0.078 | -0.036 | 0.47 | 0.041 |
| N10_480 | alle | info 2025 | 11 | 847 | 3.28 | 91 % | 54 % | 51 % | +0.010 | 0.36 | 0.27 | +0.033 | -0.030 | 1.42 | 0.040 |
| N10_480 | S1 | Train | 4 | 1052 | 1.02 | 63 % | 57 % | 55 % | +0.064 | 2.58 | 2.39 | +0.065 | -0.033 | 3.91 | 0.027 |
| N10_480 | S1 | Val 2024 | 4 | 273 | 1.05 | 63 % | 55 % | 55 % | +0.069 | 1.37 | 1.21 | +0.072 | -0.010 | 1.57 | 0.029 |
| N10_480 | S1 | info 2025 | 4 | 266 | 1.03 | 65 % | 56 % | 53 % | +0.048 | 1.02 | 0.93 | +0.050 | -0.023 | 1.50 | 0.027 |
| N10_EOD | alle | Train | 11 | 3173 | 3.07 | 87 % | 47 % | 50 % | -0.037 | -2.81 | -2.07 | -0.115 | -0.035 | -0.21 | 0.033 |
| N10_EOD | alle | Val 2024 | 11 | 882 | 3.41 | 92 % | 51 % | 49 % | -0.025 | -0.96 | -0.81 | -0.086 | -0.038 | 0.50 | 0.041 |
| N10_EOD | alle | info 2025 | 11 | 846 | 3.28 | 91 % | 54 % | 53 % | +0.028 | 1.08 | 0.83 | +0.090 | -0.034 | 2.41 | 0.040 |
| N10_EOD | S1 | Train | 4 | 1053 | 1.02 | 63 % | 53 % | 56 % | +0.061 | 2.74 | 2.56 | +0.062 | -0.032 | 4.18 | 0.027 |
| N10_EOD | S1 | Val 2024 | 4 | 273 | 1.05 | 63 % | 53 % | 57 % | +0.055 | 1.17 | 1.05 | +0.058 | -0.024 | 1.67 | 0.029 |
| N10_EOD | S1 | info 2025 | 4 | 266 | 1.03 | 65 % | 52 % | 56 % | +0.047 | 1.15 | 1.08 | +0.048 | -0.021 | 1.67 | 0.027 |
| A | alle | Train | 11 | 3173 | 3.07 | 87 % | 32 % | 48 % | -0.021 | -1.44 | -1.04 | -0.065 | -0.030 | 0.61 | 0.033 |
| A | alle | Val 2024 | 11 | 882 | 3.41 | 92 % | 33 % | 46 % | -0.032 | -1.11 | -0.91 | -0.110 | -0.028 | -0.16 | 0.041 |
| A | alle | info 2025 | 11 | 846 | 3.28 | 91 % | 37 % | 51 % | +0.043 | 1.49 | 1.12 | +0.141 | -0.030 | 2.53 | 0.040 |
| A | S1 | Train | 5 | 1357 | 1.31 | 72 % | 36 % | 53 % | +0.068 | 3.06 | 2.88 | +0.090 | -0.022 | 4.05 | 0.025 |
| A | S1 | Val 2024 | 5 | 374 | 1.44 | 75 % | 39 % | 53 % | +0.080 | 1.74 | 1.63 | +0.115 | -0.004 | 1.82 | 0.029 |
| A | S1 | info 2025 | 5 | 344 | 1.33 | 74 % | 38 % | 53 % | +0.087 | 2.05 | 1.98 | +0.115 | -0.019 | 2.51 | 0.026 |
| B | alle | Train | 11 | 3696 | 3.57 | 87 % | 70 % | 58 % | -0.029 | -2.75 | -1.98 | -0.105 | -0.035 | 0.56 | 0.033 |
| B | alle | Val 2024 | 11 | 1022 | 3.95 | 92 % | 70 % | 58 % | -0.036 | -1.71 | -1.42 | -0.142 | -0.039 | 0.16 | 0.041 |
| B | alle | info 2025 | 11 | 964 | 3.74 | 91 % | 73 % | 60 % | +0.016 | 0.72 | 0.52 | +0.059 | -0.032 | 2.22 | 0.039 |
| B | S1 | Train | 5 | 1547 | 1.49 | 72 % | 75 % | 63 % | +0.041 | 2.57 | 2.45 | +0.061 | -0.027 | 4.24 | 0.024 |
| B | S1 | Val 2024 | 5 | 435 | 1.68 | 75 % | 73 % | 63 % | +0.040 | 1.25 | 1.15 | +0.068 | -0.016 | 1.76 | 0.028 |
| B | S1 | info 2025 | 5 | 397 | 1.54 | 74 % | 77 % | 61 % | +0.051 | 1.70 | 1.65 | +0.079 | -0.015 | 2.20 | 0.025 |


## Welche Instrumente haben bei diesen Kosten eine Chance?
Die Kosten in R je Trade ergeben sich aus `COST · Kurs / Stopabstand`. Der Stop liegt in der Bandmitte, typisch 0,5–1,1 % vom Kurs. Der Brutto-Vorteil von noise-1.0 auf dem besten Markt (NAS100) beträgt etwa 0,12–0,17 R.
- **Kosten unkritisch:**
  - NAS100: 0,013–0,016 R.
  - GER40: 0,017–0,027 R.
  - US500: 0,019–0,027 R.
  - US30: 0,022–0,028 R.
- **Kosten erheblich:**
  - HK50: 0,03 R.
  - US2000: 0,03–0,04 R.
  - FRA40: 0,035–0,043 R.
  - UK100: 0,04–0,06 R.
  - JPN225: 0,044 R.
  - ESTX50 und AUS200: 0,05–0,07 R. Das ist die Hälfte eines typischen Vorteils von 0,1 R.
- **Eine Chance haben nur:**
  - NAS100: brutto Train +0,12, 2024 +0,17.
  - HK50: brutto +0,06 / +0,16.
  - GER40: brutto Train −0,01, 2024 +0,17, also unsicher.
  - US500: brutto +0,05 / +0,04, kaum mehr als die Kosten.
  - JPN225: brutto Train +0,14, danach negativ.
- **Ohne Chance**, weil das Ergebnis schon vor Kosten nicht positiv ist: US30, US2000, FRA40, UK100, AUS200.
- **ESTX50:** brutto etwa null, die Kosten von 3 bp machen es negativ.
- Der echte Qberx-Spread ist unbekannt. Ist er bei den Nicht-US-Indizes kleiner als angenommen, ändert das am Bild wenig: Die Verlierer sind auch brutto Verlierer.

## Auswahlverzerrung
S1 wurde auf Train gewählt, deshalb sind die Train-Zahlen von S1 (t gegen Null ≈ 4) zu gut. Zur Prüfung (`extra_train.py`, nur Train) habe ich S1 auf einer Train-Hälfte gewählt (H1 = bis 2021, H2 = 2022–23) und auf der anderen gemessen:

| Regel | Auswahl auf | gewählt | R auf der anderen Hälfte (n, t) | Rest (nicht gewählt) | alle |
|---|---|---|---|---|---|
| N10_EOD | H1 | NAS100, US500, JPN225, HK50 | +0,044 (612, 1,5) | −0,086 | −0,041 |
| N10_EOD | H2 | NAS100, US500, JPN225, HK50 | +0,085 (441, 2,5) | −0,087 | −0,033 |
| A | H1 | NAS100, US500, JPN225, HK50 | +0,065 (612, 2,0) | −0,066 | −0,021 |
| A | H2 | NAS100, US500, GER40, JPN225, HK50 | +0,082 (568, 2,5) | −0,092 | −0,021 |
| B | H1 | NAS100, US500, JPN225 | +0,044 (525, 1,6) | −0,043 | −0,021 |
| B | H2 | NAS100, GER40, JPN225, HK50 | +0,025 (492, 0,9) | −0,069 | −0,040 |

- Die Auswahl ist zwischen den Hälften recht stabil, und die gewählten Instrumente bleiben auf der anderen Hälfte positiv. Die abgewählten bleiben negativ.
- Auf 2024 und 2025 hält das Vorzeichen des Portfolios ebenfalls. Innerhalb des Portfolios wechseln aber die Träger: 2024 trugen NAS100, GER40 und HK50, während JPN225 kippte.
- Ehrliche Erwartung für S1: etwa +0,04 bis +0,08 R je Trade netto. Das liegt unter den Train-Zahlen.

## Kandidaten (nach der vorab festgelegten Kandidatenregel)
Alle drei erfüllen die Bedingung: Train R > 0 mit Tages-t ≥ 2 und t gegen Null ≥ 2, 2024 R netto > 0. Es ist dreimal derselbe Einstieg. Die Kandidaten sind also stark überlappend und nicht unabhängig. Für den gesperrten Test sollte die Bewertung auf Portfolio-Ebene erfolgen (alle Trades der Instrumente zusammen). Die Einzelzellen je Instrument sind mit n ≈ 60–100 je Jahr zu klein.

| Kandidat | Instrumente | Train n / Tag / Tage ≥1 / Treffer / R / Tages-t | Null R Train | 2024 n / Tag / Treffer / R / Tages-t | Null R 2024 | 2025 (Info) R |
|---|---|---|---|---|---|---|
| `kandidat_A_s1.py` | NAS100, US500, GER40, JPN225, HK50 | 1357 / 1,31 / 72 % / TvS 36 % / +0,068 / 2,88 | −0,022 | 374 / 1,44 / 39 % / +0,080 / 1,63 | −0,004 | +0,087 (n 344) |
| `kandidat_B_s1.py` | NAS100, US500, GER40, JPN225, HK50 | 1547 / 1,49 / 72 % / TP1vS 75 % / +0,041 / 2,45 | −0,027 | 435 / 1,68 / 73 % / +0,040 / 1,15 | −0,016 | +0,051 (n 397, TP1vS 77 %) |
| `kandidat_n10eod_s1.py` | NAS100, US500, JPN225, HK50 | 1053 / 1,02 / 63 % / TvS 53 % / +0,061 / 2,56 | −0,032 | 273 / 1,05 / 53 % / +0,055 / 1,05 | −0,024 | +0,047 (n 266) |

- **A_s1:** Einstieg wie noise-1.0 je lokaler Kassasitzung, erster Trade des Tages je Instrument. Stop Bandmitte, Ziel 1,5R, Zeitausstieg zum letzten Ausstieg der Sitzung. Höchstes R je Trade und je Tag.
- **B_s1:** Paper-Einstieg (alle Halbstunden-Signale mit SMA20-Filter, Wiedereinstieg), Stop Bandmitte. Teilziel 0,5R für 50 %, danach Break-even, Rest bis Fensterende. Einziger Kandidat mit „Treffer“ ≥ 60 % (Teilziel vor Stop) und die meisten Setups.
- **n10eod_s1:** noise-1.0 als echter Daytrade (Ziel 1R, Ausstieg zum Sitzungsende) auf 4 Instrumenten. Etwa 1 Trade je Tag, das Vierfache von noise-1.0 allein.
- **Quelle:** Einstieg Zarattini/Aziz/Barbon 2024. Die Ausstiege A und B stammen aus der Familie „ausstiege“. Auswahl S1 nach REGELN.md.
- **Reihenfolge, falls nur einer geprüft wird:** A_s1, dann B_s1. n10eod_s1 bringt gegenüber A_s1 wenig Neues.
- **Prüfungen** (`pruefung.py`), für alle 3 Kandidaten und alle Instrumente erfüllt:
  - Das Kandidatenmodul liefert dieselben Trades wie der Forschungslauf.
  - Abschneide-Test an 10 Zeitpunkten je Instrument: gleiche Signale. `i_last` wird nur für abgeschlossene Tage verglichen.
  - Laden ab Auswertungsbeginn − 90 Tage (wie `locked_run`) gibt dieselben Signale wie ab dev-Start.

## Zielprofil
| Ziel | A_s1 | B_s1 | n10eod_s1 | alle 11 (N10_EOD) |
|---|---|---|---|---|
| 1 positive Erwartung | Train/2024/2025 positiv | positiv | positiv | negativ (2025 leicht positiv) |
| 2 ≥ 0,5 R je Trade | nein (0,07–0,09) | nein (0,04–0,05) | nein (0,047–0,061) | nein |
| 3 Target vor Stop ≥ 60 % | nein (36–39 %) | ja, Teilziel 73–77 % | nein (52–53 %) | nein |
| 4 ≥ 1 Setup je Handelstag | im Mittel 1,3–1,4; Tage ≥1: 72–75 % | 1,5–1,7; 72–75 % | 1,0; 63–65 % | 3,1–3,4; 87–92 % |

Praktischer Hinweis: Serverzeit ist NY+7, deutsche Zeit liegt etwa 1 h darunter. Die Asien-Setups liegen damit nachts: JPN225-Einstiege etwa 1–6 Uhr, HK50 etwa 3–9 Uhr deutscher Zeit. Market-Einstiege sind für Alex dort kaum handelbar. Ohne JPN225 und HK50 bleiben 2024 bei A_s1 0,96, bei B_s1 1,16 und bei n10eod_s1 0,57 Trades je Tag.

## Varianten
59 Varianten im Ledger (`ergebnisse/varianten/noise_indizes.csv`):
- 44 Zellen (11 Instrumente × 4 Regeln),
- 8 Portfolios (4 Regeln × {alle, S1}),
- 6 Hälften-Auswahlen,
- 1 Vergleich der Pausenbehandlung bei JPN225.

Keine Parameter wurden je Instrument abgestimmt. Nach 2024 wurde nichts mehr geändert.

## Probleme, Datenlücken, Zweifel
- **Datenlücken** (Pedram): FRA40/UK100 2023-03 bis 07 Nachmittage lückenhaft, AUS200 29 Tage ohne erste Stunde. Kein Tagesfilter (`day_ok` existiert in `qbt.noise_area`, wird von `noise.signals` aber nicht benutzt).
- **Quellen:** US30/US2000 kommen von Pedram (Bid), NAS100/US500 von ts4. Ob die schwachen Ergebnisse von US30 und US2000 an der Quelle liegen, lässt sich im dev-Zeitraum nicht prüfen (keine zweite Quelle).
- **JPN225:** Die Tokioter Börse schließt seit 05.11.2024 um 15:30 statt 15:00. `noise.SESS` (und damit hier) nutzt weiter 15:00/14:30. Das betrifft nur die letzten 2 Monate von 2024 und 2026. Nicht angepasst, weil es nach dem Blick auf 2024 eine Parameteränderung wäre.
- **HK50:** Die Sitzung 9:30–16:00 mit Ausstieg 15:30 ist eigene Festlegung (Analogie zu den Nicht-US-Sitzungen in `SESS`).
- **`lib`-Befunde** (nicht geändert):
  - `noise.prepare`/`qbt.session_frame` behandeln Mittagspausen als Sitzung (JPN225-Signale um 12:00/12:30 Tokio).
  - HK50 fehlt in `noise.SESS`.
  - `qbt.summarize` bildet Tages-Cluster nach NY-Datum. Die Asien-Sitzungen (Tokio 9:00 = 19:00/20:00 NY) werden damit über zwei NY-Tage geteilt. Für Einzelinstrumente mit einem Trade je Tag ist das harmlos. Das Portfolio hier nutzt das Serverdatum.
- **t-Werte:** 2024 sind alle t < 2 (Tages-t 1,0–1,6). Bestätigt ist nur das Vorzeichen.
- **Auswahl:** Die S1-Instrumente sind einzeln meist nicht signifikant (US500, HK50, GER40 auf Train t < 1,1). Der Kandidat lebt vom Portfolio und von NAS100.
- **Literatur:** Volltexte waren nicht erreichbar (WebFetch DNS). Die Länderergebnisse bei Baltussen et al. und Li et al. habe ich nicht selbst gelesen.
- **Beobachtung ohne Test:** UK100 und AUS200 sind brutto deutlich negativ (Umkehr statt Momentum). Eine umgekehrte Regel wäre eine nachträgliche Erfindung und wurde nicht geprüft.

## Dateien
- **Regeln und Module:** `REGELN.md` (vorab), `ni_sitzung.py`, `ni_regeln.py`, `run.py` (train/val/info25), `extra_train.py`, `pruefung.py`, `qa_daten.py`, `zusammenfassung.py`.
- **Ergebnisse:** `zellen_*.csv`, `portfolio_*.csv`, `trades_*.csv`, `auswahl_train.json`, `tabellen.txt`.
