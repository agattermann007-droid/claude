"""Pruefung: eng7 mit Voreinstellungen (keine Noise-Ausstiege, Fade-T1 absolut) rechnet exakt wie eng6.
Konten 6.20 Ertrag und Sicher auf dem GFT-Ersatz, mehrere Starts und Stoerungen; Vergleich aller Zaehler und Trades.
Einzige gewollte Abweichung: Wird ein Noise-Teil von der Abschluss-Ernte teilweise geschlossen, zaehlt eng7 den Teilgewinn
zum Trade-Ergebnis (wie der EA im Serien-Stopp: eine Position mit allen Teilschliessungen). eng6 zaehlte nur den Rest.
Deshalb wird "Ertrag" zusaetzlich ohne Noise in der Ernte (bank_mods 11) verglichen - dort muss alles gleich sein.
Aufruf: python t_eng7.py"""
import numpy as np
import eng6, eng7, evl6 as V, r6, x40, x41


def check(kw, gpx, rule, label):
    blks, info = x40.PB.blocks("gft", rule, info=True)
    mk = x40.market("gft")
    mk.set_generic(blks)
    GP = eng6.gparams([dict(on=1, risk=0.75, maxtrades=1, **gpx) for _ in x40.F10])
    P6 = eng6.params(**dict(r6.SAFE, **kw))
    P7 = eng7.params(**dict(r6.SAFE, **kw))
    assert np.array_equal(P6, P7[:len(P6)])
    ok = True; n = 0
    a0 = mk.day_index(V.WARM)
    for (a, h) in ((a0, 250), (a0 + 97, 500), (a0 + 311, 250), (a0 + 400, 750)):
        b = min(a + h, len(mk.days) - 1)
        for seed in (0, 3, 11):
            ms = eng6.make_masks(mk, seed, 0.08 if seed > 0 else 0.0)
            P6s = P6.copy(); P7s = P7.copy()
            if seed > 0:
                P6s[eng6.PI["slip_frac"]] = 0.3; P7s[eng7.PI["slip_frac"]] = 0.3
            r_6 = eng6.run(mk, P6s, a, b, seed=seed, masks=ms, GP=GP)
            r_7 = eng7.run(mk, P7s, a, b, seed=seed, masks=ms, GP=GP)
            same = np.array_equal(r_6["st"], r_7["st"]) and np.array_equal(r_6["tr"], r_7["tr"]) and np.array_equal(r_6["ev"], r_7["ev"])
            ok &= same; n += 1
            if not same:
                print("  ABWEICHUNG", label, a, h, seed)
    print(f"{label}: {n} Konten, {'IDENTISCH' if ok else 'ABWEICHUNG'}", flush=True)
    return ok


if __name__ == "__main__":
    ok = check(dict(x40.ERT, bank_mods=11), dict(harv=1), x41.S70_OHNE, "6.20 Ertrag, Ernte ohne Noise")
    ok &= check(x40.SIC, {}, x41.S70_OHNE, "6.20 Sicher")
    check(x40.ERT, dict(harv=1), x41.S70_OHNE, "6.20 Ertrag (Noise-Teilernte: gewollte Abweichung moeglich)")
    print("GESAMT", "IDENTISCH" if ok else "ABWEICHUNG")
