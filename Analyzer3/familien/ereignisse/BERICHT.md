# Familie ereignisse – Bericht (Stand 15.10.2026, Daten v2 nach Uhrkorrektur)

**Ergebnis: 1 schwacher Kandidat** – `kandidat_fade930.py` (NAS100, CPI/NFP-Tage, Gegenrichtung der 8:30→9:30-Bewegung,
9:30–15:00 ET, Ziel 1 R). Train 71 % Target vor Stop / +0,23 R (t 2,2), Val 2024 67 % / +0,19 R (t 1,1), jeweils klar über
dem Nullmodell (50 % / −0,03 bzw. −0,01 R). Er hält die formalen Kriterien knapp ein, hat aber deutliche Warnzeichen (siehe unten).
Pre-FOMC-Drift, Post-FOMC-Reaktion, CPI/NFP-Momentum, Gold/FX nach 8:30 und EIA: **kein Kandidat**. Ein Ereignistag-Filter
für noise-1.0 bringt auf Train nichts.

## Vorgehen
- Alle Uhrzeiten NY (Server − 7 h). Fenster [Start, Ende): Signalkerze = Kerze um Start−5 (Entscheidung an ihrem Schluss),
  Market-Einstieg zur Eröffnung der Kerze um Start, Zeitausstieg am Schluss der Kerze um Ende−5 (US-Indizes spätestens 15:00).
- Stop = k × σ_F, σ_F = Wurzel des Mittels der quadrierten Fensterrenditen derselben Uhrzeit der letzten 20 Handelstage
  (strikt vor dem Signaltag). k = 1; nur für die Fenster direkt nach dem FOMC-Statement k = 3, weil dort die Fenster-
  Volatilität auf Train ≈ 3 × normal ist (RMS 3,0–4,0 σ_F), also 1 × σ der gleichartigen Ereignisfenster.
- Ziele 0,5 / 1 / 2 R und „none“ (nur Zeitausstieg) → `tradeoff.csv` (inkl. Nullmodell-Zeilen, R pro Tag).
- Kalender nur lesend aus `/home/user/data/cal`: FOMC nur `scheduled=1` (alle dev-Statements 14:00), CPI/NFP 8:30,
  EIA mit der jeweiligen Uhrzeit (10:30, an Feiertagswochen 11:00/13:00; Fenster relativ zur Veröffentlichung).
  US-Indizes nur an vollen Börsentagen (`us_market_calendar.csv`).
- Train = dev-Start bis 2023 (NAS100 2021–23, sonst 2020–23), Val = 2024 (einmal). Nullmodell `qbt.report_cell` (K = 20).
- Kosten `qdata.COST`; sie machen bei kurzen Fenstern viel aus (WTI 1 h ≈ 0,08 R, WTI 30 min ≈ 0,23 R, FX 3 h 0,04–0,07 R).

## Regeln und Quellen
| Regel | Ereignis / Instr. | Fenster NY, Richtung | Quelle |
|---|---|---|---|
| PF930 / PF1000 | FOMC; NAS100, US500 | 9:30 bzw. 10:00 → 13:55, long | Lucca/Moench 2015 JF 70(1); Abschwächung: Kurov/Wolfe/Gilbert 2021 FRL 40 |
| RELIEF_SEP | FOMC mit Projektionen (Mär/Jun/Sep/Dez) | 13:55 → 14:55, long | Gu/Kurov/Wolfe 2018 JEF („Relief rallies“: kaufen 5 min vor, schließen 55 min nach) |
| RELIEF_PC | alle geplanten FOMC (seit 2019 alle mit PK) | 13:55 → 14:55, long | wie oben, ausgedehnt |
| REV30 | FOMC | Reaktion 14:00–14:30 umkehren, 14:30 → 15:00 | Boguth/Grégoire/Martineau 2019 WP „Price pressure and efficiency on FOMC announcements“ (Umkehr bis 60 bp) |
| CONT30 | FOMC | Reaktion 14:00–14:30 fortsetzen, 14:30 → 15:00 | Alex-Grundregel; **nicht** literaturgestützt, nur zur Info |
| MOM930 / MOM1000 | CPI ∪ NFP; NAS100, US500 | Richtung 8:30→9:30 (→10:00) fortsetzen bis 15:00 | Gao/Han/Li/Zhou 2018 JFE (Intraday-Momentum stärker an Makro-Tagen; Original sagt die letzte Halbstunde voraus – nicht handelbar, daher Daytrade-Form) |
| PREM | CPI ∪ NFP | 9:30 → 15:00, long | Savor/Wilson 2013 JFQA (Ankündigungstags-Prämie) |
| FADE930 | CPI ∪ NFP; NAS100, US500 | Richtung 8:30→9:30 **umkehren**, 9:30 → 15:00 | Grant/Wolf/Yu 2005 JBF 29(5), Fung/Mok/Lam 2000 JBF 24(7): Umkehr großer Eröffnungsbewegungen in Indexfutures. **Auf Train gewählt, nachdem MOM930 dort klar negativ war (Spiegelregel).** |
| FADE930_KEIN | Tage ohne FOMC/CPI/NFP | wie FADE930 | Kontrolle: ist der Effekt ereignisspezifisch? |
| FXMOM30 | CPI ∪ NFP; XAUUSD, EURUSD, GBPUSD, AUDUSD, USDCAD, USDCHF | Richtung 8:30→9:00 fortsetzen bis 12:00 | Evans/Lyons 2008 JFE, Love/Payne 2008 JFQA (Order-Flow trägt News weiter). Gegenposition: schnelle Anpassung (Ederington/Lee 1995; Andersen u. a. 2003; Elder/Miao/Ramchander 2012) |
| EIA_CONT | EIA; WTI, BRENT | Richtung t→t+30 fortsetzen, t+30 → 14:30 | Wen/Indriawan/Lien/Xu 2023 Energy Journal 44(5): an EIA-Tagen sagt die Halbstunde ab 10:30 die Schluss-Halbstunde voraus |
| EIA_CONT_LIT | EIA | Richtung t→t+30, 15:30 → 16:00 | dieselbe Studie wörtlich (letzte Halbstunde) |
| EIA_REV | EIA | Richtung t→t+30 umkehren, t+30 → t+90 | Li/Geman 2018 J. Energy Markets 11(2): Reaktion ~25 min, dann schnelle Umkehr |

Post-FOMC-Fortsetzung: Die Literatur stützt sie **nicht** (Boguth u. a. 2019: Umkehr; Gu/Kurov/Wolfe 2018: unbedingter
Relief-Long nach SEP-Sitzungen). Deshalb Umkehr und Relief als Literaturregeln, Fortsetzung nur als Info.

## Ergebnisse je Zelle (Ziel 1 R; alle Ziele in `tradeoff.csv`, Rohzellen `zellen_train.csv`, `zellen_val.csv`, `noise_*.csv`)
TvS = Target vor Stop, Gew. = Gewinnquote, R = R netto je Trade, t = Trade-t (= Tages-t, höchstens 1 Trade/Tag und Zelle).
N10_* = noise-1.0 (Referenz-Rekonstruktion, Ziel 1 R) nur an Ereignistagen / Nicht-Ereignistagen.

| Regel · Inst. | Tr n | /Tag | TvS | Gew. | R | t | Null TvS | Null Gew. | Null R | Val n | /Tag | TvS | Gew. | R | t | Null TvS | Null Gew. | Null R |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PF930 · NAS100 | 23 | 0.030 | 50 % | 43 % | +0.02 | +0.1 | 49 % | 53 % | +0.03 | 8 | 0.031 | 67 % | 50 % | +0.10 | +0.4 | 44 % | 45 % | -0.06 |
| PF930 · US500 | 30 | 0.029 | 56 % | 50 % | +0.01 | +0.1 | 48 % | 51 % | +0.01 | 8 | 0.031 | 67 % | 50 % | +0.22 | +0.9 | 43 % | 47 % | -0.06 |
| PF1000 · NAS100 | 23 | 0.030 | 40 % | 57 % | +0.01 | +0.1 | 47 % | 53 % | +0.01 | 8 | 0.031 | 0 % | 62 % | +0.04 | +0.2 | 48 % | 50 % | -0.01 |
| PF1000 · US500 | 30 | 0.029 | 60 % | 47 % | +0.03 | +0.3 | 46 % | 52 % | -0.01 | 8 | 0.031 | 50 % | 75 % | +0.14 | +0.7 | 52 % | 49 % | +0.01 |
| RELIEF_SEP · NAS100 | 12 | 0.016 | 45 % | 42 % | -0.15 | -0.5 | 36 % | 59 % | +0.03 | 4 | 0.015 | 67 % | 50 % | +0.18 | +0.4 | 0 % | 53 % | -0.01 |
| RELIEF_SEP · US500 | 15 | 0.015 | 45 % | 53 % | -0.03 | -0.1 | 50 % | 58 % | +0.02 | 4 | 0.015 | 67 % | 50 % | +0.15 | +0.3 | 20 % | 47 % | -0.06 |
| RELIEF_PC · NAS100 | 22 | 0.028 | 59 % | 59 % | +0.10 | +0.5 | 46 % | 55 % | +0.01 | 8 | 0.031 | 75 % | 75 % | +0.34 | +1.3 | 7 % | 44 % | -0.12 |
| RELIEF_PC · US500 | 29 | 0.028 | 56 % | 59 % | +0.12 | +0.7 | 40 % | 55 % | -0.01 | 8 | 0.031 | 75 % | 50 % | +0.27 | +1.0 | 17 % | 41 % | -0.12 |
| REV30 · NAS100 | 22 | 0.028 | 47 % | 41 % | -0.11 | -0.5 | 46 % | 44 % | -0.07 | 8 | 0.031 | 50 % | 50 % | -0.12 | -0.4 | 58 % | 47 % | -0.05 |
| REV30 · US500 | 29 | 0.028 | 60 % | 52 % | +0.08 | +0.5 | 49 % | 48 % | -0.00 | 8 | 0.031 | 20 % | 50 % | -0.18 | -0.5 | 36 % | 42 % | -0.09 |
| CONT30 · NAS100 | 22 | 0.028 | 53 % | 59 % | +0.08 | +0.4 | 55 % | 53 % | +0.03 | 8 | 0.031 | 50 % | 50 % | +0.07 | +0.2 | 36 % | 47 % | -0.01 |
| CONT30 · US500 | 29 | 0.028 | 40 % | 48 % | -0.12 | -0.7 | 53 % | 46 % | -0.04 | 8 | 0.031 | 80 % | 50 % | +0.13 | +0.4 | 64 % | 49 % | +0.03 |
| MOM930 · NAS100 | 67 | 0.087 | 29 % | 40 % | -0.25 | -2.4 | 50 % | 50 % | +0.00 | 24 | 0.092 | 39 % | 46 % | -0.14 | -0.7 | 50 % | 50 % | -0.02 |
| MOM930 · US500 | 90 | 0.087 | 37 % | 40 % | -0.17 | -1.9 | 50 % | 49 % | -0.01 | 24 | 0.092 | 50 % | 54 % | +0.02 | +0.1 | 49 % | 47 % | -0.03 |
| MOM1000 · NAS100 | 67 | 0.087 | 32 % | 49 % | -0.16 | -1.6 | 52 % | 51 % | +0.01 | 24 | 0.092 | 53 % | 58 % | +0.12 | +0.7 | 50 % | 47 % | -0.02 |
| MOM1000 · US500 | 90 | 0.087 | 43 % | 53 % | -0.00 | -0.0 | 47 % | 48 % | -0.04 | 24 | 0.092 | 57 % | 54 % | +0.10 | +0.6 | 46 % | 47 % | -0.07 |
| PREM · NAS100 | 67 | 0.087 | 50 % | 51 % | +0.01 | +0.1 | 48 % | 52 % | +0.01 | 24 | 0.092 | 61 % | 62 % | +0.20 | +1.1 | 50 % | 52 % | +0.02 |
| PREM · US500 | 90 | 0.087 | 47 % | 48 % | -0.00 | -0.0 | 48 % | 54 % | +0.03 | 24 | 0.092 | 56 % | 54 % | +0.08 | +0.5 | 49 % | 50 % | +0.00 |
| FADE930 · NAS100 | 67 | 0.087 | 71 % | 57 % | +0.23 | +2.2 | 50 % | 49 % | -0.03 | 24 | 0.092 | 67 % | 58 % | +0.19 | +1.1 | 50 % | 49 % | -0.01 |
| FADE930 · US500 | 90 | 0.087 | 61 % | 57 % | +0.12 | +1.3 | 50 % | 50 % | -0.02 | 24 | 0.092 | 50 % | 42 % | -0.06 | -0.3 | 51 % | 50 % | -0.01 |
| FADE930_KEIN · NAS100 | 630 | 0.814 | 49 % | 50 % | -0.02 | -0.6 | 50 % | 50 % | -0.01 | 217 | 0.831 | 53 % | 53 % | +0.02 | +0.4 | 50 % | 50 % | -0.01 |
| FADE930_KEIN · US500 | 839 | 0.811 | 53 % | 50 % | -0.01 | -0.2 | 50 % | 50 % | -0.01 | 215 | 0.824 | 50 % | 51 % | -0.01 | -0.3 | 51 % | 49 % | -0.02 |
| EIA_CONT · WTI | 177 | 0.195 | 59 % | 58 % | +0.10 | +1.7 | 48 % | 48 % | -0.07 | 52 | 0.199 | 51 % | 52 % | -0.04 | -0.3 | 52 % | 49 % | -0.05 |
| EIA_CONT · BRENT | 177 | 0.195 | 53 % | 52 % | -0.00 | -0.1 | 49 % | 49 % | -0.06 | 52 | 0.199 | 46 % | 52 % | -0.10 | -0.8 | 51 % | 49 % | -0.07 |
| EIA_CONT_LIT · WTI | 177 | 0.195 | 43 % | 32 % | -0.46 | -7.1 | 48 % | 39 % | -0.36 | 52 | 0.199 | 39 % | 33 % | -0.59 | -5.0 | 49 % | 37 % | -0.53 |
| EIA_CONT_LIT · BRENT | 176 | 0.193 | 40 % | 30 % | -0.52 | -8.2 | 51 % | 39 % | -0.37 | 52 | 0.199 | 46 % | 35 % | -0.59 | -5.1 | 48 % | 33 % | -0.62 |
| EIA_REV · WTI | 177 | 0.195 | 41 % | 42 % | -0.22 | -3.5 | 49 % | 46 % | -0.11 | 52 | 0.199 | 36 % | 35 % | -0.27 | -2.3 | 47 % | 46 % | -0.14 |
| EIA_REV · BRENT | 177 | 0.195 | 47 % | 47 % | -0.14 | -2.1 | 50 % | 47 % | -0.11 | 52 | 0.199 | 41 % | 40 % | -0.23 | -1.9 | 48 % | 46 % | -0.14 |
| FXMOM30 · XAUUSD | 91 | 0.088 | 42 % | 48 % | -0.10 | -1.1 | 49 % | 48 % | -0.04 | 24 | 0.092 | 56 % | 50 % | +0.03 | +0.1 | 52 % | 48 % | -0.02 |
| FXMOM30 · EURUSD | 94 | 0.090 | 39 % | 44 % | -0.20 | -2.3 | 49 % | 47 % | -0.06 | 24 | 0.092 | 32 % | 33 % | -0.40 | -2.3 | 44 % | 45 % | -0.12 |
| FXMOM30 · GBPUSD | 94 | 0.090 | 44 % | 45 % | -0.12 | -1.3 | 51 % | 50 % | -0.04 | 24 | 0.092 | 30 % | 38 % | -0.39 | -2.1 | 49 % | 47 % | -0.09 |
| FXMOM30 · AUDUSD | 94 | 0.090 | 42 % | 45 % | -0.13 | -1.4 | 50 % | 48 % | -0.05 | 23 | 0.088 | 41 % | 48 % | -0.11 | -0.6 | 50 % | 47 % | -0.06 |
| FXMOM30 · USDCAD | 94 | 0.090 | 51 % | 50 % | -0.07 | -0.9 | 49 % | 49 % | -0.07 | 24 | 0.092 | 55 % | 46 % | -0.05 | -0.3 | 49 % | 45 % | -0.13 |
| FXMOM30 · USDCHF | 94 | 0.090 | 38 % | 41 % | -0.22 | -2.5 | 48 % | 47 % | -0.10 | 24 | 0.092 | 29 % | 38 % | -0.44 | -2.4 | 47 % | 47 % | -0.11 |
| N10_alle · NAS100 | 226 | 0.292 | 57 % | 60 % | +0.11 | +2.0 | 48 % | 47 % | -0.04 | 68 | 0.261 | 57 % | 59 % | +0.14 | +1.4 | 53 % | 53 % | +0.04 |
| N10_ereignis · NAS100 | 29 | 0.037 | 53 % | 66 % | +0.08 | +0.5 | 45 % | 45 % | -0.09 | 12 | 0.046 | 71 % | 83 % | +0.45 | +2.1 | 50 % | 52 % | +0.01 |
| N10_kein_ereignis · NAS100 | 197 | 0.255 | 58 % | 59 % | +0.12 | +2.0 | 51 % | 50 % | +0.00 | 56 | 0.215 | 54 % | 54 % | +0.07 | +0.7 | 53 % | 51 % | +0.02 |
| N10_fomc · NAS100 | 7 | 0.009 | 43 % | 43 % | -0.16 | -0.4 | 46 % | 44 % | -0.09 | 2 | 0.008 | 0 % | 100 % | +0.65 | +11.0 | 50 % | 53 % | +0.06 |
| N10_cpinfp · NAS100 | 22 | 0.028 | 58 % | 73 % | +0.16 | +1.0 | 49 % | 49 % | -0.02 | 11 | 0.042 | 71 % | 82 % | +0.43 | +1.9 | 54 % | 54 % | +0.05 |
| N10_alle · US500 | 304 | 0.294 | 53 % | 54 % | +0.02 | +0.5 | 49 % | 49 % | -0.03 | 80 | 0.307 | 48 % | 52 % | +0.00 | +0.0 | 50 % | 49 % | -0.03 |
| N10_ereignis · US500 | 42 | 0.041 | 46 % | 52 % | -0.03 | -0.2 | 54 % | 52 % | +0.03 | 13 | 0.050 | 67 % | 69 % | +0.28 | +1.2 | 52 % | 54 % | -0.00 |
| N10_kein_ereignis · US500 | 262 | 0.253 | 54 % | 54 % | +0.03 | +0.6 | 51 % | 50 % | -0.01 | 67 | 0.257 | 44 % | 49 % | -0.05 | -0.5 | 49 % | 50 % | -0.02 |
| N10_fomc · US500 | 8 | 0.008 | 67 % | 50 % | +0.16 | +0.5 | 58 % | 58 % | +0.12 | 3 | 0.011 | 100 % | 67 % | +0.32 | +0.9 | 44 % | 57 % | -0.02 |
| N10_cpinfp · US500 | 34 | 0.033 | 40 % | 53 % | -0.08 | -0.5 | 49 % | 49 % | -0.03 | 11 | 0.042 | 62 % | 64 % | +0.23 | +0.8 | 50 % | 54 % | -0.01 |

### Kandidat FADE930 · NAS100 – Trade-off-Kurve
| Ziel | Train TvS | Gew. | R | t | Null TvS / R | Val TvS | Gew. | R | t | Null TvS / R |
|---|---|---|---|---|---|---|---|---|---|---|
| 0,5 R | 81 % | 72 % | +0,12 | +1,6 | 71 % / −0,01 | 77 % | 71 % | +0,09 | +0,7 | 68 % / −0,04 |
| **1 R** | **71 %** | 57 % | **+0,23** | **+2,2** | 50 % / −0,03 | **67 %** | 58 % | **+0,19** | +1,1 | 50 % / −0,01 |
| 2 R | 30 % | 51 % | +0,23 | +1,8 | 22 % / −0,00 | 38 % | 46 % | +0,13 | +0,6 | 21 % / +0,04 |
| none | – | 49 % | +0,26 | +1,7 | – / +0,01 | – | 46 % | +0,15 | +0,6 | – / +0,07 |
n Train 67 (0,087/Tag), Val 24 (0,092/Tag). Info 2025 (verbraucht, entscheidet nichts): n 21, TvS 46 %, Gew. 43 %, −0,08 R (Null 55 % / +0,01 R).

## Befunde
1. **Pre-FOMC-Drift** ist 2020–23 nicht mehr messbar (bestes Train-t 1,0 bei PF1000·US500·0,5 R; vor der Uhrkorrektur
   waren es t 2,0 – getragen von falsch getakteten US500-Kerzen 2020). Passt zu Kurov/Wolfe/Gilbert 2021. 2024 leicht positiv (n 8).
2. **Post-FOMC**: Relief-Long nach SEP-Sitzungen negativ (n 12/15), über alle Sitzungen schwach positiv (t 0,5–0,7);
   2024 +0,27…+0,34 R bei n 8 – zu wenig, nach Val keine Änderung. Umkehr (REV30) und Fortsetzung (CONT30) beide ≈ 0.
   Alex' Grundregel „Fortsetzung schlägt Umkehr“ trägt nach dem FOMC-Statement nicht.
3. **CPI/NFP, Indizes**: Die Literatur-Fortsetzung der Vor-Eröffnungsreaktion ist **klar falsch herum**: MOM930 Train
   NAS100 −0,25 R (t −2,4), US500 −0,17 R (t −1,9), 2024 NAS100 −0,14 R. Die Spiegelregel FADE930 ist an Nicht-Ereignistagen
   wirkungslos (FADE930_KEIN ≈ 0 R, n 630/839) – der Effekt hängt also am 8:30-Termin. Auf Train in jedem Jahr
   (2021 +0,31, 2022 +0,34, 2023 +0,05 R), für CPI und NFP sowie long und short positiv.
4. **CPI/NFP, Gold/FX**: Fortsetzung der ersten 30 min bis 12:00 verliert überall, bei EURUSD/GBPUSD/USDCHF auch deutlich
   unter dem Nullmodell (Train t −2,3/−1,3/−2,5; 2024 −0,4 R). Hinweis auf Umkehr, die aber durch Kosten (0,04–0,07 R) und
   fehlende Literatur für Stunden-Horizonte nicht als Regel getestet wurde (keine Nachjustierung nach Sicht).
5. **EIA (WTI/BRENT)**: Fortsetzung t→t+30 bis 14:30 (Wen u. a. 2023) auf Train WTI +0,15 R (t 1,9, ohne Ziel) bzw.
   +0,10 R (t 1,7, 1 R), klar über Null (t_vs_null 2,2–2,8), BRENT ≈ 0 – **knapp unter t 2**, kein Kandidat. 2024 negativ
   (WTI −0,04…−0,15 R). Umkehr (Li/Geman 2018) klar negativ (t −3,5); wörtliche 30-min-Regel scheitert an Kosten (−0,46 R).
6. **noise-1.0 an Ereignistagen**: Train NAS100 +0,08 R (n 29) gegen +0,12 R an anderen Tagen, US500 −0,03 gegen +0,03 –
   kein größerer Vorteil an Ereignistagen; 2024 umgekehrt (+0,45 R, n 12). Uneinheitlich → kein Filter.

## Kandidat
`familien/ereignisse/kandidat_fade930.py` (NAME `ereignis-fade930`, INSTRUMENTS `['NAS100']`):
An CPI- und NFP-Tagen (Kalender) die Bewegung 8:30→9:30 ET messen; um 9:30 ET (16:30 Serverzeit) Market-Einstieg in
Gegenrichtung, Stop 1 × σ_F (20-Tage-RMS der 9:30–15:00-Rendite), Ziel 1 R, Zeitausstieg 15:00 ET (22:00 Server).
Quelle: Grant/Wolf/Yu 2005, Fung/Mok/Lam 2000 (Umkehr großer Eröffnungsbewegungen). Prüfung `pruefung.py`: Modul =
Forschungslauf (91/91 Trades gleich), Abschneide-Test 18/18 gleich (T an Signalkerzen, kurz davor, zufällig).

Warnzeichen: Richtung erst nach dem negativen Train-Befund der Literaturregel gewählt; t 2,2 bei 146 protokollierten
Varianten; US500 mit derselben Regel 2024 negativ (−0,06 R); 2025 (Info) negativ; R +0,19–0,23 liegt unter dem
Zielprofil 0,5 R; nur ≈ 0,09 Trades/Tag (24 Ereignistage im Jahr).

## Varianten
146 protokollierte Varianten: 15 Regeln → 34 Zellen Regel × Instrument × 4 Ziele = 136, plus 10 noise-1.0-Teilmengen
(5 Tagesmengen × NAS100/US500). Ledger `ergebnisse/varianten/ereignisse.csv`: Zeilen `note=v2` gelten; `note=train/val` sind die verworfenen
Läufe vor der Uhrkorrektur (Dateien in `v1_vor_datenkorrektur/`).

## Probleme, Zweifel
- Val 2024 (v1) wurde vor der Datenkorrektur einmal angesehen; die 2024-Zahlen der Index-/FX-Regeln sind in v2 identisch,
  die Kandidatenwahl auf Train v2 ist dieselbe wie auf Train v1 (FADE930·NAS100 unverändert). PF1000·US500 fiel durch die
  Korrektur von t 2,0 auf 1,0 – Beispiel, wie dünn die FOMC-Stichproben sind (8 Sitzungen/Jahr).
- WTI/BRENT: Feb–Jul 2023 fehlen (n 177 statt ≈ 205 auf Train).
- Wen u. a. 2023: Volltext nicht erreichbar; Halbstundenraster ab 9:30 aus Sekundärquellen erschlossen (EIA 10:30 = Beginn
  der dritten Halbstunde). Boguth u. a. 2019 nur als Working Paper/Abstract gelesen.
- Gao u. a. 2018 lässt sich nicht wörtlich handeln (Ziel ist 15:30–16:00, NAS100.c ohne Kerzen 15–16 Uhr).
- Keine Fehler in `lib/` gefunden.
