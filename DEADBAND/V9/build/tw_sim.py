"""DEADBAND V9 - den GESAMTEN neuen MQL5-Block (tw_block.mq5) im C++-Geruest uebersetzen und die Oktober-Tage durchspielen.

tw_alles.inc = Globale + alle TW-Funktionen, mechanisch uebersetzt (Array-Parameter/-Variablen -> std::vector, sonst nichts).
MQL-Funktionen (CopyRates, PrintFormat, TimeCurrent, ...) sind in tw_sim.cpp nachgebildet.
Kurse: Replikat (freie Daten). NAS-D1 ab 26.09.2026 aus NQ-Futures (oct9.nas_d1_ergaenzt); NAS-M5 fehlt ab 26.09.2026.
Ereignisse: je Servertag 01.-16.10.2026 ein Durchlauf um 00:01 Server, dazu die 16 Fade-artigen Live-Trades (ohne Noise).
Ausgabe: Journalzeilen, wie V9 sie geschrieben haette -> SCRATCH/tw_sim_oktober.txt
"""
import os, re, subprocess, sys
import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HIER), "replikat"))
import aufbau9 as AU, daten9 as DA, oct9 as OC, check_live9 as CL

ARBEIT = os.path.join(DA.SCRATCH, "tw_check")
SYM = {"XAU": "XAUUSD.x", "NAS": "NAS100.x"}


def uebersetzen():
    src = open(os.path.join(HIER, "tw_block.mq5")).read()
    t = src[src.index("#define TW_NR"):]
    t = re.sub(r"(const\s+)?\b(double|bool|int|long|MqlRates)\s*&\s*(\w+)\[\]", r"\1std::vector<\2> &\3", t)

    def dekl(m):
        namen = [x.strip().replace("[]", "") for x in m.group(3).split(",")]
        return f"std::vector<{m.group(1)}>{m.group(2)}{', '.join(namen)};"
    t = re.sub(r"\b(double|bool|int|long|MqlRates)(\s+)((?:\w+\[\]\s*,\s*)*\w+\[\])\s*;", dekl, t)
    assert "[]" not in t
    os.makedirs(ARBEIT, exist_ok=True)
    open(os.path.join(ARBEIT, "tw_alles.inc"), "w").write("// AUTOMATISCH aus build/tw_block.mq5 erzeugt (tw_sim.py)\n" + t)
    exe = os.path.join(ARBEIT, "tw_sim")
    r = subprocess.run(["g++", "-O2", "-std=c++17", "-Wall", "-Wextra", "-Wno-format-security", "-I", ARBEIT,
                        os.path.join(HIER, "tw_sim.cpp"), "-o", exe], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr); raise SystemExit("C++-Uebersetzung fehlgeschlagen")
    return exe, r.stderr.strip()


def schreibe_daten(A, pfad):
    D = A["D"]
    d1n, ratio, nneu = OC.nas_d1_ergaenzt(D)
    d1 = {"XAU": {k: D["XAU"]["d1"][k] for k in ("o", "h", "l", "c", "key")}, "NAS": d1n}
    with open(pfad, "wb") as f:
        np.array([2], np.int64).tofile(f)
        for s in ("XAU", "NAS"):
            f.write(SYM[s].encode().ljust(32, b"\0"))
            x = d1[s]
            t = np.asarray(x["key"], np.int64) * 86400
            np.array([len(t)], np.int64).tofile(f); t.tofile(f)
            for k in ("o", "h", "l", "c"):
                np.asarray(x[k], np.float64).tofile(f)
            m = D[s]
            t = (np.asarray(m["ny"], np.int64) + 420) * 60
            np.array([len(t)], np.int64).tofile(f); t.tofile(f)
            for k in ("o", "h", "l", "c"):
                np.asarray(m[k], np.float64).tofile(f)
    return ratio, nneu


def server_sek(s):
    return int(np.datetime64(s.replace(" ", "T"), "s").astype(np.int64))


def main(name="frei"):
    exe, warn = uebersetzen()
    print("g++ -O2 -Wall -Wextra (ganzer TW-Block mit MQL-Attrappen): ok" + (f"\nWarnungen:\n{warn}" if warn else ", keine Warnungen"))
    A = AU.baue(name)
    dat = os.path.join(ARBEIT, "sim.bin")
    ratio, nneu = schreibe_daten(A, dat)
    module, ev = {}, []
    for tag in np.arange(np.datetime64("2026-10-01"), np.datetime64("2026-10-17")):
        if np.datetime64(tag, "D").astype(object).weekday() < 5:
            ev.append((server_sek(str(tag) + " 00:01"), "T"))
    for (te, sy, d, lot, px, sl, tp, tx, pxx, usd, mod) in CL.LIVE:
        if mod == "Noise":
            continue
        nm = mod.split("/")[0]
        if nm not in module:
            module[nm] = (len(module), 0 if sy == "XAU" else 1)
        t = server_sek(te) // 300 * 300
        ev.append((t, f"S {t} {module[nm][0]} {d}"))
    ev.sort(key=lambda x: x[0])
    with open(os.path.join(ARBEIT, "ereignisse.txt"), "w") as f:
        for t, e in ev:
            f.write((f"T {t}" if e == "T" else e) + "\n")
    with open(os.path.join(ARBEIT, "module.txt"), "w") as f:
        for nm, (m, k) in module.items():
            f.write(f"{m} {k} {nm}\n")
    r = subprocess.run([exe, dat, os.path.join(ARBEIT, "ereignisse.txt"), os.path.join(ARBEIT, "module.txt")],
                       capture_output=True, text=True, check=True)
    kopf = (f"# Simulierte V9-Journalzeilen 01.-16.10.2026 (C++-Geruest, Replikat-Kurse; NAS-D1 ab 26.09. aus NQ-Futures "
            f"x {ratio:.5f}, {nneu} Tage; NAS-M5 fehlt ab 26.09.)\n")
    out = kopf + r.stdout
    open(os.path.join(DA.SCRATCH, "tw_sim_oktober.txt"), "w").write(out)
    print(out)


def signale(name="frei", von="2024-01-01", bis="2026-09-25"):
    """Gesamter Signalpfad gegen Python: je Signal (alle Module, beide Symbole) die Journalzeile parsen und mit
    tests9.flags vergleichen (Tagesregeln der Gegenrichtung, NAS: NA/TR)."""
    import tests9 as T, regime9 as RG
    exe, _ = uebersetzen()
    A = AU.baue(name)
    dat = os.path.join(ARBEIT, "sim.bin")
    schreibe_daten(A, dat)
    FL = T.flags(A)
    a = int(np.datetime64(von, "m").astype(np.int64)); b = int(np.datetime64(bis, "m").astype(np.int64))
    module, ev, soll = {}, [], []
    for s in A["sigs"]:
        nm = s["name"]
        k = 0 if s["sym"] == "XAU" else 1
        for i in np.nonzero((s["t_entry"] >= a) & (s["t_entry"] < b))[0]:
            if nm not in module:
                module[nm] = len(module)
            t = (int(s["t_entry"][i]) + 420) * 60
            d = int(s["dir"][i])
            key = "dn" if d > 0 else "up"
            regeln = [r for r in RG.REGELN if FL[nm][key][r][i]]
            soll.append((t, nm, d, ",".join(regeln) or "-", bool(FL[nm]["dn"]["NA"][i]), bool(FL[nm]["dn"]["TR"][i]), k))
            ev.append((t, f"S {t} {module[nm]} {d}"))
    ev.sort(key=lambda x: x[0]); soll.sort(key=lambda x: x[0])
    with open(os.path.join(ARBEIT, "ereignisse_sig.txt"), "w") as f:
        for t, e in ev:
            f.write(e + "\n")
    with open(os.path.join(ARBEIT, "module_sig.txt"), "w") as f:
        for s in A["sigs"]:
            if s["name"] in module:
                f.write(f"{module[s['name']]} {0 if s['sym'] == 'XAU' else 1} {s['name']}\n")
    r = subprocess.run([exe, dat, os.path.join(ARBEIT, "ereignisse_sig.txt"), os.path.join(ARBEIT, "module_sig.txt")],
                       capture_output=True, text=True, check=True)
    ist = [z for z in r.stdout.splitlines() if z.startswith("DEADBAND9 TW Signal")]
    assert len(ist) == len(soll), (len(ist), len(soll))
    erg = dict(signale=len(soll), regeln_gleich=0, nas_mit_wert=0, nas_ohne_wert=0, na_gleich=0, tr_gleich=0, abw=[])
    for z, (t, nm, d, rg, na, tr, k) in zip(ist, soll):
        m = re.search(r"Signal (\S+) \S+ (LONG|SHORT): Tagesregeln \w+ \[([^\]]*)\]", z)
        ok = m and m.group(1) == nm and m.group(3) == rg
        erg["regeln_gleich"] += bool(ok)
        if not ok and len(erg["abw"]) < 5:
            erg["abw"].append((z, nm, rg))
        if k == 1:
            q = re.search(r"NA (JA|nein), TR (JA|nein)", z)
            if q:
                erg["nas_mit_wert"] += 1
                erg["na_gleich"] += (q.group(1) == "JA") == na
                erg["tr_gleich"] += (q.group(2) == "JA") == tr
            else:
                erg["nas_ohne_wert"] += 1
    print(erg)
    return erg


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "signale":
        signale(sys.argv[1])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else "frei")
