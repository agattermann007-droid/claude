"""Stufe 8: Jahreswerte und Ueberschneidung ausgewaehlter Stroeme (Signalebene)."""
import numpy as np, gsig as G, scan6 as S, n8sig as N

def trades(sym, gen, args):
    D, ny, days, t_end, atr = S.prep(sym)
    ie, d, rd, tp, ix = gen(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, *args)
    R, *_ = G.simulate(sym, ie, d, rd, tp, ix)
    return ny[ie], R, d

def yearly(t, R):
    y = (t // 1440 // 365.25 + 1970).astype(int)
    out = []
    for yy in np.unique(y):
        r = R[y == yy]; p = r[r > 0].sum(); q = -r[r < 0].sum()
        out.append(f"{yy}: n{len(r):3d} PF{p/q if q else 9.9:4.2f} {r.sum():+6.1f}R")
    return " | ".join(out)

def daily(t, R):
    d = t // 1440
    u, inv = np.unique(d, return_inverse=True); s = np.zeros(len(u)); np.add.at(s, inv, R)
    return dict(zip(u.tolist(), s.tolist()))

CANDS = {
 "A ORB NAS 5min long": ("NAS", N.gen_orb, (570, 575, 635, 960, 0, 0.0, 0.0, 1, 0.0, 99.0, 1)),
 "B PULL NAS long": ("NAS", N.gen_pull, (20, 50, 600, 900, 955, 12, 0.03, 3.0, 1, 1)),
 "C MOM NAS 30min": ("NAS", N.gen_mom, (570, 600, 720, 0.1, 0, 0.25, 0.0, 0)),
 "D PDL NAS break": ("NAS", N.gen_pdl, (570, 900, 955, 0, 0.15, 2.0, 0)),
 "E SB NAS long": ("NAS", N.gen_sb, (-420, 570, 570, 660, 720, 0.08, 1.0, 1, 0.05, 0)),
}
if __name__ == "__main__":
    dd = {}
    for k, (sym, gen, args) in CANDS.items():
        t, R, d = trades(sym, gen, args)
        print(f"{k:<22s} {yearly(t, R)}")
        dd[k] = daily(t, R)
    ks = list(dd)
    print("Korrelation der Tagesergebnisse (gemeinsame Tage):")
    for i in range(len(ks)):
        row = []
        for j in range(len(ks)):
            c = sorted(set(dd[ks[i]]) & set(dd[ks[j]]))
            a = np.array([dd[ks[i]][x] for x in c]); b = np.array([dd[ks[j]][x] for x in c])
            row.append(f"{np.corrcoef(a, b)[0,1]:+.2f}/{len(c):3d}" if len(c) > 5 else "   -   ")
        print(f"{ks[i][:10]:<10s} " + " ".join(row))
