"""Build 6.60: Regime-Fruehwarnung rueckwirkend. Wann haette der EA (RegimeWaechter) gemeldet?
  FRUEHWARNUNG      Fades live, PF der letzten 200 virtuellen Fade-Signale < Fruehwarn-PF (Vorgabe 1,25 wie der EA), hoechstens alle 7 Tage,
                    neu scharf erst nach PF >= Fruehwarn-PF + 0,05
  FADE-REGIME AUS   PF <= Abschalt-PF (FadePortPF 1,15): Fades nur noch virtuell
Gleiche Rechnung wie der Portfolio-Waechter (pg_guard.port_live_ea / FadePortfolioPF): Ergebnisse zaehlen ab dem Zeitpunkt, zu
dem der EA sie kennt, die letzten 200 innerhalb von 600 Tagen; ohne volle 200 keine Meldung. Fremddaten bis 2021, danach
GFT-Ersatz (in der 2026-Ordnerkopie bis 08/2026).
Aufruf: python a60_warn.py [Fruehwarn-PF] [Abschalt-PF]"""
import numpy as np, sys
import pg_guard as PGd, pg_blocks as PB, x41

WARN = float(sys.argv[1]) if len(sys.argv) > 1 else 1.25
TH = float(sys.argv[2]) if len(sys.argv) > 2 else 1.15
N, WIN, DAY = 200, 600, 1440

rule = x41.S70_OHNE
exempt = set(rule.get("exempt", ()))
kt_l, te_l, R_l, mi_l = [], [], [], []
for i, nm in enumerate(PB.F10):
    fk = {}
    for ds in ("ext", "gft"):
        f = PB.fi(ds, nm)
        keep, live, tp, w = PB.apply_rule(f, rule if nm not in exempt else dict(kind="none"))
        fk[ds] = (f, keep)
    (f1, k1), (f2, k2) = fk["ext"], fk["gft"]
    v1 = (f1["t_entry"] < PGd.LIM22) & k1
    kt_l.append(np.r_[PGd.known_time("ext", f1)[v1], PGd.known_time("gft", f2)[k2]])
    te_l.append(np.r_[f1["t_entry"][v1], f2["t_entry"][k2]])
    R_l.append(np.r_[f1["R"][v1], f2["R"][k2]]); mi_l.append(np.full(int(v1.sum() + k2.sum()), i))
kt = np.concatenate(kt_l).astype(np.int64); te = np.concatenate(te_l).astype(np.int64)
R = np.concatenate(R_l); mi = np.concatenate(mi_l)
o = np.lexsort((mi, kt)); kt = kt[o]; R = R[o]; te = te[o]


def d(t):
    return str(np.datetime64(int(t), "m"))[:10]


# Zustand nach jedem neuen Ergebnis (mehrere Ergebnisse mit gleichem Zeitpunkt zusammen)
ev = []                    # (Zeit, Art, PF)  Art: W = Fruehwarnung (erste der Episode), w = Wiederholung, A = AUS, L = WIEDER LIVE
meld, warn_t, episode = -1, 0, None
episodes = []              # [Beginn, Ende, endete mit AUS?]
last_pf = []
j = 0
while j < len(kt):
    k = j
    while k + 1 < len(kt) and kt[k + 1] == kt[j]:
        k += 1
    now = kt[k] + 5        # Pruefung nach dem Verbuchen (EA: spaetestens 5 Minuten spaeter)
    j = k + 1
    if k + 1 < N or kt[k + 1 - N] < now - WIN * DAY:
        continue
    w = R[k + 1 - N:k + 1]
    pos = w[w > 0].sum(); neg = -w[w < 0].sum()
    pf = pos / neg if neg > 0 else 9.9
    last_pf.append((now, pf))
    live = 1 if pf > TH else 0
    warn_zone = WARN > TH and live == 1 and pf < WARN
    warn_before = warn_t
    if meld >= 0 and live != meld:
        if live == 1:                                    # EA: Vorwarnung steckt in der WIEDER-LIVE-Meldung (ein Push)
            ev.append((now, "L+W" if warn_zone else "L", pf))
            if warn_zone:
                if episode is None:
                    episode = now
                warn_t = now
        else:
            ev.append((now, "A", pf))
            if episode is not None:
                episodes.append([episode, now, True]); episode = None
    meld = live
    if warn_zone and warn_t == warn_before and (warn_t == 0 or now - warn_t >= 7 * DAY):
        ev.append((now, "W" if warn_t == 0 else "w", pf))
        if warn_t == 0 and episode is None:
            episode = now
        warn_t = now
    if warn_t > 0 and pf >= WARN + 0.05:
        warn_t = 0
        if episode is not None:
            episodes.append([episode, now, False]); episode = None
if episode is not None:
    episodes.append([episode, None, False])

print(f"Fruehwarnung PF < {WARN:.2f}, Abschaltung PF <= {TH:.2f} (letzte {N} Signale, {WIN} Tage)")
LOG = []
print("Meldungen (W = Fruehwarnung, A = Fade-Regime AUS, L = wieder live, L+W = wieder live mit Vorwarnung; Wiederholungen nicht gelistet):")
for t, a, pf in ev:
    if a != "w":
        print(f"  {d(t)} {a} PF {pf:.2f}")
print("Warn-Episoden (Beginn -> Ende, mit/ohne Abschaltung, Vorlauf in Tagen, virtuelles R der Fades bis zum Ende):")
for b, e, aus in episodes:
    if e is None:
        print(f"  {d(b)} -> (offen)")
        continue
    s = (te >= b) & (te < e)
    print(f"  {d(b)} -> {d(e)}  {'AUS' if aus else 'erholt'}  {(e - b) / DAY:5.0f} Tage  Fades {s.sum():3d} Signale {R[s].sum():+6.1f} R")
PER = (("2006-13", "2006-01-01", "2014-01-01"), ("2014-21", "2014-01-01", "2022-01-01"), ("2022-25", "2022-01-01", "2026-01-01"),
       ("2026", "2026-01-01", "2027-01-01"))
tt = np.array([t for t, _ in last_pf]); pp = np.array([p for _, p in last_pf])
for nm, a, b in PER:
    a_, b_ = np.datetime64(a, "m").astype(np.int64), np.datetime64(b, "m").astype(np.int64)
    s = (tt >= a_) & (tt < b_)
    if not s.any():
        continue
    e_ = [x for x in ev if a_ <= x[0] < b_]
    ep = [x for x in episodes if a_ <= x[0] < b_]
    print(f"{nm}: PF Median {np.median(pp[s]):.2f} (p10 {np.percentile(pp[s], 10):.2f}), Anteil live {100 * (pp[s] > TH).mean():.0f} %, "
          f"im Warnbereich {100 * ((pp[s] > TH) & (pp[s] < WARN)).mean():.0f} % | Warn-Episoden {len(ep)} "
          f"(davon mit Abschaltung {sum(1 for x in ep if x[2])}) | Abschaltungen {sum(1 for x in e_ if x[1] == 'A')}, "
          f"ohne Warnung vorher {sum(1 for x in e_ if x[1] == 'A' and not any(p[2] and p[1] == x[0] for p in episodes))}")
