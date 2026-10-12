"""Zurueckrollen-Test: Log mit Zeilen von mt5-1.3 und mt5-1.4 (inkl. Schatten), dann --auswerten mit BEIDEN Fassungen.
Aufruf: python3 rollback_test.py <ta_mt5.py neu> <ta_mt5_v1.3_backup.py>"""
import json, os, random, shutil, sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt, integration as it

neu, alt = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
ta = bt.lade_modul(neu)
se = it.lade_serien(ta)
d = os.path.join(it.S, 'rollback_export')
shutil.rmtree(d, ignore_errors=True)
os.makedirs(d)
rnd = random.Random(3)
t = bt.jahr(2022) + 86400 * 60
NYZ = ZoneInfo('America/New_York')
formen = {}
for modul, n in ((alt, 12), (neu, 40)):
    for i in range(n):
        t += rnd.choice((300, 600, 900))
        while True:
            ny = datetime.fromtimestamp(t, NYZ)
            if ny.weekday() < 5 and 10 * 60 <= ny.hour * 60 + ny.minute <= 15 * 60 + 25:
                break
            t += 1800
        it.schreibe(d, se, t)
        o = it.rufe(modul, d, t + 299, '--news', '[]')
        it.kontrolle(o)
        formen[(os.path.basename(modul), o['form'])] = formen.get((os.path.basename(modul), o['form']), 0) + 1
it.schreibe(d, se, t + 86400)
rows = [json.loads(z) for z in open(os.path.join(d, 'signale.jsonl'), encoding='utf-8')]
print('Formen', formen, '| Zeilen', len(rows), {v: sum(r.get('version') == v for r in rows) for v in ('mt5-1.3', 'mt5-1.4')},
      '| zielstufe-Werte 1.4:', sorted({r.get('zielstufe') for r in rows if r.get('version') == 'mt5-1.4' and r.get('quelle') != 'schatten'}, key=str))
for modul in (neu, alt):
    o = it.rufe(modul, d, t + 86400, '--auswerten')
    print('=== --auswerten mit', os.path.basename(modul), '-> Form', o['form'])
    print(o['ausgabe'])
    assert o['form'] == 'L', o['ausgabe']
