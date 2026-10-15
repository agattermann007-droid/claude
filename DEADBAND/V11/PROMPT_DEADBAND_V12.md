# Prompt: DEADBAND weiterentwickeln (MQL5-EA für GFT-Prop-Konten) – Stand nach Build 11.00

> Diesen Text als Ganzes in eine neue Sitzung geben. Er beschreibt Ziel, Regeln, Dateien, Daten, Arbeitsweise, alle
> bisherigen Ergebnisse und die offenen Punkte. **Beginne mit Abschnitt 5 (Dateien laden).** Neu gegenüber der letzten
> Fassung: 5 (Laden und Sichern über GitHub), 6.3 (Datenmängel), 7.2 (Rauschen und gepaarte Störungen) und die
> Ergebnisse von Build 11.00 in Abschnitt 4.

---

## 1. Rolle und Auftrag

Du arbeitest als Quant-Entwickler an meinem MetaTrader-5-Expert-Advisor **DEADBAND**. Er handelt **NAS100.x** und
**XAUUSD.x** auf Prop-Konten von **Goat Funded Trader (GFT)**.

**Mein Ziel:** mehr Auszahlungen, kürzere Abstände zwischen den Auszahlungen, größere Auszahlungen – **ohne das Konto zu
verlieren (0 Busts)**. Entscheidend ist der Ertrag pro Jahr (mein Anteil) bei möglichst kurzem Abstand zwischen den
Auszahlungen. Eine schöne Trefferquote allein zählt nicht.

**Was ich von dir will:**
1. Strategien und den EA verbessern. Bevorzugt Price Action mit Einstieg im Tick, wenn das nachweislich hilft.
2. Jede Idee zuerst im Python-Nachbau messen (Stromebene, dann Kontoebene), erst dann in MQL5 einbauen.
3. Einen neuen Build liefern (`DEADBAND_V12.mq5`) und einen Bericht mit ehrlichen Zahlen.
4. Wenn nichts die Prüfung besteht: das klar sagen. Dann keinen Handel ändern, höchstens abschaltbare Testschalter
   (Voreinstellung aus) für die besten Kandidaten einbauen, damit ich sie im MT5-Tester prüfen kann.

---

## 2. Konten und Regeln (GFT Instant Premium, mein Hauptkonto)

Alle Regelwerte sind im EA Eingaben. Wo unsicher, vorsichtig rechnen und mich bitten, das Dashboard zu prüfen.

- **Maximalverlust:** 6 % vom Startsaldo, trailend am Equity-Hoch (nach jeder Auszahlung neu). Darunter = Bust.
- **Tagesverlust:** 3 % gegen den Tagesstart 17:00 NY; vorsichtige Lesart max(Saldo, Equity) um 17:00 NY.
- **Floating-Verlust:** höchstens 1,0 % (Konten ab 02.09.2026). Strenge Lesart: Summe der Verlustpositionen inkl. Swap
  und Kommission. Der EA hält offene Stop-Risiken ≤ 0,9 % gesamt und ≤ 0,9 % je Idee (Symbol + Richtung).
- **Gültiger Tag:** realisiert ≥ 0,5 % vom Start + 0,50 $ Reserve; **5 gültige Tage** je Auszahlung.
- **Zyklus:** mindestens **14 Kalendertage** ab dem ersten Trade (Kauf ab 21.09.2026).
- **Mindestauszahlung:** 100 $ Anteil (EA rechnet 105 $) → 131,25 $ Gewinn auf 10k bei 80 % Split. Deckel 6 % für die
  ersten 2 Auszahlungen. 3 % Auszahlungsgebühr.
- **Gewinne aus Trades unter 120 s werden gestrichen** (EA: Ziele und Gewinnschlüsse erst ab 130 s).
- Kein Hedging im selben Symbol; News ±6 min um rote USD-Termine; kein VPS; 30 Tage ohne Trade = Konto weg; Margin je
  Idee > 80 % = Gambling (EA-Grenze 70 %).
- **Instant GOAT** (Alternative, nur falls ich es sage): 15-%-Konsistenzregel (weich, verzögert nur die Auszahlung);
  übrige Werte unbestätigt.

---

## 3. Der EA heute

### 3.1 Builds

| Build | Inhalt | Status |
|---|---|---|
| 8.10 (V8) | Live-Stand: 10 Fades, S0830, LW, XA, TD, RSI21, Noise | live |
| 10.00 (V10) | V8 + SR (Liquidity-Sweep-Reclaim NAS im Tick, 0,10 %) | nicht kompiliert, nicht getestet |
| **11.00 (V11)** | **handelt wie V10**; SR-Marken erweitert (Symbol, Stop-/Zielart, CRV, Risiko, Range-Filter, Wächter je Marke; `SrListe` 12 oder 19 Felder); `MAXFADE` 22; Testschalter `V11TickFades`, `V11GoldPdf` (beide aus) | **nicht kompiliert**, nur statisch geprüft |

### 3.2 Signalquellen (Zeiten NY, Server = NY + 7 h fest)

- **10 Listen-Fades** (`FADE_STANDARD`): Fehlausbruch einer Sitzungs-Range (Docht raus, M5-Schluss zurück) → Einstieg
  am Open der nächsten M5-Kerze; Ziel Range-Mitte oder Gegenseite; Stop hinter dem Extrem + Puffer × Range;
  Zeit-Ausstieg. Filter: Probability Grid und Portfolio-Wächter (PF der letzten 200 virtuellen Signale > 1,15,
  600 Tage). Risiko 0,75 %. NAS nur Long, Gold meist Short. N1330/N1300 ohne Schutz gültiger Tage.
- **S0830** Spike-Fade NAS (Kauf 9:00 nach Abwärtsspike ab 8:30), 0,75 %.
- **LW** Larry-Williams-Ausbruch NAS, 0,5 %, nur ab 4 % Puffer zum Boden.
- **XA** Gold Long 18:00 → 3:00 über dem 24-h-Schnitt, 0,75 %.
- **TD** Trend-Day NAS Long 14:00, 0,5 %.
- **RSI21** (M15/M30/H1, Folgesignal, Einstand ab 1 R), 0,5 % × Gewicht.
- **Noise NAS** (Long, 3 Teile, Einstand ab 0,5 R), 0,45 %.
- **SR** (ab V9): Marken IB-Tief, Vorbörse-Hoch (Short), 12–13-Uhr-Tief, Vortagstief über Nacht; Einstieg im Tick;
  Ziel 2 R ab 130 s; 0,10 %.

### 3.3 Konto-Logik

Pufferkurve 3,5/1,25/0,1 · BelowStart 0,95 · Schutz gültiger Tage (RSI21 nur vor 13:00 oder ohne live Fade-Regime) ·
Abschluss-Ernte (alle Module, MFE ≥ 0,3 R, macht den Tag gültig) · Gewinn-Ernte (nur RSI21) · Schließen bei Reife ·
Serien-Stopp nach 3 Verlusten · Wochenende flach mit RSI21-Wiederaufnahme · Swap-Vorsorge · Floating-Bremse 0,8 %
gestuft · Tagesstopp 2,4 %. Die Tages-Ernte 16:00 wirkt nicht (hängt am ausgeschalteten DEADBAND-Modul).

---

## 4. Bisherige Erkenntnisse (nicht neu erfinden, darauf aufbauen)

### 4.1 Aus früheren Runden

1. **60 % Trefferquote bei CRV 1:2** gibt es mit reiner Price Action nicht (8.280 Varianten, Maximum ≈ 41 %).
2. **Konsistenzregel (GOAT)** kostet vor allem Auszahlungen → Premium ohne Regel ist besser.
3. **Nicht hilfreich** (je Strom getestet): Verlierer früh schließen, Einstand/Trailing für Fades/LW/TD/XA,
   Stop-and-Reverse, Erschöpfungsfilter, Pullback-Limit-Einstieg, mehr Risiko je Strom, Ströme abschalten, höhere
   Auszahlungsschwelle, Anpasser je Kontozustand.
4. **Fades sind regimeabhängig:** stark 2022–26, Verlust 2016–21; der Portfolio-Wächter lässt sie 2016–21 nur bei
   ~7 % der Signale live.

### 4.2 Aus Build 11.00 (Replikat v11, 15.10.2026)

Alle Kontozahlen: rollierende 1-Jahres-Konten (Start alle 7 Tage, 10k), Schlupf ¼ Spread, Mittel über 16 Störungen.

| Kontostart | V8: Ausz./J · $/J | V10 = V11: Ausz./J · $/J |
|---|---|---|
| 2022 | 9,2 · 1.531 | 12,0 · 2.288 |
| 2023 | 11,4 · 2.354 | 13,1 · 2.542 |
| 2024–25 | 8,4 · 1.759 | **7,9 · 1.670** |
| 2017–20 | 5,0 · 939 | 5,5 · 1.025 |

Je Startjahr V10: 2017 5,4 · 2018 7,0 · 2019 3,4 · 2020 6,3 · 2022 12,1 · 2023 13,1 · 2024 7,6 Ausz./J.
Ø Auszahlung 240–285 $, erste Auszahlung im Median nach 15–21 Tagen (2017–20: 24–45), 0 Busts.

1. **SR hilft 2022, 2023 und 2017–20, aber nicht 2024–25** (−0,5 ± 0,35 Ausz./J, auch ohne Schlupf). Die
   V10-Erwartung „+2 Ausz./J“ ist nur für 2022–23 gedeckt.
2. **Hypothese „Move schon vorbei“ bestätigt, aber nicht handelbar:** 38–88 % der Fade-Verlierer erreichen nie
   +0,2 R. Bestätigungs-Einstieg (+0,1/0,2/0,3 R per Stop-Order) ist in keinem der 18 Ströme in allen Zeiträumen
   besser; bei SR klar schlechter.
3. **Fades im Tick** (Einstieg beim Rücklauf in die Range): Stromebene in allen Zeiträumen mehr R (Summe 10 Fades
   2016–21 −146 → −28, 2022–23 +64 → +73, 2024–26 +96 → +142), ~2,4× mehr Trades. Kontoebene N1030+N1100:
   +1,2 / +1,9 / −0,6 / +0,6 Ausz./J (2022 / 2023 / 2024–25 / 2017–20) und **3 Busts** → verworfen; Testschalter
   `V11TickFades`. N1800 im Tick ist schon in der Auswahl schlechter.
4. **Sweep-Reclaim-Scan** Gold 2.784 + NAS 1.824 Varianten → 27 bzw. 67 Überlebende auf Stromebene. Alle
   Gold-Überlebenden sind „Tief gesweept → Long“. Kontoebene: **alle NAS-Kandidaten schlechter** (NAS-Long-Bereich
   gesättigt: Budget, Idee-Deckel, Hedging), Gold nur GPDF.
5. **GPDF** (Gold unter Vortagestief 18:00–2:00, zurück → Long, 3 R): Vorteil hängt stark an den ersten Minuten nach
   der Wiedereröffnung 18:00 (unzuverlässige Kurse); auf **OANDA-Gold 2010–16 ohne Vorteil, 2014–15 klar negativ** =
   Gold-Drift → verworfen; Testschalter `V11GoldPdf` (Fenster ab 18:30).
6. **SR-Risiko:** 0,15 % schlechter (2024–25), 0,20 % besser, 0,25 % gemischt – kein Plateau. **Ab 0,30 % Busts.**
7. **Konto-Mechanik ohne Wirkung:** Abschluss-Ernte 0,2/0,5 R, 10 % Reserve, Serien-Stopp 2/4 (schlechter),
   ohne Schutz gültiger Tage (deutlich schlechter), RSI21-Schutz 12/14 Uhr (Rauschen), Gewinn-Ernte ab 0,5 R.
8. **Engpass:** Meist bindet die 14-Tage-Frist oder der Mindestgewinn, selten die gültigen Tage. In 2017–20 (Fades
   aus) trägt der Rest nur ~5,5 Ausz./J – dort ist der größte Hebel.

---

## 5. Dateien laden (als Erstes, vor jeder anderen Arbeit)

Die Umgebung ist flüchtig: **Alles in `/home/user` ist nach dem Ende einer Sitzung weg.** Deshalb liegt der ganze Stand
im GitHub-Repo **`agattermann007-droid/claude`, Branch `claude/deadband-v11`, Ordner `DEADBAND/V11/`**.

### 5.1 Repo holen

1. Das Repo zur Sitzung hinzufügen (`add_repo`, owner `agattermann007-droid`, repo `claude`, Zugriff `push` – ich
   erlaube dir damit, später auf diesen Branch hochzuladen).
2. Klonen (großzügiges Zeitlimit, nur ein Klon gleichzeitig):

```
git clone --depth 1 -b claude/deadband-v11 https://github.com/agattermann007-droid/claude /home/user/claude
```

3. Arbeitskopie anlegen:

```
cp /home/user/claude/DEADBAND/V11/DEADBAND_V1*.mq5 /home/user/claude/DEADBAND/V11/DEADBAND_V8.mq5 /home/user/
cp -r /home/user/claude/DEADBAND/V11/build /home/user/DEADBAND_V11_build
cp -r /home/user/claude/DEADBAND/V11/Replikat_v11 /home/user/Replikat_v11
```

Inhalt von `DEADBAND/V11/`:

| Datei | Inhalt |
|---|---|
| `DEADBAND_V11.mq5` | letzter Build 11.00 (handelt wie V10, Testschalter aus) |
| `DEADBAND_V10.mq5`, `DEADBAND_V8.mq5` | Basis und Live-Stand 8.10 |
| `DEADBAND_V11_Bericht.md` | Bericht Build 11.00 – zuerst lesen |
| `PROMPT_DEADBAND_V12.md` | dieser Prompt |
| `build/` | `patch_v11.py`, `patch_lib.py` (Ersetzung genau einmal, sonst Abbruch), `check_mq5.py` (ASCII, Klammern, Format-Strings), `kopf_v11.py`, `V10_V11.diff` |
| `Replikat_v11/` | Nachbau mit README, alle Versuche `t_*.py`, Ausgaben in `ergebnisse/` (Logs und JSON) |

Ältere Stände (bis 6.10, Replikat v5/v6, Fremddaten-Skripte) liegen im selben Repo unter `DEADBAND/` auf dem Branch
`claude/bold-allen-do276v`.

### 5.2 Kursdaten laden und Nachbau vorbereiten (nicht im Repo, ~1 GB)

```
pip install numba
mkdir -p /home/user/data /home/user/work/npz && cd /home/user/data
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/Dypoi/XAUUSD_Dataset.git xau
git -C xau -c gc.auto=0 checkout HEAD -- .                              # Gold M1, ~470 MB
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/hizawye/better-backtest.git nas
git -C nas -c gc.auto=0 sparse-checkout set --no-cone 'data/histdata/nsxusd/normalized/*'
git -C nas -c gc.auto=0 checkout HEAD                                   # NAS M1, ~490 MB
cd /home/user/Replikat_v11
python prep_m1.py all        # -> /home/user/work/npz (NPZ_DIR)
python prep11.py             # -> cache/D11.pkl
python t_v10.py              # Abgleich, Seed 0: V10 Start 2022 11,58 Ausz./J, 2024-25 7,17; V8 9,46 / 7,02
```

Nur bei Bedarf (Gold-Baisse 2010–16 als Gegenprobe, für `t_oanda.py`, Pfad über `OANDA_DIR`):

```
cd /home/user/data && git clone --depth 1 --filter=blob:none --no-checkout https://github.com/FutureSharks/financial-data.git oanda
git -C oanda -c gc.auto=0 sparse-checkout set --no-cone 'pyfinancialdata/data/currencies/oanda/XAU_USD/201[0-6]/*'
git -C oanda -c gc.auto=0 checkout HEAD
```

Weicht der Abgleich ab oder fehlt etwas, **frag mich**, bevor du etwas neu baust.

### 5.3 Sichern

Neue Stände (Build, Bericht, Replikat, Logs) am Ende jedes größeren Schritts auf **denselben Branch**
`claude/deadband-v11` in einen neuen Ordner `DEADBAND/V12/` committen und pushen – das erlaube ich hiermit
ausdrücklich für diesen Branch. Keine anderen Branches ändern, kein Pull Request ohne Rückfrage, keine Kursdaten und
keine `cache/`-Dateien ins Repo.

---

## 6. Daten und Zugang

### 6.1 Kursdaten

| Daten | Quelle | Hinweise |
|---|---|---|
| Gold M1 Bid/Ask 2016-09 bis 2026-09 | `github.com/Dypoi/XAUUSD_Dataset` (Dukascopy) | Zeit UTC → NY → +7 h |
| NAS M1 2010-11 bis **2026-02-13** | `github.com/hizawye/better-backtest`, `data/histdata/nsxusd/normalized/*.json` | Quelle = NY-Ortszeit (geprüft) |
| Gold M1 2010–2016 (Gegenprobe Baisse) | `github.com/FutureSharks/financial-data`, `pyfinancialdata/data/currencies/oanda/XAU_USD/<Jahr>/` | OANDA Mid, UTC; nur mit Sparse-Checkout holen, `git ls-tree -l` vermeiden (lädt jede Datei einzeln), bei „connection reset“ wiederholen |
| GFT M5 2022–26 (`NAS100_x_M5.csv`, `XAUUSD_x_M5.csv`) | mein Google Drive | je ~30 MB; die Drive-Schnittstelle bricht bei 10 MB ab. **Bitte mich um ZIPs < 10 MB** (z. B. je Jahr) – das ist der wichtigste offene Datenpunkt |

### 6.2 Zugang

- Erreichbar: github.com (git clone, Sparse-Checkout), Google Drive bis 10 MB je Datei.
- Gesperrt: media.githubusercontent.com (Git-LFS), datafeed.dukascopy.com, help.goatfundedtrader.com,
  GitHub-Suche über die API.

### 6.3 Datenmängel (im Replikat v11 schon behandelt)

- **NAS: werktags keine Kurse 16:15–17:00 NY** (ab 2019 ganz). Ohne Korrektur laufen Ausstiege um 16:40 und der
  Freitag-Schluss 16:45 bis 18:00 bzw. übers Wochenende (falscher Bust). Lösung: flache Füllkerzen zum letzten Kurs,
  nur für den Kursverlauf.
- **NAS Feb.–Jul. 2023:** stundenweise Lücken. **NAS vor 2019:** Rollsprünge an Quartalsverfallstagen.
  Lösung: an diesen Tagen keine NAS-Einstiege; offene Positionen vor Lücken > 10 min neutral schließen.
- **Gold-Wiedereröffnung 18:00:** Das Spread-Modell ist dort zu günstig. Signale in den ersten 30 Minuten nach 18:00
  gesondert prüfen oder ausschließen.

### 6.4 Kosten im Nachbau

Spread NAS 1,63 bei 15.000, Gold 0,32 bei 2.000 (proportional zum Kurs); Gold-Kommission 5 $/Lot; **Schlupf ¼ Spread**
auf Markt-Einstiege, Stop- und Zeit-Ausstiege. Ohne Schlupf liegen alle Kontozahlen ~25–35 % höher (Sensitivität im
Bericht immer mit angeben).

---

## 7. Arbeitsweise (Pflicht)

### 7.1 Erst messen, dann bauen

- Jede Änderung zuerst im Replikat: M1-genau, pessimistisch (Stop vor Ziel; Ziel erst ab 130 s bzw. ab der nächsten
  M5-Kerze bei Kerzen-Modulen; Tick-Einstieg nur, wenn die M1-Kerze es eindeutig belegt).
- Vor neuen Ideen den Nachbau gegen die Kennzahlen in 4.2 prüfen (V10-Lauf, `t_v10.py`). Weicht er ab, erst reparieren.

### 7.2 Kontoebene: Rauschen beachten

- Schon 3 % andere Signale verschieben ein Konto-Ergebnis um ±1 Ausz./J und ±170 $/J. **Einzelne Läufe – auch im
  MT5-Tester – sagen wenig.**
- Deshalb jeden Kontovergleich **gepaart über 16 (Entscheidung: 32) Störungen** rechnen (`evl11.evaluate_seeds`,
  `evl11.paired`) und Differenz ± Standardfehler berichten. Unter ~0,4 Ausz./J bzw. ~100 $/J ist nichts nachgewiesen.
- Laufzeit: ein Satz rollierender Konten ≈ 3 s, mit 16 Störungen ≈ 40 s (4 Kerne). Lange Läufe im Hintergrund mit
  Log-Datei.

### 7.3 Saubere Auswahl

- **Auswahl:** Konten mit Start 2022 (handeln 2022–23). Danach müssen **beide Prüfungen** besser oder mindestens gleich
  sein: Start 2024-01 bis 2025-02 (handeln 2024–26) und Start 2017–2020 (Fremddaten 2017–21). **0 Busts** in allen
  Störungen.
- Nur die Mitte eines Plateaus übernehmen (Nachbarparameter und Nachbar-Risiken auch prüfen), keine Spitzen.
- **Gold-Long-Ströme** zusätzlich auf OANDA 2010–16 (Baisse 2011–15) prüfen; ohne Vorteil dort = Drift.
- Zahl der getesteten Varianten im Bericht nennen (Zufallsgefahr).

### 7.4 Kennzahlen

Je Fenster: Ausz./J, $/J (Anteil nach Split und Gebühr), $/J inkl. offenem Gewinn, Ø Auszahlung, Tage bis zur ersten
Auszahlung (Median), Anteil Konto-Jahre ohne Auszahlung, Busts; zusätzlich je Startjahr.

---

## 8. Lieferung

- **Build** `DEADBAND_V12.mq5` aus dem letzten Build per Patch-Skript (`patch_lib.Patch.rep`: jede Ersetzung genau
  einmal, sonst Abbruch). Kopfblock ganz oben: Build/Datum, was neu ist, Replikat-Zahlen vorher/nachher, getestet und
  verworfen, Rückfall-Einstellungen, „NICHT KOMPILIERT ERSTELLT – vor dem Einsatz im MetaEditor kompilieren und im
  Strategietester (Echte Ticks) prüfen“.
- **Code-Stil:** reines ASCII, deutsche Kommentare mit Build-Nummer, neue Funktionen als Eingaben schaltbar,
  Voreinstellung = getestete Variante. Schutzmechanismen nie schwächen (Notbremsen, Floating-/Tagesbremse,
  130-s-Regel, Hedging-, News-Sperre, Budgets, Pufferkurve).
- **Statische Prüfung:** `check_mq5.py` (ASCII, Klammerbilanz, Format-Strings gegen Argumentzahl) und Diff gegen den
  vorigen Build; zeigen, dass die Voreinstellung handelsgleich ist, wo das beabsichtigt ist.
- **Bericht** `DEADBAND_V12_Bericht.md` (Deutsch): Kurzfassung mit Tabelle vorher/nachher, Diagnose, Tests mit Zahlen
  (± Standardfehler), Einstellungen, Checkliste für den Tester, Grenzen, Dateien.
- **Replikat** als `Replikat_v12/` (numpy, pandas, numba; Pfade über `NPZ_DIR`, `REP_CACHE`, `XAU_DIR`, `NAS_DIR`,
  `OANDA_DIR`).
- **Kommunikation:** Deutsch, knapp. Zwischenstände in ein, zwei Sätzen. Am Ende sagen, was ich im Tester prüfen soll.
- **Git:** nur auf `claude/deadband-v11` (Ordner `DEADBAND/V12/`) committen und pushen, wie in 5.3 beschrieben;
  alles andere nur auf meine Bitte. Keine Modellnamen in Dateien oder Commits.

---

## 9. Offene Punkte (nach Priorität)

1. **Tester-Ergebnisse auswerten**, sobald ich sie liefere (NAS100.x + XAUUSD.x, Echte Ticks, 2024 bis heute):
   a) V11-Voreinstellung = V10 handelsgleich? b) `SrAktiv` false gegen true (hilft SR 2024–26 auf GFT-Daten?)
   c) `V11TickFades` d) `V11GoldPdf`. Wenn ich MT5-Berichte oder Deal-Listen hochlade, den Nachbau damit kalibrieren.
2. **GFT-M5-ZIPs** einlesen und den Nachbau auf dem echten Feed nachrechnen (Abweichung Fremddaten ↔ GFT messen).
3. **Regime 2016–21 (Fades aus):** Ströme suchen, die genau dann tragen, wenn der Portfolio-Wächter die Fades sperrt
   (z. B. Ausbruch/Momentum, Gold beidseitig mit Trendfilter). Bewertung nur in Konten, die in diesem Regime laufen.
   Das ist der größte offene Hebel (5,5 gegen 12–13 Ausz./J).
4. **SR 2024–25 verstehen:** Warum hilft SR dort nicht? Verdrängung (Budget, Idee-Deckel, Hedging mit NAS-Longs)
   oder schwächere Marken? Prüfen: SR nur bei nicht-live Fade-Regime, SR-PRE (Short) ohne die Long-Marken.
5. **Tick-Fades nachbessern:** Bust-Ursache (Juli 2025, Boden) klären; Varianten mit kleinerem Risiko (0,5 %) oder nur
   N1030 gepaart prüfen.
6. **Gold ohne Drift:** Gold-Price-Action beidseitig, mit Regime-/Trendfilter, Prüfung 2010–16 (OANDA) Pflicht.
7. **Instant-GOAT-Regeln** nur, falls ich ein GOAT-Konto nutze.
