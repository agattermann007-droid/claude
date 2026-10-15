"""Replikat v11 - Kontomotor auf M1 (Nachfolger von eng6, Replikat v6).

Ein Ereignis = eine NY-Minute mit Kursen (Vereinigung beider Symbole). Je Minute in dieser Reihenfolge:
Tageswechsel 17:00 NY (Swap, gueltige Tage, Auszahlung) -> Freitag-Schluss -> Wiederaufnahme RSI21 -> Noise-Pruefung
-> Einstiege RSI21, Noise, generische Stroeme (Fades, Spike, LW, XA, TD, SR, neue) -> Firmenregeln und EA-Bremsen am
schlechtesten Kurs der Minute -> Stop/Ziel/Zeit/Einstand -> Datenloch -> Swap-Vorsorge -> Abschluss-Ernte ->
Gewinn-Ernte -> Reife/Auszahlung -> Serien-Stopp.

Konventionen (pessimistisch): Long zum Ask; Stop vor Ziel in derselben Minute; Ziel erst ab tpdelay Minuten nach dem
Einstieg (Fades: naechste M5-Kerze, SR: 130 s -> 4. Minute); Schlupf je slip x Spread auf Markt-Einstiege, Stop- und
Zeit-Ausstiege; Equity-Hoch am besten Kurs, Boden/Floating/Tagesregel am schlechtesten Kurs der Minute.
Plaetze: 0-1 RSI21 A (XAU, NAS), 2-3 RSI21 B, 4-6 Noise-Teile (NAS), ab G0 = 7 generisch (2 je Strom: XAU, NAS).
"""
import numpy as np
from numba import njit

NG = 24
R0 = 0; RB0 = 2; NZ0 = 4; NZ1 = 7; G0 = 7
NSLOT = G0 + 2 * NG
GPN = ["on", "risk", "maxtrades", "budget", "ripeclose", "harv", "usefak", "tpdelay", "minsprd", "minbuf", "gsfree",
       "maxloss", "fixstop", "noser"]          # v12: noser 1 = Trades des Stroms zaehlen nicht fuer den Serien-Stopp
GPI = {n: i for i, n in enumerate(GPN)}
G_NOSER = GPI["noser"]

PN = ["start", "fee", "maxlosspct", "rulefloat", "ruleday", "validpct", "needvalid", "cycledays", "minpayout", "split",
      "paycap", "paycapn", "paydelay", "rebuydelay",
      "floatstop", "floatgestuft", "floatminsaldo", "daystop", "brakeslip", "tagesrefeq",
      "ddfull", "ddmin", "ddfmin", "belowstart", "gesamtbudget", "idea_cap", "lev", "idea_margin", "minlottol",
      "r21_on", "r21_risk", "r21_goldmult", "r21_w0", "r21_w1", "r21_w2", "r21_budget", "r21_rr_nas", "r21_rr_gold",
      "r21_exitbars", "r21_exitdays", "r21_maxloss", "r21_second", "r21_ripeclose", "r21_ber", "r21_beplus",
      "r21_gsfrom", "r21_gsregime",
      "nz_on", "nz_risk", "nz_parts", "nz_ripeclose", "nz_ber", "nz_beplus",
      "ge_on", "ge_minr", "ge_auf", "ge_rueck",
      "we_on", "we_close", "we_reentry", "we_reif", "we_stopmaxr", "we_spreadr",
      "slip", "bank_on", "bank_minr", "bank_from", "bank_to", "bank_margin", "bank_mods", "bank_last", "bank_prof",
      "cool_n", "cool_days", "valid_guard", "swap_guard", "float_losers", "rule_losers", "minhold",
      "kons_pct", "kons_cap", "gen_off", "r21_regfak"]
PI = {n: i for i, n in enumerate(PN)}

DEF = dict(start=10000.0, fee=148.5, maxlosspct=6.0, rulefloat=1.0, ruleday=3.0, validpct=0.505, needvalid=5,
           cycledays=14, minpayout=105.0, split=0.80, paycap=6.0, paycapn=2, paydelay=1, rebuydelay=1,
           floatstop=0.80, floatgestuft=1, floatminsaldo=1, daystop=2.4, brakeslip=0.05, tagesrefeq=1,
           ddfull=3.5, ddmin=1.25, ddfmin=0.1, belowstart=0.95, gesamtbudget=0.9, idea_cap=0.9, lev=20.0,
           idea_margin=70.0, minlottol=2.0,
           r21_on=1, r21_risk=0.50, r21_goldmult=0.70, r21_w0=1.25, r21_w1=1.0, r21_w2=0.75, r21_budget=1.2,
           r21_rr_nas=2.2, r21_rr_gold=2.64, r21_exitbars=5760, r21_exitdays=8, r21_maxloss=2, r21_second=1,
           r21_ripeclose=1, r21_ber=1.0, r21_beplus=0.05, r21_gsfrom=13.0, r21_gsregime=1,
           nz_on=1, nz_risk=0.45, nz_parts=3, nz_ripeclose=1, nz_ber=0.5, nz_beplus=0.05,
           ge_on=1, ge_minr=1.0, ge_auf=0.05, ge_rueck=0.0,
           we_on=1, we_close=16.75, we_reentry=1, we_reif=1, we_stopmaxr=2.0, we_spreadr=0.15,
           slip=0.25, bank_on=1, bank_minr=0.3, bank_from=0.0, bank_to=17.0, bank_margin=0.05, bank_mods=15,
           bank_last=5, bank_prof=0.0, cool_n=3, cool_days=0, valid_guard=1, swap_guard=0.80, float_losers=1,
           rule_losers=1, minhold=3, kons_pct=0.0, kons_cap=0.0, gen_off=0,
           r21_regfak=1.0)


def params(**kw):
    c = dict(DEF)
    for k in kw:
        if k not in PI:
            raise KeyError(k)
    c.update(kw)
    Pv = np.zeros(len(PN))
    for n, v in c.items():
        Pv[PI[n]] = float(v)
    return Pv


def gparams(streams):
    GP = np.zeros((NG, len(GPN)))
    for s in range(NG):
        GP[s, GPI["usefak"]] = 1.0; GP[s, GPI["ripeclose"]] = 1.0; GP[s, GPI["tpdelay"]] = 5.0
    for s, kw in enumerate(streams):
        for n, v in kw.items():
            GP[s, GPI[n]] = float(v)
    return GP


ST = ["npay", "sumpay", "nbust", "floor_b", "float_b", "day_b", "ntr", "wins", "pnl", "valid_days", "trade_days",
      "brake_f", "brake_d", "we_close", "we_re", "bank", "ge", "cool", "first_pay", "end_bal", "end_eq", "cyc_days",
      "gs_block", "ripe_n", "lim_valid", "lim_profit", "lim_ten", "maxstreak", "hole_close", "swapg", "end_mode",
      "kons_wait", "bestday"]
SI = {n: i for i, n in enumerate(ST)}
MAXEV = 400
MAXTR = 20000

# Spalten Positions-Arrays
F_ENT, F_SL, F_TP, F_RD, F_REF, F_LOTS, F_SWAP, F_MFE, F_COMM, F_ACC, F_LAST, F_W = range(12)
NFC = 12
I_ON, I_SYM, I_DIR, I_I1, I_TMIN, I_XEV, I_BE, I_TF, I_STR, I_FIX = range(10)
NIC = 10


@njit(cache=True)
def _ddf(eq, peak, floor_dist, start, ddfull, ddmin, ddfmin):
    if ddfull <= 0.0:
        return 1.0
    buf = (eq - (peak - floor_dist)) / start * 100.0
    if buf >= ddfull:
        return 1.0
    if buf <= ddmin:
        return ddfmin
    return ddfmin + (1.0 - ddfmin) * (buf - ddmin) / (ddfull - ddmin)


@njit(cache=True)
def _open_risk(PFa, PIa, mpp):
    r_all = 0.0
    for q in range(PIa.shape[0]):
        if PIa[q, I_ON] == 1:
            dist = (PFa[q, F_ENT] - PFa[q, F_SL]) * PIa[q, I_DIR]
            if dist > 0.0:
                r_all += dist * PFa[q, F_LOTS] * mpp[PIa[q, I_SYM]]
    return r_all


@njit(cache=True)
def _risk_of(PFa, PIa, mpp, q):
    dist = (PFa[q, F_ENT] - PFa[q, F_SL]) * PIa[q, I_DIR]
    if dist > 0.0:
        return dist * PFa[q, F_LOTS] * mpp[PIa[q, I_SYM]]
    return 0.0


@njit(cache=True)
def _idea_risk(PFa, PIa, mpp, sy, d):
    r = 0.0
    for q in range(PIa.shape[0]):
        if PIa[q, I_ON] == 1 and PIa[q, I_SYM] == sy and PIa[q, I_DIR] == d:
            r += _risk_of(PFa, PIa, mpp, q)
    return r


@njit(cache=True)
def _worst_eq(PFa, PIa, mpp, bal):
    """Equity, wenn alle offenen Positionen an ihrem Stop schliessen (BodenLuft)."""
    w = bal
    for q in range(PIa.shape[0]):
        if PIa[q, I_ON] == 1:
            w += (PFa[q, F_SL] - PFa[q, F_ENT]) * PIa[q, I_DIR] * PFa[q, F_LOTS] * mpp[PIa[q, I_SYM]] + PFa[q, F_SWAP]
    return w


@njit(cache=True)
def _margin_ok(PFa, PIa, mpp, lev, idea_margin, sy, d, lots, px, eq):
    if lev <= 0.0:
        return True
    used = 0.0; idea = 0.0
    for q in range(PIa.shape[0]):
        if PIa[q, I_ON] == 1:
            m = PFa[q, F_LAST] * mpp[PIa[q, I_SYM]] * PFa[q, F_LOTS] / lev
            used += m
            if PIa[q, I_SYM] == sy and PIa[q, I_DIR] == d:
                idea += m
    mneu = px * mpp[sy] * lots / lev
    if mneu > (eq - used) * 0.8:
        return False
    if idea_margin > 0.0 and idea + mneu > eq * idea_margin / 100.0:
        return False
    return True


@njit(cache=True)
def _lots(r, rd, mppv, rest, minlottol):
    if r <= 0.0 or rd <= 0.0:
        return 0.0
    if 0.01 * rd * mppv > r * minlottol:
        return 0.0
    lots = np.floor(r / (rd * mppv) / 0.01 + 0.5) * 0.01
    if lots < 0.01:
        lots = 0.01
    if lots * rd * mppv > rest + 1e-9:
        lots = np.floor(rest / (rd * mppv) / 0.01 + 1e-9) * 0.01
        if lots < 0.01 - 1e-12:
            return 0.0
    return np.round(lots, 2)


@njit(cache=True)
def _hedge(PIa, Won, Wdir, sy, d, k_self):
    for q in range(PIa.shape[0]):
        if PIa[q, I_ON] == 1 and PIa[q, I_SYM] == sy and PIa[q, I_DIR] != d:
            return True
    for q in range(NZ0):
        if Won[q] and q != k_self and (q % 2) == sy and Wdir[q] != d:
            return True
    return False


@njit(cache=True)
def run_path(Pv, d0, d1, ev_i, ev_day, ev_nymin, ev_dow, days, day_first, day_dow,
             o1, h1, l1, c1, sp1, hole,
             r_ev, r_sym, r_tf, r_dir, r_rd, r_first, r_reg, r_next,
             z_ev, z_close, z_UB, z_vw, z_dist, z_entry, z_next, ev_nzeod,
             g_ev, g_str, g_sym, g_dir, g_ent, g_fix, g_sl, g_tp, g_xev, g_w, g_next, GP,
             out_ev, out_tr, st):
    n_ev = ev_day.shape[0]
    nd = days.shape[0]
    mpp = np.array([100.0, 10.0])
    comm = np.array([5.0, 0.0])
    stoplvl = np.array([0.05, 1.5])
    start = Pv[0]; fee = Pv[1]; maxlosspct = Pv[2]; rulefloat = Pv[3]; ruleday = Pv[4]
    validpct = Pv[5]; needvalid = int(Pv[6]); cycledays = int(Pv[7])
    minpayout = Pv[8]; split = Pv[9]; paycap = start * Pv[10] / 100.0; paycapn = int(Pv[11])
    paydelay = int(Pv[12]); rebuydelay = int(Pv[13])
    floatstop = Pv[14]; floatgestuft = Pv[15] > 0.5; floatminsaldo = Pv[16] > 0.5; daystop = Pv[17]
    brakeslip = Pv[18]; tagesrefeq = Pv[19] > 0.5
    ddfull = Pv[20]; ddmin = Pv[21]; ddfmin = Pv[22]; belowstart = Pv[23]; gesamtbudget = Pv[24]
    idea_cap = Pv[25]; lev = Pv[26]; idea_margin = Pv[27]; minlottol = Pv[28]
    r21_on = Pv[29] > 0.5; r21_risk = Pv[30]; r21_gm = Pv[31]; r21_w = np.array([Pv[32], Pv[33], Pv[34]])
    r21_budget = Pv[35]; r21_rr = np.array([Pv[37], Pv[36]]); r21_exitbars = int(Pv[38]); r21_exitdays = Pv[39]
    r21_maxloss = int(Pv[40]); r21_second = Pv[41] > 0.5; r21_ripeclose = Pv[42] > 0.5; r21_ber = Pv[43]; r21_beplus = Pv[44]
    r21_gsfrom = Pv[45]; r21_gsregime = Pv[46] > 0.5
    nz_on = Pv[47] > 0.5; nz_risk = Pv[48]; nz_parts = int(Pv[49]); nz_ripeclose = Pv[50] > 0.5; nz_ber = Pv[51]; nz_beplus = Pv[52]
    ge_on = Pv[53] > 0.5; ge_minr = Pv[54]; ge_auf = Pv[55]; ge_rueck = Pv[56]
    we_on = Pv[57] > 0.5; we_close = Pv[58]; we_reentry = Pv[59] > 0.5; we_reif = Pv[60] > 0.5
    we_stopmaxr = Pv[61]; we_spreadr = Pv[62]
    slip = Pv[63]
    bank_on = Pv[64] > 0.5; bank_minr = Pv[65]; bank_from = Pv[66]; bank_to = Pv[67]; bank_margin = Pv[68]
    bank_mods = int(Pv[69]); bank_last = int(Pv[70]); bank_prof = Pv[71]
    cool_n = int(Pv[72]); cool_days = int(Pv[73]); valid_guard = Pv[74] > 0.5; swap_guard = Pv[75]
    float_losers = Pv[76] > 0.5; rule_losers = Pv[77] > 0.5; minhold = int(Pv[78])
    kons_pct = Pv[79]; kons_cap = Pv[80]; gen_off = Pv[81] > 0.5
    r21_regfak = Pv[82]                     # v12: RSI21 x Faktor, solange die Fades nicht live sind (EA RegimeGroesse)

    floor_dist = start * maxlosspct / 100.0
    needday = start * validpct / 100.0
    minprofit = minpayout / split

    bal = start; peak = start
    valid_days = 0; trade_days = 0; cyc_start = -1; npay_acc = 0
    mode = 0; wait = 0
    n_out = 0; n_tr = 0
    PFa = np.zeros((NSLOT, NFC)); PIa = np.zeros((NSLOT, NIC), np.int64)
    Won = np.zeros(NZ0, np.bool_); Wdir = np.zeros(NZ0, np.int64); Wsl = np.zeros(NZ0); Wtp = np.zeros(NZ0)
    Wlots = np.zeros(NZ0); Wrd = np.zeros(NZ0); Wref = np.zeros(NZ0); Wmfe = np.zeros(NZ0); Wbe = np.zeros(NZ0, np.int64)
    Wi1 = np.zeros(NZ0, np.int64); Wtmin = np.zeros(NZ0, np.int64); Wfri = np.zeros(NZ0, np.int64)
    pw = np.zeros(NSLOT)
    g_trades = np.zeros(2 * NG, np.int64); losses = np.zeros(NSLOT, np.int64)
    day_real = 0.0; day_had = False; day_start_bal = start; day_ref_plus = 0.0; day_locked = False
    cur_streak = 0; max_streak = 0
    cool_until = -1; cons_loss = 0
    v5_day = -1; pr_day = -1; pr_ok = False
    tr_done = 0; nz_pid = -1.0; nz_sum = 0.0; nz_pend = False
    first_pay = -1.0
    # Konsistenz (GOAT): realisiert je Tag im Zyklus
    best_day = 0.0

    if d0 >= nd:
        return 0, 0
    p = day_first[d0]
    end_ev = n_ev
    if d1 < nd:
        end_ev = day_first[d1]
    dayidx = ev_day[p]
    d_start = days[dayidx]
    ri = r_next[p]; zi = z_next[p]; gi = g_next[p]
    nr = r_ev.shape[0]; nzc = z_ev.shape[0]; ngs = g_ev.shape[0]

    while p < end_ev:
        di = ev_day[p]
        nymin = ev_nymin[p]
        nyh = nymin / 60.0
        dow = ev_dow[p]
        # ================================================= Tageswechsel (17:00 NY)
        if di != dayidx:
            mult = 3.0 if day_dow[dayidx] == 3 else 1.0
            for k in range(NSLOT):
                if PIa[k, I_ON] == 1:
                    if PIa[k, I_SYM] == 0:
                        sw = (-64.47 if PIa[k, I_DIR] > 0 else 23.84) * PFa[k, F_LOTS] * mult
                    else:
                        rate = -3.0 if PIa[k, I_DIR] > 0 else -1.5
                        sw = PFa[k, F_ENT] * 10.0 * PFa[k, F_LOTS] * (rate / 100.0 / 360.0) * mult
                    PFa[k, F_SWAP] += sw
            if day_had:
                trade_days += 1
                st[10] += 1
                if day_real >= needday:
                    valid_days += 1
                    st[9] += 1
                if day_real > best_day:
                    best_day = day_real
            if mode == 2 or mode == 3:
                wait -= 1
                if wait <= 0:
                    if mode == 2:
                        amt = bal - start
                        if npay_acc < paycapn and amt > paycap:
                            amt = paycap
                        if amt < 0.0:
                            amt = 0.0
                        bal -= amt
                        peak = bal
                        if n_out < MAXEV:
                            out_ev[n_out, 0] = 1.0; out_ev[n_out, 1] = float(days[di]); out_ev[n_out, 2] = amt
                            n_out += 1
                        st[0] += 1; st[1] += amt
                        if first_pay < 0:
                            first_pay = float(days[di] - d_start)
                        if cyc_start >= 0:
                            st[21] += float(days[di] - cyc_start)
                        npay_acc += 1
                    else:
                        bal = start; peak = start; npay_acc = 0
                        if n_out < MAXEV:
                            out_ev[n_out, 0] = 3.0; out_ev[n_out, 1] = float(days[di]); out_ev[n_out, 2] = fee
                            n_out += 1
                    valid_days = 0; trade_days = 0; cyc_start = -1
                    v5_day = -1; pr_day = -1; pr_ok = False; best_day = 0.0
                    mode = 0
            dayidx = di
            day_start_bal = bal
            flt0 = 0.0
            for k in range(NSLOT):
                if PIa[k, I_ON] == 1:
                    flt0 += (PFa[k, F_LAST] - PFa[k, F_ENT]) * PIa[k, I_DIR] * PFa[k, F_LOTS] * mpp[PIa[k, I_SYM]] + PFa[k, F_SWAP]
            day_ref_plus = flt0 if (tagesrefeq and flt0 > 0.0) else 0.0
            day_real = 0.0; day_had = False; day_locked = False
            for q in range(2 * NG):
                g_trades[q] = 0
            for k in range(NSLOT):
                losses[k] = 0

        # ================================================= Freitag: Wochenend-Schluss
        we_now = we_on and dow == 5 and nyh >= we_close
        if we_now:
            for k in range(NSLOT):
                if PIa[k, I_ON] == 0:
                    continue
                sy = PIa[k, I_SYM]
                ii = ev_i[sy, p]
                if ii < 0:
                    continue
                d = PIa[k, I_DIR]
                px = o1[sy, ii] + (sp1[sy, ii] if d < 0 else 0.0) - d * slip * sp1[sy, ii]
                pnl = (px - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP]
                bal += pnl; day_real += pnl - PFa[k, F_COMM]; day_had = True
                st[8] += pnl; st[13] += 1
                tot = PFa[k, F_ACC] + pnl - PFa[k, F_COMM]
                if we_reentry and k < NZ0 and (mode == 0 or we_reif) and PFa[k, F_RD] > 0.0:
                    Won[k] = True; Wdir[k] = d; Wsl[k] = PFa[k, F_SL]; Wtp[k] = PFa[k, F_TP]; Wlots[k] = PFa[k, F_LOTS]
                    Wrd[k] = PFa[k, F_RD]; Wref[k] = PFa[k, F_REF]; Wmfe[k] = PFa[k, F_MFE]; Wbe[k] = PIa[k, I_BE]
                    Wi1[k] = PIa[k, I_I1]; Wtmin[k] = PIa[k, I_TMIN]; Wfri[k] = days[dayidx]
                PIa[k, I_ON] = 0
                if n_tr < MAXTR:
                    out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                    out_tr[n_tr, 4] = float(PIa[k, I_STR]); n_tr += 1
                if pnl < 0.0:
                    losses[k] += 1
        for k in range(NZ0):
            if Won[k]:
                seit = days[dayidx] - Wfri[k]
                if (dow >= 2 and dow <= 4 and seit >= 3) or seit >= 6:
                    Won[k] = False

        # ================================================= Einstiege erlaubt?
        entries_ok = (mode == 0) and (not day_locked) and not (we_on and dow == 5 and nyh >= we_close - 5.0 / 60.0)
        if cool_until >= 0 and days[dayidx] <= cool_until:
            entries_ok = False
        if kons_pct > 0.0 and kons_cap > 0.0 and day_real >= start * kons_cap / 100.0:
            entries_ok = False
        gs = valid_guard and cyc_start >= 0 and valid_days < needvalid and day_real >= needday
        # ---- Sonntag-/Montag-Wiederaufnahme (RSI21)
        if we_on and we_reentry and (dow == 0 and nyh >= 18.0 or dow == 1):
            for k in range(NZ0):
                if not Won[k]:
                    continue
                if mode == 2 or (mode != 0 and not we_reif) or (mode != 0 and r21_ripeclose):
                    Won[k] = False
                    continue
                if day_locked or PIa[k, I_ON] == 1:
                    continue
                sy = k % 2
                ii = ev_i[sy, p]
                if ii < 0:
                    continue
                spr = sp1[sy, ii]
                if we_spreadr > 0.0 and spr > we_spreadr * Wrd[k] and dow == 0 and nyh < 19.0:
                    continue
                d = Wdir[k]
                if _hedge(PIa, Won, Wdir, sy, d, k):
                    continue
                bid = o1[sy, ii]; ask = bid + spr
                ent = (ask if d > 0 else bid) + d * slip * spr
                chk = bid if d > 0 else ask
                if (d > 0 and chk <= Wsl[k]) or (d < 0 and chk >= Wsl[k]):
                    Won[k] = False
                    continue
                if Wtp[k] > 0.0 and ((d > 0 and chk >= Wtp[k]) or (d < 0 and chk <= Wtp[k])):
                    Won[k] = False
                    continue
                nsl = Wsl[k]
                if we_stopmaxr > 0.0:
                    tight = ent - d * we_stopmaxr * Wrd[k]
                    if (d > 0 and tight > nsl) or (d < 0 and tight < nsl):
                        nsl = tight
                PIa[k, I_ON] = 1; PIa[k, I_SYM] = sy; PIa[k, I_DIR] = d; PFa[k, F_ENT] = ent; PFa[k, F_SL] = nsl
                PFa[k, F_TP] = Wtp[k]; PFa[k, F_RD] = Wrd[k]; PFa[k, F_REF] = Wref[k]; PFa[k, F_LOTS] = Wlots[k]
                PFa[k, F_SWAP] = 0.0; PFa[k, F_MFE] = Wmfe[k]; PIa[k, I_BE] = 1; PIa[k, I_I1] = Wi1[k]
                PIa[k, I_TMIN] = Wtmin[k]; PFa[k, F_COMM] = comm[sy] * Wlots[k]; bal -= PFa[k, F_COMM]
                PFa[k, F_ACC] = 0.0; PFa[k, F_LAST] = bid; PIa[k, I_XEV] = -1; PIa[k, I_STR] = -1; PIa[k, I_FIX] = 0
                Won[k] = False
                st[14] += 1

        # ---- Noise: Pruefung (Ausstieg unter dem Band), Tagesende 15:55, Freitag
        while zi < nzc and z_ev[zi] < p:
            zi += 1
        zcur = -1
        if zi < nzc and z_ev[zi] == p:
            zcur = zi
        nz_open = 0
        for k in range(NZ0, NZ0 + nz_parts):
            if PIa[k, I_ON] == 1:
                nz_open += 1
        if nz_open > 0 and (ev_nzeod[p] == 1 or (zcur >= 0 and z_close[zcur] < z_UB[zcur]) or we_now):
            ii = ev_i[1, p]
            if ii >= 0:
                for k in range(NZ0, NZ0 + nz_parts):
                    if PIa[k, I_ON] == 0:
                        continue
                    px = o1[1, ii] - slip * sp1[1, ii]
                    pnl = (px - PFa[k, F_ENT]) * PFa[k, F_LOTS] * 10.0 + PFa[k, F_SWAP]
                    bal += pnl; day_real += pnl; day_had = True; st[8] += pnl
                    if pnl < 0.0:
                        losses[k] += 1
                    if n_tr < MAXTR:
                        out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = pnl; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                        out_tr[n_tr, 4] = -2.0; n_tr += 1
                    PIa[k, I_ON] = 0

        # ---- Groessenfaktor (Equity am Open)
        eq_now = bal
        for k in range(NSLOT):
            if PIa[k, I_ON] == 1:
                ii = ev_i[PIa[k, I_SYM], p]
                px = PFa[k, F_LAST]
                if ii >= 0:
                    px = o1[PIa[k, I_SYM], ii] + (sp1[PIa[k, I_SYM], ii] if PIa[k, I_DIR] < 0 else 0.0)
                eq_now += (px - PFa[k, F_ENT]) * PIa[k, I_DIR] * PFa[k, F_LOTS] * mpp[PIa[k, I_SYM]] + PFa[k, F_SWAP]
        fak = _ddf(eq_now, peak, floor_dist, start, ddfull, ddmin, ddfmin)
        if eq_now < start:
            fak *= belowstart
        buf_now = (eq_now - (peak - floor_dist)) / start * 100.0

        # ---- RSI21
        while ri < nr and r_ev[ri] < p:
            ri += 1
        while ri < nr and r_ev[ri] == p:
            a = ri
            ri += 1
            if not r21_on or not entries_ok:
                continue
            if r_first[a] == 1:
                continue
            if gs and (nyh < r21_gsfrom or (r21_gsregime and r_reg[a] == 0)):
                st[22] += 1
                continue
            sy = r_sym[a]; d = r_dir[a]
            if r21_maxloss > 0 and losses[R0 + sy] + losses[RB0 + sy] >= r21_maxloss:
                continue
            kA = R0 + sy; kB = RB0 + sy
            ke = -1
            if PIa[kA, I_ON] == 0:
                if not Won[kA]:
                    ke = kA
            elif r21_second:
                if PIa[kA, I_DIR] == d and PIa[kB, I_ON] == 0 and not Won[kB]:
                    ke = kB
            if ke < 0:
                continue
            if _hedge(PIa, Won, Wdir, sy, d, ke):
                continue
            rd = r_rd[a]
            if rd < stoplvl[sy] * 1.2:
                continue
            w = r21_w[r_tf[a]] * (r21_gm if sy == 0 else 1.0)
            r = start * r21_risk / 100.0 * w * fak
            if r_reg[a] == 0:
                r *= r21_regfak
            orisk_r = 0.0
            for q in range(NZ0):
                if PIa[q, I_ON] == 1:
                    orisk_r += _risk_of(PFa, PIa, mpp, q)
            rest = start * r21_budget / 100.0 - orisk_r
            rest2 = start * gesamtbudget / 100.0 - _open_risk(PFa, PIa, mpp)
            if rest2 < rest:
                rest = rest2
            if idea_cap > 0.0:
                rest3 = start * idea_cap / 100.0 - _idea_risk(PFa, PIa, mpp, sy, d)
                if rest3 < rest:
                    rest = rest3
            if rest < r:
                r = rest
            if r <= 0.0:
                continue
            lots = _lots(r, rd, mpp[sy], rest, minlottol)
            if lots <= 0.0:
                continue
            ii = ev_i[sy, p]
            if ii < 0:
                continue
            spr = sp1[sy, ii]; op = o1[sy, ii]
            if not _margin_ok(PFa, PIa, mpp, lev, idea_margin, sy, d, lots, op, eq_now):
                continue
            ent = (op + spr if d > 0 else op) + d * slip * spr
            k = ke
            PIa[k, I_ON] = 1; PIa[k, I_SYM] = sy; PIa[k, I_DIR] = d; PFa[k, F_ENT] = ent; PFa[k, F_SL] = ent - d * rd
            PFa[k, F_TP] = ent + d * r21_rr[sy] * rd; PFa[k, F_RD] = rd; PFa[k, F_REF] = ent; PFa[k, F_LOTS] = lots
            PFa[k, F_SWAP] = 0.0; PFa[k, F_MFE] = 0.0; PIa[k, I_BE] = 0; PIa[k, I_I1] = ii
            PIa[k, I_TMIN] = days[dayidx] * 1440 + nymin; PFa[k, F_COMM] = comm[sy] * lots; bal -= PFa[k, F_COMM]
            PFa[k, F_ACC] = 0.0; PFa[k, F_LAST] = op; PIa[k, I_TF] = r_tf[a]; PIa[k, I_XEV] = -1; PIa[k, I_STR] = -1
            PIa[k, I_FIX] = 0
            if cyc_start < 0:
                cyc_start = days[dayidx]

        # ---- Noise-Einstiege
        if zcur >= 0 and nz_on and entries_ok and z_entry[zcur] == 1 and z_close[zcur] > z_UB[zcur]:
            ii = ev_i[1, p]
            if gs:
                st[22] += 1
            elif (not _hedge(PIa, Won, Wdir, 1, 1, -1)) and ii >= 0:
                for q in range(nz_parts):
                    k = NZ0 + q
                    if PIa[k, I_ON] == 1:
                        continue
                    dist = z_dist[zcur, q]
                    if dist <= 0.0 or dist < 1.5 * 1.2:
                        continue
                    rest = start * gesamtbudget / 100.0 - _open_risk(PFa, PIa, mpp)
                    if idea_cap > 0.0:
                        rest3 = start * idea_cap / 100.0 - _idea_risk(PFa, PIa, mpp, 1, 1)
                        if rest3 < rest:
                            rest = rest3
                    r = start * nz_risk / 100.0 * z_vw[zcur] / nz_parts * fak
                    if rest < r:
                        r = rest
                    lots = _lots(r, dist, 10.0, rest, minlottol)
                    if lots <= 0.0:
                        continue
                    if not _margin_ok(PFa, PIa, mpp, lev, idea_margin, 1, 1, lots, o1[1, ii], eq_now):
                        continue
                    spr = sp1[1, ii]
                    ent = o1[1, ii] + spr + slip * spr
                    PIa[k, I_ON] = 1; PIa[k, I_SYM] = 1; PIa[k, I_DIR] = 1; PFa[k, F_ENT] = ent; PFa[k, F_SL] = ent - dist
                    PFa[k, F_TP] = 0.0; PFa[k, F_RD] = dist; PFa[k, F_REF] = ent; PFa[k, F_LOTS] = lots; PFa[k, F_SWAP] = 0.0
                    PFa[k, F_MFE] = 0.0; PIa[k, I_BE] = 0; PIa[k, I_I1] = ii; PFa[k, F_COMM] = 0.0; PFa[k, F_ACC] = 0.0
                    PFa[k, F_LAST] = o1[1, ii]; PIa[k, I_TMIN] = days[dayidx] * 1440 + nymin; PIa[k, I_XEV] = -1
                    PIa[k, I_STR] = -2; PIa[k, I_FIX] = 0
                    if cyc_start < 0:
                        cyc_start = days[dayidx]

        # ---- Generische Stroeme
        while gi < ngs and g_ev[gi] < p:
            gi += 1
        while gi < ngs and g_ev[gi] == p:
            a = gi
            gi += 1
            s_ = g_str[a]
            if gen_off or GP[s_, 0] <= 0.5 or not entries_ok:
                continue
            if gs and GP[s_, 10] <= 0.5:
                st[22] += 1
                continue
            if GP[s_, 9] > 0.0 and buf_now < GP[s_, 9]:
                continue
            sy = g_sym[a]
            k = G0 + 2 * s_ + sy
            if PIa[k, I_ON] == 1:
                continue
            ii = ev_i[sy, p]
            if ii < 0 or g_xev[a] <= p:
                continue
            if GP[s_, 2] > 0.5 and g_trades[2 * s_ + sy] >= int(GP[s_, 2]):
                continue
            if GP[s_, 11] > 0.5 and losses[k] >= int(GP[s_, 11]):
                continue
            d = g_dir[a]
            if _hedge(PIa, Won, Wdir, sy, d, -1):
                continue
            spr = sp1[sy, ii]; op = o1[sy, ii]
            if g_fix[a] == 1:
                ent = g_ent[a] + d * slip * spr
            else:
                ent = (op + spr if d > 0 else op) + d * slip * spr
            sl = g_sl[a]; tp = g_tp[a]
            rd = (ent - sl) * d
            if rd <= stoplvl[sy] * 1.2 or (tp > 0.0 and (tp - ent) * d <= 0.0):
                continue
            if GP[s_, 8] > 0.0 and rd < GP[s_, 8] * spr:
                continue
            r = start * GP[s_, 1] / 100.0 * g_w[a]
            if GP[s_, 6] > 0.5:
                r *= fak
            rest = start * gesamtbudget / 100.0 - _open_risk(PFa, PIa, mpp)
            if GP[s_, 3] > 0.0:
                orisk_g = 0.0
                for q in range(G0, NSLOT):
                    if PIa[q, I_ON] == 1 and (q - G0) // 2 == s_:
                        orisk_g += _risk_of(PFa, PIa, mpp, q)
                rest_g = start * GP[s_, 3] / 100.0 - orisk_g
                if rest_g < rest:
                    rest = rest_g
            if idea_cap > 0.0:
                rest3 = start * idea_cap / 100.0 - _idea_risk(PFa, PIa, mpp, sy, d)
                if rest3 < rest:
                    rest = rest3
            luft = _worst_eq(PFa, PIa, mpp, bal) - (peak - floor_dist) - start * 0.002
            if luft < rest:
                rest = luft
            if rest < r:
                r = rest
            lots = _lots(r, rd, mpp[sy], rest, minlottol)
            if lots <= 0.0:
                continue
            if not _margin_ok(PFa, PIa, mpp, lev, idea_margin, sy, d, lots, op, eq_now):
                continue
            PIa[k, I_ON] = 1; PIa[k, I_SYM] = sy; PIa[k, I_DIR] = d; PFa[k, F_ENT] = ent; PFa[k, F_SL] = sl
            PFa[k, F_TP] = tp; PFa[k, F_RD] = rd; PFa[k, F_REF] = ent; PFa[k, F_LOTS] = lots; PFa[k, F_SWAP] = 0.0
            PFa[k, F_MFE] = 0.0; PIa[k, I_BE] = 1; PIa[k, I_I1] = ii; PIa[k, I_TMIN] = days[dayidx] * 1440 + nymin
            PFa[k, F_COMM] = comm[sy] * lots; bal -= PFa[k, F_COMM]; PFa[k, F_ACC] = 0.0; PFa[k, F_LAST] = op
            PIa[k, I_XEV] = g_xev[a]; PIa[k, I_STR] = s_; PIa[k, I_FIX] = g_fix[a]
            g_trades[2 * s_ + sy] += 1
            if cyc_start < 0:
                cyc_start = days[dayidx]

        # ================================================= Firmenregeln und EA-Bremsen (Minutenverlauf)
        anyon = False
        for k in range(NSLOT):
            if PIa[k, I_ON] == 1:
                anyon = True
        if anyon:
            worst = 0.0; best = 0.0; gap = 0.0; worst_l = 0.0; gap_l = 0.0
            fbasis = start
            if floatminsaldo and bal < start:
                fbasis = bal
            for k in range(NSLOT):
                if PIa[k, I_ON] == 0:
                    continue
                sy = PIa[k, I_SYM]
                ii = ev_i[sy, p]
                d = PIa[k, I_DIR]
                if ii < 0:
                    wpx = PFa[k, F_LAST] + (0.0 if d > 0 else 0.0); bpx = wpx; opx = wpx
                else:
                    sp = sp1[sy, ii]
                    if d > 0:
                        opx = o1[sy, ii]
                        wpx = l1[sy, ii]
                        if wpx < PFa[k, F_SL]:
                            wpx = PFa[k, F_SL]
                        bpx = h1[sy, ii]
                        if PFa[k, F_TP] > 0.0 and bpx > PFa[k, F_TP]:
                            bpx = PFa[k, F_TP]
                    else:
                        opx = o1[sy, ii] + sp
                        wpx = h1[sy, ii] + sp
                        if wpx > PFa[k, F_SL]:
                            wpx = PFa[k, F_SL]
                        bpx = l1[sy, ii] + sp
                        if PFa[k, F_TP] > 0.0 and bpx < PFa[k, F_TP]:
                            bpx = PFa[k, F_TP]
                    PFa[k, F_LAST] = c1[sy, ii]
                pw[k] = (wpx - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP]
                worst += pw[k]
                best += (bpx - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP]
                g_k = (opx - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP]
                gap += g_k
                if g_k < 0.0:
                    gap_l += g_k
                if pw[k] < 0.0:
                    worst_l += pw[k]
                fav = (bpx - PFa[k, F_REF]) * d / PFa[k, F_RD]
                if fav > PFa[k, F_MFE]:
                    PFa[k, F_MFE] = fav
            if bal + best > peak:
                peak = bal + best
            day_ref = day_start_bal + day_ref_plus
            bust = 0
            if bal + worst <= peak - floor_dist:
                bust = 1
            elif rulefloat > 0.0 and (gap_l if rule_losers else gap) <= -fbasis * rulefloat / 100.0:
                bust = 2
            elif rulefloat > 0.0 and rule_losers and (not float_losers) and worst_l <= -fbasis * rulefloat / 100.0 \
                    and worst > -fbasis * floatstop / 100.0:
                bust = 2
            elif ruleday > 0.0 and bal + gap - day_ref <= -day_ref * ruleday / 100.0:
                bust = 3
            if bust > 0:
                for k in range(NSLOT):
                    if PIa[k, I_ON] == 1:
                        bal += pw[k]; st[8] += pw[k]
                        PIa[k, I_ON] = 0
                for k in range(NZ0):
                    Won[k] = False
                if n_out < MAXEV:
                    out_ev[n_out, 0] = 2.0; out_ev[n_out, 1] = float(days[dayidx]); out_ev[n_out, 2] = bal - start
                    out_ev[n_out, 3] = float(bust); out_ev[n_out, 4] = float(p); out_ev[n_out, 5] = gap_l; n_out += 1
                st[2] += 1
                st[2 + bust] += 1
                mode = 3; wait = rebuydelay
                cur_streak = 0; cons_loss = 0; nz_pend = False; tr_done = n_tr
                if dayidx + 1 < nd:
                    p = day_first[dayidx + 1]
                    if p > end_ev:
                        p = end_ev
                else:
                    p = end_ev
                if p >= end_ev:
                    break
                ri = r_next[p]; zi = z_next[p]; gi = g_next[p]
                continue
            # --- EA-Bremsen (Floating-Bremse gestuft, Tagesstopp)
            lim_f = -fbasis * floatstop / 100.0
            wsum = worst_l if float_losers else worst
            if floatstop > 0.0 and wsum <= lim_f:
                st[11] += 1
                target = -fbasis * (floatstop + brakeslip) / 100.0
                if target < wsum:
                    target = wsum
                if floatgestuft:
                    while True:
                        wsum_r = 0.0
                        for k in range(NSLOT):
                            if PIa[k, I_ON] == 1 and (pw[k] < 0.0 or not float_losers):
                                wsum_r += pw[k]
                        if wsum_r > lim_f:
                            break
                        tgt_r = target if wsum_r < target else wsum_r
                        ratio = tgt_r / wsum_r if wsum_r < 0.0 else 1.0
                        wk = -1; wv = 0.0
                        for k in range(NSLOT):
                            if PIa[k, I_ON] == 1 and pw[k] * ratio < wv:
                                wv = pw[k] * ratio; wk = k
                        if wk < 0:
                            break
                        k = wk
                        pnl = pw[k] * ratio
                        bal += pnl; day_real += pnl - PFa[k, F_COMM]; day_had = True; st[8] += pnl
                        tot = PFa[k, F_ACC] + pnl - PFa[k, F_COMM]
                        if n_tr < MAXTR:
                            out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                            out_tr[n_tr, 4] = float(PIa[k, I_STR]); n_tr += 1
                        losses[k] += 1
                        PIa[k, I_ON] = 0
                else:
                    ratio = target / wsum if wsum < 0.0 else 1.0
                    for k in range(NSLOT):
                        if PIa[k, I_ON] == 1:
                            pnl = pw[k] * ratio
                            bal += pnl; day_real += pnl - PFa[k, F_COMM]; day_had = True; st[8] += pnl
                            tot = PFa[k, F_ACC] + pnl - PFa[k, F_COMM]
                            if n_tr < MAXTR:
                                out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                                out_tr[n_tr, 4] = float(PIa[k, I_STR]); n_tr += 1
                            losses[k] += 1
                            PIa[k, I_ON] = 0
            else:
                dstop = -start * daystop / 100.0
                if bal + worst - day_ref <= dstop and worst < 0.0:
                    st[12] += 1
                    target = (day_ref + dstop - start * brakeslip / 100.0) - bal
                    if target < worst:
                        target = worst
                    ratio = target / worst if worst < 0.0 else 1.0
                    for k in range(NSLOT):
                        if PIa[k, I_ON] == 1:
                            pnl = pw[k] * ratio
                            bal += pnl; day_real += pnl - PFa[k, F_COMM]; day_had = True; st[8] += pnl
                            tot = PFa[k, F_ACC] + pnl - PFa[k, F_COMM]
                            if n_tr < MAXTR:
                                out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                                out_tr[n_tr, 4] = float(PIa[k, I_STR]); n_tr += 1
                            if pnl < 0:
                                losses[k] += 1
                            PIa[k, I_ON] = 0
                    day_locked = True
            if bal - day_ref <= -start * daystop / 100.0:
                day_locked = True

        # ================================================= Ausstiege (Stop, Ziel, Einstand, Zeit)
        for k in range(NSLOT):
            if PIa[k, I_ON] == 0:
                continue
            sy = PIa[k, I_SYM]
            ii = ev_i[sy, p]
            if ii < 0:
                continue
            d = PIa[k, I_DIR]
            sp = sp1[sy, ii]
            lo = l1[sy, ii]; hi = h1[sy, ii]
            if d > 0:
                hit_sl = lo <= PFa[k, F_SL]
                hit_tp = PFa[k, F_TP] > 0.0 and hi >= PFa[k, F_TP]
            else:
                hit_sl = hi + sp >= PFa[k, F_SL]
                hit_tp = PFa[k, F_TP] > 0.0 and lo + sp <= PFa[k, F_TP]
            held = ii - PIa[k, I_I1]
            px = 0.0
            closed = False
            if k >= G0 and PIa[k, I_XEV] >= 0 and p >= PIa[k, I_XEV] and held > 0:
                px = o1[sy, ii] + (sp if d < 0 else 0.0) - d * slip * sp
                closed = True
            elif hit_sl:
                px = PFa[k, F_SL]
                if d > 0 and o1[sy, ii] < PFa[k, F_SL] and held > 0:
                    px = o1[sy, ii]
                if d < 0 and o1[sy, ii] + sp > PFa[k, F_SL] and held > 0:
                    px = o1[sy, ii] + sp
                px -= d * slip * sp
                closed = True
            elif hit_tp and (k < G0 or held >= int(GP[(k - G0) // 2, 7])) and (k >= G0 or held >= minhold):
                px = PFa[k, F_TP]
                closed = True
            else:
                if k < NZ0:
                    tnow = days[dayidx] * 1440 + nymin
                    if (r21_exitbars > 0 and held >= r21_exitbars) or (r21_exitdays > 0 and (tnow - PIa[k, I_TMIN]) >= r21_exitdays * 1440):
                        px = c1[sy, ii] + (sp if d < 0 else 0.0) - d * slip * sp
                        closed = True
                    elif r21_ber > 0.0 and PIa[k, I_BE] == 0 and PFa[k, F_MFE] >= r21_ber:
                        cand = PFa[k, F_REF] + d * r21_beplus * PFa[k, F_RD]
                        if (cand - PFa[k, F_SL]) * d > 0.0:
                            PFa[k, F_SL] = cand
                        PIa[k, I_BE] = 1
                elif k < NZ1:
                    if nz_ber > 0.0 and PIa[k, I_BE] == 0 and PFa[k, F_MFE] >= nz_ber:
                        cand = PFa[k, F_REF] + d * nz_beplus * PFa[k, F_RD]
                        if (cand - PFa[k, F_SL]) * d > 0.0:
                            PFa[k, F_SL] = cand
                        PIa[k, I_BE] = 1
            if closed:
                pnl = (px - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP]
                bal += pnl; day_real += pnl - PFa[k, F_COMM]; day_had = True; st[8] += pnl
                tot = PFa[k, F_ACC] + pnl - PFa[k, F_COMM]
                if n_tr < MAXTR:
                    out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                    out_tr[n_tr, 4] = float(PIa[k, I_STR]); n_tr += 1
                if pnl < 0.0:
                    losses[k] += 1
                PIa[k, I_ON] = 0

        # ================================================= Datenloch (nur Replikat): vor dem Loch neutral schliessen
        for k in range(NSLOT):
            if PIa[k, I_ON] == 0:
                continue
            sy = PIa[k, I_SYM]
            ii = ev_i[sy, p]
            if ii < 0 or not hole[sy, ii]:
                continue
            d = PIa[k, I_DIR]
            px = c1[sy, ii] + (sp1[sy, ii] if d < 0 else 0.0)
            pnl = (px - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP]
            bal += pnl; day_real += pnl - PFa[k, F_COMM]; day_had = True; st[8] += pnl
            tot = PFa[k, F_ACC] + pnl - PFa[k, F_COMM]
            if n_tr < MAXTR:
                out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                out_tr[n_tr, 4] = float(PIa[k, I_STR]); n_tr += 1
            PIa[k, I_ON] = 0
            st[28] += 1
            if k < NZ0:
                Won[k] = False

        # ================================================= Swap-Vorsorge: letzte 10 min vor 17:00 NY
        if swap_guard > 0.0 and nymin >= 16 * 60 + 50 and nymin < 17 * 60 and not we_now:
            tripl = 3.0 if day_dow[dayidx] == 3 else 1.0
            fbasis = start
            if floatminsaldo and bal < start:
                fbasis = bal
            for it in range(NSLOT):
                lossum = 0.0; wk = -1; wv = 0.0
                for k in range(NSLOT):
                    if PIa[k, I_ON] == 1:
                        sy = PIa[k, I_SYM]
                        ii = ev_i[sy, p]
                        px = PFa[k, F_LAST] + ((sp1[sy, ii] if ii >= 0 else 0.0) if PIa[k, I_DIR] < 0 else 0.0)
                        if sy == 0:
                            swn = (-64.47 if PIa[k, I_DIR] > 0 else 23.84) * PFa[k, F_LOTS] * tripl
                        else:
                            swn = PFa[k, F_ENT] * 10.0 * PFa[k, F_LOTS] * ((-3.0 if PIa[k, I_DIR] > 0 else -1.5) / 100.0 / 360.0) * tripl
                        v = (px - PFa[k, F_ENT]) * PIa[k, I_DIR] * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP] + swn
                        if v < 0.0:
                            lossum += v
                        if v < wv:
                            wv = v; wk = k
                if lossum > -fbasis * swap_guard / 100.0 or wk < 0:
                    break
                k = wk
                sy = PIa[k, I_SYM]
                ii = ev_i[sy, p]
                d = PIa[k, I_DIR]
                px = PFa[k, F_LAST] + ((sp1[sy, ii] if ii >= 0 else 0.0) if d < 0 else 0.0)
                pnl = (px - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP]
                bal += pnl; day_real += pnl - PFa[k, F_COMM]; day_had = True; st[8] += pnl
                tot = PFa[k, F_ACC] + pnl - PFa[k, F_COMM]
                if n_tr < MAXTR:
                    out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                    out_tr[n_tr, 4] = float(PIa[k, I_STR]); n_tr += 1
                if pnl < 0.0:
                    losses[k] += 1
                PIa[k, I_ON] = 0
                st[29] += 1

        # ================================================= Abschluss-Ernte (5.10/6.10): Tag gueltig machen
        bank_ok = bank_on and cyc_start >= 0
        if bank_on and bank_last > 0:
            vbl = valid_days + (1 if (day_had and day_real >= needday) else 0)
            bank_ok = bank_ok and (vbl >= needvalid - bank_last) and (bal - start >= minprofit * bank_prof)
        if bank_ok and not day_locked and day_real < needday and nyh >= bank_from and nyh < bank_to and mode <= 1:
            need = needday * (1.0 + bank_margin)
            gain = 0.0
            for pas in range(2):
                for k in range(NSLOT):
                    if PIa[k, I_ON] == 0:
                        continue
                    if k < NZ0 and (bank_mods & 2) == 0:
                        continue
                    if k >= NZ0 and k < NZ1 and (bank_mods & 4) == 0:
                        continue
                    if k >= G0 and ((bank_mods & 8) == 0 or GP[(k - G0) // 2, 5] <= 0.5):
                        continue
                    sy = PIa[k, I_SYM]
                    ii = ev_i[sy, p]
                    if ii < 0 or ii - PIa[k, I_I1] < minhold:
                        continue
                    d = PIa[k, I_DIR]
                    px = c1[sy, ii] + (sp1[sy, ii] if d < 0 else 0.0)
                    pl = (px - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP] - comm[sy] * PFa[k, F_LOTS]
                    if pl <= 0.0 or PFa[k, F_MFE] < bank_minr:
                        continue
                    if pas == 0:
                        gain += pl
                        continue
                    perlot = pl / PFa[k, F_LOTS]
                    lots = np.ceil((need - day_real) / perlot / 0.01 - 1e-9) * 0.01
                    if lots < 0.01:
                        lots = 0.01
                    if lots > PFa[k, F_LOTS] - 0.01:
                        lots = PFa[k, F_LOTS]
                    lots = np.round(lots, 2)
                    st[15] += 1
                    if lots >= PFa[k, F_LOTS]:
                        pnl = pl + comm[sy] * PFa[k, F_LOTS]
                        bal += pnl; day_real += pnl - PFa[k, F_COMM]; day_had = True; st[8] += pnl
                        tot = PFa[k, F_ACC] + pnl - PFa[k, F_COMM]
                        if n_tr < MAXTR:
                            out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                            out_tr[n_tr, 4] = float(PIa[k, I_STR]); n_tr += 1
                        PIa[k, I_ON] = 0
                    else:
                        frac = lots / PFa[k, F_LOTS]
                        pnl = (px - PFa[k, F_ENT]) * d * lots * mpp[sy] + PFa[k, F_SWAP] * frac
                        cpart = PFa[k, F_COMM] * frac
                        bal += pnl; day_real += pnl - cpart; day_had = True; st[8] += pnl
                        PFa[k, F_ACC] += pnl - cpart
                        PFa[k, F_COMM] -= cpart
                        PFa[k, F_SWAP] *= (1.0 - frac)
                        PFa[k, F_LOTS] = np.round(PFa[k, F_LOTS] - lots, 2)
                    if day_real >= need:
                        break
                if pas == 0 and day_real + gain < need:
                    break

        # ================================================= Gewinn-Ernte (nur RSI21; nur der Mindestgewinn fehlt)
        vh = valid_days + (1 if (day_had and day_real >= needday) else 0)
        if ge_on and mode == 0 and cyc_start >= 0 and vh >= needvalid and (days[dayidx] - cyc_start) >= cycledays \
                and bal - start < minprofit and nyh < 17.0:
            ziel = start + minprofit * (1.0 + ge_auf)
            fehlt = ziel - bal
            gain = 0.0
            for pas in range(2):
                for k in range(NZ0):
                    if PIa[k, I_ON] == 0:
                        continue
                    sy = PIa[k, I_SYM]
                    ii = ev_i[sy, p]
                    if ii < 0 or ii - PIa[k, I_I1] < minhold:
                        continue
                    d = PIa[k, I_DIR]
                    bid = c1[sy, ii]; ask = bid + sp1[sy, ii]
                    favR = (bid - PFa[k, F_REF]) / PFa[k, F_RD] if d > 0 else (PFa[k, F_REF] - ask) / PFa[k, F_RD]
                    px = bid if d > 0 else ask
                    pl = (px - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP] - comm[sy] * PFa[k, F_LOTS]
                    if not (pl > 0.0 and PFa[k, F_MFE] >= ge_minr and PFa[k, F_MFE] - favR >= ge_rueck):
                        continue
                    if pas == 0:
                        gain += pl
                        continue
                    pnl = (px - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP]
                    bal += pnl; day_real += pnl - PFa[k, F_COMM]; day_had = True; st[8] += pnl
                    tot = PFa[k, F_ACC] + pnl - PFa[k, F_COMM]
                    if n_tr < MAXTR:
                        out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                        out_tr[n_tr, 4] = float(PIa[k, I_STR]); n_tr += 1
                    st[16] += 1
                    PIa[k, I_ON] = 0
                    if bal >= ziel:
                        break
                if pas == 0 and not (gain >= fehlt and fehlt > 0.0):
                    break

        # ================================================= Reife / Auszahlung
        if mode == 0 and cyc_start >= 0:
            vq = valid_days + (1 if (day_had and day_real >= needday) else 0)
            if vq >= needvalid and v5_day < 0:
                v5_day = days[dayidx]
            okp = bal - start >= minprofit
            if okp and not pr_ok:
                pr_day = days[dayidx]
            pr_ok = okp
        if mode == 0 or mode == 1:
            vh = valid_days + (1 if (day_had and day_real >= needday) else 0)
            ripe = (vh >= needvalid) and (cyc_start >= 0) and (days[dayidx] - cyc_start >= cycledays) and (bal - start >= minprofit)
            if ripe and kons_pct > 0.0:
                bd = best_day
                if day_had and day_real > bd:
                    bd = day_real
                if bd > (bal - start) * kons_pct / 100.0:
                    ripe = False
                    st[31] += 1.0 / 1440.0
            if mode == 0 and ripe:
                mode = 1
                st[23] += 1
                tday = cyc_start + cycledays
                lv = v5_day if v5_day >= 0 else days[dayidx]
                lp = pr_day if pr_day >= 0 else days[dayidx]
                if lv >= lp and lv >= tday:
                    st[24] += 1
                elif lp >= lv and lp >= tday:
                    st[25] += 1
                else:
                    st[26] += 1
            if mode == 1:
                for k in range(NSLOT):
                    if PIa[k, I_ON] == 0:
                        continue
                    if k < NZ0 and not r21_ripeclose:
                        continue
                    if k >= NZ0 and k < NZ1 and not nz_ripeclose:
                        continue
                    if k >= G0 and GP[(k - G0) // 2, 4] <= 0.5:
                        continue
                    sy = PIa[k, I_SYM]
                    ii = ev_i[sy, p]
                    if ii < 0:
                        continue
                    d = PIa[k, I_DIR]
                    px = c1[sy, ii] + (sp1[sy, ii] if d < 0 else 0.0)
                    pnl = (px - PFa[k, F_ENT]) * d * PFa[k, F_LOTS] * mpp[sy] + PFa[k, F_SWAP]
                    if pnl > 0.0 and ii - PIa[k, I_I1] < minhold:
                        continue
                    bal += pnl; day_real += pnl - PFa[k, F_COMM]; day_had = True; st[8] += pnl
                    tot = PFa[k, F_ACC] + pnl - PFa[k, F_COMM]
                    if n_tr < MAXTR:
                        out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(PIa[k, I_TMIN])
                        out_tr[n_tr, 4] = float(PIa[k, I_STR]); n_tr += 1
                    PIa[k, I_ON] = 0
                anyon = False; wwait = False
                for k in range(NSLOT):
                    if PIa[k, I_ON] == 1:
                        anyon = True
                for k in range(NZ0):
                    if Won[k]:
                        wwait = True
                if (not anyon) and not (we_reif and wwait):
                    vh = valid_days + (1 if (day_had and day_real >= needday) else 0)
                    ripe = (vh >= needvalid) and (cyc_start >= 0) and (days[dayidx] - cyc_start >= cycledays) and (bal - start >= minprofit)
                    if ripe and kons_pct > 0.0:
                        bd = best_day
                        if day_had and day_real > bd:
                            bd = day_real
                        if bd > (bal - start) * kons_pct / 100.0:
                            ripe = False
                    if ripe:
                        mode = 2; wait = paydelay
                        for k in range(NZ0):
                            Won[k] = False
                    else:
                        mode = 0

        # ================================================= Serien-Stopp (Noise-Teile eines Signals = ein Trade)
        while tr_done < n_tr:
            slot_ = int(out_tr[tr_done, 2]); res_ = out_tr[tr_done, 1]; pid_ = out_tr[tr_done, 3]
            tr_done += 1
            st[6] += 1
            if res_ > 0.0:
                st[7] += 1
            if slot_ >= NZ0 and slot_ < NZ1:
                if nz_pend and pid_ == nz_pid:
                    nz_sum += res_
                else:
                    if nz_pend:
                        if nz_sum < 0.0:
                            cons_loss += 1; cur_streak += 1
                        else:
                            cons_loss = 0; cur_streak = 0
                    nz_pid = pid_; nz_sum = res_; nz_pend = True
            else:
                str_ = int(out_tr[tr_done - 1, 4])
                if slot_ >= G0 and str_ >= 0 and GP[str_, G_NOSER] > 0.5:
                    continue                                  # v12: Strom ohne Serienzaehler
                if res_ < 0.0:
                    cons_loss += 1; cur_streak += 1
                else:
                    cons_loss = 0; cur_streak = 0
            if cur_streak > max_streak:
                max_streak = cur_streak
        if nz_pend:
            still = False
            for k in range(NZ0, NZ1):
                if PIa[k, I_ON] == 1 and float(PIa[k, I_TMIN]) == nz_pid:
                    still = True
            if not still:
                if nz_sum < 0.0:
                    cons_loss += 1; cur_streak += 1
                else:
                    cons_loss = 0; cur_streak = 0
                if cur_streak > max_streak:
                    max_streak = cur_streak
                nz_pend = False
        if cool_n > 0 and cons_loss >= cool_n:
            cool_until = days[dayidx] + cool_days
            st[17] += 1
            cons_loss = 0

        # ================================================= weiter
        anyon = False
        for k in range(NSLOT):
            if PIa[k, I_ON] == 1:
                anyon = True
        for k in range(NZ0):                  # v12: wartende Wochenend-Wiederaufnahme -> Minute fuer Minute (wie der EA je Tick);
            if Won[k]:                        # sonst haengt der Zeitpunkt der Wiederaufnahme an fremden Signal-Minuten
                anyon = True
        if not anyon:
            nxt = end_ev
            if mode == 0:
                if ri < nr and r_ev[ri] < nxt:
                    nxt = r_ev[ri]
                zj = zi                       # v12: naechste Noise-Pruefung NACH p (zi zeigt noch auf die gerade
                while zj < nzc and z_ev[zj] <= p:     # bearbeitete Minute - sonst fiel die folgende Pruefung aus, wenn
                    zj += 1                           # keine anderen Signale dazwischen lagen)
                if zj < nzc and z_ev[zj] < nxt:
                    nxt = z_ev[zj]
                if gi < ngs and g_ev[gi] < nxt and g_ev[gi] > p:
                    nxt = g_ev[gi]
            if dayidx + 1 < nd:
                jump = day_first[dayidx + 1]
                if jump < nxt:
                    nxt = jump
            if nxt <= p:
                nxt = p + 1
            p = nxt
            if p >= end_ev:
                break
            continue
        p += 1

    st[27] = max_streak
    st[18] = first_pay
    st[19] = bal
    eqe = bal
    for k in range(NSLOT):
        if PIa[k, I_ON] == 1:
            eqe += (PFa[k, F_LAST] - PFa[k, F_ENT]) * PIa[k, I_DIR] * PFa[k, F_LOTS] * mpp[PIa[k, I_SYM]] + PFa[k, F_SWAP]
    st[20] = eqe
    st[30] = mode
    st[32] = best_day
    return n_out, n_tr
