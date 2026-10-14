"""DEADBAND Sidecar - reine Logik ohne MT5 und ohne Windows (unit-getestet, research/sidecar/tests).

Zeit:     GFT-Serverzeit = NY + 7 h in allen Phasen (EU-Umstellung egal). NY-Sommerzeit: 2. Sonntag Maerz 02:00 bis
          1. Sonntag November 02:00 Ortszeit. Ohne tzdata-Paket gerechnet (Windows-Python hat keine Zonendatenbank).
Zustand:  Datei deadband_sidecar.txt (ASCII, schluessel=wert, CRLF), atomar geschrieben (temp + replace).
          Letzte Zeile ende=1. Fehlt sie, ist die Datei kaputt -> der EA handelt wie heute (fail-open).
Kalender: CSV von DEADBAND_Kalender_Export.mq5 (Serverzeit, Tabs, UTF-8) -> Sperrfenster je Symbol.
Alarme:   Entprellung - derselbe Alarm hoechstens alle 30 min, Entwarnung genau einmal.
"""
import csv
import datetime as dt
import os

VERSION = 1
SERVER_NACH_NY_H = 7
UTC = dt.timezone.utc


# ------------------------------------------------------------------ Zeit
def _sonntag(jahr, monat, nr):
    """Datum des nr-ten Sonntags im Monat."""
    d = dt.date(jahr, monat, 1)
    erster = d + dt.timedelta(days=(6 - d.weekday()) % 7)
    return erster + dt.timedelta(days=7 * (nr - 1))


def ny_sommerzeit(utc):
    """True, wenn in New York Sommerzeit gilt (utc: aware datetime)."""
    j = utc.year
    beginn = dt.datetime.combine(_sonntag(j, 3, 2), dt.time(7, 0), UTC)    # 02:00 EST = 07:00 UTC
    ende = dt.datetime.combine(_sonntag(j, 11, 1), dt.time(6, 0), UTC)     # 02:00 EDT = 06:00 UTC
    return beginn <= utc < ende


def ny_aus_utc(utc):
    """NY-Ortszeit (naiv)."""
    return (utc + dt.timedelta(hours=-4 if ny_sommerzeit(utc) else -5)).replace(tzinfo=None)


def server_aus_utc(utc):
    """GFT-Serverzeit (naiv) = NY + 7 h."""
    return ny_aus_utc(utc) + dt.timedelta(hours=SERVER_NACH_NY_H)


def utc_aus_server(server):
    """Serverzeit (naiv) -> UTC (aware). Server = UTC+3 (NY-Sommer) bzw. UTC+2 (NY-Winter)."""
    for h in (3, 2):
        kand = (server - dt.timedelta(hours=h)).replace(tzinfo=UTC)
        if server_aus_utc(kand) == server:
            return kand
    return (server - dt.timedelta(hours=2)).replace(tzinfo=UTC)          # Uhrumstellungsstunde: eindeutig genug


def server_epoch(utc):
    """Serverzeit als Sekunden seit 1970 (wie datetime in MQL5 / Tick-Zeit im MetaTrader5-Paket)."""
    return int((server_aus_utc(utc) - dt.datetime(1970, 1, 1)).total_seconds())


def server_text(t):
    return t.strftime("%Y.%m.%d %H:%M:%S")


# ------------------------------------------------------------------ Handelszeit (fuer das Tick-Alter)
FEIERTAGE = {  # US-Boersenfeiertage und verkuerzte Tage (NY-Datum): Tick-Alter wird dort nicht geprueft
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
    "2026-11-26", "2026-11-27", "2026-12-24", "2026-12-25",
    "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31", "2027-06-18", "2027-07-05", "2027-09-06",
    "2027-11-25", "2027-11-26", "2027-12-24",
    "2028-01-17", "2028-02-21", "2028-04-14", "2028-05-29", "2028-06-19", "2028-07-03", "2028-07-04", "2028-09-04",
    "2028-11-23", "2028-11-24", "2028-12-25"}


def in_handelszeit(utc, anlauf_min=15, feiertage=FEIERTAGE):
    """Sonntag 18:00 bis Freitag 17:00 NY ohne die taegliche Pause 17:00-18:00 NY; nach jeder Eroeffnung (18:00)
    anlauf_min Minuten Schonfrist; an Feiertagen und verkuerzten Tagen keine Pruefung."""
    ny = ny_aus_utc(utc)
    wt = ny.weekday()                      # 0 = Montag ... 6 = Sonntag
    m = ny.hour * 60 + ny.minute
    if ny.date().isoformat() in feiertage:
        return False
    if (ny + dt.timedelta(hours=7)).date().isoformat() in feiertage:   # Abend vor einem Feiertag (gleicher Servertag)
        return False
    if wt == 5:
        return False
    if wt == 6:
        return m >= 18 * 60 + anlauf_min
    if wt == 4 and m >= 17 * 60:
        return False
    if 17 * 60 <= m < 18 * 60 + anlauf_min:
        return False
    return True


# ------------------------------------------------------------------ Kalender
def lies_kalender(pfad, min_bedeutung=3):
    """Termine [(server_dt, code, name)] hoher Bedeutung mit genauer Uhrzeit, sortiert, gleiche Zeit einmal.
    Kaputte Zeilen werden uebersprungen (Anzahl als zweiter Rueckgabewert)."""
    termine = {}
    kaputt = 0
    with open(pfad, encoding="utf-8", errors="replace", newline="") as f:
        for z in csv.DictReader(f, delimiter="\t"):
            try:
                if int(z["importance"]) < min_bedeutung or int(z["time_mode"]) != 0:
                    continue
                t = dt.datetime.strptime(z["server_time"].strip(), "%Y.%m.%d %H:%M:%S")
            except (KeyError, ValueError, TypeError):
                kaputt += 1
                continue
            termine.setdefault(t, (t, (z.get("code") or "").strip(), (z.get("name") or "").strip()))
    return [termine[k] for k in sorted(termine)], kaputt


def fenster(termine, server_jetzt, vor_min, nach_min):
    """(von, bis) des laufenden oder naechsten Sperrfensters [Termin - vor, Termin + nach]; ueberlappende Fenster
    werden zusammengefasst. (None, None), wenn keins mehr kommt. Der EA sperrt, solange von <= jetzt <= bis."""
    vor = dt.timedelta(minutes=vor_min); nach = dt.timedelta(minutes=nach_min)
    von = bis = None
    for t, _, _ in termine:
        a, b = t - vor, t + nach
        if von is None:
            if b >= server_jetzt:
                von, bis = a, b
        elif a <= bis:
            bis = max(bis, b)
        else:
            break
    return von, bis


def sperre(termine, server_jetzt, vor_min, nach_min):
    """(gesperrt, bis, naechster) zur Serverzeit: gesperrt, wenn ein Termin in [jetzt - nach, jetzt + vor] liegt;
    bis = Ende des laengsten laufenden Fensters; naechster = naechster Termin nach jetzt (oder None)."""
    vor = dt.timedelta(minutes=vor_min); nach = dt.timedelta(minutes=nach_min)
    bis = None
    naechster = None
    for t, _, _ in termine:
        if t - vor <= server_jetzt <= t + nach:
            if bis is None or t + nach > bis:
                bis = t + nach
        if t > server_jetzt and naechster is None:
            naechster = t
    return bis is not None, bis, naechster


# ------------------------------------------------------------------ Zustandsdatei
def zustand_text(werte):
    """werte: dict (Reihenfolge bleibt). Setzt version vorne und ende=1 hinten. Nur ASCII, keine '=' im Schluessel."""
    zeilen = [f"version={VERSION}"]
    for k, v in werte.items():
        k = str(k); v = "" if v is None else str(v)
        if "=" in k or "\n" in k or "\n" in v or "\r" in v:
            raise ValueError(f"ungueltiger Eintrag {k!r}")
        zeilen.append(f"{k}={v}")
    zeilen.append("ende=1")
    text = "\r\n".join(zeilen) + "\r\n"
    return text.encode("ascii", "replace").decode("ascii")


def schreibe_zustand(pfad, werte):
    """Atomar: erst <pfad>.tmp schreiben, dann ersetzen (der EA liest nie eine halbe Datei)."""
    tmp = pfad + ".tmp"
    with open(tmp, "w", encoding="ascii", newline="") as f:
        f.write(zustand_text(werte))
        f.flush()
        os.fsync(f.fileno())
    for versuch in range(20):
        try:
            os.replace(tmp, pfad)
            return
        except PermissionError:                  # Windows: EA liest gerade (ohne FILE_SHARE_DELETE) - kurz warten
            import time
            time.sleep(0.05)
    raise PermissionError(f"{pfad} bleibt gesperrt")


def lies_zustand(pfad, jetzt_utc, max_alter_s):
    """Wie der EA: (ok, werte, grund). ok=False -> fail-open (Datei fehlt, kaputt, falsche Version, zu alt)."""
    try:
        with open(pfad, encoding="ascii", errors="strict") as f:
            text = f.read()
    except FileNotFoundError:
        return False, {}, "fehlt"
    except (OSError, UnicodeDecodeError):
        return False, {}, "unlesbar"
    werte = {}
    for z in text.splitlines():
        if "=" in z:
            k, v = z.split("=", 1)
            werte[k.strip()] = v.strip()
    if werte.get("ende") != "1":
        return False, werte, "unvollstaendig"
    if werte.get("version") != str(VERSION):
        return False, werte, "version"
    try:
        alter = jetzt_utc.timestamp() - int(werte["zeit_utc"])
    except (KeyError, ValueError):
        return False, werte, "ohne zeit"
    if alter > max_alter_s or alter < -60:
        return False, werte, f"alt {int(alter)} s"
    return True, werte, "ok"


# ------------------------------------------------------------------ Alarme
class Entprellung:
    """Je Alarmschluessel: erste Meldung sofort, Wiederholung fruehestens nach sperre_s, Entwarnung einmal."""

    def __init__(self, sperre_s=1800):
        self.sperre_s = sperre_s
        self.aktiv = {}                        # schluessel -> Zeitpunkt der letzten Meldung (epoch s)

    def pruefe(self, schluessel, fehler, text, jetzt_s):
        """Rueckgabe: Meldungstext oder None."""
        if fehler:
            letzte = self.aktiv.get(schluessel)
            if letzte is None or jetzt_s - letzte >= self.sperre_s:
                self.aktiv[schluessel] = jetzt_s
                return text if letzte is None else text + " (dauert an)"
            return None
        if schluessel in self.aktiv:
            del self.aktiv[schluessel]
            return "OK wieder: " + text
        return None


# ------------------------------------------------------------------ Konfiguration
STANDARD = {
    "terminal_pfad": "", "portable": "0", "datenordner": "", "symbole": "XAUUSD.x;NAS100.x",
    "max_datenalter_s": "180", "max_tickalter_s": "120", "takt_s": "60", "alarm_sperre_min": "30",
    "ntfy_server": "https://ntfy.sh", "ntfy_thema": "", "log_ordner": r"C:\Trading\sidecar\logs",
    "kalender_datei": "", "nachrichten_sperre": "0", "sperre_vor_min": "15", "sperre_nach_min": "15",
    "kalender_warn_tage": "7", "anlauf_min": "15",
}
ALTLAST = r"c:\program files\metatrader 5"


def lies_konfig(pfad):
    """config.ini (Abschnitt [sidecar]) mit Standardwerten. Prueft den Terminalpfad gegen die Altlast."""
    import configparser
    cp = configparser.ConfigParser(interpolation=None)
    cp.read(pfad, encoding="utf-8")
    k = dict(STANDARD)
    if cp.has_section("sidecar"):
        k.update({a: b for a, b in cp.items("sidecar")})
    tp = k["terminal_pfad"].replace("/", "\\").strip().strip('"').rstrip("\\").lower()
    if tp == ALTLAST or tp.startswith(ALTLAST + "\\"):
        raise ValueError("terminal_pfad zeigt auf die Altlast C:\\Program Files\\MetaTrader 5 - verboten")
    return k
