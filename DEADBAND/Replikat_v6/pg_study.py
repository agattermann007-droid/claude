"""Grid-Studie Teil 1: Haengt das Ergebnis der Fade-Signale (virtuell, alle Signale) von den Probability-Grid-Merkmalen ab?
Durchgehende Fremddaten 2006-2025 (pg_data), Perioden 2006-13 / 2014-21 / 2022-23 / 2024-25.
Aufruf: python pg_study.py [tf length maxpiv] ..."""
import numpy as np, sys, itertools
import pg_data as PD
PD.use_all()
import pg_fade as PF

F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
PER = [("06-13", 2006, 2014), ("14-21", 2014, 2022), ("22-23", 2022, 2024), ("24-25", 2024, 2026)]


def stat(R):
    n = len(R)
    if n == 0:
        return "   -   "
    w = R[R > 0].sum(); l = -R[R < 0].sum()
    pf = w / l if l > 0 else 9.9
    return f"{n:4d} {100 * (R > 0).mean():3.0f}% {R.mean():+.2f} PF{pf:4.2f}"


def table(title, R, yr, groups):
    print(f"  {title}")
    print("    " + " " * 22 + " | ".join(f"{p[0]:^24s}" for p in PER))
    for lbl, m in groups:
        cells = []
        for _, a, b in PER:
            k = m & (yr >= a) & (yr < b)
            cells.append(f"{stat(R[k]):24s}")
        print(f"    {lbl:22s}" + " | ".join(cells))


def load():
    fis = {nm: PF.fade_info(nm) for nm in F10}
    return fis


def run(cfgs):
    fis = load()
    R = np.concatenate([fis[nm]["R"] for nm in F10])
    yr = PD.year_of(np.concatenate([fis[nm]["t_entry"] for nm in F10]))
    print("Fade-Signale gesamt", len(R), "| je Periode:", {p[0]: int(((yr >= p[1]) & (yr < p[2])).sum()) for p in PER})
    table("alle Signale", R, yr, [("alle", np.ones(len(R), bool))])
    for tf, L, mp in cfgs:
        X = np.concatenate([PF.grid_features(fis[nm], tf, L, mp, 30) for nm in F10])
        ok = np.isfinite(X[:, 2])
        al = X[:, 1]; pe = X[:, 2]; pb = X[:, 3]; be = X[:, 4]; pt = X[:, 5]; ss = X[:, 6]
        print(f"\n=== Zeitebene M{tf} Laenge {L} max. Schenkel {mp}: Merkmal vorhanden {ok.mean() * 100:.0f} %, "
              f"gegen den Lauf {np.mean(al[ok] < 0) * 100:.0f} %, Median Schenkel je Richtung {np.nanmedian(X[:, 7]):.0f}")
        g = [("mit Lauf", ok & (al > 0)), ("gegen Lauf", ok & (al < 0))]
        table("Ausrichtung (Fade in / gegen die Laufrichtung des Grids)", R, yr, g)
        g = []
        for a_, nm_ in ((-1, "gegen"), (1, "mit")):
            for lo, hi in ((0, 0.33), (0.33, 0.67), (0.67, 1.01)):
                g.append((f"{nm_} p_ext {lo:.2f}-{min(hi, 1):.2f}", ok & (al == a_) & (pe >= lo) & (pe < hi)))
        table("Reife des Laufs (Rang der Laufgroesse)", R, yr, g)
        g = []
        for a_, nm_ in ((-1, "gegen"), (1, "mit")):
            for lo, hi in ((0, 0.33), (0.33, 0.67), (0.67, 1.01)):
                g.append((f"{nm_} p_bar {lo:.2f}-{min(hi, 1):.2f}", ok & (al == a_) & (pb >= lo) & (pb < hi)))
        table("Reife des Laufs (Rang der Laufdauer)", R, yr, g)
        g = []
        for a_, nm_ in ((-1, "gegen"), (1, "mit")):
            for lo, hi in ((0, 0.1), (0.1, 0.3), (0.3, 1.01)):
                g.append((f"{nm_} beyond {lo:.1f}-{min(hi, 1):.1f}", ok & (al == a_) & (be >= lo) & (be < hi)))
        table("Grid-Wahrscheinlichkeit 'beyond' (1-p_ext)(1-p_bar)", R, yr, g)
        okt = np.isfinite(pt)
        g = [(f"p_tgt {lo:.2f}-{min(hi, 1):.2f}", okt & (pt >= lo) & (pt < hi)) for lo, hi in ((0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 1.01))]
        table("Zielweg (Rang unter den Schenkeln in Fade-Richtung; Chance ~ 1 - p_tgt)", R, yr, g)
        oks = np.isfinite(ss)
        g = [(f"surv_stop {lo:.2f}-{min(hi, 1):.2f}", oks & (ss >= lo) & (ss < hi)) for lo, hi in ((0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.01))]
        table("Chance, dass der Lauf bis zum Stop weiterlaeuft (nur gegen den Lauf)", R, yr, g)


def targets(cfgs, pcts=(20, 30, 40, 50, 60, 70), modes=("min", "set")):
    """Grid-Ziel: Linie des Perzentils pct der Schenkel in Fade-Richtung ab dem Extrem des Fehlausbruchs
    ('min' = nur, wenn naeher als das bisherige Ziel; 'set' = immer). Virtuelle Ergebnisse je Periode."""
    import gsig as G, pgrid as PG
    fis = load()
    yr = PD.year_of(np.concatenate([fis[nm]["t_entry"] for nm in F10]))
    R0 = np.concatenate([fis[nm]["R"] for nm in F10])
    def summ(R):
        cells = []
        for _, a, b in PER:
            k = (yr >= a) & (yr < b)
            yrs = b - a if b <= 2026 else 2
            w = R[k][R[k] > 0].sum(); l = -R[k][R[k] < 0].sum()
            cells.append(f"R/J {R[k].sum() / yrs:+6.1f} WR {100 * (R[k] > 0).mean():3.0f}% PF {w / l if l > 0 else 9.9:4.2f}")
        return " | ".join(cells)
    print(f"{'Basis (Mitte/Gegenseite)':34s} {summ(R0)}")
    for tf, L, mp in cfgs:
        for mode in modes:
            for pct in pcts:
                Rs = []
                for nm in F10:
                    f = fis[nm]
                    t0, done_at, res = PF.pivots(f["sym"], tf, L)
                    bias, piv_px, piv_bar, piv_bias, cur_px, cur_bar, lc, ld, ls, lb = res
                    q = done_at[f["j"]].astype(np.int64)
                    lv = PG.grid_level(q, f["d"].astype(np.int64), f["ex"], float(pct), piv_px, bias, lc, ld, ls, int(mp), 30)
                    g_new = (lv - f["ent"]) * f["d"]; g_old = f["tp"] * f["rd"]
                    ok = np.isfinite(g_new) & (g_new > 0)
                    g = np.where(ok, np.minimum(g_old, g_new) if mode == "min" else g_new, g_old)
                    R = G.simulate(f["sym"], f["ie"], f["d"], f["rd"], g / f["rd"], f["ix"])[0]
                    Rs.append(R)
                print(f"M{tf} L{L} {mode:3s} p{pct:2d}{'':22s} {summ(np.concatenate(Rs))}", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "ziel":
        b = a[1:]
        cfgs = [(int(b[i]), int(b[i + 1]), int(b[i + 2])) for i in range(0, len(b), 3)] or [(5, 20, 1000), (15, 20, 1000), (60, 10, 1000)]
        targets(cfgs)
    else:
        if a:
            cfgs = [(int(a[i]), int(a[i + 1]), int(a[i + 2])) for i in range(0, len(a), 3)]
        else:
            cfgs = [(tf, L, 1000) for tf in (5, 15, 60) for L in (10, 20, 40)]
        run(cfgs)
