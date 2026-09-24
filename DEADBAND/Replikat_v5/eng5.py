"""DEADBAND 5.00 KOMBI Replikat - numba-Kern (ein Pfad = ein Konto ueber die Laufzeit, Neukauf nach Bust).

Konventionen (pessimistisch, wie eng3):
  - Einstieg am Open der M5-Kerze des Signals, Long zum Ask (Bid + Spread), Short zum Bid
  - in derselben M5-Kerze zaehlt der Stop VOR dem Ziel
  - Firmenregeln: Boden am schlechtesten Kurs, Floating-/Tagesregel am Kerzen-Open (die EA-Bremsen
    wirken im Echtbetrieb tickgenau), Equity-Hoch am besten Kurs
  - EA-Bremsen: Ausfuehrung am Bremsniveau plus Schlupf
Plaetze: 0-1 DEADBAND (XAU, NAS), 2-3 RSI21 A, 4-5 RSI21 B, 6.. Noise-Teile (NAS).
"""
import numpy as np, os, pickle
from numba import njit
import prep5 as P

HERE = os.path.dirname(os.path.abspath(__file__))
NSLOT = 9
NZ0 = 6

# ------------------------------------------------------------------ Parameter
PN = [
    # Konto / Regeln
    "start", "fee", "maxlosspct", "rulefloat", "ruleday", "validpct", "needvalid", "cycledays",
    "minpayout", "split", "paycap", "paycapn", "paydelay", "rebuydelay",
    # EA-Bremsen
    "floatstop", "floatgestuft", "floatminsaldo", "daystop", "brakeslip", "tagesrefeq",
    # Groesse
    "ddfull", "ddmin", "ddfmin", "belowstart", "gesamtbudget",
    # DEADBAND
    "db_on", "db_risk0", "db_risk1", "db_mult", "db_hourboost", "db_hourfrom", "db_sess0", "db_sess1",
    "db_tp1r", "db_be", "db_tp1f", "db_tpf0", "db_tpf1", "db_maxhold", "db_maxtrades", "db_maxloss", "db_budget",
    "minlottol",
    # RSI21
    "r21_on", "r21_risk", "r21_goldmult", "r21_w0", "r21_w1", "r21_w2", "r21_budget", "r21_rr_nas", "r21_rr_gold",
    "r21_exitbars", "r21_exitdays", "r21_maxloss", "r21_second", "r21_ripeclose", "r21_stopmult",
    # Noise
    "nz_on", "nz_risk", "nz_parts", "nz_ripeclose",
    # Ernte / Gewinn-Ernte
    "harvest", "harvminr", "harvmargin", "harvfrom", "harvpartial", "harvminr2", "harvgap",
    "ge_on", "ge_rueck", "ge_minr", "ge_auf",
    # Wochenende
    "we_on", "we_close", "we_reentry", "we_reif", "we_stopmaxr", "we_spreadr",
    # Stoerung
    "slip_frac", "stopmode",
    # --- Erweiterungen (5.10-Forschung), Voreinstellung = 5.00-Verhalten ---
    "bank_on", "bank_minr", "bank_from", "bank_to", "bank_margin", "bank_mods",
    "cool_n", "cool_days", "streak_n", "streak_mult", "streak_reset",
    "prot_on", "prot_frac", "prot_minprofit",
    "ripe_mode", "floorguard", "floorguard_mult", "daylossmax", "day_trade_cap",
    "db_tpfix", "r21_bepct", "nz_k_unused", "cyc_risk_after", "cyc_risk_mult",
    "db_minprofit_close", "maxopen", "valid_stop", "valid_stop_from",
    "harv_any_mods", "ge_mode", "stop_after_valid",
    "float_losers", "idea_cap", "lev", "idea_margin", "open_cap", "rule_losers", "swap_guard",
    "db_trail_from", "db_trail_dist", "r21_tp1r", "r21_tp1f", "r21_be", "r21_trail_from", "r21_trail_dist",
    "r21_first_mult", "bank_last", "bank_prof", "day_entry_stop", "floor_eod", "floor_rel",
]
PI = {n: i for i, n in enumerate(PN)}


def params(**kw):
    c = dict(start=10000.0, fee=148.5, maxlosspct=6.0, rulefloat=1.0, ruleday=3.0, validpct=0.5, needvalid=5,
             cycledays=10, minpayout=105.0, split=0.80, paycap=6.0, paycapn=2, paydelay=2, rebuydelay=1,
             floatstop=0.80, floatgestuft=1, floatminsaldo=1, daystop=2.4, brakeslip=0.05, tagesrefeq=1,
             ddfull=4.0, ddmin=1.5, ddfmin=0.6, belowstart=0.8, gesamtbudget=2.0,
             db_on=1, db_risk0=0.259, db_risk1=0.288, db_mult=0.9, db_hourboost=1.5, db_hourfrom=9.0,
             db_sess0=3.0, db_sess1=13.0, db_tp1r=2.0, db_be=0.3, db_tp1f=0.0, db_tpf0=8.0, db_tpf1=10.0,
             db_maxhold=192, db_maxtrades=1, db_maxloss=2, db_budget=0.8, minlottol=2.0,
             r21_on=1, r21_risk=0.70, r21_goldmult=0.70, r21_w0=1.25, r21_w1=1.0, r21_w2=0.75, r21_budget=1.2,
             r21_rr_nas=2.2, r21_rr_gold=2.64, r21_exitbars=1152, r21_exitdays=8, r21_maxloss=2, r21_second=1,
             r21_ripeclose=1, r21_stopmult=1.0,
             nz_on=1, nz_risk=0.30, nz_parts=3, nz_ripeclose=1,
             harvest=2, harvminr=2.0, harvmargin=0.05, harvfrom=16.0, harvpartial=1, harvminr2=0.5, harvgap=0.3,
             ge_on=1, ge_rueck=1.25, ge_minr=1.0, ge_auf=0.05,
             we_on=1, we_close=16.75, we_reentry=1, we_reif=1, we_stopmaxr=2.0, we_spreadr=0.15,
             slip_frac=0.0, stopmode=0,
             bank_on=0, bank_minr=0.0, bank_from=0.0, bank_to=17.0, bank_margin=0.05, bank_mods=3,
             cool_n=0, cool_days=0, streak_n=0, streak_mult=1.0, streak_reset=1,
             prot_on=0, prot_frac=1.0, prot_minprofit=1.0,
             ripe_mode=0, floorguard=0.0, floorguard_mult=1.0, daylossmax=0.0, day_trade_cap=0,
             db_tpfix=0.0, r21_bepct=0.0, nz_k_unused=0.0, cyc_risk_after=0, cyc_risk_mult=1.0,
             db_minprofit_close=0, maxopen=0, valid_stop=0, valid_stop_from=0.0,
             harv_any_mods=0, ge_mode=0, stop_after_valid=0,
             float_losers=0, idea_cap=0.0, lev=10.0, idea_margin=70.0, open_cap=0.0, rule_losers=0, swap_guard=0.0,
             db_trail_from=0.0, db_trail_dist=0.0, r21_tp1r=0.0, r21_tp1f=0.0, r21_be=0.0, r21_trail_from=0.0, r21_trail_dist=0.0, r21_first_mult=0.0, bank_last=0, bank_prof=0.0, day_entry_stop=0.0, floor_eod=0, floor_rel=0)
    for k in kw:
        if k not in PI:
            raise KeyError(k)
    c.update(kw)
    Pv = np.zeros(len(PN))
    for n, v in c.items():
        Pv[PI[n]] = float(v)
    return Pv


# ------------------------------------------------------------------ Markt + Signale
class Market:
    def __init__(self, sigfile="sig5.pkl"):
        with open(os.path.join(P.OUT, sigfile), "rb") as f:
            S = pickle.load(f)
        D = P.build()
        self.D = D
        syms = ("XAU", "NAS")
        t0 = D["XAU"]["ny"]; t1 = D["NAS"]["ny"]
        allt = np.union1d(t0, t1)
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
        self.ev_nyday = (allt // 1440).astype(np.int64)
        self.ev_dow = ((self.ev_nyday + 4) % 7).astype(np.int64)             # 0 = Sonntag (NY)
        self.day_dow = ((self.days + 4) % 7).astype(np.int64)                # Servertag: 0 = Sonntag
        L = max(len(t0), len(t1))

        def pad(key, dt=np.float64):
            a = np.zeros((2, L), dtype=dt)
            for k, s in enumerate(syms):
                x = D[s][key]
                a[k, :len(x)] = x
            return a
        self.o5, self.h5, self.l5, self.c5, self.sp5 = pad("o"), pad("h"), pad("l"), pad("c"), pad("sp")
        # M15-Gruppe je M5 (Haltedauer DEADBAND)
        g = np.zeros((2, L), np.int64)
        for k, s in enumerate(syms):
            ny = D[s]["ny"]
            key = ny // 15
            _, inv = np.unique(key, return_inverse=True)
            g[k, :len(ny)] = inv
        self.grp15 = g
        # Zeitluecke vor der Kerze (> 10 min) und Datenloch nach der Kerze (ungewoehnliche Luecke, kein normales WE)
        gap5 = np.zeros((2, L), np.bool_); hole5 = np.zeros((2, L), np.bool_)
        for k, s in enumerate(syms):
            ny = D[s]["ny"]
            dt = np.diff(ny)
            gap5[k, 1:len(ny)] = dt > 10
            gap5[k, 0] = True
            wd = (ny[:-1] // 1440 + 4) % 7
            normal_we = (wd == 5) & (dt >= 2940) & (dt <= 3010)
            holiday = (dt <= 330) | ((wd == 4) | (wd == 5)) & (dt <= 4500) | ((dt >= 1500) & (dt <= 1740))
            hole = (dt > 90) & ~normal_we & ~holiday
            hole5[k, :len(ny) - 1] = hole
        self.gap5 = gap5; self.hole5 = hole5
        # --- DEADBAND-Kandidaten (Session/Short-Filter im Sim)
        rows = []
        for k, s in enumerate(syms):
            x = S["db"][s]
            ev = np.searchsorted(allt, D[s]["ny"][x["i5"]])
            for a in range(len(x["T"])):
                rows.append((int(ev[a]), k, int(x["dir"][a]), float(x["rd"][a]), float(x["f"][a]), int(x["m15"][a]),
                             float(x["nyh"][a]), int(x["i5"][a])))
        rows.sort()
        A = np.array(rows)
        self.db = dict(ev=A[:, 0].astype(np.int64), sym=A[:, 1].astype(np.int64), dir=A[:, 2].astype(np.int64),
                       rd=A[:, 3], f=A[:, 4], m15=A[:, 5].astype(np.int64), nyh=A[:, 6], i5=A[:, 7].astype(np.int64))
        # --- RSI21 (nur Folgesignale sind Einstiegskandidaten; Reihenfolge ev, sym, tf)
        r = S["r21"]
        rows = []
        for a in range(len(r["T"])):
            k = int(r["sym"][a])
            T = int(r["T"][a])
            ny = D[syms[k]]["ny"]
            i5 = int(np.searchsorted(ny, T))
            if i5 >= len(ny):
                continue
            ev = int(np.searchsorted(allt, ny[i5]))
            rows.append((ev, k, int(r["tf"][a]), int(r["dir"][a]), float(r["rd"][a]), i5, 1 - int(r["folge"][a])))
        rows.sort()
        A = np.array(rows)
        self.r21 = dict(ev=A[:, 0].astype(np.int64), sym=A[:, 1].astype(np.int64), tf=A[:, 2].astype(np.int64),
                        dir=A[:, 3].astype(np.int64), rd=A[:, 4], i5=A[:, 5].astype(np.int64), first=A[:, 6].astype(np.int64))
        # --- Noise-Pruefungen
        z = S["nz"]
        nyN = D["NAS"]["ny"]
        ev = np.searchsorted(allt, nyN[z["i5"]])
        eod = np.searchsorted(allt, nyN[z["eod_i5"]])
        self.nz = dict(ev=ev.astype(np.int64), em=z["em"], close=z["close"], UB=z["UB"], vw=z["vw"],
                       dist=np.ascontiguousarray(z["dist"]), entry_ok=z["entry_ok"], eod_ev=eod.astype(np.int64),
                       day=z["day"])
        n_ev = len(allt)
        self.db["next"] = np.searchsorted(self.db["ev"], np.arange(n_ev + 1), side="left").astype(np.int64)
        self.r21["next"] = np.searchsorted(self.r21["ev"], np.arange(n_ev + 1), side="left").astype(np.int64)
        self.nz["next"] = np.searchsorted(self.nz["ev"], np.arange(n_ev + 1), side="left").astype(np.int64)
        # EOD-Ereignisse (sortiert, eindeutig)
        ue = np.unique(self.nz["eod_ev"])
        self.nz_eod = ue.astype(np.int64)
        flag = np.zeros(n_ev + 1, np.int64)
        flag[ue] = 1
        self.ev_nzeod = flag

    def day_index(self, date):
        return int(np.searchsorted(self.days, (np.datetime64(date, "D").astype(np.int64))))


# ------------------------------------------------------------------ Statistik
ST = ["ntr", "wins", "pnl", "npay", "sumpay", "nbust", "floor_b", "float_b", "day_b",
      "trade_days", "valid_days", "loss_days", "db_tr", "db_pnl", "r21_tr", "r21_pnl", "nz_tr", "nz_pnl",
      "harv", "ge", "brake_f", "brake_d", "we_close", "we_re", "cyc_days", "entries", "maxstreak",
      "streak5", "streak8", "maxlday", "lday3", "maxdd", "db_w", "r21_w", "nz_w", "ripe_lost", "bank", "cool",
      "gaps_max", "gaps_sum", "fg_skip", "lim_valid", "lim_profit", "lim_ten", "cyc_v5", "cyc_pr", "swapg", "r_seen", "r_mode", "r_loss", "r_slot", "r_hedge", "r_budget", "r_minlot", "r_margin", "r_taken"]
SI = {n: i for i, n in enumerate(ST)}
MAXEV = 2000
MAXTR = 6000


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
def _idea_risk(p_on, p_sym, p_dir, p_entry, p_sl, p_lots, mpp, sy, d):
    r = 0.0
    for q in range(p_on.shape[0]):
        if p_on[q] and p_sym[q] == sy and p_dir[q] == d:
            dist = (p_entry[q] - p_sl[q]) * p_dir[q]
            if dist > 0.0:
                r += dist * p_lots[q] * mpp[p_sym[q]]
    return r


@njit(cache=True)
def _margin_ok(p_on, p_sym, p_dir, p_lots, p_last, mpp, lev, idea_margin, sy, d, lots, px, eq):
    """GFT: neue Order <= 80 % der freien Margin, Idee (Symbol+Richtung) <= idea_margin % der Equity. Hebel lev."""
    if lev <= 0.0:
        return True
    used = 0.0; idea = 0.0
    for q in range(p_on.shape[0]):
        if p_on[q]:
            m = p_last[q] * mpp[p_sym[q]] * p_lots[q] / lev
            used += m
            if p_sym[q] == sy and p_dir[q] == d:
                idea += m
    mneu = px * mpp[sy] * lots / lev
    frei = eq - used
    if mneu > frei * 0.8:
        return False
    if idea_margin > 0.0 and idea + mneu > eq * idea_margin / 100.0:
        return False
    return True


@njit(cache=True)
def run_path(Pv, d0, d1, seed,
             ev_i, ev_day, ev_nymin, ev_dow, days, day_first, day_dow,
             o5, h5, l5, c5, sp5, grp15, gap5, hole5,
             db_ev, db_sym, db_dir, db_rd, db_f, db_m15, db_nyh, db_next,
             r_ev, r_sym, r_tf, r_dir, r_rd, r_first, r_next,
             z_ev, z_em, z_close, z_UB, z_vw, z_dist, z_entry, z_next, ev_nzeod,
             skipmask_db, skipmask_r, skipmask_z,
             out_ev, out_tr, st):
    np.random.seed(seed)
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
    db_on = Pv[25] > 0.5; db_risk = np.array([Pv[26], Pv[27]]); db_mult = Pv[28]; db_hb = Pv[29]; db_hbfrom = Pv[30]
    db_s0 = Pv[31]; db_s1 = Pv[32]; db_tp1r = Pv[33]; db_be = Pv[34]; db_tp1f = Pv[35]
    db_tpf = np.array([Pv[36], Pv[37]]); db_maxhold = int(Pv[38]); db_maxtrades = int(Pv[39]); db_maxloss = int(Pv[40])
    db_budget = Pv[41]; minlottol = Pv[42]
    r21_on = Pv[43] > 0.5; r21_risk = Pv[44]; r21_gm = Pv[45]; r21_w = np.array([Pv[46], Pv[47], Pv[48]])
    r21_budget = Pv[49]; r21_rr = np.array([Pv[51], Pv[50]]); r21_exitbars = int(Pv[52]); r21_exitdays = Pv[53]
    r21_maxloss = int(Pv[54]); r21_second = Pv[55] > 0.5; r21_ripeclose = Pv[56] > 0.5; r21_stopmult = Pv[57]
    nz_on = Pv[58] > 0.5; nz_risk = Pv[59]; nz_parts = int(Pv[60]); nz_ripeclose = Pv[61] > 0.5
    harvest = int(Pv[62]); harvminr = Pv[63]; harvmargin = Pv[64]; harvfrom = Pv[65]; harvpartial = Pv[66] > 0.5
    harvminr2 = Pv[67]; harvgap = Pv[68]
    ge_on = Pv[69] > 0.5; ge_rueck = Pv[70]; ge_minr = Pv[71]; ge_auf = Pv[72]
    we_on = Pv[73] > 0.5; we_close = Pv[74]; we_reentry = Pv[75] > 0.5; we_reif = Pv[76] > 0.5
    we_stopmaxr = Pv[77]; we_spreadr = Pv[78]
    slip_frac = Pv[79]; stopmode = int(Pv[80])
    bank_on = Pv[81] > 0.5; bank_minr = Pv[82]; bank_from = Pv[83]; bank_to = Pv[84]; bank_margin = Pv[85]
    bank_mods = int(Pv[86])
    cool_n = int(Pv[87]); cool_days = int(Pv[88]); streak_n = int(Pv[89]); streak_mult = Pv[90]
    streak_reset = int(Pv[91])
    prot_on = Pv[92] > 0.5; prot_frac = Pv[93]; prot_minprofit = Pv[94]
    ripe_mode = int(Pv[95]); floorguard = Pv[96]; floorguard_mult = Pv[97]; daylossmax = Pv[98]
    day_trade_cap = int(Pv[99]); db_tpfix = Pv[100]; r21_bepct = Pv[101]
    cyc_risk_after = int(Pv[103]); cyc_risk_mult = Pv[104]
    maxopen = int(Pv[106]); valid_stop = int(Pv[107]); valid_stop_from = Pv[108]
    harv_any_mods = int(Pv[109]); ge_mode = int(Pv[110]); stop_after_valid = int(Pv[111])
    float_losers = Pv[112] > 0.5; idea_cap = Pv[113]; lev = Pv[114]; idea_margin = Pv[115]; open_cap = Pv[116]; rule_losers = Pv[117] > 0.5; swap_guard = Pv[118]
    db_trail_from = Pv[119]; db_trail_dist = Pv[120]; r21_tp1r = Pv[121]; r21_tp1f = Pv[122]; r21_be = Pv[123]
    r21_trail_from = Pv[124]; r21_trail_dist = Pv[125]; r21_first_mult = Pv[126]; bank_last = int(Pv[127]); bank_prof = Pv[128]; day_entry_stop = Pv[129]; floor_eod = Pv[130] > 0.5; floor_rel = Pv[131] > 0.5

    floor_dist = start * maxlosspct / 100.0
    needday = start * validpct / 100.0
    minprofit = minpayout / split

    # ---- Kontozustand
    bal = start; peak = start
    valid_days = 0; trade_days = 0; cyc_start = -1; npay_acc = 0
    mode = 0; wait = 0
    n_out = 0; n_tr = 0
    # Positionen
    p_on = np.zeros(NSLOT, np.bool_); p_sym = np.zeros(NSLOT, np.int64); p_dir = np.zeros(NSLOT, np.int64)
    p_entry = np.zeros(NSLOT); p_sl = np.zeros(NSLOT); p_tp = np.zeros(NSLOT); p_rd = np.zeros(NSLOT)
    p_ref = np.zeros(NSLOT); p_lots = np.zeros(NSLOT); p_swap = np.zeros(NSLOT); p_mfe = np.zeros(NSLOT)
    p_be = np.zeros(NSLOT, np.bool_); p_t1 = np.zeros(NSLOT, np.bool_); p_i5 = np.zeros(NSLOT, np.int64)
    p_m15 = np.zeros(NSLOT, np.int64); p_tmin = np.zeros(NSLOT, np.int64); p_comm = np.zeros(NSLOT)
    p_acc = np.zeros(NSLOT)            # realisiert aus Teilschliessungen (fuer Serienstatistik)
    p_last = np.zeros(NSLOT); p_w = np.zeros(NSLOT); p_tfm = np.zeros(NSLOT, np.int64)
    p_v1 = np.zeros(NSLOT)
    # Wochenend-Vormerkungen
    w_on = np.zeros(NSLOT, np.bool_); w_dir = np.zeros(NSLOT, np.int64); w_sl = np.zeros(NSLOT); w_tp = np.zeros(NSLOT)
    w_lots = np.zeros(NSLOT); w_rd = np.zeros(NSLOT); w_ref = np.zeros(NSLOT); w_mfe = np.zeros(NSLOT)
    w_be = np.zeros(NSLOT, np.bool_); w_t1 = np.zeros(NSLOT, np.bool_); w_i5 = np.zeros(NSLOT, np.int64)
    w_m15 = np.zeros(NSLOT, np.int64); w_tmin = np.zeros(NSLOT, np.int64); w_fri = np.zeros(NSLOT, np.int64)
    w_acc = np.zeros(NSLOT)
    # Tageszaehler
    db_trades = np.zeros(2, np.int64); losses = np.zeros(NSLOT, np.int64)
    day_real = 0.0; day_had = False; day_start_bal = start; day_ref_plus = 0.0
    day_locked = False
    # Serien
    cur_streak = 0; max_streak = 0; cur_lday = 0; max_lday = 0
    cool_until = -1            # Tagesindex, bis zu dem keine Einstiege
    cons_loss = 0              # Verluste in Folge (fuer Groessenbremse)
    bal_peak_c = start; maxdd = 0.0
    last_pay_day = -1; gaps_max = 0.0; gaps_sum = 0.0; first_day = -1
    day_trades_all = 0
    v5_day = -1; pr_day = -1; pr_ok = False
    tr_done = 0; nz_pid = -1.0; nz_sum = 0.0; nz_pend = False

    if d0 >= nd:
        return 0, 0
    p = day_first[d0]
    end_ev = n_ev
    if d1 < nd:
        end_ev = day_first[d1]
    dayidx = ev_day[p]
    first_day = days[dayidx]
    last_pay_day = days[dayidx]
    dbi = db_next[p]; ri = r_next[p]; zi = z_next[p]
    ndb = db_ev.shape[0]; nr = r_ev.shape[0]; nzc = z_ev.shape[0]

    while p < end_ev:
        di = ev_day[p]
        nymin = ev_nymin[p]
        nyh = nymin / 60.0
        dow = ev_dow[p]
        # ================================================= Tageswechsel (17:00 NY)
        if di != dayidx:
            mult = 3.0 if day_dow[dayidx] == 3 else 1.0          # Mittwoch-Servertag -> dreifacher Swap
            for k in range(NSLOT):
                if p_on[k]:
                    if p_sym[k] == 0:
                        sw = (-64.47 if p_dir[k] > 0 else 23.84) * 0.01 * 100.0 * p_lots[k] * mult
                    else:
                        rate = -3.0 if p_dir[k] > 0 else -1.5
                        sw = p_entry[k] * 10.0 * p_lots[k] * (rate / 100.0 / 360.0) * mult
                    p_swap[k] += sw
            if day_had:
                trade_days += 1
                st[9] += 1
                if day_real >= needday:
                    valid_days += 1
                    st[10] += 1
                if day_real < 0.0:
                    st[11] += 1
                    cur_lday += 1
                    if cur_lday > max_lday:
                        max_lday = cur_lday
                    if cur_lday == 3:
                        st[30] += 1
                else:
                    cur_lday = 0
            if mode == 2 or mode == 3:
                wait -= 1
                if wait <= 0:
                    if mode == 2:
                        profit = bal - start
                        amt = profit
                        if npay_acc < paycapn and amt > paycap:
                            amt = paycap
                        if amt < 0.0:
                            amt = 0.0
                        bal -= amt
                        peak = bal
                        if n_out < MAXEV:
                            out_ev[n_out, 0] = 1.0; out_ev[n_out, 1] = float(days[di]); out_ev[n_out, 2] = amt
                            n_out += 1
                        st[3] += 1; st[4] += amt
                        if cyc_start >= 0:
                            st[24] += float(days[di] - cyc_start)
                        gap_ = float(days[di] - last_pay_day)
                        if gap_ > gaps_max:
                            gaps_max = gap_
                        gaps_sum += gap_
                        last_pay_day = days[di]
                        npay_acc += 1
                    else:
                        bal = start; peak = start; npay_acc = 0
                        if n_out < MAXEV:
                            out_ev[n_out, 0] = 3.0; out_ev[n_out, 1] = float(days[di]); out_ev[n_out, 2] = fee
                            n_out += 1
                    valid_days = 0; trade_days = 0; cyc_start = -1
                    v5_day = -1; pr_day = -1; pr_ok = False
                    bal_peak_c = bal
                    mode = 0
            dayidx = di
            day_start_bal = bal
            flt0 = 0.0
            for k in range(NSLOT):
                if p_on[k]:
                    flt0 += (p_last[k] - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[p_sym[k]] + p_swap[k]
            day_ref_plus = flt0 if (tagesrefeq and flt0 > 0.0) else 0.0
            if floor_eod and bal + flt0 > peak:
                peak = bal + flt0
            day_real = 0.0; day_had = False; day_locked = False
            db_trades[0] = 0; db_trades[1] = 0
            for k in range(NSLOT):
                losses[k] = 0
            day_trades_all = 0

        i0 = ev_i[0, p]; i1 = ev_i[1, p]
        # Kurse am Open dieser Kerze je Symbol (Bid) und Spread
        # ================================================= Hilfsgroessen
        eq_open = bal
        for k in range(NSLOT):
            if p_on[k]:
                ii = ev_i[p_sym[k], p]
                px = p_last[k]
                if ii >= 0:
                    px = o5[p_sym[k], ii] + (sp5[p_sym[k], ii] if p_dir[k] < 0 else 0.0)
                eq_open += (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[p_sym[k]] + p_swap[k]
        fbasis = start
        if floatminsaldo and bal < start:
            fbasis = bal

        # ================================================= Freitag: Wochenend-Schluss
        we_now = we_on and dow == 5 and nyh >= we_close
        if we_now:
            for k in range(NSLOT):
                if not p_on[k]:
                    continue
                sy = p_sym[k]
                ii = ev_i[sy, p]
                if ii < 0:
                    continue
                px = o5[sy, ii] + (sp5[sy, ii] if p_dir[k] < 0 else 0.0)
                pnl = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[sy] + p_swap[k]
                bal += pnl; day_real += pnl - p_comm[k]; day_had = True
                st[2] += pnl; st[22] += 1
                tot = p_acc[k] + pnl - p_comm[k]
                vorm = we_reentry and k < NZ0 and (mode == 0 or we_reif) and p_rd[k] > 0.0
                if vorm:
                    w_on[k] = True; w_dir[k] = p_dir[k]; w_sl[k] = p_sl[k]; w_tp[k] = p_tp[k]; w_lots[k] = p_lots[k]
                    w_rd[k] = p_rd[k]; w_ref[k] = p_ref[k]; w_mfe[k] = p_mfe[k]; w_be[k] = p_be[k]; w_t1[k] = p_t1[k]
                    w_i5[k] = p_i5[k]; w_m15[k] = p_m15[k]; w_tmin[k] = p_tmin[k]; w_fri[k] = ev_i[0, p] * 0 + days[dayidx]
                p_on[k] = False
                # Trade-Protokoll (Wochenend-Schluss beendet den Trade)
                if n_tr < MAXTR:
                    out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                    n_tr += 1
                if pnl < 0.0:
                    losses[k] += 1
                # Serie
                if tot < 0.0:
                    cur_streak += 1
                    if cur_streak > max_streak:
                        max_streak = cur_streak
                    if cur_streak == 5:
                        st[27] += 1
                    if cur_streak == 8:
                        st[28] += 1
                else:
                    cur_streak = 0
        # Vormerkungen verfallen (ab Dienstag)
        for k in range(NSLOT):
            if w_on[k]:
                seit = days[dayidx] - w_fri[k]
                if (dow >= 2 and dow <= 4 and seit >= 3) or seit >= 6:
                    w_on[k] = False

        # ================================================= Einstiege am Open
        entries_ok = (mode == 0) and (not day_locked) and not (we_on and dow == 5 and nyh >= we_close - 5.0 / 60.0)
        if cool_until >= 0 and days[dayidx] <= cool_until:
            entries_ok = False
        if day_trade_cap > 0 and day_trades_all >= day_trade_cap:
            entries_ok = False
        if valid_stop > 0 and day_had and day_real >= needday and nyh >= valid_stop_from:
            entries_ok = False
        if stop_after_valid > 0 and cyc_start >= 0:
            vsa = valid_days + (1 if (day_had and day_real >= needday) else 0)
            if vsa >= needvalid and bal - start >= minprofit * prot_minprofit:
                entries_ok = False
        # Sonntag-/Montag-Wiederaufnahme
        if we_on and we_reentry and (dow == 0 and nyh >= 18.0 or dow == 1):
            for k in range(NSLOT):
                if not w_on[k]:
                    continue
                if mode == 2 or (mode != 0 and not we_reif):
                    w_on[k] = False
                    continue
                if k >= 2 and k < NZ0 and mode != 0 and r21_ripeclose:
                    w_on[k] = False
                    continue
                if day_locked or p_on[k]:
                    continue
                sy = 0 if (k == 0 or k == 2 or k == 4) else 1
                ii = ev_i[sy, p]
                if ii < 0:
                    continue
                spr = sp5[sy, ii]
                if we_spreadr > 0.0 and spr > we_spreadr * w_rd[k] and dow == 0 and nyh < 19.0:
                    continue
                d = w_dir[k]
                # Hedging-Sperre
                hed = False
                for q in range(NSLOT):
                    if p_on[q] and p_sym[q] == sy and p_dir[q] != d:
                        hed = True
                if hed:
                    continue
                bid = o5[sy, ii]; ask = bid + spr
                ent = ask if d > 0 else bid
                chk = bid if d > 0 else ask
                if (d > 0 and chk <= w_sl[k]) or (d < 0 and chk >= w_sl[k]):
                    w_on[k] = False
                    continue
                if w_tp[k] > 0.0 and ((d > 0 and chk >= w_tp[k]) or (d < 0 and chk <= w_tp[k])):
                    w_on[k] = False
                    continue
                nsl = w_sl[k]
                if we_stopmaxr > 0.0:
                    tight = ent - d * we_stopmaxr * w_rd[k]
                    if (d > 0 and tight > nsl) or (d < 0 and tight < nsl):
                        nsl = tight
                p_on[k] = True; p_sym[k] = sy; p_dir[k] = d; p_entry[k] = ent; p_sl[k] = nsl; p_tp[k] = w_tp[k]
                p_rd[k] = w_rd[k]; p_ref[k] = w_ref[k]; p_lots[k] = w_lots[k]; p_swap[k] = 0.0; p_mfe[k] = w_mfe[k]
                p_be[k] = w_be[k]; p_t1[k] = True; p_i5[k] = w_i5[k]; p_m15[k] = w_m15[k]; p_tmin[k] = w_tmin[k]
                p_comm[k] = comm[sy] * p_lots[k]; bal -= p_comm[k]; p_acc[k] = 0.0; p_last[k] = bid
                p_v1[k] = 0.0
                w_on[k] = False
                st[23] += 1

        # ---- Noise: Pruefung (Ausstieg) und Tagesende 15:55
        while zi < nzc and z_ev[zi] < p:
            zi += 1
        zcur = -1
        if zi < nzc and z_ev[zi] == p:
            zcur = zi
        nz_open = 0
        for k in range(NZ0, NZ0 + nz_parts):
            if p_on[k]:
                nz_open += 1
        eodnow = ev_nzeod[p] == 1
        if nz_open > 0 and (eodnow or (zcur >= 0 and z_close[zcur] < z_UB[zcur]) or (we_now)):
            ii = ev_i[1, p]
            if ii >= 0:
                for k in range(NZ0, NZ0 + nz_parts):
                    if not p_on[k]:
                        continue
                    px = o5[1, ii]
                    pnl = (px - p_entry[k]) * p_lots[k] * 10.0 + p_swap[k]
                    bal += pnl; day_real += pnl; day_had = True
                    st[2] += pnl; st[16] += 1; st[17] += pnl
                    if pnl > 0:
                        st[34] += 1
                    if pnl < 0.0:
                        losses[k] += 1
                    tot = pnl
                    if n_tr < MAXTR:
                        out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                        n_tr += 1
                    if tot < 0.0:
                        cur_streak += 1
                        if cur_streak > max_streak:
                            max_streak = cur_streak
                        if cur_streak == 5:
                            st[27] += 1
                        if cur_streak == 8:
                            st[28] += 1
                    else:
                        cur_streak = 0
                    p_on[k] = False

        # ---- gemeinsame Groessenfaktoren (Equity am Open)
        eq_now = bal
        for k in range(NSLOT):
            if p_on[k]:
                ii = ev_i[p_sym[k], p]
                px = p_last[k]
                if ii >= 0:
                    px = o5[p_sym[k], ii] + (sp5[p_sym[k], ii] if p_dir[k] < 0 else 0.0)
                eq_now += (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[p_sym[k]] + p_swap[k]
        fak = _ddf(eq_now, peak, floor_dist, start, ddfull, ddmin, ddfmin)
        if eq_now < start:
            fak *= belowstart
        buf_now = (eq_now - (peak - floor_dist)) / start * 100.0
        if floorguard > 0.0 and buf_now < floorguard:
            fak *= floorguard_mult
            if floorguard_mult <= 0.0:
                entries_ok = False
        if streak_n > 0 and cons_loss >= streak_n:
            fak *= streak_mult
        if prot_on:
            vv = valid_days + (1 if (day_had and day_real >= needday) else 0)
            if bal - start >= minprofit * prot_minprofit and vv >= needvalid - 1:
                fak *= prot_frac
        if cyc_risk_after > 0 and cyc_start >= 0 and (days[dayidx] - cyc_start) >= cyc_risk_after:
            fak *= cyc_risk_mult
        n_open = 0
        for k in range(NSLOT):
            if p_on[k]:
                n_open += 1
        if maxopen > 0 and n_open >= maxopen:
            entries_ok = False
        if day_entry_stop > 0.0 and (eq_now - (day_start_bal + day_ref_plus)) <= -start * day_entry_stop / 100.0:
            entries_ok = False

        # offenes Risiko je Art
        def_dummy = 0
        # ---- DEADBAND
        while dbi < ndb and db_ev[dbi] < p:
            dbi += 1
        while dbi < ndb and db_ev[dbi] == p:
            a = dbi
            dbi += 1
            if not db_on or not entries_ok:
                continue
            if skipmask_db[a]:
                continue
            k = db_sym[a]
            if p_on[k] or w_on[k]:
                continue
            nyh_e = db_nyh[a]
            if nyh_e < db_s0 or nyh_e >= db_s1:
                continue
            if db_trades[k] >= db_maxtrades or losses[k] >= db_maxloss:
                continue
            d = db_dir[a]
            hed = False
            for q in range(NSLOT):
                if (p_on[q] and p_sym[q] == k and p_dir[q] != d) or (w_on[q] and q != k and ((q % 2) == (k % 2)) and q < NZ0 and w_dir[q] != d):
                    hed = True
            if hed:
                continue
            rd = db_rd[a]
            r = start * db_risk[k] / 100.0 * db_mult
            if db_hb > 0.0 and nyh_e >= db_hbfrom:
                r *= db_hb
            r *= db_f[a]
            r *= fak
            # Budgets
            orisk_db = 0.0; orisk_all = 0.0
            for q in range(NSLOT):
                if p_on[q]:
                    dist = (p_entry[q] - p_sl[q]) * p_dir[q]
                    if dist > 0.0:
                        rr_ = dist * p_lots[q] * mpp[p_sym[q]]
                        orisk_all += rr_
                        if q < 2:
                            orisk_db += rr_
            rest = start * db_budget / 100.0 - orisk_db
            rest2 = start * gesamtbudget / 100.0 - orisk_all
            if rest2 < rest:
                rest = rest2
            if idea_cap > 0.0:
                rest3 = start * idea_cap / 100.0 - _idea_risk(p_on, p_sym, p_dir, p_entry, p_sl, p_lots, mpp, k, d)
                if rest3 < rest:
                    rest = rest3
            if rest < r:
                r = rest
            if r <= 0.0:
                continue
            if 0.01 * rd * mpp[k] > r * minlottol:
                continue
            lots = np.floor(r / (rd * mpp[k]) / 0.01 + 0.5) * 0.01
            if lots < 0.01:
                lots = 0.01
            if lots * rd * mpp[k] > rest + 1e-9:
                lots = np.floor(rest / (rd * mpp[k]) / 0.01 + 1e-9) * 0.01
                if lots < 0.01 - 1e-12:
                    continue
            lots = np.round(lots, 2)
            ii = ev_i[k, p]
            if ii < 0:
                continue
            spr = sp5[k, ii]
            op = o5[k, ii]
            if not _margin_ok(p_on, p_sym, p_dir, p_lots, p_last, mpp, lev, idea_margin, k, d, lots, op, eq_now):
                continue
            ent = op + spr if d > 0 else op
            if slip_frac > 0.0:
                ent += d * np.random.random() * slip_frac * spr
            sl = ent - d * rd
            tpf = db_tpf[k]
            if db_tpfix > 0.0:
                tpf = db_tpfix
            p_on[k] = True; p_sym[k] = k; p_dir[k] = d; p_entry[k] = ent; p_sl[k] = sl; p_tp[k] = ent + d * tpf * rd
            p_rd[k] = rd; p_ref[k] = ent; p_lots[k] = lots; p_swap[k] = 0.0; p_mfe[k] = 0.0; p_be[k] = False
            p_t1[k] = False; p_i5[k] = ii; p_m15[k] = grp15[k, ii]; p_tmin[k] = days[dayidx] * 1440 + nymin
            p_comm[k] = comm[k] * lots; bal -= p_comm[k]; p_acc[k] = 0.0; p_last[k] = op
            v1 = np.floor(lots * db_tp1f / 0.01 + 1e-9) * 0.01
            if v1 < 0.01 or lots - v1 < 0.01:
                v1 = 0.0
            p_v1[k] = np.round(v1, 2)
            db_trades[k] += 1
            day_trades_all += 1
            st[25] += 1
            if cyc_start < 0:
                cyc_start = days[dayidx]
            n_open += 1
            if maxopen > 0 and n_open >= maxopen:
                entries_ok = False

        # ---- RSI21
        while ri < nr and r_ev[ri] < p:
            ri += 1
        newA = np.zeros(2, np.bool_)
        while ri < nr and r_ev[ri] == p:
            a = ri
            ri += 1
            st[47] += 1
            if not r21_on or not entries_ok:
                st[48] += 1
                continue
            if skipmask_r[a]:
                continue
            if r_first[a] == 1 and r21_first_mult <= 0.0:
                continue
            sy = r_sym[a]
            d = r_dir[a]
            if r21_maxloss > 0 and losses[2 + sy] + losses[4 + sy] >= r21_maxloss:
                st[49] += 1
                continue
            kA = 2 + sy; kB = 4 + sy
            ke = -1
            if not p_on[kA]:
                if not w_on[kA]:
                    ke = kA
            elif r21_second:
                if p_dir[kA] == d and (not p_on[kB]) and (not w_on[kB]):
                    ke = kB
            if ke < 0:
                st[50] += 1
                continue
            hed = False
            for q in range(NSLOT):
                if (p_on[q] and p_sym[q] == sy and p_dir[q] != d):
                    hed = True
                if w_on[q] and q != ke and q < NZ0 and ((q == sy) or (q == 2 + sy) or (q == 4 + sy)) and w_dir[q] != d:
                    hed = True
            if hed:
                st[51] += 1
                continue
            rd = r_rd[a] * r21_stopmult
            if rd < stoplvl[sy] * 1.2:
                continue
            w = r21_w[r_tf[a]] * (r21_gm if sy == 0 else 1.0)
            if r_first[a] == 1:
                w *= r21_first_mult
            r = start * r21_risk / 100.0 * w * fak
            orisk_r = 0.0; orisk_all = 0.0
            for q in range(NSLOT):
                if p_on[q]:
                    dist = (p_entry[q] - p_sl[q]) * p_dir[q]
                    if dist > 0.0:
                        rr_ = dist * p_lots[q] * mpp[p_sym[q]]
                        orisk_all += rr_
                        if q >= 2 and q < NZ0:
                            orisk_r += rr_
            rest = start * r21_budget / 100.0 - orisk_r
            rest2 = start * gesamtbudget / 100.0 - orisk_all
            if rest2 < rest:
                rest = rest2
            idea_lim = False
            if idea_cap > 0.0:
                rest3 = start * idea_cap / 100.0 - _idea_risk(p_on, p_sym, p_dir, p_entry, p_sl, p_lots, mpp, sy, d)
                if rest3 < rest:
                    rest = rest3
                    idea_lim = True
            if rest < r:
                r = rest
            if r <= 0.0:
                st[52] += 1
                if idea_lim:
                    continue
                break
            if 0.01 * rd * mpp[sy] > r * minlottol:
                st[53] += 1
                continue
            lots = np.floor(r / (rd * mpp[sy]) / 0.01 + 0.5) * 0.01
            if lots < 0.01:
                lots = 0.01
            if lots * rd * mpp[sy] > rest + 1e-9:
                lots = np.floor(rest / (rd * mpp[sy]) / 0.01 + 1e-9) * 0.01
                if lots < 0.01 - 1e-12:
                    continue
            lots = np.round(lots, 2)
            ii = ev_i[sy, p]
            if ii < 0:
                continue
            spr = sp5[sy, ii]
            op = o5[sy, ii]
            if not _margin_ok(p_on, p_sym, p_dir, p_lots, p_last, mpp, lev, idea_margin, sy, d, lots, op, eq_now):
                st[54] += 1
                break
            ent = op + spr if d > 0 else op
            if slip_frac > 0.0:
                ent += d * np.random.random() * slip_frac * spr
            k = ke
            rrr = r21_rr[sy]
            p_on[k] = True; p_sym[k] = sy; p_dir[k] = d; p_entry[k] = ent; p_sl[k] = ent - d * rd; p_tp[k] = ent + d * rrr * rd
            p_rd[k] = rd; p_ref[k] = ent; p_lots[k] = lots; p_swap[k] = 0.0; p_mfe[k] = 0.0; p_be[k] = r21_tp1r <= 0.0
            p_t1[k] = r21_tp1r <= 0.0; p_i5[k] = ii; p_m15[k] = 0; p_tmin[k] = days[dayidx] * 1440 + nymin
            p_comm[k] = comm[sy] * lots; bal -= p_comm[k]; p_acc[k] = 0.0; p_last[k] = op; p_v1[k] = 0.0
            if r21_tp1r > 0.0 and r21_tp1f > 0.0:
                v1r = np.floor(lots * r21_tp1f / 0.01 + 1e-9) * 0.01
                if v1r >= 0.01 and lots - v1r >= 0.01:
                    p_v1[k] = np.round(v1r, 2)
            p_tfm[k] = r_tf[a]
            st[55] += 1
            day_trades_all += 1
            st[25] += 1
            if cyc_start < 0:
                cyc_start = days[dayidx]
            n_open += 1
            if not r21_second:
                # ohne zweiten Platz: ein Einstieg je Kerze
                while ri < nr and r_ev[ri] == p:
                    ri += 1
            if maxopen > 0 and n_open >= maxopen:
                entries_ok = False

        # ---- Noise-Einstiege
        if zcur >= 0 and nz_on and entries_ok and z_entry[zcur] == 1 and z_close[zcur] > z_UB[zcur] and not skipmask_z[zcur]:
            hed = False
            for q in range(NSLOT):
                if p_on[q] and p_sym[q] == 1 and p_dir[q] < 0:
                    hed = True
                if w_on[q] and (q == 1 or q == 3 or q == 5) and w_dir[q] < 0:
                    hed = True
            ii = ev_i[1, p]
            if (not hed) and ii >= 0:
                for q in range(nz_parts):
                    k = NZ0 + q
                    if p_on[k]:
                        continue
                    dist = z_dist[zcur, q]
                    if dist <= 0.0 or dist < 1.5 * 1.2:
                        continue
                    orisk_all = 0.0
                    for q2 in range(NSLOT):
                        if p_on[q2]:
                            dd_ = (p_entry[q2] - p_sl[q2]) * p_dir[q2]
                            if dd_ > 0.0:
                                orisk_all += dd_ * p_lots[q2] * mpp[p_sym[q2]]
                    rest = start * gesamtbudget / 100.0 - orisk_all
                    if idea_cap > 0.0:
                        rest3 = start * idea_cap / 100.0 - _idea_risk(p_on, p_sym, p_dir, p_entry, p_sl, p_lots, mpp, 1, 1)
                        if rest3 < rest:
                            rest = rest3
                    r = start * nz_risk / 100.0 * z_vw[zcur] / nz_parts * fak
                    if rest < r:
                        r = rest
                    if r <= 0.0:
                        continue
                    if 0.01 * dist * 10.0 > r * minlottol:
                        continue
                    lots = np.floor(r / (dist * 10.0) / 0.01 + 0.5) * 0.01
                    if lots < 0.01:
                        lots = 0.01
                    if lots * dist * 10.0 > rest + 1e-9:
                        lots = np.floor(rest / (dist * 10.0) / 0.01 + 1e-9) * 0.01
                        if lots < 0.01 - 1e-12:
                            continue
                    lots = np.round(lots, 2)
                    if not _margin_ok(p_on, p_sym, p_dir, p_lots, p_last, mpp, lev, idea_margin, 1, 1, lots, o5[1, ii], eq_now):
                        continue
                    spr = sp5[1, ii]
                    ent = o5[1, ii] + spr
                    if slip_frac > 0.0:
                        ent += np.random.random() * slip_frac * spr
                    p_on[k] = True; p_sym[k] = 1; p_dir[k] = 1; p_entry[k] = ent; p_sl[k] = ent - dist; p_tp[k] = 0.0
                    p_rd[k] = dist; p_ref[k] = ent; p_lots[k] = lots; p_swap[k] = 0.0; p_mfe[k] = 0.0; p_be[k] = True
                    p_t1[k] = True; p_i5[k] = ii; p_comm[k] = 0.0; p_acc[k] = 0.0; p_last[k] = o5[1, ii]; p_v1[k] = 0.0
                    p_tmin[k] = days[dayidx] * 1440 + nymin
                    day_trades_all += 1
                    st[25] += 1
                    if cyc_start < 0:
                        cyc_start = days[dayidx]

        # ================================================= Kontoschicht (Kerzenverlauf)
        anyon = False
        for k in range(NSLOT):
            if p_on[k]:
                anyon = True
        if anyon:
            worst = 0.0; best = 0.0; gap = 0.0; worst_l = 0.0; gap_l = 0.0
            for k in range(NSLOT):
                if not p_on[k]:
                    continue
                sy = p_sym[k]
                ii = ev_i[sy, p]
                d = p_dir[k]
                if ii < 0:
                    wpx = p_last[k]; bpx = p_last[k]; opx = p_last[k]
                else:
                    sp = sp5[sy, ii]
                    if d > 0:
                        opx = o5[sy, ii] if gap5[sy, ii] else p_last[k]
                        wpx = l5[sy, ii]
                        if wpx < p_sl[k]:
                            wpx = p_sl[k]
                        bpx = h5[sy, ii]
                        if p_tp[k] > 0.0 and bpx > p_tp[k]:
                            bpx = p_tp[k]
                    else:
                        opx = (o5[sy, ii] + sp) if gap5[sy, ii] else p_last[k] + sp
                        wpx = h5[sy, ii] + sp
                        if wpx > p_sl[k]:
                            wpx = p_sl[k]
                        bpx = l5[sy, ii] + sp
                        if p_tp[k] > 0.0 and bpx < p_tp[k]:
                            bpx = p_tp[k]
                    p_last[k] = c5[sy, ii]
                p_w[k] = (wpx - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k]
                worst += p_w[k]
                best += (bpx - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k]
                g_k = (opx - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k]
                gap += g_k
                if g_k < 0.0:
                    gap_l += g_k
                if p_w[k] < 0.0:
                    worst_l += p_w[k]
                fav = (bpx - p_ref[k]) * d / p_rd[k]
                if fav > p_mfe[k]:
                    p_mfe[k] = fav
            if (not floor_eod) and bal + best > peak:
                peak = bal + best
            day_ref = day_start_bal + day_ref_plus
            bust = 0
            flo = peak * (1.0 - maxlosspct / 100.0) if floor_rel else peak - floor_dist
            if bal + worst <= flo:
                bust = 1
            elif rulefloat > 0.0 and (gap_l if rule_losers else gap) <= -fbasis * rulefloat / 100.0:
                bust = 2
            elif rulefloat > 0.0 and rule_losers and (not float_losers) and worst_l <= -fbasis * rulefloat / 100.0 \
                    and worst > -fbasis * floatstop / 100.0:
                bust = 2                                   # Verlierer ueber 1 %, Netto-Bremse greift nicht
            elif ruleday > 0.0 and bal + gap - day_ref <= -day_ref * ruleday / 100.0:
                bust = 3
            if bust > 0:
                for k in range(NSLOT):
                    if p_on[k]:
                        pnl = p_w[k]
                        bal += pnl; st[2] += pnl
                        p_on[k] = False
                    w_on[k] = False
                if n_out < MAXEV:
                    out_ev[n_out, 0] = 2.0; out_ev[n_out, 1] = float(days[dayidx]); out_ev[n_out, 2] = bal - start
                    out_ev[n_out, 3] = float(bust); out_ev[n_out, 4] = float(p); out_ev[n_out, 5] = gap_l
                    n_out += 1
                st[5] += 1
                st[5 + bust] += 1
                mode = 3; wait = rebuydelay
                cur_streak = 0; cons_loss = 0; cur_lday = 0; nz_pend = False; tr_done = n_tr
                if dayidx + 1 < nd:
                    p = day_first[dayidx + 1]
                    if p > end_ev:
                        p = end_ev
                else:
                    p = end_ev
                if p >= end_ev:
                    break
                dbi = db_next[p]; ri = r_next[p]; zi = z_next[p]
                continue
            # --- EA-Bremsen
            lim_f = -fbasis * floatstop / 100.0
            wsum = worst_l if float_losers else worst
            if floatstop > 0.0 and wsum <= lim_f:
                st[20] += 1
                target = -fbasis * (floatstop + brakeslip) / 100.0
                if target < wsum:
                    target = wsum
                ratio = target / wsum if wsum < 0.0 else 1.0
                if floatgestuft:
                    # groesster Verlierer zuerst; danach die verbleibenden Positionen erneut an ihrem
                    # schlechtesten Kurs pruefen (tickgenaue Bremse), bis ihr Buchverlust ueber der Grenze liegt
                    rem = target
                    while True:
                        wsum_r = 0.0
                        for k in range(NSLOT):
                            if p_on[k] and (p_w[k] < 0.0 or not float_losers):
                                wsum_r += p_w[k]
                        if wsum_r > lim_f:
                            break
                        tgt_r = target if wsum_r < target else wsum_r
                        ratio = tgt_r / wsum_r if wsum_r < 0.0 else 1.0
                        wk = -1; wv = 0.0
                        for k in range(NSLOT):
                            if p_on[k] and p_w[k] * ratio < wv:
                                wv = p_w[k] * ratio; wk = k
                        if wk < 0:
                            break
                        k = wk
                        pnl = p_w[k] * ratio
                        bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
                        tot = p_acc[k] + pnl - p_comm[k]
                        if n_tr < MAXTR:
                            out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                            n_tr += 1
                        if k < 2:
                            st[12] += 1; st[13] += tot
                        elif k < NZ0:
                            st[14] += 1; st[15] += tot
                        else:
                            st[16] += 1; st[17] += tot
                        losses[k] += 1
                        cur_streak += 1
                        if cur_streak > max_streak:
                            max_streak = cur_streak
                        if cur_streak == 5:
                            st[27] += 1
                        if cur_streak == 8:
                            st[28] += 1
                        p_on[k] = False
                        rem -= wv
                        # verbleibende Positionen: schlechtester Kurs bleibt p_w (Kerze laeuft weiter)
                else:
                    for k in range(NSLOT):
                        if p_on[k]:
                            pnl = p_w[k] * ratio
                            bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
                            tot = p_acc[k] + pnl - p_comm[k]
                            if n_tr < MAXTR:
                                out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                                n_tr += 1
                            losses[k] += 1
                            cur_streak += 1
                            if cur_streak > max_streak:
                                max_streak = cur_streak
                            p_on[k] = False
            else:
                dstop = -start * daystop / 100.0
                if daylossmax > 0.0 and -start * daylossmax / 100.0 > dstop:
                    dstop = -start * daylossmax / 100.0
                if bal + worst - day_ref <= dstop and worst < 0.0:
                    st[21] += 1
                    target = (day_ref + dstop - start * brakeslip / 100.0) - bal
                    if target < worst:
                        target = worst
                    ratio = target / worst if worst < 0.0 else 1.0
                    for k in range(NSLOT):
                        if p_on[k]:
                            pnl = p_w[k] * ratio
                            bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
                            tot = p_acc[k] + pnl - p_comm[k]
                            if n_tr < MAXTR:
                                out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                                n_tr += 1
                            if pnl < 0:
                                losses[k] += 1
                            if tot < 0.0:
                                cur_streak += 1
                                if cur_streak > max_streak:
                                    max_streak = cur_streak
                                if cur_streak == 5:
                                    st[27] += 1
                                if cur_streak == 8:
                                    st[28] += 1
                            else:
                                cur_streak = 0
                            p_on[k] = False
                    day_locked = True
            # Tagesstopp-Zustand (auch ohne offene Verluste)
            dstop2 = -start * daystop / 100.0
            if daylossmax > 0.0 and -start * daylossmax / 100.0 > dstop2:
                dstop2 = -start * daylossmax / 100.0
            if bal - day_ref <= dstop2:
                day_locked = True

        # ================================================= Ausstiege (Stop, Ziel, Stop-Nachzug, Zeit)
        for k in range(NSLOT):
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
            closed = False
            if hit_sl:
                px = p_sl[k]
                if d > 0 and o5[sy, ii] < p_sl[k]:
                    px = o5[sy, ii]                               # Gap ueber den Stop
                if d < 0 and o5[sy, ii] + sp > p_sl[k]:
                    px = o5[sy, ii] + sp
                closed = True
            elif hit_tp:
                px = p_tp[k]
                closed = True
            else:
                if k < 2:
                    # DEADBAND: Stop ins Plus ab Tp1R, Teilverkauf, Zeit-Exit
                    lvl = p_ref[k] + d * db_tp1r * p_rd[k]
                    t1hit = (hi >= lvl) if d > 0 else (lo + sp <= lvl)
                    if t1hit and not p_t1[k]:
                        p_t1[k] = True
                        if p_v1[k] > 0.0:
                            frac = p_v1[k] / p_lots[k]
                            pnl = (lvl - p_entry[k]) * d * p_v1[k] * mpp[sy] + p_swap[k] * frac
                            bal += pnl; day_real += pnl; day_had = True; st[2] += pnl
                            p_acc[k] += pnl
                            p_swap[k] *= (1.0 - frac)
                            p_lots[k] = np.round(p_lots[k] - p_v1[k], 2)
                            p_v1[k] = 0.0
                    if t1hit and not p_be[k]:
                        cand = p_ref[k] + d * db_be * p_rd[k]
                        if (cand - p_sl[k]) * d > 0.0:
                            p_sl[k] = cand
                        p_be[k] = True
                    held = grp15[sy, ii] - p_m15[k]
                    if db_maxhold > 0 and held >= db_maxhold:
                        px = c5[sy, ii] + (sp if d < 0 else 0.0); closed = True
                    elif db_trail_from > 0.0 and p_mfe[k] >= db_trail_from:
                        cand = p_ref[k] + d * (p_mfe[k] - db_trail_dist) * p_rd[k]
                        if (cand - p_sl[k]) * d > 0.0:
                            p_sl[k] = cand
                elif k < NZ0:
                    held5 = ii - p_i5[k]
                    tnow = days[dayidx] * 1440 + nymin
                    if (r21_exitbars > 0 and held5 >= r21_exitbars) or (r21_exitdays > 0 and (tnow - p_tmin[k]) >= r21_exitdays * 1440):
                        px = c5[sy, ii] + (sp if d < 0 else 0.0); closed = True
                    else:
                        if r21_tp1r > 0.0 and not p_t1[k]:
                            lvl = p_ref[k] + d * r21_tp1r * p_rd[k]
                            t1hit = (hi >= lvl) if d > 0 else (lo + sp <= lvl)
                            if t1hit:
                                p_t1[k] = True
                                if p_v1[k] > 0.0:
                                    frac = p_v1[k] / p_lots[k]
                                    pnl = (lvl - p_entry[k]) * d * p_v1[k] * mpp[sy] + p_swap[k] * frac
                                    bal += pnl; day_real += pnl; day_had = True; st[2] += pnl
                                    p_acc[k] += pnl
                                    p_swap[k] *= (1.0 - frac)
                                    p_lots[k] = np.round(p_lots[k] - p_v1[k], 2)
                                    p_v1[k] = 0.0
                                cand = p_ref[k] + d * r21_be * p_rd[k]
                                if (cand - p_sl[k]) * d > 0.0:
                                    p_sl[k] = cand
                                p_be[k] = True
                        if r21_trail_from > 0.0 and p_mfe[k] >= r21_trail_from:
                            cand = p_ref[k] + d * (p_mfe[k] - r21_trail_dist) * p_rd[k]
                            if (cand - p_sl[k]) * d > 0.0:
                                p_sl[k] = cand
            if closed:
                pnl = (px - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k]
                bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
                tot = p_acc[k] + pnl - p_comm[k]
                if n_tr < MAXTR:
                    out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                    n_tr += 1
                if k < 2:
                    st[12] += 1; st[13] += tot
                    if tot > 0:
                        st[32] += 1
                elif k < NZ0:
                    st[14] += 1; st[15] += tot
                    if tot > 0:
                        st[33] += 1
                else:
                    st[16] += 1; st[17] += tot
                    if tot > 0:
                        st[34] += 1
                if pnl < 0.0:
                    losses[k] += 1
                if tot < 0.0:
                    cur_streak += 1
                    if cur_streak > max_streak:
                        max_streak = cur_streak
                    if cur_streak == 5:
                        st[27] += 1
                    if cur_streak == 8:
                        st[28] += 1
                else:
                    cur_streak = 0
                p_on[k] = False

        # ================================================= Datenloch (nur Replikat): vor dem Loch neutral schliessen
        for k in range(NSLOT):
            if not p_on[k]:
                continue
            sy = p_sym[k]
            ii = ev_i[sy, p]
            if ii < 0 or not hole5[sy, ii]:
                continue
            px = c5[sy, ii] + (sp5[sy, ii] if p_dir[k] < 0 else 0.0)
            pnl = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[sy] + p_swap[k]
            bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
            tot = p_acc[k] + pnl - p_comm[k]
            if n_tr < MAXTR:
                out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                n_tr += 1
            p_on[k] = False
            w_on[k] = False

        # ================================================= Swap-Vorsorge (Forschung): vor 17:00 NY
        if swap_guard > 0.0 and nymin >= 16 * 60 + 50 and nymin < 17 * 60 and not we_now:
            tripl = 3.0 if day_dow[dayidx] == 3 else 1.0
            lossum = 0.0
            for k in range(NSLOT):
                if p_on[k]:
                    sy = p_sym[k]
                    ii = ev_i[sy, p]
                    px = p_last[k] + ((sp5[sy, ii] if ii >= 0 else 0.0) if p_dir[k] < 0 else 0.0)
                    if sy == 0:
                        swn = (-64.47 if p_dir[k] > 0 else 23.84) * p_lots[k] * tripl
                    else:
                        swn = p_entry[k] * 10.0 * p_lots[k] * ((-3.0 if p_dir[k] > 0 else -1.5) / 100.0 / 360.0) * tripl
                    v = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[sy] + p_swap[k] + swn
                    if v < 0.0:
                        lossum += v
            lim_s = -fbasis * swap_guard / 100.0
            while lossum <= lim_s:
                wk = -1; wv = 0.0
                for k in range(NSLOT):
                    if p_on[k]:
                        sy = p_sym[k]
                        ii = ev_i[sy, p]
                        px = p_last[k] + ((sp5[sy, ii] if ii >= 0 else 0.0) if p_dir[k] < 0 else 0.0)
                        if sy == 0:
                            swn = (-64.47 if p_dir[k] > 0 else 23.84) * p_lots[k] * tripl
                        else:
                            swn = p_entry[k] * 10.0 * p_lots[k] * ((-3.0 if p_dir[k] > 0 else -1.5) / 100.0 / 360.0) * tripl
                        v = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[sy] + p_swap[k] + swn
                        if v < wv:
                            wv = v; wk = k
                if wk < 0:
                    break
                k = wk
                sy = p_sym[k]
                ii = ev_i[sy, p]
                px = p_last[k] + ((sp5[sy, ii] if ii >= 0 else 0.0) if p_dir[k] < 0 else 0.0)
                pnl = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[sy] + p_swap[k]
                bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
                tot = p_acc[k] + pnl - p_comm[k]
                if n_tr < MAXTR:
                    out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                    n_tr += 1
                if pnl < 0.0:
                    losses[k] += 1
                if tot < 0.0:
                    cur_streak += 1
                    if cur_streak > max_streak:
                        max_streak = cur_streak
                else:
                    cur_streak = 0
                p_on[k] = False
                lossum -= wv
                st[46] += 1

        # ================================================= Ernte (gueltigen Tag sichern)
        anydb = False; fltdb = 0.0
        for k in range(NZ0):
            if p_on[k]:
                pl = (p_last[k] + (sp5[p_sym[k], max(ev_i[p_sym[k], p], 0)] if p_dir[k] < 0 else 0.0) - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[p_sym[k]] + p_swap[k]
                if k < 2:
                    fltdb += pl
                    anydb = True
        if harvest > 0 and not day_locked and day_real < needday and (fltdb > 0.0 or harv_any_mods > 0):
            fenster = (harvest == 1) or (harvest == 2 and nyh >= harvfrom and nyh < 17.0)
            need = needday * (1.0 + harvmargin)
            st2 = fenster and harvminr2 > 0.0 and (need - day_real) <= harvgap * needday
            flt_cond = fltdb if harv_any_mods == 0 else 1e18
            if fenster and day_real + flt_cond >= need:
                gain = 0.0
                kmax = NZ0
                for k in range(kmax):
                    if not p_on[k]:
                        continue
                    ii = ev_i[p_sym[k], p]
                    if ii < 0:
                        continue
                    px = c5[p_sym[k], ii] + (sp5[p_sym[k], ii] if p_dir[k] < 0 else 0.0)
                    pl = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[p_sym[k]] + p_swap[k]
                    kand = (p_mfe[k] >= harvminr) or (st2 and p_mfe[k] >= harvminr2)
                    if pl > 0.0 and kand:
                        gain += pl
                if day_real + gain >= need:
                    for k in range(kmax):
                        if not p_on[k]:
                            continue
                        sy = p_sym[k]
                        ii = ev_i[sy, p]
                        if ii < 0:
                            continue
                        px = c5[sy, ii] + (sp5[sy, ii] if p_dir[k] < 0 else 0.0)
                        pl = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[sy] + p_swap[k]
                        kand = (p_mfe[k] >= harvminr) or (st2 and p_mfe[k] >= harvminr2)
                        if pl <= 0.0 or not kand:
                            continue
                        lots = p_lots[k]
                        if harvpartial:
                            perlot = pl / p_lots[k]
                            lots = np.ceil((need - day_real) / perlot / 0.01 - 1e-9) * 0.01
                            if lots < 0.01:
                                lots = 0.01
                            if lots > p_lots[k] - 0.01:
                                lots = p_lots[k]
                            lots = np.round(lots, 2)
                        st[18] += 1
                        if lots >= p_lots[k]:
                            pnl = pl
                            bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
                            tot = p_acc[k] + pnl - p_comm[k]
                            if n_tr < MAXTR:
                                out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                                n_tr += 1
                            if k < 2:
                                st[12] += 1; st[13] += tot
                                if tot > 0:
                                    st[32] += 1
                            else:
                                st[14] += 1; st[15] += tot
                                if tot > 0:
                                    st[33] += 1
                            if tot < 0.0:
                                cur_streak += 1
                                if cur_streak > max_streak:
                                    max_streak = cur_streak
                            else:
                                cur_streak = 0
                            p_on[k] = False
                        else:
                            frac = lots / p_lots[k]
                            pnl = (px - p_entry[k]) * p_dir[k] * lots * mpp[sy] + p_swap[k] * frac
                            bal += pnl; day_real += pnl; day_had = True; st[2] += pnl
                            p_acc[k] += pnl
                            p_swap[k] *= (1.0 - frac)
                            p_lots[k] = np.round(p_lots[k] - lots, 2)
                        if day_real >= need:
                            break

        # ================================================= Banking (Forschung): Tag sofort gueltig machen
        bank_ok = bank_on
        if bank_on and bank_last > 0:
            vbl = valid_days + (1 if (day_had and day_real >= needday) else 0)
            bank_ok = (cyc_start >= 0) and (vbl >= needvalid - bank_last) and (bal - start >= minprofit * bank_prof)
        if bank_ok and not day_locked and day_real < needday and nyh >= bank_from and nyh < bank_to and mode <= 1:
            need = needday * (1.0 + bank_margin)
            gain = 0.0
            for k in range(NSLOT):
                if not p_on[k]:
                    continue
                if k < 2 and (bank_mods & 1) == 0:
                    continue
                if k >= 2 and k < NZ0 and (bank_mods & 2) == 0:
                    continue
                if k >= NZ0 and (bank_mods & 4) == 0:
                    continue
                sy = p_sym[k]
                ii = ev_i[sy, p]
                if ii < 0:
                    continue
                px = c5[sy, ii] + (sp5[sy, ii] if p_dir[k] < 0 else 0.0)
                pl = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[sy] + p_swap[k]
                if pl > 0.0 and p_mfe[k] >= bank_minr:
                    gain += pl
            if day_real + gain >= need:
                for k in range(NSLOT):
                    if not p_on[k]:
                        continue
                    if k < 2 and (bank_mods & 1) == 0:
                        continue
                    if k >= 2 and k < NZ0 and (bank_mods & 2) == 0:
                        continue
                    if k >= NZ0 and (bank_mods & 4) == 0:
                        continue
                    sy = p_sym[k]
                    ii = ev_i[sy, p]
                    if ii < 0:
                        continue
                    px = c5[sy, ii] + (sp5[sy, ii] if p_dir[k] < 0 else 0.0)
                    pl = (px - p_entry[k]) * p_dir[k] * p_lots[k] * mpp[sy] + p_swap[k]
                    if pl <= 0.0 or p_mfe[k] < bank_minr:
                        continue
                    perlot = pl / p_lots[k]
                    lots = np.ceil((need - day_real) / perlot / 0.01 - 1e-9) * 0.01
                    if lots < 0.01:
                        lots = 0.01
                    if lots > p_lots[k] - 0.01:
                        lots = p_lots[k]
                    lots = np.round(lots, 2)
                    st[36] += 1
                    if lots >= p_lots[k]:
                        pnl = pl
                        bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
                        tot = p_acc[k] + pnl - p_comm[k]
                        if n_tr < MAXTR:
                            out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                            n_tr += 1
                        if k < 2:
                            st[12] += 1; st[13] += tot
                            if tot > 0:
                                st[32] += 1
                        elif k < NZ0:
                            st[14] += 1; st[15] += tot
                            if tot > 0:
                                st[33] += 1
                        else:
                            st[16] += 1; st[17] += tot
                            if tot > 0:
                                st[34] += 1
                        if tot < 0.0:
                            cur_streak += 1
                            if cur_streak > max_streak:
                                max_streak = cur_streak
                        else:
                            cur_streak = 0
                        p_on[k] = False
                    else:
                        frac = lots / p_lots[k]
                        pnl = (px - p_entry[k]) * p_dir[k] * lots * mpp[sy] + p_swap[k] * frac
                        bal += pnl; day_real += pnl; day_had = True; st[2] += pnl
                        p_acc[k] += pnl
                        p_swap[k] *= (1.0 - frac)
                        p_lots[k] = np.round(p_lots[k] - lots, 2)
                    if day_real >= need:
                        break

        # ================================================= Gewinn-Ernte (nur der Mindestgewinn fehlt)
        vh = valid_days + (1 if (day_had and day_real >= needday) else 0)
        if ge_on and mode == 0 and cyc_start >= 0 and vh >= needvalid and (days[dayidx] - cyc_start) >= cycledays \
                and bal - start < minprofit and nyh < 17.0:
            ziel = start + minprofit * (1.0 + ge_auf)
            fehlt = ziel - bal
            gain = 0.0
            for k in range(NZ0):
                if not p_on[k]:
                    continue
                sy = p_sym[k]
                ii = ev_i[sy, p]
                if ii < 0:
                    continue
                d = p_dir[k]
                bid = c5[sy, ii]; ask = bid + sp5[sy, ii]
                favR = (bid - p_ref[k]) / p_rd[k] if d > 0 else (p_ref[k] - ask) / p_rd[k]
                px = bid if d > 0 else ask
                pl = (px - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k] - comm[sy] * p_lots[k]
                okk = pl > 0.0 and p_mfe[k] >= ge_minr and (p_mfe[k] - favR >= ge_rueck or ge_mode == 1)
                if okk:
                    gain += pl
            if gain >= fehlt and fehlt > 0.0:
                for k in range(NZ0):
                    if not p_on[k]:
                        continue
                    sy = p_sym[k]
                    ii = ev_i[sy, p]
                    if ii < 0:
                        continue
                    d = p_dir[k]
                    bid = c5[sy, ii]; ask = bid + sp5[sy, ii]
                    favR = (bid - p_ref[k]) / p_rd[k] if d > 0 else (p_ref[k] - ask) / p_rd[k]
                    px = bid if d > 0 else ask
                    pl = (px - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k] - comm[sy] * p_lots[k]
                    okk = pl > 0.0 and p_mfe[k] >= ge_minr and (p_mfe[k] - favR >= ge_rueck or ge_mode == 1)
                    if not okk:
                        continue
                    pnl = (px - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k]
                    bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
                    tot = p_acc[k] + pnl - p_comm[k]
                    if n_tr < MAXTR:
                        out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                        n_tr += 1
                    if k < 2:
                        st[12] += 1; st[13] += tot
                        if tot > 0:
                            st[32] += 1
                    else:
                        st[14] += 1; st[15] += tot
                        if tot > 0:
                            st[33] += 1
                    cur_streak = 0
                    st[19] += 1
                    p_on[k] = False
                    if bal >= ziel:
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
            if mode == 0 and ripe:
                mode = 1
                tday = cyc_start + cycledays
                lv = v5_day if v5_day >= 0 else days[dayidx]
                lp = pr_day if pr_day >= 0 else days[dayidx]
                if lv >= lp and lv >= tday:
                    st[41] += 1
                elif lp >= lv and lp >= tday:
                    st[42] += 1
                else:
                    st[43] += 1
                st[44] += float(lv - cyc_start); st[45] += float(lp - cyc_start)
            if mode == 1:
                # RSI21 und Noise bei Reife schliessen; DEADBAND je stopmode
                for k in range(2, NSLOT):
                    if not p_on[k]:
                        continue
                    if k < NZ0 and not r21_ripeclose:
                        continue
                    if k >= NZ0 and not nz_ripeclose:
                        continue
                    sy = p_sym[k]
                    ii = ev_i[sy, p]
                    if ii < 0:
                        continue
                    d = p_dir[k]
                    px = c5[sy, ii] + (sp5[sy, ii] if d < 0 else 0.0)
                    pnl = (px - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k]
                    if ripe_mode == 1 and pnl < 0.0:
                        continue
                    bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
                    tot = p_acc[k] + pnl - p_comm[k]
                    if n_tr < MAXTR:
                        out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                        n_tr += 1
                    if k < NZ0:
                        st[14] += 1; st[15] += tot
                        if tot > 0:
                            st[33] += 1
                    else:
                        st[16] += 1; st[17] += tot
                        if tot > 0:
                            st[34] += 1
                    if tot < 0.0:
                        cur_streak += 1
                        if cur_streak > max_streak:
                            max_streak = cur_streak
                        if cur_streak == 5:
                            st[27] += 1
                        if cur_streak == 8:
                            st[28] += 1
                    else:
                        cur_streak = 0
                    p_on[k] = False
                if stopmode >= 1:
                    for k in range(2):
                        if not p_on[k]:
                            continue
                        sy = p_sym[k]
                        ii = ev_i[sy, p]
                        if ii < 0:
                            continue
                        d = p_dir[k]
                        px = c5[sy, ii] + (sp5[sy, ii] if d < 0 else 0.0)
                        pnl = (px - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k]
                        if stopmode == 2 and pnl <= 0.0:
                            continue
                        vv2 = valid_days + (1 if (day_had and day_real + pnl >= needday) else 0)
                        if vv2 < needvalid or bal + pnl - start < minprofit:
                            continue
                        bal += pnl; day_real += pnl - p_comm[k]; day_had = True; st[2] += pnl
                        tot = p_acc[k] + pnl - p_comm[k]
                        if n_tr < MAXTR:
                            out_tr[n_tr, 0] = float(days[dayidx]); out_tr[n_tr, 1] = tot; out_tr[n_tr, 2] = float(k); out_tr[n_tr, 3] = float(p_tmin[k])
                            n_tr += 1
                        st[12] += 1; st[13] += tot
                        if tot > 0:
                            st[32] += 1
                        if tot < 0:
                            cur_streak += 1
                        else:
                            cur_streak = 0
                        p_on[k] = False
                anyon = False; wwait = False
                for k in range(NSLOT):
                    if p_on[k]:
                        anyon = True
                    if w_on[k]:
                        wwait = True
                if (not anyon) and not (we_reif and wwait):
                    vh = valid_days + (1 if (day_had and day_real >= needday) else 0)
                    ripe = (vh >= needvalid) and (cyc_start >= 0) and (days[dayidx] - cyc_start >= cycledays) and (bal - start >= minprofit)
                    if ripe:
                        mode = 2; wait = paydelay
                        for k in range(NSLOT):
                            w_on[k] = False
                    else:
                        mode = 0
                        st[35] += 1

        # Serienzaehler aus dem Trade-Protokoll: Noise-Teile eines Signals = ein Trade
        while tr_done < n_tr:
            slot_ = int(out_tr[tr_done, 2]); res_ = out_tr[tr_done, 1]; pid_ = out_tr[tr_done, 3]
            tr_done += 1
            if slot_ >= NZ0:
                if nz_pend and pid_ == nz_pid:
                    nz_sum += res_
                else:
                    if nz_pend:
                        if nz_sum < 0.0:
                            cons_loss += 1
                        else:
                            cons_loss = 0
                    nz_pid = pid_; nz_sum = res_; nz_pend = True
            else:
                if res_ < 0.0:
                    cons_loss += 1
                else:
                    cons_loss = 0
        if nz_pend:
            still = False
            for k in range(NZ0, NSLOT):
                if p_on[k] and float(p_tmin[k]) == nz_pid:
                    still = True
            if not still:
                if nz_sum < 0.0:
                    cons_loss += 1
                else:
                    cons_loss = 0
                nz_pend = False
        # Pause nach Verlustserie (jede Verlust-Schliessung zaehlt, auch Bremse/Noise/Wochenende)
        if cool_n > 0 and cons_loss >= cool_n:
            cool_until = days[dayidx] + cool_days
            st[37] += 1
            cons_loss = 0

        # Kontokurve (realisiert) fuer Drawdown innerhalb der Zyklen
        if bal > bal_peak_c:
            bal_peak_c = bal
        if bal_peak_c - bal > maxdd:
            maxdd = bal_peak_c - bal

        # ================================================= weiter
        anyon = False
        for k in range(NSLOT):
            if p_on[k]:
                anyon = True
        if not anyon:
            nxt = end_ev
            if mode == 0:
                if dbi < ndb and db_ev[dbi] < nxt:
                    nxt = db_ev[dbi]
                if ri < nr and r_ev[ri] < nxt:
                    nxt = r_ev[ri]
                if zi < nzc and z_ev[zi] < nxt and z_ev[zi] > p:
                    nxt = z_ev[zi]
            if dayidx + 1 < nd:
                jump = day_first[dayidx + 1]
                if jump < nxt:
                    nxt = jump
            # Wochenend-Wiederaufnahme: Sonntag 18:00 ist ohnehin ein neuer Tag
            if nxt <= p:
                nxt = p + 1
            p = nxt
            if p >= end_ev:
                break
            continue
        p += 1

    st[26] = max_streak; st[29] = max_lday; st[31] = maxdd
    st[38] = gaps_max; st[39] = gaps_sum
    # offene Luecke bis zum Ende zaehlt fuer gaps_max
    if end_ev > 0:
        endday = days[min(ev_day[min(end_ev, n_ev) - 1], nd - 1)]
        g_ = float(endday - last_pay_day)
        if g_ > st[38]:
            st[38] = g_
    return n_out, n_tr


# ------------------------------------------------------------------ Wrapper
def make_masks(mk, seed, frac):
    rng = np.random.default_rng(seed)
    if frac <= 0.0:
        return (np.zeros(len(mk.db["ev"]), np.bool_), np.zeros(len(mk.r21["ev"]), np.bool_),
                np.zeros(len(mk.nz["ev"]), np.bool_))
    return (rng.random(len(mk.db["ev"])) < frac, rng.random(len(mk.r21["ev"])) < frac, rng.random(len(mk.nz["ev"])) < frac)


def run(mk, Pv, d0, d1, seed=0, skip=0.0, masks=None):
    out = np.zeros((MAXEV, 6)); tr = np.zeros((MAXTR, 4)); st = np.zeros(len(ST))
    if masks is None:
        masks = make_masks(mk, seed, skip)
    ne, nt = run_path(Pv, int(d0), int(d1), int(seed),
                      mk.ev_i, mk.ev_day, mk.ev_nymin, mk.ev_dow, mk.days, mk.day_first, mk.day_dow,
                      mk.o5, mk.h5, mk.l5, mk.c5, mk.sp5, mk.grp15, mk.gap5, mk.hole5,
                      mk.db["ev"], mk.db["sym"], mk.db["dir"], mk.db["rd"], mk.db["f"], mk.db["m15"], mk.db["nyh"], mk.db["next"],
                      mk.r21["ev"], mk.r21["sym"], mk.r21["tf"], mk.r21["dir"], mk.r21["rd"], mk.r21["first"], mk.r21["next"],
                      mk.nz["ev"], mk.nz["em"], mk.nz["close"], mk.nz["UB"], mk.nz["vw"], mk.nz["dist"], mk.nz["entry_ok"],
                      mk.nz["next"], mk.ev_nzeod,
                      masks[0], masks[1], masks[2], out, tr, st)
    d1c = min(d1, len(mk.days) - 1)
    yrs = (mk.days[d1c] - mk.days[d0]) / 365.25
    return dict(st=st, ev=out[:ne].copy(), tr=tr[:nt].copy(), years=yrs)
