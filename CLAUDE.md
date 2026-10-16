# Memory

## Me
Nutzer: **Alex**, Trader und Eigentümer des MT5-Expert-Advisors **DEADBAND**; handelt ein **GFT Instant Premium**
10k-Konto (Goat Funded Trader, bleibt bei GFT). Kommunikation **auf Deutsch**, knapp und ehrlich. Ich (Claude)
entscheide selbst und frage nur, wenn ich blockiert bin.

## Aktueller Stand (17.10.2026)
| Was | Wert |
|-----|------|
| **Beste Version** | **DEADBAND V13, Build 13.00** – `DEADBAND/V13/DEADBAND_V13.mq5` – **kompiliert** (MetaEditor GFT, 0 Fehler/0 Warnungen), Tester offen |
| **Live** | Build **8.10** (V8). **XA handelt live nie** (`FadeDurchlauf`/`frisch`, Signal direkt nach der Tagespause) → Live-Referenz im Nachbau = „V8 ohne XA“ |
| **Neu in 13.00** | V12-Code mit `AsiaAktiv=false`, `SrRiskPct=0.05`, `V12TickN1030=false` (Handel = V10 mit SR 0,05 %, ohne XA) |
| **Rückfall** | 12.00: `V12TickN1030=true`, `SrRiskPct=0.10`, `AsiaAktiv=true` · Live-Handel 8.10: `SrAktiv=false`, `V12TickN1030=false` |
| **Bericht** | `DEADBAND/V13/DEADBAND_V13_Bericht.md` (Repo-Fassung ohne Kontodaten) |
| **Nachbau** | `DEADBAND/V13/Replikat_v13/` = v12 + **GFT-Feed** (M1-Export, echte Spreads) + Windows-Prozess-Konfiguration (`gsetup.py`, `evl11.INIT`) |
| **Prompt alt** | `DEADBAND/V12/PROMPT_DEADBAND_V13.md` (vor dem Live-Abgleich geschrieben – Abschnitt Ergebnisse überholt) |

V13 gegen den echten Live-Stand („V8 ohne XA“), Differenz Ausz./J, 32 gepaarte Störungen, 0 Busts überall:

| Kontostart | GFT-Feed Schlupf ¼ | Schlupf ½ | Spread ×2 | Fremddaten |
|---|---|---|---|---|
| 2022 | +0,20 | +0,09 | +1,42 | +1,32 |
| 2023 | +1,72 | +0,83 | +2,38 | +2,75 |
| 2024–25 | +1,09 | +1,39 | +0,88 | +0,79 |
| 2025–26 (nur GFT) | +0,22 | +0,68 | +0,07 | – |
| 2017–20 / 2011–15 | – | – | – | +0,29 / +0,53 |

Wichtig: Der EA handelt Trade für Trade wie der Nachbau (29 Live-Trades geprüft). Das alte Spread-Modell ist bei
heutigen Kursen ~2× zu teuer; auf dem GFT-Feed liegen alle Kontozahlen deutlich höher (V8 ohne XA 11–16 Ausz./J).
V12 wie geliefert ist kostenempfindlich (Tick-N1030 2025–26 −0,9, Spread ×2 −3,7 Ausz./J).
→ Details: `memory/projects/deadband-v13.md` (V12: `deadband-v12.md`), verworfene Ideen: `memory/projects/deadband-verworfen.md`

## Ziele des Nutzers (Rangfolge)
1. **0 Busts** (harte Grenze) 2. mehr Auszahlungen/Jahr 3. größere Auszahlungen 4. kürzere Zyklen.
Ertrag/Jahr (eigener Anteil) zählt, nicht die Trefferquote.

## Offene Punkte
1. **MT5-Tester** (Echte Ticks, ab 2024): V13 gegen V13 mit `SrAktiv=false` (= V8-Handel) und gegen V12-Werte – auswerten
2. **Live-Wechsel V8 → V13** macht Alex (kontospezifische Eingaben übernehmen, Bericht V13 Abschnitt 7)
3. **GFT-Kursdaten liegen vor** (M1/M5 ab 2010, NAS dicht ab 28.10.2019) im Drive `DEADBAND_Kursdaten_20261016_2245`,
   ZIP je Jahr < 9 MB. Neue Ideen immer gegen „V8 ohne XA“ bzw. V13 auf GFT-Feed UND Fremddaten mit Kostenstress messen.
4. Regime „Fades aus“ (2011–21): nur Ströme mit **hoher Trefferquote** suchen
5. Tick-Module sind kostenempfindlich – neue Tick-Ideen nur mit Schlupf ½ und Spread ×2 bewerten

## Terms
| Term | Meaning |
|------|---------|
| **GFT** | Boden 6 % trailend am Equity-Hoch, Floating −1 %, Tag −3 % (17:00 NY), gültiger Tag ≥ 0,5 % + 0,50 $, 5 gültige Tage, Zyklus ≥ 14 Tage, Ausz. ≥ 105 $ (80 %), Gewinne < 120 s gestrichen, kein Hedging, Server = NY + 7 h |
| **Fades** | 10 Listen-Fades (N1030 … X1000S), Fehlausbruch einer Sitzungs-Range, Portfolio-Wächter PF200 > 1,15 |
| **Wächter live / Fades aus** | Fades handeln nur bei live Wächter: 2011–21 fast nie, ab 2023 fast immer |
| **SR** | Sweep-Reclaim NAS im Tick, 4 Marken (IB, PRE, H12, PDN), 0,10 % (10.00–12.00), **0,05 % ab 13.00** |
| **V8 ohne XA** | echter Live-Stand: XA (Gold-Asien) ist im Code an, handelt aber live nie (Signal nach der Tagespause, `frisch`) |
| **GFT-Feed** | Nachbau auf dem M1-Export des GFT-Terminals mit echten Bar-Spreads (`xg.py`, `REP_SPREAD=gft`), Fenster 2022/2023/2024-25/2025-26 |
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
| **DEADBAND V13** | aktuelle beste Version (s. oben) → `memory/projects/deadband-v13.md` |
| **DEADBAND V12** | Vorgänger (Tick-N1030, kostenempfindlich) → `memory/projects/deadband-v12.md` |
| **Build-Historie** | 6.x … 13.00 in einer Tabelle → `memory/projects/deadband-historie.md` |
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
- **Das Repo ist öffentlich:** keine Kontodaten (Saldo, Boden, Trade-Listen, Deals, Live-CSV, Login) ins Repo.
