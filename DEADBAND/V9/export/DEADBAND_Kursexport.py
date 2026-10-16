# -*- coding: utf-8 -*-
"""
DEADBAND V9 - Kursexport aus dem laufenden GFT-MT5 (NAS100.x, XAUUSD.x; M1 und M5).

Ablauf:
  1. GFT-MT5 offen und eingeloggt lassen.
  2. Doppelklick auf DEADBAND_Kursexport.cmd (installiert bei Bedarf MetaTrader5 + pandas).
  3. Das Skript legt einen NEUEN Ordner "DEADBAND_Kursdaten_<Datum>" an:
     - im Google-Drive-Ordner (Google Drive fuer Desktop, "Meine Ablage"/"My Drive"), falls gefunden,
     - sonst auf dem Desktop (dann diesen Ordner in Google Drive hochladen).
     Darin je Symbol, Zeitrahmen und Jahr eine ZIP (< 9 MB) im MT5-Exportformat
     (Tab-getrennt, <DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>, Serverzeit)
     und MANIFEST.txt (Zeilen, erster/letzter Zeitpunkt, SHA-256 je ZIP).
Es wird nichts gehandelt und keine bestehende Datei ueberschrieben.

Optionen:  --start 2010-01-01   --tf M1,M5   --path "C:\\...\\terminal64.exe"   --ziel "D:\\Ordner"
"""
import argparse, datetime as dt, hashlib, io, os, string, sys, time, zipfile

try:
    import MetaTrader5 as mt5
    import numpy as np
    import pandas as pd
except ImportError as e:
    print("FEHLT:", e, "-> bitte DEADBAND_Kursexport.cmd starten (installiert MetaTrader5 und pandas).")
    sys.exit(1)

SYMBOLE = ["NAS100.x", "XAUUSD.x"]
MAX_ZIP = 9 * 1024 * 1024
UTC = dt.timezone.utc


def drive_ordner():
    """Google Drive fuer Desktop: Laufwerk mit 'Meine Ablage'/'My Drive' oder Ordner im Benutzerprofil."""
    kand = []
    for lw in string.ascii_uppercase[3:]:
        for n in ("Meine Ablage", "My Drive"):
            kand.append(f"{lw}:\\{n}")
    home = os.path.expanduser("~")
    for n in ("Google Drive\\Meine Ablage", "Google Drive\\My Drive", "My Drive", "Google Drive"):
        kand.append(os.path.join(home, n))
    for p in kand:
        if os.path.isdir(p):
            return p
    return None


def neuer_ordner(basis):
    name = "DEADBAND_Kursdaten_" + dt.datetime.now().strftime("%Y%m%d_%H%M")
    p = os.path.join(basis, name)
    i = 2
    while os.path.exists(p):
        p = os.path.join(basis, f"{name}_{i}")
        i += 1
    os.makedirs(p)
    return p


def verbinden(pfad):
    ok = mt5.initialize(path=pfad) if pfad else mt5.initialize()
    if not ok:
        print("MT5 nicht erreichbar:", mt5.last_error())
        print("-> GFT-MT5 starten und einloggen, oder --path \"...\\terminal64.exe\" angeben.")
        sys.exit(2)
    acc, ti = mt5.account_info(), mt5.terminal_info()
    server = acc.server if acc else "?"
    print(f"Verbunden: Server {server}, Firma {acc.company if acc else '?'}, Terminal {ti.path if ti else '?'}")
    if acc and not any(k in (server + " " + acc.company).upper() for k in ("GFT", "GOAT")):
        print("WARNUNG: Das scheint kein GFT-Terminal zu sein. Bei mehreren MT5 bitte --path zum GFT-terminal64.exe angeben.")
    if ti is not None:
        print(f"Max. Balken im Chart: {ti.maxbars}")
        if ti.maxbars < 5_000_000:
            print("HINWEIS: MT5 liefert hoechstens 'Max. Balken im Chart' Kerzen. Fuer die volle Historie:")
            print("         Extras -> Optionen -> Charts -> Max. Balken im Chart = Unbegrenzt, MT5 neu starten, Skript erneut starten.")
    return server


def symbol_finden(name):
    if mt5.symbol_info(name) is not None:
        mt5.symbol_select(name, True)
        return name
    stamm = name.split(".")[0]
    treffer = [s.name for s in (mt5.symbols_get() or []) if stamm in s.name.upper()]
    if treffer:
        print(f"Symbol {name} nicht gefunden, nehme {treffer[0]} (Kandidaten: {treffer[:6]})")
        mt5.symbol_select(treffer[0], True)
        return treffer[0]
    print(f"Symbol {name} nicht gefunden.")
    return None


def holen(sym, tf, start, ende):
    """Kerzen in Monatsstuecken holen (MT5 laedt fehlende Historie dabei vom Server nach)."""
    teile = []
    a = dt.datetime(start.year, start.month, 1, tzinfo=UTC)
    while a < ende:
        b = dt.datetime(a.year + (a.month == 12), a.month % 12 + 1, 1, tzinfo=UTC)
        r = None
        for versuch in range(4):
            r = mt5.copy_rates_range(sym, tf, a, b)
            if r is not None:
                break
            time.sleep(1.5)
        if r is not None and len(r):
            teile.append(pd.DataFrame(r))
        a = b
    if not teile:
        return None
    df = pd.concat(teile, ignore_index=True).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    return df


def als_mt5_csv(df, digits):
    t = pd.to_datetime(df["time"], unit="s")          # Kerzenzeit = Serverzeit (MT5 speichert sie als Sekunden)
    f = f"{{:.{digits}f}}".format
    out = io.StringIO()
    out.write("<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\r\n")
    d, h = t.dt.strftime("%Y.%m.%d").to_numpy(), t.dt.strftime("%H:%M:%S").to_numpy()
    o, hi, lo, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    tv, rv, sp = (df[k].to_numpy() for k in ("tick_volume", "real_volume", "spread"))
    for i in range(len(df)):
        out.write(f"{d[i]}\t{h[i]}\t{f(o[i])}\t{f(hi[i])}\t{f(lo[i])}\t{f(c[i])}\t{tv[i]}\t{rv[i]}\t{sp[i]}\r\n")
    return out.getvalue().encode("ascii")


def zip_schreiben(pfad, name_csv, daten):
    with zipfile.ZipFile(pfad, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr(name_csv, daten)
    return os.path.getsize(pfad)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2010-01-01")
    ap.add_argument("--tf", default="M5,M1")
    ap.add_argument("--path", default=None)
    ap.add_argument("--ziel", default=None)
    a = ap.parse_args()
    start = dt.datetime.strptime(a.start, "%Y-%m-%d").replace(tzinfo=UTC)
    ende = dt.datetime.now(UTC) + dt.timedelta(days=2)
    tfs = {"M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5}

    server = verbinden(a.path)
    basis = a.ziel or drive_ordner()
    if basis:
        print("Zielbasis:", basis)
    else:
        basis = os.path.join(os.path.expanduser("~"), "Desktop")
        print("Kein Google-Drive-Ordner gefunden -> Desktop. Den neuen Ordner danach in Google Drive hochladen.")
    ziel = neuer_ordner(basis)
    print("Neuer Ordner:", ziel)

    manifest = [f"DEADBAND Kursexport {dt.datetime.now():%Y-%m-%d %H:%M}  Server {server}  Start {a.start}",
                "Datei\tZeilen\tErste Kerze\tLetzte Kerze\tBytes\tSHA256"]
    for name in SYMBOLE:
        sym = symbol_finden(name)
        if not sym:
            manifest.append(f"{name}\tFEHLT")
            continue
        digits = mt5.symbol_info(sym).digits
        kurz = sym.replace(".", "_")
        for tfn in [x.strip().upper() for x in a.tf.split(",") if x.strip()]:
            print(f"{sym} {tfn}: lade ...", flush=True)
            df = holen(sym, tfs[tfn], start, ende)
            if df is None or df.empty:
                print(f"  keine Daten ({mt5.last_error()})")
                manifest.append(f"{kurz}_{tfn}\tKEINE DATEN")
                continue
            jahre = pd.to_datetime(df["time"], unit="s").dt.year
            print(f"  {len(df)} Kerzen, {pd.to_datetime(df['time'].iloc[0], unit='s')} .. {pd.to_datetime(df['time'].iloc[-1], unit='s')}")
            for j in sorted(jahre.unique()):
                teil = df[jahre == j]
                monat = pd.to_datetime(teil["time"], unit="s").dt.month
                # erst ein Jahr je ZIP; ist die ZIP groesser als 9 MB, dieselbe (eigene, neue) Datei loeschen
                # und das Jahr halb-, viertel- bzw. monatsweise schreiben
                for n in (1, 2, 4, 12):
                    stuecke = [teil[(monat - 1) // (12 // n) == k] for k in range(n)]
                    stuecke = [s for s in stuecke if len(s)]
                    zeilen, zu_gross = [], False
                    for k, s in enumerate(stuecke):
                        suff = f"_{k + 1}von{n}" if n > 1 else ""
                        csvn = f"{kurz}_{tfn}_{j}{suff}.csv"
                        zp = os.path.join(ziel, f"{kurz}_{tfn}_{j}{suff}.zip")
                        groesse = zip_schreiben(zp, csvn, als_mt5_csv(s, digits))
                        t0, t1 = (pd.to_datetime(s["time"].iloc[i], unit="s") for i in (0, -1))
                        zeilen.append((zp, f"{os.path.basename(zp)}\t{len(s)}\t{t0}\t{t1}\t{groesse}\t{sha256(zp)}"))
                        zu_gross |= groesse > MAX_ZIP
                    if not zu_gross or n == 12:
                        break
                    for zp, _ in zeilen:
                        os.remove(zp)
                for zp, z in zeilen:
                    manifest.append(z)
                    print(f"  {os.path.basename(zp)}: {z.split(chr(9))[1]} Zeilen, {os.path.getsize(zp) / 1e6:.1f} MB")
    with open(os.path.join(ziel, "MANIFEST.txt"), "w", encoding="utf-8", newline="\r\n") as fh:
        fh.write("\n".join(manifest) + "\n")
    mt5.shutdown()
    print("\nFERTIG:", ziel)
    print("Liegt der Ordner nicht im Google-Drive-Ordner: bitte in Google Drive hochladen (Ordner egal).")


if __name__ == "__main__":
    main()
