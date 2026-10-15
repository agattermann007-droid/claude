"""Fades im Tick: Einstieg beim Ruecklauf in die Range (M1, wie SR) statt am Open nach dem M5-Schluss."""
import numpy as np
import gen11 as G, pa11 as PA, sim11 as M
fades = G.list_fades()
def fmt(res):
    return " | ".join(f"{p}: n{v['n']:4d} WR{v['wr']:3.0f}% E{v['er']:+.3f} S{v['sum']:+6.1f}" for p, v in res.items())
tot = {}
for (nm, s, r0, L, tlen, xoff, buf, tgt, dirs, mx), fb in zip(G.FADE_STANDARD, fades):
    r1, te, xm = G.fade_times(r0, L, tlen, xoff)
    r = M.simulate(fb, tpdelay=5); ok = r["why"] >= 0
    base = {lab: M.stats(r["R"][ok], fb["t"][ok], lo, hi) for lo, hi, lab in PA.PER}
    print(f"{nm:6s} M5     {fmt(base)}")
    tot.setdefault("M5", []).append(base)
    for md in (0.3, 0.6, 99.0):
        for dr in ([dirs] if dirs != 0 else [1, -1]):
            b = PA.sweep(s, r0, r1, 0, r1, te, xm, 0.0, md, 0.0, 1, buf, 1 if tgt == 0 else 2, 0.0, mx, dr, minsp=6.0, minatr=0.0)
            res, _ = PA.evalb(b, tpdelay=4)
            print(f"{nm:6s} Tick md{md:4.1f} {fmt(res)}")
            tot.setdefault(f"T{md}", []).append(res)
print("== Summe alle 10 Fades ==")
for k, lst in tot.items():
    print(k, " | ".join(f"{p}: n{sum(x[p]['n'] for x in lst):5d} S{sum(x[p]['sum'] for x in lst):+7.1f}R" for p in ("16-21", "22-23", "24-26")))
