"""Pruefung der Kandidaten:
1) Kandidatenmodul (wie locked_run: prepare -> signals -> qbt.simulate) liefert dieselben Trades wie der Forschungslauf.
2) Abschneide-Test: signals auf df bis T liefert fuer alle Signale bis T dieselben Signale (und dieselbe Nachzieh-Spalte).
3) Zelle mit qbt.report_cell so, wie der gesperrte Lauf sie rechnet.
"""
import importlib.util
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)

import numpy as np
import pandas as pd

import common as C
import qbt
import qdata as Q
import varianten as V

KAND = {'kandidat_A_n10_ziel15.py': ('N10', 't15_15'),
        'kandidat_B_paps_tp05be.py': ('PAPS', 'tp05_be'),
        'kandidat_C_pap0_tp10paper.py': ('PAP0', 'tp10_paper')}
FIELDS = ['d', 'stop', 'tgt_R', 'tp1_R', 'tp1_frac', 'be_after_tp1', 'trail']


def lade(f):
    spec = importlib.util.spec_from_file_location(f[:-3], os.path.join(HIER, f))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def key(x, sig):
    s = sig.copy()
    s['t'] = x.index[s['i_sig'].to_numpy()]
    return s.set_index('t')


def main():
    pd.set_option('display.width', 250)
    for f, (entry, exn) in KAND.items():
        mod = lade(f)
        for inst in mod.INSTRUMENTS:
            df = Q.load(inst, Q.dev_start(inst), '2025-01-01')
            x = mod.prepare(df, inst)
            sig = mod.signals(x, inst)
            tr = qbt.trades_only(qbt.simulate(x, sig, inst))
            # 1) gleich dem Forschungslauf
            xr = C.load(inst)
            trr = C.run(xr, C.make_signals(xr, entry, dict(V.EXITS_N10 if entry == 'N10' else V.EXITS_PAP)[exn]), inst)
            same = (len(tr) == len(trr) and (tr['i_sig'].to_numpy() == trr['i_sig'].to_numpy()).all()
                    and np.allclose(tr['R'].to_numpy(), trr['R'].to_numpy()))
            print(f'\n== {f} {inst}: Trades gleich Forschungslauf: {same} (n {len(tr)} / {len(trr)})')
            cell = qbt.report_cell(x, tr, C.periods(inst))
            print(cell[['n', 'per_day', 'tvs', 'win', 'R', 't', 't_day', 'null_tvs', 'null_win', 'null_R', 't_vs_null']].round(3).to_string())
            # 2) Abschneide-Test
            full = key(x, sig)
            rng = np.random.default_rng(1)
            ts = list(rng.choice(full.index[full.index >= pd.Timestamp('2022-01-01')], 6, replace=False))
            ins_idx = x.index[x['in_sess'] & (x.index >= pd.Timestamp('2022-01-01'))]
            ts += list(rng.choice(ins_idx, 6, replace=False))
            bad = 0
            for T in sorted(ts):
                T = pd.Timestamp(T)
                dT = df[df.index <= T].copy()
                dT.attrs.update(df.attrs)
                xT = mod.prepare(dT, inst)
                sT = key(xT, mod.signals(xT, inst))
                a = full[full.index <= T]
                cols = [c for c in FIELDS if c in a.columns]
                ok = a.index.equals(sT.index)
                if ok:
                    for c in cols:
                        u, v = a[c].to_numpy(), sT[c].to_numpy()
                        if u.dtype.kind in 'fc':
                            ok &= np.allclose(u, v, equal_nan=True)
                        else:
                            ok &= bool((u == v).all())
                    # i_last als Zeitpunkt, nur fuer Tage vor dem Tag von T
                    dT_day = xT['sday'].iloc[-1]
                    m = a['sday'] < dT_day
                    ok &= bool((x.index[a.loc[m, 'i_last'].to_numpy()] == xT.index[sT.loc[m, 'i_last'].to_numpy()]).all())
                if 'tr_paper_dir' in x.columns and ok:
                    u = x.loc[x.index <= T, 'tr_paper_dir'].to_numpy()
                    v = xT['tr_paper_dir'].to_numpy()
                    ok &= np.allclose(u, v, equal_nan=True)
                bad += (not ok)
                print(f'  T={T}  Signale bis T: {len(a):4d} / {len(sT):4d}  gleich: {ok}')
            print(f'  Abschneide-Test: {len(ts) - bad}/{len(ts)} gleich')


if __name__ == '__main__':
    main()
