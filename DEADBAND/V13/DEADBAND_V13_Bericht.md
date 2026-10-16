# DEADBAND V13 – Bericht (Build 13.00, 17.10.2026)

> Repo-Fassung ohne Kontodaten: Saldo, Boden, Trade-Liste, Live-Ergebnisse in $ und die Live-CSV-Dateien liegen nur
> lokal bei Alex (`Downloads\DEADBAND_V13\`).

## 1. Kurzfassung

**Auftrag:** Aus den bisherigen Live-Trades die Änderungen ableiten, die die Auszahlungen maximieren.

**Vorgehen:** Ich habe die 29 Live-Trades vom 28.09. bis 16.10.2026 aus dem GFT-Konto geholt und den Nachbau zum ersten Mal auf den echten GFT-Kursen gerechnet (M1-Export, echte Spreads). Danach habe ich die Builds gegen das gerechnet, was live **tatsächlich** passiert.

**Drei Befunde:**

1. **Der EA handelt genau wie der Nachbau.** Alle 24 Fade-Trades, S0830 und LW finden sich im Nachbau auf dem GFT-Feed wieder:
   - Stop identisch, Einstieg meist 0–0,5 Punkte daneben, Live-R = virtuelles R.
   - Die Verluste seit 28.09. sind gewöhnliche Signal-Ergebnisse, kein Ausführungsfehler.
2. **XA (Gold-Asien) kann live nie handeln.** Das gilt für alle Builds ab 8.00 und auch für den MT5-Tester.
   - Das Signal kommt an der ersten Kerze nach der Tagespause (18:00 NY).
   - `FadeDurchlauf` wertet nur Kerzen live aus, vor denen keine Lücke liegt (`frisch`, Zeile 6773 in V8).
   - Der Nachbau hat XA immer mitgerechnet. Alle bisherigen Vergleiche bezogen sich damit auf einen Handel, den es live nicht gibt.
3. **V12, im Repo als „beste Version“ geführt, ist auf dem GFT-Feed kostenempfindlich.** Der Tick-Einstieg von N1030 verliert im jüngsten Fenster 2025–26:
   - −0,89 Auszahlungen/Jahr bei normalen Kosten,
   - −3,66 bei doppeltem Spread.

**Build 13.00 = V12-Code mit drei geänderten Voreinstellungen:**

| Eingabe | 12.00 | **13.00** | Wirkung live |
|---|---|---|---|
| `AsiaAktiv` | true | **false** | keine (XA handelte nie); Nachbau und Tester entsprechen damit dem Echtbetrieb |
| `SrRiskPct` | 0,10 | **0,05** | SR-Marken mit halbem Risiko |
| `V12TickN1030` | true | **false** | N1030 wieder auf M5 (wie V8) |

Gegenüber dem heutigen Live-Stand (8.10, praktisch ohne XA) kommt damit vor allem **SR mit 0,05 %** dazu.

**Ergebnis (Nachbau, 32 gepaarte Störungen, 1-Jahres-Konten alle 7 Tage, Differenz zu V8 ohne XA = Live-Stand):**

| Fenster (Kontostart) | Ausz./J live → V13 | Differenz Ausz./J | Differenz $/J | Busts |
|---|---|---|---|---|
| GFT 2022 | 15,74 → 15,94 | +0,20 ± 0,12 | +155 ± 37 | 0 |
| GFT 2023 | 14,86 → 16,58 | +1,72 ± 0,13 | +384 ± 46 | 0 |
| GFT 2024–25 | 12,68 → 13,77 | +1,09 ± 0,14 | +253 ± 33 | 0 |
| GFT 2025–26 (neu) | 11,65 → 11,87 | +0,22 ± 0,27 | +15 ± 58 | 0 |
| Fremd 2022 | 9,90 → 11,22 | +1,32 ± 0,12 | +537 ± 32 | 0 |
| Fremd 2023 | 9,94 → 12,69 | +2,75 ± 0,23 | +443 ± 53 | 0 |
| Fremd 2024–25 | 6,26 → 7,04 | +0,79 ± 0,26 | +120 ± 49 | 0 |
| Fremd 2017–20 | 5,00 → 5,30 | +0,29 ± 0,09 | +80 ± 19 | 0 |
| Fremd 2011–15 | 3,44 → 3,96 | +0,53 ± 0,07 | +138 ± 15 | 0 |

V13 ist in keinem Fenster schlechter als der Live-Stand, auch nicht unter Kostenstress (Abschnitt 5.3). Der Vorteil ist **2023 und 2024–25 klar**, 2022 und 2025–26 auf dem GFT-Feed klein (im Rauschen). „$/J“ ist dein Anteil nach 80 % Split und 3 % Gebühr.

## 2. Abgleich der Live-Trades

### 2.1 Daten

Alles nur gelesen aus dem GFT-Terminal (`mt5_live_holen.py`):
- Deals und Orders mit SL/TP (nur lokal).
- Ticks NAS100.x ab 07.09., XAUUSD.x ab 02.10. (früher liefert der Server für Gold keine Ticks).
- Symboldaten: Kontrakt NAS 10, Gold 100, beide 2 Stellen.

Die EA-Logs liegen nicht auf diesem PC: V8 läuft auf einem anderen Rechner, hier sind nur die Builds 4.x/5.00.

### 2.2 Ergebnis je Modul

Die Tabelle je Modul (Trades, R, $) steht nur in der lokalen Fassung. Für die Strategie sagen 29 Trades nichts aus
(Streuung ±4 R). Vor dem 28.09. lief noch das alte DEADBAND-Ausbruchsmodul (Magic 230250/51).

### 2.3 Live gegen Nachbau (`g_live.py`, Ergebnis-CSV nur lokal)

- **Fades, S0830, LW:** Jeder Live-Trade hat ein Nachbau-Signal zur selben Minute.
  - Stop identisch.
  - Einstieg im Mittel +0,06 Punkte. S0830 um 9:00 NY: +3,5 Punkte.
  - Live-R = virtuelles R (Abweichung meist < 0,05 R).
- **Signale ohne Live-Trade**, alle durch EA-Regeln erklärbar:
  - LW 13×, meist wegen `LwMinPuffer` 4 % (die 13 Signale zusammen hätten −5,6 R gebracht),
  - X0630 2× wegen Schutz gültiger Tage bzw. Serien-Stopp,
  - X1000S 1×,
  - **XA 8×** (siehe 3).
- **Noise:** live jeweils eine Stunde später (11:00 statt 10:00 NY). Beide Tage hatten um 10:00 NY eine rote USD-Nachricht; das ist die News-Sperre, die der Nachbau nicht nachbildet.
- **Spreads** (Ticks gegen Minutenkerzen, Sep./Okt. 2026):
  - NAS im Mittel 1,77 Punkte, Gold 0,41.
  - Der GFT-Bar-Spread entspricht dem Tick-Mittel (NAS 1,00×, Gold 0,92×).
  - Das alte Spread-Modell des Nachbaus (proportional zum Kurs) rechnet bei heutigen Kursen NAS 3,32 und Gold 0,67, also etwa doppelte Kosten.
- **Schlupf:**
  - Markt-Einstiege zum Kerzen-Open live praktisch 0 (Modell: ¼ Spread).
  - Stop-Ausstiege 0–2,7 Punkte, im Mittel etwa ½ Spread (Modell: ¼). Deshalb der Stresstest mit ½ Spread.

## 3. Fund: XA handelt live nie

`FadeDurchlauf` (V8 Zeile 6773, V12 Zeile 7325, gleich in allen Builds ab 6.00):

```
bool frisch = (TimeCurrent() - b0 < 60) && (b0 - r[n-2].time == PeriodSeconds(PERIOD_M5));
... FadeKerze(m, r[i], r[i+1], frisch && i == n-2);
```

Wie das XA blockiert:
- XA wertet das Kerzenpaar (letzte Kerze vor 17:00 NY, erste Kerze ab 18:00 NY) aus.
- Zwischen diesen beiden Kerzen liegen 65 Minuten, also gilt `frisch` = false.
- XA rechnet deshalb nur virtuell.
- Im Live-Zeitraum gab es 8 XA-Signale und 0 XA-Trades.

Die Sperre gegen Datenlücken ist für alle anderen Module richtig; XA ist das einzige Modul, dessen Signal immer direkt hinter der Tagespause liegt.

**Reparieren lohnt sich nicht.** Ohne Codeänderung ginge es über `AsiaEinNY = -355`, also Einstieg 18:05 NY ohne Lücke. Gegen den Live-Stand bringt das (GFT-Feed, 32 Störungen):

| XA-Einstieg | 2022 | 2023 | 2024–25 | 2025–26 |
|---|---|---|---|---|
| 18:05 NY | −1,13 | +0,62 | +0,74 | −1,09 |
| 18:10 NY | −0,57 | +0,18 | +0,81 | −1,30 |

XA bringt etwas Geld (+40 bis +480 $/J), verschiebt aber die Auszahlungen. Der Strom ist schwach (GFT 2022–26: +0,058 R je Trade, PF 1,33) und kostet über Serien-Stopps und den Schutz gültiger Tage andere Trades. Deshalb ist XA in V13 abgeschaltet.

## 4. Nachbau auf dem GFT-Feed

### 4.1 Daten und Abgleich

- **GFT-M1-Export** vom 16.10.2026: NAS100.x ab 28.10.2019 (davor nur Platzhalter-Kerzen), XAUUSD.x ab 2011.
  - Serverzeit ist NY + 7 h, auch in den Wochen mit verschobener Sommerzeit.
  - Bekannte Lücken auf dem Server: NAS 06.06.–23.08.2024, Gold 11.–28.10.2024.
- **Kostenmodell:** Bar-Spread × 1,0 (NAS) bzw. × 1,1 (Gold), kalibriert gegen die Ticks. Schlupf ¼ Spread wie bisher.
- **Fenster:** Start 2022, 2023, 2024-01 bis 2025-02, neu **2025-02 bis 2025-10** (läuft bis 16.10.2026).
- **Windows-Anpassung:** Die Rechenprozesse erben unter Windows die Signale nicht. `evl11.INIT` und `gsetup.py` konfigurieren deshalb jeden Prozess.
  - Kontrolle: Auf den Fremddaten trifft mein Aufbau den V12-Bericht exakt, z. B. V12 gegen V10 +0,66 / +1,30 / −0,07 / +0,23 / −0,01 und V8 gegen V10 −2,56 / −1,57 / −0,14 / −0,71 / −0,62.

### 4.2 Stromebene (GFT-Feed 2022–26, R je Trade)

Alle Ströme sind positiv:
- N1030 +0,31, S0830 +0,30, LW +0,27, X0300S +0,22, X1000S +0,19, SRPRE +0,22, SRIB +0,19, SRT1030 +0,19 …
- am schwächsten SRH12 +0,06, XA +0,06, SRPDN +0,02.
- 2026 schwächer: N1800 −0,10, N1330 −0,02, N1300 −0,08, X1000S −0,08, LW −0,04.

Auf dem GFT-Feed liegt das Kontoergebnis deutlich über den Fremddaten (V8 mit XA 2022: 15,4 statt 9,7 Ausz./J). Hauptgrund sind die echten, etwa halb so hohen Spreads.

### 4.3 Builds wie geliefert (mit XA, wie der Nachbau bisher rechnete)

| GFT-Feed, gepaart | 2022 | 2023 | 2024–25 | 2025–26 |
|---|---|---|---|---|
| V10 gegen V8 | +1,04 | +1,12 | −1,44 | +1,63 |
| V12 gegen V10 | +0,32 | −0,04 | **−2,47** | **−1,15** |

Der starke Einbruch von V12 in 2024–25 kommt aus dem Zusammenspiel mit XA. Ohne XA, also so, wie V12 live handeln würde, sieht es so aus (gegen V8 ohne XA): +0,87 / +1,73 / +1,11 / **−0,89 ± 0,36**.

## 5. Tests für Build 13.00

Zahl der geprüften Varianten (Zufallsgefahr): 21 Konto-Varianten, dazu 3 Kosten-Szenarien auf dem GFT-Feed und 2 auf den Fremddaten.

### 5.1 Was die Schwäche 2025–26 verursacht

| Variante (ohne XA) gegen V8 ohne XA, GFT | 2022 | 2023 | 2024–25 | 2025–26 |
|---|---|---|---|---|
| V8 + nur N1030 im Tick | −0,15 | +0,36 | +0,53 | **−1,09** |
| V10 (SR 0,10, N1030 M5) | +0,06 | +1,26 | +1,51 | −0,46 |
| V12 (SR 0,10 + Tick-N1030) | +0,87 | +1,73 | +1,11 | −0,89 |
| nur SRIB + SRPRE | +0,86 | +1,44 | +0,10 | −0,42 |
| nur SRIB | +0,35 | +1,20 | +1,23 | −1,95 |

Zwei Ursachen:
- **Tick-N1030:** schwach 2025–26 und kostenempfindlich, siehe 5.3.
- **SR mit 0,10 %:** Die SR-Verluste (39 % Treffer) lösen doppelt so viele Serien-Stopps aus (V8 22 je Jahr, V10 53), die dann die Fades mit hoher Trefferquote sperren.

### 5.2 SR-Risiko (Plateau)

| SR-Risiko (V10-Handel, ohne XA) | GFT 2022 | 2023 | 2024–25 | 2025–26 | Fremd 2022 | 2023 | 2024–25 | 2017–20 | 2011–15 |
|---|---|---|---|---|---|---|---|---|---|
| 0,03 | −0,83 | +0,68 | +0,65 | +0,44 | +1,62 | +2,50 | +0,06 | +0,28 | +0,36 |
| **0,05** | **+0,20** | **+1,72** | **+1,09** | **+0,22** | **+1,32** | **+2,75** | **+0,79** | **+0,29** | **+0,53** |
| 0,075 | −0,19 | +1,38 | +1,42 | +0,43 | +1,85 | +2,89 | +1,24 | +0,56 | +0,75 |
| 0,10 | +0,06 | +1,26 | +1,51 | −0,46 | +1,54 | +3,15 | +2,09 | +0,78 | +0,87 |

- Auf den Fremddaten ist mehr SR besser, auf dem GFT-Feed 2025–26 weniger.
- 0,05 % ist die einzige Stufe, die in allen Fenstern und Kosten-Szenarien (5.3) mindestens gleich ist.
- Die Nachbarn 0,03 und 0,075 haben je ein leicht negatives Fenster; die Fläche ist also flach mit Rauschen um ±0,5.
- Ehrlich gesagt: Mit 0,10 % wären auf den Fremddaten 2024–25 und 2017–20 etwa +1,3 bzw. +0,5 Ausz./J mehr drin. Das kostet aber im jüngsten GFT-Fenster.

### 5.3 Kostenstress (gegen V8 ohne XA, GFT-Feed, Ausz./J)

| Szenario | Variante | 2022 | 2023 | 2024–25 | 2025–26 |
|---|---|---|---|---|---|
| ohne Schlupf | **V13** | +0,07 | +2,41 | +1,09 | +1,53 |
| Schlupf ¼ (Basis) | **V13** | +0,20 | +1,72 | +1,09 | +0,22 |
| Schlupf ½ | **V13** | +0,09 | +0,83 | +1,39 | +0,68 |
| Schlupf ½ | V12-Code + Tick-N1030 + SR 0,05 | +1,05 | +1,13 | +1,11 | **−0,85** |
| altes Spread-Modell (≈ ×2) | **V13** | +1,42 | +2,38 | +0,88 | +0,07 |
| altes Spread-Modell (≈ ×2) | V12-Code + Tick-N1030 + SR 0,05 | +1,88 | +2,60 | +0,55 | **−3,66** |

Auf den Fremddaten mit Schlupf ½: V13 +1,99 / +2,71 / +1,03 / +0,01 / +0,46. **0 Busts in allen Rechnungen.**

### 5.4 Kennzahlen V13 (GFT-Feed, Mittel über 16 Störungen)

| Fenster | Ausz./J | $/J | Ø Auszahlung | 1. Ausz. (Median) | ohne Ausz. | Busts |
|---|---|---|---|---|---|---|
| 2022 | 15,99 | 2.950 | 238 $ | 17 T | 0 % | 0 |
| 2023 | 16,46 | 3.600 | 282 $ | 17 T | 0 % | 0 |
| 2024–25 | 13,76 | 3.161 | 296 $ | 16 T | 0 % | 0 |
| 2025–26 | 11,75 | 2.307 | 253 $ | 18 T | 0 % | 0 |

Zum Vergleich der Live-Stand (V8 ohne XA): 15,61 / 14,75 / 12,47 / 11,30 Ausz./J, 2.740 / 3.165 / 2.853 / 2.228 $/J.

Fremddaten V13: 2022 11,10 · 2023 12,56 · 2024–25 7,44 · 2017–20 5,30 · 2011–15 3,88 Ausz./J; 1. Auszahlung im Median 16–37 Tage.

## 6. Kontozustand

Nur in der lokalen Fassung. Allgemein gilt: Unter dem Startsaldo und mit wenig Puffer zum Boden handeln alle Module
über die Pufferkurve kleiner, und LW ist unter 4 % Puffer gesperrt. V13 ändert daran nichts; die Pufferkurve ist der
Bust-Schutz und wird nicht geschwächt.

## 7. Checkliste

**Strategietester** (GFT-Terminal, NAS100.x + XAUUSD.x, Echte Ticks; V13 liegt schon unter `MQL5\Experts\DEADBAND\DEADBAND_V13.ex5`):

1. **V13 Voreinstellung** gegen **V13 mit `SrAktiv=false`** (= V8-Handel) und gegen **V12** (`V12TickN1030=true`, `SrRiskPct=0.10`):
   - Zeitraum 01.01.2024 bis heute, möglichst auch 2022–2023.
   - Vergleichen: Auszahlungen, $, kleinster Abstand zum Boden.
2. Im Journal: „XA“ darf mit `AsiaAktiv=false` gar nicht angelegt werden. SR-Trades mit Risiko 0,05 % × Pufferkurve.
3. Einzelne Tester-Läufe schwanken um ±1 Ausz./J. Bitte mehrere Startdaten nehmen (01.01., 01.04., 01.07.2024).

**Wechsel im Live-Konto** (machst du selbst, am besten am Wochenende oder ohne offene Position):

1. V13 im MetaEditor des Live-Rechners kompilieren (hier: 0 Fehler, 0 Warnungen).
2. Am Live-Chart V8 entfernen und V13 einhängen.
3. **Kontospezifische Eingaben vom V8-Chart übernehmen:** `KaufdatumGFT`, `StartBalanceOverride`, `FloorOverride` + `FloorOverrideZeit`, `AuszahlungKennung`, `MagicBase` (230250 – damit V13 Zyklus, gültige Tage und Positionen erkennt), `UsePush`, News-Einstellungen.
4. Nur die drei Werte aus Abschnitt 1 sind neu; alle anderen Eingaben wie in V8/V12.
5. Nach dem Start im Journal prüfen: „Fade-Module … LIVE“, „SR … 0,05 %“, Boden wie im GFT-Dashboard.

**Rückfall:** `SrAktiv=false` (+ `V12TickN1030=false`) = Handel wie 8.10. Oder V12-Werte: `V12TickN1030=true`, `SrRiskPct=0.10`, `AsiaAktiv=true`.

## 8. Grenzen

- **Kurze Live-Strecke:** 29 Trades sind für die Strategie keine Aussage (Streuung ±4 R). Der Wert des Abgleichs liegt darin, dass er Ausführung und Nachbau bestätigt und den XA-Fehler zeigt.
- **GFT-Feed erst ab 2020** (NAS). Die Regime „Fades aus“ (2011–21) lassen sich nur auf den Fremddaten prüfen.
- **Kurzes Fenster 2025–26:** 35 Starts, Standardfehler ±0,25–0,36 Ausz./J. Dort ist V13 nur „gleich oder leicht besser“.
- **Auswahl:** Das SR-Risiko 0,05 % habe ich gewählt, nachdem ich die Schwäche 2025–26 gesehen hatte. Die Plateau-Prüfung und die Fremddaten mildern, aber beseitigen diese Gefahr nicht.
- **Nicht nachgebildet:** News-Sperre (verschiebt Noise und einzelne Einstiege), Kontoerkenner/Anpasser (neutral), Margin nur grob. SR-Tick-Einstiege gibt es live noch nicht (V8 hat kein SR). Ihr echter Schlupf ist unbekannt, deshalb der Stresstest.
- **Laufzeit:** V13 ist kompiliert, aber nicht im Strategietester gelaufen; den Tester habe ich nicht gestartet.

## 9. Dateien (Repo `DEADBAND/V13/`; lokal zusätzlich `.ex5`, Compiler-Log und Live-Daten in `Downloads\DEADBAND_V13\`)

| Datei | Inhalt |
|---|---|
| `DEADBAND_V13.mq5` | Build 13.00 (lokal kompiliert, 0 Fehler/0 Warnungen) |
| `DEADBAND_V13_Bericht.md` | dieser Bericht (Repo-Fassung ohne Kontodaten) |
| `build/` | `patch_v13.py` (5 exakte Ersetzungen aus V12, braucht `../V12/build/patch_lib.py`), `V12_V13.diff` |
| `Replikat_v13/` | Nachbau v12 + GFT-Feed: `prep_gft.py`, `xg.py`/`xe.py` (Datensätze), `gsetup.py` (Prozess-Konfiguration), `g_live.py` (Live-Abgleich), `g_streams.py`, `g_base.py`, `g_var.py`, `g_mods.py`, `g_final.py`, geändert `prep11.py` (`REP_SPREAD=gft`), `evl11.py` (`INIT`), `prep_ext.py` (Kopie statt Verweis) |
| `Replikat_v13/ergebnisse/` | Logs der Modellrechnungen und Endzahlen `final_*.json` (die Live-Dateien `a1_trades.csv`, `g_live_abgleich.csv` und die Kontodaten liegen nur lokal) |

Kursdaten: GFT-Export in `D:\Meine Ablage\DEADBAND_Kursdaten_20261016_2245` (Google Drive); Fremddaten in `Downloads\DEADBAND_V12_Live\fremd\` (nicht im Repo).
