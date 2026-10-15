"""v12: Unabhaengigkeitstest des Kontomotors - ein abgeschalteter Strom (on = 0) mit Signalen in jeder 7. Minute darf
kein Konto veraendern (vor dem Fix: Noise-Pruefungen und RSI21-Wiederaufnahme hingen an fremden Signal-Minuten)."""
import x12  # noqa: F401
import numpy as np
import cfg11 as C, evl11 as V, eng11 as E
S = C.signals(); m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
Pv = E.params()
t = m.ev_t[::7]
t = t[(t > m.ev_t[0] + 1440 * 30)]
dummy = dict(name="DUMMY", sym=np.ones(len(t), np.int64), t=t, dir=np.ones(len(t), np.int64), ent=np.zeros(len(t)),
             fix=np.zeros(len(t), np.int64), sl=np.zeros(len(t)), tp=np.zeros(len(t)), tx=t + 30)
W = {k: V.WIN5[k] for k in ("Pruef 2024-25", "Pruef 2017-20", "Pruef 2011-15")}
m.set_generic(C.blocks(S)); a = V.evaluate(Pv, C.gp_v10(), windows=W)
m.set_generic(C.blocks(S, extra=[(18, dummy)])); b = V.evaluate(Pv, C.gp_v10(extra=[dict(on=0)]), windows=W)
for w in W:
    print(V.line("ohne Dummy " + w[-7:], a[w])); print(V.line("mit Dummy  " + w[-7:], b[w]))
ra = np.array([x[2:5] for x in a["_rows"]]); rb = np.array([x[2:5] for x in b["_rows"]])
print("Konten mit Abweichung (Ausz., Summe, Endsaldo):", int(np.any(np.abs(ra - rb) > 1e-6, axis=1).sum()), "von", len(ra))
