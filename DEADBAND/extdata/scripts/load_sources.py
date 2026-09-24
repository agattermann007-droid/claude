import glob, json
import numpy as np, pandas as pd
from common import *

def load_nsx_histdata():
    return pd.read_pickle(f'{EXT}/work/nsx_histdata_m1.pkl')   # Spalten open..volume, ts (roh, Quell-Wanduhr)

def load_oanda(instr):
    fs = sorted(glob.glob(f'{EXT}/raw/oanda_futuresharks/pyfinancialdata/data/currencies/oanda/{instr}/*/*.csv'))
    df = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    df['ts'] = pd.to_datetime(df['time'])
    df = df.drop(columns=['time']).sort_values('ts').drop_duplicates('ts')
    return df

def load_dypoi():
    fs = sorted(glob.glob(f'{EXT}/raw/dypoi_dukascopy_xauusd_m1/XAUUSD_M1_*.csv'))
    df = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    df['ts'] = pd.to_datetime(df['timestamp'])
    df = df.drop(columns=['timestamp']).sort_values('ts')
    return df
