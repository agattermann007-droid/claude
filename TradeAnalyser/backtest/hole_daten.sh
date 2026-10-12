#!/bin/sh
# Laedt die oeffentlichen Kursdaten fuer den Backtest nach ../data (nicht im Repo, siehe README.md).
set -e
cd "$(dirname "$0")/.." && mkdir -p data/eth5 && cd data
curl -sSf -o US100_M5.csv "https://media.githubusercontent.com/media/ts4blader/market_data/5246088b258b9e94cf43300e5bd8769695c49526/US100/US100_M5.csv"
echo "db36c6ae92ce71a493a8af8aa926f2d07920280bec8defb777edb6ac108af742  US100_M5.csv" | sha256sum -c -
curl -sSf -o GER30_1m_head.csv https://raw.githubusercontent.com/getdata-finance/ger30-1m-ohlcv-index-historical-data/aa3f192e943062c6ed826fe9e79a21f0b36ef558/GER30_1m.csv
curl -sSf -o GER30_1m_tag.csv https://raw.githubusercontent.com/getdata-finance/ger30-1m-ohlcv-index-historical-data/f432d3f2b3cf2a0e7990a3d33cecba348a66e09b/GER30_1m.csv
curl -sSf -o DEUIDXEUR_M5.csv https://raw.githubusercontent.com/TheSnowGuru/Stocks-Futures-Financial-Time-series-Tick-Bar-Data/5fa48d39fd20858d6591db25e6eeee5de45ce6fd/indices/dax30/DEUIDXEUR_M5.csv
sha256sum -c - <<'SUMS'
f2692e0d1e34ef8ed79e52d9a88ccc4d3a5cb9cf82d0809c4c0066e183dc89d7  GER30_1m_head.csv
e9252a91d07e6dfc3c28aefc729bc66742b7ef5a1bbaee4e6807e2f27cc96b85  GER30_1m_tag.csv
6a2b1aa46b0ab4c169fb01e7e516ff8bcf7f9430cdd986341d98e68a89f929da  DEUIDXEUR_M5.csv
SUMS
for y in 2021 2022 2023 2024 2025 2026; do for m in 01 02 03 04 05 06 07 08 09 10 11 12; do
  [ "$y$m" -gt 202609 ] && continue
  f=ETHUSDT-5m-$y-$m.parquet
  curl -sSf -o eth5/$f "https://media.githubusercontent.com/media/Speirsy11/crypto-dataset/92c4399f5a5438101410a957763d421f85d9b3f7/data/interval_id=5m/symbol_id=ETHUSDT/year=$y/month=$m/$f"
done; done
echo fertig
