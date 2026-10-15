"""Laeufe der Familie 'ausstiege'.

Aufruf:  python3 -W ignore run.py train NAS100 US500     (nur Train, Daten bis 2023-12-31)
         python3 -W ignore run.py val NAS100 US500       (Val 2024, einmalig nach der Auswahl auf Train)
Schreibt ergebnis_<phase>.csv und protokolliert jede Variante im Ledger.
"""
import json
import os
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)

import numpy as np
import pandas as pd

import common as C
import ledger
import varianten as V

# v2: Lauf mit qdata ohne Vorlauf-Kerzen vor dev_start (Aenderung in lib/qdata.py um 19:15); v1-Zeilen im Ledger
# stammen aus dem Lauf davor (Vorlauf 60 Tage vor dev_start) und sind ueberholt.
# v3: Lauf auf korrigierten Kerzendateien (ts4-Uhr zeitweise 1 h daneben, US500 2020-03-08..2020-11-01 und 2021-03-14..04-09,
# NAS100 2021-03-14..04-08). v1/v2-Zeilen sind ueberholt.
NOTE = 'v3'


def hit_metric(ex, s, tp1vs):
    if not np.isnan(ex.get('tgt', np.nan)):
        return s['tvs'], 'Target vor Stop'
    if ex.get('tp1') is not None:
        return tp1vs, 'Teilziel vor Stop'
    return s['win'], 'Gewinnquote'


def run_inst(inst, phase, log=True):
    pers = C.periods(inst)
    per = {'Train': pers['Train']} if phase == 'train' else {'Val 2024': pers['Val 2024']}
    x = C.load(inst, eval_end='2024-01-01' if phase == 'train' else '2025-01-01')
    rows = []
    for entry, exn, ex in V.VARIANTS:
        t0 = time.time()
        sig = C.make_signals(x, entry, ex)
        tr = C.run(x, sig, inst)
        tab = C.cell(x, tr, per)
        (pname, (a, b)), = per.items()
        trp = tr[(tr['t_entry'] >= pd.Timestamp(a)) & (tr['t_entry'] < pd.Timestamp(b))]
        tp1vs = np.nan
        if ex.get('tp1') is not None and len(trp):
            codes = C.tp1_hits(x, trp, inst)
            tp1vs = (codes == 1).sum() / max(((codes == 1) | (codes == -1)).sum(), 1)
        s = tab.loc[pname]
        hit, art = hit_metric(ex, s, tp1vs)
        name = f'{inst}|{V.label(entry, exn)}'
        if log:
            ledger.log_variant(C.FAMILIE, name, dict(inst=inst, entry=entry, **{k: v for k, v in ex.items()}), tab,
                               note=NOTE + (f' tp1vs={tp1vs:.4f}' if not np.isnan(tp1vs) else ''))
        r = dict(inst=inst, variante=V.label(entry, exn), entry=entry, exit=exn, periode=pname,
                 has_target=V.has_target(ex), trefferquote=hit, art_trefferquote=art, tp1vs=tp1vs,
                 R_pro_tag=s['R'] * s['per_day'])
        r.update({k: s.get(k, np.nan) for k in ['n', 'per_day', 'tvs', 'win', 'R', 't', 't_day', 'time_exit',
                                                 'null_tvs', 'null_win', 'null_R', 't_vs_null']})
        rows.append(r)
        print(f"{name:28s} n {int(s['n']):4d} /Tag {s['per_day']:.2f} TvS {s['tvs']:.3f} win {s['win']:.3f} "
              f"hit {hit:.3f} R {s['R']:+.3f} t {s['t']:.2f} tday {s['t_day']:.2f} nullR {s['null_R']:+.3f} "
              f"tvn {s.get('t_vs_null', np.nan):.2f} R/Tag {r['R_pro_tag']:+.3f} ({time.time() - t0:.0f}s)", flush=True)
    return rows


if __name__ == '__main__':
    phase = sys.argv[1]
    insts = sys.argv[2:] or ['NAS100']
    out = []
    for inst in insts:
        out += run_inst(inst, phase)
    f = os.path.join(HIER, f'ergebnis_{phase}.csv')
    pd.DataFrame(out).to_csv(f, index=False)
    print('geschrieben', f)
