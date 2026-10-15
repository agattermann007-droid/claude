"""Datenschicht fuer Analyzer 3: einheitliche M5-Kerzen in Qberx-Serverzeit (New York + 7 h).

Kanonische Dateien: /home/user/data/m5/<INST>.parquet, Index = Eroeffnungszeit der Kerze in Serverzeit (naiv),
Spalten o, h, l, c, v, src. Eine Kerze umfasst [t, t+5 min).

Zeitraeume (Protokoll):
  dev    : DEV_START[inst] .. 2024-12-31   (Train bis 2023-12-31, Validierung 2024)
  info25 : 2025 (verbraucht, nur Zusatzinfo)
  locked : alles vor DEV_START[inst] und 2026-01-01 .. Ende. Nur mit Freigabe (siehe lock_open()).

Zugriff fuer die Forschung ausschliesslich ueber load(inst, eval_start, eval_end, warmup_days).
Die Funktion liefert Kerzen ab eval_start - warmup_days (zum Aufwaermen von Indikatoren) bis eval_end
und verweigert jeden Auswertungsbereich, der in einen gesperrten Zeitraum faellt.
"""
import glob
import os

import numpy as np
import pandas as pd

DATA = os.environ.get('QDATA', '/home/user/data')
M5DIR = os.path.join(DATA, 'm5')
RAW = os.path.join(DATA, 'raw')
LOCKFILE = os.path.join(DATA, 'LOCK_OPEN')          # existiert erst nach Freigabe des gesperrten Tests

DEV_END = pd.Timestamp('2025-01-01')                 # exklusiv
INFO25_END = pd.Timestamp('2026-01-01')
DEFAULT_DEV_START = pd.Timestamp('2020-01-01')
# NAS100: Entwicklungsdaten ab 2021 (MT5-Export); 2005-2020 wurde nie benutzt und bleibt gesperrt.
DEV_START = {'NAS100': pd.Timestamp('2021-01-01')}

# Roundtrip-Kosten als Anteil am Preis (konservative Annahmen, Spread bei Qberx noch offen).
COST = {
    'NAS100': 0.0001, 'US500': 0.0001, 'US30': 0.00012, 'US2000': 0.0003,
    'GER40': 0.0001, 'UK100': 0.0002, 'FRA40': 0.0002, 'ESTX50': 0.0003, 'JPN225': 0.0003, 'AUS200': 0.0003,
    'XAUUSD': 0.00015, 'XAGUSD': 0.0006, 'WTI': 0.0006, 'BRENT': 0.0006,
    'BTCUSD': 0.0008, 'ETHUSD': 0.0008,
    'EURUSD': 0.00011, 'GBPUSD': 0.00015, 'AUDUSD': 0.00015, 'USDCAD': 0.00015, 'USDCHF': 0.00018,
}


def dev_start(inst):
    return DEV_START.get(inst, DEFAULT_DEV_START)


def lock_open():
    return os.path.exists(LOCKFILE)


def split_of(inst, t):
    t = pd.Timestamp(t)
    if t < dev_start(inst):
        return 'locked_pre'
    if t < DEV_END:
        return 'dev'
    if t < INFO25_END:
        return 'info25'
    return 'locked_26'


def check_range(inst, eval_start, eval_end):
    """eval_end exklusiv. Wirft PermissionError, wenn ein gesperrter Bereich ausgewertet werden soll."""
    a, b = pd.Timestamp(eval_start), pd.Timestamp(eval_end)
    bad = (a < dev_start(inst)) or (b > INFO25_END)
    if bad and not lock_open():
        raise PermissionError(f'{inst}: Auswertung {a.date()}..{b.date()} beruehrt gesperrte Daten '
                              f'(dev ab {dev_start(inst).date()}, Sperre ab 2026-01-01). Erst nach Freigabe.')


def available():
    return sorted(os.path.basename(f)[:-8] for f in glob.glob(os.path.join(M5DIR, '*.parquet')))


def _read(inst):
    return pd.read_parquet(os.path.join(M5DIR, inst + '.parquet'))


def load(inst, eval_start=None, eval_end=None, warmup_days=60):
    """Kerzen fuer die Auswertung [eval_start, eval_end) plus Vorlauf. Standard: ganzer dev-Zeitraum."""
    a = pd.Timestamp(eval_start) if eval_start is not None else dev_start(inst)
    b = pd.Timestamp(eval_end) if eval_end is not None else DEV_END
    check_range(inst, a, b)
    df = _read(inst)
    lo = a - pd.Timedelta(days=warmup_days)
    if not lock_open():
        lo = max(lo, dev_start(inst))      # auch zum Aufwaermen keine gesperrten Kerzen vor der Freigabe
    df = df[(df.index >= lo) & (df.index < b)].copy()
    df.attrs['inst'] = inst
    df.attrs['eval_start'] = a
    df.attrs['eval_end'] = b
    return df


def coverage(inst):
    """Nur Metadaten (keine Kurse): Kerzen je Jahr und Quelle. Erlaubt fuer alle Zeitraeume."""
    df = _read(inst)
    return df.groupby([df.index.year, 'src']).size().unstack(fill_value=0)


# ---------------------------------------------------------------- Zeitumrechnung

def utc_to_server(idx_utc):
    """naive UTC-Zeitstempel -> naive Serverzeit (NY-Ortszeit + 7 h, US-Sommerzeitregel)."""
    t = pd.DatetimeIndex(idx_utc).tz_localize('UTC').tz_convert('America/New_York').tz_localize(None)
    return t + pd.Timedelta(hours=7)


def server_to_ny(idx_server):
    return pd.DatetimeIndex(idx_server) - pd.Timedelta(hours=7)


def server_to_tz(idx_server, tz):
    """naive Serverzeit -> naive Ortszeit in tz (z. B. 'Europe/Berlin', 'Asia/Tokyo')."""
    ny = server_to_ny(idx_server)
    return ny.tz_localize('America/New_York', ambiguous='NaT', nonexistent='shift_forward').tz_convert(tz).tz_localize(None)


def fixed_offset_to_server(idx, hours):
    """Quelle mit fester UTC-Verschiebung (z. B. HistData EST = -5) -> Serverzeit."""
    return utc_to_server(pd.DatetimeIndex(idx) - pd.Timedelta(hours=hours))


# ---------------------------------------------------------------- Aggregation

def to_m5(df1):
    """M1 (Index Serverzeit, Spalten o h l c v) -> M5 im Serverraster."""
    g = df1.groupby(df1.index.floor('5min'))
    out = pd.DataFrame({'o': g['o'].first(), 'h': g['h'].max(), 'l': g['l'].min(), 'c': g['c'].last(), 'v': g['v'].sum()})
    return out.dropna(subset=['o'])


def clean(df):
    df = df[~df.index.duplicated(keep='last')].sort_index()
    df = df[df.index.dayofweek < 5]   # Wochenende in Serverzeit (Sa/So) raus
    bad = (df.h < df[['o', 'c']].max(axis=1)) | (df.l > df[['o', 'c']].min(axis=1)) | (df.l <= 0)
    return df[~bad]


# ---------------------------------------------------------------- Rohquellen

def src_ts4(sym):
    f = os.path.join(RAW, 'ts4', f'{sym}_M5.csv')
    d = pd.read_csv(f)
    d.columns = [c.strip().lower() for c in d.columns]
    idx = pd.to_datetime(d.iloc[:, 0])
    out = pd.DataFrame({'o': d.iloc[:, 1].values, 'h': d.iloc[:, 2].values, 'l': d.iloc[:, 3].values,
                        'c': d.iloc[:, 4].values, 'v': d.iloc[:, 5].values}, index=idx)
    return out


def src_oanda(instr):
    fs = sorted(glob.glob(os.path.join(RAW, 'fs/pyfinancialdata/data/currencies/oanda', instr, '*', '*.csv')))
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    d['ts'] = pd.to_datetime(d['time'])
    d = d.drop_duplicates('ts').sort_values('ts')
    idx = utc_to_server(d['ts'].values)
    m1 = pd.DataFrame({'o': d['open'].values, 'h': d['high'].values, 'l': d['low'].values, 'c': d['close'].values,
                       'v': d['volume'].values.astype(float)}, index=idx)
    m1 = m1[~m1.index.duplicated()]
    return to_m5(m1)


def src_histdata_fs(sym, utc_offset_hours=-5):
    """HistData M1 aus FutureSharks (Semikolon, 'YYYYMMDD HHMMSS'), deklariert EST ohne Sommerzeit."""
    fs = sorted(glob.glob(os.path.join(RAW, 'fs/pyfinancialdata/data/stocks/histdata', sym, '*.csv')))
    d = pd.concat([pd.read_csv(f, sep=';', header=None, names=['t', 'o', 'h', 'l', 'c', 'v']) for f in fs])
    idx = fixed_offset_to_server(pd.to_datetime(d['t'], format='%Y%m%d %H%M%S'), utc_offset_hours)
    m1 = pd.DataFrame({'o': d.o.values, 'h': d.h.values, 'l': d.l.values, 'c': d.c.values, 'v': d.v.values * 0.0}, index=idx)
    m1 = m1[~m1.index.duplicated()]
    return to_m5(m1)


def src_bitstamp_btc():
    fs = sorted(glob.glob(os.path.join(RAW, 'fs/pyfinancialdata/data/cryptocurrencies/bitstamp/BTC_USD/*.csv')))
    d = pd.concat([pd.read_csv(f) for f in fs])
    idx = utc_to_server(pd.to_datetime(d['date']).values)
    m1 = pd.DataFrame({'o': d.open.values, 'h': d.high.values, 'l': d.low.values, 'c': d.close.values, 'v': 0.0}, index=idx)
    m1 = m1[~m1.index.duplicated()]
    return to_m5(m1)


def build(inst, parts):
    """parts: Liste (name, DataFrame, start, end) in aufsteigender Prioritaet; spaetere ueberschreiben fruehere."""
    pieces = []
    for name, df, a, b in parts:
        x = df
        if a is not None:
            x = x[x.index >= pd.Timestamp(a)]
        if b is not None:
            x = x[x.index < pd.Timestamp(b)]
        x = x.copy()
        x['src'] = name
        pieces.append(x)
    df = pd.concat(pieces)
    df = clean(df)
    os.makedirs(M5DIR, exist_ok=True)
    df.to_parquet(os.path.join(M5DIR, inst + '.parquet'))
    return df
