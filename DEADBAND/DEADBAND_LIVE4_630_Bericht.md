# DEADBAND LIVE 4 – Build 6.30 TREFFER

Bericht vom 25.09.2026 · GFT Instant Premium 10k (Konto ab 02.09.2026)

## 1. Kurzfassung

Auftrag: die Gesamt-Trefferquote weiter ausbauen.

**Build 6.30** ändert nur die Ausstiege, nicht die Einstiege:

1. **Fades:** Liegt ein Fade 0,6 R im Plus, wird die Hälfte der Position geschlossen. Stop und Ziel bleiben.
2. **RSI21:** Liegt der Trade 1 R im Plus, geht der Stop auf Einstieg + 0,05 R.
3. **Noise:** dasselbe je Teilposition (R = Stop-Abstand des Teils).

Beide Regeln greifen erst ab der M5-Kerze nach der Einstiegskerze und nach der Mindesthaltedauer (130 s). Für den
Teilgewinn gilt zusätzlich die News-Regel. Alles andere bleibt wie 6.20 (Probability Grid, Wächter, Budget,
Kontoerkennung).

**Ergebnis** im Konto-Replikat mit allen GFT-Regeln. Gerechnet ist auf dem GFT-Ersatz aus Fremddaten 2022–2025 (16
Störungen, jeden Handelstag ein neues Konto), der Wächter arbeitet wie im EA:

| Kennzahl je Jahr | 6.20 Ertrag | **6.30 Ertrag** (Echtbetrieb) | 6.20 Sicher | **6.30 Sicher** |
|---|---:|---:|---:|---:|
| **Trefferquote** | 63,1 % | **65,0 %** | 68,5 % | **70,4 %** |
| Auszahlungen | 7,34 | **7,33** | 4,12 | **4,13** |
| Busts | 0,032 | **0,000** | 0,000 | **0,000** |
| Netto | 2152 $ | **2171 $** | 1162 $ | **1123 $** |
| Serien ≥ 5 Verluste | 2,72 | **1,98** | 0,80 | **0,53** |
| Serien ≥ 6 Verluste | 1,45 | **0,96** | 0,24 | **0,05** |
| längste Serie Ø / max | 7,6 / 13 | **7,0 / 11** | 5,5 / 10 | **4,8 / 9** |
| Fremddaten 2006–21: Treffer · Ausz. · Busts | 48,9 % · 1,97 · 0,395 | 51,1 % · 1,83 · 0,347 | 57,2 % · 0,43 · 0,246 | 59,2 % · 0,48 · 0,228 |

- **Die Trefferquote steigt um knapp 2 Punkte, ohne Auszahlungen zu kosten**, und zwar in jedem Startjahr 2022–2025
  (Abschnitt 3.4). Dazu kommen null Busts und ein Drittel weniger Serien ≥ 6 („Ertrag“) bzw. 80 % weniger
  („Sicher“).
- **Im alten Regime (2006–21)** gibt es ebenfalls mehr Treffer, weniger Busts und weniger Serien. In „Ertrag“ sinken
  die Auszahlungen dort etwas (1,83 statt 1,97), in „Sicher“ steigen sie.
- **Mehr ist teuer.** Strengere Werte derselben Regeln bringen in „Ertrag“ kaum mehr Treffer (65,9 %), aber nur noch
  5,8 Auszahlungen je Jahr. Mit weiteren Regeln, die der EA nicht hat (festes Noise-Ziel, RSI21-Teilgewinn), wären es
  67,6 % bei ebenfalls 5,8 bzw. 69,6 % bei 5,1 Auszahlungen (Abschnitt 3.3). **Über 70 % gibt es nur mit „Sicher“.**

**Warum nicht mehr?** Die Gesamt-Trefferquote wird von den zwei Trendfolge-Modulen begrenzt: Noise liegt bei 49 %,
RSI21 bei 57 %. Die Fades liegen schon bei rund 70 %. Trendfolger verdienen an wenigen großen Gewinnern.
Teilgewinne und früher Einstand machen aus vielen kleinen Verlierern kleine Gewinner, kappen aber auch die großen
Läufe. Genau das zeigte schon die Recherche zu 6.00: Über 70 % Treffer mit positivem Erwartungswert gibt es für diese
Märkte nur mit einem reinen Fade-Portfolio („Sicher“) und weniger Ertrag.

**Nicht geprüft:** Kompilieren in MetaEditor, Strategietester, Demo. Das bleibt Pflicht (Abschnitt 6).

## 2. Woraus die Trefferquote besteht

Ein Trade ist hier eine Idee: Die drei Noise-Teile eines Signals zählen zusammen als ein Trade, Teilschließungen
gehören zu ihrer Position. So zählt auch der Serien-Stopp im EA. Das MT5-Journal und das GFT-Dashboard zählen jede
Position bzw. jeden Ausstiegs-Deal einzeln und zeigen deshalb andere, meist höhere Quoten.

6.20 Ertrag auf dem GFT-Ersatz, je Jahr (Netto · Trades · Trefferquote):

| Modul | 6.20 | 6.30 |
|---|---|---|
| 10 Fades zusammen | 1573 $ · 198 · 70 % | 1550 $ · 200 · 72 % |
| Noise (NAS, Trendfolge) | 447 $ · 76 · **49 %** | 505 $ · 83 · **53 %** |
| RSI21 (Trendfolge) | 777 $ · 65 · **57 %** | 769 $ · 65 · **59 %** |
| **gesamt** | 340 Trades · **63,1 %** | 350 Trades · **65,0 %** |

Einzeln (6.20 → 6.30): N1030 74 → 74 %, N1330 81 → 82 %, X0630 68 → 68 %, X0400 63 → 62 %, N1800 73 → 71 %,
N0930 72 → 76 %, N1100 64 → 66 %, N1300 75 → 77 %, X0300S 58 → 65 %, X1000S 58 → 63 %.

Noise hat in 6.30 mehr Trades: Ein Teil, der am Einstand ausgestoppt wird, macht den Platz frei. Bei der nächsten
stündlichen Prüfung kann der Teil wieder einsteigen, so wie in 6.20 nach jedem anderen Ausstieg.

## 3. Was gesucht und geprüft wurde

### 3.1 Signal-Ebene der Fades (`pg_wr.py`)

Alle virtuellen Fade-Signale mit Grid-Regel 6.20, Fremddaten 2006–2025. Zellen: Trefferquote · R je Signal, je Periode:

| Variante | 2006–13 | 2014–21 | 2022–23 | 2024–25 |
|---|---|---|---|---|
| 6.20 (Ziel Range-Mitte) | 57,8 % · −0,025 | 54,7 % · −0,085 | 66,4 % · +0,132 | 67,2 % · +0,134 |
| Teilgewinn 50 % bei 0,5 R | 59,9 % · −0,021 | 56,9 % · −0,082 | 68,3 % · +0,107 | 69,9 % · +0,126 |
| Einstand ab 0,5 R | 65,2 % · −0,027 | 61,1 % · −0,096 | 71,7 % · +0,096 | 74,2 % · +0,115 |
| Einstand ab 0,4 R | 68,3 % · −0,015 | 63,4 % · −0,104 | 73,8 % · +0,087 | 75,9 % · +0,105 |
| Teilgewinn 0,25 R + Einstand | 75,8 % · −0,011 | 70,9 % · −0,090 | 79,0 % · +0,038 | 81,7 % · +0,062 |
| Ziel nur 60 % des Wegs | 66,3 % · −0,035 | 62,5 % · −0,104 | 72,0 % · +0,057 | 74,3 % · +0,089 |

Jede höhere Trefferquote kostet Ertrag je Signal. Ein früher Einstand hebt die Quote am stärksten, ein näheres Ziel ist
die schlechteste Art, sie zu erkaufen. Die Serien werden in jeder Variante kürzer.

### 3.2 Konto-Screening (`x42.py`, 8 Störungen)

Replikat `eng7` = `eng6` plus Teilgewinn/Einstand/Ziel für Noise (`t_eng7.py`: sonst identisch). Zellen: Auszahlungen ·
Busts · Netto · Serien ≥ 6 · Trefferquote je Jahr, GFT-Ersatz:

| Variante | Ergebnis |
|---|---|
| 6.20 Ertrag | 7,48 · 0,036 · 2211 $ · 1,33 · 63,4 % |
| *nur Fades* | |
| Einstand ab 0,4 R | 6,35 · 0,079 · 1863 $ · 0,85 · 66,4 % |
| Einstand ab 0,75 R | 7,28 · 0,072 · 2151 $ · 0,79 · 64,3 % |
| Teilgewinn 50 % bei 0,5 R | 7,05 · 0,021 · 2075 $ · 0,83 · 64,4 % |
| Teilgewinn 50 % bei 70 % des Zielwegs | 7,20 · 0,049 · 2129 $ · 1,23 · 63,8 % |
| *nur RSI21* | |
| Einstand ab 1 R | 7,35 · 0,000 · 2140 $ · 1,03 · 63,6 % |
| Teilgewinn 50 % bei 0,5 R + Einstand | 6,13 · 0,025 · 1707 $ · 0,70 · 65,0 % |
| *nur Noise* | |
| Einstand ab 1 R | 7,66 · 0,033 · 2286 $ · 1,37 · 64,1 % |
| Einstand ab 0,5 R | 7,34 · 0,054 · 2168 $ · 1,39 · 64,6 % |
| Ziel 1 R je Teil | 7,51 · 0,038 · 2154 $ · 0,90 · 64,1 % |
| *Kombinationen* | |
| Noise + RSI21 Einstand ab 1 R | 7,62 · 0,000 · 2267 $ · 1,16 · 64,3 % |
| … + Fade-Teilgewinn 50 % bei 0,5 R | 7,35 · 0,000 · 2193 $ · 0,71 · 65,5 % |
| **… + Fade-Teilgewinn 50 % bei 0,6 R** | **7,43 · 0,000 · 2195 $ · 0,89 · 65,1 %** |
| … + Fade-Teilgewinn 50 % bei 0,4 R | 7,06 · 0,000 · 2111 $ · 0,67 · 65,6 % |
| … + Fade-Einstand ab 0,75 R | 7,25 · 0,001 · 2159 $ · 0,64 · 65,3 % |
| Nachbarn: Noise-Einstand ab 0,75 / 1,5 R | 7,23 / 7,48 · 0,000 · 64,0 / 63,7 % |
| Nachbarn: RSI21-Einstand ab 0,75 / 1,5 R | 6,86 / 7,32 · 0,001 / 0,020 · 63,7 / 64,2 % |
| *mehr Treffer, nur mit den Regeln des EA 6.30* | |
| Einstand Noise + RSI21 ab 0,5 R, Fade-Teilgewinn 50 % bei 0,4 R | 5,83 · 0,000 · 1710 $ · 0,48 · 65,9 % |
| Einstand ab 0,75 R, Fade-Teilgewinn 50 % bei 0,4 R | 6,18 · 0,000 · 1866 $ · 1,03 · 64,8 % |
| Einstand ab 1 R, Fade-Teilgewinn 70 % bei 0,3 R | 5,81 · 0,000 · 1765 $ · 0,86 · 65,7 % |
| *mehr Treffer mit weiteren Regeln (nicht im EA)* | |
| Noise-Ziel 1 R, RSI21 Teilgewinn + Einstand, Fade-Teilgewinn + Einstand | 5,88 · 0,002 · 1749 $ · 0,08 · 67,8 % |
| Noise-Einstand 0,5 R, RSI21 Teilgewinn 0,5 R + Einstand, Fade-Einstand 0,4 R | 5,13 · 0,055 · 1450 $ · 0,41 · 69,6 % |
| *Sicher (nur Fades)* | |
| 6.20 Sicher | 4,14 · 0,000 · 1173 $ · 0,26 · 68,6 % |
| Teilgewinn 50 % bei 0,5 R | 3,80 · 0,000 · 1040 $ · 0,05 · 70,8 % |
| Teilgewinn 50 % bei 0,4 R | 3,51 · 0,000 · 989 $ · 0,04 · 70,8 % |
| Teilgewinn 70 % bei 0,3 R | 2,32 · 0,000 · 679 $ · 0,04 · 72,0 % |
| Einstand ab 0,4 R (nicht im EA) | 3,02 · 0,000 · 851 $ · 0,09 · 75,3 % |

- Einzelne Regeln bewegen die Gesamtquote nur um 0,2–3 Punkte, weil jede nur ein Modul trifft.
- Der Einstand für Noise und RSI21 ab 1 R kostet nichts und nimmt die Busts heraus.
- Der Fade-Teilgewinn halbiert fast die Serien ≥ 6.
- Beim RSI21-Einstand ist 1 R das Optimum dieses Rasters. Die Nachbarn 0,75 und 1,5 R sind schwächer, der Wert ist
  deshalb eher optimistisch. Für Noise liegen alle drei Einstellungen nahe beieinander.

### 3.3 Endbewertung (`x43.py`, 16 Störungen, Wächter wie im EA)

**GFT-Ersatz 2022–2025** (jeder Handelstag ein neues Konto, 1/2/3 Jahre):

| Variante | Treffer | Ausz./J | Busts/J | Netto/J | Serien ≥ 5 | Serien ≥ 6 | längste Ø / max | gültige Tage/J |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 6.20 Ertrag | 63,1 % | 7,34 | 0,032 | 2152 $ | 2,72 | 1,45 | 7,6 / 13 | 52,0 |
| 6.30, nur Noise + RSI21 Einstand | 64,0 % | 7,48 | 0,009 | 2198 $ | 2,28 | 1,19 | 7,3 / 13 | 51,5 |
| **6.30 Ertrag (Echtbetrieb)** | **65,0 %** | **7,33** | **0,000** | **2171 $** | **1,98** | **0,96** | **7,0 / 11** | 48,8 |
| 6.30, Fade-Teilgewinn bei 0,5 R | 65,3 % | 7,18 | 0,000 | 2126 $ | 1,74 | 0,75 | 7,0 / 11 | 46,7 |
| 6.30, Fade-Einstand ab 0,75 R | 65,0 % | 7,21 | 0,001 | 2140 $ | 1,93 | 0,77 | 6,5 / 12 | 49,7 |
| mehr Treffer, weitere Regeln (Noise-Ziel 1 R, RSI21 + Fade Teilgewinn und Einstand; nicht im EA) | 67,6 % | 5,84 | 0,001 | 1712 $ | 0,98 | 0,19 | 5,5 / 11 | 41,4 |
| 6.20 Sicher | 68,5 % | 4,12 | 0,000 | 1162 $ | 0,80 | 0,24 | 5,5 / 10 | 32,0 |
| **6.30 Sicher** (Fade-Teilgewinn bei 0,6 R) | **70,4 %** | **4,13** | **0,000** | **1123 $** | **0,53** | **0,05** | **4,8 / 9** | 29,8 |
| Sicher, Teilgewinn bei 0,5 R | 70,7 % | 3,77 | 0,000 | 1035 $ | 0,34 | 0,05 | 4,6 / 8 | 25,8 |
| Sicher, Teilgewinn bei 70 % des Zielwegs | 70,2 % | 4,11 | 0,000 | 1137 $ | 0,76 | 0,24 | 5,5 / 10 | 29,5 |
| Sicher, mehr Treffer (Fade-Einstand ab 0,4 R; nicht im EA) | 75,0 % | 2,94 | 0,000 | 829 $ | 0,29 | 0,07 | 4,6 / 8 | 24,5 |

Streuung über die 16 Störungen: Trefferquote ±0,4–0,8 Punkte, Auszahlungen ±0,3–0,5. Der Abstand der Trefferquoten
liegt damit klar über der Streuung. Die Auszahlungen von 6.20 und 6.30 sind gleich.

**Fremddaten 2006–2021** (anderes Regime; jeder dritte Tag):

| Variante | Treffer | Ausz./J | Busts/J | Netto/J | Serien ≥ 5 | Serien ≥ 6 | längste Ø / max |
|---|---:|---:|---:|---:|---:|---:|---:|
| 6.20 Ertrag | 48,9 % | 1,97 | 0,395 | 497 $ | 4,58 | 2,81 | 9,8 / 18 |
| 6.30, nur Noise + RSI21 Einstand | 50,5 % | 1,83 | 0,404 | 460 $ | 4,35 | 2,50 | 9,8 / 16 |
| **6.30 Ertrag (Echtbetrieb)** | **51,1 %** | **1,83** | **0,347** | **481 $** | **4,36** | **2,47** | **9,7 / 16** |
| mehr Treffer, weitere Regeln (nicht im EA) | 56,1 % | 1,52 | 0,311 | 372 $ | 3,40 | 1,90 | 8,4 / 14 |
| 6.20 Sicher | 57,2 % | 0,43 | 0,246 | 82 $ | 0,76 | 0,31 | 5,6 / 10 |
| **6.30 Sicher** | **59,2 %** | **0,48** | **0,228** | **97 $** | **0,74** | **0,31** | **5,6 / 10** |

Die Voreinstellung ist die günstige Stufe. Erst der Fade-Teilgewinn senkt im alten Regime die Busts; der Einstand
allein tut das nicht.

### 3.4 Startjahre (1-Jahres-Konten, GFT-Ersatz)

Zellen: Auszahlungen · Busts · Serien ≥ 6 · Trefferquote.

| Variante | Start 2022 | Start 2023 | Start 2024 | Start 2025 ⁽*⁾ |
|---|---|---|---|---|
| 6.20 Ertrag | 8,56 · 0,05 · 1,16 · 66,8 % | 8,26 · 0,05 · 2,05 · 62,6 % | 5,07 · 0 · 0,94 · 60,9 % | 4,60 · 0 · 0,75 · 63,6 % |
| **6.30 Ertrag** | **8,46 · 0 · 0,77 · 68,3 %** | **8,20 · 0 · 1,66 · 64,9 %** | **5,10 · 0 · 0,30 · 62,7 %** | **4,42 · 0 · 0,29 · 64,2 %** |
| 6.20 Sicher | 4,30 · 0 · 0,00 · 72,3 % | 4,42 · 0 · 0,05 · 68,1 % | 3,44 · 0 · 0,62 · 66,2 % | 3,43 · 0 · 0,78 · 69,9 % |
| **6.30 Sicher** | **4,08 · 0 · 0,00 · 73,6 %** | **4,38 · 0 · 0,06 · 69,5 %** | **3,60 · 0 · 0,07 · 69,1 %** | **3,72 · 0 · 0,09 · 71,9 %** |

⁽*⁾ Die Ersatzdaten enden am 31.12.2025, deshalb gibt es für Start 2025 nur wenige Konten.

Die Trefferquote steigt in jedem Startjahr. Die Serien ≥ 6 sinken in „Ertrag“ in jedem Startjahr, in „Sicher“ ab Start
2024 deutlich (2022/23 waren sie dort schon fast null). Die Auszahlungen liegen jeweils im Rahmen der Streuung.

## 4. Was 6.30 ändert

| Eingabe | Wert | Bedeutung |
|---|---:|---|
| `FadeT1R` | 0,6 | Fade: ab X R (R = Stop-Abstand beim Einstieg) wird `FadeT1Anteil` geschlossen, Stop und Ziel bleiben (0 = aus, wie 6.20) |
| `FadeT1Anteil` | 0,5 | Anteil der Fade-Position (0,1–0,9) |
| `R21EinstandAbR` | 1,0 | RSI21: Stop auf Einstand + `EinstandPlusR`, sobald der Kurs X R im Plus war (0 = aus). Nicht nach einer Wochenend-Wiederaufnahme |
| `NzEinstandAbR` | 1,0 | Noise: je Teil Stop auf Einstand + `EinstandPlusR` ab X R (R = Stop-Abstand des Teils; 0 = aus) |
| `EinstandPlusR` | 0,05 | neuer Stop = Einstieg + X R: deckt Spread und Kosten, der Trade endet als kleiner Treffer |

> **Strengere Werte lohnen nicht.** `R21EinstandAbR=0.5`, `NzEinstandAbR=0.5` und `FadeT1R=0.4` bringen im Screening
> 65,9 % Treffer, aber nur 5,8 statt 7,4 Auszahlungen je Jahr (Abschnitt 3.2). Wer eine deutlich höhere Trefferquote
> will, nimmt „Sicher“ (`DEADBAND_LIVE4_630_Sicher.set`, 70,4 %).

Verhalten:

- **Zeitpunkt wie im Replikat:** Teilgewinn und Einstand erst ab der M5-Kerze nach der Einstiegskerze und nach
  `MinHalteSek` (130 s). So kann ein Einstand-Stop nie einen Gewinn unter 2 Minuten Haltedauer schließen.
- **Teilgewinn nach der Gewinn-/News-Regel** (`GewinnSchlussOk`). Ist die Teilmenge kleiner als das Mindestlot oder
  bliebe weniger als das Mindestlot übrig, entfällt der Teilgewinn. Das Replikat rechnet ebenso.
- **Neustart:** Ein Stop im Plus heißt „Einstand erledigt“. Ein Ausstiegs-Deal in der Historie der Position heißt
  „Teilgewinn erledigt“. Das R eines Trades mit Einstand-Stop kommt aus der Eröffnungs-Order. Die Abschluss-Ernte
  rechnet deshalb auch nach einem Neustart mit dem richtigen R.
- **Wochenende:** Eine RSI21-Position, die nach dem Wochenende wieder aufgenommen wird, bekommt keinen Einstand (wie
  im Replikat). Ein schon gesetzter Einstand-Stop wird bei der Wiederaufnahme übernommen.
- **Journal:**
  - `FADE X0400 Teilgewinn 0.05 von 0.11 Lot bei 0.60 R (Stop und Ziel bleiben)`
  - `RSI21: Stop auf Einstand … (Einstieg + 0.05 R) - Kurs war 1.00 R im Plus`
  - `NOISE Teil #…: Stop auf Einstand …`
  - beim Start die Zeile `6.30 Trefferquote | …`
- **Panel:** Zeile „Trefferquote“ mit den Einstellungen und der Zahl der Teilgewinne seit dem Start.
- **Serien-Stopp:** Er zählt eine Position mit allen Teilschließungen als einen Trade (wie seit 5.10). Ein Trade, der
  nach dem Teilgewinn am Stop endet, kann deshalb insgesamt ein Treffer oder ein Verlust sein.

## 5. Prüfung

- **Replikat eng7 = eng6** mit ausgeschalteten 6.30-Regeln (`t_eng7.py`): gleiche Zähler, Trades und Auszahlungen in
  allen geprüften Konten.
  - Einzige gewollte Abweichung: Wird ein Noise-Teil von der Abschluss-Ernte teilweise geschlossen, zählt eng7 den
    Teilgewinn zum Trade. Der EA tut das seit 5.10 im Serien-Stopp.
  - Auf die Endzahlen von 6.20 hat das keinen sichtbaren Einfluss (x43 = x41 auf allen Stellen).
- **Abgleich EA ↔ Replikat** (`t_port_630.py`): Die Entscheidungen von `FadeTeilgewinn`, `EinstandSetzen` und
  `NzEinstand` sind wörtlich nach Python übertragen und laufen Kerze für Kerze auf echten Signalen:
  - Fades: 10 Module, 1 580 Signale, Teilgewinn bei 0,6 R
  - RSI21-Folgesignale: 835 Signale, Einstand ab 1 R
  - Noise: alle drei Teile, 1 007 Signale

  Ergebnis: **identisch** mit der Replikat-Logik (Auslösekerze, Teilmenge, R je Signal). Protokoll:
  `Replikat_v6/ergebnisse/t_port_630.txt`.
- **Statische Prüfung** (`t_mq5.py`): Klammern, Format-Argumente, Deklarationen vor der Verwendung – bestanden.
- **Gegenlesen** durch einen Sub-Agenten: REVIEW_TEIL
- **Nicht** geprüft: Kompilieren in MetaEditor, Strategietester, Demo.

## 6. Echtbetrieb

Dateien:

- `DEADBAND_LIVE4.mq5`: Die Voreinstellungen **sind** das Echtbetrieb-Set („Ertrag“ + Grid + 6.30).
- `DEADBAND_LIVE4_Echtbetrieb.set`: dieselben Werte als Datei.
- `DEADBAND_LIVE4_630_Sicher.set`: „Sicher“ (nur Fades) + Grid + Fade-Teilgewinn.
- Rückweg:
  - `FadeT1R=0`, `R21EinstandAbR=0`, `NzEinstandAbR=0` (Handelslogik wie 6.20)
  - oder `rollback_6.20/` (mq5 und beide Sets); ältere Stände in `rollback_6.10/`, `rollback_6.00/`, …

Inbetriebnahme:

1. `DEADBAND_LIVE4.mq5` in MetaEditor kompilieren. Erwartet: 0 Fehler.
2. **Max. Balken im Chart = Unbegrenzt** (wie 6.20).
3. Strategietester: „Jeder Tick anhand realer Ticks“, XAUUSD.x M15, 2024–2026. Im Journal prüfen:
   - `6.30 Trefferquote | Fade-Teilgewinn 50 % ab 0.60 R …` beim Start,
   - Fade-Trades mit `Teilgewinn … Lot bei 0.60 R`, danach das Ziel (`Ziel … gesetzt`) für den Rest,
   - RSI21 und Noise mit `Stop auf Einstand …` nur nach mindestens 1 R Vorlauf und nie in der Einstiegskerze,
   - sonst alles wie 6.20.
4. Eine Woche auf einem Demokonto mit gleicher Serverzeit, dann live nur auf dem eigenen PC, EIN Chart.

## 7. Grenzen und Hinweise

1. **Kein GFT-Datentest.** Die Konto-Zahlen stammen vom GFT-Ersatz aus Fremddaten (breitere Spreads). Nachrechnen:
   GFT-Exporte nach `data/`, dann `python prep5.py && python sig5.py && python x43.py gft`.
2. **Tick gegen Kerze.** Das Replikat löst Teilgewinn und Einstand am Hoch bzw. Tief der M5-Kerze aus. Der EA
   reagiert auf den laufenden Kurs.
   - Ein kurzer Ausschlag zwischen zwei Ticks kann verpasst werden.
   - Ein Einstand-Stop kann in derselben Kerze getroffen werden, in der er gesetzt wurde. Das Replikat prüft ihn erst ab
     der nächsten Kerze.
   - Beides sind kleine Unterschiede.
3. **Trefferquote ist nicht Ertrag.** Die günstige Stufe kostet nichts. Jede weitere Stufe kostet Auszahlungen
   (Abschnitt 3.3). Über 70 % gibt es nur mit „Sicher“.
4. **Nicht kompiliert, nicht im Tester** (Abschnitt 5).
5. **Lizenz** des Grid-Konzepts unverändert (Bericht 6.20, Abschnitt 10).

## Anhang: Replikat

`Replikat_v6/README.md` (Abschnitt Build 6.30):

- Motor: `eng7.py`
- Signal-Ebene: `pg_wr.py`
- Screening: `x42.py`
- Endbewertung: `x43.py`
- Prüfungen: `t_eng7.py`, `t_port_630.py`
- Ergebnisse: `ergebnisse/x42_gft.json`, `x43_gft.json`, `x43_ext.json`
