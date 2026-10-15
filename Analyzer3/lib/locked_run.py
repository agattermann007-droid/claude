"""Gesperrter Test: laeuft genau einmal.

Voraussetzungen:
  - ergebnisse/KRITERIEN_GESPERRT.md existiert und enthaelt einen ```json-Block mit Kandidaten, Zeitraeumen und Schwellen.
  - ergebnisse/gesperrt/LAUF.json existiert noch NICHT (sonst Abbruch: der Test ist verbraucht).
Ablauf: Pruefsumme der Kriterien festhalten -> Sperre oeffnen -> alle Kandidaten rechnen -> Sperre schliessen ->
Ergebnisse und Bewertung nach ergebnisse/gesperrt/ schreiben.

Aufruf: python3 locked_run.py
"""
import hashlib
import importlib.util
import json
import os
import re
import sys
import traceback

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import qbt
import qdata as Q

ROOT = os.path.join(HIER, '..')
KRIT = os.path.join(ROOT, 'ergebnisse', 'KRITERIEN_GESPERRT.md')
OUT = os.path.join(ROOT, 'ergebnisse', 'gesperrt')


def lade_kandidat(pfad):
    spec = importlib.util.spec_from_file_location(os.path.basename(pfad)[:-3], pfad)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(pfad))
    spec.loader.exec_module(m)
    return m


def main():
    if not os.path.exists(KRIT):
        sys.exit('Kriteriendatei fehlt: ' + KRIT)
    os.makedirs(OUT, exist_ok=True)
    lauf = os.path.join(OUT, 'LAUF.json')
    if os.path.exists(lauf):
        sys.exit('Gesperrter Test wurde bereits ausgefuehrt (' + lauf + '). Kein zweiter Lauf.')
    txt = open(KRIT, encoding='utf-8').read()
    sha = hashlib.sha256(txt.encode()).hexdigest()
    cfg = json.loads(re.search(r'```json\n(.*?)\n```', txt, re.S).group(1))
    meta = {'kriterien_sha256': sha, 'start': pd.Timestamp.utcnow().isoformat(), 'kandidaten': [k['name'] for k in cfg['kandidaten']]}
    json.dump(meta, open(lauf, 'w'), indent=1)
    open(Q.LOCKFILE, 'w').write(sha)
    rows, alle = [], []
    try:
        for k in cfg['kandidaten']:
            mod = lade_kandidat(os.path.join(ROOT, k['modul']))
            for inst in k['instrumente']:
                for per in k['zeitraeume']:
                    a, b = per['von'], per['bis']
                    try:
                        df = Q.load(inst, a, b, warmup_days=90)
                    except Exception as e:
                        rows.append({'kandidat': k['name'], 'inst': inst, 'zeitraum': per['name'], 'fehler': str(e)})
                        continue
                    ev = df[(df.index >= pd.Timestamp(a)) & (df.index < pd.Timestamp(b))]
                    if len(ev) < 1000:
                        rows.append({'kandidat': k['name'], 'inst': inst, 'zeitraum': per['name'], 'fehler': 'keine/zu wenige Daten'})
                        continue
                    x = mod.prepare(df, inst)
                    sig = mod.signals(x, inst)
                    res = qbt.simulate(x, sig, inst)
                    tr = qbt.trades_only(res)
                    tr = tr[(tr['t_entry'] >= pd.Timestamp(a)) & (tr['t_entry'] < pd.Timestamp(b))]
                    cell = qbt.report_cell(x, tr, {per['name']: (a, b)}, K=20, seed=11)
                    r = cell.iloc[0].to_dict()
                    r.update({'kandidat': k['name'], 'inst': inst, 'zeitraum': per['name'],
                              'erster_tag': str(ev.index[0].date()), 'letzter_tag': str(ev.index[-1].date())})
                    rows.append(r)
                    t2 = tr.copy()
                    t2['kandidat'] = k['name']
                    t2['zeitraum'] = per['name']
                    alle.append(t2[['kandidat', 'inst', 'zeitraum', 't_sig', 't_entry', 't_exit', 'd', 'E', 'stop', 'X', 'R_gross', 'R', 'code']])
    except Exception:
        traceback.print_exc()
    finally:
        if os.path.exists(Q.LOCKFILE):
            os.remove(Q.LOCKFILE)
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(OUT, 'zellen.csv'), index=False)
    if alle:
        pd.concat(alle).to_csv(os.path.join(OUT, 'trades.csv'), index=False)
    meta['ende'] = pd.Timestamp.utcnow().isoformat()
    json.dump(meta, open(lauf, 'w'), indent=1)
    pd.set_option('display.width', 250)
    print(res.round(3).to_string())


if __name__ == '__main__':
    main()
