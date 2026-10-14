"""Tagesdatensaetze fuer den Bootstrap (PLAN 3.3) aus einem durchgehenden eng6-Lauf (konto.tageslauf).

Je Prop-Tag, auf Groessenfaktor 1 zurueckgerechnet (geteilt durch fak0 = Faktor zu Tagesbeginn):
  dE    Equity-Aenderung inkl. offener Positionen (Swap des Rollovers zaehlt zum Folgetag)
  dmin  tiefste Equity im Tag gegen den Tagesstart (Kerzenebene, unguenstigster Kurs je Kerze)
  dmax  hoechste Equity im Tag gegen den Tagesstart
  flt   groesster Floating-Verlust der Verlustpositionen (strenge Lesart, inkl. Swap)
  real  realisiertes Tagesergebnis (Kommission abgezogen) - entscheidet den gueltigen Tag
  ref   Tagesreferenz der 3-%-Regel gegen den Tagesstart (Saldo + offener Gewinn, wie tagesrefeq)
  bal   Saldo gegen den Tagesstart (Basis der Floating-Regel unter Start)
  gap   Kalendertage seit dem vorigen Datensatz (Wochenende = 3)
  akt   1 = an dem Tag lief eine Position oder es wurde gehandelt
"""
import numpy as np

import eng6 as E

FELDER = ("dE", "dmin", "dmax", "flt", "real", "ref", "bal", "gap", "akt")
FI = {f: i for i, f in enumerate(FELDER)}


def aus_lauf(tage):
    """tage: res['tage'] aus eng6.run(..., tage=True) (Spalten eng6.KDN). Rueckgabe (tag, X[n, len(FELDER)])."""
    K = {n: i for i, n in enumerate(E.KDN)}
    t = tage
    tag = t[:, K["tag"]].astype(np.int64)
    eq = t[:, K["equity"]]
    e0 = np.r_[t[0, K["saldo0"]], eq[:-1]]
    f = t[:, K["fak0"]].copy()
    f[~(f > 0)] = 1.0
    X = np.zeros((len(tag), len(FELDER)))
    X[:, FI["dE"]] = (eq - e0) / f
    X[:, FI["dmin"]] = (np.minimum(t[:, K["eq_min"]], eq) - e0) / f
    X[:, FI["dmax"]] = (np.maximum(t[:, K["eq_max"]], eq) - e0) / f
    X[:, FI["flt"]] = t[:, K["flt_min"]] / f
    X[:, FI["real"]] = t[:, K["real"]] / f
    X[:, FI["ref"]] = (t[:, K["saldo0"]] + t[:, K["refplus"]] - e0) / f
    X[:, FI["bal"]] = (t[:, K["saldo0"]] - e0) / f
    X[:, FI["gap"]] = np.r_[1, np.diff(tag)]
    X[:, FI["akt"]] = ((t[:, K["real"]] != 0) | (eq != e0) | (t[:, K["eq_min"]] != t[:, K["eq_max"]])).astype(float)
    return tag, X


def ausrichten(*laeufe):
    """Mehrere (tag, X) auf gemeinsame Prop-Tage bringen (gepaarter Bootstrap: gleicher Index = gleicher Tag)."""
    gemein = laeufe[0][0]
    for tg, _ in laeufe[1:]:
        gemein = np.intersect1d(gemein, tg)
    out = []
    for tg, X in laeufe:
        out.append(X[np.searchsorted(tg, gemein)])
    return gemein, out


def schneiden(tag, X, von=None, bis=None):
    """Datensaetze im Bereich [von, bis] (Prop-Tag als 'YYYY-MM-DD'); gap des ersten Tags = 1."""
    m = np.ones(len(tag), bool)
    if von:
        m &= tag >= np.datetime64(von, "D").astype(np.int64)
    if bis:
        m &= tag <= np.datetime64(bis, "D").astype(np.int64)
    X2 = X[m].copy()
    if len(X2):
        X2[0, FI["gap"]] = 1
    return tag[m], X2
