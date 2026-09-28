"""Pruefung: eng8 mit Voreinstellungen (Schutz gueltiger Tage aus, Abschluss-Ernte wie 6.30) rechnet exakt wie eng7.
Konten 6.30 Ertrag und Sicher auf dem GFT-Ersatz, mehrere Starts und Stoerungen; Vergleich aller Zaehler von eng7 (eng8
hat nur zusaetzliche Diagnose-Zaehler am Ende), aller Trades und Ereignisse.
Aufruf: python t_eng8.py"""
import numpy as np
import eng7, eng8, evl6 as V, r6, x40, x42

NR = dict(nz_tp1r=1.0, nz_be=0.05, r21_tp1r=1.0, r21_be=0.05)


def check(kw, gpx, label):
    blks, info, mk = x42.setup("gft")
    mk.set_generic(blks)
    GP = eng7.gparams([dict(on=1, risk=0.75, maxtrades=1, **gpx) for _ in x40.F10])
    P7 = eng7.params(**dict(r6.SAFE, **kw))
    P8 = eng8.params(**dict(r6.SAFE, **kw))
    assert np.array_equal(P7, P8[:len(P7)])
    n7 = len(eng7.ST)
    ok = True; n = 0
    a0 = mk.day_index(V.WARM)
    for (a, h) in ((a0, 250), (a0 + 97, 500), (a0 + 311, 250), (a0 + 400, 750), (a0 + 5, 750)):
        b = min(a + h, len(mk.days) - 1)
        for seed in (0, 3, 11):
            ms = eng7.make_masks(mk, seed, 0.08 if seed > 0 else 0.0)
            P7s = P7.copy(); P8s = P8.copy()
            if seed > 0:
                P7s[eng7.PI["slip_frac"]] = 0.3; P8s[eng8.PI["slip_frac"]] = 0.3
            r7 = eng7.run(mk, P7s, a, b, seed=seed, masks=ms, GP=GP)
            r8 = eng8.run(mk, P8s, a, b, seed=seed, masks=ms, GP=GP)
            same = np.array_equal(r7["st"], r8["st"][:n7]) and np.array_equal(r7["tr"], r8["tr"]) and np.array_equal(r7["ev"], r8["ev"])
            ok &= same; n += 1
            if not same:
                print("  ABWEICHUNG", label, a, h, seed)
    print(f"{label}: {n} Konten, {'IDENTISCH' if ok else 'ABWEICHUNG'}", flush=True)
    return ok


if __name__ == "__main__":
    ok = check(dict(x42.ERT, **NR), dict(x42.H, tp1r=0.6, tp1f=0.5), "6.30 Ertrag")
    ok &= check(dict(x42.ERT, **NR, minpayout=105.0, bank_last=5), dict(x42.H, tp1r=0.6, tp1f=0.5), "6.30 Ertrag, MP min, Ernte immer")
    ok &= check(x42.SIC, dict(tp1r=0.6, tp1f=0.5), "6.30 Sicher")
    print("GESAMT", "IDENTISCH" if ok else "ABWEICHUNG")
