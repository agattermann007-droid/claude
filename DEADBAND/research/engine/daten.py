"""Kursdaten: MT5-Exporte einlesen, am Stichtag trennen, als Replikat-Format ablegen.

Zeitachse wie das Replikat: NY-Minuten seit Epoche (int64), Serverzeit = NY + 7 h.
Prop-Tag (17:00 NY bis 17:00 NY) = Servertag = (ny + 420) // 1440.

Stichtag-Sperre (Walk-Forward, PLAN 3.5):
  installiere() schreibt DEADBAND/data/ (nur bis zum Stichtag) und DEADBAND/data_blind/ (alles).
  lade(..., blind=False) liest nur data/. blind=True liest data_blind/ und schreibt einen Eintrag in
  research/ergebnisse/blindlauf_protokoll.txt - der Blindlauf darf genau einmal stattfinden.

Eingabeformate:
  A) MT5 "Balken exportieren" / DEADBAND_Daten_Export.mq5: Tab, <DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>
  B) mt5_export_v2.py (Python, Drive): Komma, time,open,high,low,close,tick_volume,spread,real_volume; 'time' traegt
     faelschlich '+00:00', ist aber Serverzeit (copy_rates liefert Serverzeit als Epoche).
"""
import datetime as dt
import hashlib
import json
import os

import numpy as np
import pandas as pd

from . import konfig as K


def _sha256(pfad):
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def lies_mt5(pfad):
    """DataFrame mit server (datetime64[ns]), open, high, low, close, tickvol, spread (Punkte), sortiert, ohne Duplikate."""
    with open(pfad, "rb") as f:
        kopf = f.read(4096)
    if kopf.startswith(b"\xff\xfe") or b"\x00" in kopf[:200]:
        raise ValueError(f"{pfad}: UTF-16 - bitte als ANSI/UTF-8 exportieren (DEADBAND_Daten_Export.mq5 tut das)")
    text = kopf.decode("latin-1")
    if text.startswith("<DATE>"):
        df = pd.read_csv(pfad, sep="\t")
        df.columns = [c.strip("<>").lower() for c in df.columns]
        server = pd.to_datetime(df["date"] + " " + df["time"], format="%Y.%m.%d %H:%M:%S")
        out = pd.DataFrame({"server": server, "open": df["open"], "high": df["high"], "low": df["low"],
                            "close": df["close"], "tickvol": df["tickvol"], "spread": df["spread"]})
    elif text.startswith("time,"):
        df = pd.read_csv(pfad)
        server = pd.to_datetime(df["time"].str.slice(0, 19), format="%Y-%m-%d %H:%M:%S")
        out = pd.DataFrame({"server": server, "open": df["open"], "high": df["high"], "low": df["low"],
                            "close": df["close"], "tickvol": df["tick_volume"], "spread": df["spread"]})
    else:
        raise ValueError(f"{pfad}: unbekanntes Format (Kopf {text[:40]!r})")
    out = out.sort_values("server", kind="stable").drop_duplicates("server", keep="last").reset_index(drop=True)
    return out


def schreibe_mt5(df, pfad, digits=2):
    """Format A (wie die GFT-Exporte, CRLF), lesbar von Replikat_v6/prep5.load."""
    s = df["server"]
    out = pd.DataFrame({"<DATE>": s.dt.strftime("%Y.%m.%d"), "<TIME>": s.dt.strftime("%H:%M:%S"),
                        "<OPEN>": df["open"].map(lambda x: f"{x:.{digits}f}"),
                        "<HIGH>": df["high"].map(lambda x: f"{x:.{digits}f}"),
                        "<LOW>": df["low"].map(lambda x: f"{x:.{digits}f}"),
                        "<CLOSE>": df["close"].map(lambda x: f"{x:.{digits}f}"),
                        "<TICKVOL>": df["tickvol"].astype(np.int64), "<VOL>": 0,
                        "<SPREAD>": df["spread"].astype(np.int64)})
    out.to_csv(pfad, sep="\t", index=False, lineterminator="\r\n")


def stichtag_grenze():
    return pd.Timestamp(K.STICHTAG_SERVER_ENDE)


def installiere(quellen, ziel=K.DATEN, ziel_blind=K.DATEN_BLIND, digits=None, protokoll=None):
    """quellen: dict Zieldateiname -> Quellpfad (z. B. {'XAUUSD.x_M5.csv': '.../XAUUSD.x_M5.csv'}).
    Schreibt die Auswahl-Daten (< Stichtag-Grenze) nach ziel und alles nach ziel_blind. Liefert ein Manifest."""
    os.makedirs(ziel, exist_ok=True)
    os.makedirs(ziel_blind, exist_ok=True)
    grenze = stichtag_grenze()
    manifest = {"stichtag_grenze_server": str(grenze), "dateien": {}}
    for name, pfad in quellen.items():
        df = lies_mt5(pfad)
        dg = (digits or {}).get(name, 2)
        auswahl = df[df["server"] < grenze]
        schreibe_mt5(auswahl, os.path.join(ziel, name), dg)
        schreibe_mt5(df, os.path.join(ziel_blind, name), dg)
        manifest["dateien"][name] = dict(
            quelle=os.path.basename(pfad), sha256_quelle=_sha256(pfad), zeilen=int(len(df)),
            zeilen_auswahl=int(len(auswahl)), erste=str(df["server"].iloc[0]) if len(df) else None,
            letzte_auswahl=str(auswahl["server"].iloc[-1]) if len(auswahl) else None)
    if protokoll:
        os.makedirs(os.path.dirname(protokoll), exist_ok=True)
        with open(protokoll, "w") as f:
            json.dump(manifest, f, indent=1)
    return manifest


def ny_minuten(server):
    """Serverzeit (datetime64) -> NY-Minuten seit Epoche."""
    t = pd.to_datetime(server) - pd.Timedelta(hours=K.NY_VERSATZ_H)
    return t.values.astype("datetime64[m]").astype(np.int64)


def protokolliere_blindzugriff(was, grund=""):
    """Jeder Zugriff auf data_blind/ wird mit Zeitstempel protokolliert (der Blindlauf findet genau einmal statt)."""
    os.makedirs(K.ERGEBNISSE, exist_ok=True)
    with open(os.path.join(K.ERGEBNISSE, "blindlauf_protokoll.txt"), "a") as f:
        f.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()} blind geoeffnet: {was} - {grund}\n")


def letzte_serverzeit(pfad):
    """Serverzeit der letzten Zeile einer MT5-CSV (nur das Dateiende wird gelesen)."""
    with open(pfad, "rb") as f:
        f.seek(0, os.SEEK_END)
        n = f.tell()
        f.seek(max(0, n - 4096))
        zeilen = [z for z in f.read().decode("utf-8", "replace").splitlines() if z.strip()]
    z = zeilen[-1]
    if z[4:5] == ".":                                     # MT5: YYYY.MM.DD<TAB>HH:MM:SS
        teile = z.split("\t")
        return pd.Timestamp(teile[0].replace(".", "-") + " " + teile[1])
    return pd.Timestamp(z[:19])                           # Python-Export: YYYY-MM-DD HH:MM:SS+00:00,...


def pruefe_auswahl_ordner(ordner=K.DATEN):
    """Kein CSV in data/ darf Zeilen ab dem Stichtag enthalten (sonst ist die Auswahl verunreinigt)."""
    grenze = stichtag_grenze()
    for fn in sorted(os.listdir(ordner)):
        if fn.lower().endswith(".csv") and letzte_serverzeit(os.path.join(ordner, fn)) >= grenze:
            raise RuntimeError(f"{fn} in {ordner} enthaelt Daten nach dem Stichtag - Auswahl-Daten sind verunreinigt")


def lade(dateiname, blind=False, grund=""):
    """Arrays ny, o, h, l, c, v, sp_pkt (Spread in Punkten) aus data/ (Auswahl) oder data_blind/ (nur Blindlauf)."""
    if blind:
        protokolliere_blindzugriff(dateiname, grund)
        pfad = os.path.join(K.DATEN_BLIND, dateiname)
    else:
        pfad = os.path.join(K.DATEN, dateiname)
    df = lies_mt5(pfad)
    if not blind and len(df) and df["server"].iloc[-1] >= stichtag_grenze():
        raise RuntimeError(f"{pfad} enthaelt Daten nach dem Stichtag - Auswahl-Daten sind verunreinigt")
    return dict(ny=ny_minuten(df["server"]), o=df["open"].to_numpy(float), h=df["high"].to_numpy(float),
                l=df["low"].to_numpy(float), c=df["close"].to_numpy(float), v=df["tickvol"].to_numpy(float),
                sp_pkt=df["spread"].to_numpy(float))


def aggregiere(ny, o, h, l, c, v, minuten, versatz=0):
    """Balken aus feineren Balken wie Replikat_v6/prep5.agg: Schluessel floor((ny+versatz)/minuten).
    D1 = Servertag: minuten 1440, versatz 420."""
    key = (ny + versatz) // minuten
    uniq, first = np.unique(key, return_index=True)
    last = np.r_[first[1:] - 1, len(ny) - 1]
    return dict(t=uniq * minuten - versatz, o=o[first], h=np.maximum.reduceat(h, first),
                l=np.minimum.reduceat(l, first), c=c[last], v=np.add.reduceat(v, first), first=first, last=last, key=uniq)


def prop_tag(ny):
    """Prop-Tag-Schluessel (Servertag) je NY-Minute."""
    return (np.asarray(ny) + 420) // 1440
