"""Machbarkeit: 5.10 mit Mindestauszahlung 3 % / 4 % (brutto) - Kennzahlen gegen die neuen Anforderungen."""
import json, numpy as np, robust as R
P50 = dict(db_tp1r=1.5, db_be=0.05, db_tp1f=0.5)
C2 = dict(P50, r21_risk=0.63, nz_risk=0.45, ge_mode=1, bank_on=1, bank_last=2, bank_minr=0.5, bank_mods=1,
          cool_n=4, cool_days=0, idea_cap=1.25)
C = [("5.10", C2),
     ("5.10 Ausz>=3%", dict(C2, minpayout=240.0)),
     ("5.10 Ausz>=4%", dict(C2, minpayout=320.0))]
res = R.run(C, "feas.json")
for k, v in res.items():
    m = v["mean"]; b1 = v["by"]["250"]
    print(f"{k:16s} Ausz/J {m['pay']:5.2f} $/Ausz {m['paymean']:4.0f} Busts/J {m['bust']:5.3f} Netto {m['net']:5.0f} brutto/J {m['gross']:5.0f} "
          f"S5 {m['s5']:5.2f} S8 {m['s8']:4.2f} maxS {m['mx']:5.2f} Tr/J {m['tr']:4.0f} WR {m['wr']:4.1f} Zyklus {m['cyc']:4.1f}d P(B)1J {b1['p_bust']:.3f}")
