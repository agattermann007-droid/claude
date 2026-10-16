"""Hilfen fuer Patch-Skripte: exakte Ersetzungen, jede muss genau einmal passen (sonst Abbruch), nur ASCII."""
import sys


class Patch:
    def __init__(self, src):
        self.s = open(src, "r", encoding="ascii").read()
        self.n = 0

    def rep(self, old, new, label=""):
        c = self.s.count(old)
        if c != 1:
            sys.exit(f"ABBRUCH: Ersetzung '{label}' passt {c}-mal (erwartet genau 1):\n{old[:300]}")
        self.s = self.s.replace(old, new)
        self.n += 1

    def save(self, dst):
        try:
            self.s.encode("ascii")
        except UnicodeEncodeError as e:
            sys.exit(f"ABBRUCH: Nicht-ASCII-Zeichen im Ergebnis: {e}")
        open(dst, "w", encoding="ascii", newline="").write(self.s)
        print(f"{self.n} Ersetzungen -> {dst}")


def between(s, start, end):
    """Text von start (inklusive) bis end (exklusive); beide Marken muessen genau einmal vorkommen."""
    for mk in (start, end):
        c = s.count(mk)
        if c != 1:
            sys.exit(f"ABBRUCH: Marke passt {c}-mal: {mk[:120]}")
    a = s.index(start); b = s.index(end)
    if b <= a:
        sys.exit("ABBRUCH: Endmarke vor Startmarke")
    return s[a:b]
