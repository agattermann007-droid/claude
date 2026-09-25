"""Build 6.40: Regime-Waechter der Fades auf Signal-Ebene. Alle virtuellen Signale der 10 Module mit Grid-Regel S (wie 6.20,
N1800 ohne Grid), Fremddaten bis 2021 + GFT-Ersatz ab 2022 in einer Kette (so rechnet auch der Kontomotor den Waechter).
Verglichen wird, welche Signale ein Waechter live laesst: R je Jahr und Signale je Jahr je Periode (2006-13, 2014-21,
2022-25), schlimmster Rueckgang der live-Signale in R.

Waechter (live = True):
  modul   : PF der letzten N Signale des Moduls > th (6.00-6.30: N 30, th 1,2)
  port    : PF der letzten N abgeschlossenen Signale ALLER Module > th
  oder    : modul ODER port (Modul schwach, Portfolio stark)
  und     : modul(th_m) UND port (Modul gut und Portfolio gut)
Abgeschlossen = geplanter Zeit-Ausstieg vor dem Einstieg des neuen Signals (Studie, vorsichtig); der Kontomotor nutzt
dagegen den Zeitpunkt, zu dem der EA das Ergebnis kennt (known_time, port_live_ea - geprueft in t_port_640.py).
Aufruf: python pg_guard.py   (Ausgabe auch nach ergebnisse/pg_guard.txt)"""
import numpy as np, sys
import pg_blocks as PB, x41, streams as ST

LIM22 = ST.LIM22
PER = (("2006-13", "2006-01-01", "2014-01-01"), ("2014-21", "2014-01-01", "2022-01-01"), ("2022-25", "2022-01-01", "2026-01-01"))


def chain(rule=x41.S70_OHNE, names=PB.F10):
    """Virtuelle Signalkette je Modul: t_entry, t_exit, R (Grid-Regel angewandt), Modulindex."""
    out = []
    exempt = set(rule.get("exempt", ()))
    for s_, nm in enumerate(names):
        per = {}
        for ds in ("ext", "gft"):
            f = PB.fi(ds, nm)
            keep, live, tp, w = PB.apply_rule(f, rule if nm not in exempt else dict(kind="none"))
            per[ds] = (f, keep)
        f1, k1 = per["ext"]; f2, k2 = per["gft"]
        v1 = (f1["t_entry"] < LIM22) & k1
        te = np.r_[f1["t_entry"][v1], f2["t_entry"][k2]]
        tx = np.r_[f1["t_exit"][v1], f2["t_exit"][k2]]
        R = np.r_[f1["R"][v1], f2["R"][k2]]
        out.append(dict(name=nm, te=te, tx=tx, R=R, s=np.full(len(R), s_)))
    return out


def pf(w):
    pos = w[w > 0].sum(); neg = -w[w < 0].sum()
    return pos / neg if neg > 0 else 9.9


def guard_module(R, N, th):
    live = np.zeros(len(R), bool)
    for i in range(N, len(R)):
        live[i] = pf(R[i - N:i]) > th
    return live


def guard_port(ch, N, th):
    """je Modul: live-Maske nach dem Portfolio-PF der letzten N abgeschlossenen Signale aller Module."""
    te = np.concatenate([c["te"] for c in ch]); tx = np.concatenate([c["tx"] for c in ch]); R = np.concatenate([c["R"] for c in ch])
    o = np.argsort(tx, kind="stable"); tx_s = tx[o]; R_s = R[o]
    out = []
    for c in ch:
        k = np.searchsorted(tx_s, c["te"], side="left")         # Anzahl vor dem Einstieg abgeschlossener Signale
        live = np.zeros(len(c["R"]), bool)
        for i, kk in enumerate(k):
            if kk >= N:
                live[i] = pf(R_s[kk - N:kk]) > th
        out.append(live)
    return out


_OUT = []


def evaluate(ch, masks, label):
    rows = []
    for (pn, a, b) in PER:
        lo = np.datetime64(a, "m").astype(np.int64); hi = np.datetime64(b, "m").astype(np.int64)
        yrs = (hi - lo) / (365.25 * 1440)
        if pn == "2022-25":
            yrs = 4.0
        r = 0.0; n = 0; allr = 0.0; alln = 0
        seq_t = []; seq_r = []
        for c, m in zip(ch, masks):
            sel = (c["te"] >= lo) & (c["te"] < hi)
            r += c["R"][sel & m].sum(); n += int((sel & m).sum())
            allr += c["R"][sel].sum(); alln += int(sel.sum())
            seq_t.append(c["tx"][sel & m]); seq_r.append(c["R"][sel & m])
        t = np.concatenate(seq_t); rr = np.concatenate(seq_r)
        o = np.argsort(t); cum = np.cumsum(rr[o])
        dd = float((np.maximum.accumulate(np.r_[0.0, cum]) - np.r_[0.0, cum]).max()) if len(cum) else 0.0
        rows.append(f"{pn}: {r / yrs:+6.1f} R/J {n / yrs:5.1f} Sig/J PF {pf(np.concatenate(seq_r)) if len(rr) else 0:4.2f} DD {dd:5.1f} R (alle {allr / yrs:+6.1f} R/J {alln / yrs:5.1f})")
    s = f"{label:<34s} | " + " | ".join(rows)
    print(s, flush=True); _OUT.append(s)


if __name__ == "__main__":
    ch = chain()
    N0 = 30
    evaluate(ch, [np.ones(len(c["R"]), bool) for c in ch], "ohne Waechter")
    for th in (1.0, 1.1, 1.2, 1.3):
        evaluate(ch, [guard_module(c["R"], N0, th) for c in ch], f"Modul PF30 > {th}")
    for N in (30, 60, 100, 150, 200):
        for th in (1.0, 1.1, 1.2, 1.3):
            evaluate(ch, guard_port(ch, N, th), f"Portfolio PF{N} > {th}")
    for N in (60, 100, 150):
        for th in (1.1, 1.2, 1.3):
            gp = guard_port(ch, N, th)
            evaluate(ch, [guard_module(c["R"], 30, 1.2) | g for c, g in zip(ch, gp)], f"Modul1.2 ODER Port{N}>{th}")
            evaluate(ch, [guard_module(c["R"], 30, 1.0) & g for c, g in zip(ch, gp)], f"Modul1.0 UND Port{N}>{th}")
    import os
    open(os.path.join("ergebnisse", "pg_guard.txt"), "w").write("\n".join(_OUT) + "\n")


# ---------------------------------------------------------------- Bloecke fuer den Kontomotor (wie pg_blocks.blocks)
def port_live(te_all, tx_all, R_all, N, th, window_days=600):
    """live-Maske je Signal (Reihenfolge wie te_all) nach dem PF der letzten N abgeschlossenen Signale aller Module.
    EA-getreu: die N Signale muessen im Fenster der letzten window_days Tage abgeschlossen sein (Historie beim Start)."""
    o = np.argsort(tx_all, kind="stable"); tx_s = tx_all[o]; R_s = R_all[o]
    k = np.searchsorted(tx_s, te_all, side="left")
    live = np.zeros(len(te_all), bool)
    for i, kk in enumerate(k):
        if kk < N:
            continue
        if window_days and tx_s[kk - N] < te_all[i] - int(window_days) * 1440:
            continue
        live[i] = pf(R_s[kk - N:kk]) > th
    return live


_KT = {}


def known_time(ds, f):
    """Zeitpunkt, zu dem der EA das virtuelle Ergebnis kennt: FadeKerze(b) verbucht es am Ende der Kerze b = Open der
    naechsten Kerze nx. Stop/Ziel in Kerze iout -> Zeit der Kerze iout+1; Zeit-Ausstieg am Open der Kerze iout -> deren Zeit."""
    key = (ds, f["name"])
    if key not in _KT:
        import cands as K
        ST._use(ds)
        D, ny, days, t_end, atr = K._prep(f["sym"])
        io = np.asarray(f["iout"], np.int64)
        nxt = np.minimum(io + 1, len(ny) - 1)
        kt = np.where(f["why"] == 0, ny[np.minimum(io, len(ny) - 1)], ny[nxt])
        kt = np.where((f["why"] != 0) & (io + 1 >= len(ny)), ny[-1] + 5, kt)
        _KT[key] = kt.astype(np.int64)
    return _KT[key]


def port_live_ea(te_all, kt_all, mi_all, R_all, N, th, window_days=600):
    """wie port_live, aber mit dem Zeitpunkt, zu dem der EA das Ergebnis kennt (kt), Reihenfolge (kt, Modul) und nur
    Ergebnisse mit kt < Einstieg (te) - so rechnet FadeWaechterOk im Portfolio-Modus."""
    o = np.lexsort((mi_all, kt_all)); kt_s = kt_all[o]; R_s = R_all[o]
    k = np.searchsorted(kt_s, te_all, side="left")
    live = np.zeros(len(te_all), bool)
    for i, kk in enumerate(k):
        if kk < N:
            continue
        if window_days and kt_s[kk - N] < te_all[i] - int(window_days) * 1440:
            continue
        live[i] = pf(R_s[kk - N:kk]) > th
    return live


def blocks_port(target, rule, N, th, window_days=600, names=PB.F10, combine=None, mod_guard=("pf", 30, 1.2), filters=True, info=False,
                ea_time=True):
    """Fade-Bloecke mit Portfolio-Waechter. combine: None = nur Portfolio, 'and' / 'or' = mit Modul-Waechter mod_guard.
    ea_time: Ergebnisse zaehlen ab dem Zeitpunkt, zu dem der EA sie kennt (sonst erst nach dem geplanten Zeit-Ausstieg)."""
    import x35 as X, gsig as G
    exempt = set(rule.get("exempt", ()))
    mods = []
    for s_, nm in enumerate(names):
        per = {}
        for ds in ("ext", "gft"):
            f = PB.fi(ds, nm)
            keep, live, tp, w = PB.apply_rule(f, rule if nm not in exempt else dict(kind="none"))
            assert not np.any(np.abs(tp - f["tp"]) > 1e-12)
            per[ds] = (f, keep, live, tp, w, f["R"])
        f1, k1, l1, tp1, w1, R1 = per["ext"]; f2, k2, l2, tp2, w2, R2 = per["gft"]
        v1 = (f1["t_entry"] < LIM22) & k1
        kt1 = known_time("ext", f1); kt2 = known_time("gft", f2)
        mods.append(dict(per=per, v1=v1, Rv=np.r_[R1[v1], R2[k2]], te=np.r_[f1["t_entry"][v1], f2["t_entry"][k2]],
                         tx=np.r_[f1["t_exit"][v1], f2["t_exit"][k2]], kt=np.r_[kt1[v1], kt2[k2]]))
    te_all = np.concatenate([m["te"] for m in mods]); tx_all = np.concatenate([m["tx"] for m in mods])
    R_all = np.concatenate([m["Rv"] for m in mods])
    if ea_time:
        kt_all = np.concatenate([m["kt"] for m in mods])
        mi_all = np.concatenate([np.full(len(m["Rv"]), i) for i, m in enumerate(mods)])
        pl = port_live_ea(te_all, kt_all, mi_all, R_all, N, th, window_days)
    else:
        pl = port_live(te_all, tx_all, R_all, N, th, window_days)
    out = []; stats = []; pos = 0
    for s_, (nm, md) in enumerate(zip(names, mods)):
        n = len(md["Rv"])
        g_live = pl[pos:pos + n].copy(); pos += n
        if combine is not None:
            mode, Nm, thm = mod_guard
            gm = ST.guard_mask(md["Rv"], Nm, mode, thm)
            if window_days:
                gm &= PB.guard_window(md["te"], Nm, window_days)
            g_live = (g_live & gm) if combine == "and" else (g_live | gm)
        f1, k1, l1, tp1, w1, R1 = md["per"]["ext"]; f2, k2, l2, tp2, w2, R2 = md["per"]["gft"]
        v1 = md["v1"]; n1 = int(v1.sum())
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


# ---------------------------------------------------------------- 6.40: zusammengesetzte Waechter (alle Bedingungen UND)
def live_scope(te_all, kt_all, mi_all, R_all, grp_all, N, th, window_days=600):
    """PF der letzten N bekannten Ergebnisse (kt < te) innerhalb der eigenen Gruppe (grp: 0 = alle, sonst Symbol/Modul)."""
    live = np.zeros(len(te_all), bool)
    for g in np.unique(grp_all):
        sel = np.nonzero(grp_all == g)[0]
        live[sel] = port_live_ea(te_all[sel], kt_all[sel], mi_all[sel], R_all[sel], N, th, window_days)
    return live


def blocks_multi(target, rule, conds, window_days=600, names=PB.F10, filters=True, info=False, w_extra=None):
    """conds: Liste (Bereich, N, th) mit Bereich 'port' (alle Fades), 'sym' (Fades desselben Symbols), 'mod' (Modul),
    alle mit UND verknuepft (EA-Zeitpunkt, Fenster window_days). w_extra: optional (conds2, w) - Signale, die conds erfuellen,
    aber conds2 nicht, bekommen das Risikogewicht w (sonst 1)."""
    import x35 as X, gsig as G
    exempt = set(rule.get("exempt", ()))
    mods = []
    for s_, nm in enumerate(names):
        per = {}
        for ds in ("ext", "gft"):
            f = PB.fi(ds, nm)
            keep, live, tp, w = PB.apply_rule(f, rule if nm not in exempt else dict(kind="none"))
            per[ds] = (f, keep, live, tp, w, f["R"])
        f1, k1, l1, tp1, w1, R1 = per["ext"]; f2, k2, l2, tp2, w2, R2 = per["gft"]
        v1 = (f1["t_entry"] < LIM22) & k1
        kt1 = known_time("ext", f1); kt2 = known_time("gft", f2)
        mods.append(dict(per=per, v1=v1, Rv=np.r_[R1[v1], R2[k2]], te=np.r_[f1["t_entry"][v1], f2["t_entry"][k2]],
                         kt=np.r_[kt1[v1], kt2[k2]], sym=f1["sym"]))
    te_all = np.concatenate([m["te"] for m in mods]); kt_all = np.concatenate([m["kt"] for m in mods])
    R_all = np.concatenate([m["Rv"] for m in mods])
    mi_all = np.concatenate([np.full(len(m["Rv"]), i) for i, m in enumerate(mods)])
    sy_all = np.concatenate([np.full(len(m["Rv"]), 1 if m["sym"] == "NAS" else 2) for m in mods])

    def mask(cs):
        L = np.ones(len(te_all), bool)
        for scope, N, th in cs:
            grp = np.zeros(len(te_all), np.int64) if scope == "port" else (sy_all if scope == "sym" else mi_all + 10)
            L &= live_scope(te_all, kt_all, mi_all, R_all, grp, N, th, window_days)
        return L
    pl = mask(conds)
    wl = np.ones(len(te_all))
    if w_extra is not None:
        c2, wv = w_extra
        l2m = mask(c2)
        wl = np.where(pl & ~l2m, wv, 1.0)
    out = []; stats = []; pos = 0
    for s_, (nm, md) in enumerate(zip(names, mods)):
        n = len(md["Rv"])
        g_live = pl[pos:pos + n].copy(); g_w = wl[pos:pos + n].copy(); pos += n
        f1, k1, l1, tp1, w1, R1 = md["per"]["ext"]; f2, k2, l2, tp2, w2, R2 = md["per"]["gft"]
        v1 = md["v1"]; n1 = int(v1.sum())
        if target == "ext":
            f, keep, live, tp, w = f1, k1, l1, tp1, w1.copy()
            m = np.zeros(len(f["R"]), bool); m[np.nonzero(v1)[0]] = g_live[:n1]
            ww = np.ones(len(f["R"])); ww[np.nonzero(v1)[0]] = g_w[:n1]
        else:
            f, keep, live, tp, w = f2, k2, l2, tp2, w2.copy()
            m = np.zeros(len(f["R"]), bool); m[np.nonzero(k2)[0]] = g_live[n1:]
            ww = np.ones(len(f["R"])); ww[np.nonzero(k2)[0]] = g_w[n1:]
        w = w * ww
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
