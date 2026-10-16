"""Replikat 9 - Oktober 2026: welche Regel haette welchen Live-Trade gesperrt? (Signal-Ebene, Live-Ergebnisse in R)

Tagesbalken NAS: freie CFD-Daten (D1 Servertag) bis zum letzten vollstaendigen Tag, danach NQ-Futures (Yahoo NQ=F, Tag
18:00-17:00 ET = Servertag) aus github.com/Kubula-xu/claude-finance-data, skaliert auf das CFD-Niveau (Median-Verhaeltnis
der ueberlappenden Tage). Gold: XAU-Tagesbalken aus den freien Daten (TradingView-Reihe bis 16.10.).
Die Intraday-Regeln (NA, TR) brauchen M5-Kurse und fehlen hier fuer NAS.
"""
import os, sys
import numpy as np, pandas as pd
import aufbau9 as AU, regime9 as RG, check_live9 as CL

KUB = "/tmp/claude-0/-home-user-claude/3553ba7e-fec6-5bb4-911e-4fa14d84d65c/scratchpad/raw/probe_Kubula-xu_claude-finance-data/data"
MPP = {"XAU": 100.0, "NAS": 10.0}


def nas_d1_ergaenzt(D):
    d1 = D["NAS"]["d1"]
    key = d1["key"].astype(np.int64)
    letzte = int(key[-2])                                    # letzter sicher vollstaendiger Servertag (der letzte kann angebrochen sein)
    q = pd.read_csv(os.path.join(KUB, "nq_1d.csv"))
    q["tag"] = pd.to_datetime(q.Datetime_UTC).dt.tz_localize(None).values.astype("datetime64[D]").astype(np.int64)
    ov = q[q.tag.isin(key[-30:-1])]
    idx = np.searchsorted(key, ov.tag.values)
    ratio = float(np.median(d1["c"][idx] / ov.Close.values))
    neu = q[q.tag > letzte]
    keep = key <= letzte
    out = {k: np.r_[d1[k][keep], neu[c].values * ratio] for k, c in (("o", "Open"), ("h", "High"), ("l", "Low"), ("c", "Close"))}
    out["key"] = np.r_[key[keep], neu.tag.values]
    return out, ratio, len(neu)


def auswertung(A):
    D = A["D"]
    d1n, ratio, nneu = nas_d1_ergaenzt(D)
    FT = {"NAS": RG.tagesregeln(d1n), "XAU": RG.tagesregeln(D["XAU"]["d1"])}
    keys = {"NAS": d1n["key"], "XAU": D["XAU"]["d1"]["key"].astype(np.int64)}
    zeilen = []
    for (te, sy, d, lot, px, sl, tp, tx, pxx, usd, mod) in CL.LIVE:
        t = CL.ny_min(te)
        sd = (t + 420) // 1440
        j = int(np.searchsorted(keys[sy], sd, side="left") - 1)
        fl = {r: bool(FT[sy][r][0 if d > 0 else 1][j]) for r in RG.REGELN}
        risk = lot * abs(px - sl) * MPP[sy] if sl > 0 else np.nan
        R = usd / risk if risk and risk > 0 else np.nan
        zeilen.append(dict(zeit=te, sym=sy, dir=d, modul=mod, usd=usd, R=R, tag=str(np.datetime64(int(keys[sy][j]), "D")), **fl))
    return pd.DataFrame(zeilen), ratio, nneu


if __name__ == "__main__":
    A = AU.baue(sys.argv[1] if len(sys.argv) > 1 else "frei")
    df, ratio, nneu = auswertung(A)
    pd.set_option("display.width", 250)
    print(f"NQ-Ergaenzung: {nneu} Tage, Faktor {ratio:.5f}")
    print(df.to_string(index=False))
    nas_long_fades = df[(df.sym == "NAS") & (df.dir > 0) & (df.modul != "Noise")]
    print("\nNAS-Long-Fades + S0830 (ohne Noise):", len(nas_long_fades), "Trades, Summe", round(nas_long_fades.usd.sum(), 2), "$,",
          round(nas_long_fades.R.sum(), 2), "R")
    for r in RG.REGELN:
        g = nas_long_fades[nas_long_fades[r]]
        print(f"  {r:3s}: gesperrt {len(g):2d} Trades, {g.usd.sum():8.2f} $, {g.R.sum():6.2f} R")
