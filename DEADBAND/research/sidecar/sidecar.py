"""DEADBAND Sidecar - Begleitprozess auf dem Windows-Server (research/PLAN.md Abschnitt 9). Sendet KEINE Orders.

Jede Minute: GFT-Terminal laeuft (Prozesspfad)? -> erst dann MetaTrader5.initialize(path=<GFT terminal64.exe>);
verbunden, Algo Trading an, Kontodaten lesbar, Tick-Alter je Symbol in der Handelszeit. Ergebnis als Zustandsdatei
MQL5\\Files\\deadband_sidecar.txt fuer den EA (patch_sidecar_lesen.mq5) und Alarme ueber ntfy.sh und MT5-Push (der EA
setzt neue Alarmzeilen in SendNotification um). Nur lesende Aufrufe: terminal_info, account_info, positions_get,
symbol_info_tick. Keine Kontonummern, Passwoerter oder Tokens im Log.

Aufruf:
  python sidecar.py                   Dauerbetrieb (Aufgabe "DEADBAND Sidecar")
  python sidecar.py --einmal          ein Durchlauf, Ergebnis auf der Konsole
  python sidecar.py --selbsttest      Setup-Pruefung: Paket, Terminal, Zustandsdatei schreiben und lesen
  python sidecar.py --testalarm       eine Testmeldung (ntfy und MT5-Push ueber den EA)
  python sidecar.py --trocken ORDNER  Trockenlauf ohne MT5: Zustandsdatei nach ORDNER
"""
import argparse
import datetime as dt
import logging
import logging.handlers
import os
import sys
import time
import urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import sidecar_kern as SK  # noqa: E402

ZUSTAND = "deadband_sidecar.txt"
LOG = logging.getLogger("sidecar")


# ------------------------------------------------------------------ Log (UTC, rotierend 7 x 5 MB)
def log_einrichten(ordner, konsole=False):
    os.makedirs(ordner, exist_ok=True)
    fmt = logging.Formatter("%(asctime)sZ %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    fmt.converter = time.gmtime
    h = logging.handlers.RotatingFileHandler(os.path.join(ordner, "sidecar.log"), maxBytes=5 * 1024 * 1024,
                                             backupCount=7, encoding="utf-8")
    h.setFormatter(fmt)
    LOG.handlers[:] = [h]
    if konsole:
        k = logging.StreamHandler(sys.stdout)
        k.setFormatter(fmt)
        LOG.addHandler(k)
    LOG.setLevel(logging.INFO)


# ------------------------------------------------------------------ Windows-Prozesse (ctypes, ohne Zusatzpaket)
def laufende_programme():
    """Vollstaendige Pfade aller laufenden Prozesse (nur Windows; sonst leer)."""
    if os.name != "nt":
        return []
    import ctypes
    from ctypes import wintypes
    psapi = ctypes.WinDLL("psapi"); k32 = ctypes.WinDLL("kernel32")
    ids = (wintypes.DWORD * 4096)()
    n = wintypes.DWORD()
    if not psapi.EnumProcesses(ids, ctypes.sizeof(ids), ctypes.byref(n)):
        return []
    pfade = []
    for i in range(n.value // ctypes.sizeof(wintypes.DWORD)):
        h = k32.OpenProcess(0x1000, False, ids[i])                     # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            continue
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(1024)
            if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                pfade.append(buf.value)
        finally:
            k32.CloseHandle(h)
    return pfade


def gleicher_pfad(a, b):
    return os.path.normcase(os.path.normpath(a or "")) == os.path.normcase(os.path.normpath(b or ""))


def terminal_laeuft(pfad):
    return any(gleicher_pfad(p, pfad) for p in laufende_programme())


# ------------------------------------------------------------------ MT5 (nur lesend, nie der Standardpfad)
class Terminal:
    def __init__(self, pfad, portable):
        if not pfad or not os.path.isabs(pfad):
            raise ValueError("terminal_pfad fehlt in config.ini - ohne expliziten Pfad wird MT5 nie angesprochen")
        self.pfad = pfad
        self.portable = portable
        self.mt5 = None

    def verbinden(self):
        if self.mt5 is not None:
            return True
        import MetaTrader5 as mt5
        if not mt5.initialize(path=self.pfad, portable=self.portable, timeout=15000):
            LOG.warning("initialize fehlgeschlagen: %s", mt5.last_error())
            mt5.shutdown()
            return False
        ti = mt5.terminal_info()
        ziel = os.path.dirname(self.pfad)
        if ti is None or not gleicher_pfad(ti.path, ziel):
            LOG.error("falsches Terminal verbunden (%s statt %s) - getrennt", getattr(ti, "path", None), ziel)
            mt5.shutdown()
            return False
        self.mt5 = mt5
        LOG.info("verbunden mit %s (Build %s)", ti.path, getattr(ti, "build", "?"))
        return True

    def trennen(self):
        if self.mt5 is not None:
            try:
                self.mt5.shutdown()
            finally:
                self.mt5 = None

    def lesen(self, symbole):
        m = self.mt5
        ti = m.terminal_info(); ai = m.account_info()
        if ti is None:
            raise RuntimeError(f"terminal_info: {m.last_error()}")
        pos = m.positions_get()
        ticks = {}
        for s in symbole:
            t = m.symbol_info_tick(s)
            ticks[s] = int(t.time) if t is not None and t.time else None
        return dict(verbunden=bool(ti.connected), algo=bool(ti.trade_allowed), konto=ai is not None,
                    positionen=len(pos) if pos is not None else -1, ticks=ticks)


# ------------------------------------------------------------------ Alarme
def ntfy(k, text):
    if not k["ntfy_thema"]:
        return False
    req = urllib.request.Request(k["ntfy_server"].rstrip("/") + "/" + k["ntfy_thema"], data=text.encode("utf-8"),
                                 headers={"Title": "DEADBAND Sidecar", "Priority": "high", "Tags": "warning"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return 200 <= r.status < 300
    except Exception as e:                                              # Netz weg: im Log, Sidecar laeuft weiter
        LOG.warning("ntfy nicht gesendet: %s", type(e).__name__)
        return False


class Sidecar:
    def __init__(self, k, trocken_ordner=None):
        self.k = k
        self.symbole = [s.strip() for s in k["symbole"].split(";") if s.strip()]
        self.trocken = trocken_ordner is not None
        files = trocken_ordner or os.path.join(k["datenordner"], "MQL5", "Files")
        self.zustand_pfad = os.path.join(files, ZUSTAND)
        self.terminal = None if self.trocken else Terminal(k["terminal_pfad"], k["portable"] == "1")
        self.entprell = SK.Entprellung(int(k["alarm_sperre_min"]) * 60)
        self.alarm_nr, self.alarm_text = self._letzter_alarm()
        self.kalender = []; self.kalender_stand = None

    def _letzter_alarm(self):
        """Alarmnummer ueber Neustarts fortsetzen (der EA meldet jede neue Nummer genau einmal)."""
        try:
            w = {}
            with open(self.zustand_pfad, encoding="ascii", errors="replace") as f:
                for z in f:
                    if "=" in z:
                        a, b = z.rstrip("\r\n").split("=", 1)
                        w[a] = b
            return int(w.get("alarm_nr", "0")), w.get("alarm_text", "")
        except (OSError, ValueError):
            return 0, ""

    def melden(self, text, jetzt):
        self.alarm_nr += 1
        self.alarm_text = text[:200]
        LOG.warning("ALARM %d: %s", self.alarm_nr, text)
        if not self.trocken:
            ntfy(self.k, text)

    def _kalender(self, jetzt_server):
        pfad = self.k["kalender_datei"]
        if not pfad or self.k["nachrichten_sperre"] != "1":
            return None
        try:
            st = os.path.getmtime(pfad)
        except OSError:
            return "Kalenderdatei fehlt"
        if st != self.kalender_stand:
            self.kalender, kaputt = SK.lies_kalender(pfad)
            self.kalender_stand = st
            LOG.info("Kalender geladen: %d Termine, %d kaputte Zeilen", len(self.kalender), kaputt)
        if not self.kalender or self.kalender[-1][0] < jetzt_server + dt.timedelta(days=int(self.k["kalender_warn_tage"])):
            return "Kalender laeuft aus - DEADBAND_Kalender_Export erneut ausfuehren"
        return None

    def durchlauf(self, jetzt=None):
        jetzt = jetzt or dt.datetime.now(SK.UTC)
        server = SK.server_aus_utc(jetzt)
        w = {"zeit_utc": int(jetzt.timestamp()), "zeit_server": SK.server_epoch(jetzt),
             "schreibzeit_utc": jetzt.strftime("%Y-%m-%dT%H:%M:%SZ"), "schreibzeit_server": SK.server_text(server)}
        pruef = []                                                       # (schluessel, fehler, text)
        lage = None
        if self.trocken:
            w.update(terminal=0, verbunden=0, algo=0, konto=0, positionen=-1)
        else:
            laeuft = terminal_laeuft(self.terminal.pfad)
            pruef.append(("terminal", not laeuft, "GFT-Terminal laeuft nicht"))
            if laeuft and self.terminal.verbinden():
                try:
                    lage = self.terminal.lesen(self.symbole)
                except Exception as e:
                    LOG.warning("Lesen fehlgeschlagen (%s) - neu verbinden", type(e).__name__)
                    self.terminal.trennen()
            elif not laeuft:
                self.terminal.trennen()
            pruef.append(("mt5", laeuft and lage is None, "Terminal laeuft, aber MetaTrader5-Paket erreicht es nicht"))
            w.update(terminal=int(laeuft), verbunden=int(bool(lage and lage["verbunden"])),
                     algo=int(bool(lage and lage["algo"])), konto=int(bool(lage and lage["konto"])),
                     positionen=lage["positionen"] if lage else -1)
            if lage:
                pruef.append(("verbunden", not lage["verbunden"], "Terminal nicht mit dem Server verbunden"))
                pruef.append(("algo", not lage["algo"], "Algo Trading ist aus"))
                pruef.append(("konto", not lage["konto"], "Kontodaten nicht lesbar"))
        handelszeit = SK.in_handelszeit(jetzt, int(self.k["anlauf_min"]))
        jetzt_s = SK.server_epoch(jetzt)
        for s in self.symbole:
            tz = lage["ticks"].get(s) if lage else None
            alter = jetzt_s - tz if tz else -1
            w[f"tickalter_{s}"] = alter
            if lage and lage["verbunden"]:
                alt = handelszeit and (tz is None or alter > int(self.k["max_tickalter_s"]))
                pruef.append((f"tick_{s}", alt, f"{s}: letzter Tick aelter als {self.k['max_tickalter_s']} s"))
        kal = self._kalender(server)
        pruef.append(("kalender", kal is not None, kal or "Kalender"))
        sperren = self.k["nachrichten_sperre"] == "1" and self.kalender
        gesperrt, bis, naechster = SK.sperre(self.kalender, server, int(self.k["sperre_vor_min"]),
                                             int(self.k["sperre_nach_min"])) if sperren else (False, None, None)
        von, bis_f = SK.fenster(self.kalender, server, int(self.k["sperre_vor_min"]),
                                int(self.k["sperre_nach_min"])) if sperren else (None, None)
        for s in self.symbole:                                          # US-Termine: alle Symbole gleich
            w[f"sperre_{s}"] = int(gesperrt)
            w[f"sperre_bis_{s}"] = SK.server_text(bis) if bis else ""
            w[f"fenster_von_{s}"] = SK.server_text(von) if von else ""
            w[f"fenster_bis_{s}"] = SK.server_text(bis_f) if bis_f else ""
        w["naechster_termin"] = SK.server_text(naechster) if naechster else ""
        w["kalender_bis"] = SK.server_text(self.kalender[-1][0]) if self.kalender else ""
        for schl, fehler, text in pruef:
            m = self.entprell.pruefe(schl, fehler, text, jetzt.timestamp())
            if m:
                self.melden(m, jetzt)
        offen = [s for s, f, _ in pruef if f]
        w["heartbeat"] = "OK" if not offen else ("FEHLER" if {"terminal", "mt5", "verbunden"} & set(offen) else "WARNUNG")
        w["probleme"] = ";".join(offen)
        w["alarm_nr"] = self.alarm_nr
        w["alarm_text"] = self.alarm_text
        SK.schreibe_zustand(self.zustand_pfad, w)
        return w

    def dauerbetrieb(self):
        takt = int(self.k["takt_s"])
        LOG.info("Start: %d Symbole, Takt %d s, Zustand %s", len(self.symbole), takt, self.zustand_pfad)
        while True:
            t0 = time.time()
            try:
                w = self.durchlauf()
                if w["heartbeat"] != "OK":
                    LOG.info("Heartbeat %s: %s", w["heartbeat"], w["probleme"])
            except Exception as e:
                LOG.exception("Durchlauf fehlgeschlagen")
                m = self.entprell.pruefe("sidecar", True, f"Sidecar-Fehler: {type(e).__name__}", time.time())
                if m:
                    self.melden(m, dt.datetime.now(SK.UTC))
                if self.terminal:
                    self.terminal.trennen()
            time.sleep(max(1.0, takt - (time.time() - t0)))


# ------------------------------------------------------------------ Einzelinstanz
def sperre_einzelinstanz(ordner):
    pfad = os.path.join(ordner, "sidecar.lock")
    f = open(pfad, "a+")
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        return None
    return f


def selbsttest(k):
    ok = True
    print("Python", sys.version.split()[0])
    try:
        import MetaTrader5 as mt5
        print("MetaTrader5", mt5.__version__)
    except Exception as e:
        print("FEHLER: MetaTrader5 nicht importierbar:", e); return False
    print("Terminal:", k["terminal_pfad"], "vorhanden" if os.path.isfile(k["terminal_pfad"]) else "FEHLT")
    ok &= os.path.isfile(k["terminal_pfad"])
    sc = Sidecar(k)
    if terminal_laeuft(k["terminal_pfad"]):
        w = sc.durchlauf()
        print(f"Heartbeat {w['heartbeat']} | verbunden {w['verbunden']} | Algo {w['algo']} | Konto lesbar {w['konto']}")
        for s in sc.symbole:
            print(f"  {s}: Tick-Alter {w['tickalter_' + s]} s")
        sc.terminal.trennen()
    else:
        print("WARNUNG: GFT-Terminal laeuft gerade nicht - nur die Zustandsdatei wird geprueft")
        os.makedirs(os.path.dirname(sc.zustand_pfad), exist_ok=True)
        SK.schreibe_zustand(sc.zustand_pfad, {"zeit_utc": int(time.time()), "heartbeat": "SELBSTTEST"})
    gut, werte, grund = SK.lies_zustand(sc.zustand_pfad, dt.datetime.now(SK.UTC), int(k["max_datenalter_s"]))
    print("Zustandsdatei:", sc.zustand_pfad, "->", grund)
    return ok and gut


def main(argv=None):
    ap = argparse.ArgumentParser(description="DEADBAND Sidecar")
    ap.add_argument("--konfig", default=os.path.join(HIER, "config.ini"))
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--einmal", action="store_true")
    g.add_argument("--selbsttest", action="store_true")
    g.add_argument("--testalarm", action="store_true")
    g.add_argument("--trocken", metavar="ORDNER")
    ap.add_argument("--zyklen", type=int, default=1, help="nur mit --trocken")
    a = ap.parse_args(argv)
    k = SK.lies_konfig(a.konfig)
    if a.trocken:
        log_einrichten(a.trocken, konsole=True)
        sc = Sidecar(k, trocken_ordner=a.trocken)
        for i in range(a.zyklen):
            sc.durchlauf()
        print("Trockenlauf: Zustand geschrieben nach", sc.zustand_pfad)
        return 0
    log_einrichten(k["log_ordner"], konsole=a.einmal or a.selbsttest or a.testalarm)
    if a.selbsttest:
        return 0 if selbsttest(k) else 1
    if a.testalarm:
        sc = Sidecar(k)
        sc.melden("Testalarm DEADBAND Sidecar - bitte ignorieren", dt.datetime.now(SK.UTC))
        w = sc.durchlauf()
        print("Testalarm Nr.", w["alarm_nr"], "- ntfy gesendet, der EA meldet ihn per Push (wenn patch_sidecar_lesen laeuft)")
        return 0
    lock = sperre_einzelinstanz(k["log_ordner"])
    if lock is None:
        print("Sidecar laeuft schon - Ende")
        return 0
    sc = Sidecar(k)
    if a.einmal:
        w = sc.durchlauf()
        for kk, v in w.items():
            print(f"{kk}={v}")
        return 0
    sc.dauerbetrieb()
    return 0


if __name__ == "__main__":
    sys.exit(main())
