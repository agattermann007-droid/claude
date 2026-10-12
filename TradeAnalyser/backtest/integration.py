"""Integrationstest fuer ta_mt5.py ueber den echten Programmweg (Prozessaufruf wie im Skill):
TA_Export-Ordner mit NAS100 (US100-Export), GER40 (Dukascopy), ETH (Binance) zur selben Zeit (2021-01 .. 2023-09),
dann setup-Laeufe in Zeitfolge (Signal-Log + Schatten), Einzelabfragen, --auswerten, Chart, Kontrolle wie SKILL.md Schritt 5."""
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt

S = os.path.join(bt.HIER, '..')
QUELLEN = {'NAS100': os.path.join(S, 'data'), 'GER40': os.path.join(S, 'data_gerduk'), 'ETH': os.path.join(S, 'data_eth')}


def lade_serien(ta):
    se = {}
    for n, d in QUELLEN.items():
        os.environ['BT_DATA'] = d
        bt.DATA = d
        se[n] = bt.Serie(n, ta)
    return se


def schreibe(d, se, now_s, n5=1500, n30=500):
    """Export-Stand zur Zeit now_s (UTC). Laufende Kerze = die Kerze, die now_s enthaelt. Rueckgabe: offset."""
    import bisect
    status = {'export_gmt': time.time(), 'verbunden': 1}
    off = None
    for n, s in se.items():
        j = bisect.bisect_right(s.tu, now_s) - 1
        if j < 0 or now_s - s.tu[j] >= 300:
            # keine laufende Kerze: Markt ruht -> letzte Kerze liegt zurueck (zeit_ alt)
            pass
        if j < 0:
            continue
        o = s.off[j]
        off = off or o
        g = s.g_of5[j]
        a, _ = s.grp[g]
        rows5 = [(s.ts[i], *s.M5[i][1:]) for i in range(max(0, j - n5 + 1), j + 1)]
        bs = s.M5[a:j + 1]
        lauf = (s.k30[a] * 1800, bs[0][1], max(b[2] for b in bs), min(b[3] for b in bs), bs[-1][4], sum(b[5] for b in bs))
        rows30 = [(s.k30[s.grp[k][0]] * 1800, *s.M30[k][1:]) for k in range(max(0, g - n30), g)] + [lauf]
        for tf, rows in (('M5', rows5), ('M30', rows30)):
            with open(os.path.join(d, n + '_' + tf + '.csv'), 'w', encoding='utf-8') as fh:
                fh.write('time,open,high,low,close,tick_volume\n')
                for r in rows:
                    fh.write('%d,%s,%s,%s,%s,%s\n' % (r[0], repr(r[1]), repr(r[2]), repr(r[3]), repr(r[4]), repr(r[5])))
                fh.write('END\n')
        status['sym_' + n] = n + '.x'
        # letzter Tick: Ende der letzten Kerze, hoechstens jetzt (Abstand zur Exportzeit wie live)
        status['zeit_' + n] = status['export_gmt'] - max(0, now_s - (s.tu[j] + 299))
    status['offset'] = off
    with open(os.path.join(d, 'status.txt'), 'w', encoding='utf-8') as fh:
        for k, v in status.items():
            fh.write('%s=%s\n' % (k, v))
        fh.write('END=1\n')
    return off


def rufe(modul, d, now_s, *args):
    zeit = datetime.fromtimestamp(now_s, timezone.utc).astimezone().isoformat()
    p = subprocess.run([sys.executable, modul, '--dir', d, '--zeit', zeit, *args], capture_output=True, text=True, timeout=300)
    try:
        return json.loads(p.stdout)
    except ValueError:
        raise SystemExit('KEIN JSON: ' + p.stdout[-800:] + p.stderr[-2000:])


def kontrolle(out):
    """SKILL.md Schritt 5."""
    if out['form'] != 'A':
        return None
    z = out['ausgabe'].split('\n')
    assert z[0].startswith('Entry:') and z[1].startswith('Target:') and z[2].startswith('Stop:') and z[3].startswith('Begründung:'), z
    assert all(x.startswith('(Chart') for x in z[4:]), z
    E = float(z[0].rsplit('@', 1)[1])
    T = float(z[1].split(':')[1])
    S_ = float(z[2].split(':')[1])
    long = ' Long ' in z[0]
    assert (S_ < E < T) if long else (T < E < S_), (z[0], E, T, S_)
    return z


def main():
    modul = os.path.abspath(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    ta = bt.lade_modul(modul)
    se = lade_serien(ta)
    rnd = random.Random(5)
    d = os.path.join(S, 'integration_export')
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    start = bt.jahr(2022) + 86400 * rnd.randrange(0, 200)
    t = start
    formen, arten, texte = {}, {}, []
    fenster = os.environ.get('NUR_FENSTER') == '1'
    from zoneinfo import ZoneInfo
    for i in range(n):
        t += rnd.choice((300, 900, 1800, 3600, 7200)) if not fenster else rnd.choice((300, 600, 900, 1500))
        if fenster:  # nur US-Kernzeit 10:00-15:25 New York an Werktagen
            while True:
                ny = datetime.fromtimestamp(t, ZoneInfo('America/New_York'))
                if ny.weekday() < 5 and 10 * 60 <= ny.hour * 60 + ny.minute <= 15 * 60 + 25:
                    break
                t += 1800
        schreibe(d, se, t)
        out = rufe(modul, d, t + 299, '--news', '[]')
        formen[out['form']] = formen.get(out['form'], 0) + 1
        assert out['version'] == ta.TA_VERSION
        z = kontrolle(out)
        if z:
            arten[z[0].split()[3]] = arten.get(z[0].split()[3], 0) + 1
            assert out['chart'] and os.path.exists(os.path.expanduser(out['chart'])), out
            texte.append(out['ausgabe'])
        else:
            assert out['chart'] is None
            texte.append(out['ausgabe'])
        if i % 7 == 3:
            for inst in ('NAS', 'DAX', 'ETH'):
                o2 = rufe(modul, d, t + 299, '--news', '[]', '--nur', inst)
                kontrolle(o2)
    # News-Sperre
    schreibe(d, se, t)
    hm = datetime.fromtimestamp(t + 299 + 600, ZoneInfo('Europe/Vienna')).strftime('%H:%M')  # Termine gelten fuer den heutigen Wiener Tag
    o3 = rufe(modul, d, t + 299, '--news', json.dumps([['CPI', hm, 'WIEN']]), '--nur', 'NAS100')
    assert o3['form'] == 'B' and 'News-Sperre' in o3['ausgabe'], o3['ausgabe']
    # Auswertung einige Tage spaeter
    schreibe(d, se, t + 3 * 86400)
    o4 = rufe(modul, d, t + 3 * 86400, '--auswerten')
    sig = [json.loads(z) for z in open(os.path.join(d, 'signale.jsonl'), encoding='utf-8')]
    print('Formen', formen, '| Orderarten', arten, '| Signalzeilen', len(sig), '| davon Schatten', sum(r.get('quelle') == 'schatten' for r in sig),
          '| vergleich', {k: sum(r.get('vergleich') == k for r in sig) for k in ('gleich', 'anders', 'alt_kein', 'fehler')})
    print('--- Beispielausgaben')
    for x in [x for x in texte if x.startswith('Entry')][:3] + [x for x in texte if x.startswith('Kein')][:2]:
        print(x)
        print()
    print('--- auswerten (Form %s)' % o4['form'])
    print(o4['ausgabe'])


if __name__ == '__main__':
    main()
