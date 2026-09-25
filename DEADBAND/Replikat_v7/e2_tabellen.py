"""Tabellen fuer den Bericht 6.20: RSI21 allein (ohne Konto), Fremddaten 2006-2025, gleiche Signale/Regeln wie die EA.
Kennzahlen je Variante: Trades/J, Trefferquote, Ø R, PF, R/J (R x Gewicht), laengste Verlustserie, groesster Rueckgang (R),
Sharpe (Wochen), Bust-Ersatz (Rueckgang >= 12 R je Jahr), R/J bei gleicher Bust-Haeufigkeit wie 6.10 (RP36).
-> ergebnisse/e2.json"""
import os, json
import numpy as np
import r7sig as G, r7sim as M, r7kand as KD, r7lab as LB
import s8_guard as SG
import r7lim as L

C = LB.C; D = LB.D
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ergebnisse")
os.makedirs(OUT, exist_ok=True)
res = {}


def add(gruppe, lbl, p, **kw):
    A, m = LB.run(lbl, p, show=False, **kw)
    m = {k: v for k, v in m.items()}
    res.setdefault(gruppe, {})[lbl] = m
    print(LB.short(f"[{gruppe}] {lbl}", m), flush=True)


B = KD.basis(C)
g = C["sym"] == 0; d = C["dir"]
add("basis", "6.10 (Basis)", B)
# Regeln einzeln
add("regeln", "ohne Folgesignal", dict(B, folge_min=0))
add("regeln", "ohne Kreuz-Bestaetigung (beide)", dict(B, cross=None))
add("regeln", "NAS ohne Kreuz (Gold Kreuz|Gate)", KD.k1(C))
add("regeln", "ohne H4-Divergenz", dict(B, use_div=False))
add("regeln", "Shorts ohne Regime", dict(B, short_rule="none"))
add("regeln", "NAS-Longs ohne SMA200", dict(B, nas_long_rule="none"))
add("regeln", "ohne zweiten Platz", B, sim=dict(second=False))
add("regeln", "Gold nur M15", KD.kg(C))
add("regeln", "nur M15 (beide)", dict(B, tfs=(0,)))
# Schwelle, Laenge, Zeitfenster
for ob in (72.5, 77.5):
    add("signal", f"RSI > {ob}", dict(B, oben=ob))
add("signal", "Gold ab 3:00 NY (London)", dict(B, extra=np.where(g, True, C["nyh"] >= 9.5), ab=3.0))
add("signal", "NAS bis 15:00 NY", dict(B, nas_bis=15.0))
# Ausstiege
add("ausstieg", "Stop 3 ATR (Ziel gleich weit)", B, rd_mult=1.5, tp=(5.28 / 3, 4.4 / 3))
add("ausstieg", "Ziel 3,0 / 2,5 R", B, tp=(3.0, 2.5))
add("ausstieg", "ohne Ziel, Nachzug ab 2 R / 1 R", B, tp=(0.0, 0.0), sim=dict(trail_from=2.0, trail_dist=1.0))
add("ausstieg", "Break-even ab 1 R", B, sim=dict(be_at=1.0, be_to=0.0))
add("ausstieg", "Zeit-Exit 24 h (288 M5)", B, sim=dict(exitbars=288, exitdays=0))
add("ausstieg", "Zeit-Stop 36 Kerzen bei < 0,5 R", B, sim=dict(ts_bars=36, ts_mfe=0.5))
# Filter
d1 = np.where(d > 0, C["d1rsi"], 100 - C["d1rsi"])
add("filter", "ADX > 25", dict(B, post=C["adx"] > 25))
add("filter", "H4-RSI in Richtung (> 50)", dict(B, post=np.where(d > 0, C["h4rsi"] > 50, C["h4rsi"] < 50)))
add("filter", "D1-RSI in Richtung (> 52,5)", dict(B, post=d1 > 52.5))
add("filter", "Ausbruch 20 Kerzen", dict(B, post=np.where(d > 0, C["close"] > C["hh20"], C["close"] < C["ll20"])))
add("filter", "ATR-Rang > 0,4", dict(B, post=C["atrpct"] > 0.4))
use, Rv, tx = SG.virtual(B)
add("filter", "Waechter PF der letzten 20 > 1 (je Symbol)", dict(B, post=SG.guard(use, Rv, tx, 20, 1.0, "pf", per_sym=True)))
v = C["vrel"]; okv = ~np.isfinite(v) | (v <= 0)
for th in (1.0, 1.5, 2.0):
    add("volumen", f"Volumen >= {th} x Mittel(50)", dict(B, post=okv | (v >= th)))
add("volumen", "Volumen < 1,0 x Mittel(50) (Rest)", dict(B, post=okv | (v < 1.0)))
# 6.20
add("6.20", "Gold-Faktor 0,5", B, gold_mult=0.5)
add("6.20", "6.20: Volumen 1,5 + Gold-Faktor 0,5", KD.KAND["Volumen 1.5"](C), gold_mult=0.5)
add("6.20", "Standalone-Bestwert: NAS ohne Kreuz + NAS-Long ohne SMA200 + Gold nur M15", KD.k1gn(C))
# Einzelsignale: Limit-Rueckzug statt Markt (gleiche Signalmenge)
E = G.entries(C, B)
lim = {}
for lo, lb in ((0.0, 0), (0.25, 12), (0.5, 24)):
    Rs = []; fs = []
    for s in G.SYMS:
        e = E[s]; dd = D[s]
        R, f, _ = L.sim_lim(dd["o"], dd["h"], dd["l"], dd["c"], dd["sp"], e["i5"].astype(np.int64), e["dir"].astype(np.int64), e["rd"],
                            e["tp"], lo, lb, 1152, M.COMM[s])
        Rs.append(R[f]); fs.append(f)
    R = np.concatenate(Rs); f = np.concatenate(fs)
    lim[f"Limit {lo} R / {lb} Kerzen"] = dict(gefuellt=float(f.mean()), avgR=float(R.mean()), wr=float((R > 0).mean()))
    print(f"[limit] Limit {lo} R / {lb} Kerzen: gefuellt {100*f.mean():.1f} %, ØR {R.mean():+.3f}", flush=True)
res["limit"] = lim
json.dump(res, open(os.path.join(OUT, "e2.json"), "w"), indent=1, default=float)
