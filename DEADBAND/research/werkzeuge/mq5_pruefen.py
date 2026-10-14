"""Statische Pruefung von MQL5-Dateien (ersetzt nicht den MetaEditor - dort muss jede Datei kompiliert werden).

Prueft:
  1. kein BOM, nur ASCII (Regel des Auftrags: String-Literale nur ASCII; hier strenger: die ganze Datei)
  2. Klammerbilanz () [] {} ausserhalb von Kommentaren, Strings und Zeichen-Literalen
  3. StringFormat/PrintFormat: Zahl der Platzhalter (%% ausgenommen, * fuer Breite/Genauigkeit zaehlt mit) = Zahl der Argumente,
     StringFormat nie ohne Argument
  4. #define-Namen nicht vor ihrer Definition verwendet (Fehlertyp der Builds 6.10-Zwischenstaende)

Aufruf: python mq5_pruefen.py DATEI.mq5 [...]   Rueckgabe 0 = ohne Befund, 1 = Befunde
"""
import re
import sys

SPEC = re.compile(r"%(%|[-+ #0]*(\*|\d+)?(\.(\*|\d+))?(I64|I32|ll|l|h)?[diouxXeEfgGcCsS])")


def maskieren(src):
    """Kommentare, Strings und Zeichen-Literale durch Leerzeichen ersetzen (Zeilenumbrueche bleiben).
    Liefert (maskierter Text, Liste der String-Literale mit Startposition)."""
    out = list(src)
    lits = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = " "
            i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
        elif c == '"' or c == "'":
            j = i + 1
            while j < n and src[j] != c:
                if src[j] == "\\":
                    j += 1
                j += 1
            if c == '"':
                lits.append((i, src[i + 1:j]))
            for k in range(i, min(j + 1, n)):
                if out[k] != "\n":
                    out[k] = " " if k not in (i, j) else c
            i = j + 1
        else:
            i += 1
    return "".join(out), lits


def zeile(src, pos):
    return src.count("\n", 0, pos) + 1


def klammern(src, mask):
    befunde = []
    paar = {")": "(", "]": "[", "}": "{"}
    stapel = []
    for i, c in enumerate(mask):
        if c in "([{":
            stapel.append((c, i))
        elif c in ")]}":
            if not stapel or stapel[-1][0] != paar[c]:
                befunde.append(f"Z. {zeile(src, i)}: '{c}' ohne passende oeffnende Klammer")
                return befunde
            stapel.pop()
    for c, i in stapel[-3:]:
        befunde.append(f"Z. {zeile(src, i)}: '{c}' nicht geschlossen")
    return befunde


def argumente(mask, src, start):
    """Argumente eines Aufrufs ab der oeffnenden Klammer bei 'start' (Positionen in src) auf oberster Ebene trennen."""
    tiefe = 0
    teile, beg = [], start + 1
    i = start
    while i < len(mask):
        c = mask[i]
        if c in "([{":
            tiefe += 1
        elif c in ")]}":
            tiefe -= 1
            if tiefe == 0:
                teile.append(src[beg:i])
                return teile, i
        elif c == "," and tiefe == 1:
            teile.append(src[beg:i])
            beg = i + 1
        i += 1
    return None, None


def formate(src, mask, lits):
    befunde = []
    lit_at = {p: s for p, s in lits}
    for m in re.finditer(r"\b(StringFormat|PrintFormat)\s*\(", mask):
        name = m.group(1)
        teile, ende = argumente(mask, src, m.end() - 1)
        if teile is None:
            befunde.append(f"Z. {zeile(src, m.start())}: {name} ohne schliessende Klammer")
            continue
        fmt_src = teile[0]
        # Format = ein Literal oder eine Verkettung von Literalen
        off = m.end() + (len(fmt_src) - len(fmt_src.lstrip()))
        stuecke = re.findall(r'"((?:[^"\\]|\\.)*)"', fmt_src)
        rest = re.sub(r'"((?:[^"\\]|\\.)*)"', "", fmt_src).replace("+", "").strip()
        if not stuecke or rest:
            continue                                   # Format nicht statisch - nicht pruefbar
        fmt = "".join(stuecke)
        noetig = 0
        for s in SPEC.finditer(fmt):
            if s.group(1) == "%":
                continue
            noetig += 1 + (1 if s.group(2) == "*" else 0) + (1 if s.group(4) == "*" else 0)
        da = len(teile) - 1
        if name == "StringFormat" and da == 0:
            befunde.append(f"Z. {zeile(src, m.start())}: StringFormat ohne Argument (reinen Text direkt zuweisen)")
        elif noetig != da:
            befunde.append(f"Z. {zeile(src, m.start())}: {name} braucht {noetig} Argument(e), hat {da}")
    return befunde


def defines(src, mask):
    befunde = []
    for m in re.finditer(r"^[ \t]*#define[ \t]+([A-Za-z_]\w*)", src, re.M):
        name, pos = m.group(1), m.start()
        erst = re.search(r"\b" + re.escape(name) + r"\b", mask)
        if erst and erst.start() < pos:
            befunde.append(f"Z. {zeile(src, erst.start())}: {name} vor seiner Definition (Z. {zeile(src, pos)}) verwendet")
    return befunde


def pruefe(pfad):
    roh = open(pfad, "rb").read()
    befunde = []
    if roh.startswith(b"\xef\xbb\xbf") or roh.startswith(b"\xff\xfe") or roh.startswith(b"\xfe\xff"):
        befunde.append("Datei beginnt mit BOM")
    for nr, z in enumerate(roh.split(b"\n"), 1):
        if any(b > 127 for b in z):
            befunde.append(f"Z. {nr}: Zeichen ausserhalb ASCII")
            break
    src = roh.decode("utf-8", errors="replace")
    mask, lits = maskieren(src)
    befunde += klammern(src, mask)
    befunde += formate(src, mask, lits)
    befunde += defines(src, mask)
    return befunde


if __name__ == "__main__":
    fehler = 0
    for p in sys.argv[1:]:
        b = pruefe(p)
        print(f"{p}: {'ohne Befund' if not b else str(len(b)) + ' Befund(e)'}")
        for x in b:
            print("  " + x)
        fehler += len(b)
    sys.exit(1 if fehler else 0)
