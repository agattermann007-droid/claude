"""Build 6.60, Kandidat K6: Noise-Area-Momentum auch SHORT (Originalstrategie Zarattini/Aziz/Barbon 2024 ist zweiseitig;
die Short-Seite verdient laut Studie vor allem an Abverkaufstagen - genau dort verlieren die Long-Fades auf NAS100).
Signal-Ebene, unabhaengig vom Konto: je Handelstag Pruefungen zur vollen Stunde 10:00-15:00 NY wie sig5.nz_days;
Long ueber UB = max(Eroeffnung, Vortagesschluss) x (1 + k sigma), Short unter LB = min(Eroeffnung, Vortagesschluss) x (1 - k sigma);
Ausstieg an der naechsten Pruefung, wenn der Kurs wieder im Band ist, an einem der drei Stops (0,35/0,5/0,75 Tages-Sigma x
Zeitfaktor) oder um 15:55. Ergebnis in R der Signal-Risikoeinheit (drei gleich grosse Teile), Kosten: Spread.
Ausgabe je Jahr 2006-2025 fuer Long und Short, dazu die Korrelation der Tagesergebnisse mit den NAS-Fades (virtuell).
Aufruf: python a60_nzs.py [ausgabe.txt]"""
import numpy as np, sys, os, pickle
from numba import njit
import prep5 as P, sig5 as S5, gext, gsig as G, streams as ST
import a60_sig as A

OUT = []


def say(s=""):
    print(s, flush=True); OUT.append(s)


def nz_days2(d, ntage=14, k=1.0, checks=(600, 660, 720, 780, 840, 900), last_entry=930, schluss=955, first_check=600,
             stops=(0.35, 0.5, 0.75), zeitpow=0.5):
    """wie sig5.nz_days (ohne Vola-Gewicht), zusaetzlich LB; Rueckgabe je Pruefung: Tag, Minute, i5, Schluss, UB, LB, Stops."""
    ny = d["ny"]; o = d["o"]; c = d["c"]
    nyday = ny // 1440; nymin = (ny % 1440).astype(np.int64)
    days = np.unique(nyday)
    stats = {}
    for dd in days:
        idx = np.nonzero(nyday == dd)[0]
        mm = nymin[idx]
        sel = idx[(mm >= 570) & (mm < 960)]
        if len(sel) == 0:
            stats[int(dd)] = None; continue
        m0 = nymin[sel[0]]
        cl = np.full(78, -1.0)
        for q in sel:
            cl[(nymin[q] - 570) // 5] = c[q]
        stats[int(dd)] = dict(open=o[sel[0]] if m0 <= 575 else -1.0, cnt=len(sel), close=c[sel[-1]], lastm=int(nymin[sel[-1]]) + 4,
                              cl=cl, idx=sel)
    out = []
    for dd in days:
        dd = int(dd)
        if (dd + 4) % 7 in (0, 6) or dd in S5.FREI_DAYS:
            continue
        st = stats.get(dd)
        if st is None or st["open"] <= 0:
            continue
        hist = [x for x in range(dd - 60, dd) if stats.get(x) is not None]
        erw = dd - 1
        for g in range(10):
            if (erw + 4) % 7 not in (0, 6) and erw not in S5.FREI_DAYS:
                break
            erw -= 1
        se = stats.get(erw)
        if se is None or se["lastm"] < 950:
            continue
        vi = [x for x in hist if ((x + 4) % 7) not in (0, 6) and stats[x]["cnt"] >= 60]
        if len(vi) < ntage + 1:
            continue
        pc = stats[vi[-1]]["close"]
        rs = [np.log(stats[vi[j]]["close"] / stats[vi[j - 1]]["close"]) for j in range(len(vi) - ntage, len(vi))
              if stats[vi[j]]["close"] > 0 and stats[vi[j - 1]]["close"] > 0]
        if len(rs) < ntage // 2:
            continue
        sd = float(np.std(rs))
        last14 = vi[len(vi) - ntage:]
        sig = np.full(78, -1.0)
        for b in range(78):
            vals = [abs(stats[x]["cl"][b] / stats[x]["open"] - 1.0) for x in last14 if stats[x]["cl"][b] > 0 and stats[x]["open"] > 0]
            if len(vals) >= ntage // 2:
                sig[b] = float(np.mean(vals))
        O = st["open"]
        refU = max(O, pc); refL = min(O, pc)
        span = float(schluss - first_check)
        sel = st["idx"]; mins = nymin[sel]
        jj = np.searchsorted(mins, schluss)
        eod = int(sel[jj]) if jj < len(sel) else int(sel[-1])
        for em in checks:
            b = (em - 570) // 5 - 1
            if b < 0 or b >= 78 or sig[b] < 0:
                continue
            close = st["cl"][b]
            if close <= 0:
                continue
            jj = np.searchsorted(mins, em)
            if jj >= len(sel):
                continue
            i5 = int(sel[jj])
            tfak = max(0.1, (schluss - em) / span) ** zeitpow if zeitpow > 0 else 1.0
            out.append((dd, em, i5, close, refU * (1.0 + k * sig[b]), refL * (1.0 - k * sig[b]), eod, em <= last_entry,
                        *[s_ * O * sd * tfak for s_ in stops]))
    return np.array(out, dtype=np.float64)


@njit(cache=True)
def sim_side(A, o, h, l, sp, side):
    """A: Pruefungen (sortiert nach Tag, Minute). side +1 Long, -1 Short. Rueckgabe: je Signal (Tag, R, i5)."""
    n = A.shape[0]
    res = np.zeros((n, 3)); m = 0
    q = 0
    while q < n:
        dd = A[q, 0]
        # alle Pruefungen dieses Tages
        e = q
        while e < n and A[e, 0] == dd:
            e += 1
        k = q
        while k < e:
            close = A[k, 3]; UB = A[k, 4]; LB = A[k, 5]; ok = A[k, 7] > 0.5
            cond = (close > UB) if side > 0 else (close < LB)
            if not (ok and cond):
                k += 1
                continue
            i5 = int(A[k, 2]); eod = int(A[k, 6])
            ent = o[i5] + (sp[i5] if side > 0 else 0.0)
            d1 = A[k, 8]; d2 = A[k, 9]; d3 = A[k, 10]
            dists = np.array([d1, d2, d3])
            alive = np.array([True, True, True])
            acc = 0.0
            # naechste Pruefungen
            nxt = k + 1
            j = i5
            done = False
            while not done:
                # Ausstieg an einer Pruefung: Kerze der Pruefung erreicht
                if nxt < e and j == int(A[nxt, 2]):
                    c2 = A[nxt, 3]
                    out_ = (c2 < A[nxt, 4]) if side > 0 else (c2 > A[nxt, 5])
                    if out_:
                        px = o[j] + (sp[j] if side < 0 else 0.0)
                        for t in range(3):
                            if alive[t]:
                                acc += (px - ent) * side / dists[t]
                                alive[t] = False
                        done = True
                        break
                    nxt += 1
                if j >= eod:
                    px = o[j] + (sp[j] if side < 0 else 0.0)
                    for t in range(3):
                        if alive[t]:
                            acc += (px - ent) * side / dists[t]
                            alive[t] = False
                    done = True
                    break
                # Stops in der Kerze j
                for t in range(3):
                    if not alive[t]:
                        continue
                    stp = ent - side * dists[t]
                    if side > 0 and l[j] <= stp:
                        acc += -1.0 if o[j] > stp else (o[j] - ent) / dists[t]
                        alive[t] = False
                    elif side < 0 and h[j] + sp[j] >= stp:
                        acc += -1.0 if o[j] + sp[j] < stp else (ent - (o[j] + sp[j])) / dists[t]
                        alive[t] = False
                if not (alive[0] or alive[1] or alive[2]):
                    done = True
                    break
                j += 1
                if j >= o.shape[0]:
                    break
            res[m, 0] = dd; res[m, 1] = acc / 3.0; res[m, 2] = i5; m += 1
            # naechster Einstieg erst ab der Pruefung nach dem Ausstieg
            k = nxt if nxt > k else k + 1
            while k < e and int(A[k, 2]) <= j:
                k += 1
        q = e
    return res[:m]


def run(ds):
    ST._use(ds)
    d = (G._D if G._D is not None else G.data())["NAS"]
    f = os.path.join(P.OUT, f"nzs_{ds}.pkl")
    if os.path.exists(f):
        Aa = pickle.load(open(f, "rb"))
    else:
        Aa = nz_days2(d); pickle.dump(Aa, open(f, "wb"))
    L = sim_side(Aa, d["o"], d["h"], d["l"], d["sp"], 1)
    Sx = sim_side(Aa, d["o"], d["h"], d["l"], d["sp"], -1)
    return L, Sx


def per_year(res, years):
    out = []
    for y in years:
        lo = np.datetime64(f"{y}-01-01", "D").astype(np.int64); hi = np.datetime64(f"{y + 1}-01-01", "D").astype(np.int64)
        r = res[(res[:, 0] >= lo) & (res[:, 0] < hi), 1]
        if len(r) == 0:
            out.append(f"{y}: -"); continue
        pos = r[r > 0].sum(); neg = -r[r < 0].sum()
        out.append(f"{y}: {len(r):3d} {100 * (r > 0).mean():3.0f}% {r.sum():+5.1f}R PF{pos / neg if neg > 0 else 9.9:4.2f}")
    return out


if __name__ == "__main__":
    outf = sys.argv[1] if len(sys.argv) > 1 else os.path.join("ergebnisse", "a60_nzs.txt")
    Le, Se = run("ext"); Lg, Sg = run("gft")
    lim = np.datetime64("2022-01-01", "D").astype(np.int64)
    L = np.r_[Le[Le[:, 0] < lim], Lg]; Sx = np.r_[Se[Se[:, 0] < lim], Sg]
    years = range(2006, 2026)
    say("Noise-Area-Momentum NAS100 (Signal-Ebene, R je Signal der Risikoeinheit): Zellen Jahr: Signale Treffer% Summe-R PF")
    for nm, res in (("Long", L), ("Short", Sx)):
        cells = per_year(res, years)
        for i in range(0, len(cells), 5):
            say(f"  {nm:5s} " + " | ".join(cells[i:i + 5]))
    # Perioden
    for nm, res in (("Long", L), ("Short", Sx)):
        cells = []
        for pn, a, b in A.PER:
            lo = np.datetime64(a, "D").astype(np.int64); hi = np.datetime64(b, "D").astype(np.int64)
            r = res[(res[:, 0] >= lo) & (res[:, 0] < hi), 1]
            yrs = (hi - lo) / 365.25
            pos = r[r > 0].sum(); neg = -r[r < 0].sum()
            cells.append(f"{pn}: {len(r) / yrs:5.1f}/J {r.mean():+.3f} R/Sig PF {pos / neg if neg > 0 else 9.9:4.2f} R/J {r.sum() / yrs:+5.1f}")
        say(f"  {nm:5s} Perioden: " + " | ".join(cells))
    # Korrelation Tagesergebnis Short-Noise gegen NAS-Long-Fades (virtuell, 2022-25) und 2006-21
    fad = {}
    import pg_blocks as PB, cands as K
    for nm in PB.F10:
        if K.FADES[nm]["sym"] != "NAS":
            continue
        c = A.chain(nm)
        for t, r in zip(c["te"], c["R"]):
            fad[int(t // 1440)] = fad.get(int(t // 1440), 0.0) + r
    sd_ = {}
    for dd, r, _ in Sx:
        sd_[int(dd)] = sd_.get(int(dd), 0.0) + r
    for pn, a, b in (("2006-21", "2006-01-01", "2022-01-01"), ("2022-25", "2022-01-01", "2026-01-01")):
        lo = np.datetime64(a, "D").astype(np.int64); hi = np.datetime64(b, "D").astype(np.int64)
        both = [d for d in sd_ if lo <= d < hi and d in fad]
        if len(both) > 10:
            x = np.array([sd_[d] for d in both]); y = np.array([fad[d] for d in both])
            say(f"  {pn}: Tage mit Short-Noise und NAS-Fade: {len(both)}, Korrelation der Tages-R {np.corrcoef(x, y)[0, 1]:+.2f}; "
                f"Short-Noise an Tagen mit Fade-Verlust (< -0,5 R): {x[y < -0.5].sum():+.1f} R in {int((y < -0.5).sum())} Tagen")
    open(outf, "w").write("\n".join(OUT) + "\n")
