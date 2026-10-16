# -*- coding: utf-8 -*-
"""Live-Trades je Position: Modul, Risiko (SL-Abstand), R, Haltedauer, Ausstiegsgrund, Spread beim Einstieg."""
import os, json, numpy as np, pandas as pd
W = os.path.dirname(os.path.abspath(__file__))
L = os.path.join(W, "live")
deals = pd.read_csv(os.path.join(L, "deals.csv"), sep=";")
orders = pd.read_csv(os.path.join(L, "orders.csv"), sep=";")
info = json.load(open(os.path.join(L, "symbole.json"), encoding="utf-8"))
CS = {s: float(info[s]["trade_contract_size"]) for s in info}
print("Kontrakt:", CS, "| Stellen:", {s: info[s]["digits"] for s in info})
for d in (deals, orders):
    for c in [c for c in d.columns if c.startswith("time") and not c.endswith("msc")]:
        d[c] = pd.to_datetime(d[c], unit="s")
tick = {}
for s in CS:
    z = np.load(os.path.join(L, f"ticks_{s.replace('.', '_')}.npz"))
    tick[s] = (z["t"], z["bid"], z["ask"])

def spread_bei(s, t_ms):
    t, b, a = tick[s]
    i = np.searchsorted(t, t_ms, side="right") - 1
    if i < 0 or t_ms - t[i] > 60_000:
        return np.nan
    return a[i] - b[i]

d = deals[deals["symbol"].notna() & (deals["position_id"] > 0)]
rows = []
for pid, g in d.groupby("position_id"):
    e = g[g["entry"] == 0]
    x = g[g["entry"] != 0]
    if e.empty or x.empty:
        continue
    e = e.iloc[0]
    o = orders[(orders["position_id"] == pid)].sort_values("time_setup")
    sl = o["sl"].iloc[0] if len(o) else np.nan
    tp = o["tp"].iloc[0] if len(o) else np.nan
    sym, vol, px = e["symbol"], e["volume"], e["price"]
    lng = e["type"] == 0
    risk = abs(px - sl) * vol * CS[sym] if sl and sl > 0 else np.nan
    net = (x["profit"] + x["commission"] + x["swap"] + x["fee"]).sum() + e["commission"]
    ex = x.iloc[-1]
    grund = "SL" if str(ex["comment"]).startswith("[sl") else "TP" if str(ex["comment"]).startswith("[tp") else "EA"
    sp = spread_bei(sym, int(e["time_msc"]))
    rows.append(dict(ein=e["time"], aus=ex["time"], sym=sym.split(".")[0], richt="L" if lng else "S", magic=int(e["magic"]),
                     modul=str(e["comment"]) if isinstance(e["comment"], str) else "-", lot=vol, preis=px, sl=sl, tp=tp,
                     stop_pkt=abs(px - sl) if sl else np.nan, ziel_pkt=abs(tp - px) if tp else np.nan,
                     risiko=risk, netto=net, R=net / risk if risk else np.nan, min=(ex["time"] - e["time"]).total_seconds() / 60,
                     grund=grund, spread=sp, spread_stop=sp / abs(px - sl) if sl else np.nan))
T = pd.DataFrame(rows).sort_values("ein").reset_index(drop=True)
T.to_csv(os.path.join(W, "a1_trades.csv"), sep=";", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
v8 = T[T["ein"] >= "2026-09-28"]
print(v8[["ein", "sym", "richt", "modul", "lot", "stop_pkt", "ziel_pkt", "risiko", "netto", "R", "min", "grund", "spread", "spread_stop"]].round(2).to_string())
print("\nV8-Phase ab 28.09.: Trades", len(v8), "Netto", round(v8["netto"].sum(), 2), "Summe R", round(v8["R"].sum(), 2))
g = v8.groupby("modul").agg(n=("R", "size"), R=("R", "sum"), netto=("netto", "sum"), risiko_mittel=("risiko", "mean"),
                            treffer=("netto", lambda s: (s > 0).mean()))
print(g.round(2).to_string())
alt = T[T["ein"] < "2026-09-28"]
print("\nAlte Phase bis 25.09.: Trades", len(alt), "Netto", round(alt["netto"].sum(), 2), "Summe R", round(alt["R"].sum(), 2))
print(alt.groupby("modul").agg(n=("R", "size"), R=("R", "sum"), netto=("netto", "sum")).round(2).to_string())
