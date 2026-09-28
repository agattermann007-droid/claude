"""Abgleich EA <-> Replikat fuer Build 6.40 (Auszahlungstakt).

1. Zeitpunkt der virtuellen Fade-Ergebnisse: woertliche Uebertragung der virtuellen Trade-Fuehrung aus FadeKerze
   (DEADBAND_LIVE4.mq5; Stop vor Ziel, Ziel nicht in der Einstiegskerze, Zeit-Ausstieg am Open der naechsten Kerze) mit
   FadeVirtSchluss(m, px, nx.time) gegen pg_guard.known_time (Replikat) - je Modul alle Signale, GFT-Ersatz und Fremddaten.
2. Portfolio-Waechter: woertliche Uebertragung von FadePortfolioPF / FadeWaechterOk (Ringpuffer FADEHIST je Modul,
   Schluessel (Zeit*16 + Modul)*4096 + Platz, aufsteigend sortiert, rueckwaerts bis FadePortN Signale innerhalb FadeHistTage)
   gegen pg_guard.port_live_ea - fuer jedes Signal der Kette (Fremddaten bis 2021 + GFT-Ersatz ab 2022, Grid-Regel S wie 6.20).
3. Schutz gueltiger Tage: Entscheidung des EA (GueltigSchutzPruefen) gegen die Replikat-Bedingung (eng8, vp_on 3) auf einem
   Raster von Zustaenden.
Aufruf: python t_port_640.py   (Protokoll: ergebnisse/t_port_640.txt)"""
import numpy as np, math, os, sys
import gsig as G, cands as K, pg_blocks as PB, pg_guard as PGd, x41, streams as ST


def atr_mql(d1t, d1h, d1l, d1c, rs):
    """wie t_port.atr_mql (FadeAtr: iBarShift + CopyRates(sh+1, 15))."""
    k = np.searchsorted(d1t, rs, side="right") - 1
    if k - 15 < 0:
        return 0.0
    idx = list(range(k - 15, k))
    s = 0.0
    for i in range(1, 15):
        a, b = idx[i], idx[i - 1]
        s += max(d1h[a], d1c[b]) - min(d1l[a], d1c[b])
    return s / 14.0

FADEHIST = 256
LOG = []


def say(s):
    print(s, flush=True); LOG.append(s)


# ------------------------------------------------------------------ 1. Zeitpunkt der virtuellen Ergebnisse
def port_known(sym, r0, L, tlen, xoff, buf, tgt, dirs, mx=0.6, mn=0.0):
    """wie t_port.port (FadeKerze 6.00), zusaetzlich der Zeitpunkt nx.time, zu dem FadeVirtSchluss das Ergebnis verbucht."""
    D = G._D[sym] if G._D is not None else G.data()[sym]
    ny = D["ny"]; o, h, l, c, sp = D["o"], D["h"], D["l"], D["c"], D["sp"]
    d1 = D["d1"]; d1t, d1h, d1l, d1c = d1["t"], d1["h"], d1["l"], d1["c"]
    comm = G.COMM[G.SYM[sym]] / G.MPP[G.SYM[sym]]
    st = dict(day=None, nbar=0, hh=-1e300, ll=1e300, ready=False, done=False, skip=False, rng=0.0, exHi=0.0, exLo=0.0)
    v = None; out = []

    def zeiten(Dt):
        rs = Dt * 1440 + r0; re = rs + L; te = re + tlen
        xm = min(re + tlen + xoff, Dt * 1440 + 1000)
        if xm <= te: te = xm - 5
        return rs, re, te, xm

    def schluss(px, t_nx):                               # FadeVirtSchluss(m, px, nx.time)
        out.append((int(ny[v["iB"]]), ((px - v["ent"]) * v["d"] - comm) / v["rd"], int(t_nx)))

    for j in range(len(ny) - 1):
        t, tn = int(ny[j]), int(ny[j + 1])
        if v is not None and j >= v["iB"]:
            if v["d"] > 0:
                slHit = l[j] <= v["sl"]; tpHit = h[j] >= v["tp"]
            else:
                slHit = h[j] + sp[j] >= v["sl"]; tpHit = l[j] + sp[j] <= v["tp"]
            if slHit:
                px = v["sl"]
                if v["d"] > 0 and o[j] < v["sl"]: px = o[j]
                if v["d"] < 0 and o[j] + sp[j] > v["sl"]: px = o[j] + sp[j]
                schluss(px, tn); v = None
            elif tpHit and j > v["iB"]:
                schluss(v["tp"], tn); v = None
        if v is not None and tn >= v["xm"]:
            px = o[j + 1] if v["d"] > 0 else o[j + 1] + sp[j + 1]
            schluss(px, tn); v = None
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


def check_known():
    ok_all = True
    for ds in ("gft", "ext"):
        ST._use(ds)
        for nm in PB.F10:
            p = dict(K.FADES[nm]); sym = p.pop("sym"); dirs = p.pop("dirs"); mx = p.pop("mx", 0.6); mn = p.pop("mn", 0.0)
            got = port_known(sym, p["r0"], p["L"], p["tlen"], p["xoff"], p["buf"], p["tgt"], dirs, mx, mn)
            f = PB.fi(ds, nm)
            kt = PGd.known_time(ds, f)
            ref = list(zip(f["t_entry"].tolist(), f["R"].tolist(), kt.tolist()))
            ST._use(ds)
            # Zuordnung ueber die Einstiegszeit; bekannte Ausnahme (Bericht 6.00, t_port.py): Signale am ersten Tag mit
            # Tages-ATR am Datenbeginn (21.01.2022 im GFT-Ersatz) - live hat MT5 genug D1-Historie
            start_d = int(G.data()["XAU"]["ny"][0] // 1440) if ds == "gft" else -1
            rr = {a[0]: a for a in ref}; gg = {b[0]: b for b in got}
            only_r = [k for k in rr if k not in gg]; only_g = [k for k in gg if k not in rr]
            diff = [k for k in rr if k in gg and not (abs(rr[k][1] - gg[k][1]) < 1e-9 and rr[k][2] == gg[k][2])]
            known = [k for k in only_r + only_g if ds == "gft" and k // 1440 - start_d <= 20]
            n_ok = not diff and len(only_r) + len(only_g) == len(known)
            ok_all &= n_ok
            extra = f" (ausser {len(known)} Signal(en) am Datenbeginn {np.datetime64(int(known[0]), 'm')}, ATR ohne Vorlauf)" if known else ""
            if not n_ok:
                say(f"  {ds} {nm}: Referenz {len(ref)}, Port {len(got)} -> ABWEICHUNG nur Referenz {only_r[:3]} nur Port {only_g[:3]} R/Zeit {diff[:3]}")
            else:
                say(f"  {ds} {nm:7s}: {len(ref):5d} Signale, Einstieg/R/Zeitpunkt des Ergebnisses identisch{extra}")
    return ok_all


# ------------------------------------------------------------------ 2. Portfolio-Waechter
def ea_port_pf(bufs, tSig, N, hist_days):
    """FadePortfolioPF (MQL5) woertlich: bufs[m] = Liste (t, R) des Ringpuffers (aelteste zuerst, hoechstens FADEHIST)."""
    keys = []
    for m, b in enumerate(bufs):
        nh = len(b)
        for i in range(nh):                                     # Platz wie im Ringpuffer (ph - 1 - i), hier Listenindex
            slot = nh - 1 - i
            t, r = b[slot]
            if t <= 0 or t >= tSig:
                continue
            keys.append(((t * 16 + m) * 4096 + slot, m, slot))
    if not keys:
        return 0.0, 0
    keys.sort()
    tMin = tSig - hist_days * 1440
    pos = neg = 0.0; n = 0
    for k, m, slot in reversed(keys):
        if n >= N:
            break
        if (k // 4096) // 16 < tMin:
            break
        r = bufs[m][slot][1]
        if r > 0: pos += r
        else: neg -= r
        n += 1
    if n == 0:
        return 0.0, 0
    return (pos / neg if neg > 0 else 9.9), n


def check_port(N=200, th=1.15, hist_days=600):
    """Kette wie pg_guard.blocks_port (Grid-Regel S, N1800 ohne Grid): EA-Entscheidung je Signal gegen port_live_ea."""
    rule = x41.S70_OHNE
    exempt = set(rule.get("exempt", ()))
    mods = []
    for nm in PB.F10:
        per = {}
        for ds in ("ext", "gft"):
            f = PB.fi(ds, nm)
            keep, live, tp, w = PB.apply_rule(f, rule if nm not in exempt else dict(kind="none"))
            per[ds] = (f, keep)
        f1, k1 = per["ext"]; f2, k2 = per["gft"]
        v1 = (f1["t_entry"] < ST.LIM22) & k1
        mods.append(dict(te=np.r_[f1["t_entry"][v1], f2["t_entry"][k2]], kt=np.r_[PGd.known_time("ext", f1)[v1], PGd.known_time("gft", f2)[k2]],
                         R=np.r_[f1["R"][v1], f2["R"][k2]]))
    te_all = np.concatenate([m["te"] for m in mods]); kt_all = np.concatenate([m["kt"] for m in mods])
    R_all = np.concatenate([m["R"] for m in mods]); mi_all = np.concatenate([np.full(len(m["R"]), i) for i, m in enumerate(mods)])
    ref = PGd.port_live_ea(te_all, kt_all, mi_all, R_all, N, th, hist_days)
    # EA: Ereignisse in Zeitfolge - Ergebnisse (kt) in die Ringpuffer, Entscheidungen bei jedem Signal (te)
    ev = [(int(kt_all[i]), 0, int(mi_all[i]), i) for i in range(len(R_all))] + [(int(te_all[i]), 1, int(mi_all[i]), i) for i in range(len(R_all))]
    ev.sort(key=lambda x: (x[0], x[1], x[2]))
    bufs = [[] for _ in mods]
    got = np.zeros(len(R_all), bool); n_used = np.zeros(len(R_all), int)
    for t, kind, m, i in ev:
        if kind == 0:                                           # FadeVirtSchluss: Ergebnis verbuchen (Ringpuffer)
            bufs[m].append((t, float(R_all[i])))
            if len(bufs[m]) > FADEHIST:
                bufs[m].pop(0)
        else:                                                   # FadeLive -> FadeWaechterOk(m, tSig)
            pf, n = ea_port_pf(bufs, t, N, hist_days)
            got[i] = (n >= N and pf > th)
            n_used[i] = n
    same = np.array_equal(ref, got)
    yrs = lambda sel: f"{int(sel.sum())} von {len(sel)}"
    pre = te_all < ST.LIM22
    say(f"  Portfolio-Waechter PF{N} > {th}: {len(R_all)} Signale (Fremddaten bis 2021 + GFT-Ersatz), live nach Replikat "
        f"{yrs(ref)}, nach EA {yrs(got)} -> {'IDENTISCH' if same else 'ABWEICHUNG'} "
        f"(bis 2021 live {int(ref[pre].sum())}, ab 2022 live {int(ref[~pre].sum())})")
    if not same:
        idx = np.nonzero(ref != got)[0][:5]
        for i in idx:
            say(f"    Signal {i}: Modul {mi_all[i]}, Einstieg {np.datetime64(int(te_all[i]), 'm')}, Replikat {ref[i]}, EA {got[i]}, n {n_used[i]}")
    return same


# ------------------------------------------------------------------ 3. Schutz gueltiger Tage
def check_schutz():
    """EA: GueltigSchutz && kBereit && kCycleStart > 0 && kValidDays < NeedValidDays && GueltigHeuteReal() >= Schwelle.
    Replikat (eng8, vp_on 3): day_had and day_real >= needday and valid_days < needvalid (Zyklus laeuft: day_real > 0 nur
    nach einem Trade im Zyklus)."""
    ok = True; n = 0
    schwelle = 10000 * 0.005 + 0.5
    for valid in range(0, 7):
        for real in (-80.0, 0.0, 30.0, 50.49, 50.5, 50.51, 75.0, 200.0):
            for cyc in (0, 1):
                ea = bool(cyc > 0 and valid < 5 and real >= schwelle)
                day_had = real != 0.0
                rep = bool(cyc > 0 and day_had and real >= 50.5 and valid < 5)
                ok &= (ea == rep); n += 1
    say(f"  Schutz gueltiger Tage: {n} Zustaende, Entscheidung EA = Replikat: {'IDENTISCH' if ok else 'ABWEICHUNG'}")
    return ok


if __name__ == "__main__":
    say("1. Zeitpunkt der virtuellen Fade-Ergebnisse (FadeKerze -> FadeVirtSchluss(m, px, nx.time) gegen pg_guard.known_time)")
    ok1 = check_known()
    say("2. Portfolio-Waechter (FadePortfolioPF/FadeWaechterOk gegen pg_guard.port_live_ea)")
    ok2 = check_port(200, 1.15) & check_port(200, 1.2) & check_port(100, 1.1)
    say("3. Schutz gueltiger Tage")
    ok3 = check_schutz()
    say("GESAMT " + ("IDENTISCH" if (ok1 and ok2 and ok3) else "ABWEICHUNG"))
    os.makedirs("ergebnisse", exist_ok=True)
    open(os.path.join("ergebnisse", "t_port_640.txt"), "w").write("\n".join(LOG) + "\n")
