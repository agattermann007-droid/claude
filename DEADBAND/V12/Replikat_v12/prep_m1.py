# Replikat v11 - Datenaufbereitung: M1-Kurse -> Serverzeit (NY + 7 h), numpy-Archiv
# Aufruf: python prep_m1.py [all|xau|nasraw|nas]
# Gold: Dukascopy UTC (Bid/Ask) -> NY-Ortszeit -> +7 h
# NAS:  HistData NSXUSD; Zeitbasis wird hier pro Datensatz bestimmt (siehe nas_shift)
import os, sys, glob, json, numpy as np, pandas as pd
XAU_DIR = os.environ.get('XAU_DIR', '/home/user/data/xau')
NAS_DIR = os.environ.get('NAS_DIR', '/home/user/data/nas/data/histdata/nsxusd/normalized')
OUT = os.environ.get('NPZ_DIR', '/home/user/work/npz')

def ny_to_server(ts_ny_naive):
    return ts_ny_naive + pd.Timedelta(hours=7)

def gold():
    fs = sorted(glob.glob(os.path.join(XAU_DIR, 'XAUUSD_M1_*.csv')))
    df = pd.concat([pd.read_csv(f, usecols=['timestamp','open_bid','high_bid','low_bid','close_bid','close_ask']) for f in fs])
    df = df.drop_duplicates('timestamp').sort_values('timestamp')
    t = pd.to_datetime(df['timestamp']).dt.tz_localize('UTC').dt.tz_convert('America/New_York').dt.tz_localize(None)
    srv = ny_to_server(t)
    sec = (srv.values.astype('datetime64[s]').astype(np.int64))
    np.savez(os.path.join(OUT, 'XAU_m1.npz'), t=sec, o=df.open_bid.values, h=df.high_bid.values, l=df.low_bid.values,
             c=df.close_bid.values, spr=(df.close_ask.values - df.close_bid.values))
    print('XAU', len(sec), pd.Timestamp(sec[0], unit='s'), pd.Timestamp(sec[-1], unit='s'))

def nas_raw():
    fs = sorted(glob.glob(os.path.join(NAS_DIR, 'nsxusd_m1_*.json')))
    parts = []
    for f in fs:
        d = pd.DataFrame(json.load(open(f)))
        parts.append(d[['timestamp','open','high','low','close']])
    df = pd.concat(parts).drop_duplicates('timestamp').sort_values('timestamp')
    return df

def nas_final():
    # Pruefung (Minute mit groesster Bewegung je Jahr/Saison): 9:30/8:30 liegen in allen
    # Jahren 2010-2026, Sommer wie Winter, auf der Quellzeit -> Quelle = NY-Ortszeit.
    d = np.load(os.path.join(OUT, 'NAS_raw.npz'))
    sec = d['ts'] + 7 * 3600
    np.savez(os.path.join(OUT, 'NAS_m1.npz'), t=sec, o=d['o'], h=d['h'], l=d['l'], c=d['c'])
    print('NAS', len(sec), pd.Timestamp(sec[0], unit='s'), pd.Timestamp(sec[-1], unit='s'))

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if which in ('all', 'xau'):
        gold()
    if which in ('all', 'nasraw'):
        df = nas_raw()
        np.savez(os.path.join(OUT, 'NAS_raw.npz'), ts=df.timestamp.values//1000, o=df.open.values, h=df.high.values, l=df.low.values, c=df.close.values)
        print('NAS raw', len(df))
    if which in ('all', 'nas'):
        nas_final()
