"""Build 6.60: Zerlegung je Kalenderjahr, wo Fade-Signale (und ihr virtuelles R) auf dem Weg ins Konto wegfallen:
S0 alle Signale (Grid-Regel S wie im EA), S1 nach Feiertags- und Spread-Filter (Stop >= 6 Spreads), S2 nach Portfolio-Waechter
(= Bloecke fuer den Kontomotor), S3 im Konto gehandelt (Mittel je Konto-Jahr, 1-Jahres-Konten, Stoerungen).
Zusaetzlich fuer S2-Signale, die das Konto NICHT handelt, der Grund (Konto im Reife-/Auszahlungsmodus, Serien-Stopp, Schutz
gueltiger Tage, Budget/offene Position) - bestimmt mit einem Zustandsprotokoll je Kerze (nur Diagnose, eng10 unveraendert).
Aufruf: python a60_stufen.py [Variante] [gft|ext]"""
import numpy as np, sys
import x60, x48, r6, x35 as X, pg_blocks as PB, x41
import eng10 as E, evl6 as V, evl10 as V10

lbl = sys.argv[1] if len(sys.argv) > 1 else "6.50 Ertrag"
target = sys.argv[2] if len(sys.argv) > 2 else "gft"
kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x60.VAR[lbl])
blks, info, mk = x60.setup(target, rule, extra)
yr_of_min = lambda t: int(str(np.datetime64(int(t), "m"))[:4])
rows = {}
S2 = {}
for s_, nm in enumerate(PB.F10):
    f = PB.fi(target, nm)
    exempt = set(x41.S70_OHNE.get("exempt", ()))
    keep, live, tp, w = PB.apply_rule(f, x41.S70_OHNE if nm not in exempt else dict(kind="none"))
    import streams as ST
    ST._use(target)
    te = f["t_entry"]; tx = f["t_exit"]
    sp = X.spread_at(target, f["sym"], te)
    hol = np.array([(int(a // 1440) not in X.FREI) and (int(b // 1440) not in X.FREI) for a, b in zip(te, tx)], bool)
    spr = f["rd"] >= X.MINSP * sp
    b = blks[s_]
    in2 = np.isin(te, b["t_entry"])
    for i in range(len(te)):
        if not keep[i]:
            continue
        y = yr_of_min(te[i])
        a = rows.setdefault((y, nm), np.zeros(8))
        a[0] += 1; a[1] += f["R"][i]
        if hol[i] and spr[i]:
            a[2] += 1; a[3] += f["R"][i]
            if not spr[i]:
                pass
        if in2[i]:
            a[4] += 1; a[5] += f["R"][i]
            S2[(s_, int(te[i]))] = f["R"][i]
        if not spr[i]:
            a[6] += 1; a[7] += f["R"][i]
# S3 aus dem Konto
V._MK = mk
mk.r21["reg"] = x48.r21_regime(target, mk)
GP = x60.fade_gp(gpx, frisk, per, extra_gp)
V.set_generic(blks, GP)
Pv = E.params(**dict(r6.SAFE, **kw))
yr_of = lambda d: int(str(np.datetime64(int(d), "D"))[:4])
traded = {}
cover = {}
nseed = 4
starts = V.starts(mk, 250, 4, V.WARM if target == "gft" else "2006-09-01", None if target == "gft" else "2021-12-31")
tdays = {}
for d in range(len(mk.days)):
    tdays[yr_of(mk.days[d])] = tdays.get(yr_of(mk.days[d]), 0) + 1
for (a, b) in starts:
    for d in range(a, min(b, len(mk.days) - 1)):
        y = yr_of(mk.days[d]); cover[y] = cover.get(y, 0) + nseed
    for seed in range(nseed):
        ms = V.masks(mk, seed, 0.08 if seed > 0 else 0.0)
        P2 = Pv.copy()
        if seed > 0:
            P2[E.PI["slip_frac"]] = 0.3
        r = E.run(mk, P2, a, b, seed=seed, masks=ms, GP=GP)
        for row in r["tr"]:
            sl = int(row[2])
            if sl < E.G0 or row[7] <= 0:
                continue
            s_ = (sl - E.G0) // 2
            tmin = int(row[3])
            v = S2.get((s_, tmin), S2.get((s_, tmin - 1440)))
            if v is None:
                continue
            y = yr_of(row[0])
            t = traded.setdefault((y, PB.F10[s_]), np.zeros(3))
            t[0] += 1; t[1] += v; t[2] += row[1] / row[7]
years = sorted({k[0] for k in rows if k[0] >= (2022 if target == "gft" else 2006)})
print(f"{target} {lbl}: Signale / Summe R je Kalenderjahr: S0 alle -> S1 Filter -> S2 Waechter -> S3 im Konto je Konto-Jahr (virt. R | Konto-R)")
for nm in PB.F10 + ["SUMME"]:
    cells = []
    for y in years:
        if nm == "SUMME":
            a = sum((rows.get((y, n), np.zeros(8)) for n in PB.F10), np.zeros(8))
            t = sum((traded.get((y, n), np.zeros(3)) for n in PB.F10), np.zeros(3))
        else:
            a = rows.get((y, nm), np.zeros(8)); t = traded.get((y, nm), np.zeros(3))
        kj = cover.get(y, 0) / max(tdays.get(y, 1), 1)
        t = t / max(kj, 1e-9)
        cells.append(f"{a[0]:3.0f}/{a[1]:+5.1f} {a[2]:3.0f}/{a[3]:+5.1f} {a[4]:3.0f}/{a[5]:+5.1f} {t[0]:4.1f}/{t[1]:+5.1f}|{t[2]:+5.1f} (Spr-Filter {a[6]:2.0f}/{a[7]:+5.1f})")
    print(f"{nm:7s} " + "   ".join(cells))
print("Jahre:", years)
