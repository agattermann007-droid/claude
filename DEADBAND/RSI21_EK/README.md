# RSI21 EK (Eigenkapital): Replikat, Optimierung, EA

RSI21 Continuation aus DEADBAND LIVE 4 Build 6.60 als eigene Strategie für **eigenes Kapital**: ohne Prop-Firmen-Regeln,
Größe in % der Equity (Zinseszins), auf Rendite optimiert. Bericht: `RSI21_EK_Bericht.md`.

Kursdaten und Zwischenstände liegen **nicht** im Repo (`cache/`, `../extdata/*.csv`).

## Daten

`ek_data.py` baut einen durchgehenden M5-Datensatz beider Symbole (NY-Zeit, Serverzeit = NY + 7 h):

| Symbol | Quelle | Zeitraum |
|---|---|---|
| Gold | `../extdata/XAUUSD_ext_M5.csv` (OANDA / Dukascopy) | 2006-03-20 – 2026-09-02 |
| NAS100 | `../extdata/NAS100_ext_M5.csv` (OANDA / HistData / MT5-Broker US100), ab 2026-01-01 `../extdata/NAS100_duka_M5.csv` (Dukascopy-Ticks, Kerzen 16:15–16:55 NY flach ergänzt) | 2005-01-03 – 2026-08-28 |

Neu aufbauen: Rohdaten laut `../extdata/DATEN_BERICHT.md` (Abschnitte 9 und 10) laden, dann `../extdata/scripts/run_all.sh`
und `../extdata/scripts/build_nas_dukascopy.py`. Die Prüfsummen stimmen mit dem Datenbericht überein.

Spread wie Replikat v6 (`gext.load`): max(Datei-Spread, Kurs × relativer GFT-Spread) („breit“), Kommission Gold 5 $/Lot,
Swap als Zinsmodell (Long zahlt US-Leitzins + 2,5 %, Short erhält Leitzins − 2,5 %, je Jahr, dreifach nach Mittwoch).

## Dateien

| Datei | Inhalt |
|---|---|
| `ek_data.py` | Datensatz 2006–2026 → `cache/D.pkl` |
| `ek_sig.py` | RSI21-Signale: `features` (einmal je Datensatz) und `select` (Schwellen, Filter, Zeitfenster, Zeitebenen, Folgesignal); `cross_ea` = RSI des anderen Symbols wie im EA |
| `ek_sim.py` | Eigenkapital-Kontomotor (numba): Plätze je Symbol, Stop/Ziel/Einstand/Nachzug/Teilgewinn/Zeit-Ausstieg, Zinseszins, Margin, Swap, Kommission, Störungen |
| `ek_eval.py` | Kennzahlen: CAGR, größter Rückgang, Sharpe, Volatilität, Trades, Trefferquote, R je Trade, PF, Jahre |
| `ek_base.py` | Ausgangslage: RSI21 aus 6.60 als Eigenkapital-Konto, Aufschlüsselung je Symbol/Zeitebene/Richtung/Stunde/Jahr |
| `ek_ofat.py` | Sensitivität: jeder Parameter einzeln (1 % Risiko) → `ergebnisse/ek_ofat.json` |
| `ek_opt.py` | parallele Auswertung von Varianten (je Periode T 2006–16, V 2017–21, Z 2022–26, G gesamt) |
| `ek_ca.py` | Koordinatensuche: Rendite bei gleicher Schwankung (25 % Jahresvolatilität), 4 Störungen; `R:TV` = Walk-Forward (Auswahl 2006–21, Sperre für T und V), `R:TVZ` = alle Perioden → `ergebnisse/ek_ca_*.json/.log` |
| `ek_final.py` | Endbewertung: Vergleich bei gleicher Schwankung (16 Störungen), Risiko-Tabelle (1:20/1:30/1:100), Jahre, Stress, Monte Carlo → `ergebnisse/ek_final.json` |
| `t_ek_sim.py` | Prüfung: Signale = `sig5.r21_signals`, Konto = `eng10` mit abgeschalteten GFT-Regeln (Trade für Trade) → `ergebnisse/t_ek_sim.txt` |
| `t_ek_port.py` | Abgleich EA ↔ Replikat: Tagesregime aus H1 (EA) gegen D1 (Replikat), RSI des anderen Symbols → `ergebnisse/t_ek_port.txt` |
| `t_ek_set.py` | Prüfung: EA-Voreinstellungen = `RSI21_EK.set` = Endstand des Replikats |
| `RSI21_EK.mq5`, `RSI21_EK.set` | EA und Preset |

## Ablauf

```
pip install numpy pandas numba
python ek_data.py                 # Datensatz -> cache/D.pkl
python t_ek_sim.py                # Pruefung gegen sig5/eng10
python ek_base.py 0.5             # Ausgangslage
python ek_ofat.py                 # Sensitivitaet
python ek_ca.py R:TV 4            # Walk-Forward-Suche (Auswahl 2006-21)
python ek_ca.py R:TVZ 4           # Endstand (alle Perioden, Sperre je Periode)
python ek_final.py <Risiko>       # Endbewertung
python t_ek_port.py && python t_ek_set.py && python ../Replikat_v6/t_mq5.py RSI21_EK.mq5
```
