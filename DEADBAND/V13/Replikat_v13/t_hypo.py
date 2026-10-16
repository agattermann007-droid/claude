"""Hypothese 'Move vorbei': MFE der Verlierer je Strom + Bestaetigungs-Einstieg (Stop-Order x R in Signalrichtung)."""
import numpy as np
import cfg11 as C, sim11 as M
S = C.signals()
PER = [("2016-09-01", "2022-01-01", "16-21"), ("2022-01-01", "2024-01-01", "22-23"), ("2024-01-01", "2026-03-01", "24-26")]
def per(t, R):
    out = []
    for lo, hi, lab in PER:
        st = M.stats(R, t, lo, hi)
        out.append(f"{lab}: n{st['n']:4d} WR{st['wr']:3.0f}% E{st['er']:+.3f} S{st['sum']:+6.1f}")
    return " | ".join(out)
streams = [(b["name"], {k: (v[b["live"]] if isinstance(v, np.ndarray) and len(v) == len(b["live"]) else v) for k, v in b.items()}) for b in S["fades"]]
streams += [("S0830", S["spike"]), ("LW", S["lw"]), ("XA", S["xa"]), ("TD", S["td"])] + [(b["name"], b) for b in S["sr"]]
print("== Verlierer: Anteil ohne +0,1 / +0,2 R Vorlauf (alle Jahre, live-Signale) ==")
for nm, b in streams:
    tpd = 4 if nm.startswith("SR") else 5
    r = M.simulate(b, tpdelay=tpd)
    ok = r["why"] >= 0
    los = ok & (r["R"] < 0)
    print(f"{nm:6s} Verlierer {los.sum():4d}  MFE<0,1R {100*np.mean(r['mfe'][los] < 0.1):3.0f}%  MFE<0,2R {100*np.mean(r['mfe'][los] < 0.2):3.0f}%   Gewinner MFE<0,2R {100*np.mean(r['mfe'][ok & (r['R']>0)] < 0.2):3.0f}%")
print("== Bestaetigungs-Einstieg ==")
for nm, b in streams:
    tpd = 4 if nm.startswith("SR") else 5
    r = M.simulate(b, tpdelay=tpd); ok = r["why"] >= 0
    print(f"{nm:6s} Basis        {per(b['t'][ok], r['R'][ok])}")
    for xr in (0.1, 0.2, 0.3):
        for wm in (30, 0):
            c = M.simulate_conf(b, xr, wm, tpdelay=tpd); ok = c["why"] >= 0
            print(f"{nm:6s} x{xr:.1f} w{wm:3d}    {per(b['t'][ok], c['R'][ok])}")
