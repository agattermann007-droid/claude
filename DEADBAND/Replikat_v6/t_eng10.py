"""Pruefung: eng10 mit Voreinstellungen rechnet exakt wie eng9 (alle Zaehler bis auf den neuen sv_up, Trades, Ereignisse).
Konten 6.50 Ertrag und 6.40 Sicher auf dem GFT-Ersatz, mehrere Starts und Stoerungen (8 % ausgelassen, Schlupf).
Aufruf: python t_eng10.py"""
import numpy as np
import eng9, eng10, evl6 as V, r6, x40, x44, x48


def run_pair(mk, kw, GP9, GP10, label):
    P9 = eng9.params(**dict(r6.SAFE, **kw))
    P10 = eng10.params(**dict(r6.SAFE, **kw))
    ok = True; n = 0
    a0 = mk.day_index(V.WARM)
    for (a, h) in ((a0, 250), (a0 + 97, 500), (a0 + 311, 250), (a0 + 400, 750), (a0 + 5, 750)):
        b = min(a + h, len(mk.days) - 1)
        for seed in (0, 3, 11):
            ms = eng9.make_masks(mk, seed, 0.08 if seed > 0 else 0.0)
            P9s = P9.copy(); P10s = P10.copy()
            if seed > 0:
                P9s[eng9.PI["slip_frac"]] = 0.3; P10s[eng10.PI["slip_frac"]] = 0.3
            r9 = eng9.run(mk, P9s, a, b, seed=seed, masks=ms, GP=GP9)
            r10 = eng10.run(mk, P10s, a, b, seed=seed, masks=ms, GP=GP10)
            same = (np.array_equal(r9["st"], r10["st"][:len(r9["st"])]) and np.array_equal(r9["tr"], r10["tr"][:, :8])
                    and np.array_equal(r9["ev"], r10["ev"]))
            ok &= same; n += 1
            if not same:
                print("  ABWEICHUNG", label, a, h, seed, len(r9["tr"]), len(r10["tr"]))
    print(f"{label}: {n} Konten, {'IDENTISCH' if ok else 'ABWEICHUNG'}", flush=True)
    return ok


def check(label, kw, gpx, risk, per):
    blks, info, mk = x44.setup("gft", "P200/1.15")
    mk.set_generic(blks)
    mk.r21["reg"] = x48.r21_regime("gft", mk)
    gp = []
    for i, _ in enumerate(x40.F10):
        d = dict(on=1, risk=risk, maxtrades=1, **gpx)
        if per and i in per:
            d.update(per[i])
        gp.append(d)
    GP9 = eng9.gparams(gp); GP10 = eng10.gparams(gp)
    assert np.array_equal(GP9, GP10[:GP9.shape[0]]) and not GP10[GP9.shape[0]:, 0].any()
    return run_pair(mk, kw, GP9, GP10, label)


if __name__ == "__main__":
    v = x48.VAR["6.50 Ertrag"]
    ok = check("6.50 Ertrag", v[0], v[1], v[2], v[4])
    v = x48.VAR["6.40 Ertrag"]
    ok &= check("6.40 Ertrag", v[0], v[1], v[2], None)
    v = x48.VAR["6.50 Sicher"]
    ok &= check("6.50 Sicher", v[0], v[1], v[2], None)
    print("GESAMT", "IDENTISCH" if ok else "ABWEICHUNG")
