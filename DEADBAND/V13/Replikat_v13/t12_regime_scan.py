"""v12 / Prompt 9.3: Kandidaten fuer das Regime "Fades aus" auf Stromebene.

Zeitraeume: 2011-16 (erweiterter Satz, Gold = OANDA), 2016-21, 2022-23, 2024-26. Je Kandidat alle Signale und nur die
Signale bei NICHT live Portfolio-Waechter (gate). Auswahlregel (vor dem Lauf festgelegt): gegated E >= +0,05 R und
PF >= 1,10 in 2016-21 (Auswahl, n >= 40) UND gegated E > 0 in 2011-16 (unabhaengige Pruefung, n >= 20).
Ausgabe: ergebnisse/t12_regime_scan.log / .pkl
"""
import x12  # noqa: F401  (erweiterter Datensatz)
import itertools, pickle, time, numpy as np
import cfg11 as C, gen11 as G, sim11 as M, reg12 as R

PER = [("2011-01-01", "2016-09-01", "11-16"), ("2016-09-01", "2022-01-01", "16-21"),
       ("2022-01-01", "2024-01-01", "22-23"), ("2024-01-01", "2026-03-01", "24-26")]
S = C.signals()
live_at = G.portfolio_guard(S["fades"])

# Waechter-Zustand je Halbjahr (Anteil der Handelstage 12:00 NY, an denen die Fades live waeren)
days = np.arange(np.datetime64("2011-01-03", "D").astype(np.int64), np.datetime64("2026-02-01", "D").astype(np.int64))
days = days[(days + 4) % 7 < 5]
lv = np.array([live_at(int(d) * 1440 + 720)[0] for d in days])
yr = (days.astype("datetime64[D]").astype("datetime64[Y]").astype(int) + 1970)
print("Waechter live (Anteil Tage):", {int(y): round(float(lv[yr == y].mean()), 2) for y in np.unique(yr)}, flush=True)


def ev(b, tpd=5):
    r = M.simulate(b, tpdelay=tpd)
    ok = r["why"] >= 0
    gl = np.array([not live_at(int(t))[0] for t in b["t"]], bool)
    out = {}
    for lo, hi, lab in PER:
        out[lab] = M.stats(r["R"][ok], b["t"][ok], lo, hi)
        out["g" + lab] = M.stats(r["R"][ok & gl], b["t"][ok & gl], lo, hi)
    return out


CANDS = []
for n, dirs, (sm, s), crv in itertools.product((5, 15, 30), (0, 1), ((0, 0.10), (0, 0.20), (1, 0.0)), (0.0, 2.0, 5.0)):
    CANDS.append((f"ORB n{n} d{dirs} sm{sm} s{s} crv{crv}", lambda n=n, dirs=dirs, sm=sm, s=s, crv=crv: R.orb(n, dirs, sm, s, crv)))
for (ts, ti, x), s, minr, dirs in itertools.product(((600, 930, 955), (600, 600, 955), (630, 630, 955), (840, 840, 955)),
                                                    (0.2, 0.4), (0.0, 0.3), (0, 1)):
    CANDS.append((f"IMOM sig{ts} in{ti} x{x} s{s} minr{minr} d{dirs}",
                  lambda ts=ts, ti=ti, x=x, s=s, minr=minr, dirs=dirs: R.imom(ts, ti, x, s, minr, dirs)))
for nm in [f[0] for f in G.FADE_STANDARD]:
    for sm, crv, dirs in itertools.product((0, 1), (1.0, 2.0), (0, 1)):
        CANDS.append((f"BRK {nm} sm{sm} crv{crv} d{dirs}", lambda nm=nm, sm=sm, crv=crv, dirs=dirs: R.brk_fade(nm, smode=sm, crv=crv, dirs=dirs)))
for (r0, L, tl, xo), sm, crv, n in itertools.product(((-360, 480, 300, 60), (-360, 480, 540, 0), (120, 240, 240, 120), (480, 90, 240, 120)),
                                                      (0, 1), (1.0, 2.0), (20, 50)):
    CANDS.append((f"GBRK r{r0} L{L} t{tl} sm{sm} crv{crv} n{n}", lambda r0=r0, L=L, tl=tl, xo=xo, sm=sm, crv=crv, n=n:
                  R.gbrk(r0, L, tl, xo, smode=sm, crv=crv, n=n)))

import cand11 as K
for nm in [f[0] for f in G.FADE_STANDARD]:
    CANDS.append((f"TICK {nm}", lambda nm=nm: K.tick_fade(nm, md=0.6)))

rows = []
t0 = time.time()
for lab, f in CANDS:
    b = f()
    if len(b["t"]) < 30:
        continue
    o = ev(b, 4 if lab.startswith("TICK") else 5)
    rows.append(dict(name=lab, **{f"{k}_{q}": v[q] for k, v in o.items() for q in ("n", "er", "pf", "sum", "wr")}))
    g = o["g16-21"]; g0 = o["g11-16"]
    sel = g["n"] >= 40 and g["er"] >= 0.05 and g["pf"] >= 1.10 and g0["n"] >= 20 and g0["er"] > 0
    print(f"{'*' if sel else ' '} {lab:42s} " + " | ".join(
        f"{p} n{o[p]['n']:4d} E{o[p]['er']:+.3f} PF{o[p]['pf']:4.2f}" for p in ("11-16", "16-21", "22-23", "24-26")) +
        "  || gated " + " | ".join(f"{p} n{o['g'+p]['n']:4d} E{o['g'+p]['er']:+.3f}" for p in ("11-16", "16-21", "22-23", "24-26")),
        flush=True)
print(f"{len(rows)} Varianten, {time.time()-t0:.0f}s")
pickle.dump(rows, open("ergebnisse/t12_regime_scan.pkl", "wb"))
