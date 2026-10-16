"""Kandidaten neuer Stroeme (Stromnummern ab 18) und Tick-Fades. Parameter = Mitte der Ueberlebenden des Scans."""
import numpy as np
import gen11 as G, pa11 as PA, cfg11 as C

CANDS = {
    # Gold: Sweep des Tiefs -> Long
    "GASIA": dict(sym="XAU", la=-360, lb=120, loff=0, w0=480, w1=660, x=720, sd=0.0, md=0.3, sb=0.03, tmode=2, crv=0.0, dr=1),
    "GPRE":  dict(sym="XAU", la=360, lb=500, loff=0, w0=510, w1=630, x=720, sd=0.0, md=0.6, sb=0.03, tmode=2, crv=0.0, dr=1),
    "GPDF":  dict(sym="XAU", la=-360, lb=1020, loff=-1, w0=-360, w1=120, x=480, sd=0.0, md=0.6, sb=0.10, tmode=0, crv=3.0, dr=1),
    "GPD":   dict(sym="XAU", la=500, lb=810, loff=-1, w0=480, w1=720, x=955, sd=0.0, md=0.3, sb=0.03, tmode=0, crv=2.0, dr=1),
    # NAS
    "NPM":   dict(sym="NAS", la=780, lb=870, loff=0, w0=870, w1=945, x=955, sd=0.0, md=0.6, sb=0.03, tmode=2, crv=0.0, dr=1),
    "NPDC":  dict(sym="NAS", la=900, lb=960, loff=-1, w0=570, w1=690, x=955, sd=0.0, md=0.6, sb=0.03, tmode=2, crv=0.0, dr=1),
    "NASIA": dict(sym="NAS", la=-360, lb=180, loff=0, w0=180, w1=570, x=955, sd=0.05, md=0.6, sb=0.10, tmode=2, crv=0.0, dr=1),
    "NORB":  dict(sym="NAS", la=570, lb=585, loff=0, w0=585, w1=720, x=955, sd=0.0, md=0.6, sb=0.03, tmode=2, crv=0.0, dr=1),
}


def cand_block(name, **over):
    p = dict(CANDS[name]); p.update(over)
    sym = p.pop("sym")
    return PA.sweep(sym, p["la"], p["lb"], p["loff"], p["w0"], p["w1"], p["x"], p["sd"], p["md"], 0.0, 0, p["sb"],
                    p["tmode"], p["crv"], 99.0, p["dr"], name=name)


def tick_fade(name, md=0.6, live_at=None, buf_over=None):
    """Listen-Fade mit Einstieg im Tick (Ruecklauf in die Range). Nur, solange der Portfolio-Waechter (M5-virtuell) live ist."""
    for (nm, s, r0, L, tlen, xoff, buf, tgt, dirs, mx) in G.FADE_STANDARD:
        if nm != name:
            continue
        r1, te, xm = G.fade_times(r0, L, tlen, xoff)
        if buf_over is not None:                 # v12: Nachbarn des Stop-Puffers pruefen
            buf = buf_over
        b = PA.sweep(s, r0, r1, 0, r1, te, xm, 0.0, md, 0.0, 1, buf, 1 if tgt == 0 else 2, 0.0, mx, dirs if dirs != 0 else 1,
                     minsp=6.0, minatr=0.0, name=name + "T")
        if live_at is not None:
            m = np.array([live_at(int(t))[0] for t in b["t"]], bool)
            b = {k: (v[m] if isinstance(v, np.ndarray) and len(v) == len(m) else v) for k, v in b.items()}
        return b
    raise KeyError(name)
