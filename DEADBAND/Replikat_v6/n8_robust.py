"""Stufe 8: Robustheit - dieselben Varianten auf GFT 2022-25 (IS/OOS) und auf Fremddaten 2006-2021 (ext).
Aufruf: python n8_robust.py familie [...]  -> ergebnisse/n8_robust_<fam>.json, Liste der Varianten, die ueberall halten."""
import sys, json, numpy as np
import gsig as G, gext, cands as K, n8_scan as NS

def run_all(jobs, ds):
    if ds == "ext":
        G._D = gext.data_ext()
    else:
        G._D = None; G.data()
    K._CACHE.clear()
    out = {}
    for j in jobs:
        r = NS.run(*j)
        if r is not None:
            out[r["label"]] = r
    return out

if __name__ == "__main__":
    for fam in sys.argv[1:]:
        jobs = NS.FAMS[fam]()
        g = run_all(jobs, "gft"); e = run_all(jobs, "ext")
        rows = []
        for lbl, r in g.items():
            x = e.get(lbl)
            if x is None:
                continue
            ext = {k: v for k, v in x["IS"].items()}          # ext: alles vor 2024 = IS-Teil (2005-2021)
            rows.append(dict(label=lbl, IS=r["IS"], OOS=r["OOS"], F=r["F"], EXT=ext))
        json.dump(rows, open(f"ergebnisse/n8_robust_{fam}.json", "w"), default=float)
        good = [r for r in rows if r["IS"]["n"] >= 40 and r["IS"]["pf"] > 1.15 and r["OOS"]["pf"] > 1.15 and r["EXT"]["pf"] > 1.08 and r["EXT"]["n"] >= 150]
        good.sort(key=lambda r: -(min(r["IS"]["Ry"], r["OOS"]["Ry"]) + r["EXT"]["Ry"]))
        print(f"\n=== {fam}: {len(rows)} Varianten, ueberall positiv (IS/OOS PF>1.15, ext PF>1.08): {len(good)}")
        for r in good[:25]:
            a, b, c = r["IS"], r["OOS"], r["EXT"]
            print(f"{r['label']:<64s} IS PF{a['pf']:4.2f} R/J{a['Ry']:+5.1f} gü{a['vy']:4.0f} | OOS PF{b['pf']:4.2f} R/J{b['Ry']:+5.1f} | EXT n{c['n']:5d} PF{c['pf']:4.2f} R/J{c['Ry']:+5.1f} WR{c['wr']:3.0f}")
        sys.stdout.flush()
