"""RSI21 Eigenkapital - Kandidaten aus den Bausteinen des Walk-Forward (ek_ca R:TV, Auswahl 2006-21, 2022-26 ungesehen).

Bewertung wie ek_final A: Rendite bei 25 % Jahresvolatilitaet (Risiko je Kandidat aus der Volatilitaet 2006-21, damit 2022-26
auch fuer die Groesse ungesehen bleibt), 16 Stoerungen. Zusaetzlich paarweise gegen 6.60 je Stoerung: CAGR-Differenz je
Periode (Mittel, besser in x von 16).
Aufruf: python ek_kand.py -> ergebnisse/ek_kand.json"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ek_ca as C                                                   # noqa: E402

B = dict(C.BASE_SEL)
A1 = dict(be_at=2.5, rr_nas=3.0)                                    # WF Runde 1: Einstand spaet, NAS-Ziel 3 R
P1 = dict(nslots=3, maxloss=1, w0=1.5, w1=1.0, w2=0.5)              # WF Runde 1: 3 Plaetze, 1 Verlust/Tag, Gewicht M15
A2 = dict(be_at=0.0, rr_gold=3.5)                                   # WF Runde 2: kein Einstand, Gold-Ziel 3,5 R
P2 = dict(nslots=5, maxloss=2, first_mult=1.0, goldmult=1.3)        # WF Runde 4/5: 5 Plaetze, erstes Signal, Gold-Faktor
F_WF = dict(cross_on=False, folge_min=60, gold_bis=13.0, tf_gold=(0,), nas_long_regime=False, stop_atr=1.75, nas_bis=16.0)

def M(*ds):
    """Bausteine zusammensetzen (spaetere ueberschreiben fruehere)."""
    out = {}
    for d in ds:
        out.update(d)
    return out


KAND = [
    ("K0 6.60", B, {}),
    ("K1 Ausstieg (Einstand 2,5 R, NAS-Ziel 3 R)", B, dict(A1)),
    ("K2 K1 + 3 Plaetze, 1 Verlust/Tag, M15 x1,5", B, M(A1, P1)),
    ("K3 K2 ohne Einstand, Gold-Ziel 3,5 R", B, M(A1, P1, A2)),
    ("K4 K3 + 5 Plaetze, erstes Signal, Gold x1,3", B, M(A1, P1, A2, P2)),
    ("K5 WF-Endstand (mit Filtern)", M(B, F_WF), M(A1, P1, A2, P2)),
]


def extra():
    fn = os.path.join(HERE, "ergebnisse", "ek_ca_RTVZ.json")
    if not os.path.exists(fn):
        return []
    d = json.load(open(fn))
    sel = dict(d["sel"])
    for k in ("tf_gold", "tf_nas"):
        if k in sel:
            sel[k] = tuple(sel[k])
    sel7 = dict(sel, tf_gold=(0, 1))
    return [("K6 Endstand R:TVZ (alle Perioden, in-sample)", sel, dict(d["sim"])),
            ("K7 K6 mit Gold M15+M30 (Signale wie 6.60)", sel7, dict(d["sim"]))]


if __name__ == "__main__":
    kand = KAND + extra()
    res = C.run_many(kand, 16, "R:TV")          # r* aus der Volatilitaet 2006-21 (2022-26 bleibt ungesehen)
    base_rows = res[0][0]
    out = []
    for (nm, sel, sim), (rows, rk) in zip(kand, res):
        sm = C.summary(rows)
        d = {}
        for p in ("T", "V", "Z", "G"):
            diff = np.array([r[p]["cagr"] - b[p]["cagr"] for r, b in zip(rows, base_rows)])
            d[p] = (float(diff.mean()), int((diff > 0).sum()))
        out.append(dict(name=nm, sel=sel, sim=sim, r=rk, sm=sm, pair=d))
        print(f"{nm:46s} {C.fmt(sm, rk)}")
        print(f"{'':46s} gegen 6.60: " + " | ".join(f"{p} {100 * d[p][0]:+6.1f} Pp ({d[p][1]}/16)" for p in ("T", "V", "Z", "G")), flush=True)
    with open(os.path.join(HERE, "ergebnisse", "ek_kand.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
