#!/bin/bash
# Kompletter Neuaufbau aus extdata/raw (Downloads siehe DATEN_BERICHT.md, Abschnitt "Reproduktion").
set -e
cd "$(dirname "$0")"
python3 prepare_sources.py
python3 build_xauusd.py
python3 build_mt5_sources.py
python3 build_nas100.py
for a in "XAUUSD_ext XAUUSD.x" "NAS100_ext NAS100.x" "NAS100_ext_histdata NAS100.x" "XAUUSD_ext_oanda" "XAUUSD_ext_mt5 XAUUSD.x"; do
  set -- $a; python3 quality.py ../$1_M5.csv $1 $2 > ../work/quality_$1.txt 2>&1
done
python3 rolljumps.py > ../work/rolljumps.txt 2>&1
sha256sum ../*_M5.csv
