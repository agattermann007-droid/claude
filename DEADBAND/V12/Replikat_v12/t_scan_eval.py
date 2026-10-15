import pickle, pandas as pd, numpy as np, sys
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40); pd.set_option("display.max_rows", 200)
for sym in ("XAU", "NAS"):
    df = pd.DataFrame(pickle.load(open(f"ergebnisse/scan_{sym}.pkl", "rb")))
    sel = df[(df["22-23_n"] >= 60) & (df["22-23_er"] >= 0.10) & (df["22-23_pf"] >= 1.15)]
    ok = sel[(sel["24-26_er"] > 0.03) & (sel["16-21_er"] > 0.03)]
    print(f"== {sym}: {len(df)} Varianten, Auswahl 22-23: {len(sel)}, davon in 24-26 UND 16-21 positiv (>0,03 R): {len(ok)}")
    cols = ["mark", "w0", "w1", "x", "dr", "sd", "md", "sb", "tm", "crv", "22-23_n", "22-23_er", "22-23_pf", "24-26_n", "24-26_er", "16-21_n", "16-21_er"]
    print(ok.sort_values("22-23_er", ascending=False)[cols].head(40).to_string(index=False))
    # Zaehlung je Marke/Fenster
    g = ok.groupby(["mark", "w0", "w1", "dr"]).size()
    print(g.to_string())
