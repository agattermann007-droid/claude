"""Kalibrierung: Testerbericht lesen (HTML UTF-16 und XML, englisch/deutsch) und Zaehlweise."""
import numpy as np
import pytest

from engine import kalibrierung as KA

DEALS = [
    # zeit, deal, symbol, typ, richtung, volumen, preis, order, kommission, swap, gewinn, saldo, kommentar
    ("2022.08.23 00:00:00", "1", "", "balance", "", "", "", "", "0.00", "0.00", "10 000.00", "10 000.00", ""),
    ("2022.08.23 10:00:00", "2", "XAUUSD.x", "buy", "in", "0.10", "1750.00", "2", "-0.50", "0.00", "0.00", "9 999.50", "DEADBAND L"),
    ("2022.08.23 10:00:00", "3", "NAS100.x", "buy", "in", "0.20", "13000.0", "3", "0.00", "0.00", "0.00", "9 999.50", "NOISE 0.50"),
    ("2022.08.23 10:00:00", "4", "NAS100.x", "buy", "in", "0.20", "13000.0", "4", "0.00", "0.00", "0.00", "9 999.50", "NOISE 1.00"),
    ("2022.08.23 11:00:00", "5", "NAS100.x", "sell", "out", "0.20", "13010.0", "5", "0.00", "0.00", "20.00", "10 019.50", ""),
    ("2022.08.23 12:00:00", "6", "NAS100.x", "sell", "out", "0.20", "13005.0", "6", "0.00", "0.00", "10.00", "10 029.50", ""),
    ("2022.08.26 16:45:00", "7", "XAUUSD.x", "sell", "out", "0.10", "1752.00", "7", "0.00", "-1.29", "20.00", "10 048.21", ""),
    ("2022.08.28 18:00:00", "8", "XAUUSD.x", "buy", "in", "0.10", "1751.00", "8", "-0.50", "0.00", "0.00", "10 047.71", "DEADBAND WE"),
    ("2022.08.29 09:00:00", "9", "XAUUSD.x", "sell", "out", "0.10", "1741.00", "9", "0.00", "0.00", "-100.00", "9 947.71", "sl 1741.00"),
    ("2022.08.30 09:00:00", "10", "NAS100.x", "sell", "in", "0.10", "13100.0", "10", "0.00", "0.00", "0.00", "9 947.71", "FADE N1030"),
    ("2022.08.30 10:00:00", "11", "NAS100.x", "buy", "out", "0.10", "13050.0", "11", "0.00", "0.00", "50.00", "9 997.71", ""),
    ("2022.09.10 00:00:00", "12", "", "balance", "", "", "", "", "0.00", "0.00", "-131.25", "9 866.46", "withdrawal"),
]


def _html(pfad, kopf):
    z = ["<html><body><table><tr><th>Orders</th></tr>",
         "<tr>" + "".join(f"<th>{k}</th>" for k in ("Open Time", "Order", "Symbol", "Type", "Volume", "Price", "S / L", "T / P", "Time", "State", "Comment")) + "</tr>",
         "<tr><td>2022.08.23 10:00:00</td><td>2</td><td>XAUUSD.x</td><td>buy</td><td>0.10 / 0.10</td><td>1750</td><td></td><td></td><td></td><td>filled</td><td>DEADBAND L</td></tr>",
         "</table><table><tr><th colspan=13>Deals</th></tr>",
         "<tr>" + "".join(f"<td>{k}</td>" for k in kopf) + "</tr>"]
    for d in DEALS:
        z.append("<tr>" + "".join(f"<td>{c}</td>" for c in d) + "</tr>")
    z.append("<tr><td colspan=13></td></tr><tr><td>0</td><td>Summe</td></tr></table></body></html>")
    open(pfad, "wb").write("\n".join(z).encode("utf-16"))


def _xml(pfad, kopf):
    zelle = lambda c: f'<Cell><Data ss:Type="String">{c}</Data></Cell>'
    z = ['<?xml version="1.0"?>\n<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" '
         'xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"><Worksheet ss:Name="Tester"><Table>',
         "<Row>" + zelle("Deals") + "</Row>", "<Row>" + "".join(zelle(k) for k in kopf) + "</Row>"]
    for d in DEALS:
        z.append("<Row>" + "".join(zelle(c) for c in d) + "</Row>")
    z.append("</Table></Worksheet></Workbook>")
    open(pfad, "w", encoding="utf-8").write("".join(z))


EN = ("Time", "Deal", "Symbol", "Type", "Direction", "Volume", "Price", "Order", "Commission", "Swap", "Profit", "Balance", "Comment")
DE = ("Zeit", "Deal", "Symbol", "Typ", "Richtung", "Volumen", "Preis", "Auftrag", "Kommission", "Swap", "Gewinn", "Kontostand", "Kommentar")


@pytest.mark.parametrize("art,kopf", [("html", EN), ("html", DE), ("xml", EN), ("xml", DE)])
def test_bericht_lesen_und_zaehlen(tmp_path, art, kopf):
    p = tmp_path / f"bericht.{art}"
    (_html if art == "html" else _xml)(str(p), kopf)
    df = KA.deals(str(p))
    assert len(df) == len(DEALS)
    m = KA.auswerten_mt5(df)
    assert m["trades"] == 3                                   # DEADBAND (WE setzt fort), NOISE (2 Teile = 1), FADE
    assert m["einstiegs_deals"] == 5
    assert m["netto"] == pytest.approx(-0.5 - 0.5 + 20 + 10 + 20 - 1.29 - 100 + 50)
    assert m["auszahlungen"] == 1 and m["auszahlung_summe"] == pytest.approx(131.25)
    assert m["je_modul_trades"] == {"DB": 1, "NZ": 1, "N1030": 1}
    assert m["je_modul_netto"]["DB"] == pytest.approx(-0.5 + 20 - 1.29 - 0.5 - 100)
    assert m["je_modul_netto"]["NZ"] == pytest.approx(30.0)
    assert m["je_modul_netto"]["N1030"] == pytest.approx(50.0)


def test_gate():
    mt5 = dict(trades=100, netto=1000.0, je_modul_trades={"DB": 100}, je_modul_netto={"DB": 1000.0})
    ok = dict(trades=104, netto=1090.0, je_modul_trades={"DB": 104}, je_modul_netto={"DB": 1090.0})
    assert KA.gate(mt5, ok)["bestanden"]
    assert not KA.gate(mt5, dict(ok, trades=106))["bestanden"]
    assert not KA.gate(mt5, dict(ok, netto=1110.0))["bestanden"]


def test_modulnamen_eng6():
    import eng6 as E
    assert KA.modul_eng6(0) == "DB" and KA.modul_eng6(3) == "R21" and KA.modul_eng6(E.NZ0) == "NZ"
    assert KA.modul_eng6(E.G0) == "N1030" and KA.modul_eng6(E.G0 + 2 * 13 + 1) == "TD"


def test_referenzlauf_synthetisch(daten):
    import eng6 as E
    from engine import familien as FA, konto as KO, signale as SG
    mk = E.Market(D=daten, S=None)
    d = daten["NAS"]
    sig = FA.f3_asien(d, SG.indikatoren_m15(d), 0.65, m=1e9)
    blk = KO.familien_block(d, "NAS", sig, 0, stoplvl=1.5)
    res = KA.referenzlauf(mk, [blk], [KO.familien_gp("NAS")], von="2021-02-01", bis="2021-09-30")
    e = KA.auswerten_eng6(res)
    assert e["trades"] > 10 and set(e["je_modul_trades"]) == {"N1030"}   # Strom 0 traegt im Replikat den ersten Namen
    assert e["netto"] == pytest.approx(sum(e["je_modul_netto"].values()))


def test_md_tabelle():
    import pandas as pd
    t = KA.md_tabelle(pd.DataFrame([dict(a=1, b="x")]))
    assert t.splitlines() == ["| a | b |", "|---|---|", "| 1 | x |"]
