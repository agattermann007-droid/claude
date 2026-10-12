"""Backtest-Harness fuer ta_mt5.py (beliebige Fassung als Modul).

Modell: Je Instrument ein Trader, der bei JEDER M5-Kerze "--nur <Instrument>" aufruft, solange er flach ist
(keine wartende Order, keine Position). Aufrufzeit = 1 s vor Schluss der Kerze j; diese Kerze ist die "laufende"
Kerze des Exports (kurs = ihr Schluss), Kerze j-1 die letzte geschlossene. Ein Signal wird mit bewerte() des
Moduls ausgewertet (Beruehrung = Fuellung, Stop vor Target in derselben Kerze), ab Kerze j+1. Danach ist der Trader
flach ab dem Ende des Signals (ergebnis['ende']).

Kosten: die Kurse sind Bid. Netto-R zieht je gefuelltem Trade einen Spread (SPREAD[inst], Kurspunkte) ab.
News: keine (historischer Kalender fehlt) -> ev = [].
"""
import bisect
import importlib.util
import math
import os
import pickle
import sys
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

HIER = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('BT_DATA') or os.path.join(HIER, '..', 'data')
NY = ZoneInfo('America/New_York')
SPREAD = {'NAS100': 1.5, 'GER40': 1.5, 'ETH': 2.0}
KLASSE = {'NAS100': 'INDEX', 'GER40': 'INDEX', 'ETH': 'ETH'}


def lade_modul(pfad, name=None):
    name = name or os.path.splitext(os.path.basename(pfad))[0]
    spec = importlib.util.spec_from_file_location(name, pfad)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def offset_von(t_server):
    """Serverzeit NY+7 -> Offset Server minus UTC in Sekunden (7200 oder 10800)."""
    ny_naiv = datetime.fromtimestamp(t_server - 7 * 3600, timezone.utc).replace(tzinfo=None)
    off = ny_naiv.replace(tzinfo=NY).utcoffset()
    return 7 * 3600 + int(off.total_seconds())


class Serie:
    """Vorberechnete M5- und M30-Daten eines Instruments (UTC-Zeiten wie im Script nach Abzug des Offsets)."""

    def __init__(self, name, ta):
        self.name = name
        with open(os.path.join(DATA, name + '_M5.pkl'), 'rb') as fh:
            raw = pickle.load(fh)
        self.ts = [r[0] for r in raw]  # Serverzeit
        self.off = [offset_von(t) for t in self.ts]
        self.M5 = [[r[0] - o, r[1], r[2], r[3], r[4], r[5]] for r, o in zip(raw, self.off)]
        self.tu = [b[0] for b in self.M5]
        self.day5 = [t // 86400 for t in self.ts]
        # VWAP M5 ueber die ganze Serie (Reset je Server-Tag; identisch zu vwap_baender auf jedem Fenster, das den Sessionstart enthaelt)
        idx = iter(range(len(self.M5)))
        self.V5 = ta.vwap_baender(self.M5, lambda b, it=idx: self.day5[next(it)])
        # Sessionstart je Kerze
        self.sess = [0] * len(self.M5)
        s = 0
        for i in range(len(self.M5)):
            if i == 0 or self.day5[i] != self.day5[i - 1]:
                s = i
            self.sess[i] = s
        # M30 aus M5 (Serverzeit-Raster 30 min)
        self.k30 = [t // 1800 for t in self.ts]
        M30, grp = [], []
        for i, b in enumerate(self.M5):
            if not grp or self.k30[i] != self.k30[grp[-1][0]]:
                grp.append([i, i])
            else:
                grp[-1][1] = i
        self.grp = grp  # je M30-Kerze [erste M5, letzte M5]
        self.g_of5 = [0] * len(self.M5)
        for g, (a, e) in enumerate(grp):
            for i in range(a, e + 1):
                self.g_of5[i] = g
            bs = self.M5[a:e + 1]
            t30 = self.k30[a] * 1800 - self.off[a]
            M30.append([t30, bs[0][1], max(b[2] for b in bs), min(b[3] for b in bs), bs[-1][4], sum(b[5] for b in bs)])
        self.M30 = M30
        self.day30 = [self.day5[a] for a, _ in grp]
        idx2 = iter(range(len(M30)))
        self.V30 = ta.vwap_baender(M30, lambda b, it=idx2: self.day30[next(it)])
        self.ST = ta.supertrend(M30, ta.SET['ST_ATR'], ta.SET['ST_FAKTOR'])
        # kumulative VWAP-Summen M30 je Session fuer die laufende (unvollstaendige) M30-Kerze
        self.cum30 = []
        pv = v = pv2 = 0.0
        for g, b in enumerate(M30):
            if g == 0 or self.day30[g] != self.day30[g - 1]:
                pv = v = pv2 = 0.0
            self.cum30.append((pv, v, pv2))  # Summen VOR Kerze g
            src = (b[2] + b[3] + b[4]) / 3
            vol = b[5] if b[5] > 0 else 1.0
            pv += src * vol
            v += vol
            pv2 += src * src * vol

    def objekte(self, ta, j, n5=None):
        """A (M30) und F (M5) wie lade_instrument/baue, Stand: Kerze j laeuft (fast fertig)."""
        s = self.sess[j]
        a5 = max(0, min(s - 2, j - 100))
        B5 = self.M5[a5:j + 1]
        V5 = self.V5[a5:j + 1]
        F = ta.baue(B5, V5, 300)
        F['Vlist'] = V5
        g = self.g_of5[j]
        a, _ = self.grp[g]
        bs = self.M5[a:j + 1]
        lauf = [self.M30[g][0], bs[0][1], max(b[2] for b in bs), min(b[3] for b in bs), bs[-1][4], sum(b[5] for b in bs)]
        g0 = max(0, g - 70)
        B30 = self.M30[g0:g] + [lauf]
        V30 = self.V30[g0:g]
        pv, v, pv2 = self.cum30[g]
        src = (lauf[2] + lauf[3] + lauf[4]) / 3
        vol = lauf[5] if lauf[5] > 0 else 1.0
        pv += src * vol
        v += vol
        pv2 += src * src * vol
        vw = pv / v
        sd = math.sqrt(max(pv2 / v - vw * vw, 0.0))
        if sd < abs(vw) * 1e-9:
            sd = 0.0
        V30 = V30 + [[vw, vw + sd, vw - sd, vw + 2 * sd, vw - 2 * sd, vw + 3 * sd, vw - 3 * sd]]
        st = [self.ST[g - 1], (None, None)]
        A = ta.baue(B30, V30, 1800, st)
        return A, F


def lauf(ta, serie, von=None, bis=None, Z=None, sequenziell=True, schritt=1, mit_daten=False):
    """Fuehrt den Trader ueber [von, bis) (UTC-Sekunden) aus. Rueckgabe: Liste der Signale mit Ergebnis."""
    Z = Z or ta.SET
    M5 = serie.M5
    n = len(M5)
    i0 = bisect.bisect_left(serie.tu, von) if von else 0
    i1 = bisect.bisect_left(serie.tu, bis) if bis else n
    i0 = max(i0, 400)
    frei_ab = 0
    out = []
    j = i0
    while j < i1 - 1:
        now_s = M5[j][0] + 299
        if now_s < frei_ab:
            j += 1
            continue
        try:
            A, F = serie.objekte(ta, j)
            e = ta.instrument(serie.name, KLASSE[serie.name], A, F, now_s * 1000, [], Z)
        except RuntimeError:
            j += 1
            continue
        if e.get('status') == 'Trade':
            sg = e['signal']
            r = {'inst': serie.name, 'zeit': now_s, 'art': e['orderart'], 'klasse': e['klasse'], 'crv': e['crv'],
                 'distanzATR': e['distanzATR'], 'd': sg['d'], 'E': sg['E'], 'S': sg['S'], 'T': sg['T'], 'kurs': sg['kurs'],
                 'atr5': sg['atr5'], 'verfall': sg.get('verfall'), 'zielstufe': sg.get('zielstufe', 0), 'level': sg.get('level')}
            for k in ('extra',):
                if k in sg:
                    r[k] = sg[k]
            if mit_daten:
                r['daten'] = e.get('daten')
                r['zeilen'] = e.get('zeilen')
            K = M5[j - 1:min(n, j + 200)]
            res = ta.bewerte(r, K, 1e18)
            if res is None:
                res = {'status': 'offen', 'R': None, 'ende': now_s}
            r['ergebnis'] = res
            out.append(r)
            if sequenziell:
                frei_ab = res.get('ende', now_s) or now_s
        j += schritt
    return out


def kennzahlen(sig, spread=None):
    st = lambda r: r['ergebnis']['status']
    fill = [r for r in sig if st(r) in ('Target', 'Stop', 'Zeitablauf', 'unklar')]
    rr = [r for r in fill if r['ergebnis']['R'] is not None]
    tz = sum(st(r) == 'Target' for r in fill)
    sz = sum(st(r) == 'Stop' for r in fill)
    za = [r for r in fill if st(r) == 'Zeitablauf']
    netto = 0.0
    for r in rr:
        risk = r['d'] * (r['E'] - r['S'])
        sp = (spread or 0.0)
        netto += r['ergebnis']['R'] - sp / risk
    tage = len({datetime.fromtimestamp(r['zeit'], timezone.utc).date() for r in sig}) or 1
    gew = sum(1 for r in rr if r['ergebnis']['R'] > 0)
    out = {
        'signale': len(sig), 'gefuellt': len(fill), 'fuellquote': len(fill) / len(sig) if sig else 0,
        'target': tz, 'stop': sz, 'zeitablauf': len(za), 'unklar': sum(st(r) == 'unklar' for r in fill),
        'winrate_TvS': tz / (tz + sz) if tz + sz else 0, 'winrate_Rpos': gew / len(rr) if rr else 0,
        'summeR': sum(r['ergebnis']['R'] for r in rr), 'R_je_trade': (sum(r['ergebnis']['R'] for r in rr) / len(rr)) if rr else 0,
        'summeR_netto': netto, 'R_netto_je_trade': netto / len(rr) if rr else 0,
        'market': sum(r['art'] == 'Market' for r in sig), 'limit': sum(r['art'] == 'Limit' for r in sig),
        'verworfen': sum(st(r) == 'verworfen' for r in sig), 'nicht_gefuellt': sum(st(r) == 'nicht gefuellt' for r in sig),
        'crv_median': sorted(r['crv'] for r in sig)[len(sig) // 2] if sig else 0,
    }
    wz = [(r['ergebnis']['fuellung'] - r['zeit']) / 60 for r in fill if r['ergebnis'].get('fuellung')]
    out['wartezeit_median_min'] = sorted(wz)[len(wz) // 2] if wz else 0
    hd = [(r['ergebnis']['ende'] - (r['ergebnis'].get('fuellung') or r['zeit'])) / 60 for r in fill if r['ergebnis'].get('ende')]
    out['haltedauer_median_min'] = sorted(hd)[len(hd) // 2] if hd else 0
    out['handelstage'] = tage
    out['trades_je_tag'] = len(fill) / tage
    return out


def fmt(k):
    return ('Sig %(signale)d | gef %(gefuellt)d (%(fuellquote).0f%%) | T %(target)d S %(stop)d ZA %(zeitablauf)d | WR(T/S) %(wr).1f%% | '
            'R %(summeR)+.1f (%(R_je_trade)+.3f/Tr) | netto %(summeR_netto)+.1f (%(R_netto_je_trade)+.3f/Tr) | M %(market)d L %(limit)d | '
            'warte %(wartezeit_median_min).0f min | halte %(haltedauer_median_min).0f min | CRVmed %(crv_median).2f | %(trades_je_tag).1f Tr/Tag') % dict(
        k, fuellquote=100 * k['fuellquote'], wr=100 * k['winrate_TvS'])


def jahr(y):
    return int(datetime(y, 1, 1, tzinfo=timezone.utc).timestamp())


def _job(arg):
    modul, inst, y, zjson = arg
    import json as _j
    ta = lade_modul(modul, 'm_%s_%d' % (inst, y))
    Z = dict(ta.SET, **_j.loads(zjson)) if zjson else ta.SET
    s = Serie(inst, ta)
    return y, lauf(ta, s, jahr(y), jahr(y + 1), Z=Z)


def bericht(modul, inst, jahre, zjson='', procs=3, out=''):
    """Je Jahr ein Prozess; druckt Kennzahlen je Jahr und gesamt. Rueckgabe: {jahr: signale}."""
    from multiprocessing import Pool
    with Pool(min(procs, len(jahre))) as pool:
        res = dict(pool.map(_job, [(modul, inst, y, zjson) for y in jahre]))
    alle = []
    for y in jahre:
        alle += res[y]
        print(inst, y, fmt(kennzahlen(res[y], SPREAD[inst])))
    print(inst, 'GESAMT', fmt(kennzahlen(alle, SPREAD[inst])))
    if out:
        with open(out, 'wb') as fh:
            pickle.dump(res, fh)
    return res


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--modul', default=os.path.join(HIER, '..', 'ta_mt5.py'))
    ap.add_argument('--inst', default='NAS100')
    ap.add_argument('--jahre', default='2021,2022,2023')
    ap.add_argument('--set', default='', help='JSON mit SET-Ueberschreibungen, z. B. {"MIN_CRV": 1.0}')
    ap.add_argument('--procs', type=int, default=3)
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    bericht(os.path.abspath(a.modul), a.inst, [int(x) for x in a.jahre.split(',')], a.set, a.procs, a.out)
