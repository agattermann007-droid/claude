"""Signale der alten Module (DEADBAND, RSI21, Noise) auf den Fremddaten 2006-2021."""
import numpy as np, pickle, os, time
import prep5 as P, gext, sig5 as S5
t = time.time()
DX = gext.data_ext()
D = {}
for s, d in DX.items():
    d = dict(d)
    ny = d["ny"]
    d["pday"] = (ny + 420) // 1440
    for key, mins in (("m15", 15), ("m30", 30), ("h1", 60)):
        d[key] = P.agg(ny, d["o"], d["h"], d["l"], d["c"], d["v"], mins)
    D[s] = d
db = {"XAU": S5.db_candidates(D, "XAU", 0.70, False), "NAS": S5.db_candidates(D, "NAS", 0.65, True)}
r21 = S5.r21_signals(D)
nz = S5.nz_days(D)
pickle.dump(dict(db=db, r21=r21, nz=nz), open(os.path.join(P.OUT, "sig5_ext.pkl"), "wb"))
pickle.dump(D, open(os.path.join(P.OUT, "DXfull.pkl"), "wb"))
print(f"DEADBAND XAU {len(db['XAU']['T'])}, NAS {len(db['NAS']['T'])}, RSI21 {len(r21['T'])} (Folge {r21['folge'].sum()}), Noise-Pruefungen {len(nz['day'])} [{time.time()-t:.0f}s]")
