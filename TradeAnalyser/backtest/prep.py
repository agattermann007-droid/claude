"""Konvertiert Kursdaten in ein einheitliches Format: Serverzeit NY+7 (wie Qberx/GFT), M5-Kerzen [t_server, o, h, l, c, vol].
Ausgabe: data/<NAME>_M5.pkl (Liste von Tupeln, aufsteigend, ohne Duplikate)."""
import csv, pickle, sys, os
from datetime import datetime, timezone, timedelta

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')


def us100():
    rows = []
    with open(os.path.join(D, 'US100_M5.csv')) as fh:
        r = csv.reader(fh)
        next(r)
        for z in r:
            t = int(datetime.strptime(z[0], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp())  # Serverzeit als "naive UTC"-Sekunden
            rows.append((t, float(z[1]), float(z[2]), float(z[3]), float(z[4]), float(z[5])))
    return rows


def speichere(name, rows):
    rows = sorted({r[0]: r for r in rows}.values())
    with open(os.path.join(D, name + '_M5.pkl'), 'wb') as fh:
        pickle.dump(rows, fh)
    print(name, len(rows), datetime.utcfromtimestamp(rows[0][0]), datetime.utcfromtimestamp(rows[-1][0]))


def utc_zu_server(t_utc):
    """UTC-Sekunden -> Serverzeit-Sekunden (NY+7, US-Sommerzeit)."""
    from zoneinfo import ZoneInfo
    off = datetime.fromtimestamp(t_utc, timezone.utc).astimezone(ZoneInfo('America/New_York')).utcoffset().total_seconds()
    return int(t_utc + off + 7 * 3600)


def m1_zu_m5(rows1):
    """rows1: [(t_server, o, h, l, c, v)] M1 aufsteigend -> M5 im Serverzeit-Raster."""
    out = {}
    for t, o, h, l, c, v in rows1:
        k = t - t % 300
        if k not in out:
            out[k] = [k, o, h, l, c, v]
        else:
            b = out[k]
            b[2] = max(b[2], h)
            b[3] = min(b[3], l)
            b[4] = c
            b[5] += v
    return [tuple(b) for b in sorted(out.values())]


def ger_getdata():
    m1 = {}
    for f in ('GER30_1m_tag.csv', 'GER30_1m_head.csv'):
        with open(os.path.join(D, f)) as fh:
            r = csv.reader(fh)
            next(r)
            for z in r:
                t = int(datetime.fromisoformat(z[0]).timestamp())
                m1[t] = (utc_zu_server(t), round(float(z[1]), 2), round(float(z[2]), 2), round(float(z[3]), 2), round(float(z[4]), 2), float(z[5]))
    return m1_zu_m5([m1[t] for t in sorted(m1)])


def ger_dukascopy():
    rows = []
    with open(os.path.join(D, 'DEUIDXEUR_M5.csv')) as fh:
        r = csv.reader(fh, delimiter='\t')
        next(r)
        for z in r:
            t = int(datetime.strptime(z[0], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp())
            ts = utc_zu_server(t)
            rows.append((ts, float(z[1]), float(z[2]), float(z[3]), float(z[4]), 1.0))  # Volumen unbekannt -> gleich gewichtet
    # UTC-M5 und Server-M5 haben dasselbe 5-min-Raster (Offset ganze Stunden)
    return rows


def speichere_in(ordner, name, rows):
    os.makedirs(ordner, exist_ok=True)
    rows = sorted({r[0]: r for r in rows}.values())
    with open(os.path.join(ordner, name + '_M5.pkl'), 'wb') as fh:
        pickle.dump(rows, fh)
    print(ordner, name, len(rows), datetime.fromtimestamp(rows[0][0], timezone.utc), datetime.fromtimestamp(rows[-1][0], timezone.utc))


def eth_binance():
    import glob
    import pyarrow.parquet as pq
    rows = []
    for f in sorted(glob.glob(os.path.join(D, 'eth5', 'ETHUSDT-5m-*.parquet'))):
        t = pq.read_table(f, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']).to_pydict()
        for ts, o, h, l, c, v in zip(t['timestamp'], t['open'], t['high'], t['low'], t['close'], t['volume']):
            tu = int(ts.timestamp())
            rows.append((utc_zu_server(tu), float(o), float(h), float(l), float(c), float(v)))
    return rows


if __name__ == '__main__':
    # Erwartet die Rohdaten aus hole_daten.sh in ../data; schreibt ../data (NAS100), ../data_ger26, ../data_gerduk, ../data_eth
    B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    speichere('NAS100', us100())
    speichere_in(os.path.join(B, 'data_ger26'), 'GER40', ger_getdata())
    speichere_in(os.path.join(B, 'data_gerduk'), 'GER40', ger_dukascopy())
    speichere_in(os.path.join(B, 'data_eth'), 'ETH', eth_binance())
