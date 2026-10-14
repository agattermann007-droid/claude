"""Feste Einstellungen der Forschung (research/PLAN.md). Aenderungen hier nur mit Eintrag im Bericht."""
import os

HIER = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HIER)
DEADBAND = os.path.dirname(RESEARCH)
REPLIKAT = os.path.join(DEADBAND, "Replikat_v6")
DATEN = os.path.join(DEADBAND, "data")            # Auswahl-Daten bis zum Stichtag (gitignored)
DATEN_BLIND = os.path.join(DEADBAND, "data_blind")  # vollstaendige Daten - nur fuer den einen Blindlauf (gitignored)
ERGEBNISSE = os.path.join(RESEARCH, "ergebnisse")

# Walk-Forward (E6): Auswahl bis einschliesslich Prop-Tag 30.06.2025 (endet 17:00 NY = 01.07.2025 00:00 Serverzeit)
STICHTAG = "2025-06-30"
STICHTAG_SERVER_ENDE = "2025-07-01 00:00:00"     # erste Serverzeit, die NICHT mehr zur Auswahl gehoert

# Serverzeit = NY + 7 h (GFT, alle Sommerzeit-Phasen; EA NYOffsetHours = 7)
NY_VERSATZ_H = 7

# Seeds (PLAN 3.7)
SEED_BOOTSTRAP = 20261014            # + Blockgroesse
SEED_ZUFALL = 7000                   # + Familie * 100 + Symbolindex

# GFT Instant Premium, EA-Lesart (E5)
GFT = dict(start=10000.0, kontopreis=148.5, boden_pct=6.0, float_pct=1.0, tag_pct=3.0, gueltig_pct=0.5,
           gueltig_reserve=0.50, gueltige_tage=5, zyklus_tage=10, min_auszahlung=105.0, anteil=0.80,
           deckel_pct=6.0, deckel_anzahl=2, haltedauer_s=120)

# Pufferkurve und Faktor unter Start wie V8.10 (DDFullPct/DDMinPct/DDMinFactor, BelowStartMult)
PUFFERKURVE = dict(voll=3.5, minimum=1.25, faktor=0.1, unter_start=0.95)

# Bootstrap (Auftrag Abschnitt 5)
BOOT_PFADE = 1000
BOOT_BLOECKE = (1, 5, 20)
BOOT_TAGE_JE_PFAD = 252

# Zufallsvergleich (PLAN 6.6)
ZUFALL_LAEUFE = 1000
ZUFALL_SCHWELLE = 0.95               # > 50 Varianten in einer Familie: 0.99
