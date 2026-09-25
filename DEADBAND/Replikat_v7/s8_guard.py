"""Screening 8: Regime-Waechter fuer RSI21 (wie bei den Fades): Einstieg nur, wenn die letzten N virtuellen
Folgesignale (unabhaengig simuliert, vor dem Signal geschlossen) PF > x bzw. Summe > 0 hatten."""
import numpy as np
import r7data, r7sig as G, r7sim as M, r7lim as L, r7kand as KD
from r7lab import run, C, D


def virtual(p):
    """Virtuelles Ergebnis je Folgesignal (Index in C): R, Ausstiegszeit (NY-Minute)."""
    m = G.valid_mask(C, p)
    f = G.follow(C, m, p["folge_min"])
    use = m & f
    Rv = np.full(len(C["T"]), np.nan); tx = np.full(len(C["T"]), np.iinfo(np.int64).max)
    for si, s in enumerate(G.SYMS):
        idx = np.nonzero(use & (C["sym"] == si))[0]
        d = D[s]
        tp = np.full(len(idx), 2.64 if si == 0 else 2.2)
        R, fl, jx = L.sim_lim(d["o"], d["h"], d["l"], d["c"], d["sp"], C["i5"][idx].astype(np.int64), C["dir"][idx].astype(np.int64),
                              C["rd"][idx], tp, 0.0, 0, 1152, M.COMM[s])
        Rv[idx] = R; tx[idx] = d["ny"][jx]
    return use, Rv, tx


def guard(use, Rv, tx, N, th, mode="pf", per_sym=False, per_dir=False):
    live = np.zeros(len(use), bool)
    idx = np.nonzero(use)[0]
    T = C["T"]
    for i in idx:
        cand = idx[(tx[idx] < T[i])]
        if per_sym:
            cand = cand[C["sym"][cand] == C["sym"][i]]
        if per_dir:
            cand = cand[C["dir"][cand] == C["dir"][i]]
        if len(cand) < N:
            live[i] = True
            continue
        last = cand[np.argsort(tx[cand], kind="stable")][-N:]
        w = Rv[last]
        if mode == "pf":
            pos = w[w > 0].sum(); neg = -w[w < 0].sum()
            live[i] = (pos / neg if neg > 0 else 9.9) > th
        else:
            live[i] = w.sum() > th
    return live


if __name__ == "__main__":
    for nm, fn in (("Basis", KD.basis), ("K1", KD.k1)):
        p = fn(C)
        run(nm, p)
        use, Rv, tx = virtual(p)
        for N, th, mode, ps in ((10, 1.0, "pf", True), (20, 1.0, "pf", True), (30, 1.0, "pf", True), (20, 0.0, "sum", True),
                                (20, 1.2, "pf", True), (30, 1.2, "pf", False), (40, 1.0, "pf", False), (15, 0.8, "pf", True)):
            live = guard(use, Rv, tx, N, th, mode, per_sym=ps)
            run(f"  {nm} Waechter {mode} {N} > {th} {'je Symbol' if ps else 'gesamt'}", dict(p, post=live))
