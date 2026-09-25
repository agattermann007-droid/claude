"""RSI21 Eigenkapital - Sensitivitaet: jeder Parameter einzeln um die 6.60-Voreinstellung (Risiko 1 %, Hebel 1:20),
Kennzahlen je Periode T (2006-16), V (2017-21), Z (2022-26). Aufruf: python ek_ofat.py -> ergebnisse/ek_ofat.json"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ek_opt as O                                                  # noqa: E402

SEL = {  # Signal-Parameter (ek_sig.select)
    "oben": [70.0, 72.5, 77.5, 80.0],
    "cross": [50.0, 60.0, 65.0],
    "cross_on": [False],
    "folge_min": [0, 60, 120, 480, 1440],
    "ab": [0.0, 3.0, 8.0, 10.0],
    "nas_bis": [11.0, 12.0, 14.0, 15.0, 16.0, 17.0, 24.0],
    "gold_bis": [13.0, 15.0, 24.0],
    "gold_ohne_h1": [False],
    "tf_gold": [(0,), (1,), (0, 1)],
    "tf_nas": [(0,), (1,), (2,), (0, 1)],
    "use_div": [False],
    "short_regime": [False],
    "nas_long_regime": [False],
    "gold_gate": [False],
    "longs": [False],
    "shorts": [False],
    "stop_atr": [1.5, 2.5, 3.0, 4.0],
}
SIM = {  # Konto-Parameter (ek_sim.params)
    "rr_nas": [1.5, 3.0, 4.0, 0.0],
    "rr_gold": [1.8, 3.5, 5.0, 0.0],
    "be_at": [0.0, 0.5, 1.5, 2.0],
    "be_plus": [0.25, 0.5],
    "exitbars": [288, 576, 2304, 0],
    "exitdays": [0.0],
    "maxloss": [0, 1, 3],
    "nslots": [1, 3],
    "first_mult": [0.5, 1.0],
    "goldmult": [0.5, 1.0],
    "we_close": [16.75],
}
PAIRS = {  # gekoppelte Konto-Parameter
    "trail 1.0/0.75": dict(trail_from=1.0, trail_dist=0.75),
    "trail 1.5/1.0": dict(trail_from=1.5, trail_dist=1.0),
    "trail 2.0/1.0": dict(trail_from=2.0, trail_dist=1.0),
    "trail 2.0/1.5": dict(trail_from=2.0, trail_dist=1.5),
    "trail 3.0/1.5 ohne Ziel": dict(trail_from=3.0, trail_dist=1.5, rr_nas=0.0, rr_gold=0.0),
    "tp1 1.0/50%": dict(tp1r=1.0, tp1f=0.5),
    "tp1 1.5/50%": dict(tp1r=1.5, tp1f=0.5),
    "w 1/1/1": dict(w0=1.0, w1=1.0, w2=1.0),
    "w 1.5/1/0.5": dict(w0=1.5, w1=1.0, w2=0.5),
    "w 1/1.25/1.5": dict(w0=1.0, w1=1.25, w2=1.5),
    "budget 2 %": dict(budget=2.0),
}

if __name__ == "__main__":
    V = [("6.60 (Basis)", {}, {})]
    for k, vals in SEL.items():
        for v in vals:
            V.append((f"sel {k}={v}", {k: v}, {}))
    for k, vals in SIM.items():
        for v in vals:
            V.append((f"sim {k}={v}", {}, {k: v}))
    for nm, kw in PAIRS.items():
        V.append((f"sim {nm}", {}, dict(kw)))
    for fl in (14, 28):
        V.append((f"feat rsi_len={fl}", {}, {}, {"rsi_len": fl}))
    rows = O.evaluate(V, workers=4)
    O.save(rows, "ek_ofat.json")
    for r in rows:
        print(O.line(r))
