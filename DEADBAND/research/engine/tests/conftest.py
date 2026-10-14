import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HIER))
DEADBAND = os.path.dirname(RESEARCH)
for p in (RESEARCH, os.path.join(DEADBAND, "Replikat_v6")):
    if p not in sys.path:
        sys.path.insert(0, p)
