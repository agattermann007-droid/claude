"""Build 6.60, Kandidat K2: die sechs NAS100-Fade-Module UNVERAENDERT (Uhrzeiten, Puffer, Ziel, Range-Filter, Richtung) auf
den US500 (S&P 500 CFD) uebertragen. Signal-Ebene je Jahr 2020-2025 (2020-21 = vor dem Fade-Regime), dazu dieselben Module
auf NAS100 aus derselben Broker-Quelle (GFT-Ersatz 2022-25 bzw. Fremddaten bis 2021) und die Ueberschneidung der Signaltage.
Kosten: Spread = max(Datei, Kurs x relativer Spread wie NAS100), keine Kommission (GFT: Indizes 0 $).
Aufruf: python a60_spx.py [ausgabe.txt]"""
import numpy as np, pandas as pd, os, sys, pickle
import prep5 as P, gsig as G, scan6 as S, pg_fade as PF, cands as K, gext, streams as ST

EXTF = os.path.join(gext.EXT, "US500_ext_M5.csv")
REL = gext.REL_SPREAD["NAS"]
OUT = []


def say(s=""):
    print(s, flush=True); OUT.append(s)


def load_spx(spread_factor=1.0):
    f = os.path.join(P.OUT, f"DSPX_{spread_factor:.2f}.pkl")
    if os.path.exists(f):
        return pickle.load(open(f, "rb"))
    ex = pd.read_csv(EXTF, sep="\t")
    ex.columns = [c.strip("<>").lower() for c in ex.columns]
    t = pd.to_datetime(ex["date"] + " " + ex["time"], format="%Y.%m.%d %H:%M:%S")
    ny = (t - pd.Timedelta(hours=7)).values.astype("datetime64[m]").astype(np.int64)
    o = ex["open"].to_numpy(float); h = ex["high"].to_numpy(float); l = ex["low"].to_numpy(float); c = ex["close"].to_numpy(float)
    sp = ex["spread"].to_numpy(float) * P.POINT
    rel = REL * c
    sp = np.where(np.isnan(sp) | (sp <= 0), rel, np.maximum(sp, rel)) * spread_factor
    v = ex["tickvol"].to_numpy(float)
    d = dict(ny=ny, o=o, h=h, l=l, c=c, sp=sp, v=v)
    d["d1"] = P.agg(ny, o, h, l, c, v, 1440, offset=420)
    pickle.dump(d, open(f, "wb"))
    return d


def daily_atr(D, n=14):
    d1 = D["d1"]; h, l, c = d1["h"], d1["l"], d1["c"]
    tr = np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1]); tr = np.r_[h[0] - l[0], tr]
    atr = np.convolve(tr, np.ones(n) / n, mode="full")[:len(tr)]; atr[:n - 1] = np.nan
    return d1["t"] + 1440, atr


def signals(D, nm, comm_px=0.0):
    p = dict(K.FADES[nm]); p.pop("sym")
    r0, L, tlen, xoff, buf, tgt, dirs = p["r0"], p["L"], p["tlen"], p["xoff"], p["buf"], p["tgt"], p["dirs"]
    mx = p.get("mx", 0.6); mn = p.get("mn", 0.0)
    ny = D["ny"]
    days = np.unique(ny // 1440); days = days[((days + 4) % 7 >= 1) & ((days + 4) % 7 <= 5)]
    t_end, atr = daily_atr(D)
    r1 = r0 + L; tend = r1 + tlen; xm = min(r1 + tlen + xoff, 16 * 60 + 40)
    if xm <= tend:
        tend = xm - 5
    ie, d, rd, tp, ix, *_ = PF.gen_fade_info(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, r0, r1, tend, xm,
                                             buf, tgt, dirs, mn, mx)
    R = G._sim(D["o"], D["h"], D["l"], D["c"], D["sp"], ie.astype(np.int64), d.astype(np.int64), rd, tp, ix.astype(np.int64),
               0.0, 0.0, -99.0, 0.0, 0.0, comm_px, 1)[0]
    ok = rd >= 6.0 * D["sp"][ie]                                        # wie im EA: Stop >= 6 Spreads
    return dict(te=ny[ie][ok], R=R[ok], day=(ny[ie][ok] // 1440))


def per_year(te, R, years):
    out = []
    for y in years:
        lo = np.datetime64(f"{y}-01-01", "m").astype(np.int64); hi = np.datetime64(f"{y + 1}-01-01", "m").astype(np.int64)
        s = (te >= lo) & (te < hi)
        r = R[s]
        if len(r) == 0:
            out.append(f"{y}: -"); continue
        pos = r[r > 0].sum(); neg = -r[r < 0].sum()
        out.append(f"{y}: {len(r):3d} WR{100 * (r > 0).mean():3.0f}% {r.sum():+5.1f}R PF{pos / neg if neg > 0 else 9.9:4.2f}")
    return " | ".join(out)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("ergebnisse", "a60_spx.txt")
    NAS6 = ["N1030", "N1330", "N1800", "N0930", "N1100", "N1300"]
    DS = load_spx()
    ST._use("gft"); DN = G.data()["NAS"]
    ST._use("ext"); DNx = G._D["NAS"]
    years = range(2020, 2026)
    say("NAS-Fade-Module unveraendert auf US500 (ohne Grid-Filter, mit Stop >= 6 Spreads; Kosten: Spread wie NAS relativ zum Kurs)")
    tots = {"SPX": ([], []), "NAS": ([], [])}
    overlap = []
    for nm in NAS6:
        s = signals(DS, nm)
        n1 = signals(DNx, nm); n2 = signals(DN, nm)
        lim = np.datetime64("2022-01-01", "m").astype(np.int64)
        nte = np.r_[n1["te"][n1["te"] < lim], n2["te"]]; nR = np.r_[n1["R"][n1["te"] < lim], n2["R"]]
        say(f"== {nm}")
        say(f"  US500 : {per_year(s['te'], s['R'], years)}")
        say(f"  NAS100: {per_year(nte, nR, years)}")
        tots["SPX"][0].append(s["te"]); tots["SPX"][1].append(s["R"])
        tots["NAS"][0].append(nte); tots["NAS"][1].append(nR)
        sd = set((s["te"] // 1440).tolist()); nd = set((nte // 1440).tolist())
        both = len(sd & nd); overlap.append((nm, len(sd), len(nd), both))
    say("== Summe der 6 Module")
    for k in ("SPX", "NAS"):
        te = np.concatenate(tots[k][0]); R = np.concatenate(tots[k][1])
        say(f"  {k:6s}: {per_year(te, R, years)}")
    say("Signaltage je Modul: US500 / NAS100 / beide (Anteil der US500-Tage, an denen NAS dasselbe Modul hatte)")
    for nm, a, b, c in overlap:
        say(f"  {nm}: {a} / {b} / {c} ({100 * c / max(a, 1):.0f} %)")
    # Korrelation der Tagesergebnisse (R je Tag, alle 6 Module), 2022-25
    def daily(te, R):
        dd = {}
        for t, r in zip(te, R):
            if t >= np.datetime64("2022-01-01", "m").astype(np.int64):
                dd[int(t // 1440)] = dd.get(int(t // 1440), 0.0) + r
        return dd
    a = daily(np.concatenate(tots["SPX"][0]), np.concatenate(tots["SPX"][1]))
    b = daily(np.concatenate(tots["NAS"][0]), np.concatenate(tots["NAS"][1]))
    common = sorted(set(a) & set(b))
    if len(common) > 10:
        x = np.array([a[d] for d in common]); y = np.array([b[d] for d in common])
        say(f"Tage mit Signalen auf beiden 2022-25: {len(common)}, Korrelation der Tages-R: {np.corrcoef(x, y)[0, 1]:.2f}; "
            f"nur US500: {len(set(a) - set(b))} Tage (R {sum(a[d] for d in set(a) - set(b)):+.1f}), nur NAS: {len(set(b) - set(a))} Tage")
    open(out, "w").write("\n".join(OUT) + "\n")
