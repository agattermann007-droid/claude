"""Register aller Strom-Generatoren (Fades, Noise v2, Eroeffnungsmomentum) fuer beide Datensaetze + Regime-Waechter."""
import numpy as np, gsig as G, gext, cands as K, scan6 as S, sig5 as S5

LIM22 = np.datetime64("2022-01-01", "m").astype(np.int64)
_VT = {}


def _use(dataset):
    G._D = gext.data_ext() if dataset == "ext" else None
    if dataset != "ext":
        G.data()
    K._CACHE.clear()


def _nz2(every=30, stop_mult=0.35):
    import nz2
    return nz2.nz2(0, every=every, stop_mult=stop_mult)


def _odm(t0=570, t1=600, xm=630, k=0.25, stopk=0.3, dirs=1):
    D, ny, days, t_end, atr = S.prep("NAS")
    ie, d, rd, ix = S.gen_mom(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, t0, t1, xm, k, 0, stopk, dirs)
    return K.block("NAS", ie, d, rd, np.zeros(len(ie)), ix, 0), (ie, d, rd, 0.0, ix)


def gen(name):
    if name in K.FADES:
        p = K.FADES[name]
        return K.fade(0, **p), p["sym"]
    if name == "NZ2":
        return _nz2(), "NAS"
    if name == "NZ2h":
        return _nz2(every=60, stop_mult=0.5), "NAS"
    if name == "ODM":
        return _odm(), "NAS"
    raise KeyError(name)


def virt(dataset, name):
    key = (dataset, name)
    if key not in _VT:
        _use(dataset)
        (b, (ie, d, rd, tp, ix)), sym = gen(name)
        R, *_ = G.simulate(sym, ie, d, rd, tp, ix)
        _VT[key] = (b, R)
    return _VT[key]


def guard_days(t, R, days, pf_th, nmin):
    live = np.zeros(len(R), bool)
    for i in range(len(R)):
        m = (t < t[i]) & (t >= t[i] - days * 1440)
        w = R[m]
        if len(w) < nmin:
            continue
        pos = w[w > 0].sum(); neg = -w[w < 0].sum()
        live[i] = (pos / neg if neg > 0 else 9.9) > pf_th
    return live


def guard_mask(R, N, mode, th, t=None):
    live = np.ones(len(R), bool)
    if mode == "off":
        return live
    if mode == "days":
        return guard_days(t, R, N, th, 10)
    live[:] = False
    for i in range(N, len(R)):
        w = R[i - N:i]
        if mode == "sum":
            live[i] = w.sum() > th
        else:
            pos = w[w > 0].sum(); neg = -w[w < 0].sum()
            live[i] = (pos / neg if neg > 0 else 9.9) > th
    return live


def blocks(names, target, guards):
    """guards: dict name -> (mode, N, th); fehlt -> ohne Waechter."""
    out = []
    for s_, nm in enumerate(names):
        b1, R1 = virt("ext", nm); b2, R2 = virt("gft", nm)
        pre = b1["t_entry"] < LIM22
        R = np.r_[R1[pre], R2]
        mode, N, th = guards.get(nm, ("off", 0, 0.0))
        t = np.r_[b1["t_entry"][pre], b2["t_entry"]]
        live = guard_mask(R, N, mode, th, t)
        n1 = int(pre.sum())
        if target == "ext":
            b = b1; m = np.zeros(len(b1["t_entry"]), bool); m[np.nonzero(pre)[0]] = live[:n1]
        else:
            b = b2; m = live[n1:]
        blk = {k: (v[m] if isinstance(v, np.ndarray) and len(v) == len(m) else v) for k, v in b.items()}
        blk["str"] = s_
        out.append(blk)
    return out
