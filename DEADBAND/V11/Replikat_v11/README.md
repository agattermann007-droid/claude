# Replikat v11 – Python-Nachbau von DEADBAND V10 (M1, Kontoebene)

Neu aufgebaut am 14.10.2026, weil `Replikat_v10/` mit der alten Umgebung verloren war. Grundlage: der
Kontomotor `eng6.py` aus Replikat v6 (GitHub), umgebaut auf M1-Schritte und den Regelstand von V10.

## Daten

| Datei | Quelle | Zeitbasis |
|---|---|---|
| `XAU_m1.npz` | `github.com/Dypoi/XAUUSD_Dataset` (Dukascopy M1 Bid/Ask, 2016-09 … 2026-09) | UTC → New York → +7 h |
| `NAS_m1.npz` | `github.com/hizawye/better-backtest`, `data/histdata/nsxusd/normalized/*.json` (HistData NSXUSD, 2010-11 … 2026-02) | Quelle = NY-Ortszeit (geprüft: 9:30-/8:30-Sprung in jedem Jahr, Sommer wie Winter) → +7 h |
| (Prüfung) OANDA XAU_USD M1 2010–2016 | `github.com/FutureSharks/financial-data` (Mid), Pfad über `OANDA_DIR` | UTC → NY |

Bekannte Datenmängel (NAS) und ihre Behandlung:
- 16:15–17:00 NY fehlen werktags (ab 2019 ganz). GFT handelt bis 17:00 → flache Füllkerzen zum letzten Kurs (`prep11.fill_close`), sonst rutschen Ausstiege um 16:40 und der Freitag-Schluss 16:45 auf 18:00 bzw. übers Wochenende.
- Feb.–Jul. 2023 stundenweise Lücken, vor 2019 Rollsprünge an Quartalsverfallstagen → an diesen Tagen keine neuen NAS-Einstiege, offene Positionen vor Lücken > 10 min in der Kassasitzung neutral geschlossen (`gen11.bad_days`, `mk11.Market.hole`).

## Dateien

| Datei | Inhalt |
|---|---|
| `prep_m1.py` | Rohdaten → `NAS_m1.npz`, `XAU_m1.npz` (Pfade: `XAU_DIR`, `NAS_DIR`, `NPZ_DIR`) |
| `prep11.py` | M1 → NY-Minuten, Spread-Modell (NAS 1,63 bei 15.000, Gold 0,32 bei 2.000), M5/M15/M30/H1/D1 wie prep5 |
| `prep5.py`, `sig5.py` | aus Replikat v6 unverändert: Indikatoren wie MT5, RSI21-Signale, Noise-Prüfungen |
| `gen11.py` | Signal-Generatoren Zeile für Zeile nach dem MQL5-Code: Listen-Fades (`FadeKerze`) mit Probability Grid und Portfolio-Wächter, S0830, LW, XA, TD, SR (`SrTick` auf M1), Feiertage |
| `sim11.py` | Einzelstrom-Simulator M1 (R je Trade) und Bestätigungs-Einstieg |
| `eng11.py` | Kontomotor M1 (GFT Premium): Boden trailend am Equity-Hoch, Floating 1 % (Verlierer), Tagesverlust 3 %, gültige Tage 0,5 % + 0,50 $, 5 Tage, Zyklus 14 Tage, Mindestgewinn 131,25 $, Deckel 6 % für 2 Auszahlungen; EA-Bremsen (Floating 0,8 % gestuft, Tagesstopp 2,4 %), Budgets 0,9 % gesamt/je Idee, Pufferkurve 3,5/1,25/0,1, Hedging-Sperre, Serien-Stopp 3, Schutz gültiger Tage (mit GueltigSchutzFrei und RSI21-Regel 13:00/Regime), Abschluss-Ernte (alle Module, MFE ≥ 0,3 R), Gewinn-Ernte (RSI21), Schließen bei Reife, Wochenende mit Wiederaufnahme, Swap-Vorsorge, Margin |
| `mk11.py` | Ereignisgitter (Minuten beider Symbole), Zuordnung der Signale, Datenlöcher |
| `cfg11.py` | Stromnummern und Parameter von V8 und V10, Signal-Zwischenspeicher |
| `evl11.py` | Rollierende Konten (alle 7 Tage ein 10k-Konto, 1 Jahr), Kennzahlen, gepaarte Störungs-Seeds |
| `pa11.py` | allgemeiner Sweep-Reclaim-Generator im Tick (Forschung) |
| `cand11.py` | geprüfte Kandidaten (Gold-/NAS-Marken, Tick-Fades) |
| `t_*.py` | die Versuche aus dem Bericht (Ausgaben in `ergebnisse/`) |

## Konventionen (pessimistisch)

- Long zum Ask; Schlupf ¼ Spread auf Markt-Einstiege, Stop- und Zeit-Ausstiege.
- In derselben Minute zählt der Stop vor dem Ziel. Ziel bei Kerzen-Modulen erst ab der nächsten M5-Kerze (wie `FadeVerwalten`), bei SR ab der 4. Minute (130-s-Regel bei Einstieg mitten in der Minute).
- Tick-Einstieg (SR): Rückkehr in der Sweep-Minute nur, wenn deren Schluss schon zurück ist; sonst in einer späteren Minute zur Marke bzw. zum Open, wenn darüber eröffnet.
- Firmenregeln am schlechtesten Kurs der Minute, Equity-Hoch am besten Kurs.
- Kein Tick-Replay, keine News-Sperre im Nachbau.

## Ablauf

```
pip install numpy pandas numba
python prep_m1.py all                  # -> NPZ_DIR
python prep11.py                       # -> cache/D11.pkl
python t_streams.py                    # Einzelströme gegen die Berichtszahlen
python t_v10.py                        # V8 gegen V10, rollierende Konten
python t_final1.py; python t_final2.py # gepaarte Vergleiche (16/32 Seeds)
```

Laufzeit: ein Satz rollierender Konten (≈ 370 Konten) ≈ 3 s, mit 16 Störungs-Seeds ≈ 40 s (4 Kerne).
