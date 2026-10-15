"""Pruefung noise_ausstiege / code: Kerzenabdeckung je NY-Uhrzeit im dev-Zeitraum (nur ueber qdata.load)."""
import sys
sys.path.insert(0, '/home/user/claude/Analyzer3/lib')
import numpy as np, pandas as pd
import qdata as Q

for inst in ['NAS100', 'US500']:
    df = Q.load(inst, Q.dev_start(inst), '2025-01-01', warmup_days=0)
    ny = Q.server_to_ny(df.index)
    wd = ny.dayofweek < 5
    print(inst, 'Kerzen', len(df), 'von', df.index[0], 'bis', df.index[-1])
    print(' Quellen:', df['src'].value_counts().to_dict())
    tod = pd.Series(ny.hour * 60 + ny.minute, index=df.index)
    days = pd.Series(ny.normalize()).nunique()
    hh = (tod // 30) * 30
    cnt = hh[wd].groupby(hh[wd]).size()
    tab = pd.DataFrame({'kerzen': cnt, 'je_tag_von6': cnt / days})
    tab.index = [f'{v//60:02d}:{v%60:02d}' for v in tab.index]
    print(' Tage:', days)
    print(tab.T.round(2).to_string())
    # Quellen je Jahr
    print(df.groupby([df.index.year, 'src']).size().unstack(fill_value=0))
    # Volumen > 0 Anteil
    print(' Anteil v>0:', (df['v'] > 0).mean().round(3))
