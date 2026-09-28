"""Build 6.20: Reicht die Waechter-Historie des EA (FadeHistTage = 600 Tage) mit Grid-Filter noch fuer die Mindestzahl
von 30 virtuellen Signalen? Je Modul: Anteil der Signale 2022-25, vor denen im Fenster weniger als 30 (gefilterte)
Signale liegen - dann ist das Modul nach einem Neustart nur virtuell. Dazu Minimum und Median der Signalzahl im
600-Tage-Fenster. Ergebnis: nur N1800 faellt mit Grid dauerhaft unter 30 (-> GridOhne = N1800).
Aufruf: python t_window.py"""
import numpy as np
import pg_blocks as PB, pg_rules as RU

RULE = RU.fade_filter(5, 15, 1000, RU.c_stop_survival(0.70))
T22 = np.datetime64("2022-01-01", "m").astype(np.int64)

if __name__ == "__main__":
    print("Modul    Anteil Signale 2022-25 mit < 30 Signalen im Fenster davor (6.20 / 6.10)        | 600 Tage: min/Median 6.20 | 6.10")
    for nm in PB.F10:
        fe = PB.fi("ext", nm); fg = PB.fi("gft", nm)
        ke = PB.apply_rule(fe, RULE)[0]; kg = PB.apply_rule(fg, RULE)[0]
        pre = fe["t_entry"] < T22
        te = np.r_[fe["t_entry"][pre], fg["t_entry"]]; kk = np.r_[ke[pre], kg]
        g = te >= T22
        txt = []
        for days in (600, 1000, 1500):
            c = np.array([int(((te > t - days * 1440) & (te < t) & kk).sum()) for t in te[g]])
            c0 = np.array([int(((te > t - days * 1440) & (te < t)).sum()) for t in te[g]])
            txt.append(f"{days:4d} T: {(c < 30).mean():4.0%} / {(c0 < 30).mean():4.0%}")
            if days == 600:
                mm = f"{c.min():3d} / {int(np.median(c)):3d} | {c0.min():3d} / {int(np.median(c0)):3d}"
        print(f"{nm:7s}  " + ", ".join(txt) + f"  | {mm}", flush=True)
