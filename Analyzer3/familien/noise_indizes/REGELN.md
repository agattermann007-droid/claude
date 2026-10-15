# Familie noise_indizes – vorab festgelegte Regeln (geschrieben 15.10.2026 vor jeder Strategie-Rechnung)

Diese Datei wird vor dem ersten Backtest geschrieben und danach nicht mehr geändert (Nachträge nur unten unter "Nachtrag", mit Uhrzeit).

## Instrumente (fest, 11)
NAS100 (ts4, dev ab 2021), US500 (ts4), US30, US2000, GER40, FRA40, ESTX50, UK100, JPN225, AUS200, HK50 (Pedram, Bid, ohne Volumen -> VWAP gleichgewichtet).

## Sitzungen (Ortszeit; Kassasitzung, letzter Ausstieg)
- Aus `lib/noise.py: SESS` unverändert: US 9:30–16:00 NY, Ausstieg 15:00; GER40/ESTX50 9:00–17:30 Berlin, FRA40 9:00–17:30 Paris, Ausstieg 17:00; UK100 8:00–16:30 London, Ausstieg 16:00; JPN225 9:00–15:00 Tokio, Ausstieg 14:30; AUS200 10:00–16:00 Sydney, Ausstieg 15:30.
- Neu HK50: Asia/Hong_Kong 9:30–16:00, letzter Ausstieg 15:30 (30 min vor Kassaschluss wie bei allen Nicht-US-Indizes in SESS).
- Mittagspausen: JPN225 11:30–12:30 Tokio, HK50 12:00–13:00 Hongkong. Kerzen in der Pause gelten als außerhalb der Sitzung
  (`in_sess = False`): sie zählen nicht für Noise-Area, VWAP und Signalraster. Signalmarken nur, wenn die Signalkerze in Handelszeit liegt
  (JPN225: Marken 9:30 … 11:30 und 13:00 … 14:00; HK50: 10:00 … 12:00 und 13:30 … 15:00). Das Raster bleibt Uhrzeit-basiert
  (Minuten seit Kassaeröffnung). Offene Positionen laufen durch die Pause weiter (der CFD wird dort weiter gestellt, Stop/Ziel können greifen).

## Einstieg E0 = noise-1.0 unverändert
M30-Raster ab 30 min nach Kassaeröffnung bis vor den letzten Ausstieg, Schluss außerhalb der Noise-Area (Lookback 14, vol_mult 1,
Sitzungseröffnung und Vortagesschluss der Kassasitzung), Trendfilter Vortagesschluss gegen SMA20 der Sitzungsschlüsse bis Vortag,
Market zur nächsten Eröffnung, Stop Bandmitte (UB+LB)/2.

## Regeln (je Instrument gleich, nicht je Instrument abgestimmt)
- `N10_480`: erster Trade des Tages, Ziel 1R, Bewertung nach 480 min (i_sig + 96 Kerzen). Nur Vergleich mit dem Maßstab.
- `N10_EOD`: erster Trade des Tages, Ziel 1R, Zeitausstieg zum letzten Ausstieg der Sitzung (echter Daytrade). Für Alex maßgeblich.
- `A`: wie N10_EOD, aber Ziel 1,5R (Kandidat A der Familie 'ausstiege').
- `B`: Paper-Einstieg (alle Halbstunden-Signale mit SMA20-Filter, nach Ausstieg Wiedereinstieg erlaubt, eine Position zur Zeit),
  Teilziel 0,5R für 50 %, danach Stop auf Einstieg, Rest ohne Ziel bis zum letzten Ausstieg (Kandidat B der Familie 'ausstiege').

## Literatur (Schritt 3)
Wird nur übernommen, wenn eine Regel ohne Optimierung klar definiert ist. Ergebnis der Suche: siehe BERICHT.md. (Keine neue Regel übernommen,
siehe Begründung dort.)

## Portfolio und Auswahl (vorab)
- `alle`: alle 11 Instrumente ohne Auswahl, für jede Regel. Immer berichtet.
- `S1` (Auswahlregel, je Regel getrennt angewandt): Instrument rein, wenn auf Train (dev-Start bis 2023-12-31) gilt
  R netto > 0 UND R netto > Nullmodell-R (qbt.report_cell, K 20, seed 7). Sonst raus. Keine weitere Auswahl.
- Jede Portfolio-Zusammenstellung (Regel × {alle, S1}) zählt als eigene Variante.
- Portfoliotag = Serverdatum (NY+7): Asien-, Europa- und US-Sitzung eines Kalendertags fallen auf dasselbe Serverdatum.
  Handelstage = Werktage (Serverdatum), an denen mindestens eines der 11 Instrumente Sitzungskerzen hat.
  Kennzahlen: n, Trades je Handelstag, Anteil Tage mit ≥ 1 Trade (Setup), Target vor Stop, Gewinnquote, R netto je Trade,
  R je Handelstag, t (Trade-Ebene) und Tages-Cluster-t (Summe R je Portfoliotag, Tage ohne Trade nicht mitgezählt wie in qbt).
  Nullmodell des Portfolios = Trade-gewichtetes Mittel der Nullmodelle der Instrumente.
- Kosten: qdata.COST (Annahmen). Je Instrument berichtet: Kosten in R je Trade (Mittel von COST·E/Risiko).

## Kandidaten (höchstens 3, Entscheidung nur auf Train)
Je Daytrade-Regel (N10_EOD, A, B) höchstens ein Portfolio-Kandidat: S1, wenn S1 auf Train R > 0 mit Tages-Cluster-t ≥ 2 und R klar über dem
Nullmodell (t gegen Null ≥ 2); sonst `alle`, wenn dieses die Bedingung erfüllt; sonst kein Kandidat. 2024 wird danach einmal angesehen; ein
Kandidat wird verworfen, wenn das Portfolio 2024 R netto ≤ 0 hat. Keine Parameteränderung nach 2024.

## Nachtrag (nach Datenprüfung qa_daten.py, vor jeder Strategie-Rechnung)
- Zeitlage geprüft: Die größte mittlere |5-min-Rendite| liegt bei allen 11 Instrumenten an der lokalen Kassaeröffnung (bzw. bei HK50 an der
  Futures-Eröffnung 9:15 und an der Kasse 9:30, AUS200 am SPI-Start 9:50 und 10:00). UTC->Serverzeit passt.
- HK50 hat in der Mittagspause praktisch keine Kerzen (HSI-Futures pausieren), JPN225 hat dort Kerzen (Nikkei-Futures laufen durch).
- Datenlücken: FRA40 und UK100 2023-03 bis 2023-07 fehlt am Nachmittag etwa die Hälfte der Kerzen (113/115 Tage); AUS200 hat 29 Tage
  mit fehlender erster Stunde. Entscheidung: Regeln bleiben unverändert (kein Tagesfilter, wie im gesperrten Lauf), Lücken werden im
  Bericht genannt.
