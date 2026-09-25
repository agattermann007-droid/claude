"""Ersatz fuer die GFT-Exporte (../data/*.csv sind nicht im Repo): Fremddaten 2022-01-03 .. 2025-12-31 im GFT-Format.

Gold = Dukascopy (Dypoi-M1), NAS100 = MT5-Broker-Export US100 (siehe ../extdata/DATEN_BERICHT.md). Korrelation der
M5-Renditen mit GFT 0,994-0,999. Gold-Spreads von Dukascopy sind breiter als bei GFT: Median je Jahr Dukascopy
30/30/33/51 Punkte, GFT 7/8/9/22 (2022-2025, Datenbericht Abschnitt 5.1) - der Gold-Spread wird je Jahr mit diesem
Verhaeltnis skaliert (mindestens 1 Punkt). NAS unveraendert. Danach laufen prep5/sig5/x39 unveraendert ('gft')."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
GOLD_FAKTOR = {"2022": 7 / 30, "2023": 8 / 30, "2024": 9 / 33, "2025": 22 / 51}
os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
for src, dst, gold in (("XAUUSD_ext_M5.csv", "XAUUSD.x_M5.csv", True), ("NAS100_ext_M5.csv", "NAS100.x_M5.csv", False)):
    n = 0
    with open(os.path.join(BASE, "extdata", src), newline="") as f, open(os.path.join(BASE, "data", dst), "w", newline="") as g:
        head = f.readline()
        g.write(head)
        for line in f:
            d = line[:10]
            if not ("2022.01.03" <= d <= "2025.12.31"):
                continue
            if gold:
                c = line.rstrip("\r\n").split("\t")
                c[8] = str(max(1, int(round(int(c[8]) * GOLD_FAKTOR[d[:4]]))))
                line = "\t".join(c) + "\r\n"
            g.write(line); n += 1
    print(dst, n, "Zeilen")
