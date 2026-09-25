# DEADBAND LIVE 4 – Build 6.20 (RSI21 verbessert)

Bericht vom 25.09.2026 · GFT Instant Premium 10k · Auftrag: „Verbessere die RSI21-Strategie, alle Wege offen“

## 1. Kurzfassung

Build 6.20 ändert nur das RSI21-Modul. Alles andere ist 6.10 (Fades, Noise, Kontoerkennung, Ernten, Bremsen).

1. **Neu: Volumen-Bestätigung.** Ein RSI21-Einstieg braucht auf der Signalkerze ein Tick-Volumen von mindestens
   dem 1,5-Fachen des Mittels der letzten 50 Kerzen derselben Zeitebene (`R21VolFaktor 1.5`, `R21VolKerzen 50`). Für
   das Folgesignal zählt das Signal auch ohne Volumen. Grund: Signale unter 1,0 × Mittel brachten 2006–2025 nur
   +0,18 R je Trade, die übrigen +0,41 R.
2. **Risiko umgeschichtet:** Gold-Faktor 0,70 → **0,50** (Gold-RSI21: +0,25 R je Trade, NAS-RSI21: +0,66 R),
   RSI21-Risiko 0,50 → **0,60 %**.

Replikat, Konto „Ertrag“ (Auszahlung ab 3 %, strenge Regel-Lesart):

| Kennzahl je Jahr | Ersatz-GFT 2022–25: 6.10 | **6.20** | Fremddaten 2006–21: 6.10 | **6.20** |
|---|---:|---:|---:|---:|
| Auszahlungen | 8,14 | **8,20** | 1,94 | **2,09** |
| Busts | 0,028 | **0,004** | 0,364 | **0,259** |
| Netto | 2459 $ | 2467 $ | 494 $ | 536 $ |
| Serien ≥ 5 / ≥ 6 Verluste | 2,78 / 1,10 | 2,54 / 1,03 | 4,67 / 2,73 | 4,03 / 2,54 |
| längste Serie: Mittel / schlimmste | 6,6 / 10 | 6,7 / 10 | 10,1 / 18 | 10,0 / 16 |
| mittlerer größter Rückgang je Konto | 399 $ | 383 $ | 515 $ | 505 $ |
| RSI21: Ergebnis / Trades / Treffer | 916 $ / 62 / 58 % | 869 $ / 55 / 60 % | 467 $ / 52 / 51 % | 504 $ / 43 / 54 % |

Nach Startjahr (1-Jahres-Konten, Ersatz-GFT), Auszahlungen / Busts: 2022 9,28 / 0,018 → 9,33 / 0,000 · 2023
9,45 / 0,008 → 9,41 / 0,000 · 2024 5,43 / 0,050 → 5,65 / 0,018 · 2025 4,41 / 0,151 → 4,26 / 0,043.
Streuung über die 16 Störungen: 8,20 ± 0,47 Auszahlungen, Busts 0,004 ± 0,012. Fremddaten je Startjahr
(1-Jahres-Konten 2006–2021): weniger Busts in 11 von 16 Jahren (gleich in 3, mehr in 2009 und 2011), mehr
Auszahlungen in 9 von 16 Jahren (`Replikat_v7/ergebnisse/e3.json`).

RSI21 **allein** (ohne Konto, 2006–2025, R × Gewicht): Sharpe (Wochen) 1,23 → **1,36**, Profitfaktor 1,69 → 1,89,
längste Verlustserie 21 → 16 Trades, größter Rückgang 24,4 → 20,9 R.

**Ehrlich bewertet:** Der Hauptgewinn ist **weniger Busts** bei gleichen bis etwas mehr Auszahlungen – nicht mehr
Ertrag. Die Regeln von RSI21 v3.4 sind im Konto nahe an ihrem Optimum. Die Variante mit dem höchsten RSI21-Ertrag
(Abschnitt 3.5) steigert die Busts im Konto stark und wurde deshalb **nicht** übernommen. Der Volumen-Filter hat
einen Schwachpunkt: Auf einem zweiten Gold-Feed mit echtem MT5-Tickvolumen (2018–2024) bestätigt er sich nicht
(Abschnitt 3.7). Er lässt sich mit `R21VolFaktor=0` abschalten; die Risiko-Umschichtung allein ist ebenfalls besser
als 6.10.

## 2. Daten und Werkzeug

- **Kursdaten neu aufgebaut** aus den Quellen des Datenberichts (`extdata/scripts/run_all.sh`). Die SHA-256 der
  Ergebnisdateien stimmen mit dem Datenbericht überein (NAS100_ext `dfef735d…87ab`, XAUUSD_ext `8532e33b…b462`).
- **Die GFT-Exporte 2022–2026 liegen nicht im Repo.** Ersatz („Ersatz-GFT“): Fremddaten 2022-01-03 … 2025-12-31
  (Gold Dukascopy, NAS100 MT5-Broker-Export), Gold-Spread je Jahr auf den GFT-Median skaliert (7/8/9/22 statt
  30/30/33/51 Punkte; ohne diese Skalierung waren die Gold-Fades zu teuer und das Konto zu schwach). 6.10 erreicht
  darauf 8,14 Auszahlungen / 0,03 Busts (Bericht 6.10 auf den Originaldaten 2022–26: 7,51 / 0,00).
- **Gegenprobe:** 6.10 auf den Fremddaten 2006–21 neu gerechnet: 1,99 / 0,34 / 511 $ gegen 2,02 / 0,40 / 503 $ im
  Bericht 6.10 (gleiche Daten; Unterschied aus Bibliotheksversionen, im Rauschen).
- **RSI21-Labor** (`Replikat_v7/`): Signale vektorisiert (identisch mit `sig5.r21_signals`, 4632 von 4632), eigener
  Positions-Simulator ohne Konto (Plätze A/B, Verlustgrenze je Tag, Wochenend-Pause mit Wiederaufnahme, Swap,
  Kommission). Kennzahlen: R × Gewicht je Jahr, Sharpe der Wochensummen, Bust-Ersatz (Rückgang ≥ 12 R),
  „Risiko-Parität“ (R je Jahr bei gleich vielen Bust-Ersatz-Ereignissen wie 6.10). Epochen 2006–10, 11–15, 16–19,
  20–21, 22–23, 24–25.
- **Kontomotor** wie x39 (Replikat v6): alle Module, GFT-Regeln, rollierende Konten 1/2/3 Jahre, Störungen.

## 3. Was gesucht und geprüft wurde

Rund 150 Varianten ohne Konto, über 100 im Kontomotor. Die wichtigsten:

### 3.1 RSI21 allein – die Regeln einzeln abgeschaltet (2006–2025)

| Variante | Trades/J | Ø R | R/J | längste Serie | Sharpe | R/J bei gleichem Bust-Ersatz |
|---|---:|---:|---:|---:|---:|---:|
| **6.10** | 50,9 | +0,39 | +19,9 | 21 | 1,23 | +20,1 |
| ohne Folgesignal | 72,5 | +0,27 | +19,9 | 19 | 1,07 | +17,1 |
| ohne Kreuz-Bestätigung (beide) | 85,4 | +0,32 | +27,5 | 24 | 1,28 | +20,3 |
| NAS ohne Kreuz (Gold: Kreuz oder Gate) | 75,1 | +0,38 | +28,2 | 20 | 1,36 | +22,7 |
| ohne H4-Divergenz | 51,5 | +0,39 | +19,8 | 21 | 1,23 | +20,0 |
| Shorts ohne Regime | 69,4 | +0,27 | +18,4 | 20 | 1,01 | +14,9 |
| NAS-Longs ohne SMA200 | 53,2 | +0,38 | +20,0 | 23 | 1,21 | +22,9 |
| ohne zweiten Platz | 28,7 | +0,36 | +10,5 | 11 | 1,16 | +18,6 |
| Gold nur M15 | 45,5 | +0,45 | +20,5 | 16 | 1,31 | +24,4 |

Folgesignal und Regime-Regel für Shorts tragen. Die H4-Divergenz ist neutral. Die Kreuz-Bestätigung kostet RSI21
allein viel Ertrag – im Konto ist sie aber der wichtigste Risikoschutz (3.5).

### 3.2 Signal, Zeitfenster, Zeitebenen

- **RSI-Länge:** 21 ist das Optimum (14: Sharpe 1,11, 18: 1,37, 24: 1,29, 28: 1,06 – jeweils mit den übrigen
  Regeln der Standalone-Bestvariante).
- **Schwelle:** 72,5 viel schlechter (Ø R +0,17), 77,5 besser je Trade (+0,51), aber weniger R je Jahr.
- **Zeitebenen:** M15 trägt fast alles. M5 zusätzlich: Sharpe 1,23 → 1,06. H4: bedeutungslos (0,7 Signale/J).
  Gold M30 ist schwach (+0,09 R long, −0,08 R short je Trade).
- **Zeitfenster:** Gold schon ab 3:00 NY (London) bringt allein mehr Ertrag (Sharpe aber 1,22). Im Konto:
  2022–25 7,51 statt 8,07 Auszahlungen, 2006–21 2,32 statt 1,99 Auszahlungen bei 0,47 statt 0,34 Busts.
  NAS über 13:00 NY hinaus: schlechter.

### 3.3 Ausstiege

Stop 2 ATR und Ziel 2,64 / 2,2 R sind auf einem Plateau. Weitere Stops (3–6 ATR), Break-even, Stop-Nachzug,
Teilgewinn, Zeit-Stop und frühere Zeit-Exits heben die Trefferquote, aber nicht die risikobereinigte Leistung. Im
Konto: Zeit-Exit 24 h 7,54 statt 8,07 Auszahlungen (Ersatz-GFT). Größere Ziele (ab 4,0 / 3,5 R): mehr R je Jahr,
aber Verlustserien bis 42 Trades.

### 3.4 Filter und Ideen aus der Recherche (Web und YouTube)

| Idee | Quelle / Gedanke | Ergebnis (RSI21 allein) |
|---|---|---|
| Einstieg per Limit beim Rücksetzer | „Pullback-Strategien“ (YouTube) | schlechter: gefüllt werden die schwachen Trades (Ø R +0,47 → +0,41 bei 0,25 R, nur 54 % gefüllt) |
| RSI-Bereichswechsel (Cardwell/Brown: Bullenmarkt-RSI 40–80, Kauf beim Rücksetzer auf 40–50) | Bereichsregel nach einem RSI21-Signal | kein Vorteil (Ø R −0,35 bis 0,00 je nach Einstellung) |
| Trend-Filter höherer Zeitebenen (H4-RSI, Tages-RSI, SMA50, Ausbruch) | „RSI + EMA/SMA-Trend“ | höherer Ø R, aber weniger Trades; Sharpe gleich oder schlechter |
| ADX, ATR-Rang (Volatilitäts-Regime, vgl. VIX-Filter) | „RSI-Momentum mit VIX-Filter“ | neutral |
| Regime-Wächter wie bei den Fades | PF der letzten 20 Signale > 1 | halbiert den Rückgang, kostet aber ein Viertel des Ertrags; Sharpe 1,13 |
| **Volumen-Bestätigung** | „Momentum nur mit Volumen“ | **Signale unter 1,0 × Mittel: +0,18 R, Sharpe 0,34; ab 1,5 × Mittel: Sharpe 1,36** |

### 3.5 Warum nicht „NAS ohne Kreuz-Bestätigung“?

Die beste Variante **ohne Konto** ist: NAS ohne Kreuz-Bestätigung, NAS-Longs ohne SMA200-Bedingung, Gold nur M15.
Sie hat 76 Trades/J, Sharpe 1,52 statt 1,23 und ist in allen sechs Epochen besser. Im Konto ist das anders:

| Konto (Auszahlungen / Busts je Jahr) | Ersatz-GFT 2022–25 | Fremddaten 2006–21 |
|---|---|---|
| 6.10 (RSI21 0,50 %) | 8,14 / 0,028 | 1,99 / 0,342 |
| NAS ohne Kreuz, RSI21 0,50 % | 8,21 / 0,249 | 2,54 / 0,589 |
| Standalone-Bestvariante, RSI21 0,50 % | 7,90 / 0,316 | 2,66 / 0,421 |
| Standalone-Bestvariante, RSI21 0,35 % | 7,70 / 0,169 | 2,30 / 0,245 |
| Standalone-Bestvariante, RSI21 0,20 % | 7,30 / 0,048 | – |
| NAS-Kreuz-Schwelle 45 statt 55 ¹ | 8,21 / 0,095 | 2,22 / 0,495 |

¹ 8 statt 16 Störungen (Ersatz-GFT). Fremddaten jeweils 4 Störungen.

2006–21 bringt die Variante bei gleichen Busts rund 25 % mehr Auszahlungen. 2022–25 hat sie bei **jeder**
Risikostufe mehr Busts als 6.10 – selbst mit 0,20 % Risiko. Der mittlere größte Rückgang je Konto steigt bei 0,50 %
von 399 $ auf 459–473 $: Die zusätzlichen NAS-Trades verlieren offenbar in denselben Phasen wie die übrigen Module. Die
Kreuz-Bestätigung (Gold-RSI in dieselbe Richtung) wirkt im Konto als Risikoschutz. Sie bleibt.

### 3.6 Konto-Raster um 6.10 (Auswahl, Ersatz-GFT mit 8 Störungen, Fremddaten mit 4)

| Variante | Ersatz-GFT: Ausz / Busts / Netto | Fremddaten: Ausz / Busts / Netto |
|---|---|---|
| 6.10 | 8,07 / 0,038 / 2447 | 1,99 / 0,342 / 511 |
| ohne zweiten Platz | 7,70 / 0,001 / 2196 | 1,61 / 0,238 / 397 |
| max. 1 RSI21-Verlust je Tag | 8,15 / 0,026 / 2468 | 2,04 / 0,350 / 522 |
| Gold-Faktor 0,5 | 7,96 / 0,001 / 2348 | 1,96 / 0,250 / 499 |
| RSI21-Budget 0,8 % | 8,25 / 0,003 / 2483 | 1,97 / 0,360 / 498 |
| Ziel NAS 2,6 R | 8,21 / 0,059 / 2446 | 2,03 / 0,350 / 519 |
| Zeit-Exit 576 M5 | 7,81 / 0,013 / 2339 | 1,99 / 0,327 / 507 |
| Volumen ≥ 1,5 × Mittel | 8,08 / 0,043 / 2462 | 2,13 / 0,311 / 555 |
| Volumen ≥ 2,0 × Mittel | 8,26 / 0,001 / 2513 | 1,94 / 0,251 / 501 |

Feinbewertung (Ersatz-GFT 16 Störungen, Fremddaten 8; Ausz / Busts / Netto / mittlerer größter Rückgang):

| Variante | Ersatz-GFT 2022–25 | Fremddaten 2006–21 |
|---|---|---|
| 6.10 | 8,14 / 0,028 / 2459 / 399 | 1,94 / 0,364 / 494 / 515 |
| Gold 0,5 + Risiko 0,6 | 8,20 / 0,014 / 2462 / 398 | 2,02 / 0,322 / 507 / 517 |
| **Volumen 1,5 + Gold 0,5 + Risiko 0,6 (= 6.20)** | **8,20 / 0,004 / 2467 / 383** | **2,09 / 0,259 / 536 / 505** |
| … + max. 1 Verlust je Tag | 8,21 / 0,005 / 2474 / 383 | 2,07 / 0,251 / 532 / 503 |
| … Volumen 1,3 | 7,93 / 0,000 / 2355 / 390 | 2,00 / 0,301 / 508 / 511 |
| … Volumen 1,7 | 8,30 / 0,000 / 2494 / 385 | 2,00 / 0,279 / 508 / 501 |
| … Gold 0,4 | 8,13 / 0,000 / 2409 / 380 | 1,98 / 0,247 / 504 / 498 |
| … Gold 0,6 | 8,16 / 0,020 / 2465 / 396 | 2,14 / 0,318 / 557 / 507 |
| … Risiko 0,55 | 8,09 / 0,004 / 2394 / 386 | 1,94 / 0,258 / 496 / 502 |
| … Risiko 0,65 | 8,13 / 0,001 / 2433 / 390 | 2,16 / 0,282 / 559 / 505 |
| … Risiko 0,7 | 8,01 / 0,021 / 2443 / 408 | 2,18 / 0,328 / 562 / 507 |

Alle Nachbarn liegen bei den Busts deutlich unter 6.10 und bei den Auszahlungen gleich oder darüber: ein Plateau,
kein Einzeltreffer. „Max. 1 Verlust je Tag“ bringt nichts Messbares und bleibt bei 2. Beide Teile tragen: nur Gold 0,5 +
Risiko 0,6 ergibt 8,20 / 0,014 bzw. 2,02 / 0,322, nur der Volumen-Filter 8,09 / 0,021 bzw. 2,08 / 0,306.

### 3.7 Gegenprobe: Volumen je Datenquelle

Das Tick-Volumen stammt je nach Zeitraum aus verschiedenen Quellen. Ø R der 6.10-Trades (RSI21 allein) mit
Volumen ≥ 1,5 × Mittel gegen < 1,5 × Mittel:

| Symbol, Quelle | ≥ 1,5 × Mittel | < 1,5 × Mittel |
|---|---|---|
| Gold, OANDA-Tickanzahl 2006–2011 | +0,16 R (105 Trades) | −0,38 R (38) |
| Gold, Dukascopy-Ticks 2011–2016 | +0,27 R (163) | −0,33 R (41) |
| Gold, Dukascopy-Proxy 2016–2025 | +0,61 R (234) | +0,14 R (71) |
| NAS, OANDA-Tickanzahl 2006–2020 | +0,42 R (184) | +0,71 R (17) |
| NAS, MT5-Broker 2021–2025 | +0,77 R (125) | −0,13 R (14) |
| **Gold, MT5-Broker 2018–2024** (zweiter Feed, `t_volmt5.py`) | +0,43 R (173) | +0,62 R (53) |

In drei Gold-Quellen über 20 Jahre trägt der Filter deutlich. Auf dem MT5-Broker-Feed 2018–2024 – dessen Tickvolumen
dem von GFT am nächsten kommt – bestätigt er sich für Gold **nicht** (dort waren die Trades mit wenig Volumen sogar
besser; kleine Zahl, aber ein Warnzeichen). Für NAS gibt es zu wenige Trades mit wenig Volumen für ein Urteil.

## 4. Was 6.20 ändert

| Eingabe | 6.10 | **6.20** | Wirkung |
|---|---:|---:|---|
| `R21VolFaktor` (neu) | – | **1.5** | RSI21-Einstieg nur, wenn Tick-Volumen der Signalkerze ≥ 1,5 × Mittel; 0 = aus (wie 6.10) |
| `R21VolKerzen` (neu) | – | **50** | Kerzen für das Mittel, inklusive Signalkerze, gleiche Zeitebene (wie `VolRel` des DEADBAND-Moduls) |
| `R21GoldMult` | 0,70 | **0,50** | kleinere Gold-RSI21-Positionen |
| `R21RiskPct` | 0,50 | **0,60** | größere NAS-RSI21-Positionen (M15: 0,75 % statt 0,625 %; Gold M15: 0,375 % statt 0,4375 %) |

Umsetzung in `HandleR21`: Die Prüfung liegt nach Platzwahl und Hedging-Sperre, vor der Größenberechnung. Das
Signal-Gedächtnis (Folgesignal) bleibt unverändert. Fehlen die Kerzen, gibt es keinen Einstieg (Meldung
„Tick-Volumen … nicht verfügbar“). Ohne Tick-Volumen (Mittel 0) lässt die Prüfung durch – wie das Replikat.

Presets: `DEADBAND_LIVE4_Echtbetrieb.set` = Voreinstellungen 6.20. `DEADBAND_LIVE4_610_Sicher.set` gilt weiter
(RSI21 dort aus; die neuen Eingaben sind der Vollständigkeit halber eingetragen). Rückweg: `rollback_6.10/`.

## 5. Inbetriebnahme

1. `DEADBAND_LIVE4.mq5` nach `MQL5\Experts\` kopieren, in MetaEditor kompilieren (erwartet: 0 Fehler).
2. Im Journal beim Start: `DEADBAND4: 6.20 RSI21 Volumen-Bestaetigung AN (Tick-Volumen der Signalkerze >= 1.50 x
   Mittel der letzten 50 Kerzen) | Risiko 0.60 % je Trade x Gewicht, Gold x0.50`.
3. Strategietester („Jeder Tick anhand realer Ticks“, XAUUSD.x M15): Neben den RSI21-Einstiegen erscheinen Zeilen
   `RSI21: LONG-Signal M15 ohne Volumen-Bestaetigung (0.87 x Mittel < 1.50) - kein Einstieg`. Etwa jedes siebte
   Folgesignal wird so ausgelassen (2006–25: 51 → 44 Trades je Jahr ohne Konto).
4. Alles Weitere wie im Bericht 6.10 (Kontoerkennung, Presets, nur eigener PC).

## 6. Grenzen und Hinweise

1. **Ersatz- statt Originaldaten:** Die GFT-Exporte fehlen im Repo. Die Ersatzdaten enden 2025-12-31. Die
   Zahlen für 2022–25 sind daher mit den Berichten 6.00/6.10 **nicht direkt vergleichbar**. Vergleichbar sind
   6.10 und 6.20 unter gleichen Annahmen.
2. **Tick-Volumen:** Im Replikat ist Gold ab 2016 ein Proxy aus dem Dukascopy-Volumen, NAS stammt von OANDA bzw.
   einem anderen MT5-Broker, NAS 2020-05…12 hat kein Volumen. Auf einem zweiten Gold-Feed mit echtem
   MT5-Tickvolumen (2018–2024) bestätigt sich der Filter nicht (3.7). Mit GFT-Tickvolumen ist er ungeprüft. Wer ihm
   nicht traut, setzt `R21VolFaktor=0`: Übrig bleibt die Umschichtung (Gold 0,5, Risiko 0,6), im Replikat allein
   schon besser als 6.10 (8,20 / 0,014 bzw. 2,02 / 0,322 Auszahlungen / Busts).
   Kleiner Unterschied zum Replikat: Hat das Terminal weniger als `R21VolKerzen` Kerzen der Zeitebene, lässt die EA
   das Signal aus (Meldung „Tick-Volumen … nicht verfuegbar“); das Replikat ließ die ersten 50 Kerzen der Daten durch.
   Mit „Max. Balken im Chart = Unbegrenzt“ tritt das nicht auf.
3. **Busts sind seltene Ereignisse.** Auf den Ersatzdaten stammen sie überwiegend aus einer Phase (Juni 2025, Fades
   im Verlust). Die Senkung von 0,028 auf 0,004 je Jahr ist deshalb weniger sicher als die Richtung, die beide
   Datensätze zeigen.
4. **Nicht kompiliert, nicht im Tester** (kein MetaEditor in dieser Umgebung). Geprüft: Klammern, Format-Aufrufe,
   Eingaben gegen die Presets (206 von 206), zusätzlich ein unabhängiges Code-Review der Änderung (keine Kompilier-
   oder Logikfehler gefunden; die Build-Kennung in Kontobericht und Panel wurde danach auf 6.20 gesetzt).
   `CopyTickVolume` wird wie in der bestehenden `VolRel` genutzt.
5. Die Ausprägung „NAS ohne Kreuz“ (3.5) ist **nicht** als Eingabe eingebaut. Wer RSI21 **allein** auf einem Konto
   handelt (ohne Fades und Noise), findet sie im Labor (`r7kand.k1gn`); im Kombi-Konto erhöht sie die Busts.

## 7. Quellen der Recherche

- [RSI Range Rules (LuxAlgo)](https://www.luxalgo.com/library/concept/rsi-range-rules/),
  [Cardwell RSI Range-Shift (TradingView)](https://www.tradingview.com/chart/XAUUSD/aB1EGX45-The-Cardwell-RSI-Range-Shift-Strategy/)
- [RSI Momentum Strategy (QuantifiedStrategies)](https://www.quantifiedstrategies.com/rsi-momentum-strategy/),
  [70-30 RSI Strategy (QuantifiedStrategies)](https://www.quantifiedstrategies.com/70-30-rsi-trading-strategy/)
- [Momentum RSI mit VIX-Filter (Options Cafe)](https://options.cafe/blog/momentum-rsi-strategy-backtest-results/)
- YouTube (nur Titel/Beschreibungen, youtube.com war aus der Umgebung gesperrt):
  [RSI Momentum Strategy (Trading Rules And backtest)](https://www.youtube.com/shorts/hDrjFDpT_M8),
  [Most Traders Use RSI Wrong – Try This Pullback Strategy](https://www.youtube.com/watch?v=UOr6x8lGjaI),
  [RSI Divergence (GOLD) Trading Strategy](https://www.youtube.com/watch?v=RJH-2TD1fZk),
  [RSI + MACD Momentum Combo](https://www.youtube.com/watch?v=Pa4j1YDCiKM),
  [RSI and MA Strategy with Trailing Stop Loss](https://www.youtube.com/watch?v=AP1TLQxSHjM)
