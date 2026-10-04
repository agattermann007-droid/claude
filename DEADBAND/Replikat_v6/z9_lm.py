"""Stufe 8.10: Trend-Day / Schluss-Momentum NAS (n9sig.gen_lastmom) im Konto-Replikat.
Reihenfolge laut Arbeitsweise: 1) allein (alte Module aus), 2) GFT-Handhabung (Risiko, Puffer-Schwelle),
3) mit 8.00 kombiniert. Kandidat = einzige robuste Rasterstelle: 14:00, Rendite seit Vortagesschluss >= 0,75 ATR, nur Long,
Stop 0,3 ATR, Ausstieg 15:55. Aufruf: python z9_lm.py [gft|ext]"""
import sys, json
import eng6 as E, evl6 as V, n8_konto as NK, n8_port as NP, n9sig as N9, z8

LM = ("NAS", N9.gen_lastmom, (840, 955, 0, 0.75, 0, 0.3, 0.0, 1, 960))
NP.LIB["LM"] = LM

if __name__ == "__main__":
    ds = sys.argv[1] if len(sys.argv) > 1 else "gft"
    out = {}
    if ds == "gft":
        for lbl, gp, kw in (("LM allein 0,75 %", {}, {}), ("LM allein 0,5 % ab 3 %", dict(risk=0.5, minbuf=3.0), {}),
                            ("LM allein 0,75 % Kurve 3,5/1,25/0,1", {}, z8.KW80)):
            r = NK.konto([LM + (gp,)], kw=kw)
            out[lbl] = r["mean"]
            print(NK.line(lbl, r["mean"]), flush=True)
    z8.NEW80.append("LM")
    for lbl, risk in (("8.00 + LM 0,5 %", 0.5), ("8.00 + LM 0,75 %", 0.75)):
        z8.RISK80["LM"] = risk
        z8._DS = None
        r = z8.evaluate(ds)
        out[lbl] = r
        print(z8.kurz(lbl, r), flush=True)
    z8.save(f"ergebnisse/z9_lm_{ds}.json", out)
