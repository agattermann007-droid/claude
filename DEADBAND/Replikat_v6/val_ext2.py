"""Abgleich: Externe Daten im Zeitraum 2022-2026 gegen GFT-Daten (gleiche Fades) + Zeitversatz-Pruefung."""
import numpy as np, pickle, os
import gext, gsig as G, prep5 as P

def load_overlap(sym):
    d = gext.load(sym, until="2026-09-03")
    lim = np.datetime64("2022-01-03", "m").astype(np.int64)
    k = d["ny"] >= lim
    out = {x: d[x][k] for x in ("ny", "o", "h", "l", "c", "sp", "v")}
    out["d1"] = P.agg(out["ny"], out["o"], out["h"], out["l"], out["c"], out["v"], 1440, offset=420)
    return out

gft = G.data()
ext = {s: load_overlap(s) for s in ("XAU", "NAS")}
# Zeitversatz: Korrelation der 5-min-Renditen bei Verschiebung um -2..+2 Stunden
for s in ("XAU", "NAS"):
    a = gft[s]; b = ext[s]
    ra = np.r_[0, np.diff(np.log(a["c"]))]; rb = np.r_[0, np.diff(np.log(b["c"]))]
    common, ia, ib = np.intersect1d(a["ny"], b["ny"], return_indices=True)
    print(s, "gemeinsame Kerzen", len(common))
    best = None
    for sh in range(-180, 181, 30):
        c2, i1, i2 = np.intersect1d(a["ny"], b["ny"] + sh, return_indices=True)
        x = ra[i1]; y = rb[i2]; m = np.isfinite(x) & np.isfinite(y) & (np.abs(x) < 0.05) & (np.abs(y) < 0.05)
        cc = np.corrcoef(x[m], y[m])[0, 1]
        print(f"   Versatz {sh:+4d} min: Korrelation {cc:.3f}")
pickle.dump(ext, open(os.path.join(P.OUT, "DXo.pkl"), "wb"))
