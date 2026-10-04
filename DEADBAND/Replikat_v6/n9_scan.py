"""Stufe 8.10: Raster der neuen Kandidaten (Signalebene) mit Auswahl 2022-23, Pruefung 2024-25 (Gold 2026) und
Fremddaten 2005-21 - gleiche Messung wie n8_scan/n8_robust. Aufruf: python n9_scan.py lastmom fix"""
import sys, json
import n8_scan as NS, n8_robust as NR, n8sig as N, n9sig as N9


def fam_lastmom():
    out = []
    for sym in ("NAS", "XAU"):
        for t1, xm in ((840, 955), (900, 955), (930, 955), (930, 960)):
            for g in NS.grid(refmode=(0, 1), thr=(0.0, 0.25, 0.5, 0.75), rev=(0, 1), stopk=(0.15, 0.3), tpr=(0.0, 1.0), dirs=(0, 1)):
                args = (t1, xm, g["refmode"], g["thr"], g["rev"], g["stopk"], g["tpr"], g["dirs"], 960)
                out.append((sym, N9.gen_lastmom, args, f"LM {sym} {t1}-{xm} ref{g['refmode']} thr{g['thr']} rev{g['rev']} s{g['stopk']} t{g['tpr']} d{g['dirs']}"))
    return out


def fam_fix():
    """Gold vor/um den London-PM-Fix (15:00 London = 10:00 NY): Short von t_in bis t_out; zur Kontrolle auch Long."""
    out = []
    for t_in, t_out in ((540, 605), (570, 605), (570, 620), (585, 620), (570, 660), (480, 605), (600, 720)):
        for g in NS.grid(d0=(-1, 1), stopk=(0.15, 0.3, 0.5), tpr=(0.0, 1.0), trend=(0, 288)):
            args = (t_in, t_out, g["d0"], g["stopk"], g["tpr"], g["trend"], 0b111110)
            out.append(("XAU", N.gen_hold, args, f"FIX XAU {t_in}-{t_out} d{g['d0']} s{g['stopk']} t{g['tpr']} tr{g['trend']}"))
    return out


NS.FAMS.update(lastmom=fam_lastmom, fix=fam_fix)

if __name__ == "__main__":
    for fam in sys.argv[1:]:
        jobs = NS.FAMS[fam]()
        g = NR.run_all(jobs, "gft"); e = NR.run_all(jobs, "ext")
        rows = []
        for lbl, r in g.items():
            x = e.get(lbl)
            if x is None:
                continue
            rows.append(dict(label=lbl, IS=r["IS"], OOS=r["OOS"], F=r["F"], EXT=x["IS"]))
        json.dump(rows, open(f"ergebnisse/n9_robust_{fam}.json", "w"), default=float)
        good = [r for r in rows if r["IS"]["n"] >= 40 and r["IS"]["pf"] > 1.15 and r["OOS"]["pf"] > 1.15 and r["EXT"]["pf"] > 1.08 and r["EXT"]["n"] >= 150]
        good.sort(key=lambda r: -(min(r["IS"]["Ry"], r["OOS"]["Ry"]) + r["EXT"]["Ry"]))
        print(f"\n=== {fam}: {len(rows)} Varianten, ueberall positiv (IS/OOS PF>1.15, ext PF>1.08): {len(good)}")
        for r in good[:25]:
            a, b, c = r["IS"], r["OOS"], r["EXT"]
            print(f"{r['label']:<62s} IS n{a['n']:4d} PF{a['pf']:4.2f} R/J{a['Ry']:+5.1f} gü{a['vy']:4.0f} | OOS PF{b['pf']:4.2f} R/J{b['Ry']:+5.1f} | EXT n{c['n']:5d} PF{c['pf']:4.2f} R/J{c['Ry']:+5.1f} WR{c['wr']:3.0f}")
        best = sorted([r for r in rows if r["IS"]["n"] >= 40], key=lambda r: -r["IS"]["Ry"])[:8]
        print("-- Top 8 nach IS R/J (Auswahl nur IS):")
        for r in best:
            a, b, c = r["IS"], r["OOS"], r["EXT"]
            print(f"{r['label']:<62s} IS PF{a['pf']:4.2f} R/J{a['Ry']:+5.1f} | OOS PF{b['pf']:4.2f} R/J{b['Ry']:+5.1f} | EXT PF{c['pf']:4.2f} R/J{c['Ry']:+5.1f}")
        sys.stdout.flush()
