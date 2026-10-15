# Familie „ausstiege“ – Bericht (15.10.2026)

Auftrag: bessere Ausstiege für Noise-Area-Momentum (Einstieg unverändert aus `lib/noise.py`), Ziel ≥ 0,5 R je Trade und/oder Target vor Stop > 60 %.
Hauptmarkt NAS100 (Train 2021–23, Val 2024), US500 als Robustheitsprüfung mit derselben Regel ohne eigene Abstimmung (Train 2020–23, Val 2024).
Alle Zahlen sind netto (Kosten aus `qdata.COST`) und mit `qbt.simulate` gerechnet. Nullmodell aus `qbt.null_model` (K = 20).

## Kurzfazit
- **Kein Ausstieg erreicht 0,5 R je Trade.** Auf NAS100 Train liegt das beste R je Trade mit sichtbarem Ziel und Ausstieg 15:00 bei +0,13 R (Ziel 1,5R). Mit 480 min sind es +0,17 R, aber dann läuft die Position über das Sitzungsende hinaus.
- **Target vor Stop über 60 % ist mit kleinem Ziel leicht erreichbar** (0,5R: 75–77 %). Mit Ziel 0,5R auf die ganze Position sinkt R aber (N10 +0,06 R). Ein Teilziel (50 % bei 0,5R, danach Break-even) behält die Erwartung: PAPS Train 77 % / +0,105 R (t 2,6), 2024 75 % / +0,125 R.
- Der Ausstieg verschiebt nur den Punkt auf der Trade-off-Kurve. Auf denselben Trades verbessert kein Ausstieg R gegenüber noise-1.0 signifikant. Gepaart gegen noise-1.0: Ziel 1,5R +0,018 R (t 0,6) auf Train und +0,026 R (t 0,5) in 2024. Paper-Nachzug −0,043 R (t −0,9) auf Train.
- Der Paper-Ausstieg (Nachzug max(UB,VWAP), kein Ziel) senkt R je Trade auf NAS100. Mit Wiedereinstieg erhöht er die Anzahl der Trades auf rund 1,1 je Tag und macht die Ergebnisse statistisch stabiler (t ≈ 2,6–3,0). Das Ergebnis je Trade bleibt aber klein (+0,04 R).
- US500 trägt keine der Regeln: Auf Train hat keine Variante t ≥ 2. In 2024 sind die Kandidaten A und B auf US500 negativ.

## Umsetzung (wichtig zum Lesen der Zahlen)
- **Einstiege:** N10 = noise-1.0-Einstieg (`signals(x, grid=30, trend='cprev', one_per_day=True)`). PAPS / PAP0 = Paper-Einstieg: alle Halbstunden-Signale 10:00–14:30 NY, nach einem Ausstieg ist ein neuer Einstieg erlaubt (eine Position zur Zeit), PAPS mit und PAP0 ohne SMA20-Filter.
- **Nachzieh-Spalten** (`common.add_trails`): Der Wert wird nur am Schluss der Halbstunden-Kerzen gesetzt und gilt bis zur nächsten Marke. Er nutzt nur Daten bis zu dieser Kerze. qbt nutzt an Kerze i den Wert von i−1 und zieht den Stop nur nach.
- **R-Einheit bei Nachzieh-Ausstiegen:** Der Anfangsstop ist die Bandmitte. Er gilt nur in der Einstiegskerze, ab der nächsten Kerze greift der Nachzug. So ist R in allen Varianten in derselben Einheit gemessen (Abstand zur Bandmitte). Abweichungen vom Paper: Das Paper prüft nur zum Halbstunden-Schluss und schließt dann. Hier ruht der Stop zwischen den Marken als Stop-Order. Außerdem zieht qbt nur nach, ein fallender VWAP lockert den Stop nicht.
- **Long max(UB,VWAP) und Short min(LB,VWAP)** brauchen zwei Spalten, qbt erlaubt aber nur eine je Lauf. Deshalb rechnet `common.run` Long und Short getrennt mit `seq=False` und stellt danach exakt die Sequenzlogik von qbt nach. Geprüft: Mit einer gemeinsamen Spalte sind die Ergebnisse identisch zu `qbt.simulate(seq=True)`. Das Nullmodell wird je Spalte gerechnet und gewichtet kombiniert. Kandidat C nutzt stattdessen eine richtungsbezogene Einzelspalte (siehe Modul). Er liefert dieselben 1145 Trades.
- **Trefferquote:** Bei festem Ziel Target vor Stop (TvS). Bei Teilziel „Teilziel vor Stop“ (TP1vS): Dafür werden dieselben Trades ein zweites Mal mit Ziel = TP1 gerechnet, sonst mit gleichem Stop und Nachzug. Ohne Ziel gilt die Gewinnquote. Für das Nullmodell gibt es keine TP1vS, nur Gewinnquote und R.
- **Maróy 2025** (SSRN 5095349, „Improvements to Intraday Momentum Strategies Using Parameter Optimization and Different Exit Strategies“) ist nicht auf arXiv. Volltext und Folgeseiten waren von hier aus nicht erreichbar (SSRN, ResearchGate und Substack per Proxy oder DNS blockiert). Laut Abstract waren die besten Ausstiege „VWAP“, „VWAP & Ladder“ und „Ladder“, alle Parameter optimiert (auf QQQ mit Sekundendaten). Übernommen habe ich nur den „VWAP“-Ausstieg als Nachzieh-Stop = VWAP allein (Variante `vwaptrail`). Diese Definition ist aus dem Namen abgeleitet und nicht am Volltext geprüft. Ladder habe ich nicht übernommen: Die Regel ist nicht ohne optimierte Parameter definiert, und die Definition war nicht zugänglich.
- Datenhinweis: In `qdata` gibt es für NAS100 und US500 Kerzen von 15:00 bis 16:00 NY und auch später. Die Annahme „keine Kerzen 15–16 Uhr“ stimmt für diese Daten nicht. Der Zeitausstieg 15:00 ist trotzdem wie verlangt umgesetzt (Standard von `noise.SESS`).
- `lib/qdata.py` wurde während der Arbeit geändert (19:15: kein Vorlauf mehr vor dev_start). Ich habe alles neu gerechnet (Ledger-Notiz „v2“). Für NAS100 sind die Zahlen identisch, weil vor 2021 im Vorlauf keine Kerzen lagen. Für US500 Train ändern sie sich leicht (n 310 → 306). Die v1-Dateien `ergebnis_*_v1.csv` sind nur noch Archiv.

## Ergebnisse NAS100 (38 Regeln)
Spalten: Train n, Trades/Tag, Trefferquote (Art), R, t, Null-R, t gegen Null, R/Tag | 2024 n, Trefferquote, R, t, Null-R.

| Variante | n | /Tag | Treffer | R | t | Null R | t vs Null | R/Tag | n 24 | Treffer 24 | R 24 | t 24 | Null R 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N10_ref_t10_480 (noise-1.0) | 226 | 0.29 | 57 % (TvS) | +0.110 | 1.99 | -0.038 | 2.67 | +0.032 | 68 | 57 % | +0.138 | 1.41 | +0.042 |
| N10_t05_480 | 226 | 0.29 | 75 % (TvS) | +0.077 | 1.89 | -0.048 | 3.06 | +0.023 | 68 | 76 % | +0.092 | 1.28 | -0.003 |
| N10_t15_480 | 226 | 0.29 | 41 % (TvS) | +0.168 | 2.63 | -0.017 | 2.90 | +0.049 | 68 | 41 % | +0.175 | 1.52 | +0.092 |
| N10_t20_480 | 226 | 0.29 | 24 % (TvS) | +0.130 | 1.99 | +0.002 | 1.97 | +0.038 | 68 | 17 % | +0.156 | 1.34 | +0.110 |
| N10_t05_15 | 225 | 0.29 | 75 % (TvS) | +0.061 | 1.58 | -0.036 | 2.52 | +0.018 | 68 | 79 % | +0.105 | 1.60 | -0.014 |
| N10_t10_15 | 225 | 0.29 | 53 % (TvS) | +0.098 | 1.93 | -0.030 | 2.52 | +0.029 | 68 | 58 % | +0.150 | 1.61 | -0.001 |
| **N10_t15_15 (A)** | 225 | 0.29 | 34 % (TvS) | +0.130 | 2.26 | -0.025 | 2.69 | +0.038 | 68 | 35 % | +0.164 | 1.54 | +0.026 |
| N10_t20_15 | 225 | 0.29 | 16 % (TvS) | +0.098 | 1.68 | -0.019 | 1.99 | +0.029 | 68 | 15 % | +0.187 | 1.67 | +0.035 |
| N10_paper | 225 | 0.29 | 36 % (Gew) | +0.069 | 2.17 | -0.007 | 2.39 | +0.020 | 68 | 35 % | +0.106 | 1.53 | +0.002 |
| N10_vwaptrail | 225 | 0.29 | 44 % (Gew) | +0.072 | 1.74 | -0.008 | 1.94 | +0.021 | 68 | 47 % | +0.198 | 2.31 | +0.015 |
| N10_tp10_be | 225 | 0.29 | 53 % (TP1) | +0.102 | 1.93 | -0.025 | 2.39 | +0.030 | 68 | 58 % | +0.179 | 1.81 | +0.013 |
| N10_tp05_be | 225 | 0.29 | 75 % (TP1) | +0.093 | 2.14 | -0.028 | 2.78 | +0.027 | 68 | 79 % | +0.176 | 2.24 | +0.005 |
| N10_tp10_vwap | 225 | 0.29 | 22 % (TP1) | +0.067 | 1.79 | -0.012 | 2.10 | +0.020 | 68 | 33 % | +0.184 | 2.48 | +0.012 |
| N10_tp05_vwap | 225 | 0.29 | 47 % (TP1) | +0.057 | 1.75 | -0.015 | 2.21 | +0.017 | 68 | 53 % | +0.147 | 2.36 | +0.006 |
| N10_tp10_paper | 225 | 0.29 | 16 % (TP1) | +0.072 | 2.44 | -0.007 | 2.68 | +0.021 | 68 | 21 % | +0.104 | 1.72 | -0.003 |
| N10_tp05_paper | 225 | 0.29 | 32 % (TP1) | +0.060 | 2.41 | -0.008 | 2.72 | +0.017 | 68 | 32 % | +0.076 | 1.51 | -0.001 |
| N10_stopvwap_t10 | 222 | 0.29 | 55 % (TvS) | +0.059 | 0.95 | -0.107 | 2.67 | +0.017 | 68 | 58 % | +0.033 | 0.24 | -0.157 |
| N10_stopband_t10 | 225 | 0.29 | 53 % (TvS) | +0.087 | 2.40 | -0.002 | 2.46 | +0.025 | 68 | 53 % | +0.121 | 1.77 | +0.024 |
| PAPS_t05_15 | 372 | 0.48 | 75 % (TvS) | +0.046 | 1.67 | -0.023 | 2.48 | +0.022 | 117 | 78 % | +0.093 | 2.02 | -0.011 |
| PAPS_t10_15 | 287 | 0.37 | 51 % (TvS) | +0.070 | 1.68 | -0.020 | 2.15 | +0.026 | 89 | 55 % | +0.130 | 1.74 | -0.032 |
| PAPS_t15_15 | 256 | 0.33 | 34 % (TvS) | +0.101 | 1.94 | -0.031 | 2.53 | +0.033 | 76 | 35 % | +0.167 | 1.74 | -0.004 |
| PAPS_t20_15 | 242 | 0.31 | 17 % (TvS) | +0.095 | 1.70 | -0.028 | 2.20 | +0.030 | 73 | 15 % | +0.192 | 1.85 | +0.005 |
| PAPS_paper | 431 | 0.56 | 35 % (Gew) | +0.054 | 2.62 | -0.009 | 3.05 | +0.030 | 134 | 37 % | +0.072 | 1.75 | -0.021 |
| PAPS_vwaptrail | 340 | 0.44 | 43 % (Gew) | +0.068 | 2.22 | -0.006 | 2.40 | +0.030 | 99 | 48 % | +0.165 | 2.60 | -0.000 |
| PAPS_tp10_be | 235 | 0.30 | 53 % (TP1) | +0.099 | 1.94 | -0.015 | 2.23 | +0.030 | 71 | 57 % | +0.173 | 1.79 | +0.027 |
| **PAPS_tp05_be (B)** | 255 | 0.33 | 77 % (TP1) | +0.105 | 2.64 | -0.026 | 3.28 | +0.035 | 78 | 75 % | +0.125 | 1.68 | +0.001 |
| PAPS_tp10_paper | 431 | 0.56 | 11 % (TP1) | +0.054 | 2.83 | -0.008 | 3.26 | +0.030 | 134 | 15 % | +0.073 | 1.94 | -0.020 |
| PAPS_tp05_paper | 431 | 0.56 | 27 % (TP1) | +0.045 | 2.72 | -0.009 | 3.28 | +0.025 | 134 | 28 % | +0.052 | 1.61 | -0.022 |
| PAP0_t05_15 | 720 | 0.93 | 75 % (TvS) | +0.025 | 1.28 | -0.019 | 2.24 | +0.024 | 238 | 78 % | +0.062 | 1.86 | -0.010 |
| PAP0_t10_15 | 559 | 0.72 | 52 % (TvS) | +0.040 | 1.33 | -0.008 | 1.61 | +0.029 | 183 | 56 % | +0.082 | 1.64 | +0.008 |
| PAP0_t15_15 | 500 | 0.65 | 30 % (TvS) | +0.052 | 1.46 | -0.013 | 1.84 | +0.034 | 164 | 37 % | +0.094 | 1.50 | +0.003 |
| PAP0_t20_15 | 480 | 0.62 | 17 % (TvS) | +0.052 | 1.36 | -0.013 | 1.69 | +0.032 | 156 | 20 % | +0.113 | 1.64 | +0.000 |
| PAP0_paper | 857 | 1.11 | 33 % (Gew) | +0.037 | 2.59 | -0.005 | 2.92 | +0.041 | 288 | 31 % | +0.041 | 1.50 | -0.009 |
| PAP0_vwaptrail | 661 | 0.85 | 41 % (Gew) | +0.042 | 1.93 | +0.003 | 1.79 | +0.036 | 232 | 39 % | +0.078 | 2.07 | -0.009 |
| PAP0_tp10_be | 468 | 0.60 | 52 % (TP1) | +0.051 | 1.43 | -0.003 | 1.52 | +0.031 | 150 | 57 % | +0.109 | 1.72 | -0.008 |
| PAP0_tp05_be | 509 | 0.66 | 75 % (TP1) | +0.050 | 1.78 | -0.016 | 2.37 | +0.033 | 174 | 77 % | +0.060 | 1.28 | -0.001 |
| **PAP0_tp10_paper (C)** | 857 | 1.11 | 11 % (TP1) | +0.039 | 2.96 | -0.004 | 3.29 | +0.044 | 288 | 12 % | +0.036 | 1.48 | -0.010 |
| PAP0_tp05_paper | 857 | 1.11 | 25 % (TP1) | +0.029 | 2.56 | -0.006 | 3.07 | +0.033 | 288 | 26 % | +0.031 | 1.48 | -0.012 |

Abkürzungen: `tXX` = festes Ziel XX/10 R, `_15` = Zeitausstieg 15:00 NY, `_480` = 480 min. `paper` = Nachzug max(UB,VWAP)/min(LB,VWAP). `vwaptrail` = Nachzug VWAP (Maróy). `tpXX_be` = 50 % bei XX/10 R, danach Break-even, Rest bis 15:00. `tpXX_vwap`/`tpXX_paper` = 50 % bei XX/10 R, Nachzug ab Einstieg. `stopvwap`/`stopband` = Stop VWAP bzw. Gegenband bei Ziel 1R.
Trade-off-Punkte: `tradeoff.csv`. Alle Zellen (auch US500, Null-Trefferquoten): `ergebnis_train.csv`, `ergebnis_val.csv`.

## Kandidaten
Die Auswahl erfolgte nur auf NAS100 Train und wurde vor dem Blick auf 2024 in `auswahl_train.json` festgehalten. Filter: R > 0, t ≥ 2, t gegen Null ≥ 2, sichtbares Ziel, Ausstieg 15:00.

| Kandidat | Train n / Tag / Treffer / Gew / R / t | Null Train Treffer / Gew / R | 2024 n / Tag / Treffer / Gew / R / t | Null 2024 Treffer / Gew / R | info 2025 R |
|---|---|---|---|---|---|
| A `kandidat_A_n10_ziel15.py` | 225 / 0,29 / TvS 34,5 % / 56,0 % / +0,130 / 2,26 | 32,1 % / 46,0 % / −0,025 | 68 / 0,26 / 34,6 % / 61,8 % / +0,164 / 1,54 | 33,5 % / 50,7 % / +0,026 | +0,091 (n 62) |
| B `kandidat_B_paps_tp05be.py` | 255 / 0,33 / TP1vS 76,8 % / 66,7 % / +0,105 / 2,64 | – / 56,4 % / −0,026 | 78 / 0,30 / 75,0 % / 66,7 % / +0,125 / 1,68 | – / 57,3 % / +0,001 | +0,054 (n 74, TP1vS 77 %) |
| C `kandidat_C_pap0_tp10paper.py` | 857 / 1,11 / TP1vS 11,0 % / 33,0 % / +0,039 / 2,96 | – / 45,2 % / −0,004 | 288 / 1,10 / 11,8 % / 30,6 % / +0,036 / 1,48 | – / 43,0 % / −0,010 | −0,005 (n 292) |

- **A (höchstes R je Trade):** Einstieg wie noise-1.0. Stop Bandmitte, Ziel 1,5R, Zeitausstieg 15:00 NY. Quelle: Einstieg Zarattini/Aziz/Barbon 2024, Ziel als runde R-Stufe.
- **B (beste Trefferquote ≥ 60 %):** Paper-Einstieg mit SMA20 (alle Halbstunden-Signale, Wiedereinstieg), Stop Bandmitte. Target = 0,5R für 50 % der Position, danach Stop auf Einstieg, Rest bis 15:00 NY.
- **C (höchstes R je Handelstag):** Paper-Einstieg ohne Filter, Stop Bandmitte, danach Paper-Nachzug max(UB,VWAP)/min(LB,VWAP) zu den Halbstunden-Marken. Target = 1R für 50 %, Rest mit Nachzug bis 15:00 NY. Das Teilziel wird nur in 11 % der Fälle vor dem Stop erreicht, es ist faktisch ein Nachzieh-Ausstieg. In 2025 (nur Info) ist C leicht negativ.
- Alle drei: `INSTRUMENTS = ['NAS100']`. Auf US500 ist mit derselben Regel keine auf Train signifikant, A und B sind in 2024 negativ.
- Prüfungen (`pruefung.py`): Die Kandidatenmodule liefern über `qbt.simulate` dieselben Trades wie der Forschungslauf. Der Abschneide-Test (12 Zeitpunkte je Kandidat) ergab überall gleiche Signale, für C auch gleiche Nachzieh-Spalte. `i_last` (15:00 des Signaltags) ist auf abgeschnittenen Daten am laufenden Tag noch nicht bestimmbar. Das gilt genauso für noise-1.0, verglichen habe ich es deshalb nur für abgeschlossene Tage.

## Varianten
38 Regeln (18 mit N10-Einstieg, je 10 mit PAPS und PAP0), jede auf NAS100 und US500 gerechnet. Im Ledger sind das 76 Varianten (`ergebnisse/varianten/ausstiege.csv`, v1- und v2-Zeilen).

## Probleme und Zweifel
- Das Ziel von 0,5 R je Trade ist mit Ausstiegen allein nicht erreichbar. Der Vorteil des Einstiegs liegt bei etwa 0,1 R je Trade in Bandmitten-Einheiten. Die Ausstiege verteilen ihn nur zwischen Trefferquote und Gewinngröße um. Gepaart gegen noise-1.0 ist kein Unterschied signifikant.
- Die t-Werte in 2024 liegen bei allen Kandidaten unter 2 (n 68–288). Nur das Vorzeichen ist bestätigt.
- Bei Nachzieh-Varianten nutzt das Nullmodell den Nachzug des Zufallstags. Ein Long an einem Tag unter dem Band wird dann sofort ausgestoppt. Das Null-R liegt deshalb mechanisch nahe 0, und „t gegen Null“ ist dort weniger aussagekräftig als bei festen Zielen.
- Kandidat C im gesperrten Lauf: `locked_run` rechnet das Nullmodell mit der richtungsbezogenen Einzelspalte. An Zufallstagen ohne Signal gibt es dort keinen Nachzug. Das ergibt ein etwas anderes Null-R (Train −0,006 statt −0,004).
- Maróy 2025: Volltext nicht gelesen (siehe oben). Die VWAP-Ausstiegsregel ist aus dem Namen abgeleitet.
