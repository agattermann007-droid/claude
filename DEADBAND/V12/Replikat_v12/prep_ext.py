"""Replikat v12 - erweiterte Datenbasis 2010-2026 fuer ein drittes Pruefungsfenster (Konten mit Start 2011-2015).

Gold vor 2016-09-01: OANDA XAU_USD M1 (Mid, github.com/FutureSharks/financial-data, Pfad ueber OANDA_DIR) als Bid-Ersatz
(Abweichung ~ halber Spread, das Spread-Modell kommt wie sonst aus prep11). Ab 2016-09-01 unveraendert Dukascopy.
NAS: dieselbe Datei wie im Standardsatz (HistData ab 2010-11).
Ergebnis: NPZ_EXT/XAU_m1.npz (zusammengesetzt) und NPZ_EXT/NAS_m1.npz (Verweis). Danach:
  NPZ_DIR=$NPZ_EXT REP_CACHE=$CACHE_EXT python prep11.py
Wochenend-Einzelkurse (Fr 17:00 bis So 17:00 NY) werden entfernt.
"""
import glob, os, numpy as np, pandas as pd

OANDA = os.environ.get("OANDA_DIR", "/home/user/data/oanda/pyfinancialdata/data/currencies/oanda/XAU_USD")
NPZ = os.environ.get("NPZ_STD", "/home/user/work/npz")
OUT = os.environ.get("NPZ_EXT", "/home/user/work/npz_ext")
CUT = pd.Timestamp("2016-09-01 00:00:00")          # NY-Ortszeit


def main():
    os.makedirs(OUT, exist_ok=True)
    fs = sorted(glob.glob(os.path.join(OANDA, "*/*.csv")))
    df = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates("time").sort_values("time")
    t = pd.to_datetime(df["time"]).dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    keep = (t < CUT).to_numpy().copy()
    # Wochenende: Freitag ab 17:00 bis Sonntag vor 17:00 NY
    dow = t.dt.dayofweek.to_numpy(); hr = t.dt.hour.to_numpy()
    we = ((dow == 4) & (hr >= 17)) | (dow == 5) | ((dow == 6) & (hr < 17))
    keep &= ~we
    t = t[keep]; df = df[keep]
    srv = (t + pd.Timedelta(hours=7)).values.astype("datetime64[s]").astype(np.int64)
    z = np.load(os.path.join(NPZ, "XAU_m1.npz"))
    cut_srv = int((CUT + pd.Timedelta(hours=7)).to_datetime64().astype("datetime64[s]").astype(np.int64))
    m = z["t"] >= cut_srv
    out = dict(t=np.r_[srv, z["t"][m]])
    for k in ("o", "h", "l", "c"):
        src = {"o": "open", "h": "high", "l": "low", "c": "close"}[k]
        out[k] = np.r_[df[src].to_numpy(float), z[k][m]]
    np.savez(os.path.join(OUT, "XAU_m1.npz"), **out)
    nas = os.path.join(OUT, "NAS_m1.npz")
    if not os.path.exists(nas):
        os.symlink(os.path.join(NPZ, "NAS_m1.npz"), nas)
    print("XAU ext", len(out["t"]), pd.Timestamp(out["t"][0], unit="s"), pd.Timestamp(out["t"][-1], unit="s"),
          "OANDA-Minuten", len(srv))


if __name__ == "__main__":
    main()
