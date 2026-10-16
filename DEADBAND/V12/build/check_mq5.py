"""Statische Pruefung einer .mq5-Datei (ohne MetaEditor):
  1) reines ASCII
  2) Klammerbilanz () [] {} ausserhalb von Strings/Kommentaren, je Funktion und gesamt
  3) PrintFormat/StringFormat: Zahl der Platzhalter (%% ausgenommen, %.*f zaehlt 2) gegen die Zahl der Argumente
Aufruf: python check_mq5.py DATEI [nur_zeilen_von-bis ...]"""
import re, sys

path = sys.argv[1]
src = open(path, "rb").read()
ok = True
try:
    src.decode("ascii")
    print("ASCII: ok")
except UnicodeDecodeError as e:
    print("ASCII: FEHLER", e); ok = False
s = src.decode("ascii", errors="replace")


def strip(s):
    """Strings und Kommentare durch Leerzeichen ersetzen (Zeilen bleiben erhalten)."""
    out = []; i = 0; n = len(s)
    while i < n:
        c = s[i]
        if s.startswith("//", i):
            j = s.find("\n", i); j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif s.startswith("/*", i):
            j = s.find("*/", i + 2); j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in s[i:j])); i = j
        elif c == '"' or c == "'":
            j = i + 1
            while j < n and s[j] != c:
                j += 2 if s[j] == "\\" else 1
            out.append(c + " " * (j - i - 1) + c); i = j + 1
        else:
            out.append(c); i += 1
    return "".join(out)


code = strip(s)
pairs = {"(": ")", "[": "]", "{": "}"}
stack = []
for ln, line in enumerate(code.split("\n"), 1):
    for ch in line:
        if ch in pairs:
            stack.append((ch, ln))
        elif ch in pairs.values():
            if not stack or pairs[stack[-1][0]] != ch:
                print(f"Klammer: FEHLER Zeile {ln}: '{ch}' ohne passende oeffnende"); ok = False
                stack = []
                break
            stack.pop()
if stack:
    print(f"Klammer: FEHLER {len(stack)} offen, erste bei Zeile {stack[0][1]} '{stack[0][0]}'"); ok = False
else:
    print("Klammerbilanz: ok (gesamt)")


def split_args(t):
    """Argumente eines Aufrufs (Text zwischen den aeusseren Klammern) auf oberster Ebene trennen."""
    args = []; depth = 0; cur = []; i = 0; inq = None
    while i < len(t):
        c = t[i]
        if inq:
            cur.append(c)
            if c == "\\":
                cur.append(t[i + 1]); i += 2; continue
            if c == inq:
                inq = None
        elif c in "\"'":
            inq = c; cur.append(c)
        elif c in "([{":
            depth += 1; cur.append(c)
        elif c in ")]}":
            depth -= 1; cur.append(c)
        elif c == "," and depth == 0:
            args.append("".join(cur)); cur = []
        else:
            cur.append(c)
        i += 1
    if cur:
        args.append("".join(cur))
    return args


nfmt = 0; bad = 0
for m in re.finditer(r"\b(PrintFormat|StringFormat)\s*\(", s):
    i = m.end(); depth = 1; inq = None; j = i
    while j < len(s) and depth > 0:
        c = s[j]
        if inq:
            if c == "\\":
                j += 2; continue
            if c == inq:
                inq = None
        elif c in "\"'":
            inq = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        j += 1
    body = s[i:j - 1]
    args = split_args(body)
    fmt_parts = re.findall(r'"((?:[^"\\]|\\.)*)"', args[0])
    if not fmt_parts or not args[0].strip().startswith('"'):
        continue                                   # Format nicht als Literal (z. B. Variable) - nicht pruefbar
    fmt = "".join(fmt_parts)
    f2 = fmt.replace("%%", "")
    specs = re.findall(r"%[-+ #0]*(\*|\d+)?(?:\.(\*|\d+))?(?:I64|ll|l|h)?([diouxXeEfgGcsC])", f2)
    need = 0
    for w, p, t in specs:
        need += 1 + (w == "*") + (p == "*")
    have = len(args) - 1
    nfmt += 1
    if need != have:
        bad += 1; ok = False
        ln = s.count("\n", 0, m.start()) + 1
        print(f"Format: FEHLER Zeile {ln}: {need} Platzhalter, {have} Argumente: {fmt[:90]}")
print(f"Format-Strings: {nfmt} geprueft, {bad} Fehler")
print("ERGEBNIS:", "OK" if ok else "FEHLER")
