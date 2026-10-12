# Trade-Analyser mt5-1.4: Entry am Kurs und höhere Trefferquote

Stand 12.10.2026. Grundlage ist `ta_mt5.py` mt5-1.3 (Prüfsumme `54b571ca…df19e`), wie es im Projekt „Analyzer“ und auf dem PC liegt.

## 1. Kurzfassung

Alex wollte zwei Dinge: einen Entry immer nahe am aktuellen Kurs, also eine Order, die sofort gefüllt wird, und eine höhere Trefferquote.

- **Entry:** mt5-1.4 gibt nur noch Market-Orders zum aktuellen Kurs aus. Jede Order ist sofort gefüllt. Bei mt5-1.3 waren es zu 99,7 % Limits, und im Backtest wurden nur rund 36 % davon gefüllt.
- **Trefferquote:** „Target vor Stop“ steigt im Backtest von 22–28 % auf 56–62 %. Das gilt auf allen Daten, auch auf denen, die bei der Entwicklung nicht benutzt wurden.
- **Ertrag:** Nach Spread liegt mt5-1.4 bei etwa ±0 R je Trade (−0,05 bis +0,06). mt5-1.3 lag bei −0,06 bis −0,28 R.
- **Ehrlich gesagt:** Ein belegter Vorteil ist das nicht. Die höhere Trefferquote kommt vor allem vom Verhältnis Stop zu Target (CRV 0,75 statt ≥ 1,5). Dass das Ergebnis nicht mehr deutlich negativ ist, liegt an drei Dingen:
  - Der Spread fällt bei einem weiten Stop weniger ins Gewicht.
  - Gehandelt wird nur in der Haupthandelszeit.
  - Die ungünstige Auswahl bei Limit-Füllungen entfällt: Gefüllt werden vor allem Limits, durch die der Kurs weiterläuft.

## 2. Was sich ändert

| | mt5-1.3 | mt5-1.4 |
|---|---|---|
| Orderart | Limit an der Pullback-Leiter (+1σ / VWAP / −1σ) oder an ±2σ; Market nur am Level mit Bestätigungskerze | **nur Market** zum aktuellen Kurs |
| Handelszeit | rund um die Uhr (außer Sperren) | NAS100 und ETH 09:45–15:30 New York (meist 15:45–21:30 Wien), GER40 09:15–17:00 Wien |
| Regime | Supertrend M30 + Seite zum M30-VWAP; Range über VWAP-Kreuzungen | unverändert |
| Range | Limit-Fade an ±2σ, Target VWAP | **kein Trade** |
| Trend-Einstieg | Limit am nächsten Leiter-Level | **Rücksetzer:** letzte geschlossene 5min-Kerze gegen den Trend, Kurs 0,25–1,5 ATR5 unter dem Hoch (Long) bzw. über dem Tief (Short) der letzten 12 Kerzen |
| Stop | Swing oder Band plus Puffer, mindestens 1 ATR5 | 3 × ATR5 hinter dem Entry |
| Target | nächstes Band oder Tageshoch mit CRV ≥ 1,5 | 0,75 × Risiko, mindestens 0,2 % (ETH 0,3 %) |
| Eröffnungssperre | Market gesperrt, Limits erlaubt | gar kein Trade |
| News-Sperre, VWAP-Reset, Kerzenabgleich, Markt geschlossen | | unverändert |
| Signal-Log, `auswerten` | Regelvergleich gegen mt5-1.1 | Regelvergleich gegen **mt5-1.3** (Schatten-Spur), Trefferquote je Version |

Alle neuen Werte stehen in `SET` (`MARKT_MODUS`, `HANDELSZEIT_*`, `RS_KERZEN`, `RS_MIN_ATR`, `RS_MAX_ATR`, `STOP_ATR`, `ZIEL_R`, `MIN_CRV_MARKT`). `MARKT_MODUS=False` liefert exakt die Regeln von mt5-1.3, und genau so rechnet das Script die Schatten-Spur.

Beispielausgabe (aus dem Integrationstest, NAS100 2022):

```
Entry: NAS100 Short Market @ 12552
Target: 12474
Stop: 12657
Begründung: Trend Short, weil der 30min-Supertrend Short bei 12683 steht und der Kurs 12552 unter dem 30min-VWAP 12606 liegt; Setup ist ein Rücksetzer im Trend: die letzte 5min-Kerze schloss gegen den Trend und der Kurs liegt 0,5 ATR5 über dem Tief der letzten 12 5min-Kerzen 12532, Einstieg sofort zum Marktpreis. Stop 3 ATR5 (104 Punkte) über dem Entry bei 12657, Target 0,75 x Risiko bei 12474, CRV 0,7.
```

## 3. Wie getestet wurde

**Backtest-Harness** (`backtest/bt.py`):
- Sie lädt das Script als Modul und ruft seine eigenen Funktionen auf: `analysiere`, `instrument`, `bewerte`.
- Modell: Je Instrument fragt ein Trader bei jeder 5min-Kerze ab, solange er keine Order und keine Position hat, und zwar 1 s vor Kerzenschluss.
- Jedes Signal wird mit `bewerte()` des Scripts ausgewertet, also genau wie bei „auswerten“:
  - Berührung = Füllung.
  - Stop und Target in derselben Kerze zählen als Stop.
  - Nach 480 min wird zum letzten Kurs bewertet („Zeitablauf“).

**Prüfung der Harness** (`backtest/validate.py`):
- Für zufällige Zeitpunkte schreibt sie einen echten TA_Export-Ordner, startet das Script wie im Skill als Prozess und vergleicht die Ausgabe.
- mt5-1.3: 180 von 180 identisch.
- mt5-1.4: 200 von 200 identisch (NAS100, GER40, ETH).

**Integrationstest** (`backtest/integration.py`): Er läuft über alle drei Instrumente gleichzeitig und prüft:
- `setup` und `--nur` sowie die News-Sperre
- Signal-Log und Schatten-Zeilen
- `--auswerten` und den Chart
- die Kontrolle aus SKILL.md Schritt 5

**Daten** (öffentliche Quellen von GitHub, siehe `backtest/hole_daten.sh`, mit Prüfsummen):

| Instrument | Quelle | Zeitraum | Volumen |
|---|---|---|---|
| NAS100 | MT5-Broker-Export US100 (ts4blader/market_data), Serverzeit NY+7 wie Qberx | 2021–2025 | Tickvolumen |
| GER40 | getdata-finance GER30 1m (DAX-40-CFD) | Feb–Sep 2026 | Tickvolumen |
| GER40 | Dukascopy DEUIDXEUR M5 (TheSnowGuru) | Okt 2020 – Sep 2023 | keines → VWAP gleich gewichtet |
| ETH | Binance Spot ETHUSDT 5m (Speirsy11/crypto-dataset) | 2021 – Sep 2026 | Volumen |

**Kosten:**
- Spread 1,5 Punkte (NAS100, GER40) bzw. 2 USD (ETH) je Trade.
- Kein Slippage, keine Swaps, keine Kommission.
- Kein News-Kalender, weil historische Termine fehlen.

**Vorgehen gegen Überanpassung:**
- Fünf Regelfamilien wurden von getrennten Agenten untersucht: Trend-Pullback, Range-Fade, Geometrie, Session-Filter und Momentum.
- Abgestimmt wurde nur auf NAS100 2021–2023.
- 2024 diente als einmalige Kontrolle; danach wurde nichts mehr verändert.
- NAS100 2025, beide GER40-Datensätze und ETH hat keine Variante vorher gesehen. Erst auf diesen Daten wurde zwischen den fünf Endkandidaten gewählt.
- Jede Variante hat ein zweiter Agent unabhängig nachgerechnet und auf Blick in die Zukunft geprüft.

## 4. Ergebnisse

### mt5-1.3 gegen mt5-1.4

`ergebnis_tabelle.md` enthält die vollständige Tabelle.

| Lauf | Version | Signale | gefüllt | Target vor Stop | R > 0 | R je Trade brutto | R je Trade nach Spread | Zeitablauf | Haltedauer Median | Stop-Abstand Median |
|---|---|---|---|---|---|---|---|---|---|---|
| NAS100 2021–23 (Abstimmung) | 1.3 | 8978 | 36 % | 26,6 % | 29 % | −0,044 | −0,121 | 6 % | 40 min | 20 |
| | **1.4** | 1560 | 100 % | **62,4 %** | 60 % | +0,079 | +0,055 | 14 % | 80 min | 72 |
| NAS100 2024 (Kontrolle) | 1.3 | 2638 | 36 % | 26,5 % | 30 % | −0,033 | −0,098 | 8 % | 45 min | 23 |
| | **1.4** | 509 | 100 % | **59,4 %** | 55 % | +0,015 | −0,006 | 15 % | 75 min | 78 |
| NAS100 2025 (zurückgehalten) | 1.3 | 2663 | 37 % | 21,9 % | 26 % | −0,132 | −0,184 | 8 % | 40 min | 29 |
| | **1.4** | 478 | 100 % | **57,2 %** | 54 % | +0,006 | −0,011 | 14 % | 100 min | 99 |
| GER40 2026 (zurückgehalten) | 1.3 | 1672 | 38 % | 27,2 % | 29 % | −0,032 | −0,079 | 6 % | 45 min | 31 |
| | **1.4** | 407 | 100 % | **56,4 %** | 56 % | +0,007 | −0,012 | 5 % | 75 min | 83 |
| GER40 2021–23 Dukascopy (zurückgehalten) | 1.3 | 6689 | 35 % | 27,6 % | 31 % | +0,017 | −0,064 | 8 % | 40 min | 18 |
| | **1.4** | 1808 | 100 % | **58,6 %** | 58 % | +0,051 | +0,020 | 6 % | 85 min | 52 |
| ETH 2021–26 (zurückgehalten) | 1.3 | 21524 | 37 % | 26,4 % | 32 % | −0,078 | −0,282 | 10 % | 55 min | 11 |
| | **1.4** | 3351 | 100 % | **60,9 %** | 59 % | +0,051 | −0,050 | 6 % | 75 min | 27 |

So liest man die Spalten:
- **Target vor Stop:** die Kennzahl von „auswerten“. Zeitabläufe zählen dort nicht mit.
- **R > 0:** der Anteil der gefüllten Trades mit Gewinn, Zeitabläufe eingeschlossen.
- **Signale:** Die Zahl ist im Modell kleiner als bei mt5-1.3, weil nur in der Handelszeit und nur im Rücksetzer gehandelt wird. Im Modell sind das rund 2 Trades je Instrument und Handelstag.

### Die fünf Kandidaten auf den zurückgehaltenen Daten

Jede Zelle zeigt Target vor Stop / R je Trade nach Spread.

| Variante | NAS100 2025 | GER40 Feb–Sep 2026 | GER40 2021–23 | ETH 2021–26 |
|---|---|---|---|---|
| **Trend-Pullback (gewählt)** | 57 % / −0,011 | 56 % / −0,012 | 59 % / +0,020 | 61 % / −0,050 |
| Geometrie (Stop 5 ATR5, Target 0,5 R) | 73 % / −0,022 | 69 % / −0,002 | 70 % / −0,011 | 72 % / −0,032 |
| Momentum (Trendtag, nur NAS100) | 67 % / −0,039 | 68 % / −0,004 | 68 % / −0,023 | 69 % / −0,054 |
| Session-Filter (US-Nachmittag, starker Trend) | 71 % / −0,016 | 62 % / −0,088 | 72 % / +0,022 | 68 % / −0,111 |
| Range-Fade (nur Long, −2σ) | 59 % / −0,078 | 57 % / +0,010 | 56 % / −0,056 | 63 % / −0,138 |

Momentum ist für GER40 und ETH ab Werk abgeschaltet; hier wurde es zum Vergleich trotzdem gerechnet.

Alle fünf Varianten sahen in der Abstimmung positiv aus, mit +0,02 bis +0,08 R. Momentum und Range-Fade hielten auch 2024. Auf den zurückgehaltenen Daten liegt keine Variante überall im Plus.

Trend-Pullback wurde gewählt, weil es am robustesten ist:
- Es hat das beste Ergebnis auf NAS100 2025 und liegt sonst nahe am besten Wert.
- Es hat die wenigsten Zeitabläufe (5–15 % statt 13–30 %).
- Der Stop ist kleiner als bei Geometrie (3 statt 5 ATR5).
- Die Regel ist leicht zu erklären.

## 5. Warum eine hohe Trefferquote allein nichts beweist

Zum Vergleich wurde bei jeder Kerze ein Market-Trade in **zufälliger** Richtung eröffnet (`backtest/geometrie.py`):

| Stop | Target | Target vor Stop | R je Trade brutto | nach Spread |
|---|---|---|---|---|
| 1 ATR5 | 1 ATR5 | 52 % | −0,016 | −0,18 |
| 1,5 ATR5 | 1 ATR5 | 62 % | −0,014 | −0,12 |
| 2 ATR5 | 1 ATR5 | 67 % | −0,019 | −0,10 |
| 1 ATR5 | 0,5 ATR5 | 68 % | −0,036 | −0,20 |

Die Trefferquote folgt fast genau Stop / (Stop + Target), ganz ohne Analyse.

Auch die Richtung des M30-Supertrends brachte über den ganzen Tag gegenüber dem Zufall nichts. Dasselbe gilt für die Lage zum VWAP und für die Bestätigungskerze (`backtest/scan.py`).

Daraus folgt:
- Wer die Trefferquote erhöhen will, kann das jederzeit über ein kleineres CRV tun.
- Ob dabei Geld übrig bleibt, entscheidet allein, ob die Regel besser ist als der Zufall.
- mt5-1.4 ist auf allen Daten leicht besser als der Zufall bei gleicher Geometrie: brutto +0,006 bis +0,08 R je Trade. Der Vorsprung ist aber ungefähr so groß wie die Kosten.

Mit der Stellschraube `ZIEL_R` lässt sich die Trefferquote weiter verschieben. 0,5 statt 0,75 ergab auf den zurückgehaltenen Daten 61–69 % Target vor Stop, bei 0,01–0,02 R weniger je Trade.

## 6. Grenzen und Risiken

- **Großer Stop:** Bei NAS100 im Median 70–100 Punkte, bei GER40 50–80, bei ETH etwa 27 USD. Die Positionsgröße muss sich danach richten, damit das Geldrisiko je Trade gleich bleibt.
- **Ein Stop kostet mehr als ein Treffer bringt:** ungefähr 1,33 Target-Abstände.
- **Verlustserien:** Im Backtest gab es bis zu 6–8 Stops in Folge. Der größte Rückgang lag je Datensatz bei 15–24 R vor Kosten (ein Trader pro Instrument, jede Kerze abgefragt).
- **Zeitablauf:** 5–15 % der Trades erreichen in 8 Stunden weder Target noch Stop; im Schnitt verlieren sie leicht. Trades vom Nachmittag können über den US-Kassaschluss und die tägliche Pause um 17:00 New York laufen. Swaps sind nicht eingerechnet.
- **ETH hängt am Spread:** Mit einem Spread unter etwa 1 USD läge ETH im Plus, mit 2 USD bei −0,05 R. Der tatsächliche Spread von ETHUSD.pro bei Qberx war nicht bekannt. Außerdem stammen die ETH-Daten von Binance Spot, nicht vom Broker.
- **GER40-Daten:** Die 2026er-Daten umfassen nur 8 Monate. Die Dukascopy-Daten haben kein Volumen, der VWAP ist dort gleich gewichtet.
- **News:** Im Backtest gab es keine News. Die News-Sperre bleibt, sie verhindert aber nur den Einstieg. Ein laufender Trade kann in einen Termin hineinlaufen; die Begründung nennt den nächsten Termin.
- **Weniger Signale:** Außerhalb der Handelszeit, im Range und ohne Rücksetzer gibt es keinen Trade (Form B mit Grund). Ein „setup“ am Vormittag in Wien liefert höchstens GER40.
- **Abfragezeitpunkt:** Im Modell wird 1 s vor Kerzenschluss abgefragt. Live kommt die Abfrage irgendwann in der Kerze, und zwischen Ausgabe und Order vergehen einige Sekunden.

## 7. Kontrolle im Live-Betrieb

Jeder Lauf rechnet die Regeln von mt5-1.3 im Schatten mit. „auswerten“ zeigt dazu:
- Die Zeile „Regelvergleich mt5-1.4 gegen mt5-1.3“ vergleicht beide Regelwerke über dieselben Läufe.
- Ein Urteil gibt es erst an den festen Prüfpunkten bei 50, 100 und 150 gefüllten Trades.
- Lautet das Urteil `ZURÜCK AUF mt5-1.3`, stellt der Befehl „mt5-1.4 zurückrollen“ die alte Fassung wieder her.
- Die Zeile „Version mt5-1.4“ zeigt die eigene Trefferquote der neuen Fassung.

## 8. Installation

1. **Sicherung anlegen:** Im Projekt „Analyzer“ zwei Dateien ablegen:
   - `claude/ta_mt5_v1.3_backup.py` = `TradeAnalyser/ta_mt5_v1.3_backup.py` (das bisherige Script, Prüfsumme `54b571ca5772e2adce15d5a73aa21c33805d7b97759d1ea84d7e1f32b32df19e`)
   - `claude/SKILL_trade-analyser-mt5_v1.3_backup.md` = `TradeAnalyser/SKILL_trade-analyser-mt5_v1.3_backup.md`

   Der Rückroll-Befehl braucht beide Dateien.
2. **Script ersetzen:** `claude/ta_mt5.py` im Projekt durch `TradeAnalyser/ta_mt5.py` ersetzen. Die Prüfsumme steht in `TradeAnalyser/SKILL.md`.
3. **Skill ersetzen:** Den Skill `trade-analyser-mt5` durch `TradeAnalyser/SKILL.md` ersetzen.
4. **Erstes „setup“:** Die Prüfsumme auf dem PC passt dann nicht mehr. Die Wiederherstellung des Skills holt das neue Script aus dem Projekt und legt es selbst in den TA_Export-Ordner. `signale.jsonl` und `auswertung.jsonl` bleiben erhalten.

## 9. Dateien

| Datei | Inhalt |
|---|---|
| `ta_mt5.py` | mt5-1.4 |
| `SKILL.md` | Skill für mt5-1.4 |
| `ta_mt5_v1.3_backup.py` | bisheriges Script, unverändert |
| `SKILL_trade-analyser-mt5_v1.3_backup.md` | bisheriger Skill, unverändert |
| `backtest/` | Harness, Prüfungen, Datenbeschaffung, Ergebnistabelle (Anleitung in `backtest/README.md`) |
