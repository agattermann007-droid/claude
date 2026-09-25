"""RSI21 Eigenkapital - Ausgangslage: RSI21 aus 6.60 (Signale, Stop, Ziel, Einstand, Zeit-Ausstieg, zweiter Platz, 2 Verluste
je Tag) als Eigenkapital-Konto ohne Prop-Regeln. Kennzahlen je Periode und Jahr, Trade-Ebene je Symbol/Zeitebene/Richtung/
Einstiegsstunde. Aufruf: python ek_base.py [risk] -> Ausgabe auf stdout."""
import os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ek_data, ek_sig, ek_sim, ek_eval as V                        # noqa: E402

PER = [("2006-01-01", "2017-01-01", "2006-16"), ("2017-01-01", "2022-01-01", "2017-21"),
       ("2022-01-01", "2026-09-01", "2022-26"), ("2006-01-01", "2026-09-01", "gesamt")]


def show(res, title):
    print(f"--- {title}")
    for a, b, nm in PER:
        m = V.metrics(res, a, b)
        print(f"  {nm:8s} {V.fmt(m)}")


def breakdown(mk, res):
    tr = res["tr"]
    R = V.trades_R(res)
    t_in = tr[:, 16].astype(np.int64)
    yr = (t_in // 1440).astype("datetime64[D]").astype("datetime64[Y]").astype(int) + 1970
    hr = (t_in % 1440) // 60
    print("  Trade-Ebene (R je Trade inkl. Kosten und Swap):")
    for nm, key in (("Symbol", tr[:, 2]), ("Zeitebene", tr[:, 4]), ("Richtung", tr[:, 5]), ("Platz B", tr[:, 3] >= 2),
                    ("Ausstieg", tr[:, 13]), ("Einstand", tr[:, 14])):
        parts = []
        for v in np.unique(key):
            m = key == v
            parts.append(f"{v:g}: n {m.sum()} R {R[m].mean():+.3f} WR {100 * (R[m] > 0).mean():.0f}%")
        print(f"   {nm:9s} " + " | ".join(parts))
    for s in (0, 1):
        parts = []
        for h in range(0, 24):
            m = (tr[:, 2] == s) & (hr == h)
            if m.sum() >= 10:
                parts.append(f"{h}h {m.sum()}/{R[m].mean():+.2f}")
        print(f"   {V.SYMN[s]} je Stunde (n/R): " + "  ".join(parts))
    parts = []
    for y in np.unique(yr):
        m = yr == y
        parts.append(f"{y}: {m.sum()}/{R[m].mean():+.2f}")
    print("   je Jahr (n/R): " + "  ".join(parts))


if __name__ == "__main__":
    risk = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    t0 = time.time()
    D = ek_data.load()
    F = ek_sig.features(D)
    mk = ek_sim.Market(D)
    sg = ek_sig.select(F)
    R = mk.signals(sg)
    print(f"Signale {len(sg['T'])}, Folgesignale {int(sg['folge'].sum())}  [{time.time() - t0:.0f}s]")
    for sm, nm in ((1, "Zinsmodell-Swap"), (0, "GFT-Swap"), (2, "ohne Swap")):
        Pv = ek_sim.params(risk=risk, swap_mode=sm)
        t1 = time.time()
        res = ek_sim.run(mk, R, Pv)
        show(res, f"6.60-RSI21 als Eigenkapital, Risiko {risk} % x Gewicht, {nm}  [{time.time() - t1:.2f}s]")
        if sm == 1:
            breakdown(mk, res)
            print("  Jahre: " + "  ".join(f"{y}: {100 * v['ret']:+.0f}%/{100 * v['maxdd']:.0f}%" for y, v in V.by_year(res).items()))
            print("  Zaehler: " + ", ".join(f"{n} {res['st'][i]:g}" for i, n in enumerate(ek_sim.ST)))
