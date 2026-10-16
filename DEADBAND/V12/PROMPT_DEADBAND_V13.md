# Prompt: DEADBAND weiterentwickeln (MQL5-EA für GFT-Prop-Konten) – Stand nach Build 12.00

> Diesen Text als Ganzes in eine neue Sitzung geben. Er beschreibt Ziel, Regeln, Dateien, Daten, Arbeitsweise, alle
> bisherigen Ergebnisse und die offenen Punkte. **Beginne mit Abschnitt 5 (Dateien laden).** Neu gegenüber der letzten
> Fassung: Nachbau v12 (zwei Motorfehler behoben, erweiterter Datensatz 2010–26, Prüffenster 2011–15), Build 12.00
> (N1030 im Tick), Ergebnisse in 4.3, Arbeitsweise 7.2 (Hintergrund-Zeitlimit) und 7.5 (Motor-Unabhängigkeitstest).

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
3. Einen neuen Build liefern (`DEADBAND_V13.mq5`) und einen Bericht mit ehrlichen Zahlen.
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
| 11.00 (V11) | handelt wie V10; SR-Marken erweitert (19 Felder), Testschalter `V11TickFades`, `V11GoldPdf` (aus) | nicht kompiliert |
| **12.00 (V12)** | **V11 + N1030 im Tick (`SRT1030`, `V12TickN1030` an, 0,50 %); M5-N1030 nur virtuell** | **nicht kompiliert**, nur statisch geprüft |

### 3.2 Signalquellen (Zeiten NY, Server = NY + 7 h fest)

- **10 Listen-Fades** (`FADE_STANDARD`): Fehlausbruch einer Sitzungs-Range (Docht raus, M5-Schluss zurück) → Einstieg
  am Open der nächsten M5-Kerze; Ziel Range-Mitte oder Gegenseite; Stop hinter dem Extrem + Puffer × Range;
  Zeit-Ausstieg. Filter: Probability Grid und Portfolio-Wächter (PF der letzten 200 virtuellen Signale > 1,15,
  600 Tage). Risiko 0,75 %. NAS nur Long, Gold meist Short. N1330/N1300 ohne Schutz gültiger Tage.
  **Ab 12.00: N1030 handelt im Tick (`SRT1030`, Einstieg beim Rücklauf in die Range, 0,50 %).**
- **S0830** Spike-Fade NAS (Kauf 9:00 nach Abwärtsspike ab 8:30), 0,75 %.
- **LW** Larry-Williams-Ausbruch NAS, 0,5 %, nur ab 4 % Puffer zum Boden.
- **XA** Gold Long 18:00 → 3:00 über dem 24-h-Schnitt, 0,75 %.
- **TD** Trend-Day NAS Long 14:00, 0,5 %.
- **RSI21** (M15/M30/H1, Folgesignal, Einstand ab 1 R), 0,5 % × Gewicht.
- **Noise NAS** (Long, 3 Teile, Einstand ab 0,5 R), 0,45 %.
- **SR**: Marken IB-Tief, Vorbörse-Hoch (Short), 12–13-Uhr-Tief, Vortagstief über Nacht; Einstieg im Tick; Ziel 2 R ab
  130 s; 0,10 %. (`SRT1030` ist technisch ein Modul vom SR-Typ und handelt auch bei `SrAktiv=false`.)

### 3.3 Konto-Logik

Pufferkurve 3,5/1,25/0,1 · BelowStart 0,95 · Schutz gültiger Tage (RSI21 nur vor 13:00 oder ohne live Fade-Regime) ·
Abschluss-Ernte (alle Module, MFE ≥ 0,3 R, macht den Tag gültig) · Gewinn-Ernte (nur RSI21) · Schließen bei Reife ·
Serien-Stopp nach 3 Verlusten · Wochenende flach mit RSI21-Wiederaufnahme · Swap-Vorsorge · Floating-Bremse 0,8 %
gestuft · Tagesstopp 2,4 %.

---

## 4. Bisherige Erkenntnisse (nicht neu erfinden, darauf aufbauen)

### 4.1 Aus früheren Runden

1. **60 % Trefferquote bei CRV 1:2** gibt es mit reiner Price Action nicht (8.280 Varianten, Maximum ≈ 41 %).
2. **Konsistenzregel (GOAT)** kostet vor allem Auszahlungen → Premium ohne Regel ist besser.
3. **Nicht hilfreich** (je Strom getestet): Verlierer früh schließen, Einstand/Trailing für Fades/LW/TD/XA,
   Stop-and-Reverse, Erschöpfungsfilter, Pullback-Limit-Einstieg, mehr Risiko je Strom, Ströme abschalten, höhere
   Auszahlungsschwelle, Anpasser je Kontozustand, Bestätigungs-Einstieg (+0,1–0,3 R).
4. **Fades sind regimeabhängig:** stark 2022–26, Verlust 2011–21; der Portfolio-Wächter lässt sie live:
   2011–12, 2014–18, 2020–21: 0 %; 2013: 44 %; 2019: 42 %; 2022: 53 %; ab 2023: 98–100 % der Tage.
5. GPDF (Gold-Vortagestief) = Gold-Drift (OANDA 2010–16 ohne Vorteil) → verworfen.

### 4.2 Nachbau v12: Fehler behoben – V11-Kontozahlen sind überholt

- Im Nachbau v11 fielen **Noise-Prüfungen aus**, wenn bei flachem Konto keine anderen Signale dazwischen lagen, und die
  **RSI21-Wiederaufnahme** hing an fremden Signal-Minuten. Dadurch veränderte jeder zusätzliche Strom nebenbei den
  Noise-Strom; Vergleiche „mit/ohne Strom X“ waren verzerrt. Behoben in `eng11.py` (Replikat v12), geprüft mit
  `t12_engine_check.py` (ein abgeschalteter Dummy-Strom verändert 0 von 521 Konten).
- **Korrigiert ist V10 in allen Fenstern mindestens so gut wie V8, auch 2024–25** (V8 − V10: −0,14 ± 0,21 Ausz./J,
  −92 ± 43 $/J). Der V11-Befund „SR hilft 2024–25 nicht“ war ein Artefakt.

### 4.3 Aus Build 12.00 (Replikat v12, 16.10.2026)

Alle Kontozahlen: rollierende 1-Jahres-Konten (Start alle 7 Tage, 10k), Schlupf ¼ Spread, gepaart über 32 Störungen.

| Kontostart | V8 Ausz./J · $/J | V10 = V11 | **V12** |
|---|---|---|---|
| 2022 (Auswahl) | 9,70 · 1.697 | 12,27 · 2.409 | **12,93 · 2.522** |
| 2023 | 11,63 · 2.383 | 13,20 · 2.576 | **14,49 · 2.811** |
| 2024-01 bis 2025-02 | 7,54 · 1.563 | 7,68 · 1.656 | **7,61 · 1.676** |
| 2017–20 | 4,85 · 926 | 5,57 · 1.054 | **5,79 · 1.116** |
| 2011–15 (neu, Gold OANDA) | 3,09 · 597 | 3,71 · 681 | **3,71 · 681** |

0 Busts überall. Je Startjahr und weitere Kennzahlen: `DEADBAND_V12_Bericht.md`, Abschnitt 5.

1. **N1030 im Tick, 0,50 %** besteht: 2022 +0,66 ± 0,12, 2023 +1,30 ± 0,14, 2017–20 +0,23 ± 0,03 Ausz./J; 2024–25
   (−0,07 ± 0,17) und 2011–15 gleich; Plateau Risiko 0,40–0,60 %, Puffer 0,2–0,4 × Range; Gegenprobe N1030 auf M5
   mit 0,50 % ohne Wirkung. **Vorbehalt:** ohne Schlupf etwa halber Vorteil und 2024–25 −0,38 ± 0,24 (nicht
   signifikant, Richtung überall leicht negativ) – Tester-Ergebnis abwarten. **N1030+N1100 im Tick** (0,75 % und 0,50 %): Busts am 10.10.2013 und 21.07.2025;
   **N1100 allein**: 2024–25 −0,47.
2. **SR**: Marken 2024–26 auf Stromebene stark (+0,09 bis +0,19 R). Verdrängung real (doppelt so viele Serien-Stopps;
   NAS-Long-Fades verlieren ~280 $/J), SR selbst +239 $/J. Verworfen: SR ohne Serienzähler, Serien-Stopp aus/4, SR nur
   bei Fades live/aus, nur SRPRE, je eine Marke weg. **SR-Risiko > 0,10 % → Busts in 2011–15** (0,15 %: 14; 0,20 %:
   198; 0,30 %: 364).
3. **Regime „Fades aus“ (2011–21):** 208 Stromkandidaten (ORB, Intraday-Momentum IMOM, Ausbruch statt Fade,
   Gold-Trend, Tick-Fades), 13 bestehen auf Stromebene (IMOM bis +0,28 R, ORB5), **0 von 44 auf Kontoebene**. Ursache:
   niedrige Trefferquote (~35 %) + enger Stop → weniger gültige Tage, mehr Serien-Stopps, Busts am trailenden Boden
   (ORB: Tausende). **Unter den GFT-Regeln helfen nur Ströme mit hoher Trefferquote und mäßiger Positionsgröße.**
   Regime-Größe ×1,25 für RSI21/Noise: schlechter, 45 Busts.
4. **Engpass:** In „Fades aus“-Fenstern fehlen gültige Tage (2011–15 ~25, 2017–20 ~37, 2022 ~74 je Konto-Jahr).

---

## 5. Dateien laden (als Erstes, vor jeder anderen Arbeit)

Die Umgebung ist flüchtig: **Alles in `/home/user` ist nach dem Ende einer Sitzung weg.** Deshalb liegt der ganze Stand
im GitHub-Repo **`agattermann007-droid/claude`, Branch `claude/deadband-v11`, Ordner `DEADBAND/V12/`** (ältere Stände
in `DEADBAND/V11/` auf demselben Branch).

### 5.1 Repo holen

1. Das Repo zur Sitzung hinzufügen (`add_repo`, owner `agattermann007-droid`, repo `claude`, Zugriff `push` – ich
   erlaube dir damit, später auf diesen Branch hochzuladen).
2. Klonen (großzügiges Zeitlimit, nur ein Klon gleichzeitig):

```
git clone --depth 1 -b claude/deadband-v11 https://github.com/agattermann007-droid/claude /home/user/claude
```

3. Arbeitskopie anlegen:

```
cp /home/user/claude/DEADBAND/V12/DEADBAND_V12.mq5 /home/user/claude/DEADBAND/V11/DEADBAND_V11.mq5 /home/user/
cp -r /home/user/claude/DEADBAND/V12/build /home/user/DEADBAND_V12_build
cp -r /home/user/claude/DEADBAND/V12/Replikat_v12 /home/user/Replikat_v12
```

| Datei in `DEADBAND/V12/` | Inhalt |
|---|---|
| `DEADBAND_V12.mq5` | letzter Build 12.00 |
| `DEADBAND_V12_Bericht.md` | Bericht Build 12.00 – zuerst lesen |
| `PROMPT_DEADBAND_V13.md` | dieser Prompt |
| `build/` | `patch_v12.py`, `patch_lib.py` (Ersetzung genau einmal, sonst Abbruch), `check_mq5.py`, `kopf_v12.py`, `V11_V12.diff` |
| `Replikat_v12/` | Nachbau mit README, alle Versuche `t12_*.py` (und ältere `t_*.py`), Ausgaben in `ergebnisse/` |

### 5.2 Kursdaten laden und Nachbau vorbereiten (nicht im Repo, ~1,2 GB)

```
pip install numba
mkdir -p /home/user/data /home/user/work/npz && cd /home/user/data
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/Dypoi/XAUUSD_Dataset.git xau
git -C xau -c gc.auto=0 checkout HEAD -- .                              # Gold M1, ~580 MB
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/hizawye/better-backtest.git nas
git -C nas -c gc.auto=0 sparse-checkout set --no-cone 'data/histdata/nsxusd/normalized/*'
git -C nas -c gc.auto=0 checkout HEAD                                   # NAS M1, ~550 MB
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/FutureSharks/financial-data.git oanda
git -C oanda -c gc.auto=0 sparse-checkout set --no-cone 'pyfinancialdata/data/currencies/oanda/XAU_USD/201[0-6]/*'
git -C oanda -c gc.auto=0 checkout HEAD                                 # Gold 2010-16, ~170 MB
cd /home/user/Replikat_v12
python prep_m1.py all                    # -> /home/user/work/npz
python prep_ext.py                       # -> /home/user/work/npz_ext (Gold OANDA + Dukascopy, NAS)
NPZ_DIR=/home/user/work/npz_ext REP_CACHE=/home/user/work/cache_ext python prep11.py
python t12_engine_check.py               # Motor-Unabhaengigkeit: 0 von 521 Konten duerfen abweichen
python t12_base.py                       # Grundlinie, 32 Seeds -> ergebnisse/base_v10_32.pkl
python t12_final.py                      # V10 gegen V12
```

Abgleich (Seed 0, erweiterter Satz, korrigierter Motor): V10 Start 2022 11,86, 2024–25 8,14, 2017–20 5,78,
2011–15 3,64 Ausz./J; V8 9,82 / 7,22 / 4,82 / 3,30. 32 Seeds: V10 12,27 / 13,20 / 7,68 / 5,57 / 3,71 (Fenster 2022,
2023, 2024–25, 2017–20, 2011–15). Weicht der Abgleich ab oder fehlt etwas, **frag mich**, bevor du etwas neu baust.

### 5.3 Sichern

Neue Stände (Build, Bericht, Replikat, Logs) am Ende jedes größeren Schritts auf **denselben Branch**
`claude/deadband-v11` in einen neuen Ordner `DEADBAND/V13/` committen und pushen – das erlaube ich hiermit
ausdrücklich für diesen Branch. Keine anderen Branches ändern, kein Pull Request ohne Rückfrage, keine Kursdaten und
keine `cache/`- oder `.pkl`-Dateien ins Repo.

---

## 6. Daten und Zugang

### 6.1 Kursdaten

| Daten | Quelle | Hinweise |
|---|---|---|
| Gold M1 Bid/Ask 2016-09 bis 2026-09 | `github.com/Dypoi/XAUUSD_Dataset` (Dukascopy) | Zeit UTC → NY → +7 h |
| NAS M1 2010-11 bis **2026-02-13** | `github.com/hizawye/better-backtest`, `data/histdata/nsxusd/normalized/*.json` | Quelle = NY-Ortszeit (geprüft) |
| Gold M1 2010–2016-08 | `github.com/FutureSharks/financial-data`, OANDA XAU_USD (Mid) | mit `prep_ext.py` vor Dukascopy gesetzt → Prüffenster 2011–15 |
| GFT M5 2022–26 (`NAS100_x_M5.csv`, `XAUUSD_x_M5.csv`) | mein Google Drive | je ~30 MB; die Drive-Schnittstelle bricht bei 10 MB ab. **Bitte mich um ZIPs < 10 MB** (z. B. je Jahr) – weiter der wichtigste offene Datenpunkt |

### 6.2 Zugang

- Erreichbar: github.com (git clone, Sparse-Checkout), Google Drive bis 10 MB je Datei.
- Gesperrt: media.githubusercontent.com (Git-LFS), datafeed.dukascopy.com, help.goatfundedtrader.com,
  GitHub-Suche über die API.

### 6.3 Datenmängel (im Nachbau behandelt)

- **NAS: werktags keine Kurse 16:15–17:00 NY** (ab 2019 ganz) → flache Füllkerzen zum letzten Kurs.
- **NAS Feb.–Jul. 2023:** stundenweise Lücken. **NAS vor 2019:** Rollsprünge an Quartalsverfallstagen → an diesen Tagen
  keine NAS-Einstiege; offene Positionen vor Lücken > 10 min neutral schließen.
- **Gold-Wiedereröffnung 18:00:** Spread-Modell dort zu günstig; Signale in den ersten 30 Minuten gesondert prüfen.
- **OANDA-Gold 2010–16** ist Mid statt Bid (Abweichung ~ halber Spread); Wochenend-Einzelkurse entfernt.

### 6.4 Kosten im Nachbau

Spread NAS 1,63 bei 15.000, Gold 0,32 bei 2.000 (proportional zum Kurs); Gold-Kommission 5 $/Lot; **Schlupf ¼ Spread**
auf Markt-Einstiege, Stop- und Zeit-Ausstiege. Sensitivität ohne Schlupf im Bericht immer mit angeben.

---

## 7. Arbeitsweise (Pflicht)

### 7.1 Erst messen, dann bauen

- Jede Änderung zuerst im Replikat: M1-genau, pessimistisch (Stop vor Ziel; Ziel erst ab 130 s bzw. ab der nächsten
  M5-Kerze bei Kerzen-Modulen; Tick-Einstieg nur, wenn die M1-Kerze es eindeutig belegt).
- Vor neuen Ideen den Nachbau gegen die Kennzahlen in 5.2 prüfen. Weicht er ab, erst reparieren.

### 7.2 Kontoebene: Rauschen und Laufzeit

- Schon 3 % andere Signale verschieben ein Konto-Ergebnis um ±1 Ausz./J. **Einzelne Läufe – auch im MT5-Tester – sagen
  wenig.** Jeden Kontovergleich **gepaart über 16 (Entscheidung: 32) Störungen** rechnen (`evl11.evaluate_seeds`,
  `evl11.paired`, Fenster `evl11.WIN5`) und Differenz ± Standardfehler berichten.
- Laufzeit: 32 Störungen × 5 Fenster ≈ 3,5–4 min (4 Kerne). **Hintergrundbefehle werden nach 2 Stunden beendet** –
  lange Ketten in Stücke < 2 h teilen, Ergebnisse je Variante sofort ins Log schreiben.
- `pkill -f` / `pgrep -f` mit dem Skriptnamen trifft auch die eigene Shell (deren Befehlszeile enthält den Namen) –
  Prozesse über `ps -eo pid,args | grep "^ *[0-9]* python ..."` suchen.

### 7.3 Saubere Auswahl

- **Auswahl:** Konten mit Start 2022. Danach müssen **alle Prüfungen** besser oder mindestens gleich sein: Start
  2024-01 bis 2025-02, Start 2017–2020 und **Start 2011–2015**. **0 Busts** in allen Störungen.
- Für Ströme, die nur bei „Fades aus“ handeln, ist 2022 wenig aussagekräftig: dann Auswahl 2017–20 und Prüfung
  2011–15 (unabhängige Daten) plus 2022/2024–25 nicht schlechter.
- Nur die Mitte eines Plateaus übernehmen (Nachbarparameter und Nachbar-Risiken auch prüfen), keine Spitzen.
  Gegenprobe rechnen, die den Mechanismus isoliert (z. B. gleiches Risiko ohne die neue Einstiegslogik).
- **Gold-Long-Ströme** zusätzlich auf OANDA 2010–16 prüfen; ohne Vorteil dort = Drift.
- Zahl der getesteten Varianten im Bericht nennen (Zufallsgefahr).

### 7.4 Kennzahlen

Je Fenster: Ausz./J, $/J (Anteil nach Split und Gebühr), $/J inkl. offenem Gewinn, Ø Auszahlung, Tage bis zur ersten
Auszahlung (Median), Anteil Konto-Jahre ohne Auszahlung, Busts; zusätzlich je Startjahr.

### 7.5 Motor-Unabhängigkeit

Nach jeder Änderung am Kontomotor `t12_engine_check.py` laufen lassen: Ein abgeschalteter Strom darf kein Konto
verändern. Ein Vergleich „mit/ohne X“ ist nur dann sauber.

---

## 8. Lieferung

- **Build** `DEADBAND_V13.mq5` aus dem letzten Build per Patch-Skript (`patch_lib.Patch.rep`: jede Ersetzung genau
  einmal, sonst Abbruch). Kopfblock ganz oben: Build/Datum, was neu ist, Replikat-Zahlen vorher/nachher, getestet und
  verworfen, Rückfall-Einstellungen, „NICHT KOMPILIERT ERSTELLT – vor dem Einsatz im MetaEditor kompilieren und im
  Strategietester (Echte Ticks) prüfen“.
- **Code-Stil:** reines ASCII, deutsche Kommentare mit Build-Nummer, neue Funktionen als Eingaben schaltbar,
  Voreinstellung = getestete Variante. Schutzmechanismen nie schwächen (Notbremsen, Floating-/Tagesbremse,
  130-s-Regel, Hedging-, News-Sperre, Budgets, Pufferkurve).
- **Statische Prüfung:** `check_mq5.py` und Diff gegen den vorigen Build; zeigen, dass die Rückfall-Einstellung
  handelsgleich ist.
- **Bericht** `DEADBAND_V13_Bericht.md` (Deutsch): Kurzfassung mit Tabelle vorher/nachher, Diagnose, Tests mit Zahlen
  (± Standardfehler), Einstellungen, Checkliste für den Tester, Grenzen, Dateien.
- **Replikat** als `Replikat_v13/` (numpy, pandas, numba; Pfade über `NPZ_DIR`, `REP_CACHE`, `REP_T_LO`, `XAU_DIR`,
  `NAS_DIR`, `OANDA_DIR`).
- **Kommunikation:** Deutsch, knapp. Zwischenstände in ein, zwei Sätzen. Am Ende sagen, was ich im Tester prüfen soll.
- **Git:** nur auf `claude/deadband-v11` (Ordner `DEADBAND/V13/`) committen und pushen; alles andere nur auf meine
  Bitte. Keine Modellnamen in Dateien oder Commits.

---

## 9. Offene Punkte (nach Priorität)

1. **Tester-Ergebnisse auswerten**, sobald ich sie liefere (NAS100.x + XAUUSD.x, Echte Ticks, 2024 bis heute):
   a) V12 mit `V12TickN1030=false` = V11 handelsgleich? b) V12 Voreinstellung gegen a) (Einstiege `SRT1030`,
   Kleinster Abstand zum Boden) c) `SrAktiv` false gegen true. Wenn ich MT5-Berichte oder Deal-Listen hochlade, den
   Nachbau damit kalibrieren (insbesondere Tick-Einstiege `SRT1030`/SR gegen die M1-Schätzung).
2. **GFT-M5-ZIPs** einlesen und den Nachbau auf dem echten Feed nachrechnen.
3. **Regime „Fades aus“ (2011–21):** weiter offen. Gesucht sind Ströme mit **hoher Trefferquote** (≥ 55–60 %) und
   mäßiger Positionsgröße, die gültige Tage erzeugen, wenn die Fades gesperrt sind. Nicht wiederholen: ORB,
   Intraday-Momentum, Ausbruch statt Fade, Gold-Trend-Ausbruch, Regime-Größe > 1, SR-Risiko > 0,10 %.
4. **Weitere Fades im Tick einzeln** (N0930, N1300, N1800 waren auf Stromebene im Tick besser): jeweils allein, mit
   kleinerem Risiko, gepaart gegen V12; Busts 10/2013 und 7/2025 besonders prüfen.
5. **Konto-Mechanik mit korrigiertem Motor nachrechnen**, die in V11 nur mit dem fehlerhaften Nachbau geprüft wurde
   (Abschluss-Ernte 0,2/0,5 R, Reserve, RSI21-Schutzzeit, Gewinn-Ernte).
6. **Gold ohne Drift:** Gold-Price-Action beidseitig, mit Regime-/Trendfilter, Prüfung 2010–16 (OANDA) Pflicht.
7. **Instant-GOAT-Regeln** nur, falls ich ein GOAT-Konto nutze.
