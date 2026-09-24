"""Fade-Bloecke mit Regime-Waechter fuer beide Datensaetze (Fremddaten bis 2021, GFT ab 2022)."""
import numpy as np, gsig as G, gext, cands as K

LIM22 = np.datetime64("2022-01-01", "m").astype(np.int64)
_VT = {}


def _virt(dataset, nm):
    key = (dataset, nm)
    if key not in _VT:
        G._D = gext.data_ext() if dataset == "ext" else None
        if dataset != "ext":
            G.data()
        K._CACHE.clear()
        p = K.FADES[nm]
        b, (ie, d, rd, tp, ix) = K.fade(0, **p)
        R, *_ = G.simulate(p["sym"], ie, d, rd, tp, ix)
        _VT[key] = (b, R)
    return _VT[key]


def guard_mask(R, N, mode, th):
    live = np.zeros(len(R), bool)
    for i in range(N, len(R)):
        w = R[i - N:i]
        if mode == "sum":
            live[i] = w.sum() > th
        elif mode == "pf":
            pos = w[w > 0].sum(); neg = -w[w < 0].sum()
            live[i] = (pos / neg if neg > 0 else 9.9) > th
        else:
            live[i] = True
    return live


def blocks(names, target, N=40, mode="sum", th=0.0):
    """target 'ext' oder 'gft': Bloecke (Stroeme 0..) nur mit Waechter-freigegebenen Signalen des Zieldatensatzes.
    Der Waechter laeuft ueber die verkettete Historie (Fremddaten vor 2022, danach GFT)."""
    out = []; info = []
    for s_, nm in enumerate(names):
        b1, R1 = _virt("ext", nm); b2, R2 = _virt("gft", nm)
        pre = b1["t_entry"] < LIM22
        R = np.r_[R1[pre], R2]
        live = guard_mask(R, N, mode, th) if mode != "off" else np.ones(len(R), bool)
        n1 = int(pre.sum())
        if target == "ext":
            b = b1; m = np.zeros(len(b1["t_entry"]), bool); m[np.nonzero(pre)[0]] = live[:n1]
        else:
            b = b2; m = live[n1:]
        blk = {k: (v[m] if isinstance(v, np.ndarray) and len(v) == len(m) else v) for k, v in b.items()}
        blk["str"] = s_
        out.append(blk); info.append((nm, int(m.sum()), len(m)))
    return out, info
