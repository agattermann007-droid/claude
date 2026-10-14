"""Handelssimulator (engine/handel.py) und Kontomotor eng6 (generischer Strom mit DEADBAND-Ausstieg, we_resume) gehen
bei denselben Einstiegen gleich aus. Konto so gross, dass Lot-Rundung und Kontoregeln keine Rolle spielen.
Daten synthetisch (Open = Schluss davor), keine Forschungsaussage."""
import numpy as np
import pytest

from engine import handel as HD
from engine import spec as SP


OFFEN = dict(start=1e8, rulefloat=0.0, ruleday=0.0, maxlosspct=99.0, floatstop=0.0, daystop=99.0, ddfull=0.0, belowstart=1.0,
             gesamtbudget=1000.0, idea_cap=0.0, lev=0.0, idea_margin=0.0, needvalid=999, minpayout=1e12, db_on=0, r21_on=0,
             nz_on=0, harvest=0, ge_on=0, bank_on=0, valid_stop=0, cool_n=0, swap_guard=0.0, slip_frac=0.0, minlottol=1e9,
             we_on=1, we_reentry=1, we_reif=1, we_stopmaxr=2.0, we_spreadr=0.15, we_genau=1)


@pytest.mark.parametrize("kurz,sym", [("XAU", SP.XAU), ("NAS", SP.NAS)])
def test_gleiches_ergebnis(daten, kurz, sym):
    import eng6 as E
    D = daten
    mk = E.Market(D=D, S=None)
    d = D[kurz]
    M = HD.markt_arrays(d["ny"], d["o"], d["h"], d["l"], d["c"], d["sp"])
    rng = np.random.default_rng(4)
    n = 300
    ein = np.sort(rng.choice(np.arange(200, len(d["ny"]) - 4000), n, replace=False))
    richtung = rng.choice([-1, 1], n)
    a = np.clip(np.abs(np.diff(d["c"]))[ein - 1], 0.2, None)
    rd = d["c"][ein] * rng.uniform(0.002, 0.006, n)
    tx = HD.zeit_ausstieg_ny(M, ein, 192)
    k = 0 if kurz == "XAU" else 1
    blk = dict(str=0, sym=np.full(n, k), dir=richtung, t_entry=d["ny"][ein], rd=rd, tp=8.0, t_exit=tx, w=1.0)
    mk.set_generic([blk])
    GP = E.gparams([dict(on=1, risk=0.1, tp1r=1.5, tp1f=0.5, be=0.05, tpdelay=0, we_resume=1, usefak=0, ripeclose=0)])
    r = E.run(mk, E.params(**OFFEN), 0, len(mk.days), GP=GP)
    tr = r["tr"]
    assert len(tr) > 50
    risiko = 1e8 * 0.1 / 100.0
    # eng6-Zeilen je Einstieg zusammenfassen (Wochenend-Schluss + Wiederaufnahme = ein Einstieg)
    tmin = tr[:, 3].astype(np.int64)
    # eng6 traegt die Einstiegsminute als Servertag*1440 + NY-Minute ein: nach 17:00 NY einen Tag zu spaet
    tmin = np.where(tmin % 1440 >= 17 * 60, tmin - 1440, tmin)
    eng = {}
    for t_, v in zip(tmin, tr[:, 1]):
        eng[t_] = eng.get(t_, 0.0) + v
    idx = {int(t): i for i, t in enumerate(d["ny"][ein])}
    sel = [idx[t] for t in eng if t in idx]
    erg = HD.handel(M, sym, ein[sel], richtung[sel], rd[sel], 8.0)
    mpp = sym.geld_je_preis()
    lots = np.floor(risiko / (rd[sel] * mpp) / 0.01 + 0.5) * 0.01             # wie eng6 (tatsaechliches Risiko)
    r_eng = np.array([eng[int(d["ny"][ein[i]])] for i in sel]) / (lots * rd[sel] * mpp)
    diff = np.abs(r_eng - erg[:, 0])
    # Rest: eng6 rundet den halben Lot beim Teilverkauf ab (floor), der Simulator rechnet genau 50 %
    assert np.max(diff) < 1e-3, (np.max(diff), int(np.argmax(diff)))
    assert np.mean(diff < 1e-9) > 0.7
    assert (erg[:, 5] == 3).sum() >= 3 and (erg[:, 6] == 2).sum() >= 3, "Zeit-Exit und Wiederaufnahme muessen vorkommen"
