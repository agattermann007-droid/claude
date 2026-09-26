# Prüfprotokoll Build 6.70 (vorab festgelegt)

Stand 26.09.2026, festgelegt **vor** den Konto-Tests der Kandidaten Z1–Z6. Vorher liefen nur die Reproduktion der Basis 6.60
(Kursdaten byte-identisch neu aufgebaut, alle Basiszahlen der Berichte exakt getroffen) und eine Diagnose der Basis
(`a70_diag.py`, `ergebnisse/a70_diag_gft.txt`):

- **Verlustserien ≥ 5** (2,36 je Jahr, 1-Jahres-Konten): 33 % ihrer Verluste stammen von Noise (Anteil an allen Verlusten 24 %),
  22 % von RSI21 (17 %). **65 %** der Verluste in einer Serie liegen am selben Tag wie der vorige Verlust.
- **Knapp verfehlte Tage:** 55,8 Handelstage je Jahr enden mit 0–50,50 $ realisiert, **48,7 davon mit einem Fade-Gewinn**.
  N1330 (46 Trades je Jahr, Treffer 80 %) und N1300 (33, 80 %) treffen ihr Ziel fast immer unter 0,71 R (Median 0,28 bzw.
  0,45 R), X0630 und X1000S in 68 % der Treffer.

Z5 und Z6 kamen nach dieser Diagnose hinzu (Tages-Cluster, Anteil Noise), ohne dass ihre Wirkung vorher gerechnet wurde.

Auftrag: **mehr Nettogewinn, mehr Auszahlungen, weniger Verlustserien.** Wie bei allen Builds seit
6.00 gilt zusätzlich: nicht mehr Bust-Risiko. Die Zahl der geprüften Varianten wird mitgezählt und im Bericht genannt.

## Basis und Daten

- Basis: **6.60** (Echtbetrieb, Branch-Stand `6af75df`, Replikat-Variante `x60` „6.60b“).
- Daten: GFT-Ersatz 2022–2025 mit breiten Spreads (`mk_proxy.py`) und mit GFT-nahen Spreads (×0,6, Ordnerkopie);
  Fremddaten 2006–2021 (anderes Regime, Sicherheit). Der Zukunftstest 2026 ist seit 6.60 **verbraucht**: Er wird nur
  berichtet, entscheidet nichts.
- Replikat: `eng11` (= `eng10` mit Voreinstellungen, geprüft mit `t_eng11.py`), Bewertung `evl11`, Screening `x70.py`, Zukunftstest `x70f.py`.

## Kennzahlen

Auszahlungen je Jahr (A), Netto je Jahr (N), Verlustserien: Serien ≥ 5 und ≥ 6 je Jahr (S5, S6) und längste Serie (Mittel,
schlimmste); dazu Busts, kleinster Abstand zum Boden (Mittel, Anteil Konten < 100 $ / < 200 $), Trefferquote.
Ein Trade ist wie bisher eine Idee (die drei Noise-Teile eines Signals zählen als ein Trade).

## Annahmekriterien (alle müssen gelten)

- **K-a Ziel:** Screening (8 Störungen, jeder 2. Handelstag), beide Spread-Lagen. Mindestens ein Ziel deutlich besser,
  keines schlechter:
  - deutlich besser: A ≥ Basis + 0,2 **oder** N ≥ Basis + 3 % **oder** S6 ≤ Basis − 20 % (und S5 ≤ Basis);
  - nicht schlechter: A ≥ Basis − 0,1, N ≥ Basis − 1 %, S5 und S6 ≤ Basis + 5 % (mindestens + 0,05 je Jahr Toleranz).
- **K-b Walk-Forward:** Parameterwerte werden mit den 1-Jahres-Konten gewählt, die 2022–2023 starten. Die Konten mit Start
  2024–2025 dürfen bei A und N nicht schlechter sein als die Basis.
- **K-c Sicherheit:** 0 Busts auf dem Ersatz; kleinster Abstand zum Boden im Mittel ≥ Basis − 10 $; Anteil Konten
  < 100 $ höchstens Basis + 0,5 Prozentpunkte; Fremddaten 2006–21: Busts je Jahr ≤ Basis + 0,005 und Bust im 1. Jahr
  ≤ Basis + 0,5 Prozentpunkte.
- **K-d Rauschen:** Endbewertung 16 Störungen, jeder Handelstag, paarweise gegen die Basis: das Ziel, für das die Änderung
  gedacht ist, besser in ≥ 12 von 16 Störungen, in beiden Spread-Lagen.
- **K-e Plateau:** Nachbarwerte eines gewählten Parameters erfüllen K-a ebenfalls (kein Einzelspitzenwert).
- **K-f Einfachheit:** höchstens zwei neue Eingaben je Änderung; Werte aus der Regelmechanik, nicht aus dem besten Ergebnis.
- **K-g Stress:** mit Kanten-Abschlag (20 % der Fade-Gewinner zufällig entfernt, auch für den Wächter) keine
  Verschlechterung der Sicherheit gegenüber der Basis unter demselben Abschlag.

Werden mehrere Kandidaten angenommen, muss auch ihre Kombination K-a bis K-g gegen die Basis erfüllen.

## Kandidaten

| Nr | Idee | Begründung (ex ante) | Werte |
|---|---|---|---|
| Z1 | **Ziel für den gültigen Tag mit Gewinnsicherung:** Erreicht ein Fade sein Ziel, würde das Schließen den Tag aber nicht gültig machen, obwohl dem Zyklus noch gültige Tage fehlen, bleibt die Position offen: Stop auf Einstieg + L × Zielweite (Gewinn gesichert), neues Ziel dort, wo das Schließen den Tag gültig macht (Schwelle + 5 %), höchstens M R vom Einstieg | Engpass sind die gültigen Tage (Bericht 6.60, Abschnitt 3: in 72 % der Zyklen zuletzt erfüllt). Ein Fade-Treffer unter der Schwelle zählt für den Takt nicht (N1330/N1300: Ziel 0,3–0,5 R, machen nie allein einen Tag gültig). Die Sicherung verhindert, dass aus dem Treffer ein Verlust wird: kein zusätzliches Verlustrisiko, keine größere Position (anders als K1 in 6.60) | Mitte L 0,5 (halbe Zielweite bleibt sicher), M 1,0 (Ziel höchstens so weit wie der Stop). Nachbarn L 0,3 / 0,7, M 0,8 / 1,2 |
| Z2 | **Tagessperre der Fades je Symbol:** nach einem Fade-Verlust im Symbol keine weiteren Fades in diesem Symbol bis 17:00 NY | Fades verlieren an Trendtagen; an einem Trendtag scheitern mehrere Fades desselben Symbols nacheinander (sieben NAS-Module, alle long). Der Serien-Stopp greift erst nach drei Verlusten über alle Module | 1 (Nachbar 2) |
| Z3 | **Fade-Einstand:** Stop auf Einstieg + 0,05 R, sobald der Fade X R im Plus war (ohne Teilgewinn) | Weniger Verlierer → weniger Serien, weniger Rückgang zum Boden. 6.30 (andere Regeln): Serien ≥ 6 −40 %, Auszahlungen −0,1 | X 0,6 (Nachbarn 0,5 / 0,75) |
| Z4 | **Serien-Stopp nach 2** statt 3 Verlusten in Folge (Rest des Tages) | direkte Begrenzung der Serien | 2 (Basis 3) |
| Z5 | **Tages-Einstiegsstopp:** keine neuen Einstiege, sobald die Equity X % vom Startsaldo unter dem Tagesstart liegt (Tagesreferenz wie die Tagesbremse) | 65 % der Serien-Verluste folgen am selben Tag auf einen Verlust; ein schlechter Tag setzt sich fort | X 0,75 (ein voller Fade-Verlust; Nachbarn 0,5 / 1,0) |
| Z6 | **Noise-Tagespause:** nach N Noise-Teilen mit Verlust keine neuen Noise-Einstiege bis 17:00 NY | Noise stellt ein Drittel der Serien-Verluste; ein Noise-Teil kann nach dem Ausstieg an einer späteren Prüfung wieder einsteigen (Fehlsignale um die Bandgrenze an einem richtungslosen Tag) | N 1 (Nachbar 2) |

## Statistik

- Paarweise je Störung (gleiche ausgelassene Signale und gleicher Schlupf für Basis und Variante).
- Anzahl der geprüften Varianten wird gezählt; bei der Endauswahl zusätzlich die Streuung über 16 Störungen.
- Absolute Zahlen sind Replikat-Schätzungen; belastbar ist der Vergleich unter gleichen Annahmen.
