# Replikat v13 – Nachbau v12 auf dem GFT-Feed (Windows)

Fortsetzung von `Replikat_v12/` (Aufbau, Konventionen, Datenmängel dort). Neu in v13, alles auf Alex' Windows-PC gerechnet:

## Datensätze

| Satz | Vorbereitung | Startmodul | Fenster |
|---|---|---|---|
| GFT-Feed (M1-Export 16.10.2026, NAS ab 28.10.2019, Gold ab 2011) | `py -3 prep_gft.py` → `npz_gft/`, dann `py -3 g_prep.py` (`REP_SPREAD=gft` echte Bar-Spreads, `=modell` altes Modell) | `xg.py` | `xg.WING`: 2022, 2023, 2024-01–2025-02, 2025-02–2025-10 |
| Fremddaten wie v12 (Dukascopy, HistData, OANDA) | `py -3 e_prep.py` (Pfade unter `../fremd/`) | `xe.py` | `evl11.WIN5` |

`prep11.py`: Schalter `REP_SPREAD=gft` nimmt den Bar-Spread des GFT-Exports (NAS × 1,0, Gold × 1,1; kalibriert gegen Ticks Sep./Okt. 2026, `a2_spread.py`).

## Windows

Rechenprozesse starten frisch und erben die Signale nicht. `evl11.INIT = (gsetup.init_worker, (build, kw))` konfiguriert jeden Prozess. Alle Skripte haben einen `if __name__ == "__main__"`-Block. Kontrolle: Auf den Fremddaten trifft der Aufbau den V12-Bericht exakt.

## Skripte

| Datei | Inhalt |
|---|---|
| `mt5_live_holen.py` | Orders/Deals/Ticks/Symboldaten aus dem laufenden GFT-MT5 (nur lesend) |
| `a1_trades.py` | Live-Trades je Position: Modul, R, Haltedauer, Ausstieg, Spread |
| `a2_spread.py` | Bar-Spread gegen Tick-Spread |
| `g_live.py` | Live-Trades gegen Nachbau-Signale (gleiche Minute, Stop, R) |
| `g_streams.py` | Stromebene je Jahr auf dem GFT-Feed |
| `gsetup.py` | Builds V8/V10/V12 + Schalter: `off`, `tick`, `tick_risk`, `risk`, `sr_risk`, `xa_ein` |
| `g_base.py`, `g_var.py`, `g_mods.py`, `g_final.py` | Kontoebene: Grundlinie, gepaarte Varianten, Modul-Bilanz, Endauswertung mit `--slip` |

Aufrufbeispiel: `py -3 g_var.py gft V8_ohneXA V13 --seeds 32 --workers 10` (Zwischenspeicher `erg_*/var_*.pkl`).

Wichtig: Der Live-Stand ist **V8 ohne XA** (`V8_ohneXA`), nicht V8 – XA handelt live nie (Bericht Abschnitt 3).
