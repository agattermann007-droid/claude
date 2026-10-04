"""Vergleich aeltester Stand (Build 3.00 = DEADBAND v25, nur Ausbruch) gegen 8.10 im selben Replikat (eng6, gepaart).
Firmenregeln wie in allen Stufe-8-Bewertungen (strenge Floating-Lesart rule_losers, Margin/Hebel, Mindestauszahlung 105 $,
Deckel 6 % fuer die ersten zwei Auszahlungen). EA-Logik von 3.00 (Kopf + Eingaben der Datei aus dem Drive):
 nur DEADBAND, Session 3-12 NY, Risiko 0,259/0,288 % x Profil (Sicher 1,0 / Mittel 1,2), Stundenfaktor 1,3 ab 9 NY,
 Tranche bei 3,5 R ohne Teilverkauf, Stop danach +0,5 R, Endziel 8/10 R, Zeit-Exit 192 M15, 1 Trade/Tag, Budget 0,8 %,
 Sicherheitsbremse v19 (x0,5 unter 1,3 % Puffer), Floating-Bremse 0,85 % netto, Tagesstopp 2,4 %, Ernte ab 16 NY (2 R),
 KEINE Pufferkurve, kein unter-Start-Faktor, keine Wochenend-Pause, keine Gewinn-Ernte, keine 5.10-Bremsen.
Nicht nachgebildet: HarvestAnyR 4 der Profile (jederzeit ernten ab 4 R Vorlauf). Gueltiger Tag ab 0,50 % (8.10: 0,505 %).
Aufruf: python z8_v300.py gft|ext"""
import sys, os, pickle, json
import eng6 as E, evl6 as V, prep5 as P, z8

V300 = dict(rule_losers=1, float_losers=0, swap_guard=0.0, validpct=0.50, minpayout=105.0,
            db_on=1, r21_on=0, nz_on=0, db_risk0=0.259, db_risk1=0.288, db_mult=1.0, db_hourboost=1.3, db_hourfrom=9.0,
            db_sess0=3.0, db_sess1=12.0, db_tp1r=3.5, db_tp1f=0.0, db_be=0.5, db_tpf0=8.0, db_tpf1=10.0, db_maxhold=192,
            db_maxtrades=1, db_maxloss=2, db_budget=0.8, gesamtbudget=2.0, minlottol=2.0,
            floatstop=0.85, floatgestuft=0, floatminsaldo=0, daystop=2.4, idea_margin=0.0,
            ddfull=0.0, belowstart=1.0, floorguard=1.3, floorguard_mult=0.5,
            harvest=2, harvminr=2.0, harvmargin=0.05, harvfrom=16.0, harvpartial=1, harvminr2=0.0,
            ge_on=0, we_on=0, stopmode=0)


def run(ds, mult):
    if ds == "ext":
        V._MK = E.Market(D=pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb")),
                         S=pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb")))
    else:
        V._MK = None
        V.mk()
    GP = E.gparams([])
    V.set_generic([], GP)
    Pv = E.params(**dict(V300, db_mult=mult))
    if ds == "ext":
        return {"ext": V.evaluate(Pv, GP=GP, horizons=(250, 500), step=9, seeds=(0, 1, 2, 3), warm="2006-09-01", end="2021-12-31")["mean"]}
    sd = tuple(range(8))
    return {"all": V.evaluate(Pv, GP=GP, horizons=(250, 500), step=3, seeds=sd, skip=0.05, end="2025-12-31")["mean"],
            "IS": V.evaluate(Pv, GP=GP, horizons=(250,), step=2, seeds=sd, skip=0.05, warm="2022-03-21", end="2023-12-31")["mean"],
            "OOS": V.evaluate(Pv, GP=GP, horizons=(250,), step=2, seeds=sd, skip=0.05, warm="2024-01-02", end="2025-12-31")["mean"]}


if __name__ == "__main__":
    ds = sys.argv[1] if len(sys.argv) > 1 else "gft"
    fn = f"ergebnisse/z8_v300_{ds}.json"
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    for lbl, mult in (("3.00 Sicher (x1,0)", 1.0), ("3.00 Mittel (x1,2)", 1.2)):
        if lbl not in res:
            res[lbl] = run(ds, mult)
            json.dump(res, open(fn, "w"), default=float, indent=1)
        print(z8.kurz(lbl, res[lbl]) + "  Pleiten B/F/T " + " ".join(
            f"{p}:{m['b_floor']:.2f}/{m['b_float']:.2f}/{m['b_day']:.2f}" for p, m in res[lbl].items()), flush=True)
