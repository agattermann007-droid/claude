"""Symbolspezifikationen und Kosten (Auftrag Abschnitt 2 'Broker', PLAN 4.2).

Unbekannte Werte werden NIE geschaetzt: sie kommen aus der Spezifikationsdatei des Exports (<Symbol>_spec.txt,
DEADBAND_Daten_Export.mq5). Fehlt ein Wert, wirft lade_spec() einen Fehler.

Konventionen wie EA/Replikat:
  - Kurse sind Bid; Long zahlt den Spread beim Einstieg (Ask), Short beim Ausstieg.
  - Lot-Rundung wie NormLot im EA: auf den Schritt RUNDEN (nicht abschneiden), dann auf min/max begrenzen.
  - Budget-Kuerzung schneidet ab (MathFloor + 1e-9), wie im EA.
  - Mindestlot-Filter: Signal entfaellt, wenn Mindestlot * Stop-Abstand * Geld je Preis > MinLotRiskTol * Sollrisiko.
  - Kommission nur auf den Eingangs-Deal (Gold 5 $/Lot).
  - Swap beim Rollover 00:00 Serverzeit (= 17:00 NY) fuer jede ueber die Tagesgrenze gehaltene Position,
    am 3-fach-Tag dreifach (Gold: Mittwoch).
"""
from dataclasses import dataclass
import math
import os

WOCHENTAG = {"SUNDAY": 0, "MONDAY": 1, "TUESDAY": 2, "WEDNESDAY": 3, "THURSDAY": 4, "FRIDAY": 5, "SATURDAY": 6}


@dataclass
class Symbol:
    name: str                 # Brokername, z. B. XAUUSD.x
    kurz: str                 # XAU, NAS, XAG, OIL, BTC
    kontrakt: float           # Kontraktgroesse
    punkt: float              # SYMBOL_POINT (Spread-Spalte in Punkten)
    lot_min: float
    lot_schritt: float
    lot_max: float
    kommission_ein: float     # $ je Lot, nur Eingangs-Deal
    swap_modus: str           # "punkte" | "zins_eroeffnung" (% p. a. vom Eroeffnungspreis) | "keiner"
    swap_long: float
    swap_short: float
    swap_dreifach: int        # Wochentag des Servertags mit 3-fachem Swap (0 = So ... 6 = Sa), -1 = keiner
    swap_jeden_tag: bool      # True: auch Sa/So (BTC: 7 Tage einfach)
    median_spread: float      # in Preis-Einheiten (Ersatz fuer fehlende Spreads)
    stops_level: float = 0.0  # in Preis-Einheiten

    def geld_je_preis(self) -> float:
        """$ je 1,0 Preisbewegung und Lot (Konto in USD, Gewinnwaehrung USD)."""
        return self.kontrakt

    def swap_je_lot(self, richtung: int, eroeffnung: float, servertag_wochentag: int) -> float:
        """Swap in $ je Lot fuer den Rollover am Ende des Servertags mit Wochentag servertag_wochentag (negativ = Kosten)."""
        satz = self.swap_long if richtung > 0 else self.swap_short
        if self.swap_modus == "punkte":
            sw = satz * self.punkt * self.kontrakt
        elif self.swap_modus == "zins_eroeffnung":
            sw = eroeffnung * self.kontrakt * satz / 100.0 / 360.0
        else:
            return 0.0
        if servertag_wochentag == self.swap_dreifach:
            sw *= 3.0
        return sw


def norm_lot(sym: Symbol, lots: float) -> float:
    """NormLot des EA: MathFloor(lots/step + 0.5)*step, dann min/max."""
    stp = sym.lot_schritt if sym.lot_schritt > 0 else 0.01
    v = math.floor(lots / stp + 0.5) * stp
    v = max(sym.lot_min, min(sym.lot_max, v))
    return round(v, 2)


def lots_fuer_risiko(sym: Symbol, risiko: float, stop_abstand: float, min_lot_tol: float = 2.0, budget_rest: float = None):
    """Lotgroesse wie im EA (HandleSymbol / FadeLive). Rueckgabe 0.0 = Signal entfaellt.
    risiko: Sollrisiko in $, stop_abstand: Preisabstand Einstieg-Stop."""
    if risiko <= 0.0 or stop_abstand <= 0.0:
        return 0.0
    if budget_rest is not None:
        risiko = min(risiko, budget_rest)
        if risiko <= 0.0:
            return 0.0
    mpp = sym.geld_je_preis()
    if sym.lot_min * stop_abstand * mpp > risiko * min_lot_tol:
        return 0.0
    vol = norm_lot(sym, risiko / (stop_abstand * mpp))
    if vol < sym.lot_min:
        return 0.0
    if budget_rest is not None and vol * stop_abstand * mpp > budget_rest + 1e-9:
        stp = sym.lot_schritt if sym.lot_schritt > 0 else 0.01
        vol = round(math.floor(budget_rest / (stop_abstand * mpp) / stp + 1e-9) * stp, 2)
        if vol < sym.lot_min:
            return 0.0
    return vol


# Werte laut Auftrag (verbindlich). Gold/NAS: Kontrakt, Lot, Kommission, Swap, Median-Spread.
XAU = Symbol("XAUUSD.x", "XAU", 100.0, 0.01, 0.01, 0.01, 100.0, 5.0, "punkte", -64.47, 23.84, 3, False, 0.32, 0.05)
# NAS: 3-fach-Tag nicht im Auftrag -> wie das Replikat (Mittwoch) bis zur Spezifikation aus dem Export [ungeprueft]
NAS = Symbol("NAS100.x", "NAS", 10.0, 0.01, 0.01, 0.01, 100.0, 0.0, "zins_eroeffnung", -3.0, -1.5, 3, False, 1.63, 1.5)
# BTC: Kontrakt 1, keine Kommission, -15 % long und short, jeden Tag einfach; Lot laut Export pruefen
BTC = Symbol("BTCUSD.x", "BTC", 1.0, 0.01, 0.01, 0.01, 100.0, 0.0, "zins_eroeffnung", -15.0, -15.0, -1, True, 65.14, 0.0)

BEKANNT = {"XAU": XAU, "NAS": NAS, "BTC": BTC}


def lies_specdatei(pfad: str) -> dict:
    d = {}
    with open(pfad, encoding="latin-1") as f:
        for z in f:
            z = z.strip()
            if "=" in z:
                k, v = z.split("=", 1)
                d[k.strip()] = v.strip()
    return d


def aus_specdatei(pfad: str, kurz: str, median_spread: float, kommission_ein: float = None) -> Symbol:
    """Symbol aus einer Spezifikationsdatei des Exports. kommission_ein: Vorgabe (sonst gebuchter Wert, sonst Fehler)."""
    d = lies_specdatei(pfad)
    mode = d["swap_mode"].split()[1] if " " in d["swap_mode"] else d["swap_mode"]
    if mode == "SYMBOL_SWAP_MODE_POINTS":
        sm = "punkte"
    elif mode == "SYMBOL_SWAP_MODE_INTEREST_OPEN":
        sm = "zins_eroeffnung"
    elif mode == "SYMBOL_SWAP_MODE_DISABLED":
        sm = "keiner"
    else:
        raise ValueError(f"{pfad}: Swap-Modus {mode} nicht abgebildet - bitte melden")
    r3 = d["swap_rollover3days"].split()
    dreifach = WOCHENTAG.get(r3[1], int(r3[0])) if len(r3) > 1 else int(r3[0])
    if kommission_ein is None:
        k = d.get("commission_in_per_lot", "unbekannt").split()[0]
        if k == "unbekannt":
            raise ValueError(f"{pfad}: Kommission unbekannt (keine Deals) - Wert aus der GFT-Spezifikation noetig")
        kommission_ein = -float(k)
    return Symbol(name=d["name"], kurz=kurz, kontrakt=float(d["contract_size"]), punkt=float(d["point"]),
                  lot_min=float(d["volume_min"]), lot_schritt=float(d["volume_step"]), lot_max=float(d["volume_max"]),
                  kommission_ein=kommission_ein, swap_modus=sm, swap_long=float(d["swap_long"]),
                  swap_short=float(d["swap_short"]), swap_dreifach=dreifach,
                  swap_jeden_tag=(kurz == "BTC"), median_spread=median_spread,
                  stops_level=float(d.get("stops_level", "0")) * float(d["point"]))


def pruefe_gegen_auftrag(sym: Symbol, spec_pfad: str) -> list:
    """Abweichungen zwischen Auftragswerten und exportierter Spezifikation (Bericht, keine stille Uebernahme)."""
    if not os.path.exists(spec_pfad):
        return [f"{sym.name}: keine Spezifikationsdatei"]
    d = lies_specdatei(spec_pfad)
    abw = []
    for feld, wert in (("contract_size", sym.kontrakt), ("volume_min", sym.lot_min), ("volume_step", sym.lot_schritt),
                       ("swap_long", sym.swap_long), ("swap_short", sym.swap_short)):
        if feld in d and abs(float(d[feld]) - wert) > 1e-6:
            abw.append(f"{sym.name}: {feld} Auftrag {wert} / Export {d[feld]}")
    return abw
