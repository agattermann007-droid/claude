# Familie „ausstiege“ – Bericht (15.10.2026, Stand v3: korrigierte Kerzendateien)

Auftrag: bessere Ausstiege für Noise-Area-Momentum (Einstieg unverändert aus `lib/noise.py`), Ziel ≥ 0,5 R je Trade und/oder Target vor Stop > 60 %.
Hauptmarkt NAS100 (Train 2021–23, Val 2024), US500 als Robustheitsprüfung mit derselben Regel ohne eigene Abstimmung (Train 2020–23, Val 2024).
Alle Zahlen sind netto (Kosten aus `qdata.COST`) und mit `qbt.simulate` gerechnet. Nullmodell aus `qbt.null_model` (K = 20).

## Kurzfazit
- **Kein Ausstieg erreicht 0,5 R je Trade.** Auf NAS100 Train liegt das beste R je Trade mit sichtbarem Ziel und Ausstieg 15:00 bei +0,139 R (Ziel 1,5R). Mit 480 min sind es +0,175 R, aber dann läuft die Position über das Sitzungsende hinaus.
- **Target vor Stop über 60 % ist mit kleinem Ziel leicht erreichbar** (0,5R: 74–77 %). Mit Ziel 0,5R auf die ganze Position sinkt R aber (N10 +0,065 R). Ein Teilziel (50 % bei 0,5R, danach Break-even) behält die Erwartung: PAPS Train 77 % / +0,110 R (t 2,8), 2024 75 % / +0,125 R.
- Der Ausstieg verschiebt nur den Punkt auf der Trade-off-Kurve. Auf denselben Trades verbessert kein Ausstieg R gegenüber noise-1.0 signifikant. Gepaart gegen noise-1.0: Ziel 1,5R +0,024 R (t 0,8) auf Train und +0,026 R (t 0,5) in 2024. Paper-Nachzug −0,037 R (t −0,75) auf Train.
- Der Paper-Ausstieg (Nachzug max(UB,VWAP), kein Ziel) senkt R je Trade auf NAS100. Mit Wiedereinstieg erhöht er die Anzahl der Trades auf rund 1,1 je Tag und macht die Ergebnisse statistisch stabiler (t ≈ 2,6–3,0). Das Ergebnis je Trade bleibt aber klein (+0,04 R).
- US500: A und B tragen nicht (Train t ≈ 1, 2024 negativ). C erfüllt auf den korrigierten Kerzen knapp die vorab festgelegte US500-Regel (Train +0,024 R, t 2,01; 2024 +0,039 R) und umfasst deshalb jetzt NAS100 und US500.

## Umsetzung (wichtig zum Lesen der Zahlen)
- **Einstiege:** N10 = noise-1.0-Einstieg (`signals(x, grid=30, trend='cprev', one_per_day=True)`). PAPS / PAP0 = Paper-Einstieg: alle Halbstunden-Signale 10:00–14:30 NY, nach einem Ausstieg ist ein neuer Einstieg erlaubt (eine Position zur Zeit), PAPS mit und PAP0 ohne SMA20-Filter.
- **Nachzieh-Spalten** (`common.add_trails`): Der Wert wird nur am Schluss der Halbstunden-Kerzen gesetzt und gilt bis zur nächsten Marke. Er nutzt nur Daten bis zu dieser Kerze. qbt nutzt an Kerze i den Wert von i−1 und zieht den Stop nur nach.
- **R-Einheit bei Nachzieh-Ausstiegen:** Der Anfangsstop ist die Bandmitte. Er gilt nur in der Einstiegskerze, ab der nächsten Kerze greift der Nachzug. So ist R in allen Varianten in derselben Einheit gemessen (Abstand zur Bandmitte). Abweichungen vom Paper: Das Paper prüft nur zum Halbstunden-Schluss und schließt dann. Hier ruht der Stop zwischen den Marken als Stop-Order. Außerdem zieht qbt nur nach, ein fallender VWAP lockert den Stop nicht.
- **Long max(UB,VWAP) und Short min(LB,VWAP)** brauchen zwei Spalten, qbt erlaubt aber nur eine je Lauf. Deshalb rechnet `common.run` Long und Short getrennt mit `seq=False` und stellt danach exakt die Sequenzlogik von qbt nach. Geprüft: Mit einer gemeinsamen Spalte sind die Ergebnisse identisch zu `qbt.simulate(seq=True)`. Das Nullmodell wird je Spalte gerechnet und gewichtet kombiniert. Kandidat C nutzt stattdessen eine richtungsbezogene Einzelspalte (siehe Modul). Er liefert dieselben Trades (NAS100 1147, US500 1437).
- **Trefferquote:** Bei festem Ziel Target vor Stop (TvS). Bei Teilziel „Teilziel vor Stop“ (TP1vS): Dafür werden dieselben Trades ein zweites Mal mit Ziel = TP1 gerechnet, sonst mit gleichem Stop und Nachzug. Ohne Ziel gilt die Gewinnquote. Für das Nullmodell gibt es keine TP1vS, nur Gewinnquote und R.
- **Maróy 2025** (SSRN 5095349, „Improvements to Intraday Momentum Strategies Using Parameter Optimization and Different Exit Strategies“) ist nicht auf arXiv. Volltext und Folgeseiten waren von hier aus nicht erreichbar (SSRN, ResearchGate und Substack per Proxy oder DNS blockiert). Laut Abstract waren die besten Ausstiege „VWAP“, „VWAP & Ladder“ und „Ladder“, alle Parameter optimiert (auf QQQ mit Sekundendaten). Übernommen habe ich nur den „VWAP“-Ausstieg als Nachzieh-Stop = VWAP allein (Variante `vwaptrail`). Diese Definition ist aus dem Namen abgeleitet und nicht am Volltext geprüft. Ladder habe ich nicht übernommen: Die Regel ist nicht ohne optimierte Parameter definiert, und die Definition war nicht zugänglich.
- **Datenhinweis:** In `qdata` gibt es für NAS100 und US500 Kerzen von 15:00 bis 16:00 NY und auch später. Die Annahme „keine Kerzen 15–16 Uhr“ stimmt für diese Daten nicht. Der Zeitausstieg 15:00 ist trotzdem wie verlangt umgesetzt (Standard von `noise.SESS`).
- **Versionen:**
  - v1: mit Vorlauf vor dev_start.
  - v2: `qdata` ohne Vorlauf vor dev_start.
  - v3: korrigierte ts4-Kerzen (Uhr zeitweise 1 h daneben: US500 2020-03-08..2020-11-01 und 2021-03-14..04-09, NAS100 2021-03-14..04-08).
  - Gültig ist v3 (`ergebnis_train.csv`, `ergebnis_val.csv`, Ledger-Notiz „v3“). Die Dateien `ergebnis_*_v1.csv` und `ergebnis_*_v2.csv` sind nur Archiv.
  - v3 gegen v2: NAS100 Train ändert sich um höchstens 0,009 R, US500 Train um höchstens 0,027 R. 2024 ist unverändert.

## Ergebnisse NAS100 (38 Regeln)
Spalten: Train n, Trades/Tag, Trefferquote (Art), R, t, Null-R, t gegen Null, R/Tag | 2024 n, Trefferquote, R, t, Null-R.

| Variante | n | /Tag | Treffer | R | t | Null R | t vs Null | R/Tag | n 24 | Treffer 24 | R 24 | t 24 | Null R 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N10_ref_t10_480 (noise-1.0) | 226 | 0.29 | 57 % (TvS) | +0.113 | 2.04 | -0.040 | 2.76 | +0.033 | 68 | 57 % | +0.138 | 1.41 | +0.042 |
| N10_t05_480 | 226 | 0.29 | 75 % (TvS) | +0.081 | 1.97 | -0.045 | 3.07 | +0.024 | 68 | 76 % | +0.092 | 1.28 | -0.003 |
| N10_t15_480 | 226 | 0.29 | 42 % (TvS) | +0.175 | 2.73 | -0.020 | 3.04 | +0.051 | 68 | 41 % | +0.175 | 1.52 | +0.092 |
| N10_t20_480 | 226 | 0.29 | 24 % (TvS) | +0.136 | 2.08 | -0.004 | 2.13 | +0.040 | 68 | 17 % | +0.156 | 1.34 | +0.110 |
| N10_t05_15 | 225 | 0.29 | 75 % (TvS) | +0.065 | 1.67 | -0.034 | 2.55 | +0.019 | 68 | 79 % | +0.105 | 1.60 | -0.014 |
| N10_t10_15 | 225 | 0.29 | 53 % (TvS) | +0.105 | 2.04 | -0.032 | 2.67 | +0.030 | 68 | 58 % | +0.150 | 1.61 | -0.001 |
| **N10_t15_15 (A)** | 225 | 0.29 | 35 % (TvS) | +0.139 | 2.39 | -0.028 | 2.87 | +0.040 | 68 | 35 % | +0.164 | 1.54 | +0.026 |
| N10_t20_15 | 225 | 0.29 | 16 % (TvS) | +0.106 | 1.80 | -0.023 | 2.19 | +0.031 | 68 | 15 % | +0.187 | 1.67 | +0.035 |
| N10_paper | 225 | 0.29 | 36 % (Gew) | +0.078 | 2.40 | -0.008 | 2.63 | +0.023 | 68 | 35 % | +0.106 | 1.53 | +0.002 |
| N10_vwaptrail | 225 | 0.29 | 44 % (Gew) | +0.079 | 1.88 | -0.008 | 2.07 | +0.023 | 68 | 47 % | +0.198 | 2.31 | +0.015 |
| N10_tp10_be | 225 | 0.29 | 53 % (TP1) | +0.109 | 2.05 | -0.027 | 2.55 | +0.032 | 68 | 58 % | +0.179 | 1.81 | +0.013 |
| N10_tp05_be | 225 | 0.29 | 75 % (TP1) | +0.099 | 2.27 | -0.026 | 2.87 | +0.029 | 68 | 79 % | +0.176 | 2.24 | +0.005 |
| N10_tp10_vwap | 225 | 0.29 | 23 % (TP1) | +0.073 | 1.93 | -0.011 | 2.22 | +0.021 | 68 | 33 % | +0.184 | 2.48 | +0.012 |
| N10_tp05_vwap | 225 | 0.29 | 48 % (TP1) | +0.062 | 1.88 | -0.014 | 2.31 | +0.018 | 68 | 53 % | +0.147 | 2.36 | +0.006 |
| N10_tp10_paper | 225 | 0.29 | 16 % (TP1) | +0.079 | 2.67 | -0.008 | 2.92 | +0.023 | 68 | 21 % | +0.104 | 1.72 | -0.003 |
| N10_tp05_paper | 225 | 0.29 | 32 % (TP1) | +0.065 | 2.60 | -0.010 | 3.01 | +0.019 | 68 | 32 % | +0.076 | 1.51 | -0.001 |
| N10_stopvwap_t10 | 222 | 0.29 | 55 % (TvS) | +0.058 | 0.93 | -0.112 | 2.74 | +0.017 | 68 | 58 % | +0.033 | 0.24 | -0.157 |
| N10_stopband_t10 | 225 | 0.29 | 55 % (TvS) | +0.095 | 2.63 | -0.002 | 2.68 | +0.028 | 68 | 53 % | +0.121 | 1.77 | +0.024 |
| PAPS_t05_15 | 376 | 0.49 | 75 % (TvS) | +0.047 | 1.70 | -0.012 | 2.14 | +0.023 | 117 | 78 % | +0.093 | 2.02 | -0.011 |
| PAPS_t10_15 | 288 | 0.37 | 51 % (TvS) | +0.076 | 1.80 | -0.008 | 1.99 | +0.028 | 89 | 55 % | +0.130 | 1.74 | -0.032 |
| PAPS_t15_15 | 256 | 0.33 | 35 % (TvS) | +0.108 | 2.07 | -0.028 | 2.61 | +0.036 | 76 | 35 % | +0.167 | 1.74 | -0.004 |
| PAPS_t20_15 | 242 | 0.31 | 17 % (TvS) | +0.102 | 1.82 | -0.025 | 2.27 | +0.032 | 73 | 15 % | +0.192 | 1.85 | +0.005 |
| PAPS_paper | 425 | 0.55 | 35 % (Gew) | +0.059 | 2.78 | -0.008 | 3.17 | +0.032 | 134 | 37 % | +0.072 | 1.75 | -0.021 |
| PAPS_vwaptrail | 336 | 0.43 | 43 % (Gew) | +0.072 | 2.32 | -0.005 | 2.49 | +0.031 | 99 | 48 % | +0.165 | 2.60 | -0.000 |
| PAPS_tp10_be | 235 | 0.30 | 53 % (TP1) | +0.106 | 2.06 | -0.012 | 2.30 | +0.032 | 71 | 57 % | +0.173 | 1.79 | +0.027 |
| **PAPS_tp05_be (B)** | 255 | 0.33 | 77 % (TP1) | +0.110 | 2.76 | -0.026 | 3.41 | +0.036 | 78 | 75 % | +0.125 | 1.68 | +0.001 |
| PAPS_tp10_paper | 425 | 0.55 | 12 % (TP1) | +0.058 | 2.98 | -0.008 | 3.40 | +0.032 | 134 | 15 % | +0.073 | 1.94 | -0.020 |
| PAPS_tp05_paper | 425 | 0.55 | 27 % (TP1) | +0.048 | 2.85 | -0.009 | 3.37 | +0.026 | 134 | 28 % | +0.052 | 1.61 | -0.022 |
| PAP0_t05_15 | 728 | 0.94 | 74 % (TvS) | +0.025 | 1.24 | -0.014 | 1.92 | +0.023 | 238 | 78 % | +0.062 | 1.86 | -0.010 |
| PAP0_t10_15 | 564 | 0.73 | 51 % (TvS) | +0.040 | 1.33 | -0.017 | 1.88 | +0.029 | 183 | 56 % | +0.082 | 1.64 | +0.008 |
| PAP0_t15_15 | 504 | 0.65 | 30 % (TvS) | +0.054 | 1.51 | -0.006 | 1.69 | +0.035 | 164 | 37 % | +0.094 | 1.50 | +0.003 |
| PAP0_t20_15 | 484 | 0.63 | 17 % (TvS) | +0.053 | 1.40 | -0.020 | 1.91 | +0.033 | 156 | 20 % | +0.113 | 1.64 | +0.000 |
| PAP0_paper | 859 | 1.11 | 32 % (Gew) | +0.037 | 2.57 | -0.003 | 2.80 | +0.041 | 288 | 31 % | +0.041 | 1.50 | -0.009 |
| PAP0_vwaptrail | 661 | 0.85 | 41 % (Gew) | +0.044 | 2.01 | +0.003 | 1.88 | +0.037 | 232 | 39 % | +0.078 | 2.07 | -0.009 |
| PAP0_tp10_be | 472 | 0.61 | 51 % (TP1) | +0.051 | 1.44 | -0.003 | 1.53 | +0.031 | 150 | 57 % | +0.109 | 1.72 | -0.008 |
| PAP0_tp05_be | 514 | 0.66 | 75 % (TP1) | +0.050 | 1.79 | -0.011 | 2.19 | +0.033 | 174 | 77 % | +0.060 | 1.28 | -0.001 |
| **PAP0_tp10_paper (C)** | 859 | 1.11 | 11 % (TP1) | +0.039 | 2.90 | -0.004 | 3.16 | +0.043 | 288 | 12 % | +0.036 | 1.48 | -0.010 |
| PAP0_tp05_paper | 859 | 1.11 | 25 % (TP1) | +0.029 | 2.52 | -0.004 | 2.88 | +0.032 | 288 | 26 % | +0.031 | 1.48 | -0.012 |

Abkürzungen: `tXX` = festes Ziel XX/10 R, `_15` = Zeitausstieg 15:00 NY, `_480` = 480 min. `paper` = Nachzug max(UB,VWAP)/min(LB,VWAP). `vwaptrail` = Nachzug VWAP (Maróy). `tpXX_be` = 50 % bei XX/10 R, danach Break-even, Rest bis 15:00. `tpXX_vwap`/`tpXX_paper` = 50 % bei XX/10 R, Nachzug ab Einstieg. `stopvwap`/`stopband` = Stop VWAP bzw. Gegenband bei Ziel 1R.
Trade-off-Punkte: `tradeoff.csv`. Alle Zellen (auch Null-Trefferquoten): `ergebnis_train.csv`, `ergebnis_val.csv`.

## Ergebnisse US500 (gleiche Regeln, keine Abstimmung)
| Variante | n | /Tag | Treffer | R | t | Null R | t vs Null | R/Tag | n 24 | Treffer 24 | R 24 | t 24 | Null R 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N10_ref_t10_480 | 304 | 0.29 | 53 % (TvS) | +0.025 | 0.50 | -0.028 | 1.08 | +0.007 | 80 | 48 % | +0.002 | 0.02 | -0.033 |
| N10_t05_480 | 304 | 0.29 | 72 % (TvS) | +0.004 | 0.10 | -0.040 | 1.18 | +0.001 | 80 | 64 % | -0.093 | -1.20 | -0.045 |
| N10_t15_480 | 304 | 0.29 | 40 % (TvS) | +0.082 | 1.45 | -0.023 | 1.85 | +0.024 | 80 | 26 % | -0.101 | -0.96 | -0.009 |
| N10_t20_480 | 304 | 0.29 | 28 % (TvS) | +0.102 | 1.66 | -0.019 | 1.98 | +0.030 | 80 | 15 % | -0.103 | -0.92 | +0.011 |
| N10_t05_15 | 304 | 0.29 | 69 % (TvS) | -0.009 | -0.27 | -0.041 | 0.91 | -0.003 | 80 | 62 % | -0.085 | -1.13 | -0.024 |
| N10_t10_15 | 304 | 0.29 | 48 % (TvS) | +0.028 | 0.64 | -0.028 | 1.27 | +0.008 | 80 | 47 % | +0.013 | 0.14 | -0.015 |
| N10_t15_15 | 304 | 0.29 | 32 % (TvS) | +0.051 | 1.03 | -0.019 | 1.42 | +0.015 | 80 | 24 % | -0.083 | -0.82 | +0.001 |
| N10_t20_15 | 304 | 0.29 | 21 % (TvS) | +0.065 | 1.23 | -0.015 | 1.50 | +0.019 | 80 | 15 % | -0.072 | -0.66 | +0.016 |
| N10_paper | 304 | 0.29 | 32 % (Gew) | +0.040 | 1.32 | -0.016 | 1.84 | +0.012 | 80 | 26 % | +0.091 | 1.24 | -0.013 |
| N10_vwaptrail | 304 | 0.29 | 39 % (Gew) | +0.051 | 1.35 | -0.015 | 1.75 | +0.015 | 80 | 36 % | +0.052 | 0.63 | -0.008 |
| N10_tp10_be | 304 | 0.29 | 48 % (TP1) | +0.041 | 0.88 | -0.024 | 1.39 | +0.012 | 80 | 47 % | +0.032 | 0.31 | -0.007 |
| N10_tp05_be | 304 | 0.29 | 69 % (TP1) | +0.023 | 0.60 | -0.030 | 1.38 | +0.007 | 80 | 62 % | -0.070 | -0.85 | -0.011 |
| N10_tp10_vwap | 304 | 0.29 | 22 % (TP1) | +0.041 | 1.26 | -0.017 | 1.78 | +0.012 | 80 | 32 % | +0.070 | 0.99 | -0.009 |
| N10_tp05_vwap | 304 | 0.29 | 45 % (TP1) | +0.032 | 1.12 | -0.022 | 1.88 | +0.010 | 80 | 50 % | +0.039 | 0.65 | -0.009 |
| N10_tp10_paper | 304 | 0.29 | 13 % (TP1) | +0.033 | 1.26 | -0.020 | 2.01 | +0.010 | 80 | 25 % | +0.103 | 1.74 | -0.019 |
| N10_tp05_paper | 304 | 0.29 | 28 % (TP1) | +0.022 | 0.96 | -0.021 | 1.89 | +0.007 | 80 | 36 % | +0.067 | 1.34 | -0.020 |
| N10_stopvwap_t10 | 302 | 0.29 | 56 % (TvS) | +0.050 | 0.95 | -0.126 | 3.36 | +0.015 | 80 | 57 % | +0.065 | 0.64 | -0.081 |
| N10_stopband_t10 | 304 | 0.29 | 44 % (TvS) | +0.038 | 1.18 | -0.010 | 1.48 | +0.011 | 80 | 45 % | -0.020 | -0.29 | +0.014 |
| PAPS_t05_15 | 493 | 0.48 | 71 % (TvS) | +0.002 | 0.07 | -0.023 | 1.00 | +0.001 | 133 | 62 % | -0.063 | -1.17 | -0.054 |
| PAPS_t10_15 | 385 | 0.37 | 48 % (TvS) | +0.027 | 0.74 | -0.022 | 1.34 | +0.010 | 107 | 44 % | -0.013 | -0.17 | -0.007 |
| PAPS_t15_15 | 351 | 0.34 | 32 % (TvS) | +0.043 | 0.98 | -0.011 | 1.23 | +0.015 | 91 | 24 % | -0.034 | -0.36 | -0.018 |
| PAPS_t20_15 | 334 | 0.32 | 22 % (TvS) | +0.060 | 1.22 | -0.014 | 1.50 | +0.019 | 88 | 15 % | -0.046 | -0.45 | -0.020 |
| PAPS_paper | 582 | 0.56 | 32 % (Gew) | +0.025 | 1.38 | -0.009 | 1.87 | +0.014 | 144 | 26 % | +0.070 | 1.35 | -0.024 |
| PAPS_vwaptrail | 447 | 0.43 | 41 % (Gew) | +0.050 | 1.81 | -0.010 | 2.17 | +0.022 | 108 | 38 % | +0.101 | 1.38 | -0.019 |
| PAPS_tp10_be | 322 | 0.31 | 48 % (TP1) | +0.037 | 0.83 | -0.023 | 1.35 | +0.011 | 87 | 46 % | +0.019 | 0.19 | -0.019 |
| PAPS_tp05_be | 345 | 0.33 | 71 % (TP1) | +0.024 | 0.68 | -0.016 | 1.12 | +0.008 | 96 | 62 % | -0.054 | -0.72 | -0.010 |
| PAPS_tp10_paper | 582 | 0.56 | 10 % (TP1) | +0.024 | 1.46 | -0.011 | 2.13 | +0.013 | 144 | 17 % | +0.065 | 1.58 | -0.024 |
| PAPS_tp05_paper | 582 | 0.56 | 23 % (TP1) | +0.013 | 0.94 | -0.013 | 1.84 | +0.008 | 144 | 27 % | +0.041 | 1.15 | -0.024 |
| PAP0_t05_15 | 954 | 0.92 | 69 % (TvS) | -0.017 | -0.92 | -0.022 | 0.28 | -0.016 | 260 | 70 % | -0.022 | -0.62 | -0.032 |
| PAP0_t10_15 | 747 | 0.72 | 45 % (TvS) | -0.004 | -0.15 | -0.014 | 0.37 | -0.003 | 206 | 52 % | +0.042 | 0.79 | -0.005 |
| PAP0_t15_15 | 685 | 0.66 | 31 % (TvS) | +0.007 | 0.22 | -0.014 | 0.65 | +0.005 | 181 | 36 % | +0.054 | 0.84 | -0.018 |
| PAP0_t20_15 | 651 | 0.63 | 20 % (TvS) | +0.020 | 0.57 | +0.002 | 0.51 | +0.012 | 174 | 26 % | +0.053 | 0.73 | -0.012 |
| PAP0_paper | 1139 | 1.10 | 30 % (Gew) | +0.029 | 2.11 | -0.009 | 2.76 | +0.031 | 298 | 28 % | +0.044 | 1.37 | -0.020 |
| PAP0_vwaptrail | 893 | 0.86 | 38 % (Gew) | +0.045 | 2.20 | -0.005 | 2.47 | +0.039 | 234 | 38 % | +0.085 | 1.96 | -0.002 |
| PAP0_tp10_be | 628 | 0.61 | 45 % (TP1) | -0.005 | -0.15 | -0.011 | 0.18 | -0.003 | 168 | 54 % | +0.067 | 1.04 | +0.030 |
| PAP0_tp05_be | 677 | 0.65 | 67 % (TP1) | -0.013 | -0.51 | -0.020 | 0.25 | -0.009 | 185 | 70 % | +0.001 | 0.02 | -0.008 |
| PAP0_tp10_paper | 1139 | 1.10 | 10 % (TP1) | +0.024 | 2.01 | -0.010 | 2.85 | +0.027 | 298 | 14 % | +0.039 | 1.45 | -0.020 |
| PAP0_tp05_paper | 1139 | 1.10 | 23 % (TP1) | +0.015 | 1.40 | -0.012 | 2.58 | +0.016 | 298 | 27 % | +0.025 | 1.10 | -0.021 |

## Kandidaten
Die Auswahl erfolgte nur auf NAS100 Train und wurde vor dem Blick auf 2024 in `auswahl_train.json` festgehalten. Filter: R > 0, t ≥ 2, t gegen Null ≥ 2, sichtbares Ziel, Ausstieg 15:00. Auf den v3-Daten ergibt dieselbe Regel dieselbe Auswahl.

| Kandidat | Train n / Tag / Treffer / Gew / R / t | Null Train Treffer / Gew / R | 2024 n / Tag / Treffer / Gew / R / t | Null 2024 Treffer / Gew / R | info 2025 R |
|---|---|---|---|---|---|
| A `kandidat_A_n10_ziel15.py` NAS100 | 225 / 0,29 / TvS 35,2 % / 56,0 % / +0,139 / 2,39 | 31,9 % / 45,8 % / −0,028 | 68 / 0,26 / 34,6 % / 61,8 % / +0,164 / 1,54 | 33,5 % / 50,7 % / +0,026 | +0,091 (n 62) |
| B `kandidat_B_paps_tp05be.py` NAS100 | 255 / 0,33 / TP1vS 77,0 % / 66,7 % / +0,110 / 2,76 | – / 56,3 % / −0,026 | 78 / 0,30 / 75,0 % / 66,7 % / +0,125 / 1,68 | – / 57,3 % / +0,001 | +0,054 (n 74, TP1vS 77 %) |
| C `kandidat_C_pap0_tp10paper.py` NAS100 | 859 / 1,11 / TP1vS 10,8 % / 32,7 % / +0,039 / 2,90 | – / 45,2 % / −0,004 | 288 / 1,10 / 11,8 % / 30,6 % / +0,036 / 1,48 | – / 43,0 % / −0,010 | −0,005 (n 292) |
| C US500 | 1139 / 1,10 / TP1vS 9,7 % / 30,2 % / +0,024 / 2,01 | – / 43,1 % / −0,010 | 298 / 1,14 / 14,3 % / 29,2 % / +0,039 / 1,45 | – / 40,1 % / −0,020 | +0,003 (n 273) |

- **A (höchstes R je Trade):** Einstieg wie noise-1.0. Stop Bandmitte, Ziel 1,5R, Zeitausstieg 15:00 NY. Quelle: Einstieg Zarattini/Aziz/Barbon 2024, Ziel als runde R-Stufe. `INSTRUMENTS = ['NAS100']`.
- **B (beste Trefferquote ≥ 60 %):** Paper-Einstieg mit SMA20 (alle Halbstunden-Signale, Wiedereinstieg), Stop Bandmitte. Target = 0,5R für 50 % der Position, danach Stop auf Einstieg, Rest bis 15:00 NY. `INSTRUMENTS = ['NAS100']`.
- **C (höchstes R je Handelstag):** Paper-Einstieg ohne Filter, Stop Bandmitte, danach Paper-Nachzug max(UB,VWAP)/min(LB,VWAP) zu den Halbstunden-Marken. Target = 1R für 50 %, Rest mit Nachzug bis 15:00 NY. Das Teilziel wird nur in ~11 % der Fälle vor dem Stop erreicht, es ist faktisch ein Nachzieh-Ausstieg.
  - `INSTRUMENTS = ['NAS100', 'US500']`: Auf US500 ist die vorab festgelegte Regel (Train R > 0 mit t ≥ 2 und 2024 R > 0) seit v3 knapp erfüllt (t 2,01). In v2 war sie es nicht (t 1,30).
  - In 2025 (nur Info) liegt C bei etwa 0 R (NAS100 −0,005, US500 +0,003).
- Prüfungen (`pruefung.py`): Die Kandidatenmodule liefern über `qbt.simulate` dieselben Trades wie der Forschungslauf. Der Abschneide-Test (12 Zeitpunkte je Kandidat und Instrument) ergab überall gleiche Signale, für C auch gleiche Nachzieh-Spalte. `i_last` (15:00 des Signaltags) ist auf abgeschnittenen Daten am laufenden Tag noch nicht bestimmbar. Das gilt genauso für noise-1.0, verglichen habe ich es deshalb nur für abgeschlossene Tage.

## Varianten
38 Regeln (18 mit N10-Einstieg, je 10 mit PAPS und PAP0), jede auf NAS100 und US500 gerechnet. Im Ledger sind das 76 Varianten (`ergebnisse/varianten/ausstiege.csv`, Zeilen v1, v2 und v3; gültig ist v3).

## Probleme und Zweifel
- Das Ziel von 0,5 R je Trade ist mit Ausstiegen allein nicht erreichbar. Der Vorteil des Einstiegs liegt bei etwa 0,1 R je Trade in Bandmitten-Einheiten. Die Ausstiege verteilen ihn nur zwischen Trefferquote und Gewinngröße um. Gepaart gegen noise-1.0 ist kein Unterschied signifikant.
- Die t-Werte in 2024 liegen bei allen Kandidaten unter 2 (n 68–298). Nur das Vorzeichen ist bestätigt. Die Aufnahme von US500 in C hängt an t 2,01 auf Train und kippte erst mit der Datenkorrektur.
- Bei Nachzieh-Varianten nutzt das Nullmodell den Nachzug des Zufallstags. Ein Long an einem Tag unter dem Band wird dann sofort ausgestoppt. Das Null-R liegt deshalb mechanisch nahe 0, und „t gegen Null“ ist dort weniger aussagekräftig als bei festen Zielen.
- Kandidat C im gesperrten Lauf: `locked_run` rechnet das Nullmodell mit der richtungsbezogenen Einzelspalte. An Zufallstagen ohne Signal gibt es dort keinen Nachzug. Das ergibt ein anderes Null-R:
  - NAS100 Train −0,008 statt −0,004.
  - US500 Train −0,002 statt −0,010; t gegen Null damit 2,2 statt 2,85.
- Maróy 2025: Volltext nicht gelesen (siehe oben). Die VWAP-Ausstiegsregel ist aus dem Namen abgeleitet.
