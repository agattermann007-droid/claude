# Auftrag für die Claude-Sitzung auf Alex' PC: MT5-Kursexport für DEADBAND V9

Du läufst **auf Alex' Windows-PC**, auf dem das GFT-MetaTrader-5 läuft (Konto GFT Instant Premium 10k, EA DEADBAND im Echtbetrieb).
Eine Cloud-Sitzung („DEADBAND V9 Entwicklung“) hat V9 gebaut und braucht dafür die echten GFT-Kurse. Sie kommt selbst nicht an MT5 heran.
**Deine einzige Aufgabe:** die Kurshistorie von `NAS100.x` und `XAUUSD.x` aus dem laufenden GFT-MT5 exportieren und so ablegen,
dass Alex sie der Cloud-Sitzung geben kann. Antworte Alex auf Deutsch, kurz.

## Was schon da ist und was fehlt

- Alex hat bereits M5-Exporte von **03.01.2022 bis 02.09.2026 16:20** (Serverzeit) hochgeladen.
- **Es fehlt vor allem September und Oktober 2026 bis heute.** Am wichtigsten ist NAS100.x vom 01.10. bis heute, für den Abgleich der 17 Live-Trades vom 01.–16.10.2026.
- Erwünscht ist so viel Historie, wie der GFT-Server liefert (Start 2010), in **M5 und M1**.

## Grenzen (verbindlich)

- **Erlaubt:** lesen, rechnen, neue Dateien und Ordner anlegen, das Exportskript unten ausführen, die Python-Pakete `MetaTrader5`, `pandas` und `numpy` per `pip install --user` installieren (kostenlos).
- **Erst Alex fragen und auf seine Antwort warten, bevor du:**
  - irgendetwas handelst, Orders oder Positionen anfasst;
  - den laufenden EA, seinen Chart, seine Eingaben oder das Konto änderst;
  - MT5-Einstellungen änderst (auch „Max. Balken im Chart“) oder MT5 neu startest oder schließt;
  - eine bestehende Datei überschreibst oder löschst (nur neue Namen anlegen);
  - etwas kaufst oder eine kostenpflichtige Datenquelle nutzt.
- **Nicht in MT5 einloggen** und keine Zugangsdaten eingeben oder erfragen. MT5 muss schon laufen und eingeloggt sein. Wenn nicht, Alex bitten, es zu starten.
- Das Skript handelt nicht. `mt5.initialize()` verbindet sich nur lesend mit dem laufenden Terminal, `mt5.shutdown()` trennt nur diese Verbindung; MT5 und der EA laufen weiter.

## Schritte

1. **Prüfen:** Läuft `terminal64.exe` vom GFT-MT5? In PowerShell: `Get-Process terminal64 | Select-Object Path`.
   - Laufen mehrere MT5: den Pfad des GFT-Terminals merken und später als `--path` übergeben.
   - Läuft keins: Alex bitten, GFT-MT5 zu starten und einzuloggen. Nicht selbst starten.
2. **Python:** `py -3 --version`, sonst `python --version`. Das MetaTrader5-Paket braucht 64-bit-Python 3.8 bis 3.12 unter Windows.
   - Fehlt Python: Alex fragen, ob du Python 3.12 (64 bit) von python.org installieren darfst.
   - Pakete installieren: `py -3 -m pip install --user MetaTrader5 pandas numpy`.
3. **Neuen Arbeitsordner anlegen,** z. B. `%USERPROFILE%\Documents\DEADBAND_Export_<JJJJMMTT>`. Darin das Skript unten unverändert als `DEADBAND_Kursexport.py` speichern.
4. **Ausführen** (aus dem Arbeitsordner):
   ```
   py -3 DEADBAND_Kursexport.py --start 2010-01-01 --tf M5,M1
   ```
   - Bei mehreren Terminals zusätzlich `--path "C:\...\terminal64.exe"` (GFT) angeben.
   - Ziel: Ohne `--ziel` legt das Skript einen **neuen** Ordner `DEADBAND_Kursdaten_<JJJJMMTT_HHMM>` im Google-Drive-Ordner an („Meine Ablage“/„My Drive“, falls Google Drive für Desktop installiert ist), sonst auf dem Desktop.
   - Dauer: einige Minuten; M1 ab 2010 dauert am längsten.
   - Bleibt M1 leer oder hängt es: zuerst nur `--tf M5` laufen lassen, M1 danach getrennt.
5. **Prüfen** (MANIFEST.txt im neuen Ordner und Konsolenausgabe):
   - Je Symbol M5 vorhanden, **letzte Kerze von heute** (Serverzeit = New York + 7 h, also kurz vor der aktuellen Serverzeit).
   - Erste Kerze notieren. Liefert der Server nur ab 2022, ist das in Ordnung.
   - Meldet das Skript „HINWEIS: MT5 liefert höchstens 'Max. Balken im Chart' Kerzen“ und fehlt deshalb Historie: Alex fragen, ob er `Extras → Optionen → Charts → Max. Balken im Chart = Unbegrenzt` setzen möchte. Das braucht einen MT5-Neustart, also nur am Wochenende oder wenn keine Position offen ist. Nicht selbst ändern.
   - Kurz gegenprüfen: Je Symbol und Jahr die Zeilen aus dem MANIFEST nennen. In M5 sind es etwa 68.000 bis 71.000 Zeilen je volles Jahr; so viele hatte Alex' Handexport 2022–2025.
   - Ausnahme NAS100.x 2024: Im Handexport waren es nur 54.434 Zeilen, dort fehlt ein Stück. Melde, ob der neue Export für 2024 mehr Zeilen hat.
6. **Übergabe an Alex** (eine kurze Nachricht):
   - Pfad des neuen Ordners.
   - Je Symbol und Zeitrahmen: erste und letzte Kerze, Zeilen gesamt.
   - Wie die Daten zur Cloud-Sitzung kommen:
     - **a)** Liegt der Ordner im Google-Drive-Ordner, wird er automatisch hochgeladen. Alex schreibt der Cloud-Sitzung nur: „Export liegt in Drive: DEADBAND_Kursdaten_…“.
     - **b)** Sonst zieht Alex die ZIP-Dateien direkt in den Chat der Cloud-Sitzung „DEADBAND V9 Entwicklung“ (je Datei unter 9 MB). Mindestens müssen dabei sein: `NAS100_x_M5_2026.zip` und `XAUUSD_x_M5_2026.zip`, dazu `MANIFEST.txt`.

## Format, das die Cloud-Sitzung erwartet

Tab-getrennt, wie der MT5-Export aus dem Symbolfenster:
`<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>`, Datum `JJJJ.MM.TT`, Zeit `HH:MM:SS` in **Serverzeit**,
Spread in Punkten. Dateinamen beginnen mit `NAS100` bzw. `XAUUSD` und enthalten `_M5_` bzw. `_M1_`. Das Skript erzeugt genau das.

## Falls das Python-Skript nicht läuft: Handexport (Alex macht das, du leitest an)

In MT5: `Strg+U` → Symbol `NAS100.x` doppelklicken → Reiter **Balken** → Zeitrahmen **M5** → Zeitraum von 01.01.2010 bis heute
→ **Abfragen** → **Exportieren** → als `NAS100.x_M5_<von>_<bis>.csv` speichern. Dasselbe für `XAUUSD.x`. Danach die CSV
zippen (je ZIP unter 9 MB, wenn nötig eine ZIP je Jahr) und wie in Schritt 6 übergeben.

## Das Exportskript (unverändert als `DEADBAND_Kursexport.py` speichern)

Quelle: Repo `agattermann007-droid/claude`, Branch `claude/peaceful-fermi-75ytyi`, Datei `DEADBAND/V9/export/DEADBAND_Kursexport.py`
(sha256 8c90064e762d5cb8da7b1e13a3772dc2134da04e6124048d7544d267bafb2d85).

```python
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
```
