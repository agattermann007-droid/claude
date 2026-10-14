"""Zufallsvergleich (PLAN 6.6 b): Schlaegt die Familie zufaellige Einstiege mit sonst gleichen Bedingungen?

Je Lauf, getrennt je Kalenderjahr:
  - gleiche Anzahl Einstiege wie die Familie in diesem Jahr,
  - Einstiegskerzen zufaellig (ohne Zuruecklegen) aus allen M15-Kerzen im Session-Fenster der Familie
    (Uhrzeit-Spanne der Familien-Einstiege, Mo-Fr, nicht in den 5 min vor dem Freitags-Schluss),
  - Richtungen = die Richtungen der Familie in diesem Jahr, zufaellig vertauscht,
  - Stop 3 x ATR14 (M15) der Kerze vor dem Einstieg, Ausstieg identisch (handel.handel),
  - eine Position je Symbol: ueberlappende Einstiege entfallen (fuer Familie und Zufall gleich).
Kennzahl: Netto-R (Summe R nach Kosten). Bestanden, wenn die Familie >= 95 % der Laeufe schlaegt
(> 50 Varianten in der Familie: 99 %). Seed = 7000 + Familie x 100 + Symbolindex (konfig).
Zusatz Familie 1: gleiche Termine, zufaellige Richtung (nur Information).
"""
import numpy as np

from . import handel as HD
from . import konfig as K


def ohne_ueberlappung(ein, aus):
    """Indizes der Einstiege, die genommen werden, wenn je Symbol nur eine Position laeuft (zeitlich sortiert)."""
    order = np.argsort(ein, kind="stable")
    frei = -1
    nimm = []
    for a in order:
        if ein[a] > frei:
            nimm.append(a)
            frei = aus[a]
    return np.array(nimm, np.int64)


def netto_r(M, sym, ein, richtung, rd, ziel_r):
    """Netto-R der genommenen Trades (ohne Ueberlappung) und die Einzelergebnisse."""
    if len(ein) == 0:
        return 0.0, np.zeros((0, len(HD.ERG)))
    erg = HD.handel(M, sym, ein, richtung, rd, ziel_r)
    nimm = ohne_ueberlappung(np.asarray(ein), erg[:, 2].astype(np.int64))
    return float(erg[nimm, 0].sum()), erg[nimm]


def fenster(t_sig_m15_start):
    """Uhrzeit-Spanne (NY-Minuten des Tages, [von, bis]) der Einstiegskerzen der Familie."""
    m = np.asarray(t_sig_m15_start) % 1440
    return int(m.min()), int(m.max())


def kandidaten(d, atr, von, bis, we_schluss=16.75):
    """M15-Kerzen (Index j der Einstiegskerze), deren Beginn im Fenster liegt; Mo-Fr; ATR der Vorkerze vorhanden."""
    B = d["m15"]
    t = B["t"]
    m = t % 1440
    dow = (t // 1440 + 4) % 7
    j = np.arange(len(t))
    ok = (m >= von) & (m <= bis) & (dow >= 1) & (dow <= 5) & (j >= 1)
    ok &= ~((dow == 5) & (m >= we_schluss * 60 - 5))
    ok[1:] &= np.isfinite(atr[:-1]) & (atr[:-1] > 0)
    return j[ok]


def vergleich(d, sym, sig, ziel_r, familie, symbolindex, laeufe=K.ZUFALL_LAEUFE, schwelle=K.ZUFALL_SCHWELLE):
    """sig: Familiensignale (i5, dir, rd, j). Rueckgabe dict mit Netto-R der Familie, der Zufallslaeufe und Quantil."""
    from .signale import indikatoren_m15
    B = d["m15"]
    M = HD.markt_arrays(d["ny"], d["o"], d["h"], d["l"], d["c"], d["sp"])
    atr = indikatoren_m15(d)
    fam_r, fam_erg = netto_r(M, sym, sig["i5"], sig["dir"], sig["rd"], ziel_r)
    j_ein = np.asarray(sig["j"]) + 1                                       # Einstiegskerze (M15)
    von, bis = fenster(B["t"][j_ein])
    pool = kandidaten(d, atr, von, bis)
    jahr_pool = (B["t"][pool] // 1440).astype("datetime64[D]").astype("datetime64[Y]").astype(int)
    jahr_fam = (B["t"][j_ein] // 1440).astype("datetime64[D]").astype("datetime64[Y]").astype(int)
    rng = np.random.default_rng(K.SEED_ZUFALL + 100 * familie + symbolindex)
    ein_all, dir_all, rd_all, lauf_all = [], [], [], []
    for lauf in range(laeufe):
        for y in np.unique(jahr_fam):
            n = int((jahr_fam == y).sum())
            p = pool[jahr_pool == y]
            if len(p) < n:
                raise ValueError(f"Jahr {y}: nur {len(p)} Kandidaten fuer {n} Einstiege")
            jj = rng.choice(p, n, replace=False)
            dd = rng.permutation(np.asarray(sig["dir"])[jahr_fam == y])
            ein_all.append(B["first"][jj]); dir_all.append(dd); rd_all.append(3.0 * atr[jj - 1])
            lauf_all.append(np.full(n, lauf))
    ein = np.concatenate(ein_all); dirs = np.concatenate(dir_all); rd = np.concatenate(rd_all)
    lauf_id = np.concatenate(lauf_all)
    erg = HD.handel(M, sym, ein, dirs, rd, ziel_r)                        # alle Laeufe in einem Aufruf
    zr = np.zeros(laeufe)
    for lauf in range(laeufe):
        m = np.nonzero(lauf_id == lauf)[0]
        nimm = ohne_ueberlappung(ein[m], erg[m, 2].astype(np.int64))
        zr[lauf] = erg[m[nimm], 0].sum()
    quantil = float((zr < fam_r).mean())
    return dict(netto_r=fam_r, trades=len(fam_erg), zufall_r=zr, quantil=quantil, bestanden=quantil >= schwelle,
                fenster=(von, bis), pool=len(pool), seed=K.SEED_ZUFALL + 100 * familie + symbolindex)


def gleiche_termine_zufallsrichtung(d, sym, sig, ziel_r, familie, symbolindex, laeufe=K.ZUFALL_LAEUFE):
    """Familie 1 (Information): dieselben Einstiege, Richtung je Termin zufaellig."""
    M = HD.markt_arrays(d["ny"], d["o"], d["h"], d["l"], d["c"], d["sp"])
    fam_r, _ = netto_r(M, sym, sig["i5"], sig["dir"], sig["rd"], ziel_r)
    rng = np.random.default_rng(K.SEED_ZUFALL + 100 * familie + 50 + symbolindex)
    n = len(sig["i5"])
    i5 = np.asarray(sig["i5"])
    lang = HD.handel(M, sym, i5, np.ones(n, np.int64), sig["rd"], ziel_r)
    kurz = HD.handel(M, sym, i5, -np.ones(n, np.int64), sig["rd"], ziel_r)
    zr = np.zeros(laeufe)
    for lauf in range(laeufe):
        dd = rng.choice([-1, 1], n)
        erg = np.where((dd > 0)[:, None], lang, kurz)
        nimm = ohne_ueberlappung(i5, erg[:, 2].astype(np.int64))
        zr[lauf] = erg[nimm, 0].sum()
    return dict(netto_r=fam_r, zufall_r=zr, quantil=float((zr < fam_r).mean()))
