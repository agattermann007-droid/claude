# -*- coding: utf-8 -*-
"""
DEADBAND V9 - Datenexport aus dem LAUFENDEN GFT-MetaTrader-5. NUR LESEN: handelt nicht, aendert nichts an MT5, am EA
oder am Konto, startet MT5 nicht selbst, ueberschreibt und loescht keine bestehende Datei (alles kommt in einen NEUEN Ordner).

Was exportiert wird (alles in den neuen Ordner DEADBAND_Daten_<JJJJMMTT_HHMM>):
  1. Kerzen NAS100.x und XAUUSD.x in M5 und D1 (M1 mit --tf M1,M5,D1) ab --start (Voreinstellung 2010) bis jetzt, MT5-Exportformat
     (Tab, <DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>, Serverzeit), ZIP je Jahr (< 9 MB).
     Luecken > 84 h zwischen zwei Kerzen werden bis zu 3-mal nachgeladen; was bleibt, steht in PRUEFUNG.txt.
  2. Ticks (Bid/Ask) ab --ticks-ab (Voreinstellung 01.10.2026) bis jetzt, ZIP je Tag.
  3. Symboldaten (symbol_info) als JSON, Serverzeit-Versatz zu UTC.
  4. Kontohistorie: Deals und Orders ab --konto-ab (Voreinstellung 01.08.2026) als CSV, Kontokopf (ohne Namen) als JSON.
  5. Kopien (nur lesen) aus dem MT5-Datenordner: EA-Logs und Terminal-Journal ab --dateien-ab, MQL5\\Files\\DEADBAND*,
     Chartprofile (*.chr) und Presets (*.set) mit DEADBAND, Liste aller DEADBAND-Experten (+ Quelltexte ab --dateien-ab).
  6. MANIFEST.txt (jede Datei mit Zeilen, Zeitraum, Groesse, SHA-256) und PRUEFUNG.txt (Kurzbericht).

Aufruf:  py -3 DEADBAND_Datenexport.py [--path "C:\\...\\terminal64.exe"] [--ziel "D:\\Ordner"] [--start 2010-01-01]
         [--tf M5,D1] [--ticks-ab 2026-10-01] [--ohne-ticks] [--konto-ab 2026-08-01] [--dateien-ab 2026-09-01] [--ohne-dateien]
"""
import argparse, datetime as dt, glob, hashlib, io, json, os, string, subprocess, sys, time, zipfile, zlib

try:
    import MetaTrader5 as mt5
    import numpy as np
    import pandas as pd
except ImportError as e:
    print("FEHLT:", e, "-> py -3 -m pip install --user MetaTrader5 pandas numpy")
    sys.exit(1)

SYMBOLE = ["NAS100.x", "XAUUSD.x"]
MAX_ZIP = 9 * 1024 * 1024
LUECKE_S = 84 * 3600                       # laenger als ein langes Wochenende = Ausfall
UTC = dt.timezone.utc
LOG = []                                   # Meldungen fuer PRUEFUNG.txt


def melde(txt):
    print(txt, flush=True)
    LOG.append(txt)


# ------------------------------------------------------------------ Verbindung (nur an ein laufendes Terminal)
def laufende_terminals():
    """Pfade laufender terminal64.exe (Windows). None = nicht feststellbar."""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Get-Process terminal64 -ErrorAction SilentlyContinue | ForEach-Object { if ($_.Path) { $_.Path } else { '?' } }"],
                           capture_output=True, text=True, timeout=30)
        return [z.strip() for z in r.stdout.splitlines() if z.strip()]
    except Exception:
        return None


def verbinden(pfad):
    lt = laufende_terminals()
    if lt is not None:
        if not lt:
            melde("ABBRUCH: Kein MT5 (terminal64.exe) laeuft. Bitte GFT-MT5 starten und einloggen - das Skript startet MT5 nicht selbst.")
            sys.exit(2)
        if len(lt) > 1 and not pfad:
            melde("ABBRUCH: Mehrere MT5 laufen:\n  " + "\n  ".join(lt) + "\nBitte --path mit dem GFT-terminal64.exe angeben.")
            sys.exit(2)
        bekannt = [os.path.normcase(os.path.abspath(p)) for p in lt if p != "?"]
        if pfad and "?" not in lt and os.path.normcase(os.path.abspath(pfad)) not in bekannt:
            melde(f"ABBRUCH: {pfad} laeuft nicht. Laufend: {lt}")
            sys.exit(2)
        if not pfad and lt[0] != "?":
            pfad = lt[0]
    ok = mt5.initialize(path=pfad) if pfad else mt5.initialize()
    if not ok:
        melde(f"ABBRUCH: MT5 nicht erreichbar: {mt5.last_error()}")
        sys.exit(2)
    acc, ti = mt5.account_info(), mt5.terminal_info()
    if acc is None or ti is None:
        melde("ABBRUCH: MT5 meldet kein eingeloggtes Konto. Bitte in MT5 einloggen (das Skript loggt sich nicht ein).")
        mt5.shutdown()
        sys.exit(2)
    melde(f"Verbunden: Server {acc.server}, Firma {acc.company}, Konto {acc.login}, Terminal {ti.path}, Datenordner {ti.data_path}")
    if not any(k in (acc.server + " " + acc.company).upper() for k in ("GFT", "GOAT")):
        melde("WARNUNG: Server/Firma enthalten weder GFT noch GOAT - ist das das GFT-Terminal? Sonst --path angeben.")
    melde(f"Max. Balken im Chart: {ti.maxbars}")
    if ti.maxbars < 5_000_000:
        melde("HINWEIS: MT5 liefert hoechstens 'Max. Balken im Chart' Kerzen je Zeitrahmen. Fehlt deshalb Historie: Alex fragen, ob er "
              "Extras -> Optionen -> Charts -> Max. Balken im Chart = Unbegrenzt setzt (MT5-Neustart noetig, nur ohne offene Position).")
    return acc, ti


# ------------------------------------------------------------------ Hilfen
def neuer_ordner(basis):
    name = "DEADBAND_Daten_" + dt.datetime.now().strftime("%Y%m%d_%H%M")
    p = os.path.join(basis, name)
    i = 2
    while os.path.exists(p):
        p = os.path.join(basis, f"{name}_{i}")
        i += 1
    os.makedirs(p)
    return p


def drive_ordner():
    kand = [f"{lw}:\\{n}" for lw in string.ascii_uppercase[3:] for n in ("Meine Ablage", "My Drive")]
    home = os.path.expanduser("~")
    kand += [os.path.join(home, n) for n in ("Google Drive\\Meine Ablage", "Google Drive\\My Drive", "My Drive", "Google Drive")]
    for p in kand:
        if os.path.isdir(p):
            return p
    return None


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def zip_neu(pfad, eintraege):
    """Neue ZIP (Name darf noch nicht existieren) mit [(name, bytes)]. Rueckgabe Groesse."""
    assert not os.path.exists(pfad), pfad
    with zipfile.ZipFile(pfad, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n, b in eintraege:
            z.writestr(n, b)
    return os.path.getsize(pfad)


def zips_geteilt(ziel, basis, eintraege, manifest):
    """Eintraege auf ZIPs < 9 MB verteilen (basis_1.zip, basis_2.zip ...), schon komprimiert gemessen."""
    teil, n, groesse = [], 1, 0
    def raus(teil, n):
        p = os.path.join(ziel, f"{basis}_{n}.zip")
        g = zip_neu(p, teil)
        manifest.append(f"{os.path.basename(p)}\t{len(teil)} Dateien\t-\t-\t{g}\t{sha256(p)}")
    for name, b in eintraege:
        k = len(zlib.compress(b, 6))
        if teil and groesse + k > MAX_ZIP * 0.95:
            raus(teil, n); n += 1; teil, groesse = [], 0
        teil.append((name, b)); groesse += k
    if teil:
        raus(teil, n)


def zeit(ts):
    return pd.to_datetime(ts, unit="s")


# ------------------------------------------------------------------ Kerzen
TF = {"M1": (lambda: mt5.TIMEFRAME_M1, 60), "M5": (lambda: mt5.TIMEFRAME_M5, 300), "D1": (lambda: mt5.TIMEFRAME_D1, 86400)}


def bars_holen(sym, tf, a, b):
    r = None
    for _ in range(4):
        r = mt5.copy_rates_range(sym, tf, a, b)
        if r is not None:
            break
        time.sleep(1.5)
    return None if r is None or not len(r) else pd.DataFrame(r)


def bars(sym, tfn, start, ende):
    tf = TF[tfn][0]()
    teile, fehler = [], 0
    a = dt.datetime(start.year, start.month, 1, tzinfo=UTC)
    schritt = 12 if tfn == "D1" else 1
    while a < ende:
        m = a.month - 1 + schritt
        b = dt.datetime(a.year + m // 12, m % 12 + 1, 1, tzinfo=UTC)
        d = bars_holen(sym, tf, a, b)
        if d is not None:
            teile.append(d)
        a = b
    if not teile:
        return None, []
    df = pd.concat(teile, ignore_index=True).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    # Luecken nachladen (bis 3 Durchgaenge); D1: erst ab 5 Tagen (langes Wochenende = 4 Tage)
    grenze = 120 * 3600 if tfn == "D1" else LUECKE_S
    rest = []
    for runde in range(3):
        t = df["time"].to_numpy()
        lu = [(int(t[i - 1]), int(t[i])) for i in np.nonzero(np.diff(t) > grenze)[0] + 1]
        if not lu:
            break
        neu = []
        for (x, y) in lu:
            d = bars_holen(sym, tf, dt.datetime.fromtimestamp(x, UTC), dt.datetime.fromtimestamp(y, UTC))
            if d is not None:
                neu.append(d)
        if neu:
            df = pd.concat([df] + neu, ignore_index=True).drop_duplicates("time").sort_values("time").reset_index(drop=True)
        rest = lu
        time.sleep(2)
    t = df["time"].to_numpy()
    rest = [(int(t[i - 1]), int(t[i])) for i in np.nonzero(np.diff(t) > grenze)[0] + 1]
    return df, rest


def als_mt5_csv(df, digits):
    t = zeit(df["time"])
    f = f"{{:.{digits}f}}".format
    out = io.StringIO()
    out.write("<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\r\n")
    d, h = t.dt.strftime("%Y.%m.%d").to_numpy(), t.dt.strftime("%H:%M:%S").to_numpy()
    o, hi, lo, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    tv, rv, sp = (df[k].to_numpy() for k in ("tick_volume", "real_volume", "spread"))
    for i in range(len(df)):
        out.write(f"{d[i]}\t{h[i]}\t{f(o[i])}\t{f(hi[i])}\t{f(lo[i])}\t{f(c[i])}\t{tv[i]}\t{rv[i]}\t{sp[i]}\r\n")
    return out.getvalue().encode("ascii")


def bars_schreiben(ziel, kurz, tfn, df, digits, manifest):
    jahre = zeit(df["time"]).dt.year
    zeilen_jahr = {}
    for j in sorted(jahre.unique()):
        teil = df[jahre == j]
        zeilen_jahr[int(j)] = len(teil)
        monat = zeit(teil["time"]).dt.month
        for n in (1, 2, 4, 12):
            stuecke = [s for s in (teil[(monat - 1) // (12 // n) == k] for k in range(n)) if len(s)]
            erg, zu_gross = [], False
            for k, s in enumerate(stuecke):
                suff = f"_{k + 1}von{n}" if n > 1 else ""
                zp = os.path.join(ziel, f"{kurz}_{tfn}_{j}{suff}.zip")
                g = zip_neu(zp, [(f"{kurz}_{tfn}_{j}{suff}.csv", als_mt5_csv(s, digits))])
                erg.append((zp, f"{os.path.basename(zp)}\t{len(s)}\t{zeit(s['time'].iloc[0])}\t{zeit(s['time'].iloc[-1])}\t{g}"))
                zu_gross |= g > MAX_ZIP
            if not zu_gross or n == 12:
                break
            for zp, _ in erg:                       # eigene, gerade angelegte Datei - neu aufteilen
                os.remove(zp)
        for zp, z in erg:
            manifest.append(f"{z}\t{sha256(zp)}")
    return zeilen_jahr


# ------------------------------------------------------------------ Ticks
def ticks_csv(d, digits):
    f = f"{{:.{digits}f}}".format
    out = io.StringIO()
    out.write("time_msc;bid;ask;last;volume;flags\r\n")
    for tm, bi, ak, la, vo, fl in zip(d["time_msc"], d["bid"], d["ask"], d["last"], d["volume"], d["flags"]):
        out.write(f"{tm};{f(bi)};{f(ak)};{f(la)};{vo};{fl}\r\n")
    return out.getvalue().encode("ascii")


def ticks(ziel, sym, kurz, digits, von, bis, manifest):
    tag = dt.datetime(von.year, von.month, von.day, tzinfo=UTC)
    n_ges = 0
    while tag < bis:
        nxt = tag + dt.timedelta(days=1)
        r = None
        for _ in range(3):
            r = mt5.copy_ticks_range(sym, tag, nxt, mt5.COPY_TICKS_ALL)
            if r is not None:
                break
            time.sleep(1.5)
        if r is not None and len(r):
            d = pd.DataFrame(r)
            n_ges += len(d)
            b = ticks_csv(d, digits)
            name = f"{kurz}_TICKS_{tag:%Y%m%d}"
            zp = os.path.join(ziel, name + ".zip")
            g = zip_neu(zp, [(name + ".csv", b)])
            if g > MAX_ZIP:                          # eigene Datei: in 4 Teile zu je 6 Stunden aufteilen
                os.remove(zp)
                h = pd.to_datetime(d["time_msc"], unit="ms").dt.hour.to_numpy() // 6
                for k in range(4):
                    s = d[h == k]
                    if not len(s):
                        continue
                    zk = os.path.join(ziel, f"{name}_{k + 1}von4.zip")
                    gk = zip_neu(zk, [(f"{name}_{k + 1}von4.csv", ticks_csv(s, digits))])
                    manifest.append(f"{os.path.basename(zk)}\t{len(s)}\t-\t-\t{gk}\t{sha256(zk)}")
            else:
                manifest.append(f"{os.path.basename(zp)}\t{len(d)}\t-\t-\t{g}\t{sha256(zp)}")
        tag = nxt
    return n_ges


# ------------------------------------------------------------------ Konto und Symbole
def satz_liste(recs):
    return pd.DataFrame([r._asdict() for r in recs]) if recs else pd.DataFrame()


def konto(ziel, acc, von, bis, manifest):
    kopf = {k: getattr(acc, k, None) for k in ("login", "server", "company", "currency", "balance", "equity", "profit", "margin",
                                               "margin_free", "leverage", "trade_mode", "margin_mode", "limit_orders")}
    p = os.path.join(ziel, "Konto.json")
    with open(p, "x", encoding="utf-8") as fh:
        json.dump(kopf, fh, indent=1, default=str)
    erg = {}
    for name, fn in (("Deals", mt5.history_deals_get), ("Orders", mt5.history_orders_get)):
        recs = fn(von, bis)
        df = satz_liste(recs)
        q = os.path.join(ziel, f"Konto_{name}.csv")
        with open(q, "x", encoding="utf-8", newline="") as fh:
            df.to_csv(fh, sep=";", index=False)
        manifest.append(f"{os.path.basename(q)}\t{len(df)}\t{von:%Y-%m-%d}\t{bis:%Y-%m-%d}\t{os.path.getsize(q)}\t{sha256(q)}")
        erg[name] = len(df)
    return erg


def symbole_json(ziel, syms):
    out = {}
    for s in syms:
        i = mt5.symbol_info(s)
        out[s] = i._asdict() if i is not None else None
    p = os.path.join(ziel, "Symbole.json")
    with open(p, "x", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)


def serverzeit(sym):
    t = mt5.symbol_info_tick(sym)
    if t is None or not t.time:
        return None
    jetzt = time.time()
    return dict(letzter_tick_server=str(zeit(t.time)), versatz_h=round((t.time - jetzt) / 3600.0, 2))


# ------------------------------------------------------------------ Dateien aus dem MT5-Datenordner (nur lesen)
def dateien(ziel, data_path, ab, manifest):
    ab_ts = ab.timestamp()
    gruppen = {
        "EA_Logs": [p for p in glob.glob(os.path.join(data_path, "MQL5", "Logs", "*.log")) if os.path.getmtime(p) >= ab_ts],
        "Terminal_Journal": [p for p in glob.glob(os.path.join(data_path, "Logs", "*.log")) if os.path.getmtime(p) >= ab_ts],
        "EA_Files": glob.glob(os.path.join(data_path, "MQL5", "Files", "DEADBAND*")),
    }
    def hat_deadband(p):
        try:
            b = open(p, "rb").read()
        except OSError:
            return False
        return b"DEADBAND" in b.upper() or "DEADBAND".encode("utf-16-le") in b or "deadband".encode("utf-16-le") in b
    gruppen["Chartprofile"] = [p for p in glob.glob(os.path.join(data_path, "MQL5", "Profiles", "**", "*.chr"), recursive=True) if hat_deadband(p)]
    gruppen["Presets"] = [p for p in glob.glob(os.path.join(data_path, "MQL5", "Presets", "**", "*.set"), recursive=True) if hat_deadband(p)]
    experten = sorted(set(glob.glob(os.path.join(data_path, "MQL5", "Experts", "**", "*DEADBAND*"), recursive=True)
                          + glob.glob(os.path.join(data_path, "MQL5", "Experts", "**", "*Deadband*"), recursive=True)))
    gruppen["Experten_Quelltext"] = [p for p in experten if p.lower().endswith(".mq5") and os.path.getmtime(p) >= ab_ts]
    liste = ["Datei\tBytes\tGeaendert\tSHA256"]
    for p in experten:
        if os.path.isfile(p):
            liste.append(f"{os.path.relpath(p, data_path)}\t{os.path.getsize(p)}\t{dt.datetime.fromtimestamp(os.path.getmtime(p)):%Y-%m-%d %H:%M}\t{sha256(p)}")
    q = os.path.join(ziel, "Experten_Liste.txt")
    with open(q, "x", encoding="utf-8", newline="\r\n") as fh:
        fh.write("\n".join(liste) + "\n")
    zahl = {}
    for g, ps in gruppen.items():
        eintraege = []
        for p in ps:
            try:
                with open(p, "rb") as fh:          # nur lesen; geteilter Zugriff mit dem laufenden MT5
                    eintraege.append((os.path.relpath(p, data_path).replace("\\", "/"), fh.read()))
            except OSError as e:
                melde(f"  nicht lesbar: {p} ({e})")
        zahl[g] = len(eintraege)
        if eintraege:
            zips_geteilt(ziel, g, eintraege, manifest)
    return zahl, len(experten)


# ------------------------------------------------------------------ Ablauf
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=None)
    ap.add_argument("--ziel", default=None)
    ap.add_argument("--start", default="2010-01-01")
    ap.add_argument("--tf", default="M5,D1")
    ap.add_argument("--ticks-ab", default="2026-10-01")
    ap.add_argument("--ohne-ticks", action="store_true")
    ap.add_argument("--konto-ab", default="2026-08-01")
    ap.add_argument("--dateien-ab", default="2026-09-01")
    ap.add_argument("--ohne-dateien", action="store_true")
    a = ap.parse_args()
    tag = lambda s: dt.datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=UTC)
    ende = dt.datetime.now(UTC) + dt.timedelta(days=2)

    acc, ti = verbinden(a.path)
    basis = a.ziel or drive_ordner() or os.path.join(os.path.expanduser("~"), "Desktop")
    ziel = neuer_ordner(basis)
    melde(f"Neuer Ordner: {ziel}" + ("  (Google-Drive-Ordner: wird automatisch hochgeladen)" if drive_ordner() and ziel.startswith(drive_ordner()) else ""))
    manifest = [f"DEADBAND Datenexport {dt.datetime.now():%Y-%m-%d %H:%M} (PC-Zeit)  Server {acc.server}  Konto {acc.login}  MaxBars {ti.maxbars}",
                "Datei\tZeilen\tErste\tLetzte\tBytes\tSHA256"]
    pruef = {"server": acc.server, "maxbars": ti.maxbars, "symbole": {}}

    syms = {}
    for name in SYMBOLE:
        if mt5.symbol_info(name) is None:
            stamm = name.split(".")[0]
            tr = [s.name for s in (mt5.symbols_get() or []) if stamm in s.name.upper()]
            melde(f"Symbol {name} fehlt; Kandidaten {tr[:6]}" + (f" -> nehme {tr[0]}" if tr else ""))
            if not tr:
                continue
            name = tr[0]
        info = mt5.symbol_info(name)
        if not info.visible:                         # nur falls nicht in der Marktuebersicht (der EA handelt beide, also normal sichtbar)
            melde(f"{name} war nicht in der Marktuebersicht - fuer den Export eingeblendet")
            mt5.symbol_select(name, True)
            info = mt5.symbol_info(name)
        syms[name] = info
    symbole_json(ziel, list(syms))
    for sym in syms:
        sz = serverzeit(sym)
        pruef["symbole"][sym] = {"serverzeit": sz}
        melde(f"{sym}: letzter Tick {sz}  (GFT erwartet: Server = New York + 7 h, also UTC+3 im Sommer)")

    for sym, info in syms.items():
        kurz = sym.replace(".", "_")
        for tfn in [x.strip().upper() for x in a.tf.split(",") if x.strip()]:
            melde(f"{sym} {tfn}: lade ab {a.start} ...")
            df, rest = bars(sym, tfn, tag(a.start), ende)
            if df is None:
                melde(f"  KEINE DATEN ({mt5.last_error()})")
                pruef["symbole"][sym][tfn] = "KEINE DATEN"
                continue
            zj = bars_schreiben(ziel, kurz, tfn, df, info.digits, manifest)
            t0, t1 = zeit(df["time"].iloc[0]), zeit(df["time"].iloc[-1])
            lu = [f"{zeit(x)} -> {zeit(y)} ({(y - x) / 86400:.1f} Tage)" for x, y in rest]
            pruef["symbole"][sym][tfn] = dict(kerzen=len(df), erste=str(t0), letzte=str(t1), je_jahr=zj, luecken_ueber_84h=lu)
            melde(f"  {len(df)} Kerzen {t0} .. {t1}; je Jahr {zj}")
            for x in lu:
                melde(f"  LUECKE (nach 3 Nachladeversuchen): {x}")
        if not a.ohne_ticks:
            melde(f"{sym} Ticks ab {a.ticks_ab} ...")
            n = ticks(ziel, sym, kurz, info.digits, tag(a.ticks_ab), ende, manifest)
            pruef["symbole"][sym]["ticks"] = n
            melde(f"  {n} Ticks")

    kv = konto(ziel, acc, tag(a.konto_ab), ende, manifest)
    pruef["konto"] = kv
    melde(f"Konto {acc.login}: {kv.get('Deals', 0)} Deals, {kv.get('Orders', 0)} Orders ab {a.konto_ab}")
    if not a.ohne_dateien:
        zahl, nexp = dateien(ziel, ti.data_path, tag(a.dateien_ab), manifest)
        pruef["dateien"] = zahl
        melde(f"Kopiert (nur gelesen): {zahl}; DEADBAND-Experten gelistet: {nexp}")

    with open(os.path.join(ziel, "MANIFEST.txt"), "x", encoding="utf-8", newline="\r\n") as fh:
        fh.write("\n".join(manifest) + "\n")
    with open(os.path.join(ziel, "PRUEFUNG.txt"), "x", encoding="utf-8", newline="\r\n") as fh:
        fh.write(json.dumps(pruef, indent=1, default=str) + "\n\nMeldungen:\n" + "\n".join(LOG) + "\n")
    mt5.shutdown()                                   # trennt nur die Python-Verbindung; MT5 und EA laufen weiter
    groesse = sum(os.path.getsize(os.path.join(ziel, f)) for f in os.listdir(ziel))
    print(f"\nFERTIG: {ziel}  ({len(os.listdir(ziel))} Dateien, {groesse / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
