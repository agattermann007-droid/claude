# Replikat v6: Suche nach neuen Ansätzen und Build 6.00

Python-Nachbau des GFT-Kontos mit beliebigen Signalströmen. Damit wurden neue Strategien gesucht, gegen die
alten Module geprüft (Ablation: welches Modul stört welches?) und die beiden Ausprägungen von Build 6.00
bewertet. Kursdaten und Zwischenstände liegen **nicht** im Repo.

## Daten

| Ordner | Inhalt | Quelle |
|---|---|---|
| `../data/` | MT5-Exporte `XAUUSD.x_M5.csv`, `NAS100.x_M5.csv` (03.01.2022 – 02.09.2026) | GFT-Terminal (wie Replikat v5) |
| `../extdata/` | Fremddaten XAUUSD 2006–2026, NAS100 2005–2025 (M5, NY-Zeit wie GFT) | frei verfügbare Datensätze, siehe `../extdata/DATEN_BERICHT.md` |

`../extdata/scripts/run_all.sh` baut die Fremddaten aus den Rohdaten neu auf (Downloads siehe Datenbericht).

## Dateien

| Datei | Inhalt |
|---|---|
| `prep5.py`, `sig5.py`, `eng5.py`, `evl5.py`, `batch.py` | Grundlage aus Replikat v5 (unverändert) |
| `eng6.py` | Kontomotor v6 = eng5 plus bis zu 14 generische Signalströme (`GP`-Spalten: Risiko, Max. Trades, Budget, Ziel-Verzögerung …). `t_eng6.py` prüft: ohne Ströme exakt eng5 |
| `evl6.py` | Bewertung: rollierende Starts, 1/2/3 Jahre, Störungen, Serien ≥ 5/6/8, kleinste Auszahlung, Ergebnis je Modul |
| `r6.py` | Grundeinstellungen (`SAFE` = strenge Regel-Lesart, `C510`, `PAY3` = Auszahlung ab 3 %) |
| `gsig.py` | schneller Einzel-Simulator für Signallisten (R je Trade, Trefferquote, Kennzahlen) |
| `scan6.py`, `scan6_run*.py` | Scanner: Ausbruch (B), Fehlausbruch-Fade (F), Tageszeit-Momentum (M), Sweep (S), rollende Fades; Auswahl nur mit guter In-Sample- **und** Out-of-Sample-Leistung (Grenze 01.07.2024) |
| `scan7_long.py`, `scan8_epochs.py` | dieselben Raster auf 2006–2021 (Fremddaten) bzw. über 4 Epochen |
| `cands.py` | die ausgewählten Fades (`FADES`) als Signalblöcke |
| `nz2.py` | Noise-Area-Momentum v2 als generischer Strom |
| `gext.py`, `sig_ext.py`, `val_ext*.py` | Fremddaten laden, alte Module darauf rechnen, Abgleich 2022–26 Fremd- gegen GFT-Daten |
| `guard.py`, `guard2.py`, `guardblk.py`, `streams.py` | Regime-Wächter (virtuelle Trades, PF/Summe der letzten N) und Signalblöcke für beide Datensätze |
| `x20.py` … `x30.py` | Einzelversuche (Break-even, Konflikt-Test ohne DEADBAND, Fade-Portfolios, Wächter, Mischungen) |
| `x31.py` | **Endbewertung GFT 2022–26** (16 Störungen) inkl. Startjahre |
| `x33.py` | Endzahlen auf GFT-Daten und Fremddaten 2006–2021 |
| `x32.py` | dasselbe mit Wächter „180 Tage“ (verworfen) |
| `t_feas.py`, `t_diag.py`, `t_se2.py` | Machbarkeit 5.10 bei 3/4 % Mindestauszahlung, Engpass-Diagnose, Streuung |
| `x34.py`, `t_se3.py` | 6.00 mit Auszahlung ab 4 %; Streuung von 6.00 über die 16 Störungen |
| `x35.py` | **Endzahlen 6.00 nach dem Code-Review** (Fades ohne US-Feiertage, Stop ≥ 6 Spreads) auf GFT-Daten (mit Startjahren) und Fremddaten |
| `x36.py` | **Build 6.10**: Screening letzter Verbesserungen (Abschluss-Ernte aller Module, Wächter-Schwelle, Fade-Risiko, Serien-Stopp) auf GFT- und Fremddaten |
| `x37.py` | **Endbewertung 6.10** (16 Störungen, Startjahre, Streuung) auf GFT-Daten und Fremddaten |
| `x38.py`, `x39.py` | 6.10 mit gültigem Tag erst ab 52 $ bzw. **50,50 $** (Reserve `ValidDayReserveUSD` wie im EA; x39 = Endzahlen) |
| `t_diag3.py` | Engpass-Diagnose 6.00: was hält die Auszahlung auf (gültige Tage oder Mindestgewinn)? |
| `t_port.py` | **Abgleich EA ↔ Replikat**: wörtliche Übertragung von `FadeKerze` (MQL5) gegen `scan6.gen_fade` + `gsig.simulate` |
| **Build 6.20 (Probability Grid)** | |
| `pgrid.py` | Nachbau des LuxAlgo-Probability-Grid: Schwung-Pivots aus Kerzenkörpern (`lux_pivots`), Zeitebenen aus M5 (`tf_bars`), Rang/Perzentil der Schenkel, Merkmale je Signal (`features`: Laufrichtung, Reife `p_ext`/`p_bar`, `beyond`, Zielweg, Stop-Chance) |
| `t_pgrid.py` | Prüfung `lux_pivots` gegen eine wörtliche Übertragung von `fetchPivot`/`fetchData` (Pine v6) |
| `pg_data.py` | durchgehender Datensatz 2006–2025 aus den Fremddaten (Grid-Historie und Vorstudie) |
| `pg_fade.py` | Fade-Signale mit Signal-Kerze, Extrem, Stop, Ziel (`gen_fade_info` = `scan6.gen_fade` plus Angaben) und Grid-Merkmale |
| `pg_study.py`, `pg_scan.py`, `pg_spread.py` | Vorstudie auf Signal-Ebene: Merkmale gegen Ergebnis je Periode (2006–13, 2014–21, 2022–23, 2024–25), Parameter-Raster der Regeln A/S/B, Grid-Ziel (`pg_study.py ziel`), Abhängigkeit vom Spread |
| `pg_study_old.py` | dasselbe für RSI21-Folgesignale und NAS-Noise (kein stabiler Effekt) |
| `pg_module.py` | Wirkung der Grid-Regel je Fade-Modul (ausgelassene Signale, PF und R je Jahr vorher/nachher) |
| `pg_blocks.py`, `pg_old.py`, `pg_rules.py` | Fade-Blöcke für eng6 mit Grid-Regel (Filter, Ziel, Gewicht; Wächter auf gefiltertem oder ganzem Strom), Auslass-Masken für RSI21/Noise, Varianten |
| `x40.py` | **Konto-Screening 6.20**: `python x40.py gft\|ext "Variante\|..." Störungen Schritt` → `ergebnisse/x40_*.json` |
| `x41.py` | **Endbewertung 6.20** gegen 6.10 (Ertrag/Sicher, Grid mit und ohne N1800, `GridNurLive`), Wächter wie im EA nur über die letzten 600 Tage; 16 Störungen, Startjahre, Streuung → `ergebnisse/x41_*.json` |
| `mk_proxy.py` | Ersatz der GFT-Exporte aus den Fremddaten 03.01.2022–31.12.2025 (Spread wie `gext`), wenn `../data/*.csv` fehlen |
| `t_port_grid.py` | **Abgleich EA ↔ Replikat** für das Grid: wörtliche Übertragung von `GridM5`/`GridKerze`/`GridRang`/`GridFadeOk` gegen `pgrid` für alle Fade-Signale 2006–2025 |
| `t_mq5.py` | statische Prüfung des EA (Klammern, Format-Argumente, Makros/Globale vor Verwendung, unbekannte Funktionen) |
| `t_window.py` | Reicht die Wächter-Historie des EA (600 Tage) mit Grid für die Mindestzahl 30? (nur N1800 nicht → `GridOhne`) |
| **Build 6.30 (Trefferquote)** | |
| `eng7.py` | Kontomotor v7 = eng6 plus Teilgewinn/Einstand/Ziel je Noise-Teil (`nz_tp1r`, `nz_tp1f`, `nz_be`, `nz_tp`), T1 für RSI21 und Noise erst ab der Kerze nach dem Einstieg, Fade-T1 wahlweise als Anteil des Zielwegs (`tp1r` < 0); Noise-Teilernte zählt zum Trade (wie der Serien-Stopp im EA) |
| `t_eng7.py` | Prüfung: eng7 mit Voreinstellungen = eng6 (bis auf die Noise-Teilernte) |
| `pg_wr.py` | Signal-Ebene der Fades: Trefferquote und R je Signal mit Teilgewinn, Einstand, näherem Ziel (Perioden 2006–2025) |
| `x42.py` | **Konto-Screening 6.30**: Einstand/Teilgewinn/Ziel für Fades, RSI21, Noise und Kombinationen → `ergebnisse/x42_gft.json` |
| `x43.py` | **Endbewertung 6.30** gegen 6.20 (16 Störungen, Startjahre, Streuung inkl. Trefferquote) → `ergebnisse/x43_*.json` |
| `t_port_630.py` | **Abgleich EA ↔ Replikat** für 6.30: wörtliche Übertragung von `FadeTeilgewinn`/`EinstandSetzen`/`NzEinstand` gegen die Replikat-Logik auf echten Signalen |
| `ergebnisse/*.json` | Ergebnisse (große Scan-Raster nicht im Repo, mit `scan6_run*.py` neu erzeugbar) |

## Ablauf

```
pip install numpy pandas numba
python prep5.py && python sig5.py          # GFT-Daten -> cache/
python sig_ext.py                          # Fremddaten -> cache/ (braucht ../extdata/*.csv)
python x39.py gft                          # Endbewertung 6.10 (wie der EA) GFT 2022-26 (4 Prozesse, ~10 min)
python x39.py ext                          # Fremddaten 2006-21
# Build 6.20 (Probability Grid); ohne GFT-Exporte vorher: python mk_proxy.py (Ersatz 2022-2025)
python pg_scan.py                          # Vorstudie: Parameter-Raster der Grid-Regeln (Signal-Ebene)
python x40.py gft "6.10 Ertrag|E S M5 L15 s70" 16 1   # Konto, 16 Stoerungen, jeden Handelstag ein Konto
python x40.py ext "6.10 Ertrag|E S M5 L15 s70" 4      # Fremddaten 2006-21
python x41.py gft                          # Endbewertung 6.20 gegen 6.10 (GFT-Daten bzw. Ersatz)
python x41.py ext                          # dasselbe auf den Fremddaten 2006-21
python t_port_grid.py 5 15 1000 0.70 0     # Abgleich EA <-> Replikat (Grid)
# Build 6.30 (Trefferquote)
python pg_wr.py                            # Signal-Ebene der Fades (Teilgewinn, Einstand)
python x42.py gft all 8 2                  # Konto-Screening (8 Stoerungen, jeder 2. Tag)
python x43.py gft && python x43.py ext     # Endbewertung 6.30 gegen 6.20
python t_eng7.py && python t_port_630.py   # Pruefungen
python t_mq5.py                            # statische Pruefung des EA
```

## Konventionen

Wie Replikat v5 (Einstieg am Open der nächsten M5-Kerze, Long zum Ask, Stop vor Ziel in derselben Kerze,
strenge Lesart der Floating-Regel, Auszahlungsregeln von GFT). Zusätzlich für die Fades: Ziel frühestens ab
der zweiten Kerze (130-s-Regel), Zeit-Ausstieg am Open der ersten Kerze ab der Ausstiegszeit, Kommission
Gold 5 $/Lot. Fremddaten: Spread proportional zum Kurs (Stand 2022–26).

## Grenzen

- Die Fades wurden auf 2022–2026 **gesucht** (viele Varianten). In- und Out-of-Sample-Hälfte sind beide
  positiv, aber auf 2006–2021 verlieren dieselben Regeln. Der Regime-Wächter begrenzt diese Verluste, er
  beseitigt sie nicht.
- Kein Tick-Replay, keine News-Sperre im Nachbau, NAS-Datenloch 2024.
- Absolute Zahlen sind Schätzungen. Belastbar ist der Vergleich der Varianten unter gleichen Annahmen.
