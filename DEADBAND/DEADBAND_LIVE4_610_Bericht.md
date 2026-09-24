# DEADBAND LIVE 4 – Build 6.10 (Echtbetrieb)

Bericht vom 24.09.2026 · GFT Instant Premium 10k (Konto ab 02.09.2026)

## 1. Kurzfassung

Build 6.10 ist die Echtbetrieb-Version. Die Handelslogik ist die von 6.00 (10 Fehlausbruch-Fades mit
Regime-Wächter, RSI21, NAS-Noise, DEADBAND-Einstiege aus). Neu sind drei Dinge:

1. **Abschluss-Ernte für alle Module.** Fehlen nur noch höchstens 3 gültige Tage bis zur Auszahlung, realisiert
   der EA offenen Gewinn (Position hat mindestens 0,3 R Vorlauf erreicht) so weit, dass der Tag die 0,5 %
   schafft. Bis 6.00 galt das nur für DEADBAND – und das ist aus. Die Engpass-Analyse zeigt, warum das
   wirkt: Nur 31 % der Handelstage waren gültige Tage, und in der Hälfte der Zyklen kam die Auszahlung erst,
   als der letzte gültige Tag fehlte.
2. **Genau wie getestet:** Das Fade-Ziel wird erst ab der Kerze nach der Einstiegskerze gesetzt (so rechnet
   das Replikat), die Kommission des Regime-Wächters wird als Hin- und Rückweg aus der Historie gemessen.
   Die Voreinstellungen des EA sind das Echtbetrieb-Set.
3. **Kontoerkennung beim Laden** (Abschnitt 4).

Replikat auf den GFT-Kursen 2022–2026 (16 Störungen, rollierend 1/2/3 Jahre, strenge Regel-Lesart,
Auszahlung ab 3 % = 300 $; 6.10 mit gültigem Tag ab 50,50 $ wie im EA):

| Kennzahl | 5.10 | 6.00 Ertrag | **6.10 Ertrag** (Echtbetrieb) | 6.10 Sicher |
|---|---:|---:|---:|---:|
| Auszahlungen je Jahr | 5,51 | 7,20 | **7,51** | 5,86 |
| Auszahlung im Mittel | 361 $ | 386 $ | 368 $ | 353 $ |
| Busts je Jahr | 0,17 | 0,00 | **0,00** | 0,00 |
| Netto je Jahr | 1517 $ | 2158 $ | 2143 $ | 1603 $ |
| Serien ≥ 5 Verluste je Jahr | 11,8 | 2,26 | **1,87** | 0,62 |
| Serien ≥ 6 Verluste je Jahr | 6,15 | 0,49 | **0,36** | 0,07 |
| längste Serie: Mittel / schlimmste | 9,4 / 13 | 6,4 / 10 | **5,9 / 10** | 5,0 / 10 |
| Trefferquote | 45 % | 61 % | 63 % | 68 % |

Nach Startjahr (1-Jahres-Konten, 6.10 Ertrag): **2022: 10,1 Auszahlungen**, 2023: 8,6, 2024: 4,9, 2025: 7,5
– Busts praktisch 0 (höchstens 0,001 je Jahr). Streuung über die 16 Störungen: 7,51 ± 0,49 Auszahlungen
(Standardfehler 0,12), Busts 0. Die 0,50-$-Reserve für gültige Tage kostet 0,05 Auszahlungen je Jahr, 2 $
hätten 0,21 gekostet.

Fremddaten 2006–2021 (anderes Regime, 4 Störungen): 6.10 Ertrag 2,02 Auszahlungen / 0,40 Busts / 503 $
je Jahr (6.00: 2,00 / 0,43 / 524 $); Sicher 0,56 / 0,33 / 104 $.

**Die Anforderungen bleiben ehrlich bewertet wie in 6.00:** 10 Auszahlungen je Jahr erreicht nur das
Startjahr 2022; im Mittel sind es 7,5. Busts 0 auf 2022–26, nicht auf 2006–21. Serien über 5 Verluste:
selten (0,36 je Jahr mit ≥ 6), aber nicht ausgeschlossen.

## 2. Was gesucht und geprüft wurde

### 2.1 Engpass-Analyse

Wann wird eine Auszahlung reif? Es müssen 5 gültige Tage (≥ 0,5 % realisiert), 10 Zyklustage und
300 $ Gewinn zusammenkommen. Im Replikat (6.00, alle Zyklen 2022–26):

| | zuletzt erfüllt: gültige Tage | zuletzt erfüllt: Mindestgewinn | Handelstage bis 5 gültige Tage | bis 300 $ | Anteil gültiger Tage |
|---|---:|---:|---:|---:|---:|
| Sicher | 37 % | 63 % | 35,7 | 46,3 | 32 % |
| Ertrag | 50 % | 49 % | 29,6 | 36,8 | 31 % |

Ein Fade-Gewinn liegt bei 0,75 % Risiko und Ziel Range-Mitte oft knapp unter 0,5 % – der Tag zählt dann
nicht. Hier setzt die Abschluss-Ernte an.

### 2.2 Screening (GFT 2022–26, 8 Störungen; Gegenprobe Fremddaten 2006–21, 4 Störungen)

| Variante | GFT: Ausz. / Busts / Netto / Serien ≥ 5 | Fremd: Ausz. / Busts / Netto | Urteil |
|---|---|---|---|
| 6.00 Ertrag (Basis) | 7,03 / 0,00 / 2128 $ / 2,25 | 2,00 / 0,43 / 524 $ | – |
| + Abschluss-Ernte alle Module, 2 fehlen, 0,5 R | 7,19 / 0,00 / 2042 $ / 1,96 | – | schwächer als die nächste |
| **+ Abschluss-Ernte alle Module, 3 fehlen, 0,3 R** | **7,43 / 0,00 / 2110 $ / 1,82** | **2,05 / 0,40 / 515 $** | **übernommen** |
| + Abschluss-Ernte immer, 0,3 R | 7,47 / 0,00 / 2080 $ / 1,42 | 1,83 / 0,32 / 447 $ | weniger Ertrag im alten Regime |
| Wächter PF > 1,1 | 7,69 / 0,00 / 2348 $ / 2,73 | 1,98 / 0,45 / 523 $ | verworfen: längere Serien (bis 13), mehr Busts im alten Regime |
| Wächter PF > 1,3 | 6,94 / 0,00 / 2123 $ / 1,83 | – | verworfen |
| Fade-Risiko 0,65 % | 6,91 / 0,00 / 2109 $ / 2,06 | – | verworfen |
| Serien-Stopp 4 | 7,00 / 0,00 / 2104 $ / 2,48 | – | verworfen (Serien ≥ 6 verdoppelt) |
| RSI21 0,6 % / Noise 0,45 % | 7,16 / 0,01 / 2187 $ / 2,25 | – | verworfen (Busts) |
| 6.00 Sicher (Basis) | 5,80 / 0,00 / 1575 $ / 0,70 | 0,56 / 0,33 / 104 $ | – |
| Sicher + Abschluss-Ernte (3 fehlen, 0,3 R) | 5,59 / 0,00 / 1465 $ / 0,61 | 0,56 / 0,33 / 102 $ | verworfen: bei nur Fades weniger Auszahlungen |

Die Abschluss-Ernte hilft in „Ertrag“, weil RSI21- und Noise-Positionen oft genug Buchgewinn tragen, um
den Tag gültig zu machen. In „Sicher“ (nur Fades) schneidet sie Gewinner ab, ohne Tage zu retten.

## 3. Was 6.10 ändert

| Eingabe / Verhalten | 6.00 | **6.10** | Zweck |
|---|---:|---:|---|
| `AbschlussLetzte` | 2 | **3** | Ernte, sobald höchstens 3 gültige Tage fehlen |
| `AbschlussMinR` | 0,5 | **0,3** | Mindest-Vorlauf der Position in R |
| `AbschlussModule` (neu) | (nur DEADBAND) | **15 = alle** | 1 DEADBAND, 2 RSI21, 4 Noise, 8 Fades |
| Vorlauf (MFE) je Noise-/Fade-Position | – | neu | wie im Replikat; nach Neustart aus den M5-Kerzen seit Einstieg |
| Ernte zählt netto | brutto | netto | Kommission wird dem Tag angerechnet, der Tag wird sicher gültig |
| Fade-Ziel | ab 130 s | **ab der Kerze nach der Einstiegskerze** (und ≥ 130 s) | wie im getesteten Replikat |
| Kommission im Wächter | 2 × Einstieg | Hin- und Rückweg aus der Historie | wie gebucht |

Preset **Sicher** (`DEADBAND_LIVE4_610_Sicher.set`): wie 6.00 Sicher, Abschluss-Ernte aus.

## 4. Kontoerkennung beim Laden

Ziel: Sobald der EA geladen ist, kennt er genau den Kontozustand, mit dem GFT rechnet. Das gilt auch nach einem
Neustart mitten im Zyklus, mitten am Tag, mit offenen Positionen oder nach einer Auszahlung. Sub-Agenten haben die
Kontoerkennung in drei Durchgängen Zeile für Zeile geprüft; die Befunde aller Durchgänge sind umgesetzt:

| Bereich | bis 6.00 | 6.10 |
|---|---|---|
| **Vollständigkeit der Historie** | nur „nicht leer“ geprüft | Start erst, wenn die Summe aller Buchungen den Saldo ergibt (höchstens 3 min ab Verbindung warten, sonst Warnung und vorläufige Spitze mit Größe × 0,6; sobald die Historie stimmt, wird die Spitze vollständig neu bestimmt). Liegt die Einzahlung außerhalb des 400-Tage-Fensters, wird einmal die ganze Historie geladen; eine bekannte Einzahlung bleibt auch im Dauerlauf im Fenster. |
| **Auszahlung erkennen** | jede Saldo-Abbuchung ab 50 $ | nur, wenn der Saldo danach auf den Startsaldo fällt (bzw. Startsaldo + Rest über dem 6-%-Deckel) oder der Buchungskommentar zu `AuszahlungKennung` passt. Abbuchungen binnen 1 h ohne Trade dazwischen zählen zusammen (Auszahlung in Teilen). Korrekturen, gestrichene Gewinne und Gebühren setzen Zyklus und Boden **nicht** zurück (sonst läge der Boden des EA unter dem von GFT). Unklare Abbuchungen meldet der EA per Push. Von Hand: `AuszahlungZeiten` (ist eine Auszahlung, z. B. Teilauszahlung), `KeineAuszahlung` (ist keine – gilt für die ganze Gruppe und hat Vorrang). |
| Buchungen vor dem ersten Trade | Plus summiert, Minus als Auszahlung | netto = Startsaldo |
| **Gültige Tage** | Positionsergebnis am Ausstiegstag | zwei Lesarten (Ausstiegstag / jeder Deal an seinem Tag inkl. Kommissions-Buchungen); gültig nur, wenn **beide** ≥ 0,5 % + 0,50 $ Rundungsreserve (`ValidDayReserveUSD`). Gebühren (DEAL_FEE) und Abbuchungen, die keine Auszahlung sind, zählen mit. Ein Einstieg, dessen Kommission einen heute schon gültigen Tag wieder ungültig machte, wird ausgelassen (Einstiege derselben Sekunden zählen zusammen). |
| 10-Tage-Frist | 10 Prop-Tage (ab 9 Tagen + 1 min möglich) | zusätzlich volle 10 × 24 h seit dem ersten Trade des Zyklus |
| **Tagesreferenz 17:00 NY** | Equity beim ersten Tick nach dem Tageswechsel (bei Gold/NAS erst 18:00 NY, nach der Eröffnungslücke) oder nach Neustart nur der Saldo | obere Schranke des Buchgewinns um 17:00 NY aus den Kursen der letzten 2 Minuten (M1) und der Deal-Historie; auch nach einem Neustart. Nur synchrone Kurse zählen als sicher (eine Lücke nach einer Offline-Zeit liefert sonst einen alten Kurs). Bis dahin gilt vorläufig der Wert aus den vorhandenen Kursen bzw. der Equity beim Tageswechsel (die Bremsen messen nie nur vom Saldo), keine neuen Einstiege (Ernten und Ausstiege laufen weiter), neuer Versuch jede Minute, Push nach 15 min; die Sperre übersteht einen Neustart. Abzüge während des Tages zählen wie bei GFT als Tagesverlust. |
| **Equity-Spitze (Boden)** | aus der Historie beim Start, dann nur live abgetastet | beim Start enger (nur Kerzen, in denen die Position offen war, mit offenem Volumen; weiterhin nie zu tief); **jede Minute aus den M5-Hochs nachgeholt**, nach Verbindungsabbrüchen über die ganze Lücke, bis die Kurse synchron sind; neu gerechnet, sobald die Historie wächst – immer direkt nach dem Laden einer Historie, die den Saldo erklärt (sonst zählte ein eben geschlossener Trade doppelt). Gesichert wird nur mit geprüfter Historie, täglich aufgefrischt; eine gesicherte Spitze aus einem früheren Zyklus gilt nie. |
| Unvollständige Kurse für die Spitze | nur „keine Kerzen“ erkannt | auch Lücken am Anfang/Ende und nicht synchrone Kurse erkannt → Größe × 0,6, bis nachgeholt |
| **Boden-Sperre** | nur kleinere Größe nahe am Boden | vor jedem Einstieg (alle Module, auch Wiederaufnahme): Equity, wenn **alle** offenen Positionen an ihrem Stop schließen (auch Buchgewinn, der bis zum Stop zurückgegeben werden kann; ohne Stop mindestens 1 % ab dem aktuellen Kurs; ein schon überschrittener Stop bringt keine Luft), minus neues Risiko muss 0,2 % über dem Boden bleiben |
| **Kontowechsel** im selben Terminal | alter Zustand blieb im Speicher | Zustand wird beim Laden und bei Login-Wechsel vollständig zurückgesetzt (auch Wochenend-Vormerkungen, Tageszähler, Kommissions-Cache) |
| Tagesbremse vor dem Laden der Kontodaten | nur Floating-Bremse | auch 2,4-%-Tagesbremse aus der gesicherten Tagesreferenz |
| Auszahlung beantragt, noch nicht gebucht | EA handelte wieder, wenn die Reife verloren ging | `AuszahlungAngefordertAm` hält das Konto flach, bis die Auszahlung gebucht ist; die Erinnerung sagt dann „beantragt, noch nicht gebucht“ statt „jetzt beantragen“ |
| **Auszahlung verarbeiten** | im selben Durchlauf, auch wenn MT5 den Deal vor dem neuen Saldo zeigte (neue Spitze beim alten Saldo → Boden über der Equity → ganzer Zyklus ohne Einstiege); beim Neuladen an anderer Stelle konnte sie übersehen werden | erst, wenn die frisch geladene Historie den Saldo erklärt und Auszahlung + Saldo 5 s unverändert sind; geprüft gegen die zuletzt verarbeitete Auszahlung, egal wo die Historie geladen wurde. Bis dahin keine Einstiege, keine Sicherung der Spitze. Erklärt die Historie den Saldo nach 3 min noch nicht: trotzdem, mit vorläufiger Spitze und Push |
| Tag der Auszahlung | sofort wieder Einstiege | keine neuen Einstiege bis 17:00 NY |
| Vormerkungen (Wochenende) aus dem alten Zyklus | konnten nach einer Auszahlung wieder öffnen | werden verworfen |
| `CycleStartOverride` / `FloorOverride` | galten auch nach späteren Auszahlungen | gelten nur im laufenden Zyklus; `FloorOverride` nur zusammen mit `FloorOverrideZeit` (Zeitpunkt der Dashboard-Ablesung), sonst startet der EA nicht |
| NY-Versatz | automatisch aus der PC-Uhr | fest 7 h (`AutoNYOffset=false`); Abweichung der PC-Uhr nur als Hinweis |
| Ernte-Schätzung | überschrieb den realisierten Tagesgewinn (konnte eine falsche Reife auslösen) | getrennt geführt, Reife nur aus bestätigten Deals |
| Vorlauf offener RSI21-Positionen nach Neustart | 0 | aus den M5-Kerzen seit dem Einstieg |
| Inaktivität (30 Tage) | nach Kurszeit (am Wochenende eingefroren) | nach Serverzeit |
| Kredit (`ACCOUNT_CREDIT`) | als Saldo gezählt | ausgeschlossen, Warnung |

**Kontobericht:** Beim Laden (und nach Verbindungsaufbau oder Auszahlung) schreibt der EA den vollständigen Zustand
ins Journal und nach `MQL5\Files\DEADBAND4_Konto_<Login>.txt`:
- Startsaldo mit Herkunft, Auszahlungen und Deckel,
- Gewinn und Mindestgewinn, Zyklusbeginn und Zyklustag,
- **jeder Tag des Zyklus mit Betrag und Gültigkeit**,
- Equity-Spitze, Boden und Puffer, Tagesstart und Referenz,
- Buchverlust, offenes Risiko und alle offenen Positionen mit Modul,
- Serien-Stand und Modus.

Diese Werte bitte beim ersten Start mit dem GFT-Dashboard vergleichen.

Was MT5 allein nicht wissen kann, lässt sich per Eingabe festlegen:
- `StartBalanceOverride`,
- `FloorOverride` + `FloorOverrideZeit`,
- `CycleStartOverride`,
- `AuszahlungKennung` / `KeineAuszahlung` / `AuszahlungZeiten`,
- `AuszahlungAngefordertAm`.

## 5. Echtbetrieb: Dateien

- `DEADBAND_LIVE4.mq5`: Die Voreinstellungen **sind** das Echtbetrieb-Set („Ertrag“). Ohne Preset geladen läuft
  genau die getestete Version.
- `DEADBAND_LIVE4_Echtbetrieb.set`: dieselben Werte als Datei (zum Zurücksetzen nach Experimenten).
- `DEADBAND_LIVE4_610_Sicher.set`: Ausprägung „Sicher“ (nur Fades).
- Rückweg: `rollback_6.00/` (mq5 + set), ältere Stände in `rollback_5.10/`, `rollback_5.00/`.

## 6. Inbetriebnahme

1. `DEADBAND_LIVE4.mq5` nach `MQL5\Experts\` kopieren und in MetaEditor kompilieren. Erwartet: 0 Fehler.
2. Extras → Optionen → Charts → **Max. Balken im Chart = Unbegrenzt**, Terminal neu starten (Regime-Wächter braucht
   ~600 Tage M5).
3. Strategietester: „Jeder Tick anhand realer Ticks“, XAUUSD.x M15, 2024–2026. Im Journal prüfen:
   - je Fade-Modul die Zeile `FADE ... Historie ab ...` mit ≈ 25–55 Signalen je Jahr,
   - Fade-Einstiege, danach `Ziel ... gesetzt` erst in der Kerze nach der Einstiegskerze,
   - `ABSCHLUSS-ERNTE ... (Fade/Noise/RSI21, Vorlauf ... R)`, `SERIEN-STOPP`, Schließen bei Auszahlungsreife,
   - keine DEADBAND-Einstiege.
4. Eine Woche auf einem Demokonto mit gleicher Serverzeit.
5. Live **nur auf dem eigenen PC** (GFT: VPS/Server verboten), EIN Chart (XAUUSD.x M15). In `NurAufPcPfad` einen
   Teil des Terminal-Datenpfads eintragen (steht beim Start im Journal).
6. Beim ersten Start die Zeilen `KONTO ERKANNT` bzw. die Datei `MQL5\Files\DEADBAND4_Konto_<Login>.txt` mit dem
   GFT-Dashboard vergleichen: Startsaldo, gültige Tage, Boden (Max-Loss-Level), Tagesgrenze. Weicht der Boden ab:
   `FloorOverride` = Dashboard-Wert und `FloorOverrideZeit` = Zeitpunkt der Ablesung.
7. Nach dem Beantragen einer Auszahlung: `AuszahlungAngefordertAm` = Zeitpunkt (Serverzeit). Der EA bleibt dann flach,
   bis die Auszahlung gebucht ist. Nach der Buchung das Feld wieder leeren.
8. Kommt die Push-Meldung „Abbuchung ... ist KEINE Auszahlung“, obwohl es eine war (z. B. Teilauszahlung): die
   Buchungszeit aus der Meldung als `AuszahlungZeiten` eintragen (oder den Buchungskommentar als `AuszahlungKennung`).

## 7. Grenzen und Hinweise

1. **Regime-Abhängigkeit** der Fades (Bericht 6.00, Abschnitt 6.3): Auf 2006–2021 verdienen sie nicht; der Wächter
   begrenzt die Verluste erst nach einigen Signalen.
2. **Nicht kompiliert, nicht im Tester.** Die Zwischenstände 0704e96 bis dfd9120 kompilierten **nicht** (`MAXFADE`
   vor seiner Definition verwendet); behoben ab 1aaeb9f. Die statische Prüfung erkennt diesen Fehlertyp jetzt
   (Makros und globale Variablen vor der Verwendung, Klammern, alle Format-Aufrufe, unbekannte Funktionen), und
   Sub-Agenten haben den Code in mehreren Durchgängen gegengelesen. Kompilieren in MetaEditor und der Tester bleiben
   Pflicht.
3. **Replikat statt Tick-Test:** M5-Kerzen, News-Sperre nicht abgebildet. Die Kontoerkennung (Abschnitt 4) ist im
   Replikat nicht nachgebildet; sie ändert das Handeln nur in Ausnahmefällen (Neustart, Lücken, Abzüge, nahe am
   Boden). Die Boden-Sperre und der Schutz gültiger Tage vor der Einstiegskommission machen den EA dort etwas
   vorsichtiger als das Replikat: eher weniger Einstiege nahe am Boden, nie mehr.
4. **Wartezeit beim Start:** Erklärt die Historie den Saldo noch nicht, verwaltet der EA bis zu 3 min keine Positionen
   (Stops und Ziele liegen beim Broker; Zeit-Ausstiege und Freitagsschluss folgen danach).
5. **GFT-Lesarten:** Der EA nimmt überall die strengere Lesart (Boden vom Equity-Hoch inkl. Buchgewinn, Tagesreferenz
   max(Saldo, Equity), gültiger Tag in beiden Kommissions-Lesarten, 10 × 24 h). Ist GFT milder, kostet das nur wenig.
6. **Hedging über eigene Konten** und **mehrere Konten mit demselben EA**: siehe Bericht 6.00, Abschnitt 8.
7. **Öffentliches Repository:** Empfehlung „Private“.
