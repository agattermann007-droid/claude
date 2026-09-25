"""Feinbewertung (volle Stoerungen): Basis gegen Risiko-Struktur-Varianten des RSI21-Moduls auf beiden Datensaetzen.
gft: 16 Stoerungen, 8 % ausgelassen; ext: 8 Stoerungen. -> cache/a5_<ziel>.json"""
import sys, os, json, time
import r7konto as K, evl6 as V, r7sig as G, r7kand as KD

VAR = [
    ("Basis (6.10)", {}),
    ("max 1 Verlust/Tag", dict(r21_maxloss=1)),
    ("max1 + Gold 0,5 + Risiko 0,55", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.55)),
    ("max1 + Gold 0,5 + Risiko 0,6", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.6)),
    ("max1 + Gold 0,5 + Risiko 0,65", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.65)),
    ("max1 + Gold 0,4 + Risiko 0,6", dict(r21_maxloss=1, r21_goldmult=0.4, r21_risk=0.6)),
    ("max1 + Gold 0,6 + Risiko 0,6", dict(r21_maxloss=1, r21_goldmult=0.6, r21_risk=0.6)),
    ("max1 + Budget 0,8", dict(r21_maxloss=1, r21_budget=0.8)),
    ("max1 + Gold 0,5 + Risiko 0,6 + Budget 0,8", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.6, r21_budget=0.8)),
    ("Gold 0,5 + Risiko 0,6", dict(r21_goldmult=0.5, r21_risk=0.6)),
]
VARS = [  # (Label, Kandidat, Motor-Parameter)
    ("Volumen 1,5", "Volumen 1.5", {}),
    ("Volumen 2,0", "Volumen 2.0", {}),
    ("Volumen 1,5 + max1 + Gold 0,5 + Risiko 0,6", "Volumen 1.5", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.6)),
    ("Volumen 1,5 + max1 + Gold 0,5 + Risiko 0,65", "Volumen 1.5", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.65)),
    ("Volumen 2,0 + max1 + Gold 0,5 + Risiko 0,65", "Volumen 2.0", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.65)),
    ("Volumen 2,0 + max1 + Gold 0,5 + Risiko 0,7", "Volumen 2.0", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.7)),
    ("Volumen 1,5 + max1 + Gold 0,5 + Risiko 0,55", "Volumen 1.5", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.55)),
    ("Volumen 1,5 + max1 + Gold 0,5 + Risiko 0,7", "Volumen 1.5", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.7)),
    ("Volumen 1,3 + max1 + Gold 0,5 + Risiko 0,6", "Volumen 1.3", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.6)),
    ("Volumen 1,7 + max1 + Gold 0,5 + Risiko 0,6", "Volumen 1.7", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.6)),
    ("Volumen 1,5 + max1 + Gold 0,4 + Risiko 0,6", "Volumen 1.5", dict(r21_maxloss=1, r21_goldmult=0.4, r21_risk=0.6)),
    ("Volumen 1,5 + max1 + Gold 0,6 + Risiko 0,6", "Volumen 1.5", dict(r21_maxloss=1, r21_goldmult=0.6, r21_risk=0.6)),
    ("Volumen 1,5 + Gold 0,5 + Risiko 0,6", "Volumen 1.5", dict(r21_goldmult=0.5, r21_risk=0.6)),
]

if __name__ == "__main__":
    targets = sys.argv[1].split(",") if len(sys.argv) > 1 else ["gft", "ext"]
    for target in targets:
        out_f = os.path.join(K.HERE, "cache", f"a5_{target}.json")
        res = json.load(open(out_f)) if os.path.exists(out_f) else {}
        D, S, blks = K.dataset(target)
        C = G.features(D)
        todo = [(lbl, "Basis", kw) for lbl, kw in VAR] + VARS
        for lbl, cand, kw in todo:
            r21 = G.r21_dict(C, KD.KAND[cand](C))
            if lbl in res:
                r = res[lbl]
            else:
                t = time.time()
                if target == "ext":
                    r = K.evaluate(target, r21=r21, kw=kw, seeds=tuple(range(8)))
                else:
                    r = K.evaluate(target, r21=r21, kw=kw, quick=False)
                res[lbl] = r
                json.dump(res, open(out_f, "w"), indent=1, default=float)
            m = r["mods"]["r21"]
            print(f"{target} {lbl:<44s} Ausz {r['pay']:5.2f} Bust {r['bust']:5.3f} Netto {r['net']:5.0f} maxDD {r['maxdd']:4.0f} S6 {r['s6']:4.2f} "
                  f"maxS {r['mx']:4.1f}/{r['mxmax']:.0f} | RSI21 {m['pnl']:5.0f}$ {m['tr']:5.1f} Tr {m['wr']:4.1f}%", flush=True)
