# DEADBAND Sidecar – Betrieb

Der Sidecar ist ein Python-Begleitprozess auf dem Server. Er **überwacht** das GFT-Terminal und **meldet** Probleme. Er sendet **keine Orders** und ändert nichts am Konto.

Fällt er aus, handelt der EA **unverändert weiter** (fail-open).

---

## 1. Was er jede Minute prüft

| Prüfung | Quelle | Alarm, wenn … |
|---|---|---|
| GFT-Terminal läuft | Windows-Prozessliste: Pfad = `terminal_pfad` aus `config.ini` | der Prozess fehlt |
| Python erreicht das Terminal | `MetaTrader5.initialize(path=<GFT terminal64.exe>)` | das Terminal läuft, ist aber nicht erreichbar |
| Verbunden mit dem Broker | `terminal_info().connected` | nicht verbunden |
| Algo Trading an | `terminal_info().trade_allowed` | aus |
| Kontodaten lesbar | `account_info()` | nicht lesbar |
| Kurse frisch | `symbol_info_tick` je Symbol | letzter Tick älter als 120 s, **nur in der Handelszeit** (Sonntag 18:15 bis Freitag 17:00 NY, ohne die Pause 17:00–18:15 NY, ohne US-Feiertage und verkürzte Tage) |

**Sicherheitsregeln:**
- `initialize` läuft nur, wenn der GFT-Prozess schon läuft. Der Sidecar startet also nie selbst ein Terminal.
- Es gibt immer einen expliziten Pfad, nie den Standardpfad.
- Die Altlast `C:\Program Files\MetaTrader 5` ist gesperrt: `config.ini` mit diesem Pfad wird abgelehnt.
- Nach dem Verbinden wird geprüft, ob `terminal_info().path` wirklich der GFT-Ordner ist. Sonst trennt der Sidecar sofort.
- Es gibt nur lesende Aufrufe: `terminal_info`, `account_info`, `positions_get`, `symbol_info_tick`.

## 2. Alarme

**Kanäle (E10):**
- **ntfy.sh:** funktioniert auch, wenn das Terminal steht.
- **MT5-Push:** nur über den gepatchten EA, siehe Abschnitt 5.

**Entprellung:**
- Gleicher Alarm höchstens alle 30 min, mit dem Zusatz „(dauert an)“.
- Entwarnung genau einmal: „OK wieder: …“.

**ntfy einrichten:**
1. App **ntfy** installieren (Android/iOS).
2. „+“ → Thema abonnieren, Server `ntfy.sh`.
3. Thema eintragen: Das Setup zeigt es an, es steht auch in `C:\Trading\sidecar\config.ini` unter `ntfy_thema`.

Das Thema wirkt wie ein Passwort: Wer es kennt, liest mit. Nicht weitergeben. Es enthält keine Kontodaten, und die Meldungen enthalten keine Kontonummer.

| Meldung | Bedeutung | Was tun |
|---|---|---|
| GFT-Terminal läuft nicht | Prozess fehlt (Absturz, Update, Neustart) | Web-Konsole öffnen, Terminal starten. Läuft der Server neu, startet „MT5 Autostart GFT“ es selbst. |
| Terminal läuft, aber MetaTrader5-Paket erreicht es nicht | `initialize` scheitert | Meist ein Terminal-Dialog (Update, Anmeldung). In der Konsole nachsehen. |
| Terminal nicht mit dem Server verbunden | Broker-Verbindung weg | Unten rechts im Terminal prüfen. Wenn es länger dauert: Konto neu anmelden. |
| Algo Trading ist aus | Knopf „Algo Trading“ aus | Wieder einschalten. Der EA meldet das zusätzlich selbst (HandelWaechter). |
| Kontodaten nicht lesbar | Anmeldung verloren | Im Terminal neu anmelden. |
| `<Symbol>`: letzter Tick älter als 120 s | keine Kurse in der Handelszeit | Marktbeobachtung prüfen. Bei Feiertagen ohne Eintrag in der Liste: ignorieren und mir melden. |
| Kalender läuft aus | nur bei `nachrichten_sperre = 1` | `DEADBAND_Kalender_Export` im Terminal erneut ausführen. |
| Sidecar-Fehler: … | Ausnahme im Sidecar | Er läuft weiter. Details im Log. Wiederholt es sich: Log schicken. |

## 3. Start, Stopp, Status

Die Aufgabe heißt **„DEADBAND Sidecar“**:
- Sie startet beim Anmelden, 90 s verzögert (also nach „MT5 Autostart GFT“, das nach 60 s startet).
- Sie läuft interaktiv im selben Benutzer.
- Nach einem Absturz startet sie neu: 3 Versuche im Abstand von 1 min.
- Läuft schon ein Sidecar, beendet sich ein zweiter sofort.

| Was | Befehl (PowerShell) |
|---|---|
| Starten | `Start-ScheduledTask -TaskName 'DEADBAND Sidecar'` |
| Stoppen | `Stop-ScheduledTask -TaskName 'DEADBAND Sidecar'` |
| Status | `Get-ScheduledTask -TaskName 'DEADBAND Sidecar' \| Get-ScheduledTaskInfo` |
| Ein Durchlauf von Hand | `C:\Trading\sidecar\venv\Scripts\python.exe C:\Trading\sidecar\sidecar.py --einmal` |
| Selbsttest | `... sidecar.py --selbsttest` |
| Testalarm | `... sidecar.py --testalarm` |

**Log:**
- Datei `C:\Trading\sidecar\logs\sidecar.log`, Zeiten in **UTC**.
- Rotiert: 7 Dateien zu je 5 MB.
- Enthält keine Kontonummern, Passwörter oder Tokens.

**Deinstallation:**
1. `Unregister-ScheduledTask -TaskName 'DEADBAND Sidecar' -Confirm:$false`
2. Ordner `C:\Trading\sidecar` löschen.

Sonst wurde nichts eingetragen: keine Registry, kein Dienst.

## 4. Zustandsdatei `MQL5\Files\deadband_sidecar.txt`

- ASCII, eine Zeile `schluessel=wert` je Eintrag, CRLF.
- Atomar geschrieben (temporäre Datei, dann ersetzen).
- Erste Zeile `version=1`, letzte Zeile `ende=1`. Fehlt `ende=1`, gilt die Datei als kaputt.

| Schlüssel | Inhalt |
|---|---|
| `zeit_utc`, `zeit_server` | Schreibzeit in Sekunden seit 1970: UTC bzw. Serverzeit (= NY + 7 h) |
| `schreibzeit_utc`, `schreibzeit_server` | dasselbe lesbar |
| `terminal`, `verbunden`, `algo`, `konto` | 1/0 |
| `positionen` | Zahl offener Positionen (−1 = unbekannt) |
| `tickalter_<Symbol>` | Sekunden seit dem letzten Tick (−1 = unbekannt) |
| `heartbeat` | `OK`, `WARNUNG` oder `FEHLER` |
| `probleme` | offene Prüfungen, mit `;` getrennt |
| `sperre_<Symbol>`, `sperre_bis_<Symbol>` | Nachrichtensperre jetzt an/aus und Ende (nur mit `nachrichten_sperre = 1`) |
| `fenster_von_<Symbol>`, `fenster_bis_<Symbol>` | laufendes oder nächstes Sperrfenster (Serverzeit) |
| `naechster_termin`, `kalender_bis` | nächster Termin, letzter Termin in der Kalenderdatei |
| `alarm_nr`, `alarm_text` | letzter Alarm. Die Nummer zählt über Neustarts weiter. |

## 5. EA-Seite (optional): `DEADBAND_Forschung\DEADBAND_V8_Sidecar`

Das Setup legt diesen EA neben den laufenden und kompiliert ihn. Er ist **V8.10 plus Lesen der Zustandsdatei** (`research/patch_sidecar_lesen.mq5`, Änderungen in `patch_sidecar_lesen.diff`). Mit den Standardwerten handelt er **identisch zu V8.10**.

| Eingabe | Standard | Wirkung |
|---|---|---|
| `SidecarLesen` | **false** | Zustandsdatei alle 10 s lesen. Bei `false`: kein Dateizugriff. |
| `SidecarMaxAlterS` | 180 | Datei fehlt, ist kaputt oder älter → **fail-open**. Der EA handelt wie ohne Sidecar, schreibt **eine** Journalzeile und sendet **einen** Push je Ausfall (5 min Schonfrist nach dem EA-Start). |
| `SidecarPush` | true | Neue Sidecar-Alarme als MT5-Push weitergeben (nur, wenn `UsePush` an ist). |
| `SidecarSperre` | **false** | Sperrfenster des Sidecars **zusätzlich** zur eingebauten News-Sperre werten. Nur bei gültigem Zustand. |

**Einschalten, wenn gewünscht:**
1. Chart des EA → Eigenschaften → Eingaben **speichern** (.set).
2. `DEADBAND_V8_Sidecar` auf denselben Chart ziehen, die .set laden, `SidecarLesen = true` setzen.

Der EA-Wechsel ist ein Neustart des EA. V8.10 baut seinen Kontozustand dabei aus der Historie neu auf, wie nach jedem Terminal-Neustart.

**Empfehlung:** Zuerst eine Woche nur mit ntfy laufen lassen. `SidecarSperre` bleibt aus. V8.10 hat seine News-Sperre schon aus dem MQL5-Kalender (PLAN 9.1), und eine zweite Quelle bringt nur dann etwas, wenn der Terminal-Kalender ausfällt.

## 6. Was bei einem Sidecar-Ausfall passiert

- **EA:** handelt unverändert weiter. Mit `SidecarLesen = true` kommt einmal „Sidecar ausgefallen (…) – EA handelt unverändert weiter“, sobald die Datei älter als 180 s ist.
- **Aufgabe:** startet den Sidecar nach einem Absturz bis zu 3-mal neu.
- **Überwachung:** fehlt in der Zeit des Ausfalls. Die eingebauten Wächter des EA (HandelWaechter, Lebenszeichen) laufen weiter.

## 7. Hinweis zum Server

V8.10 nennt im Kopf (6.10, `VpsSperre`): GFT Instant Premium mit Kauf ab 12.08.2026 verbietet VPS/Server. Der Sidecar ändert daran nichts. Er setzt den Serverbetrieb nur voraus (PLAN R1).
