# Memory

## Me
Nutzer: **Alex**, Trader und Eigentümer des MT5-Expert-Advisors **DEADBAND**; handelt ein **GFT Instant Premium**
10k-Konto (Goat Funded Trader, bleibt bei GFT). Kommunikation **auf Deutsch**, knapp und ehrlich. Ich (Claude)
entscheide selbst und frage nur, wenn ich blockiert bin.

## Aktueller Stand (16.10.2026)
| Was | Wert |
|-----|------|
| **Beste Version** | **DEADBAND V12, Build 12.00** – `DEADBAND/V12/DEADBAND_V12.mq5` – **nie kompiliert**, nur statisch geprüft |
| **Live** | Build **8.10** (V8) – bewährt; V10/V11/V12 noch nicht im Tester |
| **Neu in 12.00** | N1030 handelt im Tick (`SRT1030`, `V12TickN1030`=an, 0,50 %), M5-N1030 nur virtuell; sonst wie 11.00 = 10.00 |
| **Rückfall** | `V12TickN1030=false` = handelsgleich 11.00/10.00 |
| **Bericht** | `DEADBAND/V12/DEADBAND_V12_Bericht.md` |
| **Nächste Sitzung** | `DEADBAND/V12/PROMPT_DEADBAND_V13.md` (Abschnitt 5: Dateien und Daten laden) |
| **Nachbau** | `DEADBAND/V12/Replikat_v12/` (Kursdaten nicht im Repo, Ladebefehle im Prompt V13) |

Replikat v12, Ausz./J (32 gepaarte Störungen, Schlupf ¼ Spread, 1-Jahres-Konten alle 7 Tage):

| Kontostart | V8 | V10 = V11 | **V12** |
|---|---|---|---|
| 2022 (Auswahl) | 9,70 | 12,27 | **12,93** |
| 2023 | 11,63 | 13,20 | **14,49** |
| 2024–25 | 7,54 | 7,68 | **7,61** (gleich) |
| 2017–20 | 4,85 | 5,57 | **5,79** |
| 2011–15 | 3,09 | 3,71 | **3,71** |

0 Busts überall. Vorbehalt V12: ohne Schlupf nur halber Vorteil, 2024–25 dann −0,38 ± 0,24 (nicht signifikant).
→ Details: `memory/projects/deadband-v12.md`, verworfene Ideen: `memory/projects/deadband-verworfen.md`

## Ziele des Nutzers (Rangfolge)
1. **0 Busts** (harte Grenze) 2. mehr Auszahlungen/Jahr 3. größere Auszahlungen 4. kürzere Zyklen.
Ertrag/Jahr (eigener Anteil) zählt, nicht die Trefferquote.

## Offene Punkte
1. **MT5-Tester** (Echte Ticks, ab 2024): V12 `V12TickN1030` false/true, `SrAktiv` false/true – Ergebnisse auswerten
2. **GFT-M5-Daten** als ZIPs < 10 MB vom Nutzer anfordern (Drive bricht bei 10 MB ab)
3. Regime „Fades aus“ (2011–21, ~3,7–5,6 Ausz./J): nur Ströme mit **hoher Trefferquote** suchen
4. Weitere Fades einzeln im Tick (N0930, N1300, N1800); Konto-Mechanik mit korrigiertem Motor nachrechnen

## Terms
| Term | Meaning |
|------|---------|
| **GFT** | Boden 6 % trailend am Equity-Hoch, Floating −1 %, Tag −3 % (17:00 NY), gültiger Tag ≥ 0,5 % + 0,50 $, 5 gültige Tage, Zyklus ≥ 14 Tage, Ausz. ≥ 105 $ (80 %), Gewinne < 120 s gestrichen, kein Hedging, Server = NY + 7 h |
| **Fades** | 10 Listen-Fades (N1030 … X1000S), Fehlausbruch einer Sitzungs-Range, Portfolio-Wächter PF200 > 1,15 |
| **Wächter live / Fades aus** | Fades handeln nur bei live Wächter: 2011–21 fast nie, ab 2023 fast immer |
| **SR** | Sweep-Reclaim NAS im Tick, 4 Marken (IB, PRE, H12, PDN), 0,10 % (ab 10.00) |
| **SRT1030** | N1030 als Tick-Fade (Modul vom SR-Typ, 12.00) – handelt auch bei `SrAktiv=false` |
| **LW / XA / TD / S0830** | Larry-Williams NAS · Gold-Asien Long · Trend-Day NAS 14:00 · Spike-Fade NAS 8:30 |
| **RSI21 / Noise** | RSI-Pullback-Modul · NAS-Noise-Momentum long (3 Teile) |
| **Pufferkurve** | Größe nach Puffer zum Boden: 3,5 / 1,25 / 0,1 |
| **Serien-Stopp** | nach 3 Verlusten in Folge keine Einstiege bis 17:00 NY (schützt, nicht ändern) |
| **Störung / Seed** | Kontolauf mit 3 % anderen Signalen; Vergleiche immer gepaart über 16/32 Seeds |
| **Prüffenster** | Auswahl 2022; Prüfung 2024-01–2025-02, 2017–20, 2011–15 (Gold OANDA) |
| **Replikat v12 / eng11** | Python/numba-Nachbau M1 + Kontomotor (`Replikat_v12/`), Näherung |
→ Full glossary: `memory/glossary.md`

## Projects
| Name | What |
|------|------|
| **DEADBAND V12** | aktuelle beste Version (s. oben) → `memory/projects/deadband-v12.md` |
| **Build-Historie** | 6.x … 12.00 in einer Tabelle → `memory/projects/deadband-historie.md` |
| **DEADBAND V8** | Live-Stand 8.10, Konzept „Staffel“ → `memory/projects/deadband-v8.md` |
| **Analyzer 3** | eigenes Forschungsprojekt, Branch `claude/analyzer3-forschung` (nicht DEADBAND-Build) |

## Preferences / Regeln
- Deutsch, ehrlich: „nicht kompiliert“ sagen, Replikat = Näherung, Verschlechterungen offen nennen, Zahlen mit ± SE.
- Erst messen (Replikat: Strom, dann Konto, gepaart), dann bauen. Nur Plateau-Mitte übernehmen, Gegenprobe rechnen.
- Build per Patch-Skript (`patch_lib.Patch.rep`, jede Ersetzung genau einmal), reines ASCII, neue Funktionen schaltbar.
- Git: nur Branch **`claude/deadband-v11`** (Ordner `DEADBAND/V<n>/`), **kein PR ohne Bitte**, keine Modell-IDs.
- Branch `claude/ecstatic-johnson-mlf4v8` **nicht** mergen/übernehmen (Sicherheitsprüfung gesperrt).
- Kein `pkill -f`/`pgrep -f` mit Skriptnamen (trifft eigene Shell). Hintergrundbefehle enden nach **2 h** → Ketten teilen.
- Nach Änderungen am Kontomotor `t12_engine_check.py` laufen lassen (abgeschalteter Strom darf nichts ändern).
- Kursdaten, `cache/`, `.pkl` nie ins Repo. Erreichbar nur github.com und Drive (≤ 10 MB je Datei).
