---
name: "trade-analyser-mt5"
description: "Trade-Analyser für NAS100, GER40, ETH aus Alex' MT5. Nutzen bei \"setup\", \"NAS\", \"NAS100\", \"US100\", \"Nasdaq\", \"DAX\", \"GER40\", \"ETH\", \"ETHUSD\", \"chart\" oder \"auswerten\"."
---

# Trade-Analyser MT5

Die Kursdaten kommen aus dem offenen MT5 auf Alex' PC. Der MT5-Dienst TA_Export schreibt laufend M5- und M30-Kerzen in einen Ordner. Das Script ta_mt5.py rechnet daraus deterministisch Regime, Entry, Stop, Target, CRV, News-Sperre, Auswahl, Begründung und Chart.
Deine Arbeit: News holen, das Script ausführen, seine Ausgabe Zeichen für Zeichen weitergeben und bei einem Trade den Chart schicken. Nichts umrunden, nichts ergänzen, nie Levels raten, keine Werte aus Screenshots oder dem Gedächtnis.

## Konstanten
- ORDNER_WIN = C:\Users\agatt\AppData\Roaming\MetaQuotes\Terminal\Common\Files\TA_Export
- SHA = 55c6dae2282d359d9e354280b2f64f382b39e5b41bfd6f6e5983c1046a904c48
- Sicherung des Scripts im Projekt „Analyzer“: claude/ta_mt5.py
- Script-Version: `version` im JSON muss `mt5-1.4` sein (sonst läuft eine alte Fassung).

## Befehle
- "setup": alle drei Instrumente, genau EIN Trade (das Script wählt selbst).
- "NAS100"/"NAS"/"Nasdaq"/"US100" → ZUSATZ `--nur NAS100`. "DAX"/"GER40" → `--nur GER40`. "ETH"/"ETHUSD" → `--nur ETH`.
- "chart": den Chart des zuletzt in diesem Chat ausgegebenen Trades noch einmal schicken (Schritt 4 mit dessen Pfad). Gibt es keinen: genau `Kein Trade zum Zeichnen: zuerst setup ausführen.`
- "auswerten": nur ZEIT holen (kein News-Schritt), Schritt 2 mit ARGS = `--zeit 'ZEIT' --auswerten`, die Ausgabe (Form L) unverändert weitergeben, kein Chart. (Das Wort muss auch in der Projektanweisung und in den Auslösern des Skills stehen, sonst wird der Skill dafür nicht geladen.)
- "mt5-1.4 zurückrollen": siehe Abschnitt „Zurückrollen“.
- News-Angaben von Alex haben Vorrang (Schritt 1c).

## Ausgabeformat
Bei einem Trade zuerst der Chart als Datei, danach als Textantwort NUR das Feld "ausgabe" des Scripts, unverändert:
- Form A (Trade): die vier Zeilen Entry / Target / Stop / Begründung. Danach kann eine fünfte Zeile `(Chart nicht erstellt: …)` folgen; sie gehört zur Ausgabe.
- Form B: eine Zeile, beginnt mit `Kein Trade:`.
- Form C: eine Zeile, beginnt mit `Technischer Fehler:`.
- Form L (nur "auswerten"): die Auswertungszeilen des Scripts, unverändert.
Die Begründungszeile von Form A (und der Satz von Form B) kann mit `Nicht auswertbar (technischer Fehler): …` enden: Das Script meldet damit ausgefallene Instrumente und gehört zur Ausgabe. Ebenso `(Signal-Log nicht geschrieben: …)`: Das Script meldet damit, dass dieses Signal nicht protokolliert wurde.
Keine Einleitung, keine Disclaimer, keine Risikohinweise, kein Text zwischen den Tool-Aufrufen.

## Ablauf (so wenig Aufrufe wie möglich)

### 1. Zeit und News – im SELBEN Schritt parallel aufrufen
- Zeit-Tool → ZEIT (Zeitstempel unverändert, immer MIT Zeitzonen-Offset, z. B. 2026-10-01T14:03:12+02:00).
- Gleichzeitig genau 1 Websuche mit dem heutigen Datum aus dem Kontext: "economic calendar [Datum] CPI NFP FOMC ECB Eurozone". Entfällt, wenn Alex "keine News" oder "News ignorieren" schreibt (dann nur seine eigenen Termine, sonst NEWS = []).
- Maßgeblich ist das Datum aus ZEIT. Weicht das Kontext-Datum davon ab (Chat läuft über Mitternacht), die Suche mit dem ZEIT-Datum wiederholen.

NEWS = JSON-Liste mit doppelten Anführungszeichen, z. B. `[["CPI","08:30","ET"]]`. Namen ohne Punkt, Anführungszeichen oder Apostroph. Erlaubte Zonen: ET/EST/EDT (New York), CET/CEST/MEZ/MESZ/WIEN (Wien), GMT/UTC, BST (London). Du rechnest nie um.

a) Für jeden heutigen Termin aus dieser Tabelle IMMER den Tabelleneintrag aufnehmen:
   - US-CPI, US-PCE, NFP, US-GDP: ["Name","08:30","ET"]
   - FOMC: ["FOMC","14:00","ET"] und ["FOMC-Pressekonferenz","14:30","ET"]
   - EZB: ["EZB","14:15","CET"] und ["EZB-Pressekonferenz","14:45","CET"]
   - Eurozone-HVPI (Schnellschätzung), Eurozone-BIP (Schnellschätzung): ["Name","11:00","CET"]
   - Rede des Fed-Chairs: nur, wenn die Quelle Uhrzeit und erlaubte Zone nennt.
b) Nennt die Quelle eine Uhrzeit mit erlaubter Zone, diese ZUSÄTZLICH unverändert aufnehmen. Liefert die Suche Ergebnisse, aber kein relevanter Termin oder Uhrzeit/Zone unklar: NEWS = [] (die Einträge aus a) gelten trotzdem).
c) Alex' Angaben gehen vor: "CPI 14:30" ersetzt alle CPI-Einträge durch ["CPI","14:30","WIEN"] (bei FOMC/EZB nur den Zinsentscheid, die Pressekonferenz bleibt). "CPI ist durch" / "FOMC ignorieren" streicht diesen Typ. Fed/FOMC/Powell = FOMC, EZB/ECB = EZB, NFP/Arbeitsmarkt = NFP.

d) Websuche scheitert HART (Tool-Fehler oder null Ergebnisse): EINE zweite Suche mit anderer Formulierung ("wichtige Wirtschaftstermine heute USA Eurozone [Datum]"). Scheitert auch sie hart, KEIN Script-Lauf, sondern Form C: `Technischer Fehler: News-Kalender nicht abrufbar. Nochmal "setup" oder "setup keine News" bzw. Termine nennen.` Liefert die Suche irgendwelche Ergebnisse, gilt sie als gelesen (auch wenn sie keinen Termin enthält oder Seiten für andere Tage): weiter mit a) bis c), kein Abbruch. (Nie bei hartem Ausfall stillschweigend NEWS = [] setzen: Das Script kennt die Termine nicht und würde in CPI/NFP/FOMC hineinhandeln.)

### 2. Script – EIN device_bash-Aufruf (ZEIT und ARGS ersetzt)
ARGS = `--zeit 'ZEIT' --news 'NEWS' ZUSATZ` (setup und Instrumente) oder `--zeit 'ZEIT' --auswerten` (auswerten).
```
D=""; for f in "$HOME"/mnt/*/ta_mt5.py "$HOME"/mnt/*/TA_Export/ta_mt5.py "$HOME"/mnt/*/Files/TA_Export/ta_mt5.py "$HOME"/mnt/*/Common/Files/TA_Export/ta_mt5.py; do [ -f "$f" ] && { D=$(dirname "$f"); break; }; done; [ -z "$D" ] && { echo ORDNER_FEHLT; exit 0; }; [ "$(sha256sum "$D/ta_mt5.py" | cut -c1-64)" = "55c6dae2282d359d9e354280b2f64f382b39e5b41bfd6f6e5983c1046a904c48" ] || { echo PRUEFSUMME_FALSCH; exit 0; }; cd "$D" && python3 ta_mt5.py ARGS
```
Das Ergebnis ist JSON mit "form" (A/B/C/L), "ausgabe" und "chart" (Pfad ~/mnt/… oder null). Das Feld "log" ist nur für die Fehlersuche und wird nicht ausgegeben.

### 3. Sonderfälle
- `ORDNER_FEHLT` oder die Meldung, dass kein Ordner verbunden ist: device_request_folder_access mit ORDNER_WIN (reason: "Kursdaten des MT5-Exporters für den Trade-Analyser lesen"), dann Schritt 2 einmal wiederholen. Wieder `ORDNER_FEHLT`: Wiederherstellung.
- `PRUEFSUMME_FALSCH`: Wiederherstellung.
- Keine device-Werkzeuge (auch nicht per Tool-Suche) oder PC nicht erreichbar: `Technischer Fehler: PC nicht erreichbar (PC an, Claude-Desktop-App offen und dieser Chat mit dem PC verbunden?).`
- "ausgabe" beginnt mit `Technischer Fehler: MT5-Export nicht lesbar` (auch bei "auswerten"): 5 s warten, neue ZEIT holen, Schritt 2 genau einmal wiederholen. Jeden anderen Form-C-Text unverändert ausgeben.
- Die Antwort enthält KEIN JSON-Objekt und ist weder `ORDNER_FEHLT` noch `PRUEFSUMME_FALSCH` (die beiden haben ihre eigenen Regeln oben): `Technischer Fehler: Script-Ausgabe unlesbar` plus die letzte Zeile der Fehlermeldung, sonst nichts. Maßgeblich ist das JSON auf stdout; Warnungen davor oder daneben (z. B. eine DeprecationWarning von Python) sind kein Fehler und werden nicht ausgegeben.

### 4. Chart – nur wenn "chart" nicht null
- device_stage_files mit dem Pfad aus "chart".
- SendUserFile mit dem stagedPath, display "render", status "normal", ohne caption.
- Scheitert das: Textantwort trotzdem ausgeben, darunter genau `(Chart konnte nicht übertragen werden)`.

### 5. Ausgabe
Kontrolle bei Form A: die ersten vier Zeilen beginnen mit `Entry:`, `Target:`, `Stop:`, `Begründung:` (eine weitere Zeile, die mit `(Chart` beginnt, ist erlaubt); E, T, S aus den drei Zeilen. Long: S < E < T, Short: T < E < S. Verstoß: `Technischer Fehler: Script-Ergebnis widersprüchlich` plus Instrument und S/E/T. Sonst "ausgabe" unverändert als Textantwort.

## Wiederherstellung (nur wenn das Script fehlt oder die Prüfsumme falsch ist)
1. Projects project_read "claude/ta_mt5.py" (geht nur im Projekt „Analyzer“; sonst Form C `Technischer Fehler: ta_mt5.py fehlt auf dem PC.`). Inhalt als Datei nehmen bzw. unverändert mit Write in eine Datei schreiben.
2. Nach /mnt/user-data/outputs/ta_mt5_[ZEIT ohne Sonderzeichen].py kopieren (immer neuer Dateiname) und mit sha256sum prüfen. ≠ SHA: `Technischer Fehler: Script-Sicherung im Projekt passt nicht zur Prüfsumme.`
3. device_commit_files: stagedPath = diese Datei, devicePath = ORDNER_WIN\ta_mt5.py, force true. Dann Schritt 2 neu. Wieder falsch: `Technischer Fehler: ta_mt5.py auf dem PC lässt sich nicht wiederherstellen.`

## Zurückrollen (nur auf "mt5-1.4 zurückrollen", z. B. nach dem Urteil `ZURÜCK AUF mt5-1.3`)
1. project_read "claude/ta_mt5_v1.3_backup.py", prüfen, dass die SHA-256 `54b571ca5772e2adce15d5a73aa21c33805d7b97759d1ea84d7e1f32b32df19e` ist, dann per project_write als "claude/ta_mt5.py" ablegen.
2. project_read "claude/SKILL_trade-analyser-mt5_v1.3_backup.md" und Alex diesen Skill zum Speichern geben (propose_skills, Verbesserung von trade-analyser-mt5).
3. Beim nächsten "setup" mit dem alten Skill holt die Wiederherstellung das alte Script von selbst auf den PC. `signale.jsonl` und `auswertung.jsonl` bleiben unverändert.

## Stellschrauben
Alle Regelwerte stehen in der Zeile `SET = dict(…)` in ta_mt5.py und sind durch SHA geschützt. Nur auf Alex' ausdrücklichen Wunsch ändern: Script im Projekt und auf dem PC anpassen, neue Prüfsumme nennen, damit sie hier an BEIDEN Stellen (Konstanten und Script-Aufruf in Schritt 2) eingetragen wird; `TA_VERSION` im Script hochzählen und oben unter „Script-Version“ nachziehen.

## Regelwerk (nur Info, nie selbst nachrechnen)
- Daten: MT5-Kerzen des Brokers (aktuell Qberx: NAS100.c, GER40.pro, ETHUSD.pro). Regime aus M30, Setup aus M5, laufende Kerze = aktueller Kurs.
- Session-VWAP (hlc3, Tick-Volumen) mit ±1/2/3σ, Neustart jeden Broker-Tag 00:00 Serverzeit (Qberx UTC+3 = 23:00 Wien im Sommer). Supertrend (10, 3) auf M30.
- Ab mt5-1.4 ist JEDES Signal eine Market-Order zum aktuellen Kurs (Entry = Kurs, gerundet). Es gibt keine Limits mehr; die Order ist sofort gefüllt.
- Handelszeit (nur dann gibt es Einstiege), Montag bis Freitag: NAS100 und ETH 09:45–15:30 New York (meist 15:45–21:30 Wiener Zeit), GER40 09:15–17:00 Wien. Außerhalb, auch am Wochenende: Form B mit Grund „außerhalb der Handelszeit“.
- Eröffnungssperre NAS100 09:25–09:44 New York, GER40 08:55–09:14 Wien: dort gar kein Trade. News-Sperre 30 min vor bis 15 min nach jedem Termin. Mindestziel 0,2 % / 0,3 %. Kein Trade in den ersten 60 min nach VWAP-Neustart; geschlossen, wenn die letzte M5-Kerze > 15 min alt ist.
- REGIME: Supertrend der letzten geschlossenen M30-Kerze; RANGE, wenn Kurs und M30-VWAP dem widersprechen oder ≥ 4 Kreuzungen des M5-VWAP und Kurs zwischen ±1σ. RANGE: kein Trade.
- TREND (Richtung des Supertrends): Einstieg im Rücksetzer. Die letzte geschlossene 5min-Kerze schloss gegen den Trend (Long: rot, Short: grün) und der Kurs liegt mehr als 0,25 und höchstens 1,5 ATR5 unter dem Hoch (Long) bzw. über dem Tief (Short) der letzten 12 geschlossenen 5min-Kerzen.
- Stop 3 × ATR(14) M5 hinter dem Entry; die Begründung nennt den echten Abstand in Punkten. Target 0,75 × Risiko, mindestens das Mindestziel. Das CRV liegt damit meist bei 0,75 (die Anzeige rundet ab, z. B. „0,7“). Greift das Mindestziel, ist es höher (ruhiger Markt). Rundung: Long Stop und Target abgerundet, Short aufgerundet.
- Auswahl bei setup: TREND vor RANGE, Market vor Limit, näheres Limit, dann bei Market-Signalen ab mt5-1.4 das CRV am nächsten an 0,75 (sonst höherer CRV), dann NAS100, GER40, ETH.
- Ein Index ohne Tick seit > 15 min gilt als geschlossen (Form B), nicht als technischer Fehler; bei ETH (24/7) bleibt es ein Fehler.
- Das Script kennt keine Börsenfeiertage. An US-Feiertagen ist der NAS100-CFD dünn; im Backtest waren Signale an diesen Tagen klar schlechter. Fragt Alex danach: an US-Börsenfeiertagen besser kein NAS100-Signal handeln.
- Warum so: Getestet wurde auf NAS100 2021–25, GER40 Feb–Sep 2026 und 2021–23 sowie ETH 2021–26. Der Bericht `BERICHT_mt5-1.4.md` liegt im GitHub-Repo von Alex, nicht im Projekt.
  - mt5-1.3 kam auf 22–28 % Target vor Stop; nur rund 36 % der Limits wurden gefüllt; nach Spread −0,06 bis −0,28 R je Trade.
  - mt5-1.4 kommt auf 56–62 % Target vor Stop, und jede Order ist gefüllt. Nach Spread liegt es außerhalb der Abstimmungsdaten bei −0,03 bis +0,02 R je Trade, also etwa ±0. In der Abstimmung (NAS100 2021–23) waren es +0,055.
  - Ein belegter Vorteil ist das nicht: Zufallseinstiege mit gleichem Stop, Target und Zeitfenster schneiden auf NAS100 2024/2025 und GER40 2026 gleich ab. Die höhere Trefferquote kommt vor allem vom Verhältnis Stop zu Target.
- Stellschraube ZIEL_R (nur auf Alex' Wunsch): 0,5 statt 0,75 hebt Target vor Stop im Backtest um 4–8 Punkte (auf 61–69 %). Der Ertrag je Trade ändert sich dabei um −0,02 bis +0,003 R.
- Chart: letzte 212 M5-Kerzen, VWAP-Bänder, Entry/Stop/Target mit Risiko- und Zielzone, Wiener Zeit.

## Signal-Log und Auswertung
Jedes ausgegebene Trade-Signal (Form A) hängt das Script als Zeile an `signale.jsonl` im Scriptordner; gelingt das Schreiben nicht, steht das am Ende der Begründungszeile; die Ergebnisse schreibt "auswerten" nach `auswertung.jsonl`. "auswerten" bewertet die Signale gegen die M5-Kerzen des Brokers (Füllung, Target/Stop, R) und zeigt Füllquote, Trefferquote mit 95 %-Intervall, Summe R, Füllquote je Entfernung in ATR5, Wartezeit bis Füllung, Haltedauer, getrennt nach Klasse und Zielstufe. Gezählt werden nur Signale, die älter als 480 min sind (sonst steht ein schon gefüllter Gewinner im Nenner, ein noch wartendes Limit nicht); jüngere stehen nur als Zahl in der Kopfzeile. Jedes Signal gilt als platziert. Ein Signal desselben Instruments und derselben Richtung gilt als Wiederholung und zählt nicht mit, wenn das letzte gezählte Signal zu diesem Zeitpunkt gefüllt und im Markt war, oder wenn dessen Order noch lebte und der neue Entry höchstens 0,5 ATR5 davon entfernt ist (dieselbe Order, neu angesagt). Ein wartendes oder nie gefülltes Limit mit anderem Level macht das Folgesignal nicht zur Wiederholung. Signale, die vor einer Serverzeit-Umstellung des Brokers liegen und danach erst ausgewertet werden, sind `unbewertbar`. Reihenfolge pessimistisch (Stop und Target in derselben Kerze zählt als Stop), Füllung optimistisch (Berührung = Füllung, kein Spread): Die Füllquote ist eine Obergrenze, die Zeile „knapp“ zeigt, wie viele Füllungen nur knapp durchstoßen wurden. Ein Signal ohne Treffer (Limit nie gefüllt, Zeitablauf) wird erst bewertet, wenn der Export das ganze Auswertefenster abdeckt; bis dahin bleibt es offen (Kopfzeile „offen trotz Alter“). Signale, die älter sind als die exportierte M5-Historie, werden `unbewertbar`; deshalb mindestens einmal pro Handelstag auswerten. Ab mt5-1.4 rechnet jeder Lauf zusätzlich die Regeln von mt5-1.3 (Limit-Leiter). Unter mt5-1.3 lief derselbe Vergleich gegen mt5-1.1; mit mt5-1.4 beginnt er von vorn. Die Zeilen der alten Versionen bleiben im Log, zählen in den Gesamtzahlen mit und stehen getrennt in den Zeilen „Version …“; diese zeigen ab mt5-1.4 auch Target vor Stop je Version. Die Zeilen „Target auf erstem Level“ / „Target weiter gestreckt“ betreffen nur Signale bis mt5-1.3 (mt5-1.4 schreibt `zielstufe` −1). Jede Signalzeile trägt `vergleich` (gleich / anders / alt_kein = alte Regeln hätten Kein Trade geliefert / fehler); `grund` (ziel / markt / beide) gibt es nur in Zeilen von mt5-1.3. Wo die alten Regeln anders gewählt hätten, legt das Script eine Schatten-Zeile an (`quelle` = `schatten`, `paar` = id des echten Signals oder null bei neu Kein Trade); Schatten-Zeilen werden nie ausgegeben und zählen in keiner Hauptstatistik. Die Zeile „Regelvergleich“ stellt zwei vollständige Spuren über dieselben Läufe gegenüber: neu = alle ausgegebenen Signale der laufenden Version, alt = Signale mit `vergleich` gleich plus Schatten-Zeilen. Der „Zwischenstand“ ist nur Information. Ein Urteil gibt das Script nur an festen Prüfpunkten (50 / 100 / 150 gefüllte Trades der neuen Spur, Daten bis dahin eingefroren; t-Wert über die Tagesdifferenzen; ZURÜCK, wenn t unter −2,00 / −1,80 / −1,65). Die Zeilen „Prüfpunkt … bestanden“ und „Urteil“ gibt Claude wie den Rest unverändert weiter. Die Zeilen „Zielvorlauf“, „Limit gefüllt“ und „knapp“ betreffen nur Limit-Signale (aus mt5-1.3 und älter); mt5-1.4 erzeugt nur Market-Signale, die immer als gefüllt zählen. Die Dateien `signale.jsonl` (Signale) und `auswertung.jsonl` (Ergebnisse) werden nur angehängt, nie neu geschrieben. Regel-Änderungen erst ab etwa 150 gefüllten Trades.

## Voraussetzungen auf dem PC
MT5 (C:\Program Files\MetaTrader 5) offen und eingeloggt, Dienst TA_Export gestartet, Claude-Desktop-App offen. Findet der Dienst ein Symbol nicht: Namen in TA_Export\symbole.txt, dann Eingabe SymNAS/SymGER/SymETH im Dienst setzen.
