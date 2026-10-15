"""Varianten-Zaehlung: jede getestete Variante (auch verworfene) wird mit Kennzahlen protokolliert."""
import csv, json, os, time
import pandas as pd

LEDGER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ergebnisse', 'varianten')


def log_variant(family, name, params, table, note=''):
    """table: DataFrame aus qbt.report_cell (Index = Zeitraum). Schreibt eine Zeile je Zeitraum."""
    os.makedirs(LEDGER_DIR, exist_ok=True)
    f = os.path.join(LEDGER_DIR, f'{family}.csv')
    new = not os.path.exists(f)
    with open(f, 'a', newline='') as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(['family', 'variant', 'params', 'period', 'n', 'per_day', 'tvs', 'win', 'R', 't', 'null_tvs', 'null_R', 't_vs_null', 'note'])
        for per, r in table.iterrows():
            w.writerow([family, name, json.dumps(params, sort_keys=True, default=str), per] +
                       [r.get(k) for k in ['n', 'per_day', 'tvs', 'win', 'R', 't', 'null_tvs', 'null_R', 't_vs_null']] + [note])


def count(family=None):
    fs = [os.path.join(LEDGER_DIR, x) for x in os.listdir(LEDGER_DIR)] if os.path.isdir(LEDGER_DIR) else []
    d = pd.concat([pd.read_csv(f) for f in fs]) if fs else pd.DataFrame()
    if family is not None and len(d):
        d = d[d.family == family]
    return d.groupby('family')['variant'].nunique() if len(d) else d
