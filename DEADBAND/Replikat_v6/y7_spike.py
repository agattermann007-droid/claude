"""V7-Forschung, Stufe 2: 8:30-Spike-Fade NAS im Detail (Jahre, Regime-Waechter, Nachbarn).
Aufruf: python y7_spike.py  (braucht ../data und DEADBAND_EXT fuer die Fremddaten)"""
import numpy as np, sys
import gsig as G, scan6 as S, y7sig as Y, gext, cands as K

CANDS = [  # (ts, nbars, wait, xm, kmin, buf, tgtfrac)
    (510, 2, 6, 660, 0.25, 0.15, 0.5),
    (510, 2, 6, 660, 0.15, 0.15, 0.5),
    (510, 1, 6, 660, 0.25, 0.15, 0.5),
    (510, 2, 6, 660, 0.25, 0.15, 0.618),
    (510, 2, 4, 660, 0.25, 0.15, 0.5),
    (510, 2, 8, 660, 0.25, 0.15, 0.5),
    (510, 2, 6, 630, 0.25, 0.15, 0.5),
    (510, 2, 6, 660, 0.20, 0.15, 0.5),
    (510, 2, 6, 660, 0.25, 0.25, 0.5),
]


def trades(sym, c):
    D, ny, days, t_end, atr = S.prep(sym)
    ie, d, rd, tp, ix = Y.spike_fade(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, *c, 0)
    R, why, held, mfe, mae, iout = G.simulate(sym, ie, d, rd, tp, ix)
    return ny[ie], R, d


def guard(t, R, N, th):
    live = np.zeros(len(R), bool)
    for i in range(len(R)):
        w = R[max(0, i - N):i]
        if len(w) < N:
            continue
        pos = w[w > 0].sum(); neg = -w[w < 0].sum()
        live[i] = (pos / neg if neg > 0 else 9.9) > th
    return live


def years(t, R):
    y = (t // 1440 // 365.25 + 1970).astype(int)
    return " ".join(f"{yy}:{R[y == yy].sum():+5.1f}/{(y == yy).sum():2d}" for yy in np.unique(y))


def show(lbl, t, R):
    if len(R) == 0:
        print(f"{lbl:<44s} keine"); return
    pos = R[R > 0].sum(); neg = -R[R < 0].sum()
    print(f"{lbl:<44s} n{len(R):4d} WR{(R > 0).mean()*100:4.0f} R̄{R.mean():+.2f} PF{pos/neg if neg else 9.9:4.2f} | {years(t, R)}")


if __name__ == "__main__":
  for ds in ("ext", "gft"):
      if ds == "ext":
          G._D = gext.data_ext()
      else:
          G._D = None; G.data()
      K._CACHE.clear()
      print(f"\n######## {ds}")
      for c in CANDS:
          t, R, d = trades("NAS", c)
          show(f"{c}", t, R)
      c = CANDS[0]
      t, R, d = trades("NAS", c)
      for N, th in ((20, 1.0), (20, 1.2), (30, 1.0), (30, 1.2), (40, 1.0)):
          m = guard(t, R, N, th)
          show(f"  Waechter PF{N}>{th}", t[m], R[m])
      show("  nur Short (Spike aufwaerts)", t[d < 0], R[d < 0])
      show("  nur Long (Spike abwaerts)", t[d > 0], R[d > 0])
      dow = (t // 1440 + 4) % 7
      for w, nm in ((4, "Do (Claims)"), (5, "Fr (NFP)"), (2, "Di"), (3, "Mi")):
          show(f"  nur {nm}", t[dow == w], R[dow == w])
