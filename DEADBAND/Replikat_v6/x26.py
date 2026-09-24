"""Feinabstimmung des Fade-Portfolios: Risiko nach Qualitaet, selektiver Break-even, Groessenkurve."""
import numpy as np, eng6 as E, evl6 as V, r6, cands as K
names = ["N1030", "N1330", "X0630", "X0400", "N1800", "N0930", "N1100", "N1300", "X0300S", "X1000S"]
V.set_generic(K.fade_blocks(names), None)
base = dict(r6.C510, **r6.PAY3, gesamtbudget=0.9, idea_cap=0.9, db_on=0, r21_on=0, nz_on=0)
BE = dict(tp1r=0.5, tp1f=0.0, be=0.05)
def S(r, **kw): return dict(on=1, risk=r, maxtrades=1, **kw)
def gp(risks, be_set=()):
    return E.gparams([S(r, **(BE if names[i] in be_set else {})) if r > 0 else {} for i, r in enumerate(risks)])
sel_be = ("N1100", "N0930", "X1000S", "X0300S")
C = []
C.append(("A 10x0.75", base, gp([0.75] * 10)))
C.append(("B 10x0.75 BE sel", base, gp([0.75] * 10, sel_be)))
C.append(("C Qualitaet 0.85/0.6", base, gp([0.85, 0.7, 0.85, 0.7, 0.6, 0.5, 0.6, 0.5, 0.85, 0.7])))
C.append(("D Qualitaet + BE sel", base, gp([0.85, 0.7, 0.85, 0.7, 0.6, 0.5, 0.6, 0.5, 0.85, 0.7], sel_be)))
C.append(("E ohne N0930/N1300", base, gp([0.85, 0.75, 0.85, 0.7, 0.6, 0, 0.6, 0, 0.85, 0.7], sel_be)))
C.append(("F D + belowstart 1.0", dict(base, belowstart=1.0), gp([0.85, 0.7, 0.85, 0.7, 0.6, 0.5, 0.6, 0.5, 0.85, 0.7], sel_be)))
C.append(("G D + Kurve 3/1", dict(base, ddfull=3.0, ddmin=1.0), gp([0.85, 0.7, 0.85, 0.7, 0.6, 0.5, 0.6, 0.5, 0.85, 0.7], sel_be)))
C.append(("H D + Budget 1.0", dict(base, gesamtbudget=1.0, idea_cap=1.0), gp([0.85, 0.7, 0.85, 0.7, 0.6, 0.5, 0.6, 0.5, 0.85, 0.7], sel_be)))
r6.run(C, "x26.json")
