"""Screening 3 (ohne Konto): zusaetzliche Filter als Einstiegsfilter ('post': Signal zaehlt fuer das Folgesignal weiter)."""
import numpy as np
from s1_ablation import run, C

d = C["dir"]; g = C["sym"] == 0
up = d > 0


def dirv(x_long, x_short):
    return np.where(up, x_long, x_short)


F = {
    "ADX > 20": C["adx"] > 20,
    "ADX > 25": C["adx"] > 25,
    "ADX > 30": C["adx"] > 30,
    "ADX < 40": C["adx"] < 40,
    "ATR-Rang < 0,9": C["atrpct"] < 0.9,
    "ATR-Rang > 0,2": C["atrpct"] > 0.2,
    "ATR-Rang > 0,4": C["atrpct"] > 0.4,
    "H4-RSI mit (>50/<50)": dirv(C["h4rsi"] > 50, C["h4rsi"] < 50),
    "H4-RSI mit (>60/<40)": dirv(C["h4rsi"] > 60, C["h4rsi"] < 40),
    "D1-RSI mit (>50/<50)": dirv(C["d1rsi"] > 50, C["d1rsi"] < 50),
    "D1-RSI mit (>55/<45)": dirv(C["d1rsi"] > 55, C["d1rsi"] < 45),
    "Ausbruch 20 Kerzen": dirv(C["close"] > C["hh20"], C["close"] < C["ll20"]),
    "kein Ausbruch 20 Kerzen": ~dirv(C["close"] > C["hh20"], C["close"] < C["ll20"]),
    "ueber Vortageshoch/-tief": dirv(C["close"] > C["pdh"], C["close"] < C["pdl"]),
    "innerhalb Vortagesspanne": ~dirv(C["close"] > C["pdh"], C["close"] < C["pdl"]),
    "Tagestrend SMA20>SMA50": dirv(C["ma20"] > C["ma50"], C["ma20"] < C["ma50"]),
    "Vortag ueber SMA50": dirv(C["cprev"] > C["ma50"], C["cprev"] < C["ma50"]),
    "Abstand SMA50 < 3 Tages-ATR": np.abs(C["close"] - C["ma50"]) < 3 * C["d1atr"],
    "Abstand SMA50 < 5 Tages-ATR": np.abs(C["close"] - C["ma50"]) < 5 * C["d1atr"],
    "RSI < 85 / > 15": dirv(C["rsi"] < 85, C["rsi"] > 15),
    "RSI frisch (Vorkerze nicht jenseits)": dirv(C["rsi_prev"] <= 75, C["rsi_prev"] >= 25),
    "RSI anhaltend (Vorkerze jenseits)": dirv(C["rsi_prev"] > 75, C["rsi_prev"] < 25),
    "RSI steigt weiter": dirv(C["rsi"] > C["rsi_prev"], C["rsi"] < C["rsi_prev"]),
    "Mo-Do": C["dow"] <= 4,
    "Di-Fr": C["dow"] >= 2,
    "Kreuz-RSI > 60/<40": dirv(C["ro"] > 60, C["ro"] < 40),
}

if __name__ == "__main__":
    run("Basis (EA 6.10)")
    for nm, f in F.items():
        run(f"post: {nm}", dict(post=f))
    print("--- als Signal-Regel (zaehlt auch fuer das Folgesignal)")
    for nm in ("ADX > 25", "H4-RSI mit (>50/<50)", "D1-RSI mit (>50/<50)", "Ausbruch 20 Kerzen", "ATR-Rang > 0,2", "RSI < 85 / > 15"):
        run(f"extra: {nm}", dict(extra=F[nm]))
