"""Screening 10: Zeit-Stop (nach N M5-Kerzen schliessen, wenn der beste Kurs < m R war)."""
import r7kand as KD
from r7lab import run, C
for nm in ("Basis", "K1 NAS ohne Kreuz"):
    p = KD.KAND[nm](C)
    run(nm, p)
    for nb, mm in ((6, 0.3), (12, 0.3), (12, 0.5), (24, 0.3), (24, 0.5), (24, 0.75), (36, 0.5), (48, 0.5), (48, 0.75), (48, 1.0), (96, 1.0)):
        run(f"{nm} Zeit-Stop {nb} Kerzen, MFE < {mm} R", p, sim=dict(ts_bars=nb, ts_mfe=mm))
