"""RSI21 Eigenkapital - Randparameter (Plaetze je Symbol, Gold-Faktor, Verluste je Tag) bei GLEICHEM groessten Rueckgang.

Die Koordinatensuche (ek_ca R:TVZ) endete bei 5 Plaetzen und Gold-Faktor 1,3 - beides am Rand des Rasters, und bei gleicher
Volatilitaet stieg die Rendite mit mehr Plaetzen und mehr Gold weiter, waehrend Sharpe und Rueckgang schlechter wurden.
Deshalb hier das strengere Mass: Risiko je Konfiguration so interpoliert, dass der groesste Rueckgang 2006-26 (Mittel ueber
4 Stoerungen) 30 / 40 / 50 % betraegt, und die CAGR bei diesem Risiko; dazu der Kelly-Punkt (hoechste CAGR) 2006-26 und
2006-16. Basis: Endstand R:TVZ mit Einstand aus (auf dem Plateau gleichwertig).
Aufruf: python ek_rand.py -> ergebnisse/ek_rand.txt"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ek_ca as C, ek_opt as O                                      # noqa: E402

if __name__ == "__main__":
    d = json.load(open(os.path.join(HERE, "ergebnisse", "ek_ca_RTVZ.json")))
    sel = dict(d["sel"]); sel["tf_gold"] = tuple(sel["tf_gold"]); sel["tf_nas"] = tuple(sel["tf_nas"])
    sim = dict(d["sim"], be_at=0.0)
    cfg = [("6.60", dict(C.BASE_SEL), {})]
    for n, g, ml in ((5, 1.3, 1), (6, 1.3, 1), (8, 1.3, 1), (10, 1.3, 1), (5, 1.6, 1), (5, 2.0, 1), (8, 1.6, 1),
                     (5, 1.15, 1), (5, 1.0, 1), (5, 0.85, 1), (5, 0.7, 1), (4, 1.0, 1), (3, 1.0, 1), (5, 1.0, 2), (5, 1.0, 0),
                     (5, 0.7, 2), (5, 0.7, 0), (4, 0.7, 1), (6, 0.7, 1)):
        cfg.append((f"{n} Plaetze, Gold {g}, Verluste/Tag {ml}", sel, dict(sim, nslots=n, goldmult=g, maxloss=ml)))
    risks = [0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0]
    V = []
    for nm, s_, m_ in cfg:
        for rk in risks:
            for x in C.seeds_of(dict(m_, risk=rk), 4):
                V.append((nm, s_, x))
    rows = O.evaluate(V, workers=4)
    lines = ["Konfiguration | bei groesstem Rueckgang 2006-26 von 30 / 40 / 50 %: Risiko, CAGR 2006-26 (T / V / Z) | Kelly-Punkt"]
    i = 0
    for nm, _, _ in cfg:
        cur = []
        for rk in risks:
            rr = rows[i:i + 4]; i += 4
            cur.append((rk, float(np.mean([r["G"]["maxdd"] for r in rr])), {p: float(np.mean([r[p]["cagr"] for r in rr])) for p in ("T", "V", "Z", "G")}))
        parts = []
        dds = np.array([c[1] for c in cur])
        for tgt in (0.30, 0.40, 0.50):
            j = int(np.searchsorted(dds, tgt))
            if j == 0 or j >= len(cur):
                parts.append(f"DD{int(tgt * 100)}: -")
                continue
            w = (tgt - dds[j - 1]) / (dds[j] - dds[j - 1])
            rk = cur[j - 1][0] + w * (cur[j][0] - cur[j - 1][0])
            cg = {p: cur[j - 1][2][p] + w * (cur[j][2][p] - cur[j - 1][2][p]) for p in ("T", "V", "Z", "G")}
            parts.append(f"DD{int(tgt * 100)}: {rk:4.2f} % {100 * cg['G']:5.1f} % ({100 * cg['T']:3.0f}/{100 * cg['V']:3.0f}/{100 * cg['Z']:3.0f})")
        kg = max(cur, key=lambda c: c[2]["G"]); kt = max(cur, key=lambda c: c[2]["T"])
        lines.append(f"{nm:34s} " + " | ".join(parts) + f" | Kelly 2006-26 {100 * kg[2]['G']:.0f} % bei {kg[0]} % (DD {100 * kg[1]:.0f} %), "
                     f"2006-16 {100 * kt[2]['T']:.0f} % bei {kt[0]} %")
        print(lines[-1], flush=True)
    with open(os.path.join(HERE, "ergebnisse", "ek_rand.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
