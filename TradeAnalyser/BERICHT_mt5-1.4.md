# Trade-Analyser mt5-1.4: Entry am Kurs und höhere Trefferquote

Stand 12.10.2026. Grundlage ist `ta_mt5.py` mt5-1.3 (Prüfsumme `54b571ca…df19e`), wie es im Projekt „Analyzer“ und auf dem PC liegt.

## 1. Kurzfassung

Alex wollte zwei Dinge: einen Entry immer nahe am aktuellen Kurs, also eine Order, die sofort gefüllt wird, und eine höhere Trefferquote.

- **Entry:** mt5-1.4 gibt nur noch Market-Orders zum aktuellen Kurs aus. Jede Order ist sofort gefüllt. Bei mt5-1.3 waren es zu 99,7 % Limits, und im Backtest wurden nur rund 36 % davon gefüllt.
- **Trefferquote:** „Target vor Stop“ steigt im Backtest von 22–28 % auf 56–62 %. Das gilt auf allen sechs Datensätzen.
- **Ertrag:** Nach Spread liegt mt5-1.4 außerhalb des Abstimmungszeitraums bei −0,03 bis +0,02 R je Trade, also etwa ±0. mt5-1.3 lag auf denselben Daten bei −0,06 bis −0,28 R. Im Abstimmungszeitraum (NAS100 2021–23) waren es +0,055 R; das hat sich danach nicht gehalten.
- **Ehrlich gesagt:** Ein belegter Vorteil ist das nicht.
  - Die höhere Trefferquote kommt vor allem vom Verhältnis Stop zu Target (CRV 0,75 statt ≥ 1,5).
  - Zufallseinstiege mit derselben Geometrie im selben Zeitfenster schneiden auf NAS100 2024/2025 und GER40 2026 praktisch gleich ab (Abschnitt 5).
  - Dass das Ergebnis nicht mehr deutlich negativ ist, liegt an drei Dingen: Der weite Stop macht den Spread verhältnismäßig klein. Gehandelt wird nur in der Haupthandelszeit. Und es gibt keine Limit-Füllungen mehr, die vor allem dann zustande kamen, wenn der Kurs gegen die Position weiterlief.

## 2. Was sich ändert

| | mt5-1.3 | mt5-1.4 |
|---|---|---|
| Orderart | Limit an der Pullback-Leiter (+1σ / VWAP / −1σ) oder an ±2σ; Market nur am Level mit Bestätigungskerze | **nur Market** zum aktuellen Kurs |
| Handelszeit | rund um die Uhr (außer Sperren) | Mo–Fr: NAS100 und ETH 09:45–15:30 New York (meist 15:45–21:30 Wien), GER40 09:15–17:00 Wien |
| Regime | Supertrend M30 + Seite zum M30-VWAP; Range über VWAP-Kreuzungen | unverändert |
| Range | Limit-Fade an ±2σ, Target VWAP | **kein Trade** |
| Trend-Einstieg | Limit am nächsten Leiter-Level | **Rücksetzer:** letzte geschlossene 5min-Kerze gegen den Trend, Kurs 0,25–1,5 ATR5 unter dem Hoch (Long) bzw. über dem Tief (Short) der letzten 12 Kerzen |
| Stop | Swing oder Band plus Puffer, mindestens 1 ATR5 | 3 × ATR5 hinter dem Entry |
| Target | nächstes Band oder Tageshoch mit CRV ≥ 1,5 | 0,75 × Risiko, mindestens 0,2 % (ETH 0,3 %); dann ist das CRV höher |
| Auswahl bei „setup“ | höheres CRV zuerst | CRV am nächsten an 0,75 zuerst |
| Eröffnungssperre | Market gesperrt, Limits erlaubt | gar kein Trade (09:25–09:44 New York, 08:55–09:14 Wien) |
| News-Sperre, VWAP-Reset, Kerzenabgleich, Markt geschlossen | | unverändert |
| Signal-Log, „auswerten“ | Regelvergleich gegen mt5-1.1 | Regelvergleich gegen **mt5-1.3** (Schatten-Spur), Trefferquote je Version |

Alle neuen Werte stehen in `SET`: `MARKT_MODUS`, `HANDELSZEIT_*`, `RS_KERZEN`, `RS_MIN_ATR`, `RS_MAX_ATR`, `STOP_ATR`, `ZIEL_R`.

`MARKT_MODUS=False` liefert exakt die Regeln von mt5-1.3. Auf NAS100 2024–2025 sind alle 5301 Signale identisch. Genau so rechnet das Script die Schatten-Spur.

Log-Zeilen von mt5-1.4 bleiben für mt5-1.3 lesbar: Nach einem Zurückrollen funktioniert „auswerten“ weiter (getestet mit `backtest/rollback_test.py`).

Beispielausgabe (aus dem Integrationstest, NAS100 2022):

```
Entry: NAS100 Short Market @ 12552
Target: 12474
Stop: 12657
Begründung: Trend Short, weil der 30min-Supertrend Short bei 12683 steht und der Kurs 12552 unter dem 30min-VWAP 12606 liegt; Setup ist ein Rücksetzer im Trend: die letzte 5min-Kerze schloss gegen den Trend und der Kurs liegt 0,58 ATR5 über dem Tief der letzten 12 5min-Kerzen 12532, Einstieg sofort zum Marktpreis. Stop 3 ATR5 = 105 Punkte über dem Entry bei 12657, Target 0,75 x Risiko bei 12474, CRV 0,7.
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
- mt5-1.4 (Endstand): 191 von 191 identisch (NAS100, GER40, ETH).

**Weitere Tests:**
- `backtest/integration.py` über alle drei Instrumente gleichzeitig: `setup`, `--nur`, News-Sperre, Signal-Log mit Schatten-Zeilen, `--auswerten`, Chart und die Kontrolle aus SKILL.md Schritt 5.
- `backtest/rollback_test.py`: gemischtes Log aus mt5-1.3 und mt5-1.4, ausgewertet mit beiden Fassungen.

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

**Vorgehen, und wo es nicht sauber war:**
- Fünf Regelfamilien wurden von getrennten Agenten untersucht: Trend-Pullback, Range-Fade, Geometrie, Session-Filter und Momentum.
- Abgestimmt werden sollte nur auf NAS100 2021–2023. 2024 diente als einmalige Kontrolle; danach wurde an den Regeln nichts mehr verändert.
- Jede Variante hat ein zweiter Agent unabhängig nachgerechnet und auf Blick in die Zukunft geprüft.
- **Nicht sauber:**
  - Zwei Agenten (Momentum, Session-Filter) haben GER40 2021–23 und ETH zur Gegenprobe benutzt. Momentum hat daraufhin GER40 und ETH abgeschaltet.
  - Die Wahl zwischen den fünf Endkandidaten habe ich auf NAS100 2025, GER40 und ETH getroffen.
  - Diese Daten sind für die gewählte Variante deshalb nicht völlig unberührt. Am saubersten sind NAS100 2025 und GER40 2026.
- **Nach dem Review:** Die Handelszeit gilt jetzt nur Mo–Fr. Vorher handelte ETH auch am Wochenende, mit −0,11 R je Trade. Alle ETH-Zahlen unten sind mit dieser Korrektur gerechnet.

## 4. Ergebnisse

### mt5-1.3 gegen mt5-1.4

`backtest/ergebnis_tabelle.md` enthält die vollständige Tabelle.

| Lauf | Version | Signale | gefüllt | Target vor Stop | R > 0 | R je Trade brutto | R je Trade nach Spread | Zeitablauf | Haltedauer Median | Stop-Abstand Median |
|---|---|---|---|---|---|---|---|---|---|---|
| NAS100 2021–23 (Abstimmung) | 1.3 | 8978 | 36 % | 26,6 % | 29 % | −0,044 | −0,121 | 6 % | 40 min | 20 |
| | **1.4** | 1560 | 100 % | **62,4 %** | 60 % | +0,079 | +0,055 | 14 % | 80 min | 72 |
| NAS100 2024 (Kontrolle) | 1.3 | 2638 | 36 % | 26,5 % | 30 % | −0,033 | −0,098 | 8 % | 45 min | 23 |
| | **1.4** | 509 | 100 % | **59,4 %** | 55 % | +0,015 | −0,006 | 15 % | 75 min | 78 |
| NAS100 2025 | 1.3 | 2663 | 37 % | 21,9 % | 26 % | −0,132 | −0,184 | 8 % | 40 min | 29 |
| | **1.4** | 478 | 100 % | **57,2 %** | 54 % | +0,006 | −0,011 | 14 % | 100 min | 99 |
| GER40 Feb–Sep 2026 | 1.3 | 1672 | 38 % | 27,2 % | 29 % | −0,032 | −0,079 | 6 % | 45 min | 31 |
| | **1.4** | 407 | 100 % | **56,4 %** | 56 % | +0,007 | −0,012 | 5 % | 75 min | 83 |
| GER40 2021–23 Dukascopy | 1.3 | 6689 | 35 % | 27,6 % | 31 % | +0,017 | −0,064 | 8 % | 40 min | 18 |
| | **1.4** | 1808 | 100 % | **58,6 %** | 58 % | +0,051 | +0,020 | 6 % | 85 min | 52 |
| ETH 2021–Sep 2026 | 1.3 | 21524 | 37 % | 26,4 % | 32 % | −0,078 | −0,282 | 10 % | 55 min | 11 |
| | **1.4** | 2493 | 100 % | **61,9 %** | 60 % | +0,058 | −0,027 | 7 % | 75 min | 30 |

So liest man die Spalten:
- **Target vor Stop:** die Kennzahl von „auswerten“. Zeitabläufe zählen dort nicht mit.
- **R > 0:** der Anteil der gefüllten Trades mit Gewinn, Zeitabläufe eingeschlossen.
- **Signale:** Die Zahl ist im Modell kleiner als bei mt5-1.3, weil nur in der Handelszeit und nur im Rücksetzer gehandelt wird. Im Modell sind das rund 2 Trades je Instrument und Handelstag.

### Die fünf Kandidaten außerhalb des Abstimmungszeitraums

Jede Zelle zeigt Target vor Stop / R je Trade nach Spread. Stand vor der Mo–Fr-Korrektur, daher hier ETH mit Wochenende.

| Variante | NAS100 2024 (Kontrolle) | NAS100 2025 | GER40 Feb–Sep 2026 | GER40 2021–23 | ETH 2021–26 | Mittel der letzten vier |
|---|---|---|---|---|---|---|
| **Trend-Pullback (gewählt)** | 59 % / −0,006 | 57 % / −0,011 | 56 % / −0,012 | 59 % / +0,020 | 61 % / −0,050 | −0,013 |
| Geometrie (Stop 5 ATR5, Target 0,5 R) | 73 % / −0,011 | 73 % / −0,022 | 69 % / −0,002 | 70 % / −0,011 | 72 % / −0,032 | −0,017 |
| Momentum (Trendtag, nur NAS100) | 77 % / +0,072 | 67 % / −0,039 | 68 % / −0,004 | 68 % / −0,023 | 69 % / −0,054 | −0,030 |
| Session-Filter (US-Nachmittag, starker Trend) | 74 % / +0,023 | 71 % / −0,016 | 62 % / −0,088 | 72 % / +0,022 | 68 % / −0,111 | −0,048 |
| Range-Fade (nur Long, −2σ) | 66 % / +0,053 | 59 % / −0,078 | 57 % / +0,010 | 56 % / −0,056 | 63 % / −0,138 | −0,066 |

Momentum ist ab Werk für GER40 und ETH abgeschaltet; hier wurde es zum Vergleich trotzdem gerechnet.

Alle fünf Varianten sahen in der Abstimmung positiv aus (+0,02 bis +0,08 R). In der Kontrolle 2024 hielten Momentum, Range-Fade und Session-Filter, Trend-Pullback und Geometrie nicht. Danach verlor sich der Vorsprung bei allen.

Trend-Pullback wurde gewählt, weil es über NAS100 2025, GER40 2026, GER40 2021–23 und ETH im Mittel am wenigsten verlor:
- Es hat das beste Ergebnis auf NAS100 2025.
- Es hat weniger Zeitabläufe als Geometrie (5–14 % statt 13–30 %).
- Der Stop ist kleiner als bei Geometrie (3 statt 5 ATR5).
- Die Regel ist leicht zu erklären.

Ein Vorteil gegenüber den anderen ist damit nicht belegt; die Unterschiede liegen im Rauschen.

## 5. Warum eine hohe Trefferquote allein nichts beweist

**Zufall über den ganzen Tag** (`backtest/geometrie.py`, NAS100 2021–24): Market-Trade bei jeder Kerze in zufälliger Richtung.

| Stop | Target | Target vor Stop | R je Trade brutto | nach Spread |
|---|---|---|---|---|
| 1 ATR5 | 1 ATR5 | 52 % | −0,016 | −0,18 |
| 1,5 ATR5 | 1 ATR5 | 62 % | −0,014 | −0,12 |
| 2 ATR5 | 1 ATR5 | 67 % | −0,019 | −0,10 |
| 1 ATR5 | 0,5 ATR5 | 68 % | −0,036 | −0,20 |

Die Trefferquote folgt fast genau Stop / (Stop + Target), ganz ohne Analyse. Supertrend-Richtung, Lage zum VWAP und Bestätigungskerze brachten über den ganzen Tag nichts (`backtest/scan.py`).

**Zufall mit genau der Geometrie und dem Zeitfenster von mt5-1.4** (`backtest/zufall14.py`, drei Zufallsfolgen, R je Trade vor Kosten):

| Daten | Zufall | mt5-1.4 |
|---|---|---|
| NAS100 2021–23 (Abstimmung) | −0,015 bis 0,000 | +0,079 |
| NAS100 2024 | −0,022 bis +0,033 | +0,015 |
| NAS100 2025 | −0,037 bis −0,012 | +0,006 |
| GER40 Feb–Sep 2026 | −0,038 bis +0,003 | +0,007 |
| GER40 2021–23 | −0,049 bis +0,012 | +0,051 |
| ETH 2021–26 | −0,006 bis +0,008 | +0,058 |

Was daraus folgt:
- **NAS100 2024/2025 und GER40 2026:** mt5-1.4 ist nicht von Zufallseinstiegen mit derselben Geometrie zu unterscheiden.
- **GER40 2021–23 und ETH:** mt5-1.4 liegt vorn. Bei ETH auch nach Spread: −0,027 gegen −0,087 bis −0,101 R je Trade. Der Spread von 2 USD macht das Ergebnis aber insgesamt negativ.
- Die Trefferquote von 56–62 % ist also vor allem Geometrie. Wer sie weiter erhöhen will, kann das jederzeit über ein kleineres CRV tun. Ob dabei Geld übrig bleibt, hängt davon ab, ob die Regel besser ist als der Zufall.

Mit der Stellschraube `ZIEL_R` lässt sich die Trefferquote verschieben. 0,5 statt 0,75 ergab außerhalb der Abstimmung 61–70 % Target vor Stop (Endstand, ETH nur Mo–Fr), also +4 bis +8 Punkte. Der Ertrag je Trade änderte sich dabei um −0,02 bis +0,003 R.

## 6. Grenzen und Risiken

- **Großer Stop:** Im Median NAS100 72–99 Punkte, GER40 52–83, ETH etwa 30 USD. Die Positionsgröße muss sich danach richten, damit das Geldrisiko je Trade gleich bleibt.
- **Ein Stop kostet mehr als ein Treffer bringt:** ungefähr 1,33 Target-Abstände.
- **Verlustserien:** Im Backtest gab es bis zu 6–8 Stops in Folge. Der größte Rückgang lag nach Spread bei 18–32 R für die Indizes und 78 R für ETH (vor Kosten 16–21 R). Gerechnet ist das mit einem Trader pro Instrument, der jede Kerze abfragt.
- **Zeitablauf:** 5–15 % der Trades erreichen in 8 Stunden weder Target noch Stop; im Schnitt verlieren sie leicht. Trades vom Nachmittag können über den US-Kassaschluss und die tägliche Pause um 17:00 New York laufen. Swaps sind nicht eingerechnet.
- **ETH hängt am Spread:** Mit einem Spread unter etwa 1,4 USD läge ETH im Plus, mit 2 USD bei −0,03 R. Der tatsächliche Spread von ETHUSD.pro bei Qberx war nicht bekannt. Außerdem stammen die ETH-Daten von Binance Spot, nicht vom Broker.
- **US-Feiertage:** Das Script kennt keinen Feiertagskalender. An US-Börsenfeiertagen ist der NAS100-CFD dünn. Im Backtest lagen 21 Signale auf solchen Tagen, und sie waren klar schlechter (Target vor Stop 29 %). Besser an diesen Tagen kein NAS100-Signal handeln.
- **GER40-Daten:** Die 2026er-Daten umfassen nur 8 Monate. Die Dukascopy-Daten haben kein Volumen, der VWAP ist dort gleich gewichtet.
- **News:** Im Backtest gab es keine News. Die News-Sperre bleibt, sie verhindert aber nur den Einstieg. Ein laufender Trade kann in einen Termin hineinlaufen; die Begründung nennt den nächsten Termin.
- **Weniger Signale:** Außerhalb der Handelszeit, im Range und ohne Rücksetzer gibt es keinen Trade (Form B mit Grund). Ein „setup“ am Vormittag in Wien liefert höchstens GER40.
- **Abfragezeitpunkt:** Im Modell wird 1 s vor Kerzenschluss abgefragt. Live kommt die Abfrage irgendwann in der Kerze, und zwischen Ausgabe und Order vergehen einige Sekunden.
- **Offener Prüfpunkt, schon in mt5-1.3:** Reicht der M5-Export nicht bis zum Beginn des Broker-Tags zurück, startet das Script den VWAP still bei der ersten exportierten Kerze. Ein Fehler erscheint dann nicht. In der Handelszeit liegen bis zu etwa 270 M5-Kerzen seit dem Tagesbeginn. Der Dienst TA_Export sollte deshalb mindestens 300 M5-Kerzen schreiben. Das bitte im Dienst prüfen.

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
| `backtest/` | Harness, Prüfungen, Zufalls-Vergleiche, Datenbeschaffung, Ergebnistabelle (Anleitung in `backtest/README.md`) |
| `backtest/kandidaten/` | die vier anderen Kandidaten-Module, nur zum Nachrechnen der Kandidatentabelle |
