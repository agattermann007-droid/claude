"""Gesperrter Test: laeuft genau einmal.

Voraussetzungen:
  - ergebnisse/KRITERIEN_GESPERRT.md existiert und enthaelt einen ```json-Block (Kandidaten, Zeitraeume, Schwellen).
  - ergebnisse/gesperrt/LAUF.json existiert noch NICHT (sonst Abbruch: der Test ist verbraucht).
Ablauf: Pruefsumme der Kriterien festhalten -> Sperre oeffnen -> alle Kandidaten rechnen (Hauptregel und vorab
festgelegte Zielvarianten fuer die Trade-off-Kurve) -> Sperre schliessen -> Bewertung nach ergebnisse/gesperrt/.

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


def tage_t(tr):
    """Tages-Cluster-t ueber alle Instrumente (Summe R je NY-Tag)."""
    if len(tr) < 3:
        return np.nan
    day = Q.server_to_ny(pd.DatetimeIndex(tr['t_entry'])).normalize()
    s = pd.Series(tr['R'].to_numpy(), index=day).groupby(level=0).sum()
    return s.mean() / (s.std(ddof=1) / np.sqrt(len(s))) if len(s) > 2 and s.std(ddof=1) > 0 else np.nan


TROCKEN = False


def zeitraum(inst, a, b):
    """'DEV_START' als Grenze = Beginn der Entwicklungsdaten dieses Instruments (gesperrter Vorzeitraum endet dort).
    Im Trockenlauf wird der Beginn auf dev_start gekappt (gesperrte Kerzen bleiben zu)."""
    a = Q.dev_start(inst) if a == 'DEV_START' else pd.Timestamp(a)
    b = Q.dev_start(inst) if b == 'DEV_START' else pd.Timestamp(b)
    if TROCKEN:
        a = max(a, Q.dev_start(inst))
    return a, b


def rechne(mod, inst, a, b, override=None):
    a, b = zeitraum(inst, a, b)
    df = Q.load(inst, a, b, warmup_days=90)
    ev = df[(df.index >= pd.Timestamp(a)) & (df.index < pd.Timestamp(b))]
    if len(ev) < 1000:
        return None, None, None
    x = mod.prepare(df, inst)
    sig = mod.signals(x, inst)
    if override is not None and len(sig):
        sig = sig.copy()
        sig['tgt_R'] = override
        if 'tgt_abs' in sig.columns:
            sig['tgt_abs'] = np.nan
    res = qbt.simulate(x, sig, inst)
    tr = qbt.trades_only(res)
    tr = tr[(tr['t_entry'] >= pd.Timestamp(a)) & (tr['t_entry'] < pd.Timestamp(b))]
    return x, tr, ev


def main():
    global KRIT, OUT, TROCKEN
    trocken = TROCKEN = '--trocken' in sys.argv
    if trocken:   # Probelauf auf dev-Daten: eigene Kriteriendatei, keine Sperre oeffnen
        KRIT = sys.argv[sys.argv.index('--trocken') + 1]
        OUT = os.path.join(ROOT, 'ergebnisse', 'trocken')
        os.makedirs(OUT, exist_ok=True)
        for f in os.listdir(OUT):
            os.remove(os.path.join(OUT, f))
    if not os.path.exists(KRIT):
        sys.exit('Kriteriendatei fehlt: ' + KRIT)
    os.makedirs(OUT, exist_ok=True)
    lauf = os.path.join(OUT, 'LAUF.json')
    if os.path.exists(lauf):
        sys.exit('Gesperrter Test wurde bereits ausgefuehrt (' + lauf + '). Kein zweiter Lauf.')
    txt = open(KRIT, encoding='utf-8').read()
    sha = hashlib.sha256(txt.encode()).hexdigest()
    cfg = json.loads(re.search(r'```json\n(.*?)\n```', txt, re.S).group(1))
    S = cfg['schwellen']
    meta = {'kriterien_sha256': sha, 'start': pd.Timestamp.now('UTC').isoformat(), 'kandidaten': [k['name'] for k in cfg['kandidaten']]}
    json.dump(meta, open(lauf, 'w'), indent=1)
    if not trocken:
        open(Q.LOCKFILE, 'w').write(sha)
    zellen, alle, kurve, urteil = [], [], [], []
    try:
        for k in cfg['kandidaten']:
            mod = lade_kandidat(os.path.join(ROOT, k['modul']))
            tr_k = {}
            for per in k['zeitraeume']:
                name, a, b = per['name'], per['von'], per['bis']
                insts = per.get('instrumente', k['instrumente'])
                tr_p = []
                for inst in insts:
                    try:
                        x, tr, ev = rechne(mod, inst, a, b)
                    except Exception as e:
                        zellen.append({'kandidat': k['name'], 'inst': inst, 'zeitraum': name, 'fehler': repr(e)[:300]})
                        continue
                    if tr is None:
                        zellen.append({'kandidat': k['name'], 'inst': inst, 'zeitraum': name, 'fehler': 'keine/zu wenige Daten'})
                        continue
                    a_i, b_i = zeitraum(inst, a, b)
                    cell = qbt.report_cell(x, tr, {name: (a_i, b_i)}, K=100, seed=11).iloc[0].to_dict()
                    cell.update({'kandidat': k['name'], 'inst': inst, 'zeitraum': name,
                                 'erster_tag': str(ev.index[0].date()), 'letzter_tag': str(ev.index[-1].date())})
                    zellen.append(cell)
                    t2 = tr.copy()
                    t2['kandidat'], t2['zeitraum'] = k['name'], name
                    # Nullmodell-R je Trade-Zelle mitschreiben (fuer gepoolten Vergleich)
                    t2['null_R_zelle'] = cell.get('null_R', np.nan)
                    tr_p.append(t2)
                    for ov in k.get('kurve', []):
                        try:
                            _, tk, _ = rechne(mod, inst, a, b, override=(np.nan if ov is None else float(ov)))
                            s = qbt.summarize(tk)
                            kurve.append({'kandidat': k['name'], 'inst': inst, 'zeitraum': name, 'ziel_R': ov,
                                          'n': s['n'], 'tvs': s['tvs'], 'win': s['win'], 'R': s['R']})
                        except Exception as e:
                            kurve.append({'kandidat': k['name'], 'inst': inst, 'zeitraum': name, 'ziel_R': ov, 'fehler': repr(e)[:200]})
                if tr_p:
                    tr_k[name] = pd.concat(tr_p)
                    alle.append(tr_k[name])
            # Bewertung je Kandidat
            u = {'kandidat': k['name']}
            for name, t in tr_k.items():
                u[f'{name}_n'] = len(t)
                u[f'{name}_R'] = t['R'].mean() if len(t) else np.nan
                u[f'{name}_tvs'] = ((t.code == 1).sum() / max(((t.code == 1) | (t.code == -1)).sum(), 1)) if len(t) else np.nan
                u[f'{name}_t_tag'] = tage_t(t)
                u[f'{name}_null_R'] = np.average(t['null_R_zelle'].fillna(0)) if len(t) else np.nan
            pool = pd.concat(tr_k.values()) if tr_k else pd.DataFrame()
            if len(pool):
                R = pool['R'].to_numpy()
                sd = R.std(ddof=1)
                nullR = np.average(pool['null_R_zelle'].fillna(0))
                u.update({'pool_n': len(pool), 'pool_R': R.mean(), 'pool_t_tag': tage_t(pool),
                          'pool_null_R': nullR, 'pool_t_vs_null': (R.mean() - nullR) / (sd / np.sqrt(len(R)))})
                k1 = u['pool_R'] > 0 and u['pool_t_tag'] >= S['t_pool_min']
                k2 = u['pool_t_vs_null'] >= S['t_vs_null_min']
                k3 = all(u.get(f'{n}_R', -1) > 0 for n in S['muss_positiv'])
                u.update({'K1': k1, 'K2': k2, 'K3': k3,
                          'urteil': 'bestanden' if (k1 and k2 and k3) else ('bestanden mit Vorbehalt' if (k1 and k2) else 'nicht bestanden')})
            else:
                u['urteil'] = 'keine Daten'
            urteil.append(u)
    except Exception:
        traceback.print_exc()
    finally:
        if not trocken and os.path.exists(Q.LOCKFILE):
            os.remove(Q.LOCKFILE)
    pd.DataFrame(zellen).to_csv(os.path.join(OUT, 'zellen.csv'), index=False)
    pd.DataFrame(kurve).to_csv(os.path.join(OUT, 'kurve.csv'), index=False)
    pd.DataFrame(urteil).to_csv(os.path.join(OUT, 'urteil.csv'), index=False)
    if alle:
        cols = ['kandidat', 'inst', 'zeitraum', 't_sig', 't_entry', 't_exit', 'd', 'E', 'stop', 'X', 'R_gross', 'R', 'code']
        pd.concat(alle)[cols].to_csv(os.path.join(OUT, 'trades.csv'), index=False)
    meta['ende'] = pd.Timestamp.now('UTC').isoformat()
    json.dump(meta, open(lauf, 'w'), indent=1)
    pd.set_option('display.width', 250)
    print(pd.DataFrame(urteil).round(3).to_string())


if __name__ == '__main__':
    main()
