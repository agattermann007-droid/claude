"""Familie 'ausstiege': gemeinsame Hilfen.

- Nachzieh-Spalten, die nur an Halbstunden-Marken (10:00, 10:30, ... NY) aktualisiert werden und dazwischen den
  letzten Wert halten. Jeder Wert nutzt nur Daten bis zum Schluss seiner Kerze (UB/LB: Sigma aus Vortagen, Eroeffnung,
  Vortagesschluss; VWAP kumuliert bis zur Kerze). qbt nutzt an Kerze i den Wert der Vorkerze i-1.
- Simulation mit richtungsabhaengigem Nachzieh-Stop (Long max(UB,VWAP), Short min(LB,VWAP)): qbt erlaubt nur eine
  Nachzieh-Spalte je Lauf. Deshalb: Long- und Short-Signale getrennt mit qbt.simulate(seq=False) rechnen und danach
  exakt die Sequenzlogik von qbt (_sim, seq=True) nachstellen (Signal verfaellt, solange eine Position offen ist).
- Zellen mit Nullmodell (qbt.report_cell; bei zwei Nachzieh-Spalten Nullmodell je Spalte und gewichtet kombiniert).
- Teilziel-Trefferquote (TP1 vor Stop) ueber eine Begleitsimulation mit Ziel = TP1 auf denselben Trades.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, '..', '..', 'lib'))

import numpy as np
import pandas as pd

import qbt
import qdata as Q
import noise

FAMILIE = 'ausstiege'
TRAIL_COLS = ('tr_paperL', 'tr_paperS', 'tr_vwap')


# ---------------------------------------------------------------- Daten und Nachzieh-Spalten

def add_trails(x):
    """Nachzieh-Spalten, aktualisiert nur am Schluss der Halbstunden-Kerzen (m_close = 30, 60, ...)."""
    m = x['m_close']
    mark = (x['in_sess'] & (m >= 30) & (m % 30 == 0) & x['UB'].notna() & x['vwap'].notna()).to_numpy()
    ins = x['in_sess'].to_numpy()

    def col(v):
        s = pd.Series(np.where(mark, np.asarray(v, float), np.nan), index=x.index)
        s = s.groupby(x['sday'].to_numpy()).ffill()          # nur innerhalb des Sitzungstags weitertragen
        return s.where(ins)

    x['tr_paperL'] = col(np.maximum(x['UB'], x['vwap']))
    x['tr_paperS'] = col(np.minimum(x['LB'], x['vwap']))
    x['tr_vwap'] = col(x['vwap'])
    return x


def load(inst, eval_start=None, eval_end='2025-01-01'):
    a = eval_start or Q.dev_start(inst)
    df = Q.load(inst, a, eval_end)
    x = noise.prepare(df, inst)
    return add_trails(x)


def periods(inst):
    return {'Train': (str(Q.dev_start(inst).date()), '2024-01-01'), 'Val 2024': ('2024-01-01', '2025-01-01')}


# ---------------------------------------------------------------- Regeln

ENTRIES = {
    # noise-1.0-Einstieg: erstes Signal des Tages, SMA20-Trendfilter (Vortagesschluss gegen SMA20)
    'N10': dict(grid=30, trend='cprev', one_per_day=True),
    # Paper-Einstieg (Zarattini/Aziz/Barbon 2024): alle Halbstunden-Signale, Wiedereinstieg nach Ausstieg
    'PAPS': dict(grid=30, trend='cprev', one_per_day=False),    # mit SMA20-Filter
    'PAP0': dict(grid=30, trend='none', one_per_day=False),     # ohne Filter
}


def make_signals(x, entry, ex):
    """ex: dict(stop='mid'|'vwap'|'band', tgt=float|nan, time='T15'|'M480', trail=None|'paper'|'vwap',
    tp1=None|float (R), tp1_frac=0.5, be=False)."""
    sig = noise.signals(x, stop_mode=ex.get('stop', 'mid'), tgt_R=ex.get('tgt', np.nan), **ENTRIES[entry])
    sig['tgt_R'] = ex.get('tgt', np.nan)
    if ex.get('time', 'T15') == 'M480':
        sig['i_last'] = np.minimum(sig['i_sig'] + 96, len(x) - 1)
    tr = ex.get('trail')
    if tr == 'paper':
        sig['trail'] = np.where(sig['d'] > 0, 'tr_paperL', 'tr_paperS')
    elif tr == 'vwap':
        sig['trail'] = 'tr_vwap'
    if ex.get('tp1') is not None:
        sig['tp1_R'] = float(ex['tp1'])
        sig['tp1_frac'] = float(ex.get('tp1_frac', 0.5))
        sig['be_after_tp1'] = bool(ex.get('be', False))
    return sig


# ---------------------------------------------------------------- Simulation

def _n_trails(sig):
    return sig['trail'].dropna().nunique() if 'trail' in sig.columns else 0


def sim_free(x, sig, inst):
    """Jedes Signal unabhaengig (seq=False); bei mehreren Nachzieh-Spalten je Spalte getrennt."""
    if _n_trails(sig) <= 1:
        return qbt.simulate(x, sig, inst, seq=False)
    parts = [qbt.simulate(x, g, inst, seq=False) for _, g in sig.groupby('trail')]
    return pd.concat(parts).sort_values('i_sig', kind='stable').reset_index(drop=True)


def seq_filter(res):
    """Sequenzlogik aus qbt._sim (seq=True, Market-Einstieg) auf unabhaengig simulierte Signale anwenden."""
    res = res.sort_values('i_sig', kind='stable').reset_index(drop=True)
    code = res['code'].to_numpy().copy()
    busy = -1
    for k, (s, c, ex) in enumerate(zip(res['i_sig'].to_numpy(), res['code'].to_numpy(), res['i_exit'].to_numpy())):
        if s < busy:
            code[k] = -9
            continue
        if c == -9:
            continue
        if c == -8:
            busy = s + 2           # f = s + 1 -> busy_until = f + 1
            continue
        busy = ex + 1
    res['code'] = code
    return res


def run(x, sig, inst):
    """Trades einer Regel (eine Position je Regel und Instrument)."""
    if _n_trails(sig) <= 1:
        res = qbt.simulate(x, sig, inst)
    else:
        res = seq_filter(sim_free(x, sig, inst))
    return qbt.trades_only(res)


def tp1_hits(x, tr, inst):
    """TP1 vor Stop: Begleitsimulation der genommenen Trades mit Ziel = TP1 (volle Position, gleicher Stop/Nachzug)."""
    if len(tr) == 0 or 'tp1_R' not in tr.columns:
        return pd.Series(dtype=float)
    cols = [c for c in ('i_sig', 'd', 'stop', 'i_last', 'kind', 'trail') if c in tr.columns]
    comp = tr[cols].copy()
    comp['tgt_R'] = tr['tp1_R'].to_numpy()
    r = sim_free(x, comp, inst)
    r = r.set_index('i_sig')['code']
    return r.reindex(tr['i_sig'].to_numpy())


# ---------------------------------------------------------------- Zellen mit Nullmodell

def _combine_null(parts):
    parts = [p for p in parts if p.get('n', 0) > 0]
    if not parts:
        return dict(n=0)
    n = sum(p['n'] for p in parts)
    hs = [p['n'] * (1 - p['time_exit']) for p in parts]
    hits = sum(p['tvs'] * h for p, h in zip(parts, hs))
    return dict(n=n, R=sum(p['n'] * p['R'] for p in parts) / n, win=sum(p['n'] * p['win'] for p in parts) / n,
                tvs=hits / max(sum(hs), 1))


def cell(x, tr, pers, K=20, seed=7):
    """Wie qbt.report_cell; bei zwei Nachzieh-Spalten Nullmodell je Spalte (Long/Short) und kombiniert."""
    if _n_trails(tr) <= 1:
        return qbt.report_cell(x, tr, pers, K=K, seed=seed)
    rows = []
    for name, (a, b) in pers.items():
        a, b = pd.Timestamp(a), pd.Timestamp(b)
        xx = tr[(tr['t_entry'] >= a) & (tr['t_entry'] < b)]
        sub = x[(x.index >= a) & (x.index < b)]
        nd = qbt.n_trading_days(sub.assign()) if len(sub) else 0
        s = qbt.summarize(xx, nd)
        if s['n'] > 0:
            nm = _combine_null([qbt.null_model(x, g, K=K, seed=seed, a=a, b=b) for _, g in xx.groupby('trail')])
        else:
            nm = dict(n=0)
        s.update({'null_tvs': nm.get('tvs', np.nan), 'null_win': nm.get('win', np.nan), 'null_R': nm.get('R', np.nan)})
        if s['n'] > 1:
            sd = qbt.trades_only(xx)['R'].std(ddof=1)
            s['t_vs_null'] = (s['R'] - s['null_R']) / (sd / np.sqrt(s['n']))
        rows.append(pd.Series(s, name=name))
    return pd.DataFrame(rows)
