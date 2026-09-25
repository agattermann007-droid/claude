# Prüfprotokoll Build 6.60 (vorab festgelegt)

Stand 25.09.2026, festgelegt **vor** den Konto-Tests der Kandidaten K2 und K3. Ziel: Verbesserungen nur übernehmen, wenn sie
nicht an einer einzelnen Marktphase hängen. Die Zahl der geprüften Varianten wird mitgezählt und im Bericht genannt.

## Basis und Daten

- Basis: **6.50 Ertrag** (Echtbetrieb, Branch-Stand `bc30506`), zum Vergleich 6.40 Ertrag.
- Daten: GFT-Ersatz 2022–2025 mit breiten Spreads (`mk_proxy.py`) und mit GFT-nahen Spreads (×0,6, Ordnerkopie);
  Fremddaten 2006–2021 (anderes Regime); Gold zusätzlich bis 02.09.2026 (jüngster Abschnitt, für 6.20–6.50 unbenutzt).
- Replikat: `eng10` (= `eng9` mit Voreinstellungen, geprüft mit `t_eng10.py`: 45 Konten identisch), Bewertung `evl10`.

## Kennzahlen

Tage je Auszahlung (T), Auszahlungen je Jahr (A), Netto je Jahr (N), Busts je Jahr, kleinster Abstand zum Boden
(Mittel, Anteil Konten < 100 $ / < 200 $), Serien ≥ 6.

## Annahmekriterien (alle müssen gelten)

- **K-a Ziel:** Screening (8 Störungen, jeder 2. Handelstag), beide Spread-Lagen: A ≥ Basis − 0,1 und N ≥ Basis + 3 %,
  oder A ≥ Basis + 0,3 und N ≥ Basis − 1 %.
- **K-b Walk-Forward:** Entschieden wird mit den 1-Jahres-Konten, die 2022–2023 starten. Die Konten mit Start 2024–2025
  (jüngste Daten, danach nicht mehr angepasst) dürfen bei A und N nicht schlechter sein als die Basis.
- **K-c Sicherheit:** 0 Busts auf dem Ersatz; kleinster Abstand zum Boden im Mittel ≥ Basis − 10 $; Anteil Konten
  < 100 $ höchstens Basis + 0,5 Prozentpunkte; Fremddaten 2006–21: Busts je Jahr ≤ Basis + 0,005 und Bust im 1. Jahr
  ≤ Basis + 0,5 Prozentpunkte.
- **K-d Rauschen:** Endbewertung 16 Störungen, paarweise gegen die Basis: Hauptziel besser in ≥ 12 von 16 Störungen,
  in beiden Spread-Lagen.
- **K-e Plateau:** Nachbarwerte eines gewählten Parameters erfüllen K-a ebenfalls (kein Einzelspitzenwert).
- **K-f Einfachheit:** höchstens zwei neue Eingaben je Änderung; Werte möglichst aus Regelmechanik oder Literatur, nicht
  aus dem besten Ergebnis.
- **K-g Stress:** mit Kanten-Abschlag (20 % der Fade-Gewinner zufällig entfernt, auch für den Wächter) keine
  Verschlechterung der Sicherheit gegenüber der Basis unter demselben Abschlag.

## Kandidaten

| Nr | Idee | Begründung (ex ante) | Stand bei Festlegung |
|---|---|---|---|
| K1 | Größe für den gültigen Tag: Fade so groß, dass der Ziel-Treffer den Tag allein gültig macht (Deckel 0,8–0,9 %) | GFT-Schwelle 0,5 % ist absolut; viele Fade-Ziele liegen unter 0,76 R | **schon vor diesem Protokoll gescreent**: +0,1 Auszahlungen (Rauschen), Risiko näher an der harten −1-%-Grenze → verworfen |
| K2 | NAS-Fades unverändert auf **US500** übertragen (gleiche Uhrzeiten, Puffer, Ziele, Grid-Regel, Portfolio-Wächter) | 0DTE-Dämpfung ist für den S&P 500 belegt (Adams et al. 2025), für NAS100 nur übertragen; GFT bietet SPX500 ohne Kommission | offen; Signal-Ebene zuerst, dann Konto |
| K3 | Schocktag-Filter für Fades: keine Fades nach bzw. an Tagen mit außergewöhnlicher Bewegung | Literatur: Momentum an volatilen/News-Tagen und bei negativem Gamma (Gao et al. 2018, Baltussen et al. 2021); Fade-Verluste ballen sich an Schocktagen | offen; Größen vorab: Vortags-Spanne / ATR, Tagesbewegung bis zum Signal / ATR, ATR14 / ATR100. Übernahme nur bei gleichgerichtetem Zusammenhang in 2006–13, 2014–21, 2022–25 und auf beiden Symbolen |
| K4 | Handeln, während GFT die Auszahlung bearbeitet | spart ~2 Handelstage je Zyklus | **verworfen ohne Test**: GFT verlangt „no open trades … to receive a reward“; ob Handel bis zur Buchung erlaubt ist, ist nicht belegt; Risiko für die Auszahlung |
| K5 | Fades nur in Trendrichtung bzw. gespiegelte Module | klassische Regel „Dips im Aufwärtstrend kaufen“ | **verworfen** (Signal-Ebene `a60_sig.py`): Spiegel-Module verlieren auch 2022–25; Trendfilter kostet 2022–25 rund 40 % des Ertrags |

## Statistik

- Paarweise je Störung (gleiche ausgelassene Signale und gleicher Schlupf für Basis und Variante).
- Anzahl der geprüften Varianten wird gezählt; bei der Endauswahl zusätzlich die Streuung über 16 Störungen.
- Absolute Zahlen sind Replikat-Schätzungen; belastbar ist der Vergleich unter gleichen Annahmen.
