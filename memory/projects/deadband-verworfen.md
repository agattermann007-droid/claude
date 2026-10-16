# DEADBAND – Verworfene Ideen (nicht wiederholen)

Gesammelt aus den Berichten 6.x–12.00. „(alter Motor)“ = Kontoebene mit dem fehlerhaften Nachbau v11 oder älter
gerechnet (Noise-Prüfungen fielen aus) – nur dann neu prüfen, wenn es einen konkreten Grund gibt.

## Grundsätzliches
- **60 % Treffer bei CRV 1:2** gibt es mit reiner Price Action nicht (8.280 Varianten, Maximum ≈ 41 %).
- **Konsistenzregel (Instant GOAT)** kostet vor allem Auszahlungen → Premium ohne Regel ist besser.
- **Niedrige Trefferquote + enger Stop** schadet unter GFT-Regeln, auch bei positivem Erwartungswert: weniger
  gültige Tage, mehr Serien-Stopps, Busts am trailenden 6-%-Boden (V12: IMOM, ORB).
- Alle Busts in Tests waren Brüche des nachlaufenden Bodens.

## Ströme / Einstiege
| Idee | Runde | Ergebnis |
|---|---|---|
| ORB 5/15/30 min (+Mittelpunkt) | V8, V12 | V8 verworfen; V12 auf Kontoebene 741–2.982 Busts |
| Gao-/Intraday-Momentum (IMOM), NAS-Eröffnungsmomentum | V8, V12 | Strom +0,2 R, Konto schlechter (0 von 36 Varianten) |
| 9:30-Kerze, Silver Bullet, Judas, Turtle Soup, Magic Hours | V8 | ohne Vorteil |
| Gold-IB-Rücklauf, EMA-/VWAP-Pullback, VWAP-Fade, Gap-Fade, Bollinger | V8 | ohne Vorteil |
| Vortages-Ausbruch/-Sweep, Wochen-Eröffnung, Turn of Month | V8 | ohne Vorteil |
| Makro-Tag-Filter, Vola-Perzentil, Spike-Fade zu anderen Zeiten | V8 | ohne Vorteil |
| Connors RSI(2) NAS | V8 | robust, aber nicht übernommen (Überschneidung) |
| Ausbruch statt Fade (alle 10 Fade-Ranges), Gold-Trend-Ausbruch (D1-SMA) | V12 | 2011–16 ohne Vorteil |
| Sweep-Reclaim-Scan Gold 2.784 / NAS 1.824 Varianten | V11 | NAS-Kandidaten im Konto schlechter (NAS-Long gesättigt) |
| GPDF (Gold unter Vortagestief → Long) | V11 | Gold-Drift: OANDA 2010–16 ohne Vorteil, 2014–15 negativ |
| Bestätigungs-Einstieg (+0,1/0,2/0,3 R per Stop-Order) | V11 | in keinem der 18 Ströme besser, bei SR klar schlechter |
| Tick-Fades N1030+N1100 (0,75 % und 0,50 %) | V11, V12 | Busts 10.10.2013 und 21.07.2025 |
| N1100 allein im Tick | V12 | 2024–25 −0,47 Ausz./J |
| N1800 im Tick | V11 | schon in der Auswahl schlechter |

## SR
| Variante | Ergebnis (V12, korrigierter Motor) |
|---|---|
| SR-Risiko 0,05 % | überall schlechter |
| SR-Risiko 0,15–0,30 % | Busts in 2011–15 (14 / 198 / 252 / 364) |
| SR nur bei Fades aus / nur bei Fades live | 2022 −1,72 / −0,94 Ausz./J |
| nur SRPRE; je eine Marke weg | schlechter (ohne SRPRE: 2017–20 −1,07) |
| SR-Trades nicht im Serienzähler | 2022 −1,38, 1 Bust |

## Konto-Mechanik
| Variante | Runde | Ergebnis |
|---|---|---|
| Serien-Stopp aus / nach 2 / nach 4 | V11 (alter Motor), V12 | schlechter (aus: 2022 −0,96; 4: −1,33; je 1 Bust) |
| ohne Schutz gültiger Tage | V11 (alter Motor) | 2022 −2,02, 2023 −2,22 |
| Abschluss-Ernte 0,2 / 0,5 R, 10 % Reserve | V11 (alter Motor) | im Rauschen |
| RSI21-Schutz bis 12 / 14 Uhr; Gewinn-Ernte ab 0,5 R | V11 (alter Motor) | Rauschen / ±0 |
| Regime-Größe ×1,25 (RSI21 + Noise bei Fades aus) | V12 | 2017–20 −0,28, 45 Busts |
| mehr Risiko je Strom, Ströme abschalten, höhere Auszahlungsschwelle | ≤ V10 | nicht hilfreich |
| Verlierer früh schließen, Einstand/Trailing für Fades/LW/TD/XA, Stop-and-Reverse | ≤ V10 | nicht hilfreich |
| Erschöpfungsfilter, Pullback-Limit-Einstieg | ≤ V10 | nicht hilfreich |
| Anpasser-Faktoren je Kontozustand ≠ 1 | 8.10 | kein Satz bestand Auswahl + Prüfung (bester Auswahl-Satz 17,0 → Prüfung 8,6); Anpasser im EA an, aber alle Faktoren ×1 = neutral |
| Pufferkurve 3/1/0,1 (offensiv) | V8 | +0,6 Ausz./J, aber Pleiten auf Fremddaten |
