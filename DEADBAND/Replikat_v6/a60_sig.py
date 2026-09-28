"""Build 6.60 (Suche): Signal-Ebene der 10 Fade-Module ueber alle Perioden 2006-2025.
1. je Modul und Periode: Signale je Jahr, Trefferquote, R je Signal, PF, R je Jahr (Grid-Regel S wie im EA, N1800 ohne Grid)
2. dieselben Module in GESPIEGELTER Richtung (Short statt Long bzw. umgekehrt, sonst gleiche Parameter)
3. Aufteilung nach Tagestrend beim Signal (Schlusskurs des letzten abgeschlossenen Servertags ueber/unter SMA(50) der
   Tages-Schlusskurse; vorab festgelegt, SMA(200) nur zur Information): Fade MIT dem Trend (Long im Aufwaertstrend,
   Short im Abwaertstrend) gegen Fade GEGEN den Trend.
4. Zielweite in R (tp) je Modul: Anteil der Signale, deren Treffer bei 0,70 % Risiko einen Tag allein gueltig macht.
Aufruf: python a60_sig.py [ausgabe.txt]"""
import numpy as np, sys, os
import streams as ST, pg_fade as PF, cands as K, gsig as G, pg_blocks as PB, x41

PER = (("2006-13", "2006-01-01", "2014-01-01"), ("2014-21", "2014-01-01", "2022-01-01"),
       ("2022-23", "2022-01-01", "2024-01-01"), ("2024-25", "2024-01-01", "2026-01-01"))
LIM22 = ST.LIM22
OUT = []


def say(s=""):
    print(s, flush=True); OUT.append(s)


def t64(s):
    return np.datetime64(s, "m").astype(np.int64)


def fade_dir(ds, nm, dirs=None):
    """Signale eines Moduls auf Datensatz ds; dirs None = wie im Modul, sonst 1/-1 (gespiegelt)."""
    ST._use(ds)
    orig = K.FADES[nm]["dirs"]
    if dirs is not None:
        K.FADES[nm]["dirs"] = dirs
    try:
        f = PF.fade_info(nm)
    finally:
        K.FADES[nm]["dirs"] = orig
    f["dataset"] = ds
    return f


def trend_state(ds, sym, t_entry, n=50):
    """+1 Aufwaertstrend (letzter Servertag-Schluss > SMA(n) der Schluesse), -1 Abwaertstrend, 0 unbekannt."""
    ST._use(ds)
    D = (G._D if G._D is not None else G.data())[sym]
    d1 = D["d1"]; c = d1["c"]; t_end = d1["t"] + 1440
    sma = np.convolve(c, np.ones(n) / n, mode="full")[:len(c)]
    sma[:n - 1] = np.nan
    k = np.searchsorted(t_end, t_entry, side="right") - 1
    ok = k >= 0
    out = np.zeros(len(t_entry), np.int64)
    kk = np.maximum(k, 0)
    up = ok & np.isfinite(sma[kk]) & (c[kk] > sma[kk])
    dn = ok & np.isfinite(sma[kk]) & (c[kk] < sma[kk])
    out[up] = 1; out[dn] = -1
    return out


def chain(nm, dirs=None, grid=True):
    """Kette Fremddaten (bis 2021) + GFT-Ersatz (ab 2022) wie der Kontomotor: t_entry, R, d, tp, trend50, trend200."""
    rule = x41.S70_OHNE
    parts = []
    for ds in ("ext", "gft"):
        f = fade_dir(ds, nm, dirs)
        if grid and nm not in rule.get("exempt", ()):
            keep, live, tp, w = PB.apply_rule(f, rule)
        else:
            keep = np.ones(len(f["R"]), bool)
        sel = keep & ((f["t_entry"] < LIM22) if ds == "ext" else (f["t_entry"] >= LIM22))
        tr50 = trend_state(ds, f["sym"], f["t_entry"], 50)
        tr200 = trend_state(ds, f["sym"], f["t_entry"], 200)
        parts.append(dict(te=f["t_entry"][sel], R=f["R"][sel], d=f["d"][sel], tp=f["tp"][sel], tr50=tr50[sel], tr200=tr200[sel]))
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}


def stats(R, yrs):
    n = len(R)
    if n == 0:
        return "   -"
    pos = R[R > 0].sum(); neg = -R[R < 0].sum()
    pf = pos / neg if neg > 0 else 9.9
    return f"{n / yrs:5.1f}/J WR {100 * (R > 0).mean():3.0f}% R/Sig {R.mean():+.3f} PF {pf:4.2f} R/J {R.sum() / yrs:+6.1f}"


def per_rows(c, mask, label):
    cells = []
    for pn, a, b in PER:
        lo, hi = t64(a), t64(b)
        yrs = (hi - lo) / (365.25 * 1440)
        s = mask & (c["te"] >= lo) & (c["te"] < hi)
        cells.append(f"{pn}: {stats(c['R'][s], yrs)}")
    say(f"{label:<28s} | " + " | ".join(cells))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("ergebnisse", "a60_sig.txt")
    say("Signal-Ebene der Fade-Module (Grid-Regel S wie im EA, N1800 ohne Grid; Fremddaten bis 2021, GFT-Ersatz ab 2022)")
    say("Zellen: Signale je Jahr, Trefferquote, R je Signal, Profitfaktor, R je Jahr")
    tot = {}
    for nm in PB.F10:
        d0 = K.FADES[nm]["dirs"]
        c = chain(nm)
        m = chain(nm, dirs=-d0)
        say(f"== {nm} ({'Long' if d0 > 0 else 'Short'}, {K.FADES[nm]['sym']})")
        allm = np.ones(len(c["R"]), bool)
        per_rows(c, allm, "wie im EA")
        per_rows(c, c["tr50"] * c["d"] > 0, "  mit Trend (SMA50)")
        per_rows(c, c["tr50"] * c["d"] < 0, "  gegen Trend (SMA50)")
        per_rows(c, c["tr200"] * c["d"] > 0, "  mit Trend (SMA200)")
        per_rows(c, c["tr200"] * c["d"] < 0, "  gegen Trend (SMA200)")
        allm2 = np.ones(len(m["R"]), bool)
        per_rows(m, allm2, "gespiegelt")
        per_rows(m, m["tr50"] * m["d"] > 0, "  gespiegelt mit Trend")
        per_rows(m, m["tr50"] * m["d"] < 0, "  gespiegelt gegen Trend")
        # Zielweite: Anteil Signale mit tp * 70 $ >= 53 $ (Treffer macht den Tag allein gueltig, volle Groesse)
        sel = c["te"] >= LIM22
        tp = c["tp"][sel]
        if len(tp):
            q = np.percentile(tp, [10, 25, 50, 75, 90])
            say(f"   Zielweite tp in R (2022-25): p10 {q[0]:.2f} p25 {q[1]:.2f} Median {q[2]:.2f} p75 {q[3]:.2f} p90 {q[4]:.2f} | "
                f"Treffer allein gueltig (tp >= 0,76): {100 * np.mean(tp >= 0.757):.0f} % | mit 0,9 % Risiko (tp >= 0,59): {100 * np.mean(tp >= 0.589):.0f} %")
        tot[nm] = (c, m)
    # Summen ueber alle Module: wie im EA, nur mit Trend, gespiegelt mit Trend, Portfolio "mit Trend beide Richtungen"
    say("== Summe aller 10 Module")
    C = {k: np.concatenate([tot[n][0][k] for n in PB.F10]) for k in tot[PB.F10[0]][0]}
    M = {k: np.concatenate([tot[n][1][k] for n in PB.F10]) for k in tot[PB.F10[0]][1]}
    per_rows(C, np.ones(len(C["R"]), bool), "wie im EA")
    per_rows(C, C["tr50"] * C["d"] > 0, "  nur mit Trend")
    per_rows(C, C["tr50"] * C["d"] < 0, "  nur gegen Trend")
    per_rows(M, np.ones(len(M["R"]), bool), "gespiegelt")
    per_rows(M, M["tr50"] * M["d"] > 0, "  gespiegelt mit Trend")
    B = {k: np.r_[C[k], M[k]] for k in C}
    per_rows(B, B["tr50"] * B["d"] > 0, "beide Richtungen, mit Trend")
    open(out, "w").write("\n".join(OUT) + "\n")
