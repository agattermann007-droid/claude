"""Konto-Ebene: V8.10-Baseline und Kandidaten ueber den Kontomotor eng6 (PLAN 4.1, E1-A, E9).

- umgebung(): Replikat auf Auswahl-Daten (data/, bis zum Stichtag) oder - genau einmal - auf die Blinddaten stellen.
  Jede Umgebung hat einen eigenen Cache, damit nie Blinddaten in eine Auswahl-Rechnung geraten.
- baseline(): Stroeme und GP von V8.10 = 8.00 (z8) + Trend-Day (z8_final.TD), Motor-Parameter Y.BASE + z8.KW80.
- familien_block(): Familiensignale als generischer eng6-Strom mit DEADBAND-Ausstieg (Tp1 1,5 R / 50 %, Stop +0,05 R,
  Endziel 8/10 R, Zeit-Exit 192 M15, Wochenend-Wiederaufnahme), Einstieg nur bei flachem Symbol (E9),
  Risiko = RiskPctList x DbRiskMult wie das H1-Modul, bei Reife laufen sie aus (StopMode 0).
- tageslauf(): durchgehender Lauf fuer die Tagesdatensaetze des Bootstraps (keine Auszahlung, keine Regel-Pleite,
  Bodenverletzung = gedachtes neues Konto, EA-Bremsen aktiv).
- rollierend(): Gegenprobe wie die V8-Berichte (frische 10k-Konten an rollierenden Starts, Stoerungs-Seeds).

Alle Laeufe mit we_genau=1 (Wochenend-Wiederaufnahme wie im EA jede Kerze), Baseline und Kandidaten gleich.
"""
import os

import numpy as np

from . import daten as DT
from . import handel as HD
from . import konfig as K
from . import tage as TG

RISIKO_H1 = {"XAU": 0.259, "NAS": 0.288}          # RiskPctList (V8.10), mal DbRiskMult 0,9
H1_MULT = 0.9
ZIEL_R = {"XAU": 8.0, "NAS": 10.0}
FORSCHUNG = dict(we_genau=1)


def _replikat():
    import eng6 as E, evl6 as V, prep5 as P, gsig as G, z8, n8_port, cands, streams, y7_konto as Y
    return E, V, P, G, z8, n8_port, cands, streams, Y


def umgebung(blind=False):
    """Replikat-Daten und Caches umstellen. blind=True nur fuer den einen Blindlauf (wird protokolliert)."""
    E, V, P, G, z8, NP, C, S, Y = _replikat()
    ziel = K.DATEN_BLIND if blind else K.DATEN
    cache = os.path.join(K.RESEARCH, "cache", "blind" if blind else "auswahl")
    if P.DATA == ziel and P.OUT == cache:
        return
    if blind:
        DT.protokolliere_blindzugriff("konto.umgebung", "Replikat auf data_blind/")
    else:
        DT.pruefe_auswahl_ordner(ziel)
    os.makedirs(cache, exist_ok=True)
    P.DATA = ziel; P.OUT = cache
    G._D = None; V._MK = None; V._MASKS.clear(); V._GP = None; z8._DS = None; NP.FADES = None
    C._CACHE.clear(); S._VT.clear()
    if not os.path.exists(os.path.join(cache, "sig5.pkl")):
        import sig5
        sig5.build_all(save=True)


def baseline():
    """(Bloecke, GP-Liste) von V8.10. Braucht echte Daten (umgebung())."""
    E, V, P, G, z8, NP, C, S, Y = _replikat()
    import z8_final as ZF
    z8.use("gft")
    blks = list(z8.BLKS); gps = [dict(g) for g in z8.GPS]
    for nm, gp in ZF.TD:
        sym, gen, args = NP.LIB[nm] if nm in NP.LIB else z8.NP.LIB[nm]
        blks.append(z8.NK.block(sym, gen, args, len(blks)))
        gps.append(dict(dict(on=1, risk=0.75, maxtrades=1, harv=1), **gp))
    return blks, gps


def motor_parameter(**kw):
    E, V, P, G, z8, NP, C, S, Y = _replikat()
    c = dict(Y.BASE)
    for teil in (z8.KW80, FORSCHUNG, kw):                  # spaetere Angaben ueberschreiben fruehere
        c.update(teil)
    return E.params(**c)


def familien_block(d, kurz, sig, strom, punkt=0.01, stoplvl=0.0):
    """Familiensignale (familien.*) eines Symbols als eng6-Block. Filter wie das H1-Modul: Stop > 50 Punkte und
    >= Stopplevel. Zeit-Exit = Open der 193. M15-Kerze nach dem Einstieg."""
    M = HD.markt_arrays(d["ny"], d["o"], d["h"], d["l"], d["c"], d["sp"])
    i5 = np.asarray(sig["i5"], np.int64)
    rd = np.asarray(sig["rd"], float)
    ok = (rd > 50 * punkt) & (rd >= stoplvl)
    i5, rd, dirs = i5[ok], rd[ok], np.asarray(sig["dir"], np.int64)[ok]
    tx = HD.zeit_ausstieg_ny(M, i5, 192)
    k = 0 if kurz == "XAU" else 1
    return dict(str=strom, sym=np.full(len(i5), k), dir=dirs, t_entry=d["ny"][i5], rd=rd, tp=ZIEL_R[kurz], t_exit=tx, w=1.0)


def familien_gp(kurz, **kw):
    gp = dict(on=1, risk=RISIKO_H1[kurz] * H1_MULT, tp1r=1.5, tp1f=0.5, be=0.05, tpdelay=0, maxtrades=1, maxloss=2,
              harv=1, usefak=1, ripeclose=0, we_resume=1, flat_only=1)
    gp.update(kw)
    return gp


def tageslauf(mk, blks, gps, d0=None, d1=None, **kw):
    """Ein durchgehender Lauf -> (tag, X) fuer den Bootstrap (tage.FELDER)."""
    E = _replikat()[0]
    mk.set_generic(blks)
    GP = E.gparams(gps)
    Pv = motor_parameter(**dict(dict(needvalid=999, rulefloat=0.0, ruleday=0.0, pleite_weiter=1), **kw))
    a = 0 if d0 is None else mk.day_index(d0)
    b = len(mk.days) if d1 is None else mk.day_index(d1)
    r = E.run(mk, Pv, a, b, GP=GP, tage=True)
    t = r["tage"]
    t = t[t[:, 0] >= 0]
    return TG.aus_lauf(t), r


def rollierend(blks, gps, ende=K.STICHTAG, seeds=tuple(range(8)), **kw):
    """Gegenprobe: rollierende 10k-Konten (250/500 Tage, jeder 3. Handelstag, Stoerungen 5 %) wie z8.evaluate."""
    E, V, *_ = _replikat()
    GP = E.gparams(gps)
    V.set_generic(blks, GP)
    return V.evaluate(motor_parameter(**kw), GP=GP, horizons=(250, 500), step=3, seeds=seeds, skip=0.05, end=ende)["mean"]
