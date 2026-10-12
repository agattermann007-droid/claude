"""Bedingte Trefferquoten: fuer JEDE M5-Kerze ein gedachter Market-Trade (Long und Short) mit Stop s x ATR5 und Target t x ATR5,
erste Beruehrung entscheidet (Stop zuerst bei Gleichstand), Zeitlimit 96 Kerzen. Gruppiert nach Merkmalen.
Ohne Kosten: Vergleich mit der Geometrie (bei s=1.5, t=1.0 ohne Vorteil ca. 60 %)."""
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt

NY = ZoneInfo('America/New_York')


def ausgang(M5, j, d, E, S, T, n=96):
    for k in range(j + 1, min(len(M5), j + 1 + n)):
        h, l = M5[k][2], M5[k][3]
        hs = l <= S if d > 0 else h >= S
        ht = h >= T if d > 0 else l <= T
        if hs:
            return -1
        if ht:
            return 1
    return 0


def main(inst='NAS100', von=2021, bis=2024, s=1.5, t=1.0):
    ta = bt.lade_modul(os.path.join(bt.HIER, '..', 'ta_mt5_v1.3_backup.py'))
    se = bt.Serie(inst, ta)
    import bisect
    i0 = max(400, bisect.bisect_left(se.tu, bt.jahr(von)))
    i1 = bisect.bisect_left(se.tu, bt.jahr(bis))
    M5 = se.M5
    G = defaultdict(lambda: [0, 0])
    for j in range(i0, i1 - 1):
        if j - se.sess[j] < 12:
            continue
        C = M5[j - 15:j]
        atr = sum(max(C[i][2] - C[i][3], abs(C[i][2] - C[i - 1][4]), abs(C[i][3] - C[i - 1][4])) for i in range(1, 15)) / 14
        if atr <= 0:
            continue
        kurs = M5[j][4]
        v = se.V5[j]
        sd = (v[1] - v[0])
        z = (kurs - v[0]) / sd if sd > 0 else 0
        zb = max(-3, min(3, int(z // 0.5))) / 2  # Halb-Sigma-Klassen
        stdir = se.ST[se.g_of5[j] - 1][0]
        g = se.g_of5[j]
        v30 = se.V30[g - 1][0]
        seite30 = 1 if kurs > v30 else -1
        h = datetime.fromtimestamp(M5[j][0], NY).hour
        lc = M5[j - 1]
        kerze = 1 if lc[4] > lc[1] else -1
        for d in (1, -1):
            E = kurs
            r = ausgang(M5, j, d, E, E - d * s * atr, E + d * t * atr)
            if r == 0:
                continue
            mit_trend = 'mitST' if d == stdir else 'gegenST'
            reg = 'TREND' if seite30 == stdir else 'RANGE'
            zr = zb * d  # z in Handelsrichtung (positiv = Kurs schon in Richtung gelaufen)
            for key in (('alle',), ('trend', mit_trend), ('regime', reg, mit_trend), ('z_richtung', zr), ('z_trend', mit_trend, zr),
                        ('stunde_NY', h), ('kerze', 'mit' if kerze == d else 'gegen', mit_trend), ('regime_z', reg, mit_trend, zr)):
                G[key][0 if r > 0 else 1] += 1
    for k in sorted(G, key=lambda x: tuple(str(y) for y in x)):
        w, l = G[k]
        if w + l >= 300:
            print('%-45s n=%6d  WR %.1f%%' % (' '.join(str(x) for x in k), w + l, 100 * w / (w + l)))


if __name__ == '__main__':
    main(*sys.argv[1:2] or ['NAS100'])
