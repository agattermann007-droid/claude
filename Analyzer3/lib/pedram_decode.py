"""Decoder fuer das Monatsformat von Pedram007z/BackTest-Platform (Branch market-data, store/<SYM>/<YYYY-MM>.m1).
Format laut server/src/market/store.ts: 48-Byte-Kopf ('BTM1', Version, Dezimalstellen, Status je Tag 0=fehlt/1=zu/2=gespeichert ab Byte 8),
danach zlib(int32[gespeicherte Tage * 1440 * 4]): je Minute open-prevClose, high-open, open-low, close-open (prevClose je Tag ab 0),
Luecken = -2^31. Zeiten UTC, Bid. Wird nur gelesen, kein Code aus dem Repo ausgefuehrt."""
import glob, os, sys, zlib
import numpy as np, pandas as pd

GAP = -2147483648


def decode_month(path):
    buf = open(path, 'rb').read()
    assert buf[:4] == b'BTM1', path
    dec = buf[5]
    status = np.frombuffer(buf[8:39], np.uint8)
    y, m = map(int, os.path.basename(path)[:7].split('-'))
    stored = [d for d in range(31) if status[d] == 2]
    if not stored:
        return None
    ints = np.frombuffer(zlib.decompress(buf[48:]), np.int32).reshape(len(stored), 1440, 4).astype(np.int64)
    out = []
    for k, d in enumerate(stored):
        a = ints[k]
        gap = a[:, 0] == GAP
        a = np.where(gap[:, None], 0, a)
        # open_j = close_{j-1} + a0 ; close_j = open_j + a3 ; ueber Luecken laeuft prevClose unveraendert weiter
        inc = a[:, 0] + a[:, 3]
        close = np.cumsum(inc)
        open_ = close - a[:, 3]
        hi, lo = open_ + a[:, 1], open_ - a[:, 2]
        t0 = pd.Timestamp(year=y, month=m, day=d + 1)
        idx = t0 + pd.to_timedelta(np.arange(1440), unit='min')
        df = pd.DataFrame({'o': open_, 'h': hi, 'l': lo, 'c': close}, index=idx)[~gap] / 10 ** dec
        out.append(df)
    return pd.concat(out)


def decode_symbol(store_dir):
    parts = [decode_month(f) for f in sorted(glob.glob(os.path.join(store_dir, '*.m1')))]
    return pd.concat([p for p in parts if p is not None])


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    for sym in sys.argv[3:]:
        d = decode_symbol(os.path.join(src, sym))
        d.index.name = 'ts_utc'
        d.to_parquet(os.path.join(dst, f'{sym}_M1_UTC.parquet'))
        print(sym, len(d), d.index[0], d.index[-1], flush=True)
