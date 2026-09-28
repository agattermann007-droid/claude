"""Bewertung v11 (Build 6.70): wie evl10 mit eng11 (Zaehler ext_n = verlaengerte Ziele, ext_hit = verlaengertes Ziel
erreicht, fsym_blk = Fade-Einstiege durch die Tagessperre je Symbol ausgelassen, nz_blk = Noise-Signale durch die Noise-Tagespause
ausgelassen).
Bewertung v10 (Build 6.60): wie evl9 mit eng10 (Zaehler sv_up = vergroesserte Einstiege fuer den gueltigen Tag).
6.70: Konsistenzregel - Wartetage, gesperrte Tage, Anteil der Auszahlungen mit Konsistenz als letzter Bedingung, Netto inkl.
am Ende noch nicht ausgezahltem Gewinn (net_open).
Bewertung v9 (Build 6.50): wie evl8 mit eng9, zusaetzlich Ergebnis der Trades, die nach einem schon gueltigen Tag
eroeffnet wurden (pv: Anzahl, Summe, je Modul).
Bewertung v8 (Build 6.40): wie evl6 (rollierende Konten 1/2/3 Jahre, Stoerungen), mit eng8 und zusaetzlich
- Auszahlungstakt: Tage je Auszahlung (365,25 / Auszahlungen je Jahr), Luecke zwischen Auszahlungen (Mittel, groesste),
  Anteil der Zyklen, die zuletzt auf gueltige Tage / Mindestgewinn / 10-Tage-Frist warteten, Tage bis 5 gueltige Tage
  bzw. bis zum Mindestgewinn,
- Tages-Diagnose: realisiertes Tagesergebnis (< 0, 0-25 $, 25-50,50 $, gueltig), gueltig gewesene und wieder verlorene
  Tage, Wartetage (Reife, Auszahlung, Neukauf), Handelstage ohne Trade,
- Schutz gueltiger Tage: gekuerzte bzw. ausgelassene Einstiege."""
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import eng11 as E, evl6 as V6

V6.E = E
NEAR_SCALE = 1.0          # 6.50: Schwellen 100/200 $ (1 %/2 % von 10k) fuer groessere Konten skalieren (Startsaldo / 10000)
WARM = V6.WARM
starts = V6.starts
line6 = V6.line
EXTRA = ["d_neg", "d_0_25", "d_25_50", "d_valid", "d_vlost", "d_wait", "d_notrade", "vp_cut", "vp_block",
         "lim_valid", "lim_profit", "lim_ten", "cyc_v5", "cyc_pr", "trade_days", "gaps_sum", "bank", "sv_up",
         "cons_wait", "cons_block", "open_end", "lim_cons", "ext_n", "ext_hit", "fsym_blk", "nz_blk"]


def _job(args):
    Pv, d0, d1, seed, skip, slip, GP = args
    m = V6.mk()
    Pv = Pv.copy()
    if seed > 0:
        Pv[E.PI["slip_frac"]] = slip
    ms = V6.masks(m, seed, skip if seed > 0 else 0.0)
    rr = E.run(m, Pv, d0, d1, seed=seed, masks=ms, GP=GP)
    st = rr["st"]; S = E.SI; tr = rr["tr"]; ev = rr["ev"]
    pnls, slots = V6.ideas(tr)
    n5, n6, n8, mx, worst = V6.streaks(pnls)
    pays = ev[ev[:, 0] == 1, 2] if len(ev) else np.zeros(0)
    pdays = ev[ev[:, 0] == 1, 1] if len(ev) else np.zeros(0)
    mods = {}
    for x, sl in zip(pnls, slots):
        nm = V6.modname(int(sl))
        a = mods.setdefault(nm, [0.0, 0, 0])
        a[0] += x; a[1] += 1; a[2] += int(x > 0)
    out = dict(years=rr["years"], npay=float(st[S["npay"]]), sumpay=float(st[S["sumpay"]]), nbust=int(st[S["nbust"]]),
               floor_b=float(st[S["floor_b"]]), float_b=float(st[S["float_b"]]), day_b=float(st[S["day_b"]]),
               ntr=float(len(pnls)), wins=float((pnls > 0).sum()), n5=n5, n6=n6, n8=n8, mx=mx, worst=worst,
               gapmax=float(st[S["gaps_max"]]), maxdd=float(st[S["maxdd"]]), valid=float(st[S["valid_days"]]),
               cool=float(st[S["cool"]]), bank=float(st[S["bank"]]), ge=float(st[S["ge"]]), harv=float(st[S["harv"]]),
               cyc=float(st[S["cyc_days"]]), paymin=float(pays.min()) if len(pays) else 0.0, mods=mods)
    for k in EXTRA:
        out["x_" + k] = float(st[S[k]])
    out["minbuf"] = float(st[S["minbuf"]])
    # 6.70: Serien je Position (wie MT5/GFT-Dashboard zaehlen: jeder Noise-Teil einzeln), in Ausstiegsreihenfolge
    n5p, n6p, n8p, mxp, worstp = V6.streaks(tr[:, 1]) if len(tr) else (0, 0, 0, 0, 0.0)
    out["n5p"] = n5p; out["n6p"] = n6p; out["mxp"] = mxp
    pv = {}
    for row in tr:
        f = int(row[4])
        if f <= 0:
            continue
        nm = V6.modname(int(row[2])) + ("" if f == 1 else "*")
        a = pv.setdefault(nm, [0.0, 0, 0])
        a[0] += row[1]; a[1] += 1; a[2] += int(row[1] > 0)
    out["pv"] = pv
    # Luecken zwischen Auszahlungen (Kalendertage), erste ab Kontostart
    d0day = float(m.days[d0])
    gl = np.diff(np.r_[d0day, np.sort(pdays)]) if len(pdays) else np.zeros(0)
    out["gaps"] = gl
    return out


def agg(rows):
    a = V6.agg(rows)
    Y = sum(r["years"] for r in rows)
    for k in EXTRA:
        a["x_" + k] = sum(r["x_" + k] for r in rows) / Y
    ncyc = a["x_lim_valid"] + a["x_lim_profit"] + a["x_lim_ten"]
    a["lim_valid_pct"] = 100.0 * a["x_lim_valid"] / max(ncyc, 1e-9)
    a["lim_profit_pct"] = 100.0 * a["x_lim_profit"] / max(ncyc, 1e-9)
    a["lim_ten_pct"] = 100.0 * a["x_lim_ten"] / max(ncyc, 1e-9)
    a["lim_cons_pct"] = 100.0 * a["x_lim_cons"] / max(a["pay"] + 1e-9, 1e-9)   # 6.70: Anteil der Auszahlungen, die zuletzt auf die Konsistenz warteten
    a["net_open"] = a["net"] + 0.8 * 0.97 * a["x_open_end"]                     # 6.70: Netto inkl. am Ende noch nicht ausgezahltem Gewinn
    a["t_v5"] = a["x_cyc_v5"] / max(ncyc, 1e-9)
    a["t_pr"] = a["x_cyc_pr"] / max(ncyc, 1e-9)
    g = np.concatenate([r["gaps"] for r in rows]) if rows else np.zeros(0)
    a["gap_mean"] = float(g.mean()) if len(g) else 0.0
    a["gap_p90"] = float(np.percentile(g, 90)) if len(g) else 0.0
    a["days_per_pay"] = 365.25 / max(a["pay"], 1e-9)
    a["s5p"] = sum(r["n5p"] for r in rows) / Y                                   # 6.70: Serien je Position (MT5-Zaehlung)
    a["s6p"] = sum(r["n6p"] for r in rows) / Y
    a["mxp"] = float(np.mean([r["mxp"] for r in rows])) if rows else 0.0
    a["mxpmax"] = float(np.max([r["mxp"] for r in rows])) if rows else 0.0
    mb = np.array([r["minbuf"] for r in rows])
    a["minbuf_mean"] = float(mb.mean()) if len(mb) else 0.0
    a["near100"] = float(np.mean(mb < 100.0 * NEAR_SCALE)) if len(mb) else 0.0       # Anteil Konten, die dem Boden auf < 1 % nahekamen
    a["near200"] = float(np.mean(mb < 200.0 * NEAR_SCALE)) if len(mb) else 0.0
    pv = {}
    for r in rows:
        for nm, (x, n, w) in r.get("pv", {}).items():
            b = pv.setdefault(nm, [0.0, 0, 0])
            b[0] += x; b[1] += n; b[2] += w
    a["pv"] = {nm: dict(pnl=b[0] / Y, tr=b[1] / Y, wr=100.0 * b[2] / max(b[1], 1)) for nm, b in pv.items()}
    return a


def evaluate(Pv, GP, horizons=(250, 500, 750), step=3, seeds=tuple(range(8)), skip=0.03, slip=0.3, workers=4,
             warm=WARM, end=None, per_seed=False, by_year=False):
    m = V6.mk()
    jobs = []; tags = []
    for h in horizons:
        for (a, b) in starts(m, h, step, warm, end):
            for s in seeds:
                jobs.append((Pv, a, b, s, skip, slip, GP)); tags.append((h, s, a))
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            outs = list(ex.map(_job, jobs, chunksize=32))
    else:
        outs = [_job(j) for j in jobs]
    byh = {}
    for (h, s, a), o in zip(tags, outs):
        byh.setdefault(h, []).append(o)
    res = {h: agg(byh[h]) for h in horizons if h in byh}
    hs = [h for h in horizons if h in res]
    keys = [k for k in res[hs[0]].keys() if k not in ("mods", "pv")]
    mean = {k: float(np.mean([res[h][k] for h in hs])) for k in keys}
    mean["pv"] = res[hs[0]]["pv"]
    mean["mxmax"] = float(np.max([res[h]["mxmax"] for h in hs]))
    mean["p_bust1"] = res[hs[0]]["p_bust"]
    mean["mods"] = res[hs[0]]["mods"]
    if per_seed:
        per = []
        for s in seeds:
            hsr = [agg([o for (h, s2, a), o in zip(tags, outs) if h == hh and s2 == s]) for hh in hs]
            per.append([np.mean([x[k] for x in hsr]) for k in ("pay", "bust", "net", "s5", "s6", "mx", "wr", "net_open", "s5p", "s6p", "mxp")])
        per = np.array(per)
        mean["streuung"] = dict(mean=per.mean(0).tolist(), sd=per.std(0, ddof=1).tolist() if len(seeds) > 1 else [0.0] * 11,
                                keys=["pay", "bust", "net", "s5", "s6", "mx", "wr", "net_open", "s5p", "s6p", "mxp"], per=per.tolist())
    if by_year:
        by = {}
        for (h, s, a), o in zip(tags, outs):
            if h != hs[0]:
                continue
            y = str(np.datetime64(int(m.days[a]), "D"))[:4]
            by.setdefault(y, []).append(o)
        mean["jahre"] = {}
        for y, rows in sorted(by.items()):
            a = agg(rows)
            mean["jahre"][y] = {k: a[k] for k in ("pay", "paymean", "bust", "net", "s6", "mx", "mxmax", "wr", "gap_mean", "n", "net_open")}
    return mean


def line(label, r):
    return (f"{label:<40s} Ausz {r['pay']:5.2f} ({r['days_per_pay']:4.1f} T) Ø{r['paymean']:4.0f}$ Bust {r['bust']:5.3f} "
            f"P1 {r.get('p_bust1', r['p_bust']):5.3f} Netto {r['net']:5.0f} S6 {r['s6']:4.2f} maxS {r['mx']:4.1f}/{r['mxmax']:.0f} "
            f"WR {r['wr']:4.1f} | gueltig {r['valid']:4.1f} verl {r['x_d_vlost']:4.1f} 25-50 {r['x_d_25_50']:4.1f} "
            f"0-25 {r['x_d_0_25']:4.1f} neg {r['x_d_neg']:4.1f} warte {r['x_d_wait']:4.1f} leer {r['x_d_notrade']:4.1f} | "
            f"zuletzt gT/MG/10 {r['lim_valid_pct']:3.0f}/{r['lim_profit_pct']:3.0f}/{r['lim_ten_pct']:3.0f} % "
            f"T5g {r['t_v5']:4.1f} TMG {r['t_pr']:4.1f} | Luecke Ø {r['gap_mean']:4.1f} p90 {r['gap_p90']:4.0f} | "
            f"Boden: Abstand min Ø {r.get('minbuf_mean', 0):4.0f}$ <1% {100 * r.get('near100', 0):4.1f}% <2% {100 * r.get('near200', 0):4.1f}%")
