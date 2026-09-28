"""Pruefung: eng9 mit Voreinstellungen rechnet exakt wie eng8 (alle Zaehler, Trades - Spalten 0-3 - und Ereignisse).
Konten 6.40 Ertrag (Schutz gueltiger Tage vp 3, Portfolio-Waechter) und 6.40 Sicher auf dem GFT-Ersatz, mehrere Starts und
Stoerungen. Zusaetzlich: vp_mods 15 = alle Module gesperrt (gleich eng8), vp_mods mit allen Bits einzeln = dieselbe Sperre.
Aufruf: python t_eng9.py"""
import numpy as np
import eng8, eng9, evl6 as V, r6, x40, x44


def run_pair(mk, kw8, kw9, GP8, GP9, label):
    P8 = eng8.params(**dict(r6.SAFE, **kw8))
    P9 = eng9.params(**dict(r6.SAFE, **kw9))
    ok = True; n = 0
    a0 = mk.day_index(V.WARM)
    for (a, h) in ((a0, 250), (a0 + 97, 500), (a0 + 311, 250), (a0 + 400, 750), (a0 + 5, 750)):
        b = min(a + h, len(mk.days) - 1)
        for seed in (0, 3, 11):
            ms = eng8.make_masks(mk, seed, 0.08 if seed > 0 else 0.0)
            P8s = P8.copy(); P9s = P9.copy()
            if seed > 0:
                P8s[eng8.PI["slip_frac"]] = 0.3; P9s[eng9.PI["slip_frac"]] = 0.3
            r8 = eng8.run(mk, P8s, a, b, seed=seed, masks=ms, GP=GP8)
            r9 = eng9.run(mk, P9s, a, b, seed=seed, masks=ms, GP=GP9)
            same = np.array_equal(r8["st"], r9["st"]) and np.array_equal(r8["tr"], r9["tr"][:, :4]) and np.array_equal(r8["ev"], r9["ev"])
            ok &= same; n += 1
            if not same:
                print("  ABWEICHUNG", label, a, h, seed, len(r8["tr"]), len(r9["tr"]))
    print(f"{label}: {n} Konten, {'IDENTISCH' if ok else 'ABWEICHUNG'}", flush=True)
    return ok


def check(kw, gpx, label, rule="P200/1.15", kw9_extra=None):
    blks, info, mk = x44.setup("gft", rule)
    mk.set_generic(blks)
    GP8 = eng8.gparams([dict(on=1, risk=0.75, maxtrades=1, **gpx) for _ in x40.F10])
    GP9 = eng9.gparams([dict(on=1, risk=0.75, maxtrades=1, **gpx) for _ in x40.F10])
    assert np.array_equal(GP8, GP9[:, :GP8.shape[1]])
    return run_pair(mk, kw, dict(kw, **(kw9_extra or {})), GP8, GP9, label)


if __name__ == "__main__":
    ok = check(x44.E640, x44.H, "6.40 Ertrag")
    ok &= check(dict(x44.E640, vp_on=0), x44.H, "6.40 Ertrag ohne Schutz")
    ok &= check(x44.E640, x44.H, "6.40 Ertrag, Schutz ueber vp_mods (alle Bits, Sperre je Modul)", kw9_extra=dict(vp_mods=15 + 16))
    ok &= check(x44.S640, {}, "6.40 Sicher")
    print("GESAMT", "IDENTISCH" if ok else "ABWEICHUNG")
