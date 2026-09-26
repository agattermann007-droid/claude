"""Build 6.70 (mehr Netto, mehr Auszahlungen, weniger Verlustserien): Konto-Screening mit eng11/evl11. Basis = 6.60 (x60 "6.60b").
Prueft jede Variante nach dem vorab festgelegten Protokoll (PROTOKOLL_670.md): beide Spread-Lagen, Startjahre einzeln
(Walk-Forward: Auswahl mit Start 2022-23, Pruefung mit Start 2024-25), Stoerungen paarweise gegen die Basis, Fremddaten 2006-21.

Aufruf: python x70.py gft|ext ["Variante|..."|all] [Stoerungen] [Schritt] [Ausgabedatei]
Ergebnisse: ergebnisse/x70_{gft|ext}.json (Schluessel "Variante [Stoerungen sSchritt]"), Ordner per X70_OUT.
ABSCHLAG=0.2: Stresstest (20 % der Fade-Gewinner entfernt, wie x61) -> ..._abschlag20.json"""
import numpy as np, sys, json, os, time
import x60, x61, x48, x44, x40, r6
import eng11 as E, evl6 as V, evl11 as V11                    # evl11 zuletzt: evl6 rechnet mit eng11

H = dict(harv=1)
E660, FREI2 = x60.E660, x60.FREI2
_ex = x60._ex


def fade_gp(gpx, risk=0.75, per=None, extra=()):
    out = []
    for i, _ in enumerate(x40.F10):
        kw = dict(on=1, risk=risk, maxtrades=1, **gpx)
        if per and i in per:
            kw.update(per[i])
        out.append(kw)
    for kw in extra:
        out.append(dict(kw))
    return E.gparams(out)


def v660(kw=None, gpx=None, frisk=0.75):
    """Variante auf Basis 6.60: Konto-Zusatz kw, Fade-GP-Zusatz gpx."""
    return (dict(E660, **(kw or {})), dict(H, **(gpx or {})), frisk, "P200/1.15", _ex(FREI2), None)


VAR = {"6.60": v660()}
# Z1: Ziel fuer den gueltigen Tag mit Gewinnsicherung (Sicherung ext_lock x Zielweite, neues Ziel hoechstens ext_max R)
for _lk in (0.3, 0.5, 0.7):
    for _mx in (0.8, 1.0, 1.2):
        VAR[f"Z1 L{_lk} M{_mx}"] = v660(dict(ext_on=1, ext_lock=_lk, ext_max=_mx))
# Z2: Tagessperre der Fades je Symbol nach N Fade-Verlusten
for _n in (1, 2):
    VAR[f"Z2 Sperre {_n}"] = v660(dict(fsym_block=_n))
# Z3: Fade-Einstand (Stop auf Einstieg + 0,05 R ab X R, ohne Teilgewinn)
for _b in (0.5, 0.6, 0.75):
    VAR[f"Z3 BE{_b}"] = v660(gpx=dict(tp1r=_b, tp1f=0.0, be=0.05))
# Z4: Serien-Stopp schon nach 2 Verlusten in Folge
VAR["Z4 Serie 2"] = v660(dict(cool_n=2))
# Z5: Tages-Einstiegsstopp - keine neuen Einstiege, sobald die Equity X % vom Startsaldo unter dem Tagesstart liegt
for _x in (0.5, 0.75, 1.0):
    VAR[f"Z5 Tagesstopp {_x}"] = v660(dict(day_entry_stop=_x))
# Z6: Noise-Tagespause nach N Noise-Teilen mit Verlust
for _n in (1, 2):
    VAR[f"Z6 Noise-Pause {_n}"] = v660(dict(nz_maxloss=_n))

SEED0 = int(os.environ.get("X70_SEED0", "0"))
ABSCHLAG = float(os.environ.get("ABSCHLAG", "0"))


def evaluate(target, kw, gpx, seeds=8, step=2, per_seed=False, by_year=False, fade_risk=0.75, rule="P200/1.15", per=None,
             extra_key=None, extra_gp=(), skip_gft=0.08):
    blks, info, mk = x60.setup(target, rule, extra_key)
    V._MK = mk
    mk.r21["reg"] = x48.r21_regime(target, mk)
    GP = fade_gp(gpx, fade_risk, per, extra_gp)
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    sd = tuple(range(SEED0, SEED0 + seeds))
    if target == "ext":
        m = V11.evaluate(Pv, GP, step=step, seeds=sd, skip=0.03, warm="2006-09-01", end="2021-12-31",
                         per_seed=per_seed, by_year=by_year)
    else:
        m = V11.evaluate(Pv, GP, step=step, seeds=sd, skip=skip_gft, per_seed=per_seed, by_year=by_year)
    m["fade_live"] = sum(x[2] for x in info)
    return m


def run(target, names, seeds, step, fn=None, var=None, per_seed=True, by_year=True):
    var = var or VAR
    suf = f"_abschlag{int(round(100 * ABSCHLAG))}" if ABSCHLAG > 0 else ""
    fn = fn or os.path.join(os.environ.get("X70_OUT", "ergebnisse"), f"x70_{target}{suf}.json")
    res = json.load(open(fn)) if os.path.exists(fn) else {}
    if ABSCHLAG > 0:
        x61.abschlag(ABSCHLAG)
    for lbl in names:
        kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(var[lbl])
        key = f"{lbl} [{seeds} s{step}]" + (f" ab{SEED0}" if SEED0 else "")
        if key in res:
            print(V11.line(f"{target} {lbl}"[:40], res[key]), "(Cache)", flush=True)
            continue
        t = time.time()
        m = evaluate(target, kw, gpx, seeds, step, per_seed=per_seed, by_year=by_year, fade_risk=frisk, rule=rule, per=per,
                     extra_key=extra, extra_gp=extra_gp)
        m["variante"] = lbl
        res[key] = m
        json.dump(res, open(fn, "w"), indent=1, default=float)
        print(V11.line(f"{target} {lbl}"[:40], m), f"| S5 {m['s5']:.2f} ext {m.get('x_ext_n', 0):.1f}/{m.get('x_ext_hit', 0):.1f} "
              f"blk {m.get('x_fsym_blk', 0):.1f}/{m.get('x_nz_blk', 0):.1f} [{time.time() - t:.0f}s]", flush=True)
        if by_year and "jahre" in m:
            print("     " + " | ".join(f"{y}: {a['pay']:.2f} ({365.25 / max(a['pay'], 1e-9):.1f} T) {a['net']:.0f}$ S6 {a['s6']:.2f}"
                                       for y, a in m["jahre"].items()), flush=True)
    return res


if __name__ == "__main__":
    target = sys.argv[1]
    which = sys.argv[2] if len(sys.argv) > 2 else "all"
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    step = int(sys.argv[4]) if len(sys.argv) > 4 else (2 if target == "gft" else 6)
    fn = sys.argv[5] if len(sys.argv) > 5 else None
    names = list(VAR) if which == "all" else which.split("|")
    run(target, names, seeds, step, fn)
