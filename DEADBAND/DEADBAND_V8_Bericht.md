# DEADBAND V8 – Build 8.00: neues Konzept „Staffel“ (Bericht)

Stand: 04.10.2026 · Auftrag: mehr Auszahlungen pro Jahr, jede mit mehr Gewinn, ohne Pleiten, in kürzerer Zeit. Getestet wird ab 2022. Neue YouTube-Strategien werden zuerst **allein** bewertet und die GFT-Handhabung auf sie angepasst. Das alte Grundkonzept muss nicht bleiben.

## Ergebnis in einem Satz

Allein schlägt keine der ~25 getesteten YouTube-Strategien den DEADBAND-Kern. Zwei davon liefern aber **gültige Tage zu Zeiten, in denen DEADBAND nichts handelt**:
- den **Larry-Williams-Volatilitätsausbruch auf NAS**,
- das **Gold-Asien-Halten**.

Zusammen mit dem Fade-Kern und einer neuen, auf die Ströme abgestimmten Pufferkurve ergibt das im Konto-Replikat mit allen GFT-Regeln:

| Konto-Replikat (eng6) | 7.10 | **8.00** | Änderung |
|---|---|---|---|
| Auszahlungen / Jahr (2022–25) | 11,00 | **13,37** | +22 % |
| netto $ / Jahr (80 %, nach Gebühren) | 2008 | **2771** | +38 % |
| Ø Auszahlung | 235 $ | **267 $** | +14 % |
| Tage je Zyklus (Start bis Auszahlung) | 30,0 | **25,0** | −5 Tage |
| gültige Tage / Jahr | 65,7 | **85,0** | +29 % |
| Pleiten | 0 | **0** | |
| Auswahl-Zeitraum 2022–23 (Ausz./J, netto) | 12,57 / 2509 | **16,54 / 3293** | |
| Prüf-Zeitraum 2024–25 (Ausz./J, netto) | 7,78 / 1191 | **11,87 / 2561** | |
| Fremddaten 2006–21 (Ausz./J, netto, Pleiten) | 2,70 / 463 / 0 | **3,66 / 713 / 0** | |

> **Wichtig:**
> - 8.00 ist **nicht kompiliert und nicht im MT5-Tester gelaufen**: erst kompilieren, dann Strategietester (Echte Ticks), dann Demo.
> - Das Replikat ist der Motor auf Stand 6.10 mit generischen Strömen. Grid, Teilgewinn, Schutz je Modul und Regime-Größe von 6.20–7.00 sind darin nur angenähert. Aussagekräftig ist der **Unterschied** 7.10 → 8.00, nicht die absolute Zahl.
> - `LwAktiv=false`, `AsiaAktiv=false` und Pufferkurve 5/2,5/0,2 entsprechen 7.10.

---

## 1. Vorgehen

1. **Recherche.** Ein Recherche-Agent hat YouTube nach mechanischen Intraday-Strategien für Gold und Nasdaq durchsucht. Gefunden wurden rund 25 Strategien mit Regeln, dazu unabhängige Gegentests. Die Quellen stehen unten.
2. **Signal-Generatoren.** Jede Strategie ist als Generator im Python-Replikat umgesetzt (`Replikat_v6/n8sig.py`).
   - Einstieg immer am Open der Folgekerze, Long zum Ask.
   - Spread und Kommission eingerechnet.
   - Entscheidungen nur mit abgeschlossenen Kerzen.
3. **Raster mit getrennter Prüfung** (`n8_scan.py`, `n8_robust.py`):
   - Auswahl nur auf 2022–23.
   - Prüfung auf 2024–25, Gold zusätzlich 2026.
   - Gegenprobe auf Fremddaten 2005–21.
   - „Robust“ heißt: PF > 1,15 in beiden GFT-Hälften und PF > 1,08 auf 2005–21.
4. **Jede Strategie allein unter den GFT-Regeln** (`n8_konto.py`): eng6 mit allen GFT-Regeln in strenger Lesart, DEADBAND/RSI21/Noise/Fades aus. Rollierende 10k-Konten von 2022-03 bis 2025-12 über 1 und 2 Jahre, 8 gestörte Läufe je Start.
5. **GFT-Handhabung je Strom anpassen** (`n8_gft710.py`, `n8_port.py`). Variiert wurden:
   - Pufferkurve
   - Risiko je Strom
   - die neue **Puffer-Schwelle je Modul** (`minbuf`: Strom handelt nur bei genug Luft zum Boden)
   - Bodenwächter, Verlustgrenzen
6. **Erst dann kombinieren.** Ausgewählt wurde nach dem ganzen Zeitraum, gezeigt werden zusätzlich die Hälften und die Fremddaten.

## 2. Getestete YouTube-Strategien (Signalebene)

| Strategie (Quelle) | Varianten | robust? | Ergebnis |
|---|---|---|---|
| **Larry-Williams-Volatilitätsausbruch** NAS ([Video](https://www.youtube.com/watch?v=NQxO__tXW5o), [Pinescript-Test](https://www.youtube.com/watch?v=qpiiJ8YbPsM)) | 144 | **27** | k 0,4: PF 1,55 / 1,59 / 1,20 (2005–21, 3304 Trades), jedes GFT-Jahr positiv, Long und Short. **Übernommen (LW).** |
| **Connors RSI(2)** NAS, Tagesbasis ([Video](https://www.youtube.com/shorts/0cyy9R5kqhE)) | 192 | **34** | PF 1,5 / 1,5 / 1,4, aber nur etwa 15 gültige Tage pro Jahr. Bringt im Konto wenig (+0,5 Ausz.) und kostet in der Endauswahl. **Nicht übernommen.** |
| NAS-Eröffnungsmomentum, 30 min mitgehen (Zarattini [Noise Area](https://www.youtube.com/watch?v=NEE_jHYgCx8)) | 672 | **30** | PF 1,2–1,5 überall, überschneidet sich aber mit Noise und LW. Im Konto Pleiten. **Nicht übernommen.** |
| Gold-Asien-Halten 18:00–3:00 mit Trendfilter (Saisonalität im Tag) | 240 | 4 | PF 1,23 / 1,44 / 1,21, schwach, aber unabhängig von allem anderen. **Übernommen (XA).** |
| NQ 15-min-ORB mit Mittelpunkt-Filter ([NQ ORB Exposed](https://www.youtube.com/watch?v=g-_HjPAOD2w), tradingstats) | 576 | 4 | PF ~1,2 / 1,2 / 1,1, schwächer als LW und zur selben Zeit. Verworfen. |
| NQ 5-min-ORB / 9:30-Kerze ([9:30-Kerze](https://www.youtube.com/watch?v=jq-fpkPv3-A), [Kritik](https://www.youtube.com/watch?v=HOi5bjUhZZ0)) | 5888 | 4 | 2022–25 gut, 2005–21 PF 1,00. Ein Effekt der jüngeren Jahre. Verworfen. |
| Gold-Initial-Balance mit Rücklauf (Trade That Swing / [edgeful](https://www.youtube.com/watch?v=LiN0hplsDlU)) | 1620 | 0 | Gold: nichts. NAS-Long 2022–25 PF 1,4–2,1, aber 2005–21 PF 0,9. Verworfen. |
| ICT Silver Bullet / Judas Swing ([Video](https://www.youtube.com/watch?v=o0v4KQxZbpU)) | 252 | 3 | R/J +2–3, zu schwach. Deckt sich mit dem unabhängigen Gold-Test „Edge or Myth“ (−0,55 R). Verworfen. |
| Dokakuri „Magic Hours“ (Stunden-Range-Fade) | 576 | 0 | 2005–21 PF < 1. Verworfen. |
| Intraday-Momentum Gao (erste → letzte halbe Stunde) | 576 | 0 | Verworfen. |
| EMA-Trend-Pullback (Drift-VWAP-Art) ([Video](https://www.youtube.com/shorts/dpdwaO24QpE)) | 576 | 0 | 2022–25 gut, 2005–21 PF 0,98. Verworfen. |
| Vortageshoch/-tief-Ausbruch und Sweep | 216 | 0 | Verworfen. |
| Bollinger-Rückkehr Gold/NAS | 864 | 2 (schwach) | Verworfen. |
| Turn of the Month ([Video](https://www.youtube.com/watch?v=H7asjNMQ0OU)) | 36 | 0 | Verworfen. |
| Spike-Fade zu anderen Zeiten (Gold 8:30, 10:00, 14:00) | 11 | – | Nur NAS 8:30 Long trägt (= S0830 aus 7.10). |

## 3. Jede Strategie allein unter den GFT-Regeln

Pufferkurve 5/2,5/0,2, 0,75 %, falls nicht anders angegeben.

| Allein | Ausz./J | netto $/J | Pleiten/Kontojahr |
|---|---|---|---|
| Fade-Kern (10 Fades, 7.10) | 6,87 | 1145 | 0 |
| RSI21 + Noise (7.10) | 4,35 | 826 | 0 |
| **LW** (Larry Williams) | **5,79** | **1285** | 0,016 |
| LW mit Pufferkurve 3/1/0,3 | 8,70 | 2048 | 0,676 |
| NAS-Eröffnungsmomentum | 3,87 | 614 | 0,006 |
| RSI(2) (Kurve 3/1/0,3) | 2,08 | 382 | 0,002 |
| Vortages-Ausbruch | 1,46 | 220 | 0 |
| bestes reines Neu-Portfolio (LW 0,5 % + RSI2 + XA) | 6,73 | 1145 | 0 |
| reines Neu-Portfolio aggressiv (LW+MOM+RSI2 Kurve 3/1) | 11,35 | 2381 | **2,47** |

**Folgerungen:**
- Der Larry-Williams-Ausbruch ist allein fast so stark wie alle 10 Fades zusammen.
- Ausbrüche haben aber wenige Treffer (WR ~40 %) und lange Verlustserien. Deshalb braucht LW eine eigene GFT-Handhabung: weniger Risiko (0,5 %) und **nur mit Luft zum Boden** (ab 4 % Puffer).
- Ein reines Neu-Portfolio kommt ohne Pleiten nicht über 6,7 Auszahlungen pro Jahr. Der Fade-Kern bleibt das Herz.

## 4. GFT-Handhabung

Die stärkste Einzelstellschraube ist die **Pufferkurve**. Die Kurve 5/2,5/0,2 aus 6.40 verkleinert schon ab 1 % Rückgang und bremst damit die gültigen Tage.

| 7.10 mit Kurve | Ausz./J | netto | Pleiten |
|---|---|---|---|
| 5/2,5/0,2 (7.10) | 11,00 | 2008 | 0 |
| 4/1,5/0,3 | 12,83 | 2336 | 0 |
| 3/1/0,3 | 13,27 | 2405 | 0 |
| 3/1/0,1 | 12,87 | 2328 | 0 |

**Mit LW** ist eine zu flache Kurve gefährlich. Alle Pleiten sind Brüche des nachlaufenden 6 %-Bodens. Untersucht wurden:
- Risiko 0,4 / 0,5 / 0,6 / 0,75 %
- Puffer-Schwelle 3 / 3,5 / 4 / 4,5 / 5 %
- Kurven-Minimum 0,1 / 0,15 / 0,2 / 0,3
- Bodenwächter

**Plateau ohne Pleiten:** LW 0,5 %, Schwelle 3,5–4,5 %, Kurven-Minimum 0,1–0,2 ergibt 14,0–14,6 Auszahlungen pro Jahr. Mit der Kurve 3/1/0,1 bleibt aber auf den Fremddaten 2006–21 eine Rate von 0,001 Pleiten je Kontojahr.

**Gewählt: Kurve 3,5/1,25/0,1.** Sie hat 0 Pleiten auf **beiden** Datensätzen und kostet dafür etwa 0,6 Auszahlungen pro Jahr gegenüber der aggressivsten Einstellung.

| 7.10 + LW 0,5 % (ab 4 %) + XA | Ausz./J | netto | Pleiten 22–25 | Fremddaten 06–21 |
|---|---|---|---|---|
| Kurve 3/1/0,1 (Option „offensiv“) | 14,01 | 2920 | 0 | 3,86 / 754 / **0,001** |
| **Kurve 3,5/1,25/0,1 (8.00)** | **13,37** | **2771** | **0** | **3,66 / 713 / 0** |
| Kurve 4/1,5/0,1 | 13,17 | 2724 | 0 | 3,43 / 659 / 0 |

## 5. Was im EA neu ist (`DEADBAND_V8.mq5`)

- **Modul LW** (Larry-Williams-Ausbruch, Eingabegruppe „8.00: Larry-Williams-Ausbruch NAS“):
  - `LwKerze()` ist eine Zeile-für-Zeile-Übertragung von `n8sig.gen_lw`.
  - Die Vortages-Range wird aus den M5-Kerzen 9:30–16:00 mitgeführt.
  - Marken: Open 9:30 ± 0,4 × Range.
  - Einstieg: Schluss jenseits einer Marke bis 15:00, dann am Open der nächsten Kerze.
  - Stop: Mitte zwischen Open und Einstieg. Kein Ziel, Ausstieg 16:00.
  - Risiko 0,5 %, `LwMinPuffer` 4 %.
- **Modul XA** (Gold-Asien-Halten): `AsiaKerze()` überträgt `n8sig.gen_hold`.
  - Long 18:00 NY, wenn der Schluss über dem Schnitt der letzten 288 M5-Schlüsse liegt.
  - Stop 0,6 ATR, Ziel 1 R, Ausstieg 3:00 NY.
  - Risiko 0,75 %.
- **Puffer-Schwelle je Modul:** `F[m].minBuf`, geprüft in `FadeLive`.
- **Ziel 0 = kein Ziel:** nur Stop/Zeit-Ausstieg. `FadeLive`/`FadeVerwalten` akzeptieren das jetzt.
- **Pufferkurve** `DDFullPct/DDMinPct/DDMinFactor` = 3,5 / 1,25 / 0,1.
- Beide Module laufen über die vorhandene Fade-Maschinerie. Damit gelten alle GFT-Sperren:
  - Hedging-Verbot
  - Budget, Margin, Mindest-Stop in Spreads
  - Schutz gültiger Tage, News-Fenster, Feiertage
  - 130-s-Ziel
  - Ernte, Zeit-Ausstieg, Waisen
- Beide Module sind aus dem Portfolio-Wächter der Fades ausgenommen (wie S0830). `MAXFADE` ist 13; die Magics sind MagicBase + 50 + Modulnummer (LW 61, XA 62 bei Standardliste).
- `rollback_7.00/` und `DEADBAND_V7.mq5` (7.10) bleiben unverändert.

## 6. Ehrliche Grenzen

1. **Replikat-Motor:** eng6 = 6.10 + generische Ströme. Die Pufferkurve wurde in 6.40 mit einem anderen Motorstand auf 5/2,5/0,2 gesetzt. Ob 3,5/1,25/0,1 im echten EA genauso trägt, muss der Tester zeigen. Pleiten sind der kritische Prüfwert.
2. **Auswahl nach Ansicht:** Die Endauswahl (Risiko, Schwelle, Kurve) ist auf dem ganzen Zeitraum 2022–25 getroffen. Gegenmittel:
   - LW wurde auf 2022–23 ausgewählt und hält 2024–25 und 2005–21.
   - Die gewählte Einstellung liegt in der Mitte eines Plateaus.
   - Beide Hälften und die Fremddaten verbessern sich.
3. **Ausbrüche sind kostenempfindlich.** LW mit 2 Pkt Schlupf je Seite: PF 1,57 → 1,39; mit 4 Pkt: 1,24. Die Stop-Weite ist im Median 51 Pkt (0,30 %).
4. **Gold-Asien** ist ein schwacher Effekt: +0,1–0,4 Auszahlungen pro Jahr. Er handelt um 18:00 NY direkt nach der Tagespause, wenn der Spread breit ist. Die 6-Spreads-Regel lässt ihn dann aus.
5. **Daten:** NAS-GFT-Ersatz bis Ende 2025, Gold bis 09/2026. In den Fremddaten fehlt Gold von Januar bis September 2016.
6. **Nicht kompiliert.** Die Klammerbilanz ist geprüft. Neue Funktionen: `SonderAnlegen`, `SonderVirtuell`, `LwKerze`, `AsiaKerze`.

## 7. Prüfplan im MT5-Tester

1. Kompilieren. Beim Start erscheinen im Journal die Zeilen „8.00 Larry-Williams-Ausbruch LW …“ und „8.00 Gold-Asien-Halten XA …“.
2. Tester 2022–2025, Echte Ticks, 10 000 Start. Drei Läufe:
   - a) 8.00 wie geliefert
   - b) `LwAktiv=false`, `AsiaAktiv=false`
   - c) zusätzlich DD 5/2,5/0,2 (= 7.10)
3. Vergleichen:
   - Auszahlungen
   - kleinster Abstand zum Boden
   - Bodenbrüche (6.81-Prüfwerte)
   - Trades „FADE LW“: Einstieg nach Schluss jenseits der Marke, Stop Mitte, Ausstieg 16:00
   - Trades „FADE XA“: 18:00–3:00
4. Wenn der kleinste Abstand zum Boden in a) deutlich unter dem von c) liegt: `DDMinPct` auf 1,5 und `LwMinPuffer` auf 4,5 setzen, oder `LwRiskPct` auf 0,4.

## 8. Dateien

- `DEADBAND_V8.mq5`: Build 8.00.
- `Replikat_v6/n8sig.py`: 13 Generator-Familien (ORB, Silver Bullet, Bollinger, Pullback, Momentum ×2, Vortag, Halten, IB-Rücklauf, ORB-Mittelpunkt, Larry Williams, RSI2/IBS, Turn of Month).
- `n8_scan.py`, `n8_robust.py`: Raster mit Auswahl, Prüfung und Fremddaten.
- `n8_detail.py`: Jahre und Korrelation.
- `n8_konto.py`: Strom allein unter den GFT-Regeln.
- `n8_gft710.py`: Pufferkurve an 7.10.
- `n8_port.py`: Portfolios, Sätze a–f.
- `n8_ext.py`: Fremddaten-Konto.
- `eng6.py`: 32 statt 14 generische Ströme, neue Strom-Spalte `minbuf`.
- `evl6.py`: Pleiten nach Art (Boden/Floating/Tag).
- `Replikat_v6/ergebnisse/n8_*.json(.gz)`: alle Ergebnisse.

## Quellen

- Larry Williams: [Volatility Breakouts and the Oops Reversal Setup](https://www.youtube.com/watch?v=NQxO__tXW5o) · [Larry Williams Strategy Backtested (Pinescript)](https://www.youtube.com/watch?v=qpiiJ8YbPsM)
- Connors RSI(2): [Larry Connors' 2-Period RSI Strategy (Backtested)](https://www.youtube.com/shorts/0cyy9R5kqhE)
- Noise Area / Eröffnungsmomentum: [Intraday Momentum Trading Strategy Explained](https://www.youtube.com/watch?v=NEE_jHYgCx8)
- ORB: [NQ ORB Strategy Exposed](https://www.youtube.com/watch?v=g-_HjPAOD2w) · [ORB Backtest 56 % WR](https://www.youtube.com/watch?v=-6vzl-Myarw) · [Edgeful's ORB Formula](https://www.youtube.com/watch?v=9GTlnBXmqfM) · [I Backtested 1,178,668 ORB Trades](https://www.youtube.com/watch?v=MOG-DbgmzzI)
- 9:30-Kerze: [9:30AM Candle Scalping](https://www.youtube.com/watch?v=jq-fpkPv3-A) · [Kritik: lost $14K–$28K](https://www.youtube.com/watch?v=HOi5bjUhZZ0)
- Initial Balance Gold: [edgeful IB Algo Review](https://www.youtube.com/watch?v=LiN0hplsDlU) · [Gold IB Strategy](https://www.youtube.com/watch?v=4PEsb7O5xsA)
- Gold Asia/London: [Asia Gold Opening Range](https://www.youtube.com/watch?v=jHEXI0JQtn0) · [1-Minute Breakout GOLD & NAS100](https://www.youtube.com/watch?v=IgBhP1yXSGw) · [René Balke Gold Breakout](https://www.youtube.com/watch?v=-_Ctg8JXaIQ)
- ICT: [Silver Bullet – No Daily Bias](https://www.youtube.com/watch?v=o0v4KQxZbpU) · [Turtle Soup Gold](https://www.youtube.com/watch?v=dqHddXL1TZs) · [ICT Judas Swing Backtest](https://www.youtube.com/watch?v=HSV8ECuJ9Qc)
- London-Range NQ: [Joovier Gems London Breakout getestet](https://www.youtube.com/watch?v=8Lhfo2urf58) · [„Fails in Real Data“](https://www.youtube.com/watch?v=K18iaIlkA_w)
- Drift-VWAP-Pullback: [Video](https://www.youtube.com/shorts/dpdwaO24QpE) · Turn of Month: [Ultimo Effect](https://www.youtube.com/watch?v=H7asjNMQ0OU)
- Gegentests ohne YouTube: Zarattini & Aziz 2023 (SSRN 4416622) mit [Replikation](https://github.com/giovannibrusco/zarattini-2023-orb-qqq) · Gao/Han/Li/Zhou (JFE 2018) · arXiv 2605.04004 (MNQ, 14 Signalfamilien ohne Vorteil) · „Edge or Myth“-Gold-Tests (GitHub mathematation860-boop)
