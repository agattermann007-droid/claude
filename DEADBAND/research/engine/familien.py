"""Neue Einstiegsfamilien (PLAN.md Abschnitt 6, Steckbriefe). Startwerte sind vorab fest; Aenderung nur im Plateau-Test.

Alle Familien: Einstieg am Open der naechsten M15-Kerze (erste M5 darin), Stop 3 x ATR14 (M15) der Signalkerze,
Ausstieg wie DEADBAND (engine/handel.py). Rueckgabe je Familie: dict mit Feldern
  i5 (Einstieg, M5-Index), dir, rd (Stop-Abstand), j (Signalkerze M15), t_sig (NY-Minute Kerzenbeginn der Signalkerze)
"""
import numpy as np
import pandas as pd

START = dict(F1=dict(k=0.5), F2=dict(W=8, tau=0.1), F3=dict(m=0.6), F4=dict(N=20))


def _ergebnis(B, atr, js, dirs):
    js = np.asarray(js, np.int64); dirs = np.asarray(dirs, np.int64)
    ok = (js + 1 < len(B["t"])) & np.isfinite(atr[js]) & (atr[js] > 0)
    js, dirs = js[ok], dirs[ok]
    return dict(i5=B["first"][js + 1], dir=dirs, rd=3.0 * atr[js], j=js, t_sig=B["t"][js])


def _qualitaet(B, j, d, clsmin):
    rng = B["h"][j] - B["l"][j]
    cls = (B["c"][j] - B["l"][j]) / rng if rng > 0 else 0.5
    return cls >= clsmin if d > 0 else (1.0 - cls) >= clsmin


# ------------------------------------------------------------------ F1 Ereignis-Drift
KLASSEN = {"CPI": ("cpi",), "NFP": ("nonfarm-payrolls", "non-farm-payrolls", "nonfarm"),
           "PCE": ("pce",), "FOMC": ("fed-interest-rate-decision", "fomc-statement", "interest-rate-decision")}


def kalender_termine(kal_csv, klassen=("CPI", "NFP", "PCE", "FOMC"), ny_versatz_h=7):
    """Termine (NY-Minuten, Klasse) aus der Kalender-CSV von DEADBAND_Kalender_Export.mq5: Bedeutung hoch (3), genaue
    Uhrzeit (time_mode 0), Klassen nach Ereigniscode. Gleiche Uhrzeit = ein Termin."""
    k = pd.read_csv(kal_csv, sep="\t", encoding="utf-8", dtype=str)
    k = k[(k["importance"] == "3") & (k["time_mode"] == "0")]
    code = k["code"].fillna("").str.lower()
    klasse = pd.Series("", index=k.index)
    for kl in klassen:
        m = code.apply(lambda c: any(x in c for x in KLASSEN[kl]))
        if kl == "CPI":
            m &= ~code.str.contains("ppi")
        klasse[m & (klasse == "")] = kl
    k = k[klasse != ""].assign(klasse=klasse[klasse != ""])
    t = pd.to_datetime(k["server_time"], format="%Y.%m.%d %H:%M:%S") - pd.Timedelta(hours=ny_versatz_h)
    ny = t.values.astype("datetime64[m]").astype(np.int64)
    df = pd.DataFrame({"ny": ny, "klasse": k["klasse"].values}).drop_duplicates("ny").sort_values("ny")
    return df["ny"].to_numpy(np.int64), df["klasse"].to_numpy()


def f1_ereignis(d, atr, termine_ny, k=0.5):
    """Erste M15-Kerze, die zur Veroeffentlichung beginnt; Richtung = Vorzeichen Schluss - Eroeffnung, nur wenn
    |Schluss - Eroeffnung| >= k x ATR14 (M15) der Kerze davor (der Ausschlag selbst blaeht die Schwelle nicht auf).
    Einstieg am Open der Folgekerze (>= 15 min danach)."""
    B = d["m15"]
    js, dirs = [], []
    for T in termine_ny:
        j = int(np.searchsorted(B["t"], T))
        if j >= len(B["t"]) or B["t"][j] != T or j < 1:
            continue
        koerper = B["c"][j] - B["o"][j]
        a = atr[j - 1]
        if not (a > 0) or abs(koerper) < k * a or koerper == 0:
            continue
        js.append(j); dirs.append(1 if koerper > 0 else -1)
    return _ergebnis(B, atr, js, dirs)


# ------------------------------------------------------------------ F2 Bestaetigter Retest
def f2_retest(d, atr, h1sig, clsmin, sess=(3.0, 13.0), W=8, tau=0.1):
    """Nach einem H1-Ausbruchssignal (Kerze s, Session) innerhalb von W M15-Kerzen: Beruehrung der H1-Kante
    (Long: Tief <= Kante + tau x ATR), danach (oder in derselben Kerze) Schluss jenseits der Kante mit Kerzenqualitaet.
    Ungueltig bei Schluss jenseits der Gegenkante. Ein Retest je Ausbruchssignal; Ausbruchssignale, die waehrend eines
    laufenden Retest-Fensters entstehen, werden nicht doppelt gezaehlt."""
    B = d["m15"]
    n = len(B["t"])
    js, dirs = [], []
    belegt_bis = -1
    for a in np.argsort(h1sig["j"], kind="stable"):
        s = int(h1sig["j"][a])
        if h1sig["nyh"][a] < sess[0] or h1sig["nyh"][a] >= sess[1] or s <= belegt_bis:
            continue
        dd = int(h1sig["dir"][a])
        kante = h1sig["hH1"][a] if dd > 0 else h1sig["lH1"][a]
        gegen = h1sig["lH1"][a] if dd > 0 else h1sig["hH1"][a]
        beruehrt = False
        ende = min(n - 1, s + W)
        for j in range(s + 1, ende + 1):
            if (dd > 0 and B["c"][j] < gegen) or (dd < 0 and B["c"][j] > gegen):
                break
            tol = tau * atr[j - 1] if np.isfinite(atr[j - 1]) else 0.0
            if (dd > 0 and B["l"][j] <= kante + tol) or (dd < 0 and B["h"][j] >= kante - tol):
                beruehrt = True
            if beruehrt and ((dd > 0 and B["c"][j] > kante) or (dd < 0 and B["c"][j] < kante)) and _qualitaet(B, j, dd, clsmin):
                js.append(j); dirs.append(dd)
                break
        belegt_bis = ende
    return _ergebnis(B, atr, js, dirs)


# ------------------------------------------------------------------ F3 Asien-Spanne zur London-Eroeffnung
def _atr_d1_vor(d1, t_ny):
    """ATR14 der Servertage (SMA des TR) des letzten abgeschlossenen Servertags vor t_ny (wie FadeAtr im EA)."""
    key = (t_ny + 420) // 1440
    i = int(np.searchsorted(d1["key"], key)) - 1          # letzter Servertag vor dem Tag von t_ny
    if i < 14:
        return np.nan
    h, l, c = d1["h"][i - 14:i + 1], d1["l"][i - 14:i + 1], d1["c"][i - 14:i + 1]
    tr = np.maximum(h[1:], c[:-1]) - np.minimum(l[1:], c[:-1])
    return float(tr.mean())


def f3_asien(d, atr, clsmin, m=0.6, spanne=(-360, 180), fenster=(180, 300)):
    """Spanne = M15-Kerzen [Vortag 18:00, 03:00) NY; erste M15-Kerze mit Beginn in [03:00, 05:00) NY, die jenseits
    schliesst und Kerzenqualitaet >= clsmin hat. Nur Spannen <= m x ATR14 (D1). Ein Signal je NY-Tag (Mo-Fr)."""
    B = d["m15"]; d1 = d["d1"]
    t = B["t"]
    tage = np.unique(t // 1440)
    js, dirs = [], []
    for D in tage:
        dow = (D + 4) % 7
        if dow < 1 or dow > 5:
            continue
        a0 = np.searchsorted(t, D * 1440 + spanne[0]); a1 = np.searchsorted(t, D * 1440 + spanne[1])
        if a1 - a0 < int(0.6 * (spanne[1] - spanne[0]) / 15):
            continue
        hh = B["h"][a0:a1].max(); ll = B["l"][a0:a1].min()
        A = _atr_d1_vor(d1, D * 1440 + spanne[0])
        if not (A > 0) or hh - ll <= 0 or hh - ll > m * A:
            continue
        w0 = np.searchsorted(t, D * 1440 + fenster[0]); w1 = np.searchsorted(t, D * 1440 + fenster[1])
        for j in range(w0, w1):
            dd = 1 if B["c"][j] > hh else (-1 if B["c"][j] < ll else 0)
            if dd != 0 and _qualitaet(B, j, dd, clsmin):
                js.append(j); dirs.append(dd)
                break
    return _ergebnis(B, atr, js, dirs)


# ------------------------------------------------------------------ F4 Mehrtaegiger Trend (D1)
def f4_donchian(d, atr, N=20, sess_start_ny=180):
    """Servertag-Schluss (17:00 NY) ueber dem Hoch der vorherigen N Servertage -> Long (unter dem Tief -> Short),
    nur der erste Schluss jenseits nach einem Schluss innerhalb. Einstieg am Open der ersten M15-Kerze ab 03:00 NY des
    naechsten NY-Tags mit Kerzen; Stop 3 x ATR14 (M15) der Kerze davor."""
    B = d["m15"]; d1 = d["d1"]
    t = B["t"]
    c, h, l, key = d1["c"], d1["h"], d1["l"], d1["key"]
    js, dirs = [], []
    zustand = 0
    for i in range(N, len(c)):
        hoch = h[i - N:i].max(); tief = l[i - N:i].min()
        z = 1 if c[i] > hoch else (-1 if c[i] < tief else 0)
        if z != 0 and z != zustand:
            # Servertag key = NY 17:00 (Tag key-1) bis 17:00 (Tag key); Einstieg 03:00 NY des naechsten NY-Tags mit
            # Kerzen in der Session (Freitagsschluss -> Montag 03:00, nicht die Sonntags-Wiedereroeffnung)
            for D in range(int(key[i]) + 1, int(key[i]) + 6):
                j = int(np.searchsorted(t, D * 1440 + sess_start_ny))
                if j < len(t) and t[j] < D * 1440 + 13 * 60:
                    if j >= 1:
                        js.append(j - 1); dirs.append(z)
                    break
        zustand = z
    return _ergebnis(B, atr, js, dirs)
