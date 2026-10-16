# -*- coding: utf-8 -*-
"""GFT-M1-Export (D:\\Meine Ablage\\DEADBAND_Kursdaten_20261016_2245) -> NPZ fuer den Nachbau (Format wie prep_m1.py).
t = Serverzeit in Sekunden (Konvention NY + 7 h), o/h/l/c Bid, spr = Spread in Preis (Bar-Spread x Punkt).
NAS erst ab dem ersten Tag mit voller Kassasitzung (vorher nur Platzhalter-Kerzen).
Aufruf: py -3 prep_gft.py [diag]"""
import os, sys, io, glob, zipfile, numpy as np, pandas as pd
SRC = r"D:\Meine Ablage\DEADBAND_Kursdaten_20261016_2245"
OUT = os.environ.get("NPZ_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "npz_gft"))
os.makedirs(OUT, exist_ok=True)
PT = {"NAS": 0.01, "XAU": 0.01}


def lade(kurz):
    teile = []
    for f in sorted(glob.glob(os.path.join(SRC, f"{kurz}_M1_*.zip"))):
        with zipfile.ZipFile(f) as z:
            for n in z.namelist():
                teile.append(pd.read_csv(io.BytesIO(z.read(n)), sep="\t"))
    d = pd.concat(teile, ignore_index=True)
    t = pd.to_datetime(d["<DATE>"] + " " + d["<TIME>"], format="%Y.%m.%d %H:%M:%S")
    sec = t.values.astype("datetime64[s]").astype(np.int64)
    o = np.argsort(sec, kind="stable")
    d = d.iloc[o].reset_index(drop=True); sec = sec[o]
    keep = np.r_[True, np.diff(sec) > 0]
    return sec[keep], d[keep].reset_index(drop=True)


def diag_dst(sec, d):
    """Kassaeroeffnung 9:30 NY = 16:30 Server. Je Tag: Minute mit dem groessten Tickvolumen-Sprung 15:00-17:59 Server."""
    tv = d["<TICKVOL>"].to_numpy().astype(float)
    day = sec // 86400; m = (sec % 86400) // 60
    w = (m >= 900) & (m < 1080)
    df = pd.DataFrame(dict(day=day[w], m=m[w], tv=tv[w]))
    df["sprung"] = df.groupby("day")["tv"].diff()
    top = df.loc[df.groupby("day")["sprung"].idxmax().dropna().astype(int)]
    top["datum"] = pd.to_datetime(top["day"], unit="D")
    top["stunde"] = (top["m"] // 60).astype(int).astype(str) + ":" + (top["m"] % 60).astype(int).astype(str).str.zfill(2)
    abw = top[top["m"] != 990]
    print(f"NAS Tage gesamt {len(top)}, Oeffnungssprung nicht um 16:30 Server: {len(abw)}")
    print(abw.groupby(abw["datum"].dt.to_period("M"))["stunde"].agg(lambda s: s.value_counts().head(3).to_dict()).to_string())


def main():
    diag = len(sys.argv) > 1 and sys.argv[1] == "diag"
    for kurz, sym in (("NAS100_x", "NAS"), ("XAUUSD_x", "XAU")):
        sec, d = lade(kurz)
        if sym == "NAS":
            day = sec // 86400; m = (sec % 86400) // 60
            rth = (m >= 990) & (m < 1380)
            u, c = np.unique(day[rth], return_counts=True)
            voll = u[c >= 330]
            ab = int(voll[0]) * 86400
            print("NAS: erster Tag mit voller Kassasitzung", pd.to_datetime(ab, unit="s").date())
            k = sec >= ab
            sec, d = sec[k], d[k].reset_index(drop=True)
            if diag:
                diag_dst(sec, d)
        o, h, l, c = (d[x].to_numpy(float) for x in ("<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>"))
        spr = d["<SPREAD>"].to_numpy(float) * PT[sym]
        np.savez(os.path.join(OUT, f"{sym}_m1.npz"), t=sec, o=o, h=h, l=l, c=c, spr=spr)
        print(sym, len(sec), pd.to_datetime(sec[0], unit="s"), "..", pd.to_datetime(sec[-1], unit="s"),
              "Spread Median", np.median(spr), "p90", np.percentile(spr, 90))


if __name__ == "__main__":
    main()
