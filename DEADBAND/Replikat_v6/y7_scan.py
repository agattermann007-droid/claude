"""V7-Forschung, Stufe 1: YouTube-Ideen auf Trade-Ebene.
Aufruf: python y7_scan.py gft|ext [idee ...]
  gft = GFT-Ersatz 2022-01 .. (../data, siehe y7_data.py), Auswahl NUR auf IS (bis 30.06.2024), OOS danach
  ext = Fremddaten 2006-2021 (anderes Regime, nur zur Bestaetigung)
Bewertung je Variante: n/J, Trefferquote, Ø R, PF, R/J, Jahre; dazu der Beitrag zu GUELTIGEN TAGEN gegen die 10 Fades
(Tagesergebnis in $ bei 0,75 % Risiko = 75 $/R auf 10k, gueltig ab 50,50 $)."""
import sys, json, itertools, numpy as np
import gsig as G, scan6 as S, cands as K, y7sig as Y, gext

SPLIT = S.SPLIT
F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
RISK_USD = 75.0
VALID = 50.5


def fade_days():
    """Tagesergebnis ($) der 10 Fades ohne Waechter, je Prop-Tag (17:00 NY)."""
    out = {}
    for nm in F10:
        p = K.FADES[nm]
        (b, (ie, d, rd, tp, ix)) = K.fade(0, **p)
        R, why, held, mfe, mae, iout = G.simulate(p["sym"], ie, d, rd, tp, ix)
        ny = G.data()[p["sym"]]["ny"]
        for i, r in zip(iout, R):
            pd_ = int((ny[min(i, len(ny) - 1)] + 420) // 1440)
            out[pd_] = out.get(pd_, 0.0) + r * RISK_USD
    return out


def valid_gain(base, sym, R, iout):
    """zusaetzliche gueltige Tage und verlorene gueltige Tage, wenn der neue Strom dazukommt (je Jahr)."""
    ny = G.data()[sym]["ny"]
    add = dict(base)
    for i, r in zip(iout, R):
        pd_ = int((ny[min(i, len(ny) - 1)] + 420) // 1440)
        add[pd_] = add.get(pd_, 0.0) + r * RISK_USD
    v0 = sum(1 for v in base.values() if v >= VALID)
    v1 = sum(1 for v in add.values() if v >= VALID)
    days = np.array(sorted(add.keys()))
    yrs = max((days.max() - days.min()) / 365.25, 1e-9) if len(days) else 1.0
    return (v1 - v0) / yrs, v0 / yrs


def evaluate(sym, label, gen_out, base, rows, tpdelay=1):
    ie, d, rd, tp, ix = gen_out
    if len(ie) < 20:
        return
    R, why, held, mfe, mae, iout = G.simulate(sym, ie, d, rd, tp, ix, tpdelay=tpdelay)
    ny = G.data()[sym]["ny"]
    te = ny[ie]
    mi, mo = S.split_metrics(R, te, label)
    isr = te < SPLIT
    dv_is, v0 = valid_gain({k: v for k, v in base.items() if k * 1440 < SPLIT}, sym, R[isr], iout[isr])
    dv_oos, _ = valid_gain({k: v for k, v in base.items() if k * 1440 >= SPLIT}, sym, R[~isr], iout[~isr])
    rows.append(dict(label=label, sym=sym, IS=mi, OOS=mo, dv_is=dv_is, dv_oos=dv_oos, v0=v0))


def line(r):
    a, b = r["IS"], r["OOS"]
    f = lambda m: (f"n{m['n']:4d} WR{m['wr']:4.0f} R̄{m['avgR']:+.2f} PF{m['pf']:4.2f} R/J{m['Ry']:+5.1f}" if m.get("n", 0) else "—")
    return f"{r['label']:<58s} IS {f(a)} | OOS {f(b)} | +gültig/J IS {r['dv_is']:+5.1f} OOS {r['dv_oos']:+5.1f}"


def run(target, ideas):
    global SPLIT
    if target == "ext":
        G._D = gext.data_ext()
        SPLIT = S.SPLIT = np.datetime64("2014-01-01", "m").astype(np.int64)   # ext: 2006-13 / 2014-21
    K._CACHE.clear()
    base = fade_days()
    rows = []
    if "gap" in ideas:
        D, ny, days, t_end, atr = S.prep("NAS")
        op, cl, hi, lo = Y.rth_levels(ny, D["o"], D["h"], D["l"], D["c"], days)
        for e0, xm, (gmin, gmax), inside, (sm, sk), tf in itertools.product(
                (570, 575, 580), (600, 630, 660), ((0.0, 0.15), (0.05, 0.25), (0.1, 0.4), (0.0, 0.4)), (0, 1),
                ((0, 1.0), (0, 1.5), (1, 0.15), (1, 0.25), (2, 0.25)), (1.0, 0.5)):
            out = Y.gap_fade(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, op, cl, hi, lo,
                             e0, xm, gmin, gmax, inside, sm, sk, tf, 0)
            evaluate("NAS", f"GAP e{e0} x{xm} g{gmin}-{gmax} in{inside} s{sm}/{sk} t{tf}", out, base, rows)
    if "p1" in ideas:
        for nm in F10:
            p = dict(K.FADES[nm]); sym = p.pop("sym")
            D, ny, days, t_end, atr = S.prep(sym)
            r1 = p["r0"] + p["L"]; tend = r1 + p["tlen"]; xm = min(r1 + p["tlen"] + p["xoff"], 1000)
            if xm <= tend: tend = xm - 5
            mx = p.get("mx", 0.6)
            for nb in (1, 2, 3, 6):
                out = Y.fade_p1(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, p["r0"], r1, tend, xm,
                                p["buf"], p["tgt"], p["dirs"], 0.0, mx, nb, 1)
                evaluate(sym, f"P1 {nm} nb{nb} (nur Zusatzsignale)", out, base, rows)
    if "vwap" in ideas:
        D, ny, days, t_end, atr = S.prep("NAS")
        for (t0, t1), xm, k, buf, tg, conf in itertools.product(
                ((630, 840), (660, 870), (720, 900), (600, 720)), (930, 955), (2.0, 2.5, 3.0), (0.1, 0.25), (0, 1), (0, 1)):
            out = Y.vwap_fade(ny, D["o"], D["h"], D["l"], D["c"], D["v"], D["sp"], days, t_end, atr, t0, t1, xm, k, buf, tg, 0, conf)
            evaluate("NAS", f"VWAP {t0}-{t1} x{xm} k{k} b{buf} t{tg} c{conf}", out, base, rows)
        D, ny, days, t_end, atr = S.prep("XAU")
        for (t0, t1), xm, k, buf, tg, conf in itertools.product(
                ((630, 840), (660, 870), (720, 900)), (930, 955), (2.0, 2.5, 3.0), (0.1, 0.25), (0, 1), (0, 1)):
            out = Y.vwap_fade(ny, D["o"], D["h"], D["l"], D["c"], D["v"], D["sp"], days, t_end, atr, t0, t1, xm, k, buf, tg, 0, conf)
            evaluate("XAU", f"VWAPX {t0}-{t1} x{xm} k{k} b{buf} t{tg} c{conf}", out, base, rows)
    if "lhm" in ideas:
        for sym in ("NAS", "XAU"):
            D, ny, days, t_end, atr = S.prep(sym)
            op, cl, hi, lo = Y.rth_levels(ny, D["o"], D["h"], D["l"], D["c"], days)
            for m1, (e0, xm), kmin, sk, ug, dirs in itertools.product(
                    (600, 630), ((930, 955), (900, 955), (930, 1000) if sym == "XAU" else (930, 955)), (0.0, 0.1, 0.2),
                    (0.2, 0.35), (0, 1), (0, 1)):
                out = Y.lhm(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, cl, 570, m1, e0, xm, kmin, sk, ug, dirs)
                evaluate(sym, f"LHM {sym} m{m1} e{e0} x{xm} k{kmin} s{sk} g{ug} d{dirs}", out, base, rows)
    if "spike" in ideas:
        for sym in ("XAU", "NAS"):
            D, ny, days, t_end, atr = S.prep(sym)
            for ts, nbars, wait, xm, kmin, buf, tf in itertools.product(
                    (510, 600, 840), (1, 2), (2, 3, 6), (600, 660, 720), (0.15, 0.25, 0.4), (0.05, 0.15), (0.5, 0.618)):
                if xm <= ts + 5 * wait:
                    continue
                out = Y.spike_fade(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, ts, nbars, wait, xm, kmin, buf, tf, 0)
                evaluate(sym, f"SPIKE {sym} t{ts} n{nbars} w{wait} x{xm} k{kmin} b{buf} t{tf}", out, base, rows)
    if "wopen" in ideas:
        for sym in ("NAS", "XAU"):
            D, ny, days, t_end, atr = S.prep(sym)
            for dows, e0, xm, (dmin, dmax), sk, tf in itertools.product(
                    (4, 8, 12, 28), (570, 600, 660), (720, 900), ((0.1, 0.4), (0.2, 0.6), (0.3, 1.0)), (0.3, 0.5), (1.0, 0.5)):
                if xm <= e0:
                    continue
                out = Y.week_open_fade(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, dows, e0, xm, dmin, dmax, sk, tf)
                evaluate(sym, f"WOPEN {sym} d{dows} e{e0} x{xm} {dmin}-{dmax} s{sk} t{tf}", out, base, rows)
    if "news" in ideas or "vola" in ideas:
        for nm in F10:
            p = K.FADES[nm]; sym = p["sym"]
            (b, (ie, d, rd, tp, ix)) = K.fade(0, **p)
            R, *_ = G.simulate(sym, ie, d, rd, tp, ix)
            D, ny, days, t_end, atr = S.prep(sym)
            te = ny[ie]; dd = te // 1440
            # Termin-Proxy: Spanne der 8:30- bzw. 14:00-Kerze (M5) >= k x ATR14 und Einstieg danach; NFP = erster Freitag
            def bar_rng(minute):
                out = np.full(len(te), np.nan)
                for q, (t, day) in enumerate(zip(te, dd)):
                    j = np.searchsorted(ny, day * 1440 + minute)
                    if j < len(ny) and ny[j] == day * 1440 + minute and t > ny[j]:
                        a = S._atr_at(t_end, atr, day * 1440 + minute)
                        out[q] = (D["h"][j] - D["l"][j]) / a if a > 0 else np.nan
                return out
            r830 = bar_rng(510); r1400 = bar_rng(840)
            dow = (dd + 4) % 7; dom = (dd.astype("datetime64[D]").astype(object))
            nfp = np.array([(w == 5 and x.day <= 7) for w, x in zip(dow, dom)])
            msg = f"{nm:7s} n{len(R):4d} R̄{R.mean():+.2f}"
            for lab, msk in (("NFP", nfp), ("830>0.15", r830 > 0.15), ("830>0.25", r830 > 0.25),
                             ("1400>0.15", r1400 > 0.15), ("1400>0.25", r1400 > 0.25)):
                if msk.sum() >= 5:
                    msg += f" | {lab}: n{int(msk.sum()):3d} R̄{R[msk].mean():+.2f} Rest R̄{R[~msk].mean():+.2f}"
            # Vola-Perzentil: Rang der ATR14 in den letzten 500 Servertagen
            pr = np.full(len(te), np.nan)
            for q, t in enumerate(te):
                k = np.searchsorted(t_end, t, side="right") - 1
                if k >= 500 and np.isfinite(atr[k]):
                    w = atr[k - 499:k + 1]; pr[q] = (w < atr[k]).mean()
            for lo_, hi_ in ((0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)):
                m_ = (pr >= lo_) & (pr < hi_)
                msg += f" | P{int(lo_*100)}-{int(min(hi_,1)*100)} n{int(m_.sum())} R̄{(R[m_].mean() if m_.sum() else 0):+.2f}"
            print(msg)
    return rows


if __name__ == "__main__":
    target = sys.argv[1]
    ideas = sys.argv[2:] or ["gap", "p1", "vwap", "lhm", "spike"]
    rows = run(target, ideas)
    json.dump(rows, open(f"ergebnisse/y7_scan_{target}_{'_'.join(ideas)}.json", "w"), default=float)
    # Auswahl nur nach IS: PF > 1.2, n >= 40/J*1.5J ... beste 15 je Idee nach IS-R/J, dann OOS ansehen
    for idea in [i for i in ideas if i not in ("news", "vola")]:
        pre = {"gap": "GAP", "p1": "P1", "vwap": "VWAP", "lhm": "LHM", "spike": "SPIKE", "wopen": "WOPEN"}[idea]
        rs = [r for r in rows if r["label"].startswith(pre) and r["IS"].get("n", 0) >= 30]
        rs.sort(key=lambda r: -(r["IS"]["Ry"] if r["IS"]["pf"] > 1.0 else -99))
        print(f"\n=== {idea}: {len(rs)} Varianten, Top 15 nach IS (OOS nur ansehen) ===")
        for r in rs[:15]:
            print(line(r))
        oosok = sum(1 for r in rs if r["OOS"].get("n", 0) and r["OOS"]["pf"] > 1.0)
        print(f"   OOS PF > 1 bei {oosok}/{len(rs)} Varianten")
