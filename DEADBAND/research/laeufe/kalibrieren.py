"""Kalibrierungs-Gate (PLAN 4.4) ausfuehren: MT5-Referenzbericht von V8.10 gegen den eng6-Einzelpfad.

Aufruf (aus research/):  python -m laeufe.kalibrieren <Bericht.html|.xml> [von] [bis]
Schreibt ergebnisse/kalibrierung.json und ergebnisse/kalibrierung.md. Faellt das Gate, ist das ein STOPP.
"""
import json
import os
import sys

from engine import kalibrierung as KA
from engine import konfig as K
from engine import konto as KO


def main(bericht, von="2022-08-23", bis=K.STICHTAG):
    KO.umgebung(blind=False)
    import evl6 as V
    blks, gps = KO.baseline()
    mk = V.mk()
    res = KA.referenzlauf(mk, blks, gps, von=von, bis=bis)
    eng = KA.auswerten_eng6(res)
    mt5 = KA.auswerten_mt5(KA.deals(bericht))
    g = KA.gate(mt5, eng)
    os.makedirs(K.ERGEBNISSE, exist_ok=True)
    aus = dict(bericht=os.path.basename(bericht), von=von, bis=bis, bestanden=g["bestanden"], abw_trades=g["abw_trades"],
               abw_netto=g["abw_netto"], mt5={k: v for k, v in mt5.items()}, eng6={k: v for k, v in eng.items()},
               module=g["module"].to_dict("records"))
    json.dump(aus, open(os.path.join(K.ERGEBNISSE, "kalibrierung.json"), "w"), indent=1, default=float)
    z = [f"# Kalibrierungs-Gate V8.10 ({von} bis {bis})", "",
         f"Quelle: `laeufe/kalibrieren.py`, Bericht `{os.path.basename(bericht)}`, eng6-Einzelpfad (pleite_weiter=2, paydelay 1).", "",
         "| | MT5 | eng6 | Abweichung | Grenze |", "|---|---|---|---|---|",
         f"| Trades (Ideen) | {mt5['trades']} | {eng['trades']} | {100 * g['abw_trades']:+.1f} % | ±5 % |",
         f"| Netto $ | {mt5['netto']:.2f} | {eng['netto']:.2f} | {100 * g['abw_netto']:+.1f} % | ±10 % |",
         f"| Auszahlungen | {mt5['auszahlungen']} ({mt5['auszahlung_summe']:.0f} $) | {eng['auszahlungen']} ({eng['auszahlung_summe']:.0f} $) | | Info |",
         "", f"**Urteil: {'BESTANDEN' if g['bestanden'] else 'NICHT BESTANDEN - STOPP'}**", "",
         "## Je Modul (Diagnose; Netto-Zuordnung im MT5-Bericht heuristisch, "
         f"{mt5['mehrdeutig']} mehrdeutige Ausgaenge)", "", KA.md_tabelle(g["module"])]
    open(os.path.join(K.ERGEBNISSE, "kalibrierung.md"), "w").write("\n".join(z) + "\n")
    print("\n".join(z))
    return g["bestanden"]


if __name__ == "__main__":
    sys.exit(0 if main(*sys.argv[1:]) else 1)
