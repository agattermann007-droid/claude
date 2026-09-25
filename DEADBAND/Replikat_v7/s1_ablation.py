"""Screening 1 (ohne Konto): Beitrag jeder RSI21-Regel (Abschalt-Tests) und einfache Parameter-Nachbarn.
Kennzahl: R x Gewicht je Jahr (Gewicht = Zeitebene x Gold-Faktor wie in der EA), je Epoche."""
import numpy as np, sys
import r7data, r7sig as G, r7sim as M

D = r7data.data()
C = G.features(D)


def run(lbl, p=None, tp=None, rd_mult=1.0, sim=None, weights=(1.25, 1.0, 0.75), gold_mult=0.7, show=True):
    q = dict(G.BASE, **(p or {}))
    E = G.entries(C, q, tp=tp, weights=weights, gold_mult=gold_mult, rd_mult=rd_mult)
    trs = [M.simulate(D[s], s, E[s], **(sim or {})) for s in G.SYMS]
    A = M.merge(trs)
    m = M.metrics(A)
    if show:
        print(M.line(lbl, m), flush=True)
    return A, m


if __name__ == "__main__":
    run("Basis (EA 6.10)")
    print("--- Regeln einzeln abgeschaltet")
    run("ohne Folgesignal", dict(folge_min=0))
    run("ohne Kreuz-Bestaetigung", dict(cross=None))
    run("Gold ohne Gate (nur Kreuz)", dict(gold_gate=False))
    run("ohne H4-Divergenz", dict(use_div=False))
    run("Shorts ohne Regime", dict(short_rule="none"))
    run("NAS-Longs ohne SMA200", dict(nas_long_rule="none"))
    run("ohne zweiten Platz", sim=dict(second=False))
    run("ohne Verlustgrenze je Tag", sim=dict(maxloss=0))
    run("ohne Wochenend-Pause", sim=dict(we_on=False))
    print("--- Richtungen, Zeitebenen")
    run("nur Long", dict(dirs=(1,)))
    run("nur Short", dict(dirs=(-1,)))
    run("Gold mit H1", dict(gold_ohne_h1=False))
    for tfs in ((0,), (1,), (2,), (0, 1), (1, 2)):
        run(f"nur Zeitebenen {tfs}", dict(tfs=tfs))
    print("--- Schwelle")
    for ob in (70.0, 72.5, 77.5, 80.0):
        run(f"RSI > {ob}", dict(oben=ob))
    print("--- Zeitfenster")
    for ab in (3.0, 8.0, 9.0, 10.0, 11.0):
        run(f"ab {ab} NY", dict(ab=ab))
    for nb in (11.0, 12.0, 14.0, 15.0, 16.0):
        run(f"NAS bis {nb} NY", dict(nas_bis=nb))
    for gb in (12.0, 13.0, 15.0, 20.0):
        run(f"Gold bis {gb} NY", dict(gold_bis=gb))
    print("--- Folgesignal-Fenster")
    for fm in (60, 120, 180, 360, 480, 720):
        run(f"Folge {fm} min", dict(folge_min=fm))
