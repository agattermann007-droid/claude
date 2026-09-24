"""Build 6.20 (Probability Grid): Screening im Konto-Replikat. Basis = 6.10 (Ertrag bzw. Sicher, gueltiger Tag ab 50,50 $),
Varianten = Grid-Regeln fuer Fades (Filter, Ziel, Gewicht) und fuer RSI21/Noise (Filter).
Aufruf: python x40.py gft|ext [Variantenliste mit |] [seeds]
gft = GFT-Daten bzw. GFT-Ersatz (mk_proxy), ext = Fremddaten 2006-21."""
import numpy as np, sys, json, os, pickle, time
import eng6 as E, evl6 as V, r6, x35 as X, prep5 as P, gsig as G
import pg_blocks as PB, pg_old as PO

F10 = X.F10
B = dict(r6.C510, **r6.PAY3)
RES = 0.505
ERT = dict(B, validpct=RES, db_on=0, r21_risk=0.5, nz_risk=0.35, cool_n=3, gesamtbudget=0.9, idea_cap=0.9,
           bank_on=1, bank_last=3, bank_minr=0.3, bank_mods=15)
SIC = dict(B, validpct=RES, db_on=0, r21_on=0, nz_on=0, gesamtbudget=0.9, idea_cap=0.9)


def market(target, r21_rule=None, nz_rule=None):
    if target == "ext":
        D = pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb"))
        S = pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb"))
    else:
        PB.ST._use("gft")
        D = G.data()
        S = pickle.load(open(os.path.join(P.OUT, "sig5.pkl"), "rb"))
    rb = nb = None
    if r21_rule is not None:
        Xr = PO.r21_features(D, S, r21_rule["tf"], r21_rule["L"], r21_rule["mp"], r21_rule.get("minlegs", 30))
        good = np.where(np.isfinite(Xr[:, 2]), r21_rule["cond"](Xr), True)
        rb = ~good
    if nz_rule is not None:
        Xz = PO.nz_features(D, S, nz_rule["tf"], nz_rule["L"], nz_rule["mp"], nz_rule.get("minlegs", 30))
        good = np.where(np.isfinite(Xz[:, 2]), nz_rule["cond"](Xz), True)
        nb = ~good
    return PO.GridMarket(D, S, rb, nb)


def evaluate(target, kw, gpx, fade_rule, r21_rule=None, nz_rule=None, seeds=8, guard=("pf", 30, 1.2), step=None):
    blks, info = PB.blocks(target, fade_rule, guard=guard, info=True)
    V._MK = market(target, r21_rule, nz_rule)
    GP = E.gparams([dict(on=1, risk=0.75, maxtrades=1, **gpx) for _ in F10])
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    if target == "ext":
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=step or 9, seeds=tuple(range(min(seeds, 4))), warm="2006-09-01", end="2021-12-31")
    else:
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=step or 3, seeds=tuple(range(seeds)), skip=0.08)
    r["mean"]["fade_live"] = sum(x[2] for x in info)
    return r["mean"]


if __name__ == "__main__":
    import pg_rules as RU
    target = sys.argv[1]
    which = sys.argv[2] if len(sys.argv) > 2 else "all"
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    step = int(sys.argv[4]) if len(sys.argv) > 4 else None
    cfgs = RU.variants()
    if which != "all":
        keep = which.split("|")
        cfgs = [c for c in cfgs if c[0] in keep or any(c[0].startswith(k.rstrip("*")) for k in keep if k.endswith("*"))]
    fn = os.path.join("ergebnisse", f"x40_{target}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl, base, gpx, fr, rr, zr in cfgs:
        key = f"{lbl} [{seeds}{'' if step is None else f' s{step}'}]"
        if key in res:
            print(V.line(f"{target} {lbl}", res[key]), "(Cache)", flush=True)
            continue
        t = time.time()
        kw = ERT if base == "ERT" else SIC
        m = evaluate(target, kw, gpx, fr, rr, zr, seeds=seeds, step=step)
        res[key] = m
        json.dump(res, open(fn, "w"), indent=1, default=float)
        print(V.line(f"{target} {lbl}", m), f"| Fades live {m['fade_live']} | gueltig/J {m['valid']:.1f} [{time.time() - t:.0f}s]", flush=True)
