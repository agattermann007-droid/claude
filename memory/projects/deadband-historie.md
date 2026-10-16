# DEADBAND – Build-Historie

Jeder Build trägt die Kopfblöcke aller Vorgänger (oben in der .mq5). Zahlen sind Replikat-Werte der jeweiligen Runde
(verschiedene Nachbauten – nur innerhalb einer Zeile vergleichbar).

| Build | Datum | Kern | Ort |
|---|---|---|---|
| 3.00 | 08.09.2026 | `DEADBAND_LIVE.mq5`, Demo-Test, Checkpoint 2 (Lernprojekt `MEMORY_DEADBAND-Code.md` im Drive) | Drive |
| 5.x–6.6x | 09.–26.09. | LIVE4: Fades + Portfolio-Wächter, Grid, RSI21, Noise, Auszahlungstakt, Pufferkurve, Sondertage | Branches `claude/*` (6.10 bold-allen, 6.20 festive-archimedes, 6.30 focused-fermat, 6.40 clever-mayer, 6.50 tender-shannon, 6.60 keen-gauss, 6.70 adoring-hamilton) |
| 6.70 / 6.80 / 6.81 | 26.09.–02.10. | Prop-Firm-Echtbetrieb, BelowStart 0,95, Tester-Prüfwerte („DEAD_VERSION_FINAL“) | Kopfblöcke in jeder späteren .mq5; Branch `claude/ecstatic-johnson-mlf4v8` (Dead_Version_Final mit Push-Check) **gesperrt, nicht übernehmen** |
| 7.00 | 02.10. | Firmenprofil (Größe/Boden je Firma), GFT = handelsgleich 6.81 | `DEADBAND/rollback_7.00/` auf `claude/blissful-pasteur-23wlt0` |
| 7.10 | 04.10. | + Spike-Fade S0830 | `DEADBAND/DEADBAND_V7.mq5` auf `claude/blissful-pasteur-23wlt0` |
| 8.00 | 04.10. | „Staffel“: + LW, + XA, Pufferkurve 3,5/1,25/0,1 | Bericht `DEADBAND/DEADBAND_V8_Bericht.md` auf `claude/blissful-pasteur-23wlt0` |
| **8.10** | 04.10. | + Kontoerkenner/Anpasser (neutral), + TD (Trend-Day NAS 14:00) – **Live-Stand** | `DEADBAND/V11/DEADBAND_V8.mq5` (auch Drive) |
| 9.00 | 14.10. | + SR (Sweep-Reclaim im Tick) + Konsistenzregel GOAT | – |
| 10.00 | 14.10. | V8 + SR 0,10 % (Premium, Konsistenz aus) | `DEADBAND/V11/DEADBAND_V10.mq5` |
| 11.00 | 15.10. | handelt wie 10.00; SR-Marken erweitert (19 Felder), Testschalter `V11TickFades`, `V11GoldPdf` | `DEADBAND/V11/` |
| **12.00** | 16.10. | + N1030 im Tick (`SRT1030`, 0,50 %) – **beste Version laut Nachbau v12, nicht kompiliert** | `DEADBAND/V12/` |

Nebenprojekte auf eigenen Branches: Intrabar-/Sidecar-Forschung auf Basis V8 (`claude/upbeat-maxwell-f7pmp0`),
Analyzer 3 (`claude/analyzer3-forschung`), Trade-Analyser mt5 (`claude/peaceful-lamport-9we47e`),
RSI21 EK (`claude/dazzling-goldberg-xgo0ij`), Replikat-Vergleich 3.00 ↔ 8.10 (`claude/nice-archimedes-5zut72`).

## Nachbauten (Replikat)
| Version | Ort | Bemerkung |
|---|---|---|
| v5/v6 (eng6) | `DEADBAND/Replikat_v5`, `Replikat_v6` | Stand 6.10 + generische Ströme, V8-Bewertung |
| v11 | `DEADBAND/V11/Replikat_v11/` | neu gebaut, M1, Schlupf ¼ Spread – **Noise-Fehler** (Kontozahlen überholt) |
| **v12** | `DEADBAND/V12/Replikat_v12/` | Fehler behoben, Daten 2010–26, Prüffenster 2011–15, Unabhängigkeitstest |
