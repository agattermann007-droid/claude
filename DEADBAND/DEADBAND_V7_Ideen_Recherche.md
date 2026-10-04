# DEADBAND V7 – Recherche: Wege, die Strategie zu verbessern (GFT bleibt)

Stand: 04.10.2026 · Grundlage: YouTube-/Web-Recherche, abgeglichen mit Replikat_v6 und den Köpfen 6.00–7.00.
**Nichts davon ist gemessen.** Die Kursdateien (GFT 2022–26, extdata 2006–21) liegen nicht im Repo, also konnte
hier kein Replikat laufen. Jede Idee ist als Kandidat für das nächste Prüfprotokoll gedacht (wie PROTOKOLL_670).

## 0. Wo der Hebel liegt

Laut Kopf 6.60 liegen 90 % der gültigen Tage knapp über der Schwelle (50–106 $), meist mit **einem** Fade-Treffer.
Engpass = Zahl der Tage mit >= 0,5 % realisiert. Eine Verbesserung muss also
- **mehr unabhängige Treffer-Chancen pro Tag** liefern (neue Zeitfenster, in denen heute nichts handelt), oder
- **schlechte Fade-Tage vorher erkennen** (Verluste, die gültige Tage und Puffer kosten).

Schon geprüft (nicht wiederholen): VWAP-Ausstieg und 30-min-Prüfung für Noise (`nz2.py`), Asia-/Vortages-Sweeps
(`scan6_run2.py`), Noise short, Gold-Noise, Trend- und Schocktag-Filter, gespiegelte Fades, Fade-Einstand.

## 1. NAS-Gap-Fade 9:30–10:00 NY (neues Modul, freies Zeitfenster) – Priorität 1

**Quelle:** Gap-Statistik NQ 2015–2025 (tradingstats.net, YouTube „The Truth About Gap Fills“):
kleine Gaps, die **innerhalb der Vortagesrange** öffnen, schließen ~70–78 %; Gaps außerhalb nur 8–47 %.
Timing NQ: 34 % schließen in der ersten 5-min-Kerze, 61 % bis 10:00 NY; danach ist 2/3 des Potenzials weg.
QuantifiedStrategies NQ-Gap (60 min Haltedauer): ~157 Trades/10 J, 64 % Treffer, PF > 2 vor Kosten.

**Warum es passt:** NAS hat zwischen 9:30 und 10:00 NY heute keine Einstiege (N0930 baut bis 12:30 seine Range,
Noise prüft ab 10:00). Ein Treffer mit Ziel ≈ 1 R bei 0,75 % Risiko macht den Tag allein gültig.

**Regeln zum Testen (Vorschlag, vorher festlegen):**
- Gap = Eröffnung 9:30 gegen Schluss 16:00 Vortag (NAS100-CFD, RTH-Kerzen).
- Nur wenn Eröffnung innerhalb Vortages-RTH-Range und |Gap| <= x × ATR14 D1 (Raster 0,15 / 0,25 / 0,35).
- Richtung zum Vortagesschluss; Einstieg Open der 9:35-Kerze (die 9:30-Kerze ist zu wild für die 1-%-Regel).
- Stop: Extrem der 9:30–9:35-Kerze + Puffer bzw. 1 × Gap jenseits der Eröffnung.
- Ziel: Vortagesschluss (voll) bzw. 50 % des Gaps; Zeit-Ausstieg 10:00 NY (Raster 10:00 / 10:30).
- Gap **aufwärts** = Short: muss vor der ersten Noise-Prüfung (10:00, nur Long) flach sein → Hedging-Sperre.

**GFT-Fallen:** Ziel erst nach 130 s setzen (Gewinne < 120 s werden gestrichen) – die schnellsten Fills gehen
damit verloren, ehrlich mitrechnen. 10:00-Termine (ISM, JOLTS, Konsumklima) liegen genau am Ausstieg → News-Sperre.
Regime-Wächter wie bei den Fades (virtuell mitrechnen, live nur bei PF > Schwelle).

## 2. Makro-Tag-Filter für Fades (FOMC / CPI / NFP) – Priorität 2

**Quelle:** ES/NQ-Backtest 01–06/2026: Fade- und Retest-Einstiege „degraded sharply on FOMC and NFP days“;
mehrere Prop-Firm-Videos: an diesen Tagen eher aussetzen.

**Warum es passt:** Die ±6-min-News-Sperre verhindert nur Einstiege *im* Fenster. Ein Fade, der **vor** dem
Termin eröffnet wurde, hält durch die Veröffentlichung:
- X0630 (Gold, Range 6:30–8:30, Handel ab 8:30) – mitten in CPI/NFP 8:30.
- N1330 / N1300 (NAS, Handel ab 14:30) – FOMC 14:00 + Pressekonferenz 14:30.

**Test:** feste Datumsliste FOMC/CPI/NFP 2006–2027 (wie `NZ_FREI`, weil der Tester keinen Kalender hat).
Varianten: a) betroffene Module an diesen Tagen aus, b) nur Einstiege, deren Haltefenster den Termin enthält.
Nicht dasselbe wie der verworfene Schocktag-Filter (der reagierte auf die Bewegung, dieser kennt den Termin vorher).
Kostet wenige Signale/Jahr (~8 FOMC, 12 CPI, 12 NFP) – also wenig Risiko für den Takt.

## 3. „Turtle Soup Plus One“ für die Fade-Module – Priorität 3

**Quelle:** Connors/Raschke, *Street Smarts* (1995); ICT „Turtle Soup“-Videos.

**Heute:** Schließt eine Kerze außerhalb der Range, ist der Tag für das Modul vorbei (`F[m].done = true`).
**Plus One:** Schließt die Kerze außerhalb, aber eine der nächsten 1–2 M5-Kerzen wieder innerhalb, ist das ein
Fehlausbruch mit *gefangenen* Ausbruchskäufern – Signal. Stop hinter dem Extrem inkl. Ausbruchskerzen (`exHi`/`exLo`
gibt es schon). Mehr Signale je Modul = mehr Chancen auf einen gültigen Tag.
Risiko: Trefferquote kann sinken; Grid-Filter (Regel S) muss mitlaufen. Kleine Code-Änderung in `FadeKerze`.

## 4. Vola-Perzentil als vorausschauender Regime-Faktor – Priorität 4

**Quelle:** Mean-Reversion-Regime-Videos/Artikel: Rückkehr zur Mitte bricht oberhalb des 80. Perzentils der
Volatilität zusammen; Empfehlung Größe −50 bis −70 % statt abschalten.

**Warum:** Der Portfolio-Wächter (PF200) ist nachlaufend – er braucht Monate. Fade-Risiko × Faktor, wenn das
ATR14-D1-Perzentil (z. B. 500 Tage) > 80 %. Prüfen vor allem auf den Fremddaten 2006–21 (dort verlieren die Fades).
Überschneidet sich teilweise mit dem verworfenen Trendfilter und der Pufferkurve – nur übernehmen, wenn Busts
2006–21 sinken, ohne 2022–26 Auszahlungen zu kosten.

## 5. Prüfvorschlag

Wie 6.70: Kriterien vorher festlegen, Auswahl nur auf 2022–23, Bestätigung 2024–25, Zukunftstest 2026,
Busts auf 2006–21, Konto-Replikat mit allen GFT-Regeln (eng6), danach MT5-Tester mit den 6.81-Prüfwerten
(kleinster Abstand zum Boden, Bodenbrüche). Reihenfolge: 2 (billig, nur Datumsliste) → 1 (neues Modul) → 3 → 4.

## Quellen

- YouTube: [The Truth About Gap Fills](https://www.youtube.com/watch?v=WGXyqybDhcI)
- YouTube: [Intraday Momentum Trading Strategy Explained: The "Noise Area" System](https://www.youtube.com/watch?v=NEE_jHYgCx8)
- YouTube: [Backtesting ICT's Turtle Soup Strategy with Gold Futures](https://www.youtube.com/watch?v=dqHddXL1TZs)
- YouTube: [The One Strategy You Need for Every FOMC Day!](https://www.youtube.com/watch?v=Tpdc4AREalE)
- [Gap Fill Strategy: 2,791 Days of NQ Data](https://tradingstats.net/gap-fill-strategy/) · [When Do Gaps Fill? ES & NQ](https://tradingstats.net/when-do-gaps-fill/)
- [NQ Futures Gap Day Trading Strategy (QuantifiedStrategies)](https://quantifiedstrategies.substack.com/p/nq-futures-gap-day-trading-strategy)
- [Nasdaq-100 Pre-Market Range Containment / Failed Breakouts (VT Markets)](https://vtmarkets.com/en-asia/live-updates/nasdaq-100-pre-market-range-containment-strategy-targets-failed-breakouts-as-volatility-rises)
- [Maróy: Improvements to Intraday Momentum Strategies (SSRN)](https://papers.ssrn.com/sol3/Delivery.cfm/5095349.pdf?abstractid=5095349&mirid=1)
- [Turtle Soup Plus One (LuxAlgo)](https://www.luxalgo.com/library/concept/turtle-soup/)
- [Mean-Reversion-Regime / Vola-Perzentil (SetupAlpha)](https://setupalpha.com/blogs/articles/mean-reversion-strategy-failures-complete-fix-guide)
