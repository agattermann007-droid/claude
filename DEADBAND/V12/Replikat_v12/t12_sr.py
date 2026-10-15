"""v12 / Prompt 9.4: Warum hilft SR 2024-25 nicht? Verdraengung oder schwaechere Marken?

1) Stromebene: SR je Marke und Zeitraum (R, E, PF), getrennt nach Fade-Regime live / nicht live.
2) Kontoebene, 16 Stoerungen gemittelt: $/J je Modul V8 gegen V10 (wer verliert, wenn SR dazukommt?).
3) Kontoebene, gepaart (32 Seeds) gegen V10: SR nur bei Fades aus, SR nur bei Fades live, nur SRPRE, je eine Marke weg.
"""
import x12  # noqa: F401
import pickle, numpy as np
import cfg11 as C, evl11 as V, eng11 as E, gen11 as G, sim11 as M, reg12 as R

S = C.signals()
live_at = G.portfolio_guard(S["fades"])
PER = [("2011-01-01", "2016-09-01", "11-16"), ("2016-09-01", "2022-01-01", "16-21"),
       ("2022-01-01", "2024-01-01", "22-23"), ("2024-01-01", "2026-03-01", "24-26")]
print("== 1) SR je Marke (Stromebene, Schlupf 1/4 Spread)")
for b in S["sr"]:
    r = M.simulate(b, tpdelay=4); ok = r["why"] >= 0
    lv = np.array([live_at(int(t))[0] for t in b["t"]], bool)
    for lo, hi, lab in PER:
        a = M.stats(r["R"][ok], b["t"][ok], lo, hi)
        l1 = M.stats(r["R"][ok & lv], b["t"][ok & lv], lo, hi); l0 = M.stats(r["R"][ok & ~lv], b["t"][ok & ~lv], lo, hi)
        print(f"{b['name']:6s} {lab}: {M.fmt(a)} | Fades live: n{l1['n']:4d} E{l1['er']:+.3f} | aus: n{l0['n']:4d} E{l0['er']:+.3f}", flush=True)

m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
Pv = E.params()
W24 = {"Pruef 2024-25": V.WIN5["Pruef 2024-25"], "Auswahl 2022": V.WIN5["Auswahl 2022"]}
print("== 2) $/J je Modul (Mittel ueber 16 Stoerungen)")
m.set_generic(C.blocks(S))
names = {f"g{i}": n for i, n in enumerate(C.STREAMS)}
names.update(r21="RSI21", nz="Noise")
res = {}
for lab, GP in (("V8", C.gp_v8()), ("V10", C.gp_v10())):
    res[lab] = V.evaluate(Pv, GP, windows=W24, seeds=tuple(range(1, 17)))
for w in W24:
    a, b = res["V8"][w]["mods"], res["V10"][w]["mods"]
    ks = sorted(set(a) | set(b), key=lambda k: (len(k), k))
    print(w, f"V8 {res['V8'][w]['net']:.0f} $/J, V10 {res['V10'][w]['net']:.0f} $/J")
    for k in ks:
        x = a.get(k, dict(pnl=0, tr=0, wr=0)); y = b.get(k, dict(pnl=0, tr=0, wr=0))
        print(f"   {names.get(k, k):7s} V8 {x['pnl']:6.0f}$ {x['tr']:5.1f}tr | V10 {y['pnl']:6.0f}$ {y['tr']:5.1f}tr | diff {y['pnl']-x['pnl']:+6.0f}$ {y['tr']-x['tr']:+5.1f}tr")

print("== 3) gepaart gegen V10 (32 Seeds)")
base = pickle.load(open("ergebnisse/base_v10_32.pkl", "rb"))
SEEDS = tuple(range(1, 33))
sr_idx = {b["name"]: 14 + j for j, b in enumerate(S["sr"])}


def run(lab, sr_blocks, gp, pv=None):
    bl = C.blocks(S, which=("fades", "special"))
    for b in sr_blocks:
        bl.append((sr_idx[b["name"]], b, 1.0))
    m.set_generic(bl)
    r = V.evaluate_seeds(Pv if pv is None else pv, gp, seeds=SEEDS, windows=V.WIN5)
    print(V.paired(base, r, lab), flush=True)
    return r


out = {}
gp_ns = C.gp_v10()
for j in range(14, 18):
    gp_ns[j, E.GPI["noser"]] = 1.0
out["SR ohne Serienzaehler"] = run("SR ohne Serienzaehler", S["sr"], gp_ns)
out["Serien-Stopp aus"] = run("Serien-Stopp aus", S["sr"], C.gp_v10(), E.params(cool_n=0))
out["Serien-Stopp 4"] = run("Serien-Stopp 4", S["sr"], C.gp_v10(), E.params(cool_n=4))
out["SR nur Fades aus"] = run("SR nur Fades aus", [R.gate(b, live_at, False) for b in S["sr"]], C.gp_v10())
out["SR nur Fades live"] = run("SR nur Fades live", [R.gate(b, live_at, True) for b in S["sr"]], C.gp_v10())
out["nur SRPRE"] = run("nur SRPRE", [b for b in S["sr"] if b["name"] == "SRPRE"], C.gp_v10())
for nm in sr_idx:
    out[f"ohne {nm}"] = run(f"ohne {nm}", [b for b in S["sr"] if b["name"] != nm], C.gp_v10())
pickle.dump(out, open("ergebnisse/t12_sr.pkl", "wb"))
