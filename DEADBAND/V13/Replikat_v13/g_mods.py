"""Modul-Bilanz und Konto-Mechanik je Variante und Fenster (16 Stoerungen). Aufruf: py -3 g_mods.py gft|ext VAR1 VAR2 ..."""
import sys
DS = sys.argv[1]
if DS == "gft":
    import xg as X  # noqa: F401
else:
    import xe as X  # noqa: F401
import os

if __name__ == "__main__":
    import evl11 as V, eng11 as E, gsetup as GS, cfg11 as C
    from g_var import VAR
    WIN = X.WING if DS == "gft" else V.WIN5
    for nm in sys.argv[2:]:
        b, kw = VAR[nm]
        GP = GS.configure(b, **kw); V.INIT = (GS.init_worker, (b, kw))
        r = V.evaluate(E.params(), GP, windows=WIN, seeds=tuple(range(1, 17)), workers=6)
        for w in WIN:
            a = r[w]
            print(V.line(f"{nm} {w}", a), flush=True)
            print(f"    Trades/J {a['tr']:.0f} WR {a['wr']:.0f}%  gueltige Tage/J {a['valid']:.0f}  Serienstopps/J {a['cool']:.1f}  "
                  f"Bremsen/J {a['brake']:.1f}  GS-Sperren/J {a['gs']:.1f}  Engpass gueltig/Gewinn/14T {a['lim_v']}/{a['lim_p']}/{a['lim_t']}", flush=True)
            names = {f"g{i}": n for i, n in enumerate(C.STREAMS)}
            print("    " + "  ".join(f"{names.get(k, k)}:{v['pnl']:.0f}$/{v['tr']:.0f}" for k, v in a["mods"].items()), flush=True)
