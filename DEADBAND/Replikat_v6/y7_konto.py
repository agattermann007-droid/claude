"""V7-Forschung, Stufe 3: Konto-Replikat (eng6, alle GFT-Regeln, strenge Lesart) - Basis im Stil von 7.00 gegen neue Stroeme.
Aufruf: python y7_konto.py gft|ext [varianten...]
Basis (soweit eng6 sie kennt): 10 Fades 0,75 % mit Portfolio-Waechter (PF der letzten 200 virtuellen Fades > 1,15, nur
Ergebnisse vor dem Einstieg, 600 Tage), RSI21 0,50 %, Noise 0,45 %, Pufferkurve 5/2,5/0,2, unter Start x0,95,
Mindestauszahlung 105 $ (= 131,25 $ Gewinn), Abschluss-Ernte immer (5), Serien-Stopp 3, Budget/Idee 0,9 %, gueltiger Tag
ab 50,50 $, Schutz gueltiger Tage (valid_stop), DEADBAND aus. Nicht im 6.10-Motor: Probability Grid, Einstand RSI21/Noise,
Schutz je Modul (6.50), Regime-Groesse - die Basis ist deshalb ein 7.00-NAHER Stand, kein bitgleicher.
Bewertet wird der UNTERSCHIED Basis -> Basis + neuer Strom."""
import sys, os, json, pickle, numpy as np
import eng6 as E, evl6 as V, r6, gsig as G, gext, cands as K, scan6 as S, y7sig as Y, prep5 as P
import x35 as X

F10 = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
LIM22 = np.datetime64("2022-01-01", "m").astype(np.int64)
SPIKE = dict(ts=510, nbars=2, wait=6, xm=660, kmin=0.25, buf=0.25, tgtfrac=0.5)


def _use(ds):
    G._D = gext.data_ext() if ds == "ext" else None
    if ds != "ext":
        G.data()
    K._CACHE.clear()


def fade_virtual(ds):
    """alle virtuellen Fade-Trades eines Datensatzes: Block je Modul + R + Zeitpunkt, ab dem das Ergebnis feststeht."""
    _use(ds)
    out = []
    for nm in F10:
        p = K.FADES[nm]
        b, (ie, d, rd, tp, ix) = K.fade(0, **p)
        R, why, held, mfe, mae, iout = G.simulate(p["sym"], ie, d, rd, tp, ix)
        ny = G.data()[p["sym"]]["ny"]
        tk = ny[np.minimum(iout + 1, len(ny) - 1)]
        out.append((nm, p["sym"], b, R, tk))
    return out


def port_live(allv, pf_th=1.15, N=200, days=600):
    """Portfolio-Waechter wie 6.40: live, wenn PF der letzten N Ergebnisse (bekannt vor dem Einstieg, <= days alt) > pf_th."""
    tk = np.concatenate([v[4] for v in allv]); Rk = np.concatenate([v[3] for v in allv])
    o = np.argsort(tk, kind="stable"); tk = tk[o]; Rk = Rk[o]
    masks = []
    for nm, sym, b, R, _ in allv:
        te = b["t_entry"]; live = np.zeros(len(te), bool)
        for i, t in enumerate(te):
            j = np.searchsorted(tk, t, side="left")
            w = Rk[max(0, j - N):j]; tw = tk[max(0, j - N):j]
            w = w[tw >= t - days * 1440]
            if len(w) < N:
                continue
            pos = w[w > 0].sum(); neg = -w[w < 0].sum()
            live[i] = (pos / neg if neg > 0 else 9.9) > pf_th
        masks.append(live)
    return masks


def fade_blocks(target):
    """Fade-Bloecke mit Portfolio-Waechter (Historie ueber beide Datensaetze), Feiertage und Stop >= 6 Spreads wie x35."""
    ve = fade_virtual("ext"); vg = fade_virtual("gft")
    comb = []
    for (nm, sym, be, Re, tke), (_, _, bg, Rg, tkg) in zip(ve, vg):
        pre = be["t_entry"] < LIM22
        b = {k: (np.r_[v[pre], bg[k]] if isinstance(v, np.ndarray) and len(v) == len(pre) else v) for k, v in be.items()}
        comb.append((nm, sym, b, np.r_[Re[pre], Rg], np.r_[tke[pre], tkg]))
    lm = port_live(comb)
    _use(target)
    res = []
    for s_, ((nm, sym, b, R, tk), live) in enumerate(zip(comb, lm)):
        te = b["t_entry"]; tx = b["t_exit"]
        m = live & ((te < LIM22) if target == "ext" else (te >= LIM22))
        sp = X.spread_at(target, sym, te)
        m &= np.array([(int(a // 1440) not in X.FREI) and (int(c // 1440) not in X.FREI) for a, c in zip(te, tx)], bool)
        m &= b["rd"] >= X.MINSP * sp
        blk = {k: (v[m] if isinstance(v, np.ndarray) and len(v) == len(m) else v) for k, v in b.items()}
        blk["str"] = s_
        res.append(blk)
        print(f"  {nm}: {int(m.sum())} live von {int(((te < LIM22) if target == 'ext' else (te >= LIM22)).sum())}", flush=True)
    return res


def spike_block(target, s_, sp=SPIKE, only_dir=0):
    _use(target)
    D, ny, days, t_end, atr = S.prep("NAS")
    ie, d, rd, tp, ix = Y.spike_fade(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr,
                                    sp["ts"], sp["nbars"], sp["wait"], sp["xm"], sp["kmin"], sp["buf"], sp["tgtfrac"], only_dir)
    te = ny[ie]
    keep = np.array([int(a // 1440) not in X.FREI for a in te], bool)
    b = K.block("NAS", ie[keep], d[keep], rd[keep], tp[keep], ix[keep], s_)
    print(f"  SPIKE: {int(keep.sum())} Signale", flush=True)
    return b


BASE = dict(r6.SAFE, validpct=0.505, minpayout=105.0, db_on=0, r21_risk=0.5, nz_risk=0.45, cool_n=3, gesamtbudget=0.9,
            idea_cap=0.9, bank_on=1, bank_last=5, bank_minr=0.3, bank_mods=15, ddfull=5.0, ddmin=2.5, ddfmin=0.2,
            belowstart=0.95, valid_stop=1, ge_mode=1, ge_rueck=0.0, db_tp1r=1.5, db_be=0.05, db_tp1f=0.5)


def run_cfg(target, label, kw, blks, gps, out):
    GP = E.gparams(gps)
    V.set_generic(blks, GP)
    Pv = E.params(**dict(BASE, **kw))
    if target == "ext":
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
    else:
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500), step=3, seeds=tuple(range(8)), skip=0.05, end="2025-12-31")
    out[label] = {h: {k: v for k, v in r[h].items()} for h in r if h != "mean"}
    out[label]["mean"] = r["mean"]
    print(V.line(f"{target} {label}", r["mean"]), flush=True)


if __name__ == "__main__":
    target = sys.argv[1]
    want = sys.argv[2:]
    if target == "ext":
        V._MK = E.Market(D=pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb")), S=pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb")))
    fb = fade_blocks(target)
    gpf = [dict(on=1, risk=0.75, maxtrades=1, harv=1) for _ in F10]
    out = {}
    def sp(**kw):
        return dict(SPIKE, **kw)
    g = lambda r: dict(on=1, risk=r, maxtrades=1, harv=1)
    cfgs = {
        "Basis 7.00-nah": (fb, gpf),
        "+ Spike nur Long k0.25 0,75 %": (fb + [spike_block(target, 10, only_dir=1)], gpf + [g(0.75)]),
        "+ Spike nur Long k0.20 0,75 %": (fb + [spike_block(target, 10, sp(kmin=0.20), only_dir=1)], gpf + [g(0.75)]),
        "+ Spike nur Long k0.20 0,90 %": (fb + [spike_block(target, 10, sp(kmin=0.20), only_dir=1)], gpf + [g(0.90)]),
        "+ Spike nur Long k0.15 0,75 %": (fb + [spike_block(target, 10, sp(kmin=0.15), only_dir=1)], gpf + [g(0.75)]),
        "+ Spike beide k0.25 0,75 %": (fb + [spike_block(target, 10)], gpf + [g(0.75)]),
    }
    for lbl, (blks, gps) in cfgs.items():
        if want and not any(w in lbl for w in want):
            continue
        run_cfg(target, lbl, {}, blks, gps, out)
    json.dump(out, open(f"ergebnisse/y7_konto_{target}.json", "w"), indent=1, default=float)
