"""Ausgelieferte Dateien sind aktuell: Sidecar-Setup.cmd und patch_sidecar_lesen.mq5 entsprechen ihren Quellen."""
import os
import subprocess
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HIER))
WERKZEUGE = os.path.join(RESEARCH, "werkzeuge")
sys.path.insert(0, WERKZEUGE)
import cmd_bauen  # noqa: E402
import patch_bauen  # noqa: E402


def test_patch_aktuell_und_original_unveraendert(tmp_path):
    import patch_sidecar_bauen as PS
    neu = patch_bauen.anwenden(open(patch_bauen.EA, encoding="ascii").read(), PS.EINGRIFFE)
    assert PS.KOPF + neu == open(os.path.join(RESEARCH, "patch_sidecar_lesen.mq5"), encoding="ascii").read()
    alt = open(patch_bauen.EA, encoding="ascii").read()
    assert "Sidecar" not in alt                                     # Original-EA nie veraendert
    for name in ("SidecarLesen     = false", "SidecarSperre    = false"):
        assert name in neu                                          # Standard aus = handelsidentisch


def test_setup_cmd_aktuell(tmp_path):
    aus = tmp_path / "Sidecar-Setup.cmd"
    s = os.path.join(RESEARCH, "sidecar")
    cmd_bauen.bauen(os.path.join(s, "Sidecar-Setup.ps1"), str(aus),
                    dict(gft=os.path.join(WERKZEUGE, "gft_terminal.ps1"), sidecar=os.path.join(s, "sidecar.py"),
                         kern=os.path.join(s, "sidecar_kern.py"), ea=os.path.join(RESEARCH, "patch_sidecar_lesen.mq5")))
    assert aus.read_bytes() == open(os.path.join(s, "Sidecar-Setup.cmd"), "rb").read(), \
        "Sidecar-Setup.cmd neu bauen: python werkzeuge/cmd_bauen.py sidecar/Sidecar-Setup.ps1 sidecar/Sidecar-Setup.cmd ..."


def test_mq5_pruefung():
    r = subprocess.run([sys.executable, os.path.join(WERKZEUGE, "mq5_pruefen.py"),
                        os.path.join(RESEARCH, "patch_sidecar_lesen.mq5")], capture_output=True, text=True)
    assert r.returncode == 0 and "ohne Befund" in r.stdout, r.stdout + r.stderr


def test_patch_intrabar_aktuell_und_order_teil_unveraendert():
    import patch_intrabar_bauen as PI
    alt = open(patch_bauen.EA, encoding="ascii").read()
    neu = open(os.path.join(RESEARCH, "patch_intrabar.mq5"), encoding="ascii").read()
    assert PI.KOPF + patch_bauen.anwenden(alt, PI.EINGRIFFE) == neu
    assert "input int    EntryMode        = 0;" in neu
    # Order-Teil: Text von HedgeFrei bis Funktionsende identisch zu 8.10
    ende = "//+------------------------------------------------------------------+\n//| 4.30 Wochenend-Pause"
    a0 = alt.index(PI.ORDER_ALT); a1 = alt.index(ende)
    n0 = neu.index(PI.ORDER_ALT); n1 = neu.index(ende)
    assert alt[a0:a1] == neu[n0:n1]
    r = subprocess.run([sys.executable, os.path.join(WERKZEUGE, "mq5_pruefen.py"), os.path.join(RESEARCH, "patch_intrabar.mq5")],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "ohne Befund" in r.stdout


def test_export_setup_cmd_aktuell(tmp_path):
    aus = tmp_path / "Export-Setup.cmd"
    cmd_bauen.bauen(os.path.join(RESEARCH, "export", "Export-Setup.ps1"), str(aus),
                    dict(gft=os.path.join(WERKZEUGE, "gft_terminal.ps1"),
                         daten=os.path.join(RESEARCH, "mql5", "DEADBAND_Daten_Export.mq5"),
                         kalender=os.path.join(RESEARCH, "mql5", "DEADBAND_Kalender_Export.mq5"),
                         ea=patch_bauen.EA, intrabar=os.path.join(RESEARCH, "patch_intrabar.mq5")))
    assert aus.read_bytes() == open(os.path.join(RESEARCH, "export", "Export-Setup.cmd"), "rb").read()
