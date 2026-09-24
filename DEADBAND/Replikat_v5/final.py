import json, numpy as np, robust as R, split as SP, evl5 as V, eng5 as E, batch as B
P50 = dict(db_tp1r=1.5, db_be=0.05, db_tp1f=0.5)
C2 = dict(P50, r21_risk=0.63, nz_risk=0.45, ge_mode=1, bank_on=1, bank_last=2, bank_minr=0.5, bank_mods=1,
          cool_n=4, cool_days=0, idea_cap=1.25)
AS_IS = dict(rule_losers=0, float_losers=0, swap_guard=0.0)
C = [("5.00 wie ist | GFT zaehlt netto", AS_IS),
     ("5.00 wie ist | GFT zaehlt nur Verlierer", dict(AS_IS, rule_losers=1)),
     ("5.00 regelsicher (Bremse Verlierer + Swap)", {}),
     ("5.10 (C2)", C2),
     ("5.00 wie ist | EOD 0.94", dict(AS_IS, floor_eod=1, floor_rel=1)),
     ("5.10 (C2) | EOD 0.94", dict(C2, floor_eod=1, floor_rel=1)),
     ("5.10 (C2) | GFT zaehlt netto", dict(C2, rule_losers=0)),
]
res = R.run(C, "final.json")
R.show(res)
out = {"roll": res}
for lbl, kw in (("5.00 wie ist | GFT zaehlt netto", AS_IS), ("5.10 (C2)", C2)):
    y = SP.per_start_year(kw if lbl.startswith("5.10") else kw)
    SP.show(lbl, y)
    out.setdefault("years", {})[lbl] = y
# Pfad ab 03.01.2022, 16 Stoerungen
m = V.mk()
for lbl, kw in (("5.00 wie ist | GFT zaehlt netto", AS_IS), ("5.10 (C2)", C2)):
    kw2 = dict(B.SAFE); kw2.update(kw)
    Pv = E.params(**kw2)
    a = m.day_index("2022-01-03"); b = len(m.days)
    rows = [V.one(Pv, a, b, s, 0.08, 0.3) for s in range(16)]
    pays = [r_["npay"] for r_ in rows]; bs = [r_["nbust"] for r_ in rows]
    net = [0.8*0.97*r_["sumpay"] - 148.5*r_["nbust"] for r_ in rows]
    print(f"Pfad ab 03.01.2022 {lbl}: Auszahlungen {np.mean(pays):.1f} (min {min(pays):.0f}, max {max(pays):.0f}), Busts {np.mean(bs):.1f} (min {min(bs)}, max {max(bs)}), Netto {np.mean(net):.0f} $")
    out.setdefault("path", {})[lbl] = dict(pay=float(np.mean(pays)), paymin=float(min(pays)), paymax=float(max(pays)),
                                         bust=float(np.mean(bs)), bustmin=float(min(bs)), bustmax=float(max(bs)), net=float(np.mean(net)))
json.dump(out, open("final_all.json", "w"), indent=1, default=float)
