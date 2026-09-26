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
| **Build 6.40 (Auszahlungstakt)** | |
| `eng8.py` | Kontomotor v8 = eng7 plus Schutz gültiger Tage (`vp_on`: 1 Risiko begrenzt, 2 keine Einstiege nach gültigem Tag, **3** = 2, aber nur solange dem Zyklus noch gültige Tage fehlen, 4 = 1 ebenso), Abschluss-Ernte ganz oder Rest auf Einstand (`bank_full`, `bank_be`), Tages-Diagnose (Tagesergebnis < 0 / 0–25 / 25–50,50 $ / gültig, verlorene gültige Tage, Wartetage, Tage ohne Trade) und kleinster Abstand zum Boden je Konto (`minbuf`) |
| `t_eng8.py` | Prüfung: eng8 mit Voreinstellungen = eng7 (alle Zähler, Trades, Ereignisse) |
| `evl8.py` | Bewertung v8: wie evl6, zusätzlich Tage je Auszahlung, Lücken zwischen Auszahlungen, was die Auszahlung zuletzt aufhielt (gültige Tage / Mindestgewinn / 10-Tage-Frist), Tages-Diagnose, Abstand zum Boden (Anteil Konten < 100 $ / < 200 $) |
| `pg_guard.py` | Regime-Wächter der Fades: Signal-Studie (Modul- gegen Portfolio-Wächter, 2006–13 / 2014–21 / 2022–25), `known_time` (Zeitpunkt, zu dem der EA ein virtuelles Ergebnis kennt), `port_live_ea` (Portfolio-Wächter wie im EA), `blocks_port`/`blocks_multi` (Fade-Blöcke für den Kontomotor) |
| `x44.py` | **Konto-Screening 6.40**: Mindestgewinn, Abschluss-Ernte, Schutz gültiger Tage, Fade-Teilgewinn, Risiko, Wächter-Varianten (`P<N>/<PF>`, zusammengesetzt `M:...`), Pufferkurve, Sicher → `ergebnisse/x44_*.json` |
| `x45.py` | Zwischenbewertung (16 Störungen) der ersten 6.40-Kandidaten ohne stärkere Pufferkurve → `ergebnisse/x45_*.json` |
| `x47.py` | **Wächter-Formen und Pufferkurven** im Vergleich (Abstand zum Boden): je Modul, Portfolio, zusammengesetzt (UND/ODER), Pufferkurven 4/1,5/0,3 bis 5/3/0,2; Screening mit 8 Störungen → `ergebnisse/x47_gft.json`, `x47_ext.json`, `x47_gft_spread06.json` (Ersatz mit Spreads ×0,6); Auswahl der Kurve mit 16 Störungen → `x47_gft_16.json`, `x47_gft_spread06_16.json` |
| `nb_diag.py` | Beinahe-Busts im Detail: kleinster Abstand zum Boden je Konto und Störung, Monat des tiefsten Stands (Episode Februar/März 2025) |
| `x46.py` | **Endbewertung 6.40** gegen 6.30 (16 Störungen, Startjahre, Streuung, Abstand zum Boden, Pufferkurven, Nachbarn, Wartezeit der Auszahlung, Sicher) → `ergebnisse/x46_*.json`, mit engeren Spreads `x46_gft_spread06.json` |
| `mk_proxy.py` | GFT-Ersatz aus Fremddaten (seit 6.40 mit `SPREAD_FAKTOR`, z. B. 0,6 = GFT-nahe Spreads; nur in einer Kopie des Ordners) |
| `t_port_640.py` | **Abgleich EA ↔ Replikat** für 6.40: Zeitpunkt der virtuellen Ergebnisse (`FadeKerze`/`FadeVirtSchluss`), Portfolio-Wächter (`FadePortfolioPF`/`FadeWaechterOk`), Schutz gültiger Tage → `ergebnisse/t_port_640.txt` |
| `t_set.py` | Prüfung: Voreinstellungen des EA = Echtbetrieb-Set (bzw. Abweichungen eines anderen Sets mit `--diff`) |
| **Build 6.50 (Netto)** | |
| `eng9.py` | Kontomotor v9 = eng8 plus Schutz gueltiger Tage je Modul (`vp_mods`: 1 DEADBAND, 2 RSI21, 4 Noise, 8 Fades; `vpx` je Fade-Strom = ausgenommen), RSI21 nur vor `vp_r21_to` NY geschuetzt, Regime-Schalter `vp_r21_reg` (RSI21 frei nur bei live Fade-Portfolio-Waechter, Maske `r21["reg"]`), weitere Schutzformen (`vp_on` 5 enger Stop, 6 Kopfraum >= `vp_k` x Risiko, 7 Groesse x `vp_k`), Trade-Protokoll mit Einstiegs-Zustand (Spalten 4-7: nach gueltigem Tag, Kopfraum, RSI21-Zeitebene, Einstiegsrisiko) |
| `t_eng9.py` | Pruefung: eng9 mit Voreinstellungen = eng8 (alle Zaehler, Trades, Ereignisse; auch Sperre je Modul mit allen Bits) |
| `evl9.py` | Bewertung v9 = evl8 plus Ergebnis der Trades nach gueltigem Tag je Modul (`pv`) |
| `x48.py` | **Konto-Screening 6.50**: Schutz je Modul, Schutzformen, freie Fade-Module, Fade-/RSI21-/Noise-Risiko, RSI21-Uhrzeit, Rueckgangs- und Regime-Schalter, Zerlegung, Sicher; `r21_regime` (Portfolio-Waechter zur RSI21-Einstiegszeit); `X48_SEED0` = anderer Stoerungs-Satz -> `ergebnisse/x48_*.json` |
| `pv_ana.py`, `r21_hour.py`, `bust_ana.py`, `perseed.py` | Diagnosen: Trades nach gueltigem Tag (gleicher Tag / spaeter geschlossen, Tag gekippt), alle RSI21-Trades nach Einstiegsstunde, Busts der Fremddaten nach Monat, 6.40 gegen 6.50 paarweise je Stoerung |
| `x49.py` | **Endbewertung 6.50** gegen 6.40 (16 Stoerungen, Startjahre, Streuung, Abstand zum Boden, Zerlegung, Sicher) -> `ergebnisse/x49_*.json`, GFT-nah `x49_gft_spread06.json` |
| `x50.py` | 6.40/6.50 auf einem **400k-Konto** (Startsaldo 400 000 $, Mindestauszahlung fest in $, Varianten Mindestgewinn 1,3125 %, Fade-Risiko 0,75 %, RSI21 geschuetzt; Netto ohne Neukauf; `evl9.NEAR_SCALE` fuer die Schwellen 1 %/2 %) -> `ergebnisse/x50_*.json` |
| `t_port_650.py` | **Abgleich EA <-> Replikat** fuer 6.50: Voreinstellungen, Quelltext-Stellen, Entscheidung je Modul, Fade-Regime fuer RSI21 (FadeRegimeLive gegen `r21_regime`) -> `ergebnisse/t_port_650.txt` |
| **Build 6.60 (Zukunft)** | |
| `PROTOKOLL_660.md` | **Pruefprotokoll, vor den Tests festgelegt** (Annahmekriterien K-a bis K-g: Walk-Forward 2022-23 -> 2024-25, Sicherheit, paarweise, Plateau, Stress) |
| `eng10.py` | Kontomotor v10 = eng9 plus Groesse fuer den gueltigen Tag (`sv_on`, `sv_cap`), Noise short (`nz_short`, `nz_s_risk`), 24 Stroeme, Trade-Protokoll mit 10 Spalten |
| `t_eng10.py` | Pruefung: eng10 mit Voreinstellungen = eng9 (45 Konten, Trades und Ereignisse identisch) |
| `evl10.py` | Bewertung v10 (rollierende Konten, Stoerungen, Startjahre, Werte je Stoerung fuer den paarweisen Vergleich, Abstand zum Boden) |
| `x60.py` | **Konto-Screening 6.60** (Basis 6.50): Groesse fuer den gueltigen Tag, Pufferkurven, Noise short, N1330/N1300-Risiko, DEADBAND, Boden zum Tagesschluss, Zerlegung von 6.50, Kandidaten 6.60a/6.60b, Sicher -> `ergebnisse/x60_gft.json` (GFT-nah `x60_gft_spread06.json`) |
| `x61.py` | **Endbewertung 6.60** (6.40, 6.50, 6.60a, 6.60b; 16 Stoerungen, jeder Handelstag bzw. jeder 3. Tag auf den Fremddaten); `ABSCHLAG=0.2` = Stresstest (20 % der Fade-Gewinner entfernt, auch fuer Waechter und RSI21-Regime) -> `ergebnisse/x61_*.json` |
| `mk_proxy2026.py`, `x60f.py` | **Zukunftstest 2026**: GFT-Ersatz bis 08/2026 (NAS100 ab 2025 aus Dukascopy-Ticks, Gold bis 02.09.2026; nur in einer Ordnerkopie), Konten ab 02.01.2026 mit 100 bzw. 60 Handelstagen und durchgehendes Konto ab 2025 -> `ergebnisse/x60f_2026.json` (GFT-nah `x60f_2026_spread06.json`) |
| `a60_sig.py`, `a60_jahr.py`, `a60_drag.py`, `a60_stufen.py`, `a60_stufen2.py`, `a60_fak.py` | Diagnosen: Fade-Signale je Periode / Trend / gespiegelt / Zielweite, Konto je Startjahr und Modul, Konto gegen virtuelles Signal, Signal -> Filter -> Waechter -> Konto, ausgelassene Signale, Anteil verkleinerter Trades |
| `a60_spx.py`, `a60_schock.py`, `a60_nzs.py` | Kandidaten auf Signal-Ebene: NAS-Fades auf US500 (K2), Schocktag-Filter (K3), Noise short und Gold-Noise (K6) -> `ergebnisse/a60_*.txt` |
| `a60_warn.py` | Regime-Meldungen des EA rueckwirkend (Fruehwarnung, Abschaltung, wieder live) 2006-2025 bzw. bis 08/2026 in der Ordnerkopie -> `ergebnisse/a60_warn.txt` |
| `x62.py`, `a67_kons.py` | **Konsistenzregel 15 %** (Instant GOAT/HERO, Bericht 6.60 Anhang B): eng10 `cons_pct` (Auszahlung erst bei bestem Tag < `cons_pct` - `cons_res` % des Gewinns der Periode), `cons_cap` 1/2 = Deckel ab bestem Tag bzw. nach gueltigem Tag, Kennzahl `net_open` (inkl. am Ende nicht ausgezahltem Gewinn); a67: bester Tag je Auszahlungsperiode heute -> `ergebnisse/x62_*.json`, `a67_kons.txt` |
| `t_port_660.py` | **Abgleich EA <-> Replikat** fuer 6.60: Voreinstellungen = `6.60b`, Pruefungen 2-4 aus `t_port_650`, Regime-Meldungen ohne Einfluss auf den Handel -> `ergebnisse/t_port_660.txt` |
| **Build 6.70 (Regime)** | |
| `PROTOKOLL_670.md` | **Pruefprotokoll, vor den Tests festgelegt** (Kriterien K-a bis K-g, Kandidaten Z1-Z6; Nachtrag 1 vor Runde 2: Z9-Z11; Nachtrag 2 vor Runde 3: Z12) |
| `mk_eng11.py`, `eng11.py` | Kontomotor v11 = eng10 plus Ziel fuer den gueltigen Tag mit Gewinnsicherung (`ext_on`, `ext_lock`, `ext_max`, `ext_margin`), Tagessperre der Fades je Symbol (`fsym_block`), Noise-Tagespause (`nz_maxloss`), Regime-Groesse fuer RSI21/Noise (`reg_mult` mit `r21["reg"]`/`nz["reg"]`), Noise mit einer Position (`nz_q0`), Trade-Protokoll Spalte 10 = Ausstiegszeit; `eng11.py` wird mit `mk_eng11.py` aus `eng10.py` erzeugt |
| `t_eng11.py` | Pruefung: eng11 mit Voreinstellungen = eng10 (45 Konten, alle Zaehler, Trades, Ereignisse); jeder neue Schalter wirkt |
| `evl11.py` | Bewertung v11 = evl10 plus Zaehler der neuen Schalter und Verlustserien je Position (MT5-Zaehlung: `s5p`, `s6p`, `mxp`) |
| `x70.py` | **Screening und Endbewertung 6.70** (Basis 6.60; Varianten in `VAR`, `nz_regime` = Fade-Regime je Noise-Pruefung; `ABSCHLAG=0.2` = Stresstest) -> `ergebnisse/x70_*.json` (GFT-nah in der Ordnerkopie: `x70_gft_spread06.json`) |
| `x70f.py` | Zukunftstest 2026 mit eng11 (Ordnerkopie wie x60f) -> `ergebnisse/x70f_2026.json`, `x70f_2026_spread06.json` |
| `a70_diag.py`, `a70_verl.py`, `a70_sig.py`, `a70_bust.py`, `a70_bustmod.py` | Diagnosen: Verlustserien nach Modul und knapp verfehlte Tage, verlorene gueltige Tage und Gewinne an schon gueltigen Tagen, Z2 auf Signal-Ebene je Periode, Busts der Fremddaten nach Monat bzw. Modul |
| `mk_ea670.py`, `mk_sets670.py` | Aenderungen am EA (6.60 -> 6.70) als Textersetzungen mit eindeutigen Ankern; Presets 6.70 aus den 6.60-Sets |
| `t_port_670.py` | **Abgleich EA <-> Replikat** fuer 6.70: Voreinstellungen/Presets, Pruefungen aus 6.50/6.60, Quelltext-Stellen der Optionen, Fade-Regime zur Noise-Pruefzeit gegen `x70.nz_regime`, Tagessperre auf dem Trade-Protokoll, Laenge der Push-Texte -> `ergebnisse/t_port_670.txt` |
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
# Build 6.40 (Auszahlungstakt)
python pg_guard.py                         # Signal-Studie: Regime-Waechter je Modul gegen Portfolio
python x44.py gft "6.30 Ertrag|MP min|MP min B5" 8 2   # Konto-Screening (Varianten siehe VAR in x44.py)
python x47.py gft all 8 2 ergebnisse/x47_gft.json   # Waechter-Formen und Pufferkurven (Abstand zum Boden)
python x47.py ext all 8 6 ergebnisse/x47_ext.json
python x47.py gft "Q5 Port200>1.15, Kurve 5/2.5/0.2|R0 6.30 Ertrag" 16 2 ergebnisse/x47_gft_16.json   # Auswahl der Kurve
python nb_diag.py gft "6.40 Ertrag" 16 1 nb.json   # Beinahe-Busts je Stoerung und Monat
python x46.py gft && python x46.py ext     # Endbewertung 6.40 gegen 6.30
# engere, GFT-nahe Spreads: Ordner DEADBAND kopieren, in der Kopie (Replikat_v6):
#   SPREAD_FAKTOR=0.6 python mk_proxy.py && python prep5.py && python sig5.py
#   python x47.py gft all 8 2 x47_gft_spread06.json && X46_OUT=. python x46.py gft   (-> ergebnisse/x46_gft_spread06.json)
python t_eng8.py && python t_port_640.py   # Pruefungen (eng8 = eng7; EA <-> Replikat)
python t_set.py                            # Echtbetrieb-Set = Voreinstellungen des EA
# Build 6.50 (Netto)
python t_eng9.py                           # eng9 = eng8
python x48.py gft "6.40 Ertrag|6.40 VP0|VPM NZ+F" 8 2   # Screening (Varianten siehe VAR in x48.py); 16/48 Stoerungen fuer die Auswahl
python pv_ana.py "C50"                     # Trades nach gueltigem Tag je Modul
python x48.py ext "6.40 Ertrag|C50 R21 frei ab 13.0" 16 3   # Fremddaten (Bust-Risiko), bust_ana.py fuer die Episoden
python x49.py gft && python x49.py ext     # Endbewertung 6.50 gegen 6.40 (GFT-nah: in der Kopie mit X49_OUT=.)
python t_port_650.py && python t_set.py && python t_set.py ../DEADBAND_LIVE4_650_Sicher.set --diff
# Build 6.60 (Zukunft) - Kriterien vorab in PROTOKOLL_660.md
python t_eng10.py                          # eng10 = eng9
python x60.py gft all 8 2                  # Screening (Varianten siehe VAR in x60.py), GFT-nah in der Kopie mit X60_OUT=.
python a60_sig.py && python a60_spx.py && python a60_schock.py && python a60_nzs.py   # Signal-Ebene (braucht ../extdata/US500_ext_M5.csv)
python x61.py gft && python x61.py ext     # Endbewertung (GFT-nah: in der Kopie mit X61_OUT=.)
ABSCHLAG=0.2 python x61.py gft             # Stresstest
# Zukunftstest 2026: Ordner DEADBAND kopieren, in der Kopie (Replikat_v6):
#   pg_data.py: data_all(until="2026-09-03"); [SPREAD_FAKTOR=0.6] python mk_proxy2026.py   (-> ../data/, NAS ab 2025 Dukascopy)
#   ../extdata/NAS100_ext2026_M5.csv = NAS100_ext_M5.csv bis 31.12.2024 + ../data/NAS100.x_M5.csv ab 2025; gext.FILES["NAS"] darauf
#   python prep5.py && python sig5.py && python sig_ext.py && python x60f.py "6.40 Ertrag|6.50 Ertrag|6.60b" 100   (bzw. 60)
python a60_warn.py                         # Regime-Meldungen rueckwirkend (Vorgabe 1,25 wie der EA)
python t_port_660.py && python t_set.py && python t_set.py ../DEADBAND_LIVE4_660_Sicher.set --diff && python t_mq5.py
# Konsistenzregel 15 % (Instant GOAT/HERO): Kosten der Regel, passiv und mit Deckel
python x62.py gft "6.60|6.60 K15|6.60 K15 Tagesdeckel 1.0" 8 2 && python x62.py ext "6.60|6.60 K15|6.60 K15 Tagesdeckel 1.0" 16 3
ABSCHLAG=0.2 python x61.py gft "6.60 K15|6.60 K15 Tagesdeckel 1.0" && python a67_kons.py
# Build 6.70 (Regime) - Kriterien vorab in PROTOKOLL_670.md (Kursdaten: extdata/scripts/run_all.sh, mk_proxy.py, prep5/sig5/sig_ext)
python mk_eng11.py && python t_eng11.py    # eng11 aus eng10 erzeugen, eng11 = eng10
python a70_diag.py gft && python a70_verl.py gft   # Diagnosen der Basis
python x70.py gft all 8 2 && python x70.py ext all 16 3   # Screening (GFT-nah: Ordnerkopie mit SPREAD_FAKTOR=0.6 python mk_proxy.py ...)
python x70.py gft "6.60|Z2 Sperre 1|Z9 Regime-Groesse 0.5|Z10 Z9 + Z2" 16 1   # Endbewertung; ABSCHLAG=0.2 fuer den Stresstest
python a70_sig.py && python a70_bust.py "6.60|Z2 Sperre 1" 16 3   # Signal-Ebene und Busts der Fremddaten
# Zukunftstest 2026 in der Ordnerkopie (wie 6.60): python x70f.py "6.60|Z9 Regime-Groesse 0.5|Z10 Z9 + Z2" 100
python t_port_670.py && python t_set.py && python t_mq5.py   # EA <-> Replikat, Presets, statische Pruefung
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
- Der Zukunftstest 2026 (Build 6.60) hat die Wahl des Fade-Risikos mitbestimmt und ist damit fuer kuenftige Builds nicht
  mehr unberuehrt. Die NAS-Reihe 2025-26 (Dukascopy) ist verrauschter als die Broker-Daten (Datenbericht, Abschnitt 10).
- Build 6.70: Die Kandidaten, die an den Fades ansetzen, sind auf 2022-25 teilweise In-Sample (die Fades wurden auf 2022-26
  gesucht). Deshalb zaehlten Signal-Ebene, Startjahre und der (verbrauchte) Zukunftstest 2026 mit.
- Absolute Zahlen sind Schätzungen. Belastbar ist der Vergleich der Varianten unter gleichen Annahmen.
