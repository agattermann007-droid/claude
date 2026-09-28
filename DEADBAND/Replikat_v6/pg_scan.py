"""Grid-Studie Teil 3: Parameter-Raster fuer den Fade-Filter (virtuelle Signale, alle 10 Fades, Fremddaten 2006-2025).
Regeln: A = gegen einen jungen Lauf nicht faden (p_ext < th), S = nicht, wenn der Lauf bis zum Stop weiterlaeuft
(Grid-Chance surv_stop >= th), B = beyond (1-p_ext)(1-p_bar) > th. Ausgabe je Periode: Signale/J, R je Signal, PF,
Summe R/J; dazu Aenderung gegen alle Signale."""
import numpy as np, sys
import pg_data as PD
PD.use_all()
import pg_fade as PF
from pg_study import F10, PER, load

YRS = {"06-13": 8.0, "14-21": 8.0, "22-23": 2.0, "24-25": 2.0}


def per_stats(R, yr, keep):
    out = []
    for nm, a, b in PER:
        k = keep & (yr >= a) & (yr < b)
        r = R[k]; w = r[r > 0].sum(); l = -r[r < 0].sum()
        out.append((k.sum() / YRS[nm], r.mean() if len(r) else 0.0, w / l if l > 0 else 9.9, r.sum() / YRS[nm]))
    return out


def fmt(st, base=None):
    cells = []
    for q, (n, m, pf, s) in enumerate(st):
        d = "" if base is None else f"{s - base[q][3]:+5.1f}"
        cells.append(f"{n:5.0f}/J {m:+.3f} PF{pf:4.2f} {s:+6.1f}{d:>6s}")
    return " | ".join(cells)


def main(cfgs):
    fis = load()
    R = np.concatenate([fis[nm]["R"] for nm in F10])
    yr = PD.year_of(np.concatenate([fis[nm]["t_entry"] for nm in F10]))
    base = per_stats(R, yr, np.ones(len(R), bool))
    print(" " * 26 + " | ".join(f"{p[0]:^34s}" for p in PER))
    print(f"{'alle Signale':26s}{fmt(base)}")
    for tf, L, mp in cfgs:
        X = np.concatenate([PF.grid_features(fis[nm], tf, L, mp, 30) for nm in F10])
        ok = np.isfinite(X[:, 2]); al = X[:, 1]; pe = X[:, 2]; pb = X[:, 3]; be = X[:, 4]; ss = X[:, 6]
        print(f"--- M{tf} L{L} max{mp} (gegen den Lauf {np.mean(al[ok] < 0) * 100:.0f} %)")
        for th in (0.2, 0.25, 0.33, 0.4, 0.5):
            keep = ~(ok & (al < 0) & (pe < th))
            print(f"{'A p_ext<' + str(th):26s}{fmt(per_stats(R, yr, keep), base)}")
        for th in (0.6, 0.7, 0.75, 0.8, 0.9):
            keep = ~(ok & (al < 0) & (ss >= th))
            print(f"{'S surv_stop>=' + str(th):26s}{fmt(per_stats(R, yr, keep), base)}")
        for th in (0.2, 0.3, 0.4):
            keep = ~(ok & (al < 0) & (be > th))
            print(f"{'B beyond>' + str(th):26s}{fmt(per_stats(R, yr, keep), base)}")
        sys.stdout.flush()


if __name__ == "__main__":
    a = sys.argv[1:]
    cfgs = [(int(a[i]), int(a[i + 1]), int(a[i + 2])) for i in range(0, len(a), 3)] if a else \
        [(5, L, 1000) for L in (10, 15, 20, 30, 40)] + [(5, 20, mp) for mp in (200, 500)] + [(10, L, 1000) for L in (10, 20)] + [(15, 10, 1000)]
    main(cfgs)
