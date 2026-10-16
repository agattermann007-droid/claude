"""DEADBAND V9 - setzt die Ergebnistabellen aus den Rechenergebnissen (tests9/kosten9/muster9/tw_check JSON) in den
Berichtsentwurf ein (Platzhalter @@VARIANTEN@@, @@KOSTEN@@, @@STRESS@@, @@MODULE@@). Keine Zahl wird von Hand abgeschrieben.
Aufruf: python3 bericht_tabelle.py <entwurf.md> <DEADBAND_V9_Bericht.md (neu)> [datensatz]
"""
import json, os, sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HIER), "replikat"))
import auswertung9 as AW, daten9 as DA, regime9 as RG

INHALT = {"BASIS": "8.10 unveraendert", "Z_06": "Fade-Ziel mindestens 0,6 R", "Z_GS": "Fade-Ziel Gegenseite",
          "Z_HH": "halb an der Mitte, Rest bis Gegenseite mit Einstand", "LW_940": "LW erst ab 9:40 NY",
          "NS_R3": "NAS-Short-Fades nur im Abwaertsregime (R3)", "SM_L": "Schluss-Momentum 15:30-15:55 nur Long",
          "SM_B": "Schluss-Momentum 15:30-15:55 beide Richtungen", "CPPI": "CPPI: Groesse linear zum Puffer, voll ab 6 %"}
INHALT = {k: v.replace("ae", "ä").replace("ue", "ü").replace("oe", "ö").replace("Groesse", "Größe") for k, v in INHALT.items()}


def de(x, nk=0, vz=False):
    s = f"{x:+,.{nk}f}" if vz else f"{x:,.{nk}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


def inhalt(n, v):
    if n in INHALT:
        return INHALT[n]
    r = "+".join(v["v"]["regeln"])
    return {"S_": f"Sperre NAS-Long+S0830 bei {r}", "H_": f"halbes Risiko NAS-Long+S0830 bei {r}",
            "K_": f"Sperre NAS-Long+S0830 bei {r}", "G_": f"Sperre Gold-Short bei {r} (aufwärts)"}[n[:2]]


def varianten(res):
    P = AW.pruefe(res)
    b = res["BASIS"]["konto"]
    z = ["| Variante | Inhalt | A 1 J | A 2 J | B 1 J | B 2 J | R1 | R2: Summe R gesperrt A / B | R3: Jahre + |",
         "|---|---|---:|---:|---:|---:|:-:|---|:-:|"]
    z.append("| **BASIS** | 8.10 = V9 | " + " | ".join(f"**{de(b[f]['net'])} $** ({de(b[f]['pay'], 2)})" for f in ("A1J", "A2J", "B1J", "B2J"))
             + " | – | – | – |")
    for n, v in res.items():
        if n == "BASIS":
            continue
        p = P[n]
        d = " | ".join(de(p["dnet"][f], 0, True) for f in ("A1J", "A2J", "B1J", "B2J"))
        if p["r2"] is None:
            r2 = "–"
        else:
            a = p["sR"].get("A", [0.0, 0]); bb = p["sR"].get("B", [0.0, 0])
            r2 = f"{de(a[0], 1, True)} ({a[1]}) / {de(bb[0], 1, True)} ({bb[1]}) {'ja' if p['r2'] else 'nein'}"
        z.append(f"| {n} | {inhalt(n, v)} | {d} | {'ja' if p['r1'] else 'nein'} | {r2} | {p['npos']}/{p['nj']} {'ja' if p['r3'] else 'nein'} |")
    return "\n".join(z)


def kosten(k):
    z = ["| Variante | Spread ×1,5: A 1 J | Spread ×1,5: B 1 J | Spread ×2: A 1 J | Spread ×2: B 1 J | besteht |",
         "|---|---:|---:|---:|---:|:-:|"]
    namen = sorted({x.split("@")[0] for x in k["res"]}, key=lambda s: (s != "BASIS", s))
    for n in namen:
        c = []
        for mu in ("1.5", "2"):
            for f in ("A1J", "B1J"):
                g = k["res"][f"{n}@{mu}"][f]
                c.append(f"{de(g['net'])} $ ({de(g['pay'], 2)})")
        z.append(f"| {n} | " + " | ".join(c) + f" | {'–' if n == 'BASIS' else ('ja' if k['ok'][n] else 'nein')} |")
    return "\n".join(z)


def stress(m):
    regs = list(RG.REGELN) + ["NA", "TR"]
    z = ["| Fenster | Live-Trades | Summe R | gesperrt hätten (Trades / Summe R) |", "|---|---:|---:|---|"]
    for k, v in m["stress"].items():
        g = ", ".join(f"{r} {v[r][0]}/{de(v[r][1], 1, True)}" for r in regs if v[r][0]) or "–"
        z.append(f"| {k} | {v['n']} | {de(v['R'], 1, True)} | {g} |")
    return "\n".join(z)


def module(m):
    z = ["| Modul | A: n | A: Summe R | B: n | B: Trefferquote | B: PF | B: Summe R | Ziel-Median (R) |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    namen = []
    for k in m["module"]:
        n = k.rsplit(" ", 1)[0]
        if n not in namen:
            namen.append(n)
    for n in namen:
        a = m["module"].get(f"{n} A", {}); b = m["module"].get(f"{n} B", {})
        if not b.get("n"):
            continue
        zr = b.get("ziel_R")
        z.append(f"| {n} | {a.get('n', 0)} | {de(a.get('sumR', 0.0), 1, True)} | {b['n']} | {de(100 * b['wr'], 0)} % | "
                 f"{de(b['pf'], 2) if b['pf'] else '–'} | {de(b['sumR'], 1, True)} | {de(zr, 2) if zr == zr and zr is not None else '–'} |")
    return "\n".join(z)


def main(entwurf, ziel, name="frei"):
    assert not os.path.exists(ziel), f"{ziel} existiert schon"
    S = DA.SCRATCH
    res = json.load(open(os.path.join(S, f"tests9_{name}.json")))
    k = json.load(open(os.path.join(S, f"kosten9_{name}.json")))
    m = json.load(open(os.path.join(S, f"muster9_{name}.json")))
    t = open(entwurf, encoding="utf-8").read()
    for ph, txt in (("@@VARIANTEN@@", varianten(res)), ("@@KOSTEN@@", kosten(k)), ("@@STRESS@@", stress(m)), ("@@MODULE@@", module(m))):
        assert t.count(ph) == 1, ph
        t = t.replace(ph, txt)
    assert "@@" not in t
    open(ziel, "x", encoding="utf-8").write(t)
    print(ziel, len(t.splitlines()), "Zeilen")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "frei")
