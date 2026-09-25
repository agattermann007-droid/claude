"""Basis-Trades: Ergebnis (R) je Quintil verschiedener Merkmale beim Einstieg."""
import numpy as np
import r7sig as G, r7sim as M, r7kand as KD
from r7lab import D, C

p = dict(G.BASE)
E = G.entries(C, p)
rows = []
for si, s in enumerate(G.SYMS):
    tr = M.simulate(D[s], s, E[s])
    # Zuordnung Trade -> Kandidat ueber (i5, tf): Kandidaten mit gleichem Einstieg
    key = {(int(a), int(b)): int(ix) for a, b, ix in zip(E[s]["i5"], E[s]["tf"], E[s]["idx"])}
    for ie, tf, R in zip(tr["ie"], tr["tf"], tr["R"]):
        rows.append((key[(int(ie), int(tf))], R))
idx = np.array([r[0] for r in rows]); R = np.array([r[1] for r in rows])
d = C["dir"][idx]; px = C["close"][idx]
F = {
    "Stunde NY": C["nyh"][idx],
    "RSI (richtungsbereinigt)": np.where(d > 0, C["rsi"][idx], 100 - C["rsi"][idx]),
    "RSI Vorkerze": np.where(d > 0, C["rsi_prev"][idx], 100 - C["rsi_prev"][idx]),
    "RSI anderes Symbol": np.where(d > 0, C["ro"][idx], 100 - C["ro"][idx]),
    "ATR/Kurs": C["atr"][idx] / px,
    "ATR-Rang 500": C["atrpct"][idx],
    "ADX": C["adx"][idx],
    "H4-RSI": np.where(d > 0, C["h4rsi"][idx], 100 - C["h4rsi"][idx]),
    "D1-RSI": np.where(d > 0, C["d1rsi"][idx], 100 - C["d1rsi"][idx]),
    "Abstand SMA50 (Tages-ATR)": d * (px - C["ma50"][idx]) / C["d1atr"][idx],
    "Abstand SMA200 (Tages-ATR)": d * (px - C["maL"][idx]) / C["d1atr"][idx],
    "Ueber Vortageshoch (Tages-ATR)": np.where(d > 0, px - C["pdh"][idx], C["pdl"][idx] - px) / C["d1atr"][idx],
    "Ueber 20-Kerzen-Hoch (ATR)": np.where(d > 0, px - C["hh20"][idx], C["ll20"][idx] - px) / C["atr"][idx],
    "Stop / Tages-ATR": 2 * C["atr"][idx] / C["d1atr"][idx],
    "Wochentag": C["dow"][idx].astype(float),
}
print(f"Trades {len(R)}, ØR {R.mean():+.3f}")
for nm, x in F.items():
    ok = np.isfinite(x)
    qs = np.quantile(x[ok], [0, 0.2, 0.4, 0.6, 0.8, 1.0])
    out = []
    for a, b in zip(qs[:-1], qs[1:]):
        m = ok & (x >= a) & (x <= b)
        out.append(f"[{a:7.2f}..{b:7.2f}] {R[m].mean():+.2f}")
    print(f"{nm:<32s} " + " | ".join(out))
