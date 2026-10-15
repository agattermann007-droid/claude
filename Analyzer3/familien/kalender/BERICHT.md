# Familie kalender – Bericht (Stand 15.10.2026, Datenstand v2)

**Ergebnis: kein freigegebener Kandidat, ein Grenzfall.** Auf den korrigierten Daten (v2: ts4-Uhr 2020/2021 um 1 h
berichtigt) erreicht das Bündel **Monatswechsel + Vor-Feiertag auf US500** im Train erstmals t ≥ 2 (+0,12…+0,14 R,
t 2,1–2,2) und ist 2024 bei „kein Ziel“/2 R positiv (+0,05/+0,06 R). Der Abstand zum Nullmodell bleibt aber statistisch
unklar (t_vs_null 1,6–1,8 < 2), das Bündel wurde erst nach Stufe 1 gebildet, und die Train-t-beste Geometrie (1 R) ist
2024 negativ (−0,02 R). Nach meinem Maßstab aus v1 („klar über Null“ = t_vs_null ≥ 2) ist das kein Kandidat. Für eine
mögliche Freigabe durch die Koordination liegt das Modul als `grenzfall_tom_preh.py` bereit (gleiche Schnittstelle wie
`kandidat_*.py`, Abschneide-Prüfung bestanden). Die Overnight-Drift bleibt tot.

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
(Eröffnung→Schluss desselben Fensters) der letzten 20 NYSE-Handelstage, strikt vor dem Signaltag. Ziele 0,5 / 1 / 2 R und
„none“ (nur Zeitausstieg). Long. Kosten qdata.COST (1 bp Roundtrip): im 1-h-Fenster (σ_F ≈ 0,14–0,16 %) ≈ 0,07 R je Trade
(2024: 0,10–0,14 R), im Tagesfenster ≈ 0,01–0,02 R.

Nicht getestet: XAUUSD (für Gold keine belegte Intraday-Kalenderregel dieser Art; nur der Monats-„Autumn effect“, Baur 2013,
in der Replikation Potrykus/Augustynowicz 2024 umgekehrt). Wochentagseffekt (Montag): seit den 1990ern verschwunden/umgekehrt
(Schwert 2003), also nicht belegt.

## Ergebnisse v2 (Train = NAS100 2021–23, US500 2020–23; Val = 2024; Nullmodell = gleiche Uhrzeit/Geometrie, Zufallstag, K = 20)
TvS = Target vor Stop (bei „none“ nicht definiert), Gew. = Gewinnquote, R netto je Trade, t = Trade-t (= Tages-t, ein Trade/Tag).
Variantennamen: Regel · Instrument · Ziel (in `tradeoff.csv` mit „|“ getrennt). Volle Trade-off-Kurve (inkl. Nullmodell-Zeilen,
R pro Tag) in `tradeoff.csv`; Rohzellen in `zellen_*_stufe*.csv`; v1-Stand in `v1/`.

| Variante | Train n | /Tag | TvS | Gew. | R netto | t | Null TvS | Null Gew. | Null R | Val n | TvS | Gew. | R netto | t | Null TvS | Null Gew. | Null R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ON · NAS100 · 0.5R | 723 | 0.93 | 67 % | 56 % | -0.12 | -5.0 | 67 % | 55 % | -0.11 | 252 | 64 % | 55 % | -0.17 | -4.2 | 68 % | 57 % | -0.13 |
| ON · NAS100 · 1R | 723 | 0.93 | 49 % | 48 % | -0.07 | -2.3 | 48 % | 47 % | -0.08 | 252 | 46 % | 45 % | -0.14 | -2.8 | 47 % | 45 % | -0.14 |
| ON · NAS100 · 2R | 723 | 0.93 | 18 % | 46 % | -0.06 | -1.7 | 21 % | 44 % | -0.06 | 252 | 16 % | 42 % | -0.14 | -2.5 | 16 % | 43 % | -0.14 |
| ON · NAS100 · none | 723 | 0.93 | – | 46 % | -0.06 | -1.7 | – | 43 % | -0.07 | 252 | – | 42 % | -0.13 | -2.1 | – | 42 % | -0.13 |
| ONneg · NAS100 · 0.5R | 335 | 0.43 | 66 % | 59 % | -0.10 | -2.9 | 66 % | 54 % | -0.11 | 115 | 59 % | 54 % | -0.23 | -3.6 | 67 % | 57 % | -0.14 |
| ONneg · NAS100 · 1R | 335 | 0.43 | 51 % | 50 % | -0.05 | -1.1 | 47 % | 47 % | -0.08 | 115 | 42 % | 43 % | -0.22 | -2.7 | 46 % | 44 % | -0.15 |
| ONneg · NAS100 · 2R | 335 | 0.43 | 20 % | 46 % | -0.05 | -1.0 | 22 % | 44 % | -0.06 | 115 | 15 % | 38 % | -0.22 | -2.5 | 17 % | 41 % | -0.14 |
| ONneg · NAS100 · none | 335 | 0.43 | – | 46 % | -0.04 | -0.8 | – | 44 % | -0.06 | 115 | – | 38 % | -0.21 | -2.3 | – | 41 % | -0.14 |
| TOM · NAS100 · 0.5R | 136 | 0.18 | 67 % | 60 % | -0.03 | -0.5 | 72 % | 64 % | +0.03 | 48 | 69 % | 62 % | +0.01 | +0.1 | 66 % | 60 % | -0.05 |
| TOM · NAS100 · 1R | 136 | 0.18 | 49 % | 53 % | +0.01 | +0.2 | 50 % | 54 % | +0.03 | 48 | 59 % | 56 % | +0.15 | +1.2 | 47 % | 53 % | -0.00 |
| TOM · NAS100 · 2R | 136 | 0.18 | 10 % | 51 % | +0.04 | +0.5 | 20 % | 51 % | +0.06 | 48 | 28 % | 54 % | +0.20 | +1.4 | 13 % | 51 % | +0.02 |
| TOM · NAS100 · none | 136 | 0.18 | – | 51 % | +0.03 | +0.4 | – | 50 % | +0.06 | 48 | – | 54 % | +0.21 | +1.4 | – | 51 % | +0.04 |
| PREH · NAS100 · 0.5R | 27 | 0.03 | 71 % | 70 % | +0.07 | +0.6 | 73 % | 62 % | +0.02 | 10 | 50 % | 40 % | -0.21 | -1.0 | 63 % | 56 % | -0.10 |
| PREH · NAS100 · 1R | 27 | 0.03 | 54 % | 67 % | +0.21 | +1.5 | 49 % | 51 % | +0.02 | 10 | 50 % | 40 % | -0.06 | -0.2 | 50 % | 51 % | -0.00 |
| PREH · NAS100 · 2R | 27 | 0.03 | 14 % | 67 % | +0.24 | +1.5 | 20 % | 48 % | +0.06 | 10 | 25 % | 40 % | +0.04 | +0.1 | 14 % | 47 % | -0.01 |
| PREH · NAS100 · none | 27 | 0.03 | – | 67 % | +0.30 | +1.6 | – | 47 % | +0.05 | 10 | – | 40 % | +0.05 | +0.2 | – | 47 % | +0.01 |
| OPEXW · NAS100 · 0.5R | 171 | 0.22 | 70 % | 63 % | -0.00 | -0.1 | 71 % | 63 % | +0.01 | 58 | 56 % | 50 % | -0.18 | -2.0 | 67 % | 60 % | -0.04 |
| OPEXW · NAS100 · 1R | 171 | 0.22 | 50 % | 53 % | +0.03 | +0.5 | 49 % | 54 % | +0.02 | 58 | 33 % | 43 % | -0.18 | -1.7 | 50 % | 53 % | +0.01 |
| OPEXW · NAS100 · 2R | 171 | 0.22 | 12 % | 53 % | +0.07 | +1.0 | 19 % | 51 % | +0.05 | 58 | 12 % | 41 % | -0.17 | -1.5 | 13 % | 51 % | +0.03 |
| OPEXW · NAS100 · none | 171 | 0.22 | – | 53 % | +0.08 | +1.1 | – | 50 % | +0.06 | 58 | – | 41 % | -0.14 | -1.1 | – | 51 % | +0.04 |
| ON · US500 · 0.5R | 972 | 0.94 | 69 % | 58 % | -0.10 | -4.8 | 67 % | 54 % | -0.12 | 252 | 66 % | 53 % | -0.20 | -4.9 | 66 % | 54 % | -0.19 |
| ON · US500 · 1R | 972 | 0.94 | 49 % | 48 % | -0.07 | -2.7 | 48 % | 45 % | -0.09 | 252 | 45 % | 42 % | -0.19 | -3.9 | 44 % | 42 % | -0.21 |
| ON · US500 · 2R | 972 | 0.94 | 17 % | 45 % | -0.07 | -2.4 | 24 % | 41 % | -0.07 | 252 | 19 % | 40 % | -0.17 | -3.0 | 17 % | 40 % | -0.19 |
| ON · US500 · none | 972 | 0.94 | – | 44 % | -0.06 | -1.8 | – | 40 % | -0.05 | 252 | – | 40 % | -0.15 | -2.5 | – | 39 % | -0.18 |
| ONneg · US500 · 0.5R | 436 | 0.42 | 66 % | 59 % | -0.11 | -3.5 | 67 % | 54 % | -0.12 | 112 | 65 % | 57 % | -0.22 | -3.4 | 66 % | 55 % | -0.19 |
| ONneg · US500 · 1R | 436 | 0.42 | 48 % | 48 % | -0.08 | -2.1 | 49 % | 45 % | -0.09 | 112 | 46 % | 44 % | -0.21 | -2.6 | 44 % | 43 % | -0.22 |
| ONneg · US500 · 2R | 436 | 0.42 | 19 % | 44 % | -0.08 | -1.7 | 23 % | 41 % | -0.08 | 112 | 16 % | 40 % | -0.20 | -2.1 | 19 % | 40 % | -0.19 |
| ONneg · US500 · none | 436 | 0.42 | – | 44 % | -0.05 | -1.1 | – | 40 % | -0.03 | 112 | – | 40 % | -0.17 | -1.7 | – | 40 % | -0.17 |
| TOM · US500 · 0.5R | 186 | 0.18 | 71 % | 64 % | +0.03 | +0.6 | 70 % | 62 % | +0.00 | 48 | 63 % | 62 % | -0.04 | -0.4 | 66 % | 59 % | -0.05 |
| TOM · US500 · 1R | 186 | 0.18 | 55 % | 57 % | +0.11 | +1.9 | 48 % | 53 % | +0.01 | 48 | 50 % | 50 % | +0.00 | +0.0 | 46 % | 50 % | -0.02 |
| TOM · US500 · 2R | 186 | 0.18 | 11 % | 54 % | +0.12 | +1.8 | 18 % | 49 % | +0.02 | 48 | 19 % | 48 % | +0.08 | +0.5 | 16 % | 46 % | -0.01 |
| TOM · US500 · none | 186 | 0.18 | – | 54 % | +0.13 | +1.9 | – | 48 % | +0.02 | 48 | – | 48 % | +0.07 | +0.5 | – | 46 % | +0.00 |
| PREH · US500 · 0.5R | 36 | 0.03 | 75 % | 64 % | +0.06 | +0.6 | 71 % | 63 % | +0.01 | 10 | 50 % | 50 % | -0.19 | -0.8 | 67 % | 59 % | -0.05 |
| PREH · US500 · 1R | 36 | 0.03 | 38 % | 56 % | +0.13 | +1.0 | 49 % | 53 % | +0.04 | 10 | 33 % | 50 % | -0.09 | -0.3 | 49 % | 50 % | -0.01 |
| PREH · US500 · 2R | 36 | 0.03 | 11 % | 56 % | +0.16 | +1.2 | 18 % | 50 % | +0.05 | 10 | 0 % | 50 % | +0.01 | +0.0 | 17 % | 47 % | -0.01 |
| PREH · US500 · none | 36 | 0.03 | – | 56 % | +0.17 | +1.2 | – | 50 % | +0.06 | 10 | – | 50 % | +0.01 | +0.0 | – | 47 % | +0.00 |
| OPEXW · US500 · 0.5R | 228 | 0.22 | 67 % | 59 % | -0.05 | -1.1 | 70 % | 62 % | +0.01 | 58 | 69 % | 64 % | +0.00 | +0.0 | 67 % | 61 % | -0.03 |
| OPEXW · US500 · 1R | 228 | 0.22 | 44 % | 49 % | -0.04 | -0.8 | 48 % | 53 % | +0.02 | 58 | 40 % | 48 % | -0.06 | -0.5 | 48 % | 51 % | -0.00 |
| OPEXW · US500 · 2R | 228 | 0.22 | 10 % | 48 % | -0.02 | -0.4 | 19 % | 49 % | +0.03 | 58 | 14 % | 45 % | -0.05 | -0.5 | 16 % | 47 % | -0.00 |
| OPEXW · US500 · none | 228 | 0.22 | – | 48 % | -0.00 | -0.1 | – | 49 % | +0.03 | 58 | – | 45 % | +0.01 | +0.1 | – | 47 % | +0.02 |
| ONbig · NAS100 · 0.5R | 138 | 0.18 | 62 % | 58 % | -0.13 | -2.2 | 68 % | 54 % | -0.10 | 31 | 48 % | 48 % | -0.35 | -2.6 | 67 % | 54 % | -0.16 |
| ONbig · NAS100 · 1R | 138 | 0.18 | 48 % | 49 % | -0.07 | -1.0 | 48 % | 46 % | -0.07 | 31 | 35 % | 39 % | -0.33 | -2.0 | 45 % | 43 % | -0.16 |
| ONbig · NAS100 · 2R | 138 | 0.18 | 23 % | 43 % | -0.06 | -0.6 | 19 % | 44 % | -0.07 | 31 | 19 % | 35 % | -0.22 | -1.1 | 15 % | 41 % | -0.15 |
| ONbig · NAS100 · none | 138 | 0.18 | – | 43 % | -0.04 | -0.5 | – | 43 % | -0.07 | 31 | – | 35 % | -0.12 | -0.5 | – | 40 % | -0.15 |
| TOM+PREH · NAS100 · 0.5R | 153 | 0.20 | 69 % | 62 % | -0.01 | -0.2 | 72 % | 64 % | +0.02 | 54 | 67 % | 61 % | -0.02 | -0.2 | 67 % | 61 % | -0.04 |
| TOM+PREH · NAS100 · 1R | 153 | 0.20 | 51 % | 55 % | +0.05 | +0.7 | 50 % | 55 % | +0.04 | 54 | 58 % | 56 % | +0.13 | +1.1 | 49 % | 54 % | +0.01 |
| TOM+PREH · NAS100 · 2R | 153 | 0.20 | 11 % | 54 % | +0.08 | +1.1 | 20 % | 51 % | +0.06 | 54 | 25 % | 54 % | +0.17 | +1.2 | 15 % | 52 % | +0.03 |
| TOM+PREH · NAS100 · none | 153 | 0.20 | – | 54 % | +0.08 | +1.1 | – | 51 % | +0.07 | 54 | – | 54 % | +0.18 | +1.3 | – | 52 % | +0.05 |
| ONbig · US500 · 0.5R | 135 | 0.13 | 63 % | 61 % | -0.13 | -2.1 | 67 % | 53 % | -0.11 | 18 | 56 % | 56 % | -0.29 | -1.7 | 68 % | 54 % | -0.17 |
| ONbig · US500 · 1R | 135 | 0.13 | 49 % | 48 % | -0.07 | -0.9 | 48 % | 45 % | -0.08 | 18 | 47 % | 50 % | -0.16 | -0.7 | 44 % | 42 % | -0.21 |
| ONbig · US500 · 2R | 135 | 0.13 | 25 % | 44 % | -0.05 | -0.5 | 23 % | 42 % | -0.07 | 18 | 31 % | 39 % | -0.03 | -0.1 | 16 % | 39 % | -0.22 |
| ONbig · US500 · none | 135 | 0.13 | – | 44 % | +0.05 | +0.4 | – | 41 % | -0.04 | 18 | – | 39 % | +0.22 | +0.5 | – | 38 % | -0.18 |
| TOM+PREH · US500 · 0.5R | 210 | 0.20 | 72 % | 65 % | +0.04 | +0.9 | 70 % | 62 % | +0.00 | 54 | 62 % | 61 % | -0.07 | -0.7 | 66 % | 60 % | -0.04 |
| TOM+PREH · US500 · 1R | 210 | 0.20 | 54 % | 57 % | +0.12 | +2.2 | 48 % | 53 % | +0.02 | 54 | 47 % | 50 % | -0.02 | -0.2 | 46 % | 51 % | -0.02 |
| TOM+PREH · US500 · 2R | 210 | 0.20 | 11 % | 55 % | +0.13 | +2.1 | 18 % | 49 % | +0.03 | 54 | 17 % | 48 % | +0.06 | +0.4 | 16 % | 47 % | -0.01 |
| TOM+PREH · US500 · none | 210 | 0.20 | – | 55 % | +0.14 | +2.2 | – | 49 % | +0.03 | 54 | – | 48 % | +0.05 | +0.4 | – | 47 % | +0.02 |
| TOM+PREH_hw · NAS100 · 0.5R | 77 | 0.10 | 69 % | 61 % | -0.02 | -0.2 | 71 % | 63 % | +0.01 | 28 | 68 % | 57 % | -0.05 | -0.4 | 66 % | 60 % | -0.05 |
| TOM+PREH_hw · NAS100 · 1R | 77 | 0.10 | 52 % | 52 % | +0.04 | +0.4 | 50 % | 54 % | +0.04 | 28 | 59 % | 50 % | +0.09 | +0.5 | 51 % | 51 % | +0.01 |
| TOM+PREH_hw · NAS100 · 2R | 77 | 0.10 | 11 % | 52 % | +0.10 | +0.9 | 17 % | 51 % | +0.06 | 28 | 22 % | 50 % | +0.16 | +0.9 | 18 % | 49 % | +0.03 |
| TOM+PREH_hw · NAS100 · none | 77 | 0.10 | – | 52 % | +0.08 | +0.7 | – | 51 % | +0.08 | 28 | – | 50 % | +0.19 | +1.0 | – | 49 % | +0.07 |
| TOM+PREH_hw · US500 · 0.5R | 108 | 0.10 | 74 % | 67 % | +0.06 | +1.0 | 69 % | 62 % | +0.00 | 28 | 52 % | 54 % | -0.17 | -1.3 | 65 % | 60 % | -0.05 |
| TOM+PREH_hw · US500 · 1R | 108 | 0.10 | 59 % | 57 % | +0.15 | +2.0 | 47 % | 54 % | +0.03 | 28 | 48 % | 50 % | -0.03 | -0.2 | 48 % | 50 % | -0.01 |
| TOM+PREH_hw · US500 · 2R | 108 | 0.10 | 18 % | 54 % | +0.16 | +1.7 | 17 % | 51 % | +0.03 | 28 | 21 % | 50 % | +0.08 | +0.4 | 17 % | 46 % | +0.00 |
| TOM+PREH_hw · US500 · none | 108 | 0.10 | – | 54 % | +0.17 | +1.8 | – | 50 % | +0.02 | 28 | – | 50 % | +0.09 | +0.4 | – | 46 % | +0.04 |

## Befunde
1. **Overnight-Drift (ON, ONneg, ONbig): tot.** Brutto-R im Train ≈ 0 (NAS100 +0,01, US500 +0,02 R), netto −0,05 bis −0,13 R,
   2024 −0,12 bis −0,35 R. Mittlere 2:00–3:00-Rendite Train: NAS100 −0,17 bp (t −0,2), US500 +0,76 bp (t 1,2); kein
   Stundenfenster 0–16 Uhr sticht heraus (max |t| 2,3–2,5 bei 16 Stunden). Deckt sich mit der Folgearbeit der Autoren
   (Liberty Street Economics 07/2026 „The Disappearing Overnight Drift“: Fenster seit 2021 ≈ 0). Selbst historisch (≈ 1,4 bp/Tag)
   bliebe nach 1 bp Kosten kaum etwas. Die Vortagsbedingung hebt nichts über das Nullmodell (t_vs_null ≤ 1,1). Für ON (jeden
   Tag) ist das Nullmodell per Konstruktion fast identisch mit der Regel.
2. **Monatswechsel (TOM):** US500 Train +0,11…+0,13 R (t 1,8–1,95; Null +0,01…+0,02; t_vs_null 1,5–1,7), 2024 ≈ 0…+0,08;
   NAS100 Train ≈ 0 (unter Null), 2024 +0,15…+0,21. Inkonsistent über Instrumente, einzeln nie t ≥ 2.
3. **Vor-Feiertag (PREH):** Train NAS100 +0,21…+0,30 R, US500 +0,13…+0,17 R (bei 0,5 R ≈ +0,06), aber nur n 27/36 (t ≤ 1,6);
   2024 n 10, ≈ 0. Zu selten (0,035/Tag).
4. **OPEX-Woche (OPEXW):** Train ≈ Nullmodell oder darunter, 2024 NAS100 −0,14…−0,18 R. Trägt intraday nicht.
5. **Bündel TOM+PREH (Grenzfall):** US500 Train +0,12 / +0,13 / +0,14 R bei 1 R / 2 R / none (t 2,19 / 2,10 / 2,17;
   Null +0,02…+0,04; t_vs_null 1,82 / 1,64 / 1,61); alle vier Train-Jahre positiv (none: 2020 +0,12, 2021 +0,12, 2022 +0,06,
   2023 +0,25 R); 2024 −0,02 / +0,06 / +0,05 R (Null −0,02 / −0,01 / +0,02). NAS100 ≈ Nullmodell.
   Halloween-Filter: US500 Train t 1,7–2,0 bei halber Häufigkeit, 2024 −0,03…+0,09 – bringt nichts.
6. **Trade-off-Kurve:** 0,5 R liefert 62–75 % Target vor Stop – reine Geometrie (Ziel 0,5 σ gegen Stop 1 σ); das Nullmodell
   erreicht 66–73 %. R bei 0,5 R im Train −0,13…+0,07 (2024 bis −0,35). Größere Ziele: TvS 10–25 % (2 R) bzw. Gewinnquote ~50 %
   („none“). Kein Punkt erreicht zugleich ≥ 60 % und ≥ 0,5 R; keiner schlägt noise-1.0 im Profil.

## Grenzfall `grenzfall_tom_preh.py` (US500, nicht freigegeben)
Regel: an jedem letzten Handelstag des Monats, den ersten 3 Handelstagen und dem letzten Handelstag vor einem regulären
NYSE-Feiertag Market-Long zur 9:30-NY-Eröffnung (15:30 Wien), Stop 1 × σ_F (20 Tage), kein Ziel, Ausstieg 15:00 NY (21:00 Wien;
verkürzte Tage 13:00). Quelle: Lakonishok/Smidt 1988; Ariel 1987/1990; McConnell/Xu 2008.
Kennzahlen (Modul nachgerechnet): Train n 210, 0,20/Tag, Gewinnquote 55 %, +0,136 R, t 2,17 (Null +0,035);
2024 n 54, 48 %, +0,053 R, t 0,37 (Null +0,018).
Abschneide-Prüfung: 40 Zeitpunkte (25 genau an Signalkerzen) – identische Signale (i_sig, Richtung, Stop, Ziel).
Hinweis für den Prüfer: `i_last` ist eine Uhrzeit-Grenze und kann bei abgeschnittenen Daten naturgemäß nicht vorliegen.
Gegen eine Freigabe sprechen: t_vs_null 1,6 (< 2), Bündel nach Stufe 1 gebildet, 1-R-Geometrie 2024 negativ, Profil weit vom
Ziel (kein Ziel, ~50 % Gewinnquote, +0,05…+0,14 R). Dafür: Literaturregel, alle 5 Jahre (2020–24) positiv, gesperrter
US500-Zeitraum (2005–2019 + 2026) wäre ein langer, sauberer Test.

## Varianten
64 im Ledger (`ergebnisse/varianten/kalender.csv`), keine neuen in v2: Stufe 1 = 5 Regeln × 2 Instrumente × 4 Ziele (40),
Stufe 2 = ONbig und TOM+PREH (16), Stufe 3 = Halloween-Filter auf TOM+PREH (8). Ledger-Notizen: `train`/`val` = v1 (alte
Daten), `v2_vor_sigmafix` = erster v2-Lauf, `v2` = gültiger Stand (nach σ-Kausalitätsfix, s. u.).

## Probleme / Zweifel
- **v2-Korrekturen am eigenen Code (keine Parameter):** (a) σ_F für Tag D wurde nur gesetzt, wenn D selbst eine vollständige
  Fensterrendite hatte – kausal korrekt ist der letzte Wert strikt vor D. Betrifft 1 Trade je Zelle (TOM-Tag 2022-05-04 bzw.
  ON US500 2020-03-17); Änderung ≤ 0,01 R. (b) Bei Daten, die an der Signalkerze enden, wurde das Signal verworfen
  (Ausstiegskerze fehlt); jetzt bleibt es erhalten. Ohne Einfluss auf die dev-Zahlen, nötig für die Abschneide-Prüfung.
- Vor der Train-Auswertung (v1) habe ich zur Plausibilisierung einmal die gepoolte 2020–24-Statistik der 2–3-Uhr-Rendite
  ausgegeben (2024 vermischt mitgesehen). Kein Parameter hing davon ab.
- Das Urteil zu TOM+PREH ist datenempfindlich: v1 t 1,77, v2 t 2,17 – allein durch die 1-h-Korrektur 2020/21.
- `qbt.n_trading_days` und `qbt.null_model` zählen auch NYSE-Feiertage mit CFD-Kerzen (Trades/Tag ~3 % zu niedrig).
- PREH hat nur ~9 Fälle/Jahr. Kalenderlogik nutzt den regelbasierten NYSE-Kalender (vorab bekannt); außerplanmäßige
  Schließungen gelten bewusst nicht als Feiertag.
- WebFetch war im Container nicht möglich (DNS); Literaturangaben aus WebSearch-Zusammenfassungen.

Dateien: `kal.py` (Kalender, σ_F, Signalbau), `run_effekte.py` (`KAL_RULES=stufe1|2|3`, Phase `train|val`),
`make_tradeoff.py` (→ `tradeoff.csv`), `grenzfall_tom_preh.py`.
