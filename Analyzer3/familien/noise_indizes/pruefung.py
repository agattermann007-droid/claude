"""Pruefung der Kandidaten (nur Train-Daten):
1) Kandidatenmodul (prepare -> signals -> qbt.simulate wie locked_run) liefert dieselben Trades wie der Forschungslauf (trades_train.csv).
2) Abschneide-Test: signals auf df bis T liefert fuer alle Signalkerzen bis T dieselben Signale (d, stop, Ziel, Teilziel);
   i_last (Zeitausstieg) wird nur fuer Tage vor dem Tag von T verglichen (am laufenden Tag ist das Sitzungsende noch nicht in den Daten).
3) Startpunkt-Test: Laden ab Auswertungsbeginn - 90 Tage (wie locked_run) gibt im Auswertungsbereich dieselben Signale wie ab dev-Start.
Aufruf: python3 -W ignore pruefung.py
"""
import glob
import importlib.util
import os
import sys

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(HIER, "..", "..", "lib"))
import qbt  # noqa: E402
import qdata as Q  # noqa: E402

FIELDS = ['d', 'stop', 'tgt_R', 'tp1_R', 'tp1_frac', 'be_after_tp1']


def lade(f):
    spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def keyed(x, sig):
    s = sig.copy()
    s['t'] = x.index[s['i_sig'].to_numpy()]
    s['t_last'] = x.index[s['i_last'].to_numpy()]
    s['day'] = x['sday'].to_numpy()[s['i_sig'].to_numpy()]
    return s.set_index('t')


def same(a, b):
    if not a.index.equals(b.index):
        return False
    ok = True
    for c in [c for c in FIELDS if c in a.columns]:
        u, v = a[c].to_numpy(), b[c].to_numpy()
        ok &= np.allclose(u.astype(float), v.astype(float), equal_nan=True)
    return bool(ok)


def main():
    ref = pd.read_csv(os.path.join(HIER, 'trades_train.csv'), parse_dates=['t_entry'])
    for f in sorted(glob.glob(os.path.join(HIER, 'kandidat_*.py'))):
        mod = lade(f)
        print(f'\n== {os.path.basename(f)}  {mod.INSTRUMENTS}')
        for inst in mod.INSTRUMENTS:
            df = Q.load(inst, Q.dev_start(inst), '2024-01-01')
            x = mod.prepare(df, inst)
            sig = mod.signals(x, inst)
            tr = qbt.trades_only(qbt.simulate(x, sig, inst))
            tr = tr[tr['t_entry'] >= Q.dev_start(inst)]
            rr = ref[(ref.inst == inst) & (ref.rule == mod.RULE)]
            ok1 = len(tr) == len(rr) and np.array_equal(tr['t_entry'].to_numpy(), rr['t_entry'].to_numpy()) and \
                np.allclose(tr['R'].to_numpy(), rr['R'].to_numpy())
            # 2) Abschneide-Test
            full = keyed(x, sig)
            rng = np.random.default_rng(3)
            cand = full.index[full.index >= pd.Timestamp('2021-06-01')]
            ts = list(rng.choice(cand, 5, replace=False))
            ins = x.index[x['in_sess'] & (x.index >= pd.Timestamp('2021-06-01'))]
            ts += list(rng.choice(ins, 5, replace=False))
            bad = []
            for T in sorted(ts):
                T = pd.Timestamp(T)
                dT = df[df.index <= T].copy()
                dT.attrs.update(df.attrs)
                xT = mod.prepare(dT, inst)
                sT = keyed(xT, mod.signals(xT, inst))
                a = full[full.index <= T]
                ok = same(a, sT)
                dayT = xT['sday'].iloc[-1]
                pa, pb = a[a['day'] < dayT], sT[sT['day'] < dayT]
                ok &= bool((pa['t_last'] == pb['t_last']).all()) if len(pa) == len(pb) else False
                if not ok:
                    bad.append(str(T))
            # 3) Startpunkt-Test (Auswertung 2023, Vorlauf 90 Tage wie locked_run)
            d2 = Q.load(inst, '2023-01-01', '2024-01-01', warmup_days=90)
            x2 = mod.prepare(d2, inst)
            s2 = keyed(x2, mod.signals(x2, inst))
            f2 = full[(full.index >= pd.Timestamp('2023-01-01'))]
            s2 = s2[s2.index >= pd.Timestamp('2023-01-01')]
            ok3 = same(f2, s2) and bool((f2['t_last'] == s2['t_last']).all())
            print(f'  {inst:7s} Trades = Forschungslauf: {ok1} (n {len(tr)}/{len(rr)}) | Abschneide-Test 10 Zeitpunkte: '
                  f'{"ok" if not bad else "FEHLER " + str(bad)} | Start -90 Tage gleich: {ok3}')


if __name__ == '__main__':
    main()
