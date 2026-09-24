"""Grid-Studie Teil 5: Wirkung der Regel S je Fade-Modul (virtuelle Signale, Fremddaten 2006-2025, Spread wie gext):
Signale je Jahr, Anteil ausgelassen, PF und R je Jahr vorher/nachher, getrennt 2006-21 und 2022-25."""
import numpy as np
import pg_data as PD
PD.use_all()
import pg_fade as PF
from pg_study import F10


def pf(r):
    w = r[r > 0].sum(); l = -r[r < 0].sum()
    return w / l if l > 0 else 9.9


def main(tf=5, L=15, mp=1000, th=0.70):
    print(f"Regel S: M{tf} L{L} max{mp}, Stop-Chance >= {th:.2f} -> kein Fade gegen den Lauf")
    print(f"{'Modul':7s} | {'2006-21: Sig/J aus%  PF vorher->nachher  R/J vorher->nachher':58s} | 2022-25: Sig/J aus%  PF vorher->nachher  R/J vorher->nachher")
    for nm in F10:
        f = PF.fade_info(nm)
        X = PF.grid_features(f, tf, L, mp, 30)
        keep = ~(np.isfinite(X[:, 2]) & (X[:, 1] < 0) & (X[:, 6] >= th))
        yr = PD.year_of(f["t_entry"]); R = f["R"]
        cells = []
        for a, b, yrs in ((2006, 2022, 16.0), (2022, 2026, 4.0)):
            m = (yr >= a) & (yr < b)
            r0 = R[m]; r1 = R[m & keep]
            cells.append(f"{m.sum() / yrs:5.1f} {100 * (1 - (m & keep).sum() / max(m.sum(), 1)):4.0f}%  {pf(r0):4.2f} -> {pf(r1):4.2f}   {r0.sum() / yrs:+5.1f} -> {r1.sum() / yrs:+5.1f}")
        print(f"{nm:7s} | {cells[0]:58s} | {cells[1]}", flush=True)


if __name__ == "__main__":
    main()
