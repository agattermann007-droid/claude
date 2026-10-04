"""V7-Forschung: GFT-Ersatz ../data/*.csv aus den Fremddaten bauen (die GFT-Exporte liegen nicht im Repo).
XAUUSD.x  = XAUUSD_ext_M5 (Dukascopy, Spreads breiter als GFT) ab 03.01.2022
NAS100.x  = NAS100_ext_M5 (MT5-Broker US100) ab 03.01.2022 bis 31.12.2025
Format wie die GFT-Exporte (Serverzeit NY+7). Aufruf: DEADBAND_EXT=<pfad zu extdata> python y7_data.py"""
import os, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.environ.get("DEADBAND_EXT", os.path.join(os.path.dirname(HERE), "extdata"))
OUT = os.path.join(os.path.dirname(HERE), "data")
os.makedirs(OUT, exist_ok=True)
for src, dst in (("XAUUSD_ext_M5.csv", "XAUUSD.x_M5.csv"), ("NAS100_ext_M5.csv", "NAS100.x_M5.csv")):
    df = pd.read_csv(os.path.join(EXT, src), sep="\t", dtype=str)
    keep = df["<DATE>"] >= "2022.01.03"
    df[keep].to_csv(os.path.join(OUT, dst), sep="\t", index=False, lineterminator="\r\n")
    print(dst, keep.sum(), df[keep]["<DATE>"].iloc[0], df[keep]["<DATE>"].iloc[-1])
