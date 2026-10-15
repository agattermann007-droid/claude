"""Familie 'ereignisse': Literaturregeln um geplante Ereignisse als Daytrades.

Aufruf:  python3 -W ignore run.py train   -> nur Train (dev-Start .. 2023-12-31), Ledger-Notiz 'train'
         python3 -W ignore run.py val     -> nur Val 2024 (einmal), Ledger-Notiz 'val'
Geometrie: Stop = k x sigma_F (RMS der Fensterrendite der letzten 20 Handelstage), Ziele 0,5 / 1 / 2 R / kein Ziel.
k = 1, ausser Fenstern direkt nach dem FOMC-Statement (k = 3: dort ist die Fenster-Volatilitaet auf Train ~3 x normal,
d. h. 1 x sigma der gleichartigen Ereignisfenster ~ 3 x sigma der Normalfenster).
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import ev  # noqa: E402
import qdata as Q  # noqa: E402
import qbt  # noqa: E402
import ledger  # noqa: E402

FAM = 'ereignisse'
TARGETS = [0.5, 1.0, 2.0, np.nan]
IDX = ['NAS100', 'US500']
FX = ['XAUUSD', 'EURUSD', 'GBPUSD', 'AUDUSD', 'USDCAD', 'USDCHF']
OIL = ['WTI', 'BRENT']
NOTE = 'v2'   # Daten nach Uhrkorrektur (Neubau 15.10.2026 ~20:2x)

# name: (Ereignis, Instrumente, Fenster (start, ende) NY-Minuten, Richtung, k, Quelle)
#   Richtung: 'long' | ('cont'|'rev', a, b) = Vorzeichen der Rendite a->b fortsetzen bzw. umkehren
RULES = {
    'PF930': ('fomc', IDX, (570, 835), 'long', 1.0,
              'Lucca/Moench 2015 JF: Pre-FOMC-Drift; Long 9:30-13:55 am Statement-Tag'),
    'PF1000': ('fomc', IDX, (600, 835), 'long', 1.0,
               'Lucca/Moench 2015 JF: Pre-FOMC-Drift; Long 10:00-13:55'),
    'RELIEF_SEP': ('fomc_sep', IDX, (835, 895), 'long', 3.0,
                   'Gu/Kurov/Wolfe 2018 JEF: Relief Rally; Long 5 min vor bis 55 min nach Statement mit SEP+PK'),
    'RELIEF_PC': ('fomc', IDX, (835, 895), 'long', 3.0,
                  'Gu/Kurov/Wolfe 2018 JEF, ausgedehnt auf alle geplanten Sitzungen (seit 2019 alle mit PK)'),
    'REV30': ('fomc', IDX, (870, 900), ('rev', 840, 870), 3.0,
              'Boguth/Gregoire/Martineau 2019 WP: Umkehr der Ankuendigungsreaktion (14:00-14:30) bis 15:00'),
    'CONT30': ('fomc', IDX, (870, 900), ('cont', 840, 870), 3.0,
               'Alex-Grundregel Fortsetzung 14:00-14:30 -> 15:00 (Literatur stuetzt eher Umkehr; nur Info)'),
    'MOM930': ('cpinfp', IDX, (570, 900), ('cont', 510, 570), 1.0,
               'Gao/Han/Li/Zhou 2018 JFE: Intraday-Momentum staerker an Makro-Tagen; Richtung 8:30-9:30 bis 15:00'),
    'MOM1000': ('cpinfp', IDX, (600, 900), ('cont', 510, 600), 1.0,
                'Gao/Han/Li/Zhou 2018 JFE: erste Kassa-Halbstunde inkl. News (8:30-10:00) -> 10:00-15:00'),
    'PREM': ('cpinfp', IDX, (570, 900), 'long', 1.0,
             'Savor/Wilson 2013 JFQA: Ankuendigungstags-Praemie (CPI/NFP), intraday 9:30-15:00 long'),
    'FADE930': ('cpinfp', IDX, (570, 900), ('rev', 510, 570), 1.0,
                'Grant/Wolf/Yu 2005 JBF, Fung/Mok/Lam 2000 JBF: Umkehr grosser Eroeffnungsbewegungen in Indexfutures; '
                'Gegenrichtung 8:30-9:30 bis 15:00 (nach Train-Befund MOM930 gewaehlt, Spiegelregel)'),
    'FADE930_KEIN': ('kein', IDX, (570, 900), ('rev', 510, 570), 1.0,
                     'Kontrolle zu FADE930: gleiche Regel an Tagen ohne FOMC/CPI/NFP (ist der Effekt ereignisspezifisch?)'),
    'EIA_CONT': ('eia', OIL, (('rel', 30), 870), ('cont', ('rel', 0), ('rel', 30)), 1.0,
                 'Wen/Indriawan/Lien/Xu 2023 EJ: an EIA-Tagen sagt die Halbstunde ab Veroeffentlichung die Schluss-'
                 'Halbstunde voraus (Momentum); Daytrade-Form: Richtung t..t+30 fortsetzen bis 14:30 (NYMEX-Settlement)'),
    'EIA_CONT_LIT': ('eia', OIL, (930, 960), ('cont', ('rel', 0), ('rel', 30)), 1.0,
                     'Wen/Indriawan/Lien/Xu 2023 EJ woertlich: Richtung t..t+30 -> letzte Halbstunde 15:30-16:00'),
    'EIA_REV': ('eia', OIL, (('rel', 30), ('rel', 90)), ('rev', ('rel', 0), ('rel', 30)), 1.0,
                'Li/Geman 2018 J. Energy Markets: Reaktion dauert ~25 min, danach schnelle Umkehr; '
                'Gegenrichtung t..t+30 von t+30 bis t+90'),
    'FXMOM30': ('cpinfp', FX, (540, 720), ('cont', 510, 540), 1.0,
                'Evans/Lyons 2008 JFE, Love/Payne 2008 JFQA: Order-Flow traegt News weiter; Richtung 8:30-9:00 -> 12:00'),
}


def tname(t):
    return 'none' if np.isnan(t) else f'{t:g}R'


def res_m(v, tm):
    """Fensterzeit: absolute NY-Minute oder ('rel', Minuten nach der Ereigniszeit tm)."""
    return tm + v[1] if isinstance(v, tuple) else v


def fmt_m(v):
    return f't{v[1]:+d}' if isinstance(v, tuple) else f'{v // 60}:{v % 60:02d}'


def direction(x, days, spec, tm=None):
    if spec == 'long':
        return 1
    mode, a, b = spec
    r = ev.reaction(x, res_m(a, tm), res_m(b, tm))
    d = np.sign(r).fillna(0).astype(int)
    return d if mode == 'cont' else -d


def periods(inst, phase):
    if phase == 'train':
        return {'Train': (str(Q.dev_start(inst).date()), '2024-01-01')}
    return {'Val 2024': ('2024-01-01', '2025-01-01')}


def row_of(name, p, r, tg):
    art = 'Gewinnquote' if np.isnan(tg) else 'Target vor Stop'
    return dict(variante=name, periode=p, trefferquote=(r['win'] if np.isnan(tg) else r['tvs']), art_trefferquote=art,
                R=r['R'], R_pro_tag=r['R'] * r['per_day'], n=r['n'], per_day=r['per_day'], win=r['win'], tvs=r['tvs'],
                t=r['t'], t_day=r['t_day'], null_tvs=r['null_tvs'], null_win=r['null_win'], null_R=r['null_R'],
                t_vs_null=r.get('t_vs_null', np.nan), R_gross=r.get('R_gross', np.nan), time_exit=r['time_exit'])


def main(phase, only=None):
    rows, trades = [], []
    cache = {}
    for rn, (evk, insts, (a, b), spec, k, src) in RULES.items():
        if only and rn not in only:
            continue
        for inst in insts:
            if inst not in cache:
                end = '2024-01-01' if phase == 'train' else '2025-01-01'
                df = Q.load(inst, None, end, warmup_days=0)
                cache[inst] = ev.prep(df, inst)
            x = cache[inst]
            if evk == 'kein':
                groups = [(None, x.attrs['tdays'].difference(ev.event_days('any')))]
            else:
                et = ev.event_table(evk)
                groups = [(int(tm), g.index) for tm, g in et.groupby('t_m')]
            for tg in TARGETS:
                sigs = []
                for tm, days in groups:
                    a_, b_ = res_m(a, tm), res_m(b, tm)
                    if b_ <= a_:
                        continue
                    sigs.append(ev.build(x, days, a_, b_, direction(x, days, spec, tm), k=k, tgt_R=tg))
                sig = pd.concat(sigs, ignore_index=True)
                res = qbt.simulate(x, sig, inst)
                tr = qbt.trades_only(res)
                per = periods(inst, phase)
                cell = qbt.report_cell(x, tr, per)
                name = f'{rn}|{inst}|{tname(tg)}'
                params = dict(rule=rn, inst=inst, event=evk, win=f'{fmt_m(a)}-{fmt_m(b)} NY',
                              dir=str(spec), stop=f'{k:g}*sigmaF20', tgt_R=None if np.isnan(tg) else tg, src=src)
                ledger.log_variant(FAM, name, params, cell, note=NOTE)
                for p, r in cell.iterrows():
                    rows.append(row_of(name, p, r, tg))
                tr = tr.assign(rule=rn, tgt=tname(tg))
                lo, hi = list(per.values())[0]
                trades.append(tr[(tr['t_entry'] >= lo) & (tr['t_entry'] < hi)])
    out = pd.DataFrame(rows)
    tag = '' if not only else '_' + '_'.join(only)
    out.to_csv(os.path.join(HIER, f'zellen_{phase}{tag}.csv'), index=False)
    pd.concat(trades).to_csv(os.path.join(HIER, f'trades_{phase}{tag}.csv'), index=False)
    return out


if __name__ == '__main__':
    phase = sys.argv[1]
    only = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    out = main(phase, only)
    pd.set_option('display.width', 250)
    cols = ['variante', 'periode', 'n', 'per_day', 'tvs', 'win', 'R', 't', 't_day', 'null_tvs', 'null_R', 't_vs_null']
    print(out[cols].round(3).to_string(index=False))
