"""Synthetische M5-Kurse im GFT-Exportformat - NUR fuer Tests der Engine (keine Forschungsaussage).

Handelszeiten wie GFT: Sonntag 18:00 NY bis Freitag 17:00 NY, taegliche Pause 17:00-18:00 NY
(Serverzeit 00:00-01:00 fehlt). Zufallsweg mit Tagesgang der Volatilitaet, Spread in Punkten.
"""
import numpy as np
import pandas as pd

from . import daten as DT

PARAM = {"XAU": dict(preis=1900.0, vol_tag=0.010, spread_pkt=32, punkt=0.01),
         "NAS": dict(preis=14000.0, vol_tag=0.012, spread_pkt=163, punkt=0.01)}


def kerzen(kurz, von="2021-01-03", bis="2022-12-30", seed=1):
    """DataFrame im Format von daten.lies_mt5 (server, open, high, low, close, tickvol, spread)."""
    p = PARAM[kurz]
    rng = np.random.default_rng(seed)
    ny = pd.date_range(pd.Timestamp(von) + pd.Timedelta(hours=18), pd.Timestamp(bis) + pd.Timedelta(hours=17), freq="5min")
    wd = ny.dayofweek.values               # 0 = Montag ... 6 = Sonntag (Kalender NY)
    h = ny.hour.values
    offen = np.ones(len(ny), bool)
    offen &= ~(wd == 5)                                   # Samstag
    offen &= ~((wd == 6) & (h < 18))                      # Sonntag vor 18:00
    offen &= ~((wd == 4) & (h >= 17))                     # Freitag ab 17:00
    offen &= ~(h == 17)                                   # Tagespause
    ny = ny[offen]
    n = len(ny)
    hh = ny.hour.values + ny.minute.values / 60.0
    gang = 0.6 + 0.9 * np.exp(-((hh - 9.5) ** 2) / 4.0) + 0.4 * np.exp(-((hh - 3.0) ** 2) / 2.0)
    s5 = p["vol_tag"] / np.sqrt(276.0) * gang
    r = rng.standard_t(5, n) * s5 * np.sqrt(3.0 / 5.0)
    # leichte Trendphasen, damit Ausbruchssignale entstehen
    drift = np.repeat(rng.normal(0, 0.0003, n // 2000 + 1), 2000)[:n] * gang
    c = p["preis"] * np.exp(np.cumsum(r + drift))
    o = np.r_[p["preis"], c[:-1]]
    spanne = np.abs(rng.normal(0, 1, n)) * s5 * c * 0.8
    hi = np.maximum(o, c) + spanne * rng.random(n)
    lo = np.minimum(o, c) - spanne * rng.random(n)
    vol = np.maximum(1, (rng.gamma(2.0, 60.0, n) * gang)).astype(np.int64)
    sp = np.maximum(1, (p["spread_pkt"] * (1.0 + 0.5 * rng.random(n)) * (1.0 + 2.0 * (hh >= 17.9) * (hh < 18.6)))).astype(np.int64)
    server = ny + pd.Timedelta(hours=7)
    df = pd.DataFrame({"server": server, "open": np.round(o, 2), "high": np.round(hi, 2), "low": np.round(lo, 2),
                       "close": np.round(c, 2), "tickvol": vol, "spread": sp})
    return df


def schreibe(ordner, von="2021-01-03", bis="2022-12-30", seed=1):
    """XAUUSD.x_M5.csv und NAS100.x_M5.csv (Format wie die GFT-Exporte) in ordner."""
    import os
    os.makedirs(ordner, exist_ok=True)
    for i, (kurz, name) in enumerate((("XAU", "XAUUSD.x_M5.csv"), ("NAS", "NAS100.x_M5.csv"))):
        DT.schreibe_mt5(kerzen(kurz, von, bis, seed + i), os.path.join(ordner, name))
