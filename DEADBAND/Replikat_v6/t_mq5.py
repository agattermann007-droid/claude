"""Statische Pruefung von DEADBAND_LIVE4.mq5 (ersetzt nicht den MetaEditor):
1. Klammern (), [], {} ausgeglichen (ohne Strings/Kommentare), Funktionskoerper geschlossen
2. PrintFormat/StringFormat/Print: Anzahl der Platzhalter = Anzahl der Argumente (%*f/%.*f zaehlen doppelt)
3. Makros (#define) und globale Variablen/Eingaben vor der ersten Verwendung deklariert
4. Aufrufe unbekannter Funktionen (nicht im Code definiert und keine bekannte MQL5-Funktion)
5. doppelt definierte Funktionen (gleiche Signatur-Anzahl) und doppelte globale Namen
Aufruf: python t_mq5.py [pfad]"""
import re, sys, os

PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "DEADBAND_LIVE4.mq5")
src = open(PATH, encoding="utf-8", errors="replace").read()


def strip(s):
    """Kommentare und String-/Zeichen-Literale durch Leerzeichen ersetzen (Zeilen bleiben erhalten)."""
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
            q = c; j = i + 1
            while j < n and s[j] != q:
                j += 2 if s[j] == "\\" else 1
            out.append(q + " " * (j - i - 1) + q); i = j + 1
        else:
            out.append(c); i += 1
    return "".join(out)


code = strip(src)
lines = code.split("\n")
errors = []

# 1. Klammern
stack = []
pairs = {")": "(", "]": "[", "}": "{"}
for ln, line in enumerate(lines, 1):
    for c in line:
        if c in "([{":
            stack.append((c, ln))
        elif c in ")]}":
            if not stack or stack[-1][0] != pairs[c]:
                errors.append(f"Zeile {ln}: Klammer {c} ohne passende Oeffnung (offen: {stack[-1] if stack else None})")
                stack = []
                break
            stack.pop()
if stack:
    errors.append(f"offene Klammern am Dateiende: {stack[:5]}")

# 2. Format-Aufrufe
def split_args(s, start):
    """Argumente eines Aufrufs ab der oeffnenden Klammer s[start] == '(' (im Original mit Strings)."""
    depth = 0; args = []; cur = []; i = start; n = len(s); instr = None
    while i < n:
        c = s[i]
        if instr:
            cur.append(c)
            if c == "\\":
                cur.append(s[i + 1]); i += 2; continue
            if c == instr:
                instr = None
        elif c in "\"'":
            instr = c; cur.append(c)
        elif c in "([{":
            depth += 1
            if depth > 1: cur.append(c)
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                args.append("".join(cur).strip()); return args, i
            cur.append(c)
        elif c == "," and depth == 1:
            args.append("".join(cur).strip()); cur = []
        else:
            cur.append(c)
        i += 1
    return args, i


def fmt_count(fmt):
    n = 0
    for m in re.finditer(r"%(%|[-+ #0]*(\*|\d+)?(\.(\*|\d+))?(I64|I32|l{0,2}|h)?[diouxXeEfgGcCsS])", fmt):
        if m.group(1) == "%":
            continue
        n += 1 + (1 if m.group(2) == "*" else 0) + (1 if m.group(4) == "*" else 0)
    return n


def literal_concat(expr):
    """Zusammengesetzter Format-String aus Literalen ("a" + "b"); None, wenn nicht rein literal."""
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', expr)
    rest = re.sub(r'"((?:[^"\\]|\\.)*)"', "", expr).replace("+", "").strip()
    if rest:
        return None
    return "".join(parts)


for m in re.finditer(r"\b(PrintFormat|StringFormat)\s*\(", code):
    pos = m.end() - 1
    args, _ = split_args(src, pos)
    if not args:
        continue
    fmt = literal_concat(args[0])
    if fmt is None:
        continue
    need = fmt_count(fmt); have = len(args) - 1
    if need != have:
        ln = code[:m.start()].count("\n") + 1
        errors.append(f"Zeile {ln}: {m.group(1)} braucht {need} Argumente, hat {have}: {fmt[:70]!r}")

# 3. Makros und Globale vor Verwendung
macros = {}
for m in re.finditer(r"^#define\s+(\w+)", code, re.M):
    macros.setdefault(m.group(1), code[:m.start()].count("\n") + 1)
# globale Deklarationen: Zeilen ausserhalb von Funktionskoerpern (Tiefe {} = 0)
depth = 0; globals_ = {}; func_start = []
TYPES = r"(?:input\s+|static\s+|const\s+)*(?:int|uint|long|ulong|double|float|bool|string|datetime|color|char|uchar|short|ushort|ENUM_\w+|Mql\w+|C\w+|[A-Z]\w*Def|GridSer|FadeDef)"
for ln, line in enumerate(lines, 1):
    if depth == 0:
        s = line.strip()
        mm = re.match(rf"^{TYPES}\s+(.*);\s*$", s)
        if mm and "(" not in s.split("=")[0]:
            decl = mm.group(1)
            for part in re.split(r",(?![^\[]*\])", decl):
                nm = re.match(r"\s*(\w+)", part)
                if nm:
                    globals_.setdefault(nm.group(1), ln)
    depth += line.count("{") - line.count("}")
for name, dl in list(macros.items()) + list(globals_.items()):
    for m in re.finditer(rf"\b{re.escape(name)}\b", code):
        ul = code[:m.start()].count("\n") + 1
        if ul < dl:
            errors.append(f"Zeile {ul}: {name} verwendet vor der Deklaration in Zeile {dl}")
        break

# 4. unbekannte Funktionen
defined = set(re.findall(r"^\s*(?:static\s+)?(?:const\s+)?\w+[\w<>]*\s+(\w+)\s*\([^;]*\)\s*(?:const)?\s*$", code, re.M))
defined |= set(re.findall(r"^\s*(?:static\s+)?\w+\s+(\w+)\s*\([^;{]*\)\s*\{", code, re.M))
defined |= set(re.findall(r"^\s*(?:static\s+)?(?:const\s+)?\w+\s+(\w+)\s*\(.*\)\s*\{.*\}", code, re.M))
KNOWN = set("""Print PrintFormat StringFormat Alert Comment SendNotification MathMax MathMin MathAbs MathFloor MathCeil MathRound MathSqrt MathPow MathLog MathExp MathIsValidNumber
NormalizeDouble DoubleToString IntegerToString StringToDouble StringToInteger StringToTime TimeToString TimeCurrent TimeLocal TimeGMT TimeTradeServer TimeToStruct StructToTime
StringLen StringFind StringSubstr StringSplit StringTrimLeft StringTrimRight StringToUpper StringToLower StringReplace StringGetCharacter StringAdd CharToString ShortToString
ArrayResize ArraySize ArraySetAsSeries ArrayInitialize ArraySort ArrayFree ArrayCopy ArrayMaximum ArrayMinimum ArrayFill ArrayBsearch
SymbolInfoDouble SymbolInfoInteger SymbolInfoString SymbolSelect SymbolInfoTick AccountInfoDouble AccountInfoInteger AccountInfoString TerminalInfoInteger TerminalInfoString MQLInfoInteger MQLInfoString
CopyRates CopyBuffer CopyTime CopyClose CopyOpen CopyHigh CopyLow iTime iOpen iClose iHigh iLow iBars iBarShift Bars SeriesInfoInteger PeriodSeconds
iMA iRSI iATR iStochastic iMACD IndicatorRelease
PositionsTotal PositionGetTicket PositionSelect PositionSelectByTicket PositionGetInteger PositionGetDouble PositionGetString PositionGetSymbol
OrdersTotal OrderGetTicket OrderSelect OrderGetInteger OrderGetDouble OrderGetString OrderCalcMargin OrderCalcProfit
HistorySelect HistoryDealsTotal HistoryDealGetTicket HistoryDealGetInteger HistoryDealGetDouble HistoryDealGetString HistoryOrderGetInteger HistoryDealSelect HistoryOrderSelect HistoryOrderGetDouble
EventSetTimer EventKillTimer GetTickCount GetTickCount64 GetLastError ResetLastError Sleep IsStopped
GlobalVariableSet GlobalVariableGet GlobalVariableCheck GlobalVariableDel GlobalVariablesDeleteAll GlobalVariableTime
FileOpen FileClose FileWrite FileWriteString FileReadString FileIsEnding FileDelete FileFlush FileIsExist
ObjectCreate ObjectDelete ObjectSetInteger ObjectSetString ObjectSetDouble ObjectFind ObjectsDeleteAll ChartRedraw ChartSetInteger ChartID
CalendarValueHistory CalendarEventById CalendarCountryById
MathMod MathRand MathSrand MathArctan fabs fmax fmin fmod floor ceil round
SymbolsTotal SymbolName Digits Point _Symbol _Period Symbol Period ZeroMemory TesterStatistics CopyTickVolume GlobalVariablesFlush HistorySelectByPosition
if for while switch return sizeof""".split())
calls = set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", code))
members = set(re.findall(r"\.\s*([A-Za-z_]\w*)\s*\(", code))
unknown = sorted(c for c in calls - defined - KNOWN - members if not c.isupper() and c not in ("else",))
# Typ-Konvertierungen wie (datetime)(...) und Konstruktoren
unknown = [u for u in unknown if u not in ("int", "long", "double", "datetime", "string", "bool", "ulong", "uint", "color", "char", "uchar", "float", "short")]

# 5. doppelte Funktionsnamen
fn_def = re.findall(r"^(?:static\s+)?(?:const\s+)?[\w]+\s+(\w+)\s*\(([^)]*)\)\s*$", code, re.M)
seen = {}
for name, argl in fn_def:
    k = (name, argl.count(",") + (1 if argl.strip() else 0))
    seen[k] = seen.get(k, 0) + 1
dups = [k for k, v in seen.items() if v > 1]

print(f"Datei {os.path.basename(PATH)}: {len(lines)} Zeilen, {len(macros)} Makros, {len(globals_)} globale Namen, {len(defined)} Funktionen")
for e in errors:
    print("FEHLER", e)
if unknown:
    print("PRUEFEN (Funktion unbekannt):", ", ".join(unknown))
if dups:
    print("PRUEFEN (Funktion mehrfach mit gleicher Argumentzahl):", dups)
print("ERGEBNIS", "OK" if not errors else f"{len(errors)} Fehler")
