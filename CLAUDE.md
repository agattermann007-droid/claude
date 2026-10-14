# Memory

## Me
Nutzer: Trader und Eigentümer des MT5-Expert-Advisors **DEADBAND**, handelt ein **GFT Instant Premium** 10k-Konto (Goat Funded Trader, bleibt bei GFT). Kommunikation **auf Deutsch**, kurz und ehrlich. Ich (Claude) entscheide selbst und frage nur, wenn ich blockiert bin.

## Aktueller Stand: DEADBAND V8, Build 8.00 (04.10.2026)
| Was | Wert |
|-----|------|
| **Datei** | `DEADBAND/DEADBAND_V8.mq5` – **nie kompiliert**, Nutzer testet im MT5-Tester |
| **Bericht** | `DEADBAND/DEADBAND_V8_Bericht.md` (Methode, Zahlen, verworfene Ideen, Quellen) |
| **Konzept** | „Staffel“: Fade-Kern 7.10 + **LW** + **XA** + neue Pufferkurve |
| **LW** | Larry-Williams-Ausbruch NAS: Open 9:30 ± 0,4 × Vortages-Range (9:30–16:00), erste M5-Kerze bis 15:00 mit Schluss jenseits → Einstieg nächstes Open, Stop Mitte Open/Einstieg, kein Ziel, Ausstieg 16:00, **0,5 %**, nur ab **4 % Puffer** zum Boden (`LwMinPuffer`) |
| **XA** | Gold-Asien-Halten: Long 18:00→3:00 NY über 288-M5-Schnitt, Stop 0,6 ATR, Ziel 1 R, 0,75 % |
| **Pufferkurve** | `DDFullPct/DDMinPct/DDMinFactor` = **3,5 / 1,25 / 0,1** (7.10: 5 / 2,5 / 0,2) |
| **Replikat 2022–25** | 7.10 → 8.00: 11,00 → **13,37** Ausz./J, netto 2008 → **2771 $**, Ø 235 → 267 $, Zyklus 30 → 25 Tage, **0 Pleiten** |
| **Hälften** | 2022–23: 12,57 → 16,54 · 2024–25: 7,78 → 11,87 |
| **Fremddaten 2006–21** | 2,70 → 3,66 Ausz./J, 0 Pleiten |
| **Rückfall** | `LwAktiv=false`, `AsiaAktiv=false`, Kurve 5/2,5/0,2 = handelsgleich 7.10 |
| **Offensiv-Option** | Kurve 3/1/0,1: 14,01 Ausz./J, aber 0,001 Pleiten/Kontojahr auf 2006–21 |
→ Details: `memory/projects/deadband-v8.md`

## Ziele des Nutzers (Rangfolge)
1. **Keine Pleiten** (harte Grenze) 2. mehr Auszahlungen/Jahr 3. mehr Gewinn je Auszahlung 4. kürzere Zyklen.
Test **ab 2022** (Auswahl 22–23, Prüfung 24–25, Gegenprobe 2005–21). Neue Strategien **erst allein** unter GFT-Regeln bewerten, GFT-Handhabung anpassen, dann kombinieren. Altes Konzept darf fallen.
Nächster Wunsch: **Kontoerkenner und Anpasser** (Parametersatz je Kontozustand, z. B. Drawdown) → Prompt in `DEADBAND/PROMPT_NEUE_SITZUNG.md`.

## Terms
| Term | Meaning |
|------|---------|
| **GFT** | Goat Funded Trader Instant Premium: Boden 6 % nachlaufend, Floating −1 %, Tag −3 % (ab 17:00 NY), gültiger Tag ≥ 0,5 %, 5 gültige Tage / ≥ 10 Tage Zyklus, Ausz. ≥ 105 $ (80 %), Gewinne < 120 s gestrichen, kein Hedging, Server = NY + 7 h |
| **gültiger Tag** | Tag mit ≥ 0,505 % realisiert (50,50 $) |
| **Fades** | 10 Fehlausbruch-Module (N1030 … X1000S), Portfolio-Wächter PF200 > 1,15 |
| **S0830** | Spike-Fade NAS 8:30, nur Long (Build 7.10) |
| **RSI21 / Noise** | interne Module (RSI21-Pullback, NAS-Noise-Momentum long) |
| **Pufferkurve** | Größenfaktor nach Puffer zum Boden (DDFull/DDMin/DDMinFactor) |
| **minbuf** | Strom/Modul handelt nur ab X % Puffer (neu in 8.00, `F[m].minBuf`) |
| **Replikat / eng6** | Python/numba-Kontomotor `DEADBAND/Replikat_v6/` (Stand 6.10 + generische Ströme) – Näherung, Unterschiede zählen |
| **ext** | Fremddaten 2005–21 (GitHub-Quellen), `DEADBAND_EXT` |
→ Full glossary: `memory/glossary.md`

## Projects
| Name | What |
|------|------|
| **DEADBAND V8** | aktueller Build 8.00 (s. oben) |
| **DEADBAND V7** | `DEADBAND_V7.mq5` = 7.10, `rollback_7.00/` = Nutzerstand 7.00 |
| **Kontoerkenner** | geplant, nächste Sitzung |

## Preferences / Regeln
- Deutsch, ehrlich: nicht kompiliert sagen, Replikat = Näherung, Verschlechterung offen sagen.
- Commit + Push auf den vorgegebenen Branch, **kein PR ohne Bitte**, keine Modell-IDs in Commits.
- Branch `claude/ecstatic-johnson-mlf4v8` **nicht** mergen/übernehmen (Sicherheitsprüfung gesperrt).
- Kein `pkill -f` (trifft eigene Shell); lange Läufe per `nohup`-Skript + „FERTIG“-Marke.
- Kursdaten nicht im Repo: `DEADBAND/extdata/DATEN_BERICHT.md` + `y7_data.py`. Nur GitHub erreichbar.
