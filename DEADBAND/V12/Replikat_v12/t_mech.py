import numpy as np, pickle
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
GP = C.gp_v10()
base = V.evaluate_seeds(E.params(), GP)
print(V.paired(base, base, "V10"), flush=True)
out = {"V10": base}
for lab, kw in [("Abschluss MFE 0.2R", dict(bank_minr=0.2)), ("Abschluss MFE 0.5R", dict(bank_minr=0.5)),
                ("Abschluss Reserve 10%", dict(bank_margin=0.10)), ("Serien-Stopp 4", dict(cool_n=4)), ("Serien-Stopp 2", dict(cool_n=2)),
                ("ohne Schutz gueltiger Tage", dict(valid_guard=0)), ("RSI21-Schutz bis 12:00", dict(r21_gsfrom=12.0)),
                ("RSI21-Schutz bis 14:00", dict(r21_gsfrom=14.0)), ("Gewinn-Ernte ab 0.5R", dict(ge_minr=0.5))]:
    r = V.evaluate_seeds(E.params(**kw), GP)
    print(V.paired(base, r, lab), flush=True); out[lab] = r
pickle.dump(out, open("ergebnisse/t_mech.pkl", "wb"))
