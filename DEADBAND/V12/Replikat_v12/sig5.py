"""DEADBAND 5.00 KOMBI Replikat - Signalstroeme der drei Module (unabhaengig vom Kontozustand).

DEADBAND (M15-Ausbruch), RSI21 (M15/M30/H1, Folgesignal, H4-Divergenz), NAS-Noise (Pruefungen 10-15 NY).
Alles genau nach DEADBAND_LIVE4.mq5 Build 5.00; Abweichungen stehen am jeweiligen Ort.
"""
import numpy as np, os, pickle
from numba import njit
import prep5 as P

POINT = P.POINT
STOPLVL = {"XAU": 5 * POINT, "NAS": 150 * POINT}
NZ_FREI = ("2019.01.01;2019.01.21;2019.02.18;2019.04.19;2019.05.27;2019.07.03;2019.07.04;2019.09.02;2019.11.28;2019.11.29;2019.12.24;2019.12.25;"
           "2020.01.01;2020.01.20;2020.02.17;2020.04.10;2020.05.25;2020.07.03;2020.09.07;2020.11.26;2020.11.27;2020.12.24;2020.12.25;"
           "2021.01.01;2021.01.18;2021.02.15;2021.04.02;2021.05.31;2021.07.05;2021.09.06;2021.11.25;2021.11.26;2021.12.24;"
           "2022.01.17;2022.02.21;2022.04.15;2022.05.30;2022.06.20;2022.07.04;2022.09.05;2022.11.24;2022.11.25;2022.12.26;"
           "2023.01.02;2023.01.16;2023.02.20;2023.04.07;2023.05.29;2023.06.19;2023.07.03;2023.07.04;2023.09.04;2023.11.23;2023.11.24;2023.12.25;"
           "2024.01.01;2024.01.15;2024.02.19;2024.03.29;2024.05.27;2024.06.19;2024.07.03;2024.07.04;2024.09.02;2024.11.28;2024.11.29;2024.12.24;2024.12.25;"
           "2025.01.01;2025.01.09;2025.01.20;2025.02.17;2025.04.18;2025.05.26;2025.06.19;2025.07.03;2025.07.04;2025.09.01;2025.11.27;2025.11.28;2025.12.24;2025.12.25;"
           "2026.01.01;2026.01.19;2026.02.16;2026.04.03;2026.05.25;2026.06.19;2026.07.03;2026.09.07;2026.11.26;2026.11.27;2026.12.24;2026.12.25;"
           "2027.01.01;2027.01.18;2027.02.15;2027.03.26;2027.05.31;2027.06.18;2027.07.05;2027.09.06;2027.11.25;2027.11.26;2027.12.24")
FREI_DAYS = set(int(np.datetime64(x.replace(".", "-"), "D").astype(np.int64)) for x in NZ_FREI.split(";") if x)


def us_dst_ny(ny_min):
    """US-Sommerzeit aus NY-Ortszeit (wie R21UTC in der EA): 2. So Maerz 2:00 bis 1. So Nov 2:00."""
    t = ny_min.astype("datetime64[m]")
    y = t.astype("datetime64[Y]").astype(int) + 1970
    out = np.zeros(len(ny_min), bool)
    for yy in np.unique(y):
        mar1 = np.datetime64(f"{yy}-03-01")
        dow = (mar1.astype("datetime64[D]").astype(np.int64) + 4) % 7          # 0 = Sonntag
        second_sun = 1 + (7 - dow) % 7 + 7
        nov1 = np.datetime64(f"{yy}-11-01")
        dow2 = (nov1.astype("datetime64[D]").astype(np.int64) + 4) % 7
        first_sun = 1 + (7 - dow2) % 7
        a = (np.datetime64(f"{yy}-03-{second_sun:02d}T02:00")).astype("datetime64[m]").astype(np.int64)
        b = (np.datetime64(f"{yy}-11-{first_sun:02d}T02:00")).astype("datetime64[m]").astype(np.int64)
        m = y == yy
        out[m] = (ny_min[m] >= a) & (ny_min[m] < b)
    return out


# ------------------------------------------------------------------ DEADBAND
def db_candidates(D, s, clsmin, allow_short):
    d = D[s]; B = d["m15"]; H1 = d["h1"]; D1 = d["d1"]
    c = B["c"]; h = B["h"]; l = B["l"]; v = B["v"]; t = B["t"]
    n = len(c)
    rsi = P.rsi_wilder(c, 14)
    atr = P.atr_sma(h, l, c, 14)
    stoK, stoD = P.stoch_mt5(h, l, c, 14, 3, 3)
    macd = P.ema_mt5(c, 12) - P.ema_mt5(c, 26)
    hist = macd - P.sma(macd, 9)
    vrel = v / P.sma(v, 50)
    ratio = atr / c
    pz = np.full(n, np.nan)
    L = 500
    from numpy.lib.stride_tricks import sliding_window_view
    r2 = np.where(np.isfinite(ratio), ratio, np.inf)
    win = sliding_window_view(r2, L)
    pz[L - 1:] = (win < r2[L - 1:, None]).sum(axis=1) / float(L)
    # EMA50 auf Servertagen, je Balken der Wert des Vortags
    emaD = P.ema_mt5(D1["c"], 50)
    pday = (t + 420) // 1440
    di = np.searchsorted(D1["key"], pday)
    ema_prev = np.where(di >= 1, emaD[np.clip(di - 1, 0, len(emaD) - 1)], np.nan)
    ema_prev[di < 50] = np.nan                    # EMA braucht Vorlauf (ab ca. Mitte Maerz 2022)
    # H1 der Vorgaengerstunde
    hk = t // 60
    pos = np.searchsorted(H1["key"], hk)
    prev = pos - 1
    okh = prev >= 0
    hH1 = np.where(okh, H1["h"][np.clip(prev, 0, None)], np.nan)
    lH1 = np.where(okh, H1["l"][np.clip(prev, 0, None)], np.nan)
    # Session-VWAP des Servertags der Kerze j (tickvolumen-gewichtet)
    tp = (h + l + c) / 3.0
    w = np.where(v > 0, v, 1.0)
    cpv = np.cumsum(tp * w); cw = np.cumsum(w)
    ds = np.r_[0, np.nonzero(np.diff(pday))[0] + 1]
    dstart = np.repeat(ds, np.diff(np.r_[ds, n]))
    pv0 = np.where(dstart > 0, cpv[np.maximum(dstart - 1, 0)], 0.0)
    w0 = np.where(dstart > 0, cw[np.maximum(dstart - 1, 0)], 0.0)
    vwap = (cpv - pv0) / np.maximum(cw - w0, 1e-12)
    rows = []
    k = np.arange(1, n); j = k - 1
    T = t[k]
    nyh = (T % 1440) / 60.0
    rng = h[j] - l[j]
    clsP = np.where(rng > 0, (c[j] - l[j]) / np.where(rng > 0, rng, 1.0), 0.5)
    base = np.isfinite(hH1[k]) & np.isfinite(ema_prev[k]) & np.isfinite(rsi[j]) & np.isfinite(atr[j]) \
        & np.isfinite(pz[j]) & np.isfinite(stoK[j]) & np.isfinite(stoD[j]) & np.isfinite(hist[j]) \
        & np.isfinite(vrel[j]) & (vwap[j] > 0)
    volok = vrel[j] >= 1.0
    Lg = base & volok & (c[j] > hH1[k]) & (c[j] > ema_prev[k]) & (c[j] > vwap[j]) & (rsi[j] > 50) & (clsP >= clsmin) & (hist[j] > 0)
    Sg = base & volok & (c[j] < lH1[k]) & (c[j] < ema_prev[k]) & (c[j] < vwap[j]) & (rsi[j] < 50) & ((1 - clsP) >= clsmin) & (hist[j] < 0)
    if not allow_short:
        Sg[:] = False
    sel = np.nonzero(Lg | Sg)[0]
    dirs = np.where(Lg[sel], 1, -1)
    rd = 3.0 * atr[j[sel]]
    f = np.clip(1.40 - 0.80 * pz[j[sel]], 0.35, 2.00)
    passt = np.where(dirs > 0, stoK[j[sel]] > stoD[j[sel]], stoK[j[sel]] < stoD[j[sel]])
    f = f * np.where(passt, 1.2, 0.8)
    good = (rd > 50 * POINT) & (rd >= STOPLVL[s])
    sel, dirs, rd, f = sel[good], dirs[good], rd[good], f[good]
    kk = k[sel]
    return dict(T=t[kk], dir=dirs, rd=rd, f=f, m15=kk, i5=B["first"][kk], nyh=nyh[sel])


# ------------------------------------------------------------------ RSI21
@njit(cache=True)
def _divergence_series(closes, rsi, radius, gap, period, nmin):
    """Divergenz je H4-Bucket i (nur Buckets < i sichtbar): +1 bull, -1 bear, 0 keine, -9 unbekannt."""
    n = len(closes)
    out = np.full(n + 1, -9, np.int64)
    high = 0.0; prevHigh = 0.0; highRsi = 0.0; prevHighRsi = 0.0
    low = 0.0; prevLow = 0.0; lowRsi = 0.0; prevLowRsi = 0.0
    highs = 0; lows = 0
    # Pivot j ist bekannt, sobald j+radius geschlossen ist. Fuer 'aktuellen Bucket' i sind closes[0..i-1] sichtbar.
    jn = max(radius, period)
    for i in range(n + 1):
        # neue Pivots, die mit Sichtbarkeit bis i-1 bestimmbar sind: j + radius <= i - 1
        while jn + radius <= i - 1:
            j = jn
            isH = True; isL = True
            for q in range(j - radius, j + radius + 1):
                if closes[q] > closes[j]:
                    isH = False
                if closes[q] < closes[j]:
                    isL = False
            if isH:
                prevHigh = high; prevHighRsi = highRsi; high = closes[j]; highRsi = rsi[j]; highs += 1
            if isL:
                prevLow = low; prevLowRsi = lowRsi; low = closes[j]; lowRsi = rsi[j]; lows += 1
            jn += 1
        if i < nmin or highs < 2 or lows < 2:
            continue
        bear = (high > prevHigh) and (highRsi < prevHighRsi - gap)
        bull = (low < prevLow) and (lowRsi > prevLowRsi + gap)
        out[i] = (1 if bull else 0) - (1 if bear else 0)
    return out


def r21_h4_div(D, s):
    """H4-Buckets (UTC, aus H1-Schlusskursen), RSI(21) Wilder, Divergenz je Bucket."""
    H1 = D[s]["h1"]
    ny = H1["t"]
    utc = ny + np.where(us_dst_ny(ny), 240, 300)
    bucket = utc // 240
    ub, first = np.unique(bucket, return_index=True)
    last = np.r_[first[1:] - 1, len(bucket) - 1]
    closes = H1["c"][last]
    rsi = P.rsi_wilder(closes, 21)
    rsi = np.where(np.isfinite(rsi), rsi, 50.0)
    div = _divergence_series(closes, rsi, 2, 2.0, 21, 150)
    return ub, div          # div[i] gilt, wenn der aktuelle Bucket ub[i] ist (nur fruehere sichtbar)


def r21_signals(D, gold="XAU", nas="NAS", folge_min=240, oben=75.0, unten=25.0, cross=55.0,
                ab=9.5, nas_bis=13.0, gold_bis=17.0, gold_ohne_h1=True, use_div=True, stop_atr=2.0, sma_min=50):
    tfs = (15, 30, 60)
    keys = ("m15", "m30", "h1")
    rsiT = {}; atrT = {}
    for s in (gold, nas):
        for tf, kk in zip(tfs, keys):
            B = D[s][kk]
            rsiT[(s, tf)] = P.rsi_wilder(B["c"], 21)
            atrT[(s, tf)] = P.atr_sma(B["h"], B["l"], B["c"], 14)
    # Regime: Vortagesschluss gegen Tages-SMA200/100 (Servertage, am Anfang mit Teilhistorie >= sma_min)
    reg = {}
    for s in (gold, nas):
        D1 = D[s]["d1"]
        maL = P.sma_partial(D1["c"], 200, sma_min)
        maS = P.sma_partial(D1["c"], 100, sma_min)
        reg[s] = (D1["key"], D1["c"], maL, maS)
    div = {s: r21_h4_div(D, s) for s in (gold, nas)}
    out = []
    for s in (gold, nas):
        o = nas if s == gold else gold
        isg = s == gold
        bis = gold_bis if isg else nas_bis
        # alle neuen Balken-Zeitpunkte (Vereinigung der Zeitebenen)
        ev = {}
        for ti, (tf, kk) in enumerate(zip(tfs, keys)):
            if ti == 2 and isg and gold_ohne_h1:
                # Gold ohne H1: neue H1-Kerze wird zwar erkannt, aber nicht bewertet
                continue
            B = D[s][kk]
            for k in range(1, len(B["t"])):
                ev.setdefault(int(B["t"][k]), []).append((ti, k))
        dkey, dc, maL, maS = reg[s]
        ub, dv = div[s]
        last_sig = [0, 0]
        oB = {tf: D[o][kk] for tf, kk in zip(tfs, keys)}
        for T in sorted(ev.keys()):
            # Regime (Vortag)
            pday = (T + 420) // 1440
            di = int(np.searchsorted(dkey, pday))
            if di < 1 or not np.isfinite(maL[di - 1]) or not np.isfinite(maS[di - 1]):
                continue
            cprev = dc[di - 1]; mL = maL[di - 1]; mS = maS[di - 1]
            regv = 1 if cprev > mL else -1
            shortOk = (cprev < mL) or (cprev < mS)
            gateL = (cprev > mL) and (cprev > mS)
            gateS = (cprev < mL) and (cprev < mS)
            # Divergenz fuer den aktuellen UTC-H4-Bucket
            divv = 0; divok = True
            if use_div:
                utc = T + (240 if us_dst_ny(np.array([T]))[0] else 300)
                bi = int(np.searchsorted(ub, utc // 240))       # Index des aktuellen Buckets (bzw. Einfuegeposition)
                dval = dv[min(bi, len(dv) - 1)]
                if dval == -9:
                    divok = False
                else:
                    divv = int(dval)
            sig = []                       # (ti, dir, rsi, rd)
            has = [False, False]
            sigzeit = 0
            nyh = (T % 1440) / 60.0
            for (ti, k) in ev[T]:
                tf = tfs[ti]
                if nyh < ab or nyh >= bis:
                    continue
                r = rsiT[(s, tf)][k - 1]
                if not np.isfinite(r):
                    continue
                dr = 1 if r > oben else (-1 if r < unten else 0)
                if dr == 0:
                    continue
                if dr < 0 and not shortOk:
                    continue
                if dr > 0 and not isg and regv < 0:
                    continue
                # anderes Symbol, gleiche Zeitebene, Balken 1 zum Zeitpunkt T
                ob = oB[tf]
                po = int(np.searchsorted(ob["t"], T, side="right")) - 1
                crossOk = False
                if po - 1 >= 0:
                    ro = rsiT[(o, tf)][po - 1]
                    if np.isfinite(ro):
                        crossOk = (ro > cross) if dr > 0 else (ro < 100.0 - cross)
                if isg:
                    gate = gateL if dr > 0 else gateS
                    if not crossOk and not gate:
                        continue
                elif not crossOk:
                    continue
                if use_div:
                    if not divok:
                        continue
                    if dr * divv < 0:
                        continue
                a = atrT[(s, tf)][k - 1]
                if not np.isfinite(a) or a <= 0:
                    continue
                sig.append((ti, dr, r, stop_atr * a, k))
                has[0 if dr > 0 else 1] = True
                sigzeit = T
            if not sig:
                continue
            folge = [False, False]
            for dI in range(2):
                vor = last_sig[dI]
                folge[dI] = (folge_min <= 0) or (vor > 0 and vor < sigzeit and sigzeit - vor <= folge_min)
                if has[dI] and sigzeit > vor:
                    last_sig[dI] = sigzeit
            for (ti, dr, r, rd, k) in sorted(sig):
                ok = folge[0 if dr > 0 else 1]
                out.append((T, 0 if isg else 1, ti, dr, rd, int(ok)))
    out.sort(key=lambda x: (x[0], x[1], x[2]))
    A = np.array(out, dtype=np.float64)
    return dict(T=A[:, 0].astype(np.int64), sym=A[:, 1].astype(np.int64), tf=A[:, 2].astype(np.int64),
                dir=A[:, 3].astype(np.int64), rd=A[:, 4], folge=A[:, 5].astype(np.int64))


# ------------------------------------------------------------------ NAS-Noise
def nz_days(D, s="NAS", ntage=14, k=1.0, checks=(600, 660, 720, 780, 840, 900), last_entry=930, schluss=955,
            first_check=600, stops=(0.35, 0.5, 0.75), zeitpow=0.5, vpow=0.5, vmin=0.5, vmax=2.0):
    """Je NY-Handelstag: Eroeffnung, Vortagesschluss, Tages-Sigma und die Pruefungen (M5 statt M1)."""
    d = D[s]
    ny = d["ny"]; o = d["o"]; c = d["c"]
    nyday = ny // 1440
    nymin = (ny % 1440).astype(np.int64)
    days = np.unique(nyday)
    # je Tag: Kerzen 9:30-16:00
    stats = {}
    for dd in days:
        m = (nyday == dd)
        idx = np.nonzero(m)[0]
        mm = nymin[idx]
        sel = idx[(mm >= 570) & (mm < 960)]
        if len(sel) == 0:
            stats[int(dd)] = None
            continue
        m0 = nymin[sel[0]]
        dopen = o[sel[0]] if m0 <= 575 else -1.0
        cl = np.full(78, -1.0)
        for q in sel:
            cl[(nymin[q] - 570) // 5] = c[q]
        stats[int(dd)] = dict(open=dopen, cnt=len(sel), close=c[sel[-1]], lastm=int(nymin[sel[-1]]) + 4, cl=cl, idx=sel)
    out = []
    for dd in days:
        dd = int(dd)
        dow = (dd + 4) % 7                   # 0 = Sonntag
        if dow == 0 or dow == 6 or dd in FREI_DAYS:
            continue
        st = stats.get(dd)
        if st is None or st["open"] <= 0:
            continue
        # Vorgeschichte: letzte 60 Kalendertage
        hist = [x for x in range(dd - 60, dd) if stats.get(x) is not None]
        # letzter erwarteter Handelstag muss bis zum Schluss da sein
        erw = dd - 1
        for g in range(10):
            dw = (erw + 4) % 7
            if dw != 0 and dw != 6 and erw not in FREI_DAYS:
                break
            erw -= 1
        se = stats.get(erw)
        if se is None or se["lastm"] < 950:
            continue
        vi = [x for x in hist if ((x + 4) % 7) not in (0, 6) and stats[x]["cnt"] >= 60]
        if len(vi) < ntage + 1:
            continue
        pc = stats[vi[-1]]["close"]
        rs = []
        for j in range(len(vi) - ntage, len(vi)):
            c1 = stats[vi[j]]["close"]; c0 = stats[vi[j - 1]]["close"]
            if c1 > 0 and c0 > 0:
                rs.append(np.log(c1 / c0))
        if len(rs) < ntage // 2:
            continue
        sd = float(np.std(rs))
        last14 = vi[len(vi) - ntage:]
        # sigma je 5-min-Block (Schluss des Blocks) und historische kumulierte RV
        sig = np.full(78, -1.0)
        for b in range(78):
            vals = []
            for x in last14:
                stx = stats[x]
                if stx["cl"][b] > 0 and stx["open"] > 0:
                    vals.append(abs(stx["cl"][b] / stx["open"] - 1.0))
            if len(vals) >= ntage // 2:
                sig[b] = float(np.mean(vals))
        sumCR = np.zeros(78); cntCR = np.zeros(78)
        for x in last14:
            stx = stats[x]
            if stx["open"] <= 0:
                continue
            prev = stx["open"]; acc = 0.0; seen = False
            for b in range(78):
                v = stx["cl"][b]
                if v > 0:
                    lr = np.log(v / prev); acc += lr * lr; prev = v; seen = True
                if seen:
                    sumCR[b] += acc; cntCR[b] += 1
        histCR = np.where(cntCR > 0, sumCR / np.maximum(cntCR, 1), -1.0)
        # heute
        O = st["open"]
        todCR = np.full(78, -1.0)
        prev = O; acc = 0.0
        for b in range(78):
            v = st["cl"][b]
            if v > 0:
                lr = np.log(v / prev); acc += lr * lr; prev = v
                todCR[b] = acc
        refU = max(O, pc)
        span = float(schluss - first_check)
        for em in checks:
            b = (em - 570) // 5 - 1                  # Block, der um em endet
            if b < 0 or b >= 78 or sig[b] < 0:
                continue
            close = st["cl"][b]
            if close <= 0:
                continue
            # M5-Index der Kerze, die um em beginnt (Ausfuehrung) - falls fehlt: naechste
            sel = st["idx"]
            mins = nymin[sel]
            jj = np.searchsorted(mins, em)
            if jj >= len(sel):
                continue
            i5 = int(sel[jj])
            UB = refU * (1.0 + k * sig[b])
            tv = -1.0
            for q in range(b, -1, -1):
                if todCR[q] >= 0:
                    tv = todCR[q]
                    break
            vw = 1.0
            if histCR[b] > 0 and tv >= 0:
                ratio = np.sqrt(tv / histCR[b])
                vw = min(vmax, max(vmin, ratio)) ** (-vpow)
            tfak = max(0.1, (schluss - em) / span) ** zeitpow if zeitpow > 0 else 1.0
            dists = [st_ * O * sd * tfak for st_ in stops]
            out.append((dd, em, i5, close, UB, vw, tfak, O, sd, *dists))
    A = np.array(out, dtype=np.float64)
    nst = len(stops)
    res = dict(day=A[:, 0].astype(np.int64), em=A[:, 1].astype(np.int64), i5=A[:, 2].astype(np.int64),
               close=A[:, 3], UB=A[:, 4], vw=A[:, 5], tf=A[:, 6], O=A[:, 7], sd=A[:, 8],
               dist=A[:, 9:9 + nst].copy(), entry_ok=(A[:, 1] <= last_entry).astype(np.int64))
    # EOD-Schluss 15:55: M5-Index je Tag
    eod = {}
    for dd in np.unique(res["day"]):
        st = stats[int(dd)]
        sel = st["idx"]; mins = nymin[sel]
        jj = np.searchsorted(mins, schluss)
        eod[int(dd)] = int(sel[jj]) if jj < len(sel) else int(sel[-1])
    res["eod_i5"] = np.array([eod[int(x)] for x in res["day"]], np.int64)
    return res


def build_all(save=True):
    D = P.build()
    db = {"XAU": db_candidates(D, "XAU", 0.70, False), "NAS": db_candidates(D, "NAS", 0.65, True)}
    r21 = r21_signals(D)
    nz = nz_days(D)
    if save:
        with open(os.path.join(P.OUT, "sig5.pkl"), "wb") as f:
            pickle.dump(dict(db=db, r21=r21, nz=nz), f)
    return D, db, r21, nz


if __name__ == "__main__":
    import time
    t0 = time.time()
    D, db, r21, nz = build_all()
    for s in ("XAU", "NAS"):
        x = db[s]
        print(f"DEADBAND {s}: {len(x['T'])} Kandidaten, long {np.sum(x['dir'] > 0)}, short {np.sum(x['dir'] < 0)}")
    print(f"RSI21: {len(r21['T'])} gueltige Signale, davon Folgesignale {r21['folge'].sum()} "
          f"(XAU {np.sum((r21['sym'] == 0) & (r21['folge'] == 1))}, NAS {np.sum((r21['sym'] == 1) & (r21['folge'] == 1))})")
    print(f"Noise: {len(np.unique(nz['day']))} Tage, {len(nz['day'])} Pruefungen, Long-Signale {np.sum((nz['close'] > nz['UB']) & (nz['entry_ok'] == 1))}")
    print(f"fertig in {time.time() - t0:.1f}s")
