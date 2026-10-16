"""DEADBAND V9 - Pruefung des MQL5-Rechenkerns (TwRegeln, TwNoise) gegen den Python-Nachbau regime9.py.

1. TwSma/TwRegeln/TwNoise werden MECHANISCH aus build/tw_block.mq5 nach C++ uebersetzt (tw_kern.inc):
   Array-Parameter "T &x[]" -> "std::vector<T> &x", lokale "T a[], b[];" -> "std::vector<T> a, b;", sonst kein Eingriff.
2. g++ uebersetzt tw_check.cpp + tw_kern.inc.
3. Vergleich:
   D1  je Symbol alle Servertage: Bitmasken der ganzen Historie und rollierend auf 400 Tagen (wie TwTagesbericht im EA)
       gegen regime9.tagesregeln (ganze Historie)
   NZ  je NAS-Signal (alle Module): M5-Kerzen von Einstieg - 45 Tage bis Einstieg - 1 min (wie TwSignalBericht),
       letzte Kerze = Signalkerze; gueltig/NA/TR gegen regime9.noise_area/intraday_flags
Aufruf: python3 tw_check.py [datensatz]   (Datensatz wie aufbau9.py, Voreinstellung frei)
"""
import json, os, re, subprocess, sys
import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HIER), "replikat"))
import aufbau9 as AU, regime9 as RG, daten9 as DA

ARBEIT = os.path.join(DA.SCRATCH, "tw_check")


def kern_uebersetzen():
    src = open(os.path.join(HIER, "tw_block.mq5")).read()
    teile = []
    for kopf in ("void TwSma(", "void TwRegeln(", "bool TwNoise("):
        a = src.index(kopf)
        b = src.index("\n  }\n", a) + len("\n  }\n")
        teile.append(src[a:b])
    t = "\n".join(teile)
    t = re.sub(r"(const\s+)?\b(double|bool|int|long)\s*&\s*(\w+)\[\]", r"\1std::vector<\2> &\3", t)

    def dekl(m):
        namen = [x.strip().replace("[]", "") for x in m.group(3).split(",")]
        return f"std::vector<{m.group(1)}>{m.group(2)}{', '.join(namen)};"
    t = re.sub(r"\b(double|bool|int|long)(\s+)((?:\w+\[\]\s*,\s*)*\w+\[\])\s*;", dekl, t)
    assert "[]" not in t, "nicht uebersetzte Array-Syntax"
    os.makedirs(ARBEIT, exist_ok=True)
    pfad = os.path.join(ARBEIT, "tw_kern.inc")
    open(pfad, "w").write("// AUTOMATISCH aus build/tw_block.mq5 erzeugt (tw_check.py) - nicht von Hand aendern\n" + t)
    return pfad


def bauen():
    kern_uebersetzen()
    exe = os.path.join(ARBEIT, "tw_check")
    r = subprocess.run(["g++", "-O2", "-std=c++17", "-Wall", "-Wextra", "-I", ARBEIT, os.path.join(HIER, "tw_check.cpp"), "-o", exe],
                       capture_output=True, text=True)
    if r.returncode:
        print(r.stderr); raise SystemExit("C++-Uebersetzung fehlgeschlagen")
    return exe, r.stderr.strip()


def maske(F, seite):
    m = np.zeros(len(next(iter(F.values()))[0]), np.int64)
    for i, r in enumerate(RG.REGELN):
        m |= F[r][seite].astype(np.int64) << i
    return m


def pruefe_d1(exe, D, fen=400):
    out = {}
    for sym in ("XAU", "NAS"):
        d1 = D[sym]["d1"]
        o, h, l, c = (np.ascontiguousarray(d1[k], dtype=np.float64) for k in ("o", "h", "l", "c"))
        n = len(c)
        ein = os.path.join(ARBEIT, f"d1_{sym}.bin"); aus = ein + ".aus"
        with open(ein, "wb") as f:
            np.array([n, fen], np.int64).tofile(f)
            for x in (o, h, l, c):
                x.tofile(f)
        subprocess.run([exe, "d1", ein, aus], check=True)
        r = np.fromfile(aus, np.int32).reshape(4, n).astype(np.int64)
        F = RG.tagesregeln(d1)
        py = (maske(F, 0), maske(F, 1))
        z = {"tage": int(n)}
        for name, (cd, cu) in (("ganz", (r[0], r[1])), ("rollierend400", (r[2], r[3]))):
            sel = np.arange(n) >= (fen - 1 if name != "ganz" else 0)
            je = {}
            for i, reg in enumerate(RG.REGELN):
                bit = 1 << i
                fd = int((((cd & bit) != 0) != ((py[0] & bit) != 0))[sel].sum())
                fu = int((((cu & bit) != 0) != ((py[1] & bit) != 0))[sel].sum())
                je[reg] = (fd, fu)
            z[name] = dict(tage=int(sel.sum()), abweichungen=je,
                           tage_gleich=int(((cd == py[0]) & (cu == py[1]))[sel].sum()))
        out[sym] = z
    return out


def pruefe_nz(exe, A):
    D = A["D"]
    d = D["NAS"]
    ny = np.ascontiguousarray(d["ny"], dtype=np.int64)
    o, l, c = (np.ascontiguousarray(d[k], dtype=np.float64) for k in ("o", "l", "c"))
    NA = RG.noise_area(D, "NAS")
    ia, ib, py_ok, py_na, py_tr, isig, namen = [], [], [], [], [], [], []
    for s in A["sigs"]:
        if s["sym"] != "NAS" or not len(s["t_entry"]):
            continue
        te = s["t_entry"].astype(np.int64)
        ia.append(np.searchsorted(ny, te - 45 * 1440, side="left"))
        ib.append(np.searchsorted(ny, te, side="left"))
        na, tr = RG.intraday_flags(D, s, NA)
        py_ok.append(np.isfinite(NA[2][s["i_sig"]])); py_na.append(na); py_tr.append(tr)
        isig.append(s["i_sig"].astype(np.int64)); namen += [s["name"]] * len(te)
    ia, ib, py_ok, py_na, py_tr, isig = map(np.concatenate, (ia, ib, py_ok, py_na, py_tr, isig))
    m = len(ia)
    ein = os.path.join(ARBEIT, "nz.bin"); aus = ein + ".aus"
    with open(ein, "wb") as f:
        np.array([len(ny), m], np.int64).tofile(f)
        for x in (ny, o, l, c):
            x.tofile(f)
        ia.astype(np.int64).tofile(f); ib.astype(np.int64).tofile(f)
    subprocess.run([exe, "nz", ein, aus], check=True)
    r = np.fromfile(aus, np.int32).reshape(m, 3).astype(bool)
    letzte_ist_signal = (ib - 1) == isig
    beide = r[:, 0] & py_ok
    return dict(signale=int(m), letzte_kerze_ist_signalkerze=int(letzte_ist_signal.sum()),
                gueltig_cpp=int(r[:, 0].sum()), gueltig_py=int(py_ok.sum()), gueltig_beide=int(beide.sum()),
                gueltig_nur_cpp=int((r[:, 0] & ~py_ok).sum()), gueltig_nur_py=int((~r[:, 0] & py_ok).sum()),
                NA_abweichung=int((r[:, 1] != py_na)[beide].sum()), TR_abweichung=int((r[:, 2] != py_tr)[beide].sum()),
                NA_ja=int(py_na[beide].sum()), TR_ja=int(py_tr[beide].sum()))


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "frei"
    exe, warn = bauen()
    print("g++ -O2 -Wall -Wextra: ok" + (f" (Warnungen: {warn})" if warn else " (keine Warnungen)"), flush=True)
    A = AU.baue(name)
    erg = {"d1": pruefe_d1(exe, A["D"]), "nz": pruefe_nz(exe, A), "compiler_warnungen": warn}
    json.dump(erg, open(os.path.join(DA.SCRATCH, f"tw_check_{name}.json"), "w"), indent=1)
    print(json.dumps(erg, indent=1))
