# Daten für die DEADBAND-Forschung – Anleitung (Server, nur Web-Konsole)

Was du tust (etwa 30 min Arbeit, dazu 1–3 h Wartezeit für den Testerlauf):

1. Setupdatei herunterladen und doppelklicken (installiert und kompiliert drei Dateien im GFT-Terminal)
2. Zwei Exportskripte im Terminal starten
3. Einen Referenzlauf im Strategietester machen
4. Setupdatei erneut doppelklicken → Upload-Ordner auf dem Desktop
5. Den Upload-Ordner im Browser zu GitHub hochladen

Dein Konto wird nicht angefasst: Die Skripte lesen nur, der Referenz-EA läuft nur im Tester. Der live laufende EA wird weder ersetzt noch neu geladen. Die Altinstallation unter `C:\Program Files\MetaTrader 5` wird nie angesprochen.

---

## 1. Setupdatei

1. Im Browser des Servers öffnen und herunterladen (Knopf „Download raw file“):
   `https://github.com/agattermann007-droid/claude/blob/claude/upbeat-maxwell-f7pmp0/DEADBAND/research/export/Export-Setup.cmd`
2. Doppelklicken. Fragt Windows „Der Computer wurde geschützt“: **Weitere Informationen → Trotzdem ausführen**.
3. Die Datei sucht das laufende GFT-Terminal (die Altlast ist ausgeschlossen). Bei mehreren Treffern fragt sie nach der Nummer.
   - Sie legt ab:
     - `MQL5\Scripts\DEADBAND\DEADBAND_Daten_Export.mq5`
     - `MQL5\Scripts\DEADBAND\DEADBAND_Kalender_Export.mq5`
     - `MQL5\Experts\DEADBAND_Forschung\DEADBAND_V8_810_Referenz.mq5` (= `DEADBAND_V8.mq5` Build 8.10, unverändert)
   - Sie kompiliert alle drei mit dem MetaEditor des GFT-Terminals und zeigt je Datei **OK** oder **FEHLER**.
4. **Wichtig:** Steht beim Referenz-EA **FEHLER**, kompiliert V8.10 nicht. Dann bitte trotzdem weiter mit Schritt 2 und das Protokoll mit hochladen; ich behebe den Fehler zuerst.

Findet die Datei das Terminal nicht: Installationsordner des GFT-Terminals (dort liegt `terminal64.exe`) als einzige Zeile in `C:\Trading\gft_terminal.txt` schreiben und erneut doppelklicken.

## 2. Exportskripte

1. Im Terminal: **Extras → Optionen → Charts → Max. Balken im Chart = Unbegrenzt** (der EA braucht das ohnehin). Falls du es ändern musstest: Terminal neu starten.
2. Einen **neuen** Chart öffnen, z. B. EURUSD (nicht den Chart, auf dem DEADBAND läuft).
3. Navigator → Skripte → DEADBAND → **DEADBAND_Daten_Export** auf den Chart ziehen → OK.
   - Das dauert einige Minuten (Historie wird nachgeladen).
   - Am Ende erscheint die Meldung „DEADBAND-Export fertig“.
   - Es exportiert M5 und M15 ab 2019 für Gold, NAS100, Silber, Öl, BTC und (falls vorhanden) einen Dollar-Index, M1 ab 01.06.2025 für Gold und NAS100.
   - Dazu je Symbol die Spezifikation und eine Liste aller Symbole des Servers.
4. Danach **DEADBAND_Kalender_Export** ebenso auf den Chart ziehen → OK (US-Wirtschaftskalender ab 2019).

Alles landet in `MQL5\Files\DEADBAND_Export\`. Kontonummer und Servername stehen in keiner Datei.

## 3. Referenzlauf im Strategietester (Kalibrierung)

Ansicht → Strategietester, Reiter **Einstellungen**:

| Feld | Wert |
|---|---|
| Experte | `DEADBAND_Forschung\DEADBAND_V8_810_Referenz` |
| Symbol / Zeitrahmen | `XAUUSD.x` / `M15` |
| Datum | Benutzerdefiniert, **2022.08.23 bis 2025.06.30** (Stichtag – bitte nicht später) |
| Vorwärtstest | nein |
| Verzögerungen | ohne Verzögerung |
| Modellierung | **Jeder Tick basierend auf realen Ticks** |
| Einzahlung | 10000 USD |
| Hebel | 1:10 |
| Optimierung | deaktiviert |
| Visueller Modus | aus |

Reiter **Eingaben**: Rechtsklick → **Standardwerte laden** (= Auslieferung 8.10; `TesterAuszahlung` und `TesterPruefwerte` sind dabei an).

Start. Danach:
1. Reiter **Backtest** → Rechtsklick → **Bericht → HTML** → speichern als `C:\Trading\Berichte\V8_810_Referenz.html`.
2. Nochmal Rechtsklick → **Bericht → Open XML** → `C:\Trading\Berichte\V8_810_Referenz.xml`.
3. Die Tester-Protokolle holt die Setupdatei selbst.

Hinweis: Ein Testerlauf belegt einen Prozessorkern. Der live laufende EA arbeitet weiter; wenn möglich außerhalb der Hauptzeit 8–12 NY starten.

## 4. Upload-Ordner erstellen

`Export-Setup.cmd` erneut doppelklicken → **[2]** wählen. Auf dem Desktop entsteht `DEADBAND_Upload_<Datum>`:
- je CSV eine ZIP,
- `rest.zip` mit Spezifikationen, Kalender, Protokollen, Berichten und Tester-Logs.

Jede Datei bleibt unter 25 MB.

## 5. Zu GitHub hochladen (Browser)

**Achtung:** Das Repository `agattermann007-droid/claude` ist **öffentlich**. Die Exporte enthalten nur Kursdaten und Symbol-Spezifikationen (keine Kontonummer), wären aber für jeden sichtbar. Empfehlung (wie schon im Bericht 6.10): vorher auf **privat** stellen – Repository → Settings → ganz unten „Change visibility“ → Private. Die Arbeit hier läuft danach unverändert weiter.

1. `https://github.com/agattermann007-droid/claude/upload/claude/upbeat-maxwell-f7pmp0` öffnen (eingeloggt).
2. Alle Dateien aus `DEADBAND_Upload_<Datum>` in das Feld ziehen.
3. Unten **„Create a new branch for this commit“** wählen, Name: `daten-upload` → **Propose changes**. Einen Pull Request musst du nicht anlegen (Seite einfach schließen).
4. Mir kurz Bescheid geben. Ich hole die Dateien per git, entpacke sie lokal (nie ins Repository) und starte die Kalibrierung.

## Was ich danach mache

1. Engine gegen deinen Referenzbericht prüfen: Tradezahl ±5 %, Netto ±10 % (Gate).
2. Gate bestanden → Stufe 1 (drittes Instrument) und Stufe 2 (Familien), alles nur mit Daten bis zum Stichtag 30.06.2025.
3. Gate nicht bestanden → ich melde Abweichung und Ursache und bitte um einzelne Modul-Läufe.
