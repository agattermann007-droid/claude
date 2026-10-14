"""Einzelhandel mit DEADBAND-Ausstieg in R (fuer Familien allein und den Zufallsvergleich, PLAN 6.6).

Logik 1:1 wie das H1-Modul im EA (HandleSymbol, WochenendePruefen) in der Form, in der Replikat_v6/eng6.py sie fuer die
DEADBAND-Plaetze rechnet (das ist der Kontomotor der Baseline, beide muessen gleich ausgehen):
  Einstieg   am Open der Einstiegskerze: Long zum Ask (Bid + Spread), Short zum Bid
  je M5-Kerze (Reihenfolge wie eng6):
    1. Freitag ab 16:45 NY (Kerzenbeginn): am Open schliessen, Wiederaufnahme vormerken
    2. Sonntag ab 18:00 NY oder Montag: Wiederaufnahme am Open, wenn Stop/Ziel nicht uebersprungen (sonntags vor
       19:00 nur bei Spread <= 0,15 R);
       neuer Stop = alter Stop, hoechstens 2 R vom neuen Einstieg; danach kein Teilverkauf mehr
    3. Stop vor Ziel; Luecke ueber den Stop -> Open
    3a. Zeit-Exit: am Open der ersten Kerze der 193. M15-Kerze ab der Einstiegskerze (EA: iBarShift >= 192 beim
        ersten Tick der neuen Kerze; eng6-Generikstrom: t_exit = zeit_ausstieg_ny)
    4. sonst Tp1 (1,5 R): 50 % zum Tp1-Kurs, Stop auf Einstieg + 0,05 R
  Kosten: Spread in den Kursen, Kommission je Lot nur beim Eingang (auch bei der Wiederaufnahme), Swap beim
          Tageswechsel 17:00 NY je offenem Tag (3-fach am Dreifach-Tag), alles in R = $ / (Stop-Abstand * Geld je Preis).
Bewusst wie eng6 (nicht wie der EA): Tp1 schon in der Einstiegskerze (EA: erst nach 130 s), kein 144-h-Wanduhr-Exit.
Abweichung von eng6-DEADBAND-Plaetzen (nicht vom EA): dort Zeit-Exit am Schluss der ersten M5 der 193. M15-Kerze.

Ergebnisspalten (ERG): R netto, R brutto, Ausstiegskerze, Haltedauer in Minuten, Vorlauf (MFE) in R, Grund, Teile
Grund: 1 Stop, 2 Ziel, 3 Zeit, 4 Wiederaufnahme entfallen, 5 Datenende
"""
import numpy as np
from numba import njit

ERG = ["r", "r_brutto", "aus_i", "halte_min", "mfe", "grund", "teile"]


def markt_arrays(ny, o, h, l, c, sp):
    """Hilfsfelder je M5-Kerze: M15-Gruppe, Wochentag (0 = So, NY), NY-Stunde, Prop-Tag, Wochentag des Prop-Tags."""
    ny = np.asarray(ny, np.int64)
    grp15 = np.unique(ny // 15, return_inverse=True)[1].astype(np.int64)
    dow = ((ny // 1440 + 4) % 7).astype(np.int64)
    nyh = (ny % 1440) / 60.0
    pday = (ny + 420) // 1440
    pdow = ((pday + 4) % 7).astype(np.int64)
    return dict(ny=ny, o=np.asarray(o, float), h=np.asarray(h, float), l=np.asarray(l, float), c=np.asarray(c, float),
                sp=np.asarray(sp, float), grp15=grp15, dow=dow, nyh=nyh, pday=pday.astype(np.int64), pdow=pdow)


@njit(cache=True)
def _swap_r(modus, satz, preis, kontrakt, punkt, rd, mpp):
    if modus == 1:            # Punkte
        return satz * punkt * kontrakt / (rd * mpp)
    if modus == 2:            # % p. a. vom Eroeffnungspreis
        return preis * kontrakt * satz / 100.0 / 360.0 / (rd * mpp)
    return 0.0


@njit(cache=True)
def simuliere(ny, o, h, l, c, sp, grp15, dow, nyh, pday, pdow,
              ein_i, richtung, rd, ziel_r,
              tp1r, tp1f, be_r, maxhold15, we_an, we_schluss, we_stopmax_r, we_spread_r,
              kommission, mpp, kontrakt, punkt, swap_modus, swap_long, swap_short, swap_dreifach, swap_jeden_tag):
    """Je Einstieg (ein_i, richtung, rd = Stop-Abstand in Preis, ziel_r = Endziel in R) eine Ergebniszeile (ERG)."""
    n = ein_i.shape[0]
    nb = o.shape[0]
    out = np.zeros((n, 7))
    for t in range(n):
        i0 = ein_i[t]; d = richtung[t]; r = rd[t]
        if i0 < 0 or i0 >= nb or r <= 0.0:
            out[t, 5] = -1.0
            continue
        satz = swap_long if d > 0 else swap_short
        ent = o[i0] + (sp[i0] if d > 0 else 0.0)
        ref = ent
        sl = ent - d * r
        tp = ent + d * ziel_r * r if ziel_r > 0.0 else 0.0
        anteil = 1.0                     # offener Anteil der Position
        t1 = tp1r <= 0.0
        be = False
        m15 = grp15[i0]
        kosten = kommission / (r * mpp)
        brutto = 0.0
        mfe = 0.0
        offen = True
        wartet = False
        w_fri = 0
        teile = 1
        grund = 5
        aus = nb - 1
        tag = pday[i0]
        i = i0
        erst = True
        while i < nb:
            # Tageswechsel 17:00 NY: Swap fuer die offene Position (Tag, der gerade endet)
            if pday[i] != tag:
                if offen:
                    k = pday[i] - tag
                    for q in range(k):
                        wd = (pdow[i] - k + q + 7) % 7      # Wochentag des abgelaufenen Prop-Tags
                        if not swap_jeden_tag and (wd == 6 or wd == 0):
                            continue
                        m = 3.0 if wd == swap_dreifach else 1.0
                        kosten -= anteil * m * _swap_r(swap_modus, satz, ent, kontrakt, punkt, r, mpp)
                tag = pday[i]
            if not erst:
                # 1. Freitag-Schluss
                if we_an and offen and dow[i] == 5 and nyh[i] >= we_schluss:
                    px = o[i] + (sp[i] if d < 0 else 0.0)
                    brutto += anteil * (px - ent) * d / r
                    offen = False; wartet = True; w_fri = pday[i]; aus = i
                    i += 1
                    continue
                # Vormerkung verfaellt
                if wartet:
                    seit = pday[i] - w_fri
                    if (dow[i] >= 2 and dow[i] <= 4 and seit >= 3) or seit >= 6:
                        wartet = False; grund = 4
                        break
                # 2. Wiederaufnahme
                if wartet and ((dow[i] == 0 and nyh[i] >= 18.0) or dow[i] == 1) \
                        and not (we_spread_r > 0.0 and sp[i] > we_spread_r * r and dow[i] == 0 and nyh[i] < 19.0):
                    bid = o[i]; ask = bid + sp[i]
                    neu = ask if d > 0 else bid
                    chk = bid if d > 0 else ask
                    if (d > 0 and chk <= sl) or (d < 0 and chk >= sl):
                        wartet = False; grund = 4
                        break
                    if tp > 0.0 and ((d > 0 and chk >= tp) or (d < 0 and chk <= tp)):
                        wartet = False; grund = 4
                        break
                    if we_stopmax_r > 0.0:
                        eng = neu - d * we_stopmax_r * r
                        if (d > 0 and eng > sl) or (d < 0 and eng < sl):
                            sl = eng
                    ent = neu
                    kosten += kommission * anteil / (r * mpp)
                    t1 = True
                    offen = True; wartet = False; teile += 1
            erst = False
            if not offen:
                i += 1
                continue
            s5 = sp[i]
            if maxhold15 > 0 and grp15[i] - m15 >= maxhold15:          # 3a. Zeit-Exit am Open
                px = o[i] + (s5 if d < 0 else 0.0)
                brutto += anteil * (px - ent) * d / r
                grund = 3; aus = i; offen = False
                break
            if d > 0:
                hit_sl = l[i] <= sl
                hit_tp = tp > 0.0 and h[i] >= tp
                fav = (h[i] - ref) / r
            else:
                hit_sl = h[i] + s5 >= sl
                hit_tp = tp > 0.0 and l[i] + s5 <= tp
                fav = (ref - (l[i] + s5)) / r
            if fav > mfe:
                mfe = fav
            if hit_sl:
                px = sl
                if d > 0 and o[i] < sl:
                    px = o[i]
                if d < 0 and o[i] + s5 > sl:
                    px = o[i] + s5
                brutto += anteil * (px - ent) * d / r
                grund = 1; aus = i; offen = False
                break
            if hit_tp:
                brutto += anteil * (tp - ent) * d / r
                grund = 2; aus = i; offen = False
                break
            lvl = ref + d * tp1r * r
            t1hit = (h[i] >= lvl) if d > 0 else (l[i] + s5 <= lvl)
            if t1hit and not t1:
                t1 = True
                if tp1f > 0.0:
                    brutto += tp1f * (lvl - ent) * d / r
                    anteil -= tp1f
            if t1hit and not be:
                cand = ref + d * be_r * r
                if (cand - sl) * d > 0.0:
                    sl = cand
                be = True
            i += 1
        if offen:                                  # Datenende
            px = c[nb - 1] + (sp[nb - 1] if d < 0 else 0.0)
            brutto += anteil * (px - ent) * d / r
            aus = nb - 1; grund = 5
        out[t, 0] = brutto - kosten
        out[t, 1] = brutto
        out[t, 2] = aus
        out[t, 3] = ny[aus] - ny[i0]
        out[t, 4] = mfe
        out[t, 5] = grund
        out[t, 6] = teile
    return out


SWAPMODUS = {"keiner": 0, "punkte": 1, "zins_eroeffnung": 2}


def handel(M, sym, ein_i, richtung, rd, ziel_r, tp1r=1.5, tp1f=0.5, be_r=0.05, maxhold15=192, we_an=True,
           we_schluss=16.75, we_stopmax_r=2.0, we_spread_r=0.15):
    """Bequemer Aufruf mit markt_arrays M und spec.Symbol sym. ziel_r: Zahl oder je Einstieg. Rueckgabe (n, 7) nach ERG."""
    ein_i = np.asarray(ein_i, np.int64); richtung = np.asarray(richtung, np.int64); rd = np.asarray(rd, float)
    zr = np.full(len(ein_i), float(ziel_r)) if np.ndim(ziel_r) == 0 else np.asarray(ziel_r, float)
    return _handel_je_ziel(M, sym, ein_i, richtung, rd, zr, tp1r, tp1f, be_r, maxhold15, we_an, we_schluss, we_stopmax_r,
                           we_spread_r)


def _handel_je_ziel(M, sym, ein_i, richtung, rd, zr, tp1r, tp1f, be_r, maxhold15, we_an, we_schluss, we_stopmax_r,
                    we_spread_r):
    out = np.zeros((len(ein_i), 7))
    for z in np.unique(zr):
        m = zr == z
        out[m] = simuliere(M["ny"], M["o"], M["h"], M["l"], M["c"], M["sp"], M["grp15"], M["dow"], M["nyh"], M["pday"],
                           M["pdow"], ein_i[m], richtung[m], rd[m], float(z), tp1r, tp1f, be_r, int(maxhold15), bool(we_an),
                           float(we_schluss), float(we_stopmax_r), float(we_spread_r), sym.kommission_ein, sym.geld_je_preis(), sym.kontrakt,
                           sym.punkt, SWAPMODUS[sym.swap_modus], sym.swap_long, sym.swap_short, int(sym.swap_dreifach),
                           bool(sym.swap_jeden_tag))
    return out


def zeit_ausstieg_ny(M, ein_i, maxhold15=192):
    """t_exit fuer einen generischen eng6-Strom mit DEADBAND-Zeit-Exit: Beginn der ersten M5-Kerze der M15-Kerze
    ein+maxhold15 (eng6 schliesst generische Positionen am Open der Kerze t_exit - wie der EA beim ersten Tick)."""
    ein_i = np.asarray(ein_i, np.int64)
    g = M["grp15"]
    ziel = g[ein_i] + maxhold15
    j = np.searchsorted(g, ziel, side="left")
    nb = len(g)
    out = np.empty(len(ein_i), np.int64)
    for a in range(len(ein_i)):
        out[a] = M["ny"][j[a]] if j[a] < nb else M["ny"][-1] + 10_000_000      # Datenende: nie
    return out
