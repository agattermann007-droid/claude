"""Pruefung des Kandidaten kandidat_fade930:
1) Kandidatenmodul (wie locked_run: prepare -> signals -> qbt.simulate) liefert dieselben Trades wie der Forschungslauf
   (run.py, Regel FADE930, Ziel 1R).
2) Abschneide-Test: signals auf df bis T liefert fuer alle Signale bis T dieselben Signale (Zeit, Richtung, Stop, Ziel)
   und fuer Tage vor dem Tag von T dieselbe Schlusskerze.
3) Zelle mit qbt.report_cell wie im gesperrten Lauf (Train, Val 2024; info25 nur Info).
"""
import importlib.util
import os
import sys

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import ev  # noqa: E402
import qbt  # noqa: E402
import qdata as Q  # noqa: E402
import run as RUN  # noqa: E402


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
    mod = lade('kandidat_fade930.py')
    for inst in mod.INSTRUMENTS:
        df = Q.load(inst, Q.dev_start(inst), '2025-01-01')
        x = mod.prepare(df, inst)
        sig = mod.signals(x, inst)
        tr = qbt.trades_only(qbt.simulate(x, sig, inst))
        # 1) Forschungslauf (gleiche Regel ueber run.py-Bausteine)
        evk, insts, (a, b), spec, k, src = RUN.RULES['FADE930']
        et = ev.event_table(evk)
        sr = pd.concat([ev.build(x, g.index, a, b, RUN.direction(x, g.index, spec, int(tm)), k=k, tgt_R=1.0)
                        for tm, g in et.groupby('t_m')], ignore_index=True)
        trr = qbt.trades_only(qbt.simulate(x, sr, inst))
        same = (len(tr) == len(trr) and (tr['i_sig'].to_numpy() == trr['i_sig'].to_numpy()).all()
                and np.allclose(tr['R'].to_numpy(), trr['R'].to_numpy()))
        print(f'== {inst}: Trades gleich Forschungslauf: {same} (n {len(tr)} / {len(trr)})')
        per = {'Train': (str(Q.dev_start(inst).date()), '2024-01-01'), 'Val 2024': ('2024-01-01', '2025-01-01')}
        cell = qbt.report_cell(x, tr, per)
        print(cell[['n', 'per_day', 'tvs', 'win', 'R', 't', 't_day', 'null_tvs', 'null_win', 'null_R', 't_vs_null']].round(3).to_string())
        # 2) Abschneide-Test: 8 Signalzeitpunkte (T = Signalkerze), 4 Zeitpunkte kurz vor einer Signalkerze, 6 zufaellige
        full = key(x, sig)
        rng = np.random.default_rng(3)
        sigt = full.index[full.index >= pd.Timestamp('2021-06-01')]
        ts = list(rng.choice(sigt, 8, replace=False))
        ts += [pd.Timestamp(t) - pd.Timedelta(minutes=5) for t in rng.choice(sigt, 4, replace=False)]
        ts += list(rng.choice(x.index[x.index >= pd.Timestamp('2021-06-01')], 6, replace=False))
        bad = 0
        for T in sorted(pd.Timestamp(t) for t in ts):
            dT = df[df.index <= T].copy()
            dT.attrs.update(df.attrs)
            xT = mod.prepare(dT, inst)
            sT = key(xT, mod.signals(xT, inst))
            aT = full[full.index <= T]
            ok = aT.index.equals(sT.index)
            if ok:
                for c in ['d', 'stop', 'tgt_R']:
                    ok &= np.allclose(aT[c].to_numpy(float), sT[c].to_numpy(float), equal_nan=True)
                dayT = xT['nyday'].iloc[-1]
                m = (aT['day'] < dayT).to_numpy()
                ok &= bool((x.index[aT.loc[m, 'i_last'].to_numpy()] == xT.index[sT.loc[m, 'i_last'].to_numpy()]).all())
            bad += (not ok)
            print(f'  T={T}  Signale bis T: {len(aT):4d} / {len(sT):4d}  gleich: {ok}')
        print(f'  Abschneide-Test: {len(ts) - bad}/{len(ts)} gleich')


if __name__ == '__main__':
    main()
