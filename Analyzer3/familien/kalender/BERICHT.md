# Familie kalender – Bericht (Stand 15.10.2026)

**Ergebnis: kein Kandidat.** Keine Kalenderregel erreicht auf Train t ≥ 2, keine liegt klar über dem Nullmodell
(bester Wert t_vs_null 1,3), und die Overnight-Drift (das einzige Setup mit ~1 Signal/Tag) ist im dev-Zeitraum verschwunden.

## Regeln (Literatur, keine eigenen Erfindungen)
Alle Uhrzeiten New York (Server − 7 h). Market-Einstieg zur Fensteröffnung (Signalkerze = Kerze davor), Zeitausstieg am
Schluss der letzten Kerze vor Fensterende. Alle Fenster enden spätestens 15:00 NY (NAS100.c live ohne Kerzen 15–16 Uhr).
Handelstage/Feiertage: `pandas_market_calendars` 'NYSE', nur reguläre (vorab bekannte) Feiertage; an verkürzten Tagen endet
das Fenster mit dem Börsenschluss (13:00).

| Regel | Fenster NY (Wien) | Tage | Quelle |
|---|---|---|---|
| ON | 2:00–3:00 (8–9 Uhr) | jeder NYSE-Handelstag | Boyarchenko/Larsen/Whelan 2023, RFS 36(9) |
| ONneg | 2:00–3:00 | Vortag (15:00→15:00) < 0 | BLW 2023: Umkehr nach Ausverkäufen stärker |
| ONbig | 2:00–3:00 | Vortag ≤ −1 % | dito, nur große Ausverkäufe |
| TOM | 9:30–15:00 (15:30–21 Uhr) | letzter + erste 3 Handelstage des Monats | Ariel 1987; Lakonishok/Smidt 1988; McConnell/Xu 2008 |
| PREH | 9:30–15:00 | letzter Handelstag vor NYSE-Feiertag | Ariel 1990; Lakonishok/Smidt 1988 |
| OPEXW | 9:30–15:00 | Mo bis Verfallstag der Woche des 3. Freitags | Stivers/Sun (2010 WP, 2013 JBF): OE-Woche hoch |
| TOM+PREH | 9:30–15:00 | Vereinigung TOM ∪ PREH | Lakonishok/Smidt 1988 (beide Effekte) |
| TOM+PREH_hw | 9:30–15:00 | wie oben, nur Nov–Apr | Halloween-Filter, Bouman/Jacobsen 2002 |

Geometrie (eine runde Regel für alle): Stop = 1 × σ_F, σ_F = Wurzel des Mittels der quadrierten Fensterrenditen
(Eröffnung→Schluss desselben Fensters) der letzten 20 NYSE-Handelstage, nur Vortage. Ziele 0,5 / 1 / 2 R und „none“ (nur
Zeitausstieg). Long. Kosten qdata.COST (1 bp Roundtrip) – im 1-h-Fenster (σ_F ≈ 0,14–0,16 %) sind das ≈ 0,07 R je Trade
(2024: 0,10–0,14 R), im Tagesfenster ≈ 0,01–0,02 R.

Nicht getestet: XAUUSD (für Gold gibt es keine belegte Intraday-Kalenderregel dieser Art; nur der Monats-„Autumn effect“,
Baur 2013, der sich in der Replikation von Potrykus/Augustynowicz 2024 umgekehrt hat). Wochentagseffekt (Montag) nicht
getestet: seit den 1990ern verschwunden/umgekehrt (Schwert 2003), also nicht belegt.

## Ergebnisse (Train = NAS100 2021–23, US500 2020–23; Val = 2024; Nullmodell = gleiche Uhrzeit/Geometrie, Zufallstag, K = 20)
TvS = Target vor Stop (bei „none“ nicht definiert), Gew. = Gewinnquote, R netto je Trade, t = Trade-t (= Tages-t, ein Trade/Tag).
Variantennamen: Regel · Instrument · Ziel (in `tradeoff.csv` mit „|“ getrennt). Volle Trade-off-Kurve (inkl. Nullmodell-Zeilen, R pro Tag) in `tradeoff.csv`; Rohzellen in `zellen_*_stufe*.csv`.

| Variante | Train n | /Tag | TvS | Gew. | R netto | t | Null TvS | Null Gew. | Null R | Val n | TvS | Gew. | R netto | t | Null TvS | Null Gew. | Null R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ON · NAS100 · 0.5R | 723 | 0.93 | 67 % | 55 % | -0.12 | -5.0 | 67 % | 55 % | -0.11 | 252 | 64 % | 55 % | -0.17 | -4.2 | 68 % | 57 % | -0.13 |
| ON · NAS100 · 1R | 723 | 0.93 | 50 % | 48 % | -0.07 | -2.3 | 48 % | 47 % | -0.08 | 252 | 46 % | 45 % | -0.14 | -2.8 | 47 % | 45 % | -0.14 |
| ON · NAS100 · 2R | 723 | 0.93 | 18 % | 46 % | -0.06 | -1.8 | 21 % | 43 % | -0.07 | 252 | 16 % | 42 % | -0.14 | -2.5 | 16 % | 43 % | -0.14 |
| ON · NAS100 · none | 723 | 0.93 | – | 46 % | -0.06 | -1.8 | – | 43 % | -0.07 | 252 | – | 42 % | -0.13 | -2.1 | – | 42 % | -0.13 |
| ONneg · NAS100 · 0.5R | 337 | 0.44 | 67 % | 59 % | -0.10 | -2.9 | 66 % | 55 % | -0.11 | 115 | 59 % | 54 % | -0.23 | -3.6 | 67 % | 57 % | -0.14 |
| ONneg · NAS100 · 1R | 337 | 0.44 | 51 % | 50 % | -0.05 | -1.1 | 47 % | 47 % | -0.08 | 115 | 42 % | 43 % | -0.22 | -2.7 | 46 % | 44 % | -0.15 |
| ONneg · NAS100 · 2R | 337 | 0.44 | 19 % | 45 % | -0.05 | -1.0 | 22 % | 44 % | -0.05 | 115 | 15 % | 38 % | -0.22 | -2.5 | 17 % | 41 % | -0.14 |
| ONneg · NAS100 · none | 337 | 0.44 | – | 45 % | -0.04 | -0.9 | – | 44 % | -0.05 | 115 | – | 38 % | -0.21 | -2.3 | – | 41 % | -0.14 |
| TOM · NAS100 · 0.5R | 135 | 0.17 | 67 % | 60 % | -0.03 | -0.6 | 72 % | 64 % | +0.02 | 48 | 69 % | 62 % | +0.01 | +0.1 | 66 % | 60 % | -0.05 |
| TOM · NAS100 · 1R | 135 | 0.17 | 48 % | 53 % | +0.00 | +0.1 | 49 % | 54 % | +0.03 | 48 | 59 % | 56 % | +0.15 | +1.2 | 47 % | 53 % | -0.00 |
| TOM · NAS100 · 2R | 135 | 0.17 | 10 % | 51 % | +0.03 | +0.3 | 21 % | 51 % | +0.06 | 48 | 28 % | 54 % | +0.20 | +1.4 | 13 % | 51 % | +0.02 |
| TOM · NAS100 · none | 135 | 0.17 | – | 51 % | +0.02 | +0.2 | – | 50 % | +0.06 | 48 | – | 54 % | +0.21 | +1.4 | – | 51 % | +0.04 |
| PREH · NAS100 · 0.5R | 27 | 0.03 | 71 % | 70 % | +0.06 | +0.5 | 73 % | 62 % | +0.03 | 10 | 50 % | 40 % | -0.21 | -1.0 | 63 % | 56 % | -0.10 |
| PREH · NAS100 · 1R | 27 | 0.03 | 54 % | 67 % | +0.20 | +1.4 | 49 % | 51 % | +0.02 | 10 | 50 % | 40 % | -0.06 | -0.2 | 50 % | 51 % | -0.00 |
| PREH · NAS100 · 2R | 27 | 0.03 | 14 % | 67 % | +0.23 | +1.5 | 20 % | 48 % | +0.06 | 10 | 25 % | 40 % | +0.04 | +0.1 | 14 % | 47 % | -0.01 |
| PREH · NAS100 · none | 27 | 0.03 | – | 67 % | +0.29 | +1.5 | – | 47 % | +0.05 | 10 | – | 40 % | +0.05 | +0.2 | – | 47 % | +0.01 |
| OPEXW · NAS100 · 0.5R | 171 | 0.22 | 69 % | 63 % | -0.01 | -0.3 | 71 % | 63 % | +0.01 | 58 | 56 % | 50 % | -0.18 | -2.0 | 67 % | 60 % | -0.04 |
| OPEXW · NAS100 · 1R | 171 | 0.22 | 50 % | 53 % | +0.03 | +0.4 | 48 % | 54 % | +0.02 | 58 | 33 % | 43 % | -0.18 | -1.7 | 50 % | 53 % | +0.01 |
| OPEXW · NAS100 · 2R | 171 | 0.22 | 12 % | 53 % | +0.06 | +0.9 | 19 % | 50 % | +0.04 | 58 | 12 % | 41 % | -0.17 | -1.5 | 13 % | 51 % | +0.03 |
| OPEXW · NAS100 · none | 171 | 0.22 | – | 53 % | +0.07 | +1.0 | – | 50 % | +0.06 | 58 | – | 41 % | -0.14 | -1.1 | – | 51 % | +0.04 |
| ON · US500 · 0.5R | 971 | 0.94 | 68 % | 57 % | -0.11 | -5.3 | 65 % | 53 % | -0.14 | 252 | 66 % | 53 % | -0.20 | -4.9 | 66 % | 54 % | -0.19 |
| ON · US500 · 1R | 971 | 0.94 | 48 % | 47 % | -0.08 | -3.0 | 47 % | 45 % | -0.10 | 252 | 45 % | 42 % | -0.19 | -3.9 | 44 % | 42 % | -0.21 |
| ON · US500 · 2R | 971 | 0.94 | 16 % | 44 % | -0.08 | -2.9 | 24 % | 41 % | -0.08 | 252 | 19 % | 40 % | -0.17 | -3.0 | 17 % | 40 % | -0.19 |
| ON · US500 · none | 971 | 0.94 | – | 44 % | -0.07 | -2.4 | – | 40 % | -0.10 | 252 | – | 40 % | -0.15 | -2.5 | – | 39 % | -0.18 |
| ONneg · US500 · 0.5R | 435 | 0.42 | 65 % | 58 % | -0.13 | -3.9 | 65 % | 53 % | -0.14 | 112 | 65 % | 57 % | -0.22 | -3.4 | 66 % | 55 % | -0.19 |
| ONneg · US500 · 1R | 435 | 0.42 | 48 % | 47 % | -0.09 | -2.1 | 46 % | 45 % | -0.11 | 112 | 46 % | 44 % | -0.21 | -2.6 | 44 % | 43 % | -0.22 |
| ONneg · US500 · 2R | 435 | 0.42 | 17 % | 43 % | -0.10 | -2.2 | 23 % | 41 % | -0.09 | 112 | 16 % | 40 % | -0.20 | -2.1 | 19 % | 40 % | -0.19 |
| ONneg · US500 · none | 435 | 0.42 | – | 43 % | -0.09 | -1.7 | – | 40 % | -0.10 | 112 | – | 40 % | -0.17 | -1.7 | – | 40 % | -0.17 |
| TOM · US500 · 0.5R | 185 | 0.18 | 72 % | 64 % | +0.03 | +0.6 | 69 % | 62 % | -0.01 | 48 | 63 % | 62 % | -0.04 | -0.4 | 66 % | 59 % | -0.05 |
| TOM · US500 · 1R | 185 | 0.18 | 54 % | 56 % | +0.08 | +1.4 | 47 % | 52 % | -0.00 | 48 | 50 % | 50 % | +0.00 | +0.0 | 46 % | 50 % | -0.02 |
| TOM · US500 · 2R | 185 | 0.18 | 12 % | 54 % | +0.09 | +1.4 | 18 % | 49 % | +0.01 | 48 | 19 % | 48 % | +0.08 | +0.5 | 16 % | 46 % | -0.01 |
| TOM · US500 · none | 185 | 0.18 | – | 54 % | +0.10 | +1.4 | – | 48 % | +0.01 | 48 | – | 48 % | +0.07 | +0.5 | – | 46 % | +0.00 |
| PREH · US500 · 0.5R | 36 | 0.03 | 70 % | 58 % | -0.00 | -0.0 | 70 % | 63 % | +0.00 | 10 | 50 % | 50 % | -0.19 | -0.8 | 67 % | 59 % | -0.05 |
| PREH · US500 · 1R | 36 | 0.03 | 38 % | 56 % | +0.11 | +0.9 | 48 % | 53 % | +0.02 | 10 | 33 % | 50 % | -0.09 | -0.3 | 49 % | 50 % | -0.01 |
| PREH · US500 · 2R | 36 | 0.03 | 11 % | 56 % | +0.15 | +1.1 | 19 % | 50 % | +0.05 | 10 | 0 % | 50 % | +0.01 | +0.0 | 17 % | 47 % | -0.01 |
| PREH · US500 · none | 36 | 0.03 | – | 56 % | +0.16 | +1.1 | – | 49 % | +0.05 | 10 | – | 50 % | +0.01 | +0.0 | – | 47 % | +0.00 |
| OPEXW · US500 · 0.5R | 230 | 0.22 | 68 % | 62 % | -0.02 | -0.6 | 70 % | 62 % | +0.00 | 58 | 69 % | 64 % | +0.00 | +0.0 | 67 % | 61 % | -0.03 |
| OPEXW · US500 · 1R | 230 | 0.22 | 44 % | 50 % | -0.03 | -0.6 | 48 % | 53 % | +0.01 | 58 | 40 % | 48 % | -0.06 | -0.5 | 48 % | 51 % | -0.00 |
| OPEXW · US500 · 2R | 230 | 0.22 | 13 % | 49 % | -0.01 | -0.1 | 18 % | 49 % | +0.01 | 58 | 14 % | 45 % | -0.05 | -0.5 | 16 % | 47 % | -0.00 |
| OPEXW · US500 · none | 230 | 0.22 | – | 49 % | +0.00 | +0.1 | – | 48 % | +0.02 | 58 | – | 45 % | +0.01 | +0.1 | – | 47 % | +0.02 |
| ONbig · NAS100 · 0.5R | 138 | 0.18 | 63 % | 57 % | -0.12 | -2.1 | 68 % | 54 % | -0.10 | 31 | 48 % | 48 % | -0.35 | -2.6 | 67 % | 54 % | -0.16 |
| ONbig · NAS100 · 1R | 138 | 0.18 | 48 % | 48 % | -0.07 | -0.9 | 47 % | 46 % | -0.08 | 31 | 35 % | 39 % | -0.33 | -2.0 | 45 % | 43 % | -0.16 |
| ONbig · NAS100 · 2R | 138 | 0.18 | 22 % | 42 % | -0.05 | -0.6 | 19 % | 43 % | -0.07 | 31 | 19 % | 35 % | -0.22 | -1.1 | 15 % | 41 % | -0.15 |
| ONbig · NAS100 · none | 138 | 0.18 | – | 42 % | -0.04 | -0.4 | – | 43 % | -0.08 | 31 | – | 35 % | -0.12 | -0.5 | – | 40 % | -0.15 |
| TOM+PREH · NAS100 · 0.5R | 152 | 0.20 | 68 % | 62 % | -0.01 | -0.2 | 72 % | 64 % | +0.02 | 54 | 67 % | 61 % | -0.02 | -0.2 | 67 % | 61 % | -0.04 |
| TOM+PREH · NAS100 · 1R | 152 | 0.20 | 49 % | 55 % | +0.04 | +0.6 | 50 % | 54 % | +0.03 | 54 | 58 % | 56 % | +0.13 | +1.1 | 49 % | 54 % | +0.01 |
| TOM+PREH · NAS100 · 2R | 152 | 0.20 | 11 % | 53 % | +0.07 | +0.9 | 20 % | 51 % | +0.06 | 54 | 25 % | 54 % | +0.17 | +1.2 | 15 % | 52 % | +0.03 |
| TOM+PREH · NAS100 · none | 152 | 0.20 | – | 53 % | +0.07 | +0.9 | – | 51 % | +0.07 | 54 | – | 54 % | +0.18 | +1.3 | – | 52 % | +0.05 |
| ONbig · US500 · 0.5R | 141 | 0.14 | 65 % | 62 % | -0.10 | -1.7 | 67 % | 52 % | -0.11 | 18 | 56 % | 56 % | -0.29 | -1.7 | 68 % | 54 % | -0.17 |
| ONbig · US500 · 1R | 141 | 0.14 | 51 % | 49 % | -0.03 | -0.4 | 48 % | 45 % | -0.08 | 18 | 47 % | 50 % | -0.16 | -0.7 | 44 % | 42 % | -0.21 |
| ONbig · US500 · 2R | 141 | 0.14 | 26 % | 43 % | -0.02 | -0.2 | 23 % | 42 % | -0.06 | 18 | 31 % | 39 % | -0.03 | -0.1 | 16 % | 39 % | -0.22 |
| ONbig · US500 · none | 141 | 0.14 | – | 43 % | +0.04 | +0.4 | – | 41 % | -0.08 | 18 | – | 39 % | +0.22 | +0.5 | – | 38 % | -0.18 |
| TOM+PREH · US500 · 0.5R | 209 | 0.20 | 72 % | 64 % | +0.03 | +0.7 | 70 % | 62 % | +0.00 | 54 | 62 % | 61 % | -0.07 | -0.7 | 66 % | 60 % | -0.04 |
| TOM+PREH · US500 · 1R | 209 | 0.20 | 53 % | 56 % | +0.09 | +1.7 | 48 % | 53 % | +0.02 | 54 | 47 % | 50 % | -0.02 | -0.2 | 46 % | 51 % | -0.02 |
| TOM+PREH · US500 · 2R | 209 | 0.20 | 13 % | 54 % | +0.10 | +1.7 | 19 % | 49 % | +0.02 | 54 | 17 % | 48 % | +0.06 | +0.4 | 16 % | 47 % | -0.01 |
| TOM+PREH · US500 · none | 209 | 0.20 | – | 54 % | +0.11 | +1.8 | – | 48 % | +0.03 | 54 | – | 48 % | +0.05 | +0.4 | – | 47 % | +0.02 |
| TOM+PREH_hw · NAS100 · 0.5R | 77 | 0.10 | 68 % | 60 % | -0.03 | -0.4 | 70 % | 62 % | +0.01 | 28 | 68 % | 57 % | -0.05 | -0.4 | 66 % | 60 % | -0.05 |
| TOM+PREH_hw · NAS100 · 1R | 77 | 0.10 | 50 % | 51 % | +0.01 | +0.2 | 50 % | 54 % | +0.03 | 28 | 59 % | 50 % | +0.09 | +0.5 | 51 % | 51 % | +0.01 |
| TOM+PREH_hw · NAS100 · 2R | 77 | 0.10 | 11 % | 51 % | +0.07 | +0.6 | 17 % | 51 % | +0.06 | 28 | 22 % | 50 % | +0.16 | +0.9 | 18 % | 49 % | +0.03 |
| TOM+PREH_hw · NAS100 · none | 77 | 0.10 | – | 51 % | +0.05 | +0.5 | – | 51 % | +0.08 | 28 | – | 50 % | +0.19 | +1.0 | – | 49 % | +0.07 |
| TOM+PREH_hw · US500 · 0.5R | 108 | 0.10 | 72 % | 64 % | +0.03 | +0.5 | 69 % | 62 % | -0.00 | 28 | 52 % | 54 % | -0.17 | -1.3 | 65 % | 60 % | -0.05 |
| TOM+PREH_hw · US500 · 1R | 108 | 0.10 | 55 % | 56 % | +0.11 | +1.5 | 48 % | 54 % | +0.02 | 28 | 48 % | 50 % | -0.03 | -0.2 | 48 % | 50 % | -0.01 |
| TOM+PREH_hw · US500 · 2R | 108 | 0.10 | 17 % | 53 % | +0.12 | +1.3 | 16 % | 50 % | +0.02 | 28 | 21 % | 50 % | +0.08 | +0.4 | 17 % | 46 % | +0.00 |
| TOM+PREH_hw · US500 · none | 108 | 0.10 | – | 53 % | +0.13 | +1.4 | – | 50 % | +0.02 | 28 | – | 50 % | +0.09 | +0.4 | – | 46 % | +0.04 |

## Befunde
1. **Overnight-Drift (ON, ONneg, ONbig): tot.** Brutto-R im Train ≈ 0 (NAS100 +0,005, US500 +0,003 R), netto −0,06 bis −0,12 R,
   2024 −0,13 bis −0,23 R. Mittlere 2:00–3:00-Rendite Train: NAS100 −0,45 bp (t −0,6), US500 −0,02 bp (t −0,0) – kein
   Stundenfenster sticht heraus (Stundenprofil Train 0–16 Uhr: |t| ≤ 2,2, 2–3 Uhr unauffällig). Deckt sich mit der Folgearbeit der
   Autoren (Boyarchenko/Larsen/Whelan, Liberty Street Economics 07/2026 „The Disappearing Overnight Drift“: Fenster seit 2021 ≈ 0,
   Ursache kleinere Schluss-Orderungleichgewichte). Selbst historisch (≈ 1,4 bp/Tag) hätte der 1-h-Trade nach 1 bp Kosten
   kaum etwas übrig gelassen. Die Bedingung „negativer Vortag“ hebt nichts über das Nullmodell (t_vs_null ≤ 0,7).
   Hinweis: Für ON (jeden Tag) ist das Nullmodell per Konstruktion fast identisch mit der Regel.
2. **Monatswechsel (TOM):** US500 Train +0,08…+0,10 R (t 1,4; Null ≈ 0), 2024 ≈ 0…+0,08; NAS100 Train ≈ 0 (unter Null), 2024
   +0,15…+0,21 (t 1,2–1,4). Inkonsistent über Instrumente/Jahre, nie t ≥ 2.
3. **Vor-Feiertag (PREH):** Train NAS100 +0,20…+0,29 R, US500 +0,11…+0,16 R (bei 0,5 R ≈ 0), aber nur n 27/36
   (t ≤ 1,5); 2024 n 10, ≈ 0. Zu selten (0,035/Tag) und statistisch nicht tragfähig.
4. **OPEX-Woche (OPEXW):** Train ≈ Nullmodell (−0,03…+0,07 R), 2024 NAS100 −0,14…−0,18 R. Die belegte Richtung (Long)
   trägt intraday nicht.
5. **Bündel TOM+PREH:** US500 Train +0,09…+0,11 R (t 1,7–1,8, t_vs_null 1,3–1,4), 2024 −0,07…+0,06. NAS100 ≈ Null.
   Halloween-Filter verbessert nichts (US500 t 1,3–1,5 bei halber Häufigkeit).
6. **Trade-off-Kurve:** 0,5 R liefert durchweg 65–72 % Target vor Stop – das ist reine Geometrie (Ziel 0,5 σ gegen Stop 1 σ);
   das Nullmodell erreicht dieselben 62–73 %. R je Trade bei 0,5 R im Train zwischen −0,13 und +0,06 (2024 bis −0,35). Mit größeren Zielen sinkt TvS auf
   10–25 % (2 R) bzw. Gewinnquote ~50 % („none“), R steigt nur dort, wo eine (schwache) Drift existiert. Kein Punkt der Kurve
   kommt gleichzeitig an ≥ 60 % und ≥ 0,5 R heran; keiner schlägt noise-1.0 (57 % / +0,11 R, t 2,0).

## Kandidaten
Keine (Kriterium Train R > 0 mit t ≥ 2 und klar über Nullmodell wird von keiner Zelle erfüllt).

## Varianten
64 im Ledger (`ergebnisse/varianten/kalender.csv`): Stufe 1 = 5 Regeln × 2 Instrumente × 4 Ziele (40), Stufe 2 = ONbig und
TOM+PREH (16), Stufe 3 = Halloween-Filter auf TOM+PREH (8). Alle Entscheidungen auf Train; 2024 einmal am Ende für alle 64.

## Probleme / Zweifel
- Vor der Train-Auswertung habe ich zur Plausibilisierung einmal die *gepoolte* 2020–24-Statistik der 2–3-Uhr-Rendite (US500,
  Mittel −0,06 bp) ausgegeben, also 2024 vermischt mitgesehen. Kein Parameter hing davon ab (Regel stand aus der Literatur fest).
- `qdata.load` liefert mit dem Standard `warmup_days=60` Kerzen **vor** dev_start (NAS100: Nov/Dez 2020 aus der gesperrten
  OANDA-Quelle; US500: Nov/Dez 2019). Ich habe `warmup_days=0` benutzt (Januar 2021 bzw. 2020 ohne σ → keine Trades).
  `familien/noise10_repro.py` nutzt den Standard und liest damit gesperrte Warmup-Kerzen. Bitte prüfen, ob das gewollt ist.
- `qbt.n_trading_days` und `qbt.null_model` zählen alle Wochentage mit CFD-Kerzen, also auch NYSE-Feiertage (CFD handelt
  verkürzt) – Trades/Tag dadurch ~3 % zu niedrig, Nullmodell zieht gelegentlich Feiertage. Für die Schlüsse unerheblich.
- PREH hat nur ~9 Fälle/Jahr; jede Aussage dazu ist statistisch schwach.
- Die Kalenderlogik (Monatsletzter, Vor-Feiertag, 3. Freitag) nutzt den regelbasierten NYSE-Kalender (vorab bekannt, keine
  Kursvorschau); außerplanmäßige Schließungen (z. B. Staatstrauer) werden bewusst nicht als Feiertag behandelt.
- WebFetch war im Container nicht möglich (DNS); Literaturangaben stammen aus WebSearch-Zusammenfassungen.

Dateien: `kal.py` (Kalender, σ_F, Signalbau), `run_effekte.py` (Läufe, `KAL_RULES=stufe1|2|3`, Phase `train|val`),
`make_tradeoff.py` (→ `tradeoff.csv`).
