"""Fremddaten-Pruefung Gold 2010-2016 (OANDA Mid, M1): GPDF und bestehende Gold-Stroeme je Jahr."""
import glob, numpy as np, pandas as pd
import prep11 as P, prep5 as P5, gen11 as G, pa11 as PA, sim11 as M
import os
fs = sorted(glob.glob(os.path.join(os.environ.get("OANDA_DIR", "/home/user/data/oanda/pyfinancialdata/data/currencies/oanda/XAU_USD"), "*/*.csv")))
df = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates("time").sort_values("time")
t = pd.to_datetime(df["time"]).dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
ny1 = (t.values.astype("datetime64[m]").astype(np.int64))
o1, h1, l1, c1 = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
sp1 = c1 * P.SPK["XAU"]
d = P.to_m5(ny1, o1, h1, l1, c1, "XAU"); ny = d["ny"]
d["d1"] = P5.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 1440, offset=420)
d.update(ny1=ny1, o1=o1, h1m=h1, l1=l1, c1=c1, sp1=sp1)
G.data()                       # NAS bleibt
G._D = dict(G._D); G._D["XAU"] = d
PA._PREP.clear()
YEARS = [(f"{y}-01-01", f"{y+1}-01-01", str(y)) for y in range(2010, 2017)]
def show(nm, b, tpd=4):
    r = M.simulate(b, tpdelay=tpd); ok = r["why"] >= 0
    tot = M.stats(r["R"][ok], b["t"][ok], "2010-01-01", "2017-01-01")
    yrs = " ".join(f"{lab}:{M.stats(r['R'][ok], b['t'][ok], lo, hi)['sum']:+5.1f}" for lo, hi, lab in YEARS)
    print(f"{nm:22s} gesamt n{tot['n']:4d} WR{tot['wr']:3.0f}% E{tot['er']:+.3f} PF{tot['pf']:4.2f} | R je Jahr {yrs}", flush=True)
for w0, sb in ((-360, 0.10), (-360, 0.15), (-330, 0.10), (-330, 0.15)):
    show(f"GPDF w0{w0} sb{sb}", PA.sweep("XAU", -360, 1020, -1, w0, 120, 480, 0.0, 0.6, 0.0, 0, sb, 0, 3.0, 99.0, 1))
show("GPDF short-Spiegel", PA.sweep("XAU", -360, 1020, -1, -330, 120, 480, 0.0, 0.6, 0.0, 0, 0.15, 0, 3.0, 99.0, -1))
show("XA (bestehend)", G.xa(), 5)
for b in G.list_fades(names=("X0630", "X0400", "X0300S", "X1000S")):
    show(b["name"] + " (bestehend)", b, 5)
print("Goldkurs:", {y: round(float(c1[(ny1 >= np.datetime64(f'{y}-01-01','m').astype(np.int64))][0]), 0) for y in range(2010, 2017)})
