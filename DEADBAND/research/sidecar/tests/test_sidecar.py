"""Sidecar: Zeitzonen, Handelszeit, Kalender, Zustandsformat (fail-open), Entprellung, Konfiguration, Trockenlauf."""
import datetime as dt
import os
import sys

import pytest

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HIER))
import sidecar as SC  # noqa: E402
import sidecar_kern as SK  # noqa: E402

U = SK.UTC


def utc(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=U)


# ---------------------------------------------------------------- Zeitzonen
@pytest.mark.parametrize("u,server", [
    ("2026-10-14 12:00", "2026-10-14 15:00"),   # NY-Sommerzeit: Server = UTC+3
    ("2026-10-26 12:00", "2026-10-26 15:00"),   # nach der EU-Umstellung (25.10.), NY noch Sommerzeit: weiter UTC+3
    ("2026-10-31 21:00", "2026-11-01 00:00"),   # Samstag 17:00 NY = Servertag-Wechsel
    ("2026-11-01 05:59", "2026-11-01 08:59"),   # 01:59 EDT
    ("2026-11-01 06:00", "2026-11-01 08:00"),   # 01:00 EST: US-Umstellung (01.11.) -> UTC+2
    ("2026-11-02 12:00", "2026-11-02 14:00"),
    ("2026-03-08 06:59", "2026-03-08 08:59"),   # 01:59 EST
    ("2026-03-08 07:00", "2026-03-08 10:00"),   # 03:00 EDT
])
def test_serverzeit_ny_plus_7(u, server):
    assert SK.server_text(SK.server_aus_utc(utc(u))) == dt.datetime.strptime(server, "%Y-%m-%d %H:%M").strftime("%Y.%m.%d %H:%M:%S")


def test_17_uhr_ny_ist_mitternacht_server_in_beiden_phasen():
    for u in ("2026-10-27 21:00", "2026-11-03 22:00"):              # 17:00 EDT bzw. 17:00 EST
        s = SK.server_aus_utc(utc(u))
        assert (s.hour, s.minute) == (0, 0)
        assert SK.ny_aus_utc(utc(u)).hour == 17


def test_rueckrechnung_server_utc():
    for u in ("2026-10-14 12:00", "2026-11-02 12:00", "2027-01-15 03:30", "2027-07-01 23:59"):
        assert SK.utc_aus_server(SK.server_aus_utc(utc(u))) == utc(u)


def test_server_epoch():
    u = utc("2026-11-02 12:00")
    assert SK.server_epoch(u) == int(u.timestamp()) + 2 * 3600


# ---------------------------------------------------------------- Handelszeit
@pytest.mark.parametrize("u,erw", [
    ("2026-10-14 14:00", True),     # Mittwoch 10:00 NY
    ("2026-10-14 21:30", False),    # 17:30 NY Tagespause
    ("2026-10-14 22:05", False),    # 18:05 NY Schonfrist
    ("2026-10-14 22:20", True),
    ("2026-10-16 20:59", True),     # Freitag 16:59 NY
    ("2026-10-16 21:00", False),    # Freitag 17:00 NY
    ("2026-10-17 15:00", False),    # Samstag
    ("2026-10-18 22:20", True),     # Sonntag 18:20 NY
    ("2026-11-26 15:00", False),    # Thanksgiving
    ("2026-11-25 23:30", False),    # Vorabend (gehoert zum Servertag des Feiertags)
])
def test_handelszeit(u, erw):
    assert SK.in_handelszeit(utc(u)) == erw


# ---------------------------------------------------------------- Kalender
def _kal(pfad, zeilen):
    with open(pfad, "w", encoding="utf-8", newline="") as f:
        f.write("server_time\tvalue_id\tevent_id\tcode\tname\timportance\ttime_mode\tactual\tforecast\tprev\trevised_prev\timpact\r\n")
        for z in zeilen:
            f.write("\t".join(z) + "\r\n")


def test_kalender_parser_und_sperre(tmp_path):
    p = str(tmp_path / "kalender_US.csv")
    _kal(p, [("2026.11.06 15:30:00", "1", "1", "nonfarm-payrolls", "Nonfarm Payrolls", "3", "0", "", "50", "40", "", "0"),
             ("2026.11.06 15:30:00", "2", "2", "unemployment-rate", "Unemployment Rate", "3", "0", "", "", "", "", "0"),
             ("2026.11.06 17:00:00", "3", "3", "x", "Mittel", "2", "0", "", "", "", "", "0"),
             ("2026.11.10 00:00:00", "4", "4", "y", "Ohne Uhrzeit", "3", "1", "", "", "", "", "0"),
             ("kaputt", "5", "5", "z", "z", "3", "0", "", "", "", "", "0"),
             ("2026.11.18 21:00:00", "6", "6", "fomc", "Fed Interest Rate Decision", "3", "0", "", "", "", "", "0")])
    termine, kaputt = SK.lies_kalender(p)
    assert [t.strftime("%d %H:%M") for t, _, _ in termine] == ["06 15:30", "18 21:00"]
    assert kaputt == 1
    s = lambda x: dt.datetime.strptime(x, "%Y.%m.%d %H:%M")
    assert SK.sperre(termine, s("2026.11.06 15:10"), 15, 15)[0] is False
    g, bis, nxt = SK.sperre(termine, s("2026.11.06 15:20"), 15, 15)
    assert g and bis == s("2026.11.06 15:45") and nxt == s("2026.11.06 15:30")
    g, bis, nxt = SK.sperre(termine, s("2026.11.06 15:46"), 15, 15)
    assert not g and nxt == s("2026.11.18 21:00")
    assert SK.fenster(termine, s("2026.11.06 15:00"), 15, 15) == (s("2026.11.06 15:15"), s("2026.11.06 15:45"))
    assert SK.fenster(termine, s("2026.11.06 15:45"), 15, 15) == (s("2026.11.06 15:15"), s("2026.11.06 15:45"))
    assert SK.fenster(termine, s("2026.11.06 15:46"), 15, 15) == (s("2026.11.18 20:45"), s("2026.11.18 21:15"))
    assert SK.fenster(termine, s("2026.11.19 00:00"), 15, 15) == (None, None)
    zwei = [(s("2026.11.06 15:30"), "", ""), (s("2026.11.06 15:50"), "", ""), (s("2026.11.06 17:00"), "", "")]
    assert SK.fenster(zwei, s("2026.11.06 12:00"), 15, 15) == (s("2026.11.06 15:15"), s("2026.11.06 16:05"))


# ---------------------------------------------------------------- Zustandsformat
def test_zustand_schreiben_lesen_und_fail_open(tmp_path):
    p = str(tmp_path / "deadband_sidecar.txt")
    jetzt = utc("2026-10-14 12:00")
    assert SK.lies_zustand(p, jetzt, 180)[:3:2] == (False, "fehlt")
    SK.schreibe_zustand(p, {"zeit_utc": int(jetzt.timestamp()), "heartbeat": "OK", "sperre_XAUUSD.x": 0})
    roh = open(p, "rb").read()
    assert roh.startswith(b"version=1\r\n") and roh.endswith(b"ende=1\r\n") and not os.path.exists(p + ".tmp")
    ok, w, grund = SK.lies_zustand(p, jetzt + dt.timedelta(seconds=60), 180)
    assert ok and w["heartbeat"] == "OK" and w["sperre_XAUUSD.x"] == "0"
    assert SK.lies_zustand(p, jetzt + dt.timedelta(seconds=181), 180)[0] is False        # zu alt
    open(p, "wb").write(roh.replace(b"ende=1\r\n", b""))                                   # abgeschnitten
    assert SK.lies_zustand(p, jetzt, 180)[2] == "unvollstaendig"
    open(p, "wb").write(roh.replace(b"version=1", b"version=2"))
    assert SK.lies_zustand(p, jetzt, 180)[2] == "version"
    open(p, "wb").write(b"\xff\xfe\x00m\x00\x00")
    assert SK.lies_zustand(p, jetzt, 180)[0] is False
    with pytest.raises(ValueError):
        SK.zustand_text({"a=b": 1})
    assert "?" in SK.zustand_text({"text": "Pr\u00fcfung"})                               # nur ASCII


# ---------------------------------------------------------------- Entprellung
def test_entprellung():
    e = SK.Entprellung(1800)
    assert e.pruefe("t", True, "Terminal weg", 0) == "Terminal weg"
    assert e.pruefe("t", True, "Terminal weg", 600) is None
    assert e.pruefe("t", True, "Terminal weg", 1800) == "Terminal weg (dauert an)"
    assert e.pruefe("t", False, "Terminal weg", 1900) == "OK wieder: Terminal weg"
    assert e.pruefe("t", False, "Terminal weg", 2000) is None


# ---------------------------------------------------------------- Konfiguration
def test_konfig_und_altlast(tmp_path):
    p = tmp_path / "config.ini"
    p.write_text("[sidecar]\nterminal_pfad = C:\\Program Files\\GFT MetaTrader 5\\terminal64.exe\nmax_tickalter_s = 90\n")
    k = SK.lies_konfig(str(p))
    assert k["max_tickalter_s"] == "90" and k["max_datenalter_s"] == "180"
    p.write_text("[sidecar]\nterminal_pfad = C:\\Program Files\\MetaTrader 5 GFT\\terminal64.exe\n")
    SK.lies_konfig(str(p))                                                                  # anderer Ordner: erlaubt
    p.write_text("[sidecar]\nterminal_pfad = c:\\program files\\MetaTrader 5\\terminal64.exe\n")
    with pytest.raises(ValueError):
        SK.lies_konfig(str(p))


# ---------------------------------------------------------------- Trockenlauf
def test_trockenlauf(tmp_path):
    cfg = tmp_path / "config.ini"
    kal = tmp_path / "kalender_US.csv"
    jetzt = dt.datetime.now(U)
    t = SK.server_aus_utc(jetzt) + dt.timedelta(minutes=5)
    spaet = SK.server_aus_utc(jetzt) + dt.timedelta(days=30)
    _kal(str(kal), [(t.strftime("%Y.%m.%d %H:%M:00"), "1", "1", "cpi", "CPI", "3", "0", "", "", "", "", "0"),
                    (spaet.strftime("%Y.%m.%d %H:%M:00"), "2", "2", "cpi", "CPI", "3", "0", "", "", "", "", "0")])
    cfg.write_text(f"[sidecar]\nlog_ordner = {tmp_path}\nkalender_datei = {kal}\nnachrichten_sperre = 1\n")
    out = tmp_path / "files"
    out.mkdir()
    assert SC.main(["--konfig", str(cfg), "--trocken", str(out), "--zyklen", "2"]) == 0
    ok, w, grund = SK.lies_zustand(str(out / SC.ZUSTAND), dt.datetime.now(U), 180)
    assert ok, grund
    assert w["terminal"] == "0" and w["sperre_XAUUSD.x"] == "1" and w["sperre_NAS100.x"] == "1"
    assert w["sperre_bis_XAUUSD.x"] and w["naechster_termin"] and w["heartbeat"] == "OK"
    assert w["fenster_von_NAS100.x"] <= SK.server_text(SK.server_aus_utc(dt.datetime.now(U))) <= w["fenster_bis_NAS100.x"]
    assert os.path.exists(tmp_path / "files" / "sidecar.log")


# ---------------------------------------------------------------- Durchlauf mit nachgebildetem Terminal
def test_durchlauf_alarme(tmp_path, monkeypatch):
    gesendet = []
    monkeypatch.setattr(SC, "ntfy", lambda k, text: gesendet.append(text))
    lage = dict(verbunden=True, algo=True, konto=True, positionen=2, ticks={})
    laeuft = {"v": True}
    monkeypatch.setattr(SC, "terminal_laeuft", lambda p: laeuft["v"])
    monkeypatch.setattr(SC.Terminal, "verbinden", lambda self: True)
    monkeypatch.setattr(SC.Terminal, "lesen", lambda self, s: lage)
    monkeypatch.setattr(SC.Terminal, "trennen", lambda self: None)
    daten = tmp_path / "daten"
    (daten / "MQL5" / "Files").mkdir(parents=True)
    cfg = tmp_path / "config.ini"
    cfg.write_text(f"[sidecar]\nterminal_pfad = {tmp_path / 'terminal64.exe'}\ndatenordner = {daten}\nlog_ordner = {tmp_path}\n")
    sc = SC.Sidecar(SK.lies_konfig(str(cfg)))
    jetzt = utc("2026-10-14 14:00")                                 # Mittwoch 10:00 NY
    frisch = SK.server_epoch(jetzt) - 5
    lage["ticks"] = {"XAUUSD.x": frisch, "NAS100.x": frisch}
    w = sc.durchlauf(jetzt)
    assert w["heartbeat"] == "OK" and w["positionen"] == 2 and w["tickalter_NAS100.x"] == 5 and not gesendet
    lage["ticks"] = {"XAUUSD.x": frisch, "NAS100.x": frisch - 300}
    w = sc.durchlauf(jetzt)
    assert w["heartbeat"] == "WARNUNG" and w["probleme"] == "tick_NAS100.x" and len(gesendet) == 1
    assert w["alarm_nr"] == 1 and "NAS100.x" in w["alarm_text"]
    lage["algo"] = False
    w = sc.durchlauf(jetzt + dt.timedelta(minutes=1))
    assert "algo" in w["probleme"] and len(gesendet) == 2
    laeuft["v"] = False
    w = sc.durchlauf(jetzt + dt.timedelta(minutes=2))
    assert w["heartbeat"] == "FEHLER" and w["terminal"] == 0 and gesendet[-1] == "GFT-Terminal laeuft nicht"
    # Neustart: Alarmnummer laeuft weiter
    assert SC.Sidecar(SK.lies_konfig(str(cfg))).alarm_nr == w["alarm_nr"]
    # Wochenende: altes Tick-Alter ist kein Alarm
    laeuft["v"] = True; lage["algo"] = True
    sa = utc("2026-10-17 15:00")
    lage["ticks"] = {"XAUUSD.x": frisch, "NAS100.x": frisch}
    w = sc.durchlauf(sa)
    assert "tick_" not in w["probleme"]
