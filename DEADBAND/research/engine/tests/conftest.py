import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HIER))
DEADBAND = os.path.dirname(RESEARCH)
for p in (RESEARCH, os.path.join(DEADBAND, "Replikat_v6")):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest


@pytest.fixture(scope="session")
def daten(tmp_path_factory):
    """Synthetische XAU/NAS-Daten (engine/synthetisch.py) durch prep5.build() - nur fuer Konsistenztests."""
    import prep5 as P
    from engine import synthetisch as SY
    d = tmp_path_factory.mktemp("daten")
    SY.schreibe(str(d), "2021-01-03", "2021-09-30", seed=21)
    alt = P.DATA
    P.DATA = str(d)
    try:
        D = P.build()
    finally:
        P.DATA = alt
    return D
