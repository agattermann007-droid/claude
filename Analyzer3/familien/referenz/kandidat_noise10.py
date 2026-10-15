"""Referenz noise-1.0 (Rekonstruktion) als Kandidat fuer den gesperrten Test."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import noise

NAME = 'noise-1.0'
INSTRUMENTS = ['NAS100']


def prepare(df, inst):
    return noise.prepare(df, inst)


def signals(x, inst):
    return noise.noise10_signals(x)
