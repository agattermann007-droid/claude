# -*- coding: utf-8 -*-
"""Nur lesend: Orders (SL/TP), Deals, Ticks seit 28.09.2026 und Symboldaten aus dem laufenden GFT-MT5.
Schreibt in den Ordner live/ neben diesem Skript (neue Dateien, nichts wird ueberschrieben)."""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd, MetaTrader5 as mt5

TERM = r"C:\Program Files\Goat Funded MT5 Terminal\terminal64.exe"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live")
os.makedirs(OUT, exist_ok=True)
UTC = dt.timezone.utc

def neu(name):
    p = os.path.join(OUT, name)
    assert not os.path.exists(p), p
    return p

if not mt5.initialize(path=TERM):
    print("MT5 nicht erreichbar", mt5.last_error()); sys.exit(2)
acc, ti = mt5.account_info(), mt5.terminal_info()
print("Server", acc.server, "Balance", acc.balance, "Daten", ti.data_path)
von, bis = dt.datetime(2026, 8, 1, tzinfo=UTC), dt.datetime.now(UTC) + dt.timedelta(days=2)
for name, fn in (("orders", mt5.history_orders_get), ("deals", mt5.history_deals_get)):
    r = fn(von, bis)
    df = pd.DataFrame([x._asdict() for x in r]) if r else pd.DataFrame()
    df.to_csv(neu(f"{name}.csv"), sep=";", index=False)
    print(name, len(df))
info = {}
for s in ("NAS100.x", "XAUUSD.x"):
    info[s] = mt5.symbol_info(s)._asdict()
    t0 = dt.datetime(2026, 9, 7, tzinfo=UTC)
    teile = []
    while t0 < bis:
        t1 = t0 + dt.timedelta(days=1)
        r = mt5.copy_ticks_range(s, t0, t1, mt5.COPY_TICKS_ALL)
        if r is not None and len(r):
            teile.append(pd.DataFrame(r)[["time_msc", "bid", "ask", "flags"]])
        t0 = t1
    d = pd.concat(teile, ignore_index=True)
    np.savez_compressed(neu(f"ticks_{s.replace('.', '_')}.npz"), t=d["time_msc"].to_numpy(), bid=d["bid"].to_numpy(),
                        ask=d["ask"].to_numpy(), flags=d["flags"].to_numpy())
    print(s, "Ticks", len(d), pd.to_datetime(d["time_msc"].iloc[0], unit="ms"), "..", pd.to_datetime(d["time_msc"].iloc[-1], unit="ms"))
with open(neu("symbole.json"), "w", encoding="utf-8") as fh:
    json.dump(info, fh, indent=1, default=str)
mt5.shutdown()
