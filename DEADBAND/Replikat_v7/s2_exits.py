"""Screening 2 (ohne Konto): Ausstiege - Stop-Weite, Ziel, Zeit-Exit, Stop-Nachzug, Break-even."""
from s1_ablation import run

if __name__ == "__main__":
    run("Basis (Stop 2 ATR, Ziel 2,64/2,2 R)")
    print("--- Stop-Weite (Ziel in gleicher ATR-Entfernung)")
    for sm in (1.5, 1.75, 2.25, 2.5, 3.0):
        run(f"Stop {2*sm:.1f} ATR, Ziel gleich weit", rd_mult=sm, tp=(5.28 / (2 * sm), 4.4 / (2 * sm)))
    print("--- Ziel (Stop 2 ATR)")
    for tg, tn in ((2.0, 1.6), (2.3, 1.9), (3.0, 2.5), (3.5, 3.0), (4.0, 3.5), (5.0, 4.5), (0.0, 0.0)):
        run(f"Ziel Gold {tg} / NAS {tn} R", tp=(tg, tn))
    print("--- Zeit-Exit")
    for eb, ed in ((288, 0), (576, 0), (864, 0), (1728, 0), (2304, 12), (0, 0)):
        run(f"Zeit-Exit {eb} M5 / {ed} Tage", sim=dict(exitbars=eb, exitdays=ed))
    print("--- Stop-Nachzug / Break-even")
    for tf_, td in ((1.0, 1.0), (1.5, 1.0), (1.5, 1.5), (2.0, 1.0), (2.0, 1.5), (2.5, 1.5)):
        run(f"Nachzug ab {tf_} R, Abstand {td} R", sim=dict(trail_from=tf_, trail_dist=td))
    for tf_, td in ((1.5, 1.0), (2.0, 1.5), (2.0, 1.0), (3.0, 1.5)):
        run(f"ohne Ziel, Nachzug ab {tf_} R / {td} R", tp=(0.0, 0.0), sim=dict(trail_from=tf_, trail_dist=td))
    for ba, bt in ((1.0, 0.0), (1.5, 0.1), (2.0, 0.3)):
        run(f"Break-even ab {ba} R auf {bt} R", sim=dict(be_at=ba, be_to=bt))
