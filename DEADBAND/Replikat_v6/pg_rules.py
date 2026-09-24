"""Grid-Regeln (Varianten) fuer x40. Spalten der Merkmale siehe pgrid.features:
0 bias, 1 align (+1 in Laufrichtung, -1 gegen den Lauf), 2 p_ext, 3 p_bar, 4 beyond, 5 p_tgt, 6 surv_stop, 7/8 n Schenkel,
9 ext, 10 bars, 11 p50 in Fade-Richtung, 12 p_barext."""
import numpy as np

NONE = dict(kind="none")


def fade_filter(tf, L, mp, cond, guard_all=False, minlegs=30):
    return dict(kind="filter", tf=tf, L=L, mp=mp, cond=cond, guard_all=guard_all, minlegs=minlegs)


def fade_weight(tf, L, mp, cond, w_bad, minlegs=30):
    return dict(kind="weight", tf=tf, L=L, mp=mp, cond=cond, w_bad=w_bad, minlegs=minlegs)


def fade_target(tf, L, mp, pct, mode="min", floor_r=0.0, minlegs=30):
    return dict(kind="target", tf=tf, L=L, mp=mp, pct=pct, mode=mode, floor_r=floor_r, minlegs=minlegs)


def old_filter(tf, L, mp, cond, minlegs=30):
    return dict(tf=tf, L=L, mp=mp, cond=cond, minlegs=minlegs)


# Bedingungen (True = handeln)
def c_counter_mature(th):
    """gegen den Lauf nur, wenn der Lauf reif ist (p_ext >= th); in Laufrichtung immer."""
    return lambda X: (X[:, 1] > 0) | (X[:, 2] >= th)


def c_beyond_max(th):
    """gegen den Lauf nur, wenn beyond <= th."""
    return lambda X: (X[:, 1] > 0) | (X[:, 4] <= th)


def c_tgt_max(th):
    return lambda X: ~(X[:, 5] > th)


def c_young(th):
    """Trendfolge: nur, wenn der Lauf in Signalrichtung noch jung ist (p_ext <= th) oder gegen den Signal-Lauf."""
    return lambda X: (X[:, 1] < 0) | (X[:, 2] <= th)


def variants():
    """(Name, Basis ERT/SIC, GP-Zusatz, Fade-Regel, RSI21-Regel, Noise-Regel) - wird nach der Vorstudie gefuellt."""
    H = dict(harv=1)
    return [
        ("6.10 Ertrag", "ERT", H, NONE, None, None),
        ("6.10 Sicher", "SIC", {}, NONE, None, None),
    ]
