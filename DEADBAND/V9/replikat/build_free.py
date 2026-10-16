"""Freie Kursdaten -> M1 in GFT-Serverzeit (New York + 7 h), Bid-Kurse, Spread in Preiseinheiten.

Aufruf:  python3 -I build_free.py RAW OUT
  RAW = Ordner mit den Git-Klonen (siehe fetch_raw.sh), OUT = Zielordner (Parquet je Symbol)

Segmente (Spalte src):
  XAU: 1 OANDA Mid (bis 2016-09-01) | 2 Dukascopy M1 Bid/Ask (Dypoi, bis 2026-09-01) | 3 TradingView FX:XAUUSD M1 (navtemmt, ab 2026-09-09)
  NAS: 1 OANDA Mid (bis 2020-05-08) | 2 HistData NSXUSD (2020-05-11..12-31 und 2026-01..02-13) | 4 MT5-Broker US100 (2021-2025)
       | 5 getdata NAS100 (2026-03-26..09-25)
Mid-Kurse werden um den halben Modell-Spread auf Bid gesenkt. Spread-Modell proportional zum Kurs
(NAS 1,63 bei 15.000, Gold 0,32 bei 2.000; Stand GFT 2022-26 laut Replikat v11), wo die Quelle keinen hat.
Wie bei GFT entfallen Serverstunde 00 (17:00-18:00 NY) und Wochenenden.
"""
import glob, json, os, sys
import numpy as np, pandas as pd

RAW, OUT = sys.argv[1], sys.argv[2]
NY = "America/New_York"
SPM = {"NAS": (1.63, 15000.0), "XAU": (0.32, 2000.0)}


def utc_to_srv(ts):
    s = pd.DatetimeIndex(ts)
    s = s.tz_localize("UTC") if s.tz is None else s.tz_convert("UTC")
    return s.tz_convert(NY).tz_localize(None) + pd.Timedelta(hours=7)


def frame(ts_srv, o, h, l, c, sp, tv, src):
    df = pd.DataFrame({"o": np.asarray(o, float), "h": np.asarray(h, float), "l": np.asarray(l, float),
                       "c": np.asarray(c, float), "sp": np.asarray(sp, float), "tv": np.asarray(tv, float),
                       "src": np.int8(src)}, index=pd.DatetimeIndex(ts_srv, name="t"))
    return df


def modell_spread(sym, px):
    a, b = SPM[sym]
    return a * np.asarray(px, float) / b


def mid_zu_bid(sym, o, h, l, c):
    sp = modell_spread(sym, c)
    return o - sp / 2, h - sp / 2, l - sp / 2, c - sp / 2, sp


def oanda(sym, instr, bis):
    fs = sorted(glob.glob(f"{RAW}/oanda_futuresharks/pyfinancialdata/data/currencies/oanda/{instr}/*/*.csv"))
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    d["ts"] = pd.to_datetime(d["time"])
    d = d[(d.ts >= "2009-12-01") & (d.ts < bis)].drop_duplicates("ts").sort_values("ts")
    o, h, l, c, sp = mid_zu_bid(sym, d.open.values, d.high.values, d.low.values, d.close.values)
    return frame(utc_to_srv(d.ts), o, h, l, c, sp, d.volume.values, 1)


def dypoi(von, bis):
    fs = sorted(glob.glob(f"{RAW}/dypoi_dukascopy_xauusd_m1/XAUUSD_M1_*.csv"))
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    d["ts"] = pd.to_datetime(d["timestamp"])
    d = d[(d.ts >= von) & (d.ts < bis)].drop_duplicates("ts").sort_values("ts")
    sp = np.minimum(d.open_ask - d.open_bid, d.close_ask - d.close_bid).clip(lower=0).values
    return frame(utc_to_srv(d.ts), d.open_bid, d.high_bid, d.low_bid, d.close_bid, sp, d.volume_bid * 2837.4, 2)


def navtemmt(von):
    d = pd.read_csv(f"{RAW}/navtemmt_xauusd-autodata/data/XAUUSD_data.csv", parse_dates=["datetime"])
    d = d[d.datetime >= von].drop_duplicates("datetime").sort_values("datetime")
    sp = modell_spread("XAU", d.close.values)
    return frame(utc_to_srv(d.datetime), d.open, d.high, d.low, d.close, sp, d.volume, 3)


def histdata(bereiche):
    rows = []
    for f in sorted(glob.glob(f"{RAW}/histdata_nsxusd_better-backtest/data/histdata/nsxusd/normalized/*.json")):
        rows.extend(json.load(open(f)))
    h = pd.DataFrame(rows)
    ts = pd.to_datetime(h.timestamp, unit="ms")
    # Quellzeit -> UTC (DATEN_BERICHT Abschnitt 4): bis 2018 NY-Ortszeit, ab 2019 Europe/Athens - 7 h
    early = ts < pd.Timestamp("2019-01-01")
    utc = pd.Series(pd.NaT, index=h.index, dtype="datetime64[ns]")
    utc[early] = ts[early].dt.tz_localize(NY, ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC").dt.tz_localize(None)
    utc[~early] = (ts[~early] + pd.Timedelta(hours=7)).dt.tz_localize("Europe/Athens", ambiguous="NaT",
                                                                     nonexistent="NaT").dt.tz_convert("UTC").dt.tz_localize(None)
    h["utc"] = utc
    h = h.dropna(subset=["utc"])
    keep = np.zeros(len(h), bool)
    for a, b in bereiche:
        keep |= ((h.utc >= a) & (h.utc < b)).values
    h = h[keep].drop_duplicates("utc").sort_values("utc")
    sp = modell_spread("NAS", h.close.values)
    return frame(utc_to_srv(h.utc), h.open, h.high, h.low, h.close, sp, h.volume, 2)


def mt5_us100():
    d = pd.read_csv(f"{RAW}/ts4blader_market_data/US100/M1_seed.csv", sep="\t")
    d.columns = [c.strip("<>") for c in d.columns]
    ts = pd.to_datetime(d.DATE + " " + d.TIME, format="%Y.%m.%d %H:%M:%S")
    sp = d.SPREAD.values * 0.1
    sp = np.where(sp > 0, sp, modell_spread("NAS", d.CLOSE.values))
    return frame(ts, d.OPEN, d.HIGH, d.LOW, d.CLOSE, sp, d.TICKVOL, 4)


def getdata(von, bis):
    d = pd.read_csv(f"{RAW}/getdata_nas100_1m/NAS100_1m.csv")
    d["ts"] = pd.to_datetime(d.datetime, utc=True).dt.tz_localize(None)
    d = d[(d.ts >= von) & (d.ts < bis)].drop_duplicates("ts").sort_values("ts")
    o, h, l, c, sp = mid_zu_bid("NAS", d.open.values, d.high.values, d.low.values, d.close.values)
    return frame(utc_to_srv(d.ts), o, h, l, c, sp, d.volume, 5)


def sessionsfilter(df):
    t = df.index
    return df[(t.hour != 0) & (t.dayofweek < 5)]


def zusammen(teile):
    df = pd.concat(teile)
    df = df[~df.index.duplicated(keep="first")].sort_index()
    return sessionsfilter(df)


def main():
    os.makedirs(OUT, exist_ok=True)
    xau = zusammen([dypoi("2016-09-01", "2026-09-02"), oanda("XAU", "XAU_USD", "2016-09-01"), navtemmt("2026-09-02")])
    nas = zusammen([mt5_us100(), oanda("NAS", "NAS100_USD", "2020-05-09"),
                    histdata([("2020-05-09", "2021-01-04"), ("2025-12-31 22:00", "2026-02-14")]),
                    getdata("2026-02-14", "2026-10-17")])
    for nm, df in (("XAU", xau), ("NAS", nas)):
        df.to_parquet(f"{OUT}/{nm}_free_m1.parquet")
        seg = df.groupby("src").apply(lambda g: (len(g), str(g.index[0]), str(g.index[-1])))
        print(nm, len(df), df.index[0], df.index[-1])
        for s, v in seg.items():
            print("   src", s, v)


if __name__ == "__main__":
    main()
