"""Patch-Dateien bauen: vollstaendige Kopie von DEADBAND_V8.mq5 mit Einfuegungen an eindeutigen Ankern, dazu ein
Unified-Diff. Die Original-EA bleibt unveraendert (Auftrag Abschnitt 7).

eingriffe: Liste (anker, art, text) mit art 'vor' | 'nach' | 'ersetze'. Jeder Anker muss genau einmal vorkommen.
"""
import difflib
import os

HIER = os.path.dirname(os.path.abspath(__file__))
DEADBAND = os.path.dirname(os.path.dirname(HIER))
EA = os.path.join(DEADBAND, "DEADBAND_V8.mq5")


def anwenden(text, eingriffe):
    for anker, art, neu in eingriffe:
        n = text.count(anker)
        if n != 1:
            raise ValueError(f"Anker {n}x gefunden: {anker[:80]!r}")
        if art == "vor":
            text = text.replace(anker, neu + anker)
        elif art == "nach":
            text = text.replace(anker, anker + neu)
        elif art == "ersetze":
            text = text.replace(anker, neu)
        else:
            raise ValueError(art)
    return text


def bauen(eingriffe, ausgabe, diff_ausgabe, kopf_zusatz=""):
    alt = open(EA, encoding="ascii").read()
    neu = anwenden(alt, eingriffe)
    if kopf_zusatz:
        neu = kopf_zusatz + neu
    neu.encode("ascii")
    with open(ausgabe, "w", encoding="ascii", newline="") as f:
        f.write(neu)
    d = difflib.unified_diff(alt.splitlines(keepends=True), neu.splitlines(keepends=True),
                             "DEADBAND_V8.mq5", os.path.basename(ausgabe), n=3)
    with open(diff_ausgabe, "w", encoding="ascii", newline="") as f:
        f.writelines(d)
    return neu
