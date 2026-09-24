# Datenbericht: externe historische Intraday-Kurse für XAUUSD und NAS100

Stand: 24.09.2026 · Arbeitsverzeichnis `scratchpad/extdata/` · Zweck: Strategien außerhalb von 2022–2026 prüfen.
Alle Zahlen in diesem Bericht stammen aus den Skripten in `extdata/scripts/`. Die Ausgaben in `extdata/work/` sind reproduzierbar: Ein kompletter Neuaufbau mit `run_all.sh` ergab identische SHA-256-Prüfsummen.

---

## 1. Ergebnis in Kürze

| Datei (MT5-Format, M5, GFT-Serverzeit) | Zeitraum (Server) | Zeilen | Inhalt / Segmente | Empfehlung |
|---|---|---|---|---|
| **`XAUUSD_ext_M5.csv`** | 2006-03-20 → 2026-09-02 | 1 443 612 | **O** OANDA-Mid bis Fr 2011-05-13 · **A** Dukascopy-Ticks ab Mo 2011-05-16 · **E** 14 086 Dukascopy-Füllbars (EPSOFT) · **B** Dukascopy-M1 (Bid/Ask) ab Mo 2016-09-05 | Hauptdatei Gold |
| **`NAS100_ext_M5.csv`** | 2005-01-03 → 2025-12-31 | 1 399 877 | **O** OANDA NAS100_USD (Mid) bis Fr 2020-05-08 · **H** HistData NSXUSD 2020-05-11 → 2020-12-31 · **M** MT5-Broker-Export US100 ab Mo 2021-01-04 | Hauptdatei NAS100 |
| `XAUUSD_ext_mt5_M5.csv` | 2018-01-02 → 2024-12-31 | 496 107 | MT5-Broker-Export XAUUSD (Tickvolumen und Spread vom Broker) | **Kommt GFT am nächsten** (Kurs-Differenz im Median 0,04 USD). Für 2018–2021 als zweite Prüfung verwenden |
| `XAUUSD_ext_oanda_M5.csv` | 2006-03-20 → 2020-05-14 | 998 968 | Nur OANDA XAU_USD (Mid) | Zweiter, unabhängiger Feed (Robustheitstest) |
| `NAS100_ext_histdata_M5.csv` | 2010-11-15 → 2026-02-13 | 1 043 710 | Nur HistData NSXUSD, TICKVOL 0, SPREAD 0 | Nur als Gegenprobe. **Enthält 2012–2018 Rollsprünge** (Abschnitt 6.4) |
| `NAS100_histdata_rollspruenge.csv` | – | 53 | Je Quartalsverfall der auffälligste Bar der HistData-Reihe gegen eine Referenzreihe | Liste der zu meidenden Tage |

**Kernaussagen**
- Beide Hauptdateien decken **2010–2021 vollständig** ab. Gold beginnt 2006, NAS100 2005. Zum Abgleich überlappen beide mit den GFT-Dateien 2022–2025/26.
- **Zeitbasis geprüft:** GFT-Serverzeit = New-York-Ortszeit + 7 h mit US-Sommerzeitregeln. Jede Quelle wurde wochenweise gegen eine Referenz auf Stundenversatz getestet und tageweise auf Minutenversatz. Auffällig sind nur zwei Einzeltage in der HistData-Reihe (22.08.2025: etwa 13 min Verzögerung; 06.04.2012: 1 min).
- **Übereinstimmung mit GFT** (Korrelation der M5-Renditen, je Jahr):
  - Gold Dukascopy: 0,994–0,999
  - Gold MT5-Broker: 0,997–0,999
  - NAS MT5-Broker: 0,995–0,999
  - NAS HistData: 0,990–0,999
- **Wichtigste Einschränkungen** (Details in Abschnitt 7):
  - NAS100: SPREAD ist bis Ende 2020 immer 0 (unbekannt).
  - NAS100: TICKVOL fehlt (0) von 2020-05-11 bis 2020-12-31 sowie in 35 % bzw. 15 % der Bars im Januar und Februar 2021.
  - Gold: TICKVOL ab 2016-09 ist ein kalibrierter **Proxy** aus dem Dukascopy-Volumen.
  - Gold: Die Spreads stammen von Dukascopy und sind breiter als die von GFT.

---

## 2. Format der Ausgabedateien

- Das Format ist mit den GFT-Dateien identisch:
  - Tabulator als Trennzeichen, CRLF-Zeilenenden.
  - Kopfzeile `<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>`.
  - Datum `YYYY.MM.DD`, Zeit `HH:MM:SS`, Preise mit 2 Nachkommastellen, `VOL` immer 0.
- **Zeitstempel = Eröffnungszeit des M5-Bars in GFT-Serverzeit.** Der Bar umfasst [t, t+5 min).
  - Umrechnung: UTC → `America/New_York` → +7 h. Damit entspricht 17:00 NY immer 00:00 Server, auch in den Wochen, in denen US- und EU-Sommerzeit auseinanderfallen.
- **Sessionfilter wie bei GFT:** Bars mit Serverstunde 00 (17:00–18:00 NY, Tagespause) und Wochenend-Bars werden verworfen.
  - Die GFT-Dateien enthalten nie Bars um 00:xx.
  - Verworfen wurden 11 011 Gold-Bars und rund 9 900 NAS-Bars (OANDA 9 690, MT5 243). Die Rohdaten bleiben unverändert in `raw/`.
- Kontrolle der Wochenstruktur:
  - Alle Dateien beginnen fast immer Mo 01:00 (wie GFT).
  - Gold endet Fr 23:55.
  - NAS endet Fr 23:55 (OANDA- und MT5-Teil) bzw. Fr 23:10 (HistData, Handelsschluss dort 16:15 NY).
- **Bedeutung der Spalten TICKVOL und SPREAD je Segment:**

| Datei / Segment | TICKVOL | SPREAD (Punkte à 0,01) |
|---|---|---|
| Gold O (OANDA) | OANDA-Tickanzahl (Median 18–120 je M5) | 0 = unbekannt |
| Gold A (FX31337-Ticks) | echte Dukascopy-Tickanzahl (Median 255–602) | Minimum der Open-/Close-Spreads der M1-Bars (siehe 5.1) |
| Gold E (EPSOFT-Füllbars) | **0 = unbekannt (Markierung)** | **0 = unbekannt (Markierung)** |
| Gold B (Dypoi-M1) | **Proxy** = round(2837,4 × Dukascopy-Bid-Volumen) | wie A |
| XAUUSD_ext_mt5 | MT5-Tickvolumen des Brokers | Minimum der M1-Spreads des Brokers (MT5-Konvention) |
| NAS O (OANDA) | OANDA-Tickanzahl (Median 4–411) | 0 = unbekannt |
| NAS H (HistData) | 0 = unbekannt | 0 = unbekannt |
| NAS M (MT5 US100) | MT5-Tickvolumen (Jan./Feb. 2021: 35 %/15 % der Bars 0) | Minimum der M1-Spreads × 10 (Broker notiert mit 1 Nachkommastelle). 2021-01…03 und 2022-05…2023-02 teils 0 |

---

## 3. Quellen: Herkunft, Stand und Lizenz

| Kürzel | Repository / Datei | Commit (Stand) | Inhalt | Lizenz / Hinweis |
|---|---|---|---|---|
| Dypoi | `github.com/Dypoi/XAUUSD_Dataset`, 10 Dateien `XAUUSD_M1_YYYY0901_YYYY0901.csv` | `4f9fe4b7a9fdd864c732b6047c899b17acddc7bc` (2026-09-03) | XAUUSD M1 Bid- und Ask-OHLC plus Volumen, 2016-09-01 → 2026-09-01, UTC | Keine Lizenzdatei, Quelle im Repo nicht genannt. **Als Dukascopy nachgewiesen:** 607 044 M1-Bars sind identisch mit den Dukascopy-Ticks von FX31337, 182 878 M5-Bars identisch mit dem Dukascopy-JForex-Export von EPSOFT. Für die Dukascopy-Daten gelten deren Nutzungsbedingungen |
| FX31337 | `github.com/FX31337/FX-BT-Data-XAUUSD-DS` (Spiegel `FX-Data/FX-Data-XAUUSD-DS`), Branches `XAUUSD-2011` … `XAUUSD-2018`, stündliche `*_ticks.csv` | 2011 `75406de3`, 2012 `80df4537`, 2013 `f195a948`, 2014 `880879ee`, 2015 `88d49391`, 2016 `1d0b950f`, 2017 `6cdee812`, 2018 `e392db6b` (alle vom 24.06.2018) | Dukascopy-Ticks (Bid, Ask; UTC, ms) von 2011-05-10 bis 2018-06-19 | Keine Lizenzdatei. Daten von Dukascopy. **Zwei Fehler der Quelle:** (1) Preise um den Faktor 100 zu klein (11.9426 statt 1194.26), korrigiert; (2) die Stunde 00:00–00:59 UTC fehlt an jedem Tag (keine `--00h`-Dateien) |
| EPSOFT | `github.com/EPSOFT/Database-Currency-Pair`, `XAUUSD/5M.zip` (SHA-256 `8c1e92dc…3c210c6`) | `d34d6497b2fcf9e2f1b6ea13fd2ed22f4ad708ea` (2023-04-05) | Dukascopy-JForex-Export „XAUUSD_Candlestick_5_M_BID“ 2007–2023, Ortszeit New York mit GMT-Offset | Repo unter GPL-3.0. **Stark lückenhaft** (einzelne Monate nur zu 5–40 %), Volumenangaben mit wechselnden Einheiten. Nur zum Füllen der fehlenden UTC-Stunde 0 verwendet, nachdem die Gleichheit mit A und B geprüft war |
| OANDA | `github.com/FutureSharks/financial-data`, `pyfinancialdata/data/currencies/oanda/{NAS100_USD,XAU_USD}/YYYY/*.csv` | `7ba1d404aa8b0e1c0f71321acebadcbfb9bcca8d` (2020-05-28) | Minutenkerzen aus der OANDA-v20-API, Preiskomponente **„mid“** (lt. `oanda_prices.py`), UNIX-Zeit (UTC), `volume` = Tickanzahl. NAS 2005-01 → 2020-05-14, Gold 2006-03 → 2020-05-14 | Repo unter GPL-3.0. Daten von OANDA, deren Bedingungen gelten |
| HistData | `github.com/hizawye/better-backtest`, `data/histdata/nsxusd/normalized/nsxusd_m1_YYYYMM.json` (184 Dateien) + `manifest.json` (mit SHA-256 der Original-ZIPs `HISTDATA_COM_ASCII_NSXUSD_M1_*.zip`) | `c95db5a185ac024133dd8e7e2af4a77525258ca3` (2026-02-18) | HistData.com NSXUSD (Nasdaq-100) M1, 2010-11-14 → 2026-02-13, 5 075 918 Bars. Die Originalwerte bleiben unverändert erhalten, `timestamp` ist `Date.UTC(Quell-Wanduhrzeit)` | Keine Lizenzdatei. HistData stellt die Daten kostenlos zum Download bereit. Die Nutzungsbedingungen konnten nicht abgerufen werden (histdata.com gesperrt), vor Weitergabe bitte prüfen. Laut Formatbeschreibung (zitiert im README von `philipperemy/FX-1-Minute-Data`) sind es Bid-Quotes in „EST ohne Sommerzeit“. **Die Zeitangabe ist für NSXUSD empirisch falsch** (Abschnitt 4) |
| MT5-US100 | `github.com/ts4blader/market_data`, `US100/M1_seed.csv` (Git-LFS, SHA-256 `f78a0702…941824`, geprüft) | `5246088b258b9e94cf43300e5bd8769695c49526` (2026-07-25) | MT5-Export (gleiches Format wie GFT) US100 M1, 2021-01-04 → 2025-12-31, mit TICKVOL, VOL und SPREAD | Keine Lizenzdatei. **Broker unbekannt**, Serverzeit = NY+7 (geprüft) |
| MT5-XAU | `github.com/AntonDonev/Tiamat`, `TiamatOffline/XAUUSD_M1_RAW.csv` (Git-LFS, SHA-256 `b877f735…e423ade`, geprüft) | `1c2e8372281dee502fd52a40f8ee007b13a992cc` (2025-11-30) | MT5-Export XAUUSD M1, 2018-01-02 → 2024-12-31, mit TICKVOL und SPREAD | Keine Projektlizenz. **Broker unbekannt**, Serverzeit = NY+7 (geprüft). Kurse nahezu identisch mit GFT |

Bezugswege:
- `git clone`/`git fetch`, in der Regel mit `--depth 1` bzw. `--filter=blob:none` und Sparse-Checkout.
- `raw.githubusercontent.com` mit HTTP-Range-Abfragen zum Ansehen einzelner Dateien.
- Git-LFS-Objekte über `media.githubusercontent.com/media/<owner>/<repo>/<commit>/<pfad>`.

---

## 4. Zeitzonen: Bestimmung und Umrechnung

**Zielzeit:** Server = NY-Ortszeit + 7 h, d. h. UTC+2 im Winter und UTC+3 bei US-Sommerzeit.

- **Beleg für die Zielzeit:** Dukascopy (UTC), umgerechnet nach NY+7, passt in **242 von 242 Wochen** (2022–2026) ohne Stundenversatz zu den GFT-Dateien. Das gilt auch für die DST-Wochen, in denen US- und EU-Sommerzeit auseinanderfallen. Der Median der Wochenkorrelation der M5-Renditen beträgt 0,998.

**Verfahren:**
- Wochenweiser Offset-Scan: Korrelation der M5-Log-Renditen für jeden Kandidaten-Stundenversatz.
- Zusätzlich tageweise Lead/Lag-Prüfung ±6 Bars (M5) bzw. ±10 min (M1).

| Quelle | Deklarierte Zeit | Ergebnis der Prüfung | Umrechnung |
|---|---|---|---|
| Dukascopy (A, B, E) | UTC | 242/242 Wochen Versatz 0 gegen GFT. Tages-Check an 1 190 Tagen gegen GFT: kein Versatz | UTC → NY → +7 h. EPSOFT: Ortszeit minus angegebenem GMT-Offset ergibt UTC |
| OANDA | UTC (UNIX) | 372/372 Wochen Versatz 0 gegen Dukascopy (Gold 2011–2018). Tages-Check an 2 326 Tagen (M1): alle Lag 0 | UTC → NY → +7 h |
| MT5-US100, MT5-XAU | Serverzeit | 198 bzw. 366 Wochen konsistent mit NY+7. In allen 14 bzw. 24 DST-Differenzwochen gilt die **US**-Regel. Tages-Check an 965 bzw. 763 Tagen: kein Versatz | keine Umrechnung nötig (bereits NY+7) |
| **HistData NSXUSD** | „EST ohne Sommerzeit“ | **Nicht zutreffend.** 2010-11 → 2018: **New-York-Ortszeit** (US-Regel in 27/27 Differenzwochen gegen OANDA). **Ab 2019: UTC−5 h, +1 h während der EU-Sommerzeit** (EU-Regel in 7/7 Differenzwochen gegen OANDA 2019–20 und in 14/14 gegen GFT 2022–26). Die Sonntagseröffnung liegt deshalb 2019–2022 in 3–4 Wochen pro Jahr scheinbar bei 17:00 statt 18:00 | bis 2018-12-31: Server = Quelle + 7 h. Ab 2019: Quelle + 7 h = Europe/Athens-Ortszeit → UTC → NY → +7 h. In den Differenzwochen (vom 2. bis zum letzten Sonntag im März sowie vom letzten Sonntag im Oktober bis zum 1. Sonntag im November) ist Server = Quelle **+8 h** |

**Tages-Check der HistData-Reihe:**
- 997 Tage gegen GFT: nur der **22.08.2025** fällt auf. Beim Powell-Auftritt um 10:00 NY zeigt HistData den Sprung erst um 10:13, eine Verzögerung der Quelle.
- 2 446 Tage gegen OANDA: nur der 06.04.2012 (Karfreitag, 1 min).

---

## 5. Aufbereitung je Datei

### 5.1 `XAUUSD_ext_M5.csv`

**Segment O (OANDA), 2006-03-20 → 2011-05-13**
- OANDA-M1 (Mid) zu M5 zusammengefasst, TICKVOL = Summe der OANDA-Ticks, SPREAD 0.
- OANDA-Mid liegt im Mittel 0,11–0,21 USD über Dukascopy-Bid (halber Spread).

**Segment A (FX31337-Ticks), 2011-05-16 → 2016-09-02**
- 211,7 Mio. Ticks mit `fx31337_ticks_to_m1.py` zu M1-Bid/Ask aggregiert, Preise ×100 korrigiert.
- Prüfung aller Ticks: keine Ask<Bid-Fälle, keine Nullpreise, keine Zeitrücksprünge, keine doppelten Zeitstempel.
- Die fehlende Stunde 00:00–00:59 UTC entspricht 02:00/03:00 Server bzw. 19:00/20:00 NY. Sie wurde mit **14 086 nicht-flachen M5-Bars aus EPSOFT** gefüllt, soweit vorhanden. Beide Quellen sind Dukascopy-Bid; gegen A stimmen 99,2–99,6 % der gemeinsamen Bars exakt überein, Abweichungen fast nur 2011/12.
- Füllbars haben TICKVOL=0 und SPREAD=0. **Diese Kombination kommt in A sonst nicht vor und dient als Markierung.**
- Nicht füllbar blieben 193 Lücken von je 60 min um 19/20 Uhr NY: 2011: 6, 2012: 6, 2013: 17, 2014: 51, 2015: 27, 2016: 86. Dazu kommen 14 kleinere Lücken von 35–110 min.

**Segment B (Dypoi-M1), ab 2016-09-05**
- Vollständig, auch die UTC-Stunde 0.
- Die Jahresdateien überlappen am 1. September; die doppelten Zeilen sind identisch und wurden entfernt.

**Nahtstellen:** Beide Nahtstellen liegen am Wochenende (2011-05-14, 2016-09-03). Der Kurssprung an der Naht entspricht der normalen Wochenendlücke.

**TICKVOL-Proxy (B):**
- Kalibrierung: Median der Tagesverhältnisse von Tickanzahl (A) zu Bid-Volumen (B) in der Überlappung 2016-09-01 → 2018-06-19 (121 473 M5-Bars). Ergebnis k = **2837,4**.
- Korrelation Proxy/Ticks je M5: 0,863 (logarithmiert 0,943). Typischer Fehler je Bar: ±14,5 %.
- Das Monatsverhältnis schwankt zwischen 1787 und 3686.
- Für Filter vom Typ „Volumen > gleitender Schnitt“ taugt der Proxy. Absolute Tickzahlen sind es nicht.
- Korrelation des Proxys mit GFT-TICKVOL: 0,62–0,83.

**SPREAD in A und B:**
- Gleich definiert als Minimum über die M1-Bars des M5-Bars von min(Open-Spread, Close-Spread) × 100.
- Das ist eine Näherung an die übliche MT5-Konvention: Je Bar wird der kleinste Spread gespeichert. Dazu passt, dass der Median-Bar-Spread der GFT-Datei 2022–2024 nur 7–9 Punkte beträgt.
- 2011–2018 liegt die Näherung im Median **5,4 Punkte über dem exakten Tick-Minimum** (Median der Differenzen; die Mediane selbst: 0,271 gegenüber 0,192 USD).
- Dukascopy-Spreads sind breiter als die von GFT. Median je Jahr:
  - ext: 2022 30, 2023 30, 2024 33, 2025 51, 2026 62 Punkte
  - GFT: 7, 8, 9, 22, 32 Punkte

### 5.2 `NAS100_ext_M5.csv`

- **O (OANDA-Mid), 2005-01-03 → 2020-05-08:** TICKVOL = OANDA-Ticks. OANDA erzeugt nur Minuten mit Ticks, deshalb gibt es in ruhigen Nachtstunden der frühen Jahre weniger Bars (2005: Median 202 M5-Bars/Tag, ab 2011: 258–274).
- **H (HistData), 2020-05-11 → 2020-12-31:** Umrechnung wie in Abschnitt 4, TICKVOL 0 und SPREAD 0. Der tägliche Handelsschluss liegt bei 16:15 NY (letzter Bar 23:10 Server). Es fehlen also 23:15–23:55 Server gegenüber GFT.
- **M (MT5-US100), 2021-01-04 → 2025-12-31:** Broker-Export. TICKVOL = MT5-Tickvolumen. SPREAD = Minimum der M1-Spreads × 10, um vom 0,1-Punkt des Brokers auf den 0,01-Punkt von GFT umzurechnen.
- **Nahtstellen:** 2020-05-09 und 2021-01-02, jeweils am Wochenende.
  - An der Naht O→H zeigen beide Quellen dieselbe Wochenendlücke (Mo-Open OANDA 9197, HistData 9189).
  - Niveau H−M im Januar 2021: −6 Punkte (Median).
- **Warum nicht durchgehend HistData?** Die HistData-Reihe folgt 2011–2018 dem NQ-Frontmonat und **springt an den Rollterminen** (Abschnitt 6.4). OANDA zeigt diese Sprünge nicht und liefert zusätzlich Tickvolumen. Ab 2021 liefert der MT5-Export Tickvolumen und Spread.

### 5.3 Alternativdateien

- `XAUUSD_ext_oanda_M5.csv`: OANDA wie Segment O, bis 2020-05-14.
- `XAUUSD_ext_mt5_M5.csv`: MT5-XAU, aggregiert wie Segment M. Die Serverzeit war bereits NY+7; es wurden keine Bars verworfen.
- `NAS100_ext_histdata_M5.csv`: HistData wie Segment H, 2010-11-15 → 2026-02-13. Bis 2018 wurden 5 276 Bars um 00:xx Server (17:00–17:15 NY) verworfen.

---

## 6. Qualitätsprüfung

Geprüft wurde auf:
- inkonsistente Bars (OHLC), doppelte Zeitstempel, Wochenend-Bars: **überall 0**;
- Lücken > 30 min innerhalb eines Handelstages;
- Ausreißer: Range > 15 × Tagesmedian oder |Rendite| > 2 % in 5 min.

Stichproben zeigen: Die Ausreißer sind überwiegend echte News-Bewegungen (NFP 15:30 Server, FOMC 21:00/21:15, Covid-Crash März 2020).

### 6.1 Abdeckung je Jahr (Hauptdateien)

`XAUUSD_ext_M5.csv` (276 = volle M5-Bars/Tag bei 23 h):

| Jahr | Bars | Tage | Bars/Tag (Median) | TICKVOL=0-Anteil | SPREAD Median | Lücken > 30 min | Lückenstunden | Ausreißer |
|---|---|---|---|---|---|---|---|---|
| 2006 | 51 944 | 205 | 264 | 0 | 0 | 47 | 77,1 | 22 |
| 2007 | 70 827 | 260 | 276 | 0 | 0 | 16 | 28,2 | 17 |
| 2008 | 71 217 | 261 | 276 | 0 | 0 | 8 | 18,0 | 9 |
| 2009 | 71 061 | 261 | 276 | 0 | 0 | 13 | 15,4 | 14 |
| 2010 | 71 095 | 260 | 276 | 0 | 0 | 17 | 27,5 | 14 |
| 2011 | 71 080 | 259 | 276 | 0,027 | 30 | 17 | 21,8 | 3 |
| 2012 | 70 688 | 260 | 276 | 0,043 | 30 | 8 | 7,2 | 21 |
| 2013 | 70 437 | 258 | 276 | 0,041 | 30 | 18 | 17,8 | 22 |
| 2014 | 69 755 | 258 | 276 | 0,035 | 25 | 59 | 58,1 | 30 |
| 2015 | 70 445 | 258 | 276 | 0,039 | 25 | 28 | 28,0 | 27 |
| 2016 | 69 832 | 258 | 276 | 0,015 | 26 | 87 | 87,8 | 17 |
| 2017 | 70 572 | 257 | 276 | 0 | 20 | 1 | 0,9 | 20 |
| 2018 | 70 843 | 258 | 276 | 0 | 20 | 0 | 0 | 7 |
| 2019 | 70 859 | 258 | 276 | 0 | 26 | 2 | 2,8 | 16 |
| 2020 | 71 106 | 259 | 276 | 0 | 31 | 1 | 1,0 | 3 |
| 2021 | 70 878 | 258 | 276 | 0 | 30 | 0 | 0 | 12 |
| 2022–2025 | je ~70 600–71 200 | 257–259 | 276 | 0 | 30–51 | 0–1 | ≤ 1 | 1–19 |
| 2026 (bis 02.09.) | 47 309 | 173 | 276 | 0 | 62 | 0 | 0 | 6 |

`NAS100_ext_M5.csv` (volle Session bei OANDA/MT5 = 276 Bars/Tag, HistData = 267):

| Jahr | Bars | Bars/Tag (Median) | TICKVOL=0-Anteil | SPREAD Median | Lücken > 30 min | Lückenstunden | Ausreißer |
|---|---|---|---|---|---|---|---|
| 2005 | 50 630 | 202 | 0 | 0 | 164 | 136,3 | 8 |
| 2006 | 54 959 | 219 | 0 | 0 | 122 | 106,2 | 38 |
| 2007 | 59 549 | 234 | 0 | 0 | 98 | 95,9 | 24 |
| 2008 | 63 247 | 250 | 0 | 0 | 53 | 44,8 | 17 |
| 2009 | 65 513 | 261 | 0 | 0 | 22 | 17,3 | 7 |
| 2010 | 66 704 | 265 | 0 | 0 | 23 | 19,2 | 15 |
| 2011 | 68 165 | 269 | 0 | 0 | 7 | 4,6 | 8 |
| 2012 | 67 114 | 265 | 0 | 0 | 20 | 47,2 | 13 |
| 2013 | 65 602 | 258,5 | 0 | 0 | 20 | 15,0 | 18 |
| 2014 | 68 811 | 271 | 0 | 0 | 3 | 10,7 | 15 |
| 2015 | 69 875 | 273 | 0 | 0 | 0 | 0 | 13 |
| 2016 | 70 410 | 274 | 0 | 0 | 1 | 3,7 | 7 |
| 2017 | 69 712 | 273 | 0 | 0 | 4 | 14,7 | 17 |
| 2018 | 69 927 | 273 | 0 | 0 | 0 | 0 | 9 |
| 2019 | 69 958 | 273 | 0 | 0 | 1 | 3,0 | 19 |
| 2020 | 68 481 | 267 | **0,649** | 0 | 14 | 50,8 | 11 |
| 2021 | 69 447 | 274 | 0,039 | 170 | 2 | 1,4 | 12 |
| 2022 | 69 839 | 276 | 0 | 90 | 6 | 15,4 | 33 |
| 2023 | 70 606 | 276 | 0 | 170 | 3 | 3,4 | 26 |
| 2024 | 70 987 | 276 | 0 | 180 | 1 | 1,0 | 21 |
| 2025 | 70 341 | 276 | 0 | 180 | 10 | 23,4 | 25 |

Größte Lücken und ihre Ursachen:
- NAS 16.03.2020 01:35–16:45 Server: Limit-down-Sperre, in beiden Quellen gleich.
- Gold 2019-07-04, 13:25–15:25 NY: US-Feiertag. Gold 2016-09-02, 13:10–15:00 NY: Datenlücke in FX31337.
- Detaillisten stehen in `work/quality_*.txt` und `work/quality_*.pkl`.

### 6.2 Vergleich mit den GFT-Dateien (gemeinsame Bars)

| Datei | Jahr | Bars | Rendite-Korr. M5 | Close-Differenz Median | Range-Verhältnis | TICKVOL-Korr. | SPREAD ext / GFT |
|---|---|---|---|---|---|---|---|
| XAUUSD_ext (Dukascopy B) | 2022 | 70 890 | 0,9982 | −0,10 USD | 1,000 | 0,83 | 30 / 7 |
| | 2023 | 70 576 | 0,9971 | −0,08 | 0,991 | 0,62 | 30 / 8 |
| | 2024 | 68 224 | 0,9985 | −0,12 | 1,000 | 0,80 | 33 / 9 |
| | 2025 | 70 196 | 0,9977 | −0,17 | 1,011 | 0,65 | 51 / 22 |
| | 2026 | 47 309 | 0,9937 | −0,16 | 1,017 | 0,64 | 62 / 32 |
| XAUUSD_ext_mt5 | 2022 | 70 880 | 0,9990 | **+0,04** | 1,00 | **0,95** | 0 / 7 |
| | 2023 | 70 583 | 0,9968 | +0,04 | 0,99 | 0,90 | 4 / 8 |
| | 2024 | 68 224 | 0,9984 | +0,04 | 1,00 | 0,94 | 5 / 9 |
| NAS100_ext (MT5 M) | 2022 | 69 788 | 0,9984 | +4,3 Pkt | 0,992 | 0,75 | 90 / 100 |
| | 2023 | 70 555 | 0,9986 | +0,9 | 0,974 | 0,83 | 170 / 100 |
| | 2024 | 54 419 | 0,9983 | +22,2 | 1,007 | 0,73 | 180 / 140 |
| | 2025 | 69 495 | 0,9952 | +18,1 | 1,000 | 0,92 | 180 / 163 |
| NAS100_ext_histdata | 2022 | 68 552 | 0,9986 | +4,2 | 1,000 | – | 0 / 100 |
| | 2023 | 59 869 | 0,9991 | −3,4 | 1,008 | – | 0 / 100 |
| | 2024 | 52 317 | 0,9981 | +1,9 | 1,010 | – | 0 / 140 |
| | 2025 | 67 330 | 0,9911 | +0,7 | 1,003 | – | 0 / 163 |

- Wochenkorrelation, Median bzw. Minimum:
  - XAUUSD_ext 0,998 / 0,966
  - XAUUSD_ext_mt5 0,999 / 0,978
  - NAS MT5 0,999 / 0,834
  - NAS HistData 0,999 / 0,706
- Die schwächsten NAS-Wochen fallen auf News-Termine:
  - CPI 15.01.2025 und 12.02.2025: GFT-Kurs eingefroren, der 15:30-Bar ist flach.
  - CPI 12.08.2025.
  - Powell 22.08.2025: HistData verzögert.
- Abdeckung gegenüber GFT:
  - Gold: 162 GFT-Bars ohne ext-Gegenstück.
  - NAS MT5: 1 285 GFT-Bars ohne ext-Gegenstück.
  - NAS HistData: 8 753 fehlende Bars um 23:xx Server (Handelsschluss 16:15 NY) sowie die Lücken von 2023 (März–Juli 2023 täglich 1–2 h Datenlücken, 513 Lücken bzw. 594 h).

### 6.3 Quervergleiche zwischen den Quellen

- **Dukascopy untereinander:**
  - FX31337-Ticks (aggregiert) und Dypoi-M1 sind in der Überlappung in allen 607 044 Minuten identisch (Bid-OHLC und Ask-Close).
  - EPSOFT ist gegen Dypoi zu 100 % identisch, gegen FX31337 zu 99,2–99,6 %.
  - Das bestätigt die ×100-Korrektur und die UTC-Zeit.
- **Gold Dukascopy gegen OANDA (2011–2020, M5):** Renditekorrelation je Jahr 0,959–0,996, OANDA-Mid − Dukascopy-Bid = +0,11 … +0,21 USD.
- **NAS HistData gegen OANDA (2010–2020):** Renditekorrelation je Jahr 0,963–0,998. Das Niveau weicht um −3 … +15 Punkte ab, verursacht durch die Futures-Basis der HistData-Reihe.

### 6.4 Bekannte Auffälligkeiten

1. **Rollsprünge in HistData NSXUSD** (betrifft nur `NAS100_ext_histdata_M5.csv`, nicht die Hauptdatei):
   - Bis etwa 2017 liegen die Kurse auf dem 0,25-Raster des NQ-Futures (2011: 96 %).
   - An 16 Quartalsverfällen zwischen 2012-09 und 2018-09 springt die Reihe gegenüber OANDA um −0,17 … −0,88 % bzw. +0,28 … +0,39 %.
   - 2012–2016 geschieht das am Verfallsfreitag 09:25–09:55 NY, 2017–2018 am Donnerstag davor um 16:30 NY.
   - Ab 2019 ist kein systematisches Muster mehr zu erkennen; die Preise haben dann mehr Nachkommastellen, die Reihe ist CFD-ähnlich.
   - Liste: `NAS100_histdata_rollspruenge.csv`.
2. **HistData 2025-08-22:** etwa 13 Minuten Verzögerung ab 10:00 NY. **HistData 2023-03 bis 2023-07:** viele stundenweise Lücken.
3. **FX31337-Gold:** Die UTC-Stunde 0 fehlt systematisch; teilweise gefüllt, siehe 5.1.
4. **MT5-US100:** Im Januar/Februar 2021 fehlt in 35 %/15 % der Bars das Tickvolumen (Broker lieferte dort nur VOL). SPREAD ist 2021-01…03 und in ~30 % der Bars 2022-05…2023-02 gleich 0. Der Kurs liegt 2024/25 im Median 18–22 Punkte über GFT, anscheinend eine andere Preisbasis des Brokers.
5. **Lücken in den vorhandenen GFT-Dateien** (Nebenbefund, durch die ext-Dateien abgedeckt):
   - NAS100.x: 2024-05-27 → 2024-06-03 und **2024-06-06 → 2024-08-23 (78 Tage)**.
   - XAUUSD.x: **2024-10-11 → 2024-10-28 (16,5 Tage)**.
   - Beide Symbole: 2025-02-21 → 2025-02-25.

---

## 7. Hinweise für die Backtests

- **Pro Lauf nur eine Reihe verwenden.** Das Niveau von ext- und GFT-Reihen weicht ab: Gold −0,1 … −0,17 USD (Dukascopy), NAS ±5 … +22 Punkte. Ein Aneinanderhängen im selben Lauf erzeugt künstliche Sprünge. Für den Abgleich 2022–2025 dieselbe Strategie getrennt auf ext und GFT laufen lassen.
- **Kosten:**
  - SPREAD = 0 bedeutet unbekannt. Betroffen sind NAS bis 2020, Gold bis 2011-05 und die Gold-Füllbars (TICKVOL=0 und SPREAD=0).
  - Im Backtest dafür GFT-typische Werte einsetzen (Gold 0,32; NAS 1,6 Punkte) oder generell mit festen GFT-Spreads rechnen.
  - Die Dukascopy-Spreads der Golddatei sind breiter als GFT (ab 2025 etwa doppelt so breit) und damit eher konservativ.
- **Volumenfilter** (DEADBAND „Volumen > Schnitt“):
  - Gold: bis 2016-08 echte Ticks, danach Proxy. Das TICKVOL-Niveau springt an den Nähten 2011-05 und 2016-09.
  - NAS: ohne Volumen sind 2020-05-11 bis 2020-12-31 sowie Teile von Januar/Februar 2021. Bei `0 > Schnitt` entsteht dort nie ein Signal. Diesen Zeitraum entweder ausschließen oder den Filter dort deaktivieren.
- **NAS-Sessions:**
  - OANDA und MT5 handeln bis 16:59 NY (wie GFT).
  - HistData 2020-05 bis 2020-12 nur bis 16:15 NY.
  - Frühe OANDA-Jahre (2005–2008) sind nachts dünn (weniger Bars).
- **Gold 2018–2021:** Zusätzlich `XAUUSD_ext_mt5_M5.csv` testen. Kurse und Tickvolumen dieser Reihe sind nahezu GFT-identisch (die Spreads sind kleiner als bei GFT). Damit ist sie der realistischste Feed vor 2022.
- **Robustheit:** Gold kann mit `XAUUSD_ext_oanda_M5.csv` gegengeprüft werden (zweiter Feed). NAS 2011–2018 **nicht** mit der HistData-Alternativdatei testen, ohne die Rolltage auszuschließen.

---

## 8. Versuche und Sackgassen

- **Blockiert** (Proxy 403): `datafeed.dukascopy.com`, `stooq.com`, `query1.finance.yahoo.com`, `www.histdata.com`, `huggingface.co`, `www.kaggle.com`, `web.archive.org`, `codeload.github.com` (Archiv-ZIPs).
- `api.github.com` ist nur für freigegebene Repos nutzbar. Das WebSearch-Kontingent der Sitzung (200) war nach wenigen eigenen Suchen erschöpft. Weiter gesucht wurde mit der GitHub-Code- und -Repo-Suche.
- **Erreichbar:** git über github.com, `raw.githubusercontent.com` (inkl. Range-Abfragen), `media.githubusercontent.com` (Git-LFS), Release-Assets.
- **Geprüft, aber nicht verwendet:**
  - `philipperemy/FX-1-Minute-Data`: keine Daten in keiner der 69 Commit-Versionen.
  - `getdata-finance/*`: nur 6-Monats-Proben.
  - `TheSnowGuru/Stocks-Futures-…`: Dukascopy Gold/USATECH M1 nur 2023, M5 ab 2020-09.
  - `HemangGadhvi04/xau_backtester`: Dukascopy Gold 2024-06 → 2026-06.
  - HistData-XAUUSD erst ab 2021 bzw. 2023: `Craig-Pang/QuantXAU` 2021–25, `Paaktingc/forex_bot` 2023–26, `abhishukla0204/Quantalytics-26` 2024, `tk1cntt/aureus` 2026-02.
  - `ejtraderLabs/historical-data`: nur m15 und größer, kein Gold-M1.
  - `ts4blader/market_data` XAUUSD: nur 2020–2025, redundant.
  - `simonnmarket/OMEGA_OS_Kernel`: nur 2026.
  - `Sai310421/xauusd-data`: nur 2026.
  - `JonusNattapong/*`, `nvn01/*`, `ayandeep-sudo/*`, `Mbaka11/*`: keine brauchbaren Kursdateien.
- **Nicht gefunden:** freie NAS100- bzw. NQ-Minutendaten mit echtem Spread vor 2021 und Gold-Minutendaten von Dukascopy vor 2011-05 (nur lückenhaft bei EPSOFT).

---

## 9. Reproduktion

```bash
cd scratchpad/extdata/raw
git clone --depth 1 https://github.com/Dypoi/XAUUSD_Dataset.git dypoi_dukascopy_xauusd_m1
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/hizawye/better-backtest.git histdata_nsxusd_better-backtest
(cd histdata_nsxusd_better-backtest && git sparse-checkout set --no-cone 'data/histdata/nsxusd/*' 'scripts/histdata/*' README.md && git checkout)
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/FutureSharks/financial-data.git oanda_futuresharks
(cd oanda_futuresharks && git sparse-checkout set --no-cone 'pyfinancialdata/data/currencies/oanda/NAS100_USD/*' 'pyfinancialdata/data/currencies/oanda/XAU_USD/*' && git checkout)
# EPSOFT: mkdir -p epsoft_dukascopy_xauusd_m5 && curl -o epsoft_dukascopy_xauusd_m5/XAUUSD_5M.zip https://raw.githubusercontent.com/EPSOFT/Database-Currency-Pair/d34d649/XAUUSD/5M.zip && (cd epsoft_dukascopy_xauusd_m5 && unzip XAUUSD_5M.zip)
# FX31337, je Jahr y=2011..2018 (je ~170 MB Pack, ~1,3 GB entpackt):
#   git clone --depth 1 --single-branch -b XAUUSD-$y https://github.com/FX31337/FX-BT-Data-XAUUSD-DS.git fx31337_dukascopy_xauusd_ticks/y$y
#   python3 ../scripts/fx31337_ticks_to_m1.py $y   # -> derived_M1/XAUUSD_M1_bidask_dukascopy_$y.csv.gz
# LFS: curl -L -o ts4blader_market_data/US100/M1_seed.csv https://media.githubusercontent.com/media/ts4blader/market_data/5246088b258b9e94cf43300e5bd8769695c49526/US100/M1_seed.csv
#      curl -L -o antondonev_tiamat/XAUUSD_M1_RAW.csv https://media.githubusercontent.com/media/AntonDonev/Tiamat/1c2e8372281dee502fd52a40f8ee007b13a992cc/TiamatOffline/XAUUSD_M1_RAW.csv
cd ../scripts && ./run_all.sh     # prepare_sources -> build_xauusd -> build_mt5_sources -> build_nas100 -> quality -> rolljumps
```

**Zwischendateien:** Die großen Zwischendateien (`work/*.pkl` über 20 MB) wurden gelöscht; `run_all.sh` erzeugt sie neu (Laufzeit etwa 6–8 min).

**Struktur von `raw/`** (≈ 3,6 GB):
- Git-Klone mit `.git`: die FX31337-Tick-Packs liegen nur noch als `.git` (≈ 1,5 GB) vor und lassen sich mit `git checkout` wiederherstellen.
- `derived_M1/`: M1-Bid/Ask-Aggregate der Ticks mit Statistikdateien.

**Skripte:**
- `common.py`: Zeitumrechnung, Resampling, Offset-Scan, Writer.
- `quality.py`, `lagcheck.py`: Prüfungen.
- `rolljumps.py`, `gold_overlap.py`, `verify_oanda_utc.py`: Einzelanalysen.

**SHA-256 der Ergebnisdateien:**
- NAS100_ext `dfef735d…87ab`
- NAS100_ext_histdata `1dad5a98…1dac`
- XAUUSD_ext `8532e33b…b462`
- XAUUSD_ext_mt5 `ab243548…23bb`
- XAUUSD_ext_oanda `dd403ce3…196a`
