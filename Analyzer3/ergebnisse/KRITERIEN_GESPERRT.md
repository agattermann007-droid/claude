# Erfolgskriterien für den gesperrten Test (festgelegt vor dem Lauf)

Stand: 15.10.2026. Diese Datei wurde geschrieben, bevor irgendein Ergebnis auf gesperrten Daten existierte. `lib/locked_run.py` speichert ihre SHA-256 in `ergebnisse/gesperrt/LAUF.json` und verweigert jeden zweiten Lauf.

## Gesperrte Daten
- **„vor“:** alles vor Beginn der Entwicklungsdaten des jeweiligen Instruments.
  - NAS100 2005-01 bis 2020-12; OANDA, mit einer Lücke von 2020-05-09 bis 2020-12-31.
  - US500 und JPN225 2005–2019; OANDA bis 2014, Pedram ab 2015.
  - GER40 2010-11 bis 2019; HistData bis 2014, Pedram ab 2015.
  - HK50 2015–2019; Pedram.
- **„2026“:** 2026-01-01 bis 2026-10-07; Pedram.
- **Datenprüfungen vor dem Lauf:** nur Uhrzeit-Abgleiche zwischen Quellen, ohne jede Strategieauswertung (siehe `daten/QUELLEN.md`). Dabei wurde die HistData-Uhr korrigiert.

## Kandidaten (Hauptregel jeweils unverändert aus dem Modul)
| Nr | Name | Modul | Instrumente |
|---|---|---|---|
| 0 | noise-1.0 (Referenz, zusätzliche Prüfung 2005–2020) | familien/referenz/kandidat_noise10.py | NAS100 |
| 1 | aus-A | familien/ausstiege/kandidat_A_n10_ziel15.py | NAS100 |
| 2 | aus-B | familien/ausstiege/kandidat_B_paps_tp05be.py | NAS100 |
| 3 | aus-C (US500 Grenzfall, t 2,01) | familien/ausstiege/kandidat_C_pap0_tp10paper.py | NAS100, US500 |
| 4 | ni-A_s1 | familien/noise_indizes/kandidat_A_s1.py | NAS100, US500, GER40, JPN225, HK50 |
| 5 | ni-B_s1 | familien/noise_indizes/kandidat_B_s1.py | NAS100, US500, GER40, JPN225, HK50 |
| 6 | ni-n10eod_s1 | familien/noise_indizes/kandidat_n10eod_s1.py | NAS100, US500, JPN225, HK50 |
| 7 | ev-fade930 (schwach: Spiegelregel, 2025 negativ) | familien/ereignisse/kandidat_fade930.py | NAS100 |
| 8 | kal-tom-preh (Grenzfall, t gegen Null 1,6) | familien/kalender/grenzfall_tom_preh.py | US500 |

## Urteil je Kandidat
Grundlage sind alle Trades eines Kandidaten über alle Instrumente, netto nach den Kosten aus `qdata.COST`.

**K1 – positive Erwartung, signifikant nach Mehrfachtest-Korrektur:**
- Bedingung: Gepoolt über „vor“ + „2026“ ist R netto je Trade > 0 und der Tages-Cluster-t ≥ **2,54**.
- Die Schwelle ist Bonferroni für 9 Hypothesen, einseitig, α = 5 %.

**K2 – besser als Zufall mit gleicher Geometrie:**
- Bedingung: Gepoolt ist der t-Wert gegen das Nullmodell ≥ **2,0**.
- Nullmodell: gleiche Geometrie, Richtung und NY-Uhrzeit, Tag gleichverteilt über den jeweiligen Zeitraum, K = 100 Ziehungen je Trade.

**K3 – trägt auch im jüngsten Zeitraum:**
- Bedingung: In „2026“ ist R netto je Trade > 0.

**Urteil:**
- **bestanden** = K1 und K2 und K3.
- **bestanden mit Vorbehalt** = K1 und K2, aber nicht K3. 2026 hat nur rund 190 Handelstage, bei einer echten Erwartung von +0,1 R ist ein negatives 2026 nicht unwahrscheinlich.
- **nicht bestanden** = sonst.

Zusätzlich je Kandidat berichtet, ohne Einfluss auf das Urteil:
- R je Trade, Target vor Stop, Trades je Tag und R je Tag in jedem Zeitraum;
- Vergleich mit noise-1.0 auf denselben gesperrten Daten;
- Erfüllung der Ziele 2–4.

## Trade-off-Kurve (beschreibend, vorab festgelegt)
- **Kandidaten:** alle mit festem Ziel (0, 1, 4, 6, 7, 8).
- **Varianten:** dieselben Signale mit Ziel 0,5 / 1 / 1,5 / 2 R und ohne Ziel. Stop und Zeitausstieg bleiben unverändert.
- **Markierter Punkt:** der Punkt mit dem höchsten R je Handelstag auf den gesperrten Daten (Ziel 1: Geld verdienen bei festem Risiko je Trade). Er wird nur gezeigt, nicht gewählt; eine Änderung der Regel wäre ein neuer, ungeprüfter Kandidat.

## Ablauf
1. Der unabhängige Prüfer (Workflow „pruefer-zukunftsblick“) muss für jedes Modul „bestanden“ melden. Bei einem Befund wird das Modul korrigiert und erneut geprüft. Ein Kandidat mit offenem Befund läuft nicht mit, das wird vermerkt.
2. `python3 lib/locked_run.py` wird genau einmal ausgeführt.
3. Ergebnisse unverändert berichten; nach dem Lauf wird keine Regel mehr geändert.

```json
{"schwellen": {"t_pool_min": 2.54, "t_vs_null_min": 2.0, "muss_positiv": ["2026"]},
 "kandidaten": [
  {"name": "noise-1.0", "modul": "familien/referenz/kandidat_noise10.py", "instrumente": ["NAS100"],
   "zeitraeume": [{"name": "vor", "von": "2005-01-01", "bis": "DEV_START"}, {"name": "2026", "von": "2026-01-01", "bis": "2026-10-08"}],
   "kurve": [0.5, 1.0, 1.5, 2.0, null]},
  {"name": "aus-A", "modul": "familien/ausstiege/kandidat_A_n10_ziel15.py", "instrumente": ["NAS100"],
   "zeitraeume": [{"name": "vor", "von": "2005-01-01", "bis": "DEV_START"}, {"name": "2026", "von": "2026-01-01", "bis": "2026-10-08"}],
   "kurve": [0.5, 1.0, 1.5, 2.0, null]},
  {"name": "aus-B", "modul": "familien/ausstiege/kandidat_B_paps_tp05be.py", "instrumente": ["NAS100"],
   "zeitraeume": [{"name": "vor", "von": "2005-01-01", "bis": "DEV_START"}, {"name": "2026", "von": "2026-01-01", "bis": "2026-10-08"}],
   "kurve": []},
  {"name": "aus-C", "modul": "familien/ausstiege/kandidat_C_pap0_tp10paper.py", "instrumente": ["NAS100", "US500"],
   "zeitraeume": [{"name": "vor", "von": "2005-01-01", "bis": "DEV_START"}, {"name": "2026", "von": "2026-01-01", "bis": "2026-10-08"}],
   "kurve": []},
  {"name": "ni-A_s1", "modul": "familien/noise_indizes/kandidat_A_s1.py", "instrumente": ["NAS100", "US500", "GER40", "JPN225", "HK50"],
   "zeitraeume": [{"name": "vor", "von": "2005-01-01", "bis": "DEV_START"}, {"name": "2026", "von": "2026-01-01", "bis": "2026-10-08"}],
   "kurve": [0.5, 1.0, 1.5, 2.0, null]},
  {"name": "ni-B_s1", "modul": "familien/noise_indizes/kandidat_B_s1.py", "instrumente": ["NAS100", "US500", "GER40", "JPN225", "HK50"],
   "zeitraeume": [{"name": "vor", "von": "2005-01-01", "bis": "DEV_START"}, {"name": "2026", "von": "2026-01-01", "bis": "2026-10-08"}],
   "kurve": []},
  {"name": "ni-n10eod_s1", "modul": "familien/noise_indizes/kandidat_n10eod_s1.py", "instrumente": ["NAS100", "US500", "JPN225", "HK50"],
   "zeitraeume": [{"name": "vor", "von": "2005-01-01", "bis": "DEV_START"}, {"name": "2026", "von": "2026-01-01", "bis": "2026-10-08"}],
   "kurve": [0.5, 1.0, 1.5, 2.0, null]},
  {"name": "ev-fade930", "modul": "familien/ereignisse/kandidat_fade930.py", "instrumente": ["NAS100"],
   "zeitraeume": [{"name": "vor", "von": "2005-01-01", "bis": "DEV_START"}, {"name": "2026", "von": "2026-01-01", "bis": "2026-10-08"}],
   "kurve": [0.5, 1.0, 1.5, 2.0, null]},
  {"name": "kal-tom-preh", "modul": "familien/kalender/grenzfall_tom_preh.py", "instrumente": ["US500"],
   "zeitraeume": [{"name": "vor", "von": "2005-01-01", "bis": "DEV_START"}, {"name": "2026", "von": "2026-01-01", "bis": "2026-10-08"}],
   "kurve": [0.5, 1.0, 1.5, 2.0, null]}
 ]}
```
