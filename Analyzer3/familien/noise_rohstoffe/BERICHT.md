# Familie noise_rohstoffe – Bericht (15.10.2026)

Auftrag: Intraday-Momentum auf Rohstoffen, BTC und FX untersuchen, mit zwei Ansätzen: Noise-Area und „market intraday momentum“ (MIM). Ziel ist, dass Alex an mehr Tagen ein Setup bekommt (Zielprofil Punkt 4), bei positiver Erwartung nach Kosten.
Instrumente: XAUUSD, XAGUSD, WTI, BRENT, BTCUSD, EURUSD, GBPUSD, AUDUSD, USDCAD, USDCHF. ETHUSD läuft nur als Gegenprobe mit.
Train 2020–2023, Val 2024 (einmal angesehen). Alle Zahlen sind netto nach `qdata.COST`, gerechnet mit `qbt.simulate`. Nullmodell aus `qbt.report_cell` mit K = 20, für die knappsten Zellen zusätzlich K = 100.
Vorab-Festlegung (Sitzungen, Regeln, Auswahl, Kandidatenregel) in `PLAN.md`, Train-Entscheid in `auswahl_train.json`.

## Kurzfazit
- **Kein Kandidat.** Keine Zelle und kein Portfolio erfüllt auf Train die Regel R > 0 mit t ≥ 2 und t gegen Null ≥ 2.
- **MIM ist nach Kosten auf allen 10 Instrumenten klar negativ.** Das gilt für jede Variante: r1, r1&r12, Rest-des-Tages, 30 oder 60 min, Ziel 0,5R/1R/kein Ziel, Teilziel B und Hoch-Vola-Filter.
  - Brutto liegt MIM bei etwa 0 R (Train −0,09 bis +0,04 R je Klasse). Die Kosten betragen 0,10–0,37 R je Trade (Train; 2024 0,17–0,45 R), denn eine halbe Stunde Bewegung ist klein gegen den Spread.
  - Das Portfolio P_alle MIM_r1_none hätte Alex fast täglich ein Setup gegeben (9,4 Trades/Tag, 99 % der Tage), aber mit −0,22 R je Trade (Train) bzw. −0,22 R (2024).
- **Der Literatur-Effekt ist als Regression da, aber nicht handelbar.** Auf Train korreliert die letzte halbe Stunde positiv mit r1: XAU +0,10 (t 3,2), XAG +0,15 (t 4,3), GBPUSD +0,10 (t 3,2), USDCAD +0,07 (t 2,3).
  - Der Vorzeichen-Trade verdient brutto aber nur 0,2–0,7 bp je Trade, bei Kosten von 1,5–6 bp. Der Zusammenhang kommt aus wenigen großen Tagen. Der Hoch-Vola-Filter (Nachtrag, datengetrieben) rettet das nicht.
  - Bei WTI ist die Korrelation negativ (−0,16, t −4,9), das ist Umkehr statt Momentum. Das war nicht vorab festgelegt und wird nicht verfolgt.
- **Noise-1.0 ist brutto nur auf Öl und BTC positiv, auf Metallen und FX schon brutto negativ.** Netto ist das beste Ergebnis BTC N10_end mit +0,054 R (t 1,3, 65 % TvS, Null −0,060 bei K = 100).
  - 2024 lag BTC bei +0,100 R (n 74). 2025 (nur Info) lag es bei −0,071 R.
  - P_sel (BRENT, BTC, WTI) liegt auf Train bei +0,024 R (t 0,9) und 2024 bei −0,009 R.
- Für Ziel 4 bringt dieser Familienansatz nichts. Mehr Setups gäbe es nur mit negativer Erwartung.

## Literatur (per WebSearch geprüft)
Volltexte waren nicht erreichbar, weil WebFetch und curl an DNS bzw. dem Proxy scheiterten. Die Regeln stammen deshalb aus Abstracts und Zusammenfassungen.
- **Gao/Han/Li/Zhou 2018**, JFE 129, 394–414 („Market intraday momentum“), SPY 1993–2013: Die erste halbe Stunde, gemessen ab dem Vortagesschluss bis 10:00, sagt die letzte halbe Stunde (15:30–16:00) voraus. Zusammen mit r12 (der vorletzten halben Stunde) ist die Vorhersage stärker, ebenso an volatilen Tagen. Handelsregel: Einstieg 15:30 in Richtung von r1, Schluss zum Handelsende. Das Timing η(r1, r12) handelt nur bei gleichem Vorzeichen von r1 und r12.
- **Elaut/Frömmel/Lampaert 2018**, JFM 37, 35–51: RUB/USD an der MICEX 2005–2014, erste halbe Stunde gegen letzte halbe Stunde. Der Effekt zeigt sich nur mit den expliziten Börsenzeiten, getrieben von der Risikoscheu der Liquiditätsgeber über Nacht. Frühere Arbeiten fanden für die Hauptwährungen gegen den USD **kaum** Intraday-Momentum.
- **Wen/Gong/Ma/Xu 2021**, Economic Modelling 95, 374–384: USO (Öl-ETF) 2006–2018. Nur die erste halbe Stunde sagt die letzte voraus, und der Übernachtanteil trägt die meiste Information. Der Effekt ist an volatilen Tagen und Tagen mit großem Volumen stärker. Handelsregel: Vorzeichen der ersten halben Stunde, Schluss zum Tagesende.
- **Li/Sakkas/Urquhart 2022**, JFM 57, 100619 („Intraday time-series momentum: global evidence…“): **Aktienindizes in 16 Industrieländern, nicht Rohstoffe**. Die Zuordnung „Rohstoffe/Gold/Öl“ im Auftrag stimmt also nicht. Für Gold habe ich keine eigene Studie zur Halbstunden-Regel gefunden.
- **Baltussen/Da/Lammers/Martens 2021**, JFE 142, 377–403: über 60 Futures (Aktien, Anleihen, **Rohstoffe, Währungen**), 1974–2020. Die Rendite vom Vortagesschluss bis 30 min vor Schluss sagt die letzten 30 min voraus. Getestet als Regel MIM_rod.
- **Shen/Urquhart/Wang 2022**, Financial Review 57(2), 319–344: Bitcoin. Die Sitzungen werden über das Volumen bestimmt, die erste halbe Stunde sagt die letzte voraus. Der Effekt ist in den umsatzstärksten Sitzungen am stärksten und wird von Liquiditätsbereitstellung getrieben. Die genauen Uhrzeiten waren nicht prüfbar.
- **Wen/Bouri/Xu/Zhao 2022**, NAJEF 62 („Intraday return predictability in the cryptocurrency markets: momentum, reversal, or both“): Stundendaten, Krypto zeigt **Momentum und Umkehr**. Die Autorenliste war in den Suchtreffern nicht sicher bestätigt.

## Sitzungen (vorab, Begründung in PLAN.md)
| Instrument | Sitzung (Ortszeit) | Fensterende/Ausstieg |
|---|---|---|
| XAUUSD, XAGUSD | New York 8:20–13:30 (COMEX-Kern) | 13:30 |
| WTI | New York 9:00–14:30 (NYMEX-Kern) | 14:30 |
| BRENT | London 8:00–16:30. Gewählt statt NY, sonst wäre Brent ein Doppel von WTI. | 16:30 |
| BTCUSD (ETH) | New York 9:30–16:00 (US-Kasse, höchster Umsatz), nur Mo–Fr | 15:00 wie NAS100 (MIM-Fenster 9:30–15:00) |
| FX (5 Paare) | London 8:00–16:00 (größter Platz, 16:00 = WM/R-Fixing) | 16:00 |

## Regeln
- N10_end: noise-1.0 unverändert, mit Zeitausstieg am Fensterende.
- N10_480: noise-1.0 mit Bewertung nach 480 min. Nach dem Hinweis des Koordinators läuft das nach Uhrzeit (`noise.last_by_clock`); die Zellen wurden neu gerechnet.
- PAPS_B: Kandidat B der Familie ausstiege (alle M30-Signale mit SMA20 und Wiedereinstieg, Stop Bandmitte, 50 % bei 0,5R, dann Break-even, Rest bis Fensterende).
- MIM_*: Richtung = Vorzeichen des Prädiktors. Market-Einstieg bei Fensterende − 30 min (MIM60: − 60 min), Ausstieg am Fensterende.
  - Stop = σ_H, das Mittel der letzten 14 Sitzungen von |Rendite im Haltefenster| (k = 1).
  - Prädiktoren: r1 (Vortagesschluss bis Eröffnung + 30), r1&r12 (Gao-Timing) und rod (Baltussen).
  - Ziele: kein Ziel, 1R, 0,5R oder Teilziel B. hv: nur Tage mit |r1| > Mittel der letzten 14 Sitzungen (Nachtrag nach Train-Lauf 1, als datengetrieben markiert).
- Trefferquote: TvS = Target vor Stop. TP1 = Teilziel vor Stop: dieselben Trades nochmals mit Ziel 0,5R und `seq=False`. Gew = Gewinnquote, verwendet bei Regeln ohne Ziel.

## Kosten in R je Trade (Mittel, Train; in Klammern 2024)
| Instrument | Noise N10_end | MIM 30 min | MIM 60 min | N10 R brutto | MIM r1 R brutto |
|---|---|---|---|---|---|
| XAUUSD | 0,03 (0,03) | 0,20 (0,17) | 0,14 | −0,022 | −0,052 |
| XAGUSD | 0,06 (0,06) | 0,37 (0,45) | 0,30 | −0,057 | −0,053 |
| WTI | 0,04 (0,07) | 0,18 (0,25) | 0,14 | +0,060 | −0,111 |
| BRENT | 0,06 (0,09) | 0,17 (0,21) | 0,12 | +0,067 | −0,051 |
| BTCUSD | 0,06 (0,05) | 0,29 (0,26) | 0,21 | +0,110 | −0,028 |
| EURUSD | 0,06 (0,07) | 0,14 (0,20) | 0,10 | −0,012 | +0,006 |
| GBPUSD | 0,06 (0,09) | 0,17 (0,25) | 0,12 | +0,044 | +0,032 |
| AUDUSD | 0,05 (0,07) | 0,14 (0,20) | 0,10 | +0,010 | +0,042 |
| USDCAD | 0,08 (0,12) | 0,20 (0,30) | 0,13 | −0,082 | +0,037 |
| USDCHF | 0,08 (0,08) | 0,22 (0,25) | 0,15 | −0,054 | −0,004 |
| ETHUSD | 0,05 (0,05) | 0,23 (0,23) | 0,16 | +0,015 | +0,034 |
MIM liegt brutto bei etwa 0, deshalb macht es auch ein günstigerer Qberx-Spread nicht positiv. Bei Noise auf BTC bliebe brutto +0,11 R. Das reicht aber nicht für t ≥ 2 (n 290).

## Portfolio (P_alle = alle 10 ohne Auswahl, P_sel = Train-Auswahl R > 0 und R > Null-R)
Spalten: Train | 2024. „Tage“ = Anteil der NY-Handelstage mit mindestens einem Trade (Train 1044 Tage, 2024 262). R/Tag = Summe R / alle Handelstage. t Tag = Tages-Cluster-t (Tage mit Trade).

| Regel | Portfolio | n | /Tag | Tage mit Trade | Treffer | R | Kosten R | R/Tag | t | t Tag | Null R | t vs Null | n 24 | /Tag 24 | Tage 24 | Treffer 24 | R 24 | R/Tag 24 | t Tag 24 | Null R 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N10_end | P_alle | 3284 | 3.15 | 90 % | 49 % TvS | -0.056 | 0.06 | -0.177 | -4.0 | -3.3 | -0.061 | 0.3 | 862 | 3.29 | 94 % | 49 % | -0.079 | -0.259 | -2.6 | -0.076 |
| N10_end | P_sel | 866 | 0.83 | 57 % | 57 % TvS | +0.024 | 0.06 | +0.020 | 0.9 | 0.9 | -0.053 | 2.9 | 246 | 0.94 | 61 % | 52 % | -0.009 | -0.008 | -0.2 | -0.083 |
| N10_480 | P_alle | 3284 | 3.15 | 90 % | 49 % TvS | -0.059 | 0.06 | -0.184 | -3.9 | -3.3 | -0.059 | 0.0 | 862 | 3.29 | 94 % | 50 % | -0.094 | -0.308 | -2.9 | -0.073 |
| N10_480 | P_sel | 866 | 0.83 | 57 % | 56 % TvS | +0.031 | 0.06 | +0.026 | 1.1 | 1.1 | -0.051 | 2.9 | 246 | 0.94 | 61 % | 52 % | -0.053 | -0.049 | -1.0 | -0.077 |
| PAPS_B | P_alle | 4051 | 3.88 | 90 % | 69 % TP1 | -0.053 | 0.06 | -0.204 | -4.6 | -3.5 | -0.057 | 0.4 | 1056 | 4.03 | 94 % | 69 % | -0.081 | -0.325 | -3.4 | -0.073 |
| PAPS_B | P_sel | 619 | 0.59 | 45 % | 78 % TP1 | +0.025 | 0.05 | +0.015 | 0.9 | 1.0 | -0.058 | 3.2 | 182 | 0.69 | 47 % | 78 % | +0.032 | +0.022 | 0.7 | -0.047 |
| MIM_r1_none | P_alle | 9808 | 9.39 | 99 % | 37 % Gew | -0.221 | 0.21 | -2.077 | -18.3 | -14.2 | -0.201 | -1.7 | 2591 | 9.89 | 100 % | 39 % | -0.218 | -2.160 | -7.3 | -0.286 |
| MIM_r1_none | P_sel | 0 (keine Auswahl) | | | | | | | | | | | | | | | | | | | |
| MIM_r1_t10 | P_alle | 9808 | 9.39 | 99 % | 48 % TvS | -0.228 | 0.21 | -2.142 | -25.2 | -20.6 | -0.218 | -1.1 | 2591 | 9.89 | 100 % | 55 % | -0.188 | -1.860 | -8.3 | -0.264 |
| MIM_r1_t10 | P_sel | 0 (keine Auswahl) | | | | | | | | | | | | | | | | | | | |
| MIM_r1_t05 | P_alle | 9808 | 9.39 | 99 % | 66 % TvS | -0.236 | 0.21 | -2.218 | -33.6 | -27.2 | -0.238 | 0.2 | 2591 | 9.89 | 100 % | 71 % | -0.222 | -2.194 | -13.3 | -0.277 |
| MIM_r1_t05 | P_sel | 0 (keine Auswahl) | | | | | | | | | | | | | | | | | | | |
| MIM_r1_B | P_alle | 9808 | 9.39 | 99 % | 66 % TP1 | -0.226 | 0.21 | -2.121 | -27.8 | -22.0 | -0.219 | -0.9 | 2591 | 9.89 | 100 % | 71 % | -0.219 | -2.164 | -11.5 | -0.278 |
| MIM_r1_B | P_sel | 0 (keine Auswahl) | | | | | | | | | | | | | | | | | | | |
| MIM_r1r12_none | P_alle | 4967 | 4.76 | 98 % | 37 % Gew | -0.219 | 0.21 | -1.044 | -12.5 | -9.7 | -0.201 | -1.0 | 1261 | 4.81 | 99 % | 35 % | -0.300 | -1.443 | -7.1 | -0.282 |
| MIM_r1r12_none | P_sel | 0 (keine Auswahl) | | | | | | | | | | | | | | | | | | | |
| MIM_rod_none | P_alle | 9820 | 9.41 | 99 % | 37 % Gew | -0.213 | 0.21 | -2.007 | -17.6 | -13.5 | -0.196 | -1.5 | 2591 | 9.89 | 100 % | 37 % | -0.256 | -2.536 | -9.0 | -0.286 |
| MIM_rod_none | P_sel | 0 (keine Auswahl) | | | | | | | | | | | | | | | | | | | |
| MIM60_r1_none | P_alle | 9836 | 9.42 | 99 % | 40 % Gew | -0.136 | 0.15 | -1.280 | -11.3 | -8.5 | -0.137 | 0.1 | 2593 | 9.90 | 100 % | 37 % | -0.213 | -2.107 | -6.8 | -0.196 |
| MIM60_r1_none | P_sel | 0 (keine Auswahl) | | | | | | | | | | | | | | | | | | | |
| MIM_r1_hv_none | P_alle | 3973 | 3.81 | 93 % | 36 % Gew | -0.223 | 0.21 | -0.847 | -11.0 | -8.4 | -0.197 | -1.3 | 1017 | 3.88 | 98 % | 37 % | -0.234 | -0.907 | -5.0 | -0.284 |
| MIM_r1_hv_none | P_sel | 0 (keine Auswahl) | | | | | | | | | | | | | | | | | | | |

### Klassen (nur beschreibend, nicht zur Auswahl): R brutto, Kosten, R netto
| Regel | Klasse | n | R brutto | Kosten R | R netto | t Tag | n 24 | R brutto 24 | R netto 24 |
|---|---|---|---|---|---|---|---|---|---|
| N10_end | Metalle | 540 | -0.039 | 0.04 | -0.080 | -2.3 | 171 | -0.058 | -0.105 |
| N10_end | Oel | 576 | +0.064 | 0.05 | +0.009 | 0.3 | 172 | +0.021 | -0.055 |
| N10_end | BTC | 290 | +0.110 | 0.06 | +0.054 | 1.3 | 74 | +0.149 | +0.100 |
| N10_end | FX | 1878 | -0.022 | 0.07 | -0.087 | -3.7 | 445 | -0.020 | -0.108 |
| N10_480 | Metalle | 540 | -0.040 | 0.04 | -0.081 | -2.2 | 171 | -0.076 | -0.122 |
| N10_480 | Oel | 576 | +0.066 | 0.05 | +0.011 | 0.3 | 172 | -0.017 | -0.093 |
| N10_480 | BTC | 290 | +0.128 | 0.06 | +0.072 | 1.5 | 74 | +0.091 | +0.042 |
| N10_480 | FX | 1878 | -0.028 | 0.07 | -0.094 | -3.8 | 445 | -0.018 | -0.105 |
| PAPS_B | Metalle | 608 | -0.006 | 0.04 | -0.046 | -1.6 | 198 | -0.046 | -0.091 |
| PAPS_B | Oel | 703 | +0.047 | 0.05 | -0.007 | -0.2 | 215 | -0.008 | -0.082 |
| PAPS_B | BTC | 339 | +0.088 | 0.06 | +0.032 | 0.9 | 89 | +0.090 | +0.042 |
| PAPS_B | FX | 2401 | -0.016 | 0.06 | -0.079 | -4.0 | 554 | -0.012 | -0.096 |
| MIM_r1_none | Metalle | 1889 | -0.052 | 0.28 | -0.332 | -9.6 | 514 | +0.005 | -0.303 |
| MIM_r1_none | Oel | 1760 | -0.081 | 0.17 | -0.254 | -9.0 | 516 | +0.022 | -0.211 |
| MIM_r1_none | BTC | 1030 | -0.028 | 0.29 | -0.315 | -8.4 | 262 | +0.100 | -0.160 |
| MIM_r1_none | FX | 5129 | +0.022 | 0.17 | -0.150 | -6.1 | 1299 | +0.042 | -0.200 |
| MIM_r1_t10 | Metalle | 1889 | -0.032 | 0.28 | -0.312 | -13.2 | 514 | +0.028 | -0.280 |
| MIM_r1_t10 | Oel | 1760 | -0.072 | 0.17 | -0.245 | -11.4 | 516 | +0.035 | -0.198 |
| MIM_r1_t10 | BTC | 1030 | -0.035 | 0.29 | -0.322 | -12.1 | 262 | +0.078 | -0.182 |
| MIM_r1_t10 | FX | 5129 | -0.000 | 0.17 | -0.173 | -9.8 | 1299 | +0.093 | -0.149 |
| MIM_r1_t05 | Metalle | 1889 | -0.032 | 0.28 | -0.311 | -17.2 | 514 | -0.020 | -0.329 |
| MIM_r1_t05 | Oel | 1760 | -0.074 | 0.17 | -0.248 | -14.4 | 516 | -0.001 | -0.234 |
| MIM_r1_t05 | BTC | 1030 | -0.037 | 0.29 | -0.323 | -15.1 | 262 | +0.048 | -0.212 |
| MIM_r1_t05 | FX | 5129 | -0.015 | 0.17 | -0.187 | -14.0 | 1299 | +0.065 | -0.177 |
| MIM_r1_B | Metalle | 1889 | -0.042 | 0.28 | -0.321 | -14.7 | 514 | -0.015 | -0.324 |
| MIM_r1_B | Oel | 1760 | -0.071 | 0.17 | -0.245 | -12.5 | 516 | +0.004 | -0.229 |
| MIM_r1_B | BTC | 1030 | -0.014 | 0.29 | -0.300 | -11.8 | 262 | +0.074 | -0.186 |
| MIM_r1_B | FX | 5129 | +0.003 | 0.17 | -0.169 | -10.6 | 1299 | +0.062 | -0.180 |
| MIM_r1r12_none | Metalle | 987 | -0.017 | 0.28 | -0.301 | -5.8 | 253 | -0.078 | -0.383 |
| MIM_r1r12_none | Oel | 883 | -0.057 | 0.17 | -0.228 | -5.7 | 243 | +0.030 | -0.204 |
| MIM_r1r12_none | BTC | 500 | -0.052 | 0.29 | -0.343 | -6.3 | 131 | +0.078 | -0.175 |
| MIM_r1r12_none | FX | 2597 | +0.011 | 0.17 | -0.162 | -4.7 | 634 | -0.088 | -0.329 |
| MIM_rod_none | Metalle | 1892 | -0.040 | 0.28 | -0.320 | -9.4 | 514 | +0.006 | -0.302 |
| MIM_rod_none | Oel | 1758 | -0.051 | 0.17 | -0.224 | -7.8 | 516 | +0.052 | -0.180 |
| MIM_rod_none | BTC | 1033 | +0.015 | 0.29 | -0.272 | -7.0 | 262 | +0.166 | -0.094 |
| MIM_rod_none | FX | 5137 | +0.014 | 0.17 | -0.159 | -6.6 | 1299 | -0.060 | -0.302 |
| MIM60_r1_none | Metalle | 1911 | -0.002 | 0.21 | -0.213 | -6.6 | 514 | -0.029 | -0.241 |
| MIM60_r1_none | Oel | 1766 | -0.022 | 0.13 | -0.150 | -5.6 | 518 | -0.059 | -0.232 |
| MIM60_r1_none | BTC | 1030 | -0.028 | 0.21 | -0.239 | -6.2 | 262 | +0.049 | -0.143 |
| MIM60_r1_none | FX | 5129 | +0.038 | 0.12 | -0.081 | -3.3 | 1299 | -0.045 | -0.209 |
| MIM_r1_hv_none | Metalle | 737 | -0.094 | 0.28 | -0.377 | -5.9 | 188 | -0.043 | -0.353 |
| MIM_r1_hv_none | Oel | 725 | -0.085 | 0.18 | -0.260 | -5.6 | 215 | +0.076 | -0.160 |
| MIM_r1_hv_none | BTC | 382 | +0.023 | 0.30 | -0.272 | -3.8 | 101 | +0.106 | -0.160 |
| MIM_r1_hv_none | FX | 2129 | +0.027 | 0.17 | -0.147 | -3.8 | 513 | +0.007 | -0.236 |

## Knappste Zellen mit Nullmodell K = 100 (`out/null_K100.csv`) und Info 2025
| Zelle | Train n / R / t / Null R (K100) / t vs Null | 2024 n / R / Null R (K100) | 2025 (Info) n / R |
|---|---|---|---|
| N10_end BTCUSD | 290 / +0,054 / 1,3 / −0,060 / 2,7 | 74 / +0,100 / −0,048 | 80 / −0,071 |
| N10_480 BTCUSD | 290 / +0,072 / 1,5 / −0,056 / 2,7 | 74 / +0,042 / −0,051 | 80 / −0,083 |
| PAPS_B BTCUSD | 339 / +0,032 / 0,9 / −0,060 / 2,6 | 89 / +0,042 / −0,029 | 88 / −0,084 |
| N10_end WTI | 249 / +0,016 / 0,3 / −0,051 / 1,4 | 75 / +0,119 / −0,064 | 94 / −0,284 |
| N10_end BRENT | 327 / +0,005 / 0,1 / −0,064 / 1,4 | 97 / −0,191 / −0,081 | 88 / +0,049 |
Das Nullmodell enthält die Kosten. „t gegen Null“ ≈ 2,7 bei BTC heißt: Der Einstieg ist besser als Zufall zur selben Uhrzeit, aber nach Kosten nicht signifikant größer als 0.

## Kandidaten
Keine. Die Kandidatenregel (Train R > 0, t ≥ 2, t gegen Null ≥ 2) erfüllt keine der 121 Instrument-Zellen und keines der 22 Portfolios (`auswahl_train.json`). Es gibt deshalb kein Modul `kandidat_*.py`.

## Varianten
11 Regeln (10 vorab, 1 Nachtrag MIM_r1_hv_none) × 11 Instrumente = 121 Zellen-Varianten. Dazu je Regel P_alle und P_sel (22) sowie 4 beschreibende Klassen-Portfolios (44).
Im Ledger stehen **187 Variantennamen** (`ergebnisse/varianten/noise_rohstoffe.csv`). N10_480 steht doppelt: zuerst mit 96 Kerzen, dann nach Uhrzeit, unter demselben Namen. Die Notiz „480 min nach Uhrzeit“ kennzeichnet die gültigen Zeilen.

## Probleme, Datenlücken, Zweifel
- **Literatur:** Volltexte waren nicht lesbar (Proxy/DNS). Die Regeln stammen aus Abstracts, die Session-Definition von Shen et al. (BTC) ist ungeprüft. Li/Sakkas/Urquhart 2022 behandelt Aktienindizes, nicht Rohstoffe.
- **Kosten** sind Annahmen (Qberx-Spread unbekannt). Für MIM ist das egal (brutto ≈ 0), für Noise auf BTC/Öl nicht ganz.
- **Daten:** XAG, WTI und BRENT haben Feb–Jul 2023 keine Daten (Train ohne diese Monate). BTC sind Binance-Last-Preise, keine Qberx-CFD-Kurse. XAU/XAG sind Spot-Kurse, auf denen die COMEX-Sitzung definiert ist (keine Futures).
- **Nullmodell:** Es nutzt die NY-Uhrzeit. Bei London-Sitzungen (BRENT, FX) verschiebt sich die Uhrzeit in den 2–3 Wochen im Jahr, in denen nur eine Seite Sommerzeit hat, um 1 h.
- **Trefferquote:** Für Teilziel-Regeln ist die Portfolio-Trefferquote (TP1vS) das n-gewichtete Mittel der Instrumente.
- **Ledger:** Die Train-Portfolio-Zeilen wurden zweimal geschrieben (nach dem Nachtrag MIM_hv neu gerechnet). Die Zahlen sind identisch bis auf die neue Regel.
- **Truncation:** Der Abschneide-Test (`pruefung.cut_test`, je 6 Schnitte auf BTCUSD/EURUSD) für MIM_r1_none, MIM_r1_hv_none, N10_end und PAPS_B ergab keine Abweichungen.
- **lib:** Kein Fehler gefunden. Die Korrektur `noise.last_by_clock` (480 min nach Uhrzeit) ist übernommen.

## Dateien
`PLAN.md` (Vorab), `nr.py` (Sitzungen und Signale), `run.py` (Zellen), `portfolio.py`, `tradeoff.py` → `tradeoff.csv` (374 Zeilen, Train und Val, Zellen und Portfolios), `tabellen.py`, `pruefung.py`, `auswahl_train.json`, `out/` (Zellen, Trades, Portfolio, K100).

## Alle Zellen (Train | Val 2024), Trefferquote: TvS / TP1 / Gew
| Regel | Instr. | n | /Tag | Tage | Treffer | Gew | R | t | Null TvS/Gew/R | Kosten R | n 24 | /Tag 24 | Treffer 24 | Gew 24 | R 24 | t 24 | Null 24 TvS/Gew/R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N10_end | XAUUSD | 289 | 0.28 | 28 % | 45 % TvS | 50 % | -0.051 | -1.2 | 49 %/48 %/-0.035 | 0.03 | 81 | 0.31 | 51 % | 47 % | -0.050 | -0.6 | 50 %/48 %/-0.024 |
| N10_end | XAGUSD | 251 | 0.28 | 28 % | 45 % TvS | 44 % | -0.113 | -2.4 | 50 %/48 %/-0.048 | 0.06 | 90 | 0.34 | 42 % | 40 % | -0.154 | -1.8 | 54 %/48 %/-0.026 |
| N10_end | WTI | 249 | 0.27 | 27 % | 54 % TvS | 53 % | +0.016 | 0.3 | 51 %/48 %/-0.032 | 0.04 | 75 | 0.29 | 64 % | 60 % | +0.119 | 1.3 | 49 %/48 %/-0.075 |
| N10_end | BRENT | 327 | 0.36 | 36 % | 53 % TvS | 53 % | +0.005 | 0.1 | 51 %/49 %/-0.054 | 0.06 | 97 | 0.37 | 41 % | 45 % | -0.191 | -2.1 | 48 %/47 %/-0.114 |
| N10_end | BTCUSD | 290 | 0.28 | 28 % | 65 % TvS | 52 % | +0.054 | 1.3 | 49 %/46 %/-0.070 | 0.06 | 74 | 0.28 | 61 % | 59 % | +0.100 | 1.2 | 50 %/48 %/-0.051 |
| N10_end | EURUSD | 378 | 0.36 | 36 % | 48 % TvS | 49 % | -0.067 | -1.5 | 49 %/48 %/-0.065 | 0.06 | 83 | 0.32 | 54 % | 49 % | -0.025 | -0.3 | 50 %/48 %/-0.065 |
| N10_end | GBPUSD | 337 | 0.32 | 32 % | 52 % TvS | 51 % | -0.014 | -0.3 | 51 %/49 %/-0.052 | 0.06 | 95 | 0.36 | 51 % | 48 % | -0.074 | -0.8 | 51 %/49 %/-0.080 |
| N10_end | AUDUSD | 363 | 0.35 | 35 % | 50 % TvS | 50 % | -0.039 | -0.9 | 49 %/48 %/-0.060 | 0.05 | 83 | 0.32 | 47 % | 45 % | -0.111 | -1.2 | 50 %/48 %/-0.069 |
| N10_end | USDCAD | 405 | 0.39 | 39 % | 42 % TvS | 46 % | -0.162 | -3.8 | 49 %/48 %/-0.085 | 0.08 | 101 | 0.39 | 48 % | 47 % | -0.157 | -1.8 | 51 %/48 %/-0.124 |
| N10_end | USDCHF | 395 | 0.38 | 38 % | 46 % TvS | 46 % | -0.134 | -3.2 | 50 %/47 %/-0.084 | 0.08 | 83 | 0.32 | 44 % | 41 % | -0.165 | -1.8 | 47 %/45 %/-0.115 |
| N10_end | ETHUSD | 283 | 0.27 | 27 % | 51 % TvS | 47 % | -0.031 | -0.7 | 47 %/46 %/-0.070 | 0.05 | 72 | 0.27 | 61 % | 57 % | +0.076 | 0.9 | 51 %/48 %/-0.031 |
| N10_480 | XAUUSD | 289 | 0.28 | 28 % | 45 % TvS | 48 % | -0.065 | -1.4 | 49 %/49 %/-0.032 | 0.03 | 81 | 0.31 | 50 % | 42 % | -0.065 | -0.7 | 51 %/49 %/-0.015 |
| N10_480 | XAGUSD | 251 | 0.28 | 28 % | 45 % TvS | 47 % | -0.099 | -2.0 | 51 %/48 %/-0.047 | 0.06 | 90 | 0.34 | 44 % | 43 % | -0.174 | -2.0 | 54 %/49 %/-0.022 |
| N10_480 | WTI | 249 | 0.27 | 27 % | 54 % TvS | 53 % | +0.012 | 0.2 | 52 %/50 %/-0.021 | 0.04 | 75 | 0.29 | 63 % | 60 % | +0.099 | 1.1 | 50 %/48 %/-0.071 |
| N10_480 | BRENT | 327 | 0.36 | 36 % | 54 % TvS | 54 % | +0.011 | 0.2 | 51 %/49 %/-0.054 | 0.06 | 97 | 0.37 | 42 % | 40 % | -0.242 | -2.6 | 49 %/48 %/-0.107 |
| N10_480 | BTCUSD | 290 | 0.28 | 28 % | 62 % TvS | 53 % | +0.072 | 1.5 | 48 %/47 %/-0.073 | 0.06 | 74 | 0.28 | 58 % | 50 % | +0.042 | 0.5 | 50 %/50 %/-0.044 |
| N10_480 | EURUSD | 378 | 0.36 | 36 % | 49 % TvS | 49 % | -0.060 | -1.3 | 49 %/49 %/-0.065 | 0.06 | 83 | 0.32 | 55 % | 53 % | -0.002 | -0.0 | 50 %/50 %/-0.061 |
| N10_480 | GBPUSD | 337 | 0.32 | 32 % | 52 % TvS | 49 % | -0.023 | -0.5 | 50 %/49 %/-0.058 | 0.06 | 95 | 0.36 | 52 % | 47 % | -0.089 | -1.0 | 51 %/49 %/-0.085 |
| N10_480 | AUDUSD | 363 | 0.35 | 35 % | 49 % TvS | 48 % | -0.052 | -1.1 | 49 %/49 %/-0.059 | 0.05 | 83 | 0.32 | 46 % | 49 % | -0.123 | -1.3 | 50 %/48 %/-0.065 |
| N10_480 | USDCAD | 405 | 0.39 | 39 % | 42 % TvS | 44 % | -0.187 | -4.2 | 50 %/49 %/-0.077 | 0.08 | 101 | 0.39 | 49 % | 47 % | -0.162 | -1.8 | 50 %/48 %/-0.122 |
| N10_480 | USDCHF | 395 | 0.38 | 38 % | 47 % TvS | 46 % | -0.128 | -2.9 | 50 %/48 %/-0.081 | 0.08 | 83 | 0.32 | 45 % | 47 % | -0.141 | -1.5 | 47 %/46 %/-0.120 |
| N10_480 | ETHUSD | 283 | 0.27 | 27 % | 53 % TvS | 49 % | +0.000 | 0.0 | 46 %/47 %/-0.078 | 0.05 | 72 | 0.27 | 61 % | 57 % | +0.091 | 1.0 | 52 %/48 %/-0.035 |
| PAPS_B | XAUUSD | 323 | 0.31 | 28 % | 71 % TP1 | 57 % | -0.013 | -0.4 | –/55 %/-0.024 | 0.03 | 98 | 0.38 | 74 % | 59 % | -0.024 | -0.4 | –/55 %/-0.038 |
| PAPS_B | XAGUSD | 285 | 0.31 | 28 % | 69 % TP1 | 53 % | -0.084 | -2.2 | –/55 %/-0.059 | 0.05 | 100 | 0.38 | 61 % | 45 % | -0.158 | -2.0 | –/54 %/-0.061 |
| PAPS_B | WTI | 280 | 0.31 | 27 % | 75 % TP1 | 62 % | +0.016 | 0.4 | –/56 %/-0.047 | 0.04 | 93 | 0.36 | 79 % | 67 % | +0.022 | 0.4 | –/57 %/-0.052 |
| PAPS_B | BRENT | 423 | 0.46 | 36 % | 68 % TP1 | 60 % | -0.022 | -0.5 | –/60 %/-0.042 | 0.06 | 122 | 0.47 | 65 % | 57 % | -0.161 | -2.4 | –/62 %/-0.077 |
| PAPS_B | BTCUSD | 339 | 0.32 | 28 % | 81 % TP1 | 58 % | +0.032 | 0.9 | –/52 %/-0.066 | 0.06 | 89 | 0.34 | 77 % | 64 % | +0.042 | 0.6 | –/54 %/-0.041 |
| PAPS_B | EURUSD | 493 | 0.47 | 36 % | 68 % TP1 | 61 % | -0.073 | -2.3 | –/59 %/-0.066 | 0.05 | 106 | 0.40 | 72 % | 58 % | -0.055 | -0.9 | –/57 %/-0.062 |
| PAPS_B | GBPUSD | 454 | 0.44 | 32 % | 68 % TP1 | 59 % | -0.033 | -0.9 | –/60 %/-0.045 | 0.06 | 128 | 0.49 | 71 % | 59 % | -0.087 | -1.5 | –/61 %/-0.083 |
| PAPS_B | AUDUSD | 456 | 0.44 | 35 % | 69 % TP1 | 62 % | -0.049 | -1.5 | –/60 %/-0.051 | 0.05 | 98 | 0.37 | 66 % | 59 % | -0.108 | -1.6 | –/57 %/-0.070 |
| PAPS_B | USDCAD | 498 | 0.48 | 39 % | 66 % TP1 | 60 % | -0.082 | -2.3 | –/60 %/-0.076 | 0.08 | 119 | 0.45 | 65 % | 54 % | -0.185 | -3.0 | –/56 %/-0.135 |
| PAPS_B | USDCHF | 500 | 0.48 | 38 % | 66 % TP1 | 55 % | -0.153 | -4.9 | –/59 %/-0.079 | 0.08 | 103 | 0.39 | 66 % | 56 % | -0.035 | -0.4 | –/56 %/-0.092 |
| PAPS_B | ETHUSD | 338 | 0.32 | 27 % | 75 % TP1 | 57 % | +0.020 | 0.5 | –/53 %/-0.049 | 0.04 | 91 | 0.35 | 80 % | 65 % | +0.022 | 0.3 | –/53 %/-0.067 |
| MIM_r1_none | XAUUSD | 1013 | 0.98 | 98 % | 35 % Gew | 35 % | -0.250 | -6.0 | –/35 %/-0.237 | 0.20 | 259 | 0.99 | 39 % | 39 % | -0.147 | -2.0 | –/35 %/-0.235 |
| MIM_r1_none | XAGUSD | 876 | 0.96 | 96 % | 33 % Gew | 33 % | -0.428 | -10.2 | –/32 %/-0.433 | 0.37 | 255 | 0.98 | 30 % | 30 % | -0.462 | -5.9 | –/27 %/-0.519 |
| MIM_r1_none | WTI | 872 | 0.96 | 96 % | 34 % Gew | 34 % | -0.287 | -7.5 | –/36 %/-0.161 | 0.18 | 258 | 0.99 | 40 % | 40 % | -0.270 | -4.1 | –/37 %/-0.312 |
| MIM_r1_none | BRENT | 888 | 0.98 | 98 % | 38 % Gew | 38 % | -0.222 | -5.7 | –/37 %/-0.158 | 0.17 | 258 | 0.99 | 41 % | 41 % | -0.152 | -2.1 | –/38 %/-0.201 |
| MIM_r1_none | BTCUSD | 1030 | 0.99 | 99 % | 34 % Gew | 34 % | -0.315 | -8.4 | –/32 %/-0.269 | 0.29 | 262 | 1.00 | 44 % | 44 % | -0.160 | -2.5 | –/39 %/-0.184 |
| MIM_r1_none | EURUSD | 1026 | 0.99 | 99 % | 39 % Gew | 39 % | -0.138 | -3.8 | –/38 %/-0.122 | 0.14 | 260 | 0.99 | 40 % | 40 % | -0.144 | -2.0 | –/36 %/-0.214 |
| MIM_r1_none | GBPUSD | 1027 | 0.99 | 99 % | 41 % Gew | 41 % | -0.136 | -3.7 | –/38 %/-0.158 | 0.17 | 260 | 0.99 | 38 % | 38 % | -0.205 | -2.8 | –/35 %/-0.290 |
| MIM_r1_none | AUDUSD | 1024 | 0.98 | 98 % | 41 % Gew | 41 % | -0.098 | -2.6 | –/39 %/-0.121 | 0.14 | 260 | 0.99 | 42 % | 42 % | -0.122 | -1.7 | –/36 %/-0.290 |
| MIM_r1_none | USDCAD | 1026 | 0.99 | 99 % | 39 % Gew | 39 % | -0.160 | -4.3 | –/38 %/-0.165 | 0.20 | 259 | 0.99 | 32 % | 32 % | -0.327 | -4.7 | –/32 %/-0.347 |
| MIM_r1_none | USDCHF | 1026 | 0.99 | 99 % | 37 % Gew | 37 % | -0.218 | -6.0 | –/37 %/-0.207 | 0.21 | 260 | 0.99 | 39 % | 39 % | -0.200 | -2.9 | –/35 %/-0.272 |
| MIM_r1_none | ETHUSD | 1030 | 0.99 | 99 % | 38 % Gew | 38 % | -0.192 | -5.2 | –/35 %/-0.199 | 0.23 | 262 | 1.00 | 39 % | 39 % | -0.101 | -1.3 | –/38 %/-0.161 |
| MIM_r1_t10 | XAUUSD | 1013 | 0.98 | 98 % | 46 % TvS | 43 % | -0.260 | -9.2 | 48 %/44 %/-0.229 | 0.20 | 259 | 0.99 | 50 % | 48 % | -0.164 | -3.0 | 48 %/44 %/-0.204 |
| MIM_r1_t10 | XAGUSD | 876 | 0.96 | 96 % | 50 % TvS | 45 % | -0.371 | -12.0 | 48 %/43 %/-0.403 | 0.37 | 255 | 0.98 | 53 % | 44 % | -0.398 | -6.8 | 48 %/42 %/-0.480 |
| MIM_r1_t10 | WTI | 872 | 0.96 | 96 % | 44 % TvS | 42 % | -0.272 | -9.0 | 49 %/46 %/-0.194 | 0.18 | 258 | 0.99 | 50 % | 48 % | -0.253 | -4.5 | 49 %/47 %/-0.267 |
| MIM_r1_t10 | BRENT | 888 | 0.98 | 98 % | 46 % TvS | 45 % | -0.219 | -7.3 | 49 %/46 %/-0.191 | 0.17 | 258 | 0.99 | 54 % | 49 % | -0.142 | -2.6 | 50 %/45 %/-0.223 |
| MIM_r1_t10 | BTCUSD | 1030 | 0.99 | 99 % | 47 % TvS | 41 % | -0.322 | -12.1 | 48 %/41 %/-0.314 | 0.29 | 262 | 1.00 | 56 % | 50 % | -0.182 | -3.4 | 50 %/46 %/-0.252 |
| MIM_r1_t10 | EURUSD | 1026 | 0.99 | 99 % | 51 % TvS | 47 % | -0.146 | -5.2 | 50 %/46 %/-0.148 | 0.14 | 260 | 0.99 | 58 % | 51 % | -0.091 | -1.6 | 51 %/47 %/-0.184 |
| MIM_r1_t10 | GBPUSD | 1027 | 0.99 | 99 % | 50 % TvS | 48 % | -0.159 | -5.7 | 49 %/47 %/-0.174 | 0.17 | 260 | 0.99 | 53 % | 49 % | -0.203 | -3.6 | 49 %/45 %/-0.270 |
| MIM_r1_t10 | AUDUSD | 1024 | 0.98 | 98 % | 50 % TvS | 48 % | -0.135 | -4.8 | 50 %/47 %/-0.140 | 0.14 | 260 | 0.99 | 59 % | 56 % | -0.042 | -0.8 | 50 %/47 %/-0.202 |
| MIM_r1_t10 | USDCAD | 1026 | 0.99 | 99 % | 50 % TvS | 48 % | -0.189 | -6.7 | 50 %/47 %/-0.191 | 0.20 | 259 | 0.99 | 58 % | 47 % | -0.220 | -3.9 | 49 %/43 %/-0.318 |
| MIM_r1_t10 | USDCHF | 1026 | 0.99 | 99 % | 49 % TvS | 45 % | -0.233 | -8.4 | 50 %/45 %/-0.221 | 0.21 | 260 | 0.99 | 55 % | 48 % | -0.190 | -3.5 | 51 %/44 %/-0.246 |
| MIM_r1_t10 | ETHUSD | 1030 | 0.99 | 99 % | 50 % TvS | 45 % | -0.222 | -8.5 | 48 %/43 %/-0.254 | 0.23 | 262 | 1.00 | 55 % | 47 % | -0.177 | -3.4 | 49 %/44 %/-0.247 |
| MIM_r1_t05 | XAUUSD | 1013 | 0.98 | 98 % | 64 % TvS | 59 % | -0.254 | -11.5 | 65 %/58 %/-0.250 | 0.20 | 259 | 0.99 | 65 % | 59 % | -0.220 | -5.1 | 66 %/58 %/-0.214 |
| MIM_r1_t05 | XAGUSD | 876 | 0.96 | 96 % | 68 % TvS | 51 % | -0.377 | -15.9 | 66 %/49 %/-0.410 | 0.37 | 255 | 0.98 | 68 % | 44 % | -0.440 | -9.6 | 66 %/42 %/-0.473 |
| MIM_r1_t05 | WTI | 872 | 0.96 | 96 % | 61 % TvS | 56 % | -0.277 | -11.5 | 66 %/58 %/-0.209 | 0.18 | 258 | 0.99 | 66 % | 62 % | -0.279 | -6.4 | 65 %/60 %/-0.297 |
| MIM_r1_t05 | BRENT | 888 | 0.98 | 98 % | 64 % TvS | 61 % | -0.219 | -9.3 | 66 %/59 %/-0.210 | 0.17 | 258 | 0.99 | 70 % | 64 % | -0.188 | -4.5 | 67 %/60 %/-0.238 |
| MIM_r1_t05 | BTCUSD | 1030 | 0.99 | 99 % | 66 % TvS | 53 % | -0.323 | -15.1 | 65 %/50 %/-0.341 | 0.29 | 262 | 1.00 | 73 % | 62 % | -0.212 | -5.2 | 69 %/56 %/-0.268 |
| MIM_r1_t05 | EURUSD | 1026 | 0.99 | 99 % | 68 % TvS | 63 % | -0.154 | -7.2 | 67 %/60 %/-0.166 | 0.14 | 260 | 0.99 | 72 % | 66 % | -0.156 | -3.8 | 67 %/61 %/-0.221 |
| MIM_r1_t05 | GBPUSD | 1027 | 0.99 | 99 % | 67 % TvS | 63 % | -0.175 | -8.3 | 67 %/60 %/-0.187 | 0.17 | 260 | 0.99 | 70 % | 66 % | -0.224 | -5.3 | 66 %/60 %/-0.287 |
| MIM_r1_t05 | AUDUSD | 1024 | 0.98 | 98 % | 66 % TvS | 62 % | -0.163 | -7.6 | 67 %/59 %/-0.170 | 0.14 | 260 | 0.99 | 77 % | 74 % | -0.072 | -1.8 | 69 %/64 %/-0.197 |
| MIM_r1_t05 | USDCAD | 1026 | 0.99 | 99 % | 67 % TvS | 64 % | -0.197 | -9.2 | 67 %/61 %/-0.213 | 0.20 | 259 | 0.99 | 72 % | 65 % | -0.244 | -5.8 | 66 %/58 %/-0.330 |
| MIM_r1_t05 | USDCHF | 1026 | 0.99 | 99 % | 66 % TvS | 61 % | -0.246 | -11.4 | 67 %/60 %/-0.239 | 0.21 | 260 | 0.99 | 74 % | 67 % | -0.189 | -4.7 | 69 %/61 %/-0.253 |
| MIM_r1_t05 | ETHUSD | 1030 | 0.99 | 99 % | 67 % TvS | 54 % | -0.262 | -12.6 | 64 %/51 %/-0.291 | 0.23 | 262 | 1.00 | 71 % | 58 % | -0.224 | -5.6 | 67 %/55 %/-0.266 |
| MIM_r1_B | XAUUSD | 1013 | 0.98 | 98 % | 64 % TP1 | 47 % | -0.251 | -9.3 | –/46 %/-0.238 | 0.20 | 259 | 0.99 | 65 % | 53 % | -0.189 | -3.7 | –/51 %/-0.218 |
| MIM_r1_B | XAGUSD | 876 | 0.96 | 96 % | 68 % TP1 | 26 % | -0.403 | -15.2 | –/24 %/-0.429 | 0.37 | 255 | 0.98 | 68 % | 22 % | -0.461 | -8.9 | –/18 %/-0.513 |
| MIM_r1_B | WTI | 872 | 0.96 | 96 % | 61 % TP1 | 47 % | -0.276 | -10.3 | –/48 %/-0.186 | 0.18 | 258 | 0.99 | 66 % | 39 % | -0.302 | -6.6 | –/37 %/-0.297 |
| MIM_r1_B | BRENT | 888 | 0.98 | 98 % | 64 % TP1 | 54 % | -0.214 | -8.0 | –/51 %/-0.183 | 0.17 | 258 | 0.99 | 70 % | 53 % | -0.156 | -3.2 | –/51 %/-0.214 |
| MIM_r1_B | BTCUSD | 1030 | 0.99 | 99 % | 66 % TP1 | 39 % | -0.300 | -11.8 | –/35 %/-0.299 | 0.29 | 262 | 1.00 | 73 % | 50 % | -0.186 | -4.1 | –/43 %/-0.227 |
| MIM_r1_B | EURUSD | 1026 | 0.99 | 99 % | 68 % TP1 | 58 % | -0.150 | -6.2 | –/56 %/-0.143 | 0.14 | 260 | 0.99 | 72 % | 56 % | -0.142 | -3.0 | –/52 %/-0.218 |
| MIM_r1_B | GBPUSD | 1027 | 0.99 | 99 % | 67 % TP1 | 56 % | -0.156 | -6.4 | –/52 %/-0.170 | 0.17 | 260 | 0.99 | 70 % | 44 % | -0.205 | -4.2 | –/39 %/-0.280 |
| MIM_r1_B | AUDUSD | 1024 | 0.98 | 98 % | 66 % TP1 | 57 % | -0.134 | -5.3 | –/55 %/-0.145 | 0.14 | 260 | 0.99 | 77 % | 64 % | -0.097 | -2.2 | –/55 %/-0.220 |
| MIM_r1_B | USDCAD | 1026 | 0.99 | 99 % | 67 % TP1 | 54 % | -0.171 | -6.8 | –/51 %/-0.192 | 0.20 | 259 | 0.99 | 72 % | 35 % | -0.267 | -5.8 | –/31 %/-0.337 |
| MIM_r1_B | USDCHF | 1026 | 0.99 | 99 % | 66 % TP1 | 45 % | -0.234 | -9.5 | –/45 %/-0.222 | 0.21 | 260 | 0.99 | 74 % | 45 % | -0.189 | -4.1 | –/40 %/-0.261 |
| MIM_r1_B | ETHUSD | 1030 | 0.99 | 99 % | 67 % TP1 | 44 % | -0.237 | -9.6 | –/40 %/-0.243 | 0.23 | 262 | 1.00 | 71 % | 45 % | -0.173 | -3.4 | –/43 %/-0.204 |
| MIM_r1r12_none | XAUUSD | 520 | 0.50 | 50 % | 38 % Gew | 38 % | -0.192 | -3.0 | –/35 %/-0.213 | 0.20 | 135 | 0.52 | 36 % | 36 % | -0.187 | -1.8 | –/37 %/-0.196 |
| MIM_r1r12_none | XAGUSD | 467 | 0.51 | 51 % | 31 % Gew | 31 % | -0.422 | -7.0 | –/32 %/-0.420 | 0.38 | 118 | 0.45 | 24 % | 24 % | -0.607 | -5.6 | –/26 %/-0.559 |
| MIM_r1r12_none | WTI | 430 | 0.47 | 47 % | 36 % Gew | 36 % | -0.247 | -4.5 | –/35 %/-0.163 | 0.17 | 125 | 0.48 | 41 % | 41 % | -0.302 | -3.3 | –/37 %/-0.287 |
| MIM_r1r12_none | BRENT | 453 | 0.50 | 50 % | 38 % Gew | 38 % | -0.210 | -3.8 | –/38 %/-0.165 | 0.17 | 118 | 0.45 | 42 % | 42 % | -0.099 | -0.9 | –/37 %/-0.225 |
| MIM_r1r12_none | BTCUSD | 500 | 0.48 | 48 % | 33 % Gew | 33 % | -0.343 | -6.3 | –/32 %/-0.277 | 0.29 | 131 | 0.50 | 40 % | 40 % | -0.175 | -1.8 | –/39 %/-0.181 |
| MIM_r1r12_none | EURUSD | 528 | 0.51 | 51 % | 39 % Gew | 39 % | -0.160 | -3.2 | –/38 %/-0.132 | 0.14 | 124 | 0.47 | 35 % | 35 % | -0.251 | -2.7 | –/38 %/-0.174 |
| MIM_r1r12_none | GBPUSD | 540 | 0.52 | 52 % | 41 % Gew | 41 % | -0.115 | -2.2 | –/38 %/-0.161 | 0.17 | 142 | 0.54 | 38 % | 38 % | -0.297 | -3.3 | –/36 %/-0.266 |
| MIM_r1r12_none | AUDUSD | 507 | 0.49 | 49 % | 40 % Gew | 40 % | -0.099 | -1.8 | –/39 %/-0.124 | 0.14 | 124 | 0.47 | 36 % | 36 % | -0.206 | -1.8 | –/36 %/-0.298 |
| MIM_r1r12_none | USDCAD | 515 | 0.49 | 49 % | 38 % Gew | 38 % | -0.214 | -4.1 | –/37 %/-0.197 | 0.19 | 128 | 0.49 | 23 % | 23 % | -0.537 | -6.6 | –/32 %/-0.358 |
| MIM_r1r12_none | USDCHF | 507 | 0.49 | 49 % | 37 % Gew | 37 % | -0.222 | -4.2 | –/38 %/-0.177 | 0.21 | 116 | 0.44 | 34 % | 34 % | -0.355 | -3.7 | –/34 %/-0.302 |
| MIM_r1r12_none | ETHUSD | 506 | 0.48 | 48 % | 37 % Gew | 37 % | -0.209 | -3.9 | –/35 %/-0.203 | 0.23 | 130 | 0.50 | 34 % | 34 % | -0.147 | -1.2 | –/37 %/-0.191 |
| MIM_rod_none | XAUUSD | 1014 | 0.98 | 98 % | 34 % Gew | 34 % | -0.280 | -7.0 | –/35 %/-0.221 | 0.20 | 259 | 0.99 | 39 % | 39 % | -0.110 | -1.4 | –/37 %/-0.198 |
| MIM_rod_none | XAGUSD | 878 | 0.97 | 97 % | 36 % Gew | 36 % | -0.367 | -8.8 | –/32 %/-0.429 | 0.37 | 255 | 0.98 | 29 % | 29 % | -0.496 | -6.3 | –/27 %/-0.527 |
| MIM_rod_none | WTI | 869 | 0.96 | 96 % | 37 % Gew | 37 % | -0.218 | -5.4 | –/36 %/-0.147 | 0.18 | 258 | 0.99 | 39 % | 39 % | -0.250 | -3.5 | –/37 %/-0.294 |
| MIM_rod_none | BRENT | 889 | 0.98 | 98 % | 37 % Gew | 37 % | -0.230 | -5.9 | –/38 %/-0.139 | 0.17 | 258 | 0.99 | 43 % | 43 % | -0.111 | -1.6 | –/37 %/-0.219 |
| MIM_rod_none | BTCUSD | 1033 | 0.99 | 99 % | 34 % Gew | 34 % | -0.272 | -7.0 | –/32 %/-0.275 | 0.29 | 262 | 1.00 | 44 % | 44 % | -0.094 | -1.3 | –/38 %/-0.191 |
| MIM_rod_none | EURUSD | 1027 | 0.99 | 99 % | 38 % Gew | 38 % | -0.146 | -3.9 | –/38 %/-0.118 | 0.14 | 260 | 0.99 | 38 % | 38 % | -0.200 | -2.9 | –/36 %/-0.217 |
| MIM_rod_none | GBPUSD | 1027 | 0.99 | 99 % | 39 % Gew | 39 % | -0.158 | -4.4 | –/38 %/-0.152 | 0.17 | 259 | 0.99 | 36 % | 36 % | -0.289 | -4.2 | –/35 %/-0.289 |
| MIM_rod_none | AUDUSD | 1028 | 0.99 | 99 % | 41 % Gew | 41 % | -0.112 | -3.1 | –/39 %/-0.118 | 0.14 | 260 | 0.99 | 38 % | 38 % | -0.239 | -3.4 | –/36 %/-0.284 |
| MIM_rod_none | USDCAD | 1028 | 0.99 | 99 % | 38 % Gew | 38 % | -0.181 | -4.8 | –/38 %/-0.176 | 0.20 | 260 | 0.99 | 28 % | 28 % | -0.459 | -7.2 | –/32 %/-0.344 |
| MIM_rod_none | USDCHF | 1027 | 0.99 | 99 % | 38 % Gew | 38 % | -0.196 | -5.4 | –/37 %/-0.201 | 0.21 | 260 | 0.99 | 33 % | 33 % | -0.320 | -4.7 | –/35 %/-0.305 |
| MIM_rod_none | ETHUSD | 1033 | 0.99 | 99 % | 38 % Gew | 38 % | -0.175 | -4.5 | –/35 %/-0.196 | 0.23 | 262 | 1.00 | 41 % | 41 % | -0.030 | -0.3 | –/38 %/-0.171 |
| MIM60_r1_none | XAUUSD | 1021 | 0.98 | 98 % | 40 % Gew | 40 % | -0.152 | -4.2 | –/39 %/-0.141 | 0.14 | 259 | 0.99 | 39 % | 39 % | -0.176 | -2.4 | –/40 %/-0.160 |
| MIM60_r1_none | XAGUSD | 890 | 0.98 | 98 % | 36 % Gew | 36 % | -0.284 | -6.7 | –/33 %/-0.301 | 0.30 | 255 | 0.98 | 34 % | 34 % | -0.306 | -3.7 | –/35 %/-0.290 |
| MIM60_r1_none | WTI | 877 | 0.96 | 96 % | 36 % Gew | 36 % | -0.205 | -5.4 | –/37 %/-0.144 | 0.14 | 259 | 0.99 | 34 % | 34 % | -0.292 | -4.3 | –/35 %/-0.286 |
| MIM60_r1_none | BRENT | 889 | 0.98 | 98 % | 41 % Gew | 41 % | -0.097 | -2.4 | –/40 %/-0.066 | 0.11 | 259 | 0.99 | 37 % | 37 % | -0.171 | -2.4 | –/41 %/-0.116 |
| MIM60_r1_none | BTCUSD | 1030 | 0.99 | 99 % | 35 % Gew | 35 % | -0.239 | -6.2 | –/33 %/-0.249 | 0.21 | 262 | 1.00 | 39 % | 39 % | -0.143 | -1.9 | –/35 %/-0.179 |
| MIM60_r1_none | EURUSD | 1026 | 0.99 | 99 % | 44 % Gew | 44 % | -0.067 | -1.9 | –/40 %/-0.076 | 0.10 | 260 | 0.99 | 39 % | 39 % | -0.142 | -1.9 | –/41 %/-0.114 |
| MIM60_r1_none | GBPUSD | 1027 | 0.99 | 99 % | 43 % Gew | 43 % | -0.058 | -1.5 | –/39 %/-0.101 | 0.12 | 260 | 0.99 | 41 % | 41 % | -0.088 | -1.2 | –/39 %/-0.184 |
| MIM60_r1_none | AUDUSD | 1024 | 0.98 | 98 % | 42 % Gew | 42 % | -0.052 | -1.4 | –/40 %/-0.069 | 0.10 | 260 | 0.99 | 37 % | 37 % | -0.205 | -2.9 | –/37 %/-0.177 |
| MIM60_r1_none | USDCAD | 1026 | 0.99 | 99 % | 45 % Gew | 45 % | -0.057 | -1.6 | –/40 %/-0.095 | 0.13 | 259 | 0.99 | 34 % | 34 % | -0.299 | -4.3 | –/36 %/-0.270 |
| MIM60_r1_none | USDCHF | 1026 | 0.99 | 99 % | 38 % Gew | 38 % | -0.173 | -4.7 | –/38 %/-0.139 | 0.15 | 260 | 0.99 | 35 % | 35 % | -0.309 | -4.2 | –/37 %/-0.187 |
| MIM60_r1_none | ETHUSD | 1030 | 0.99 | 99 % | 38 % Gew | 38 % | -0.172 | -4.6 | –/36 %/-0.168 | 0.16 | 262 | 1.00 | 35 % | 35 % | -0.121 | -1.4 | –/36 %/-0.125 |
| MIM_r1_hv_none | XAUUSD | 399 | 0.38 | 38 % | 33 % Gew | 33 % | -0.296 | -3.9 | –/35 %/-0.229 | 0.20 | 96 | 0.37 | 38 % | 38 % | -0.202 | -1.7 | –/37 %/-0.179 |
| MIM_r1_hv_none | XAGUSD | 338 | 0.37 | 37 % | 30 % Gew | 30 % | -0.473 | -6.7 | –/32 %/-0.415 | 0.38 | 92 | 0.35 | 28 % | 28 % | -0.509 | -3.5 | –/26 %/-0.575 |
| MIM_r1_hv_none | WTI | 358 | 0.39 | 39 % | 31 % Gew | 31 % | -0.327 | -5.2 | –/36 %/-0.154 | 0.18 | 106 | 0.41 | 39 % | 39 % | -0.259 | -2.5 | –/38 %/-0.250 |
| MIM_r1_hv_none | BRENT | 367 | 0.40 | 40 % | 38 % Gew | 38 % | -0.196 | -3.0 | –/38 %/-0.121 | 0.18 | 109 | 0.42 | 42 % | 42 % | -0.063 | -0.6 | –/38 %/-0.191 |
| MIM_r1_hv_none | BTCUSD | 382 | 0.37 | 37 % | 37 % Gew | 37 % | -0.272 | -3.8 | –/31 %/-0.307 | 0.30 | 101 | 0.39 | 44 % | 44 % | -0.160 | -1.5 | –/38 %/-0.221 |
| MIM_r1_hv_none | EURUSD | 418 | 0.40 | 40 % | 38 % Gew | 38 % | -0.178 | -3.2 | –/38 %/-0.115 | 0.15 | 101 | 0.39 | 35 % | 35 % | -0.196 | -1.7 | –/35 %/-0.198 |
| MIM_r1_hv_none | GBPUSD | 435 | 0.42 | 42 % | 41 % Gew | 41 % | -0.115 | -2.0 | –/38 %/-0.159 | 0.17 | 99 | 0.38 | 41 % | 41 % | -0.086 | -0.7 | –/36 %/-0.279 |
| MIM_r1_hv_none | AUDUSD | 429 | 0.41 | 41 % | 40 % Gew | 40 % | -0.086 | -1.4 | –/39 %/-0.122 | 0.14 | 105 | 0.40 | 38 % | 38 % | -0.163 | -1.5 | –/36 %/-0.304 |
| MIM_r1_hv_none | USDCAD | 429 | 0.41 | 41 % | 36 % Gew | 36 % | -0.189 | -3.3 | –/37 %/-0.197 | 0.20 | 109 | 0.42 | 28 % | 28 % | -0.500 | -5.4 | –/31 %/-0.379 |
| MIM_r1_hv_none | USDCHF | 418 | 0.40 | 40 % | 37 % Gew | 37 % | -0.170 | -2.7 | –/38 %/-0.194 | 0.22 | 99 | 0.38 | 37 % | 37 % | -0.213 | -1.7 | –/35 %/-0.288 |
| MIM_r1_hv_none | ETHUSD | 393 | 0.38 | 38 % | 37 % Gew | 37 % | -0.248 | -4.2 | –/35 %/-0.203 | 0.23 | 104 | 0.40 | 36 % | 36 % | -0.339 | -3.3 | –/38 %/-0.170 |
