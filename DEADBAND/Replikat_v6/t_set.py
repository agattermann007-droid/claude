"""Pruefung: Voreinstellungen des EA (input ... = Wert) gegen ein Preset (.set). Aufruf: python t_set.py [set] [--diff]
Ohne --diff muss das Set alle Eingaben mit genau den Voreinstellungen enthalten (Echtbetrieb-Set); mit --diff werden nur
die Abweichungen gelistet (z. B. Sicher-Set)."""
import re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
mq = open(os.path.join(HERE, "..", "DEADBAND_LIVE4.mq5"), encoding="utf-8").read()
inp = {}
for m in re.finditer(r'^input\s+(?!group)(\w+)\s+(\w+)\s*=\s*("[^"]*"|[^;]+);', mq, re.M):
    typ, name, val = m.group(1), m.group(2), m.group(3).strip()
    if typ == "string":
        val = val[1:-1] if val.startswith('"') else val
    elif typ == "ENUM_TIMEFRAMES":
        val = {"PERIOD_M5": "5", "PERIOD_M15": "15"}.get(val, val)
    inp[name] = (typ, val)
setf = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join(HERE, "..", "DEADBAND_LIVE4_Echtbetrieb.set")
st = {}
for l in open(setf, encoding="utf-8"):
    l = l.strip()
    if not l or l.startswith(";") or "=" not in l:
        continue
    k, v = l.split("=", 1); st[k] = v.split("||")[0]


def same(typ, a, b):
    if typ in ("double",):
        try:
            return abs(float(a) - float(b)) < 1e-12
        except ValueError:
            return False
    if typ in ("int", "long"):
        return int(float(a)) == int(float(b))
    if typ == "bool":
        return a.lower() == b.lower()
    return a == b


fehlt = [k for k in inp if k not in st]
fremd = [k for k in st if k not in inp]
abw = [(k, inp[k][1], st[k]) for k in inp if k in st and not same(inp[k][0], inp[k][1], st[k])]
print(f"{os.path.basename(setf)}: {len(inp)} Eingaben im EA, {len(st)} im Set | fehlen {fehlt} | unbekannt {fremd}")
for k, a, b in abw:
    print(f"  abweichend: {k} EA {a} / Set {b}")
if "--diff" not in sys.argv:
    print("ERGEBNIS", "OK (Set = Voreinstellungen)" if not fehlt and not fremd and not abw else "ABWEICHUNG")
