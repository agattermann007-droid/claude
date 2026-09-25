# DEADBAND LIVE 4 – Build 6.50 NETTO

Bericht vom 25.09.2026 · GFT Instant Premium 10k (Konto ab 02.09.2026)

## 1. Kurzfassung

Auftrag: 6.40 verbessern und den **Nettogewinn erhöhen, ohne Auszahlungen je Jahr zu verlieren**. Wie bei allen Builds seit
6.00 gilt zusätzlich: nicht mehr Bust-Risiko.

**Build 6.50** ändert nur, *welche* Einstiege an einem schon gültigen Tag gesperrt sind, und das Fade-Risiko. Signale,
Auszahlungsregeln, Pufferkurve und Regime-Wächter bleiben wie in 6.40:

1. **RSI21 an gültigen Tagen** (neu `GueltigSchutzR21BisNY` 13, `GueltigSchutzR21Regime` an): Der Schutz gültiger Tage sperrt
   RSI21 nur noch vor 13:00 NY und immer dann, wenn der Portfolio-Wächter die Fades nicht live handeln lässt (altes Regime).
   Ab 13:00 NY eröffnete RSI21-Trades schließen meist erst an einem Folgetag. Sie gefährden den gültigen Tag kaum und tragen
   Gewinn in die nächsten Tage.
2. **N1330 und N1300 an gültigen Tagen** (neu `GueltigSchutzFrei`): Die beiden NAS-Nachmittags-Fades (Einstieg ab 14:30 NY,
   Trefferquote rund 80 %) handeln auch an einem schon gültigen Tag. Sie waren die am häufigsten gesperrten Fades.
3. **Fade-Risiko 0,70 statt 0,75 %** (`FadeRiskPct`): mehr Luft zur Floating-Bremse bei −0,8 %.

Noise und die übrigen acht Fades bleiben an gültigen Tagen gesperrt wie in 6.40.

**Ergebnis** im Konto-Replikat mit allen GFT-Regeln (16 Störungen, rollierende Konten über 1/2/3 Jahre, jeder Handelstag
ein neues Konto). Wie bei 6.40 auf dem GFT-Ersatz aus Fremddaten 2022–2025, mit GFT-nahen und mit breiten Spreads:

| Kennzahl | 6.40 Ertrag | **6.50 Ertrag** (Echtbetrieb) |
|---|---:|---:|
| **Netto je Jahr** (80 % Anteil, 3 % Gebühr, Neukäufe), GFT-nah / breit | 2232 / 2051 $ | **2510 / 2319 $** (+12,5 / +13,1 %) |
| **Auszahlungen je Jahr**, GFT-nah / breit | 12,06 / 11,25 | **12,12 / 11,66** |
| Tage je Auszahlung, GFT-nah / breit | 30,3 / 32,5 | **30,1 / 31,3** |
| Auszahlung im Mittel (Gewinn vor 80 % und 3 %), GFT-nah / breit | 239 / 235 $ | 267 / 256 $ |
| **Busts je Jahr**, GFT-nah / breit | 0 / 0 | **0 / 0** |
| Kleinster Abstand zum Boden je Konto, Mittel, GFT-nah / breit | 248 / 255 $ | **261 / 262 $** |
| Konten, die dem Boden auf < 100 $ nahekamen, GFT-nah / breit | 0,0 / 0,0 % | **0,0 / 0,0 %** |
| Konten, die dem Boden auf < 200 $ nahekamen, GFT-nah / breit | 4,1 / 0,1 % | 5,9 / 0,0 % |
| Serien ≥ 6 Verluste je Jahr, GFT-nah / breit | 0,77 / 0,83 | 0,67 / 0,92 |
| Trefferquote, GFT-nah / breit | 66,1 / 65,6 % | 66,9 / 66,6 % |
| **Fremddaten 2006–21** (anderes Regime): Auszahlungen je Jahr | 2,16 | **2,14** |
| … Busts je Jahr / Konten mit Bust im 1. Jahr | 0,035 / 0,9 % | **0,034 / 0,6 %** |
| … kleinster Abstand zum Boden, Mittel / Netto je Jahr | 207 $ / 364 $ | 210 $ / 361 $ |

- **Mehr Netto:** +278 $ je Jahr mit GFT-nahen, +268 $ mit breiten Spreads. Die Auszahlungen sind größer (267 statt 239 $
  im Mittel, GFT-nah), weil an gültigen Tagen mehr gute Trades laufen.
- **Nicht weniger Auszahlungen:** im Mittel über 2022–2025 12,12 statt 12,06 (GFT-nah) bzw. 11,66 statt 11,25 (breit).
  GFT-nah ist das ein Gleichstand im Rahmen der Streuung (±0,5–0,7 je Störung), kein Gewinn.
- **Nicht mehr Bust-Risiko:** 0 Busts in beiden Rechnungen, kein Konto näher als 100 $ am Boden, im Mittel 7–13 $ weiter
  weg als bei 6.40. Im alten Regime 2006–21 Busts, Auszahlungen und Netto wie 6.40.
- **Nach Startjahr** (1-Jahres-Konten) ist 6.50 nicht in jedem Jahr vorn (Abschnitt 3.6): GFT-nah Start 2022 12,6 statt
  13,0 Auszahlungen (aber +66 $ Netto), Start 2024 9,3 statt 8,8. Start 2025 (nur 128 Konten) etwas weniger Netto.
- **Sicher**-Ausprägung: nur das Fade-Risiko 0,70 %. Auszahlungen gleich, +9 bis +29 $ Netto, Verlustserien unverändert
  (Abschnitt 3.7).
- **Mehr wäre möglich, aber nicht ohne Risiko:** RSI21 schon ab 11:00 NY frei brächte +417 / +480 $ Netto und 12,26 / 11,89
  Auszahlungen (GFT-nah / breit), im alten Regime aber 0,048 statt 0,035 Busts je Jahr (Episode Februar–Juni 2010). Das ist
  nur eine Option (`GueltigSchutzR21BisNY=11`), nicht voreingestellt.

**Nicht geprüft:** Kompilieren in MetaEditor, Strategietester, Demo. Das bleibt Pflicht (Abschnitt 6).

## 2. Wo 6.40 Netto liegen ließ

Der Schutz gültiger Tage von 6.40 sperrt nach einem gültigen Tag alle neuen Einstiege bis 17:00 NY, solange dem Zyklus noch
gültige Tage fehlen. Er bringt Auszahlungen, kostet aber viel Netto (Screening, breite Spreads, 8 Störungen):

| | Auszahlungen je Jahr | Netto | gültige Tage | wieder verlorene gültige Tage |
|---|---:|---:|---:|---:|
| 6.40 (Schutz für alle Module) | 11,15 | 2030 $ | 62,4 | 3,1 |
| 6.40 ohne Schutz | 10,53 | **2492 $** | 56,6 | 12,5 |

Die gesperrten Trades sind also im Mittel gute Trades. Welche? Ohne Schutz, Trades nach einem schon gültigen Tag (Zyklus
braucht noch Tage; je Jahr, Ergebnis · Zahl · Trefferquote):

| Modul | Ergebnis je Jahr | Trades je Jahr | Treffer |
|---|---:|---:|---:|
| RSI21 | **+244 $** | 13,0 | 60 % |
| N1330 / N1300 (NAS-Nachmittags-Fades) | **+72 / +68 $** | 9,0 / 6,1 | 79 / 80 % |
| X1000S / N1100 / X0630 / N1030 | +46 / +33 / +24 / +12 $ | 2,1 / 2,5 / 2,8 / 1,8 | 72 / 62 / 67 / 59 % |
| übrige Fades (X0400, N0930, X0300S) | −6 $ zusammen | 4,2 | |
| Noise | **+8 $** | 43,7 Teile | 49 % |

- **Noise** verdient an gültigen Tagen nichts. Dort bleibt der Schutz – er kostet nichts und schützt den Tag.
- **RSI21** verdient am meisten, aber nicht am gültigen Tag selbst. Aufgeteilt nach dem Tag, an dem der Trade schließt
  (Replikat, Trades nach gültigem Tag, 250-Tage-Konten):

  | RSI21 nach gültigem Tag | Trades je Jahr | Ergebnis je Jahr | Tag gekippt (Verlust > Vorsprung) |
  |---|---:|---:|---:|
  | schließt am selben Tag | 7,2 | +19 $ | 3,8 je Jahr |
  | schließt an einem Folgetag | 6,2 | **+287 $** | – |

  Ein RSI21-Trade hält bis zu 8 Tage (Einstand ab 1 R). Schließt er erst später, trägt sein Gewinn zu einem späteren Tag
  bei und kann ihn gültig machen. Schließt er noch am selben Tag, bringt er im Mittel nichts, kippt aber manchen Tag zurück.
- **Wann schließt ein RSI21-Trade noch am selben Tag mit Verlust?** Alle RSI21-Trades (auch vor dem gültigen Tag), nach
  Einstiegszeit (breit / GFT-nah):

  | Einstieg NY | Trades je Jahr | am selben Tag mit Verlust | Ergebnis je Trade |
  |---|---:|---:|---:|
  | 09:30–10:00 | 4,8 | 15 / 16 % | +28 / +26 $ |
  | 10:00–10:30 | 15,7 | **37 / 36 %** | +6 / +5 $ |
  | 10:30–11:00 | 9,6 | 26 / 26 % | +14 / +13 $ |
  | 11:00–11:30 | 11,2 | 14 / 14 % | +27 / +25 $ |
  | 11:30–12:00 | 6,1 | 20 / 22 % | +6 / +2 $ |
  | 12:00–13:00 | 10,1 | 25 / 25 % | +9 / +7 $ |
  | 13:00–15:00 | 2,9 | **7 / 10 %** | +19 / +26 $ |
  | 15:00–17:00 | 3,7 | **3 / 1 %** | +32 / +39 $ |

  Ab 13:00 NY bleibt bis zum Tageswechsel wenig Zeit, den Stop zu erreichen. Deshalb gibt 6.50 RSI21 erst ab 13:00 NY frei.
- **N1330 und N1300** laufen ab 14:30 NY, wenn der Tag oft schon gültig ist. Sie waren über die Hälfte der gesperrten
  Fade-Trades und treffen in 80 % der Fälle. Ein Verlust, der den Tag kippt, ist selten (0,9 bzw. 0,3 Tage je Jahr).

## 3. Was gesucht und geprüft wurde

Replikat `eng9` = `eng8` plus Schutz je Modul, RSI21-Uhrzeit und Regime-Schalter, weitere Schutzformen und ein
Trade-Protokoll mit dem Zustand beim Einstieg (`t_eng9.py`: mit Voreinstellungen identisch mit eng8). Screening `x48.py`,
Endbewertung `x49.py`. Die Kursdaten wurden aus den Quellen neu aufgebaut, alle fünf Dateien sind byte-identisch mit dem
Datenbericht; das Replikat rechnet 6.40 exakt wie im 6.40-Bericht (Abschnitt 5).

### 3.1 Schutzformen (Screening, breite Spreads, 8 Störungen, jeder 2. Handelstag)

Zellen: Auszahlungen je Jahr (Tage je Auszahlung) · Netto · gültige Tage · wieder verlorene gültige Tage.

| Schutz nach gültigem Tag | Ergebnis |
|---|---|
| 6.40: alle Module gesperrt | 11,15 (32,8) · 2030 $ · 62,4 · 3,1 |
| kein Schutz | 10,53 (34,7) · 2492 $ · 56,6 · 12,5 |
| nur RSI21 gesperrt | 10,17 (35,9) · 2249 $ · 54,8 · 11,8 |
| nur Noise gesperrt | 10,77 (33,9) · 2433 $ · 59,0 · 8,7 |
| nur Fades gesperrt | 10,70 (34,2) · 2333 $ · 59,3 · 9,5 |
| **Noise und Fades gesperrt, RSI21 frei** | **11,18 (32,7) · 2237 $ · 62,7 · 5,3** |
| RSI21 und Fades gesperrt, Noise frei | 10,69 (34,2) · 2154 $ · 58,7 · 8,3 |
| alle Module, Einstieg nur mit Vorsprung ≥ 1 / 0,5 / 0,25 × Risiko | 11,12 / 10,72 / 10,94 · 2030 / 1990 / 2117 $ |
| alle Module, Größe × 0,5 / × 0,33 | 10,53 / 10,60 · 2331 / 2208 $ |
| alle Module, Stop so eng, dass der Tag gültig bleibt (mind. 30 % des Stops) | 11,21 (32,6) · 2070 $ |

Nur „Noise und Fades gesperrt, RSI21 frei“ hält die Auszahlungen und bringt deutlich mehr Netto. Kleinere Positionen oder
engere Stops nach einem gültigen Tag helfen nicht: Die kleinere Position verdient weniger, der engere Stop wird öfter
getroffen.

Darauf (Arbeitsbasis „B50“, 8 Störungen): einzelne Fades frei N1330 11,29 · 2349 $, N1300 11,32 · 2362 $, beide 11,35 ·
2396 $; N1100 11,34 · 2357 $, X1000S 11,38 · 2329 $, X0630 11,10 · 2235 $, N1030 11,17 · 2275 $. Fade-Risiko 0,70 %
11,50 · 2391 $, 0,80 % 11,23 · 2207 $.

### 3.2 Rauschen und Auswahl mit 16 und 48 Störungen

Zwei Sätze zu je 8 Störungen unterschieden sich bei derselben Variante um bis zu 0,46 Auszahlungen und 90 $ Netto (RSI21-
Risiko 0,55: 10,77 gegen 11,23). Ab hier wurde deshalb mit 16 Störungen gesucht und die Endauswahl mit 48 Störungen
geprüft, jeweils mit beiden Spread-Lagen (Zellen: breit / GFT-nah).

| Variante (16 Störungen, jeder 2. Handelstag) | Auszahlungen | Netto | Abstand Ø | < 200 $ |
|---|---:|---:|---:|---:|
| 6.40 Ertrag | 11,25 / 12,06 | 2052 / 2233 $ | 255 / 248 $ | 0,1 / 4,0 % |
| B50 (RSI21 frei) | 11,20 / 11,91 | 2233 / 2442 $ | 251 / 244 $ | 0,5 / 3,8 % |
| B50, Fade-Risiko 0,70 % | 11,46 / 12,02 | 2378 / 2517 $ | 258 / 251 $ | 1,4 / 5,7 % |
| B50, N1330/N1300 frei | 11,31 / 11,83 | 2380 / 2563 $ | 250 / 242 $ | 0,6 / 2,1 % |
| **C50** = B50, 0,70 %, N1330/N1300 frei | **11,47 / 12,01** | **2511 / 2637 $** | 260 / 254 $ | 0,0 / 0,2 % |
| C50, zusätzlich N1100 und X1000S frei | 11,24 / 11,87 | 2527 / 2687 $ | 260 / 257 $ | 0,0 / 2,1 % |
| C50, alle Fades frei | 10,80 / – | 2459 / – $ | 258 / – $ | 0,4 / – % |
| C50, Fade-Risiko 0,65 % | 11,42 / 12,02 | 2470 / 2669 $ | 265 / 259 $ | 0,3 / 1,2 % |
| C50, unter Startsaldo ×0,9 statt ×0,8 | 11,53 / 12,18 | 2497 / 2650 $ | 247 / 239 $ | 1,0 / 8,5 % |
| C50, unter Startsaldo ×1,0 statt ×0,8 | 11,78 / 12,15 | 2537 / 2679 $ | 239 / 221 $ | 5,3 / 34,1 % |
| C50, Noise 0,40 % | 11,12 / 11,76 | 2395 / 2572 $ | 259 / 251 $ | 0,7 / 1,6 % |
| C50, RSI21 höchstens 3 Verluste je Tag | 11,51 / 12,05 | 2519 / 2648 $ | 260 / 254 $ | 0,0 / 0,4 % |

- Mehr freie Fades bringen etwas Netto, kosten aber Auszahlungen.
- Größere Positionen unter dem Startsaldo (`BelowStartMult` 0,9/1,0) bringen Auszahlungen, rücken die Konten aber an den
  Boden (GFT-nah 34 % unter 200 $). Verworfen.
- Mit C50 ist GFT-nah noch kein Auszahlungs-Vorsprung da (12,01 gegen 12,06). Die Ursache sind RSI21-Trades, die noch am
  selben Tag verlieren (Abschnitt 2). Deshalb die Uhrzeit:

| RSI21 frei ab NY (sonst wie C50; 16 Störungen) | 0:00 | 10:30 | 11:00 | 11:30 | 12:00 | **13:00** | 14:00 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Auszahlungen, breit | 11,47 | 11,64 | 11,90 | 11,64 | 11,50 | **11,67** | 11,45 |
| … GFT-nah | 12,01 | 12,01 | 12,24 | 12,05 | 11,99 | **12,13** | 12,13 |
| Netto, breit | 2511 $ | 2503 $ | 2534 $ | 2408 $ | 2354 $ | **2319 $** | 2244 $ |
| … GFT-nah | 2637 $ | 2612 $ | 2647 $ | 2548 $ | 2534 $ | **2510 $** | 2479 $ |

Mit 48 Störungen (jeder 2. Handelstag; 6.40: 10,95 / 11,93 Auszahlungen, 1988 / 2204 $):

| Variante | Auszahlungen breit / GFT-nah | Netto breit / GFT-nah |
|---|---:|---:|
| C50 (RSI21 immer frei) | 11,17 / 12,02 | 2444 / 2609 $ |
| C50, RSI21 frei ab 11:00 | 11,50 / 12,25 | 2456 / 2617 $ |
| **C50, RSI21 frei ab 13:00** | **11,29 / 12,09** | **2256 / 2481 $** |
| nur die Fade-Bausteine (0,70 %, N1330/N1300 frei) | 11,09 / 11,96 | 2137 / 2320 $ |
| nur RSI21 frei ab 13:00 | 11,15 / 12,00 | 2068 / 2317 $ |

11:00 ist auf dem GFT-Ersatz am besten, aber eine Spitze zwischen schwächeren Nachbarn. Entschieden hat das alte Regime.

### 3.3 Altes Regime: warum 13:00 NY und warum der Regime-Schalter

Fremddaten 2006–2021, 16 Störungen, jeder 3. Tag. Zerlegung (je ein Baustein auf 6.40):

| Variante | Auszahlungen je Jahr | Busts je Jahr | Bust im 1. Jahr | Netto | Abstand Ø |
|---|---:|---:|---:|---:|---:|
| 6.40 Ertrag | 2,16 | 0,035 | 0,9 % | 364 $ | 207 $ |
| + Fade-Risiko 0,70 % | 2,15 | 0,034 | 0,7 % | 362 $ | 209 $ |
| + N1330/N1300 frei | 2,15 | 0,034 | 0,9 % | 364 $ | 208 $ |
| + beide Fade-Bausteine | 2,14 | 0,034 | 0,7 % | 362 $ | 210 $ |
| + RSI21 immer frei | 2,07 | **0,048** | **2,7 %** | 409 $ | 199 $ |
| + RSI21 frei ab 11:00 | 2,07 | **0,051** | **2,9 %** | 384 $ | 199 $ |
| + RSI21 frei ab 13:00 | 2,03 | 0,036 | 1,1 % | 353 $ | 201 $ |
| C50, RSI21 frei ab 11:00, nur ohne Rückgang (Pufferkurve voll bzw. über Startsaldo) | 2,05–2,08 | 0,046–0,047 | 2,3 % | 377–384 $ | 201 $ |
| C50, RSI21 frei ab 13:00 (ohne Regime-Schalter) | 2,01 | 0,034 | 0,6 % | 351 $ | 203 $ |
| C50, RSI21 frei ab 11:00, mit Regime-Schalter | 2,14 | **0,048** | **2,5 %** | 360 $ | 209 $ |
| **6.50: C50, RSI21 frei ab 13:00, mit Regime-Schalter** | **2,14** | **0,034** | **0,6 %** | **361 $** | **210 $** |

- Die Fade-Bausteine sind im alten Regime neutral bis etwas sicherer.
- Alle Busts des alten Regimes fallen in **eine Episode, Februar–Juni 2010** (dazu wenige 2011; alle am Boden). RSI21 vor
  13:00 NY lässt dort mehr Konten kippen: insgesamt 5613 statt 4355 Konto-Busts (alle Starts und Störungen
  zusammengezählt), im April 2010 allein 2967 statt 1080. Eine Rückgangs-Bedingung hilft nicht. **Ab 13:00 NY** bleibt es
  bei 6.40-Niveau (6.50: 4299 Konto-Busts).
- Mit RSI21 ab 13:00 sanken im alten Regime aber die Auszahlungen (2,01 statt 2,16). Dagegen hilft der **Regime-Schalter**:
  RSI21 ist nur frei, solange der Portfolio-Wächter die Fades live handeln lässt. Er misst genau das Regime, in dem 6.50
  mehr verdient: 2022–25 war er beim Einstieg von 97 % aller RSI21-Signale live (2022: 88 %, ab 2023: 100 %), 2006–21 nur
  bei 5 %. Auf dem GFT-Ersatz ändert der Schalter kein Ergebnis (identische Zahlen), im alten Regime holt er die
  Auszahlungen auf 2,14 zurück.
- Der Schalter macht 11:00 nicht sicher: 2009 war der Wächter bei 55 % der RSI21-Signale live, und aus 2009 gestartete
  Konten kippten 2010.

### 3.4 Verworfen oder ohne Wirkung

- Schutz-Formen mit Vorsprung, kleinerer Größe oder engem Stop (Abschnitt 3.1).
- RSI21-Risiko 0,45–0,70 % und Noise 0,40–0,50 %: nur Rauschen (±0,3 Auszahlungen, ±100 $ ohne Richtung).
- Serien-Stopp nach 4 statt 3 Verlusten: 10,30 statt 11,18 Auszahlungen.
- X1000S abschalten: +23 $ (Rauschen). Mit 6.50 verliert X1000S kaum noch (−14 $ statt −70 $ je Jahr, breit).
- Größere Positionen unter dem Startsaldo: näher am Boden (Abschnitt 3.2).
- RSI21 ab 11:00 NY: mehr Busts im alten Regime (Abschnitt 3.3). Als Option im EA.

### 3.5 Endbewertung (`x49.py`, 16 Störungen, jeder Handelstag)

**GFT-Ersatz 2022–2025 mit GFT-nahen Spreads** (Spreads ×0,6):

| Variante | Ausz./J (Tage) | Ø Ausz. | Busts | Netto | Serien ≥ 6 | längste Ø/max | Treffer | kleinster Abstand Ø | < 100 $ | < 200 $ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6.40 Ertrag | 12,06 (30,3) | 239 $ | 0 | 2232 $ | 0,77 | 7,1 / 10 | 66,1 % | 248 $ | 0,0 % | 4,1 % |
| **6.50 Ertrag** | **12,12 (30,1)** | 267 $ | **0** | **2510 $** | 0,67 | 7,2 / 10 | 66,9 % | **261 $** | **0,0 %** | 5,9 % |
| nur Fade-Bausteine | 12,05 (30,3) | 251 $ | 0 | 2343 $ | 0,62 | 7,2 / 10 | 66,9 % | 257 $ | 0,0 % | 5,8 % |
| nur RSI21 frei ab 13:00 | 12,11 (30,2) | 249 $ | 0 | 2336 $ | 0,83 | 7,2 / 10 | 66,1 % | 252 $ | 0,0 % | 3,9 % |
| Option RSI21 ab 11:00 | 12,26 (29,8) | 278 $ | 0 | 2649 $ | 0,62 | 7,0 / 10 | 67,1 % | 255 $ | 0,0 % | 0,2 % |
| 6.40 Sicher | 7,91 (46,2) | 242 $ | 0 | 1487 $ | 0,00 | 4,5 / 5 | 69,7 % | 264 $ | 0,0 % | 1,4 % |
| **6.50 Sicher** | **8,00 (45,7)** | 244 $ | 0 | **1516 $** | 0,00 | 4,5 / 5 | 69,8 % | 274 $ | 0,0 % | 1,2 % |

**GFT-Ersatz 2022–2025 mit breiten Spreads** (wie in den Berichten 6.20–6.40):

| Variante | Ausz./J (Tage) | Ø Ausz. | Busts | Netto | Serien ≥ 6 | längste Ø/max | Treffer | kleinster Abstand Ø | < 100 $ | < 200 $ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6.40 Ertrag | 11,25 (32,5) | 235 $ | 0 | 2051 $ | 0,83 | 7,0 / 10 | 65,6 % | 255 $ | 0,0 % | 0,1 % |
| **6.50 Ertrag** | **11,66 (31,3)** | 256 $ | **0** | **2319 $** | 0,92 | 7,4 / 11 | 66,6 % | **262 $** | **0,0 %** | 0,0 % |
| nur Fade-Bausteine | 11,32 (32,3) | 250 $ | 0 | 2195 $ | 0,91 | 7,3 / 11 | 66,4 % | 262 $ | 0,0 % | 0,0 % |
| nur RSI21 frei ab 13:00 | 11,43 (32,0) | 239 $ | 0 | 2116 $ | 0,79 | 7,0 / 10 | 65,5 % | 256 $ | 0,0 % | 0,2 % |
| Option RSI21 ab 11:00 | 11,89 (30,7) | 274 $ | 0 | 2531 $ | 0,94 | 7,4 / 11 | 66,8 % | 262 $ | 0,0 % | 0,0 % |
| 6.40 Sicher | 7,11 (51,4) | 222 $ | 0 | 1225 $ | 0,02 | 4,8 / 6 | 69,3 % | 253 $ | 0,0 % | 0,9 % |
| **6.50 Sicher** | **7,11 (51,4)** | 224 $ | 0 | **1234 $** | 0,02 | 4,8 / 6 | 69,2 % | 261 $ | 0,0 % | 0,3 % |

Streuung über die 16 Störungen: 6.50 Ertrag 12,12 ± 0,54 Auszahlungen und 2510 ± 148 $ (GFT-nah), 11,66 ± 0,73 und
2319 ± 191 $ (breit); 6.40: 12,06 ± 0,62 / 2232 ± 146 $ und 11,25 ± 0,73 / 2051 ± 150 $.

**Fremddaten 2006–2021** (anderes Regime; jeder dritte Tag):

| Variante | Ausz./J | Busts/J | Bust im 1. Jahr | Netto | Serien ≥ 6 | Treffer | kleinster Abstand Ø | < 100 $ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 6.40 Ertrag | 2,16 | 0,035 | 0,9 % | 364 $ | 2,21 | 48,2 % | 207 $ | 14,6 % |
| **6.50 Ertrag** | **2,14** | **0,034** | **0,6 %** | 361 $ | 2,21 | 48,2 % | **210 $** | 14,3 % |
| 6.50 ohne Regime-Schalter | 2,01 | 0,034 | 0,6 % | 351 $ | 2,26 | 47,9 % | 203 $ | 14,4 % |
| Option RSI21 ab 11:00 | 2,14 | 0,048 | 2,5 % | 360 $ | 2,20 | 48,2 % | 209 $ | 14,4 % |
| 6.40 Sicher | 0,25 | 0,000 | 0,0 % | 49 $ | 0,21 | 54,8 % | 377 $ | 7,9 % |
| 6.50 Sicher | 0,25 | 0,000 | 0,0 % | 48 $ | 0,20 | 54,7 % | 384 $ | 6,6 % |

Was sich im Konto verschiebt (breit, 6.40 → 6.50, je Jahr): Trades 357 → 376, Handelstage ohne Trade 62,2 → 60,8, gültige
Tage 63,2 → 63,7, davon wieder verloren 3,1 → 4,4, Zyklen zuletzt durch gültige Tage / Mindestgewinn / 10-Tage-Frist
begrenzt 64/29/7 → 72/21/7 %. Ergebnis je Modul (250-Tage-Konten): RSI21 576 → 687 $, N1330 170 → 237 $, N1300 103 →
167 $, X1000S −70 → −14 $, Noise 487 → 480 $.

### 3.6 Nach Startjahr (1-Jahres-Konten)

Zellen: Auszahlungen je Jahr (Tage je Auszahlung) · Netto. Busts in allen Zellen 0.

| Variante | Start 2022 | Start 2023 | Start 2024 | Start 2025 ⁽*⁾ |
|---|---|---|---|---|
| 6.40 Ertrag, GFT-nah | 13,02 (28,1) · 2585 $ | 13,87 (26,3) · 2650 $ | 8,78 (41,6) · 1439 $ | 9,79 (37,3) · 1709 $ |
| **6.50 Ertrag, GFT-nah** | 12,59 (29,0) · **2651 $** | 13,84 (26,4) · **3097 $** | **9,29 (39,3) · 1622 $** | 9,63 (37,9) · 1664 $ |
| 6.40 Ertrag, breit | 12,14 (30,1) · 2368 $ | 12,45 (29,3) · 2360 $ | 8,83 (41,4) · 1405 $ | 8,73 (41,8) · 1335 $ |
| **6.50 Ertrag, breit** | **12,20 (29,9) · 2602 $** | **12,92 (28,3) · 2709 $** | **9,28 (39,4) · 1584 $** | 8,15 (44,8) · 1249 $ |
| 6.40 Sicher, GFT-nah | 7,77 (47,0) · 1578 $ | 8,92 (40,9) · 1760 $ | 6,46 (56,5) · 1049 $ | 7,50 (48,7) · 1418 $ |
| 6.50 Sicher, GFT-nah | 7,57 (48,3) · 1531 $ | 8,87 (41,2) · 1799 $ | 6,89 (53,0) · 1115 $ | 7,77 (47,0) · 1416 $ |

⁽*⁾ Die Ersatzdaten enden am 31.12.2025, deshalb gibt es für Start 2025 nur 128 Konten (Starts Anfang Januar).

- Netto ist in den Startjahren 2022–2024 in beiden Spread-Lagen höher.
- Die Auszahlungen sind im Mittel über die Jahre höher, aber nicht in jedem Jahr: GFT-nah Start 2022 −0,43.
- Start 2025 ist ein Zeitfenster von wenigen Tagen; dort liegt 6.50 etwas zurück.

### 3.7 Sicher

„Sicher“ handelt nur die Fades und hat die kürzesten Verlustserien. Zerlegung (16 Störungen, jeder Handelstag; breit / GFT-nah):

| Variante | Auszahlungen | Netto | Serien ≥ 6 | längste max |
|---|---:|---:|---:|---:|
| 6.40 Sicher | 7,11 / 7,91 | 1225 / 1487 $ | 0,02 / 0,00 | 6 / 5 |
| **Fade-Risiko 0,70 % (= 6.50 Sicher)** | **7,11 / 8,00** | **1234 / 1516 $** | **0,02 / 0,00** | **6 / 5** |
| N1330/N1300 frei | 7,17 / 8,19 | 1270 / 1574 $ | 0,24 / 0,00 | 7 / 5 |
| beides | 7,10 / 8,14 | 1276 / 1575 $ | 0,25 / 0,00 | 7 / 5 |

Die Freigabe von N1330/N1300 bringt auch bei „Sicher“ Netto, verlängert mit breiten Spreads aber die Serien. Das Sicher-Set
nimmt deshalb nur das Fade-Risiko 0,70 %. Wer mehr Netto will: `GueltigSchutzFrei=N1330;N1300` auch im Sicher-Set.

## 4. Was 6.50 ändert

| Eingabe | 6.40 | **6.50** | Bedeutung |
|---|---:|---:|---|
| `FadeRiskPct` | 0,75 | **0,70** | Risiko je Fade-Trade in % vom Startsaldo (× Pufferkurve) |
| `GueltigSchutzR21BisNY` (neu) | – | **13,0** | RSI21: Schutz gültiger Tage für Einstiege vor X NY; danach frei (24 = immer geschützt wie 6.40, 0 = nie) |
| `GueltigSchutzR21Regime` (neu) | – | **true** | RSI21 ab `GueltigSchutzR21BisNY` nur frei, solange der Portfolio-Wächter die Fades live handeln lässt |
| `GueltigSchutzFrei` (neu) | – | **N1330;N1300** | Fade-Module ohne Schutz gültiger Tage (leer = alle geschützt wie 6.40) |
| Sicher-Set: `GueltigSchutzFrei` | – | **leer** | Sicher: nur das Fade-Risiko ändert sich |

Verhalten:

- **Schutz gültiger Tage:** Wann er greift, ist unverändert (heute realisiert ≥ 50,50 $ in beiden Kommissions-Lesarten, dem
  Zyklus fehlen ohne heute noch gültige Tage, bis 17:00 NY). Neu ist nur, *wen* er sperrt:
  - Noise, DEADBAND und alle Fades außer `GueltigSchutzFrei`: keine neuen Einstiege (wie 6.40).
  - RSI21: keine neuen Einstiege vor 13:00 NY. Ab 13:00 NY neue Einstiege, wenn der Portfolio-Wächter live ist.
  - N1330 und N1300: handeln wie an jedem anderen Tag (Wächter, Serien-Stopp, News-Fenster usw. gelten weiter).
- **Uhrzeit und Regime** werden zum Open der laufenden M5-Kerze bestimmt, wie im Replikat. Der Portfolio-Wächter wird genau
  wie für die Fades gerechnet (PF der letzten 200 virtuellen Fade-Signale, die vor diesem Zeitpunkt feststanden, > 1,15;
  unabhängig von `FadeWaechterModus`), einmal je M5-Kerze. Sind die Fades nicht geladen oder ist die Historie eines Moduls
  noch unvollständig, gilt das Regime als nicht live: RSI21 bleibt dann geschützt.
- **Journal:** `SCHUTZ GUELTIGER TAG - … keine neuen Einstiege (Noise, Fades ausser N1330,N1300, RSI21 vor 13:00 NY oder ohne
  Fade-Regime) bis 17:00 NY`. Beim Start: `6.40 Auszahlungstakt | … Schutz gueltiger Tage AN (6.50: …)`. Namen in
  `GueltigSchutzFrei`, die kein Fade-Modul sind, meldet der EA als `WARNUNG GueltigSchutzFrei`.
- **Panel:** Titel „DEADBAND LIVE 6.50 NETTO“, Zeile „Auszahlungstakt“ mit dem Umfang des Schutzes und dem Fade-Risiko,
  Status „TAG GUELTIG - Schutz bis 17:00 NY: …“.
- **Rückweg zu 6.40** im selben EA: `FadeRiskPct=0.75`, `GueltigSchutzR21BisNY=24`, `GueltigSchutzFrei=` (leer). Oder
  `rollback_6.40/` (mq5 und beide Sets). Ein 6.40-Set in den 6.50-EA geladen lässt die drei neuen Eingaben auf den
  6.50-Werten.
- **Option mehr Netto, mehr Risiko:** `GueltigSchutzR21BisNY=11` (Abschnitt 3.3; nicht empfohlen).

## 5. Prüfung

- **Kursdaten neu aufgebaut** aus den Quellen des Datenberichts (`extdata/scripts/run_all.sh`): alle fünf Dateien
  byte-identisch (SHA-256 wie im Datenbericht). GFT-Ersatz mit `mk_proxy.py` (breit) und `SPREAD_FAKTOR=0.6` (GFT-nah, in
  einer Kopie des Ordners).
- **Baseline reproduziert:** 6.40 Ertrag im Screening 11,15 / 2030 $ / Trefferquote 65,6 % (wie `x44_gft.json`), in der
  Endbewertung 12,06 / 2232 $ (GFT-nah) und 11,25 / 2051 $ (breit), Fremddaten 2,16 / 0,035 / 364 $ – alles wie im
  6.40-Bericht.
- **Replikat eng9 = eng8** mit Voreinstellungen (`t_eng9.py`): alle Zähler, Trades und Ereignisse identisch (6.40 Ertrag, mit
  und ohne Schutz, Schutz über die Modul-Bits, 6.40 Sicher; je 15 Konten).
- **Abgleich EA ↔ Replikat** (`t_port_650.py`, Protokoll `Replikat_v6/ergebnisse/t_port_650.txt`):
  1. Voreinstellungen des EA = Replikat-Variante „6.50 Ertrag“ (Fade-Risiko, Uhrzeit, Regime-Schalter, freie Module,
     Modul-Reihenfolge, Wächter).
  2. Die entscheidenden Quelltext-Stellen in EA und Replikat sind vorhanden.
  3. Entscheidung „Schutz sperrt einen neuen Einstieg“ je Modul auf 18 816 Zuständen (gültige Tage, Tagesergebnis, Zyklus,
     NY-Stunde inkl. 12:55/13:00/13:05, Regime, Modul): **identisch**.
  4. Regime für RSI21: `FadeRegimeLive` (Ringpuffer und `FadePortfolioPF` wörtlich wie in `t_port_640.py`) gegen
     `x48.r21_regime` für alle RSI21-Signale: GFT-Ersatz 1036 Signale, davon 1002 live; Fremddaten 3550, davon 182 live –
     **identisch**.
  - DEADBAND ist im EA an gültigen Tagen gesperrt wie in 6.40; im Replikat ist DEADBAND aus (`DbAktiv=false`).
- **Presets** (`t_set.py`): `DEADBAND_LIVE4_Echtbetrieb.set` enthält alle 227 Eingaben mit genau den Voreinstellungen des EA.
  Das Sicher-Set weicht nur in `R21Aktiv`, `NzAktiv`, `SerienStopp` und `GueltigSchutzFrei` ab.
- **Statische Prüfung** (`t_mq5.py`): Klammern, Format-Argumente, Deklarationen vor der Verwendung – bestanden.
- **Nicht** geprüft: Kompilieren in MetaEditor, Strategietester, Demo.

## 6. Echtbetrieb

Dateien:

- `DEADBAND_LIVE4.mq5`: Die Voreinstellungen **sind** das Echtbetrieb-Set („Ertrag“ + 6.50).
- `DEADBAND_LIVE4_Echtbetrieb.set`: dieselben Werte als Datei.
- `DEADBAND_LIVE4_650_Sicher.set`: „Sicher“ (nur Fades) mit Fade-Risiko 0,70 %.
- Rückweg: `rollback_6.40/` (mq5, `DEADBAND_LIVE4_Echtbetrieb.set`, `DEADBAND_LIVE4_640_Sicher.set`); ältere Stände in
  `rollback_6.30/`, `rollback_6.20/`, …

Inbetriebnahme:

1. `DEADBAND_LIVE4.mq5` in MetaEditor kompilieren. Erwartet: 0 Fehler.
2. **Max. Balken im Chart = Unbegrenzt** (wie 6.20/6.40). Portfolio-Wächter und RSI21-Regime brauchen 200 virtuelle Signale
   in 600 Tagen M5.
3. Strategietester: „Jeder Tick anhand realer Ticks“, XAUUSD.x M15, 2024–2026. Im Journal prüfen:
   - beim Start `6.40 Auszahlungstakt | … Schutz gueltiger Tage AN (6.50: Noise, Fades ausser N1330,N1300, RSI21 vor 13:00 NY
     oder ohne Fade-Regime)` und in der Fade-Zeile `Risiko 0.70 %`,
   - nach einem gültigen Tag `SCHUTZ GUELTIGER TAG …`, danach keine Noise-Einstiege und keine Fades außer N1330/N1300 bis
     17:00 NY; RSI21-Einstiege nur ab 13:00 NY,
   - ein N1330/N1300-Signal an einem gültigen Tag wird live gehandelt (`FADE N1330 … LONG`), andere Fades melden
     `Tag schon gueltig …`,
   - Rest wie 6.40 (Auszahlungsreife, Pufferkurve, Portfolio-Wächter).
4. Eine Woche auf einem Demokonto mit gleicher Serverzeit, dann live nur auf dem eigenen PC, EIN Chart.
5. **Auszahlung sofort beantragen,** sobald der EA „JETZT AUSZAHLUNG BEANTRAGEN“ meldet (Push), dann
   `AuszahlungAngefordertAm` setzen – wie in 6.40.

## 7. Grenzen und Hinweise

1. **Kein GFT-Datentest.** Alle Konto-Zahlen stammen vom GFT-Ersatz aus Fremddaten (bis 31.12.2025), einmal mit GFT-nahen,
   einmal mit breiten Spreads. Mit den GFT-Exporten nachrechnen: Dateien nach `data/`, dann `python prep5.py && python
   sig5.py` und `python x49.py gft`.
2. **Auszahlungen GFT-nah nur gleich:** +0,06 je Jahr ist kein belastbarer Gewinn, aber auch kein Verlust. Mit breiten Spreads
   +0,41. Nach Startjahr nicht in jedem Jahr vorn (Abschnitt 3.6).
3. **Netto-Plus hängt am heutigen Regime.** Im alten Regime 2006–21 verdient 6.50 so viel wie 6.40 (361 statt 364 $ je
   Jahr); der Regime-Schalter hält RSI21 dort geschützt.
4. **Bust-Risiko:** 0 Busts auf dem GFT-Ersatz, kein Konto näher als 100 $ am Boden, im Mittel weiter weg als 6.40.
   GFT-nah kamen etwas mehr Konten dem Boden auf < 200 $ nahe (5,9 statt 4,1 %); mit breiten Spreads weniger (0,0 statt
   0,1 %). Im alten Regime Busts wie 6.40 (0,034 statt 0,035 je Jahr, Bust im 1. Jahr 0,6 statt 0,9 %). Pufferkurve und
   Wächter unverändert – nicht lockern (Bericht 6.40, Abschnitt 3.4).
5. **Gewählt aus mehreren Varianten:** Die Uhrzeit 13:00 und die zwei freien Fades sind nach Ergebnissen gewählt. Dagegen
   stehen: Die Uhrzeit folgt aus dem Verlust-Anteil aller RSI21-Trades nach Einstiegszeit (Abschnitt 2, viel größere
   Stichprobe als die Konten-Ergebnisse) und aus dem alten Regime, nicht aus dem besten GFT-Ergebnis (das wäre 11:00). Die
   zwei Fades sind die mit den meisten gesperrten Trades und der höchsten Trefferquote. Die Auswahl wurde mit 16 und 48
   Störungen in beiden Spread-Lagen und auf den Fremddaten geprüft.
6. **Mehr Verlustserien mit breiten Spreads:** Serien ≥ 6 je Jahr 0,92 statt 0,83 (GFT-nah weniger: 0,67 statt 0,77);
   längste Serie max. 11 statt 10.
7. **Tick gegen Kerze:** Das Replikat entscheidet je M5-Kerze. Der EA rechnet Uhrzeit und Regime ebenfalls zum Open der
   laufenden M5-Kerze, den Schutz selbst laufend (wie 6.40).
8. **Nicht kompiliert, nicht im Tester** (Abschnitt 5).
9. **Lizenz** des Grid-Konzepts unverändert (Bericht 6.20, Abschnitt 10).

## Anhang: Replikat

`Replikat_v6/README.md` (Abschnitt Build 6.50):

- Motor: `eng9.py`, Bewertung: `evl9.py`
- Screening: `x48.py` (Varianten in `VAR`, `X48_SEED0` für einen zweiten Störungs-Satz), Endbewertung: `x49.py`
- Diagnosen: `pv_ana.py` (Trades nach gültigem Tag), `r21_hour.py` (RSI21 nach Einstiegsstunde), `bust_ana.py` (Busts der
  Fremddaten nach Monat)
- Prüfungen: `t_eng9.py`, `t_port_650.py`, `t_set.py`, `t_mq5.py`
- Ergebnisse: `ergebnisse/x48_*.json`, `x49_*.json` (GFT-nah: `x48_gft_spread06.json`, `x49_gft_spread06.json`),
  `t_port_650.txt`
- Kursdaten: `extdata/scripts/run_all.sh` baut die Fremddaten neu, `Replikat_v6/mk_proxy.py` den GFT-Ersatz
  (`SPREAD_FAKTOR=0.6` für GFT-nahe Spreads, nur in einer Kopie des Ordners).
