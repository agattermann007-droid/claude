"""Abgleich EA <-> Replikat fuer das Probability Grid (Build 6.20): woertliche Python-Uebertragung von GridM5/GridKerze/
GridIndex/GridRang (MQL5) gegen pgrid (lux_pivots + tf_bars + features) auf den durchgehenden Kursen 2006-2025.
Verglichen werden je Fade-Signal: Laufrichtung, p_ext, p_bar, Anzahl Schenkel."""
import numpy as np, sys
import pg_data as PD, pg_blocks as PB, pgrid as PG


class GridEA:
    """Zustand wie struct GridSer im EA."""
    def __init__(self, tf_min, L, maxpiv):
        self.ts = tf_min * 60; self.L = L; self.maxpiv = maxpiv
        self.aggOn = False; self.aggT = 0; self.aggO = 0.0; self.aggC = 0.0
        self.t = []; self.bo = []; self.bc = []; self.bias = []; self.pivPx = []; self.pivBar = []; self.curPx = []; self.curBar = []
        self.legConf = []; self.legDir = []; self.legSz = []; self.legBars = []
        self.b = 0; self.cbar = -1; self.pbar = -1; self.lbar = -1; self.cpx = 0.0; self.ppx = 0.0; self.lpx = 0.0

    def kerze(self, t, o, c):
        i = len(self.t)
        self.t.append(t); self.bo.append(o); self.bc.append(c)
        if i == 0:
            self.cpx = c; self.cbar = 0; self.lpx = c; self.lbar = 0
        if i >= self.L - 1:
            up = -1e308; lo = 1e308
            for j in range(i - self.L + 1, i + 1):
                a = max(self.bo[j], self.bc[j]); z = min(self.bo[j], self.bc[j])
                if a > up: up = a
                if z < lo: lo = z
            mx = max(o, c); mn = min(o, c)
            b = self.b; nb = b
            if mx == up: nb = 1
            elif mn == lo: nb = -1
            neu = False
            if nb != b and nb != 0:
                if b != 0:
                    neu = True; self.ppx = self.cpx; self.pbar = self.cbar
                self.cpx = up if nb == 1 else lo; self.cbar = i; self.b = nb
            elif b != 0:
                alt = self.cpx
                self.cpx = max(up, self.cpx) if b == 1 else min(lo, self.cpx)
                if self.cpx != alt: self.cbar = i
            if neu and self.lpx > 0.0:
                bd = self.pbar - self.lbar
                if bd != 0:
                    self.legConf.append(i); self.legDir.append(1 if self.ppx > self.lpx else -1)
                    self.legSz.append(abs(self.ppx - self.lpx) / self.lpx); self.legBars.append(bd)
                    self.lpx = self.ppx; self.lbar = self.pbar
        self.bias.append(self.b); self.pivPx.append(self.ppx); self.pivBar.append(self.pbar); self.curPx.append(self.cpx); self.curBar.append(self.cbar)

    def m5(self, bt, bo, bc, tn):
        kb = bt - bt % self.ts
        if not self.aggOn or kb != self.aggT:
            self.aggOn = True; self.aggT = kb; self.aggO = bo
        self.aggC = bc
        kn = tn - tn % self.ts
        if kn != kb:
            self.kerze(self.aggT, self.aggO, self.aggC); self.aggOn = False

    def index(self, tEntry):
        kb = tEntry - tEntry % self.ts
        lo, hi, r = 0, len(self.t) - 1, -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if self.t[mid] < kb: r = mid; lo = mid + 1
            else: hi = mid - 1
        return r

    def rang(self, i, d, x, dauer):
        n = 0; cnt = 0
        for q in range(len(self.legSz) - 1, -1, -1):
            if n >= self.maxpiv: break
            if self.legConf[q] > i or self.legDir[q] != d: continue
            n += 1
            v = float(self.legBars[q]) if dauer else self.legSz[q]
            if v <= x: cnt += 1
        return (cnt / n if n > 0 else 0.0), n


def check(sym, tf, L, mp, nq=400, seed=1):
    A = PD.data_all()[sym]
    ny, o, c = A["ny"], A["o"], A["c"]
    srv = (ny + 420) * 60                                   # Serverzeit in Sekunden (NY + 7 h)
    g = GridEA(tf, L, mp)
    rng = np.random.default_rng(seed)
    # Abfragen: zufaellige Einstiegskerzen (Gewicht auf 2022+), Richtung zufaellig
    qi = np.sort(rng.choice(np.arange(len(ny) // 3, len(ny) - 1), nq, replace=False))
    qd = rng.choice([-1, 1], nq)
    res_ea = []
    k = 0
    for j in range(len(ny) - 1):
        g.m5(int(srv[j]), o[j], c[j], int(srv[j + 1]))
        while k < nq and qi[k] == j + 1:                     # Einstieg bei Kerze j+1: Zustand nach Verarbeitung von Kerze j
            i = g.index(int(srv[j + 1]))
            d = int(qd[k])
            if i < 0 or g.bias[i] == 0 or g.pivBar[i] < 0:
                res_ea.append((np.nan, np.nan, np.nan, 0)); k += 1; continue
            b = g.bias[i]
            ext = abs(g.curPx[i] - g.pivPx[i]) / g.pivPx[i]
            pe, n1 = g.rang(i, b, ext, False)
            pb, _ = g.rang(i, b, float(i - g.pivBar[i]), True)
            res_ea.append((b, pe if n1 >= 30 else np.nan, pb if n1 >= 30 else np.nan, n1)); k += 1
    ea = np.array(res_ea, float)
    X = PB.feats(sym, ny[qi], qd, np.ones(nq), np.ones(nq), np.ones(nq), np.ones(nq), tf, L, mp, 30)
    same_b = np.array_equal(np.nan_to_num(ea[:, 0]), np.nan_to_num(X[:, 0]))
    same_pe = np.allclose(ea[:, 1], X[:, 2], equal_nan=True, atol=1e-12)
    same_pb = np.allclose(ea[:, 2], X[:, 3], equal_nan=True, atol=1e-12)
    same_n = np.array_equal(ea[:, 3], np.nan_to_num(X[:, 7]))
    ok = same_b and same_pe and same_pb and same_n
    print(f"{sym} M{tf} L{L} max{mp}: {nq} Abfragen - Richtung {'gleich' if same_b else 'ABW'}, p_ext {'gleich' if same_pe else 'ABW'}, "
          f"p_bar {'gleich' if same_pb else 'ABW'}, Schenkel {'gleich' if same_n else 'ABW'}", flush=True)
    if not ok:
        bad = np.nonzero(~np.isclose(ea[:, 1], X[:, 2], equal_nan=True) | (ea[:, 3] != np.nan_to_num(X[:, 7])))[0][:5]
        for b_ in bad:
            print("   ", qi[b_], ea[b_], X[b_, [0, 2, 3, 7]])
    return ok


if __name__ == "__main__":
    cfgs = [(int(sys.argv[i]), int(sys.argv[i + 1]), int(sys.argv[i + 2])) for i in range(1, len(sys.argv), 3)] or [(15, 20, 1000), (5, 20, 1000), (60, 10, 300)]
    ok = True
    for tf, L, mp in cfgs:
        for sym in ("XAU", "NAS"):
            ok &= check(sym, tf, L, mp)
    print("GESAMT", "IDENTISCH" if ok else "ABWEICHUNG")
