"""RSI21-Labor: gemeinsame Helfer fuer die Screenings (Daten, Merkmale, Lauf mit Risiko-Paritaet)."""
import numpy as np
import r7data, r7sig as G, r7sim as M

D = r7data.data()
C = G.features(D)


def run(lbl, p=None, tp=None, rd_mult=1.0, sim=None, weights=(1.25, 1.0, 0.75), gold_mult=0.7, show=True, syms=False):
    q = dict(G.BASE, **(p or {}))
    E = G.entries(C, q, tp=tp, weights=weights, gold_mult=gold_mult, rd_mult=rd_mult)
    trs = [M.simulate(D[s], s, E[s], **(sim or {})) for s in G.SYMS]
    A = M.merge(trs)
    m = M.metrics(A)
    f, ry = M.risk_parity(A, 0.36)
    f2, ry2 = M.risk_parity(A, 0.2)
    m["rp36"] = ry; m["rp20"] = ry2
    if show:
        print(M.line(lbl, m) + f" | RP36 {ry:+.1f} RP20 {ry2:+.1f}", flush=True)
        if syms:
            for si, s in enumerate(G.SYMS):
                print(M.line(f"    {s}", M.metrics(M.sub(A, A["sym"] == si))), flush=True)
    return A, m


def short(lbl, m):
    eps = " ".join(f"{v:+5.1f}" for v in m["ep"].values())
    return (f"{lbl:<46s} {m['tpy']:5.1f}/J ØR{m['avgR']:+.3f} R/J{m['Ry']:+6.1f} DD{m['ddR']:5.1f} maxS{m['maxS']:3d} "
            f"B12 {m['b12']:.2f} Sh {m['sh']:.2f} RP36 {m['rp36']:+5.1f} RP20 {m['rp20']:+5.1f} | {eps}")


def srun(lbl, p=None, **kw):
    A, m = run(lbl, p, show=False, **kw)
    print(short(lbl, m), flush=True)
    return A, m
