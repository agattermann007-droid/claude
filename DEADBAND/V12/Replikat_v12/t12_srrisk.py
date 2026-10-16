"""v12: SR-Risiko mit korrigiertem Motor neu (V11-Bericht 4.4 war mit dem Noise-Fehler gerechnet). 32 Seeds, 5 Fenster."""
import x12  # noqa: F401
import pickle
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"]); m.set_generic(C.blocks(S))
Pv = E.params()
base = pickle.load(open("ergebnisse/base_v10_32.pkl", "rb"))
out = {}
for risk in (0.05, 0.15, 0.20, 0.25, 0.30):
    r = V.evaluate_seeds(Pv, C.gp_v10(sr_risk=risk), seeds=tuple(range(1, 33)), windows=V.WIN5)
    out[risk] = r
    print(V.paired(base, r, f"SR {risk:.2f}%"), flush=True)
pickle.dump(out, open("ergebnisse/t12_srrisk.pkl", "wb"))
