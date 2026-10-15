"""Replikat v11 - Markt (Ereignisgitter M1), Signalzuordnung und Lauf eines Kontos."""
import numpy as np, os, pickle
import gen11 as G, eng11 as E

T_LO = int(np.datetime64("2016-09-01", "m").astype(np.int64))


class Market:
    def __init__(self, t_lo=T_LO, t_hi=None):
        D = G.data()
        syms = ("XAU", "NAS")
        if t_hi is None:
            t_hi = min(int(D["XAU"]["ny1"][-1]), int(D["NAS"]["ny1"][-1])) + 1
        self.t_lo, self.t_hi = t_lo, t_hi
        arrs = {}
        for k, s in enumerate(syms):
            ny = D[s]["ny1"]
            a = np.searchsorted(ny, t_lo); b = np.searchsorted(ny, t_hi)
            arrs[s] = (a, b)
        allt = np.union1d(D["XAU"]["ny1"][arrs["XAU"][0]:arrs["XAU"][1]], D["NAS"]["ny1"][arrs["NAS"][0]:arrs["NAS"][1]])
        self.ev_t = allt
        n = len(allt)
        self.off = np.array([arrs["XAU"][0], arrs["NAS"][0]], np.int64)
        L = max(arrs[s][1] - arrs[s][0] for s in syms)
        self.ev_i = np.full((2, n), -1, np.int64)
        self.o1 = np.zeros((2, L)); self.h1 = np.zeros((2, L)); self.l1 = np.zeros((2, L)); self.c1 = np.zeros((2, L))
        self.sp1 = np.zeros((2, L)); self.hole = np.zeros((2, L), np.bool_)
        self.ny1 = []
        for k, s in enumerate(syms):
            a, b = arrs[s]
            ny = D[s]["ny1"][a:b]
            self.ny1.append(ny)
            m = len(ny)
            self.ev_i[k, np.searchsorted(allt, ny)] = np.arange(m)
            self.o1[k, :m] = D[s]["o1"][a:b]; self.h1[k, :m] = D[s]["h1m"][a:b]; self.l1[k, :m] = D[s]["l1"][a:b]
            self.c1[k, :m] = D[s]["c1"][a:b]; self.sp1[k, :m] = D[s]["sp1"][a:b]
            dt = np.diff(ny)
            wd = (ny[:-1] // 1440 + 4) % 7
            mins = ny[:-1] % 1440
            normal_we = (wd == 5) & (dt >= 2900) & (dt <= 3010)
            holiday = (dt <= 330) | (((wd == 4) | (wd == 5)) & (dt <= 4500)) | ((dt >= 1500) & (dt <= 1740))
            hole = (dt > 90) & ~normal_we & ~holiday
            if s == "NAS":   # Luecke in der Kassasitzung (Datenloch 2023, Rollspruenge vor 2019)
                rth = (mins >= 570) & (mins < 955) & (wd >= 1) & (wd <= 5)
                hole |= rth & (dt > 10) & ((ny[:-1] // 1440) == (ny[1:] // 1440))
            self.hole[k, :m - 1] = hole
        pday = (allt + 420) // 1440
        self.days, self.day_first = np.unique(pday, return_index=True)
        self.day_first = self.day_first.astype(np.int64)
        self.ev_day = np.searchsorted(self.days, pday).astype(np.int64)
        self.ev_nymin = (allt % 1440).astype(np.int64)
        self.ev_dow = ((allt // 1440 + 4) % 7).astype(np.int64)
        self.day_dow = ((self.days + 4) % 7).astype(np.int64)
        self.bad = {0: set(G.bad_days("XAU").tolist()), 1: set(G.bad_days("NAS").tolist())}
        self.set_r21(None); self.set_nz(None); self.set_generic([])

    # ---------------------------------------------------------- Zuordnung Zeit -> Ereignis mit Kurs im Symbol
    def ev_of(self, sym, t, tol=10):
        ny = self.ny1[sym]
        i = np.searchsorted(ny, t)
        ok = i < len(ny)
        ic = np.minimum(i, len(ny) - 1)
        ok &= (ny[ic] - t) <= tol
        ev = np.searchsorted(self.ev_t, ny[ic])
        return np.where(ok, ev, -1)

    def _next(self, ev):
        return np.searchsorted(ev, np.arange(len(self.ev_t) + 1), side="left").astype(np.int64)

    def set_r21(self, r21, reg=None):
        if r21 is None:
            z = np.zeros(0, np.int64)
            self.r = dict(ev=z, sym=z, tf=z, dir=z, rd=np.zeros(0), first=z, reg=z)
        else:
            ev = np.full(len(r21["T"]), -1, np.int64)
            for k in (0, 1):
                m = r21["sym"] == k
                ev[m] = self.ev_of(k, r21["T"][m], 10)
            day = r21["T"] // 1440
            ok = ev >= 0
            ok &= np.array([int(d) not in self.bad[int(s)] for d, s in zip(day, r21["sym"])], bool)
            rg = np.ones(len(ev), np.int64) if reg is None else reg.astype(np.int64)
            o = np.lexsort((r21["tf"][ok], r21["sym"][ok], ev[ok]))
            self.r = dict(ev=ev[ok][o], sym=r21["sym"][ok][o].astype(np.int64), tf=r21["tf"][ok][o].astype(np.int64),
                          dir=r21["dir"][ok][o].astype(np.int64), rd=r21["rd"][ok][o].astype(float),
                          first=(1 - r21["folge"][ok][o]).astype(np.int64), reg=rg[ok][o])
        self.r["next"] = self._next(self.r["ev"])

    def set_nz(self, nz):
        n_ev = len(self.ev_t)
        if nz is None:
            z = np.zeros(0, np.int64)
            self.z = dict(ev=z, close=np.zeros(0), UB=np.zeros(0), vw=np.zeros(0), dist=np.zeros((0, 3)), entry=z)
            self.ev_nzeod = np.zeros(n_ev + 1, np.int64)
        else:
            D = G.data(); ny5 = D["NAS"]["ny"]
            t = ny5[nz["i5"]]; te = ny5[nz["eod_i5"]]
            ev = self.ev_of(1, t, 10); eod = self.ev_of(1, te, 10)
            ok = (ev >= 0) & np.array([int(d) not in self.bad[1] for d in nz["day"]], bool)
            self.z = dict(ev=ev[ok], close=nz["close"][ok], UB=nz["UB"][ok], vw=nz["vw"][ok],
                          dist=np.ascontiguousarray(nz["dist"][ok]), entry=nz["entry_ok"][ok].astype(np.int64))
            flag = np.zeros(n_ev + 1, np.int64)
            e2 = np.unique(eod[eod >= 0])
            flag[e2] = 1
            self.ev_nzeod = flag
        self.z["next"] = self._next(self.z["ev"])

    def set_generic(self, blocks):
        """blocks: Liste (Stromnummer, Block aus gen11, Gewicht). Filter wie FadeLive: kein Einstieg an US-Feiertagen
        bzw. wenn der Ausstieg auf einen faellt; nur Replikat: keine Einstiege an Tagen mit Datenluecken (NAS)."""
        cols = {k: [] for k in ("ev", "str", "sym", "dir", "ent", "fix", "sl", "tp", "xev", "w")}
        for s_, b, w in blocks:
            if len(b["t"]) == 0:
                continue
            sym = b["sym"].astype(np.int64)
            ev = np.full(len(b["t"]), -1, np.int64)
            for k in (0, 1):
                m = sym == k
                tol = np.where(b["fix"][m] == 1, 0, 10)
                e1 = self.ev_of(k, b["t"][m], 10)
                ev[m] = np.where((b["fix"][m] == 1) & (e1 >= 0) & (self.ev_t[np.maximum(e1, 0)] != b["t"][m]), -1, e1)
            xev = np.searchsorted(self.ev_t, b["tx"])
            d_in = b["t"] // 1440; d_out = b["tx"] // 1440
            ok = (ev >= 0) & (xev > ev)
            ok &= ~np.isin(d_in, G.FREI_ARR) & ~np.isin(d_out, G.FREI_ARR)
            ok &= np.array([int(d) not in self.bad[int(s)] for d, s in zip(d_in, sym)], bool)
            m = int(ok.sum())
            cols["ev"].append(ev[ok]); cols["str"].append(np.full(m, s_, np.int64)); cols["sym"].append(sym[ok])
            cols["dir"].append(b["dir"][ok].astype(np.int64)); cols["ent"].append(b["ent"][ok]); cols["fix"].append(b["fix"][ok].astype(np.int64))
            cols["sl"].append(b["sl"][ok]); cols["tp"].append(b["tp"][ok]); cols["xev"].append(xev[ok].astype(np.int64))
            cols["w"].append(np.full(m, float(w)) if np.ndim(w) == 0 else np.asarray(w, float)[ok])
        if cols["ev"]:
            g = {k: np.concatenate(v) for k, v in cols.items()}
        else:
            g = dict(ev=np.zeros(0, np.int64), str=np.zeros(0, np.int64), sym=np.zeros(0, np.int64), dir=np.zeros(0, np.int64),
                     ent=np.zeros(0), fix=np.zeros(0, np.int64), sl=np.zeros(0), tp=np.zeros(0), xev=np.zeros(0, np.int64), w=np.zeros(0))
        o = np.lexsort((g["sym"], g["str"], g["ev"]))
        g = {k: np.ascontiguousarray(v[o]) for k, v in g.items()}
        for k in ("ev", "str", "sym", "dir", "fix", "xev"):
            g[k] = g[k].astype(np.int64)
        g["next"] = self._next(g["ev"])
        self.g = g

    def day_index(self, date):
        return int(np.searchsorted(self.days, np.datetime64(date, "D").astype(np.int64)))

    def run(self, Pv, GP, d0, d1):
        out = np.zeros((E.MAXEV, 6)); tr = np.zeros((E.MAXTR, 5)); st = np.zeros(len(E.ST))
        r, z, g = self.r, self.z, self.g
        ne, nt = E.run_path(Pv, int(d0), int(d1), self.ev_i, self.ev_day, self.ev_nymin, self.ev_dow, self.days,
                            self.day_first, self.day_dow, self.o1, self.h1, self.l1, self.c1, self.sp1, self.hole,
                            r["ev"], r["sym"], r["tf"], r["dir"], r["rd"], r["first"], r["reg"], r["next"],
                            z["ev"], z["close"], z["UB"], z["vw"], z["dist"], z["entry"], z["next"], self.ev_nzeod,
                            g["ev"], g["str"], g["sym"], g["dir"], g["ent"], g["fix"], g["sl"], g["tp"], g["xev"], g["w"],
                            g["next"], GP, out, tr, st)
        d1c = min(d1, len(self.days) - 1)
        yrs = (self.days[d1c] - self.days[d0]) / 365.25
        return dict(st=st, ev=out[:ne].copy(), tr=tr[:nt].copy(), years=yrs)
