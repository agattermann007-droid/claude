"""Screening 17: RSI21-Rueckzug (Idee 'RSI range shift', Cardwell/Brown): nach einem gueltigen RSI21-Signal gilt fuer
H Stunden 'Bullen-Bereich'; faellt der RSI(21) derselben Zeitebene unter L und dreht wieder ueber L+U, Einstieg in
Signalrichtung (Stop 2 ATR, Ziel wie RSI21). Eigenstaendig bewertet und zusammen mit RSI21."""
import numpy as np
import r7sig as G, r7sim as M, r7kand as KD
import prep5 as P
from r7lab import D, C, short


def pullback_cands(p, H=24, L=45.0, U=5.0, tfs=(0,), tp=(2.64, 2.2), stop_atr=2.0, maxwait_bars=None):
    m = G.valid_mask(C, dict(G.BASE, **p))
    out = {}
    for si, s in enumerate(G.SYMS):
        rows = []
        for ti in tfs:
            kk = G.KEYS[ti]
            B = D[s][kk]
            r = P.rsi_wilder(B["c"], 21)
            a = P.atr_sma(B["h"], B["l"], B["c"], 14)
            t = B["t"]
            sel = np.nonzero(m & (C["sym"] == si) & (C["tf"] == ti))[0]
            # Signale je Richtung: Zeit T (Beginn der Kerze nach der Signalkerze)
            for dd in (1, -1):
                Ts = C["T"][sel[C["dir"][sel] == dd]]
                if len(Ts) == 0:
                    continue
                # je Kerze k: letzte Signalzeit <= t[k]
                j = np.searchsorted(Ts, t, side="right") - 1
                last = np.where(j >= 0, Ts[np.clip(j, 0, None)], -10**12)
                active = (t - last) <= H * 60
                x = r if dd > 0 else 100.0 - r
                armed = False; prev_act_sig = -1
                for k in range(1, len(t) - 1):
                    if not active[k]:
                        armed = False
                        continue
                    if last[k] != prev_act_sig:
                        prev_act_sig = last[k]; armed = False
                    if not np.isfinite(x[k]):
                        continue
                    if x[k] < L:
                        armed = True
                    elif armed and x[k] > L + U and np.isfinite(a[k]) and a[k] > 0:
                        rows.append((t[k + 1], ti, dd, stop_atr * a[k]))
                        armed = False
        if not rows:
            out[s] = None
            continue
        rows.sort()
        A = np.array(rows, dtype=float)
        T = A[:, 0].astype(np.int64)
        ny = D[s]["ny"]
        i5 = np.searchsorted(ny, T)
        ok = i5 < len(ny)
        # Handelszeit wie RSI21 (Kerzenbeginn NY 9:30 .. Gold 17 / NAS 13)
        nyh = (T % 1440) / 60.0
        bis = 17.0 if si == 0 else 13.0
        ok &= (nyh >= 9.5) & (nyh < bis)
        w = np.where(A[:, 1] == 0, 1.25, 1.0) * (0.7 if si == 0 else 1.0)
        out[s] = dict(i5=i5[ok], dir=A[ok, 2].astype(np.int64), rd=A[ok, 3], tp=np.full(ok.sum(), tp[si]), tf=A[ok, 1].astype(np.int64), w=w[ok])
    return out


def run_c(lbl, cands, sim=None):
    trs = [M.simulate(D[s], s, cands[s], **(sim or {})) for s in G.SYMS if cands.get(s) is not None]
    A = M.merge(trs)
    m = M.metrics(A)
    m["rp36"] = M.risk_parity(A, 0.36)[1]; m["rp20"] = M.risk_parity(A, 0.2)[1]
    print(short(lbl, m), flush=True)
    return A


if __name__ == "__main__":
    p = KD.basis(C)
    for H, L, U in ((24, 45, 5), (24, 50, 5), (24, 40, 5), (12, 45, 5), (48, 45, 5), (24, 45, 10), (72, 45, 5)):
        c = pullback_cands(p, H, L, U)
        run_c(f"Rueckzug H{H} L{L} U{U} (M15)", c)
    c = pullback_cands(p, 24, 45, 5, tfs=(0, 1))
    run_c("Rueckzug H24 L45 U5 (M15+M30)", c)
