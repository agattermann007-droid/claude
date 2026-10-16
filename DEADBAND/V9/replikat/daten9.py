"""Replikat 9 - Kursdaten: M1/M5-Quellen -> M5-Reihe je Symbol im Format von Replikat_v6/prep5.build().

Zeitachse: NY-Minuten seit Epoche (Serverzeit - 7 h). Kurse Bid, Spread in Preiseinheiten.
Quellen werden nach Vorrang zusammengesetzt (GFT-Export vor freien Daten); je Kerze steht die Quelle in 'src'.
  src  1 OANDA | 2 Dukascopy (Gold) bzw. HistData (NAS) | 3 TradingView FX:XAUUSD | 4 MT5-Broker US100
       5 getdata NAS100 | 9 GFT-Export (MT5, NAS100.x/XAUUSD.x)
Spread je M5 = kleinster M1-Spread (MT5-Konvention der Exporte).
"""
import glob, io, os, sys, zipfile
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
V6 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "Replikat_v6")
sys.path.insert(0, V6)
import prep5 as P                                   # Indikatoren und Balken-Aggregation wie MT5 (unveraendert)

SCRATCH = os.environ.get("DB9_DATA", "/tmp/claude-0/-home-user-claude/3553ba7e-fec6-5bb4-911e-4fa14d84d65c/scratchpad/data")
SYMS = ("XAU", "NAS")


def m1_zu_m5(df):
    """df: Index Serverzeit (M1 oder M5), Spalten o,h,l,c,sp,tv,src -> M5-DataFrame (Index Serverzeit, Kerzenbeginn)."""
    g = df.groupby(df.index.floor("5min"))
    out = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(),
                        "sp": g.sp.min(), "tv": g.tv.sum(), "src": g.src.first()})
    return out


def lese_mt5_export(pfade):
    """MT5-Export (Tab, <DATE> <TIME> ...) aus CSV- oder ZIP-Dateien -> DataFrame M1/M5 in Serverzeit, src 9."""
    teile = []
    for p in pfade:
        if p.lower().endswith(".zip"):
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if n.lower().endswith(".csv"):
                        teile.append(pd.read_csv(io.BytesIO(z.read(n)), sep="\t"))
        else:
            teile.append(pd.read_csv(p, sep="\t"))
    d = pd.concat(teile, ignore_index=True)
    d.columns = [c.strip("<>").upper() for c in d.columns]
    ts = pd.to_datetime(d.DATE + " " + d.TIME, format="%Y.%m.%d %H:%M:%S")
    sp = d.SPREAD.to_numpy(float) * P.POINT
    df = pd.DataFrame({"o": d.OPEN.values, "h": d.HIGH.values, "l": d.LOW.values, "c": d.CLOSE.values,
                       "sp": sp, "tv": d.TICKVOL.values.astype(float), "src": np.int8(9)}, index=pd.DatetimeIndex(ts, name="t"))
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def lade_m5(sym, gft=None, frei=True, von=None, bis=None):
    """M5 je Symbol: GFT-Export (falls angegeben) hat Vorrang, freie Daten fuellen davor/danach/Luecken > 1 Tag nicht."""
    teile = []
    if gft is not None and len(gft):
        g5 = m1_zu_m5(gft) if (gft.index.to_series().diff().dt.total_seconds().median() < 300) else gft
        teile.append(g5)
    if frei:
        f = pd.read_parquet(os.path.join(SCRATCH, f"{sym}_free_m1.parquet"))
        f5 = m1_zu_m5(f)
        if teile:
            g = teile[0].index
            g0, g1 = g[0], g[-1]
            # innerhalb der GFT-Spanne nur GFT - ausser in echten Ausfaellen des Exports (Luecke zwischen zwei GFT-Kerzen
            # > 3,5 Tage, also laenger als ein langes Wochenende; z. B. NAS 06.06.-23.08.2024, Gold 11.-28.10.2024)
            gv = g.values
            j = np.searchsorted(gv, f5.index.values)
            innen = (f5.index >= g0) & (f5.index <= g1)
            jj = np.clip(j, 1, len(gv) - 1)
            luecke = (gv[jj] - gv[jj - 1]) > np.timedelta64(84, "h")
            nicht_in_gft = ~np.isin(f5.index.values, gv)
            f5 = f5[~innen | (luecke & nicht_in_gft)]
        teile.append(f5)
    df = pd.concat(teile)
    df = df[~df.index.duplicated(keep="first")].sort_index()
    if von is not None:
        df = df[df.index >= von]
    if bis is not None:
        df = df[df.index < bis]
    sp0 = P.DEFSPREAD[sym]
    df["sp"] = np.where(np.isfinite(df.sp) & (df.sp > 0), df.sp, sp0 * df.c / (15000.0 if sym == "NAS" else 2000.0))
    return df


def baue_D(m5, spread_mult=1.0):
    """m5: dict sym -> M5-DataFrame. Rueckgabe wie prep5.build(): je Symbol ny, o, h, l, c, sp, v, pday, m15, m30, h1, d1, src."""
    D = {}
    for s in SYMS:
        df = m5[s]
        ny = (df.index.values.astype("datetime64[m]").astype(np.int64) - 420)
        d = dict(ny=ny, o=df.o.to_numpy(float), h=df.h.to_numpy(float), l=df.l.to_numpy(float), c=df.c.to_numpy(float),
                 sp=df.sp.to_numpy(float) * spread_mult, v=df.tv.to_numpy(float), src=df.src.to_numpy(np.int8))
        d["pday"] = (ny + 420) // 1440
        for k, mins, off in (("m15", 15, 0), ("m30", 30, 0), ("h1", 60, 0), ("d1", 1440, 420)):
            d[k] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], mins, off)
        D[s] = d
    return D


def info(D):
    for s in SYMS:
        d = D[s]
        print(f"{s}: {len(d['ny'])} M5 {np.datetime64(int(d['ny'][0]), 'm')} .. {np.datetime64(int(d['ny'][-1]), 'm')} (NY), "
              f"D1 {len(d['d1']['t'])}, Quellen {dict(zip(*np.unique(d['src'], return_counts=True)))}")
