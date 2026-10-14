"""Kalibrierungs-Gate (PLAN 4.4): MT5-Testerbericht (HTML oder XML, deutsch oder englisch) gegen eng6.

Pflicht: Tradezahl +-5 %, Netto +-10 %. Diagnose je Modul (Kommentar des Einstiegs-Deals).
Zaehlweise auf beiden Seiten gleich: ein Trade = eine Einstiegsidee
  - Wochenend-Wiederaufnahme ("DEADBAND WE", "RSI21 WE") setzt den Trade fort,
  - Noise-Teile mit gleicher Einstiegsminute sind ein Trade.
Netto = Summe Gewinn + Kommission + Swap aller Handels-Deals (Auszahlungen per TesterWithdrawal zaehlen nicht).
Referenzlauf eng6: wie der Tester ohne GFT-Abbruch (pleite_weiter=2, keine Regel-Pleiten), Auszahlung 1 Tag nach
Reife und flach (TesterAuszahlStd 24 h).
"""
import html
import re
from html.parser import HTMLParser

import numpy as np
import pandas as pd

GENERISCH = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S",
             "S0830", "LW", "XA", "TD"]                 # eng6-Strom s (z8 + z8_final.TD) -> EA-Name (FADE_STANDARD, 7.10, 8.00)
TOL_TRADES = 0.05
TOL_NETTO = 0.10

SPALTEN = {"zeit": ("time", "zeit"), "deal": ("deal",), "symbol": ("symbol",), "typ": ("type", "typ"),
           "richtung": ("direction", "richtung"), "volumen": ("volume", "volumen"), "preis": ("price", "preis"),
           "order": ("order", "auftrag"), "kommission": ("commission", "kommission", "provision"),
           "swap": ("swap",), "gewinn": ("profit", "gewinn"), "saldo": ("balance", "kontostand", "saldo"),
           "kommentar": ("comment", "kommentar")}


class _Zeilen(HTMLParser):
    def __init__(self):
        super().__init__()
        self.zeilen = []; self._z = None; self._c = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._z = []
        elif tag in ("td", "th") and self._z is not None:
            self._c = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._z is not None and self._c is not None:
            self._z.append(" ".join("".join(self._c).split()))
            self._c = None
        elif tag == "tr" and self._z is not None:
            self.zeilen.append(self._z); self._z = None

    def handle_data(self, data):
        if self._c is not None:
            self._c.append(data)


def _text(pfad):
    roh = open(pfad, "rb").read()
    if roh[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return roh.decode("utf-16")
    if roh[:3] == b"\xef\xbb\xbf":
        return roh[3:].decode("utf-8")
    try:
        return roh.decode("utf-8")
    except UnicodeDecodeError:
        return roh.decode("cp1252")


def zeilen(pfad):
    """Alle Tabellenzeilen des Berichts als Listen von Zelltexten (HTML-Bericht oder XML 'Excel 2003')."""
    t = _text(pfad)
    if "<Workbook" in t[:5000] or "urn:schemas-microsoft-com:office:spreadsheet" in t[:5000]:
        out = []
        for z in re.findall(r"<(?:ss:)?Row\b[^>]*>(.*?)</(?:ss:)?Row>", t, flags=re.S):
            out.append([" ".join(html.unescape(re.sub(r"<[^>]+>", "", c)).split())
                        for c in re.findall(r"<(?:ss:)?Cell\b[^>]*>(.*?)</(?:ss:)?Cell>", z, flags=re.S)])
        return out
    p = _Zeilen()
    p.feed(t)
    return p.zeilen


def _zahl(s):
    s = (s or "").replace("\xa0", "").replace(" ", "")
    if s == "":
        return 0.0
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    return float(s)


def deals(pfad):
    """DataFrame der Deals-Tabelle."""
    Z = zeilen(pfad)
    kopf = None
    for i, z in enumerate(Z):
        kl = [c.strip().lower() for c in z]
        if "deal" in kl and ("direction" in kl or "richtung" in kl):
            kopf = i
            break
    if kopf is None:
        raise ValueError(f"{pfad}: keine Deals-Tabelle gefunden")
    kl = [c.strip().lower() for c in Z[kopf]]
    idx = {}
    for name, syn in SPALTEN.items():
        for j, c in enumerate(kl):
            if c in syn:
                idx[name] = j
                break
    fehlt = [n for n in ("zeit", "typ", "richtung", "volumen", "gewinn", "kommentar", "symbol") if n not in idx]
    if fehlt:
        raise ValueError(f"{pfad}: Spalten fehlen {fehlt} (Kopf {Z[kopf]})")
    rows = []
    for z in Z[kopf + 1:]:
        if len(z) < len(kl) - 1 or not re.match(r"\d{4}\.\d{2}\.\d{2}", z[idx["zeit"]] if idx["zeit"] < len(z) else ""):
            if rows:
                break
            continue
        g = lambda n: z[idx[n]] if n in idx and idx[n] < len(z) else ""
        rows.append(dict(zeit=pd.Timestamp(g("zeit").replace(".", "-", 2)), symbol=g("symbol"), typ=g("typ").lower(),
                         richtung=g("richtung").lower(), volumen=_zahl(g("volumen")), preis=_zahl(g("preis")),
                         kommission=_zahl(g("kommission")), swap=_zahl(g("swap")), gewinn=_zahl(g("gewinn")),
                         saldo=_zahl(g("saldo")), kommentar=g("kommentar")))
    return pd.DataFrame(rows)


def modul_aus_kommentar(k):
    k = (k or "").strip()
    if k.startswith("DEADBAND"):
        return "DB"
    if k.startswith("RSI21"):
        return "R21"
    if k.startswith("NOISE"):
        return "NZ"
    if k.startswith("FADE "):
        return k[5:].split()[0]
    return "?"


def modul_eng6(slot):
    import eng6 as E
    slot = int(slot)
    if slot < 2:
        return "DB"
    if slot < E.NZ0:
        return "R21"
    if slot < E.NZ1:
        return "NZ"
    s = (slot - E.G0) // 2
    return GENERISCH[s] if s < len(GENERISCH) else f"g{s}"


_KAUF = ("buy", "kauf", "kaufen")
_VERKAUF = ("sell", "verkauf", "verkaufen")


def auswerten_mt5(df):
    """Trades (Ideen), Netto, Auszahlungen und Diagnose je Modul aus der Deals-Tabelle."""
    handel = df[df["typ"].isin(_KAUF + _VERKAUF)].copy()
    saldo = df[~df["typ"].isin(_KAUF + _VERKAUF)]
    netto = float((handel["gewinn"] + handel["kommission"] + handel["swap"]).sum())
    ein = handel[handel["richtung"].str.startswith(("in", "ein")) & ~handel["richtung"].str.contains("out|aus")]
    ideen = []
    for _, r in ein.iterrows():
        k = r["kommentar"]
        if k.endswith(" WE"):
            continue
        m = modul_aus_kommentar(k)
        schl = (m, r["symbol"], r["zeit"].floor("min")) if m == "NZ" else (m, r["symbol"], r["zeit"], r.name)
        ideen.append((m, schl))
    eindeutig = {s: m for m, s in ideen}
    je_modul_n = pd.Series(list(eindeutig.values())).value_counts().to_dict() if eindeutig else {}
    # Netto je Modul: Ausgangs-Deals der offenen Position desselben Symbols und derselben Richtung zuordnen
    # (eindeutig bei einer Position; sonst gleiche Restmenge, sonst die aelteste - heuristisch, nur Diagnose)
    offen = []
    je_modul_netto = {}
    mehrdeutig = 0
    for _, r in handel.iterrows():
        betrag = r["gewinn"] + r["kommission"] + r["swap"]
        if r["richtung"].startswith(("in", "ein")) and not re.search("out|aus", r["richtung"]):
            m = modul_aus_kommentar(r["kommentar"])
            offen.append([m, r["symbol"], 1 if r["typ"] in _KAUF else -1, r["volumen"]])
            je_modul_netto[m] = je_modul_netto.get(m, 0.0) + betrag
            continue
        d = -1 if r["typ"] in _KAUF else 1                                # Ausgang Kauf schliesst Verkauf
        kand = [o for o in offen if o[1] == r["symbol"] and o[2] == d and o[3] > 1e-9]
        if not kand:
            je_modul_netto["?"] = je_modul_netto.get("?", 0.0) + betrag
            continue
        if len({o[0] for o in kand}) > 1:
            mehrdeutig += 1
        gleich = [o for o in kand if abs(o[3] - r["volumen"]) < 1e-9]
        o = gleich[0] if gleich else kand[0]
        o[3] -= r["volumen"]
        je_modul_netto[o[0]] = je_modul_netto.get(o[0], 0.0) + betrag
        offen = [x for x in offen if x[3] > 1e-9]
    aus = saldo[saldo["gewinn"] < 0]
    return dict(trades=len(eindeutig), netto=netto, auszahlungen=int(len(aus)),
                auszahlung_summe=float(-aus["gewinn"].sum()), je_modul_trades=je_modul_n, je_modul_netto=je_modul_netto,
                mehrdeutig=mehrdeutig, einstiegs_deals=int(len(ein)))


def auswerten_eng6(res):
    """Gleiche Kennzahlen aus einem eng6-Lauf (res = eng6.run)."""
    import eng6 as E
    tr = res["tr"]
    ideen = {}
    netto_m = {}
    for row in tr:
        slot = int(row[2]); m = modul_eng6(slot)
        schl = (m, int(row[3])) if E.NZ0 <= slot < E.NZ1 else (slot, int(row[3]))
        ideen[schl] = m
        netto_m[m] = netto_m.get(m, 0.0) + float(row[1])
    ev = res["ev"]
    aus = ev[ev[:, 0] == 1] if len(ev) else np.zeros((0, 6))
    return dict(trades=len(ideen), netto=float(tr[:, 1].sum()) if len(tr) else 0.0, auszahlungen=int(len(aus)),
                auszahlung_summe=float(aus[:, 2].sum()), je_modul_trades=pd.Series(list(ideen.values())).value_counts().to_dict(),
                je_modul_netto=netto_m)


def gate(mt5, eng):
    """Urteil des Gates und Tabelle je Modul."""
    dt = (eng["trades"] - mt5["trades"]) / max(mt5["trades"], 1)
    dn = (eng["netto"] - mt5["netto"]) / max(abs(mt5["netto"]), 1e-9)
    module = sorted(set(mt5["je_modul_trades"]) | set(eng["je_modul_trades"]) | set(mt5["je_modul_netto"]) | set(eng["je_modul_netto"]))
    tab = pd.DataFrame([dict(modul=m, mt5_trades=mt5["je_modul_trades"].get(m, 0), eng6_trades=eng["je_modul_trades"].get(m, 0),
                             mt5_netto=round(mt5["je_modul_netto"].get(m, 0.0), 2), eng6_netto=round(eng["je_modul_netto"].get(m, 0.0), 2))
                        for m in module])
    return dict(bestanden=bool(abs(dt) <= TOL_TRADES and abs(dn) <= TOL_NETTO), abw_trades=dt, abw_netto=dn, module=tab)


def referenzlauf(mk, blks, gps, von="2022-08-23", bis=None, **kw):
    """eng6-Einzelpfad wie der Tester: 10 000 $, keine GFT-Abbrueche, Auszahlung 1 Tag nach Reife und flach."""
    import eng6 as E
    from . import konfig as K
    from .konto import motor_parameter
    bis = bis or K.STICHTAG
    mk.set_generic(blks)
    GP = E.gparams(gps)
    Pv = motor_parameter(**dict(dict(pleite_weiter=2, rulefloat=0.0, ruleday=0.0, paydelay=1), **kw))
    a = mk.day_index(von)
    b = int(np.searchsorted(mk.days, np.datetime64(bis, "D").astype(np.int64), side="right"))
    return E.run(mk, Pv, a, b, GP=GP)


def md_tabelle(df):
    """DataFrame als Markdown-Tabelle (ohne Zusatzpaket)."""
    kopf = "| " + " | ".join(str(c) for c in df.columns) + " |"
    trenn = "|" + "|".join("---" for _ in df.columns) + "|"
    zeilen = ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join([kopf, trenn] + zeilen)
