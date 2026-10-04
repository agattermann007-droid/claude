"""Stufe 8: Gegenprobe der Kandidaten im Konto-Replikat auf Fremddaten 2006-2021 (eng6, gleiche Regeln)."""
import os, json, pickle
import eng6 as E, evl6 as V, y7_konto as Y, n8_konto as NK, n8_port as NP, prep5 as P

V._MK = E.Market(D=pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb")), S=pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb")))
fb = Y.fade_blocks("ext")
sp = Y.spike_block("ext", 10, dict(Y.SPIKE, kmin=0.20), only_dir=1)

def build(new, risks):
    blks = list(fb) + [sp]
    gps = [dict(on=1, risk=0.75, maxtrades=1, harv=1) for _ in fb] + [dict(on=1, risk=0.75, maxtrades=1, harv=1)]
    for nm in new:
        s_ = len(blks)
        sym, gen, args = NP.LIB[nm]
        blks.append(NK.block(sym, gen, args, s_))
        rv = risks.get(nm, 0.75)
        gps.append(dict(dict(on=1, risk=0.75, maxtrades=1, harv=1), **rv) if isinstance(rv, dict) else dict(on=1, risk=rv, maxtrades=1, harv=1))
    for i, b in enumerate(blks):
        b["str"] = i
    return blks, gps

DD3 = NP.DD3
CF = [
    ("7.10+LW 0.5 mb4+XASIA DD4 fmin0.1", ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(NP.DD4, ddfmin=0.1)),
    ("7.10+LW 0.5 mb4+XASIA DD3.5/1.25 fmin0.1", ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(ddfull=3.5, ddmin=1.25, ddfmin=0.1)),
]
CF_ALT = [
    ("7.10", [], {}, {}),
    ("7.10 DD3 fmin0.1", [], {}, dict(DD3, ddfmin=0.1)),
    ("7.10+LW 0.5 mb4 DD3 fmin0.1", ["LW"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.1)),
    ("7.10+LW 0.5 mb4+XASIA DD3 fmin0.1", ["LW", "XASIA"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.1)),
    ("7.10+LW 0.5 mb4 DD3 fmin0.2", ["LW"], {"LW": dict(risk=0.5, minbuf=4.0)}, dict(DD3, ddfmin=0.2)),
]
out = json.load(open("ergebnisse/n8_ext.json")) if os.path.exists("ergebnisse/n8_ext.json") else {}
for lbl, new, risks, kw in CF:
    blks, gps = build(new, risks)
    GP = E.gparams(gps); V.set_generic(blks, GP)
    r = V.evaluate(E.params(**dict(Y.BASE, **kw)), GP=GP, horizons=(250, 500), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")
    out[lbl] = r["mean"]
    print(NK.line("ext " + lbl, r["mean"]) + " | " + NP.btype(r["mean"]), flush=True)
    json.dump(out, open("ergebnisse/n8_ext.json", "w"), default=float, indent=1)
