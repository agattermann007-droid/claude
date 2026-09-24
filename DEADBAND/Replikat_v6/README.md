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
| `t_port.py` | **Abgleich EA ↔ Replikat**: wörtliche Übertragung von `FadeKerze` (MQL5) gegen `scan6.gen_fade` + `gsig.simulate` |
| `ergebnisse/*.json` | Ergebnisse (große Scan-Raster nicht im Repo, mit `scan6_run*.py` neu erzeugbar) |

## Ablauf

```
pip install numpy pandas numba
python prep5.py && python sig5.py          # GFT-Daten -> cache/
python sig_ext.py                          # Fremddaten -> cache/ (braucht ../extdata/*.csv)
python x35.py gft                          # Endbewertung 6.00 GFT 2022-26 (4 Prozesse, ~10 min)
python x35.py ext                          # Fremddaten 2006-21
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
