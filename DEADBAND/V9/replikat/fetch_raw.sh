#!/bin/bash
# Laedt die oeffentlichen Rohdaten (siehe DEADBAND/extdata/DATEN_BERICHT.md, Abschnitt 9) nach $1
set -x
R=$1; cd $R || exit 1
[ -d dypoi_dukascopy_xauusd_m1 ] || git clone --depth 1 https://github.com/Dypoi/XAUUSD_Dataset.git dypoi_dukascopy_xauusd_m1
if [ ! -d histdata_nsxusd_better-backtest ]; then
  git clone --filter=blob:none --no-checkout --depth 1 https://github.com/hizawye/better-backtest.git histdata_nsxusd_better-backtest
  (cd histdata_nsxusd_better-backtest && git sparse-checkout set --no-cone 'data/histdata/nsxusd/*' 'scripts/histdata/*' README.md && git checkout)
fi
if [ ! -d oanda_futuresharks ]; then
  git clone --filter=blob:none --no-checkout --depth 1 https://github.com/FutureSharks/financial-data.git oanda_futuresharks
  (cd oanda_futuresharks && git sparse-checkout set --no-cone 'pyfinancialdata/data/currencies/oanda/NAS100_USD/*' 'pyfinancialdata/data/currencies/oanda/XAU_USD/*' && git checkout)
fi
mkdir -p ts4blader_market_data/US100 antondonev_tiamat
[ -s ts4blader_market_data/US100/M1_seed.csv ] || curl -sSL -o ts4blader_market_data/US100/M1_seed.csv https://media.githubusercontent.com/media/ts4blader/market_data/5246088b258b9e94cf43300e5bd8769695c49526/US100/M1_seed.csv
[ -s antondonev_tiamat/XAUUSD_M1_RAW.csv ] || curl -sSL -o antondonev_tiamat/XAUUSD_M1_RAW.csv https://media.githubusercontent.com/media/AntonDonev/Tiamat/1c2e8372281dee502fd52a40f8ee007b13a992cc/TiamatOffline/XAUUSD_M1_RAW.csv
du -sh $R/*
echo FERTIG
