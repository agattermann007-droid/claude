"""Stufe 8.10: Kontoerkenner und Anpasser im Konto-Replikat (eng6 mit Zustandsmaschine, st_on / SM).
Basis = 8.00 (10 Fades mit Portfolio-Waechter, Spike 8:30, LW 0,5 % ab 4 % Puffer, Gold-Asien XA, RSI21, Noise,
Pufferkurve 3,5/1,25/0,1). Zustaende siehe eng6.ZN. Klassen der Matrix SM: 0 DEADBAND, 1 RSI21, 2 Noise, 3+s Strom s
(s 0..9 Fades, 10 Spike, 11 LW, 12 XA).
Bewertung: ganzer Zeitraum (250/500 Tage, Starts 2022-03..2025-12), Auswahl IS (Starts 2022-03..2023, Ende 2023-12),
Pruefung OOS (Starts ab 2024, Ende 2025-12), Fremddaten 2006-2021 (ext)."""
import os, sys, json, pickle, numpy as np
import eng6 as E, evl6 as V, y7_konto as Y, n8_port as NP, n8_konto as NK, prep5 as P

KW80 = dict(ddfull=3.5, ddmin=1.25, ddfmin=0.1)
NEW80 = ["LW", "XASIA"]
RISK80 = {"LW": dict(risk=0.5, minbuf=4.0)}
# Gruppen fuer die Matrix
G_FADE = list(range(3, 13)); G_SPIKE = [13]; G_LW = [14]; G_XA = [15]; G_R21 = [1]; G_NZ = [2]
G_TD = [16]                      # 8.10: Trend-Day (Strom 13, extra=[("LM", ...)]) = EA-Klasse 7
GROUPS = dict(fade=G_FADE, spike=G_SPIKE, lw=G_LW, xa=G_XA, r21=G_R21, nz=G_NZ, td=G_TD)

_DS = None


def use(ds):
    """Datensatz waehlen: 'gft' (GFT-Ersatz 2022-25) oder 'ext' (Fremddaten 2006-21). Baut die 8.00-Stroeme."""
    global _DS, BLKS, GPS
    if _DS == ds:
        return
    if ds == "ext":
        V._MK = E.Market(D=pickle.load(open(os.path.join(P.OUT, "DXfull.pkl"), "rb")),
                         S=pickle.load(open(os.path.join(P.OUT, "sig5_ext.pkl"), "rb")))
        fb = Y.fade_blocks("ext")
        blks = list(fb) + [Y.spike_block("ext", 10, dict(Y.SPIKE, kmin=0.20), only_dir=1)]
        gps = [dict(on=1, risk=0.75, maxtrades=1, harv=1) for _ in blks]
        for nm in NEW80:
            s_ = len(blks)
            sym, gen, args = NP.LIB[nm]
            blks.append(NK.block(sym, gen, args, s_))
            rv = RISK80.get(nm, 0.75)
            gps.append(dict(dict(on=1, risk=0.75, maxtrades=1, harv=1), **rv) if isinstance(rv, dict) else dict(on=1, risk=rv, maxtrades=1, harv=1))
        for i, b in enumerate(blks):
            b["str"] = i
    else:
        V._MK = None
        V.mk()
        blks, gps = NP.build(True, NEW80, RISK80, spike=True)
    BLKS, GPS = blks, gps
    _DS = ds


def sm_from(rows):
    """rows: dict Zustand -> dict Gruppe(fade/spike/lw/xa/r21/nz/all) -> Faktor."""
    SM = E.smatrix()
    for zn, g in (rows or {}).items():
        for grp, f in g.items():
            cols = [c for v in GROUPS.values() for c in v] if grp == "all" else GROUPS[grp]
            for c in cols:
                SM[E.ZI[zn], c] = float(f)
    return SM


def evaluate(ds, kw=None, rows=None, parts=("all", "IS", "OOS"), gps_mod=None, seeds=None, extra=None):
    """Ein Satz: kw = Motor-Parameter (zusaetzlich zu 8.00), rows = Zustandsfaktoren, extra = [(Name in NP.LIB, GP-dict)]
    zusaetzliche Stroeme (Platz 13 ff.). Gibt dict je Teil zurueck."""
    use(ds)
    gps = [dict(g) for g in GPS]
    blks = list(BLKS)
    for nm, gp in (extra or []):
        sym, gen, args = NP.LIB[nm]
        b = NK.block(sym, gen, args, len(blks))
        blks.append(b)
        gps.append(dict(dict(on=1, risk=0.75, maxtrades=1, harv=1), **gp))
    if gps_mod:
        for i, m in gps_mod.items():
            gps[i].update(m)
    GP = E.gparams(gps)
    V.set_generic(blks, GP)
    Pv = E.params(**dict(Y.BASE, **KW80, **(kw or {})))
    SM = sm_from(rows)
    out = {}
    if ds == "ext":
        out["ext"] = V.evaluate(Pv, GP=GP, horizons=(250, 500), step=9, seeds=seeds or (0, 1, 2, 3), warm="2006-09-01",
                                end="2021-12-31", SM=SM)["mean"]
        return out
    sd = seeds or tuple(range(8))
    if "all" in parts:
        out["all"] = V.evaluate(Pv, GP=GP, horizons=(250, 500), step=3, seeds=sd, skip=0.05, end="2025-12-31", SM=SM)["mean"]
    if "IS" in parts:
        out["IS"] = V.evaluate(Pv, GP=GP, horizons=(250,), step=2, seeds=sd, skip=0.05, warm="2022-03-21", end="2023-12-31", SM=SM)["mean"]
    if "OOS" in parts:
        out["OOS"] = V.evaluate(Pv, GP=GP, horizons=(250,), step=2, seeds=sd, skip=0.05, warm="2024-01-02", end="2025-12-31", SM=SM)["mean"]
    return out


def short(m):
    return f"{m['pay']:5.2f}/{m['net']:5.0f}/{m['bust']:.3f}"


def kurz(lbl, r):
    s = f"{lbl:<44s}"
    for p in ("all", "IS", "OOS", "ext"):
        if p in r:
            m = r[p]
            s += f" | {p} {m['pay']:5.2f} {m['net']:5.0f}$ B{m['bust']:.3f} Ø{m['paymean']:3.0f} Z{m['cyc']:4.1f}T g{m['valid']:4.1f}"
    return s


def gruppe(nm):
    if nm.startswith("g"):
        i = int(nm[1:])
        return "fade" if i < 10 else ("spike" if i == 10 else ("lw" if i == 11 else ("xa" if i == 12 else ("td" if i == 13 else nm))))
    return nm


def zustandstabelle(m):
    """Tage/Jahr je Zustand, Pleiten je Zustand, Ergebnis je Zustand und Gruppe ($/J, Trades/J, WR)."""
    lines = []
    zd = m["zdays"]; zb = m["zbust"]
    tot = {}
    for k, v in m["zm"].items():
        z, nm = k.split("|")
        g = gruppe(nm)
        a = tot.setdefault((z, g), [0.0, 0.0, 0.0])
        a[0] += v["pnl"]; a[1] += v["tr"]; a[2] += v["tr"] * v["wr"] / 100.0
    gs = ["fade", "spike", "lw", "xa", "td", "r21", "nz"]
    lines.append(f"{'Zustand':<10s} {'Tage/J':>7s} {'Pleit/J':>7s} " + " ".join(f"{g:>16s}" for g in gs) + f" {'Summe':>8s}")
    for z, zn in enumerate(E.ZN):
        cells = []; s = 0.0
        for g in gs:
            a = tot.get((zn, g))
            if a and a[1] > 0:
                cells.append(f"{a[0]:6.0f}$ {a[1]:4.1f} {100*a[2]/a[1]:3.0f}%"); s += a[0]
            else:
                cells.append(f"{'-':>16s}")
        lines.append(f"{zn:<10s} {zd[z]:7.1f} {zb[z]:7.3f} " + " ".join(f"{c:>16s}" for c in cells) + f" {s:8.0f}")
    return "\n".join(lines)


def save(fn, res):
    json.dump(res, open(fn, "w"), default=float, indent=1)


if __name__ == "__main__":
    ds = sys.argv[1] if len(sys.argv) > 1 else "gft"
    r = evaluate(ds)
    print(kurz(f"8.00 {ds}", r), flush=True)
    for p, m in r.items():
        print(f"--- {p}\n" + zustandstabelle(m), flush=True)
    save(f"ergebnisse/z8_mess_{ds}.json", r)
