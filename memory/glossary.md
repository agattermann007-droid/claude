# Glossar (DEADBAND / GFT)

## Konto und Regeln (GFT Instant Premium)
| Term | Bedeutung |
|------|-----------|
| GFT | Goat Funded Trader – Prop-Firma des Nutzers, Konto Instant Premium 10k |
| Instant GOAT | Alternative mit 15-%-Konsistenzregel (nur auf ausdrücklichen Wunsch) |
| Boden | Max-Loss-Level, 6 % unter Equity-Hoch, nachlaufend (nach jeder Auszahlung neu); darunter = Bust |
| Puffer | Abstand Equity → Boden in % vom Startsaldo |
| Bust / Pleite | Bruch einer Firmenregel (Boden, Floating −1 %, Tag −3 %) → Konto weg |
| gültiger Tag | Tag mit ≥ 0,5 % realisiert + 0,50 $ Reserve (50,50 $ bei 10k) |
| Zyklus | Zeit bis zur Auszahlung: ≥ 14 Kalendertage ab erstem Trade (Kauf ab 21.09.2026) und 5 gültige Tage |
| Mindestauszahlung | 105 $ Anteil (EA) → 131,25 $ Gewinn bei 80 % Split; Deckel 6 % für die ersten 2 Auszahlungen; 3 % Gebühr |
| 120-s-Regel | Gewinne aus Trades < 120 s werden gestrichen; EA setzt Ziele erst ab 130 s (`FadeZielAbSek`) |
| Floating-Regel | offene Verluste ≤ 1,0 % (strenge Lesart inkl. Swap/Kommission); EA-Bremse 0,8 % gestuft |
| Tagesstart | 17:00 NY; Tagesstopp des EA 2,4 % |
| Server-Zeit | NY + 7 h fest |

## Module und Ströme
| Term | Bedeutung |
|------|-----------|
| Fades / Listen-Fades | 10 Module `FADE_STANDARD`: Fehlausbruch einer Sitzungs-Range (Docht raus, M5-Schluss zurück), Einstieg nächstes M5-Open, 0,75 % |
| N1030 … X1000S | Fade-Namen = Symbol + Range-Start NY (N = NAS, X = Gold; S = Short): N1030, N1330, X0630, X0400, N1800, N0930, N1100, N1300, X0300S, X1000S |
| Portfolio-Wächter | Fades live nur bei PF der letzten 200 virtuellen Fade-Signale > 1,15 (600 Tage) |
| Fade-Regime live / „Fades aus“ | Wächter live bzw. nicht; 2011–21 fast immer aus, ab 2023 fast immer live |
| Probability Grid | Filter für Fades (M5-Swing-Statistik), N1800 ohne Grid |
| S0830 | Spike-Fade NAS: Kauf 9:00 nach Abwärtsspike ab 8:30 (7.10) |
| LW | Larry-Williams-Ausbruch NAS, 0,5 %, nur ab 4 % Puffer (8.00) |
| XA | Gold-Asien Long 18:00 → 3:00 NY über 24-h-Schnitt (8.00) |
| TD | Trend-Day NAS Long 14:00 bei Tagesbewegung ≥ 0,75 ATR (8.10) |
| RSI21 | RSI-Pullback M15/M30/H1, Folgesignal, Einstand ab 1 R, 0,5 % × Gewicht |
| Noise | NAS-Noise-Momentum long, 3 Teile, Prüfungen stündlich 10–15 Uhr, 0,45 % |
| SR | Liquidity-Sweep-Reclaim NAS im Tick, Ziel 2 R, 0,10 % (9.00/10.00); Marken SRIB, SRPRE (Short), SRH12, SRPDN |
| SrListe | Marken-Definition, 12 oder 19 Felder (ab 11.00: Symbol, Stop-/Ziel-Art, CRV, Risiko, Range-Filter, Wächter) |
| Tick-Fade | Fade mit Einstieg im Tick beim Rücklauf in die Range (statt nach M5-Schluss) |
| SRT1030 / SRT1100 | N1030/N1100 als Tick-Fade (Modul vom SR-Typ); SRT1030 ist in 12.00 Standard |
| GPDF | Gold-Vortagestief-Sweep Long (11.00 Testschalter, verworfen: Drift) |
| IMOM | Intraday-Momentum NAS (Vortagsschluss → 10:00/10:30) – in 12.00 verworfen |
| ORB | Opening-Range-Breakout – verworfen (V8 und V12) |
| Staffel | Konzept 8.00: viele Ströme zu verschiedenen Tageszeiten |

## Konto-Logik im EA
| Term | Bedeutung |
|------|-----------|
| Pufferkurve | Größenfaktor nach Puffer: voll ab 3,5 %, ×0,1 bei ≤ 1,25 % (`DDFullPct/DDMinPct/DDMinFactor`) |
| BelowStart | Größe ×0,95 unter Startsaldo |
| Schutz gültiger Tage / GueltigSchutz | keine neuen Einstiege an einem schon gültigen Tag, solange noch gültige Tage fehlen (Ausnahmen: N1330/N1300; RSI21 erst ab 13:00 NY und nur bei live Fades frei) |
| Abschluss-Ernte | offene Gewinne (MFE ≥ 0,3 R) schließen, um den Tag gültig zu machen |
| Gewinn-Ernte | nur RSI21 |
| Reife / Schließen bei Reife | Zyklus erfüllt → flach, Auszahlung beantragen |
| Serien-Stopp | nach 3 Verlusten in Folge keine Einstiege bis 17:00 NY |
| Budgets | offenes Stop-Risiko ≤ 0,9 % gesamt und ≤ 0,9 % je Idee (Symbol + Richtung) |
| Idee | Symbol + Richtung (für Budget, Margin ≤ 70 %, Hedging-Sperre) |
| Wochenende flach | Freitag 16:45 schließen, RSI21 Sonntag/Montag wiederaufnehmen |
| RegimeGroesse | RSI21/Noise × Faktor bei Fades aus (6.70, nur ≤ 1; > 1 in 12.00 verworfen) |
| Kontoerkenner / Anpasser | Zustand des Kontos (REIF, TIEF, LEICHT, …); Anpasser-Faktoren je Zustand, Voreinstellung neutral (8.10) |
| minbuf / LwMinPuffer | Modul handelt nur ab X % Puffer |
| Magic | `MagicBase + 50 + Modulindex` für Fade-/Sondermodule (MAXFADE 22) |

## Nachbau und Methode
| Term | Bedeutung |
|------|-----------|
| Replikat / Nachbau | Python/numba-Nachbau des EA auf M1 mit Kontomotor (aktuell v12, `DEADBAND/V12/Replikat_v12/`) |
| eng11 | Kontomotor des Nachbaus v11/v12 (v12: zwei Fehler behoben) |
| eng6 | älterer Kontomotor (Replikat v5/v6, Stand 6.10) |
| Stromebene / Kontoebene | R je Trade eines Stroms allein / ganze Konten unter GFT-Regeln |
| rollierende Konten | alle 7 Tage ein frisches 10k-Konto, 1 Jahr Laufzeit |
| Störung / Seed | Lauf mit 3 % anderen Signalen; Vergleiche gepaart über 16 (Entscheidung 32) Seeds, Differenz ± SE |
| Rauschgrenze | < ~0,4 Ausz./J bzw. ~100 $/J ist nichts nachgewiesen |
| Auswahl / Prüfung | Auswahl Kontostart 2022; Prüfung 2024-01–2025-02, 2017–20, 2011–15 (`WIN5`) |
| Schlupf | ¼ Spread auf Markt-Einstiege, Stop- und Zeit-Ausstiege (Sensitivität ohne Schlupf immer mit angeben) |
| Plateau | nur Mitte übernehmen, Nachbarparameter und -risiken mitprüfen; Gegenprobe rechnen |
| ext / erweiterter Datensatz | v12: Gold OANDA 2010–16 + Dukascopy, NAS HistData ab 2010-11 (`prep_ext.py`); früher (v6): Fremddaten 2005–21 |
| Ausz./J, $/J | Auszahlungen je Konto-Jahr; Anteil nach 80 % Split und 3 % Gebühr |
| Unabhängigkeitstest | `t12_engine_check.py`: abgeschalteter Strom darf kein Konto verändern |
| IS / OOS | (alt) Auswahl 2022–23 / Prüfung 2024–25 |
