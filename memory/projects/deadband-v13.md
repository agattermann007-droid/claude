# DEADBAND V13 – Build 13.00 (beste Version, Stand 17.10.2026)

**Auch genannt:** V13, 13.00, „Live-Abgleich“
**Status:** gebaut 17.10.2026 in einer lokalen Sitzung auf Alex' PC, **kompiliert** im MetaEditor des GFT-Terminals
(0 Fehler, 0 Warnungen), statisch geprüft. MT5-Tester steht aus. Ordner `DEADBAND/V13/` (Repo-Fassung ohne Kontodaten).

## Was es ist
V12-Code mit drei Voreinstellungen (`build/patch_v13.py`, 5 Ersetzungen):
| Eingabe | 12.00 | 13.00 |
|---|---|---|
| `AsiaAktiv` | true | **false** – XA handelt live nie (siehe unten), damit Nachbau/Tester = Echtbetrieb |
| `SrRiskPct` | 0,10 | **0,05** |
| `V12TickN1030` | true | **false** – N1030 wieder auf M5 |
Handel = V10 (V8 + SR) mit SR 0,05 % und ohne XA. Rückfall 12.00: `V12TickN1030=true`, `SrRiskPct=0.10`,
`AsiaAktiv=true`. Rückfall Live-Handel 8.10: `SrAktiv=false`, `V12TickN1030=false`.

## Befunde der Live-Runde
- **Live = Nachbau:** Die 29 Live-Trades 28.09.–16.10.2026 (8.10) finden sich im Nachbau auf dem GFT-Feed Minute für
  Minute wieder, Stop identisch, Einstieg meist < 0,5 Punkte daneben, Live-R = virtuelles R.
- **XA handelt live nie** (alle Builds ab 8.00, auch Tester): `FadeDurchlauf` setzt `frisch` nur, wenn die vorige M5-Kerze
  genau 5 min vorher liegt; XA kommt an der ersten Kerze nach der Tagespause (65 min Lücke) → nur virtuell. Live-Stand
  ist also **„V8 ohne XA“** – das ist die richtige Referenz. XA reparieren (`AsiaEinNY` −355/−350): nicht robust.
- **Spreads:** GFT-Bar-Spread = Tick-Mittel (NAS 1,77, Gold 0,41 Punkte im Sep./Okt. 2026). Das proportionale Modell des
  Nachbaus rechnet bei heutigen Kursen etwa doppelt so teuer (NAS 3,32). Schlupf live: Markt-Einstiege ≈ 0, Stops ≈ ½ Spread.
- **Nachbau auf dem GFT-Feed** (M1-Export, NAS ab 28.10.2019, Gold ab 2011): Kontozahlen viel höher als auf Fremddaten
  (V8 2022 ≈ 15 statt 10 Ausz./J). Neues Fenster „Neu 2025-26“ (Starts 2025-02 bis 2025-10).
- **V12 kostenempfindlich:** Tick-N1030 auf dem GFT-Feed 2025–26 −0,9 Ausz./J, mit doppeltem Spread −3,7. Ursache der
  Schwäche 2025–26: Tick-N1030 und SR 0,10 (doppelt so viele Serien-Stopps, die Fades sperren).

## Zahlen (32 gepaarte Störungen, Differenz V13 − „V8 ohne XA“, Ausz./J)
| Fenster | Schlupf ¼ | ohne Schlupf | Schlupf ½ | Spread ×2 |
|---|---|---|---|---|
| GFT 2022 | +0,20 ± 0,12 | +0,07 | +0,09 | +1,42 |
| GFT 2023 | +1,72 ± 0,13 | +2,41 | +0,83 | +2,38 |
| GFT 2024–25 | +1,09 ± 0,14 | +1,09 | +1,39 | +0,88 |
| GFT 2025–26 | +0,22 ± 0,27 | +1,53 | +0,68 | +0,07 |
| Fremd 2022 / 2023 / 2024–25 / 2017–20 / 2011–15 | +1,32 / +2,75 / +0,79 / +0,29 / +0,53 | | Schlupf ½: +1,99 / +2,71 / +1,03 / +0,01 / +0,46 | |
0 Busts überall. SR-Plateau 0,03–0,075 (0,05 einzige Stufe ohne negatives Fenster). V13 GFT absolut: 15,99 / 16,46 /
13,76 / 11,75 Ausz./J, 2.950 / 3.600 / 3.161 / 2.307 $/J.

## Replikat v13 (`DEADBAND/V13/Replikat_v13/`)
Nachbau v12 + GFT-Feed, unter **Windows** gerechnet: `evl11.INIT` + `gsetup.configure()` konfigurieren jeden
Rechenprozess (sonst handeln die Prozesse nichts). `xg.py` (GFT, `REP_SPREAD=gft|modell`), `xe.py` (Fremddaten wie v12),
`prep_gft.py`, `g_var.py` (Varianten-Liste `VAR`, gepaart), `g_final.py` (`--slip`), `g_live.py` (Live-Abgleich, braucht
lokale Live-CSV). Kontrolle: Fremddaten treffen den V12-Bericht exakt.

## Tester-Checkliste (offen)
V13 gegen V13 mit `SrAktiv=false` (= V8-Handel) und gegen V12-Werte; Echte Ticks ab 2024, mehrere Startdaten. Beim
Live-Wechsel kontospezifische Eingaben vom V8-Chart übernehmen (`KaufdatumGFT`, `FloorOverride`(+Zeit),
`StartBalanceOverride`, `AuszahlungKennung`, `MagicBase` 230250).
