"""Baut eine Doppelklick-Setupdatei (cmd/PowerShell-Polyglott) mit eingebetteten Dateien.

Muster (bewaehrt auf dem Server, nur Web-Konsole, Download per Browser):
  Zeile 1 '<# :' ist fuer cmd ein Sprungziel, fuer PowerShell der Beginn eines Blockkommentars.
  Der cmd-Teil startet PowerShell mit dem Inhalt derselben Datei; der PowerShell-Teil steht nach '#>'.
Eingebettete Dateien stehen als PowerShell-Here-Strings @' ... '@ im Text (wortwoertlich, keine Ersetzung).
Platzhalter im PowerShell-Rumpf: ##DATEI:<name>##  ->  Here-String mit dem Inhalt der Datei,
                                 ##CODE:<name>##   ->  Inhalt der Datei wortwoertlich (PowerShell-Bausteine).
Ausgabe: nur ASCII, CRLF.

Aufruf: python cmd_bauen.py RUMPF.ps1 AUSGABE.cmd name=pfad [name=pfad ...]
"""
import sys

KOPF = """<# : cmd-Teil - PowerShell liest diese Zeilen als Kommentar
@echo off
setlocal
set "DEADBAND_SELF=%~f0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Expression ([IO.File]::ReadAllText($env:DEADBAND_SELF))"
echo.
pause
exit /b
#>
"""


def here_string(text):
    if "\n'@" in "\n" + text:
        raise ValueError("Datei enthaelt eine Zeile, die mit '@ beginnt - nicht einbettbar")
    return "@'\n" + text.rstrip("\n") + "\n'@"


def bauen(rumpf_pfad, aus_pfad, dateien):
    rumpf = open(rumpf_pfad, encoding="ascii").read()
    for name, pfad in dateien.items():
        inhalt = open(pfad, encoding="ascii").read().replace("\r\n", "\n")
        rumpf = rumpf.replace(f"##DATEI:{name}##", here_string(inhalt))
        rumpf = rumpf.replace(f"##CODE:{name}##", inhalt.rstrip("\n"))
    if "##DATEI:" in rumpf or "##CODE:" in rumpf:
        raise ValueError("nicht ersetzter Platzhalter: " + rumpf[rumpf.find("##"):][:60])
    text = KOPF + rumpf
    text.encode("ascii")                                  # wirft bei Nicht-ASCII
    text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    with open(aus_pfad, "w", encoding="ascii", newline="") as f:
        f.write(text)


if __name__ == "__main__":
    args = dict(a.split("=", 1) for a in sys.argv[3:])
    bauen(sys.argv[1], sys.argv[2], args)
    print("geschrieben:", sys.argv[2])
