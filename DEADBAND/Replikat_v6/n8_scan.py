"""Neues Konzept (Stufe 8): IS/OOS-Raster der eigenstaendigen Strategien auf den GFT-Ersatzdaten ab 2022.
IS = 2022-2023, OOS = 2024-2025 (Gold zusaetzlich 2026 als Zukunftstest). Ausgewaehlt wird nur nach IS.
Aufruf: python n8_scan.py [familie ...]   (orb sb bb pull mom pdl)"""
import sys, json, itertools, numpy as np
import gsig as G, scan6 as S, n8sig as N

T_IS = np.datetime64("2024-01-01", "m").astype(np.int64)
T_OOS = np.datetime64("2026-01-01", "m").astype(np.int64)
VALID_R = 50.5 / 75.0          # ein Tag ist gueltig ab 0,505 % = 0,673 R bei 0,75 % Risiko


def stats(R, t):
    if len(R) == 0:
        return dict(n=0, pf=0.0, Ry=0.0, wr=0.0, tpy=0.0, vy=0.0, avgR=0.0)
    yrs = max((t.max() - t.min()) / 1440 / 365.25, 0.5)
    day = t // 1440
    ud, inv = np.unique(day, return_inverse=True)
    ds = np.zeros(len(ud)); np.add.at(ds, inv, R)
    pos = R[R > 0].sum(); neg = -R[R < 0].sum()
    return dict(n=int(len(R)), pf=float(pos / neg) if neg > 0 else 9.9, Ry=float(R.sum() / yrs), wr=float((R > 0).mean() * 100),
                tpy=float(len(R) / yrs), vy=float((ds >= VALID_R).sum() / yrs), lossy=float((ds < 0).sum() / yrs), avgR=float(R.mean()))


def run(sym, gen, args, label):
    D, ny, days, t_end, atr = S.prep(sym)
    ie, d, rd, tp, ix = gen(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, *args)
    if len(ie) == 0:
        return None
    R, why, held, mfe, mae, iout = G.simulate(sym, ie, d, rd, tp, ix)
    t = ny[ie]
    mi = t < T_IS; mo = (t >= T_IS) & (t < T_OOS); mf = t >= T_OOS
    return dict(label=label, sym=sym, IS=stats(R[mi], t[mi]), OOS=stats(R[mo], t[mo]), F=stats(R[mf], t[mf]))


def grid(**kw):
    keys = list(kw)
    for vals in itertools.product(*kw.values()):
        yield dict(zip(keys, vals))


def fam_orb():
    out = []
    for sym, r0s in (("NAS", (570,)), ("XAU", (-300, 480, 570))):
        for r0 in r0s:
            r1s = {570: (575, 585, 600, 630), 480: (510, 540, 570), -300: (60, 120, 180)}[r0]
            for r1 in r1s:
                tends = (r1 + 60, r1 + 180)
                xms = (720, 960) if r0 >= 480 else (480, 720)
                for g in grid(tend=tends, xm=xms, sm=((0, 0.0), (1, 0.0), (2, 0.2), (3, 0.05)), tpr=(0.0, 1.0, 2.0, 3.0),
                              dirs=(0, 1), maxn=(1, 2), mx=(99.0, 0.6)):
                    if g["tend"] >= g["xm"]:
                        continue
                    args = (r0, r1, g["tend"], g["xm"], g["sm"][0], g["sm"][1], g["tpr"], g["dirs"], 0.0, g["mx"], g["maxn"])
                    out.append((sym, N.gen_orb, args, f"ORB {sym} r{r0}-{r1} w{g['tend']} x{g['xm']} s{g['sm'][0]}/{g['sm'][1]} t{g['tpr']} d{g['dirs']} n{g['maxn']} mx{g['mx']}"))
    return out


def fam_sb():
    out = []
    setups = (("NAS", 570, 600, 600, 660, 720), ("NAS", -420, 570, 570, 660, 720), ("NAS", 570, 630, 630, 720, 840),
              ("XAU", -300, 120, 120, 300, 480), ("XAU", 120, 480, 480, 660, 720), ("XAU", 570, 600, 600, 660, 720),
              ("NAS", 780, 840, 840, 900, 955))
    for sym, a0, a1, w0, w1, xm in setups:
        for g in grid(buf=(0.02, 0.08), tp=((1.0, 0), (2.0, 0), (0.0, 1)), dirs=(0, 1, -1), minsw=(0.0, 0.05)):
            args = (a0, a1, w0, w1, xm, g["buf"], g["tp"][0], g["dirs"], g["minsw"], g["tp"][1])
            out.append((sym, N.gen_sb, args, f"SB {sym} ref{a0}-{a1} w{w0}-{w1} x{xm} b{g['buf']} t{g['tp']} d{g['dirs']} sw{g['minsw']}"))
    return out


def fam_bb():
    out = []
    wins = {"XAU": ((-360, 120, 180), (690, 840, 900), (120, 900, 960)), "NAS": ((690, 840, 900), (600, 900, 955), (-360, 300, 420))}
    for sym in ("XAU", "NAS"):
        for w0, w1, xm in wins[sym]:
            for g in grid(bk=(2.0, 2.5, 3.0), rlo=(25.0, 101.0), stopk=(0.15, 0.3, 0.5), mintp=(0.5, 1.0), maxn=(1, 3), dirs=(0, 1)):
                args = (20, g["bk"], 14, g["rlo"], w0, w1, xm, g["stopk"], g["dirs"], g["mintp"], g["maxn"])
                out.append((sym, N.gen_bb, args, f"BB {sym} w{w0}-{w1} x{xm} k{g['bk']} rsi{g['rlo']} s{g['stopk']} mt{g['mintp']} n{g['maxn']} d{g['dirs']}"))
    return out


def fam_pull():
    out = []
    wins = {"XAU": ((120, 480, 600), (570, 840, 960)), "NAS": ((600, 900, 955), (570, 720, 840))}
    for sym in ("XAU", "NAS"):
        for w0, w1, xm in wins[sym]:
            for g in grid(es=(50, 100, 200), swing=(6, 12), buf=(0.03, 0.1), tpr=(1.0, 2.0, 3.0), maxn=(1, 2), dirs=(0, 1)):
                args = (20, g["es"], w0, w1, xm, g["swing"], g["buf"], g["tpr"], g["dirs"], g["maxn"])
                out.append((sym, N.gen_pull, args, f"PULL {sym} w{w0}-{w1} x{xm} e{g['es']} sw{g['swing']} b{g['buf']} t{g['tpr']} n{g['maxn']} d{g['dirs']}"))
    return out


def fam_mom():
    out = []
    setups = (("XAU", 120, 210, (360, 600)), ("XAU", 180, 240, (420, 600)), ("XAU", 480, 570, (720, 900)),
              ("NAS", 570, 840, (955,)), ("NAS", 570, 900, (955,)), ("NAS", 570, 600, (720, 900)), ("NAS", -360, 570, (630, 720)),
              ("XAU", -360, 120, (300, 480)))
    for sym, t0, t1, xms in setups:
        for g in grid(xm=xms, k=(0.1, 0.25, 0.4), rev=(0, 1), stopk=(0.25, 0.5), tpr=(0.0, 1.5), dirs=(0, 1)):
            args = (t0, t1, g["xm"], g["k"], g["rev"], g["stopk"], g["tpr"], g["dirs"])
            out.append((sym, N.gen_mom, args, f"MOM {sym} {t0}-{t1} x{g['xm']} k{g['k']} rev{g['rev']} s{g['stopk']} t{g['tpr']} d{g['dirs']}"))
    return out


def fam_pdl():
    out = []
    for sym in ("XAU", "NAS"):
        for w0, w1, xm in ((570, 720, 900), (120, 480, 600), (570, 900, 955)):
            for g in grid(mode=(0, 1), buf=(0.05, 0.15), tpr=(1.0, 2.0, 0.0), dirs=(0, 1, -1)):
                args = (w0, w1, xm, g["mode"], g["buf"], g["tpr"], g["dirs"])
                out.append((sym, N.gen_pdl, args, f"PDL {sym} w{w0}-{w1} x{xm} m{g['mode']} b{g['buf']} t{g['tpr']} d{g['dirs']}"))
    return out


FAMS = dict(orb=fam_orb, sb=fam_sb, bb=fam_bb, pull=fam_pull, mom=fam_mom, pdl=fam_pdl)


def line(r):
    a, b, f = r["IS"], r["OOS"], r["F"]
    s = (f"{r['label']:<62s} IS n{a['n']:4d} WR{a['wr']:3.0f} PF{a['pf']:4.2f} R/J{a['Ry']:+6.1f} gü/J{a['vy']:5.1f} | "
         f"OOS n{b['n']:4d} WR{b['wr']:3.0f} PF{b['pf']:4.2f} R/J{b['Ry']:+6.1f} gü/J{b['vy']:5.1f}")
    if f["n"]:
        s += f" | 26 n{f['n']:3d} PF{f['pf']:4.2f} R/J{f['Ry']:+5.1f}"
    return s


def fam_mom2():
    out = []
    setups = (("NAS", 570, 600, 930, 960), ("NAS", -420, 600, 930, 960), ("NAS", 570, 900, 930, 960),
              ("NAS", 570, 600, 900, 960), ("XAU", 480, 600, 900, 955), ("XAU", -420, 480, 840, 955))
    for sym, t0, t1, te, xm in setups:
        for g in grid(k=(0.0, 0.1, 0.25), rev=(0, 1), stopk=(0.15, 0.3), tpr=(0.0, 1.5), dirs=(0, 1), same=(0, 1)):
            args = (t0, t1, te, xm, g["k"], g["rev"], g["stopk"], g["tpr"], g["dirs"], g["same"])
            out.append((sym, N.gen_mom2, args, f"MOM2 {sym} {t0}-{t1} e{te} x{xm} k{g['k']} rev{g['rev']} s{g['stopk']} t{g['tpr']} d{g['dirs']} sm{g['same']}"))
    return out


def fam_hold():
    out = []
    setups = (("XAU", -360, 180), ("XAU", -360, 480), ("XAU", -420, 120), ("XAU", 180, 600), ("XAU", 600, 960), ("XAU", 480, 690),
              ("NAS", -360, 570), ("NAS", -360, 240), ("NAS", 240, 570), ("NAS", 570, 960), ("NAS", 840, 960), ("NAS", -420, 0))
    for sym, a, b in setups:
        for g in grid(d0=(1, -1), stopk=(0.3, 0.6, 1.0), tpr=(0.0, 1.0), trend=(0, 288)):
            args = (a, b, g["d0"], g["stopk"], g["tpr"], g["trend"], 0b111110)
            out.append((sym, N.gen_hold, args, f"HOLD {sym} {a}->{b} d{g['d0']} s{g['stopk']} t{g['tpr']} tr{g['trend']}"))
    return out


FAMS.update(mom2=fam_mom2, hold=fam_hold)


def fam_ibret():
    out = []
    for sym, r0, r1, xm in (("XAU", 570, 630, 955), ("XAU", 510, 570, 955), ("NAS", 570, 630, 955), ("XAU", 480, 540, 900), ("XAU", 120, 180, 480)):
        for g in grid(fin=(0.15, 0.25, 0.35), sin=(0.5, 0.6, 0.8), tout=(0.25, 0.5, 0.75), tend=(r1 + 120, r1 + 240), dirs=(0, 1, -1), mx=(99.0, 0.7)):
            args = (r0, r1, g["tend"], xm, g["fin"], g["sin"], g["tout"], g["dirs"], 0.0, g["mx"])
            out.append((sym, N.gen_ibret, args, f"IBR {sym} {r0}-{r1} w{g['tend']} x{xm} in{g['fin']} st{g['sin']} tg{g['tout']} d{g['dirs']} mx{g['mx']}"))
    return out


def fam_mh():
    """Dokakuri Magic Hours: Stunden-Range fade zur Mitte (= Fade-Konzept auf neuen Zeitfenstern)."""
    out = []
    fade = S.gen_fade
    for sym in ("NAS", "XAU"):
        for r0 in (300, 360, 420, 480) if sym == "NAS" else (-300, -240, 60, 120, 180, 300, 420, 480):
            for g in grid(tlen=(60, 120), xo=(95, 180), buf=(0.75, 1.0), tgt=(0, 1), dirs=(0, 1, -1)):
                r1 = r0 + 60
                args = (r0, r1, r1 + g["tlen"], r1 + g["tlen"] + g["xo"], g["buf"], g["tgt"], g["dirs"], 0.0, 0.6)
                out.append((sym, fade, args, f"MH {sym} {r0}+60 w{g['tlen']} x+{g['xo']} b{g['buf']} t{g['tgt']} d{g['dirs']}"))
    return out


def fam_orbmid():
    out = []
    for sym, m0, m1 in (("NAS", 120, 480), ("NAS", -420, 570), ("XAU", -300, 120), ("XAU", 120, 480)):
        for r0, r1 in ((570, 585), (570, 600), (570, 575)):
            for g in grid(xm=(720, 960), sm=((0, 0.0), (1, 0.0), (2, 0.25)), tpr=(0.0, 1.0, 1.5, 2.0), tend=(r1 + 60, r1 + 150)):
                args = (m0, m1, r0, r1, g["tend"], g["xm"], g["sm"][0], g["sm"][1], g["tpr"], 99.0)
                out.append((sym, N.gen_orbmid, args, f"ORBM {sym} mid{m0}-{m1} r{r0}-{r1} w{g['tend']} x{g['xm']} s{g['sm']} t{g['tpr']}"))
    return out


def fam_lw():
    out = []
    for sym, p0, p1, t0, tend, xms in (("NAS", 570, 960, 570, 900, (960,)), ("XAU", -420, 1020, -360, 900, (955,)), ("XAU", 570, 960, 570, 900, (955,))):
        for g in grid(xm=xms, k=(0.15, 0.25, 0.4, 0.6), sm=((0, 0.0), (1, 0.3), (1, 0.6)), tpr=(0.0, 1.5, 3.0), dirs=(0, 1)):
            args = (p0, p1, t0, tend, g["xm"], g["k"], g["sm"][0], g["sm"][1], g["tpr"], g["dirs"])
            out.append((sym, N.gen_lw, args, f"LW {sym} k{g['k']} s{g['sm']} t{g['tpr']} d{g['dirs']}"))
    return out


def fam_daily():
    out = []
    for sym, ts, rs in (("NAS", 955, 570), ("XAU", 955, -360)):
        for g in grid(kind=(0, 1), thr=(0.1, 0.2), ma=(0, 200 // 1 * 1), mh=(3, 5), stopk=(0.6, 1.0, 1.5), dirs=(0, 1)):
            thr = g["thr"] if g["kind"] == 0 else g["thr"] * 100.0
            args = (g["kind"], ts, rs, thr, g["ma"], g["mh"], g["stopk"], 0.0, g["dirs"])
            out.append((sym, N.gen_daily, args, f"DAY {sym} {'IBS' if g['kind'] == 0 else 'RSI2'} thr{thr} ma{g['ma']} mh{g['mh']} s{g['stopk']} d{g['dirs']}"))
    return out


def fam_tom():
    out = []
    for sym in ("NAS", "XAU"):
        for g in grid(before=(1, 2, 5), after=(1, 3), stopk=(0.6, 1.0, 1.5)):
            out.append((sym, N.gen_tom, (955, g["before"], g["after"], g["stopk"], 0.0), f"TOM {sym} b{g['before']} a{g['after']} s{g['stopk']}"))
    return out


FAMS.update(ibret=fam_ibret, mh=fam_mh, orbmid=fam_orbmid, lw=fam_lw, daily=fam_daily, tom=fam_tom)


if __name__ == "__main__":
    fams = sys.argv[1:] or list(FAMS)
    for fam in fams:
        jobs = FAMS[fam]()
        res = [r for r in (run(*j) for j in jobs) if r is not None]
        json.dump(res, open(f"ergebnisse/n8_scan_{fam}.json", "w"), default=float)
        ok = [r for r in res if r["IS"]["n"] >= 30]
        ok.sort(key=lambda r: -r["IS"]["Ry"])
        npos = sum(1 for r in ok if r["OOS"]["pf"] > 1.0)
        both = [r for r in ok if r["IS"]["pf"] > 1.2 and r["OOS"]["pf"] > 1.2 and r["OOS"]["n"] >= 20]
        print(f"\n=== {fam}: {len(res)} Varianten, {len(ok)} mit IS n>=30, OOS PF>1: {npos}, IS+OOS PF>1.2: {len(both)} ===")
        print("-- Top 12 nach IS R/J:")
        for r in ok[:12]:
            print(line(r))
        print("-- Top 12 nach min(IS,OOS) R/J (nur Ansicht, Auswahl bleibt IS):")
        both.sort(key=lambda r: -min(r["IS"]["Ry"], r["OOS"]["Ry"]))
        for r in both[:12]:
            print(line(r))
        sys.stdout.flush()
