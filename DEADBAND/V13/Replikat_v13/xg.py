"""Live-Runde 16.10.2026: Nachbau auf dem GFT-Feed (prep_gft.py). VOR allen anderen Modulen importieren.
REP_SPREAD=gft (echte Bar-Spreads, Voreinstellung) oder modell (proportional wie bisher, eigener Cache)."""
import os
_W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("REP_SPREAD", "gft")
os.environ.setdefault("NPZ_DIR", os.path.join(_W, "npz_gft"))
os.environ.setdefault("REP_CACHE", os.path.join(_W, "cache_gft_" + os.environ["REP_SPREAD"]))
os.environ.setdefault("REP_T_LO", "2019-11-01")

# Fenster auf dem GFT-Feed (NAS ab 28.10.2019; Daten bis 16.10.2026)
WING = {"Auswahl 2022": ("2022-01-03", "2022-12-31"), "2023": ("2023-01-01", "2023-12-31"),
        "Pruef 2024-25": ("2024-01-01", "2025-02-13"), "Neu 2025-26": ("2025-02-14", "2025-10-15")}
