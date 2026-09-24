"""Fade-Bloecke fuer eng6 mit Probability-Grid-Regeln (wie x35.blocks_filtered: Waechter PF > 1,2 aus 30 ueber die
verkettete Historie, keine US-Feiertage, Stop >= 6 Spreads) - zusaetzlich Grid-Filter, Grid-Ziel oder Risikogewicht.

Grid-Merkmale kommen immer aus dem durchgehenden Datensatz 2006-2025 (pg_data): dieselben Kurse wie Fremddaten und
GFT-Ersatz, die Schenkel-Historie reicht so auch am Beginn des Ersatzes (2022) weit genug zurueck (im EA: Historie der
Zeitebene beim Start laden)."""
import numpy as np
import gsig as G, streams as ST, x35 as X, pg_fade as PF, pg_data as PD, pgrid as PG

LIM22 = ST.LIM22
F10 = X.F10
_FI = {}
_PA = {}


def fi(dataset, nm):
    key = (dataset, nm)
    if key not in _FI:
        ST._use(dataset)
        _FI[key] = PF.fade_info(nm)
        _FI[key]["dataset"] = dataset
    return _FI[key]


def piv_all(sym, tf, L):
    key = (sym, tf, L)
    if key not in _PA:
        A = PD.data_all()[sym]
        t0, o, h, l, c, done_at = PG.tf_bars(A["ny"], A["o"], A["h"], A["l"], A["c"], tf)
        _PA[key] = (A["ny"], done_at, PG.lux_pivots(o, c, L), t0, o, c)
    return _PA[key]


def qbar_at(sym, tf, L, t_entry):
    ny, done_at, res, *_ = piv_all(sym, tf, L)
    i5 = np.searchsorted(ny, t_entry)
    assert np.all(ny[np.minimum(i5, len(ny) - 1)] == t_entry), "Einstiegskerze fehlt im durchgehenden Datensatz"
    return done_at[i5 - 1].astype(np.int64)


def feats(sym, t_entry, d, ex, goal, st, ent, tf, L, mp, minlegs=30):
    ny, done_at, res, *_ = piv_all(sym, tf, L)
    bias, piv_px, piv_bar, piv_bias, cur_px, cur_bar, lc, ld, ls, lb = res
    q = qbar_at(sym, tf, L, t_entry)
    return PG.features(q, np.asarray(d, np.int64), np.asarray(ex, float), np.asarray(goal, float), np.asarray(st, float),
                       np.asarray(ent, float), bias, piv_px, piv_bar, cur_px, cur_bar, lc, ld, ls, lb, int(mp), int(minlegs))


def level(sym, t_entry, d, ref, pct, tf, L, mp, minlegs=30):
    ny, done_at, res, *_ = piv_all(sym, tf, L)
    bias, piv_px, piv_bar, piv_bias, cur_px, cur_bar, lc, ld, ls, lb = res
    q = qbar_at(sym, tf, L, t_entry)
    return PG.grid_level(q, np.asarray(d, np.int64), np.asarray(ref, float), float(pct), piv_px, bias, lc, ld, ls, int(mp), int(minlegs))


def apply_rule(f, rule):
    """rule: dict(tf, L, mp, minlegs, kind, ...). Rueckgabe (keep_virtuell, keep_live, tp_neu (in R), w).
    kind 'none'   : unveraendert
         'filter' : Signal nur, wenn Bedingung erfuellt (cond: Funktion X -> bool je Signal; NaN-Merkmale = erlaubt)
         'weight' : Risikogewicht w = w_bad, wenn Bedingung verletzt
         'target' : Ziel = naeher/weiter aus Grid-Linie (pct) ab dem Extrem, Modus 'min' (nur naeher) / 'set' (immer)"""
    n = len(f["R"])
    keep = np.ones(n, bool); tp = f["tp"].copy(); w = np.ones(n)
    kind = rule.get("kind", "none")
    if kind == "none":
        return keep, keep.copy(), tp, w
    Xf = feats(f["sym"], f["t_entry"], f["d"], f["ex"], f["goal"], f["st"], f["ent"], rule["tf"], rule["L"], rule["mp"], rule.get("minlegs", 30))
    if kind in ("filter", "weight"):
        good = rule["cond"](Xf)
        good = np.where(np.isfinite(Xf[:, 2]), good, True)            # ohne Grid-Daten: wie bisher
        if kind == "filter":
            keep = good
        else:
            w = np.where(good, 1.0, rule["w_bad"])
    elif kind == "target":
        lv = level(f["sym"], f["t_entry"], f["d"], f["ex"], rule["pct"], rule["tf"], rule["L"], rule["mp"], rule.get("minlegs", 30))
        g_new = (lv - f["ent"]) * f["d"]
        g_old = tp * f["rd"]
        ok = np.isfinite(g_new) & (g_new > 0.0)
        if rule.get("mode", "min") == "min":
            g = np.where(ok, np.minimum(g_old, g_new), g_old)
        else:
            g = np.where(ok, g_new, g_old)
        if rule.get("floor_r", 0.0) > 0.0:
            g = np.maximum(g, rule["floor_r"] * f["rd"])
        tp = g / f["rd"]
    live = keep.copy()
    if rule.get("guard_all", False):
        keep = np.ones(n, bool)                                        # Waechter sieht alle Signale, Grid nur live
    return keep, live, tp, w


def blocks(target, rule, guard=("pf", 30, 1.2), names=F10, filters=True, info=False):
    """Bloecke fuer eng6 (Stroeme 0..9) auf dem Ziel-Datensatz ('gft' = GFT bzw. Ersatz, 'ext' = Fremddaten bis 2021)."""
    out = []; stats = []
    for s_, nm in enumerate(names):
        per = {}
        for ds in ("ext", "gft"):
            f = fi(ds, nm)
            keep, live, tp, w = apply_rule(f, rule)
            if np.any(np.abs(tp - f["tp"]) > 1e-12):
                ST._use(ds)
                R = G.simulate(f["sym"], f["ie"], f["d"], f["rd"], tp, f["ix"])[0]
            else:
                R = f["R"]
            per[ds] = (f, keep, live, tp, w, R)
        f1, k1, l1, tp1, w1, R1 = per["ext"]; f2, k2, l2, tp2, w2, R2 = per["gft"]
        pre = f1["t_entry"] < LIM22
        # virtuelle Historie fuer den Waechter: nur Signale, die das Modul (mit Grid-Regel) virtuell fuehrt
        v1 = pre & k1
        Rv = np.r_[R1[v1], R2[k2]]
        mode, N, th = guard
        g_live = ST.guard_mask(Rv, N, mode, th) if mode != "off" else np.ones(len(Rv), bool)
        n1 = int(v1.sum())
        if target == "ext":
            f, keep, live, tp, w = f1, k1, l1, tp1, w1
            m = np.zeros(len(f["R"]), bool); m[np.nonzero(v1)[0]] = g_live[:n1]
        else:
            f, keep, live, tp, w = f2, k2, l2, tp2, w2
            m = np.zeros(len(f["R"]), bool); m[np.nonzero(k2)[0]] = g_live[n1:]
        m &= live
        ST._use(target)
        te = f["t_entry"]; tx = f["t_exit"]
        if filters:
            sp = X.spread_at(target, f["sym"], te)
            m &= np.array([(int(a // 1440) not in X.FREI) and (int(b // 1440) not in X.FREI) for a, b in zip(te, tx)], bool)
            m &= f["rd"] >= X.MINSP * sp
        blk = dict(str=s_, sym=np.full(int(m.sum()), G.SYM[f["sym"]]), dir=f["d"][m], t_entry=te[m], rd=f["rd"][m],
                   tp=tp[m], t_exit=tx[m], w=w[m])
        out.append(blk)
        stats.append((nm, len(te), int(m.sum())))
    if info:
        return out, stats
    return out
