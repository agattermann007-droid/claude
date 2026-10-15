"""Familie noise_rohstoffe: Sitzungen, Noise-Area-Regeln und 'market intraday momentum' (MIM) fuer
Rohstoffe, BTC und FX. Vorab-Festlegung in PLAN.md. Nur Daten bis zur Signalkerze; i_last (Zeitausstieg
am Fensterende) ist wie bei noise-1.0 ein Index in die Zukunft, aber nur eine Uhrzeit.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import noise  # noqa: E402

NY, LDN = 'America/New_York', 'Europe/London'
# (tz, Eroeffnung, Sitzungsschluss, Fensterende = Zeitausstieg)
SESS = {
    'XAUUSD': (NY, (8, 20), (13, 30), (13, 30)),
    'XAGUSD': (NY, (8, 20), (13, 30), (13, 30)),
    'WTI': (NY, (9, 0), (14, 30), (14, 30)),
    'BRENT': (LDN, (8, 0), (16, 30), (16, 30)),
    'BTCUSD': (NY, (9, 30), (16, 0), (15, 0)),
    'ETHUSD': (NY, (9, 30), (16, 0), (15, 0)),
    **{fx: (LDN, (8, 0), (16, 0), (16, 0)) for fx in ('EURUSD', 'GBPUSD', 'AUDUSD', 'USDCAD', 'USDCHF')},
}
INSTS = ['XAUUSD', 'XAGUSD', 'WTI', 'BRENT', 'BTCUSD', 'EURUSD', 'GBPUSD', 'AUDUSD', 'USDCAD', 'USDCHF']
CHECK = ['ETHUSD']


def prepare(df, inst):
    """Noise-Area auf der Instrument-Sitzung plus MIM-Merkmale."""
    x = noise.prepare(df, inst, sess=SESS[inst])
    x.attrs['inst'] = inst
    return x


# ------------------------------------------------------------------ Noise-Area-Regeln

def sig_n10(x, mode='end'):
    """noise-1.0 unveraendert; mode 'end' = Zeitausstieg Fensterende, '480' = i_sig + 96 Kerzen."""
    sig = noise.signals(x, grid=30, trend='cprev', one_per_day=True, stop_mode='mid', tgt_R=1.0)
    if mode == '480':   # Uhrzeit statt 96 Kerzen (Korrektur lib/noise.py: kein Halten uebers Wochenende)
        sig['i_last'] = noise.last_by_clock(x, sig['i_sig'], 480)
    return sig


def sig_paps_b(x):
    """Kandidat B der Familie ausstiege, Zeitausstieg Fensterende."""
    sig = noise.signals(x, grid=30, trend='cprev', one_per_day=False, stop_mode='mid', tgt_R=np.nan)
    sig['tgt_R'] = np.nan
    sig['tp1_R'] = 0.5
    sig['tp1_frac'] = 0.5
    sig['be_after_tp1'] = True
    return sig


# ------------------------------------------------------------------ MIM

def _bar_at(x, ok, end_min):
    """Je Sitzungstag: Position der Kerze, deren Schluss genau bei end_min (Minuten seit Mitternacht, Ortszeit) liegt."""
    m = ok & (x['m_bar'].to_numpy() + 5 == end_min)
    pos = np.flatnonzero(m)
    return pd.Series(pos, index=x['sday'].to_numpy()[pos]).groupby(level=0).first()


def mim_frame(x, H=30, lookback=14):
    """Je Sitzungstag: Positionen und Kurse fuer r1, r12, Rest-des-Tages und sigma_H (nur Vergangenheit)."""
    tz, op, cl, ex = SESS[x.attrs['inst']]
    om, em = op[0] * 60 + op[1], ex[0] * 60 + ex[1]
    ok = x['in_sess'].to_numpy()
    c = x['c'].to_numpy(float)
    i30 = _bar_at(x, ok, om + 30)
    isig = _bar_at(x, ok, em - H)
    isig30 = _bar_at(x, ok, em - 30)
    i60 = _bar_at(x, ok, em - 60)
    iend = _bar_at(x, ok, em)
    days = pd.Index(sorted(set(x.loc[x['in_sess'], 'sday'])))
    f = pd.DataFrame(index=days)
    f['i30'], f['isig'], f['isig30'], f['i60'], f['iend'] = i30, isig, isig30, i60, iend
    cprev = x.loc[x['in_sess']].groupby('sday')['Cprev'].first()
    f['Cprev'] = cprev
    cc = lambda col: pd.Series(np.where(f[col].notna(), c[f[col].fillna(0).astype(int)], np.nan), index=f.index)
    f['c30'], f['csig'], f['csig30'], f['c60'], f['cend'] = cc('i30'), cc('isig'), cc('isig30'), cc('i60'), cc('iend')
    f['r1'] = f['c30'] / f['Cprev'] - 1
    f['r12'] = f['csig30'] / f['c60'] - 1
    f['rod'] = f['csig30'] / f['Cprev'] - 1
    hold = (f['cend'] / f['csig'] - 1).abs()
    f['sigma_H'] = hold.rolling(lookback, min_periods=10).mean().shift(1)
    # Zeitausstieg: letzte Kerze mit Schluss <= Fensterende (wie noise.last_bar_index)
    okl = ok & (x['m_bar'].to_numpy() + 5 <= em)
    pl = np.flatnonzero(okl)
    f['ilast'] = pd.Series(pl, index=x['sday'].to_numpy()[pl]).groupby(level=0).max()
    return f


def sig_mim(x, pred='r1', H=30, tgt_R=np.nan, tp1=False, hv=False):
    """MIM: Richtung = Vorzeichen des Praediktors, Einstieg Fensterende - H (Market zur naechsten Eroeffnung),
    Stop = sigma_H, Ziel tgt_R (NaN = kein Ziel), Zeitausstieg Fensterende.
    pred: 'r1' (Vortagesschluss -> Eroeffnung+30), 'r1r12' (beide gleiches Vorzeichen), 'rod' (Vortagesschluss -> Ende-30)."""
    f = mim_frame(x, H=H)
    if pred == 'r1':
        d = np.sign(f['r1'])
    elif pred == 'r1r12':
        d = np.where((f['r1'] > 0) & (f['r12'] > 0), 1, np.where((f['r1'] < 0) & (f['r12'] < 0), -1, 0))
        d = pd.Series(d, index=f.index).where(f['r1'].notna() & f['r12'].notna())
    elif pred == 'rod':
        d = np.sign(f['rod'])
    else:
        raise ValueError(pred)
    f['d'] = d
    if hv:   # nur Tage mit |r1| ueber dem Mittel der letzten 14 Sitzungen (ohne heute)
        a1 = f['r1'].abs()
        f.loc[~(a1 > a1.rolling(14, min_periods=10).mean().shift(1)), 'd'] = 0
    g = f[f['d'].notna() & (f['d'] != 0) & f['isig'].notna() & f['sigma_H'].notna() & f['ilast'].notna()
          & (f['sigma_H'] > 0)].copy()
    # kein Filter ilast > isig: auf abgeschnittenen Daten ist das Fensterende noch nicht da (qbt markiert solche Faelle als -8)
    sig = pd.DataFrame({'i_sig': g['isig'].astype(np.int64).to_numpy(), 'd': g['d'].astype(np.int64).to_numpy(),
                        'sday': g.index.to_numpy()})
    sig['stop'] = g['csig'].to_numpy() * (1 - sig['d'].to_numpy() * g['sigma_H'].to_numpy())
    sig['tgt_R'] = tgt_R
    sig['i_last'] = g['ilast'].astype(np.int64).to_numpy()
    sig['kind'] = 'market'
    if tp1:
        sig['tgt_R'] = np.nan
        sig['tp1_R'] = 0.5
        sig['tp1_frac'] = 0.5
        sig['be_after_tp1'] = True
    return sig.reset_index(drop=True)


RULES = {
    'N10_end': (lambda x: sig_n10(x, 'end'), 'Target vor Stop'),
    'N10_480': (lambda x: sig_n10(x, '480'), 'Target vor Stop'),
    'PAPS_B': (sig_paps_b, 'Teilziel vor Stop'),
    'MIM_r1_none': (lambda x: sig_mim(x, 'r1', 30), 'Gewinnquote'),
    'MIM_r1_t10': (lambda x: sig_mim(x, 'r1', 30, 1.0), 'Target vor Stop'),
    'MIM_r1_t05': (lambda x: sig_mim(x, 'r1', 30, 0.5), 'Target vor Stop'),
    'MIM_r1_B': (lambda x: sig_mim(x, 'r1', 30, tp1=True), 'Teilziel vor Stop'),
    'MIM_r1r12_none': (lambda x: sig_mim(x, 'r1r12', 30), 'Gewinnquote'),
    'MIM_rod_none': (lambda x: sig_mim(x, 'rod', 30), 'Gewinnquote'),
    'MIM60_r1_none': (lambda x: sig_mim(x, 'r1', 60), 'Gewinnquote'),
    'MIM_r1_hv_none': (lambda x: sig_mim(x, 'r1', 30, hv=True), 'Gewinnquote'),   # Nachtrag nach Train-Lauf 1
}
