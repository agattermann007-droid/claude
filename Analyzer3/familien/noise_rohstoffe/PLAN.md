# Familie noise_rohstoffe – Vorab-Festlegung (geschrieben vor dem ersten Ergebnislauf, 15.10.2026)

Ziel: Intraday-Momentum (Noise-Area und „market intraday momentum“, MIM) auf Rohstoffen, BTC und FX, damit Alex an mehr
Tagen ein Setup bekommt (Zielprofil Punkt 4), bei positiver Erwartung nach Kosten. Vor diesem Text wurde nur die
Datenabdeckung je Uhrzeit angesehen (keine Renditen).

## Sitzungen (Ortszeit; tz, Eröffnung, Schluss, Fensterende/Ausstieg)
| Instrument | Sitzung | Begründung |
|---|---|---|
| XAUUSD, XAGUSD | New York 8:20–13:30, Ende 13:30 | COMEX-Kernzeit (ehemaliges Parkett), 13:30 ≈ Settlement. Höchste Liquidität des Tages. |
| WTI | New York 9:00–14:30, Ende 14:30 | NYMEX-Kernzeit, 14:28–14:30 Settlement. |
| BRENT | London 8:00–16:30, Ende 16:30 | Gewählt: London-Tag. Grund: Mit der NY-Sitzung wäre Brent fast ein Doppel von WTI (gleiches Fenster, gleiche Richtung) und brächte keine zusätzlichen Setup-Tage. Der London-Tag ist der europäische Haupthandel, liegt für Alex am Vormittag und verteilt die Setups über den Tag. ICE-Settlement (19:30 London) wird bewusst nicht benutzt. |
| BTCUSD | New York 9:30–16:00, Ende 15:00 | Gewählt: US-Kassasitzung. Grund: Umsatz und Volatilität von BTC sind in den US-Stunden am höchsten. Shen/Urquhart/Wang 2022 finden die stärkste Vorhersagbarkeit in den umsatzstärksten Sitzungen. Der UTC-Tag beginnt in der illiquiden Asien-Nacht ohne Eröffnungsereignis. Ende 15:00 wie bei NAS100 (passt zu Alex). Damit nur Mo–Fr. Für MIM ist das Fenster 9:30–15:00, die „letzte halbe Stunde“ ist also 14:30–15:00. |
| EURUSD, GBPUSD, AUDUSD, USDCAD, USDCHF | London 8:00–16:00, Ende 16:00 | Gewählt: London. Grund: London ist der größte FX-Platz, und 16:00 ist das WM/Reuters-Fixing (Ende der Hauptliquidität, gebündelter Order-Flow). Elaut/Frömmel/Lampaert 2018 finden FX-Intraday-Momentum nur mit den expliziten Handelszeiten. 8 h ergeben 15 M30-Marken (NY 8–12 nur 7). Gleiche Regel für alle FX-Paare. |
| ETHUSD | wie BTC | nur Gegenprobe, wird nie ausgewählt |

## Regeln (für alle Instrumente gleich, nicht je Instrument abgestimmt)
Noise-Area (Zarattini/Aziz/Barbon 2024; `lib/noise.py`):
- **N10_end**: noise-1.0 unverändert (M30-Raster ab Eröffnung+30, Lookback 14, SMA20-Filter Vortagesschluss, erster Trade des Tages, Stop Bandmitte, Ziel 1R), Zeitausstieg Fensterende.
- **N10_480**: dieselben Signale, Bewertung nach 480 min (ab Train-Lauf 1b nach Uhrzeit, `noise.last_by_clock`; zuerst fälschlich 96 Kerzen), nur zum Vergleich.
- **PAPS_B**: Kandidat B der Familie ausstiege: alle M30-Signale mit SMA20-Filter, Wiedereinstieg nach Ausstieg, Stop Bandmitte, Teilziel 50 % bei 0,5R, danach Break-even, Rest ohne Ziel bis Fensterende.

Market intraday momentum (MIM):
- Prädiktor r1 = Schluss bei Eröffnung+30 min / Schluss der Vortagessitzung − 1. Das ist die erste halbe Stunde ab dem Vortagesschluss, wie bei Gao/Han/Li/Zhou 2018 (SPY). Wen/Gong/Ma/Xu 2021 (USO) zeigen, dass der Übernachtanteil den Großteil der Information trägt.
- Signalkerze = Kerze mit Schluss bei Fensterende − 30 min. Richtung = Vorzeichen von r1. Market-Einstieg zur nächsten Eröffnung (= Fensterende − 30). Zeitausstieg am Fensterende. Das entspricht der Handelsregel bei Gao et al. 2018, Wen et al. 2021, Elaut et al. 2018 und Shen et al. 2022: Einstieg zu Beginn der letzten halben Stunde, Schluss zum Sitzungsende.
- Stop (einfache Volatilitätsregel, k = 1): Abstand = σ_H. Das ist das Mittel der letzten 14 Sitzungen (mindestens 10) von |Schluss(Ende)/Schluss(Ende−H) − 1| für dasselbe Uhrzeitfenster, also derselbe Schätzer wie die Noise-Area, nur auf die Haltedauer H bezogen.
- **MIM_r1_none**: kein Ziel, bis Fensterende (reine Literaturregel).
- **MIM_r1_t10** / **MIM_r1_t05**: Ziel 1R / 0,5R.
- **MIM_r1_B**: Teilziel wie Kandidat B (50 % bei 0,5R, dann Break-even, Rest bis Fensterende).
- **MIM_r1r12_none**: Gao et al. Timing η(r1, r12). Long nur, wenn r1 > 0 und r12 > 0, Short nur, wenn beide < 0 (r12 = Rendite Ende−60 → Ende−30).
- **MIM_rod_none**: Prädiktor ist die Rendite vom Vortagesschluss bis Ende−30 (Rest-des-Tages) nach Baltussen/Da/Lammers/Martens 2021 (über 60 Futures inkl. Rohstoffe und Währungen).
- **MIM60_r1_none**: Einstieg Ende−60 („letzte 60 min“), σ_60, kein Ziel.

## Portfolio und Auswahl
- **P_alle** (immer berichtet): alle 10 Instrumente (ohne ETH) je Regel, eine Position je Instrument und Regel.
- **P_sel** (Auswahlregel, zählt als Variante): je Regel die Instrumente mit Train R netto > 0 UND Train R > Null-R Train. Nur auf Train.
- Kennzahlen: n, Trades/Tag, Anteil Tage mit Trade, Target vor Stop (bei Teilziel: Teilziel vor Stop, ohne Ziel: Gewinnquote), R netto, R/Tag (über alle NY-Handelstage), Trade-t, Tages-Cluster-t, Null-R, Kosten in R je Trade.

## Kandidatenregel (nur Train)
Eine Zelle (Instrument oder Portfolio × Regel) kommt in Frage, wenn: Train R netto > 0, t ≥ 2 (Trade- oder Tages-Cluster-t) und t gegen Null ≥ 2.
Unter den Kandidaten in Frage: höchstens 3, Priorität nach Train R/Tag (Ziel 4). Bei Gleichstand wird die Zelle mit Trefferquote ≥ 60 % bevorzugt.
Festhalten in `auswahl_train.json` vor dem Lauf auf 2024. Danach 2024 einmal. Kandidat nur, wenn 2024 R netto > 0, sonst verworfen.

## Nachtrag nach Train-Lauf 1 (vor jedem Blick auf 2024)
Befund Train: In der Regression der letzten halben Stunde auf r1 ist die Korrelation bei XAU (+0,10), XAG (+0,15),
GBPUSD (+0,10) und USDCAD (+0,07) positiv, mit t > 2. Der reine Vorzeichen-Trade verdient aber brutto nur 0,2–0,7 bp
je Trade, bei Kosten von 1,5–6 bp. Der Zusammenhang kommt aus Tagen mit großer Bewegung. Gao et al. 2018 (und Wen et
al. 2021 für Öl) berichten ebenfalls, dass die Vorhersagbarkeit an volatilen Tagen stärker ist.
Deshalb gibt es eine einzige zusätzliche Regel, datengetrieben und so gekennzeichnet:
- **MIM_r1_hv_none**: wie MIM_r1_none, aber nur an Tagen mit |r1| > Mittel von |r1| der letzten 14 Sitzungen
  (k = 1, Lookback 14 wie überall). Sie zählt als eigene Variante und muss dieselbe Kandidatenregel erfüllen.
