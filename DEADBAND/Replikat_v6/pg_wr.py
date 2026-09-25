"""Build 6.30 (Trefferquote), Teil 1: Signal-Ebene der Fades. Wie aendern Teilgewinn (T1), Stop auf Einstand (BE) und
naeheres Ziel die Trefferquote und das Ergebnis je Signal? Alle virtuellen Fade-Signale mit Grid-Regel 6.20 (N1800 ohne),
durchgehende Fremddaten 2006-2025, Perioden wie pg_study. T1 und Ziel wahlweise in R oder als Anteil des Wegs zum Ziel.
Aufruf: python pg_wr.py"""
import numpy as np
from numba import njit
import pg_data as PD
PD.use_all()
import pg_fade as PF, pg_blocks as PB, pg_rules as RU, gsig as G

F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
PER = [("06-13", 2006, 2014), ("14-21", 2014, 2022), ("22-23", 2022, 2024), ("24-25", 2024, 2026)]
RULE = RU.fade_filter(5, 15, 1000, RU.c_stop_survival(0.70))


@njit(cache=True)
def sim(o, h, l, sp, ie, d, rd, tpr, ix, t1r, t1f, be, comm_px, tpdelay):
    """wie gsig._sim, aber T1-Niveau je Signal (t1r in R, <= 0 = kein T1); be = neuer Stop in R nach T1 (<= -9 = keiner)."""
    n = ie.shape[0]
    R = np.zeros(n); t1hit = np.zeros(n, np.bool_)
    for t in range(n):
        i = ie[t]; dd = d[t]; r = rd[t]
        ent = o[i] + (sp[i] if dd > 0 else 0.0)
        sl = ent - dd * r
        tp = ent + dd * tpr[t] * r if tpr[t] > 0.0 else 0.0
        left = 1.0; acc = 0.0; done1 = t1r[t] <= 0.0
        j = i
        while True:
            if j >= ix[t] or j >= o.shape[0]:
                jj = min(j, o.shape[0] - 1)
                px = o[jj] + (sp[jj] if dd < 0 else 0.0)
                acc += left * (px - ent) * dd
                break
            lo = l[j]; hi = h[j]; s_ = sp[j]
            if dd > 0:
                hit_sl = lo <= sl; hit_tp = tp > 0.0 and hi >= tp
            else:
                hit_sl = hi + s_ >= sl; hit_tp = tp > 0.0 and lo + s_ <= tp
            if hit_sl:
                px = sl
                if dd > 0 and o[j] < sl:
                    px = o[j]
                if dd < 0 and o[j] + s_ > sl:
                    px = o[j] + s_
                acc += left * (px - ent) * dd
                break
            if hit_tp and j - i >= tpdelay:
                acc += left * (tp - ent) * dd
                break
            if not done1 and j - i >= tpdelay:
                lvl = ent + dd * t1r[t] * r
                if (dd > 0 and hi >= lvl) or (dd < 0 and lo + s_ <= lvl):
                    done1 = True; t1hit[t] = True
                    if t1f > 0.0:
                        acc += t1f * (lvl - ent) * dd; left -= t1f
                    if be > -9.0:
                        cand = ent + dd * be * r
                        if (cand - sl) * dd > 0.0:
                            sl = cand
            j += 1
        R[t] = (acc - comm_px) / r
    return R, t1hit


def load():
    """Signale je Modul (nach Grid-Regel 6.20) mit Jahr."""
    out = {}
    for nm in F10:
        f = PF.fade_info(nm)
        keep = PB.apply_rule(f, RULE if nm != "N1800" else dict(kind="none"))[0]
        out[nm] = {k: (v[keep] if isinstance(v, np.ndarray) and len(v) == len(keep) else v) for k, v in f.items()}
    return out


def run_var(fis, t1_mode, t1, t1f, be, tgt_scale=1.0):
    """t1_mode 'R' = T1 bei t1 R, 'Z' = bei t1 x Weg zum Ziel; tgt_scale = Ziel naeher (x Weg zum Ziel)."""
    Rs, ts, hits = [], [], []
    for nm in F10:
        f = fis[nm]; sym = f["sym"]; D = G.data()[sym]; k = G.SYM[sym]
        tpr = f["tp"] * tgt_scale
        t1r = np.full(len(tpr), t1) if t1_mode == "R" else tpr * t1
        if t1 <= 0:
            t1r = np.zeros(len(tpr))
        R, hit = sim(D["o"], D["h"], D["l"], D["sp"], f["ie"].astype(np.int64), f["d"].astype(np.int64), f["rd"].astype(float),
                     tpr.astype(float), f["ix"].astype(np.int64), t1r.astype(float), float(t1f), float(be), G.COMM[k] / G.MPP[k], 1)
        Rs.append(R); ts.append(f["t_entry"]); hits.append(hit)
    R = np.concatenate(Rs); t = np.concatenate(ts); o = np.argsort(t, kind="stable")
    return R[o], t[o], np.concatenate(hits)[o]


def stats(R, t):
    yr = PD.year_of(t)
    cells = []
    for _, a, b in PER:
        m = (yr >= a) & (yr < b); x = R[m]; Y = b - a
        w = x[x > 0].sum(); lo = -x[x < 0].sum()
        cur = 0; n6 = 0; mx = 0
        for v in x:
            if v < 0:
                cur += 1; mx = max(mx, cur); n6 += (cur == 6)
            else:
                cur = 0
        cells.append((len(x), 100 * (x > 0).mean(), x.mean(), w / lo if lo > 0 else 9.9, x.sum() / Y, n6 / Y, mx))
    return cells


def fmt(c):
    return f"{c[1]:4.1f}% {c[2]:+.3f} PF{c[3]:4.2f} {c[4]:+5.1f}R/J S6 {c[5]:3.1f} m{c[6]:2d}"


if __name__ == "__main__":
    fis = load()
    print("Fade-Signale (Grid 6.20):", sum(len(fis[nm]["R"]) for nm in F10))
    print(f"{'Variante':34s} " + " | ".join(f"{p[0]:^37s}" for p in PER))
    V = [("6.20 (Ziel Range-Mitte)", "R", 0, 0, -99, 1.0)]
    for t1 in (0.25, 0.4, 0.5, 0.75):
        for be in (0.0, 0.05, 0.1):
            V.append((f"BE: ab {t1} R Stop auf +{be} R", "R", t1, 0.0, be, 1.0))
    for q in (0.5, 0.7):
        for be in (0.0, 0.05):
            V.append((f"BE: ab {q:.0%} Zielweg Stop +{be} R", "Z", q, 0.0, be, 1.0))
    for t1, f_ in ((0.25, 0.5), (0.4, 0.5), (0.5, 0.5), (0.5, 0.33)):
        for be in (-99, 0.05):
            V.append((f"T1 {t1} R {f_:.0%}" + (f", Stop +{be}" if be > -9 else ""), "R", t1, f_, be, 1.0))
    for q in (0.5, 0.7):
        for be in (-99, 0.05):
            V.append((f"T1 {q:.0%} Zielweg 50%" + (f", Stop +{be}" if be > -9 else ""), "Z", q, 0.5, be, 1.0))
    for sc in (0.6, 0.8):
        V.append((f"Ziel {sc:.0%} des Wegs", "R", 0, 0, -99, sc))
    for lbl, mode, t1, f_, be, sc in V:
        R, t, hit = run_var(fis, mode, t1, f_, be, sc)
        print(f"{lbl:34s} " + " | ".join(fmt(c) for c in stats(R, t)), flush=True)
