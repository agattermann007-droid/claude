"""DEADBAND V9 - Muster und Stressfenster (beschreibend, keine Varianten).

1. Live-Signale der NAS-Long-Fades + S0830 (und Gold-Shorts) je Stressfenster: Zahl, Summe R, und was jede Regel gesperrt haette
2. Verlustserien wie im Oktober 2026: rollierende Summe ueber 11 Live-Trades <= -3,5 R - wie oft, und Ergebnis der naechsten 20
3. Kennzahlen je Modul (Live-Signale) in A und B
"""
import json, os, sys
import numpy as np
import aufbau9 as AU, tests9 as T, regime9 as RG, daten9 as DA

STRESS = {"Feb-Mar 2020": ("2020-02-01", "2020-04-01"), "2022": ("2022-01-01", "2023-01-01"),
          "Aug 2024": ("2024-08-01", "2024-09-01"), "Apr 2025": ("2025-04-01", "2025-05-01")}


def nm(s):
    return int(np.datetime64(s, "m").astype(np.int64))


def main(name="frei"):
    A = AU.baue(name)
    sigs = A["sigs"]
    FL = T.flags(A)
    out = {"stress": {}, "serien": {}, "module": {}}
    # 1) Stressfenster
    for grp, mods, key, dsel in (("NAS-Long", T.NAS_LONG, "dn", 1), ("Gold-Short", T.GOLD_SHORT, "up", -1)):
        for wn, (a, b) in STRESS.items():
            row = {"n": 0, "R": 0.0}
            for s in sigs:
                if s["name"] not in mods:
                    continue
                m = T.live_set(A, s) & np.isfinite(s["R"]) & (s["t_entry"] >= nm(a)) & (s["t_entry"] < nm(b)) & (s["dir"] == dsel)
                row["n"] += int(m.sum()); row["R"] += float(s["R"][m].sum())
                for r in list(RG.REGELN) + ["NA", "TR"]:
                    f = FL[s["name"]][key][r] & m
                    x = row.setdefault(r, [0, 0.0]); x[0] += int(f.sum()); x[1] += float(s["R"][f].sum())
            out["stress"][f"{grp} {wn}"] = row
    # 2) Serien (NAS-Long live, zeitlich sortiert)
    t, R = [], []
    for s in sigs:
        if s["name"] in T.NAS_LONG:
            m = T.live_set(A, s) & np.isfinite(s["R"])
            t.append(s["t_entry"][m]); R.append(s["R"][m])
    t = np.concatenate(t); R = np.concatenate(R); o = np.argsort(t); t = t[o]; R = R[o]
    for w, (a, b) in T.WIN.items():
        m = (t >= nm(a)) & (t < nm(b))
        rr = R[m]; tt = t[m]
        cs = np.r_[0.0, np.cumsum(rr)]
        roll = cs[11:] - cs[:-11]
        hits = np.nonzero(roll <= -3.5)[0]
        # unabhaengige Episoden: Beginn je 11 Trades auseinander
        ep = []
        last = -100
        for h in hits:
            if h >= last + 11:
                ep.append(h); last = h
        fwd = [float(rr[h + 11:h + 31].sum()) for h in ep if h + 31 <= len(rr)]
        out["serien"][w] = dict(trades=int(len(rr)), sumR=float(rr.sum()), episoden=len(ep),
                                daten=[str(np.datetime64(int(tt[h + 10] // 1440), "D")) for h in ep],
                                folge20_mittel=float(np.mean(fwd)) if fwd else None, folge20=fwd,
                                mittel20_alle=float(np.mean([rr[i:i + 20].sum() for i in range(0, len(rr) - 20)])) if len(rr) > 20 else None)
    # 3) Module
    for s in sigs:
        m = T.live_set(A, s) & np.isfinite(s["R"])
        w = T.fenster_von(s["t_entry"])
        for f in ("A", "B"):
            q = m & (w == f)
            r = s["R"][q]
            out["module"][f"{s['name']} {f}"] = dict(n=int(q.sum()), wr=float(np.mean(r > 0)) if len(r) else None,
                                                    sumR=float(r.sum()), pf=float(r[r > 0].sum() / -r[r < 0].sum()) if (r < 0).any() else None,
                                                    ziel_R=float(np.median(np.where(s["goal"][q] > 0, (s["goal"][q] - s["ent"][q]) * s["dir"][q] / s["rd"][q], np.nan))) if q.any() else None)
    json.dump(out, open(os.path.join(DA.SCRATCH, f"muster9_{name}.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    o = main(sys.argv[1] if len(sys.argv) > 1 else "frei")
    for k, v in o["stress"].items():
        regs = " ".join(f"{r}:{v[r][0]}/{v[r][1]:+.1f}" for r in list(RG.REGELN) + ["NA", "TR"] if v[r][0])
        print(f"{k:24s} live {v['n']:3d} Summe {v['R']:+6.1f} R | gesperrt (n/R): {regs}")
    for k, v in o["serien"].items():
        print(f"Serien {k}: {v['trades']} Trades, Summe {v['sumR']:+.1f} R, Episoden <= -3,5 R in 11: {v['episoden']} {v['daten']}, "
              f"naechste 20 Trades im Mittel {v['folge20_mittel']}, alle 20er-Fenster {v['mittel20_alle']}")
    for k, v in o["module"].items():
        if v["n"]:
            print(f"{k:10s} n {v['n']:4d} WR {v['wr']:.2f} PF {v['pf'] if v['pf'] is None else round(v['pf'], 2)} Summe {v['sumR']:+6.1f} R, Ziel-Median {v['ziel_R']:.2f} R")
