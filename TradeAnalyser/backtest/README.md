# Backtest für ta_mt5.py

Mit diesen Werkzeugen sind die Zahlen in `../BERICHT_mt5-1.4.md` entstanden. Die Kursdaten sind nicht im Repo; `hole_daten.sh` lädt sie und prüft ihre Prüfsummen.

```sh
./hole_daten.sh                 # Rohdaten nach ../data (US100, GER30/DAX, ETHUSDT)
pip install pyarrow matplotlib  # pyarrow für die ETH-Parquet-Dateien, matplotlib für den Chart im Integrationstest
python3 prep.py                 # -> ../data/NAS100_M5.pkl, ../data_ger26, ../data_gerduk, ../data_eth (Serverzeit NY+7 wie Qberx)

# Kennzahlen je Jahr (ein Prozess je Jahr), Modul frei wählbar; --out schreibt die Signale für tabelle.py:
python3 -W ignore bt.py --modul ../ta_mt5.py --inst NAS100 --jahre 2021,2022,2023,2024,2025 --out r14_nas.pkl
BT_DATA=../data_ger26  python3 -W ignore bt.py --modul ../ta_mt5.py --inst GER40 --jahre 2026 --out r14_ger26.pkl
BT_DATA=../data_gerduk python3 -W ignore bt.py --modul ../ta_mt5.py --inst GER40 --jahre 2021,2022,2023 --out r14_gerduk.pkl
BT_DATA=../data_eth    python3 -W ignore bt.py --modul ../ta_mt5.py --inst ETH --jahre 2021,2022,2023,2024,2025,2026 --out r14_eth.pkl
# dasselbe mit --modul ../ta_mt5_v1.3_backup.py und --out r13_nas.pkl, r13_ger26.pkl, r13_gerduk.pkl, r13_eth.pkl
python3 -W ignore tabelle.py    # im selben Ordner wie die .pkl-Dateien -> Tabelle wie ergebnis_tabelle.md
python3 -W ignore bt.py --modul ../ta_mt5.py --set '{"ZIEL_R": 0.5}' --jahre 2025     # Stellschraube testen
python3 -W ignore bt.py --modul kandidaten/ta_momentum_continuation.py --jahre 2025    # die anderen Kandidaten (Bericht Abschnitt 4)

# Vergleich mit Zufallseinstiegen gleicher Geometrie und gleichen Zeitfensters (Bericht Abschnitt 5):
python3 -W ignore zufall14.py NAS100 2025 3

# Harness gegen den echten Programmweg prüfen (Script als Prozess, TA_Export-Ordner nachgebaut):
python3 -W ignore validate.py --modul ../ta_mt5.py --inst NAS100 --n 60 --nur-trades
# Integrationstest über alle drei Instrumente (setup, --nur, News-Sperre, Log, Schatten, --auswerten, Chart):
NUR_FENSTER=1 python3 -W ignore integration.py ../ta_mt5.py 80
# Zurückrollen: gemischtes Log mt5-1.3/mt5-1.4, --auswerten mit beiden Fassungen:
python3 -W ignore rollback_test.py ../ta_mt5.py ../ta_mt5_v1.3_backup.py
```

| Datei | Zweck |
|---|---|
| `bt.py` | Harness: ein Trader je Instrument fragt bei jeder M5-Kerze ab, solange er flach ist; Auswertung mit `bewerte()` des Scripts; `--out` speichert die Signale (pickle) |
| `validate.py` | gleicht die Harness mit dem Prozessaufruf des Scripts ab |
| `integration.py` | Ende-zu-Ende-Test über den echten Programmweg |
| `prep.py`, `hole_daten.sh` | Datenbeschaffung und Umrechnung in Serverzeit |
| `geometrie.py` | Vergleich: Market-Einstieg in zufälliger Richtung mit festem Stop/Target in ATR5, ganzer Tag |
| `zufall14.py` | Vergleich: Zufallsrichtung mit genau der Geometrie und dem Zeitfenster von mt5-1.4 |
| `rollback_test.py` | gemischtes Log aus mt5-1.3 und mt5-1.4, `--auswerten` mit beiden Fassungen |
| `kandidaten/` | die vier anderen Regel-Kandidaten aus der Variantensuche (nur zum Nachrechnen) |
| `scan.py` | bedingte Trefferquoten je Merkmal (VWAP-Lage, Trend, Stunde, Kerze) |
| `tabelle.py` | Vergleichstabelle mt5-1.3 / mt5-1.4 aus den `--out`-Dateien (`ergebnis_tabelle.md`) |

## Annahmen

- **Kosten:** Spread 1,5 Punkte bei NAS100 und GER40, 2 USD bei ETH, nur in der Netto-Spalte. Kein Slippage, keine Swaps.
- **News:** Kein News-Kalender.
- **Füllung:** Berührung zählt als Füllung. Bei Stop und Target in derselben Kerze zählt der Stop. Nach 480 min wird zum letzten Kurs bewertet.
- **M30-Kerzen:** Sie werden aus den M5-Kerzen gebildet; die laufende M30-Kerze ist entsprechend unvollständig.
