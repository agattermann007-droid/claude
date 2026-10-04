# DEADBAND V7 – Build 7.10: Spike-Fade NAS 8:30 (Bericht)

Stand: 04.10.2026 · Basis: Build 7.00 (Stand des Nutzers, `rollback_7.00/DEADBAND_V7.mq5`) · GFT Instant Premium unverändert.

**Kurz:** Von den sieben YouTube-Ideen, die ich auf echten Kursen getestet habe, hält nur eine auf beiden Datensätzen:
**den Abwärts-Spike nach den US-Daten um 8:30 NY im NAS100 kaufen**. Daraus wird das neue Fade-Modul **S0830**.
Ergebnis im Konto-Replikat mit allen GFT-Regeln:

- 2022–25: **10,26 → 11,00 Auszahlungen pro Jahr**, netto 1873 → 2008 $/J, 0 Pleiten.
- Im gepaarten Test (gleiche Starts, gleiche Störungen): **+0,62 Auszahlungen/J** (SE 0,20, besser in 12 von 16 Läufen) und **+130 $/J netto** (SE 40, besser in 14 von 16).
- Unabhängige Daten 2006–21: 2,62 → 2,70 Ausz./J, 0 Pleiten, besser in 7 von 8 Läufen.
- Verlustserien ab 6 Trades (S6) werden in beiden Datensätzen seltener.

> **Wichtig:** 7.10 wurde ohne MetaEditor erstellt und ist **nicht kompiliert**. Vor dem Einsatz:
> 1. Kompilieren.
> 2. Im Strategietester (Echte Ticks, GFT-Symbole) prüfen.
> 3. Kurz auf dem Demo laufen lassen.
>
> `SpikeAktiv=false` handelt gleich wie 7.00.

---

## 1. Was das Modul macht

Die Videos zum Nachrichtenhandel beschreiben ein wiederkehrendes Muster. Der erste Ausschlag nach CPI, NFP oder Claims ist oft zu groß und wird in den folgenden 15–30 Minuten teilweise zurückgenommen („fade the news spike“, „Judas Swing“). DEADBAND handelt im NAS heute zwischen 8:30 und 10:00 NY nichts, das Zeitfenster ist also frei.

| Schritt | Regel (Voreinstellung) | Eingabe |
|---|---|---|
| Messung | Open der 8:30-Kerze = p0. Die Kerzen 8:30 und 8:35 bestimmen die Richtung. | `SpikeStartNY=510`, `SpikeMessKerzen=2` |
| Richtung | Ausschlag nach unten größer als nach oben → **Long**. Ausschlag mindestens 0,20 × ATR(D1,14). | `SpikeKMin=0.20`, `SpikeRichtung=1` |
| Einstieg | Open der 9:00-Kerze (nach 6 M5-Kerzen). Das Tief bis 8:55 ist das Spike-Extrem. | `SpikeWarteKerzen=6` |
| Stop | Spike-Tief − 0,25 ATR | `SpikeStopATR=0.25` |
| Ziel | Tief + 50 % der Strecke Tief → p0 (halbe Rückkehr). Ziel erst nach 130 s, wie bei allen Fades. | `SpikeZiel=0.5` |
| Ausstieg | spätestens 11:00 NY | `SpikeAusstiegNY=660` |
| Größe | 0,75 % vom Startsaldo × Pufferkurve × BelowStartMult, gedeckelt durch Gesamt- und Ideen-Budget | `SpikeRiskPct=0.75` |

Es gelten alle übrigen Fade-Sperren:
- GueltigSchutz
- News-Fenster (±6 min um 8:30 liegt vor dem Einstieg um 9:00)
- Hedging-Sperre
- US-Feiertage
- Fade-Tagessperre
- Stop mindestens 6 Spreads
- Margin
- Einstieg kostet keinen gültigen Tag

**Kein** Portfolio-Wächter, **kein** Probability Grid: Beides ist für dieses Modul im Replikat ungetestet. Ohne Wächter war es dort besser.

Technisch:
- S0830 ist ein elfter Eintrag in `F[]` (`MAXFADE 11`, Magic = MagicBase + 50 + 10). Verwaltung, Zeit-Ausstieg, Waisen und Abschluss-Ernte laufen deshalb unverändert über den Fade-Code.
- Die Signal-Logik steht in der neuen Funktion `SpikeKerze()`.
- Sie ist eine Zeile-für-Zeile-Übertragung von `Replikat_v6/y7sig.py:spike_fade`.
- Bei einer Lücke in den M5-Kerzen zwischen 8:30 und 9:00 gibt es an diesem Tag kein Signal.
- Mit `FadeAus=S0830` rechnet das Modul nur virtuell.

## 2. Ergebnisse

### 2.1 Signal (Replikat `gsig.simulate`: Einstieg Open der Folgekerze mit Spread, Ziel ab der 2. Kerze, Kommission)

Spezifikation 7.10, `python y7_spike710.py`:

| Daten | Richtung | n | Treffer | R̄ | PF | Jahre (R/Zahl) |
|---|---|---|---|---|---|---|
| GFT 2022–25 | **Long k0,20** | 40 | **92 %** | +0,32 | **5,27** | 22: +2,7/13 · 23: +3,8/9 · 24: +4,5/14 · 25: +1,7/4 |
| GFT 2022–25 | Short k0,20 | 58 | 78 % | +0,12 | 1,69 | |
| 2005–21 | **Long k0,20** | 111 | **87 %** | +0,17 | **2,70** | 15 von 17 Jahren ≥ 0 |
| 2005–21 | Short k0,20 | 143 | 78 % | +0,08 | 1,48 | 2016–19 negativ |
| GFT 2022–25 | Long k0,15 / k0,25 | 61 / 32 | 87 / 91 % | +0,17 / +0,34 | 2,32 / 4,64 | |
| 2005–21 | Long k0,15 / k0,25 | 178 / 67 | 85 / 87 % | +0,10 / +0,21 | 1,77 / 3,28 | |

Die Treffer sind klein (halbe Rückkehr), kommen aber sehr regelmäßig. Genau das braucht der Engpass „gültige Tage“: ein Treffer bei 0,75 % Risiko mit rund 0,7 R Zielweite macht den Tag allein gültig.

### 2.2 Konto-Replikat mit allen GFT-Regeln

Motor: `eng6`, Einstellungen 7.00-nah:
- SAFE
- validpct 0,505, Mindestauszahlung 105 $
- RSI21 0,5 %, Noise 0,45 %
- Bank 5/0,3
- DD-Kurve 5/2,5/0,2
- BelowStart 0,95
- GueltigSchutz an
- Fades mit Portfolio-Wächter PF200 > 1,15

Mittel der Horizonte 250 und 500 Tage über viele Startzeitpunkte. S6 = Verlustserien ≥ 6 pro Jahr (weniger ist besser).

| GFT-Ersatzdaten 2022–25 | Ausz./J | netto $/J | Pleiten | S6 |
|---|---|---|---|---|
| Basis 7.00-nah | 10,26 | 1873 | 0 | 1,52 |
| + Spike beide Richtungen 0,75 % | 10,28 | 1907 | 0 | 1,23 |
| + Spike nur Long k0,25 | 10,77 | 1993 | 0 | 1,13 |
| **+ Spike nur Long k0,20 (7.10)** | **11,00** | **2008** | **0** | **1,11** |
| + Spike nur Long k0,20, 0,90 % | 11,06 | 1993 | 0 | 1,11 |
| + Spike nur Long k0,15 | 10,18 | 1832 | 0 | 1,17 |

| Fremddaten 2006–21 | Ausz./J | netto $/J | Pleiten | S6 |
|---|---|---|---|---|
| Basis 7.00-nah | 2,62 | 447 | 0 | 1,93 |
| + Spike beide k0,25 | 2,67 | 453 | 0 | 1,60 |
| + Spike nur Long k0,25 | 2,64 | 455 | 0 | 1,73 |
| **+ Spike nur Long k0,20 (7.10)** | **2,70** | **463** | **0** | **1,69** |
| + Spike nur Long k0,15 | 2,75 | 474 | 0 | 1,54 |

Gepaarter Test (`y7_paar.py`, gleiche Starts, 5 % zufällig ausgelassene Signale, Schlupf 0,3):

| | Δ Ausz./J | Δ netto $/J | besser in |
|---|---|---|---|
| GFT, Long k0,20 | **+0,62** (SE 0,20) | **+130** (SE 40) | 12/16 bzw. 14/16 |
| GFT, Long k0,25 | +0,45 (SE 0,23) | +114 (SE 40) | 10/16 bzw. 11/16 |
| 2006–21, Long k0,20 | +0,08 (SE 0,03) | +14 (SE 7) | 7/8 |
| 2006–21, Long k0,25 | +0,02 (SE 0,02) | +6 (SE 3) | 4/8 bzw. 6/8 |

**Warum nur Long:** Short-Spikes (Daten bullisch, dann Short) stehen im NAS gegen RSI21 und Noise, die nur Long handeln. Die Hedging-Sperre schneidet dann eins von beiden ab. Mit beiden Richtungen bleibt der Netto-Gewinn, aber die Zahl der Auszahlungen steigt nicht (10,28). Auch auf Signalebene ist Short in beiden Datensätzen schwächer.

**Warum 0,75 % statt 0,90 %:** 0,90 % bringt +0,06 Auszahlungen bei weniger netto. 0,75 % ist wie bei den Fades schon groß genug, damit ein Treffer den Tag gültig macht.

## 3. Ehrliche Grenzen

1. **Der Motor ist ein Proxy.** `eng6` bildet den Stand 6.10 plus generische Signalströme ab. Einzelheiten von 6.20–7.00 sind nur angenähert:
   - Grid
   - Teilgewinn
   - Klemm- und Schlupf-Wächter
   - Firmenprofil
   - Regime-Größe

   Die Basis trifft die rund 10 Ausz./J des Nutzers. Die Differenz ist aussagekräftiger als die absolute Zahl.
2. **Auswahl nach Ansicht der Daten.** „Nur Long“ und k0,20 wurden gewählt, nachdem beide Datensätze angesehen waren. Gegenmittel:
   - Long ist in **beiden** Datensätzen und in jedem Teilzeitraum besser als Short.
   - Die Nachbarwerte k0,15 und k0,25 sind ebenfalls besser als die Basis.
   - Auf GFT-Daten ist die erste Hälfte (IS 2022 – 06/2024) für sich positiv.
3. **Wenige Signale:** rund 10 pro Jahr auf GFT-Daten, 2005–21 nur 6–7 pro Jahr, 2025 nur 4.
   - Ein Jahr ohne Daten-Spikes bringt fast nichts, kostet aber auch fast nichts.
   - Der größte Einzelverlust ist durch Stop und Budget begrenzt.
4. **Daten:** NAS-GFT-Ersatz bis 31.12.2025 (MT5-US100). Gold 2016 Jan–Sep fehlt in den Fremddaten (Umwandlung abgebrochen), das trifft nur die Gold-Fades.
5. **Nicht kompiliert, nicht im MT5-Tester geprüft.** Die Klammerbilanz ist geprüft. Alle neuen Funktionen (`SpikeAnlegen`, `SpikeKerze`) sind definiert und an allen nötigen Stellen eingebunden (Liste, Portfolio-Wächter, Wächter, Kerze, Risiko, Ziel nach Neustart, Startmeldung).

## 4. Getestet und verworfen

Jede Idee als Signalstrom auf GFT-Ersatzdaten. Auswahl auf IS (bis 06/2024), OOS nur angesehen.

| Idee (YouTube-Quelle) | Varianten | Ergebnis |
|---|---|---|
| NAS-Gap-Fade 9:30–10:00 („The Truth About Gap Fills“) | 720 | Bester IS-PF 1,09, OOS 0,70. Kein Paar mit IS und OOS > 1,2. Die Statistik aus dem Video gilt für Futures-RTH-Gaps. Am CFD mit 130-s-Regel und Spread bleibt nichts. **Verworfen.** |
| Turtle Soup Plus One für die Fade-Module (ICT/Connors) | 40 | Zusatzsignale IS PF bis 1,9, OOS 0,83. **Verworfen.** |
| VWAP-Abweichungs-Fade NAS | 336 | IS PF ≤ 1,05. **Verworfen.** |
| Tageshoch/-tief-Timing („How To Identify The High & Low Of The Day“) | 288 | GFT IS PF 1,39, OOS 0,99. 2006–21: 1 von 288 OOS > 1. **Verworfen.** |
| Wochen-Eröffnungs-Fade | 576 | 13 Varianten mit IS und OOS > 1,2, aber der Beste nach IS kippt OOS auf 0,63. Kein stabiles Plateau. **Verworfen.** |
| Makro-Tag-Filter FOMC/CPI/NFP für die Fades („The One Strategy You Need for Every FOMC Day“) | je Modul | Uneinheitlich. X0630 an NFP-Tagen R̄ −0,36, aber nur n = 9. N1100/N0930 an starken 8:30-Tagen sogar besser. **Kein Filter**, aber genau diese Beobachtung (starke 8:30-Bewegung → spätere Rückkehr) führte zum Spike-Modul. |
| Vola-Perzentil als Regime-Faktor | je Modul | Kein monotoner Zusammenhang zwischen Perzentil und R̄. **Verworfen.** |
| **Spike-Fade 8:30 NAS** („How To Trade The News In Under 3 Minutes“, „ICT Judas Swing“) | 636 + 676 | GFT: 339 von 636 OOS > 1. Beide Richtungen 2006–21 schwach (22 von 676), **nur Long** stabil → **7.10**. |

## 5. Dateien

- `DEADBAND_V7.mq5`: Build 7.10. Neuer Kopfblock, Eingabegruppe „7.10: Spike-Fade NAS 8:30“, `SpikeAnlegen()`, `SpikeKerze()`, kleine Einbindungen im Fade-Code.
- `rollback_7.00/DEADBAND_V7.mq5`: unveränderter Stand 7.00.
- `Replikat_v6/y7sig.py`: Signal-Generatoren (Gap, Plus One, VWAP, Tageshoch/-tief, Spike, Wochen-Eröffnung).
- `Replikat_v6/y7_scan.py`: IS/OOS-Raster je Idee.
- `y7_spike.py`, `y7_spike710.py`: Spike-Details.
- `y7_konto.py`: Konto-Replikat.
- `y7_paar.py`: gepaarter Test.
- `y7_data.py`: Datenaufbau.
- `Replikat_v6/ergebnisse/y7_*.json`: alle Rasterergebnisse.

Nachrechnen: Daten nach `Replikat_v6/README.md` bzw. `extdata/DATEN_BERICHT.md` aufbauen, `DEADBAND_EXT=<extdata>` setzen. Dann `python y7_data.py`, `python y7_scan.py gft spike`, `python y7_konto.py gft`, `python y7_paar.py gft`.

## 6. Prüfplan im MT5-Tester (vor dem Live-Einsatz)

1. Kompilieren. Journal beim Start: die Zeile „7.10 Spike-Fade S0830 NAS100 …“ muss erscheinen.
2. Tester 2022–2025, Echte Ticks, Startsaldo 10 000, Einstellungen wie 7.00. Einmal `SpikeAktiv=false` (muss 7.00 entsprechen), einmal `true`.
3. Vergleichen:
   - Auszahlungen
   - gültige Tage
   - kleinster Abstand zum Boden
   - Bodenbrüche (6.81-Prüfwerte)
   - Trades mit Kommentar „FADE S0830“: Einstieg 9:00 NY, Ziel nach ≥ 130 s, Ausstieg spätestens 11:00
4. Erst wenn 7.10 im Tester nicht schlechter ist als 7.00: Demo, dann Live.

## Quellen (Recherche dieser Runde)

- YouTube: [How To Trade The News In Under 3 Minutes (NFP, CPI, FOMC)](https://www.youtube.com/watch?v=4uuc3aGJ3RQ)
- YouTube: [The ICT Judas Swing Forex Strategy – Backtested Results 2023](https://www.youtube.com/watch?v=HSV8ECuJ9Qc)
- YouTube: [The One Strategy You Need for Every FOMC Day!](https://www.youtube.com/watch?v=Tpdc4AREalE)
- YouTube: [How To Identify The High & Low Of The Day (NQ Weekly Recap)](https://www.youtube.com/watch?v=Lb7bjjGsqN4)
- YouTube: [The Truth About Gap Fills](https://www.youtube.com/watch?v=WGXyqybDhcI)
- YouTube: [Backtesting ICT's Turtle Soup Strategy with Gold Futures](https://www.youtube.com/watch?v=dqHddXL1TZs)
- YouTube: [Intraday Momentum Trading Strategy Explained: The "Noise Area" System](https://www.youtube.com/watch?v=NEE_jHYgCx8)
- YouTube: [If You Only Watch ONE Trend Reversal Video, Make It This One](https://www.youtube.com/watch?v=e7PHu65hBFQ)
- YouTube (ORB, als Gegenstück geprüft, nicht übernommen): [NQ ORB Strategy Exposed](https://www.youtube.com/watch?v=g-_HjPAOD2w) · [Backtest: Opening Range Breakout on Indices](https://www.youtube.com/watch?v=ga2YHdXkLi4) · [Day Trading NQ Futures 5-Minute ORB](https://www.youtube.com/watch?v=tii3aSH5Aew) · [Opening Range Breakout Trading Strategies](https://www.youtube.com/watch?v=ZhAd4leZVvU) · [Backtest ORB on SPY 1 min](https://www.youtube.com/watch?v=DJRyi_NNgjM)
- Weitere Quellen der ersten Runde: `DEADBAND_V7_Ideen_Recherche.md`
