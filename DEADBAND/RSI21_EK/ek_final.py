"""RSI21 Eigenkapital - Endbewertung.

Konfigurationen: 6.60 (RSI21 wie im DEADBAND-EA, nur ohne Prop-Regeln), WF = Endstand der Suche mit Auswahl 2006-21
(ergebnisse/ek_ca_RTV.json, 2022-26 ungesehen), END = Endstand der Suche ueber alle Perioden (ek_ca_RTVZ.json).
  A  Vergleich bei gleicher Schwankung: Risiko r* so, dass die Tagesrenditen 2006-26 25 % Jahresvolatilitaet haben
     (Hebel 1:20, Margin bis 90 %), 16 Stoerungen (Seed 0 ungestoert, sonst 3 % Signale ausgelassen, Schlupf bis 0,3 Spreads)
  B  Risiko-Tabelle END: Risiko je Trade x Hebel (1:20 / 1:30 / 1:100): CAGR und groesster Rueckgang je Periode
  C  END je Kalenderjahr beim gewaehlten Risiko
  D  Stress beim gewaehlten Risiko: 20 % der Gewinner-Signale entfernt, Kosten (Schlupf bis 1 Spread), Swap x2,
     RSI des anderen Symbols wie im EA (cross_ea), ohne Datenloch-Schluss nicht moeglich (Replikat-Konvention)
  E  Monte Carlo: Block-Bootstrap (20 Handelstage) der Tagesrenditen 2006-26 -> CAGR und groesster Rueckgang in 5 Jahren
Aufruf: python ek_final.py RISIKO  -> ergebnisse/ek_final.json, Ausgabe auf stdout"""
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ek_opt as O, ek_ca as C, ek_data, ek_sig, ek_sim, ek_eval as V      # noqa: E402

PERS = ("T", "V", "Z", "G")


def load_cfg(fn):
    d = json.load(open(os.path.join(HERE, "ergebnisse", fn)))
    sel = dict(d["sel"])
    for k in ("tf_gold", "tf_nas"):
        if k in sel:
            sel[k] = tuple(sel[k])
    return sel, dict(d["sim"])


def agg(rows):
    out = {}
    for p in PERS:
        out[p] = {k: (float(np.mean([r[p][k] for r in rows])), float(np.std([r[p][k] for r in rows])))
                  for k in ("cagr", "maxdd", "sharpe", "vol", "tr_y", "avgR", "pf", "wr")}
    return out


def line_agg(nm, a, rk):
    s = f"{nm:22s} r* {rk:4.2f} %"
    for p in PERS:
        c = a[p]
        s += f" | {p} {100 * c['cagr'][0]:6.1f}±{100 * c['cagr'][1]:4.1f}% SR{c['sharpe'][0]:4.2f} DD{100 * c['maxdd'][0]:3.0f}% n{c['tr_y'][0]:4.0f} R{c['avgR'][0]:+.2f}"
    return s


if __name__ == "__main__":
    risk = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    t0 = time.time()
    cfgs = {"6.60": (dict(C.BASE_SEL), {})}
    for nm, fn in (("WF (Auswahl 2006-21)", "ek_ca_RTV.json"), ("END", "ek_ca_RTVZ.json")):
        if os.path.exists(os.path.join(HERE, "ergebnisse", fn)):
            cfgs[nm] = load_cfg(fn)
    out = dict(risk=risk, cfg={k: dict(sel=v[0], sim=v[1]) for k, v in cfgs.items()})
    # ---- A: gleiche Schwankung, 16 Stoerungen
    print("A  Vergleich bei 25 % Jahresvolatilitaet 2006-26 (16 Stoerungen, Mittel ± SD)")
    out["A"] = {}
    for nm, (sel, sim) in cfgs.items():
        rows, rk = C.run_many([(nm, sel, sim)], 16, "G")[0]
        a = agg(rows)
        out["A"][nm] = dict(r=rk, m=a)
        print("  " + line_agg(nm, a, rk), flush=True)
    sel, sim = cfgs["END"] if "END" in cfgs else cfgs["6.60"]
    # ---- B: Risiko-Tabelle
    print("B  Risiko-Tabelle END (Seed 0): CAGR / groesster Rueckgang je Periode")
    risks = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
    V_ = []
    for lev in (20.0, 30.0, 100.0):
        for rk in risks:
            V_.append((f"lev{lev:g} r{rk}", sel, dict(sim, risk=rk, lev_gold=lev, lev_nas=lev)))
    rows = O.evaluate(V_, workers=4)
    out["B"] = []
    for r in rows:
        out["B"].append(dict(name=r["name"], m={p: r[p] for p in PERS}, st=r["st"]))
        print(f"  {r['name']:14s} " + " | ".join(f"{p} {100 * r[p]['cagr']:6.1f}%/{100 * r[p]['maxdd']:3.0f}%" for p in PERS)
              + f" | Margin gekuerzt {r['st'][5]:.0f}, ausgelassen {r['st'][6]:.0f}", flush=True)
    # ---- C/D/E: gewaehltes Risiko
    O._init("D.pkl")
    R = O.signals(sel)
    Pv = ek_sim.params(**dict(O.BASE_SIM, **dict(sim, risk=risk)))
    res = ek_sim.run(O._W["mk"], R, Pv)
    yrs = V.by_year(res)
    print(f"C  END je Jahr bei {risk} % Risiko (Rendite / groesster Rueckgang im Jahr)")
    print("  " + "  ".join(f"{y}: {100 * v['ret']:+.0f}%/{100 * v['maxdd']:.0f}%" for y, v in yrs.items()))
    out["C"] = yrs
    out["C_trades"] = V.metrics(res)
    # D Stress
    print(f"D  Stress bei {risk} % Risiko (Seed 0)")
    out["D"] = {}
    tr = res["tr"]
    Rv = V.trades_R(res)
    win_sig = tr[Rv > 0, 17].astype(np.int64)
    rng = np.random.default_rng(20)
    skip = np.zeros(len(R["ev"]), np.bool_)
    skip[win_sig[rng.random(len(win_sig)) < 0.2]] = True
    variants = {
        "Basis": (R, Pv, None),
        "20 % der Gewinner entfernt": (R, Pv, skip),
        "Schlupf bis 1 Spread": (R, ek_sim.params(**dict(O.BASE_SIM, **dict(sim, risk=risk, slip=1.0))), None),
        "Swap x2": (R, ek_sim.params(**dict(O.BASE_SIM, **dict(sim, risk=risk, swap_mult=2.0))), None),
        "ohne Swap": (R, ek_sim.params(**dict(O.BASE_SIM, **dict(sim, risk=risk, swap_mode=2))), None),
    }
    Fea = ek_sig.features(O._W["mk"].D, cross_ea=True)
    Rea = O._W["mk"].signals(ek_sig.select(Fea, **sel))
    variants["RSI anderes Symbol wie EA"] = (Rea, Pv, None)
    for nm, (RR, PP, sk) in variants.items():
        rr = ek_sim.run(O._W["mk"], RR, PP, seed=1 if nm.startswith("Schlupf") else 0, skip=sk)
        mm = {p: V.metrics(rr, *O.PER[p]) for p in PERS}
        out["D"][nm] = mm
        print(f"  {nm:28s} " + " | ".join(f"{p} {100 * mm[p]['cagr']:6.1f}%/{100 * mm[p]['maxdd']:3.0f}%" for p in PERS), flush=True)
    # E Monte Carlo
    day = res["day"]
    eq = day[:, 1]
    lr = np.diff(np.log(eq))
    n5 = 5 * 252
    B = 20
    rng = np.random.default_rng(7)
    cag = []; mdd = []
    for _ in range(4000):
        idx = []
        while len(idx) < n5:
            s0 = rng.integers(0, len(lr) - B)
            idx.extend(range(s0, s0 + B))
        x = lr[np.array(idx[:n5])]
        path = np.exp(np.cumsum(x))
        pk = np.maximum.accumulate(np.r_[1.0, path])
        mdd.append(float(np.max(1.0 - np.r_[1.0, path] / pk)))
        cag.append(float(path[-1] ** (1.0 / 5.0) - 1.0))
    q = [5, 25, 50, 75, 95]
    out["E"] = dict(cagr={str(k): float(np.percentile(cag, k)) for k in q}, maxdd={str(k): float(np.percentile(mdd, k)) for k in q},
                    p_dd50=float(np.mean(np.array(mdd) >= 0.5)), p_dd30=float(np.mean(np.array(mdd) >= 0.3)),
                    p_loss=float(np.mean(np.array(cag) < 0.0)))
    print(f"E  Monte Carlo 5 Jahre (Block-Bootstrap 2006-26), {risk} % Risiko: CAGR p5/p50/p95 "
          f"{100 * np.percentile(cag, 5):.0f} / {100 * np.percentile(cag, 50):.0f} / {100 * np.percentile(cag, 95):.0f} %, "
          f"groesster Rueckgang p50/p95 {100 * np.percentile(mdd, 50):.0f} / {100 * np.percentile(mdd, 95):.0f} %, "
          f"P(Rueckgang >= 30 %) {100 * out['E']['p_dd30']:.0f} %, >= 50 % {100 * out['E']['p_dd50']:.0f} %, "
          f"P(Verlust nach 5 J) {100 * out['E']['p_loss']:.1f} %")
    with open(os.path.join(HERE, "ergebnisse", "ek_final.json"), "w") as f:
        json.dump(dict(out, sel=sel, sim=dict(sim, risk=risk), fkw={}), f, indent=1, default=str)
    print(f"fertig [{time.time() - t0:.0f}s]")
