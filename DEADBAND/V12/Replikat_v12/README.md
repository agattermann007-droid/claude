# Replikat v12 – Python-Nachbau von DEADBAND (M1, Kontoebene)

Fortsetzung von `Replikat_v11/` (README dort für Aufbau, Konventionen und Datenmängel). Neu in v12:

## 1. Zwei Fehler im Kontomotor behoben (`eng11.py`)

Beide betrafen nur den Nachbau, nicht den EA. Im EA wird jeder Tick bearbeitet, im Nachbau springt der Motor bei
flachem Konto zur nächsten Minute mit einem Signal. Dabei gingen zwei Dinge verloren:

1. **Noise-Prüfungen fielen aus.** Nach einer Noise-Prüfung (stündlich 10–15 Uhr NY) zeigte der Zeiger noch auf die
   gerade bearbeitete Minute. Die *folgende* Prüfung wurde beim Sprung übersehen, wenn keine anderen Signale
   dazwischen lagen. Folge: Noise handelte zu selten und zu spät, und **jeder zusätzliche Strom veränderte nebenbei
   den Noise-Strom** (mehr Signal-Minuten = mehr besuchte Prüfungen). Vergleiche „mit/ohne Strom X“ waren dadurch
   verzerrt.
2. **RSI21-Wiederaufnahme nach dem Wochenende** hing ebenfalls an der nächsten besuchten Minute. Jetzt läuft der
   Motor Minute für Minute, solange eine Wiederaufnahme aussteht.

Prüfung: `t12_engine_check.py` – ein abgeschalteter Dummy-Strom mit Signalen in jeder 7. Minute verändert kein
einziges von 521 Konten (vorher schon in Seed 0 ±1,7 Ausz./J).

Wirkung auf die Kennzahlen: V10 2024–25 (Seed 0) 7,17 → 8,14 Ausz./J. Alle Kontozahlen aus dem V11-Bericht sind
damit überholt; die Grundlinie ist in `ergebnisse/t12_base.log` neu gerechnet, alte Logs in `ergebnisse/alt_vor_fix/`.

## 2. Erweiterter Datensatz 2010–2026 und Prüffenster 2011–15

`prep_ext.py` setzt Gold aus OANDA M1 (Mid, 2010-01 bis 2016-08) und Dukascopy (ab 2016-09) zusammen; NAS wie bisher
(HistData ab 2010-11). Damit lassen sich ganze Konten mit Start 2011–2015 rechnen – ein drittes, unabhängiges
Prüffenster, in dem der Portfolio-Wächter die Fades fast nie live lässt (Regime „Fades aus“).

```
export OANDA_DIR=/home/user/data/oanda/pyfinancialdata/data/currencies/oanda/XAU_USD
python prep_ext.py                                                    # -> /home/user/work/npz_ext
NPZ_DIR=/home/user/work/npz_ext REP_CACHE=/home/user/work/cache_ext python prep11.py
```

Alle `t12_*.py` importieren zuerst `x12.py` (setzt `NPZ_DIR`, `REP_CACHE`, `REP_T_LO=2010-12-01`). Ab 2016-09 sind
die Kurse identisch zum Standardsatz; die Kennzahlen 2022–25 stimmen exakt überein, 2017–20 bis auf ±0,01 Ausz./J
(längere Historie des Portfolio-Wächters).

Fenster (`evl11.WIN5`): Auswahl 2022, 2023, Prüfung 2024-01 bis 2025-02, Prüfung 2017–20, **Prüfung 2011–15**.

## 3. Neue Bausteine

| Datei | Inhalt |
|---|---|
| `x12.py` | Pfade des erweiterten Satzes (vor allen anderen Modulen importieren) |
| `prep_ext.py` | Gold OANDA + Dukascopy zusammensetzen |
| `reg12.py` | Generatoren für das Regime „Fades aus“: ORB, Intraday-Momentum (IMOM), Ausbruch statt Fade, Gold-Trend-Ausbruch; `gate()` = nur bei Fades live/aus |
| `eng11.py` | + `r21_regfak` (RSI21 × Faktor bei Fades aus, wie EA `RegimeGroesse`), + Stromfeld `noser` (Trades zählen nicht für den Serien-Stopp), + die zwei Korrekturen oben |
| `evl11.py` | + `WIN5`, + Kennzahl `gs` (Sperren durch den Schutz gültiger Tage) |
| `mk11.py` | Startzeit über `REP_T_LO` |
| `t12_base.py` | Grundlinie V8/V10, 5 Fenster, 32 gepaarte Störungen (`ergebnisse/base_v10_32.pkl`) |
| `t12_regime_scan.py` | 208 Kandidaten auf Stromebene, Regel vor dem Lauf festgelegt |
| `t12_acct.py` | Kandidaten auf Kontoebene (Stufe 1: 16 Seeds, 3 Fenster; Bestätigung: 32 Seeds, 5 Fenster) |
| `t12_sr.py`, `t12_sr_diag.py` | Diagnose SR 2024–25 (Stromebene je Marke, Modul-Bilanz, Serien-Stopps, Varianten) |
| `t12_tick.py` | Tick-Fades mit kleinerem Risiko / nur N1030, Bust-Ursachen |
| `t12_regsize.py` | Regime-Größe > 1 für bestehende Ströme |
| `t12_engine_check.py` | Unabhängigkeitstest des Motors |
| `t12_imom_diag.py` | IMOM im Konto (Modul-Ergebnis mit/ohne Abschluss-Ernte, Serienzähler) |
| `t12_tickbust.py` | Bust-Ursachen der Tick-Fades (2011–15: alle am 10.10.2013) |
| `t12_tick2.py` | Bestätigung N1030 im Tick: Risiko 0,40/0,60, Puffer 0,2/0,4, Gegenprobe M5 0,50 % |
| `t12_srrisk.py` | SR-Risiko 0,05–0,30 % mit korrigiertem Motor |
| `t12_final.py` | Endauswertung V10 gegen V12 (16 Seeds je Fenster/Startjahr, 32 Seeds gepaart, ohne Schlupf) |
| `t12_bericht.py` | setzt die Tabellen aus `t12_final` in den Bericht ein |

## 4. Ergebnis Build 12.00

Übernommen: **N1030 im Tick mit 0,50 %** (`cand11.tick_fade("N1030")`, Stromnummer von N1030, `tpdelay` 4, Risiko 0,50).
Gepaart gegen V10, 32 Störungen: 2022 +0,66 ± 0,12, 2023 +1,30 ± 0,14, 2024–25 −0,07 ± 0,17, 2017–20 +0,23 ± 0,03,
2011–15 −0,01 Ausz./J, 0 Busts. Ohne Schlupf etwa halber Vorteil, 2024–25 −0,38 ± 0,24. Alles Weitere im Bericht
`DEADBAND_V12_Bericht.md`.

Laufzeit: 32 Störungen × 5 Fenster (≈ 630 Konten je Störung) ≈ 4 min auf 4 Kernen.
