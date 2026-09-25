"""RSI21-Labor: Positions-Simulator je Symbol (ohne Konto) und Kennzahlen.

Konventionen wie eng6 (RSI21-Plaetze):
  - Einstieg am Open der M5-Kerze des Signals, Long zum Ask (Bid + Spread), Short zum Bid
  - Stop vor Ziel in derselben Kerze, Gap ueber den Stop zum Open, Ziel auch in der Einstiegskerze
  - Zeit-Exit am Schluss der Kerze, in der N M5-Kerzen bzw. N Tage erreicht sind (nach Stop/Ziel)
  - Platz A, Platz B (nur in Richtung von A), je Kerze ohne Platz B nur ein Einstieg
  - hoechstens `maxloss` Verluste je Servertag (17:00 NY) und Symbol, keine Gegenposition (Hedging-Sperre)
  - Freitag ab `we_close` (NY) schliessen, Sonntag ab 18:00 NY wieder aufnehmen, wenn der Kurs zwischen Stop und
    Ziel liegt (Stop hoechstens `we_stopmaxr` R vom neuen Einstieg); verfaellt ab Dienstag
  - Swap je Nacht (Servertag), mittwochs dreifach; Kommission je Lot (in Preis-Einheiten je Einheit)
R je Trade = Summe aller Teile (auch Wiederaufnahme) / Stop-Abstand beim Einstieg, inkl. Spread, Swap, Kommission."""
import numpy as np
from numba import njit

# Swap wie eng6 (GFT-Stand): Gold in USD je Lot und Nacht (100 Unzen), NAS in % p. a. vom Kurs
SWAP_XAU = (-0.6447, 0.2384)          # Preis-Einheiten je Einheit und Nacht (long, short)
SWAP_NAS = (-0.03 / 360.0, -0.015 / 360.0)
COMM = {"XAU": 5.0 / 100.0, "NAS": 0.0}   # 5 $/Lot bei 100 $/Punkt


@njit(cache=True)
def _sim(o, h, l, c, sp, ny, ci5, cdir, crd, ctp, ctf, cw,
         second, maxloss, exitbars, exitdays, we_on, we_close, we_stopmaxr,
         trail_from, trail_dist, be_at, be_to, comm_px, sw_l, sw_s, sw_rel, xb_arr, xb_on, add_min, add_be, ts_bars, ts_mfe):
    n = o.shape[0]
    nc = ci5.shape[0]
    MAXT = nc + 10
    # Trade-Protokoll: i_entry, i_exit, dir, tf, slot, R, w, grund, mfe, mae, teile
    T_ie = np.zeros(MAXT, np.int64); T_ix = np.zeros(MAXT, np.int64); T_d = np.zeros(MAXT, np.int64)
    T_tf = np.zeros(MAXT, np.int64); T_sl = np.zeros(MAXT, np.int64); T_R = np.zeros(MAXT)
    T_w = np.zeros(MAXT); T_why = np.zeros(MAXT, np.int64); T_mfe = np.zeros(MAXT); T_mae = np.zeros(MAXT)
    T_parts = np.zeros(MAXT, np.int64)
    nt = 0
    # Positionen (2 Plaetze)
    on = np.zeros(2, np.bool_); d_ = np.zeros(2, np.int64); ent = np.zeros(2); sl = np.zeros(2); tp = np.zeros(2)
    rd = np.zeros(2); ref = np.zeros(2); mfe = np.zeros(2); mae = np.zeros(2); i0 = np.zeros(2, np.int64)
    t0 = np.zeros(2, np.int64); tid = np.zeros(2, np.int64); acc = np.zeros(2); swap = np.zeros(2)
    # Vormerkung Wochenende
    won = np.zeros(2, np.bool_); wday = np.zeros(2, np.int64)
    losses = 0
    ci = 0
    if nc == 0:
        return T_ie[:0], T_ix[:0], T_d[:0], T_tf[:0], T_sl[:0], T_R[:0], T_w[:0], T_why[:0], T_mfe[:0], T_mae[:0], T_parts[:0]
    j0 = ci5[0]
    pday_prev = (ny[j0] + 420) // 1440
    for j in range(j0, n):
        t = ny[j]
        nymin = t % 1440
        nyh = nymin / 60.0
        dow = ((t // 1440) + 4) % 7                 # 0 = Sonntag (NY-Kalendertag)
        pday = (t + 420) // 1440
        if pday != pday_prev:
            # Tageswechsel: Swap fuer offene Positionen (Mittwoch-Servertag dreifach), Verlustzaehler zuruecksetzen
            mult = 3.0 if ((pday_prev + 4) % 7) == 3 else 1.0
            nd = pday - pday_prev
            if nd > 3:
                nd = 1
            for k in range(2):
                if on[k]:
                    if sw_rel:
                        r_ = sw_l if d_[k] > 0 else sw_s
                        swap[k] += r_ * ent[k] * mult
                    else:
                        swap[k] += (sw_l if d_[k] > 0 else sw_s) * mult
            losses = 0
            pday_prev = pday
        s_ = sp[j]
        # --- Freitag: Wochenend-Schluss am Open
        we_now = we_on and dow == 5 and nyh >= we_close
        if we_now:
            for k in range(2):
                if not on[k]:
                    continue
                px = o[j] + (s_ if d_[k] < 0 else 0.0)
                part = (px - ent[k]) * d_[k] + swap[k]
                acc[k] += part
                q = tid[k]
                T_ix[q] = j; T_R[q] = (acc[k] - comm_px * T_parts[q]) / rd[k]; T_why[q] = 3
                T_mfe[q] = mfe[k]; T_mae[q] = mae[k]
                if part < 0.0:
                    losses += 1
                on[k] = False
                won[k] = True; wday[k] = pday
        # Vormerkungen verfallen
        for k in range(2):
            if won[k]:
                seit = pday - wday[k]
                if (dow >= 2 and dow <= 4 and seit >= 3) or seit >= 6:
                    won[k] = False
        # --- Sonntag-/Montag-Wiederaufnahme
        if we_on and (dow == 0 and nyh >= 18.0 or dow == 1):
            for k in range(2):
                if not won[k] or on[k]:
                    continue
                q = tid[k]
                dd = d_[k]
                hed = False
                for m in range(2):
                    if on[m] and d_[m] != dd:
                        hed = True
                if hed:
                    continue
                bid = o[j]; ask = bid + s_
                e = ask if dd > 0 else bid
                chk = bid if dd > 0 else ask
                won[k] = False
                if (dd > 0 and chk <= sl[k]) or (dd < 0 and chk >= sl[k]):
                    continue
                if tp[k] > 0.0 and ((dd > 0 and chk >= tp[k]) or (dd < 0 and chk <= tp[k])):
                    continue
                nsl = sl[k]
                if we_stopmaxr > 0.0:
                    tight = e - dd * we_stopmaxr * rd[k]
                    if (dd > 0 and tight > nsl) or (dd < 0 and tight < nsl):
                        nsl = tight
                on[k] = True; ent[k] = e; sl[k] = nsl; swap[k] = 0.0
                T_parts[q] += 1; T_why[q] = -1
        # --- Einstiege am Open
        entries_ok = not (we_on and dow == 5 and nyh >= we_close - 5.0 / 60.0)
        while ci < nc and ci5[ci] < j:
            ci += 1
        took_bar = False
        while ci < nc and ci5[ci] == j:
            a = ci
            ci += 1
            if not entries_ok or took_bar:
                continue
            if maxloss > 0 and losses >= maxloss:
                continue
            dd = cdir[a]
            ke = -1
            if not on[0]:
                if not won[0]:
                    ke = 0
            elif second:
                if d_[0] == dd and (not on[1]) and (not won[1]):
                    favA = ((o[j] + (0.0 if dd > 0 else s_)) - ref[0]) * dd / rd[0]
                    if add_min <= -9.0 or favA >= add_min:
                        ke = 1
                        if add_be > -9.0:
                            cand = ref[0] + dd * add_be * rd[0]
                            if (cand - sl[0]) * dd > 0.0 and (o[j] - cand) * dd > 0.0:
                                sl[0] = cand
            if ke < 0:
                continue
            hed = False
            for m in range(2):
                if on[m] and d_[m] != dd:
                    hed = True
                if won[m] and m != ke and d_[m] != dd:
                    hed = True
            if hed:
                continue
            e = o[j] + (s_ if dd > 0 else 0.0)
            r_ = crd[a]
            on[ke] = True; d_[ke] = dd; ent[ke] = e; rd[ke] = r_; ref[ke] = e
            sl[ke] = e - dd * r_
            tp[ke] = e + dd * ctp[a] * r_ if ctp[a] > 0.0 else 0.0
            mfe[ke] = 0.0; mae[ke] = 0.0; i0[ke] = j; t0[ke] = t; acc[ke] = 0.0; swap[ke] = 0.0
            q = nt
            nt += 1
            tid[ke] = q
            T_ie[q] = j; T_d[q] = dd; T_tf[q] = ctf[a]; T_sl[q] = ke; T_w[q] = cw[a]; T_parts[q] = 1; T_why[q] = -1
            if not second:
                took_bar = True
        # --- Ausstiege in der Kerze
        for k in range(2):
            if not on[k]:
                continue
            dd = d_[k]
            lo = l[j]; hi = h[j]
            if dd > 0:
                fav = (hi - ref[k]) / rd[k]; adv = (ref[k] - lo) / rd[k]
                hit_sl = lo <= sl[k]
                hit_tp = tp[k] > 0.0 and hi >= tp[k]
            else:
                fav = (ref[k] - (lo + s_)) / rd[k]; adv = ((hi + s_) - ref[k]) / rd[k]
                hit_sl = hi + s_ >= sl[k]
                hit_tp = tp[k] > 0.0 and lo + s_ <= tp[k]
            closed = False
            px = 0.0
            why = 0
            if hit_sl:
                px = sl[k]
                if dd > 0 and o[j] < sl[k]:
                    px = o[j]
                if dd < 0 and o[j] + s_ > sl[k]:
                    px = o[j] + s_
                closed = True; why = 1
                if adv > mae[k]:
                    mae[k] = adv
            elif hit_tp:
                px = tp[k]; closed = True; why = 2
                if fav > mfe[k]:
                    mfe[k] = fav
            else:
                if fav > mfe[k]:
                    mfe[k] = fav
                if adv > mae[k]:
                    mae[k] = adv
                held = j - i0[k]
                if (exitbars > 0 and held >= exitbars) or (exitdays > 0 and (t - t0[k]) >= exitdays * 1440):
                    px = c[j] + (s_ if dd < 0 else 0.0); closed = True; why = 0
                elif xb_on and xb_arr[j] * dd < 0:
                    px = c[j] + (s_ if dd < 0 else 0.0); closed = True; why = 4
                elif ts_bars > 0 and held >= ts_bars and held < ts_bars + 1 and mfe[k] < ts_mfe:
                    px = c[j] + (s_ if dd < 0 else 0.0); closed = True; why = 6
                else:
                    if be_at > 0.0 and mfe[k] >= be_at:
                        cand = ref[k] + dd * be_to * rd[k]
                        if (cand - sl[k]) * dd > 0.0:
                            sl[k] = cand
                    if trail_from > 0.0 and mfe[k] >= trail_from:
                        cand = ref[k] + dd * (mfe[k] - trail_dist) * rd[k]
                        if (cand - sl[k]) * dd > 0.0:
                            sl[k] = cand
            if closed:
                part = (px - ent[k]) * dd + swap[k]
                acc[k] += part
                q = tid[k]
                T_ix[q] = j; T_R[q] = (acc[k] - comm_px * T_parts[q]) / rd[k]; T_why[q] = why
                T_mfe[q] = mfe[k]; T_mae[q] = mae[k]
                if part < 0.0:
                    losses += 1
                on[k] = False
    # offene Positionen am Datenende: zum letzten Schluss
    for k in range(2):
        if on[k]:
            q = tid[k]
            px = c[n - 1] + (sp[n - 1] if d_[k] < 0 else 0.0)
            acc[k] += (px - ent[k]) * d_[k] + swap[k]
            T_ix[q] = n - 1; T_R[q] = (acc[k] - comm_px * T_parts[q]) / rd[k]; T_why[q] = 5
            T_mfe[q] = mfe[k]; T_mae[q] = mae[k]
    # Trades, deren letzter Teil am Freitag endete, ohne Wiederaufnahme: Grund 3 bleibt stehen
    return (T_ie[:nt], T_ix[:nt], T_d[:nt], T_tf[:nt], T_sl[:nt], T_R[:nt], T_w[:nt], T_why[:nt], T_mfe[:nt],
            T_mae[:nt], T_parts[:nt])


def simulate(d, sym, cand, second=True, maxloss=2, exitbars=1152, exitdays=8, we_on=True, we_close=16.75, we_stopmaxr=2.0,
             trail_from=0.0, trail_dist=0.0, be_at=0.0, be_to=0.0, swap=True, xb=None, add_min=-99.0, add_be=-99.0, ts_bars=0, ts_mfe=0.0):
    """d: Kursdaten eines Symbols (r7data), cand: dict mit i5, dir, rd, tp, tf, w (nach i5, tf sortiert)."""
    if swap:
        sw = SWAP_XAU if sym == "XAU" else SWAP_NAS
    else:
        sw = (0.0, 0.0)
    xb_on = xb is not None
    xb_arr = np.asarray(xb, np.int64) if xb_on else np.zeros(1, np.int64)
    out = _sim(d["o"], d["h"], d["l"], d["c"], d["sp"], d["ny"], np.asarray(cand["i5"], np.int64), np.asarray(cand["dir"], np.int64),
               np.asarray(cand["rd"], float), np.asarray(cand["tp"], float), np.asarray(cand["tf"], np.int64), np.asarray(cand["w"], float),
               bool(second), int(maxloss), int(exitbars), float(exitdays), bool(we_on), float(we_close), float(we_stopmaxr),
               float(trail_from), float(trail_dist), float(be_at), float(be_to), COMM[sym], float(sw[0]), float(sw[1]), sym == "NAS",
               xb_arr, xb_on, float(add_min), float(add_be), int(ts_bars), float(ts_mfe))
    keys = ("ie", "ix", "dir", "tf", "slot", "R", "w", "why", "mfe", "mae", "parts")
    tr = dict(zip(keys, out))
    tr["t"] = d["ny"][tr["ie"]]
    tr["sym"] = np.full(len(tr["R"]), 0 if sym == "XAU" else 1)
    return tr


def merge(trs):
    keys = trs[0].keys()
    m = {k: np.concatenate([t[k] for t in trs]) for k in keys}
    o = np.argsort(m["t"], kind="stable")
    return {k: v[o] for k, v in m.items()}


def sub(tr, mask):
    return {k: v[mask] for k, v in tr.items()}


EPOCHS = (("06-10", 2006, 2010), ("11-15", 2011, 2015), ("16-19", 2016, 2019), ("20-21", 2020, 2021), ("22-23", 2022, 2023),
          ("24-25", 2024, 2025))


def year_of(t):
    return (t.astype("datetime64[m]").astype("datetime64[Y]").astype(int) + 1970)


def metrics(tr, weighted=True):
    R = tr["R"] * (tr["w"] if weighted else 1.0)
    t = tr["t"]
    n = len(R)
    if n == 0:
        return dict(n=0)
    yrs = max((t.max() - t.min()) / 1440 / 365.25, 1e-9)
    cur = 0; mx = 0
    for x in R:
        if x < 0:
            cur += 1; mx = max(mx, cur)
        else:
            cur = 0
    cum = np.cumsum(R); dd = float(np.max(np.maximum.accumulate(np.r_[0.0, cum])[1:] - cum))
    wins = R[R > 0].sum(); loss = -R[R < 0].sum()
    y = year_of(t)
    ep = {}
    for nm, a, b in EPOCHS:
        m = (y >= a) & (y <= b)
        if m.any():
            ep[nm] = float(R[m].sum() / (b - a + 1))
    # Bust-Ersatz: Rueckgang vom Hoch um X R (Gewicht 1 = 0,5 % Risiko -> 6 % Boden = 12 R), danach Neustart am Tief
    bz = {}
    for X in (8.0, 12.0):
        pk = 0.0; cu = 0.0; nb = 0
        for x in R:
            cu += x
            if cu > pk:
                pk = cu
            if pk - cu >= X:
                nb += 1; pk = cu
        bz[X] = nb / yrs
    # Sharpe der Wochensummen (annualisiert, Wochen ohne Trade = 0) - stabiler als Einzel-Ereignisse
    wk = (tr["t"] // 10080)
    w0 = wk.min(); nw = int(wk.max() - w0 + 1)
    ws = np.zeros(nw); np.add.at(ws, (wk - w0).astype(np.int64), R)
    sh = float(ws.mean() / ws.std() * np.sqrt(52)) if ws.std() > 0 else 0.0
    return dict(n=n, tpy=n / yrs, wr=float((R > 0).mean() * 100), avgR=float(R.mean()), pf=float(wins / loss) if loss > 0 else 99.0,
                Ry=float(R.sum() / yrs), maxS=mx, ddR=dd, ep=ep, b8=bz[8.0], b12=bz[12.0], sh=sh)


def line(lbl, m):
    if m.get("n", 0) == 0:
        return f"{lbl:<44s} keine Trades"
    eps = " ".join(f"{k}:{v:+5.1f}" for k, v in m["ep"].items())
    return (f"{lbl:<44s} n{m['n']:5d} {m['tpy']:5.1f}/J WR{m['wr']:5.1f} ØR{m['avgR']:+.3f} PF{m['pf']:5.2f} R/J{m['Ry']:+6.2f} "
            f"maxS{m['maxS']:3d} DD{m['ddR']:5.1f} B12 {m['b12']:.2f} Sh {m['sh']:.2f} | {eps}")


def busts(R, X):
    pk = 0.0; cu = 0.0; nb = 0
    for x in R:
        cu += x
        if cu > pk:
            pk = cu
        if pk - cu >= X:
            nb += 1; pk = cu
    return nb


def risk_parity(tr, target=0.36, X=12.0):
    """Faktor f auf die Groesse, bei dem der Bust-Ersatz (Rueckgang >= X R) so oft vorkommt wie `target` je Jahr;
    Rueckgabe (f, R/J x f). Gleiche Bust-Haeufigkeit -> vergleichbarer Ertrag."""
    R = tr["R"] * tr["w"]
    t = tr["t"]
    yrs = max((t.max() - t.min()) / 1440 / 365.25, 1e-9)
    lo, hi = 0.2, 3.0
    for _ in range(30):
        f = 0.5 * (lo + hi)
        if busts(R * f, X) / yrs > target:
            hi = f
        else:
            lo = f
    f = lo
    return f, float(R.sum() / yrs * f)
