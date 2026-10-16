# DEADBAND V12 – Build 12.00 (beste Version, Stand 16.10.2026)

**Auch genannt:** V12, 12.00, „N1030 im Tick“
**Status:** gebaut 16.10.2026, gepusht (Branch `claude/deadband-v11`, Commit 485b543, Ordner `DEADBAND/V12/`),
**nicht kompiliert**, nur statisch geprüft (ASCII, Klammern, 389 Format-Strings). MT5-Tester steht aus.

## Was es ist
V11 (= Handel wie V10: V8 + SR) plus **N1030 im Tick**: Modul `SRT1030` über `SrEintrag` (Range 10:30–12:30 NY,
Fenster bis 13:30, Einstieg im Tick beim Rücklauf in die Range nach Docht unter das Tief, Stop 0,3 × Range hinter dem
Extrem, Ziel Range-Mitte ab 130 s, Ausstieg 15:30, Range ≤ 0,6 ATR, Durchbruch ab 0,6 ATR, nur bei live
Portfolio-Wächter). Risiko `V12TickN1030Risk` 0,50 %. Das M5-Modul N1030 rechnet nur virtuell (Wächter gleich).
Eingaben: `V12TickN1030` (true), `V12TickN1030Risk` (0,50). Wird ignoriert, wenn `V11TickFades` an ist.
Rückfall: `V12TickN1030=false` = handelsgleich 11.00. Module 19 von `MAXFADE` 22.

## Zahlen (Replikat v12, 32 gepaarte Störungen, Differenz V12 − V11)
| Kontostart | Ausz./J | $/J |
|---|---|---|
| 2022 (Auswahl) | +0,66 ± 0,12 | +112 ± 35 |
| 2023 | +1,30 ± 0,14 | +235 ± 44 |
| 2024–25 | −0,07 ± 0,17 | +21 ± 41 |
| 2017–20 | +0,23 ± 0,03 | +61 ± 8 |
| 2011–15 | −0,01 ± 0,00 | −1 ± 1 |
0 Busts. Plateau: Risiko 0,40–0,60 %, Stop-Puffer 0,2–0,4 × Range (alle besser bzw. gleich). Gegenprobe N1030 auf
M5 mit 0,50 %: ohne Wirkung → Vorteil kommt vom Tick-Einstieg. 0,75 % → 12 Busts (2011–15).
Ohne Schlupf: 2022 +0,33, 2023 +0,44, 2024–25 −0,38 ± 0,24, 2017–20 +0,20 → Vorteil hängt teils am Schlupf-Modell.
Je Startjahr besser 2018, 2019, 2022, 2023; gleich 2011–17, 2020 (Fades nicht live); leicht schlechter 2024–25.

## Grundlinie (korrigierter Nachbau, 32 Seeds, Ausz./J · $/J)
| Start | V8 | V10 = V11 | V12 |
|---|---|---|---|
| 2022 | 9,70 · 1.697 | 12,27 · 2.409 | 12,93 · 2.522 |
| 2023 | 11,63 · 2.383 | 13,20 · 2.576 | 14,49 · 2.811 |
| 2024–25 | 7,54 · 1.563 | 7,68 · 1.656 | 7,61 · 1.676 |
| 2017–20 | 4,85 · 926 | 5,57 · 1.054 | 5,79 · 1.116 |
| 2011–15 | 3,09 · 597 | 3,71 · 681 | 3,71 · 681 |
Ohne Schlupf V10: 14,4 / 16,3 / 9,9 / 6,9 / 4,8 Ausz./J. Ø Auszahlung 237–279 $, erste Auszahlung Median 15–30 Tage,
2011–15 ~14 % Konto-Jahre ohne Auszahlung.

## Wichtige Befunde dieser Runde
- **Nachbau-Fehler (v11) behoben:** Noise-Prüfungen fielen bei flachem Konto aus, wenn keine anderen Signale
  dazwischen lagen; RSI21-Wiederaufnahme hing an fremden Signal-Minuten. Jeder zusätzliche Strom veränderte dadurch
  nebenbei Noise. Alle Kontozahlen aus dem V11-Bericht sind überholt. Test: `t12_engine_check.py` (0/521 Konten).
- **SR hilft auch 2024–25** (V8 − V10: −0,14 ± 0,21 Ausz./J, −92 ± 43 $/J) – V11-Befund war Artefakt.
- SR verdoppelt die Serien-Stopps (61 statt 31/J), die NAS-Long-Fades verlieren ~280 $/J, SR selbst +239 $/J.
  Die Serien-Stopps schützen (ohne sie schlechter). SR-Risiko > 0,10 % → Busts in 2011–15.
- **Regime „Fades aus“:** Wächter live 2011–12/2014–18/2020–21 0 %, 2013 44 %, 2019 42 %, 2022 53 %, ab 2023 98–100 %.
  Engpass dort = gültige Tage (2011–15 ~25/J, 2017–20 ~37/J, 2022 ~74/J). Ströme mit ~35 % Treffern und engem Stop
  (IMOM, ORB) verdienen zwar, machen aber das Konto schlechter (Verlusttage, Serien-Stopps, Busts am trailenden Boden).
- Tick-Fades N1030+N1100: Busts in zwei Episoden (10.10.2013, 21.07.2025) – viele Konten laufen gemeinsam hinein.

## Replikat v12 (`DEADBAND/V12/Replikat_v12/`)
Python/numba, M1. Erweiterter Datensatz: Gold OANDA 2010-01–2016-08 + Dukascopy, NAS HistData ab 2010-11
(`prep_ext.py`, `x12.py` setzt `NPZ_DIR`/`REP_CACHE`/`REP_T_LO`). Fenster `evl11.WIN5`. Wichtige Skripte:
`t12_base.py` (Grundlinie → `base_v10_32.pkl`), `t12_final.py` (V10 gegen V12), `t12_engine_check.py`,
`t12_regime_scan.py`, `t12_acct.py`, `t12_sr*.py`, `t12_tick*.py`, `t12_srrisk.py`. Motor `eng11.py` neu:
`r21_regfak`, Stromfeld `noser`. Laufzeit 32 Seeds × 5 Fenster ≈ 4 min (4 Kerne).
Abgleich Seed 0 (erweitert, korrigiert): V10 2022 11,86 · 2024–25 8,14 · 2017–20 5,78 · 2011–15 3,64.

## Build-Werkzeug (`DEADBAND/V12/build/`)
`patch_v12.py` (7 exakte Ersetzungen auf V11), `patch_lib.py`, `check_mq5.py`, `kopf_v12.py`/`.txt`, `V11_V12.diff`.
Neu bauen: `python patch_v12.py ../DEADBAND_V11.mq5 ../DEADBAND_V12.mq5 && python check_mq5.py ../DEADBAND_V12.mq5`.

## Tester-Checkliste (offen)
1. `V12TickN1030=false` = V11 handelsgleich. 2. V12 Voreinstellung gegen 1. (Einstiege `SRT1030`, Auszahlungen,
Kleinster Abstand zum Boden), mehrere Startdaten ab 2024, wenn möglich 2022–23. 3. `SrAktiv` false gegen true.
