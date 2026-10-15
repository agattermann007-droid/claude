# Datenquellen Analyzer 3 (Stand 15.10.2026)

Alle Kerzen werden mit `lib/build_alle.py` zu M5 in Qberx-Serverzeit (New York + 7 h) gebaut: `/home/user/data/m5/<INST>.parquet`.

| Quelle | Commit | Inhalt | Verwendung |
|---|---|---|---|
| ts4blader/market_data | 5246088b | MT5-Broker-Export M5, Serverzeit NY+7; US100 2021–25, US500/XAU/FX 2020–25 | dev und 2025 für NAS100, US500, XAU, FX |
| Pedram007z/BackTest-Platform, Branch market-data | 364d4848 | M1 UTC, Bid (Krypto Binance-Last), 2015-01 bis 2026-10-07 (Öl bis 10-01); Format BTM1, eigener Decoder `lib/pedram_decode.py` | dev für US30, US2000, GER40, FRA40, ESTX50, UK100, JPN225, AUS200, HK50, XAG, WTI, BRENT, BTC, ETH; gesperrt 2015–2019 und 2026 für alle |
| FutureSharks/financial-data | 7ba1d404 | OANDA M1 UTC (Mid) 2005–2020-05; HistData ETX/GRX 2010–18; Bitstamp BTC 2012–18 | gesperrt vor 2015/2020 |
| Makrokalender | siehe `kalender/_sources.csv` | FOMC (6 Quellen), CPI/NFP, EIA, NYSE-Kalender | Familie Ereignisse |

## Uhrzeit-Prüfungen
- **ts4-Uhrfehler:** Der Broker lief zeitweise fest auf UTC+2 statt NY+7. Bestimmt wurde das tageweise per Renditekorrelation gegen Pedram (`lib/ts4_fix.py`); die Korrektur ist in `qdata.TS4_PLUS1` hinterlegt.
  - US500 und XAU: 2020-03-08 bis 2020-11-01 und 2021-03-14 bis ca. 2021-04-08 jeweils +1 h.
  - US100: 2021-03-14 bis 2021-04-08 +1 h.
  - FX: 2021-01-27 bis 2021-02-08 +1 h. Gegengeprüft über EUR gegen XAU in beiden Quellen.
- **Pedram-Indizes:** Der Volatilitätssprung liegt jeweils an der lokalen Kassaeröffnung, gemessen 2021–23.
- **Pedram XAU/XAG/Öl:** UTC bestätigt gegen OANDA, 70–71 von 70–71 Wochen. BTC/ETH sind bitgleich mit Speirsy11-Binance.

## Bekannte Mängel
- Pedram XAG/USOIL/UKOIL: Von Feb bis Jul 2023 fehlt jede zweite Stunde. Dieser Zeitraum ist entfernt.
- Pedram USOIL: von 2023-12 bis 2026-06 OANDA-CFD; beim Wechsel im Juni 2026 springt das Niveau um etwa 1 %.
- Pedram GER40: von 2020-06 bis 2023-11 OANDA-CFD.
- Pedram 2026-09-25 bei XAU/XAG/Öl: als „geschlossen“ markiert, obwohl gehandelt wurde.
- Keine Volumen in Pedram: Der VWAP ist dort gleich gewichtet.
- ts4 XAU: Lücke vom 2021-04-20 bis 05-20, mit Pedram gefüllt.
