"""DEADBAND V9 - Uebernahmeregeln auf die Ergebnisse von tests9.py anwenden (Regeln 1-3), Kandidaten fuer den Kosten-Stress.

Regel 1: A und B, 1 und 2 Jahre: Netto/J hoeher und Busts/J nicht hoeher als BASIS
Regel 2: Sperr-/Halb-Varianten: Summe R der betroffenen Live-Trades < 0 in A und B (beide Symbole zusammen)
Regel 3: Netto-Differenz je Startjahr (1-Jahres-Konten, A und B) positiv in mindestens 5/7 der Startjahre
Regel 4 (Kosten-Stress) rechnet kosten9.py fuer die Kandidaten.
"""
import json, math, os, sys
import daten9 as DA


def pruefe(res):
    b = res["BASIS"]["konto"]
    out = {}
    for name, r in res.items():
        if name == "BASIS":
            continue
        k = r["konto"]
        r1 = all(k[f]["net"] > b[f]["net"] and k[f]["bust"] <= b[f]["bust"] + 1e-12 for f in ("A1J", "A2J", "B1J", "B2J"))
        art = r["v"]["art"]
        sR = {}
        for key, (R, n) in r["signal"].items():
            w = key.split("_")[0]
            a = sR.setdefault(w, [0.0, 0]); a[0] += R; a[1] += n
        if art in ("sperre", "halb"):
            r2 = all(sR.get(w, [0.0, 0])[0] < 0 for w in ("A", "B"))
        else:
            r2 = None
        diffs = {}
        for f in ("A1J", "B1J"):
            for y, j in k[f]["jahre"].items():
                if y in b[f]["jahre"] and j["n"] >= 5:
                    diffs[y] = j["net"] - b[f]["jahre"][y]["net"]
        npos = sum(d > 0 for d in diffs.values())
        need = math.ceil(5 / 7 * len(diffs))
        r3 = npos >= need
        out[name] = dict(r1=r1, r2=r2, r3=r3, npos=npos, nj=len(diffs), need=need, sR=sR, diffs=diffs,
                         dnet={f: k[f]["net"] - b[f]["net"] for f in ("A1J", "A2J", "B1J", "B2J")},
                         dbust={f: k[f]["bust"] - b[f]["bust"] for f in ("A1J", "A2J", "B1J", "B2J")},
                         kandidat=r1 and (r2 is None or r2) and r3)
    return out


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "frei"
    res = json.load(open(os.path.join(DA.SCRATCH, f"tests9_{name}.json")))
    P = pruefe(res)
    for n, p in P.items():
        sr = " ".join(f"{w}:{v[0]:+.1f}R/{v[1]}" for w, v in sorted(p["sR"].items()))
        dn = " ".join(f"{f}:{v:+5.0f}" for f, v in p["dnet"].items())
        print(f"{n:10s} R1 {'ja ' if p['r1'] else 'nein'} R2 {'-  ' if p['r2'] is None else ('ja ' if p['r2'] else 'nein')} "
              f"R3 {'ja ' if p['r3'] else 'nein'} ({p['npos']}/{p['nj']}, noetig {p['need']}) | dNetto {dn} | {sr} {'<= KANDIDAT' if p['kandidat'] else ''}")
