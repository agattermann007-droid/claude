# -*- coding: utf-8 -*-
"""Bar-Spread (M1-Export) gegen echten Tick-Spread je Minute; nach Uhrzeit NY. Grundlage fuer das GFT-Kostenmodell."""
import os, numpy as np, pandas as pd
W = os.path.dirname(os.path.abspath(__file__))
for sym, f in (("NAS", "NAS100_x"), ("XAU", "XAUUSD_x")):
    z = np.load(os.path.join(W, "live", f"ticks_{f}.npz"))
    t = z["t"] // 1000; sp = z["ask"] - z["bid"]
    m = t // 60
    tk = pd.DataFrame(dict(m=m, sp=sp)).groupby("m")["sp"].agg(["mean", "median", "max", "size"])
    b = np.load(os.path.join(W, "npz_gft", f"{sym}_m1.npz"))
    bar = pd.Series(b["spr"], index=b["t"] // 60, name="bar")
    j = tk.join(bar, how="inner")
    j["ny_h"] = ((j.index % 1440) // 60 - 7) % 24
    print(f"\n{sym}: {len(j)} Minuten mit Ticks und Bar | Bar-Spread / Tick-Mittel (Median): {np.median(j['bar'] / j['mean']):.2f}")
    print(f"  Tick-Spread Mittel {j['mean'].mean():.3f}  Median {j['median'].median():.3f}  | Bar-Spread Mittel {j['bar'].mean():.3f}")
    g = j.groupby("ny_h").agg(tick_mittel=("mean", "mean"), bar=("bar", "mean"), n=("size", "size"))
    print(g.round(3).T.to_string())
    # Kurs zum Vergleich mit dem Nachbau-Modell (proportional)
    c = b["c"][-20000:].mean()
    spk = {"NAS": 1.63 / 15000, "XAU": 0.32 / 2000}[sym]
    print(f"  Nachbau-Modell bei Kurs {c:.0f}: {c * spk:.3f}")
