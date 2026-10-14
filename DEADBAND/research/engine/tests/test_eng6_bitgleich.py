"""eng6 nach der Forschungs-Erweiterung (Tagesdatensaetze, we_resume, flat_only) rechnet mit Voreinstellungen
bitgleich zum Stand 8.10 (Commit d891859). Daten: synthetisch (engine/synthetisch.py), keine Forschungsaussage."""
import importlib.util
import os
import subprocess

import numpy as np
import pytest

from engine import synthetisch as SY

REF_COMMIT = "d891859"


@pytest.fixture(scope="module")
def markt(tmp_path_factory):
    import prep5 as P
    import sig5
    d = tmp_path_factory.mktemp("daten")
    SY.schreibe(str(d), "2021-01-03", "2022-06-30", seed=3)
    alt_data, alt_out = P.DATA, P.OUT
    P.DATA = str(d); P.OUT = str(tmp_path_factory.mktemp("cache"))
    try:
        D, db, r21, nz = sig5.build_all(save=False)
    finally:
        P.DATA, P.OUT = alt_data, alt_out
    S = dict(db=db, r21=r21, nz=nz)
    return D, S


@pytest.fixture(scope="module")
def ref_modul(tmp_path_factory):
    wurzel = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip()
    src = subprocess.run(["git", "show", f"{REF_COMMIT}:DEADBAND/Replikat_v6/eng6.py"], capture_output=True, text=True,
                         check=True, cwd=wurzel).stdout
    d = tmp_path_factory.mktemp("ref")
    pfad = os.path.join(d, "eng6_ref810.py")
    with open(pfad, "w") as f:
        f.write(src)
    spec = importlib.util.spec_from_file_location("eng6_ref810", pfad)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _bloecke(mk, rng, n=400):
    """zufaellige generische Signale (Einstieg am Open einer vorhandenen M5-Kerze)."""
    out = []
    for s_ in range(4):
        sym = rng.integers(0, 2, n)
        te = np.empty(n, np.int64); rd = np.empty(n); tx = np.empty(n, np.int64)
        for i in range(n):
            ny = mk.D[("XAU", "NAS")[sym[i]]]["ny"]
            j = rng.integers(500, len(ny) - 3000)
            te[i] = ny[j]; tx[i] = ny[j + rng.integers(10, 2000)]
            c = mk.D[("XAU", "NAS")[sym[i]]]["c"][j]
            rd[i] = c * rng.uniform(0.002, 0.01)
        out.append(dict(str=s_, sym=sym, dir=rng.choice([-1, 1], n), t_entry=te, rd=rd, tp=rng.choice([0.0, 1.0, 3.0, 8.0]),
                        t_exit=tx, w=1.0))
    return out


BASIS = dict(rule_losers=1, float_losers=1, swap_guard=0.8, validpct=0.505, minpayout=105.0, r21_risk=0.5, nz_risk=0.45,
             cool_n=3, gesamtbudget=0.9, idea_cap=0.9, bank_on=1, bank_last=5, bank_minr=0.3, bank_mods=15, ddfull=3.5,
             ddmin=1.25, ddfmin=0.1, belowstart=0.95, valid_stop=1, ge_mode=1, ge_rueck=0.0, db_tp1r=1.5, db_be=0.05,
             db_tp1f=0.5)
GPS = [dict(on=1, risk=0.75, maxtrades=1, harv=1), dict(on=1, risk=0.5, tp1r=1.5, tp1f=0.5, be=0.05, tpdelay=0),
       dict(on=1, risk=0.5, minbuf=4.0), dict(on=1, risk=0.6, maxloss=2, budget=0.5)]


@pytest.mark.parametrize("db_on", [0, 1])
def test_bitgleich_zu_810(markt, ref_modul, db_on):
    import eng6 as E
    D, S = markt
    mk_neu = E.Market(D=D, S=S)
    mk_ref = ref_modul.Market(D=D, S=S)
    rng = np.random.default_rng(11)
    bl = _bloecke(mk_neu, rng)
    mk_neu.set_generic(bl); mk_ref.set_generic(bl)
    Pn = E.params(**dict(BASIS, db_on=db_on)); Pr = ref_modul.params(**dict(BASIS, db_on=db_on))
    nd = len(mk_neu.days)
    for seed, skip in ((0, 0.0), (3, 0.05)):
        a = E.run(mk_neu, Pn, 60, nd, seed=seed, skip=skip, GP=E.gparams(GPS))
        b = ref_modul.run(mk_ref, Pr, 60, nd, seed=seed, skip=skip, GP=ref_modul.gparams(GPS))
        assert np.array_equal(a["st"], b["st"])
        assert np.array_equal(a["tr"], b["tr"])
        assert np.array_equal(a["ev"], b["ev"])
        c = E.run(mk_neu, Pn, 60, nd, seed=seed, skip=skip, GP=E.gparams(GPS), tage=True)
        assert np.array_equal(a["st"], c["st"]) and np.array_equal(a["tr"], c["tr"])
        assert a["st"][E.SI["ntr"]] >= 0
    assert a["st"][E.SI["entries"]] > 20, "zu wenige Einstiege - Test waere nicht aussagekraeftig"


def test_tagesdatensaetze_konsistent(markt):
    import eng6 as E
    D, S = markt
    mk = E.Market(D=D, S=S)
    mk.set_generic(_bloecke(mk, np.random.default_rng(5)))
    r = E.run(mk, E.params(**BASIS), 60, len(mk.days), seed=0, GP=E.gparams(GPS), tage=True)
    T = r["tage"]
    K = {n: i for i, n in enumerate(E.KDN)}
    assert len(T) > 300
    assert np.all(np.diff(T[:, K["tag"]]) > 0)
    # Equity-Spanne enthaelt Tagesende-Equity, Saldo-Kette passt (Saldo0 eines Tages = Saldo des Vortags ohne Auszahlung/Neukonto)
    assert np.all(T[:, K["eq_min"]] <= T[:, K["equity"]] + 1e-6)
    assert np.all(T[:, K["eq_max"]] >= T[:, K["equity"]] - 1e-6)
    ok = (T[1:, K["auszahlung"]] == 0) & (T[1:, K["neukonto"]] == 0) & (T[1:, K["pleite"]] == 0) & (T[:-1, K["pleite"]] == 0)
    assert np.allclose(T[1:, K["saldo0"]][ok], T[:-1, K["saldo"]][ok], atol=1e-6)
    # Zahl der Auszahlungen und Pleiten wie in der Statistik
    assert int((T[:, K["auszahlung"]] > 0).sum()) == int(r["st"][E.SI["npay"]])
    assert int((T[:, K["pleite"]] > 0).sum()) == int(r["st"][E.SI["nbust"]])


def test_neue_spalten_wirken(markt):
    """we_resume und flat_only veraendern das Ergebnis (sonst waeren sie wirkungslos verdrahtet)."""
    import eng6 as E
    D, S = markt
    mk = E.Market(D=D, S=S)
    mk.set_generic(_bloecke(mk, np.random.default_rng(7)))
    Pv = E.params(**BASIS)
    nd = len(mk.days)
    a = E.run(mk, Pv, 60, nd, GP=E.gparams(GPS))
    b = E.run(mk, Pv, 60, nd, GP=E.gparams([dict(g, flat_only=1) for g in GPS]))
    c = E.run(mk, Pv, 60, nd, GP=E.gparams([dict(g, we_resume=1) for g in GPS]))
    assert b["st"][E.SI["entries"]] < a["st"][E.SI["entries"]]
    assert c["st"][E.SI["we_re"]] > a["st"][E.SI["we_re"]]
