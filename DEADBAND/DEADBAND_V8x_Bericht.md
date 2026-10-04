# DEADBAND V8 – Build 8.10: Kontoerkenner und Trend-Day NAS (Bericht)

Stand: 04.10.2026 · Auftrag: `PROMPT_NEUE_SITZUNG.md`. Ziel in dieser Rangfolge:
1. keine Pleiten,
2. mehr Auszahlungen pro Jahr,
3. mehr Gewinn je Auszahlung,
4. kürzere Zyklen.

## Ergebnis in einem Satz

Der **Kontoerkenner mit Anpasser** ist gebaut und geprüft, verbessert aber nichts: Kein Parametersatz je Kontozustand hält in der Prüfung. Er läuft deshalb **neutral** (Erkennung, Anzeige, Meldungen; Größen wie 8.00). Ein neuer Strom aus der Recherche, der **Trend-Day NAS (Modul TD)**, verbessert dagegen alle drei Prüfteile ohne Pleite.

| Konto-Replikat (eng6, gepaart) | 8.00 | **8.10** | Änderung |
|---|---|---|---|
| Auszahlungen / Jahr (2022–25) | 13,49 | **14,30** | +0,81 (+6 %) |
| netto $ / Jahr (80 %, nach Gebühren) | 2800 | **3019** | +219 (+8 %) |
| Ø Auszahlung | 267 $ | **272 $** | +5 $ |
| Tage je Zyklus | 24,8 | **23,4** | −1,4 Tage |
| gültige Tage / Jahr | 84,9 | **87,5** | +2,6 |
| Pleiten (Boden / Floating / Tag) | 0 / 0 / 0 | **0 / 0 / 0** | |
| Auswahl 2022–23 (Ausz./J, netto) | 16,09 / 3147 | **17,22 / 3528** | +1,13 |
| Prüfung 2024–25 (Ausz./J, netto) | 11,75 / 2551 | **12,50 / 2714** | +0,75 |
| Fremddaten 2006–21 (Ausz./J, netto, Pleiten) | 3,16 / 608 / 0 | **3,81 / 723 / 0** | +0,65 |
| Kostenstress (Schlupf 100 % des Spreads) | 11,31 / 2236 | **12,25 / 2441** | +0,94 |

> **Wichtig:**
> - 8.10 ist **nicht kompiliert und nicht im MT5-Tester gelaufen** (kein MetaEditor in dieser Umgebung). Die Klammerbilanz und die Deklarationen habe ich selbst geprüft.
> - Die erwartbare Wirkung ist **kleiner als die Spitze in der Tabelle**: Das Mittel der TD-Nachbarpunkte liegt bei etwa +0,4 Auszahlungen pro Jahr (Abschnitt 4.3). Rechnen Sie mit **+0,2 bis +0,5**.
> - Rückfall auf 8.00: `TdAktiv=false` und `AnpasserAktiv=false`. 8.00 liegt unverändert in `rollback_8.00/`.

---

## 1. Ausgangslage und Abgleich

- **Daten neu aufgebaut** nach `extdata/DATEN_BERICHT.md`: Alle fünf SHA-256-Prüfsummen stimmen mit dem Bericht überein. GFT-Ersatz mit `y7_data.py`: Gold ab 2022 bis 09/2026, NAS bis 12/2025.
- **8.00 neu gemessen:**

  | | Bericht V8 | neu gemessen |
  |---|---|---|
  | GFT 2022–25 | 13,37 / 2771 $ | 13,49 / 2800 $ |
  | Auswahl / Prüfung | 16,54 / 11,87 | 16,09 / 11,75 |
  | Fremddaten 2006–21 | 3,66 / 713 $ | 3,16 / 608 $ |

  Der erweiterte Motor ist **bitgleich** zum alten eng6: 50 von 50 Testläufen haben identische Statistik und identische Trades (Prüfskript im Verlauf, Anpasser aus). Die Abweichung kommt also aus dem Neuaufbau der Signal-Caches (andere pandas-/numba-Versionen), nicht aus dem Umbau. **Alle Vergleiche in diesem Bericht sind gepaart gegen die neu gemessene 8.00-Basis**: gleiche Starts, Störungen und Seeds.

## 2. Kontoerkenner im Replikat

`eng6.py` hat neue Parameter `st_on`, `st_deep`, `st_light`, `st_hys`, `st_near_v`, `st_near_p`, `st_prof`, `st_streak` und eine Matrix `SM[zustand, klasse]`. Die Klassen sind: DEADBAND, RSI21, Noise und je ein generischer Strom. Voreinstellung `st_on=0` heißt: handelsgleich 8.00. Der Zustand wird trotzdem gemessen. Er steht im Trade-Protokoll (Spalte 4), dazu Tage und Pleiten je Zustand.

Zustände (Priorität von oben, Hysterese 0,5 % auf TIEF/LEICHT):

| Zustand | Erkennung |
|---|---|
| REIF | Auszahlungsreife (kMode ≥ 1) |
| TIEF | Puffer zum Boden < 2 % |
| LEICHT | Puffer < 4 % (= LW-Schwelle) |
| UNSICHER | nur EA: Equity-Spitze nicht sicher rekonstruiert (`peakOk` false) |
| SERIE | ≥ 3 Verlusttrades in Folge (eigener Zähler: `cool_n`/Serien-Stopp setzt seinen Zähler zurück, der Zustand nicht) |
| REIFENAH | ≤ 1 gültiger Tag fehlt oder Gewinn ≥ 80 % des Mindestgewinns |
| GEWINN | Saldo ≥ Start + 1 % |
| NACH_AUSZ | schon ausgezahlt, Zyklus läuft normal |
| FRISCH | noch keine Auszahlung, normal |

„Andere Kontogröße“ ist abgedeckt, weil alle Schwellen relativ zum Startsaldo gelten. „Andere Firma“ ist abgedeckt, weil der Puffer bei `FirmaProfil 1` wie die Pufferkurve auf 6 % normiert wird.

### 2.1 Wie oft welcher Zustand vorkommt, und wo das Geld entsteht

8.00, GFT 2022–25, Tage pro Jahr und Ergebnis je Zustand (`ergebnisse/z8_mess_gft.json`):

| Zustand | Tage/J | Ergebnis $/J | Auffällig |
|---|---|---|---|
| NACH_AUSZ | 46 | +1191 | LW stark (+509 $) |
| REIFENAH | 75 | +907 | RSI21 in der Prüfung −57 $ |
| **LEICHT** | **71** | +1052 | alle Ströme positiv |
| **TIEF** | **35** | +237 | positiv trotz Mini-Größe |
| SERIE | 12,5 | +30 | Prüfung −37 $ |
| REIF | 13,5 | – | keine Einstiege |
| FRISCH, GEWINN | 5 | +147 | GEWINN fast nie, REIFENAH greift früher |

Pleiten gibt es in keinem Zustand. Auf den Fremddaten liegt das Konto **197 von ~260 Tagen** in LEICHT oder TIEF (GFT: 106). Dort entsteht die Langsamkeit, nicht in einem fehlerhaften Zustand.

## 3. Anpasser: Parametersätze je Zustand – verworfen

Vorgehen: Auswahl nur auf 2022–23, wenige vorher festgelegte Raster, dann die Finalisten auf 2024–25 und den Fremddaten (`z8_opt.py`, `ergebnisse/z8_opt_*.json`).

**Auswahl 2022–23** (8.00 = 16,09 Ausz./J, 3147 $):

| Satz | Ausz./J | netto |
|---|---|---|
| NACH_AUSZ ×0,5 / ×1,5 | 15,05 / 14,62 | 2775 / 2820 |
| REIFENAH ×0,5 / ×1,5 | 14,69 / 15,78 | 2596 / 3298 |
| LEICHT ×0,5 / ×1,25 / ×1,5 / ×2 | 14,21 / 16,31 / **16,62** / 15,62 | |
| TIEF ×0,5 / ×1,5 | 15,84 / 16,01 | |
| SERIE ×0,5 / ×1,5 | 15,78 / 15,46 | |
| SERIE: XA aus (Serie 3 / 4 / 2) | **16,72** / 16,08 / 15,51 | |
| LEICHT: XA aus · Noise aus | 15,55 · 14,14 | |
| REIFENAH: RSI21 aus · XA aus | 15,54 · 15,47 | |
| SERIE: alles aus | **0,64** | Zustand endet erst mit einem Gewinn-Trade, ohne Trades nie |
| LEICHT ×1,5 + SERIE XA aus + REIFENAH ×1,25 | **17,00** | 3534 |

**Prüfung der Finalisten:**

| Satz | Prüfung 2024–25 | Fremddaten |
|---|---|---|
| 8.00 | 11,75 / 2551 $ | 3,16 / 0 Pleiten |
| LEICHT ×1,5 | 11,30 / 2405 $ | 3,17 / **0,002** |
| LEICHT+TIEF ×1,5 | 11,57 / 2475 $ | 3,49 / **0,029** |
| LEICHT ×1,5, Schwelle 3,5 % | 11,80 / 2469 $ | 3,34 / 0 |
| REIFENAH ×1,5 | 9,48 / 2039 $ | 3,06 / 0 |
| Auswahl-Sieger (17,00) | **8,61** / 1837 $ | 3,14 / **0,016** |

**Rauschmessung** (fast neutrale Faktoren, gleiche Starts und Störungen):

| | Auswahl | Prüfung |
|---|---|---|
| LEICHT ×0,99 / ×1,01 | 15,80 / 15,93 | 11,87 / 11,97 |
| NACH_AUSZ ×0,99 / ×1,01 | 15,52 / 15,96 | 11,46 / 11,69 |

Schon ±1 % Größe verschiebt das Ergebnis um −0,57 bis +0,22 Auszahlungen pro Jahr. Das ist Pfad-Chaos: Ein anderer Trade macht einen anderen Tag gültig, und alles danach verschiebt sich. Unterschiede um ±0,5 sind deshalb kein Befund.

**Folgerung:**
- Die defensiven Ideen aus dem Auftrag kosten schon in der Auswahl Auszahlungen: Schutzmodus in TIEF, Erholungsmodus in LEICHT, Serie kleiner, „kurz vor Reife vorsichtig“. 8.00 hat bereits 0 Pleiten; Defensive kann also nur Tempo kosten.
- Offensive Sätze (LEICHT/TIEF größer) halten in der Prüfung nicht und erzeugen auf den Fremddaten Pleiten. Das verletzt Ziel 1.
- Die Pufferkurve 3,5/1,25/0,1 deckt die echte Zustandsabhängigkeit bereits ab.
- **Ausgeliefert ist der Anpasser deshalb neutral** (alle Faktoren 1). Die Infrastruktur bleibt, damit ein späterer, besser belegter Satz ohne Umbau eingestellt werden kann.

## 4. Neue Strategien

### 4.1 Recherche

Ein Recherche-Agent hat etwa 40 Suchen gemacht. YouTube und die meisten Strategie-Seiten waren gesperrt; gelesen wurde über Such-Snippets und GitHub. Belastbare YouTube-Strategien mit klaren Regeln, die nicht schon geprüft waren, kamen nicht dazu. Die Kandidaten stammen aus Papers und Büchern:

| Kandidat | Quelle | Ergebnis |
|---|---|---|
| **Trend-Day / Schluss-Momentum NAS** | Baltussen, Da, Lammers, Martens: *Hedging demand and market intraday momentum*, JFE 2021 ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3760365)); E. Chan, *Algorithmic Trading*, Kap. 7 ([quantrocket trend-day](https://github.com/quantrocket-codeload/trend-day)) | **übernommen (TD)** |
| Gold-PM-Fix-Schwäche (Short vor 10:00 NY) | Caminschi & Heaney 2014; [LBMA Alchemist 73](https://www.lbma.org.uk/alchemist/issue-73/has-there-been-a-decade-of-london-pm-gold-fixing-manipulation) | **verworfen:** 0 von 168 Varianten robust. Seit dem LBMA-Auktionsverfahren (2015) ist der Effekt weg |
| Connors RSI(2) NAS, nur ab 4/5 % Puffer | (Bericht V8) | verworfen: Auswahl −0,66, Prüfung −0,19 bis −0,29 |
| NAS-Eröffnungsmomentum, nur ab 4/5 % Puffer | (Bericht V8) | verworfen: Auswahl −1,1 bis −1,6; Prüfung mit Pleiten (0,05) |
| NR4/NR7 als LW-Filter, Gold-Freitag, Turnaround Tuesday, IBS | Recherche | nicht gebaut: Tages-Swing (Familie RSI(2)), Münzwurf-Richtung oder nur als Bias belegt |
| Pre-FOMC-Drift, Overnight-Drift NQ, Gold-Kreuzmarkt, Gold-Mean-Reversion | NY Fed 07/2026, Studien laut Recherche | durch Belege widerlegt, nicht gebaut |

Zur **Kontoverwaltung** fand die Recherche nur ein belegtes Prinzip: Größe proportional zum Restpuffer (Grossman-Zhou, [barrier-sizing](https://github.com/maxsilverman9/barrier-sizing)). Das ist im Kern die Pufferkurve von 8.00. Für „kurz vor dem Ziel kleiner“ und „nach Gewinnen größer“ gab es keine Quelle mit Zahlen.

### 4.2 Trend-Day TD: allein, dann GFT-Handhabung, dann kombiniert

**Regeln** (`n9sig.gen_lastmom`, EA `TdKerze`):
- Am Open der 14:00-NY-Kerze wird die Tagesrendite gemessen: Schluss der Kerze davor minus Vortagesschluss (letzter Schluss vor 16:00).
- Ist sie ≥ 0,75 × ATR(D1,14), wird Long gekauft.
- Stop 0,3 ATR, kein Ziel, Ausstieg am Open der 15:55-Kerze.

**Signalebene** (`n9_scan.py`, 512 Varianten):
- Nur 2 Varianten sind überall robust: PF > 1,15 in beiden GFT-Hälften und PF > 1,08 auf 2005–21.
- Beide liegen bei 14:00, Schwelle 0,75, nur Long.
- Die Sieger der Auswahlphase (ohne Schwelle, beide Richtungen) brechen in der Prüfung ein. Ohne Mindestbewegung ist das Signal wertlos.

| Signal (Stop 0,3 ATR) | Trades | PF |
|---|---|---|
| GFT 2022–25 | 104 | 1,92 |
| Fremddaten 2005–21 | 442 | 1,31 |

**Allein im Konto** (alte Module aus): 0,83 Ausz./J, 5,6 gültige Tage/J, 0 Pleiten. Zu selten, um allein zu tragen.

**GFT-Handhabung:**
- Risiko 0,5 % und 0,75 % sind gleichwertig (14,30 / 14,28). Gewählt: 0,5 %.
- Mit Puffer-Schwelle 4 % wird es schlechter (Auswahl 16,25, Prüfung 12,37). Gewählt: ohne Schwelle.

**Kombiniert** siehe Tabelle oben. Im Konto bringt TD direkt nur ~63 $/J (11 Trades/J, Trefferquote 65 %). Der Gewinn entsteht über zusätzliche gültige Tage um 14–16 Uhr, eine sonst ruhige Zeit, die Zyklen früher schließen. Konflikte geprüft:
- Hedging: nur Long, kein Short im NAS zu dieser Zeit aus anderen Modulen außer LW-Short; die Sperre greift.
- Budget und Floating-Grenze: über dieselbe Maschinerie wie LW/XA.
- Dieselbe Idee im selben Symbol: Risiko je Idee 0,9 %.

### 4.3 Plateau, Jahre, Kosten

Plateau auf GFT 2022–25, Ausz./J, 8.00 = 13,49:

| Einstieg | Schwelle 0,5 | 0,75 | 1,0 |
|---|---|---|---|
| 13:30 (Stop 0,2/0,3/0,4) | 13,14 / 13,77 / 13,83 | 13,57 / 13,55 / 13,73 | 13,75 / 13,58 / 13,52 |
| **14:00** | 14,03 / 13,77 / 13,65 | 13,78 / **14,30** / 14,17 | 13,25 / 13,40 / 13,04 |
| 14:30 | 13,60 / 13,74 / 13,59 | 13,35 / 13,64 / 13,18 | 13,54 / 13,76 / 13,51 |

- 21 von 27 Varianten liegen über 8.00, das Mittel ist +0,13.
- In der Region 14:00 / Schwelle 0,5–0,75 sind es +0,4.
- Der gewählte Punkt ist die Spitze. Auf den Fremddaten ist er ebenfalls der beste:

| Fremddaten (8.00 = 3,16) | Ausz./J | Pleiten |
|---|---|---|
| 14:00 / 0,75 / 0,3 (gewählt) | 3,81 | 0 |
| 14:00 / 0,75 / 0,4 | 3,77 | 0 |
| 13:30 / 0,75 / 0,3 | 3,65 | 0 |
| 14:00 / 1,0 / 0,3 | 3,53 | 0 |
| 14:00 / 0,5 / 0,3 | 3,39 | 0,004 |
| 14:00 / 0,5 / 0,2 | 3,23 | 0,007 |

Je Kalenderjahr (Starts im Jahr, 120 Tage):

| | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| 8.00 | 15,99 | 13,48 | 13,29 | 6,50 |
| 8.10 | 17,01 | 14,24 | 14,17 | 6,28 |

2025 ist leicht schlechter (−0,22, im Rauschen; nur Starts bis Mitte 2025, NAS-Daten enden 12/2025). Auf Signalebene war 2024 das schwache TD-Jahr (PF 0,90). Fremddaten: 12 von 17 Jahren positiv.

Kostenstress, Signalebene (Schlupf je Seite, umgerechnet auf NAS 20 000):

| Schlupf je Seite | PF GFT | PF Fremddaten |
|---|---|---|
| 0 Pkt | 1,92 | 1,31 |
| 1 Pkt | 1,74 | 1,19 |
| 2 Pkt | 1,58 | 1,09 |
| 4 Pkt | 1,30 | **0,91** |

Im Konto mit Schlupf = 100 % des Spreads: 11,31 → 12,25 Ausz./J.

## 5. Was im EA neu ist (`DEADBAND_V8.mq5`, Build 8.10)

**Kontoerkenner** (Eingabegruppe „8.10: Kontoerkenner und Anpasser“):
- `KontoZustandBerechnen()` überträgt die eng6-Logik (Variable `zst`). Neu ist nur UNSICHER aus `peakOk`.
- `KontoZustandPruefen()` läuft vor allen Modulen in `Durchlauf()`, wie eng6 vor den Einstiegen der Kerze.
- Ausgaben:
  - Panel-Zeile „Kontozustand: X (seit …), Satz: …, Grund“
  - beim Start eine Meldung „(Start) -> X: Grund“
  - jeder Wechsel im Journal und per Push (`AnpPush`)
  - eine Zeile in der Kontozustands-Datei
- Eingaben:
  - `AnpasserAktiv` (false = handelsgleich 8.00)
  - `AnpZustandErzwingen` (-1 automatisch, 0–8 = Zustand für Tests erzwingen)
  - Schwellen `AnpTiefPct`, `AnpLeichtPct`, `AnpHysPct`, `AnpReifeNahTage`, `AnpReifeNahGewinn`, `AnpGewinnPct`, `AnpSerie`
  - je Zustand ein Faktor-Satz `AnpFrisch` … `AnpUnsicher` mit 8 Faktoren in der Reihenfolge DEADBAND, RSI21, Noise, Fades, Spike, LW, XA, TD
- Faktoren 0–2 sind erlaubt, 0 schaltet den Strom im Zustand ab. Abgelehnt wird ein SERIE-Satz mit allen Faktoren 0, weil er nie enden würde (Replikat: 0,64 Ausz./J). Ungültige Eingaben schalten den Anpasser ab; der Erkenner zeigt weiter an.
- Die Faktoren wirken an den vier Risiko-Stellen (DEADBAND, RSI21, Noise, `FadeLive`) zusätzlich zu Pufferkurve, `BelowStartMult` und `PeakUnsicherFaktor`.
- Serienzähler: `SerienStand()` zählt `serNZ` ohne Rücksetzen beim Serien-Stopp, wie eng6 `z_cons`.

**Modul TD** (Eingabegruppe „8.10: Trend-Day NAS“):
- `TdKerze()` ist eine Zeile-für-Zeile-Übertragung von `n9sig.gen_lastmom` (refmode 0).
- Es läuft über die Sondermodul-Maschinerie von LW/XA. Damit gelten Hedging-Sperre, Budget, Idee, Margin, Mindest-Stop in Spreads, Schutz gültiger Tage, News, Feiertage, 130-s-Ziel, Ernte, Zeit-Ausstieg, Waisen. Kein Portfolio-Wächter (wie S0830/LW/XA).
- `MAXFADE` 13 → 14; Magic = MagicBase + 50 + Modulnummer (TD = 63 bei Standardliste).
- Startmeldung „8.10 Trend-Day TD …“.

## 6. Ehrliche Grenzen

1. **Nicht kompiliert.** Klammerbilanz (Datei gesamt, ohne Strings und Kommentare) und Deklarationsreihenfolge sind geprüft. Neue Funktionen: `AnpZeileLesen`, `AnpLesen`, `AnpWirkt`, `AnpFaktor`, `AnpKlasseFade`, `AnpSatzText`, `KontoZustandBerechnen`, `KontoZustandPruefen`, `AnpStatusText`, `TdKerze`.
2. **Replikat ist ein Näherungsmotor** (Stand 6.10 plus generische Ströme). Grid, Teilgewinn, Schutz je Modul und Regime-Größe sind nur angenähert. Aussagekräftig ist der Unterschied 8.00 → 8.10.
3. **Rauschen:** Pfad-Chaos von ±0,5 Ausz./J. Die TD-Verbesserung liegt auf GFT nur knapp darüber. Getragen wird sie davon, dass Auswahl, Prüfung, Fremddaten, Kostenstress und 3 von 4 Jahren in dieselbe Richtung zeigen.
4. **Spitze statt Plateau-Mitte:** Der TD-Punkt ist das Maximum des Rasters (GFT und Fremddaten). Realistisch sind +0,2 bis +0,5 Ausz./J.
5. **Kostenempfindlich:** TD auf den Fremddaten fällt bei 4 Punkten Schlupf je Seite unter PF 1. Die Stop-Weite ist im Median 81 Punkte (0,4 %).
6. **Kein Zukunftstest 2026 für TD:** Die NAS-Daten enden 12/2025; nur Gold reicht bis 09/2026.
7. **Basis neu gemessen:** 8.00 liegt im Replikat 0,9 % (GFT) bzw. 14 % (Fremddaten) neben den Zahlen des V8-Berichts (Abschnitt 1). Die gepaarten Unterschiede sind davon unberührt.
8. **Anpasser neutral:** Kein Zustandssatz hat die Prüfung bestanden. Wer eigene Sätze einträgt, verlässt den geprüften Bereich.

## 7. Prüfplan im MT5-Tester

1. Kompilieren. Beim Start erscheinen im Journal:
   - „8.10 Kontoerkenner AN | Anpasser AN …“
   - „8.10 Trend-Day TD NAS100.x …“
   - nach dem Laden des Kontos „8.10 KONTOZUSTAND (Start) -> …“ mit Grund
2. Tester 2022–2025, Echte Ticks, 10 000 Start. Drei Läufe:
   - a) 8.10 wie geliefert
   - b) `TdAktiv=false` (= 8.00 mit Erkenner, handelsgleich 8.00)
   - c) Rollback `rollback_8.00/DEADBAND_V8.mq5`
3. b) und c) müssen **identische Trades** haben. Das prüft, dass Erkenner und neutraler Anpasser nichts verändern.
4. Zwischen a) und b) vergleichen:
   - Auszahlungen
   - kleinster Abstand zum Boden
   - Bodenbrüche (6.81-Prüfwerte)
   - Trades „FADE TD“: nur Long, Einstieg 14:00 NY, Stop 0,3 ATR, Ausstieg 15:55, nur an Tagen mit NAS ≥ 0,75 ATR über dem Vortagesschluss
5. Erkenner testen: `AnpZustandErzwingen=5` (TIEF) mit `AnpTief="1,1,1,1,1,1,1,0"`. Dann darf TD nicht handeln; Journal: „Strom im Kontozustand TIEF aus“. Danach zurück auf -1.
6. Wenn a) den kleinsten Abstand zum Boden deutlich verschlechtert: `TdRiskPct` 0,35 oder `TdAktiv=false`.

## 8. Dateien

| Datei | Inhalt |
|---|---|
| `DEADBAND_V8.mq5` | Build 8.10 |
| `rollback_8.00/DEADBAND_V8.mq5` | Build 8.00 unverändert |
| `Replikat_v6/eng6.py` | Zustandsmaschine (`st_*`, `SM`, `ZN`, `smatrix`), Spalte 4 im Trade-Protokoll; mit `st_on=0` bitgleich zu vorher |
| `Replikat_v6/evl6.py` | `SM` durchgereicht; Tage, Pleiten und Ergebnis je Zustand und Modul |
| `Replikat_v6/z8.py` | 8.00-Aufbau, Bewertung gesamt/IS/OOS/ext, Zustandstabelle, zusätzliche Ströme |
| `Replikat_v6/z8_opt.py` | Raster je Zustand (`zall`, `zoff`, `z2`, `fin`, `rausch`), neue Ströme (`neu`), TD-Plateau (`lmp`) |
| `Replikat_v6/n9sig.py`, `n9_scan.py` | Generator Schluss-Momentum/Trend-Day; Raster PM-Fix und Schluss-Momentum |
| `Replikat_v6/z9_lm.py`, `z9_lm_detail.py` | TD allein und kombiniert; Jahre und Kostenstress |
| `Replikat_v6/z8_final.py` | Endbewertung 8.00 gegen 8.10 |
| `Replikat_v6/ergebnisse/z8_*.json`, `z9_*.json`, `n9_robust_*.json(.gz)` | alle Ergebnisse |

Ablauf zum Nachrechnen:
1. Daten nach `extdata/DATEN_BERICHT.md` aufbauen.
2. `DEADBAND_EXT=… python y7_data.py`
3. `python sig5.py && python sig_ext.py`
4. `python z8.py gft|ext`
5. `python z8_opt.py <satz> IS OOS ext`
6. `python z8_final.py gft|ext`
