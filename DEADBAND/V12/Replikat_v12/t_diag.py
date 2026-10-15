"""Empfindlichkeit des Nachbaus: welche Annahme kostet wie viel (V8)."""
import numpy as np
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk()
m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
W = {k: V.WIN[k] for k in ("Auswahl 2022", "2023", "Pruef 2024-25")}
GP = C.gp_v8()
for lab, kw in [("Basis", {}), ("slip 0", dict(slip=0.0)), ("ohne GueltigSchutz", dict(valid_guard=0)), ("ohne Serien-Stopp", dict(cool_n=0)),
                ("ohne Abschluss-Ernte", dict(bank_on=0)), ("ohne Gewinn-Ernte", dict(ge_on=0)), ("ohne Swap-Vorsorge", dict(swap_guard=0.0)),
                ("ohne Margin", dict(lev=0.0)), ("Zyklus 10 T", dict(cycledays=10)), ("paydelay 2", dict(paydelay=2)),
                ("Pufferkurve aus", dict(ddfull=0.0)), ("gueltig 0,50 %", dict(validpct=0.5))]:
    r = V.evaluate(E.params(**kw), GP, windows=W)
    print(f"{lab:<22s} " + " | ".join(f"{w[:8]} {r[w]['pay']:5.2f} {r[w]['net']:5.0f}$ B{r[w]['bust']}" for w in W), flush=True)
