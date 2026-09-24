"""Abgleich EA <-> Replikat fuer das Probability Grid (Build 6.20): woertliche Python-Uebertragung von GridM5, GridKerze,
GridIndex, GridRang und GridFadeOk (DEADBAND_LIVE4.mq5) gegen das Replikat (pgrid + pg_blocks.apply_rule).
Geprueft wird fuer JEDES Signal der 10 Fade-Module auf den durchgehenden Kursen 2006-2025, ob EA und Replikat
gleich entscheiden (handeln / auslassen), und ob Rang und Stop-Chance uebereinstimmen.
Aufruf: python t_port_grid.py [tf L maxpiv stopchance minreife]"""
import numpy as np, sys
import pg_data as PD
PD.use_all()
import pg_fade as PF, pg_blocks as PB, pg_rules as RU

F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]


class GridEA:
    """Zustand wie struct GridSer im EA (ein Symbol)."""
    def __init__(self, tf_min, L, maxpiv, minlegs, stopch, minreife):
        self.ts = tf_min * 60; self.L = L; self.maxpiv = maxpiv; self.minlegs = minlegs
        self.stopch = stopch; self.minreife = minreife
        self.aggOn = False; self.aggT = 0; self.aggO = 0.0; self.aggC = 0.0; self.lastM5 = 0
        self.t = []; self.bo = []; self.bc = []; self.bias = []; self.pivPx = []; self.pivBar = []; self.curPx = []; self.curBar = []
        self.legConf = []; self.legDir = []; self.legSz = []; self.legBars = []
        self.b = 0; self.cbar = -1; self.pbar = -1; self.lbar = -1; self.cpx = 0.0; self.ppx = 0.0; self.lpx = 0.0

    def kerze(self, t, o, c):                      # GridKerze
        if self.t and t <= self.t[-1]:
            return                                 # nie doppelt oder rueckwaerts
        i = len(self.t)
        self.t.append(t); self.bo.append(o); self.bc.append(c)
        if i == 0:
            self.cpx = c; self.cbar = 0; self.lpx = c; self.lbar = 0
        if i >= self.L - 1:
            up = -1.7976931348623157e308; lo = 1.7976931348623157e308
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

    def m5(self, bt, bo, bc, tn):                  # GridM5
        kb = bt - bt % self.ts
        if not self.aggOn or kb != self.aggT:
            self.aggOn = True; self.aggT = kb; self.aggO = bo
        self.aggC = bc
        kn = tn - tn % self.ts
        if kn != kb:
            self.kerze(self.aggT, self.aggO, self.aggC); self.aggOn = False
        self.lastM5 = bt

    def index(self, tEntry):                       # GridIndex
        kb = tEntry - tEntry % self.ts
        lo, hi, r = 0, len(self.t) - 1, -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if self.t[mid] < kb: r = mid; lo = mid + 1
            else: hi = mid - 1
        return r

    def rang(self, i, d, x):                       # GridRang
        lo, hi, q0 = 0, len(self.legConf) - 1, -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if self.legConf[mid] <= i: q0 = mid; lo = mid + 1
            else: hi = mid - 1
        n = 0; cnt = 0; q = q0
        while q >= 0 and n < self.maxpiv:
            if self.legDir[q] == d:
                n += 1
                if self.legSz[q] <= x: cnt += 1
            q -= 1
        return (cnt / n if n > 0 else 0.0), n

    def fade_ok(self, tEntry, d, st):              # GridFadeOk -> (ok, p_ext, chance)
        i = self.index(tEntry)
        if i < 0 or self.bias[i] == 0 or self.pivBar[i] < 0 or self.pivPx[i] <= 0.0:
            return True, np.nan, np.nan
        b = self.bias[i]
        if d == b:
            return True, np.nan, np.nan
        ext = abs(self.curPx[i] - self.pivPx[i]) / self.pivPx[i]
        pe, n = self.rang(i, b, ext)
        if n < self.minlegs:
            return True, np.nan, np.nan
        if self.minreife > 0.0 and pe < self.minreife:
            return False, pe, np.nan
        ch = np.nan
        if self.stopch > 0.0:
            xs = abs(st - self.pivPx[i]) / self.pivPx[i]
            sj = 1.0 - pe; ss = 1.0 - self.rang(i, b, xs)[0]
            ch = ss / sj if sj > 0.0 else 0.0
            if ch >= self.stopch:
                return False, pe, ch
        return True, pe, ch


def check(tf, L, mp, stopch, minreife):
    ok_all = True
    for sym in ("XAU", "NAS"):
        names = [nm for nm in F10 if PF.K.FADES[nm]["sym"] == sym]
        fis = {nm: PF.fade_info(nm) for nm in names}
        A = PD.data_all()[sym]; ny = A["ny"]; o = A["o"]; c = A["c"]
        srv = (ny + 420) * 60
        # Abfragen aller Module dieses Symbols, sortiert nach Einstiegskerze
        Q = []
        for nm in names:
            f = fis[nm]
            for q in range(len(f["ie"])):
                Q.append((int(f["ie"][q]), nm, q))
        Q.sort()
        g = GridEA(tf, L, mp, 30, stopch, minreife)
        dec = {nm: np.ones(len(fis[nm]["ie"]), bool) for nm in names}
        ch_ea = {nm: np.full(len(fis[nm]["ie"]), np.nan) for nm in names}
        k = 0
        for j in range(len(ny) - 1):
            g.m5(int(srv[j]), o[j], c[j], int(srv[j + 1]))
            while k < len(Q) and Q[k][0] == j + 1:
                _, nm, q = Q[k]; f = fis[nm]
                okq, pe, ch = g.fade_ok(int(srv[j + 1]), int(f["d"][q]), float(f["st"][q]))
                dec[nm][q] = okq; ch_ea[nm][q] = ch
                k += 1
        rule = RU.fade_filter(tf, L, mp, (lambda X: RU.c_stop_survival(stopch)(X) & RU.c_counter_mature(minreife)(X)))
        for nm in names:
            keep, live, tp, w = PB.apply_rule(fis[nm], rule)
            same = np.array_equal(keep, dec[nm])
            Xf = PB.feats(sym, fis[nm]["t_entry"], fis[nm]["d"], fis[nm]["ex"], fis[nm]["goal"], fis[nm]["st"], fis[nm]["ent"], tf, L, mp, 30)
            both = np.isfinite(ch_ea[nm]) & np.isfinite(Xf[:, 6])
            dmax = float(np.max(np.abs(ch_ea[nm][both] - Xf[both, 6]))) if both.any() else 0.0
            ok_all &= same and dmax < 1e-12
            print(f"{nm:7s} {len(keep):5d} Signale: Replikat laesst {int((~keep).sum()):4d} aus, EA {int((~dec[nm]).sum()):4d} - "
                  f"{'GLEICH' if same else 'ABWEICHUNG'}; Stop-Chance max. Abweichung {dmax:.1e}", flush=True)
            if not same:
                bad = np.nonzero(keep != dec[nm])[0][:5]
                for b_ in bad:
                    print("     ", nm, b_, np.datetime64(int(fis[nm]["t_entry"][b_]), "m"), "Replikat", keep[b_], "EA", dec[nm][b_], "Chance EA", ch_ea[nm][b_], "Replikat", Xf[b_, 6])
    return ok_all


if __name__ == "__main__":
    a = sys.argv[1:]
    tf, L, mp, sc, mr = (int(a[0]), int(a[1]), int(a[2]), float(a[3]), float(a[4])) if len(a) >= 5 else (5, 15, 1000, 0.70, 0.0)
    ok = check(tf, L, mp, sc, mr)
    print("GESAMT", "IDENTISCH" if ok else "ABWEICHUNG")
