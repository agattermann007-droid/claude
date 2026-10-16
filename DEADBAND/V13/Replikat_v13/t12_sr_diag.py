"""v12 / 9.4: Konto-Mechanik V8 gegen V10 (16 Stoerungen gemittelt): Serien-Stopps, Schutz gueltiger Tage, Bremsen,
Abschluss-Ernten, Engpaesse (gueltige Tage / Mindestgewinn / 14 Tage), Trades und Trefferquote je Jahr."""
import x12  # noqa: F401
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
Pv = E.params()
W = {k: V.WIN5[k] for k in ("Auswahl 2022", "Pruef 2024-25", "Pruef 2017-20", "Pruef 2011-15")}
for lab, GP in (("V8", C.gp_v8()), ("V10", C.gp_v10())):
    r = V.evaluate(Pv, GP, windows=W, seeds=tuple(range(1, 17)), workers=2)
    for w in W:
        a = r[w]
        print(f"{lab:4s} {w:14s} Ausz/J {a['pay']:5.2f} Trades/J {a['tr']:6.1f} WR {a['wr']:4.1f}% Serien-Stopps/J {a['cool']:5.2f} "
              f"GS-Sperren/J {a['gs']:5.1f} Bremsen/J {a['brake']:5.2f} Ernten/J {a['bank']:5.2f} "
              f"gueltig/J {a['valid']:5.1f} | Engpass gueltig {a['lim_v']} Gewinn {a['lim_p']} 14T {a['lim_t']}", flush=True)
