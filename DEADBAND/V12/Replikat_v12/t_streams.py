"""Abgleich der Einzelstroeme gegen die Bericht-Kennzahlen (Spike, LW, XA, TD, SR, Fades)."""
import numpy as np, time
import gen11 as G, sim11 as M
PER = [("2016-09-01", "2022-01-01", "2016-21"), ("2022-01-01", "2024-01-01", "2022-23"), ("2024-01-01", "2026-03-01", "2024-26"),
       ("2022-01-01", "2026-01-01", "2022-25")]
t0 = time.time()
bl = [G.spike(), G.lw(), G.xa(), G.td()] + G.sr()
for b in bl:
    tpd = 4 if b["name"].startswith("SR") else 5
    r = M.simulate(b, tpdelay=tpd)
    ok = r["why"] >= 0
    for lo, hi, lab in PER:
        print(f"{b['name']:6s} {lab}: {M.fmt(M.stats(r['R'][ok], b['t'][ok], lo, hi))}")
fades = G.list_fades()
live_at = G.portfolio_guard(fades)
allR = []; allT = []; allL = []
for b in fades:
    r = M.simulate(b, tpdelay=5)
    ok = r["why"] >= 0
    for lo, hi, lab in PER[:3]:
        print(f"{b['name']:6s} {lab}: {M.fmt(M.stats(r['R'][ok], b['t'][ok], lo, hi))}  live {b['live'][ok & (b['t'] >= np.datetime64(lo,'m').astype(np.int64)) & (b['t'] < np.datetime64(hi,'m').astype(np.int64))].mean():.2f}")
    allR.append(r["R"][ok]); allT.append(b["t"][ok]); allL.append(b["live"][ok])
R = np.concatenate(allR); T = np.concatenate(allT); L = np.concatenate(allL)
for lo, hi, lab in PER:
    print(f"FADES alle {lab}: {M.fmt(M.stats(R, T, lo, hi))} | nur live: {M.fmt(M.stats(R[L], T[L], lo, hi))}")
print(f"{time.time()-t0:.0f}s")
