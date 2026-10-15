# Analyzer 3 – Forschungsprotokoll (verbindlich für alle Familien)

Stand 15.10.2026. Ziel: Setups finden, die Alex' Zielprofil näher kommen als noise-1.0.

## Daten und Zeiträume
- Alle Kerzen: M5 in Qberx-Serverzeit (New York + 7 h), `lib/qdata.py`, Dateien `/home/user/data/m5/<INST>.parquet`.
- **dev** = ab `qdata.dev_start(inst)` (2020-01-01, NAS100 2021-01-01) bis 2024-12-31.
  - **Train** = dev bis 2023-12-31. Hier wird entwickelt und gewählt.
  - **Validierung** = 2024. Nur zur Kontrolle; nach Blick auf 2024 werden keine Parameter mehr gedreht, höchstens Kandidaten verworfen.
- **info25** = 2025. Verbraucht (früher angesehen). Darf berichtet werden, entscheidet nichts.
- **gesperrt** = alles vor dev_start (NAS100 2005–2020, andere vor 2020) und 2026-01 bis 2026-10. Zugriff nur über `qdata.load`, die gesperrte Auswertungsbereiche verweigert. Niemand umgeht die Sperre (kein direktes Lesen der Parquet-/Rohdateien für gesperrte Zeiträume, auch nicht „nur zum Ansehen“).
- Ausnahme Datenlage: Instrumente ohne dev-Daten (nur OANDA bis 05/2020) werden in dieser Runde nicht entwickelt.

## Backtest-Regeln (`lib/qbt.py`)
- Entscheidung am Schluss der Signalkerze, Einstieg zur Eröffnung der nächsten Kerze (Market) oder per Pending-Order.
- Stop vor Ziel in derselben Kerze. Öffnet der Kurs jenseits des Stops, Ausstieg zur Eröffnung.
- Ziel exakt zum Zielkurs. Zeitausstieg zum Schluss der letzten erlaubten Kerze.
- Kosten: Roundtrip-Anteil am Preis (`qdata.COST`), in R umgerechnet, von jedem Trade abgezogen.
- Eine offene Position je Regel und Instrument.
- Kennzahlen: n, Trades pro Handelstag, **Target vor Stop** (Ziel-Treffer / (Ziel + Stop), Zeitausstiege nicht gezählt), Gewinnquote (R > 0), R netto je Trade, t-Wert (Trade-Ebene und Tages-Cluster).
- **Nullmodell** (`qbt.null_model`): gleiche Geometrie (Stopabstand in %, Ziel in R, gleicher Nachzieh-Stop), gleiche Richtung, gleiche NY-Uhrzeit, Tag gleichverteilt über denselben Zeitraum, K = 20 Ziehungen je Trade. Keine ±14-Tage-Verschiebung.
- Standard-Tabelle je Zelle: `qbt.report_cell(x, trades, {'Train': ..., 'Val 2024': ...})`.

## Referenz noise-1.0 (Rekonstruktion, `lib/noise.py: noise10_signals`)
Das Original-Script lag in dieser Sitzung nicht vor. Nachgebaut ist folgende Regel:
- M30-Raster 10:00–14:30 NY; Signal, wenn eine M30-Kerze außerhalb der Noise-Area schließt (Lookback 14).
- Trendfilter: Vortagesschluss gegen SMA20.
- Nur der erste Trade des Tages.
- Stop in der Bandmitte, Ziel 1R.
- Bewertung nach 480 min Uhrzeit (`last_by_clock`). Seit 15.10. abends korrigiert; vorher zählte der Nachbau 96 Kerzen, sodass Freitags-Trades übers Wochenende liefen.
Ergebnis NAS100 nach Uhr- und Datenkorrektur:

| Zeitraum | n | Target vor Stop | R netto | t |
|---|---|---|---|---|
| Train 2021–23 | 226 | 55,7 % | +0,102 | 1,88 |
| 2024 | 68 | 56,1 % | +0,123 | 1,25 |
| 2025 | 62 | 53,8 % | +0,097 | |

- 0,24–0,29 Trades je Handelstag.
- Nullmodell (K = 100): Train −0,017 R, 2024 ±0,000 R.
- Gemeldet: 54/60/57 % und +0,10/+0,17/+0,15 R.

## Disziplin
- Wenige, runde Parameter (z. B. 0,5 / 1 / 2 R; 14 / 20 Tage; 30-min-Raster). Literaturregeln vor eigenen Erfindungen; Quelle nennen.
- **Jede** getestete Variante wird mit `lib/ledger.py: log_variant` protokolliert (auch verworfene).
- Kandidaten für den gesperrten Test als Modul `familien/<familie>/kandidat_<name>.py` mit
  `NAME`, `INSTRUMENTS`, `prepare(df, inst) -> x`, `signals(x, inst) -> Signaltabelle`. Keine festen Datumsangaben im Code, nur Daten bis zur Signalkerze verwenden.
- Erfolgskriterien werden vor dem gesperrten Lauf in `ergebnisse/KRITERIEN_GESPERRT.md` festgeschrieben. Der gesperrte Lauf erfolgt genau einmal.
