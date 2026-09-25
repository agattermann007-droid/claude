"""RSI21-Kandidaten als Regel-Saetze (Funktion der Merkmalstabelle C, damit sie auf jedem Datensatz gleich wirken)."""
import numpy as np
import r7sig as G


def _masks(C):
    g = C["sym"] == 0
    ro = C["ro"]; d = C["dir"]
    cross55 = np.where(d > 0, ro > 55, ro < 45) & np.isfinite(ro)
    gate = np.where(d > 0, (C["cprev"] > C["maL"]) & (C["cprev"] > C["maS"]), (C["cprev"] < C["maL"]) & (C["cprev"] < C["maS"]))
    return g, cross55, gate


def basis(C):
    return dict(G.BASE)


def k1(C):
    """NAS ohne Kreuz-Bestaetigung; Gold wie bisher (Kreuz ODER Gate)."""
    g, cross55, gate = _masks(C)
    return dict(G.BASE, cross=None, extra=np.where(g, cross55 | gate, True))


def k2(C, gold_ab=3.0):
    """K1 + Gold-Signale ab gold_ab NY (London) statt 9:30."""
    g, cross55, gate = _masks(C)
    win = np.where(g, C["nyh"] >= gold_ab, C["nyh"] >= 9.5)
    return dict(G.BASE, cross=None, ab=0.0, extra=np.where(g, cross55 | gate, True) & win)


def k3(C, gold_ab=3.0):
    """K2 + Gold nur M15."""
    g, cross55, gate = _masks(C)
    win = np.where(g, C["nyh"] >= gold_ab, C["nyh"] >= 9.5)
    tf = ~g | (C["tf"] == 0)
    return dict(G.BASE, cross=None, ab=0.0, extra=np.where(g, cross55 | gate, True) & win & tf)


KAND = {"Basis": basis, "K1 NAS ohne Kreuz": k1, "K2 K1+Gold ab 3": k2, "K3 K2+Gold nur M15": k3}


def k1g(C):
    """K1 + Gold nur M15."""
    p = k1(C)
    g = C["sym"] == 0
    return dict(p, extra=p["extra"] & (~g | (C["tf"] == 0)))


def k1n(C):
    """K1 + NAS-Longs ohne SMA200-Bedingung."""
    return dict(k1(C), nas_long_rule="none")


def k1gn(C):
    """K1 + Gold nur M15 + NAS-Longs ohne SMA200."""
    return dict(k1g(C), nas_long_rule="none")


KAND.update({"K1g Gold nur M15": k1g, "K1n NAS-Long ohne SMA200": k1n, "K1gn": k1gn})


def kg(C):
    """Basis + Gold nur M15 (NAS unveraendert)."""
    p = dict(G.BASE)
    g = C["sym"] == 0
    return dict(p, extra=(~g | (C["tf"] == 0)))


def kgn(C):
    """Basis + Gold nur M15 + NAS-Longs ohne SMA200 (NAS-Kreuz bleibt)."""
    return dict(kg(C), nas_long_rule="none")


KAND.update({"Kg Gold nur M15": kg, "Kgn": kgn})


def weak_nas_nocross(C):
    """NAS-Signale ohne Kreuz-Bestaetigung (fuer reduziertes Gewicht)."""
    g, cross55, gate = _masks(C)
    return (~g) & ~cross55


def k_nasx(thr):
    """NAS-Kreuz-Schwelle thr (Gold weiter 55 | Gate)."""
    def f(C):
        g, cross55, gate = _masks(C)
        ro = C["ro"]; d = C["dir"]
        crossN = np.where(d > 0, ro > thr, ro < 100 - thr) & np.isfinite(ro)
        return dict(G.BASE, cross=None, extra=np.where(g, cross55 | gate, crossN))
    return f


for _t in (35, 40, 45, 50):
    KAND[f"NAS-Kreuz {_t}"] = k_nasx(float(_t))


def k_vol(th, base=None):
    """Einstiegsfilter Volumen: Tick-Volumen der Signalkerze >= th x Mittel der letzten 50 Kerzen (ohne Volumen: erlaubt)."""
    def f(C):
        p = (base or basis)(C)
        v = C["vrel"]
        ok = ~np.isfinite(v) | (v <= 0) | (v >= th)
        post = ok if p.get("post") is None else (p["post"] & ok)
        return dict(p, post=post)
    return f


for _t in (1.0, 1.2, 1.5, 2.0):
    KAND[f"Volumen {_t}"] = k_vol(_t)

for _t in (1.3, 1.7):
    KAND[f"Volumen {_t}"] = k_vol(_t)

KAND["K1 + Volumen 1.5"] = k_vol(1.5, base=k1)
KAND["K1 + Volumen 2.0"] = k_vol(2.0, base=k1)
KAND["K1gn + Volumen 1.5"] = k_vol(1.5, base=k1gn)


def kgl(C, gold_ab=3.0):
    """Basis + Gold-Signale ab gold_ab NY (Kreuz-Regeln unveraendert)."""
    g = C["sym"] == 0
    return dict(G.BASE, ab=0.0, extra=np.where(g, C["nyh"] >= gold_ab, C["nyh"] >= 9.5))


KAND["Gold ab 3 NY"] = kgl
