"""RSI21 Eigenkapital - Wahl der Positionsgroesse (robuster Kelly-Punkt) fuer RSI21 EK 1.00 (ek_final.FINAL_SEL/FINAL_SIM).

Je Risiko je Trade (Hebel 1:20, Margin bis 90 %): CAGR und groesster Rueckgang 2006-16 (T, schwaches Regime) und 2006-26 (G),
dieselben Kennzahlen unter Stress (20 % der Gewinner-Signale entfernt, Mittel ueber 4 Masken) und ein Monte Carlo ueber
5 Jahre (Block-Bootstrap 20 Handelstage aus 2006-26, 2000 Pfade): groesster Rueckgang p50/p95, Anteil der Pfade mit
Rueckgang >= 50 %. Gewaehlt wird das Risiko, bei dem die CAGR des schwachen Regimes UNTER STRESS am hoechsten ist
(renditemaximal auch bei schwaecherer Kante; darueber waechst nur der Rueckgang).
Aufruf: python ek_groesse.py -> ergebnisse/ek_groesse.txt"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ek_opt as O, ek_sim, ek_eval as V, ek_final as FN              # noqa: E402

if __name__ == "__main__":
    O._init("D.pkl")
    sel, sim = FN.FINAL_SEL, FN.FINAL_SIM
    R = O.signals(sel)
    mk = O._W["mk"]
    base = ek_sim.run(mk, R, ek_sim.params(**dict(O.BASE_SIM, **dict(sim, risk=1.0))))
    Rv = V.trades_R(base); tr = base["tr"]
    win_sig = tr[Rv > 0, 17].astype(np.int64)
    lines = ["Risiko | T CAGR/DD | G CAGR/DD | Stress -20 % Gewinner: T CAGR/DD, G CAGR/DD | MC 5 J: DD p50/p95, P(DD>=50 %)"]
    best = None
    for rk in (0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0):
        Pv = ek_sim.params(**dict(O.BASE_SIM, **dict(sim, risk=rk)))
        r0 = ek_sim.run(mk, R, Pv)
        mT = V.metrics(r0, *O.PER["T"]); mG = V.metrics(r0, *O.PER["G"])
        sT = []; sG = []
        for sd in range(4):
            rng = np.random.default_rng(100 + sd)
            skip = np.zeros(len(R["ev"]), np.bool_)
            skip[win_sig[rng.random(len(win_sig)) < 0.2]] = True
            rs = ek_sim.run(mk, R, Pv, skip=skip)
            sT.append(V.metrics(rs, *O.PER["T"])); sG.append(V.metrics(rs, *O.PER["G"]))
        lr = np.diff(np.log(r0["day"][:, 1]))
        rng = np.random.default_rng(7); mdd = []
        for _ in range(2000):
            idx = []
            while len(idx) < 1260:
                s0 = rng.integers(0, len(lr) - 20); idx.extend(range(s0, s0 + 20))
            path = np.exp(np.cumsum(lr[np.array(idx[:1260])]))
            pk = np.maximum.accumulate(np.r_[1.0, path])
            mdd.append(np.max(1 - np.r_[1.0, path] / pk))
        mdd = np.array(mdd)
        stT = float(np.mean([m["cagr"] for m in sT]))
        if best is None or stT > best[1]:
            best = (rk, stT)
        lines.append(f"{rk:5.2f} % | T {100 * mT['cagr']:5.1f}%/{100 * mT['maxdd']:3.0f}% | G {100 * mG['cagr']:5.1f}%/{100 * mG['maxdd']:3.0f}% | "
                     f"T {100 * stT:5.1f}%/{100 * np.mean([m['maxdd'] for m in sT]):3.0f}%, "
                     f"G {100 * np.mean([m['cagr'] for m in sG]):5.1f}%/{100 * np.mean([m['maxdd'] for m in sG]):3.0f}% | "
                     f"{100 * np.percentile(mdd, 50):3.0f}/{100 * np.percentile(mdd, 95):3.0f}%, {100 * np.mean(mdd >= 0.5):4.1f}%")
        print(lines[-1], flush=True)
    lines.append(f"robuster Kelly-Punkt (hoechste CAGR 2006-16 unter Stress): {best[0]} % Risiko je Trade")
    print(lines[-1])
    os.makedirs(os.path.join(HERE, "ergebnisse"), exist_ok=True)
    with open(os.path.join(HERE, "ergebnisse", "ek_groesse.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
