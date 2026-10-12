"""Massstab ohne Analyse: Market-Entry bei jeder Kerze (sequenziell wie die Harness), Richtung zufaellig bzw. nach
M30-Supertrend, Stop = s x ATR5(14), Target = t x ATR5. Zeigt, welche Winrate allein die Geometrie liefert."""
import os
import random
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt


def lauf(ta, s, von, bis, sm, tm, modus, seed=1):
    rnd = random.Random(seed)
    M5 = s.M5
    import bisect
    i0 = max(400, bisect.bisect_left(s.tu, von))
    i1 = bisect.bisect_left(s.tu, bis)
    frei, out, j = 0, [], i0
    while j < i1 - 1:
        now = M5[j][0] + 299
        if now < frei or s.sess[j] > j - 12:  # erste Stunde nach Reset aus
            j += 1
            continue
        C = M5[j - 15:j]
        atr = sum(max(C[i][2] - C[i][3], abs(C[i][2] - C[i - 1][4]), abs(C[i][3] - C[i - 1][4])) for i in range(1, 15)) / 14
        kurs = M5[j][4]
        if modus == 'zufall':
            d = rnd.choice((1, -1))
        elif modus == 'long':
            d = 1
        elif modus == 'short':
            d = -1
        else:
            d = s.ST[s.g_of5[j] - 1][0]
        E = ta.jsround(kurs)
        S = (E - d * sm * atr)
        T = (E + d * tm * atr)
        S = int(S // 1) if d > 0 else -int((-S) // 1)
        T = int(T // 1) if d > 0 else -int((-T) // 1)
        r = {'d': d, 'E': E, 'S': S, 'T': T, 'zeit': now, 'art': 'Market', 'atr5': atr, 'crv': (tm / sm), 'klasse': modus, 'verfall': None}
        res = ta.bewerte(r, M5[j - 1:j + 200], 1e18) or {'status': 'offen', 'R': None, 'ende': now}
        r['ergebnis'] = res
        out.append(r)
        frei = res.get('ende', now)
        j += 1
    return out


if __name__ == '__main__':
    ta = bt.lade_modul(os.path.join(bt.HIER, '..', 'ta_mt5_v1.3_backup.py'))
    s = bt.Serie('NAS100', ta)
    for modus in ('zufall', 'supertrend'):
        for sm, tm in ((1.0, 1.0), (1.5, 1.0), (2.0, 1.0), (1.0, 0.5), (1.0, 1.5)):
            sig = lauf(ta, s, bt.jahr(2021), bt.jahr(2025), sm, tm, modus)
            print(modus, 'Stop %.1f ATR, Target %.1f ATR:' % (sm, tm), bt.fmt(bt.kennzahlen(sig, 1.5)))
            sys.stdout.flush()
