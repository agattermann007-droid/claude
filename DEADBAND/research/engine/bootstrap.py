"""GFT-Bootstrap auf Tagesdatensaetzen (PLAN 3.3, Auftrag Abschnitt 5).

Kreisblock-Bootstrap: je Pfad werden Bloecke von b aufeinanderfolgenden Prop-Tagen (Start zufaellig, am Ende
umlaufend) aneinandergehaengt, bis 252 Handelstage erreicht sind. Gepaart: Baseline und Kandidat laufen auf
denselben Indexpfaden (gleicher Index = gleicher Kalendertag, tage.ausrichten).

Konto im Pfad (wie eng6/EA, Werte aus konfig):
  - Groessenfaktor zu Tagesbeginn = Pufferkurve (Puffer = Equity - Boden, in % vom Start) x 0,95 unter Start.
  - Pleite, wenn im Tag (unguenstige Reihenfolge: erst das Hoch hebt den Boden, dann das Tief):
      tiefste Equity <= Equity-Hoch - 6 % (nachlaufend inkl. offener Gewinne),
      groesster Floating-Verlust <= -1,0 % der Basis (Start, unter Start der Saldo),
      tiefste Equity - Tagesreferenz <= -3 % der Tagesreferenz.
    Rest des Tages flach, am naechsten Prop-Tag neues Konto (148,50 $; eng6 rebuydelay 1).
  - Gueltiger Tag: realisiert >= 0,5 % + 0,50 $. Reif: 5 gueltige Tage, >= 10 Kalendertage seit dem ersten
    Handelstag des Zyklus, Gewinn >= 131,25 $. Dann flach bis zur Auszahlung (2 Tageswechsel spaeter).
  - Auszahlung = Gewinn, die ersten 2 je Konto hoechstens 6 %; Saldo sinkt um den Betrag, Boden neu.
  - Netto = 0,8 x 0,97 x Auszahlungen - 148,50 $ je Pleite.
"""
import numpy as np
from numba import njit

from . import konfig as K
from .tage import FI

AUS = ("n_aus", "summe_aus", "n_pleite", "kal_tage", "n_gueltig", "rest_gewinn")


def indizes(n, block, pfade=K.BOOT_PFADE, tage=K.BOOT_TAGE_JE_PFAD, seed=None):
    """Indexpfade [pfade, tage] eines Kreisblock-Bootstraps ueber n Tage."""
    rng = np.random.default_rng(K.SEED_BOOTSTRAP + block if seed is None else seed)
    nb = -(-tage // block)
    st = rng.integers(0, n, size=(pfade, nb))
    idx = (st[:, :, None] + np.arange(block)[None, None, :]) % n
    return idx.reshape(pfade, nb * block)[:, :tage].astype(np.int64)


@njit(cache=True)
def _faktor(eq, peak, abstand, start, voll, minimum, ffak, unter):
    buf = (eq - (peak - abstand)) / start * 100.0
    if voll <= 0.0 or buf >= voll:
        f = 1.0
    elif buf <= minimum:
        f = ffak
    else:
        f = ffak + (1.0 - ffak) * (buf - minimum) / (voll - minimum)
    if eq < start:
        f *= unter
    return f


@njit(cache=True)
def _pfade(X, idx, cfg):
    start = cfg[0]; abstand = start * cfg[1] / 100.0; float_pct = cfg[2]; tag_pct = cfg[3]; needday = cfg[4]
    needvalid = int(cfg[5]); zyklus = cfg[6]; minprofit = cfg[7]; deckel = start * cfg[8] / 100.0; deckel_n = int(cfg[9])
    w_aus = int(cfg[10]); w_neu = int(cfg[11]); voll = cfg[12]; minimum = cfg[13]; ffak = cfg[14]; unter = cfg[15]
    iE = 0; imin = 1; imax = 2; iflt = 3; ireal = 4; iref = 5; ibal = 6; igap = 7; iakt = 8
    P, T = idx.shape
    out = np.zeros((P, 6))
    for p in range(P):
        eq = start; peak = start; modus = 0; warte = 0; gueltig = 0; zyk = -1.0; n_acc = 0
        kal = 0.0
        for t in range(T):
            d = idx[p, t]
            kal += X[d, igap]
            if modus == 2:                                   # wartet auf Auszahlung (flach)
                warte -= 1
                if warte > 0:
                    continue
                amt = eq - start
                if n_acc < deckel_n and amt > deckel:
                    amt = deckel
                if amt < 0.0:
                    amt = 0.0
                eq -= amt; peak = eq
                out[p, 0] += 1.0; out[p, 1] += amt
                n_acc += 1; gueltig = 0; zyk = -1.0; modus = 0
            elif modus == 3:                                 # Pleite: Pause bis zum neuen Konto
                warte -= 1
                if warte > 0:
                    continue
                eq = start; peak = start; n_acc = 0; gueltig = 0; zyk = -1.0; modus = 0
            f = _faktor(eq, peak, abstand, start, voll, minimum, ffak, unter)
            e0 = eq
            hoch = e0 + X[d, imax] * f
            tief = e0 + X[d, imin] * f
            if hoch > peak:
                peak = hoch
            saldo = e0 + X[d, ibal] * f
            fb = start if saldo >= start else saldo
            ref = e0 + X[d, iref] * f
            if tief <= peak - abstand or X[d, iflt] * f <= -fb * float_pct / 100.0 or tief - ref <= -ref * tag_pct / 100.0:
                out[p, 2] += 1.0
                modus = 3; warte = w_neu
                continue
            eq = e0 + X[d, iE] * f
            if X[d, iakt] > 0.5 and zyk < 0.0:
                zyk = kal
            if X[d, ireal] * f >= needday:
                gueltig += 1
                out[p, 4] += 1.0
            if gueltig >= needvalid and zyk >= 0.0 and kal - zyk >= zyklus and eq - start >= minprofit:
                modus = 2; warte = w_aus
        out[p, 3] = kal
        out[p, 5] = eq - start if modus != 3 else 0.0
    return out


def cfg_vektor(gft=K.GFT, puffer=K.PUFFERKURVE):
    needday = gft["start"] * gft["gueltig_pct"] / 100.0 + gft["gueltig_reserve"]
    minprofit = gft["min_auszahlung"] / gft["anteil"]
    return np.array([gft["start"], gft["boden_pct"], gft["float_pct"], gft["tag_pct"], needday, gft["gueltige_tage"],
                     gft["zyklus_tage"], minprofit, gft["deckel_pct"], gft["deckel_anzahl"], K.WARTE_AUSZAHLUNG,
                     K.WARTE_NEUKONTO, puffer["voll"], puffer["minimum"], puffer["faktor"], puffer["unter_start"]], float)


def pfade(X, idx, cfg=None):
    """Rohergebnis je Pfad (Spalten AUS)."""
    return _pfade(np.ascontiguousarray(X, dtype=np.float64), idx, cfg_vektor() if cfg is None else cfg)


def kennzahlen(roh, gft=K.GFT):
    """Netto pro Monat (Zielgroesse), Auszahlungen/Jahr, Pleiten/Jahr, bpp, Durchschnittsauszahlung, Quantile."""
    jahre = roh[:, 3].sum() / 365.25
    monate = roh[:, 3] / (365.25 / 12.0)
    netto_pfad = gft["anteil"] * K.AUSZ_FAKTOR * roh[:, 1] - gft["kontopreis"] * roh[:, 2]
    nm = netto_pfad / monate
    n_aus = roh[:, 0].sum(); n_pl = roh[:, 2].sum()
    return dict(netto_monat=float(netto_pfad.sum() / monate.sum()), netto_monat_q05=float(np.quantile(nm, 0.05)),
                netto_monat_q50=float(np.quantile(nm, 0.50)), netto_monat_q95=float(np.quantile(nm, 0.95)),
                aus_jahr=float(n_aus / jahre), pleiten_jahr=float(n_pl / jahre),
                bpp=float(n_pl / n_aus) if n_aus > 0 else float("inf"),
                aus_mittel=float(roh[:, 1].sum() / max(n_aus, 1)), pfade=int(len(roh)), netto_pfad_monat=nm)


def bewerte(X, bloecke=K.BOOT_BLOECKE, pfade_n=K.BOOT_PFADE, tage=K.BOOT_TAGE_JE_PFAD):
    """Kennzahlen je Blockgroesse (Indexpfade aus dem festen Seed, damit gepaart)."""
    erg = {}
    for b in bloecke:
        idx = indizes(len(X), b, pfade_n, tage)
        erg[b] = kennzahlen(pfade(X, idx))
    return erg


def vergleich(Xb, Xk, bloecke=K.BOOT_BLOECKE, pfade_n=K.BOOT_PFADE, tage=K.BOOT_TAGE_JE_PFAD):
    """Gepaarter Vergleich Kandidat gegen Baseline (gleiche Indexpfade). Rueckgabe je Blockgroesse: beide Kennzahlen,
    Differenz Netto/Monat und Anteil der Pfade, in denen der Kandidat mehr Netto bringt."""
    assert Xb.shape == Xk.shape
    erg = {}
    for b in bloecke:
        idx = indizes(len(Xb), b, pfade_n, tage)
        kb = kennzahlen(pfade(Xb, idx)); kk = kennzahlen(pfade(Xk, idx))
        diff = kk["netto_pfad_monat"] - kb["netto_pfad_monat"]
        erg[b] = dict(baseline=kb, kandidat=kk, diff_netto_monat=kk["netto_monat"] - kb["netto_monat"],
                      anteil_besser=float((diff > 0).mean()), diff_q05=float(np.quantile(diff, 0.05)))
    return erg
