"""Replikat 9 - Signalgenerator der Fade-artigen Module von DEADBAND V8 (Build 8.10), Zeile fuer Zeile nach dem MQL5-Code.

Module (FADE_STANDARD + Sondermodule):
  typ 0 Listen-Fade  (FadeKerze)   typ 1 Spike S0830 (SpikeKerze)   typ 2 LW (LwKerze)
  typ 3 XA (AsiaKerze)             typ 4 TD (TdKerze)
Je Modul ein Durchlauf ueber die abgeschlossenen M5-Kerzen b mit Folgekerze nx (Einstieg am Open von nx), dazu der
virtuelle Trade (FadeVirtSchluss: Stop vor Ziel, Ziel nicht in der Einstiegskerze, Zeit-Ausstieg am Open der ersten Kerze
ab dem Ausstieg; Ergebnis in R abzueglich Kommission, bekannt ab dem Open der Folgekerze).
Probability Grid (GridKerze/GridFadeOk, M5, Laenge 15, 1000 Schenkel, mind. 30, Regel S 0,70) filtert das Signal ganz
(auch virtuell, GridNurLive=false). Portfolio-Waechter (FadePortfolioPF): PF der letzten 200 virtuellen Ergebnisse
aller Listen-Fades, die vor dem Signal feststanden und hoechstens 600 Tage alt sind, muss > 1,15 sein.

Zeiten: NY-Minuten seit Epoche (Server - 7 h). Kurse Bid; Long-Einstieg = Open + Spread (Ask).
"""
import numpy as np
from numba import njit

FADE_STANDARD = ("NAS,630,120,60,120,0.3,0,1,0.6,N1030;NAS,810,60,120,120,1.0,0,1,0.6,N1330;"
                 "XAU,390,120,180,240,1.0,1,-1,0.6,X0630;XAU,240,180,60,240,0.3,0,1,0.6,X0400;"
                 "NAS,-360,180,60,120,0.3,0,1,0.6,N1800;NAS,570,180,60,120,0.3,0,1,99,N0930;"
                 "NAS,660,90,60,240,0.6,1,1,0.6,N1100;NAS,780,90,60,120,0.6,0,1,0.6,N1300;"
                 "XAU,180,90,60,120,0.3,0,-1,0.6,X0300S;XAU,600,180,60,240,0.3,0,-1,0.6,X1000S")
GRID_OHNE = ("N1800",)
SCHUTZ_FREI = ("N1330", "N1300")
KOMM_PX = {"XAU": 5.0 / 100.0, "NAS": 0.0}        # Kommission Hin+Rueck je Lot / Geld je Preiseinheit und Lot
SYMI = {"XAU": 0, "NAS": 1}


def module_v8(spike=True, lw=True, asia=True, td=True, liste=FADE_STANDARD):
    """Moduldefinitionen wie FadeListeLesen + SpikeAnlegen + SonderAnlegen (Voreinstellungen 8.10)."""
    M = []
    for x in liste.split(";"):
        f = [y.strip() for y in x.split(",")]
        M.append(dict(name=f[9], sym=f[0], typ=0, r0=int(f[1]), L=int(f[2]), tlen=int(f[3]), xoff=int(f[4]),
                      buf=float(f[5]), tgt=int(f[6]), dir=int(f[7]), mx=float(f[8]), risk=0.75, minbuf=0.0,
                      grid=f[9] not in GRID_OHNE, frei=f[9] in SCHUTZ_FREI))
    if spike:   # SpikeStartNY 510, MessKerzen 2, WarteKerzen 6, KMin 0,20, StopATR 0,25, Ziel 0,5, Ausstieg 660, Richtung 1, Risiko 0,75
        L = 6 * 5
        M.append(dict(name="S0830", sym="NAS", typ=1, r0=510, L=L, tlen=5, xoff=660 - (510 + L + 5), buf=0.25, tgt=0, dir=1, mx=99.0,
                      risk=0.75, minbuf=0.0, grid=False, frei=False, mess=2, warte=6, kmin=0.20, ziel=0.5))
    if lw:      # LwStartNY 570, Sitzung 390, K 0,4, Ende 900, Ausstieg 960, Ziel 0, Richtung 0, Risiko 0,5, MinPuffer 4
        M.append(dict(name="LW", sym="NAS", typ=2, r0=570, L=900 - 570, tlen=5, xoff=960 - (900 + 5), buf=0.0, tgt=0, dir=0, mx=99.0,
                      risk=0.50, minbuf=4.0, grid=False, frei=False, sitz=390, k=0.4, zielr=0.0))
    if asia:    # AsiaEinNY -360, AusNY 180, Trend 288, StopATR 0,6, Ziel 1 R, Risiko 0,75
        M.append(dict(name="XA", sym="XAU", typ=3, r0=-360, L=5, tlen=5, xoff=180 - (-360) - 10, buf=0.6, tgt=0, dir=1, mx=99.0,
                      risk=0.75, minbuf=0.0, grid=False, frei=False, trend=288, zielr=1.0))
    if td:      # TdEinNY 840, AusNY 955, SchlussNY 960, MinATR 0,75, StopATR 0,3, Ziel 0, Richtung 1, Risiko 0,5
        M.append(dict(name="TD", sym="NAS", typ=4, r0=840, L=5, tlen=5, xoff=955 - 840 - 10, buf=0.3, tgt=0, dir=1, mx=99.0,
                      risk=0.50, minbuf=0.0, grid=False, frei=False, schluss=960, minatr=0.75, zielr=0.0))
    return M


# ------------------------------------------------------------------ ATR der Servertage (FadeAtr)
def atr_vor_tag(D1):
    """atr[j] = Mittel des True Range der 14 Servertage vor D1-Kerze j (CopyRates D1 ab Shift sh+1, 15 Kerzen)."""
    h, l, c = D1["h"], D1["l"], D1["c"]
    n = len(c)
    tr = np.full(n, np.nan)
    tr[1:] = np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1])
    out = np.zeros(n)
    cs = np.r_[0.0, np.cumsum(np.nan_to_num(tr))]
    for j in range(15, n):
        out[j] = (cs[j] - cs[j - 14]) / 14.0          # TR der Tage j-14 .. j-1
    return out


# ------------------------------------------------------------------ Probability Grid (je Symbol, M5)
@njit(cache=True)
def grid_bauen(o, c, L):
    n = len(c)
    bias = np.zeros(n, np.int64); pivPx = np.zeros(n); pivBar = np.full(n, -1, np.int64); curPx = np.zeros(n)
    legConf = np.zeros(n, np.int64); legDir = np.zeros(n, np.int64); legSz = np.zeros(n)
    nLeg = 0
    b = 0; cpx = 0.0; cbar = -1; ppx = 0.0; pbar = -1; lpx = 0.0; lbar = -1
    for i in range(n):
        if i == 0:
            cpx = c[0]; cbar = 0; lpx = c[0]; lbar = 0
        if i >= L - 1:
            up = -1e300; lo = 1e300
            for j in range(i - L + 1, i + 1):
                a = max(o[j], c[j]); z = min(o[j], c[j])
                if a > up:
                    up = a
                if z < lo:
                    lo = z
            mx = max(o[i], c[i]); mn = min(o[i], c[i])
            nb = b
            if mx == up:
                nb = 1
            elif mn == lo:
                nb = -1
            neu = False
            if nb != b and nb != 0:
                if b != 0:
                    neu = True; ppx = cpx; pbar = cbar
                cpx = up if nb == 1 else lo
                cbar = i; b = nb
            elif b != 0:
                alt = cpx
                cpx = max(up, cpx) if b == 1 else min(lo, cpx)
                if cpx != alt:
                    cbar = i
            if neu and lpx > 0.0:
                bd = pbar - lbar
                if bd != 0:
                    legConf[nLeg] = i; legDir[nLeg] = 1 if ppx > lpx else -1
                    legSz[nLeg] = abs(ppx - lpx) / lpx; nLeg += 1
                    lpx = ppx; lbar = pbar
        bias[i] = b; pivPx[i] = ppx; pivBar[i] = pbar; curPx[i] = cpx
    return bias, pivPx, pivBar, curPx, legConf[:nLeg].copy(), legDir[:nLeg].copy(), legSz[:nLeg].copy()


@njit(cache=True)
def _grid_rang(legConf, legDir, legSz, i, d, x, maxS):
    lo = 0; hi = len(legConf) - 1; q0 = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if legConf[mid] <= i:
            q0 = mid; lo = mid + 1
        else:
            hi = mid - 1
    n = 0; cnt = 0
    q = q0
    while q >= 0 and n < maxS:
        if legDir[q] == d:
            n += 1
            if legSz[q] <= x:
                cnt += 1
        q -= 1
    return (cnt / n if n > 0 else 0.0), n


@njit(cache=True)
def grid_ok(bias, pivPx, pivBar, curPx, legConf, legDir, legSz, i, d, st, maxS, minS, maxStop):
    """GridFadeOk mit i = letzte abgeschlossene M5-Kerze vor dem Einstieg. True = handeln."""
    if i < 0 or bias[i] == 0 or pivBar[i] < 0 or pivPx[i] <= 0.0:
        return True
    b = bias[i]
    if d == b:
        return True
    ext = abs(curPx[i] - pivPx[i]) / pivPx[i]
    pe, n = _grid_rang(legConf, legDir, legSz, i, b, ext, maxS)
    if n < minS:
        return True
    if maxStop > 0.0:
        xs = abs(st - pivPx[i]) / pivPx[i]
        sJ = 1.0 - pe
        r2, n2 = _grid_rang(legConf, legDir, legSz, i, b, xs, maxS)
        sS = 1.0 - r2
        ch = sS / sJ if sJ > 0.0 else 0.0
        if ch >= maxStop:
            return False
    return True


# ------------------------------------------------------------------ ein Modul ueber alle M5-Kerzen
@njit(cache=True)
def _fadezeiten(r0, L, tlen, xoff, Dt):
    rs = Dt * 1440 + r0
    re = rs + L
    te = re + tlen
    xm = min(re + tlen + xoff, Dt * 1440 + 1000)
    if xm <= te:
        te = xm - 5
    return rs, re, te, xm


@njit(cache=True)
def _atr_at(d1key, atrj, ny):
    day = (ny + 420) // 1440
    j = np.searchsorted(d1key, day, side="right") - 1
    if j < 15:
        return 0.0
    return atrj[j]


@njit(cache=True)
def modul_lauf(typ, r0, L, tlen, xoff, buf, tgt, mdir, mx, p1, p2, p3, p4, tgtmode, lw_ab,
               ny, o, h, l, c, sp, d1key, atrj, komm,
               use_grid, g_bias, g_pivPx, g_pivBar, g_curPx, g_legConf, g_legDir, g_legSz):
    """Rueckgabe: Signal-Matrix S (je Zeile: i_sig, i_entry, t_entry, dir, ent, st, goal, xm, rd, hh, ll, exHi, exLo, rng, atr,
    R_virt, t_known, x_px, x_kind) und Zahl der vom Grid gesperrten Signale.
    p1..p4 je typ: Spike (mess, warte, kmin, ziel), LW (sitz, k, zielr, -), XA (trend, zielr, -, -), TD (schluss, minatr, zielr, -).
    V9-Testoptionen: tgtmode (Listen-Fades) 0 = V8 (Mitte bzw. Gegenseite), 1 = mindestens 0,6 R, 2 = Gegenseite,
    3 = halb an der Mitte, Rest bis zur Gegenseite mit Einstand (+0,05 R); lw_ab = erste NY-Minute einer LW-Signalkerze (0 = V8)."""
    n = len(ny)
    S = np.zeros((n // 50 + 100, 21))
    ns = 0; ngrid = 0
    day = -10**9; nbar = 0; hh = -1e300; ll = 1e300; rng = 0.0; exHi = 0.0; exLo = 0.0
    ready = False; done = False; skip = False
    vOn = False; vDir = 0; vEnt = 0.0; vSl = 0.0; vTp = 0.0; vRd = 0.0; vBar = 0; vX = 0; vRow = -1
    vT1 = 0.0; vT1Done = False; vAcc = 0.0
    spP0 = 0.0; spDir = 0; spA = 0.0; spGoal = 0.0
    lwPH = 0.0; lwPL = 0.0; lwCH = -1e300; lwCL = 1e300; lwPN = 0; lwCN = 0
    tdLetzt = -1; tdVor = -1; tdRefTag = -1; tdRef = 0.0
    for i in range(n - 1):
        t = ny[i]; tn = ny[i + 1]
        # 1) virtueller Trade
        if vOn and t >= vBar:
            spb = sp[i]
            if vDir > 0:
                slHit = l[i] <= vSl; tpHit = h[i] >= vTp
            else:
                slHit = h[i] + spb >= vSl; tpHit = l[i] + spb <= vTp
            fr = 0.5 if vT1Done else 1.0               # V9 tgtmode 3: nach dem Teilziel laeuft die halbe Position
            if slHit:
                px = vSl
                if vDir > 0 and o[i] < vSl:
                    px = o[i]
                if vDir < 0 and o[i] + spb > vSl:
                    px = o[i] + spb
                vOn = False
                S[vRow, 15] = (vAcc + fr * (px - vEnt) * vDir - komm) / vRd; S[vRow, 16] = tn; S[vRow, 17] = px; S[vRow, 18] = 1
            elif tpHit and t > vBar:
                if vT1 > 0.0 and not vT1Done:              # Teilziel in derselben Kerze ebenfalls erreicht
                    vAcc = 0.5 * (vT1 - vEnt) * vDir; fr = 0.5
                vOn = False
                S[vRow, 15] = (vAcc + fr * (vTp - vEnt) * vDir - komm) / vRd; S[vRow, 16] = tn; S[vRow, 17] = vTp; S[vRow, 18] = 2
            elif vT1 > 0.0 and not vT1Done and t > vBar:
                t1Hit = (h[i] >= vT1) if vDir > 0 else (l[i] + spb <= vT1)
                if t1Hit:
                    vT1Done = True; vAcc = 0.5 * (vT1 - vEnt) * vDir
                    nsl = vEnt + vDir * 0.05 * vRd
                    if (nsl - vSl) * vDir > 0.0:
                        vSl = nsl
        if vOn and tn >= vX:
            fr = 0.5 if vT1Done else 1.0
            px = o[i + 1] if vDir > 0 else o[i + 1] + sp[i + 1]
            vOn = False
            S[vRow, 15] = (vAcc + fr * (px - vEnt) * vDir - komm) / vRd; S[vRow, 16] = tn; S[vRow, 17] = px; S[vRow, 18] = 3
        d = 0; ent = 0.0; st = 0.0; goal = 0.0; r = 0.0; xmS = 0; a = 0.0; t1 = 0.0
        if typ == 0:
            Dt = (t - r0) // 1440
            rs, re, te, xm = _fadezeiten(r0, L, tlen, xoff, Dt)
            if Dt != day:
                day = Dt; nbar = 0; hh = -1e300; ll = 1e300; ready = False; done = False; skip = False
            dow = ((Dt + 4) % 7 + 7) % 7
            if dow < 1 or dow > 5:
                continue
            if t >= rs and t < re:
                nbar += 1
                if h[i] > hh:
                    hh = h[i]
                if l[i] < ll:
                    ll = l[i]
                continue
            if t < re or done or skip:
                continue
            if not ready:
                a0 = _atr_at(d1key, atrj, rs)
                rng = hh - ll
                if nbar < (L // 5) * 0.6 or not (a0 > 0.0) or rng <= 0.0 or rng > mx * a0:
                    skip = True
                    continue
                exHi = hh; exLo = ll; ready = True; spA = a0
            if t >= te:
                done = True
                continue
            if h[i] > exHi:
                exHi = h[i]
            if l[i] < exLo:
                exLo = l[i]
            if h[i] > hh and c[i] < hh and c[i] > ll:
                d = -1
            elif l[i] < ll and c[i] > ll and c[i] < hh:
                d = 1
            if d == 0:
                if c[i] > hh or c[i] < ll:
                    done = True
                continue
            done = True
            if mdir != 0 and d != mdir:
                continue
            if tn >= xm:
                continue
            ent = o[i + 1] + (sp[i + 1] if d > 0 else 0.0)
            st = (exLo - buf * rng) if d > 0 else (exHi + buf * rng)
            goal = 0.5 * (hh + ll) if tgt == 0 else (hh if d > 0 else ll)
            r = (ent - st) * d
            g = (goal - ent) * d
            if r <= 0.0 or g <= 0.0:
                continue
            t1 = 0.0
            if tgtmode == 1 and g < 0.6 * r:                 # V9-Test: Ziel mindestens 0,6 R
                goal = ent + d * 0.6 * r
            elif tgtmode == 2:                               # V9-Test: Gegenseite der Range
                goal = hh if d > 0 else ll
            elif tgtmode == 3:                               # V9-Test: halb an der Mitte, Rest an der Gegenseite
                mid = 0.5 * (hh + ll)
                goal = hh if d > 0 else ll
                if (mid - ent) * d > 0.0 and (goal - mid) * d > 0.0:
                    t1 = mid
            if use_grid:
                if not grid_ok(g_bias, g_pivPx, g_pivBar, g_curPx, g_legConf, g_legDir, g_legSz, i, d, st, 1000, 30, 0.70):
                    ngrid += 1
                    continue
            xmS = xm; a = spA
        elif typ == 1:                         # Spike S0830
            mess = int(p1); warte = int(p2); kmin = p3; ziel = p4
            Dt = (t - r0) // 1440
            rs, re, te, xm = _fadezeiten(r0, L, tlen, xoff, Dt)
            if Dt != day:
                day = Dt; nbar = 0; hh = -1e300; ll = 1e300; ready = False; done = False; skip = False
                spP0 = 0.0; spDir = 0; spA = 0.0; spGoal = 0.0
            dow = ((Dt + 4) % 7 + 7) % 7
            if dow < 1 or dow > 5:
                continue
            if done or skip or t < rs:
                continue
            if t >= re:
                done = True
                continue
            if nbar == 0:
                if t != rs:
                    skip = True
                    continue
                spP0 = o[i]
            elif t != rs + 5 * nbar:
                skip = True
                continue
            nbar += 1
            if h[i] > hh:
                hh = h[i]
            if l[i] < ll:
                ll = l[i]
            if nbar == mess:
                a0 = _atr_at(d1key, atrj, rs)
                up = hh - spP0; dn = spP0 - ll
                dd = -1 if up >= dn else 1
                mv = up if up >= dn else dn
                if not (a0 > 0.0) or mv < kmin * a0 or (mdir != 0 and dd != mdir):
                    skip = True
                    continue
                spDir = dd; spA = a0
            if tn != re or nbar < mess:
                continue
            done = True
            if nbar != warte or spDir == 0 or tn >= xm:
                continue
            d = spDir
            ex = ll if d > 0 else hh
            goal = ex + d * ziel * abs(ex - spP0)
            ent = o[i + 1] + (sp[i + 1] if d > 0 else 0.0)
            st = ex - d * buf * spA
            r = (ent - st) * d
            g = (goal - ent) * d
            if r <= 0.0 or g <= 0.0:
                continue
            rng = abs(ex - spP0); xmS = xm; a = spA
        elif typ == 2:                         # Larry Williams
            sitz = int(p1); kk = p2; zielr = p3
            Dt = (t - r0) // 1440
            rs, re, te, xm = _fadezeiten(r0, L, tlen, xoff, Dt)
            if Dt != day:
                if lwCN >= 12:
                    lwPH = lwCH; lwPL = lwCL; lwPN = lwCN
                lwCH = -1e300; lwCL = 1e300; lwCN = 0
                day = Dt; nbar = 0; ready = False; done = False; skip = False
                spP0 = 0.0; spA = 0.0; spGoal = 0.0; rng = 0.0
            if t >= rs and t < rs + sitz:
                lwCN += 1
                if h[i] > lwCH:
                    lwCH = h[i]
                if l[i] < lwCL:
                    lwCL = l[i]
            dow = ((Dt + 4) % 7 + 7) % 7
            if dow < 1 or dow > 5:
                continue
            if done or skip:
                continue
            if t == rs:
                spA = _atr_at(d1key, atrj, rs)
                if lwPN < 12 or not (spA > 0.0) or lwPH - lwPL <= 0.0:
                    skip = True
                    continue
                spP0 = o[i]; rng = lwPH - lwPL; ready = True
            if not ready:
                if t > rs:
                    skip = True
                continue
            if t >= re:
                done = True
                continue
            if lw_ab > 0 and (t - Dt * 1440) < lw_ab:       # V9-Test: LW-Signalkerzen erst ab lw_ab (9:35 -> Einstieg ab 9:40)
                continue
            up = spP0 + kk * rng; dn = spP0 - kk * rng
            d = 1 if c[i] > up else (-1 if c[i] < dn else 0)
            if d == 0:
                continue
            done = True
            if mdir != 0 and d != mdir:
                continue
            if tn >= xm:
                continue
            ent = o[i + 1] + (sp[i + 1] if d > 0 else 0.0)
            st = 0.5 * (spP0 + ent)
            r = (ent - st) * d
            if r <= 0.05 * spA:
                continue
            goal = ent + d * zielr * r if zielr > 0.0 else 0.0
            hh = up; ll = dn; xmS = xm; a = spA
        elif typ == 3:                         # Gold-Asien-Halten
            trend = int(p1); zielr = p2
            Dn = (tn - r0) // 1440
            tgtT = Dn * 1440 + r0
            if not (t < tgtT and tn >= tgtT and tn - tgtT <= 10):
                continue
            rs, re, te, xm = _fadezeiten(r0, L, tlen, xoff, Dn)
            if Dn != day:
                day = Dn; nbar = 0; ready = False; done = False; skip = False; spGoal = 0.0
            dow = ((Dn + 4) % 7 + 7) % 7
            if dow < 1 or dow > 5 or done:
                continue
            done = True
            if tn >= xm:
                continue
            if trend > 0:
                if i + 1 < trend:
                    continue
                s_ = 0.0
                for q in range(i - trend + 1, i + 1):
                    s_ += c[q]
                if c[i] <= s_ / trend:
                    continue
            a0 = _atr_at(d1key, atrj, tgtT)
            if not (a0 > 0.0):
                continue
            d = 1
            ent = o[i + 1] + sp[i + 1]
            r = buf * a0
            st = ent - d * r
            goal = ent + d * zielr * r if zielr > 0.0 else 0.0
            xmS = xm; a = a0
        else:                                  # Trend-Day
            schluss = int(p1); minatr = p2; zielr = p3
            Db = t // 1440
            dowb = ((Db + 4) % 7 + 7) % 7
            if Db != tdLetzt and dowb >= 1 and dowb <= 5:
                tdVor = tdLetzt; tdLetzt = Db
            mb = t - Db * 1440
            if mb < schluss and mb >= schluss - 60:
                tdRefTag = Db; tdRef = c[i]
            Dn = tn // 1440
            if tn - Dn * 1440 != r0:
                continue
            dow = ((Dn + 4) % 7 + 7) % 7
            if dow < 1 or dow > 5 or day == Dn:
                continue
            rs, re, te, xm = _fadezeiten(r0, L, tlen, xoff, Dn)
            day = Dn
            vor = tdVor if tdLetzt == Dn else tdLetzt
            if vor < 0 or tdRefTag != vor:
                continue
            if tn >= xm:
                continue
            a0 = _atr_at(d1key, atrj, Dn * 1440 + r0)
            if not (a0 > 0.0):
                continue
            rr = c[i] - tdRef
            if abs(rr) < minatr * a0 or rr == 0.0:
                continue
            d = 1 if rr > 0.0 else -1
            if mdir != 0 and d != mdir:
                continue
            ent = o[i + 1] + (sp[i + 1] if d > 0 else 0.0)
            r = buf * a0
            st = ent - d * r
            goal = ent + d * zielr * r if zielr > 0.0 else 0.0
            rng = rr; xmS = xm; a = a0
        if d == 0:
            continue
        # Signal + virtueller Trade (ueberschreibt einen noch offenen virtuellen Trade wie im EA)
        if ns >= S.shape[0]:
            S2 = np.zeros((S.shape[0] * 2, 21)); S2[:ns] = S[:ns]; S = S2
        S[ns, 0] = i; S[ns, 1] = i + 1; S[ns, 2] = tn; S[ns, 3] = d; S[ns, 4] = ent; S[ns, 5] = st; S[ns, 6] = goal
        S[ns, 7] = xmS; S[ns, 8] = r; S[ns, 9] = hh; S[ns, 10] = ll; S[ns, 11] = exHi; S[ns, 12] = exLo; S[ns, 13] = rng
        S[ns, 14] = a; S[ns, 15] = np.nan; S[ns, 16] = 0; S[ns, 17] = 0; S[ns, 18] = 0; S[ns, 19] = t1; S[ns, 20] = 0
        vOn = True; vDir = d; vEnt = ent; vSl = st; vRd = r; vBar = tn; vX = xmS; vRow = ns
        vT1 = t1; vT1Done = False; vAcc = 0.0
        if goal > 0.0:
            vTp = goal
        else:
            vTp = 1e300 if d > 0 else -1e300
        ns += 1
    return S[:ns].copy(), ngrid


SPALTEN = ("i_sig", "i_entry", "t_entry", "dir", "ent", "st", "goal", "xm", "rd", "hh", "ll", "exHi", "exLo", "rng", "atr",
           "R", "t_known", "x_px", "x_kind", "t1", "frei_")
SP = {n: i for i, n in enumerate(SPALTEN)}


def erzeuge(D, module=None, grid=True, tgtmode=0, lw_ab=0):
    """Alle Module rechnen. Rueckgabe: Liste von dicts (Moduldefinition + Signal-Spalten)."""
    if module is None:
        module = module_v8()
    pre = {}
    for s in ("XAU", "NAS"):
        d = D[s]
        G = grid_bauen(d["o"], d["c"], 15)
        pre[s] = dict(atr=atr_vor_tag(d["d1"]), key=d["d1"]["key"].astype(np.int64), G=G)
    out = []
    for m in module:
        s = m["sym"]; d = D[s]; G = pre[s]["G"]
        typ = m["typ"]
        p = {1: (m.get("mess", 0), m.get("warte", 0), m.get("kmin", 0.0), m.get("ziel", 0.0)),
             2: (m.get("sitz", 0), m.get("k", 0.0), m.get("zielr", 0.0), 0.0),
             3: (m.get("trend", 0), m.get("zielr", 0.0), 0.0, 0.0),
             4: (m.get("schluss", 0), m.get("minatr", 0.0), m.get("zielr", 0.0), 0.0)}.get(typ, (0, 0, 0.0, 0.0))
        S, ng = modul_lauf(typ, m["r0"], m["L"], m["tlen"], m["xoff"], m["buf"], m["tgt"], m["dir"], m["mx"],
                           float(p[0]), float(p[1]), float(p[2]), float(p[3]),
                           int(m.get("tgtmode", tgtmode)) if typ == 0 else 0, int(m.get("lw_ab", lw_ab)) if typ == 2 else 0,
                           d["ny"], d["o"], d["h"], d["l"], d["c"], d["sp"], pre[s]["key"], pre[s]["atr"], KOMM_PX[s],
                           bool(grid and m["grid"] and typ == 0), *G)
        r = dict(m)
        r.update({k: S[:, i] for k, i in SP.items()})
        for k in ("i_sig", "i_entry", "t_entry", "dir", "xm", "t_known", "x_kind"):
            r[k] = r[k].astype(np.int64)
        r["ngrid"] = int(ng)
        out.append(r)
    return out


# ------------------------------------------------------------------ Portfolio-Waechter (FadePortfolioPF)
def portfolio_pf(sigs, t_query, port_n=200, hist_tage=600):
    """PF und Zahl der letzten port_n virtuellen Ergebnisse aller Listen-Fades (typ 0), bekannt vor t_query, nicht
    aelter als hist_tage. Rueckgabe (pf, n) je Abfragezeit."""
    tk, R, mm = [], [], []
    for mi, s in enumerate(sigs):
        if s["typ"] != 0:
            continue
        ok = np.isfinite(s["R"]) & (s["t_known"] > 0)
        tk.append(s["t_known"][ok]); R.append(s["R"][ok]); mm.append(np.full(ok.sum(), mi))
    tk = np.concatenate(tk); R = np.concatenate(R); mm = np.concatenate(mm)
    order = np.lexsort((mm, tk))
    tk = tk[order]; R = R[order]
    pos = np.where(R > 0, R, 0.0); neg = np.where(R < 0, -R, 0.0)
    cp = np.r_[0.0, np.cumsum(pos)]; cn = np.r_[0.0, np.cumsum(neg)]
    t_query = np.asarray(t_query, np.int64)
    hi = np.searchsorted(tk, t_query, side="left")            # Ergebnisse mit t_known < t_query
    lo_t = np.searchsorted(tk, t_query - hist_tage * 1440, side="left")
    lo = np.maximum(hi - port_n, lo_t)
    n = hi - lo
    P_ = cp[hi] - cp[lo]; N_ = cn[hi] - cn[lo]
    pf = np.where(N_ > 0, P_ / np.where(N_ > 0, N_, 1.0), 9.9)
    pf = np.where(n > 0, pf, 0.0)
    return pf, n


def waechter(sigs, port_n=200, port_pf=1.15, hist_tage=600):
    """live-Flag je Signal (Listen-Fades: Portfolio-Waechter; Sondermodule immer)."""
    for s in sigs:
        if s["typ"] == 0:
            pf, n = portfolio_pf(sigs, s["t_entry"], port_n, hist_tage)
            s["pf"] = pf; s["npf"] = n
            s["live"] = (n >= port_n) & (pf > port_pf)
        else:
            s["pf"] = np.zeros(len(s["t_entry"])); s["npf"] = np.zeros(len(s["t_entry"]), np.int64)
            s["live"] = np.ones(len(s["t_entry"]), bool)
    return sigs
