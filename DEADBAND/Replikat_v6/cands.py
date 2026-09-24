"""Kandidaten als Signal-Bloecke fuer eng6 (generische Stroeme)."""
import numpy as np, gsig as G, scan6 as S

_CACHE = {}


def _prep(sym):
    if sym not in _CACHE:
        _CACHE[sym] = S.prep(sym)
    return _CACHE[sym]


def block(sym, ie, d, rd, tp, ix, stream, w=1.0):
    D, ny, *_ = _prep(sym)
    k = G.SYM[sym]
    return dict(str=stream, sym=np.full(len(ie), k), dir=d, t_entry=ny[ie], rd=rd, tp=tp, t_exit=ny[ix], w=w)


def xau_fade(stream, r0=480, r1=570, tend=750, xm=750, buf=0.3, tgt=0, dirs=-1, mn=0.0, mx=0.6):
    D, ny, days, t_end, atr = _prep("XAU")
    ie, d, rd, tp, ix = S.gen_fade(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx)
    return block("XAU", ie, d, rd, tp, ix, stream), (ie, d, rd, tp, ix)


def nas_pre_break(stream, r0=480, r1=570, tend=750, xm=1000, sm=2, sk=0.5, tp=2.0, dirs=1, mn=0.0, mx=99.0):
    D, ny, days, t_end, atr = _prep("NAS")
    ie, d, rd, ix = S.gen_break(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, r0, r1, tend, xm, sm, sk, dirs, mn, mx)
    return block("NAS", ie, d, rd, np.full(len(ie), tp), ix, stream), (ie, d, rd, tp, ix)


def nas_lasthour(stream, t0=900, t1=930, xm=1000, k=0.1, rev=0, stopk=0.3, dirs=1):
    D, ny, days, t_end, atr = _prep("NAS")
    ie, d, rd, ix = S.gen_mom(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, t0, t1, xm, k, rev, stopk, dirs)
    return block("NAS", ie, d, rd, np.zeros(len(ie)), ix, stream), (ie, d, rd, 0.0, ix)


def nas_fade(stream, r0=780, r1=870, tend=960, xm=1000, buf=0.6, tgt=0, dirs=1, mn=0.0, mx=0.6):
    D, ny, days, t_end, atr = _prep("NAS")
    ie, d, rd, tp, ix = S.gen_fade(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx)
    return block("NAS", ie, d, rd, tp, ix, stream), (ie, d, rd, tp, ix)


def fade(stream, sym, r0, L, tlen, xoff, buf, tgt, dirs, mx=0.6, mn=0.0):
    """Fade aus dem Scan-Raster (Parametrisierung wie scan6_run3)."""
    D, ny, days, t_end, atr = _prep(sym)
    r1 = r0 + L
    tend = r1 + tlen; xm = min(r1 + tlen + xoff, 16 * 60 + 40)
    if xm <= tend:
        tend = xm - 5
    ie, d, rd, tp, ix = S.gen_fade(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, r0, r1, tend, xm, buf, tgt, dirs, mn, mx)
    return block(sym, ie, d, rd, tp, ix, stream), (ie, d, rd, tp, ix)


# Portfolio-Kandidaten (zentrale, nicht beste Parameter der robusten Cluster)
FADES = {
    "N1030": dict(sym="NAS", r0=630, L=120, tlen=60, xoff=120, buf=0.3, tgt=0, dirs=1),
    "N1330": dict(sym="NAS", r0=810, L=60, tlen=120, xoff=120, buf=1.0, tgt=0, dirs=1),
    "X0630": dict(sym="XAU", r0=390, L=120, tlen=180, xoff=240, buf=1.0, tgt=1, dirs=-1),
    "X0400": dict(sym="XAU", r0=240, L=180, tlen=60, xoff=240, buf=0.3, tgt=0, dirs=1),
    "N1800": dict(sym="NAS", r0=-360, L=180, tlen=60, xoff=120, buf=0.3, tgt=0, dirs=1),
    "N0930": dict(sym="NAS", r0=570, L=180, tlen=60, xoff=120, buf=0.3, tgt=0, dirs=1, mx=99.0),
    "N1100": dict(sym="NAS", r0=660, L=90, tlen=60, xoff=240, buf=0.6, tgt=1, dirs=1),
    "N1300": dict(sym="NAS", r0=780, L=90, tlen=60, xoff=120, buf=0.6, tgt=0, dirs=1),
    "X0530": dict(sym="XAU", r0=330, L=240, tlen=60, xoff=120, buf=0.3, tgt=0, dirs=-1),
}


def fade_blocks(names):
    out = []
    for s_, nm in enumerate(names):
        b, _ = fade(s_, **FADES[nm])
        out.append(b)
    return out
FADES.update({
    "X0300S": dict(sym="XAU", r0=180, L=90, tlen=60, xoff=120, buf=0.3, tgt=0, dirs=-1),
    "X1000S": dict(sym="XAU", r0=600, L=180, tlen=60, xoff=240, buf=0.3, tgt=0, dirs=-1),
    "N1030b": dict(sym="NAS", r0=630, L=60, tlen=180, xoff=120, buf=0.6, tgt=0, dirs=1),
})
