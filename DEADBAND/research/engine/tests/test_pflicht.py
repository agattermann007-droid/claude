"""Pflichttests der Engine (Auftrag Stufe 0, Punkt 3) mit konstruierten Kerzen."""
import numpy as np
import pandas as pd
import pytest

from engine import daten as DT
from engine import handel as HD
from engine import spec as SP


def _ny(ts):
    """NY-Zeit 'YYYY-MM-DD HH:MM' -> NY-Minuten seit Epoche."""
    return int(np.datetime64(pd.Timestamp(ts).to_datetime64(), "m").astype(np.int64))


def _markt(start_ny, n, preis=2000.0, sp=0.3, schritt=0.0):
    """n M5-Kerzen ab start_ny (NY-Zeit), ohne Luecken; flacher Kurs (o=h=l=c) plus Schritt je Kerze."""
    ny = _ny(start_ny) + 5 * np.arange(n)
    c = preis + schritt * np.arange(n)
    o = np.r_[preis, c[:-1]]
    return dict(ny=ny, o=o.astype(float), h=np.maximum(o, c).astype(float), l=np.minimum(o, c).astype(float),
                c=c.astype(float), sp=np.full(n, sp))


def _sim(m, ein, d, rd, ziel=8.0, sym=SP.XAU, **kw):
    M = HD.markt_arrays(m["ny"], m["o"], m["h"], m["l"], m["c"], m["sp"])
    return HD.handel(M, sym, [ein], [d], [rd], ziel, **kw)[0]


# ---------------------------------------------------------------- 1. Lot-Rundung und Mindestlot-Filter
def test_lot_rundung_wie_normlot():
    assert SP.norm_lot(SP.XAU, 0.0349) == 0.03
    assert SP.norm_lot(SP.XAU, 0.035) == 0.04          # MathFloor(x/0.01 + 0.5): halbe Schritte runden auf
    assert SP.norm_lot(SP.XAU, 0.004) == 0.01          # unter Mindestlot -> Mindestlot (Filter entscheidet vorher)
    assert SP.norm_lot(SP.XAU, 250.0) == 100.0


def test_mindestlot_filter_und_budget():
    # Gold: Stop 6 $ -> 600 $ Risiko je Lot; Mindestlot 0,01 = 6 $
    assert SP.lots_fuer_risiko(SP.XAU, 3.5, 6.0, min_lot_tol=2.0) == 0.01        # 6 <= 2 * 3,5
    assert SP.lots_fuer_risiko(SP.XAU, 2.9, 6.0, min_lot_tol=2.0) == 0.0         # 6 > 2 * 2,9 -> Signal entfaellt
    assert SP.lots_fuer_risiko(SP.XAU, 25.9, 6.0) == 0.04                         # 0,0432 -> 0,04
    assert SP.lots_fuer_risiko(SP.XAU, 25.9, 6.0, budget_rest=20.0) == 0.03       # Budget kuerzt abwaerts (0,0333)
    assert SP.lots_fuer_risiko(SP.XAU, 25.9, 6.0, budget_rest=5.0) == 0.0         # Budget unter Mindestlot-Risiko


# ---------------------------------------------------------------- 2. Kommission nur auf den Eingangs-Deal
def test_kommission_nur_eingang():
    m = _markt("2024-03-05 04:00", 60, schritt=0.0)
    m["h"][10] += 20.0                                   # Endziel (8 R bei rd 2) erreicht -> zwei Ausstiege (Tp1 + Ziel)
    e = _sim(m, 2, 1, 2.0)
    assert e[5] == 2                                     # Ziel
    kom_r = 5.0 / (2.0 * 100.0)                          # 5 $/Lot bei 200 $ Risiko je Lot
    # Ein Ausstieg zum Tp1 und einer zum Ziel, Kommission genau einmal
    assert e[0] == pytest.approx(e[1] - kom_r)
    nas = _sim(_markt("2024-03-05 04:00", 60, preis=15000.0, sp=1.6), 2, 1, 50.0, sym=SP.NAS)
    assert nas[0] == pytest.approx(nas[1])               # NAS: keine Kommission


def test_kommission_nochmal_bei_wiederaufnahme():
    # Long Do 10:00 NY, Freitag 16:45 Schluss, Montag Wiederaufnahme, danach Stop
    ny = []
    t = _ny("2024-03-07 10:00")
    while t < _ny("2024-03-08 17:00"):
        if not (17 * 60 <= t % 1440 < 18 * 60):
            ny.append(t)
        t += 5
    t = _ny("2024-03-10 18:00")
    while t < _ny("2024-03-11 12:00"):
        if not (17 * 60 <= t % 1440 < 18 * 60):
            ny.append(t)
        t += 5
    ny = np.array(ny)
    n = len(ny)
    c = np.full(n, 2000.0)
    m = dict(ny=ny, o=c.copy(), h=c.copy(), l=c.copy(), c=c.copy(), sp=np.full(n, 0.3))
    j = int(np.searchsorted(ny, _ny("2024-03-11 08:00")))
    m["l"][j] = 1990.0                                   # Montag: Stop (rd 3) getroffen
    e = _sim(m, 0, 1, 3.0, sym=SP.XAU)
    assert e[6] == 2                                     # zwei Teile (vor und nach dem Wochenende)
    assert e[5] == 1
    swap = 1 * (-64.47 * 0.01 * 100.0) / (3.0 * 100.0)  # Do->Fr ein Swap (Do-Prop-Tag), Fr wird vorher geschlossen
    kom = 2 * 5.0 / (3.0 * 100.0)
    assert e[0] == pytest.approx(e[1] - kom + swap)


# ---------------------------------------------------------------- 3. Swap mit Mittwoch x3
def test_swap_mittwoch_dreifach():
    # Long Mi 10:00 NY gehalten bis Do 10:00 NY: Rollover Mi 17:00 NY = Ende des Mittwochs-Prop-Tags -> 3-fach
    m = _markt("2024-03-06 10:00", 288)
    e = _sim(m, 0, 1, 3.0, ziel=0.0, maxhold15=10_000)
    pro_nacht = -64.47 * 0.01 * 100.0 / (3.0 * 100.0)
    assert e[0] - e[1] == pytest.approx(3 * pro_nacht - 5.0 / 300.0)
    # Di 10:00 bis Mi 10:00: einfach
    m2 = _markt("2024-03-05 10:00", 288)
    e2 = _sim(m2, 0, 1, 3.0, ziel=0.0, maxhold15=10_000)
    assert e2[0] - e2[1] == pytest.approx(pro_nacht - 5.0 / 300.0)
    # NAS: % p. a. vom Eroeffnungspreis, short -1,5 %
    m3 = _markt("2024-03-05 10:00", 288, preis=15000.0, sp=1.6)
    e3 = _sim(m3, 0, -1, 50.0, ziel=0.0, maxhold15=10_000, sym=SP.NAS)
    erw = 15000.0 * 10.0 * -1.5 / 100.0 / 360.0 / (50.0 * 10.0)
    assert e3[0] - e3[1] == pytest.approx(erw)


# ---------------------------------------------------------------- 4. Einstieg am Open der Folgekerze
def test_einstieg_am_open_nicht_am_close():
    m = _markt("2024-03-05 04:00", 40)
    # Signalkerze 4 schliesst bei 2000, die Folgekerze 5 oeffnet 3 $ hoeher (Ausbruch laeuft weg)
    m["o"][5:] += 3.0; m["h"][5:] += 3.0; m["l"][5:] += 3.0; m["c"][5:] += 3.0
    e = _sim(m, 5, 1, 3.0, ziel=0.0, maxhold15=2)
    # Einstieg 2003 + 0,3 Spread; Zeit-Exit am Open der 3. M15-Kerze (Bid 2003) -> -0,3/3 = -0,1 R brutto
    assert e[1] == pytest.approx(-0.1)
    assert e[5] == 3


# ---------------------------------------------------------------- 5. Tageswechsel 17:00 NY
@pytest.mark.parametrize("server,tag_ny", [("2026-03-10 23:55:00", "2026-03-10"), ("2026-03-11 00:00:00", "2026-03-11"),
                                           ("2026-10-27 23:59:00", "2026-10-27"), ("2026-10-28 00:00:00", "2026-10-28")])
def test_tageswechsel_17_uhr_ny(server, tag_ny):
    """Serverzeit = NY + 7 h in allen Sommerzeit-Phasen (auch EU/US-Umstellungswochen): 00:00 Server = 17:00 NY."""
    ny = DT.ny_minuten(pd.Series([pd.Timestamp(server)]))
    pt = int(DT.prop_tag(ny)[0])
    assert np.datetime64(pt, "D") == np.datetime64(tag_ny)
    assert (ny[0] % 1440) in (16 * 60 + 55, 16 * 60 + 59, 17 * 60)


def test_swap_genau_beim_tageswechsel():
    m = _markt("2024-03-05 16:30", 6)             # 16:30-16:55 NY, kein Rollover
    e = _sim(m, 0, 1, 3.0, ziel=0.0, maxhold15=10_000)
    assert e[0] - e[1] == pytest.approx(-5.0 / 300.0)
    m2 = _markt("2024-03-05 16:30", 20)            # ueber 17:00 NY hinaus (Tagespause hier ohne Luecke)
    e2 = _sim(m2, 0, 1, 3.0, ziel=0.0, maxhold15=10_000)
    assert e2[0] - e2[1] == pytest.approx(-64.47 / 300.0 - 5.0 / 300.0)


# ---------------------------------------------------------------- weitere Regeln
def test_stop_vor_ziel_in_derselben_kerze():
    m = _markt("2024-03-05 04:00", 20)
    m["h"][3] += 50.0; m["l"][3] -= 50.0
    e = _sim(m, 1, 1, 3.0)
    assert e[5] == 1 and e[1] == pytest.approx(-1.0)     # Stop 3 $ unter dem Einstieg zum Ask (Spread steckt im Einstieg)


def test_luecke_ueber_den_stop_fuellt_am_open():
    m = _markt("2024-03-05 04:00", 20)
    m["o"][3] = 1990.0; m["l"][3] = 1989.0; m["h"][3] = 1991.0; m["c"][3] = 1990.0
    e = _sim(m, 1, 1, 3.0)
    assert e[5] == 1 and e[1] == pytest.approx((1990.0 - 2000.3) / 3.0)


def test_tp1_teilverkauf_und_einstand():
    m = _markt("2024-03-05 04:00", 40)
    m["h"][4] = 2000.3 + 1.5 * 3.0 + 0.1               # Tp1-Niveau ueberschritten
    for k in ("o", "h", "l", "c"):
        m[k][5:] = 2003.0                              # Kurs bleibt ueber dem Einstand-Stop
    m["h"][4] = 2004.9; m["c"][4] = 2003.0
    m["l"][7] = 2000.3 + 0.05 * 3.0 - 0.01             # dann zurueck unter den Einstand-Stop
    e = _sim(m, 1, 1, 3.0)
    assert e[5] == 1
    assert e[1] == pytest.approx(0.5 * 1.5 + 0.5 * 0.05)


def test_zeit_exit_nach_192_m15():
    m = _markt("2024-03-05 04:00", 192 * 3 + 30)
    e = _sim(m, 0, 1, 50.0, ziel=0.0)
    assert e[5] == 3
    assert e[3] == pytest.approx(192 * 15)           # Ausstieg am Open der 193. M15-Kerze (= 192 x 15 min spaeter)


def test_short_zahlt_spread_beim_ausstieg():
    m = _markt("2024-03-05 04:00", 20)
    e = _sim(m, 1, -1, 3.0, ziel=0.0, maxhold15=2)
    assert e[1] == pytest.approx(-0.3 / 3.0)
