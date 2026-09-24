"""Probability Grid fuer die alten Module RSI21 (Folgesignale) und NAS-Noise: Grid-Merkmale je Signal/Pruefung und
Markt-Objekte fuer eng6, in denen Signale, die eine Grid-Regel nicht erfuellen, per Auslass-Maske ausgelassen werden
(gleiche Zufallsfolgen wie ohne Regel)."""
import numpy as np, os, pickle
import eng6 as E, prep5 as P, gsig as G, pg_blocks as PB, pgrid as PG

SYMS = ("XAU", "NAS")


def _feat_generic(sym, t_entry, d, tf, L, mp, minlegs=30):
    """Merkmale fuer Trendfolge-Einstiege: Extrem/Ziel/Stop ohne Bedeutung (NaN-Spalten 5, 6 werden nicht genutzt)."""
    n = len(t_entry)
    nan = np.full(n, np.nan); one = np.ones(n)
    return PB.feats(sym, t_entry, d, one, one, one, one, tf, L, mp, minlegs)


def r21_features(D, S, tf, L, mp, minlegs=30):
    """Merkmale je RSI21-Signal (Einstieg = erste M5-Kerze ab T)."""
    r = S["r21"]
    n = len(r["T"])
    X = np.full((n, 13), np.nan)
    for k, sym in enumerate(SYMS):
        m = np.nonzero(r["sym"] == k)[0]
        if len(m) == 0:
            continue
        ny = D[sym]["ny"]
        i5 = np.searchsorted(ny, r["T"][m])
        ok = i5 < len(ny)
        te = ny[np.minimum(i5, len(ny) - 1)]
        X[m[ok]] = _feat_generic(sym, te[ok], r["dir"][m][ok], tf, L, mp, minlegs)
    return X


def nz_features(D, S, tf, L, mp, minlegs=30):
    """Merkmale je Noise-Pruefung (Long; Einstieg am Open der Pruefkerze i5)."""
    z = S["nz"]
    ny = D["NAS"]["ny"]
    te = ny[z["i5"]]
    return _feat_generic("NAS", te, np.ones(len(te), np.int64), tf, L, mp, minlegs)


class GridMarket(E.Market):
    """Markt mit zusaetzlichen Auslass-Masken fuer RSI21-Signale und Noise-Pruefungen (True = auslassen)."""
    def __init__(self, D, S, r21_block=None, nz_block=None):
        super().__init__(D=D, S=S)
        # Markt sortiert/verwirft RSI21-Zeilen: Zuordnung ueber (ev, sym, tf, dir)
        self.r21_block = np.zeros(len(self.r21["ev"]), bool)
        if r21_block is not None:
            r = S["r21"]; syms = ("XAU", "NAS")
            key_block = set()
            for a in np.nonzero(r21_block)[0]:
                k = int(r["sym"][a]); ny = D[syms[k]]["ny"]
                i5 = int(np.searchsorted(ny, int(r["T"][a])))
                if i5 >= len(ny):
                    continue
                ev = int(np.searchsorted(self.ev_t, ny[i5]))
                key_block.add((ev, k, int(r["tf"][a]), int(r["dir"][a])))
            for q in range(len(self.r21["ev"])):
                if (int(self.r21["ev"][q]), int(self.r21["sym"][q]), int(self.r21["tf"][q]), int(self.r21["dir"][q])) in key_block:
                    self.r21_block[q] = True
        self.nz_block = np.zeros(len(self.nz["ev"]), bool) if nz_block is None else np.asarray(nz_block, bool)


_orig_make_masks = E.make_masks


def make_masks(mk, seed, frac):
    m = _orig_make_masks(mk, seed, frac)
    if isinstance(mk, GridMarket):
        m = (m[0], m[1] | mk.r21_block, m[2] | mk.nz_block, m[3])
    return m


E.make_masks = make_masks
