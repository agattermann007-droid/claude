"""Pruefung: eng11 mit Voreinstellungen rechnet exakt wie eng10 (alle Zaehler bis auf die neuen ext_n/ext_hit/fsym_blk/nz_blk,
Trades, Ereignisse). Konten 6.60 (= 6.60b), 6.40 Ertrag und 6.50 Sicher auf dem GFT-Ersatz, mehrere Starts und Stoerungen
(8 % ausgelassen, Schlupf). Zusaetzlich: mit ext_on/fsym_block/nz_maxloss/reg_mult wird tatsaechlich anders gerechnet (die Schalter wirken).
Aufruf: python t_eng11.py"""
import numpy as np
import eng10, eng11, evl6 as V, r6, x40, x44, x48, x60


def run_pair(mk, kw, GP10, GP11, label, kw11=None):
    P10 = eng10.params(**dict(r6.SAFE, **kw))
    P11 = eng11.params(**dict(r6.SAFE, **kw, **(kw11 or {})))
    ok = True; n = 0; nd = 0
    a0 = mk.day_index(V.WARM)
    for (a, h) in ((a0, 250), (a0 + 97, 500), (a0 + 311, 250), (a0 + 400, 750), (a0 + 5, 750)):
        b = min(a + h, len(mk.days) - 1)
        for seed in (0, 3, 11):
            ms = eng10.make_masks(mk, seed, 0.08 if seed > 0 else 0.0)
            P10s = P10.copy(); P11s = P11.copy()
            if seed > 0:
                P10s[eng10.PI["slip_frac"]] = 0.3; P11s[eng11.PI["slip_frac"]] = 0.3
            r10 = eng10.run(mk, P10s, a, b, seed=seed, masks=ms, GP=GP10)
            r11 = eng11.run(mk, P11s, a, b, seed=seed, masks=ms, GP=GP11)
            same = (np.array_equal(r10["st"], r11["st"][:len(r10["st"])]) and np.array_equal(r10["tr"], r11["tr"][:, :10])
                    and np.array_equal(r10["ev"], r11["ev"]))
            ok &= same; n += 1; nd += int(not same)
    if kw11:
        print(f"{label} mit {kw11}: {n} Konten, davon {nd} anders gerechnet ({'WIRKT' if nd > 0 else 'WIRKT NICHT'})", flush=True)
        return nd > 0
    print(f"{label}: {n} Konten, {'IDENTISCH' if ok else 'ABWEICHUNG'}", flush=True)
    return ok


def check(label, v, kw11=None):
    kw, gpx, risk, rule, per, extra, extra_gp = x60.unpack(v)
    blks, info, mk = x44.setup("gft", rule)
    mk.set_generic(blks)
    mk.r21["reg"] = x48.r21_regime("gft", mk)
    x60._nz_lb("gft", mk)
    gp = []
    for i, _ in enumerate(x40.F10):
        d = dict(on=1, risk=risk, maxtrades=1, **gpx)
        if per and i in per:
            d.update(per[i])
        gp.append(d)
    GP10 = eng10.gparams(gp); GP11 = eng11.gparams(gp)
    assert np.array_equal(GP10, GP11)
    return run_pair(mk, kw, GP10, GP11, label, kw11)


if __name__ == "__main__":
    ok = check("6.60", x60.VAR["6.60b"])
    ok &= check("6.40 Ertrag", x60.VAR["6.40 Ertrag"])
    ok &= check("6.50 Sicher", x60.VAR["6.50 Sicher"])
    print("GESAMT", "IDENTISCH" if ok else "ABWEICHUNG")
    w = check("6.60", x60.VAR["6.60b"], dict(ext_on=1))
    w &= check("6.60", x60.VAR["6.60b"], dict(fsym_block=1))
    w &= check("6.60", x60.VAR["6.60b"], dict(nz_maxloss=1))
    w &= check("6.60", x60.VAR["6.60b"], dict(reg_mult=0.5))
    print("SCHALTER", "WIRKEN" if w else "WIRKEN NICHT")
