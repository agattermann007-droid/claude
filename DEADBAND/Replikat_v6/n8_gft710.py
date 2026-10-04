"""Stufe 8: GFT-Handhabung am 7.10-Stand variieren (Pufferkurve, Risiko) - wie viel Luft ist ohne Pleiten?"""
import sys, json, time, numpy as np, eng6 as E, evl6 as V, y7_konto as Y, n8_konto as NK
fb = Y.fade_blocks("gft")
sp = Y.spike_block("gft", 10, dict(Y.SPIKE, kmin=0.20), only_dir=1)
def run(lbl, kw, frisk=0.75, srisk=0.75):
    gps = [dict(on=1, risk=frisk, maxtrades=1, harv=1) for _ in Y.F10] + [dict(on=1, risk=srisk, maxtrades=1, harv=1)]
    GP = E.gparams(gps); V.set_generic(fb + [sp], GP)
    r = V.evaluate(E.params(**dict(Y.BASE, **kw)), GP=GP, horizons=(250, 500), step=3, seeds=tuple(range(8)), skip=0.05, end="2025-12-31")
    print(NK.line(lbl, r["mean"]), flush=True)
    return r["mean"]
out = {}
for lbl, kw in [("7.10", {}), ("dd 4/2/0.2", dict(ddfull=4.0, ddmin=2.0)), ("dd 4/1.5/0.3", dict(ddfull=4.0, ddmin=1.5, ddfmin=0.3)),
                ("dd 3.5/1.5/0.3", dict(ddfull=3.5, ddmin=1.5, ddfmin=0.3)), ("dd 5/2.5/0.4", dict(ddfmin=0.4)),
                ("dd 3/1/0.3", dict(ddfull=3.0, ddmin=1.0, ddfmin=0.3)), ("below 1.0", dict(belowstart=1.0)),
                ("cool 0", dict(cool_n=0)), ("budget 1.2", dict(gesamtbudget=1.2, idea_cap=1.2))]:
    out[lbl] = run(lbl, kw)
for fr in (0.85, 0.95):
    out[f"fade {fr}"] = run(f"Fades {fr} %", {}, frisk=fr)
json.dump(out, open("ergebnisse/n8_gft710.json", "w"), default=float, indent=1)
