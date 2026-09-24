"""Letzte Verbesserungen (Screening, GFT 2022-26, 8 Stoerungen): Abschluss-Ernte fuer alle Module, Waechter-Schwelle,
Fade-Risiko, Serien-Stopp, Budget. Basis = 6.00 Ertrag/Sicher nach dem Review (x35)."""
import numpy as np, sys, json, os, eng6 as E, evl6 as V, r6, streams as ST, x35 as X
F10 = X.F10
B = dict(r6.C510, **r6.PAY3)
ERT = dict(B, db_on=0, r21_risk=0.5, nz_risk=0.35, cool_n=3, gesamtbudget=0.9, idea_cap=0.9)
SIC = dict(B, db_on=0, r21_on=0, nz_on=0, gesamtbudget=0.9, idea_cap=0.9)
BANK = dict(bank_on=1, bank_last=2, bank_minr=0.5, bank_mods=15)
target = sys.argv[1] if len(sys.argv) > 1 else "gft"
which = sys.argv[2] if len(sys.argv) > 2 else "all"
blk_cache = {}
def blocks(pf=1.2, N=30):
    key = (pf, N)
    if key not in blk_cache:
        X.g = ("pf", N, pf)
        blk_cache[key] = X.blocks_filtered(F10, target)
    return blk_cache[key]
CFG = [
    ("Ertrag (Basis)", ERT, {}, 0.75, 1.2, 30),
    ("Ertrag + Ernte alle Module (2 fehlen, 0,5 R)", dict(ERT, **BANK), dict(harv=1), 0.75, 1.2, 30),
    ("Ertrag + Ernte alle (3 fehlen, 0,3 R)", dict(ERT, **dict(BANK, bank_last=3, bank_minr=0.3)), dict(harv=1), 0.75, 1.2, 30),
    ("Ertrag + Ernte alle (immer, 0,3 R)", dict(ERT, **dict(BANK, bank_last=0, bank_minr=0.3)), dict(harv=1), 0.75, 1.2, 30),
    ("Ertrag Waechter PF > 1,1", ERT, {}, 0.75, 1.1, 30),
    ("Ertrag Waechter PF > 1,3", ERT, {}, 0.75, 1.3, 30),
    ("Ertrag Fade 0,65 %", ERT, {}, 0.65, 1.2, 30),
    ("Ertrag Serien-Stopp 4", dict(ERT, cool_n=4), {}, 0.75, 1.2, 30),
    ("Ertrag RSI21 0,6 / Noise 0,45", dict(ERT, r21_risk=0.6, nz_risk=0.45), {}, 0.75, 1.2, 30),
    ("Sicher (Basis)", SIC, {}, 0.75, 1.2, 30),
    ("Sicher + Ernte alle (2 fehlen, 0,5 R)", dict(SIC, **BANK), dict(harv=1), 0.75, 1.2, 30),
    ("Sicher + Ernte alle (3 fehlen, 0,3 R)", dict(SIC, **dict(BANK, bank_last=3, bank_minr=0.3)), dict(harv=1), 0.75, 1.2, 30),
]
if which != "all":
    keep = set(which.split("|"))
    CFG = [c for c in CFG if c[0] in keep]
out = {}
for lbl, kw, gpx, risk, pf, N in CFG:
    blks = blocks(pf, N)
    GP = E.gparams([dict(on=1, risk=risk, maxtrades=1, **gpx) for _ in F10])
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    if target == "ext":
        import pickle, prep5 as P
        V._MK = E.Market(D=pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb")), S=pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb")))
        V.set_generic(blks, GP)
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
    else:
        r = V.evaluate(Pv, GP=GP, horizons=(250, 500, 750), step=3, seeds=tuple(range(8)), skip=0.08)
    out[lbl] = r["mean"]
    print(V.line(f"{target} {lbl}", r["mean"]), f"| gueltig/J {r['mean']['valid']:.1f}", flush=True)
json.dump(out, open(f"x36_{target}.json", "w"), indent=1, default=float)
