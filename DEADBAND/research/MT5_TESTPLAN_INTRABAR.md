# MT5-Testplan Stufe 3 – Einstieg innerhalb der Kerze

**Frage (Auftrag Stufe 3):** Ist der Einstieg des H1-Ausbruchs beim ersten Durchstoß der Kante mehr wert als nach dem bestätigten M15-Schluss?

Gemäß **E2-i** wird das H1-Modul **isoliert** getestet: `DbAktiv = true`, alle anderen Module aus. Der Zeitpunkt folgt immer aus der Handelslogik, nie aus Zufall.

**EA:** `Experts\DEADBAND_Forschung\DEADBAND_V8_Intrabar`
- Herkunft: `research/patch_intrabar.mq5`, Änderungen in `research/patch_intrabar.diff`.
- Das Export-Setup legt ihn ab und kompiliert ihn (`DATEN_EXPORT.md`, Schritt 1).
- `EntryMode = 0` ist handelsidentisch zu V8.10. Den laufenden EA ersetzt er nicht.

---

## 1. Gemeinsame Einstellungen (Reiter „Einstellungen“)

| Feld | Wert |
|---|---|
| Experte | `DEADBAND_Forschung\DEADBAND_V8_Intrabar` |
| Symbol / Zeitrahmen | `XAUUSD.x` / `M15` (der EA handelt Gold und NAS von einem Chart aus) |
| Datum | Benutzerdefiniert, **2022.08.23 bis heute** (Datenende) |
| Vorwärtstest | nein |
| Verzögerungen | ohne Verzögerung |
| Modellierung | **Jeder Tick basierend auf realen Ticks** |
| Einzahlung / Hebel | 10000 USD / 1:10 |
| Optimierung / Visueller Modus | deaktiviert / aus |

## 2. Gemeinsame Eingaben (Reiter „Eingaben“)

1. Rechtsklick → **Standardwerte laden**.
2. Dann diese Werte ändern, sonst nichts:

| Eingabe | Wert | Zweck |
|---|---|---|
| `DbAktiv` | **true** | H1-Ausbruch handelt |
| `R21Aktiv` | false | aus |
| `NzAktiv` | false | aus |
| `FadeAktiv` | false | aus (Fades rechnen nur virtuell) |
| `SpikeAktiv` | false | aus |
| `LwAktiv` | false | aus |
| `AsiaAktiv` | false | aus |
| `TdAktiv` | false | aus |

3. Rechtsklick → **Speichern** als `Intrabar_Basis.set`. Für jeden Lauf diese Datei laden und nur die Zeile aus Abschnitt 3 ändern.

`TesterAuszahlung` bleibt an (Standard), damit Auszahlungen und neue Zyklen wie live laufen.

## 3. Läufe (eine Zeile = ein Lauf)

| Nr. | Name | `EntryMode` | `IbSpreadX` | `IbHalteSek` | Bericht |
|---|---|---|---|---|---|
| 1 | A Schluss | 0 | – | – | `Intrabar_A` |
| 2 | B X=1 | 1 | 1 | – | `Intrabar_B1` |
| 3 | B X=2 | 1 | 2 | – | `Intrabar_B2` |
| 4 | B X=3 | 1 | 3 | – | `Intrabar_B3` |
| 5 | C T=30 | 2 | 1 | 30 | `Intrabar_C30` |
| 6 | C T=120 | 2 | 1 | 120 | `Intrabar_C120` |
| 7 | C T=300 | 2 | 1 | 300 | `Intrabar_C300` |
| 8 | D 7,5 min | 3 | – | – | `Intrabar_D` |

**Zu den Varianten:**
- **C** nutzt X = 1 Spread, also die Kante von B1, plus Haltezeit. Ein Vergleich C gegen B1 isoliert so die Haltezeit.
- **D** prüft einmal je Kerze ab 450 s (`IbTeilSek`, Standard).

**Nach jedem Lauf:**
1. Reiter **Backtest** → Rechtsklick → **Bericht → HTML**, speichern als `C:\Trading\Berichte\<Bericht>.html`.
2. Ebenso **Bericht → Open XML**, speichern als `C:\Trading\Berichte\<Bericht>.xml`.

**Optionale Kontrolle (empfohlen):**
- Lauf 1 noch einmal mit dem unveränderten `DEADBAND_V8_810_Referenz` und derselben `Intrabar_Basis.set`.
- Ohne die vier `EntryMode`/`Ib…`-Zeilen meldet MT5 die nur als „unbekannt“, das ist harmlos.
- Speichern als `Intrabar_A_Referenz`.
- Beide Berichte müssen **identisch** sein. Sonst ist der Patch nicht handelsidentisch, und ich suche den Fehler, bevor ich etwas auswerte.

**Rechenzeit:**
- Reale Ticks über gut 4 Jahre mit 1-s-Timer: je Lauf grob 1–4 h [Schätzung, ungeprüft].
- Die Läufe sind unabhängig. Wenn der Server genug Kerne hat, im Tester mehrere Agenten zulassen.
- Der live laufende EA arbeitet weiter; wenn möglich außerhalb von 8–12 NY starten.

## 4. Abgeben

`Export-Setup.cmd` doppelklicken → **[2]**:
- Die ZIP enthält `C:\Trading\Berichte` und die Tester-Protokolle der letzten 14 Tage.
- Die Protokolle tragen je Einstieg die Zeile „Intrabar-Signal Modus … Kante … Bid … Spread … s nach Kerzenbeginn“.

Danach hochladen wie in `DATEN_EXPORT.md`, Schritt 5, und mir kurz Bescheid geben.

## 5. Was im Patch genau passiert

| | A (0) | B (1) | C (2) | D (3) |
|---|---|---|---|---|
| Zeitpunkt | erster Tick der neuen M15-Kerze | jeder Tick und jede Timer-Sekunde | wie B | einmal je Kerze, erster Tick/Timer ab 450 s |
| Auslöser Long (Short spiegelbildlich) | Schluss > H1-Hoch | Bid ≥ H1-Hoch + X × Spread | wie B, T s ununterbrochen | Bid > H1-Hoch und (Bid − Tief) / Spanne bisher ≥ `ClsMin` |
| EMA50 (D1, Vortag) | Schluss gegen EMA | Bid gegen EMA | wie B | wie B |
| VWAP (abgeschlossene Kerzen des Prop-Tags) | Schluss | Bid | wie B | wie B |
| RSI / MACD | abgeschlossene Kerze | laufende Kerze (Schift 0) | wie B | wie B |
| Kerzenqualität | ja | nicht anwendbar | nicht anwendbar | bisherige Spanne |
| Volumen | abgeschlossene Kerze ≥ Schnitt | nicht anwendbar (Kerze unvollständig) | nicht anwendbar | zeitanteilig: bisher × 900 s / verstrichene s ≥ Schnitt |
| Session, Tageslimits, News, Wochenende | wie 8.10 (Zeit = Kerzenbeginn) | wie 8.10 (Zeit = jetzt) | wie B | wie B |
| Stop, Größe, Ausstieg, Order | `DbOrder` = unveränderter Order-Teil aus 8.10 | dasselbe | dasselbe | dasselbe |

**Eine Position je Symbol, Tageslimit 1 Trade:** Nach einem Intrabar-Einstieg gibt es in derselben Kerze und am selben Tag keinen zweiten.

## 6. Auswertung (mache ich, PLAN 7)

**Je Variante:**
- Trades, Netto, PF je Kalenderjahr,
- Ø Einstiegspreis gegen A in R (gleiche Signale, gleiche Richtung),
- Fehlausbruch-Anteil: Stop ohne vorher +1 R, aus den M1-/M5-Daten zwischen Ein- und Ausstieg,
- Tagesreihen durch den GFT-Bootstrap (Blöcke 1/5/20, Netto pro Monat, bpp),
- B und C zusätzlich mit +1 Spread Schlupf je Einstieg.

**Walk-Forward:**
- Zuerst werte ich nur Trades bis zum Stichtag 30.06.2025 aus.
- Die Trades danach öffne ich erst im Blindlauf (Stufe 4), zusammen mit der Baseline.
- Eine Variante besteht nur nach allen sechs Kriterien (PLAN 3.4).
- Eine bestandene Variante führt **nicht** automatisch zum Einbau. Sie würde zuerst die Frage aus E2 klären: ob der H1-Ausbruch überhaupt wieder eingeschaltet werden soll (dann Stufe 4 mit Baseline E1-B).
