"""Replikat v11 - Datenaufbereitung.

Quelle: M1-Kurse (prep_m1.py), Serverzeit = NY + 7 h. Hier: Zeitachse NY-Minuten seit Epoche (wie Replikat v5/v6).
  NAS: HistData NSXUSD (Quelle = NY-Ortszeit, geprueft am 9:30-Sprung je Jahr und Saison), 2010-11 .. 2026-02
  XAU: Dukascopy (UTC -> NY), 2016-09 .. 2026-09
Kosten (Annahme wie Bericht V10): Spread proportional zum Kurs, NAS 1,63 bei 15.000, Gold 0,32 bei 2.000.
Ergebnis D[sym]: M1-Arrays (ny1, o1, h1, l1, c1, sp1) und M5-Kerzen im Format von prep5 (ny, o, h, l, c, sp, v,
m15, m30, h1, d1) - die alten Signal-Generatoren (sig5) laufen unveraendert darauf.
"""
import os, pickle, numpy as np
import prep5 as P

NPZ = os.environ.get("NPZ_DIR", "/home/user/work/npz")
CACHE = os.environ.get("REP_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache"))
os.makedirs(CACHE, exist_ok=True)
SPK = {"NAS": 1.63 / 15000.0, "XAU": 0.32 / 2000.0}
FILES = {"NAS": "NAS_m1.npz", "XAU": "XAU_m1.npz"}


def load_m1(sym):
    z = np.load(os.path.join(NPZ, FILES[sym]))
    ny = z["t"] // 60 - 420
    o, h, l, c = (z[k].astype(np.float64) for k in ("o", "h", "l", "c"))
    ok = np.isfinite(o) & np.isfinite(c) & (h >= l) & (o > 0)
    ny, o, h, l, c = ny[ok], o[ok], h[ok], l[ok], c[ok]
    order = np.argsort(ny, kind="stable")
    ny, o, h, l, c = ny[order], o[order], h[order], l[order], c[order]
    keep = np.r_[True, np.diff(ny) > 0]
    ny, o, h, l, c = ny[keep], o[keep], h[keep], l[keep], c[keep]
    sp = c * SPK[sym]
    return ny.astype(np.int64), o, h, l, c, sp


def fill_close(ny, o, h, l, c):
    """NAS (HistData): werktags fehlen die Kurse 16:15-17:00 NY (ab 2019 ganz, davor 16:15-16:30); GFT handelt bis 17:00.
    Fehlende Minuten [16:15, 17:00) an Tagen mit Kursen vor 16:15 werden als flache Kerzen zum letzten Schluss
    eingefuegt - nur fuer den Kursverlauf (Ausstiege 16:40, Freitag-Schluss 16:45), nicht fuer die Signal-Kerzen."""
    day = ny // 1440; m = ny % 1440; dow = (day + 4) % 7
    cand_days = np.unique(day[(m >= 900) & (m < 975) & (dow >= 1) & (dow <= 5)])
    grid = (cand_days[:, None] * 1440 + np.arange(975, 1020)[None, :]).ravel()
    new = grid[~np.isin(grid, ny)]
    idx = np.searchsorted(ny, new) - 1              # letzte echte Kerze davor
    ok = idx >= 0
    new, idx = new[ok], idx[ok]
    ok = (new // 1440) == (ny[idx] // 1440)
    new, idx = new[ok], idx[ok]
    px = c[idx]
    ny2 = np.r_[ny, new]; o2 = np.r_[o, px]; h2 = np.r_[h, px]; l2 = np.r_[l, px]; c2 = np.r_[c, px]
    order = np.argsort(ny2, kind="stable")
    # Schluss der Fuellkerzen = letzter echter Schluss davor (bei mehreren Luecken fortgeschrieben)
    ny2, o2, h2, l2, c2 = ny2[order], o2[order], h2[order], l2[order], c2[order]
    syn = np.r_[np.zeros(len(ny), bool), np.ones(len(new), bool)][order]
    for j in np.nonzero(syn)[0]:
        if j > 0:
            o2[j] = h2[j] = l2[j] = c2[j] = c2[j - 1]
    return ny2, o2, h2, l2, c2, len(new)


def to_m5(ny, o, h, l, c, sym):
    key = ny // 5
    uniq, first = np.unique(key, return_index=True)
    last = np.r_[first[1:] - 1, len(ny) - 1]
    d = dict(ny=uniq * 5, o=o[first], h=np.maximum.reduceat(h, first), l=np.minimum.reduceat(l, first), c=c[last],
             v=(last - first + 1).astype(np.float64), m1first=first.astype(np.int64))
    d["sp"] = d["c"] * SPK[sym]
    return d


def build(force=False):
    f = os.path.join(CACHE, "D11.pkl")
    if os.path.exists(f) and not force:
        return pickle.load(open(f, "rb"))
    D = {}
    for s in ("XAU", "NAS"):
        ny1, o1, h1, l1, c1, sp1 = load_m1(s)
        d = to_m5(ny1, o1, h1, l1, c1, s)
        ny = d["ny"]
        d["pday"] = (ny + 420) // 1440
        d["m15"] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 15)
        d["m30"] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 30)
        d["h1"] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 60)
        d["d1"] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], 1440, offset=420)
        if s == "NAS":
            ny1, o1, h1, l1, c1, nfill = fill_close(ny1, o1, h1, l1, c1)
            sp1 = c1 * SPK[s]
            print(f"NAS: {nfill} flache Kerzen 16:15-17:00 NY eingefuegt", flush=True)
        d.update(ny1=ny1, o1=o1, h1m=h1, l1=l1, c1=c1, sp1=sp1)
        D[s] = d
        print(f"{s}: {len(ny1)} M1, {len(ny)} M5, {len(d['d1']['t'])} D1  {np.datetime64(int(ny1[0]), 'm')} .. {np.datetime64(int(ny1[-1]), 'm')}", flush=True)
    pickle.dump(D, open(f, "wb"), protocol=4)
    return D


if __name__ == "__main__":
    build(force=True)
