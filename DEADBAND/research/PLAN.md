# DEADBAND V8.10 – Forschungs- und Ausbauplan (Stufe 0, Schritt 1)

Stand 14.10.2026 · Branch `claude/upbeat-maxwell-f7pmp0` · Auftrag: „DEADBAND – Forschungs- und Ausbauauftrag“, Zusatz des Nutzers: **„alles mit DEADBAND V8+“**.

Dieser Plan legt fest, was getestet wird, bevor ein Lauf startet. Nach deinem OK baue ich die Engine (Stufe 0, Schritte 2–4). Bis dahin ist nichts gerechnet; alle Zahlen unten stammen aus vorhandenen Berichten und Ergebnis-JSONs im Repo und sind so gekennzeichnet.

---

## 0. Kurzfassung

- **EA-Datei:** `DEADBAND/DEADBAND_V8.mq5`, Build 8.10 (vom Branch `claude/nice-archimedes-5zut72`, Gedächtnis-Dateien von `claude/blissful-pasteur-23wlt0`; beide in diesen Branch übernommen, ohne Änderung). Vollständig gelesen (7452 Zeilen).
- **Wichtigster Befund:** V8.10 handelt den H1-Ausbruch **nicht mehr** (`DbAktiv=false` seit 6.00). Der Auftrag beschreibt aber ein System, in dem der H1-Ausbruch die Basis ist. Abschnitt 1 listet alle Abweichungen; Abschnitt 2 die Entscheidungen, die ich dafür von dir brauche.
- **Daten fehlen in dieser Umgebung vollständig** (keine MT5-Exporte, kein Referenzbericht; `data/` ist per `.gitignore` ausgeschlossen). Ohne sie kann das Kalibrierungs-Gate nicht laufen. Die Exportliste steht in Abschnitt 10.
- **Geplante Varianten insgesamt:** etwa 45–50 (Abschnitt 11). Keine Familie kommt über 50 Varianten, die 95-%-Schwelle des Zufallsvergleichs bleibt.
- **Rechenzeit:** je Stufe unter 2 h auf 4 Kernen (Schätzung). Die MT5-Läufe in Stufe 3 machst du.

---

## 1. Auftrag gegen V8.10: Abweichungen

| Punkt | Auftrag (Abschnitt 2) | V8.10 (Code, Zeile) | Folge für den Plan |
|---|---|---|---|
| H1-Ausbruch | Basis des Systems | `DbAktiv=false` (Z. 469): keine neuen Einstiege, offene werden verwaltet | Baseline muss neu festgelegt werden → **E1** |
| Weitere Module | – | 10 Fehlausbruch-Fades mit Portfolio-Wächter, RSI21, NAS-Noise, Spike S0830, LW, XA, TD | gehören zur Baseline, wenn V8.10 handelsidentisch bleibt |
| Positionen je Symbol | höchstens EINE | mehrere Module halten gleichzeitig Positionen im selben Symbol (gleiche Richtung; Gegenrichtung sperrt die Hedging-Sperre) | Regel für neue Familien → **E9** |
| Session | 3–12 NY | `SessStartNY=3`, `SessEndNY=13` (Z. 260–261) | ich nehme den Code |
| Trades je Tag | max. 2 | `MaxTradesDay=1`, `MaxLossDay=2` (Z. 308–309) | ich nehme den Code |
| Filter | EMA50 D1, VWAP, RSI50, Qualität, Volumen | zusätzlich MACD-Histogramm (`UseMacd=true`, Z. 273) | ich nehme den Code |
| Ausstieg | Tranchen, Endziel, Zeit-Exit 192 | Tp1 1,5 R (50 %, erst nach 130 s), Stop auf +0,05 R ab Tp1-Niveau, Endziel 8/10 R, Zeit-Exit 192 M15-Kerzen oder 144 h, **Freitag 16:45 NY schließen + Wiederaufnahme Sonntag** (`WeAktiv`), Tagesernte ab 16:00 NY, Abschluss-Ernte, Gewinn-Ernte | 1:1 so in die Engine; „Freitag-flat“ ist im Auftrag widerlegt, ist im EA aber Bestand – ich ändere es nicht |
| Floating-Grenze GFT | 1,5 % | 1,0 % bei Konto ab 02.09.2026 (`KontoAb20260902=true`, Z. 318) | **E5** |
| Zyklus | 10 Tage | 10 Tage, bei Kauf ab 21.09.2026 14 Tage (`RegelAusKaufdatum`, Z. 320) | **E5** |
| Mindestauszahlung, Deckel, 120-s-Regel | nicht genannt | 105 $ (= 131,25 $ Gewinn), Deckel 6 % für die ersten 2 Auszahlungen, Gewinne < 120 s gestrichen | nehme ich in den Bootstrap auf |
| Frontier-Zahlen (Befund 7) | Sharpe 1,50–1,64, Ziel ~12 Ausz./J | Replikat V8.10: 14,30 Ausz./J, 0 Pleiten (eng6, rollierende Starts) [aus `DEADBAND_V8x_Bericht.md`, in dieser Sitzung **ungeprüft**]; reiner H1-Ausbruch (Build 3.00) im selben Replikat: 6,02 Ausz./J, 2,19 Pleiten/J [aus `Replikat_v6/ergebnisse/z8_v300_gft.json`, ungeprüft] | Befunde 1–7 gelten offenbar für den reinen H1-Ausbruch. Für V8.10 messe ich die Baseline neu nach Abschnitt 5 des Auftrags |
| Server | Windows Server 2022, 24/7 | Kopf 6.10 / `VpsSperre`: „GFT Instant Premium (Kauf ab 12.08.2026) verbietet VPS/Server – nur auf dem eigenen PC“ | **Risiko R1** (Abschnitt 12). Ich ändere nichts daran, weise nur darauf hin |
| Widerlegt-Liste | Abschnitt 2 | V8-/V8x-Berichte führen weitere widerlegte Ideen | ich verwende die **Vereinigung** beider Listen (Abschnitt 3.6) |

---

## 2. Entscheidungen, die ich von dir brauche

Zu jeder Frage steht meine Empfehlung. „OK, alle Empfehlungen“ reicht als Antwort.

| Nr. | Frage | Optionen | Empfehlung |
|---|---|---|---|
| **E1** | Was ist die Baseline? | **A** V8.10 handelsidentisch (Voreinstellungen, H1 aus) · **B** V8.10 + H1-Ausbruch an (`DbAktiv=true`, Rest wie geliefert) · **C** nur das H1-Modul aus V8.10, alle anderen Module aus | **A.** Nur A misst, ob ein Kandidat das Konto verbessert, das du tatsächlich handelst. B ändert den Live-Handel schon in der Baseline. C erreicht im Replikat schon selbst nicht bpp ≤ 0,10 (Build 3.00: 2,19 Pleiten bei 6,02 Auszahlungen je Jahr, siehe oben) |
| **E2** | Stufe 3 (Einstieg innerhalb der Kerze) bei Baseline A | **i** H1-Modul isoliert im Tester (`DbAktiv=true`, alle anderen Module aus), Varianten A–D genau wie im Auftrag · **ii** auf LW übertragen (einziges V8-Modul mit Ausbruch + Schlussbestätigung) · **iii** entfällt | **i.** Beantwortet genau die Frage des Auftrags. Ein Erfolg würde zusätzlich klären, ob der H1-Ausbruch wieder eingeschaltet werden sollte (dann Stufe 4 mit E1-B) |
| **E3** | Familie 3 auf Gold? | streichen · testen | **streichen.** V8-Raster `n8_scan.py fam_orb` enthält genau diesen Ausbruch für Gold (Asien-Spanne ab 19:00 NY bis 1/2/3 Uhr NY): 1536 Varianten, 0 robust, PF-Median 0,73 (2022–23) und 0,86 (2005–21) [aus `n8_robust_orb.json.gz`]. Mit DEADBAND-Ausstieg wäre es dasselbe Signal unter anderem Namen. **NAS** wurde dort nicht getestet → bleibt drin |
| **E4** | Familie 5 (Vorlaufsignal Dollar/Renditen) | streichen · nur mit Daten testen | **streichen**, es sei denn, GFT bietet DXY/USDX als Symbol an. V8x hat „Gold-Kreuzmarkt“ als durch Literatur widerlegt geführt (Abschnitt 4.1) und nicht gebaut |
| **E5** | GFT-Regeln im Bootstrap | EA-Lesart (Floating 1,0 %, 10 Tage) · Auftrag (1,5 %) | **EA-Lesart** – sie ist die strengere und die, die dein Konto hat. Kauf ab 21.09.2026 → 14 Tage: bitte bestätigen, dass dein Konto vor dem 21.09. gekauft ist |
| **E6** | `[STICHTAG]` für den Blindlauf | 2025-06-30 · 2025-12-31 | **2025-06-30.** Blindfenster 01.07.2025 bis Datenende (≈ 15 Monate, ≈ 55 Hochwirkungs-Termine). Die V8-Module wurden mit Daten bis 12/2025 gewählt; das belastet die Baseline in beiden Armen gleich, der Vergleich Kandidat gegen Baseline bleibt fair |
| **E7** | Platzhalter | `[MAX_DATENALTER]`, `[MAX_TICKALTER]`, `[MAX_STUNDEN]` | **180 s**, **120 s** (nur in der Handelszeit), **6 h** |
| **E8** | Paket-Installationen | hier: `numba==0.67.0` (+ `llvmlite==0.49.0`), `pytest==9.1.1` · Server: Python ≥ 3.10 x64, venv, `MetaTrader5==5.0.6180`, `numpy` (feste Version passend zur Python-Version) | bitte freigeben. Versionen sind mindestens 4 Wochen alt und mit dem installierten numpy 2.5.3 verträglich |
| **E9** | Neue Familie bei offener V8-Position im selben Symbol | **streng:** nur, wenn das Symbol über alle Module flach ist · V8-Konvention (Hedging-Sperre, Budget, Risiko je Idee) | **streng** – entspricht Stufe 4 des Auftrags („Slot nur, wenn frei“, keine Parallelpositionen) |
| **E10** | Alarmkanal des Sidecars | **a** nur MT5-Push über den EA (fällt aus, wenn das Terminal steht) · **b** a + ntfy.sh · **c** a + Telegram · **d** a + E-Mail | **b.** Ein Terminal-Ausfall braucht einen Kanal am Terminal vorbei; ntfy braucht kein Konto, das Thema wird nur lokal auf dem Server gespeichert |
| **E11** | Datenübertragung zu mir | Google-Drive-Ordner · eigener Git-Branch mit ZIP | **Google Drive** (Upload im Browser des Servers; ich lese über den Drive-Connector). CSV-Dateien kommen nie ins Repo |

Zusätzlich brauche ich zwei Angaben (keine Entscheidung): den **Pfad zu `terminal64.exe` des GFT-Terminals** und den **GFT-Datenordner** (`[MT5_DATENORDNER]`). Beides steht im MT5-Journal beim Start bzw. unter Datei → Dateiordner öffnen.

---

## 3. Bewertungsrahmen (für jeden Kandidaten gleich)

### 3.1 Baseline
Gemäß E1. Gerechnet auf identischer Engine, identischen Daten und identischen Bootstrap-Pfaden wie jeder Kandidat (gepaart: gleiche Zufallsblöcke).

### 3.2 Engine-Konventionen (gesicherte Befunde)
- Einstieg **immer** am Open der Folgekerze. MT5-Kerzen sind Bid-Kurse: Long zu Bid-Open + Spread, Short zu Bid-Open. Das ist „Mid + halber Spread“ in Gegenrichtung. Ausstieg Long zum Bid, Short zum Ask.
- In derselben Kerze zählt der Stop vor dem Ziel.
- Haltedauer, Endziel und Zeit-Exit werden nie gekürzt.
- Kosten: echte Spreads aus der Spalte `<SPREAD>`, Kommission Gold 5 $/Lot nur auf den Eingangs-Deal, Swap je Modus (Abschnitt 4.1), Lot-Raster 0,01, Mindestlot-Filter `MinLotRiskTol`.

### 3.3 Bootstrap (Auftrag Abschnitt 5)
- **Tagesdatensätze** aus dem pfadtreuen Lauf (mit allen V8-Regeln: Pufferkurve, Schutz gültiger Tage, Ernten, Reife), je Prop-Tag (17:00–17:00 NY) auf **Größenfaktor 1** zurückgerechnet:
  - realisiert (Tagesergebnis für gültige Tage),
  - Equity-Änderung inkl. offener Positionen,
  - tiefste und höchste Equity im Tag (Kerzenebene),
  - größter Floating-Verlust der Verlustpositionen (strenge Lesart inkl. Swap und Einstiegskommission).
- **Pfade:** 1000 je Blockgröße 1, 5 und 20 Handelstage (Kreisblock-Bootstrap), je Pfad 252 Handelstage. Seed fest (3.7).
- **Konto im Pfad:** Start 10 000 $. Je Tag Größenfaktor = Pufferkurve 3,5/1,25/0,1 × `BelowStartMult` 0,95 wie im EA.
  - Pleite (Konto verbrannt), wenn:
    - Tagesverlust ≥ 3 % gegen den Tagesstart (Equity, Tageswechsel 17:00 NY),
    - Equity ≤ Equity-Hoch inkl. offener Gewinne − 6 % (nachlaufend),
    - Floating-Verlust ≥ 1,0 % (E5).
  - Reihenfolge im Tag ungünstig angenommen: erst das Hoch (Boden steigt), dann das Tief.
- **Auszahlung:**
  - Voraussetzungen: 5 gültige Tage (≥ 0,5 % + 0,50 $ Reserve wie im EA), ≥ 10 Zyklustage und Gewinn ≥ 131,25 $.
  - Betrag: 80 %, Deckel 6 % für die ersten 2 Auszahlungen.
  - Danach Reset aufs Startkapital, neuer Boden.
  - Nach einer Pleite startet im selben Pfad ein neues Konto.
- **Kennzahlen:** Auszahlungen/Jahr, **bpp** (verbrannte Konten je Auszahlung), Ø Auszahlung – je Blockgröße getrennt.
- **Grenze:** Ein Tages-Bootstrap kann Zustandsregeln (Schutz gültiger Tage, Reife) nur in der Form abbilden, in der sie auf dem Originalpfad gewirkt haben. Als Gegenprobe rechne ich zusätzlich die **rollierenden Konten des Replikats** (eng6, wie in den V8-Berichten). Widersprechen sich beide, steht das im Bericht.

### 3.4 BESTANDEN nur, wenn alle sechs gelten
Wie Auftrag Abschnitt 5:
1. bpp ≤ 0,10.
2. Mehr Auszahlungen/Jahr als die Baseline, in allen drei Blockgrößen.
3. Jedes Kalenderjahr positiv.
4. Plateau: ±20 % auf jedem freien Parameter kippt das Netto-R-Vorzeichen nicht, und die Auszahlungen fallen höchstens 15 %.
5. Blindlauf nicht schlechter als die Baseline im selben Fenster.
6. Realistische Kosten.

Geprüft wird in dieser Reihenfolge; das erste verfehlte Kriterium steht im Urteil.

### 3.5 Walk-Forward
Auswahl und Plateau nur mit Daten bis `[STICHTAG]` (E6). Das Blindfenster öffne ich einmal, in Stufe 4, für die Endkandidaten und die Baseline. Danach ändere ich nichts mehr.

Auch die MT5-Läufe aus Stufe 3 (bis Datenende) werte ich getrennt aus: zuerst nur die Trades bis zum Stichtag, den Rest erst im Blindlauf.

### 3.6 Widerlegt (nicht testen, auch nicht umbenannt)
**Aus dem Auftrag:**
- SMC/Marktstruktur, FVG, SuperTrend-Regime, MACD-MTF, WaveTrend, Williams Vix Fix, Squeeze, S/R + Volumen-Oszillator
- Mean-Reversion Gold M15, Trailing-Stop, Break-even, ATR-Stop-Varianten
- PDH/PDL-Regeln und -Sweep, Uhrzeit-Buckets, Session verbreitern, Fakeout-Reversal, ADR-Erschöpfung
- Parallelpositionen im selben Symbol, Serienbremse, Tages-Gewinnsperre, Risiko-Halbierung nach Verlusten
- Freitag-flat, Gold nur long, Fib-Limit, Scalping M1/M5, ORB 9:30 M15
- weitere Range-Definitionen (M30/H2/H4/rollierend), US30/EURUSD/USDJPY

**Zusätzlich aus V8/V8x** (Berichte im Repo):
- ORB 5/15 min (auch mit Mittelpunkt), 9:30-Kerze, Silver Bullet, Judas Swing, Turtle Soup
- Gold-Initial-Balance mit Rücklauf, Magic Hours, Gao-Momentum, EMA-/VWAP-Pullback, Vortages-Ausbruch und -Sweep
- Bollinger, Turn of Month, Gap-Fade, VWAP-Fade, Wochen-Eröffnung, Makro-Tag-Filter, Vola-Perzentil
- Spike-Fade zu anderen Zeiten, Gold-PM-Fix, Connors RSI(2), NAS-Eröffnungsmomentum
- Pre-FOMC-Drift, Overnight-Drift NQ, Gold-Kreuzmarkt, Gold-Mean-Reversion
- **Gold-Asien-Range-Ausbruch** (siehe E3)

### 3.7 Seeds und Herkunft der Zahlen
- **Seeds:**
  - Bootstrap: 20261014 + Blockgröße.
  - Zufallsvergleich: 7000 + Familiennummer × 100 + Symbolindex.
  - Störungen des Replikats: 0–7 wie V8.
- **Herkunft:** Jede Zahl im Bericht trägt Skriptname, Datenbereich und Seed. Nicht Prüfbares ist als [ungeprüft] markiert.
- **Mehrfachtest-Kontrolle:** Alle Varianten werden gezählt und berichtet (Datei `research/varianten.csv`). Über 50 Varianten in einer Familie → Zufallsvergleich ≥ 99 % statt 95 %.

---

## 4. Stufe 0 – Engine, Tests, Kalibrierung (nach deinem OK)

### 4.1 Aufbau `research/engine/`
| Modul | Inhalt |
|---|---|
| `spec.py` | Symbolspezifikationen laut Auftrag (Abschnitt 4.2); unbekannte Symbole nur aus deiner Spezifikation, nie geschätzt |
| `daten.py` | MT5-CSV laden (Tab, `<SPREAD>`), Serverzeit = NY + 7, Prop-Tag ab 17:00 NY, M15/H1/D1 aus M5 wie MT5 |
| `ausstieg.py` | DEADBAND-Ausstieg 1:1 aus `HandleSymbol` (Z. 3872–3945) und `WochenendePruefen` (Z. 4206–4338): Tp1 1,5 R 50 % (nach 130 s), Stop +0,05 R ab Tp1-Niveau, Endziel 8/10 R, Zeit-Exit 192 M15 oder 144 h, Freitag 16:45 NY schließen und Sonntag ab 18:00 NY wieder aufnehmen (Stop höchstens 2 R vom neuen Einstieg) |
| `familien.py` | Signalgeneratoren der Familien (Abschnitt 6), nur abgeschlossene Kerzen |
| `konto.py` | Baseline und Kombinationen über den vorhandenen, gegen 8.00/8.10 abgeglichenen Kontomotor `Replikat_v6/eng6.py` (alle GFT-Regeln, alle V8-Module, generische Ströme). Ich schreibe ihn **nicht** neu: ein zweiter Motor wäre eine neue Fehlerquelle |
| `tage.py` | Tagesdatensätze für den Bootstrap (Abschnitt 3.3) |
| `bootstrap.py` | GFT-Bootstrap 1/5/20 |
| `zufall.py` | Zufallsvergleich (Abschnitt 6.6) |
| `kalibrierung.py` | MT5-Bericht (HTML/XML) einlesen, Deals ↔ Engine-Trades abgleichen |

### 4.2 Symbolspezifikationen
| Symbol | Kontrakt | Lot min/step | Kommission | Swap | 3-fach | Median-Spread |
|---|---|---|---|---|---|---|
| XAUUSD.x | 100 | 0,01 | 5 $/Lot nur Eingang | Punkte: −64,47 long / +23,84 short | Mittwoch | 0,32 |
| NAS100.x | 10 | 0,01 | keine | % vom Eröffnungspreis p. a.: −3 long / −1,5 short | **fehlt – bitte aus der Spezifikation** | 1,63 |
| BTCUSD.x | 1 | 0,01 (bitte bestätigen) | keine | −15 % p. a. long und short, jeden Kalendertag einfach | keiner | 65,14 |
| XAGUSD.x, USOIL (Name?) | **fehlt** | **fehlt** | **fehlt** | **fehlt** | **fehlt** | aus den Daten |

### 4.3 Tests (`research/engine/tests/`, pytest)
1. Lot-Rundung wie `NormLot` (auf 0,01 zum nächsten Schritt, dann min/max) und Budget-Kürzung abwärts; Mindestlot-Filter `MinLotRiskTol`.
2. Kommission nur auf den Eingangs-Deal, auch bei Teilschließung (Tp1).
3. Swap: Gold-Punkte-Modus mit Mittwoch ×3, NAS-Zinsmodus vom Eröffnungspreis, BTC täglich; Rollover um 00:00 Serverzeit.
4. Einstieg am Open der Folgekerze, Long zum Ask; nie am Close der Signalkerze (Test mit konstruierten Kerzen).
5. Tageswechsel 17:00 NY = 00:00 Serverzeit, auch in den Wochen mit abweichender EU-/US-Umstellung.
6. Zusätzlich: Ausstiegsreihenfolge Stop vor Ziel; Wochenend-Schließung und Wiederaufnahme; Zeit-Exit nach 192 M15-Kerzen.

### 4.4 Kalibrierungs-Gate
- **Referenz:** MT5-Bericht von V8.10 mit genau den Einstellungen der Baseline (E1), „Jeder Tick basierend auf realen Ticks“, 2022-08-23 bis `[STICHTAG]`, 10 000 $, `TesterAuszahlung=true`.
- **Pflicht:** Tradezahl ±5 %, Netto ±10 %.
- **Diagnose:** zusätzlich je Modul (Magic) Trades und Netto, damit eine Abweichung einem Modul zugeordnet werden kann.
- **Nicht bestanden:** STOPP mit Abweichung und wahrscheinlicher Ursache.
- **Ehrliche Erwartung:** eng6 bildet Grid, Teilgewinn, Schutz je Modul und Regime-Größe nur näherungsweise ab (V8x-Bericht, Grenzen 2), und Auszahlungs-Resets machen jede kleine Abweichung zu einem anderen Pfad. Dass das Gate für V8.10 auf Anhieb hält, ist **nicht** sicher. Fällt es, brauche ich zur Eingrenzung je einen Testerlauf je Modul (Abschnitt 10).

---

## 5. Stufe 1 – Drittes Instrument

- **Logik:** Der H1-Ausbruch ist das einzige symbolneutrale Modul in V8. Ich rechne ihn **unverändert** auf XAGUSD, USOIL und BTCUSD.
- **Parameter vorab fest, nicht abgestimmt:**
  - XAG und Öl erhalten den Gold-Satz (0,259 %, Qualität 0,70, Endziel 8 R, keine Shorts).
  - BTC erhält den NAS-Satz (0,288 %, 0,65, 10 R, Shorts erlaubt).
- **Je Instrument:**
  - Trades, PF je Kalenderjahr,
  - Tageskorrelation der P&L zu Gold, zu NAS und zum Baseline-Portfolio,
  - Überlappung der Haltezeiten in %.
- **Sinnvoll** nur, wenn die Tageskorrelation zum Portfolio < 0,2 ist **und** kein Verlustjahr mit einem Verlustjahr von Gold oder NAS (Baseline je Symbol) zusammenfällt.
- **Erfüllt ein Instrument das:** dieselbe Bewertung wie jeder Kandidat (Abschnitt 3.4), als zusätzlicher Strom in der Baseline.
- **Fehlen Daten:** STOPP mit der Liste aus Abschnitt 10.
- **Varianten:** 3.

---

## 6. Stufe 2 – Familien (Steckbriefe)

**Für alle Familien gleich:**
- Ausführung als Market-Order am Open der Folgekerze.
- Stop 3 × ATR(14, M15) und Ausstieg **identisch** zum DEADBAND-Modul (4.1).
- Risiko je Trade wie `RiskPctList` des Symbols.
- Startwerte vorab fest.
- Plateau: jeder freie Parameter ±20 %.

### 6.1 Familie 1 – Ereignis-Drift nach CPI, NFP, FOMC, PCE (Priorität 1)
- **Mechanismus:** Große Adressen ohne Sekundenhandel bauen ihre Positionen nach einer Datenüberraschung über Stunden in deren Richtung um, nachdem der erste Schub die Richtung gezeigt hat. Auf der anderen Seite stehen Liquiditätsgeber und kurzfristige Händler, die den ersten Ausschlag zurückhandeln.
- **Signal:**
  - Termin E ∈ {CPI, NFP, PCE (je 8:30 NY), FOMC-Statement (14:00 NY)} aus dem MQL5-Kalender (Bedeutung hoch, Land US).
  - Erste abgeschlossene M15-Kerze, die zur Veröffentlichung beginnt (8:30–8:45 bzw. 14:00–14:15).
  - Richtung = Vorzeichen von Schluss − Eröffnung dieser Kerze, nur wenn |Schluss − Eröffnung| ≥ **k × ATR(14, M15)**.
  - Einstieg am Open der Folgekerze (8:45 bzw. 14:15), also ≥ 15 min nach der Veröffentlichung.
  - Gold und NAS je eigene Kerze.
- **Freie Parameter:** 1 – k, Start **0,5**.
- **Abgrenzung:**
  - Kein Richtungsfilter: erzeugt Einstiege zu festen Terminen, unabhängig vom Tagestrend.
  - Nicht auf der Widerlegt-Liste: Pre-FOMC-Drift liegt *vor* dem Termin; Spike-Fade (S0830) und „Spike-Fade zu anderen Zeiten“ handeln *gegen* den Ausschlag – hier geht es mit ihm; der Makro-Tag-Filter war ein Filter, kein Einstieg.
  - **Konflikt:** An CPI/NFP-Tagen kann S0830 um 9:00 NAS kaufen, während Familie 1 um 8:45 NAS verkauft. Die Hedging-Sperre lässt dann nur den ersten zu; ich weise die Fälle aus.
- **Häufigkeit:** etwa 44 Termine/Jahr; nach k-Filter geschätzt 2–3 Signale/Monat je Symbol.
- **Überlappung:**
  - Mit H1-Signalen hoch (die 8:30-Kerze schließt oft außerhalb der H1-Spanne), geschätzt 30–50 %.
  - Mit V8-Positionen niedrig (NAS-Noise beginnt erst 10:00).
- **Daten:** Kalenderhistorie zwingend. Fehlt sie, STOPP (Abschnitt 9.1, Export-Skript).

### 6.2 Familie 2 – Bestätigter Retest (Priorität 2)
- **Mechanismus:** Nach einem Ausbruch über eine viel beachtete Stundenkante sind die Stops der Gegenseite ausgelöst, und Händler, die den Ausbruch verpasst haben, warten an der Kante. Wird die Kante beim Rücklauf angenommen und schließt eine Kerze wieder in Ausbruchsrichtung, verteidigt die alte Gegenseite nicht mehr. Auf der anderen Seite stehen Händler, die den Ausbruch als Fehlausbruch zurückhandeln.
- **Signal:**
  - Ein vollständiges DEADBAND-Signal auf Kerze t (alle Filter des H1-Moduls), das nicht gehandelt wurde. Bei Baseline A ist das jedes H1-Signal; bei B/C gelten Slot belegt, Tageslimit, Budget, Mindestlot und News.
  - Innerhalb von **W** M15-Kerzen nach t berührt der Preis die H1-Kante (Long: Tief ≤ H1-Hoch + **τ × ATR**).
  - Danach schließt eine M15-Kerze jenseits der Kante mit Kerzenqualität ≥ `ClsMin`.
  - Ungültig, sobald eine Kerze jenseits der Gegenkante schließt.
  - Kein Limit-Einstieg.
- **Freie Parameter:** 2 – W (Start **8** = 2 h), τ (Start **0,1**).
- **Abgrenzung:**
  - Kein Richtungsfilter: neuer Einstiegszeitpunkt mit eigener Bestätigung.
  - Nicht Fib-Limit (Market nach Schluss, keine Limit-Füllung).
  - Nicht Fakeout-Reversal (gleiche Richtung wie der Ausbruch).
  - Nicht EMA-/VWAP-Pullback (Bezug ist die H1-Kante, kein gleitender Mittelwert).
- **Häufigkeit:** geschätzt 4–8/Monat je Symbol.
- **Überlappung:**
  - Mit dem auslösenden H1-Signal per Konstruktion 100 % zeitnah. Bei Baseline A gibt es diese Trades nicht, deshalb messe ich die Überlappung mit den V8-Positionen.
  - Mit V8-Positionen geschätzt 20–40 %.

### 6.3 Familie 3 – Asien-Spanne zur London-Eröffnung (Priorität 3, nur NAS – E3)
- **Mechanismus:** In der Asien-Sitzung handeln wenige, meist lokale Teilnehmer; die Spanne spiegelt Lagerhaltung statt Information. Mit London kommen die großen Aufträge aus der Nacht, deren Ausführung den Preis aus der Spanne trägt. Auf der anderen Seite stehen Market-Maker und Spannen-Händler, die die Nachtspanne verteidigen.
- **Signal:**
  - Spanne = Hoch/Tief der M15-Kerzen 18:00–03:00 NY (Wiedereröffnung bis London 08:00).
  - Erste M15-Kerze zwischen 03:00 und 05:00 NY, die außerhalb schließt, mit Qualität ≥ `ClsMin`.
  - Einstieg am Open der Folgekerze.
  - Nur Tage mit Spannenbreite ≤ **m × ATR(14, D1)**.
- **Freie Parameter:** 1 – m, Start **0,6** (wie `mx` der Fades).
- **Abgrenzung:**
  - Kein Richtungsfilter.
  - Nicht ORB 9:30 und keine „weitere Range-Definition“ des H1-Ausbruchs (Sitzungsspanne mit eigenem Zeitfenster).
  - Gold ist gestrichen (E3).
  - Gegenläufig zu den Fades X0300S/X0400 (Gold) – NAS hat zu dieser Zeit keinen Fade.
- **Häufigkeit:** geschätzt 8–12/Monat.
- **Überlappung:** mit H1-Signalen hoch (DEADBAND-Session beginnt 3:00), geschätzt 40–60 % – Gefahr „kein Mehrwert“.

### 6.4 Familie 4 – Mehrtägiger Trend auf D1 (Priorität 4)
- **Mechanismus:** Trendfolgende Fonds und regelbasierte Umschichtungen kaufen bzw. verkaufen über Tage, sobald ein Markt auf einem Mehrwochen-Extrem schließt; Leerverkäufer müssen dann ihre Stops nachziehen. Auf der anderen Seite stehen Mean-Reversion-Händler und Verkäufer von Volatilität.
- **Signal:**
  - Schluss des Prop-Tages (17:00 NY) über dem Hoch der vorherigen **N** Prop-Tage → Long (unter dem Tief → Short).
  - Nur der erste Schluss jenseits nach einem Schluss innerhalb.
  - Einstieg am Open der ersten M15-Kerze des nächsten Session-Starts (03:00 NY).
- **Freie Parameter:** 1 – N, Start **20**.
- **Abgrenzung:**
  - Vortages-Ausbruch (N = 1, intraday) ist widerlegt; N = 20 auf Tagesschluss ist ein anderes, seltenes Ereignis.
  - Keine weitere Range-Definition des H1-Ausbruchs.
  - Kein Richtungsfilter: Einstiege an Tagen ohne H1-Signal.
- **Häufigkeit:** geschätzt 1–2/Monat je Symbol.
- **Slot-Konkurrenz:** mit den Läufern (Wochenend-Wiederaufnahmen, RSI21 bis 8 Tage, Haltedauer bis 144 h) ausgewiesen: Anteil ausgelassener Signale wegen belegtem Symbol.

### 6.5 Familie 5 – Marktübergreifendes Vorlaufsignal (Priorität 5)
Empfehlung: streichen (E4). Nur wenn GFT DXY/USDX oder eine Rendite als Symbol führt und du es willst, spezifiziere ich sie vor dem Code nach demselben Schema (1 freier Parameter). Sonst melde ich im Bericht, was fehlt.

### 6.6 Prüfung je Familie
- **(a) Allein:**
  - Trades, PF je Jahr,
  - Ø Gewinner/Verlierer in R,
  - Haltedauerverteilung (Anteil > 60 h, Befund 2).
- **(b) Zufallsvergleich:**
  - 1000 Läufe (≥ 500 verlangt) mit zufälligen Einstiegs-Kerzen.
  - Gleich bleiben: Anzahl, Richtungsverteilung, Symbol, Session-Fenster der Familie und Ausstiegslogik.
  - Netto-R der Familie muss ≥ 95 % der Läufe schlagen, sonst widerlegt.
  - Für Familie 1 zusätzlich als Information: gleiche Termine, zufällige Richtung.
- **(c) Überlappung:** mit H1-Signalen und V8-Positionen gleicher Richtung (Symbol, Zeitraum). Über 50 % heißt kein Mehrwert.
- **(d) Tageskorrelation** der P&L zur Baseline.
- **Danach:** nur, wenn (b) und (c) halten, der Konto-Bootstrap (Abschnitt 3).

---

## 7. Stufe 3 – Einstiegszeitpunkt innerhalb der Kerze (MT5-Tester)

- **Ziel:** gemäß E2 (Empfehlung i: H1-Modul isoliert).
- **Datei:** `research/patch_intrabar.mq5` = vollständige Kopie von V8.10 mit Schalter `EntryMode` (0 = handelsidentisch).
- **Prüfung:** in `OnTick` **und** im 1-Sekunden-`OnTimer` (der EA ruft beides schon über `Durchlauf()` auf), damit NAS-Durchstöße auf einem Gold-Chart nicht verloren gehen.
- **Varianten genau wie im Auftrag:**
  - A Schluss,
  - B Durchstoß um X × aktuellen Spread, X ∈ {1, 2, 3},
  - C wie B plus T Sekunden jenseits, T ∈ {30, 120, 300},
  - D nach 7,5 min der laufenden M15-Kerze im obersten/untersten Anteil `ClsMin` der bisherigen Spanne.
  - Stop, Größe, Ausstieg, Session und Tageslimits identisch zu A. Kein Zufall, keine künstlichen Verzögerungen.
- **Diff:** `research/patch_intrabar.diff` zum Gegenlesen.
- **Testplan:** `research/MT5_TESTPLAN_INTRABAR.md` – Modell „Jeder Tick basierend auf realen Ticks“, 2022-08-23 bis Datenende, 10 000 $, 1:10, eine Zeile je Variante.
- **STOPP:** Du lieferst die Berichte.
- **Auswertung:**
  - je Variante Trades, Netto, PF je Jahr,
  - Ø Einstiegspreis gegen A in R,
  - Fehlausbruch-Anteil (Stop ohne vorher +1 R),
  - Bootstrap.
  - B und C zusätzlich mit +1 Spread Schlupf je Einstieg.
- **Varianten:** 8 Testerläufe, 14 Auswertungen.
- **Nicht kompiliert:** In dieser Umgebung gibt es keinen MetaEditor. Ich prüfe Klammern, Deklarationen und jeden Format-Aufruf gegen seine Argumente (`%%`, `%.*f`), nur ASCII in String-Literalen, Dateien ohne BOM.

---

## 8. Stufe 4 – Einbau (nur bestandene Kandidaten)

- **Positionen:** Je Symbol eine Position im Sinne von E9.
  - Die Basis hat Vorrang.
  - Kein Ersetzen offener Positionen.
- **Risiko:** gleiches Risiko je Trade über `RiskPctList`, kein Aufschlag.
- **Magic:** eigene Magic je Familie, `MagicBase` + 70 + Familiennummer.
  - Die Bereiche +0…7, +10…25, +30…37 und +50…63 sind belegt; +70… ist frei.
  - Die Magic-Prüfungen (`IsOurMagic` usw.) muss der Patch erweitern.
- **Regime-Umschaltung:** nur mit vorab festgelegter Regel (höchstens 1 Parameter), bestätigt auf einem anderen Instrument als dem Auswahlinstrument. Ein Filter, der 2022–23 reparieren soll, zählt nicht.
- **Patch:** `research/patch_vorschlag.mq5` nur für bestandene Kandidaten.
  - Je Familie eine eigene Funktion mit Schalter (Voreinstellung AUS = handelsidentisch) und Kommentar je Block.
  - Wird nicht eingespielt.
- **Blindlauf:** einmal, danach keine Änderung.

---

## 9. Stufe 5 – Sidecar (läuft unabhängig von den Kandidaten)

### 9.1 Wirtschaftskalender
- **Live:** reichen die MQL5-Funktionen aus. V8.10 nutzt `CalendarValueHistory` schon für die News-Sperre (Z. 1365–1388).
- **Strategietester:** liefert keinen Kalender (der EA meldet das selbst: „im Tester ohne Kalender“, Z. 1029).
  - Deshalb liefere ich gleich mit Stufe 0 das Skript `research/Kalender_Export.mq5`. Es schreibt die US-Termine hoher Bedeutung ab 2021-01-01 einmalig nach `MQL5\Files\deadband_kalender.csv`: Serverzeit, UTC, Event-ID, Name, Bedeutung, Ist/Prognose/Vorwert.
  - Daraus bekommt Familie 1 ihre Historie.
- **Externe Quelle:** nur falls das nicht reicht; dann schlage ich höchstens 2 Quellen vor und warte auf deine Wahl.

### 9.2 Zustandsdatei für den EA
- **Datei:** `<GFT-Datenordner>\MQL5\Files\deadband_sidecar.txt`, ASCII, `schluessel=wert`.
  - Atomar geschrieben (temporäre Datei, dann umbenennen).
  - Felder: Version, Schreibzeit UTC und Serverzeit, Datenalter, je Symbol Nachrichtensperre an/aus mit Ablaufzeit, Heartbeat-Status.
  - Terminal-Globalvariablen kann das Python-Paket nicht schreiben, daher die Datei.
- **EA-Seite:** `research/patch_sidecar_lesen.mq5` mit Schalter, Voreinstellung AUS = handelsidentisch.
  - Lesen im `OnTimer`.
  - Datei fehlt oder ist älter als `[MAX_DATENALTER]` → **fail-open**: der EA handelt wie heute, schreibt eine Journalzeile und sendet **eine** Push-Nachricht je Ausfall.
  - Jede neue Sperre hat einen eigenen Schalter, Voreinstellung AUS.

### 9.3 Überwachung (Heartbeat, jede Minute)
- **Prüfungen:**
  - Läuft der Prozess `terminal64.exe` **mit dem GFT-Pfad**? Prüfung über Windows-API, ohne Zusatzpaket.
  - Erst dann `initialize(path=<GFT terminal64.exe>)` – nie der Standardpfad, nie die Installation unter `C:\Program Files\MetaTrader 5`.
  - Ist das Terminal verbunden und Algo Trading an (`terminal_info`)?
  - Sind die Kontodaten lesbar (`account_info`)?
  - Ist der letzte Tick in der Handelszeit höchstens `[MAX_TICKALTER]` alt (`symbol_info_tick`)?
- **Nur lesende Aufrufe:** `account_info`, `positions_get`, `symbol_info_tick`, `terminal_info`. Keine Orders.
- **Alarm** nach E10, mit Entprellung (gleicher Alarm höchstens alle 30 min, Entwarnung einmal).
- **Log:** rotierend unter `C:\Trading\sidecar\logs` (7 × 5 MB). Keine Kontonummern, Passwörter oder Tokens im Log.

### 9.4 Installation `research/sidecar/Sidecar-Setup.cmd` (cmd/PowerShell-Polyglott, Doppelklick)
1. Python ≥ 3.10 x64 prüfen; fehlt es: Abbruch mit Anleitung (keine stille Installation ohne deine Freigabe).
2. venv unter `C:\Trading\sidecar\venv`, Pakete mit festen Versionen (E8).
3. Sidecar-Dateien eingebettet nach `C:\Trading\sidecar` schreiben.
4. GFT-Terminalpfad suchen (Ausschluss `C:\Program Files\MetaTrader 5`) und in `config.ini` eintragen; mehrdeutig → Abbruch mit Liste.
5. Aufgabe „DEADBAND Sidecar“:
   - beim Anmelden, 90 s Verzögerung, nach „MT5 Autostart GFT“;
   - interaktiv im selben Benutzer, sonst erreicht das Python-Paket das Terminal nicht;
   - Neustart bei Absturz (3 × alle 1 min).
6. Selbsttest: Import, Terminal gefunden, Zustandsdatei geschrieben und gelesen, ein Test-Alarm (nur mit deiner Bestätigung im Setup).
7. Außer der Aufgabe keine Registry-Einträge.

### 9.5 Tests
- **Unit-Tests:**
  - Kalender-Parser (CSV aus 9.1),
  - Zeitzonen: Serverzeit NY + 7 ↔ UTC, Journal in UTC, Umstellung EU 25.10.2026 und US 01.11.2026,
  - Zustandsformat (Lesen/Schreiben, Ablauf, kaputte Datei → fail-open).
- **Trockenlauf:** schreibt die Zustandsdatei in einen Testordner, ohne dass ein EA liest.
- **Betrieb:** `research/sidecar/BETRIEB.md` beschreibt Start, Stopp, Logs, Fehlerbilder und was bei einem Sidecar-Ausfall passiert (EA handelt unverändert weiter).

Der optionale Python-Papierprototyp kommt nur nach deinem ausdrücklichen OK. Ordersendung aus Python ist ausgeschlossen.

---

## 10. Daten- und Exportliste

Alles als MT5-Export „Balken“ (Symbole → Balken → Exportieren). Tabulator-CSV mit `<SPREAD>`, Serverzeit, ohne Änderung.

| Symbol (GFT-Name bitte prüfen) | Zeitrahmen | von | bis | Zweck |
|---|---|---|---|---|
| XAUUSD.x | M5, M15 | **2019-01-01** (sonst so früh wie verfügbar) | Datenende | Baseline; der Fade-Wächter braucht ~600 + 300 Tage Vorlauf |
| NAS100.x | M5, M15 | 2019-01-01 (dto.) | Datenende | Baseline |
| XAUUSD.x, NAS100.x | M1 | 2025-06-01 | Datenende | Stufe 3 (Gegenprobe Einstiegspreise) |
| XAGUSD.x | M5, M15 | 2021-01-01 | Datenende | Stufe 1 |
| USOIL / XTIUSD / WTI (Name?) | M5, M15 | 2021-01-01 | Datenende | Stufe 1 |
| BTCUSD.x | M5, M15 | 2021-01-01 | Datenende | Stufe 1 |
| DXY/USDX, falls vorhanden | M5, M15 | 2021-01-01 | Datenende | nur Familie 5 (E4) |

**Außerdem:**
1. **Spezifikation** je Symbol (Rechtsklick → Spezifikation, Text oder Bildschirmfoto) für XAGUSD, Öl, BTC und den 3-fach-Swap-Tag von NAS100.x.
2. **Kalender-CSV** aus `Kalender_Export.mq5` (liefere ich in Stufe 0).
3. **MT5-Referenzbericht** V8.10 wie 4.4 (HTML oder XML, dazu die `.set`-Datei und das Tester-Journal).
4. **Für den Fall, dass das Gate fällt:** je ein Testerlauf mit nur einem Modul aktiv (DEADBAND, Fades, RSI21, Noise, Sondermodule). Ich schicke dann die genauen Einstellungen.

---

## 11. Variantenzahl und Rechenzeit (Schätzung)

| Stufe | Varianten | Zufallsläufe | Rechenzeit |
|---|---|---|---|
| 0 Kalibrierung | 1 (Baseline) | – | < 15 min |
| 1 Instrumente | 3 | – | < 30 min |
| 2 F1 Ereignis | 3 je Symbol × 2 = 6 | 1000 je Variante | |
| 2 F2 Retest | 5 je Symbol × 2 = 10 | 1000 je Variante | |
| 2 F3 Asien (NAS) | 3 | 1000 je Variante | |
| 2 F4 D1-Trend | 3 je Symbol × 2 = 6 | 1000 je Variante | |
| 2 F5 | 0 (E4) | – | |
| 2 Summe | 25 | 25 000 | ~1–2 h |
| 3 Intrabar | 8 Testerläufe, 14 Auswertungen | – | < 30 min (Tester: deine Zeit) |
| 4 Kombination + Blindlauf | ≤ 3 | – | < 1 h |
| **Gesamt** | **≈ 46** | | |

Keine Familie hat mehr als 10 Varianten → Schwelle 95 %. Die Schätzungen der Signalhäufigkeit in Abschnitt 6 sind **Annahmen** und werden in Stufe 2 durch gemessene Werte ersetzt.

---

## 12. Risiken und Grenzen

- **R1 Server-Betrieb:** Der EA dokumentiert selbst, dass GFT Instant Premium bei Kauf ab 12.08.2026 VPS/Server verbietet (EA Z. 885–888 `VpsSperre`; Bericht 6.10, Abschnitt 6, Schritt 5). `VpsSperre` erkennt nur den MetaQuotes-VPS, nicht deinen Windows-Server. Bitte die aktuelle Regel für dein Konto bei GFT schriftlich klären – ein Verstoß kann das Konto kosten, unabhängig von jeder Strategie.
- **R2 Kalibrierung:** Abschnitt 4.4. Fällt das Gate, stoppe ich, statt mit einem unkalibrierten Motor weiterzurechnen.
- **R3 Seitwärtsjahr:** Ein echtes Seitwärtsjahr fehlt (Befund 6). Die Fremddaten 2006–2021 des Repos verwende ich nur als Gegenprobe, nicht als Auswahlbasis; sie haben keine GFT-Spreads und bei NAS bis 2020 keine Spreads.
- **R4 Bootstrap von V8:** Zustandsabhängige Regeln lassen sich auf Tagesebene nur näherungsweise abbilden (3.3). Darum rechne ich die rollierenden Konten als Gegenprobe mit.
- **R5 Kurzes Blindfenster:** ≈ 15 Monate (E6). Seltene Familien (F4: 1–2/Monat) haben dort wenige Trades; das Urteil kann deshalb „nicht entscheidbar“ lauten. Ich lockere dann kein Kriterium.
- **R6 Nicht kompiliert:** Alle `.mq5` aus diesem Auftrag sind ungeprüft, bis du sie im MetaEditor kompiliert hast.
