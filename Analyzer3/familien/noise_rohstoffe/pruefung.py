"""Pruefung der Kandidatenmodule:
1. Kandidat ueber qbt.simulate liefert dieselben Trades wie der Forschungslauf (out/trades_*.parquet).
2. Abschneide-Test: signals auf df bis Zeitpunkt T liefert fuer alle Signale bis T dieselben Signale
   (i_sig, d, stop, Ziel/Teilziel); i_last nur fuer abgeschlossene Tage verglichen.
Aufruf: python3 pruefung.py kandidat_xxx.py"""
import importlib.util
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qdata as Q  # noqa: E402
import qbt  # noqa: E402


def load_mod(path):
    spec = importlib.util.spec_from_file_location('kand', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cut_test(mod, inst, df, n_cuts=10, seed=3):
    x = mod.prepare(df, inst)
    full = mod.signals(x, inst)
    full = full.assign(t_sig=x.index[full['i_sig'].to_numpy()]).set_index('t_sig')
    rng = np.random.default_rng(seed)
    cand = full.index[(full.index > df.index[0] + pd.Timedelta(days=120))]
    cuts = list(rng.choice(cand, size=min(n_cuts, len(cand)), replace=False))
    bad = 0
    for T in cuts:
        T = pd.Timestamp(T)
        d2 = df[df.index <= T].copy()     # Daten bis einschliesslich Signalkerze
        d2.attrs.update(df.attrs)
        x2 = mod.prepare(d2, inst)
        s2 = mod.signals(x2, inst)
        s2 = s2.assign(t_sig=x2.index[s2['i_sig'].to_numpy()]).set_index('t_sig')
        a = full[full.index <= T]
        b = s2[s2.index <= T]
        cols = [k for k in ('d', 'stop', 'tgt_R', 'tp1_R', 'tp1_frac') if k in a.columns]
        if len(a) != len(b) or not a.index.equals(b.index):
            bad += 1
            print(f'  {inst} {T}: Anzahl {len(a)} vs {len(b)}')
            continue
        for k in cols:
            if not np.allclose(a[k].astype(float).fillna(-999).to_numpy(), b[k].astype(float).fillna(-999).to_numpy()):
                bad += 1
                print(f'  {inst} {T}: Spalte {k} weicht ab')
        # i_last fuer abgeschlossene Tage (Fensterende vor T)
        ta = x.index[a['i_last'].to_numpy()]
        tb = x2.index[np.minimum(b['i_last'].to_numpy(), len(x2) - 1)]
        done = ta < T
        if not (ta[done] == tb[done]).all():
            bad += 1
            print(f'  {inst} {T}: i_last weicht ab')
    return len(cuts), bad


if __name__ == '__main__':
    path = sys.argv[1]
    mod = load_mod(path)
    rule = getattr(mod, 'RULE', None)
    print(mod.NAME)
    for inst in mod.INSTRUMENTS:
        df = Q.load(inst, '2020-01-01', '2025-01-01')
        x = mod.prepare(df, inst)
        tr = qbt.trades_only(qbt.simulate(x, mod.signals(x, inst), inst))
        tr = tr[tr['t_entry'] < pd.Timestamp('2024-01-01')]
        ref = pd.read_parquet(os.path.join(HERE, 'out', f'trades_train_{inst}.parquet'))
        ref = ref[ref['rule'] == rule]
        same = len(tr) == len(ref) and np.allclose(tr['R'].to_numpy(), ref['R'].to_numpy())
        nc, bad = cut_test(mod, inst, df)
        print(f'{inst}: Trades Train {len(tr)} (Forschungslauf {len(ref)}) gleich={same}; Abschneide-Test {nc} Schnitte, Abweichungen {bad}')
