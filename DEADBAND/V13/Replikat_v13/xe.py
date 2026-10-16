"""Live-Runde: Fremddaten-Satz wie Replikat v12 (prep_ext: Gold OANDA bis 2016-08 + Dukascopy, NAS HistData), Spread-Modell
proportional. VOR allen anderen Modulen importieren."""
import os
_W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("REP_SPREAD", "modell")
os.environ.setdefault("NPZ_DIR", os.path.join(_W, "fremd", "npz_ext"))
os.environ.setdefault("REP_CACHE", os.path.join(_W, "cache_ext"))
os.environ.setdefault("REP_T_LO", "2010-12-01")
