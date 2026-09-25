"""Basis RSI21 (EA 6.10) auf 2006-2025: Aufschluesselung nach Symbol, Zeitebene, Richtung, Ausstieg, Uhrzeit, Jahr."""
import numpy as np
import r7data, r7sig as G, r7sim as M

D = r7data.data()
C = G.features(D)
p = dict(G.BASE)
E = G.entries(C, p)
trs = {s: M.simulate(D[s], s, E[s]) for s in G.SYMS}
A = M.merge(list(trs.values()))
print(M.line("Basis beide (R x Gewicht)", M.metrics(A)))
print(M.line("Basis beide (R ungewichtet)", M.metrics(A, weighted=False)))
for si, s in enumerate(G.SYMS):
    for ti, tf in enumerate(("M15", "M30", "H1")):
        for dd in (1, -1):
            m = (A["sym"] == si) & (A["tf"] == ti) & (A["dir"] == dd)
            if m.sum():
                print(M.line(f"  {s} {tf} {'long' if dd > 0 else 'short'}", M.metrics(M.sub(A, m), weighted=False)))
    m = A["sym"] == si
    print(M.line(f"  {s} Platz B", M.metrics(M.sub(A, m & (A["slot"] == 1)), weighted=False)))
why = {0: "Zeit", 1: "Stop", 2: "Ziel", 3: "WE-Schluss", 5: "Datenende"}
for w, nm in why.items():
    m = A["why"] == w
    if m.sum():
        print(f"  Ausstieg {nm:<10s} {m.sum():5d} ({100*m.mean():4.1f} %)  ØR {A['R'][m].mean():+.3f}  ØMFE {A['mfe'][m].mean():.2f}")
print("  Teile > 1 (Wochenende wieder aufgenommen):", int((A["parts"] > 1).sum()))
# MFE-Verteilung
for x in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
    print(f"  MFE >= {x:.1f} R: {100*(A['mfe'] >= x).mean():5.1f} %")
# Uhrzeit des Signals (NY)
h = (A["t"] % 1440) // 60
for hh in np.unique(h):
    m = h == hh
    print(f"  {int(hh):02d}h n{m.sum():5d} ØR {A['R'][m].mean():+.3f} WR {100*(A['R'][m]>0).mean():4.1f}")
held = A["ix"] - A["ie"]
print("  Haltedauer M5-Kerzen: Median", np.median(held), "Mittel", held.mean().round(1))
