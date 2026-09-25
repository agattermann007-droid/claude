"""RSI21-Labor: Signal-Kandidaten mit Merkmalen (vektorisiert) und Filter/Folgesignal wie RSI21 v3.4 (EA 6.10).

Ein Kandidat = geschlossene Kerze (M15/M30/H1) mit RSI jenseits einer Schwelle. Zeitpunkt T = Eroeffnung der naechsten
Kerze (NY-Minute), Einstieg am Open der M5-Kerze ab T. Die Filter der EA werden als Masken angewandt, danach das
Folgesignal (frueheres gueltiges Signal derselben Richtung und desselben Symbols hoechstens `folge_min` Minuten alt)."""
import os, sys
import numpy as np
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Replikat_v6"))
import prep5 as P          # noqa: E402
import sig5 as S5          # noqa: E402

TFS = (15, 30, 60)
KEYS = ("m15", "m30", "h1")
SYMS = ("XAU", "NAS")


@njit(cache=True)
def rma(x, n):
    out = np.empty(len(x)); s = x[0]; a = 1.0 / n
    for i in range(len(x)):
        if i:
            s = s + a * (x[i] - s)
        out[i] = s
    return out


def adx_wilder(h, l, c, n=14):
    """ADX mit Wilder-Glaettung (MT5 iADX glaettet exponentiell; fuer Filter-Tests genuegt die Form)."""
    up = np.r_[0.0, h[1:] - h[:-1]]; dn = np.r_[0.0, l[:-1] - l[1:]]
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    cp = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - cp), np.abs(l - cp)))
    atr = rma(tr, n); pdi = 100 * rma(pdm, n) / np.maximum(atr, 1e-12); mdi = 100 * rma(mdm, n) / np.maximum(atr, 1e-12)
    dx = 100 * np.abs(pdi - mdi) / np.maximum(pdi + mdi, 1e-12)
    return rma(dx, n), pdi, mdi


@njit(cache=True)
def pct_rank(x, L):
    """Anteil der letzten L Werte (inkl. aktuellem Fenster) unter dem aktuellen Wert."""
    out = np.full(len(x), np.nan)
    for i in range(L - 1, len(x)):
        v = x[i]
        if not np.isfinite(v):
            continue
        cnt = 0
        for j in range(i - L + 1, i + 1):
            if x[j] < v:
                cnt += 1
        out[i] = cnt / L
    return out


@njit(cache=True)
def roll_max(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        m = x[i - n + 1]
        for j in range(i - n + 2, i + 1):
            if x[j] > m:
                m = x[j]
        out[i] = m
    return out


@njit(cache=True)
def roll_min(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        m = x[i - n + 1]
        for j in range(i - n + 2, i + 1):
            if x[j] < m:
                m = x[j]
        out[i] = m
    return out


def features(D, rsi_len=21, lo_thr=65.0, stop_atr=2.0):
    """Alle Kandidaten mit RSI > lo_thr bzw. < 100 - lo_thr (alle Uhrzeiten, alle Zeitebenen inkl. Gold-H1)."""
    rs = {}; at = {}; ax = {}; ap = {}; hh = {}; ll = {}; vr = {}
    for s in SYMS:
        for tf, kk in zip(TFS, KEYS):
            B = D[s][kk]
            v = B["v"].astype(float)
            with np.errstate(invalid="ignore", divide="ignore"):
                vr[(s, tf)] = v / P.sma(v, 50)
            rs[(s, tf)] = P.rsi_wilder(B["c"], rsi_len)
            at[(s, tf)] = P.atr_sma(B["h"], B["l"], B["c"], 14)
            ax[(s, tf)] = adx_wilder(B["h"], B["l"], B["c"], 14)[0]
            ap[(s, tf)] = pct_rank(at[(s, tf)] / B["c"], 500)
            hh[(s, tf)] = roll_max(B["h"], 20); ll[(s, tf)] = roll_min(B["l"], 20)
    # hoehere Zeitebenen: H4 (Grenzen 17/21/1/5/9/13 NY) und Servertag, RSI(21) der letzten geschlossenen Kerze
    htf = {}
    for s in SYMS:
        d = D[s]
        h4 = P.agg(d["ny"], d["o"], d["h"], d["l"], d["c"], d["v"], 240, offset=420)
        htf[s] = (h4["t"], P.rsi_wilder(h4["c"], rsi_len), d["d1"]["t"], P.rsi_wilder(d["d1"]["c"], rsi_len),
                  P.atr_sma(d["d1"]["h"], d["d1"]["l"], d["d1"]["c"], 14))
    reg = {}
    for s in SYMS:
        D1 = D[s]["d1"]
        reg[s] = (D1["key"], D1["c"], P.sma_partial(D1["c"], 200, 50), P.sma_partial(D1["c"], 100, 50),
                  P.sma_partial(D1["c"], 50, 20), P.sma_partial(D1["c"], 20, 10), D1["h"], D1["l"])
    div = {s: S5.r21_h4_div(D, s) for s in SYMS}
    cols = {}
    for si, s in enumerate(SYMS):
        o = SYMS[1 - si]
        ny5 = D[s]["ny"]
        for ti, (tf, kk) in enumerate(zip(TFS, KEYS)):
            B = D[s][kk]
            n = len(B["t"])
            k = np.arange(2, n)
            T = B["t"][k]
            r = rs[(s, tf)][k - 1]; r2 = rs[(s, tf)][k - 2]
            a = at[(s, tf)][k - 1]
            dr = np.where(r > lo_thr, 1, np.where(r < 100.0 - lo_thr, -1, 0))
            m = (dr != 0) & np.isfinite(r) & np.isfinite(a) & (a > 0)
            k = k[m]; T = T[m]; r = r[m]; r2 = r2[m]; a = a[m]; dr = dr[m]
            # Regime (Vortag)
            dkey, dc, maL, maS, ma50, ma20, dh, dl = reg[s]
            pday = (T + 420) // 1440
            di = np.searchsorted(dkey, pday)
            okd = di >= 1
            dj = np.clip(di - 1, 0, len(dc) - 1)
            cprev = np.where(okd, dc[dj], np.nan)
            mL = np.where(okd, maL[dj], np.nan); mS = np.where(okd, maS[dj], np.nan)
            m50 = np.where(okd, ma50[dj], np.nan); m20 = np.where(okd, ma20[dj], np.nan)
            pdh = np.where(okd, dh[dj], np.nan); pdl = np.where(okd, dl[dj], np.nan)
            # anderes Symbol, gleiche Zeitebene: RSI der letzten geschlossenen Kerze zum Zeitpunkt T
            ob = D[o][kk]
            po = np.searchsorted(ob["t"], T, side="right") - 1
            ro = np.where(po - 1 >= 0, rs[(o, tf)][np.clip(po - 1, 0, None)], np.nan)
            # Divergenz des aktuellen UTC-H4-Buckets
            ub, dv = div[s]
            utc = T + np.where(S5.us_dst_ny(T), 240, 300)
            bi = np.minimum(np.searchsorted(ub, utc // 240), len(dv) - 1)
            dval = dv[bi]
            i5 = np.searchsorted(ny5, T)
            ok5 = i5 < len(ny5)
            sel = ok5
            t4, r4, td, rdd, atd = htf[s]
            j4 = np.searchsorted(t4, T, side="right") - 2          # letzte geschlossene H4-Kerze vor T
            jd = np.searchsorted(td, T, side="right") - 2
            h4r = np.where(j4 >= 0, r4[np.clip(j4, 0, None)], np.nan)
            d1r = np.where(jd >= 0, rdd[np.clip(jd, 0, None)], np.nan)
            d1a = np.where(jd >= 0, atd[np.clip(jd, 0, None)], np.nan)
            kp = np.clip(k - 2, 0, None)                            # 20 Kerzen vor der Signalkerze
            C = dict(T=T, sym=np.full(len(T), si), tf=np.full(len(T), ti), dir=dr, rsi=r, rsi_prev=r2, atr=a,
                     rd=stop_atr * a, cprev=cprev, maL=mL, maS=mS, ma50=m50, ma20=m20, pdh=pdh, pdl=pdl, ro=ro, div=dval,
                     i5=i5, kbar=k, close=B["c"][k - 1], high=B["h"][k - 1], low=B["l"][k - 1],
                     adx=ax[(s, tf)][k - 1], atrpct=ap[(s, tf)][k - 1], hh20=hh[(s, tf)][kp], ll20=ll[(s, tf)][kp],
                     h4rsi=h4r, d1rsi=d1r, d1atr=d1a, vrel=vr[(s, tf)][k - 1])
            for key, v in C.items():
                cols.setdefault(key, []).append(v[sel])
    C = {k: np.concatenate(v) for k, v in cols.items()}
    order = np.lexsort((C["tf"], C["sym"], C["T"]))
    C = {k: v[order] for k, v in C.items()}
    C["nyh"] = (C["T"] % 1440) / 60.0
    C["dow"] = ((C["T"] // 1440) + 4) % 7
    return C


BASE = dict(oben=75.0, ab=9.5, nas_bis=13.0, gold_bis=17.0, gold_ohne_h1=True, cross=55.0, gold_gate=True,
            use_div=True, folge_min=240, tfs=(0, 1, 2), short_rule="either", nas_long_rule="L", dirs=(1, -1))


def valid_mask(C, p):
    """Gueltige Signale (vor dem Folgesignal) nach den Regeln der EA; p: Parameter (BASE + Aenderungen)."""
    g = C["sym"] == 0
    r = C["rsi"]; d = C["dir"]
    m = np.where(d > 0, r > p["oben"], r < 100.0 - p["oben"])
    m &= np.isin(C["tf"], p["tfs"])
    if p["gold_ohne_h1"]:
        m &= ~(g & (C["tf"] == 2))
    bis = np.where(g, p["gold_bis"], p["nas_bis"])
    m &= (C["nyh"] >= p["ab"]) & (C["nyh"] < bis)
    m &= np.isin(d, p["dirs"])
    okr = np.isfinite(C["maL"]) & np.isfinite(C["maS"])
    m &= okr
    cp = C["cprev"]; mL = C["maL"]; mS = C["maS"]
    if p["short_rule"] == "either":
        shortOk = (cp < mL) | (cp < mS)
    elif p["short_rule"] == "both":
        shortOk = (cp < mL) & (cp < mS)
    elif p["short_rule"] == "L":
        shortOk = cp < mL
    else:
        shortOk = np.ones(len(cp), bool)
    m &= ~((d < 0) & ~shortOk)
    if p["nas_long_rule"] == "L":
        m &= ~((d > 0) & ~g & (cp <= mL))
    elif p["nas_long_rule"] == "either":
        m &= ~((d > 0) & ~g & ~((cp > mL) | (cp > mS)))
    if p.get("gold_long_rule") == "L":
        m &= ~((d > 0) & g & (cp <= mL))
    if p["cross"] is not None:
        ro = C["ro"]
        crossOk = np.where(d > 0, ro > p["cross"], ro < 100.0 - p["cross"]) & np.isfinite(ro)
        gate = np.where(d > 0, (cp > mL) & (cp > mS), (cp < mL) & (cp < mS))
        if p["gold_gate"]:
            m &= np.where(g, crossOk | gate, crossOk)
        else:
            m &= crossOk
    if p["use_div"]:
        m &= C["div"] != -9
        m &= ~(d * C["div"] < 0)
    extra = p.get("extra")
    if extra is not None:
        m &= extra
    return m


def follow(C, m, folge_min):
    """Folgesignal-Flag je gueltigem Kandidaten: frueheres gueltiges Signal (Symbol, Richtung) binnen folge_min."""
    f = np.zeros(len(m), bool)
    if folge_min <= 0:
        f[m] = True
        return f
    for si in (0, 1):
        for dd in (1, -1):
            idx = np.nonzero(m & (C["sym"] == si) & (C["dir"] == dd))[0]
            if len(idx) == 0:
                continue
            T = C["T"][idx]
            u, inv = np.unique(T, return_inverse=True)
            prev_ok = np.r_[False, (np.diff(u) <= folge_min)]
            f[idx] = prev_ok[inv]
    return f


def entries(C, p, tp=None, weights=(1.25, 1.0, 0.75), gold_mult=0.7, rd_mult=1.0):
    """Einstiegskandidaten je Symbol (dict wie r7sim.simulate erwartet)."""
    m = valid_mask(C, p)
    f = follow(C, m, p["folge_min"])
    use = m & f
    if p.get("post") is not None:
        use &= p["post"]
    if tp is None:
        tp = (2.64, 2.2)
    out = {}
    for si, s in enumerate(SYMS):
        idx = np.nonzero(use & (C["sym"] == si))[0]
        w = np.asarray(weights)[C["tf"][idx]] * (gold_mult if si == 0 else 1.0)
        tpv = np.full(len(idx), tp[si]) if np.ndim(tp[si]) == 0 else np.asarray(tp[si])[C["tf"][idx]]
        out[s] = dict(i5=C["i5"][idx], dir=C["dir"][idx], rd=C["rd"][idx] * rd_mult, tp=tpv, tf=C["tf"][idx], w=w, idx=idx)
    return out


def r21_dict(C, p, rd_mult=1.0):
    """Signalliste im Format von sig5.r21_signals (fuer den Kontomotor eng6): alle gueltigen Signale mit Folge-Flag."""
    m = valid_mask(C, p)
    f = follow(C, m, p["folge_min"])
    if p.get("post") is not None:
        f &= p["post"]
    idx = np.nonzero(m)[0]
    return dict(T=C["T"][idx].astype(np.int64), sym=C["sym"][idx].astype(np.int64), tf=C["tf"][idx].astype(np.int64),
                dir=C["dir"][idx].astype(np.int64), rd=C["rd"][idx] * rd_mult, folge=f[idx].astype(np.int64))


def r21_dict_weak(C, p, weak, rd_mult=1.0):
    """Wie r21_dict, aber nur Folgesignale; Signale in `weak` bekommen folge=0 (im Motor: Gewicht r21_first_mult)."""
    m = valid_mask(C, p)
    f = follow(C, m, p["folge_min"])
    if p.get("post") is not None:
        f &= p["post"]
    idx = np.nonzero(m & f)[0]
    return dict(T=C["T"][idx].astype(np.int64), sym=C["sym"][idx].astype(np.int64), tf=C["tf"][idx].astype(np.int64),
                dir=C["dir"][idx].astype(np.int64), rd=C["rd"][idx] * rd_mult, folge=(~weak[idx]).astype(np.int64))
