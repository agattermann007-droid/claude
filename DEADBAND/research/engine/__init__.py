"""DEADBAND V8.10 Forschungs-Engine (research/PLAN.md, Abschnitt 4)."""
import os as _os
import sys as _sys

_REPLIKAT = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))), "Replikat_v6")
if _REPLIKAT not in _sys.path:
    _sys.path.append(_REPLIKAT)
