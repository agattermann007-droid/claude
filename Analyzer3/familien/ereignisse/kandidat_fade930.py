"""Kandidat 'ereignis-fade930' (Familie ereignisse).

Regel: An CPI- und NFP-Tagen (Veroeffentlichung 8:30 ET, Termine aus dem vorab bekannten BLS-Kalender
/home/user/data/cal/cpi.csv, nfp.csv) wird die Bewegung von 8:30 bis 9:30 ET (Schluss der Kerze 8:25 -> Schluss der
Kerze 9:25) zur Kassaeroeffnung GEGEN die Richtung gehandelt: Market-Einstieg 9:30 ET, Stop 1 x sigma_F
(sigma_F = Wurzel des Mittels der quadrierten Renditen 9:30->15:00 der letzten 20 vollen Handelstage), Ziel 1 R,
Zeitausstieg 15:00 ET (Schluss der Kerze 14:55). Nur volle Handelstage (kein verkuerzter Boersentag).
Quelle: Umkehr grosser Eroeffnungsbewegungen in Indexfutures (Grant/Wolf/Yu 2005 JBF 29(5); Fung/Mok/Lam 2000 JBF 24(7));
Richtung auf Train gewaehlt, nachdem die Fortsetzungsregel (Gao/Han/Li/Zhou 2018 JFE) dort klar negativ war.
Serverzeit = NY + 7 h: Einstieg 16:30, Ausstieg 22:00 Serverzeit.
"""
import os
import sys

import numpy as np
import pandas as pd

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import ev  # noqa: E402

NAME = 'ereignis-fade930'
INSTRUMENTS = ['NAS100']
START, END = 570, 900          # 9:30-15:00 ET
TGT_R, K = 1.0, 1.0


def prepare(df, inst):
    return ev.prep(df, inst)


def signals(x, inst):
    et = ev.event_table('cpinfp')
    out = []
    for tm, g in et.groupby('t_m'):
        tm = int(tm)
        if tm >= START:
            continue
        r = ev.reaction(x, tm, START)                  # Kurs um tm -> Kurs um 9:30 (Schluss der Signalkerze 9:25)
        d = -np.sign(r).fillna(0).astype(int)
        out.append(ev.build(x, g.index, START, END, d, k=K, tgt_R=TGT_R))
    sig = pd.concat(out, ignore_index=True) if out else pd.DataFrame()
    return sig.sort_values('i_sig').reset_index(drop=True)
