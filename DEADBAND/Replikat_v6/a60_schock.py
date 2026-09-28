"""Build 6.60, Kandidat K3 (Schocktag-Filter), Signal-Ebene: R der Fade-Signale nach Marktzustand beim Einstieg, je Periode
und Symbol. Groessen (vorab festgelegt, PROTOKOLL_660.md), alle nur aus Daten VOR der Einstiegskerze:
  V1 = True Range des letzten abgeschlossenen Servertags / ATR14 (bis einschliesslich dieses Tags)
  V2 = |Schluss der letzten M5-Kerze vor dem Einstieg - Eroeffnung des laufenden Servertags| / ATR14
  V3 = ATR14 / ATR100 (Vola-Ausweitung)
Aufruf: python a60_schock.py [ausgabe.txt]"""
import numpy as np, sys, os
import streams as ST, gsig as G, pg_blocks as PB, cands as K
import a60_sig as A

OUT = []


def say(s=""):
    print(s, flush=True); OUT.append(s)


def feat(ds, sym, te):
    ST._use(ds)
    D = (G._D if G._D is not None else G.data())[sym]
    d1 = D["d1"]
    o, h, l, c = d1["o"], d1["h"], d1["l"], d1["c"]
    t_end = d1["t"] + 1440
    tr = np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1]); tr = np.r_[h[0] - l[0], tr]
    a14 = np.convolve(tr, np.ones(14) / 14, mode="full")[:len(tr)]; a14[:13] = np.nan
    a100 = np.convolve(tr, np.ones(100) / 100, mode="full")[:len(tr)]; a100[:99] = np.nan
    k = np.searchsorted(t_end, te, side="right") - 1                 # letzter abgeschlossener Servertag
    k = np.maximum(k, 0)
    v1 = tr[k] / a14[k]
    v3 = a14[k] / a100[k]
    # V2: Eroeffnung des laufenden Servertags = erste M5-Kerze ab t_end[k]; letzte M5-Kerze vor dem Einstieg
    ny = D["ny"]
    i_open = np.searchsorted(ny, t_end[k], side="left")
    i_prev = np.searchsorted(ny, te, side="left") - 1
    i_open = np.minimum(i_open, len(ny) - 1); i_prev = np.maximum(i_prev, 0)
    v2 = np.abs(D["c"][i_prev] - D["o"][i_open]) / a14[k]
    return v1, v2, v3


def rows_for(names):
    parts = []
    for nm in names:
        c = A.chain(nm)
        sym = K.FADES[nm]["sym"]
        v = [np.zeros(len(c["te"])) for _ in range(3)]
        pre = c["te"] < A.LIM22
        for ds, m in (("ext", pre), ("gft", ~pre)):
            if m.any():
                f = feat(ds, sym, c["te"][m])
                for i in range(3):
                    v[i][m] = f[i]
        parts.append(dict(te=c["te"], R=c["R"], v1=v[0], v2=v[1], v3=v[2]))
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}


BINS = {"v1": [0, 0.75, 1.0, 1.25, 1.5, 2.0, 99], "v2": [0, 0.25, 0.5, 0.75, 1.0, 1.5, 99], "v3": [0, 0.8, 1.0, 1.2, 1.5, 99]}
NAMES = {"v1": "Vortags-Spanne / ATR14", "v2": "Tagesbewegung bis Signal / ATR14", "v3": "ATR14 / ATR100"}

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("ergebnisse", "a60_schock.txt")
    groups = {"NAS": [n for n in PB.F10 if K.FADES[n]["sym"] == "NAS"], "XAU": [n for n in PB.F10 if K.FADES[n]["sym"] == "XAU"]}
    data = {g: rows_for(ns) for g, ns in groups.items()}
    say("Fade-Signale (Grid-Regel S wie im EA) nach Marktzustand beim Einstieg. Zellen: Signale je Jahr | R je Signal | PF")
    for var in ("v1", "v2", "v3"):
        say(f"== {NAMES[var]}")
        b = BINS[var]
        for g, dd in data.items():
            for pn, a, e in A.PER:
                lo, hi = A.t64(a), A.t64(e)
                yrs = (hi - lo) / (365.25 * 1440)
                s = (dd["te"] >= lo) & (dd["te"] < hi) & np.isfinite(dd[var])
                cells = []
                for q in range(len(b) - 1):
                    m = s & (dd[var] >= b[q]) & (dd[var] < b[q + 1])
                    R = dd["R"][m]
                    if len(R) < 5:
                        cells.append(f"{b[q]:.2f}+: {len(R):3d}   -        "); continue
                    pos = R[R > 0].sum(); neg = -R[R < 0].sum()
                    cells.append(f"{b[q]:.2f}+: {len(R) / yrs:5.1f} {R.mean():+.3f} {pos / neg if neg > 0 else 9.9:4.2f}")
                say(f"  {g} {pn}: " + " | ".join(cells))
    open(out, "w").write("\n".join(OUT) + "\n")
