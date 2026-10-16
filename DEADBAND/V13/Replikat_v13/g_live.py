"""Abgleich Live (28.09.-16.10.2026) gegen die Signale des Nachbaus auf dem GFT-Feed.
Je Nachbau-Signal: Zeit (Server), Strom, Richtung, Einstieg/Stop/Ziel, Waechter live, virtuelles R; dazu der passende
Live-Trade (gleicher Strom, Einstieg +-10 min) mit Preis-/Stop-Abweichung und Live-R."""
import xg  # noqa: F401
import os, numpy as np, pandas as pd

if __name__ == "__main__":
    import cfg11 as C, gen11 as G
    W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    S = C.signals()
    LO = int(np.datetime64("2026-09-28T00:00", "m").astype(np.int64)) - 420
    HI = int(np.datetime64("2026-10-17T00:00", "m").astype(np.int64)) - 420
    rows = []
    def srv(t):
        return pd.Timestamp(int(t + 420) * 60, unit="s")
    for i, b in enumerate(S["fades"]):
        m = (b["t"] >= LO) & (b["t"] < HI)
        for q in np.nonzero(m)[0]:
            rows.append(dict(t=srv(b["t"][q]), strom=C.FADE_NAMES[i], dir=int(b["dir"][q]), ent=b["ent"][q], sl=b["sl"][q],
                             tp=b["tp"][q], live=bool(b["live"][q]), vR=b["R"][q]))
    for key, nm in (("spike", "S0830"), ("lw", "LW"), ("xa", "XA"), ("td", "TD")):
        b = S[key]
        m = (b["t"] >= LO) & (b["t"] < HI)
        for q in np.nonzero(m)[0]:
            rows.append(dict(t=srv(b["t"][q]), strom=nm, dir=int(b["dir"][q]), ent=b["ent"][q], sl=b["sl"][q], tp=b["tp"][q],
                             live=True, vR=np.nan))
    sig = pd.DataFrame(rows).sort_values("t").reset_index(drop=True)
    T = pd.read_csv(os.path.join(W, "a1_trades.csv"), sep=";", parse_dates=["ein", "aus"])
    T = T[T["ein"] >= "2026-09-28"].copy()
    T["strom"] = T["modul"].str.replace("FADE ", "", regex=False)
    sig["live_trade"] = ""; sig["d_ent"] = np.nan; sig["d_sl"] = np.nan; sig["lR"] = np.nan
    used = set()
    for k, s in sig.iterrows():
        c = T[(T["strom"] == s["strom"]) & ((T["ein"] - s["t"]).abs() <= pd.Timedelta(minutes=10))]
        if len(c):
            j = c.index[0]; used.add(j)
            sig.loc[k, ["live_trade", "d_ent", "d_sl", "lR"]] = [str(c.loc[j, "ein"])[5:16], c.loc[j, "preis"] - s["ent"],
                                                                   c.loc[j, "sl"] - s["sl"], c.loc[j, "R"]]
    pd.set_option("display.width", 220)
    print(sig.round(2).to_string())
    rest = T.loc[[j for j in T.index if j not in used], ["ein", "strom", "richt", "preis", "sl", "R"]]
    print("\nLive-Trades ohne Nachbau-Signal:\n", rest.to_string())
    print("\nNoise-Pruefungen mit Einstieg im Zeitraum:")
    nz = S["nz"]; D = G.data(); ny5 = D["NAS"]["ny"]
    t = ny5[nz["i5"]]
    m = (t >= LO) & (t < HI) & (nz["entry_ok"] > 0)
    for q in np.nonzero(m)[0]:
        print(" ", srv(t[q]), "Schluss", round(float(nz["close"][q]), 2), "UB", round(float(nz["UB"][q]), 2))
    r = S["r21"]; m = (r["T"] >= LO) & (r["T"] < HI)
    print("\nRSI21-Signale im Zeitraum:", int(m.sum()))
    for q in np.nonzero(m)[0]:
        print(" ", srv(r["T"][q]), "Sym", int(r["sym"][q]), "TF", int(r["tf"][q]), "Dir", int(r["dir"][q]), "Folge", int(r["folge"][q]))
    sig.to_csv(os.path.join(W, "g_live_abgleich.csv"), sep=";", index=False)
