"""Build 6.60: Zukunftstest auf Daten, die keine Entscheidung seit 6.10 gesehen hat (Ordnerkopie mit mk_proxy2026.py:
NAS100 ab 2025 aus Dukascopy-Ticks, Gold bis 02.09.2026). Konten mit Start ab WARM60 (Vorgabe 2026-01-02), Laufzeit H Handelstage
(Vorgabe 100), jeder Handelstag ein neues Konto, 16 Stoerungen; zusaetzlich ein durchgehendes Konto ab 2025-01-02 je Kalenderjahr.
Aufruf: python x60f.py ["Variante|..."] [H] [WARM]   (Ausgabe ergebnisse/x60f.json im Arbeitsordner, Ordner per X60_OUT)"""
import numpy as np, sys, json, os, time
import x60, x48, r6
import eng10 as E, evl6 as V, evl10 as V10

which = sys.argv[1].split("|") if len(sys.argv) > 1 else ["6.40 Ertrag", "6.50 Ertrag"]
H = int(sys.argv[2]) if len(sys.argv) > 2 else 100
WARM = sys.argv[3] if len(sys.argv) > 3 else "2026-01-02"
fn = os.path.join(os.environ.get("X60_OUT", "ergebnisse"), "x60f.json")
res = json.load(open(fn)) if os.path.exists(fn) else {}
for lbl in which:
    key = f"{lbl} [H{H} ab {WARM}]"
    kw, gpx, frisk, rule, per, extra, extra_gp = x60.unpack(x60.VAR[lbl])
    blks, info, mk = x60.setup("gft", rule, extra)
    V._MK = mk
    mk.r21["reg"] = x48.r21_regime("gft", mk)
    GP = x60.fade_gp(gpx, frisk, per, extra_gp)
    V.set_generic(blks, GP)
    Pv = E.params(**dict(r6.SAFE, **kw))
    t = time.time()
    m = V10.evaluate(Pv, GP, horizons=(H,), step=1, seeds=tuple(range(16)), skip=0.08, warm=WARM, per_seed=True)
    # durchgehendes Konto ab 2025-01-02 (16 Stoerungen), je Kalenderjahr
    a = mk.day_index("2025-01-02"); b = len(mk.days) - 1
    cont = {}
    for seed in range(16):
        ms = V.masks(mk, seed, 0.08 if seed > 0 else 0.0)
        P2 = Pv.copy()
        if seed > 0:
            P2[E.PI["slip_frac"]] = 0.3
        r = E.run(mk, P2, a, b, seed=seed, masks=ms, GP=GP)
        for row in r["ev"]:
            y = str(np.datetime64(int(row[1]), "D"))[:4]
            c = cont.setdefault(y, [0, 0.0, 0])
            if row[0] == 1:
                c[0] += 1; c[1] += row[2]
            if row[0] == 3:
                c[2] += 1
    m["durchgehend"] = {y: dict(ausz=c[0] / 16, netto=(0.776 * c[1] - 148.5 * c[2]) / 16, busts=c[2] / 16) for y, c in cont.items()}
    res[key] = m
    json.dump(res, open(fn, "w"), indent=1, default=float)
    print(V10.line(f"{lbl}"[:40], m).split("| zuletzt")[0], f"| Boden min Ø {m['minbuf_mean']:.0f}$ <1% {100 * m['near100']:.1f}% "
          f"<2% {100 * m['near200']:.1f}% | n {m['n']:.0f} [{time.time() - t:.0f}s]", flush=True)
    s = m["streuung"]
    print(f"     Streuung: Ausz {s['mean'][0]:.2f} (SD {s['sd'][0]:.2f}) Netto {s['mean'][2]:.0f} (SD {s['sd'][2]:.0f})", flush=True)
    print("     durchgehendes Konto ab 02.01.2025: " + " | ".join(
        f"{y}: {c['ausz']:.1f} Ausz, {c['netto']:.0f} $, Busts {c['busts']:.2f}" for y, c in sorted(m["durchgehend"].items())), flush=True)
