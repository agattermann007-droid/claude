# DEADBAND V9 – Build 9.00 (Trendwende-Prüfung)

Bericht vom 16.10.2026 · GFT Instant Premium 10k · Grundlage: DEADBAND V8 Build 8.10 vom 04.10.2026

## 1. Kurzfassung

**Ergebnis:** Keine der 37 vorab festgelegten Änderungen hat alle vier Übernahmeregeln bestanden. **V9 handelt
deshalb laut Protokoll genau wie 8.10.** Neu ist nur der verlangte Trendwende-Bericht (TW) im Journal. Er läuft
über die Eingabe `TwBericht` (Voreinstellung an) und wirkt nicht auf Orders, Größen, Panel oder Kontologik.

**Warum keine Handelsänderung:**

- **Die Tagesregeln erkennen die Oktober-Wende zu spät.** R1, R3, R5 und R8 schlagen erst nach dem Schluss vom
  14.10. an. Sie hätten nur die drei Trades vom 15./16.10. gesperrt, zusammen −1,07 R. Die schnellste Regel ist
  R2 ab dem 13.10. mit 5 Trades und −2,38 R. Die Verluste vom 06., 12. und 13.10. liegen vor jedem Tagessignal.
- **Über 2022–2026 sperren dieselben Regeln im Mittel Gewinner.** Gesperrte Live-Trades in Fenster B:
  R1 +50,0 R, R8 +57,9 R, R3 +28,5 R, Noise-Area-Veto +34,5 R.
  - Einzige Ausnahme ist R9 (Vola-Sprung) mit −3,0 R. R9 ist aber in 5 von 9 Startjahren nicht besser als 8.10.
  - In Fenster A sperren die Regeln kaum etwas, weil die Listen-Fades dort selten live waren (Abschnitt 9).
- **Verlustserien wie im Oktober sind normal.** In 11 aufeinanderfolgenden NAS-Long-Trades ≤ −3,5 R kam
  2022–09/2026 achtmal vor, also etwa 1,7-mal im Jahr. Die 20 Trades danach brachten im Mittel +3,6 R. Das ist so
  viel wie jedes andere 20er-Fenster (+3,5 R). Nach einer Serie zu sperren hätte also nichts gebracht.

**Zahlen 8.10 = V9** (Replikat 9, freie Kursdaten; frisches 10k-Konto an jedem 3. Handelstag;
Netto/J = 0,8 × Auszahlungen − 148,50 $ je Pleite):

| Fenster | 1 Jahr | 2 Jahre |
|---|---:|---:|
| A 2016–2021 | 4,54 Auszahlungen/J · 1.064 $/J netto · 0 Pleiten | 3,92 · 913 $ · 0 |
| B 2022–10/2026 | 13,41 Auszahlungen/J · 3.031 $/J netto · 0 Pleiten | 14,05 · 3.172 $ · 0 |

**Stand der Prüfung:**

- `DEADBAND_V9.mq5` ist **NICHT KOMPILIERT ERSTELLT**. Vor dem Einsatz bitte im MetaEditor kompilieren und im
  Strategietester mit echten Ticks prüfen (Abschnitt 11).
- Der neue Code wurde mechanisch nach C++ übersetzt und gegen den Python-Nachbau gerechnet: 0 Abweichungen
  (Abschnitt 10).

## 2. Meilensteine

| Meilenstein | Stand | Beleg |
|---|---|---|
| 1 Daten geladen | **teilweise** | Freie M5-Daten 2010–10/2026 von GitHub (Abschnitt 4). Der GFT-Export aus deinem MT5 fehlt noch; das Exportskript liegt in `V9/export/`. NAS endet in den freien Daten am 25.09.2026. |
| 2 Nachbau abgeglichen | **Gold ja, NAS offen** | Alle 4 Gold-Live-Trades vom Oktober werden auf der richtigen Kerze gefunden (Einstieg/Stop/Ziel auf 0,07 Punkte genau, Ausnahme X0400-Einstieg +0,36). NAS-Oktober ist ohne Kurse nicht prüfbar. Kontoebene: Replikat 9 rechnet 2022–25 mit 14,65 Auszahlungen/J und 3.250 $/J. Der V8-Kopf nennt auf GFT-Daten 14,30 und 3.019 $/J. |
| 3 Tests gerechnet | **ja** | 37 Konfigurationen, Kontoebene A/B × 1/2 Jahre, Signalebene, Kosten-Stress, Stressfenster (Abschnitte 6–9). |
| 4 V9 gebaut | **ja, nicht kompiliert** | `DEADBAND_V9.mq5` (7.802 Zeilen), C++-Prüfung (Abschnitt 10), `DEADBAND_V9_Echtbetrieb.set` (315 Eingaben). |
| 5 Bericht | **ja** | diese Datei |

## 3. Die 17 Live-Trades vom 01.–16.10.2026

Summe −235,17 $:

- Gold: 4 Trades, +7,17 $.
- NAS: 13 Trades, −242,34 $.
  - Noise: +21,34 $.
  - LW-Short: −45,47 $.
  - **11 NAS-Long-Fades + S0830: −218,21 $ = −3,55 R**, davon 4 Gewinner.

Der NAS fiel in dieser Zeit von etwa 31.290 (Einstieg am 06.10.) auf etwa 29.410 (Einstieg am 16.10.), also um rund 6 %.
In der Tabelle stehen die Tagesregeln des letzten abgeschlossenen Servertags in Gegenrichtung zum Trade. NAS-Tageskerzen
ab dem 26.09. stammen aus den NQ-Futures, Faktor 0,99861.

| Einstieg (Server) | Sym | Richtung | Modul | Ergebnis | R | aktive Regeln (Stand) |
|---|---|---|---|---:|---:|---|
| 01.10. 20:25 | XAU | Short | X1000S | −68,32 $ | −1,12 | – (30.09.) |
| 05.10. 18:00 | NAS | Long | Noise | +21,34 $ | – | – |
| 06.10. 11:35 | XAU | Short | X0300S | −74,72 $ | −1,02 | – (05.10.) |
| 06.10. 19:35 | NAS | Long | N1100 | −33,59 $ | −0,57 | – (05.10.) |
| 06.10. 21:40 | NAS | Long | N1300/N1330 | +8,56 $ | +0,30 | – |
| 07.10. 04:10 | NAS | Long | N1800 | +11,94 $ | +0,21 | – (06.10.) |
| 07.10. 22:10 | NAS | Long | N1300/N1330 | +14,46 $ | +0,25 | – |
| 08.10. 16:55 | XAU | Short | X0630 | +64,71 $ | +0,88 | – (07.10.) |
| 09.10. 14:05 | XAU | Long | X0400 | +85,50 $ | +1,22 | R1, R5, R7, R8 (08.10.) |
| 12.10. 16:35 | NAS | Short | LW | −45,47 $ | −1,00 | R1, R5, R6, R8 aufwärts (09.10.) |
| 12.10. 19:55 | NAS | Long | N1100 | −23,48 $ | −0,34 | – (09.10.) |
| 13.10. 04:05 | NAS | Long | N1800 | −75,67 $ | −1,02 | – (12.10.) |
| 14.10. 16:00 | NAS | Long | S0830 | −64,97 $ | −1,02 | R2 (13.10.) |
| 14.10. 19:35 | NAS | Long | N1030/N0930 | −15,27 $ | −0,28 | R2 (13.10.) |
| 15.10. 19:35 | NAS | Long | N1030/N0930/N1100 | +34,67 $ | +0,94 | R1, R2, R3, R4, R5, R8 (14.10.) |
| 16.10. 19:50 | NAS | Long | Fade | −58,35 $ | −1,01 | R1, R2, R3, R5, R8 (15.10.) |
| 16.10. 19:50 | NAS | Long | Fade | −16,51 $ | −1,00 | R1, R2, R3, R5, R8 (15.10.) |

**Muster:**

1. **Kauf in einen Abwärtsschub.** Alle 11 NAS-Long-Fades kauften Schwäche während eines Rückgangs von 6 %.
   - Die 4 Gewinner waren klein: +0,21 bis +0,94 R.
   - Vier Verlierer endeten am vollen Stop (−1 R). Drei weitere schloss der EA vorher über die Zeit (−0,28 bis −0,57 R).
2. **Ungleiche Ziele.** N1330 und N1300 zielen auf die Range-Mitte, im Median 0,32 und 0,52 R, bei 1 R Stop.
   Sie brauchen also rund 75 % Treffer. Historisch erreichen sie das (2022–26: 78 % und 73 %), an Trendtagen nicht.
3. **Häufung am Ende.** Vom 12. bis 16.10. kamen 7 Long-Trades mit −3,73 R zusammen. Vom 06. bis 07.10. waren es noch +0,19 R.
4. **Tagesregeln kommen zu spät.**
   - R2 schlägt ab dem 13.10. an (5 Trades, −2,38 R).
   - R1, R3, R5 und R8 erst ab dem 14.10. (3 Trades, −1,07 R).
   - R4 hätte nur den Gewinner vom 15.10. gesperrt.
   - R6, R7, R9 und R10 hätten keinen Trade gesperrt.
5. **Gold-Shorts:** 3 Trades mit −78,33 $. Keine Aufwärtsregel war aktiv, die Verluste sind also kein Regime-Problem.
   Der Gold-Long X0400 brachte +85,50 $.
6. **Historisch normal.** Episoden mit ≤ −3,5 R in 11 aufeinanderfolgenden NAS-Long-Live-Trades gab es in B achtmal:
   01.02.2023, 19.07.2023, 04.12.2023, 19.04.2024, 07.08.2024, 10.02.2026, 01.04.2026 und 13.07.2026.
   - Die 20 Trades danach brachten im Mittel +3,63 R. Alle 20er-Fenster zusammen liegen bei +3,55 R.
   - In A gab es nur 29 NAS-Long-Live-Trades und keine solche Episode.

## 4. Daten

Der GFT-Export war beim Rechnen nicht verfügbar. Die GFT-CSV in Drive (`NAS100_x_M5.csv`, `XAUUSD_x_M5.csv`, 28–30 MB)
enden am 28.08.2026 und liegen über dem 10-MB-Limit des Drive-Zugriffs. Andere Kursserver (Dukascopy, Yahoo, Stooq) sind
von hier gesperrt. Auf deine Anweisung („hol dir die Daten selber“) habe ich freie Daten von GitHub geladen
(Skript `replikat/fetch_raw.sh`, Aufbau `replikat/build_free.py`). Alle Daten wurden auf GFT-Serverzeit (NY + 7 h) und Bid
gebracht. Wo die Quelle keinen Spread hat, gilt ein Spread-Modell (NAS 1,63 bei 15.000, Gold 0,32 bei 2.000).

| Symbol | Quelle (GitHub) | Zeitraum |
|---|---|---|
| XAU | OANDA Mid, [FutureSharks/financial-data](https://github.com/FutureSharks/financial-data) | bis 31.08.2016 |
| XAU | Dukascopy M1 Bid/Ask, [Dypoi/XAUUSD_Dataset](https://github.com/Dypoi/XAUUSD_Dataset) | 09/2016–01.09.2026 |
| XAU | TradingView FX:XAUUSD M1, [navtemmt/xauusd-autodata](https://github.com/navtemmt/xauusd-autodata) | ab 09.09.2026 bis 15.10.2026 |
| NAS | OANDA Mid NAS100_USD (FutureSharks) | bis 08.05.2020 |
| NAS | HistData NSXUSD, [hizawye/better-backtest](https://github.com/hizawye/better-backtest) | 11.05.–31.12.2020 und 01.01.–13.02.2026 |
| NAS | MT5-Broker US100 M1, [ts4blader/market_data](https://github.com/ts4blader/market_data) | 2021–2025 |
| NAS | NAS100 1m, [getdata-finance/nas100-1m-ohlcv-index-historical-data](https://github.com/getdata-finance/nas100-1m-ohlcv-index-historical-data) | 26.03.–25.09.2026 |
| NAS D1 | NQ=F täglich, [Kubula-xu/claude-finance-data](https://github.com/Kubula-xu/claude-finance-data) | nur Oktober-Auswertung (26.09.–16.10.2026) |

Lücken:

- NAS 14.02.–24.03.2026 (39 Tage) und 01.–06.04.2022.
- Gold 02.–08.09.2026.

## 5. Recherche

| Quelle | Kernaussage | Folge für den Test |
|---|---|---|
| Gao, Han, Li, Zhou (2018): *Market Intraday Momentum*, Journal of Financial Economics 129, 394–414, [doi 10.1016/j.jfineco.2018.05.009](https://profiles.wustl.edu/en/publications/market-intraday-momentum/) | Die Rendite der ersten halben Stunde sagt die letzte halbe Stunde voraus (SPY). | Schluss-Momentum 15:30–15:55 (SM_L, SM_B) |
| Baltussen, Da, Lammers, Martens (2021): *Hedging Demand and Market Intraday Momentum*, JFE 142(1), 377–403, [doi 10.1016/j.jfineco.2021.04.029](https://pure.eur.nl/en/publications/hedging-demand-and-market-intraday-momentum/) ([PDF](https://www3.nd.edu/~zda/intramom.pdf)) | Intraday-Momentum in über 60 Futures, getrieben vom Absicherungsbedarf (negatives Gamma der Händler). | Grundlage von TD (schon in 8.10) und SM |
| Barbon, Buraschi (2021): *Gamma Fragility*, FIRS-Konferenz Boston, [Universität St. Gallen](https://alexandria.unisg.ch/handle/20.500.14171/110335) | Ist das Händler-Gamma negativ, verstärken sich Kursbewegungen; ist es positiv, kehren sie um. Der Volltext wurde hier nicht online geprüft; die Aussage stammt aus der bekannten Kurzfassung. | Fades sollten an Tagen mit negativem Gamma leiden. Es gibt keine Gamma-Daten, Ersatz sind R9, R10 und NA. |
| Zarattini, Aziz, Barbon (2024): *Beat the Market – An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)*, [SFI Research Paper 24-97](https://www.sfi.ch/de/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy) | Die Noise Area (14-Tage-Mittel der Abweichung vom Open je Uhrzeit) trennt Rauschen von Trendtagen. | Noise-Area-Veto NA, Tagesrichtung TR |
| Nagel (2012): *Evaporating Liquidity*, Review of Financial Studies 25(7), 2005–2039, [NBER w17653](https://nber.org/papers/w17653) | Umkehr-Strategien (Liquiditätsbereitstellung) verdienen mehr, wenn der VIX hoch ist. | Spricht **gegen** Vola-Sperren. Bestätigt: R10 sperrt in B +19,1 R. |
| Goulding, Harvey, Mazzoleni (2023): *Momentum Turning Points*, JFE 149(3), 378–406, [doi 10.1016/j.jfineco.2023.05.007](https://scholars.duke.edu/publication/1586630) | Regime aus schnellem und langsamem Momentum (Bulle, Korrektur, Bär, Erholung). | R6 (Bär), R7 (Korrektur) |
| Moreira, Muir (2017): *Volatility-Managed Portfolios*, Journal of Finance 72(4), 1611–1644, [doi 10.1111/jofi.12513](https://www.nber.org/papers/22208) | Weniger Risiko bei hoher Vola verbessert die Sharpe Ratio. Spätere Arbeiten (Cederburg u. a.; Barroso/Detzel, zitiert in [DeMiguel u. a. 2024](https://lbsresearch.london.edu/id/eprint/3716)) zeigen, dass das außerhalb der Stichprobe und nach Kosten oft nicht hält. | Halbes Risiko bei R9/R10 (H_R9, H_R10) |
| Grossman, Zhou (1993): *Optimal Investment Strategies for Controlling Drawdowns*, Mathematical Finance 3(3), 241–276, [doi 10.1111/j.1467-9965.1993.tb00044.x](https://ideas.repec.org/a/bla/mathfi/v3y1993i3p241-276.html) | Unter einer Drawdown-Grenze ist die beste Position proportional zum Überschuss über den Boden. | CPPI-Größen. Die V8-Pufferkurve 3,5/1,25/0,1 folgt schon dieser Idee. |
| Bailey, López de Prado (2014): *The Deflated Sharpe Ratio*, Journal of Portfolio Management 40(5), 94–107, [SSRN 2460551](https://papers.ssrn.com/abstract=2460551) | Wer viele Varianten testet, muss die beste abwerten, sonst gewinnt der Zufall. | Darum gilt ein festes Protokoll mit vier harten Regeln. Bei 37 Versuchen sind kleine Vorteile wie LW_940 (+8/+26/+22/−4 $) Rauschen (vgl. V8-Kopf: Faktor ±1 % verschiebt −0,57…+0,22 Ausz./J). |

## 6. Testprotokoll (vor den Tests festgelegt, unverändert gerechnet)

**Basis** ist 8.10, mit allen V8-Eingaben auf ihrer Voreinstellung.

**Regeln** (Datei `replikat/regime9.py`). Jede Regel nutzt nur den letzten abgeschlossenen Servertag (17:00–17:00 NY).
Das Abwärtsregime sperrt NAS-Long-Fades und S0830. Gold-Shorts werden gespiegelt geprüft: Dort sperrt das Aufwärtsregime.

| Regel | Abwärtsregime |
|---|---|
| R1 | Schluss < EMA20 und EMA20 fällt |
| R2 | Schluss − Schluss vor 5 Tagen ≤ −1,5 ATR14 |
| R3 | Schluss < EMA20 und 5-Tage-Änderung ≤ −1,0 ATR14 (rekonstruierte 8.20-Regel) |
| R4 | Änderung des letzten Tages ≤ −0,75 ATR14 |
| R5 | Schluss unter dem Tief der 10 Tage davor; an, bis ein Schluss über EMA10 liegt |
| R6 | Rendite 21 Tage < 0 und 252 Tage < 0 (Bär) |
| R7 | Rendite 21 Tage < 0 und 252 Tage > 0 (Korrektur) |
| R8 | Schluss ≤ Hoch der letzten 20 Tage − 2 ATR14 |
| R9 | mittlere Tagesspanne 5 Tage / 50 Tage > 1,3 (Vola-Sprung, symmetrisch) |
| R10 | Rang der 10-Tage-Vola unter den letzten 252 Tagen > 0,8 (symmetrisch) |
| NA | Tief der Signalkerze < min(O, PC) × (1 − σ) − 0,25 σ × min(O, PC), mit O = Open 9:30, PC = Vortagesschluss, σ = 14-Tage-Mittel von \|Schluss/O − 1\| je 5-min-Block |
| TR | Schluss der Signalkerze / O − 1 < −σ |

**Sperre** heißt: kein Live-Trade. Der Portfolio-Wächter rechnet weiter mit allen virtuellen Signalen, wie bei
`FadeAus`. **Halb** heißt: halbes Risiko.

**Kontoebene:**

- An jedem 3. Handelstag startet ein frisches 10k-Konto mit 250 bzw. 500 Handelstagen Laufzeit.
- Das Konto rechnet mit allen GFT-Regeln aus V8 (Replikat `eng9` = `eng6` aus V8 plus Schutz gültiger Tage, Puffer-Schwelle je Modul und Teilziel).
- Netto/J = 0,8 × Auszahlungen − 148,50 $ je Pleite (Neukauf).
- Fenster A = 2016–2021, B = 2022–16.10.2026 (NAS faktisch bis 25.09.2026). Konten müssen im Fenster enden.

**Übernahmeregeln** (alle müssen gelten):

1. In A und B, für 1 und 2 Jahre: netto höher und Pleiten nicht höher.
2. Sperren und halbes Risiko: Die Summe R der betroffenen Live-Trades ist in A und in B < 0.
3. Das Netto ist in mindestens 5/7 der Startjahre höher. Das sind 9 Startjahre (2016–2020, 2022–2025; 2021 und 2026
   haben weniger als 5 Konten), also mindestens 7. Jahre ohne Unterschied zählen nicht als positiv. Die Lesart
   „nur Jahre mit Unterschied“ ändert nichts: Jeder Kandidat scheitert zusätzlich an Regel 1.
4. Die Änderung besteht auch mit Spread ×1,5 und ×2.

## 7. Ergebnisse aller 37 Konfigurationen

**Lesehilfe:**

- Die BASIS-Zeile zeigt Netto/J und in Klammern Auszahlungen/J.
- Die Variantenzeilen zeigen die Netto-Differenz zu BASIS in $/J.
- Pleiten: in allen Konfigurationen 0.
- R2: Summe R der gesperrten Live-Trades in A / B, Anzahl in Klammern.
- R3: Startjahre mit höherem Netto.

| Variante | Inhalt | A 1 J | A 2 J | B 1 J | B 2 J | R1 | R2: Summe R gesperrt A / B | R3: Jahre + |
|---|---|---:|---:|---:|---:|:-:|---|:-:|
| **BASIS** | 8.10 = V9 | **1.064 $** (4,54) | **913 $** (3,92) | **3.031 $** (13,41) | **3.172 $** (14,05) | – | – | – |
| S_R1 | Sperre NAS-Long+S0830 bei R1 | +6 | +29 | +29 | −95 | nein | +1,8 (12) / +50,0 (316) nein | 7/9 ja |
| S_R2 | Sperre NAS-Long+S0830 bei R2 | −23 | +0 | +45 | −1 | nein | +0,9 (1) / +24,5 (122) nein | 3/9 nein |
| S_R3 | Sperre NAS-Long+S0830 bei R3 | −19 | −9 | +157 | +85 | nein | +1,0 (7) / +28,5 (176) nein | 6/9 nein |
| S_R4 | Sperre NAS-Long+S0830 bei R4 | −19 | −18 | −54 | −123 | nein | +2,5 (4) / +13,0 (98) nein | 4/9 nein |
| S_R5 | Sperre NAS-Long+S0830 bei R5 | +25 | +100 | −141 | −211 | nein | −0,2 (8) / +28,8 (192) nein | 4/9 nein |
| S_R6 | Sperre NAS-Long+S0830 bei R6 | +0 | +0 | −73 | −34 | nein | +0,0 (0) / +31,6 (88) nein | 2/9 nein |
| S_R7 | Sperre NAS-Long+S0830 bei R7 | +35 | +116 | −303 | −351 | nein | −0,7 (7) / +34,5 (211) nein | 4/9 nein |
| S_R8 | Sperre NAS-Long+S0830 bei R8 | −1 | +21 | −288 | −367 | nein | +3,0 (8) / +57,9 (299) nein | 5/9 nein |
| S_R9 | Sperre NAS-Long+S0830 bei R9 | +15 | +93 | +46 | +137 | ja | +0,5 (3) / −3,0 (129) nein | 4/9 nein |
| S_R10 | Sperre NAS-Long+S0830 bei R10 | +12 | +96 | −120 | −209 | nein | +0,5 (3) / +19,1 (192) nein | 2/9 nein |
| H_R9 | halbes Risiko NAS-Long+S0830 bei R9 | −4 | −1 | −49 | −60 | nein | +0,3 (3) / −1,5 (129) nein | 3/9 nein |
| H_R10 | halbes Risiko NAS-Long+S0830 bei R10 | −2 | +0 | +11 | +13 | nein | +0,3 (3) / +9,5 (192) nein | 3/9 nein |
| S_NA | Sperre NAS-Long+S0830 bei NA | +0 | +1 | +75 | +14 | ja | −1,0 (1) / +34,5 (162) nein | 3/9 nein |
| S_TR | Sperre NAS-Long+S0830 bei TR | −1 | +0 | +61 | +60 | nein | −3,8 (5) / +49,5 (241) nein | 2/9 nein |
| K_R3NA | Sperre NAS-Long+S0830 bei R3+NA | −18 | −8 | −74 | −51 | nein | −0,0 (8) / +54,6 (297) nein | 5/9 nein |
| K_R3R9 | Sperre NAS-Long+S0830 bei R3+R9 | −6 | +13 | +44 | +148 | nein | +1,5 (10) / +28,4 (240) nein | 6/9 nein |
| K_R6NA | Sperre NAS-Long+S0830 bei R6+NA | +0 | +1 | +22 | −18 | nein | −1,0 (1) / +44,5 (225) nein | 3/9 nein |
| K_R3R9NA | Sperre NAS-Long+S0830 bei R3+R9+NA | −6 | +14 | −116 | −58 | nein | +0,5 (11) / +55,5 (345) nein | 4/9 nein |
| G_R1 | Sperre Gold-Short bei R1 (aufwärts) | +0 | −0 | −314 | −430 | nein | +0,7 (1) / +40,8 (281) nein | 2/9 nein |
| G_R2 | Sperre Gold-Short bei R2 (aufwärts) | +0 | +0 | +40 | +35 | nein | +0,0 (0) / +16,2 (101) nein | 3/9 nein |
| G_R3 | Sperre Gold-Short bei R3 (aufwärts) | +0 | +0 | +114 | −63 | nein | +0,0 (0) / +18,8 (143) nein | 3/9 nein |
| G_R4 | Sperre Gold-Short bei R4 (aufwärts) | +0 | +0 | −16 | −28 | nein | +0,0 (0) / +21,8 (75) nein | 2/9 nein |
| G_R5 | Sperre Gold-Short bei R5 (aufwärts) | +0 | −0 | −179 | −336 | nein | +0,7 (1) / +14,0 (181) nein | 2/9 nein |
| G_R6 | Sperre Gold-Short bei R6 (aufwärts) | +0 | −0 | −350 | −486 | nein | +0,7 (1) / +39,5 (272) nein | 2/9 nein |
| G_R7 | Sperre Gold-Short bei R7 (aufwärts) | +0 | +0 | −27 | −2 | nein | +0,0 (0) / +6,9 (21) nein | 1/9 nein |
| G_R8 | Sperre Gold-Short bei R8 (aufwärts) | +0 | −0 | −324 | −532 | nein | +0,7 (1) / +51,1 (281) nein | 2/9 nein |
| G_R9 | Sperre Gold-Short bei R9 (aufwärts) | −8 | −4 | +30 | −118 | nein | +1,1 (2) / +14,0 (82) nein | 4/9 nein |
| G_R10 | Sperre Gold-Short bei R10 (aufwärts) | −4 | −3 | +146 | +99 | nein | +1,0 (2) / +17,2 (137) nein | 4/9 nein |
| Z_06 | Fade-Ziel mindestens 0,6 R | +2 | +1 | −142 | −235 | nein | – | 3/9 nein |
| Z_GS | Fade-Ziel Gegenseite | −31 | −60 | −687 | −1.041 | nein | – | 1/9 nein |
| Z_HH | halb an der Mitte, Rest bis Gegenseite mit Einstand | +16 | +13 | −157 | −232 | nein | – | 1/9 nein |
| LW_940 | LW erst ab 9:40 NY | +8 | +26 | +22 | −4 | nein | – | 6/9 nein |
| NS_R3 | NAS-Short-Fades nur im Abwärtsregime (R3) | −0 | +1 | +110 | +118 | nein | – | 2/9 nein |
| CPPI | CPPI: Grösse linear zum Puffer, voll ab 6 % | −148 | −85 | −190 | −240 | nein | – | 2/9 nein |
| SM_L | Schluss-Momentum 15:30-15:55 nur Long | −78 | −45 | +31 | −57 | nein | – | 5/9 nein |
| SM_B | Schluss-Momentum 15:30-15:55 beide Richtungen | +35 | +65 | −161 | −281 | nein | – | 3/9 nein |

**Am knappsten gescheitert:**

- **LW_940** (LW erst ab 9:40): A +8/+26, B +22/**−4** $/J. Das reicht nur in 6 von 9 Jahren. Mit Spread ×2 liegt A bei −40 $.
- **S_R9** (Sperre bei Vola-Sprung): auf Kontoebene überall besser (+15/+93/+46/+137 $). Die gesperrten Trades sind
  aber in A positiv (+0,5 R). Die Verbesserung trägt nur 4 von 9 Jahren (2025: −172 $), und mit Spread ×1,5 ist B
  schlechter (2.173 statt 2.447 $).
- **NS_R3** (NAS-Short-Fades im Abwärtsregime): B +110/+118 $, aber A −0 $. In A gibt es fast keine Signale.
  Nur 2 von 9 Jahren sind positiv.
- **S_R3** (die 8.20-Regel): B +157/+85 $, A −19/−9 $. Die gesperrten Trades waren Gewinner (+28,5 R in B).

## 8. Kosten-Stress (Regel 4, zur Information für die drei knappsten Varianten)

Netto/J, Auszahlungen/J in Klammern, Konten über 1 Jahr. Alle drei sind schon an den Regeln 1–3 gescheitert;
die Rechnung bestätigt das nur.

| Variante | Spread ×1,5: A 1 J | Spread ×1,5: B 1 J | Spread ×2: A 1 J | Spread ×2: B 1 J | besteht |
|---|---:|---:|---:|---:|:-:|
| BASIS | 792 $ (4,01) | 2.447 $ (10,84) | 691 $ (3,62) | 2.210 $ (9,56) | – |
| LW_940 | 771 $ (3,97) | 2.368 $ (10,80) | 651 $ (3,37) | 2.227 $ (9,64) | nein |
| NS_R3 | 792 $ (4,01) | 2.533 $ (10,74) | 691 $ (3,62) | 2.144 $ (9,43) | nein |
| S_R9 | 775 $ (3,93) | 2.173 $ (9,96) | 693 $ (3,63) | 2.163 $ (9,62) | nein |

## 9. Stressfenster

Signalebene: NAS-Long-Fades + S0830 bzw. Gold-Short-Fades, die laut Wächter live gehandelt worden wären.
Rechts steht, was jede Regel gesperrt hätte. Eine Auswertung je Stressfenster auf Kontoebene wurde nicht gerechnet.

| Fenster | Live-Trades | Summe R | gesperrt hätten (Trades / Summe R) |
|---|---:|---:|---|
| NAS-Long Feb-Mar 2020 | 1 | +0,1 | R9 1/+0,1, R10 1/+0,1 |
| NAS-Long 2022 | 126 | +37,1 | R1 68/+27,6, R2 24/+12,8, R3 32/+15,4, R4 14/+9,4, R5 45/+17,4, R6 58/+26,3, R7 3/+1,6, R8 62/+25,6, R9 4/+1,4, R10 36/+12,1, NA 32/+15,0, TR 39/+16,2 |
| NAS-Long Aug 2024 | 15 | +2,1 | R1 10/−1,3, R3 5/−3,1, R4 1/+0,1, R5 7/−2,6, R7 10/−1,3, R8 10/−1,3, R9 10/−1,3, R10 12/−0,9, NA 4/+1,6, TR 6/+1,5 |
| NAS-Long Apr 2025 | 21 | +0,9 | R1 17/−1,8, R2 8/−1,1, R3 8/−1,1, R4 4/+1,6, R5 8/−1,1, R6 4/−1,1, R7 16/+1,9, R8 13/+0,9, R9 10/−3,7, R10 21/+0,9, NA 1/+0,3, TR 3/−1,7 |
| Gold-Short Feb-Mar 2020 | 0 | +0,0 | – |
| Gold-Short 2022 | 49 | +2,6 | R1 28/+3,1, R2 9/−0,6, R3 18/+0,7, R4 11/+4,5, R5 18/−0,8, R6 9/+0,8, R7 18/+4,5, R8 23/+3,4, R9 5/+2,0, R10 21/−1,3 |
| Gold-Short Aug 2024 | 9 | +2,5 | R1 8/+3,0, R2 1/+0,4, R3 2/+1,9, R4 3/+1,9, R5 5/+2,5, R6 9/+2,5, R8 5/+2,5, R9 3/+1,0, R10 1/+0,4 |
| Gold-Short Apr 2025 | 11 | −0,9 | R1 10/−1,3, R2 5/−1,5, R3 5/−1,5, R4 2/−1,2, R5 9/−0,3, R6 11/−0,9, R8 10/−1,3, R9 11/−0,9, R10 11/−0,9 |

**Oktober 2026** (Live-Trades, Abschnitt 3): 11 Trades mit −3,55 R. Am meisten hätte R2 gerettet: 5 Trades, −2,38 R.

**Deutung:**

- In kurzen, scharfen Schocks (Aug 2024, Apr 2025, Okt 2026) hätten einzelne Regeln 1–4 R gespart.
- 2022 war für die NAS-Long-Fades das beste Jahr: +37,1 R aus 126 Trades. Gerade dort hätten alle Regeln Gewinner
  gesperrt, R1 allein 68 Trades mit +27,6 R.
- Im Bärenmarkt wirken die Fades also, in kurzen Schocks nicht. Kein Tagesfilter trennt beides vorab.
- Feb–Mar 2020: Die Listen-Fades waren fast nie live, weil der Portfolio-Wächter sie abgeschaltet hatte (PF ≤ 1,15).
  Darum ist Fenster A für Fade-Sperren schwach besetzt.

**Kennzahlen je Modul** (Live-Signale; A = 2016–21, B = 2022–09/2026):

| Modul | A: n | A: Summe R | B: n | B: Trefferquote | B: PF | B: Summe R | Ziel-Median (R) |
|---|---:|---:|---:|---:|---:|---:|---:|
| N1030 | 2 | −2,0 | 104 | 69 % | 2,13 | +32,9 | 1,00 |
| N1330 | 2 | +0,6 | 229 | 78 % | 1,58 | +17,9 | 0,32 |
| X0630 | 3 | +1,3 | 237 | 68 % | 1,43 | +29,0 | 0,76 |
| X0400 | 0 | +0,0 | 128 | 64 % | 1,32 | +14,9 | 0,79 |
| N1800 | 1 | +0,5 | 90 | 64 % | 1,46 | +12,3 | 0,83 |
| N0930 | 2 | −2,0 | 100 | 66 % | 1,93 | +24,7 | 1,16 |
| N1100 | 2 | −2,0 | 154 | 60 % | 1,71 | +34,5 | 1,20 |
| N1300 | 1 | +0,6 | 178 | 73 % | 1,57 | +20,6 | 0,52 |
| X0300S | 0 | +0,0 | 123 | 60 % | 1,56 | +23,1 | 1,03 |
| X1000S | 1 | +0,5 | 97 | 59 % | 1,26 | +8,4 | 1,17 |
| S0830 | 19 | +6,1 | 47 | 94 % | 5,86 | +14,6 | 0,35 |
| LW | 1146 | +228,0 | 917 | 38 % | 1,49 | +268,1 | – |
| XA | 706 | +5,5 | 591 | 49 % | 1,23 | +25,1 | 1,00 |
| TD | 176 | +12,9 | 128 | 62 % | 1,92 | +18,0 | – |

## 10. V9 – was gebaut wurde und wie es geprüft ist

`DEADBAND_V9.mq5` wird mit `build/patch_v9.py` aus `DEADBAND_V8.mq5` erzeugt. V8 wird nur gelesen
(sha256 74b9a8e9…92dc). Jede Einfügung hat genau einen geprüften Anker:

1. Kopfblock Build 9.00 mit Begründung und Zahlen.
2. `#property version "9.00"`.
3. Eingabegruppe „9.00: Trendwende-Bericht“ mit `TwBericht = true`.
4. TW-Variablen nach `nSym`.
5. OnInit: TW-Zustand zurücksetzen und Startzeile `DEADBAND9: Build 9.00 - Handel wie 8.10 | Trendwende-Bericht AN`.
6. `FadeLive`: `TwSignalMerken` merkt sich das Signal nur. Vor der Order wird nichts gerechnet und keine Kurse abgefragt.
7. `Durchlauf`: `TwBerichteAusgeben` läuft am Ende, nach allen Einstiegen und Ernten. Es gibt einmal je Servertag den
   Tagesstand je Symbol aus (400 abgeschlossene D1-Kerzen) und danach die gemerkten Signale (NAS: M5 der letzten
   45 Tage bis zur Signalkerze). Fehlen Kerzen, versucht es der EA nach 60 s erneut.
8. Die TW-Funktionen stehen am Dateiende.

Alle Eingaben, Kontologik und GFT-Regeln sind unverändert. Die Datei ist reines ASCII mit deutschen Kommentaren.
**Rückfall:** `TwBericht = false`. Dann laufen nur zwei zusätzliche `if`-Abfragen. Der Handel ist in beiden Fällen 8.10.

**Prüfung ohne MetaEditor:**

| Prüfung | Ergebnis |
|---|---|
| `build/tw_check.py`: TwSma/TwRegeln/TwNoise aus `tw_block.mq5` per Textersetzung (Arrays → `std::vector`) nach C++, `g++ -O2 -Wall -Wextra` | übersetzt; einzige Warnung: Parameter `o` in TwRegeln unbenutzt (harmlos) |
| D1-Regeln, ganze Historie, XAU 4.358 + NAS 4.314 Tage, alle 10 Regeln in beiden Richtungen, gegen `regime9.py` | **0 Abweichungen** |
| D1-Regeln wie im EA rollierend auf 400 Tagen, 3.959 + 3.915 Tage | **0 Abweichungen** |
| Noise Area je NAS-Signal (7.172 Fenster „Einstieg − 45 Tage … Einstieg − 1 min“) | letzte Kerze = Signalkerze in 7.172 von 7.172; Wert in beiden 6.515; **NA/TR 0 Abweichungen**; 24 Signale nur in Python mit Wert (Datenlücke Feb–Mar 2026: weniger als 15 Tage im 45-Tage-Fenster, der EA schreibt dann „ohne Wert“) |
| `build/tw_sim.py`: **ganzer** TW-Block (auch TwTagesbericht, TwSignalBericht, TwBerichteAusgeben) mit nachgebildeten MQL-Funktionen (CopyRates, PrintFormat, TimeCurrent …) | übersetzt, läuft |
| Signalpfad 01.01.2024–25.09.2026, 1.944 Signale aller Module, Journalzeile gegen `tests9.flags` | Tagesregeln **1.944/1.944 gleich**; NA/TR **1.062/1.062 gleich**; 108 NAS-Signale ohne Wert (außerhalb 9:30–16:00 oder Lücke) |
| MetaEditor-Kompilierung, Strategietester | **nicht gelaufen** (hier nicht verfügbar) |

**So hätte das Journal im Oktober ausgesehen** (Ausschnitt aus der Simulation, Replikat-Kurse; ohne NAS-M5 ab 26.09.):

```
DEADBAND9 TW NAS100.x Servertag 2026.10.13: Abwaertsregime [R2] | Aufwaertsregime [R1,R6,R8] | 400 D1-Kerzen | nur Bericht, kein Einfluss auf den Handel
DEADBAND9 TW Signal S0830 NAS100.x LONG: Tagesregeln abwaerts [R2] (Stand 2026.10.13) | Intraday M5-Historie endet 2026.09.25 vor der Signalkerze | nur Bericht, V9 handelt wie 8.10
DEADBAND9 TW NAS100.x Servertag 2026.10.14: Abwaertsregime [R1,R2,R3,R4,R5,R8] | Aufwaertsregime [R6,R8] | 400 D1-Kerzen | nur Bericht, kein Einfluss auf den Handel
DEADBAND9 TW Signal N1030 NAS100.x LONG: Tagesregeln abwaerts [R1,R2,R3,R4,R5,R8] (Stand 2026.10.14) | Intraday M5-Historie endet 2026.09.25 vor der Signalkerze | nur Bericht, V9 handelt wie 8.10
DEADBAND9 TW NAS100.x Servertag 2026.10.15: Abwaertsregime [R1,R2,R3,R5,R8] | Aufwaertsregime [R6] | 400 D1-Kerzen | nur Bericht, kein Einfluss auf den Handel
```

Im echten MT5 sind die M5-Kerzen vorhanden. Dort steht statt des Hinweises „NA JA/nein, TR JA/nein“.

**MQL-Stellen, die erst der MetaEditor bestätigt:**

- `CopyRates` mit Zeitraum.
- `datetime % 86400`.
- `StringToUpper` (ändert den String selbst).
- Vorwärtsaufrufe von Funktionen am Dateiende. V8 nutzt solche Aufrufe schon, z. B. `FadeDurchlauf`.

## 11. Grenzen und Annahmen

- **Freie statt GFT-Kurse.** Mehrere Quellen sind zusammengesetzt, Spreads zum Teil modelliert, es gibt Lücken (Abschnitt 4).
  Die Kontozahlen liegen nahe am V8-Kopf (14,65 statt 14,30 Ausz./J für 2022–25), sind aber nicht dieselbe Rechnung.
- **NAS endet am 25.09.2026.** Die 13 NAS-Live-Trades vom Oktober sind im Nachbau nicht abgeglichen. Fenster B hat für
  NAS die letzten drei Wochen nicht.
- **Regeln rekonstruiert.** Der Code von Build 8.20 und `patch900.py` lag nicht vor. R1–R10 sind aus den
  Kurzbeschreibungen nachgebaut und **vor** den Tests in `regime9.py` festgelegt worden.
- **Nicht nachgebildet:** News-Sperre ±6 min und Mindesthaltedauer 130 s (beide nur live), Schlupf über den Spread hinaus.
- **Fenster A ist für Fade-Regeln schwach.** Der Portfolio-Wächter hielt die Listen-Fades 2016–2021 meist virtuell
  (nur 29 NAS-Long-Live-Trades).
- **Pleiten waren in allen 37 Konfigurationen 0.** Der Pleiten-Teil von Regel 1 hat also nichts entschieden.
- **Mehrfachtests:** 37 Versuche. Ein einzelner knapper Vorteil wäre ohnehin nicht belastbar (Deflated Sharpe Ratio).

## 12. Inbetriebnahme

1. **Kompilieren:** `DEADBAND_V9.mq5` nach `MQL5\Experts` kopieren und im MetaEditor mit F7 kompilieren.
   Erwartet: 0 Fehler. Gibt es einen Fehler im TW-Block, läuft V8 einfach weiter. Schick mir die Fehlerzeile.
2. **Tester (Pflicht vor dem Wechsel):**
   - Einstellungen: Modell „Jeder Tick basierend auf echten Ticks“, XAUUSD.x M15 wie V8, 10.000 Einzahlung,
     Zeitraum z. B. 01.09.–16.10.2026.
   - Drei Läufe: V8 mit seinen Eingaben, V9 mit `DEADBAND_V9_Echtbetrieb.set`, V9 mit `TwBericht=false`.
   - Die Handelslisten müssen **identisch** sein.
   - Im Journal von V9 erscheinen „DEADBAND9 TW …“-Zeilen: einmal je Servertag und Symbol sowie je Fade-Signal.
3. **Wechsel live:**
   - Nur flach oder am Wochenende, ein Chart, eigener PC.
   - Set `DEADBAND_V9_Echtbetrieb.set` laden.
   - Kontoeingaben aus dem laufenden V8 übernehmen, falls dort gesetzt: KaufdatumGFT, StartBalanceOverride,
     FloorOverride + FloorOverrideZeit, CycleStartOverride, Auszahlungs-Eingaben, NurAufPcPfad.
   - Gleiche MagicBase wie V8.
   - Prüfen: Startzeile „DEADBAND9: Build 9.00 - Handel wie 8.10 | Trendwende-Bericht AN“, „KONTO ERKANNT“ wie bei V8.
4. **Den Bericht nur beobachten.** Die Tests zeigen: Wer nach diesen Regeln von Hand sperrt, verliert im Mittel Geld
   (z. B. R1 in B −95 $/J über 2 Jahre).

## 13. Neu rechnen mit deinem GFT-Export

1. **Export auf dem PC:**
   - Bei laufendem und eingeloggtem GFT-MT5 `V9/export/DEADBAND_Kursexport.cmd` starten. Es braucht Python; das Paket
     `MetaTrader5` installiert das Skript selbst.
   - Es legt einen neuen Ordner `DEADBAND_Kursdaten_JJJJMMTT_HHMM` an, mit ZIPs je Jahr unter 9 MB. Es handelt nicht
     und überschreibt nichts.
   - Den Ordner in Drive hochladen.
2. **Ich rechne dann** (Ordner mit den entpackten CSV):
   ```
   cd DEADBAND/V9/replikat
   python3 aufbau9.py gft <ordner>        # GFT-Kurse haben Vorrang, freie Daten füllen davor auf
   python3 check_live9.py gft             # Abgleich aller 17 Live-Trades (auch NAS)
   python3 oct9.py gft
   python3 tests9.py gft                  # alle 37 Konfigurationen
   python3 auswertung9.py gft
   python3 kosten9.py <kandidaten> gft
   python3 muster9.py gft
   python3 ../build/tw_check.py gft       # C++-Prüfung des TW-Kerns auf GFT-Kursen
   ```
   Besteht dann eine Änderung alle Regeln, kommt sie als eigene, abschaltbare Eingabe in ein neues Build. Ohne sie
   handelt dieses Build wie 8.10.

## 14. Dateien

| Datei | Inhalt |
|---|---|
| `DEADBAND/V9/DEADBAND_V9.mq5` | Build 9.00, nicht kompiliert erstellt |
| `DEADBAND/V9/DEADBAND_V9_Echtbetrieb.set` | alle 315 Eingaben, Voreinstellung = 8.10, dazu `TwBericht=true` |
| `DEADBAND/V9/DEADBAND_V9_Bericht.md` | dieser Bericht |
| `DEADBAND/V9/build/` | `tw_block.mq5` (neuer Code), `patch_v9.py`, `gen_set.py`, `tw_check.*`, `tw_sim.*`, `bericht_tabelle.py` |
| `DEADBAND/V9/replikat/` | Replikat 9: Daten (`build_free.py`, `daten9.py`, `fetch_raw.sh`), Signale (`gen9.py`), Konto (`eng9.py`, `cfg9.py`), Bewertung (`evl9.py`, `tests9.py`, `auswertung9.py`, `kosten9.py`, `muster9.py`), Regeln (`regime9.py`), Live (`check_live9.py`, `oct9.py`) |
| `DEADBAND/V9/export/` | MT5-Kursexport (`DEADBAND_Kursexport.cmd/.py`) |
