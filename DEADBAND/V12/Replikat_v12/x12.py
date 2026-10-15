"""Replikat v12 - gemeinsame Einstellungen: erweiterter Datensatz 2010-2026 (prep_ext.py). VOR allen anderen Modulen
importieren. Pfade ueber NPZ_DIR / REP_CACHE / REP_T_LO ueberschreibbar."""
import os
os.environ.setdefault("NPZ_DIR", "/home/user/work/npz_ext")
os.environ.setdefault("REP_CACHE", "/home/user/work/cache_ext")
os.environ.setdefault("REP_T_LO", "2010-12-01")
