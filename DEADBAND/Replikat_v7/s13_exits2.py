"""Screening 13: Ausstiege nach Sharpe/Risiko-Paritaet (Basis und K1)."""
import r7kand as KD
from r7lab import srun, C
print(f"{'':46s} Trades  ØR     R/J     DD    maxS  B12  Sharpe RP36 RP20 | Epochen 06-10 11-15 16-19 20-21 22-23 24-25")
for nm in ("Basis", "K1 NAS ohne Kreuz"):
    p = KD.KAND[nm](C)
    srun(nm, p)
    for ba, bt in ((1.0, 0.0), (1.5, 0.0), (1.5, 0.3), (2.0, 0.5)):
        srun(f"  BE ab {ba} R auf {bt} R", p, sim=dict(be_at=ba, be_to=bt))
    for tf_, td in ((1.5, 1.0), (2.0, 1.0), (2.0, 1.5)):
        srun(f"  Nachzug ab {tf_} R / {td} R", p, sim=dict(trail_from=tf_, trail_dist=td))
    for tg, tn in ((2.0, 1.8), (2.3, 2.0), (3.0, 2.5), (3.5, 3.0)):
        srun(f"  Ziel {tg}/{tn}", p, tp=(tg, tn))
    for eb in (288, 576):
        srun(f"  Zeit-Exit {eb} M5", p, sim=dict(exitbars=eb, exitdays=0))
    srun("  Stop 1,75 ATR (Ziel gleich weit)", p, rd_mult=0.875, tp=(2.64 / 0.875, 2.2 / 0.875))
    srun("  Stop 2,5 ATR (Ziel gleich weit)", p, rd_mult=1.25, tp=(2.64 / 1.25, 2.2 / 1.25))
