"""Vergleich ohne Analyse mit genau der Geometrie von mt5-1.4: Richtung zufaellig, Stop STOP_ATR x ATR5, Target max(ZIEL_R x Risiko,
Mindestziel), Rundung wie im Script, gleiches Handelsfenster (Mo-Fr), gleicher sequenzieller Trader, bewerte() des Scripts.
Aufruf: python3 zufall14.py NAS100 2024,2025 5   (Instrument, Jahre, Anzahl Zufallsfolgen); Daten wie bt.py (BT_DATA)."""
import bisect
import math
import os
import random
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bt


def lauf(ta, s, inst, y, seed):
    Z = ta.SET
    MINZ = (Z['MINZIEL_ETH_PCT'] if inst == 'ETH' else Z['MINZIEL_INDEX_PCT']) / 100
    hz = Z['HANDELSZEIT_DAX_WIEN'] if inst == 'GER40' else (Z['HANDELSZEIT_ETH_NY'] if inst == 'ETH' else Z['HANDELSZEIT_NAS_NY'])
    tz = ta.WIEN if inst == 'GER40' else ta.NY
    a, b = ta.hhmm(hz[0]), ta.hhmm(hz[1])
    rnd = random.Random(seed)
    M5 = s.M5
    i0 = max(400, bisect.bisect_left(s.tu, bt.jahr(y)))
    i1 = bisect.bisect_left(s.tu, bt.jahr(y + 1))
    frei, out, j = 0, [], i0
    while j < i1 - 1:
        now = M5[j][0] + 299
        dt = datetime.fromtimestamp(now, tz)
        if now < frei or not (a <= dt.hour * 60 + dt.minute < b) or dt.weekday() >= 5 or j - s.sess[j] < 12:
            j += 1
            continue
        C = M5[j - 15:j]
        atr = sum(max(C[i][2] - C[i][3], abs(C[i][2] - C[i - 1][4]), abs(C[i][3] - C[i - 1][4])) for i in range(1, 15)) / 14
        if not atr > 0:
            j += 1
            continue
        d = rnd.choice((1, -1))
        E = ta.jsround(M5[j][4])
        S = math.floor(E - d * Z['STOP_ATR'] * atr) if d > 0 else math.ceil(E - d * Z['STOP_ATR'] * atr)
        risk = d * (E - S)
        zr, mz = Z['ZIEL_R'] * risk, math.ceil(MINZ * E)
        T = math.floor(E + max(zr, mz)) if d > 0 else math.ceil(E - max(zr, mz))
        r = {'d': d, 'E': E, 'S': S, 'T': T, 'zeit': now, 'art': 'Market', 'atr5': atr, 'crv': Z['ZIEL_R'], 'verfall': None}
        r['ergebnis'] = ta.bewerte(r, M5[j - 1:j + 200], 1e18) or {'status': 'offen', 'R': None, 'ende': now}
        out.append(r)
        frei = r['ergebnis'].get('ende', now)
        j += 1
    return out


if __name__ == '__main__':
    inst, jahre, n = sys.argv[1], [int(x) for x in sys.argv[2].split(',')], int(sys.argv[3])
    ta = bt.lade_modul(os.path.join(bt.HIER, '..', 'ta_mt5.py'))
    s = bt.Serie(inst, ta)
    for seed in range(1, n + 1):
        sig = [r for y in jahre for r in lauf(ta, s, inst, y, seed)]
        k = bt.kennzahlen(sig, bt.SPREAD[inst])
        print('%s %s Zufall %d: n=%d Target vor Stop %.1f %% brutto %+.3f netto %+.3f' % (
            inst, sys.argv[2], seed, k['gefuellt'], 100 * k['winrate_TvS'], k['R_je_trade'], k['R_netto_je_trade']))
        sys.stdout.flush()
