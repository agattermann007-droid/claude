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
Auszahlung ab 3 % = 300 $):

| Kennzahl | 5.10 | 6.00 Ertrag | **6.10 Ertrag** (Echtbetrieb) | 6.10 Sicher |
|---|---:|---:|---:|---:|
| Auszahlungen je Jahr | 5,51 | 7,20 | **7,56** | 5,89 |
| Auszahlung im Mittel | 361 $ | 386 $ | 365 $ | 351 $ |
| Busts je Jahr | 0,17 | 0,00 | **0,00** | 0,00 |
| Netto je Jahr | 1517 $ | 2158 $ | 2142 $ | 1601 $ |
| Serien ≥ 5 Verluste je Jahr | 11,8 | 2,26 | **1,87** | 0,62 |
| Serien ≥ 6 Verluste je Jahr | 6,15 | 0,49 | **0,36** | 0,06 |
| längste Serie: Mittel / schlimmste | 9,4 / 13 | 6,4 / 10 | **5,9 / 10** | 4,9 / 10 |
| Trefferquote | 45 % | 61 % | 63 % | 68 % |

Nach Startjahr (1-Jahres-Konten, 6.10 Ertrag): **2022: 10,1 Auszahlungen**, 2023: 8,6, 2024: 4,9, 2025: 7,9
– in keinem Startjahr ein Bust. Streuung über die 16 Störungen: 7,56 ± 0,47 Auszahlungen (Standardfehler
0,12), Busts 0.

Fremddaten 2006–2021 (anderes Regime, 4 Störungen): 6.10 Ertrag 2,05 Auszahlungen / 0,40 Busts / 515 $
je Jahr (6.00: 2,00 / 0,43 / 524 $); Sicher 0,56 / 0,33 / 104 $.

**Die Anforderungen bleiben ehrlich bewertet wie in 6.00:** 10 Auszahlungen je Jahr erreicht nur das
Startjahr 2022; im Mittel sind es 7,6. Busts 0 auf 2022–26, nicht auf 2006–21. Serien über 5 Verluste:
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

(wird nach dem Audit ergänzt)

## 5. Echtbetrieb

- `DEADBAND_LIVE4.mq5`: Voreinstellungen = Echtbetrieb („Ertrag“). Ohne Preset geladen läuft genau die
  getestete Version.
- `DEADBAND_LIVE4_Echtbetrieb.set`: dieselben Werte als Datei.
- `DEADBAND_LIVE4_610_Sicher.set`: Ausprägung „Sicher“.
- Rückweg: `rollback_6.00/`.
