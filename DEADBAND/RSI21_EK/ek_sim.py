"""RSI21 Eigenkapital - Kontomotor ohne Prop-Firmen-Regeln (numba).

Konventionen wie Replikat_v6/eng10 (RSI21-Teil), damit der Abgleich t_ek_sim.py Trade fuer Trade moeglich ist:
  - Einstieg am Open der ersten M5-Kerze des Symbols ab Signalzeit T, Long zum Ask (Bid + Spread), Short zum Bid.
  - Plaetze je Symbol: A (erster) und B (zweiter, nur wenn A in dieselbe Richtung laeuft; 'second').
  - Je Kerze: erst Einstiege, dann Ausstiege (auch fuer eben eroeffnete Positionen). Reihenfolge: Stop vor Ziel in derselben
    Kerze, Stop mit Gap zum Open, Ziel zum Zielkurs; sonst Zeit-Ausstieg (Kerzen-Schluss) nach exitbars M5-Kerzen des Symbols
    oder exitdays Kalendertagen; sonst Einstand (Stop auf Einstieg + be_plus R, sobald der Kurs be_at R im Plus war, ab der
    Kerze nach dem Einstieg; wirkt ab der naechsten Kerze), optional Nachzug.
  - Swap beim Tageswechsel 17:00 NY, dreifach nach dem Mittwoch-Servertag. Kommission beim Einstieg (Gold 5 $/Lot).
  - Datenloch nach einer Kerze (kein normales Wochenende/Feiertag): neutral zum Kerzen-Schluss schliessen (nur Replikat).
  - Keine Verlust-Serie-Pause, keine Tagesgrenzen, kein Boden, keine Auszahlungen, kein Wochenend-Schluss (optional),
    keine News-/Hedging-/130-s-Regeln: Eigenkapital ohne Regeln.

Groesse: Risiko = Basis x risk % x Gewicht der Zeitebene x (Gold-Faktor), Lots auf 0,01 gerundet.
  size_mode 0 = Basis Startkapital (fest, wie eng10 ohne Pufferkurve), 1 = Equity beim Einstieg (Zinseszins),
            2 = Saldo beim Einstieg.
Margin (lev > 0): Summe der Margins <= margin_cap x Equity, sonst wird die neue Position verkleinert (oder ausgelassen).
Swap: swap_mode 0 = wie eng10 (GFT: Gold -64,47 / +23,84 $ je Lot und Tag, NAS -3 / -1,5 % p.a. vom Einstiegswert),
      1 = Zinsmodell: Long zahlt (US-Leitzins + Aufschlag), Short erhaelt (Leitzins - Aufschlag), je Jahr (RATES),
      2 = kein Swap.
"""
import os, sys
import numpy as np
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MPP = np.array([100.0, 10.0])          # Geld je Preis-Einheit und Lot (Gold 100 oz, NAS 10 $/Punkt wie GFT/eng10)
COMM = np.array([5.0, 0.0])            # Kommission je Lot (eng10)
STOPLVL = np.array([0.05, 1.5])        # Mindest-Stopabstand (eng10: 5 bzw. 150 Punkte x 0,01)
# US-Leitzins (Effective Federal Funds Rate, Jahresmittel, gerundet; 2026 geschaetzt) fuer swap_mode 1
RATES = {2005: 3.2, 2006: 5.0, 2007: 5.0, 2008: 1.9, 2009: 0.2, 2010: 0.2, 2011: 0.1, 2012: 0.1, 2013: 0.1, 2014: 0.1,
         2015: 0.1, 2016: 0.4, 2017: 1.0, 2018: 1.8, 2019: 2.2, 2020: 0.4, 2021: 0.1, 2022: 1.7, 2023: 5.0, 2024: 5.1,
         2025: 4.2, 2026: 3.6}

PN = ["start", "risk", "size_mode", "w0", "w1", "w2", "goldmult", "rr_gold", "rr_nas", "exitbars", "exitdays",
      "be_at", "be_plus", "trail_from", "trail_dist", "maxloss", "second", "first_mult", "stopmult",
      "lev_gold", "lev_nas", "margin_cap", "comm_gold", "comm_nas", "swap_mode", "swap_markup", "swap_mult",
      "we_close", "slip", "budget", "minlottol", "clock_eng10", "maxlots", "stopout", "one_per_bar",
      "tp1r", "tp1f", "dd_stop", "nslots"]
PI = {n: i for i, n in enumerate(PN)}


def params(**kw):
    c = dict(start=10000.0, risk=0.5, size_mode=1, w0=1.25, w1=1.0, w2=0.75, goldmult=0.70, rr_gold=2.64, rr_nas=2.2,
             exitbars=1152, exitdays=8.0, be_at=1.0, be_plus=0.05, trail_from=0.0, trail_dist=0.0, maxloss=2, second=1,
             first_mult=0.0, stopmult=1.0, lev_gold=20.0, lev_nas=20.0, margin_cap=0.9, comm_gold=5.0, comm_nas=0.0,
             swap_mode=1, swap_markup=2.5, swap_mult=1.0, we_close=0.0, slip=0.0, budget=0.0, minlottol=2.0,
             clock_eng10=0, maxlots=0.0, stopout=0.5, one_per_bar=0, tp1r=0.0, tp1f=0.0, dd_stop=0.0, nslots=2)
    for k in kw:
        if k not in PI:
            raise KeyError(k)
    c.update(kw)
    Pv = np.zeros(len(PN))
    for n, v in c.items():
        Pv[PI[n]] = float(v)
    return Pv


class Market:
    """Gemeinsame Zeitachse beider Symbole (wie eng10.Market) und Swap-Tabellen je Servertag."""

    def __init__(self, D):
        syms = ("XAU", "NAS")
        t0 = D["XAU"]["ny"]; t1 = D["NAS"]["ny"]
        allt = np.union1d(t0, t1)
        self.D = D
        self.ev_t = allt
        n = len(allt)
        self.ev_i = np.full((2, n), -1, dtype=np.int64)
        self.ev_i[0, np.searchsorted(allt, t0)] = np.arange(len(t0))
        self.ev_i[1, np.searchsorted(allt, t1)] = np.arange(len(t1))
        pday = (allt + 420) // 1440
        self.days, self.day_first = np.unique(pday, return_index=True)
        self.day_first = self.day_first.astype(np.int64)
        self.ev_day = np.searchsorted(self.days, pday).astype(np.int64)
        self.ev_nymin = (allt % 1440).astype(np.int64)
        self.ev_dow = (((allt // 1440) + 4) % 7).astype(np.int64)
        self.day_dow = ((self.days + 4) % 7).astype(np.int64)
        L = max(len(t0), len(t1))

        def pad(key):
            a = np.zeros((2, L))
            for k, s in enumerate(syms):
                x = D[s][key]
                a[k, :len(x)] = x
            return a
        self.o5, self.h5, self.l5, self.c5, self.sp5 = pad("o"), pad("h"), pad("l"), pad("c"), pad("sp")
        hole5 = np.zeros((2, L), np.bool_)
        for k, s in enumerate(syms):
            ny = D[s]["ny"]
            dt = np.diff(ny)
            wd = (ny[:-1] // 1440 + 4) % 7
            normal_we = (wd == 5) & (dt >= 2940) & (dt <= 3010)
            holiday = (dt <= 330) | ((wd == 4) | (wd == 5)) & (dt <= 4500) | ((dt >= 1500) & (dt <= 1740))
            hole = (dt > 90) & ~normal_we & ~holiday
            hole5[k, :len(ny) - 1] = hole
        self.hole5 = hole5
        yr = (self.days.astype("datetime64[D]").astype("datetime64[Y]").astype(int) + 1970)
        self.day_year = yr.astype(np.int64)
        self.day_rate = np.array([RATES.get(int(y), 2.0) for y in yr]) / 100.0

    def day_index(self, date):
        return int(np.searchsorted(self.days, np.datetime64(date, "D").astype(np.int64)))

    def signals(self, sg):
        """Signalliste (ek_sig.select) -> Ereignisse wie eng10.Market (nur Einstiegskandidaten werden im Motor gefiltert)."""
        syms = ("XAU", "NAS")
        rows_ev = []; rows = []
        for k in (0, 1):
            m = sg["sym"] == k
            ny = self.D[syms[k]]["ny"]
            i5 = np.searchsorted(ny, sg["T"][m])
            ok = i5 < len(ny)
            ev = np.searchsorted(self.ev_t, ny[np.minimum(i5, len(ny) - 1)])
            idx = np.nonzero(m)[0][ok]
            rows.append(np.column_stack([ev[ok], np.full(ok.sum(), k), sg["tf"][idx], sg["dir"][idx], sg["rd"][idx],
                                         1 - sg["folge"][idx]]))
        A = np.vstack(rows) if rows else np.zeros((0, 6))
        order = np.lexsort((A[:, 4], A[:, 3], A[:, 2], A[:, 1], A[:, 0]))    # wie eng10: rows.sort() ueber das Tupel
        A = A[order]
        R = dict(ev=A[:, 0].astype(np.int64), sym=A[:, 1].astype(np.int64), tf=A[:, 2].astype(np.int64),
                 dir=A[:, 3].astype(np.int64), rd=np.ascontiguousarray(A[:, 4]), first=A[:, 5].astype(np.int64))
        return R


NSL = 20           # Plaetze je Symbol q = 0..9: Index 2*q + sym (A = sym, B = 2 + sym, ...)
MAXT = 20000


@njit(cache=True)
def _core(Pv, p0, p1, seed, ev_i, ev_t, ev_day, ev_nymin, ev_dow, days, day_dow, day_rate,
          o5, h5, l5, c5, sp5, hole5, r_ev, r_sym, r_tf, r_dir, r_rd, r_first, skip,
          out_tr, out_day, st):
    np.random.seed(seed)
    mpp = np.array([100.0, 10.0])
    stoplvl = np.array([0.05, 1.5])
    start = Pv[0]; risk = Pv[1]; size_mode = int(Pv[2]); wv = np.array([Pv[3], Pv[4], Pv[5]]); gm = Pv[6]
    rr = np.array([Pv[7], Pv[8]]); exitbars = int(Pv[9]); exitdays = Pv[10]; be_at = Pv[11]; be_plus = Pv[12]
    trail_from = Pv[13]; trail_dist = Pv[14]; maxloss = int(Pv[15]); second = Pv[16] > 0.5; first_mult = Pv[17]
    stopmult = Pv[18]; lev = np.array([Pv[19], Pv[20]]); margin_cap = Pv[21]; comm = np.array([Pv[22], Pv[23]])
    swap_mode = int(Pv[24]); swap_markup = Pv[25] / 100.0; swap_mult = Pv[26]; we_close = Pv[27]; slip = Pv[28]
    budget = Pv[29]; minlottol = Pv[30]; clock_eng10 = Pv[31] > 0.5; maxlots = Pv[32]; stopout = Pv[33]
    one_per_bar = Pv[34] > 0.5; tp1r = Pv[35]; tp1f = Pv[36]; dd_stop = Pv[37]; nslots = int(Pv[38])
    if nslots < 1:
        nslots = 1
    if nslots > NSL // 2:
        nslots = NSL // 2
    if not second:
        nslots = 1

    bal = start
    p_on = np.zeros(NSL, np.bool_); p_sym = np.zeros(NSL, np.int64); p_dir = np.zeros(NSL, np.int64)
    p_entry = np.zeros(NSL); p_sl = np.zeros(NSL); p_tp = np.zeros(NSL); p_rd = np.zeros(NSL); p_lots = np.zeros(NSL)
    p_swap = np.zeros(NSL); p_comm = np.zeros(NSL); p_i5 = np.zeros(NSL, np.int64); p_t = np.zeros(NSL, np.int64)
    p_be = np.zeros(NSL, np.bool_); p_mfe = np.zeros(NSL); p_last = np.zeros(NSL); p_ev = np.zeros(NSL, np.int64)
    p_tf = np.zeros(NSL, np.int64); p_risk = np.zeros(NSL); p_first = np.zeros(NSL, np.int64); p_acc = np.zeros(NSL)
    p_t1 = np.zeros(NSL, np.bool_); p_v1 = np.zeros(NSL); p_sig = np.zeros(NSL, np.int64)
    losses = np.zeros(NSL, np.int64)
    n_tr = 0; n_day = 0
    last_c = np.zeros(2); last_sp = np.zeros(2)
    peak_eq = start; maxdd = 0.0; halted = False

    p = p0
    dayidx = ev_day[p]
    ri = 0
    nr = r_ev.shape[0]
    while ri < nr and r_ev[ri] < p:
        ri += 1
    while p < p1:
        di = ev_day[p]
        nymin = ev_nymin[p]
        nyh = nymin / 60.0
        dow = ev_dow[p]
        # ================================================= Tageswechsel (17:00 NY): Swap, Tages-Equity
        if di != dayidx:
            mult = 3.0 if day_dow[dayidx] == 3 else 1.0
            for k in range(NSL):
                if p_on[k]:
                    sw = 0.0
                    if swap_mode == 0:
                        if p_sym[k] == 0:
                            sw = (-64.47 if p_dir[k] > 0 else 23.84) * 0.01 * 100.0 * p_lots[k] * mult
                        else:
                            rate = -3.0 if p_dir[k] > 0 else -1.5
                            sw = p_entry[k] * 10.0 * p_lots[k] * (rate / 100.0 / 360.0) * mult
                    elif swap_mode == 1:
                        rt = day_rate[dayidx]
                        rate = -(rt + swap_markup) if p_dir[k] > 0 else (rt - swap_markup)
                        sw = p_entry[k] * mpp[p_sym[k]] * p_lots[k] * rate / 360.0 * mult
                    p_swap[k] += sw * swap_mult
            eqd = bal
            for k in range(NSL):
                if p_on[k]:
                    px = last_c[p_sym[k]] + (last_sp[p_sym[k]] if p_dir[k] < 0 else 0.0)
                    eqd += (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[p_sym[k]] + p_swap[k]
            if n_day < out_day.shape[0]:
                out_day[n_day, 0] = float(days[dayidx]); out_day[n_day, 1] = eqd; out_day[n_day, 2] = bal
                n_day += 1
            dayidx = di
            for k in range(NSL):
                losses[k] = 0

        # ================================================= Freitag: Wochenend-Schluss (optional, we_close = NY-Stunde)
        if we_close > 0.0 and dow == 5 and nyh >= we_close:
            for k in range(NSL):
                if not p_on[k]:
                    continue
                sy = p_sym[k]
                ii = ev_i[sy, p]
                if ii < 0:
                    continue
                px = o5[sy, ii] + (sp5[sy, ii] if p_dir[k] < 0 else 0.0)
                pnl = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[sy] + p_swap[k]
                bal += pnl
                if n_tr < MAXT:
                    out_tr[n_tr, 0] = p_ev[k]; out_tr[n_tr, 1] = p; out_tr[n_tr, 2] = sy; out_tr[n_tr, 3] = k
                    out_tr[n_tr, 4] = p_tf[k]; out_tr[n_tr, 5] = p_dir[k]; out_tr[n_tr, 6] = p_lots[k]
                    out_tr[n_tr, 7] = p_entry[k]; out_tr[n_tr, 8] = px; out_tr[n_tr, 9] = p_acc[k] + pnl
                    out_tr[n_tr, 10] = p_comm[k]; out_tr[n_tr, 11] = p_swap[k]; out_tr[n_tr, 12] = p_risk[k]
                    out_tr[n_tr, 13] = 5.0; out_tr[n_tr, 14] = 1.0 if p_be[k] else 0.0; out_tr[n_tr, 15] = p_first[k]
                    out_tr[n_tr, 16] = p_t[k]; out_tr[n_tr, 17] = p_sig[k]
                    n_tr += 1
                if pnl < 0.0:
                    losses[k] += 1
                p_on[k] = False

        # ================================================= Equity am Open (Groesse, Margin)
        eq_now = bal
        for k in range(NSL):
            if p_on[k]:
                ii = ev_i[p_sym[k], p]
                px = p_last[k]
                if ii >= 0:
                    px = o5[p_sym[k], ii] + (sp5[p_sym[k], ii] if p_dir[k] < 0 else 0.0)
                eq_now += (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[p_sym[k]] + p_swap[k]

        # ================================================= Einstiege am Open
        entries_ok = not halted
        if we_close > 0.0 and dow == 5 and nyh >= we_close - 5.0 / 60.0:
            entries_ok = False
        while ri < nr and r_ev[ri] < p:
            ri += 1
        while ri < nr and r_ev[ri] == p:
            a = ri
            ri += 1
            st[0] += 1
            if not entries_ok or skip[a]:
                continue
            if r_first[a] == 1 and first_mult <= 0.0:
                continue
            sy = r_sym[a]
            d = r_dir[a]
            if maxloss > 0:
                nl = 0
                for q in range(nslots):
                    nl += losses[2 * q + sy]
                if nl >= maxloss:
                    st[1] += 1
                    continue
            ke = -1
            kA = sy
            if not p_on[kA]:
                ke = kA
            else:
                for q in range(1, nslots):
                    kq = 2 * q + sy
                    if p_dir[kA] == d and not p_on[kq]:
                        ke = kq
                        break
            if ke < 0:
                st[2] += 1
                continue
            rd = r_rd[a] * stopmult
            if rd < stoplvl[sy] * 1.2:
                continue
            w = wv[r_tf[a]] * (gm if sy == 0 else 1.0)
            if r_first[a] == 1:
                w *= first_mult
            base = start
            if size_mode == 1:
                base = eq_now
            elif size_mode == 2:
                base = bal
            r = base * risk / 100.0 * w
            rest = 1e300
            if budget > 0.0:
                orisk = 0.0
                for q in range(NSL):
                    if p_on[q]:
                        dist = (p_entry[q] - p_sl[q]) * p_dir[q]
                        if dist > 0.0:
                            orisk += dist * p_lots[q] * mpp[p_sym[q]]
                rest = base * budget / 100.0 - orisk
                if rest < r:
                    r = rest
            if r <= 0.0:
                st[3] += 1
                continue
            if 0.01 * rd * mpp[sy] > r * minlottol:
                st[4] += 1
                continue
            lots = np.floor(r / (rd * mpp[sy]) / 0.01 + 0.5) * 0.01
            if lots < 0.01:
                lots = 0.01
            if lots * rd * mpp[sy] > rest + 1e-9:
                lots = np.floor(rest / (rd * mpp[sy]) / 0.01 + 1e-9) * 0.01
                if lots < 0.01 - 1e-12:
                    continue
            if maxlots > 0.0 and lots > maxlots:
                lots = maxlots
            lots = np.round(lots, 2)
            ii = ev_i[sy, p]
            if ii < 0:
                continue
            spr = sp5[sy, ii]
            op = o5[sy, ii]
            if lev[sy] > 0.0:
                used = 0.0
                for q in range(NSL):
                    if p_on[q]:
                        used += p_last[q] * mpp[p_sym[q]] * p_lots[q] / lev[p_sym[q]]
                frei = margin_cap * eq_now - used
                mneu = op * mpp[sy] * lots / lev[sy]
                if mneu > frei:
                    lmax = np.floor(frei * lev[sy] / (op * mpp[sy]) / 0.01 + 1e-9) * 0.01
                    st[5] += 1
                    if lmax < 0.01 - 1e-12:
                        st[6] += 1
                        continue
                    lots = np.round(lmax, 2)
            ent = op + spr if d > 0 else op
            if slip > 0.0:
                ent += d * np.random.random() * slip * spr
            k = ke
            p_on[k] = True; p_sym[k] = sy; p_dir[k] = d; p_entry[k] = ent; p_sl[k] = ent - d * rd
            p_tp[k] = ent + d * rr[sy] * rd if rr[sy] > 0.0 else 0.0
            p_rd[k] = rd; p_lots[k] = lots; p_swap[k] = 0.0; p_comm[k] = comm[sy] * lots; bal -= p_comm[k]
            p_i5[k] = ii; p_be[k] = be_at <= 0.0; p_mfe[k] = 0.0; p_last[k] = op; p_ev[k] = p; p_tf[k] = r_tf[a]
            p_risk[k] = rd * lots * mpp[sy]; p_first[k] = r_first[a]; p_acc[k] = 0.0
            p_t1[k] = tp1r <= 0.0; p_v1[k] = 0.0; p_sig[k] = a
            if tp1r > 0.0 and tp1f > 0.0:
                v1r = np.floor(lots * tp1f / 0.01 + 1e-9) * 0.01
                if v1r >= 0.01 and lots - v1r >= 0.01:
                    p_v1[k] = np.round(v1r, 2)
            if clock_eng10:
                p_t[k] = days[dayidx] * 1440 + nymin
            else:
                p_t[k] = ev_t[p]
            st[7] += 1
            eq_now -= p_comm[k]
            if one_per_bar:
                while ri < nr and r_ev[ri] == p:
                    ri += 1

        # ================================================= Ausstiege (Stop, Ziel, Zeit, Einstand, Nachzug)
        for k in range(NSL):
            if not p_on[k]:
                continue
            sy = p_sym[k]
            ii = ev_i[sy, p]
            if ii < 0:
                continue
            d = p_dir[k]
            sp = sp5[sy, ii]
            lo = l5[sy, ii]; hi = h5[sy, ii]
            if d > 0:
                hit_sl = lo <= p_sl[k]
                hit_tp = p_tp[k] > 0.0 and hi >= p_tp[k]
            else:
                hit_sl = hi + sp >= p_sl[k]
                hit_tp = p_tp[k] > 0.0 and lo + sp <= p_tp[k]
            px = 0.0
            why = 0
            if hit_sl:
                px = p_sl[k]
                if d > 0 and o5[sy, ii] < p_sl[k]:
                    px = o5[sy, ii]
                if d < 0 and o5[sy, ii] + sp > p_sl[k]:
                    px = o5[sy, ii] + sp
                why = 1
            elif hit_tp:
                px = p_tp[k]
                why = 2
            else:
                held5 = ii - p_i5[k]
                if clock_eng10:
                    tnow = days[dayidx] * 1440 + nymin
                else:
                    tnow = ev_t[p]
                if (exitbars > 0 and held5 >= exitbars) or (exitdays > 0.0 and (tnow - p_t[k]) >= exitdays * 1440):
                    px = c5[sy, ii] + (sp if d < 0 else 0.0)
                    why = 3
                else:
                    if held5 >= 1:
                        if tp1r > 0.0 and not p_t1[k]:
                            lvl = p_entry[k] + d * tp1r * p_rd[k]
                            if (hi >= lvl) if d > 0 else (lo + sp <= lvl):
                                p_t1[k] = True
                                if p_v1[k] > 0.0:
                                    frac = p_v1[k] / p_lots[k]
                                    pnl1 = (lvl - p_entry[k]) * d * p_v1[k] * mpp[sy] + p_swap[k] * frac
                                    bal += pnl1
                                    p_acc[k] += pnl1
                                    p_swap[k] *= (1.0 - frac)
                                    p_lots[k] = np.round(p_lots[k] - p_v1[k], 2)
                                    p_v1[k] = 0.0
                        if not p_be[k]:
                            lvl = p_entry[k] + d * be_at * p_rd[k]
                            if (hi >= lvl) if d > 0 else (lo + sp <= lvl):
                                cand = p_entry[k] + d * be_plus * p_rd[k]
                                if (cand - p_sl[k]) * d > 0.0:
                                    p_sl[k] = cand
                                p_be[k] = True
                        if trail_from > 0.0:
                            fav = ((hi - p_entry[k]) / p_rd[k]) if d > 0 else ((p_entry[k] - (lo + sp)) / p_rd[k])
                            if fav > p_mfe[k]:
                                p_mfe[k] = fav
                            if p_mfe[k] >= trail_from:
                                cand = p_entry[k] + d * (p_mfe[k] - trail_dist) * p_rd[k]
                                if (cand - p_sl[k]) * d > 0.0:
                                    p_sl[k] = cand
            if why == 0 and hole5[sy, ii]:
                px = c5[sy, ii] + (sp if d < 0 else 0.0)
                why = 4
            if why > 0:
                pnl = (px - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k]
                bal += pnl
                if n_tr < MAXT:
                    out_tr[n_tr, 0] = p_ev[k]; out_tr[n_tr, 1] = p; out_tr[n_tr, 2] = sy; out_tr[n_tr, 3] = k
                    out_tr[n_tr, 4] = p_tf[k]; out_tr[n_tr, 5] = d; out_tr[n_tr, 6] = p_lots[k]
                    out_tr[n_tr, 7] = p_entry[k]; out_tr[n_tr, 8] = px; out_tr[n_tr, 9] = p_acc[k] + pnl
                    out_tr[n_tr, 10] = p_comm[k]; out_tr[n_tr, 11] = p_swap[k]; out_tr[n_tr, 12] = p_risk[k]
                    out_tr[n_tr, 13] = float(why); out_tr[n_tr, 14] = 1.0 if p_be[k] else 0.0; out_tr[n_tr, 15] = p_first[k]
                    out_tr[n_tr, 16] = p_t[k]; out_tr[n_tr, 17] = p_sig[k]
                    n_tr += 1
                if pnl < 0.0:
                    losses[k] += 1
                p_on[k] = False
            else:
                p_last[k] = c5[sy, ii]
        for s in range(2):
            ii = ev_i[s, p]
            if ii >= 0:
                last_c[s] = c5[s, ii]; last_sp[s] = sp5[s, ii]
        # ================================================= Equity zum Kerzen-Schluss: Rueckgang, Stop-out
        eqc = bal
        used = 0.0
        nopen = 0
        for k in range(NSL):
            if p_on[k]:
                nopen += 1
                px = last_c[p_sym[k]] + (last_sp[p_sym[k]] if p_dir[k] < 0 else 0.0)
                eqc += (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[p_sym[k]] + p_swap[k]
                if lev[p_sym[k]] > 0.0:
                    used += last_c[p_sym[k]] * mpp[p_sym[k]] * p_lots[k] / lev[p_sym[k]]
        if eqc > peak_eq:
            peak_eq = eqc
        if peak_eq > 0.0:
            dd = 1.0 - eqc / peak_eq
            if dd > maxdd:
                maxdd = dd
            if dd_stop > 0.0 and dd >= dd_stop / 100.0 and not halted:
                halted = True
                st[9] += 1
        if (nopen > 0 and stopout > 0.0 and used > 0.0 and eqc < stopout * used) or eqc <= 0.0:
            st[8] += 1
            for k in range(NSL):
                if not p_on[k]:
                    continue
                sy = p_sym[k]
                px = last_c[sy] + (last_sp[sy] if p_dir[k] < 0 else 0.0)
                pnl = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[sy] + p_swap[k]
                bal += pnl
                if n_tr < MAXT:
                    out_tr[n_tr, 0] = p_ev[k]; out_tr[n_tr, 1] = p; out_tr[n_tr, 2] = sy; out_tr[n_tr, 3] = k
                    out_tr[n_tr, 4] = p_tf[k]; out_tr[n_tr, 5] = p_dir[k]; out_tr[n_tr, 6] = p_lots[k]
                    out_tr[n_tr, 7] = p_entry[k]; out_tr[n_tr, 8] = px; out_tr[n_tr, 9] = p_acc[k] + pnl
                    out_tr[n_tr, 10] = p_comm[k]; out_tr[n_tr, 11] = p_swap[k]; out_tr[n_tr, 12] = p_risk[k]
                    out_tr[n_tr, 13] = 6.0; out_tr[n_tr, 14] = 1.0 if p_be[k] else 0.0; out_tr[n_tr, 15] = p_first[k]
                    out_tr[n_tr, 16] = p_t[k]; out_tr[n_tr, 17] = p_sig[k]
                    n_tr += 1
                p_on[k] = False
            if bal <= 0.0:
                halted = True
        p += 1
    # Ende: offene Positionen zum letzten Kurs bewerten (nicht schliessen), letzte Tages-Equity
    eqd = bal
    for k in range(NSL):
        if p_on[k]:
            px = last_c[p_sym[k]] + (last_sp[p_sym[k]] if p_dir[k] < 0 else 0.0)
            eqd += (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[p_sym[k]] + p_swap[k]
    if n_day < out_day.shape[0]:
        out_day[n_day, 0] = float(days[dayidx]); out_day[n_day, 1] = eqd; out_day[n_day, 2] = bal
        n_day += 1
    st[10] = maxdd
    return n_tr, n_day


ST = ["sig_seen", "sig_maxloss", "sig_slot", "sig_budget", "sig_minlot", "margin_cut", "margin_skip", "entries",
      "stopout", "dd_halt", "maxdd_bar"]
TR = ["ev_in", "ev_out", "sym", "slot", "tf", "dir", "lots", "entry", "exit", "pnl", "comm", "swap", "risk", "why",
      "be", "first", "t_in", "sig"]


def run(mk, R, Pv, d0="2006-01-01", d1="2026-12-31", seed=0, skip=None):
    """Ein Konto von d0 bis d1 (Servertage). R = mk.signals(select(...)). Rueckgabe: Trades, Tages-Equity, Zaehler."""
    i0 = mk.day_index(d0); i1 = mk.day_index(d1)
    p0 = int(mk.day_first[i0]) if i0 < len(mk.days) else len(mk.ev_t)
    p1 = int(mk.day_first[i1]) if i1 < len(mk.days) else len(mk.ev_t)
    if skip is None:
        skip = np.zeros(len(R["ev"]), np.bool_)
    out_tr = np.zeros((MAXT, len(TR)))
    out_day = np.zeros((len(mk.days) + 2, 3))
    st = np.zeros(len(ST))
    n_tr, n_day = _core(Pv, p0, p1, seed, mk.ev_i, mk.ev_t, mk.ev_day, mk.ev_nymin, mk.ev_dow, mk.days, mk.day_dow,
                        mk.day_rate, mk.o5, mk.h5, mk.l5, mk.c5, mk.sp5, mk.hole5,
                        R["ev"], R["sym"], R["tf"], R["dir"], R["rd"], R["first"], skip, out_tr, out_day, st)
    return dict(tr=out_tr[:n_tr].copy(), day=out_day[:n_day].copy(), st=st, start=Pv[PI["start"]])
