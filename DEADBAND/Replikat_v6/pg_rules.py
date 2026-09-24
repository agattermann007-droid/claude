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
    """Regel A: gegen den Lauf nur, wenn der Lauf reif ist (p_ext >= th); in Laufrichtung immer."""
    return lambda X: (X[:, 1] > 0) | (X[:, 2] >= th)


def c_stop_survival(th):
    """Regel S: gegen den Lauf nur, wenn die Grid-Chance, dass der Lauf bis zum Stop weiterlaeuft, unter th liegt."""
    return lambda X: (X[:, 1] > 0) | ~(X[:, 6] >= th)


def c_beyond_max(th):
    """Regel B: gegen den Lauf nur, wenn beyond <= th."""
    return lambda X: (X[:, 1] > 0) | (X[:, 4] <= th)


def c_young(th):
    """Trendfolge: nur, wenn der Lauf in Signalrichtung noch jung ist (p_ext <= th) oder gegen den Signal-Lauf."""
    return lambda X: (X[:, 1] < 0) | (X[:, 2] <= th)


def c_not_young_counter(th):
    """Trendfolge: nicht gegen einen jungen Lauf einsteigen (gegen den Lauf nur, wenn p_ext >= th)."""
    return lambda X: (X[:, 1] > 0) | (X[:, 2] >= th)


def variants():
    """(Name, Basis ERT/SIC, GP-Zusatz, Fade-Regel, RSI21-Regel, Noise-Regel)."""
    H = dict(harv=1)
    A = lambda th, L=20, mp=1000, ga=False: fade_filter(5, L, mp, c_counter_mature(th), guard_all=ga)
    S = lambda th, L=15, mp=1000, ga=False: fade_filter(5, L, mp, c_stop_survival(th), guard_all=ga)
    v = [
        ("6.10 Ertrag", "ERT", H, NONE, None, None),
        ("6.10 Sicher", "SIC", {}, NONE, None, None),
        ("E A M5 L20 p33", "ERT", H, A(0.33), None, None),
        ("E A M5 L20 p25", "ERT", H, A(0.25), None, None),
        ("E A M5 L20 p40", "ERT", H, A(0.40), None, None),
        ("E A M5 L20 p33 Waechter alle", "ERT", H, A(0.33, ga=True), None, None),
        ("E A M5 L30 p33", "ERT", H, A(0.33, L=30), None, None),
        ("E A M5 L20 p33 max500", "ERT", H, A(0.33, mp=500), None, None),
        ("E S M5 L15 s70", "ERT", H, S(0.70), None, None),
        ("E S M5 L15 s75", "ERT", H, S(0.75), None, None),
        ("E S M5 L20 s70", "ERT", H, S(0.70, L=20), None, None),
        ("E S M5 L20 s75", "ERT", H, S(0.75, L=20), None, None),
        ("E S M5 L15 s70 Waechter alle", "ERT", H, S(0.70, ga=True), None, None),
        ("S A M5 L20 p33", "SIC", {}, A(0.33), None, None),
        ("S S M5 L15 s70", "SIC", {}, S(0.70), None, None),
        # Nachbarn der besten Regel S
        ("E S M5 L15 s65", "ERT", H, S(0.65), None, None),
        ("E S M5 L15 s70 max500", "ERT", H, S(0.70, mp=500), None, None),
        ("E S M5 L10 s70", "ERT", H, S(0.70, L=10), None, None),
        ("S S M5 L15 s65", "SIC", {}, S(0.65), None, None),
        ("S S M5 L15 s75", "SIC", {}, S(0.75), None, None),
        ("S S M5 L20 s75", "SIC", {}, S(0.75, L=20), None, None),
        ("S S M5 L15 s70 max500", "SIC", {}, S(0.70, mp=500), None, None),
        ("S S M5 L10 s70", "SIC", {}, S(0.70, L=10), None, None),
        # strengerer Waechter zur Regel S (weniger schwache Module live)
        ("E S M5 L15 s70 W1.3", "ERT", H, dict(S(0.70), guard=("pf", 30, 1.3)), None, None),
        ("E S M5 L15 s70 W1.4", "ERT", H, dict(S(0.70), guard=("pf", 30, 1.4)), None, None),
        ("E 6.10 W1.3", "ERT", H, dict(NONE, guard=("pf", 30, 1.3)), None, None),
        ("S S M5 L15 s70 W1.3", "SIC", {}, dict(S(0.70), guard=("pf", 30, 1.3)), None, None),
    ]
    return v
