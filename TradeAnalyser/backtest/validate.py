"""Prueft die Harness gegen den echten Programmweg des Scripts: fuer zufaellige Zeitpunkte einen TA_Export-Ordner
(status.txt, <NAME>_M5.csv, <NAME>_M30.csv in Serverzeit, laufende Kerze = letzte Zeile) schreiben, das Script als
Prozess mit --zeit/--nur/--kein-chart/--kein-log starten und "ausgabe" mit der Harness-Ausgabe vergleichen."""
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt


def schreibe_export(d, serie, j, name, n5=1500, n30=500):
    off = serie.off[j]
    g = serie.g_of5[j]
    a, _ = serie.grp[g]
    # M5: Serverzeit = UTC + off (ein Offset fuer alles, wie der Live-Export ihn meldet; der Export schreibt Serverzeit)
    rows5 = [(serie.ts[i], *serie.M5[i][1:]) for i in range(max(0, j - n5 + 1), j + 1)]
    bs = serie.M5[a:j + 1]
    lauf = (serie.k30[a] * 1800, bs[0][1], max(b[2] for b in bs), min(b[3] for b in bs), bs[-1][4], sum(b[5] for b in bs))
    rows30 = [(serie.k30[serie.grp[k][0]] * 1800, *serie.M30[k][1:]) for k in range(max(0, g - n30), g)] + [lauf]

    def csv(p, rows):
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write('time,open,high,low,close,tick_volume\n')
            for r in rows:
                fh.write('%d,%s,%s,%s,%s,%s\n' % (r[0], repr(r[1]), repr(r[2]), repr(r[3]), repr(r[4]), repr(r[5])))
            fh.write('END\n')
    csv(os.path.join(d, name + '_M5.csv'), rows5)
    csv(os.path.join(d, name + '_M30.csv'), rows30)
    jetzt = time.time()
    with open(os.path.join(d, 'status.txt'), 'w', encoding='utf-8') as fh:
        fh.write('offset=%d\nexport_gmt=%f\nverbunden=1\nsym_%s=%s.x\nzeit_%s=%f\nEND=1\n' % (off, jetzt, name, name, name, jetzt))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--modul', default=os.path.join(bt.HIER, '..', 'ta_mt5.py'))
    ap.add_argument('--inst', default='NAS100')
    ap.add_argument('--n', type=int, default=150)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--nur-trades', action='store_true')
    a = ap.parse_args()
    ta = bt.lade_modul(a.modul)
    s = bt.Serie(a.inst, ta)
    rnd = random.Random(a.seed)
    gleich = anders = 0
    beispiele = []
    versuche = 0
    while gleich + anders < a.n and versuche < a.n * 50:
        versuche += 1
        j = rnd.randrange(3000, len(s.M5) - 10)
        now_s = s.M5[j][0] + 299
        try:
            A, F = s.objekte(ta, j)
            e = ta.instrument(a.inst, bt.KLASSE[a.inst], A, F, now_s * 1000, [], ta.SET)
        except RuntimeError as ex:
            continue
        if a.nur_trades and e.get('status') != 'Trade':
            continue
        form_h, text_h, _ = ta.auswahl([e], True)
        with tempfile.TemporaryDirectory() as d:
            schreibe_export(d, s, j, a.inst)
            zeit = datetime.fromtimestamp(now_s, timezone.utc).isoformat()
            p = subprocess.run([sys.executable, '-W', 'ignore', a.modul, '--dir', d, '--zeit', zeit, '--nur', a.inst, '--kein-chart', '--kein-log'],
                               capture_output=True, text=True, timeout=120)
            try:
                out = json.loads(p.stdout)
            except ValueError:
                print('KEIN JSON', p.stdout[-500:], p.stderr[-500:])
                anders += 1
                continue
        if out['ausgabe'] == text_h and out['form'] == form_h:
            gleich += 1
        else:
            anders += 1
            if len(beispiele) < 5:
                beispiele.append((zeit, form_h, text_h, out['form'], out['ausgabe']))
    print('gleich', gleich, 'anders', anders)
    for b in beispiele:
        print('---', b[0])
        print('HARNESS', b[1], b[2])
        print('SCRIPT ', b[3], b[4])


if __name__ == '__main__':
    main()
