"""v12: neue Stroeme auf Kontoebene, gepaart gegen V10 (32 Seeds, 5 Fenster). Aufruf: python t12_acct.py NAME [NAME ...]
Kandidaten in KAND (Generator, Risiko, Regime-Filter: False = nur bei Fades aus, None = immer). Stromnummer 18 (+19 ...)."""
import x12  # noqa: F401
import sys, pickle, numpy as np
import cfg11 as C, evl11 as V, eng11 as E, gen11 as G, reg12 as R

S = C.signals()
m = V.mk(); m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
live_at = G.portfolio_guard(S["fades"])
Pv = E.params()
SEEDS = tuple(range(1, 33))
base = pickle.load(open("ergebnisse/base_v10_32.pkl", "rb"))


def imom(ts, ti, s, minr, dirs, x=955):
    return lambda: R.imom(ts, ti, x, s, minr, dirs)


KAND = {}
for ts in (600, 630):
    for s in (0.2, 0.3, 0.4):
        for minr in (0.2, 0.3, 0.4):
            for dirs in (0, 1):
                KAND[f"IM{ts}_s{s}_m{minr}_d{dirs}"] = imom(ts, ts, s, minr, dirs)


for n in (5, 10):
    for dirs in (0, 1):
        for s in (0.10, 0.15):
            KAND[f"ORB{n}_d{dirs}_s{s}"] = (lambda n=n, dirs=dirs, s=s: R.orb(n, dirs, 0, s, 0.0))

# TD-Generator (Zeile fuer Zeile wie TdKerze im EA) mit IMOM-Parametern: so wird das Modul im EA gebaut (zweites TD-Modul)
for ein in (600, 630):
    for s in (0.2, 0.25, 0.3):
        for minr in (0.2, 0.3, 0.4):
            for dirs in (0, 1):
                KAND[f"TD{ein}_s{s}_m{minr}_d{dirs}"] = (lambda ein=ein, s=s, minr=minr, dirs=dirs:
                                                          G.td(ein=ein, aus=955, schluss=960, min_atr=minr, stop_atr=s,
                                                               ziel_r=0.0, richtung=dirs))

W3 = {k: V.WIN5[k] for k in ("Auswahl 2022", "Pruef 2017-20", "Pruef 2011-15")}


def run(names, risk=0.5, want=False, label=None, seeds=SEEDS, windows=V.WIN5, base=base):
    extra = []; st = []
    for j, nm in enumerate(names):
        b = KAND[nm]()
        if want is not None:
            b = R.gate(b, live_at, want)
        extra.append((18 + j, b))
        st.append(dict(on=1, risk=risk, maxtrades=1, harv=1, tpdelay=5, minsprd=6))
    m.set_generic(C.blocks(S, extra=extra))
    r = V.evaluate_seeds(Pv, C.gp_v10(extra=st), seeds=seeds, windows=windows)
    lab = label or f"{'+'.join(names)} {risk:.2f}% {'aus' if want is False else ('live' if want else 'immer')}"
    print(V.paired(base, r, lab), flush=True)
    return lab, r


if __name__ == "__main__":
    # Stufe 1 (python t12_acct.py stufe1): alle Kandidaten gegated (nur Fades aus), 0,5 %, 16 Seeds, 3 Fenster
    # (2023 und 2024-25 sind bei Fades-aus-Stroemen praktisch unveraendert: Waechter dort zu 98-100 % live)
    out = {}
    if sys.argv[1] == "stufe1":
        S16 = tuple(range(1, 17))
        b16 = {w: base[w][:16] for w in W3}
        for nm in [k for k in KAND if not k.startswith("TD")]:
            lab, r = run([nm], 0.5, seeds=S16, windows=W3, base=b16)
            out[lab] = r
        pickle.dump(out, open("ergebnisse/t12_acct_stufe1.pkl", "wb"))
    else:
        risks = [float(x) for x in sys.argv[1].split(",")]
        for nm in sys.argv[2:]:
            for rk in risks:
                lab, r = run([nm], rk)
                out[lab] = r
        pickle.dump(out, open(f"ergebnisse/t12_acct_{sys.argv[2]}.pkl", "wb"))
