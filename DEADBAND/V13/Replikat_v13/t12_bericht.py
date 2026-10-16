"""v12: Tabellen fuer den Bericht aus ergebnisse/t12_final.json/.log und base_v10_32.pkl/v12_32.pkl erzeugen und die
Platzhalter {{TAB_KURZ}}, {{TAB_FENSTER}}, {{TAB_JAHRE}}, {{SCHLUPF}} in der Berichtsdatei ersetzen.
Aufruf: python t12_bericht.py BERICHT.md"""
import json, pickle, re, sys
import numpy as np

F = json.load(open("ergebnisse/t12_final.json"))
base = pickle.load(open("ergebnisse/base_v10_32.pkl", "rb"))
v12 = pickle.load(open("ergebnisse/v12_32.pkl", "rb"))
NAME = {"Auswahl 2022": "2022 (Auswahl)", "2023": "2023", "Pruef 2024-25": "2024–25", "Pruef 2017-20": "2017–20",
        "Pruef 2011-15": "2011–15 (neu)"}


def de(x, nd=2, sign=False):
    s = f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"
    return s.replace(".", ",")


def tsd(x, sign=False):
    s = f"{abs(x):,.0f}".replace(",", ".")
    if sign:
        return ("+" if x >= 0 else "−") + s
    return ("−" if x < 0 else "") + s


rows = []
for w, nm in NAME.items():
    b, v = base[w], v12[w]
    d = v - b
    n = len(d)
    se = d.std(axis=0, ddof=1) / np.sqrt(n)
    rows.append(f"| {nm} | {de(b[:,0].mean())} | {de(v[:,0].mean())} | {de(d[:,0].mean(), sign=True)} ± {de(se[0])} | "
                f"{tsd(b[:,1].mean())} | {tsd(v[:,1].mean())} | {tsd(d[:,1].mean(), sign=True)} ± {tsd(se[1])} | "
                f"{int(b[:,2].sum())} → {int(v[:,2].sum())} |")
TAB_KURZ = "\n".join(rows)


def tab(keys, src, label):
    out = [f"| {label} | Ausz./J V11 → V12 | $/J V11 → V12 | $/J inkl. offen | Ø Auszahlung | 1. Ausz. (Median, Tage) | ohne Ausz. | Busts |",
           "|---|---|---|---|---|---|---|---|"]
    for k, nm in keys:
        a, b = src["V10"].get(k), src["V12"].get(k)
        if a is None or b is None:
            continue
        out.append(f"| {nm} | {de(a['pay'])} → {de(b['pay'])} | {tsd(a['net'])} → {tsd(b['net'])} | "
                   f"{tsd(a['net_open'])} → {tsd(b['net_open'])} | {tsd(a['avg'])} → {tsd(b['avg'])} $ | "
                   f"{a['first']:.0f} → {b['first']:.0f} | {de(100*a['zero'],1)} → {de(100*b['zero'],1)} % | "
                   f"{a['bust']} → {b['bust']} |")
    return "\n".join(out)


TAB_FENSTER = tab(list(NAME.items()), F, "Fenster")
years = sorted(F["V10"]["jahre"].keys())
TAB_JAHRE = tab([(y, y + ("*" if y == "2025" else "")) for y in years],
                {"V10": F["V10"]["jahre"], "V12": F["V12"]["jahre"]}, "Start") + \
    "\n\n\\* 2025: nur 6 Starts (NAS-Daten enden 13.02.2026)."

log = open("ergebnisse/t12_final.log").read()
sl = [ln for ln in log.splitlines() if "ohne Schlupf" in ln]
SCHLUPF = "```\n" + "\n".join(sl) + "\n```\n(Format: Fenster Ausz./J (Differenz ± SE) $/J (Differenz ± SE) Busts)"

path = sys.argv[1]
s = open(path, encoding="utf-8").read()
for k, v in (("{{TAB_KURZ}}", TAB_KURZ), ("{{TAB_FENSTER}}", TAB_FENSTER), ("{{TAB_JAHRE}}", TAB_JAHRE),
             ("{{SCHLUPF}}", SCHLUPF)):
    if s.count(k) != 1:
        raise SystemExit(f"Platzhalter {k} {s.count(k)}-mal")
    s = s.replace(k, v)
open(path, "w", encoding="utf-8").write(s)
print(TAB_KURZ); print(TAB_FENSTER); print(TAB_JAHRE); print(SCHLUPF)
