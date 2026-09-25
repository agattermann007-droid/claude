"""Konto-Raster um die Basis (beide Datensaetze): RSI21-Parameter des Motors und Signal-Varianten.
Aufruf: python a4_raster.py [gruppe]  -> cache/a4_<ziel>.json; Zeilen: Ziel, Variante, Ausz, Busts, Netto, S6, RSI21-Ergebnis."""
import sys, os, json, time
import numpy as np
import r7konto as K, evl6 as V, r7sig as G, r7kand as KD

VAR = {
    "basis": [("Basis", "Basis", {})],
    "motor": [
        ("ohne Platz B", "Basis", dict(r21_second=0)),
        ("max 1 Verlust/Tag", "Basis", dict(r21_maxloss=1)),
        ("Gewichte 1/1/1", "Basis", dict(r21_w0=1.0, r21_w1=1.0, r21_w2=1.0)),
        ("Gewichte 1,5/0,75/0,5", "Basis", dict(r21_w0=1.5, r21_w1=0.75, r21_w2=0.5)),
        ("Gold-Faktor 0,5", "Basis", dict(r21_goldmult=0.5)),
        ("Gold-Faktor 0,85", "Basis", dict(r21_goldmult=0.85)),
        ("Ziel NAS 1,8", "Basis", dict(r21_rr_nas=1.8)),
        ("Ziel NAS 2,6", "Basis", dict(r21_rr_nas=2.6)),
        ("Ziel Gold 2,2", "Basis", dict(r21_rr_gold=2.2)),
        ("Ziel Gold 3,0", "Basis", dict(r21_rr_gold=3.0)),
        ("Zeit-Exit 288", "Basis", dict(r21_exitbars=288, r21_exitdays=0)),
        ("Zeit-Exit 576", "Basis", dict(r21_exitbars=576, r21_exitdays=0)),
        ("RSI21-Budget 0,8", "Basis", dict(r21_budget=0.8)),
        ("Nachzug ab 2 R / 1 R", "Basis", dict(r21_trail_from=2.0, r21_trail_dist=1.0)),
    ],
    "kombi": [
        ("max1 + Budget 0,8", "Basis", dict(r21_maxloss=1, r21_budget=0.8)),
        ("max1 + Budget 1,0", "Basis", dict(r21_maxloss=1, r21_budget=1.0)),
        ("max1 + Gold 0,5 + Risiko 0,55", "Basis", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.55)),
        ("max1 + Gold 0,5 + Risiko 0,6", "Basis", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.6)),
        ("max1 + Budget 0,8 + Risiko 0,55", "Basis", dict(r21_maxloss=1, r21_budget=0.8, r21_risk=0.55)),
        ("max1 + Budget 0,8 + Risiko 0,6", "Basis", dict(r21_maxloss=1, r21_budget=0.8, r21_risk=0.6)),
        ("Budget 0,8 + Risiko 0,6", "Basis", dict(r21_budget=0.8, r21_risk=0.6)),
    ],
    "k1kombi": [
        ("K1 + max1 + Budget 0,8", "K1 NAS ohne Kreuz", dict(r21_maxloss=1, r21_budget=0.8)),
        ("K1 + max1 + Budget 0,6", "K1 NAS ohne Kreuz", dict(r21_maxloss=1, r21_budget=0.6)),
        ("K1gn + max1 + Budget 0,8", "K1gn", dict(r21_maxloss=1, r21_budget=0.8)),
        ("K1gn + max1 + Budget 0,6", "K1gn", dict(r21_maxloss=1, r21_budget=0.6)),
        ("K1gn + max1 + Gold 0,5 + Budget 0,8", "K1gn", dict(r21_maxloss=1, r21_goldmult=0.5, r21_budget=0.8)),
        ("Kg + max1 + Gold 0,5 + Risiko 0,6", "Kg Gold nur M15", dict(r21_maxloss=1, r21_goldmult=0.5, r21_risk=0.6)),
    ],
    "nasx": [
        ("NAS-Kreuz 50", "NAS-Kreuz 50", {}),
        ("NAS-Kreuz 45", "NAS-Kreuz 45", {}),
        ("NAS-Kreuz 40", "NAS-Kreuz 40", {}),
    ],
    "platzb": [
        ("ohne Platz B, Risiko 0,7", "Basis", dict(r21_second=0, r21_risk=0.7)),
        ("ohne Platz B, Risiko 0,8", "Basis", dict(r21_second=0, r21_risk=0.8)),
        ("ohne Platz B, Risiko 0,9", "Basis", dict(r21_second=0, r21_risk=0.9)),
        ("ohne Platz B, Risiko 0,8, Gold 0,5", "Basis", dict(r21_second=0, r21_risk=0.8, r21_goldmult=0.5)),
        ("ohne Platz B, Risiko 0,8, max1", "Basis", dict(r21_second=0, r21_risk=0.8, r21_maxloss=1)),
    ],
    "volumen": [
        ("Volumen >= 1,0", "Volumen 1.0", {}),
        ("Volumen >= 1,2", "Volumen 1.2", {}),
        ("Volumen >= 1,5", "Volumen 1.5", {}),
        ("Volumen >= 2,0", "Volumen 2.0", {}),
        ("Volumen >= 1,5 + Risiko 0,6", "Volumen 1.5", dict(r21_risk=0.6)),
    ],
    "k1vol": [
        ("K1 + Vol 1,5 + Gold 0,5 + R 0,6", "K1 + Volumen 1.5", dict(r21_goldmult=0.5, r21_risk=0.6)),
        ("K1 + Vol 2,0 + Gold 0,5 + R 0,6", "K1 + Volumen 2.0", dict(r21_goldmult=0.5, r21_risk=0.6)),
        ("K1gn + Vol 1,5 + Gold 0,5 + R 0,6", "K1gn + Volumen 1.5", dict(r21_goldmult=0.5, r21_risk=0.6)),
        ("K1gn + Vol 1,5 + Gold 0,5 + R 0,45", "K1gn + Volumen 1.5", dict(r21_goldmult=0.5, r21_risk=0.45)),
    ],
    "london": [
        ("Gold ab 3:00 NY", "Gold ab 3 NY", {}),
    ],
    "signal": [
        ("Gold nur M15", "Kg Gold nur M15", {}),
        ("Gold nur M15 + NAS-Long ohne SMA200", "Kgn", {}),
        ("NAS ohne Kreuz", "K1 NAS ohne Kreuz", {}),
        ("NAS ohne Kreuz, max 1 Verlust", "K1 NAS ohne Kreuz", dict(r21_maxloss=1)),
        ("NAS ohne Kreuz, ohne Platz B", "K1 NAS ohne Kreuz", dict(r21_second=0)),
    ],
}

if __name__ == "__main__":
    groups = sys.argv[1].split(",") if len(sys.argv) > 1 else list(VAR)
    for target in ("gft", "ext"):
        out_f = os.path.join(K.HERE, "cache", f"a4_{target}.json")
        res = json.load(open(out_f)) if os.path.exists(out_f) else {}
        D, S, blks = K.dataset(target)
        C = G.features(D)
        for gr in groups:
            for lbl, cand, kw in VAR[gr]:
                t = time.time()
                r21 = G.r21_dict(C, KD.KAND[cand](C))
                r = K.evaluate(target, r21=r21, kw=kw)
                res[lbl] = r
                json.dump(res, open(out_f, "w"), indent=1, default=float)
                m = r["mods"]["r21"]
                print(f"{target} {lbl:<40s} Ausz {r['pay']:5.2f} Bust {r['bust']:5.3f} Netto {r['net']:5.0f} S6 {r['s6']:4.2f} "
                      f"maxS {r['mx']:4.1f}/{r['mxmax']:.0f} | RSI21 {m['pnl']:5.0f}$ {m['tr']:5.1f} Tr {m['wr']:4.1f}% [{time.time()-t:.0f}s]", flush=True)
