"""Pruefung RSI21 Eigenkapital gegen das Replikat v6:
  1. ek_sig.select(features(D)) mit Voreinstellungen = sig5.r21_signals(D) (alle Felder, jede Zeile).
  2. ek_sim._core im Abgleich-Modus (feste Groesse vom Startkapital, GFT-Swap, eng10-Uhr, kein Margin-Check) = eng10 mit
     RSI21 allein und abgeschalteten GFT-Regeln (kein Boden, keine Bremsen, keine Tagesgrenze, keine Auszahlung, kein
     Wochenend-Schluss, keine Budgets, keine Pufferkurve): gleiche Trades (Einstiegszeit, Platz, Ergebnis in $).
Aufruf: python t_ek_sim.py  -> ergebnisse/t_ek_sim.txt"""
import os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Replikat_v6"))
import ek_data, ek_sig, ek_sim                                     # noqa: E402
import sig5 as S5, eng10 as E                                       # noqa: E402

OUT = []


def log(s):
    print(s, flush=True)
    OUT.append(s)


t0 = time.time()
D = ek_data.load()
log(f"Daten: Gold {len(D['XAU']['ny'])} M5, NAS {len(D['NAS']['ny'])} M5 (Naht NAS {D['meta']['naht']})")

# ---------------------------------------------------------------- 1. Signale
ref = S5.r21_signals(D)
F = ek_sig.features(D)
sg = ek_sig.select(F)
ok1 = all(len(ref[k]) == len(sg[k]) for k in ("T", "sym", "tf", "dir", "rd", "folge"))
if ok1:
    for k in ("T", "sym", "tf", "dir", "folge"):
        ok1 &= bool(np.array_equal(ref[k], sg[k]))
    ok1 &= bool(np.allclose(ref["rd"], sg["rd"], rtol=0, atol=1e-9))
log(f"1. Signale: sig5 {len(ref['T'])} (Folge {int(ref['folge'].sum())}), ek_sig {len(sg['T'])} (Folge {int(sg['folge'].sum())}) "
    f"-> {'IDENTISCH' if ok1 else 'ABWEICHUNG'}  [{time.time() - t0:.0f}s]")

# ---------------------------------------------------------------- 2. Konto gegen eng10
mk = ek_sim.Market(D)
R = mk.signals(sg)
me = E.Market(D=D, S=None)
# RSI21-Block wie eng10.Market.__init__
rows = []
syms = ("XAU", "NAS")
for a in range(len(ref["T"])):
    k = int(ref["sym"][a]); T = int(ref["T"][a])
    ny = D[syms[k]]["ny"]
    i5 = int(np.searchsorted(ny, T))
    if i5 >= len(ny):
        continue
    ev = int(np.searchsorted(me.ev_t, ny[i5]))
    rows.append((ev, k, int(ref["tf"][a]), int(ref["dir"][a]), float(ref["rd"][a]), i5, 1 - int(ref["folge"][a])))
rows.sort()
A = np.array(rows)
me.r21 = dict(ev=A[:, 0].astype(np.int64), sym=A[:, 1].astype(np.int64), tf=A[:, 2].astype(np.int64),
              dir=A[:, 3].astype(np.int64), rd=A[:, 4], i5=A[:, 5].astype(np.int64), first=A[:, 6].astype(np.int64))
me.r21["next"] = np.searchsorted(me.r21["ev"], np.arange(len(me.ev_t) + 1), side="left").astype(np.int64)
BIG = 1e9
Pe = E.params(maxlosspct=BIG, rulefloat=BIG, ruleday=BIG, floatstop=BIG, daystop=BIG, minpayout=1e12, needvalid=10 ** 6,
              ddfull=0.0, belowstart=1.0, gesamtbudget=BIG, db_on=0, nz_on=0, r21_on=1, r21_risk=0.5, r21_budget=BIG,
              r21_ripeclose=0, harvest=0, ge_on=0, we_on=0, cool_n=0, idea_cap=0.0, lev=BIG, idea_margin=BIG,
              r21_tp1r=1.0, r21_be=0.05, bank_on=0, bank_last=0, vp_on=0)
d0 = 0; d1 = len(me.days) - 1
re_ = E.run(me, Pe, d0, d1)
tr_e = re_["tr"]
tr_e = tr_e[tr_e[:, 2] >= 2]                                         # nur RSI21-Plaetze (2..5)
Pk = ek_sim.params(risk=0.5, size_mode=0, swap_mode=0, lev_gold=0.0, lev_nas=0.0, clock_eng10=1, maxloss=2, second=1,
                   be_at=1.0, be_plus=0.05, exitbars=1152, exitdays=8.0, stopout=0.0)
rk = ek_sim.run(mk, R, Pk, d0=str(mk.days[0].astype("datetime64[D]")), d1="2027-01-01")
tr_k = rk["tr"]
log(f"2. eng10 (RSI21 allein, GFT-Regeln aus): {len(tr_e)} Trades, Summe {tr_e[:, 1].sum():,.2f} $ | "
    f"ek_sim: {len(tr_k)} Trades, Summe {(tr_k[:, 9] - tr_k[:, 10]).sum():,.2f} $")
# Zuordnung: Einstiegs-Uhr (eng10: Servertag*1440 + NY-Minute), Platz (eng10 2+sym / 4+sym, ek A=sym / B=2+sym), Richtung
ke = [(int(r[3]), int(r[2]) - 2, int(r[9]), round(float(r[1]), 6)) for r in tr_e]
kk = [(int(r[16]), int(r[3]), int(r[5]), round(float(r[9] - r[10]), 6)) for r in tr_k]
ke.sort(); kk.sort()
same = len(ke) == len(kk) and all(a[:3] == b[:3] and abs(a[3] - b[3]) < 1e-6 for a, b in zip(ke, kk))
nd = sum(1 for a, b in zip(ke, kk) if a[:3] != b[:3] or abs(a[3] - b[3]) >= 1e-6)
log(f"   Trade fuer Trade (Einstieg, Platz, Richtung, Ergebnis): {'IDENTISCH' if same else f'{nd} Abweichungen'}")
if not same:
    for a, b in list(zip(ke, kk))[:400]:
        if a[:3] != b[:3] or abs(a[3] - b[3]) >= 1e-6:
            log(f"   erste Abweichung: eng10 {a}  ek {b}")
            break
log(f"fertig [{time.time() - t0:.0f}s]")
os.makedirs(os.path.join(HERE, "ergebnisse"), exist_ok=True)
with open(os.path.join(HERE, "ergebnisse", "t_ek_sim.txt"), "w") as f:
    f.write("\n".join(OUT) + "\n")
