# DEADBAND V8 – Build 8.00 „Staffel“

**Auch genannt:** V8, 8.00, „neues Konzept“, Staffel
**Status:** gebaut 04.10.2026, gepusht (Commit 9c91c1b, Branch claude/blissful-pasteur-23wlt0), **nicht kompiliert**, MT5-Tester steht aus.

## Was es ist
Aus 7.10 (Fades + RSI21 + Noise + Spike S0830) mit zwei neuen Sondermodulen und neuer Pufferkurve.
Entstehung: ~25 YouTube-Strategien einzeln unter GFT-Regeln im Replikat bewertet (alte Module aus), GFT-Handhabung je Strom angepasst, dann kombiniert.
Ergebnis: allein schlägt keine neue Strategie den Fade-Kern (bestes reines Neu-Portfolio 6,73 Ausz./J ohne Pleiten); in Kombination +22 % Auszahlungen.

## Module (neu)
- **LW** (typ 2, `LwKerze`, Replikat `n8sig.gen_lw`): NAS, Open 9:30 ± `LwK` 0,4 × Vortages-Range 9:30–16:00 (`LwSitzungMin` 390); Signal bis `LwEndeNY` 900; Einstieg Open nach Schluss jenseits; Stop Mitte Open/Einstieg; `LwZielR` 0; Ausstieg `LwAusstiegNY` 960; `LwRichtung` 0; `LwRiskPct` 0,5; `LwMinPuffer` 4,0.
  Signal: PF 1,55 (22–23) / 1,59 (24–25) / 1,20 (2005–21, 3304 Trades); Schlupf 4 Pkt/Seite → PF 1,24; Stop median 51 Pkt.
- **XA** (typ 3, `AsiaKerze`, Replikat `n8sig.gen_hold`): XAU Long `AsiaEinNY` −360 (18:00) → `AsiaAusNY` 180 (3:00), Trend 288 M5, Stop 0,6 ATR, Ziel 1 R, `AsiaRiskPct` 0,75.
- Technik: `MAXFADE` 13, Felder `typ/riskPct/minBuf/lw*` in FadeDef, `SonderAnlegen`, `SonderVirtuell`; Sondermodule ohne Portfolio-Wächter/Grid; Ziel 0 = kein Ziel in `FadeLive`/`FadeVerwalten`; Magic LW 61, XA 62 (Standardliste).

## Zahlen (Replikat eng6, rollierende 10k-Konten)
| | 7.10 | 8.00 |
|---|---|---|
| Ausz./J 2022–25 | 11,00 | 13,37 |
| netto $/J | 2008 | 2771 |
| Ø Auszahlung | 235 | 267 |
| Zyklus (Tage) | 30,0 | 25,0 |
| gültige Tage/J | 65,7 | 85,0 |
| 2022–23 / 2024–25 | 12,57 / 7,78 | 16,54 / 11,87 |
| 2006–21 Ausz./netto/Pleiten | 2,70 / 463 / 0 | 3,66 / 713 / 0 |

Pufferkurven-Plateau (mit LW 0,5 % ab 4 %, XA): 3/1/0,1 → 14,01 (2006–21: 0,001 Pleiten); 3,5/1,25/0,1 → 13,37 (gewählt, 0 Pleiten überall); 4/1,5/0,1 → 13,17.
Alle Pleiten in Tests waren Brüche des nachlaufenden 6 %-Bodens.

## Verworfen (nicht wiederholen)
ORB 5/15 min (+Mittelpunkt), 9:30-Kerze, Silver Bullet/Judas/Turtle Soup, Gold-IB-Rücklauf, Magic Hours, Gao-Momentum, EMA-/VWAP-Pullback, Vortages-Ausbruch/-Sweep, Bollinger, Turn of Month, Gap-Fade, VWAP-Fade, Wochen-Eröffnung, Makro-Tag-Filter, Vola-Perzentil, Spike-Fade zu anderen Zeiten.
Robust, aber nicht übernommen: Connors RSI(2) NAS, NAS-Eröffnungsmomentum (Pleiten/Überschneidung).

## Replikat-Dateien
`DEADBAND/Replikat_v6/`: n8sig.py, n8_scan.py, n8_robust.py, n8_detail.py, n8_konto.py, n8_gft710.py, n8_port.py (Sätze a–f), n8_ext.py; eng6.py (NG 32, GP-Spalte minbuf), evl6.py (Pleiten nach Art); Ergebnisse `ergebnisse/n8_*.json(.gz)`.

## Offene Punkte
- Kompilieren + MT5-Tester (Prüfplan im Bericht Abschnitt 7).
- Kontoerkenner und Anpasser (Prompt `DEADBAND/PROMPT_NEUE_SITZUNG.md`).
