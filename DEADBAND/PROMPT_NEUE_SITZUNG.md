# Prompt für eine neue Sitzung: DEADBAND weiterentwickeln (GFT, Kontoerkenner und Anpasser)

> In eine neue Claude-Code-Sitzung auf diesem Repository kopieren. Alles ab „Auftrag“ ist der Prompt.

---

## Auftrag

Du entwickelst meinen MetaTrader-5-Expert-Advisor **DEADBAND** weiter. Er handelt ein **Goat Funded Trader (GFT) Instant Premium**-Konto (10 000 $). Bei GFT bleibe ich. Alle Entscheidungen triffst du selbst. Frag nur, wenn du wirklich blockiert bist. Antworte mir auf Deutsch, kurz und ehrlich.

### Mein Ziel (Rangfolge)

1. **Keine Pleiten.** Ein Konto darf nie eine GFT-Regel brechen. Das ist eine harte Grenze, kein Abwägungspunkt.
2. **Mehr Auszahlungen pro Jahr.**
3. **Mehr Gewinn je Auszahlung.**
4. **Kürzere Zeit bis zur Auszahlung** (Tage je Zyklus).

Ein Vorschlag ist nur besser, wenn er 2–4 verbessert, ohne 1 zu verletzen. Das muss sowohl im Auswahl- als auch im Prüfzeitraum gelten.

### GFT Instant Premium – Regeln

So wie sie im EA und im Replikat stehen; im Zweifel den Code als Quelle nehmen.

- **Boden:** 6 % unter dem Equity-Höchststand, nachlaufend. Nach einer Auszahlung neu ab dem Saldo.
- **Floating-Verlust:** offener Verlust höchstens 1 % (strenge Lesart: über alle Positionen).
- **Tagesverlust:** höchstens 3 %. Der Tag beginnt um 17:00 NY.
- **Gültiger Tag:** ≥ 0,5 % realisiert (EA: 50,50 $ + Reserve). Für eine Auszahlung braucht es 5 gültige Tage in einem Zyklus von mindestens 10 Tagen.
- **Auszahlung:** mindestens 105 $ (= 131,25 $ Gewinn bei 80 % Anteil). Die ersten beiden Auszahlungen sind auf 6 % gedeckelt.
- **Haltedauer:** Gewinne aus Trades unter 120 s werden gestrichen. Der EA setzt das Ziel erst nach 130 s.
- **Hedging** (Gegenpositionen im selben Symbol) ist verboten.
- **Server:** Serverzeit = NY + 7 h. Symbole: `XAUUSD.x` und `NAS100.x`.

### Ausgangslage im Repo

Lies zuerst die Dateien, dann die Köpfe der EAs.

- **`DEADBAND/DEADBAND_V8.mq5`** – Build 8.00, aktueller Stand, **noch nie kompiliert**. Er enthält:
  - 10 Fade-Module (Fehlausbruch einer Sitzungs-Range) mit Portfolio-Wächter
  - RSI21, NAS-Noise
  - Spike-Fade S0830 (7.10)
  - Larry-Williams-Ausbruch NAS (Modul LW, 0,5 %, nur ab 4 % Puffer)
  - Gold-Asien-Halten (Modul XA)
  - Pufferkurve 3,5 / 1,25 / 0,1
  - Probability Grid, Schutz gültiger Tage, Abschluss-Ernte, Firmenprofil
- **`DEADBAND/DEADBAND_V7.mq5`** – 7.10. **`DEADBAND/rollback_7.00/`** – Stand 7.00.
- Berichte:
  - `DEADBAND/DEADBAND_V8_Bericht.md` – Methode, alle getesteten YouTube-Strategien, Zahlen, Grenzen. **Pflichtlektüre.**
  - `DEADBAND/DEADBAND_V7_710_Bericht.md`
  - `DEADBAND/DEADBAND_V7_Ideen_Recherche.md`
- **`DEADBAND/Replikat_v6/`** – Python/numba-Replikat:
  - `eng6.py`: Kontomotor mit allen GFT-Regeln; 32 generische Ströme, Strom-Spalte `minbuf`.
  - `evl6.py`: rollierende 10k-Konten, Störungen, Pleiten nach Art.
  - `n8sig.py`: 13 Strategie-Generatoren.
  - `n8_scan.py` / `n8_robust.py`: Raster mit Auswahl, Prüfung und Fremddaten.
  - `n8_konto.py`: Strom allein.
  - `n8_port.py`: Portfolios.
  - `n8_ext.py`: Fremddaten-Konto.
  - `y7_konto.py`: Fades mit Wächter.
- **Kursdaten liegen nicht im Repo** und müssen neu aufgebaut werden:
  1. Fremddaten nach `DEADBAND/extdata/DATEN_BERICHT.md` und den Skripten dort (GitHub-Quellen; Dukascopy ist gesperrt). Speicher sparen: höchstens eine Tick-Umwandlung gleichzeitig.
  2. `DEADBAND_EXT=<extdata>` setzen.
  3. `python y7_data.py` baut `../data/XAUUSD.x_M5.csv` und `NAS100.x_M5.csv` (GFT-Ersatz ab 2022).
- **Referenz im Replikat** (zum Prüfen, ob der Aufbau stimmt):
  - 7.10: 11,00 Auszahlungen/Jahr, 2008 $ netto, 0 Pleiten.
  - 8.00: 13,37 Auszahlungen/Jahr, 2771 $ netto, 0 Pleiten; Fremddaten 2006–21: 3,66 Auszahlungen/Jahr, 0 Pleiten.

### Arbeitsweise (verbindlich)

- **Testzeitraum ab 2022.**
  - Auswahl auf 2022–23, Prüfung auf 2024–25.
  - Gold zusätzlich 2026 als Zukunftstest.
  - Fremddaten 2005–21 als Gegenprobe. Wo sie widersprechen, sag es offen.
  - Zeige immer alle drei.
- **Neue Strategien** (YouTube, Paper, eigene Ideen) **nicht einfach dazubauen.** Reihenfolge:
  1. Allein im Konto-Replikat bewerten, alte Module aus.
  2. Die GFT-Handhabung auf die Strategie anpassen: Risiko, Puffer-Schwelle, Ziel, Zeiten, Verlustgrenzen.
  3. Erst dann mit dem Rest kombinieren und Konflikte prüfen: Hedging, Budget, Floating-Grenze, dieselbe Idee im selben Symbol.
- **Ich muss nicht beim alten Grundkonzept bleiben.** Wenn etwas anderes besser ist, darf der Fade-Kern kleiner werden oder wegfallen.
- **Weiter auf YouTube suchen.** Diese Strategien sind schon geprüft und verworfen (siehe Bericht V8), nicht wiederholen:
  - ORB 5 und 15 min, auch mit Mittelpunkt-Filter
  - 9:30-Kerze
  - Silver Bullet, Judas Swing, Turtle Soup
  - Gold-Initial-Balance mit Rücklauf
  - Magic Hours
  - Gao-Momentum
  - EMA-/VWAP-Pullback
  - Vortagesausbruch und -sweep
  - Bollinger
  - Turn of Month
  - Gap-Fade, VWAP-Fade, Wochen-Eröffnung, Makro-Tag-Filter, Vola-Perzentil

  Robust, aber noch nicht übernommen: Connors RSI(2) und NAS-Eröffnungsmomentum. YouTube und die meisten Strategie-Seiten sind im Netz gesperrt. Arbeite über Such-Snippets und GitHub-READMEs, gern mit einem Recherche-Agenten im Hintergrund.
- **Gegen Überanpassung:**
  - Wenige, vorher festgelegte Raster.
  - Plateaus statt Spitzenwerte.
  - Gepaarte Vergleiche (gleiche Starts und Störungen).
  - Kostenstress (Schlupf).
  - Jahre einzeln ansehen.
- **Was der EA tut, muss das Replikat genauso rechnen.** Neue Module werden Zeile für Zeile aus dem Generator übertragen. Im Kopf des EA steht, welche Replikat-Funktion dazugehört.

### Neu: Kontoerkenner und Anpasser

Der EA erkennt heute schon das Konto:
- Startsaldo aus den Einzahlungen
- Equity-Spitze und Boden aus der Historie
- Zyklusbeginn, gültige Tage, Auszahlungen
- Overrides wie `StartBalanceOverride`, `FloorOverride`, `CycleStartOverride`

Die Einstellungen sind aber für jeden Kontozustand gleich, abgesehen von Pufferkurve, `BelowStartMult` und der LW-Schwelle. Baue einen **Kontoerkenner mit Anpasser**: Der EA bestimmt laufend, in welchem Zustand das Konto ist, und schaltet je Zustand einen eigenen, im Replikat geprüften Parametersatz.

**1. Zustände erkennen** (Vorschlag; die Grenzen selbst festlegen und im Replikat bestimmen):

| Zustand | Erkennung | Beispiel-Anpassung (prüfen, nicht übernehmen) |
|---|---|---|
| Frisch (Start, Puffer ≈ 6 %) | Saldo ≈ Start, keine gültigen Tage | normale Größe, alle Ströme |
| Im Gewinn, Zyklus läuft | Saldo > Start, Puffer hoch | riskantere Ströme (LW) erlaubt, Ziel gültige Tage |
| Kurz vor Reife | ≥ 4 gültige Tage oder Mindestgewinn fast erreicht | nur hochsichere Ströme, kleinere Größe, Ernte-Modus |
| Reif / Auszahlung beantragt | wie heute (kMode 1/2) | keine Einstiege |
| Leichter Drawdown | Puffer 3,5–5 %, Equity < Start | Erholungsmodus: nur Ströme mit hoher Trefferquote (Fades) |
| Tiefer Drawdown / nahe Boden | Puffer < 2–2,5 % | Schutzmodus: Mini-Größe oder Pause, Pflicht-Push |
| Nach Auszahlung | Saldo auf Start zurückgesetzt, Boden neu | Neustart-Satz |
| Verlustserie / schlechtes Regime | Serien-Stopp, Portfolio-Wächter, Volatilität | Größe herunter, einzelne Ströme aus |
| EA mitten im Konto gestartet / Historie unklar | Rekonstruktion unsicher (peakOk false) | vorsichtiger Satz, bis sicher |
| Andere Kontogröße / andere Firma | Startsaldo ≠ 10k, FirmaProfil 1 | alles relativ zum Start skalieren |

**2. Anpassen:** Je Zustand einen Parametersatz:
- Risiko je Strom
- welche Ströme aktiv sind
- Puffer-Schwellen und Pufferkurve
- Ziele
- Ernte und Schutz gültiger Tage

Dazu **Hysterese**, damit der Zustand nicht hin und her springt, und Übergänge ins Journal plus Push.

**3. Im Replikat prüfen:**
- `eng6.py` um die Zustandsmaschine erweitern, als neue Parameter.
- Zuerst messen, welche Zustände wie oft vorkommen und wo Pleiten und verlorene Auszahlungen entstehen.
- Dann je Zustand optimieren: Auswahl 2022–23, Prüfung 2024–25, Fremddaten.
- Vergleichen gegen 8.00 ohne Anpasser.

**4. Im EA:**
- Panel-Zeile „Kontozustand: … (seit …), Satz: …“.
- Eingaben zum Abschalten: `AnpasserAktiv`, plus Zustand erzwingen.
- Beim Start eine Meldung, welcher Zustand erkannt wurde und warum.
- Alles muss im Strategietester laufen und darf live keine Sonderfälle haben.

### Ergebnis, das ich am Ende erwarte

1. **Neue EA-Version** (z. B. `DEADBAND_V8.mq5` als Build 8.10 oder neue Datei V9):
   - Kopfblock mit Zahlen, Quelle und Rückfall-Einstellungen (Anpasser aus = 8.00).
   - Den alten Stand als Rollback behalten.
2. **Bericht** `DEADBAND_V8x_Bericht.md`:
   - Tabelle alt gegen neu: Auszahlungen pro Jahr, netto, Ø Auszahlung, Tage je Zyklus, gültige Tage, Pleiten nach Art. Jeweils gesamt, 2022–23, 2024–25 und Fremddaten.
   - Verworfene Ideen mit Grund.
   - YouTube-Quellen als Links.
   - Ehrliche Grenzen.
   - Prüfplan für den MT5-Tester.
3. **Replikat-Skripte und Ergebnis-JSONs** im Repo. Große Dateien gzip.
4. Commit und Push auf den Branch, den die Sitzung vorgibt. **Keinen Pull Request ohne meine Bitte.**

### Ehrlichkeit

- Sag klar, dass du den EA nicht kompilieren kannst (kein MetaEditor). Prüfe Klammern, Definitionen und Eingaben selbst. Ich teste im MT5-Tester.
- Das Replikat (eng6) ist ein Näherungsmotor auf Stand 6.10. Grid, Teilgewinn, Schutz je Modul und Regime-Größe sind nur angenähert. Nenne Unterschiede statt absoluter Versprechen.
- Wenn etwas nicht besser wird, sag das. Lieber kein Update als ein schlechteres.
- Den Branch `claude/ecstatic-johnson-mlf4v8` nicht mergen und nicht übernehmen; die Sicherheitsprüfung hat das gesperrt.

### Technische Hinweise aus der letzten Sitzung

- **Kein `pkill -f …`:** Das trifft die eigene Shell (Exit 144).
- **`pgrep -f` mit Text aus der eigenen Kommandozeile findet sich selbst.** Lange Läufe besser über ein Startskript mit `nohup` und eine Marke „FERTIG“ in der Logdatei.
- Ein Konto-Lauf (eng6, 250/500 Tage, 8 Störungen) dauert 1–2 min, mit Hälften-Teilung etwa 5 min. 4 Kerne.
- Nur GitHub ist erreichbar. Yahoo, Stooq, Binance, Hugging Face und Histdata sind gesperrt. Weitere Märkte als XAU und NAS für 2022+ waren nicht zu bekommen.
