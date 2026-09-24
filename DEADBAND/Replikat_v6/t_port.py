"""Abgleich: woertliche Uebertragung von FadeKerze (MQL5, Build 6.00) gegen scan6.gen_fade + gsig.simulate."""
import numpy as np, math, gsig as G, scan6 as S, cands as K

def atr_mql(d1t, d1h, d1l, d1c, rs):
    # iBarShift(D1, tSrv, exact=false): letzte D1-Kerze mit Beginn <= rs; dann CopyRates(sh+1, 15) -> 15 Kerzen bis k-1
    k = np.searchsorted(d1t, rs, side="right") - 1
    if k - 15 < 0:
        return 0.0
    idx = range(k - 15, k)                   # 15 Kerzen, aelteste zuerst, juengste = k-1
    idx = list(idx)
    s = 0.0
    for i in range(1, 15):
        a, b = idx[i], idx[i - 1]
        s += max(d1h[a], d1c[b]) - min(d1l[a], d1c[b])
    return s / 14.0

def port(sym, r0, L, tlen, xoff, buf, tgt, dirs, mx=0.6, mn=0.0):
    D = G.data()[sym]; ny = D["ny"]; o, h, l, c, sp = D["o"], D["h"], D["l"], D["c"], D["sp"]
    d1 = D["d1"]; d1t, d1h, d1l, d1c = d1["t"], d1["h"], d1["l"], d1["c"]
    comm = G.COMM[G.SYM[sym]] / G.MPP[G.SYM[sym]]
    st = dict(day=None, nbar=0, hh=-1e300, ll=1e300, ready=False, done=False, skip=False, rng=0.0, exHi=0.0, exLo=0.0)
    v = None; out = []
    def zeiten(Dt):
        rs = Dt * 1440 + r0; re = rs + L; te = re + tlen
        xm = min(re + tlen + xoff, Dt * 1440 + 1000)
        if xm <= te: te = xm - 5
        return rs, re, te, xm
    for j in range(len(ny) - 1):
        t, tn = int(ny[j]), int(ny[j + 1])
        # 1) virtueller Trade
        if v is not None and j >= v["iB"]:
            if v["d"] > 0:
                slHit = l[j] <= v["sl"]; tpHit = h[j] >= v["tp"]
            else:
                slHit = h[j] + sp[j] >= v["sl"]; tpHit = l[j] + sp[j] <= v["tp"]
            if slHit:
                px = v["sl"]
                if v["d"] > 0 and o[j] < v["sl"]: px = o[j]
                if v["d"] < 0 and o[j] + sp[j] > v["sl"]: px = o[j] + sp[j]
                out.append((v["iB"], v["d"], v["rd"], ((px - v["ent"]) * v["d"] - comm) / v["rd"])); v = None
            elif tpHit and j > v["iB"]:
                out.append((v["iB"], v["d"], v["rd"], ((v["tp"] - v["ent"]) * v["d"] - comm) / v["rd"])); v = None
        if v is not None and tn >= v["xm"]:
            px = o[j + 1] if v["d"] > 0 else o[j + 1] + sp[j + 1]
            out.append((v["iB"], v["d"], v["rd"], ((px - v["ent"]) * v["d"] - comm) / v["rd"])); v = None
        # 2) Tageszustand
        Dt = math.floor((t - r0) / 1440)
        rs, re, te, xm = zeiten(Dt)
        if Dt != st["day"]:
            st.update(day=Dt, nbar=0, hh=-1e300, ll=1e300, ready=False, done=False, skip=False)
        dow = ((Dt + 4) % 7 + 7) % 7
        if dow < 1 or dow > 5: continue
        if rs <= t < re:
            st["nbar"] += 1; st["hh"] = max(st["hh"], h[j]); st["ll"] = min(st["ll"], l[j]); continue
        if t < re or st["done"] or st["skip"]: continue
        if not st["ready"]:
            a = atr_mql(d1t, d1h, d1l, d1c, rs)
            st["rng"] = st["hh"] - st["ll"]
            if st["nbar"] < (L // 5) * 0.6 or not (a > 0) or st["rng"] <= 0 or st["rng"] > mx * a or st["rng"] < mn * a:
                st["skip"] = True; continue
            st["exHi"], st["exLo"], st["ready"] = st["hh"], st["ll"], True
        if t >= te:
            st["done"] = True; continue
        st["exHi"] = max(st["exHi"], h[j]); st["exLo"] = min(st["exLo"], l[j])
        hh, ll = st["hh"], st["ll"]; d = 0
        if h[j] > hh and c[j] < hh and c[j] > ll: d = -1
        elif l[j] < ll and c[j] > ll and c[j] < hh: d = 1
        if d == 0:
            if c[j] > hh or c[j] < ll: st["done"] = True
            continue
        st["done"] = True
        if dirs != 0 and d != dirs: continue
        if tn >= xm: continue
        ent = o[j + 1] + (sp[j + 1] if d > 0 else 0.0)
        stp = st["exLo"] - buf * st["rng"] if d > 0 else st["exHi"] + buf * st["rng"]
        goal = 0.5 * (hh + ll) if tgt == 0 else (hh if d > 0 else ll)
        r = (ent - stp) * d; g = (goal - ent) * d
        if r <= 0 or g <= 0: continue
        v = dict(iB=j + 1, d=d, ent=ent, sl=stp, tp=goal, rd=r, xm=xm)
    return out

tot_ok = True
for nm, p in K.FADES.items():
    if nm not in ("N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"): continue
    q = dict(p); sym = q.pop("sym"); dirs = q.pop("dirs"); mx = q.pop("mx", 0.6)
    b, (ie, d, rd, tp, ix) = K.fade(0, sym, dirs=dirs, mx=mx, **q)
    R, *_ = G.simulate(sym, ie, d, rd, tp, ix)
    ref = list(zip(ie.tolist(), d.tolist(), rd.tolist(), R.tolist()))
    got = port(sym, q["r0"], q["L"], q["tlen"], q["xoff"], q["buf"], q["tgt"], dirs, mx)
    same = len(ref) == len(got) and all(a[0] == b_[0] and a[1] == b_[1] and abs(a[2] - b_[2]) < 1e-9 and abs(a[3] - b_[3]) < 1e-9 for a, b_ in zip(ref, got))
    tot_ok &= same
    print(f"{nm:7s} Referenz {len(ref):4d} Signale, Port {len(got):4d} -> {'IDENTISCH' if same else 'ABWEICHUNG'}", flush=True)
    if not same:
        sr = {x[0]: x for x in ref}; sg = {x[0]: x for x in got}
        only_r = sorted(set(sr) - set(sg)); only_g = sorted(set(sg) - set(sr))
        diffR = [k for k in set(sr) & set(sg) if abs(sr[k][3] - sg[k][3]) > 1e-9 or sr[k][1] != sg[k][1]]
        print("   nur Referenz:", only_r[:5], " nur Port:", only_g[:5], " R-Abweichungen:", len(diffR), diffR[:3])
print("GESAMT", "IDENTISCH" if tot_ok else "ABWEICHUNG")
