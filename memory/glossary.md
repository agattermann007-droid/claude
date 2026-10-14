# Glossar (DEADBAND / GFT)

| Term | Bedeutung |
|------|-----------|
| GFT | Goat Funded Trader Instant Premium (Prop-Firma des Nutzers) |
| Boden | Max-Loss-Level, 6 % unter Equity-Hoch, nachlaufend |
| Puffer | Abstand Equity → Boden in % vom Startsaldo |
| gültiger Tag | Tag mit ≥ 0,505 % realisiertem Gewinn |
| Zyklus | Zeit bis zur Auszahlung (≥ 10 Tage, 5 gültige Tage) |
| Reife / kMode | 1 = reif, keine Einstiege; 2 = flach, Auszahlung beantragen |
| Fade | Fehlausbruch einer Sitzungs-Range zurückhandeln |
| Portfolio-Wächter | Fades live nur bei PF der letzten 200 virtuellen Signale > 1,15 |
| S0830 | Spike-Fade NAS 8:30 (7.10) |
| LW | Larry-Williams-Volatilitätsausbruch NAS (8.00) |
| XA | Gold-Asien-Halten 18:00–3:00 NY (8.00) |
| Staffel | Konzept 8.00: viele Ströme zu verschiedenen Tageszeiten |
| Pufferkurve | DDFull/DDMin/DDMinFactor, Größe nach Puffer |
| minbuf / LwMinPuffer | Modul handelt nur ab X % Puffer |
| GueltigSchutz | keine Einstiege mehr an einem schon gültigen Tag |
| Abschluss-Ernte | offene Gewinne schließen, um den Tag gültig zu machen |
| eng6 | Python-Kontomotor des Replikats (Stand 6.10 + generische Ströme) |
| IS / OOS | Auswahl 2022–23 / Prüfung 2024–25 |
| ext | Fremddaten 2005–21 |
| Kontoerkenner | erkennt Startsaldo, Boden, Zyklus aus der Historie; geplant: Anpasser je Zustand |
