"""Grid-Studie Teil 2: RSI21-Folgesignale und NAS-Noise (Trendfolge) gegen die Grid-Merkmale. Einzelsimulation je Signal
(ohne Konto): RSI21 Stop 2 ATR, Ziel 2,2 R (NAS) bzw. 2,64 R (Gold), Zeit-Ausstieg nach 1152 M5-Kerzen; Noise erste
Long-Pruefung je Tag, Stop = mittlerer Teil (0,5 Sigma), Ausstieg 15:55 NY. Durchgehende Fremddaten 2006-2025.
Aufruf: python pg_study_old.py [tf L maxpiv] ..."""
import numpy as np, sys, os, pickle
import pg_data as PD, prep5 as P, sig5 as S5, gsig as G
import pg_blocks as PB

PER = [("06-13", 2006, 2014), ("14-21", 2014, 2022), ("22-23", 2022, 2024), ("24-25", 2024, 2026)]
SYMS = ("XAU", "NAS")


def full_all():
    f = os.path.join(P.OUT, "DXallfull.pkl"); fs = os.path.join(P.OUT, "sig5_all.pkl")
    if os.path.exists(f) and os.path.exists(fs):
        return pickle.load(open(f, "rb")), pickle.load(open(fs, "rb"))
    DA = PD.data_all()
    D = {}
    for s, d in DA.items():
        d = dict(d); ny = d["ny"]
        d["pday"] = (ny + 420) // 1440
        for key, mins in (("m15", 15), ("m30", 30), ("h1", 60)):
            d[key] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], mins)
        D[s] = d
    S = dict(r21=S5.r21_signals(D), nz=S5.nz_days(D))
    pickle.dump(D, open(f, "wb")); pickle.dump(S, open(fs, "wb"))
    return D, S


def stat(R):
    n = len(R)
    if n == 0:
        return "   -   "
    w = R[R > 0].sum(); l = -R[R < 0].sum()
    return f"{n:4d} {100 * (R > 0).mean():3.0f}% {R.mean():+.2f} PF{(w / l if l > 0 else 9.9):4.2f}"


def table(title, R, yr, groups):
    print(f"  {title}")
    print("    " + " " * 22 + " | ".join(f"{p[0]:^24s}" for p in PER))
    for lbl, m in groups:
        print(f"    {lbl:22s}" + " | ".join(f"{stat(R[m & (yr >= a) & (yr < b)]):24s}" for _, a, b in PER))


def r21_virtual(D, S):
    r = S["r21"]
    sel = np.nonzero(r["folge"] == 1)[0]
    R = np.full(len(r["T"]), np.nan); te = np.zeros(len(r["T"]), np.int64)
    G._D = PD.data_all()
    for k, sym in enumerate(SYMS):
        m = sel[r["sym"][sel] == k]
        ny = D[sym]["ny"]
        i5 = np.searchsorted(ny, r["T"][m]); ok = i5 < len(ny) - 1
        m = m[ok]; i5 = i5[ok]
        rr = 2.64 if sym == "XAU" else 2.2
        ix = np.minimum(i5 + 1152, len(ny) - 1)
        Rk = G.simulate(sym, i5, r["dir"][m], r["rd"][m], np.full(len(m), rr), ix)[0]
        R[m] = Rk; te[m] = ny[i5]
    return R, te


def nz_virtual(D, S):
    z = S["nz"]; ny = D["NAS"]["ny"]
    cand = np.nonzero((z["close"] > z["UB"]) & (z["entry_ok"] == 1) & (z["dist"][:, 1] > 0))[0]
    first = []; seen = set()
    for q in cand:
        if int(z["day"][q]) in seen:
            continue
        seen.add(int(z["day"][q])); first.append(q)
    first = np.array(first, np.int64)
    G._D = PD.data_all()
    i5 = z["i5"][first]; ix = z["eod_i5"][first]
    ok = ix > i5
    first = first[ok]; i5 = i5[ok]; ix = ix[ok]
    R = G.simulate("NAS", i5, np.ones(len(i5), np.int64), z["dist"][first, 1], np.zeros(len(i5)), ix)[0]
    return first, R, ny[i5]


def run(cfgs):
    D, S = full_all()
    R, te = r21_virtual(D, S)
    ok = np.isfinite(R)
    idx = np.nonzero(ok)[0]
    Rr = R[idx]; tr = te[idx]; yr = PD.year_of(tr)
    zq, Rz, tz = nz_virtual(D, S)
    yz = PD.year_of(tz)
    print(f"RSI21-Folgesignale {len(Rr)}, Noise-Tage {len(Rz)}")
    table("RSI21 alle", Rr, yr, [("alle", np.ones(len(Rr), bool))])
    table("Noise alle", Rz, yz, [("alle", np.ones(len(Rz), bool))])
    r = S["r21"]
    for tf, L, mp in cfgs:
        Xr = np.full((len(Rr), 13), np.nan)
        for k, sym in enumerate(SYMS):
            m = r["sym"][idx] == k
            if m.sum():
                Xr[m] = PB.feats(sym, tr[m], r["dir"][idx][m], np.ones(m.sum()), np.ones(m.sum()), np.ones(m.sum()), np.ones(m.sum()), tf, L, mp)
        Xz = PB.feats("NAS", tz, np.ones(len(tz), np.int64), np.ones(len(tz)), np.ones(len(tz)), np.ones(len(tz)), np.ones(len(tz)), tf, L, mp)
        print(f"\n=== Zeitebene M{tf} Laenge {L} max. Schenkel {mp}")
        for nm, Rx, Xx, yx in (("RSI21", Rr, Xr, yr), ("Noise", Rz, Xz, yz)):
            okx = np.isfinite(Xx[:, 2]); al = Xx[:, 1]; pe = Xx[:, 2]; pb = Xx[:, 3]; be = Xx[:, 4]
            g = [("mit Lauf", okx & (al > 0)), ("gegen Lauf", okx & (al < 0))]
            for a_, nm_ in ((1, "mit"), (-1, "gegen")):
                for lo, hi in ((0, 0.33), (0.33, 0.67), (0.67, 1.01)):
                    g.append((f"{nm_} p_ext {lo:.2f}-{min(hi, 1):.2f}", okx & (al == a_) & (pe >= lo) & (pe < hi)))
                for lo, hi in ((0, 0.1), (0.1, 0.3), (0.3, 1.01)):
                    g.append((f"{nm_} beyond {lo:.1f}-{min(hi, 1):.1f}", okx & (al == a_) & (be >= lo) & (be < hi)))
            table(f"{nm}: Ausrichtung, Reife, beyond", Rx, yx, g)


if __name__ == "__main__":
    a = sys.argv[1:]
    cfgs = [(int(a[i]), int(a[i + 1]), int(a[i + 2])) for i in range(0, len(a), 3)] if a else [(tf, L, 1000) for tf in (5, 15, 60) for L in (10, 20, 40)]
    run(cfgs)
