"""Stromebene auf dem GFT-Feed: R je Trade je Strom und Jahr (Einzelstrom, Schlupf 1/4 Spread, Stop vor Ziel).
Fades nur mit live Waechter (wie im EA). Zusaetzlich der Live-Zeitraum 28.09.-16.10.2026."""
import xg  # noqa: F401
import numpy as np

if __name__ == "__main__":
    import cfg11 as C, gen11 as G, sim11 as M, cand11 as K
    S = C.signals()
    live_at = G.portfolio_guard(S["fades"])
    bl = []
    for i, b in enumerate(S["fades"]):
        m = b["live"]
        bl.append((C.FADE_NAMES[i], {k: (v[m] if isinstance(v, np.ndarray) and len(v) == len(m) else v) for k, v in b.items()}, 5))
    for key, nm in (("spike", "S0830"), ("lw", "LW"), ("xa", "XA"), ("td", "TD")):
        bl.append((nm, S[key], 5))
    for j, nm in enumerate(C.SR_NAMES):
        bl.append((nm, S["sr"][j], 4))
    bl.append(("SRT1030", K.tick_fade("N1030", live_at=live_at), 4))
    yrs = list(range(2020, 2027))
    print(f"{'Strom':8s} " + " ".join(f"{y:>16d}" for y in yrs) + "   2022-26 gesamt            Live-Zeitraum")
    for nm, b, tpd in bl:
        r = M.simulate(b, tpdelay=tpd)
        R = r["R"]; t = b["t"] + 420                      # Serverzeit-Minuten
        cells = []
        for y in yrs:
            st = M.stats(R, t, f"{y}-01-01", f"{y + 1}-01-01")
            cells.append(f"{st['n']:3d} {st['er']:+.2f} {st['pf']:4.2f}" if st["n"] else " " * 16)
        g = M.stats(R, t, "2022-01-01", "2026-10-17")
        lv = M.stats(R, t, "2026-09-28", "2026-10-17")
        print(f"{nm:8s} " + " ".join(f"{c:>16s}" for c in cells) +
              f"   n {g['n']:4d} E {g['er']:+.3f} PF {g['pf']:4.2f} WR {g['wr']:4.1f}   n {lv['n']:2d} Summe {lv['sum']:+5.2f}", flush=True)
    print("Zellen: Anzahl, R je Trade, PF")
