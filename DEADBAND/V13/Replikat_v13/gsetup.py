"""Live-Runde: Konfiguration des Marktes je Build - im Hauptprozess UND in jedem Rechenprozess (Windows startet die
Prozesse frisch, sie erben die Signale nicht). Builds: V8, V10, V12 und Varianten ueber kw (siehe configure)."""
import numpy as np

_CACHE = {}


def _sig():
    import cfg11 as C, gen11 as G
    if "S" not in _CACHE:
        S = C.signals()
        _CACHE["S"] = S
        _CACHE["live_at"] = G.portfolio_guard(S["fades"])
    return _CACHE["S"], _CACHE["live_at"]


def configure(build="V12", **kw):
    """Setzt Signale am Markt (evl11.mk()) und gibt die Stromparameter GP zurueck.
    kw: tick=("N1030",)  Tick-Fades (Name -> Risiko ueber tick_risk), tick_risk=0.50,
        off=("N1800",)   Stroeme abschalten, risk={"SRIB":0.15}  Risiko je Strom, sr_risk=0.10"""
    import cfg11 as C, evl11 as V, eng11 as E, cand11 as K
    S, live_at = _sig()
    m = V.mk()
    m.set_r21(S["r21"], S["reg"]); m.set_nz(S["nz"])
    if build == "V8":
        blocks = C.blocks(S, which=("fades", "special")); GP = C.gp_v8()
    else:
        blocks = C.blocks(S); GP = C.gp_v10(sr_risk=kw.get("sr_risk", 0.10))
    ticks = kw.get("tick", ("N1030",) if build == "V12" else ())
    for nm in ticks:
        I = C.STREAMS.index(nm)
        TB = K.tick_fade(nm, live_at=live_at)
        blocks = [(s_, TB, 1.0) if s_ == I else (s_, b, w) for (s_, b, w) in blocks]
        GP[I, E.GPI["risk"]] = kw.get("tick_risk", 0.50); GP[I, E.GPI["tpdelay"]] = 4
    if "xa_ein" in kw:                       # Live-Runde: XA-Einstieg verschieben (EA-Eingabe AsiaEinNY), z. B. -355 = 18:05 NY
        import gen11 as G
        if "xa_blk" not in _CACHE or _CACHE["xa_blk"][0] != kw["xa_ein"]:
            _CACHE["xa_blk"] = (kw["xa_ein"], G.xa(ein=kw["xa_ein"]))
        I = C.STREAMS.index("XA")
        blocks = [(s_, _CACHE["xa_blk"][1], 1.0) if s_ == I else (s_, b, w) for (s_, b, w) in blocks]
    for nm in kw.get("off", ()):
        GP[C.STREAMS.index(nm), E.GPI["on"]] = 0
    for nm, r in kw.get("risk", {}).items():
        GP[C.STREAMS.index(nm), E.GPI["risk"]] = r
    m.set_generic(blocks)
    return GP


def init_worker(build, kw):
    configure(build, **kw)
