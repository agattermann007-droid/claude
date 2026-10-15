# DEADBAND V11 – Bericht (Build 11.00, 15.10.2026)

## 1. Kurzfassung

**Ergebnis dieser Runde: Keine Änderung am Handel hat die Prüfung bestanden.** V11 handelt mit Voreinstellung genau wie V10.
Neu sind zwei abschaltbare Testmodule (Voreinstellung **aus**) und die dafür nötige Erweiterung des SR-Moduls. Die Testmodule
sind dazu da, die zwei vielversprechendsten Kandidaten mit echten GFT-Ticks im MT5-Tester zu prüfen – das kann mein Nachbau nicht.

Kennzahlen aus dem neu gebauten Nachbau (Replikat v11). Methode: alle 7 Tage startet ein frisches 10k-Konto mit 1 Jahr
Laufzeit, GFT-Premium-Regeln, Schlupf ¼ Spread. Jede Zahl ist der Mittelwert über 16 Störungen (je 3 % andere Signale).
„$/J“ ist dein Anteil nach Split und 3 % Gebühr.

| Fenster (Kontostart) | | V8 (8.10) | **V10 = V11** | V11 + TickFades | V11 + GoldPdf |
|---|---|---|---|---|---|
| 2022 (Auswahl) | Ausz./J | 9,2 | **12,0** | 13,2 | 12,4 |
| | $/J | 1.531 | **2.288** | 2.527 | 2.255 |
| 2023 | Ausz./J | 11,4 | **13,1** | 15,0 | 15,3 |
| | $/J | 2.354 | **2.542** | 3.085 | 3.058 |
| 2024–25 (Prüfung) | Ausz./J | 8,4 | **7,9** | 7,3 | 8,9 |
| | $/J | 1.759 | **1.670** | 1.708 | 2.011 |
| 2017–20 (Prüfung, Fremddaten) | Ausz./J | 5,0 | **5,5** | 6,1 | 5,7 |
| | $/J | 939 | **1.025** | 1.198 | 1.022 |
| alle Fenster | Busts | 0 | **0** | **3** (2024–25) | 0 |

Weitere Kennzahlen für V10/V11:
- Ø Auszahlung 240–273 $.
- Erste Auszahlung im Median nach 16–21 Tagen (2017–20: 29 Tage).
- Konto-Jahre ohne Auszahlung: 0 % (2017–20: 1,7 %).
- Je Startjahr siehe Abschnitt 4.6.

Was du daraus mitnehmen solltest:
1. **V10 schlägt V8 im neuen Nachbau 2022, 2023 und 2017–20, aber nicht 2024–25** (−0,5 ± 0,35 Ausz./J, −89 ± 62 $/J).
   Das gilt auch ohne Schlupf (9,8 gegen 10,7 Ausz./J). Die im V10-Kopf genannte Erwartung „+2 Ausz./J“ ist nur für
   2022–23 gedeckt. Bitte im Tester gezielt 2024 bis heute mit `SrAktiv=false` gegen `true` vergleichen (Abschnitt 6).
2. **Die beiden Testmodule sind nicht übernommen**, weil sie je eine Pflichtprüfung nicht bestehen:
   - TickFades: 2024–25 −0,6 Ausz./J und 3 Busts.
   - GoldPdf: Der Vorteil verschwindet auf unabhängigen Gold-Daten 2010–16 (Gold-Baisse 2014–15 negativ). Er ist
     überwiegend Gold-Aufwärtsdrift.
3. **Deine Hypothese „der Move war schon vorbei“ ist bestätigt, aber nicht handelbar.** 38–88 % der Fade-Verlierer
   erreichen nie +0,2 R. Ein Bestätigungs-Einstieg filtert sie, kostet bei den Gewinnern aber mehr, als er spart.

## 2. Ausgangslage dieser Sitzung

- Die Umgebung war leer: V9, V10 und `Replikat_v10` aus der letzten Sitzung waren weg.
  - V8 kam aus dem Drive, V10 von dir als Upload.
  - Der Nachbau wurde **neu gebaut** (`Replikat_v11/`), auf Basis des Kontomotors `eng6.py` aus dem GitHub-Repo.
- GFT-M5-Daten: Der Drive-Download bricht an der 10-MB-Grenze ab. Deshalb liefen alle Rechnungen auf Fremddaten:
  - Gold: Dukascopy M1, 2016-09 bis 2026-09.
  - NAS: HistData M1, 2010-11 bis 2026-02.
  - Gold 2010–16: OANDA M1, nur als Gegenprobe.
- Datenmängel, gefunden und behandelt (Details in der README des Replikats):
  - **NAS: werktags fehlen die Kurse 16:15–17:00 NY** (ab 2019 komplett). Ohne Korrektur liefen die Ausstiege
    16:40 (N1330, N1300, N1100) und der Freitag-Schluss 16:45 bis 18:00 bzw. übers Wochenende. Das erzeugte im
    ersten Lauf einen falschen Bust. Behoben mit flachen Füllkerzen zum letzten Kurs.
  - NAS Feb.–Jul. 2023: stundenweise Lücken.
  - NAS vor 2019: Rollsprünge an den Quartalsverfallstagen.
  - Behandlung beider Fälle: an diesen Tagen keine neuen NAS-Einstiege, offene Positionen vor Lücken neutral geschlossen.

## 3. Nachbau v11 und Abgleich

### 3.1 Aufbau

Der Nachbau bildet nach:
- M1-Kontomotor mit allen V10-Regeln: Floating 1 % (strenge Lesart), Tagesverlust 3 %, trailender Boden 6 %,
  gültige Tage 0,5 % + 0,50 $, Zyklus 14 Tage, Mindestgewinn 131,25 $, Deckel 6 %.
- EA-Bremsen, Budgets 0,9 %, Pufferkurve, Hedging-Sperre, Serien-Stopp, Schutz gültiger Tage (mit Ausnahmen).
- Abschluss-Ernte (alle Module), Gewinn-Ernte (RSI21), Schließen bei Reife, Wochenende mit Wiederaufnahme,
  Swap-Vorsorge.
- Alle Signal-Generatoren Zeile für Zeile nach dem MQL5-Code: Fades mit Probability Grid und Portfolio-Wächter,
  S0830, LW, XA, TD, SR im Tick (M1, pessimistisch), RSI21, Noise.

Konventionen:
- Long zum Ask; Stop vor Ziel in derselben Minute.
- Ziel ab der nächsten M5-Kerze (SR: ab der 4. Minute).
- Schlupf ¼ Spread auf Markt-Einstiege, Stop- und Zeit-Ausstiege.

### 3.2 Abgleich mit den bekannten Kennzahlen

| Kennzahl | Bericht | Replikat v11 |
|---|---|---|
| Spike S0830 2022–25 | 92 % Treffer, PF 5,3, ~11/J | 87 %, PF 3,3, 12/J (2016–21: 87 %, PF 2,5; Bericht 2006–21: 87 %, PF 2,7) |
| LW PF 22–23 / 24–25 / 2016–21 | 1,55 / 1,59 / 1,20 | 1,46 / 1,42 / 1,21 |
| SR je Marke | PF 1,14–1,17 | PF 1,17–1,25 (2022–25) |
| V8 auf Premium | ≈ 3.000 $/J, 14,3 Ausz./J (eng6, ohne Schlupf) | ohne Schlupf 2.078–2.888 $/J, 12,4–14,1 Ausz./J (2022/2023) |
| SR-Risiko | ab 0,35 % Busts | ab 0,30 % Busts (37 bzw. 71 in 2017–20) |

Was der Abgleich zeigt:
- Stromebene: passt. Spike und LW liegen etwas unter dem Bericht – Folge von M1-Pessimismus und Schlupf.
- Kontoebene: Mit Schlupf liegt der Nachbau ~25–35 % unter den alten eng6-Zahlen.
- **Der Schlupf ist der größte Einzelfaktor.** Für V8 2024–25 macht er 7,0 gegen 11,9 Ausz./J (je ein Lauf).
  - Er trifft vor allem LW (kleiner Stop) und RSI21.
  - Die Kontodynamik verstärkt das: weniger Gewinn → weniger Puffer → LW pausiert unter 4 %.
- Belastbar sind deshalb die **Vergleiche unter gleichen Annahmen**, nicht die absoluten Zahlen.

### 3.3 Rauschen der Kontoebene

- Schon 3 % andere Signale verschieben V10 je Lauf um ±1 Ausz./J und ±170 $/J (2024–25).
- Deshalb habe ich alle Kontovergleiche **gepaart über 16 bzw. 32 Störungen** gerechnet und Differenz ± Standardfehler
  angegeben.
- Faustregel: Unterschiede unter ~0,4 Ausz./J bzw. ~100 $/J sind nicht von Zufall zu unterscheiden.

## 4. Tests

### 4.1 Hypothese „der Move war schon vorbei“

Anteil der Verlierer, die nie +0,2 R im Plus waren (alle Jahre, live-Signale):
- Fades 38–88 % (Mittel ≈ 50 %)
- S0830 57 %, XA 59 %, TD 51 %
- LW 29 %, SR 19–41 %

**Neuer Ansatz: Bestätigungs-Einstieg.** Das Signal wird erst gekauft bzw. verkauft, wenn der Kurs +x R in
Signalrichtung gelaufen ist (Stop-Order, x = 0,1/0,2/0,3, Wartezeit 30 min oder bis zum Ausstieg). Läuft der Kurs
vorher zum Stop, entfällt das Signal.

Ergebnis:
- Bei keinem der 18 Ströme in allen drei Zeiträumen besser.
- Die Trefferquote steigt (z. B. N1030 von 73 % auf 88–100 %), aber der Erwartungswert je Trade sinkt meist.
- Die Ziele der Fades sind klein (Range-Mitte ≈ 0,5–1 R), daher kosten 0,1–0,3 R schlechterer Einstieg bei jedem
  Gewinner mehr, als die vermiedenen Verlierer sparen.
- Bei SR ist der Bestätigungs-Einstieg klar schlechter: Der Einstieg im Tick an der Marke ist dort gerade der Vorteil.

→ verworfen (`t_hypo.py`).

### 4.2 Fades im Tick (Einstieg beim Rücklauf in die Range statt nach dem M5-Schluss)

Stromebene, Summe der 10 Fades (R):

| | 2016–21 | 2022–23 | 2024–26 |
|---|---|---|---|
| M5 wie V10 | −146 | +64 | +96 |
| im Tick | −28 | +73 | +142 |

- Im Tick gibt es ~2,4× mehr Trades.
- Je Modul ist der Tick-Fade nur bei **N1030, N1100 und N1800** in allen drei Zeiträumen besser.

Kontoebene (gepaart, 16 Störungen, Differenz zu V10, Ausz./J):

| Variante | 2022 | 2023 | 2024–25 | 2017–20 |
|---|---|---|---|---|
| N1030+N1100 | +1,20 ± 0,11 | +1,86 ± 0,25 | **−0,61 ± 0,24** | +0,61 ± 0,05 |
| N1800 allein | −0,71 ± 0,20 | – | – | – |
| alle drei | −0,24 ± 0,12 | – | – | – |

- N1030+N1100 in $: 2022 +239, 2023 +543, 2024–25 +38 ± 62, 2017–20 +173; **3 Busts** in 2024–25 (ein tiefer
  Rückgang Juli 2025).
- N1800 allein und alle drei zusammen fallen schon im Auswahlfenster durch.

→ nicht übernommen. Als **Testschalter `V11TickFades`** im EA, weil der Nachbau Tick-Einstiege nur auf M1 schätzt –
echte Ticks können das Bild ändern.

### 4.3 Neue Price-Action-Ströme (Sweep-Reclaim im Tick), Gold und NAS

Scan:
- Gold 2.784 Varianten, NAS 1.824 Varianten.
- Marken: Asien, London, Vor-NY, NY-Eröffnung, Initial Balance, Mittag, Nachmittag, Vortag.
- Gitter: Richtung, Sweep-Tiefe, Durchbruch-Grenze, Stop-Puffer, Ziel (1–3 R, Range-Mitte, Gegenseite), Ausstieg.

Ablauf:
1. Auswahl nur auf 2022–23: E ≥ +0,10 R, PF ≥ 1,15, n ≥ 60.
   - Gold 228, NAS 207.
2. Davon in 2024–26 **und** 2016–21 positiv (E > +0,03 R):
   - Gold 27, NAS 67.
   - **Alle überlebenden Gold-Varianten sind „Sweep des Tiefs → Long“** (Gold-Aufwärtsdrift!).
3. Acht Cluster-Mitten auf Kontoebene (Risiko 0,10 und 0,20 %, gepaart):
   - Gold: GASIA, GPRE, GPD, GPDF.
   - NAS: NPM, NPDC, NASIA, NORB.

Ergebnis:
- **Alle vier NAS-Kandidaten verlieren im Auswahlfenster 2022.** Der NAS-Long-Bereich ist gesättigt: Budget,
  Hedging-Sperre und Risiko je Idee teilen sich schon Fades, LW, Noise, TD und SR.
- GASIA, GPRE, GPD: nicht besser.
- Einziger Kandidat: **GPDF** (Gold unter das Vortagestief 18:00–2:00 NY und zurück → Long, Ziel 3 R).

Prüfung von GPDF:
- 78 der 424 Signale fallen in die ersten 30 Minuten nach der Wiedereröffnung 18:00, davon 57 in die ersten
  5 Minuten. Diese 57 tragen 2016–21 zwei Drittel des Vorteils (11,8 von 17,9 R).
  - Diese Kurse sind live unzuverlässig: breite Spreads, Feed-Unterschiede.
  - Variante „erst ab 18:30“, Stop-Puffer 0,15 ATR, 0,25 %: Ausz./J +0,34 / +2,18 / +1,00 / +0,17; $/J −33 / +516 /
    +342 / −4.
- **Gegenprobe OANDA-Gold 2010–16** (enthält die Baisse 2011–15): E +0,00 bis −0,05 R, 2014 und 2015 je −9 bis
  −16 R. Der Vorteil ist also überwiegend Drift; in einem Gold-Bärenmarkt würde GPDF verlieren.

→ nicht übernommen. Als **Testschalter `V11GoldPdf`** im EA.

### 4.4 SR-Risiko (32 gepaarte Störungen, Differenz zu V10 = 0,10 %)

| SR-Risiko | 2022 | 2023 | 2024–25 | 2017–20 | Busts |
|---|---|---|---|---|---|
| 0,15 % | −0,03 / +94 $ | +0,06 / +45 $ | **−0,58 / −134 $** | +0,24 / +87 $ | 0 |
| 0,20 % | +0,09 / +233 $ | +0,04 / +25 $ | +0,39 / +79 $ | +0,73 / +172 $ | 0 |
| 0,25 % | −0,47 / +110 $ | −0,33 / +8 $ | +1,22 / +186 $ | +0,23 / +16 $ | 0 |
| 0,30 % | −2,05 / −486 $ | 0,00 / +256 $ | +1,80 / +320 $ | +0,28 / 0 $ | **37** |
| 0,35 % | −2,88 / −605 $ | – | – | – | **72** |

0,20 % sieht gut aus, liegt aber als Spitze zwischen zwei schlechteren Nachbarn – **kein Plateau, keine Änderung**.

### 4.5 Konto-Mechanik (16 gepaarte Störungen, Differenz zu V10, Ausz./J)

| Variante | 2022 | 2023 | 2024–25 | 2017–20 |
|---|---|---|---|---|
| Abschluss-Ernte ab 0,2 R | −0,04 | −0,15 | +0,11 | −0,02 |
| Abschluss-Ernte ab 0,5 R | −0,15 | +0,03 | −0,25 | −0,05 |
| Abschluss-Ernte 10 % Reserve | +0,22 | +0,59 | −0,09 | +0,05 |
| Serien-Stopp 4 | **−1,03** | – | – | – |
| Serien-Stopp 2 | −0,50 | – | – | **−0,78** |
| ohne Schutz gültiger Tage | **−2,02** | **−2,22** | – | – |
| RSI21-Schutz bis 12:00 | +0,46 | – | −0,05 | – |
| RSI21-Schutz bis 14:00 | +0,63 | – | −0,01 | – |
| Gewinn-Ernte ab 0,5 R | ±0,0 | ±0,0 | ±0,0 | ±0,0 |

- Abschluss-Ernte mit 10 % Reserve: im Rahmen des Rauschens.
- RSI21-Schutzzeit: Beide Richtungen „verbessern“ 2022 – das ist Pfad-Rauschen, kein Effekt.

→ alles bleibt wie in V10.

### 4.6 V10 (= V11) je Startjahr (1-Jahres-Konten, 16 Störungen)

| Start | Ausz./J | $/J | Ø Ausz. | 1. Ausz. (Median) | ohne Ausz. |
|---|---|---|---|---|---|
| 2017 | 5,4 | 913 | 219 $ | 35 T | 0,1 % |
| 2018 | 7,0 | 1.346 | 248 $ | 24 T | 0 % |
| 2019 | 3,4 | 643 | 244 $ | 24 T | 6,6 % |
| 2020 | 6,3 | 1.207 | 246 $ | 45 T | 0 % |
| 2022 | 12,1 | 2.303 | 246 $ | 16 T | 0 % |
| 2023 | 13,1 | 2.524 | 249 $ | 21 T | 0 % |
| 2024 | 7,6 | 1.605 | 272 $ | 16 T | 0 % |
| 2025* | 10,8 | 2.385 | 285 $ | 15 T | 0 % |

\* nur 6 Starts (NAS-Daten enden 13.02.2026).

Der Regime-Wechsel ist deutlich: In 2017–20 sind die Fades fast immer nur virtuell (Wächter), dann trägt der Rest
(RSI21, Noise, LW, XA, SR) nur ~5,5 Ausz./J.

## 5. Einstellungen V11

| Eingabe | Voreinstellung | Wirkung |
|---|---|---|
| `V11TickFades` | **false** | true: N1030/N1100 rechnen nur virtuell; SRT1030/SRT1100 handeln im Tick (Range, Fenster, Stop-Puffer × Range, Ziel Mitte bzw. Gegenseite, Range ≤ 0,6 ATR, Risiko `FadeRiskPct`), nur bei live Portfolio-Wächter |
| `V11GoldPdf` | **false** | true: Modul SRGPDF (XAU, Marke = Vortag 18:00–17:00, Fenster 18:30–2:00 NY, Stop 0,15 ATR unter dem Extrem, Ziel 3 R, Ausstieg 8:00 NY) |
| `V11GoldPdfRisk` | 0,25 | Risiko je SRGPDF-Trade in % |
| `SrListe` | leer | jetzt auch 19 Felder je Marke: `Name,la,lb,loff,w0,w1,x,sd,md,rb,sb,dir,Symbol,smode,tmode,crv,Risiko,mx,Waechter` (12 Felder = wie 9.00) |

- `MAXFADE` 18 → 22. Die Fade-Magics reichen damit bis MagicBase + 50 + 21.
- **Rückfall auf 10.00:** beide Schalter aus (Voreinstellung). `DEADBAND_V10.mq5` liegt unverändert daneben.
- Mit Voreinstellung ist jeder geänderte Codepfad rechnerisch identisch zu 10.00:
  - SR-Stop × ATR, Mindeststop wie bisher, Ziel `SrCRV`.
  - Kein Wächter für SR; Listen-Fades unverändert.

## 6. Checkliste vor dem Live-Einsatz

1. V11 im MetaEditor kompilieren. **NICHT KOMPILIERT ERSTELLT.** Geprüft sind nur statisch: ASCII, Klammerbilanz,
   388 Format-Strings gegen die Argumentzahl, Diff gegen V10. Der Build ist aus `DEADBAND_V10.mq5` mit
   `patch_v11.py` reproduzierbar.
2. Strategietester, Echte Ticks, NAS100.x + XAUUSD.x, 01.01.2024 bis heute:
   - a) V11 Voreinstellung muss V10 handelsgleich sein: gleiche Trades, gleiche Auszahlungen.
   - b) **`SrAktiv=false` gegen `true`** – klärt, ob SR 2024–26 auf GFT-Daten hilft. Im Nachbau hilft SR dort nicht.
   - c) `V11TickFades=true`: Ziel ist mehr Auszahlungen bei 0 Bodenbrüchen (OnTester = kleinster Abstand zum Boden).
     Im Journal die Einstiege SRT1030/SRT1100 mit den M5-Signalen von N1030/N1100 vergleichen.
   - d) `V11GoldPdf=true`, zusätzlich 2022 und wenn möglich 2018–2019: Spreads um 18:30 NY, Ergebnis je Monat.
3. Erst wenn b/c/d im Tester klar besser sind **und** der Kleinste Abstand zum Boden nicht kleiner wird, einen
   Schalter live einschalten – dann einzeln, nicht beide zugleich.
4. Unverändert gilt: kein VPS, News-Fenster, 130-s-Regel, Hedging-Sperre, Budgets, Pufferkurve.

## 7. Grenzen

- Fremddaten statt GFT-Feed:
  - NAS HistData mit Lücken (2023), Rollsprüngen (vor 2019) und fehlender Spätsitzung.
  - Gold Dukascopy, Spread als Modell (konstant relativ zum Kurs, keine breiten Eröffnungsspreads).
  - Die Regel „Datenlücken-Tage ohne NAS-Einstiege“ senkt die Zahlen 2023 (beide Varianten gleich).
- M1 statt Ticks: Tick-Einstiege (SR, Tick-Fades) sind pessimistisch geschätzt; die Reihenfolge innerhalb einer
  Minute ist unbekannt.
- Nicht nachgebildet: News-Sperre, Kontoerkenner/Anpasser (neutral), Peak-Unsicherheit, Konsistenzregel im Detail,
  Margin nur grob (Hebel 1:20).
- Ab 2026-02-13 fehlen NAS-Daten.
- Viele Varianten = Zufallsgefahr:
  - 4.608 Scan-Varianten, 22 Kontokandidaten, 9 Mechanik-Varianten, 5 Risikostufen.
  - Bestanden hat keine; die Zahlen der Testmodule sind daher eher zu optimistisch als zu pessimistisch.
- Die Kontozahlen sind chaotisch empfindlich (±1 Ausz./J je Lauf). Einzelne Läufe – auch im MT5-Tester – sagen wenig.
  Im Tester möglichst mehrere Startdaten prüfen.

## 8. Dateien

| Datei | Inhalt |
|---|---|
| `/home/user/DEADBAND_V11.mq5` | Build 11.00 (nicht kompiliert) |
| `/home/user/DEADBAND_V10.mq5` | Basis (dein Upload, unverändert) |
| `/home/user/DEADBAND_V11_build/` | `patch_v11.py` (13 exakte Ersetzungen, Abbruch wenn eine nicht genau einmal passt), `patch_lib.py`, `kopf_v11.py`/`.txt`, `check_mq5.py` (statische Prüfung), `V10_V11.diff` |
| `/home/user/Replikat_v11/` | Nachbau (numpy, pandas, numba; Pfade über `XAU_DIR`, `NAS_DIR`, `NPZ_DIR`, `REP_CACHE`), README, alle Versuche `t_*.py`, Ausgaben in `ergebnisse/` |

Build neu erzeugen: im Ordner `DEADBAND_V11_build` `python patch_v11.py ../DEADBAND_V10.mq5 ../DEADBAND_V11.mq5`,
danach `python check_mq5.py ../DEADBAND_V11.mq5`.
