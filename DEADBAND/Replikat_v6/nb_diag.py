"""Build 6.40: Beinahe-Busts im Detail - kleinster Abstand zum Boden je Konto (Motor, schlechtester Kurs) und Monat des
tiefsten realisierten Stands (Trades + Auszahlungen), je Stoerung. Zeigt, dass die Konten < 100 $ mit Portfolio-Waechter
aus der Episode Februar/Maerz 2025 und aus einzelnen Stoerungen stammen (Bericht 6.40, Abschnitt 3.4).
Aufruf (im jeweiligen Replikat-Ordner, auch in der Kopie mit GFT-nahen Spreads):
python nb_diag.py gft "6.40 Ertrag" 16 1 aus.json   (Variante aus x44.VAR; aus.json = je Konto h, s, a, minbuf, rday)"""
import sys, os, numpy as np, json
sys.path.insert(0, os.getcwd())
from concurrent.futures import ProcessPoolExecutor
import x44, eng8 as E, evl6 as V6, evl8 as V8

def job(args):
    Pv, d0, d1, seed, skip, slip, GP = args
    m = V6.mk()
    Pv = Pv.copy()
    if seed > 0:
        Pv[E.PI["slip_frac"]] = slip
    ms = V6.masks(m, seed, skip if seed > 0 else 0.0)
    rr = E.run(m, Pv, d0, d1, seed=seed, masks=ms, GP=GP)
    st = rr["st"]; tr = rr["tr"]; ev = rr["ev"]
    minbuf = float(st[E.SI["minbuf"]])
    # realisierter Pfad: Trades (Schlusstag, Ergebnis) und Auszahlungen (Tag, Betrag)
    items = [(float(r[0]), 0, float(r[1]), int(r[2])) for r in tr]
    items += [(float(e[1]), 1, float(e[2]), -1) for e in ev if int(e[0]) in (1, 3)]
    items.sort(key=lambda x: (x[0], x[1]))
    bal = 10000.0; peak = 10000.0; best = 1e9; bday = -1; slots = {}
    for d, typ, v, sl in items:
        if typ == 1:
            bal = 10000.0 if v == 0 else bal - v; peak = bal
            continue
        bal += v
        peak = max(peak, bal)
        b = bal - (peak - 600.0)
        if b < best:
            best = b; bday = d
    return dict(minbuf=minbuf, rbest=best, rday=bday, d0=float(m.days[d0]))

def run(target, name, seeds, step):
    v = x44.VAR[name]; kw, gpx = v[0], v[1]; frisk = v[2] if len(v) > 2 else 0.75; rule = v[3] if len(v) > 3 else "S70"
    blks, info, mk = x44.setup(target, rule)
    x44.V._MK = mk
    GP = x44.fade_gp(gpx, frisk)
    x44.V.set_generic(blks, GP)
    Pv = E.params(**dict(x44.r6.SAFE, **kw))
    m = V6.mk()
    jobs = []; tags = []
    for h in (250, 500, 750):
        for (a, b) in V6.starts(m, h, step, V6.WARM, None):
            for s in range(seeds):
                jobs.append((Pv, a, b, s, 0.08, 0.3, GP)); tags.append((h, s, a))
    with ProcessPoolExecutor(4) as ex:
        outs = list(ex.map(job, jobs, chunksize=32))
    return tags, outs

if __name__ == "__main__":
    target, name, seeds, step, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    tags, outs = run(target, name, seeds, step)
    rows = [dict(h=h, s=s, a=a, **o) for (h, s, a), o in zip(tags, outs)]
    json.dump(rows, open(out, "w"))
    mb = np.array([r["minbuf"] for r in rows])
    print(name, "Konten", len(rows), "minbuf Ø", mb.mean().round(1), "<100", (mb < 100).mean().round(4), "<200", (mb < 200).mean().round(4))
    near = [r for r in rows if r["minbuf"] < 100]
    import collections
    c = collections.Counter(str(np.datetime64(int(r["rday"]), "D"))[:7] for r in near)
    print("Monat des tiefsten realisierten Stands (Konten < 100 $):", sorted(c.items()))
    c2 = collections.Counter(str(np.datetime64(int(r["rday"]), "D"))[:7] for r in rows if r["minbuf"] < 200)
    print("... Konten < 200 $:", sorted(c2.items()))
    print("je Stoerung: kleinster Abstand / Anteil < 200 $ / < 100 $")
    for s_ in range(seeds):
        mb = np.array([r["minbuf"] for r in rows if r["s"] == s_])
        print(f"  s{s_}: {mb.min():4.0f} $ {100 * (mb < 200).mean():5.1f} % {100 * (mb < 100).mean():5.1f} %")
