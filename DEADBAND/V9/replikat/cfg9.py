"""Replikat 9 - Parameter von DEADBAND V8 Build 8.10 fuer den Kontomotor eng9 und Signalbloecke der Fade-artigen Module.

Quelle der Werte: Eingaben von DEADBAND_V8.mq5 (Build 8.10, 04.10.2026). Gegenueber den Eingaben bewusst gleich behandelt:
  - MinPayoutUSD 105 / ProfitSplit 0,8 -> Mindestgewinn 131,25 $ (KontoAb20260730, MinProfitPct 0)
  - gueltiger Tag 0,5 % + 0,50 $ Reserve (ValidDayReserveUSD) -> validpct 0,505
  - Zyklus 14 Tage (Kauf ab 21.09.2026, RegelAusKaufdatum), Floating-Firmengrenze 1,0 % (KontoAb20260902)
  - Abschluss-Ernte (AbschlussLetzte 5 = immer, MinR 0,3, alle Module) = eng6 "bank"
  - Gewinn-Ernte (GeRueckgangR 0, GeMinR 1,0, Aufschlag 0,05) = eng6 "ge" mit ge_mode 1
  - Serien-Stopp 3 bis 17:00 NY = eng6 cool_n 3, cool_days 0
  - RSI21-Einstand ab 1,0 R (+0,05 R), Noise-Einstand ab 0,5 R (+0,05 R)
Nicht abgebildet (wie in allen frueheren Replikaten): News-Sperre +-6 min, 130-s-Regel bei Gewinnschluessen ausser dem
Ziel ab der Folgekerze, Kontoerkenner (8.10: alle Faktoren neutral), Margin-Kuerzung (nur FirmaProfil 1).
"""
import datetime as dt
import numpy as np
import eng9 as E
import gen9 as G

V8 = dict(
    start=10000.0, fee=148.5, maxlosspct=6.0, rulefloat=1.0, ruleday=3.0, validpct=0.505, needvalid=5, cycledays=14,
    minpayout=105.0, split=0.80, paycap=6.0, paycapn=2, paydelay=2, rebuydelay=1,
    floatstop=0.80, floatgestuft=1, floatminsaldo=1, daystop=2.4, brakeslip=0.05, tagesrefeq=1,
    ddfull=3.5, ddmin=1.25, ddfmin=0.1, belowstart=0.95, gesamtbudget=0.9,
    db_on=0,
    r21_on=1, r21_risk=0.50, r21_goldmult=0.70, r21_w0=1.25, r21_w1=1.0, r21_w2=0.75, r21_budget=1.2,
    r21_rr_nas=2.2, r21_rr_gold=2.64, r21_exitbars=1152, r21_exitdays=8, r21_maxloss=2, r21_second=1,
    r21_ripeclose=1, r21_stopmult=1.0, r21_tp1r=1.0, r21_tp1f=0.0, r21_be=0.05, r21_first_mult=0.0,
    nz_on=1, nz_risk=0.45, nz_parts=3, nz_ripeclose=1, nz_be=0.5, nz_beplus=0.05,
    harvest=2, harvminr=2.0, harvmargin=0.05, harvfrom=16.0, harvpartial=1, harvminr2=0.5, harvgap=0.3,
    ge_on=1, ge_rueck=0.0, ge_minr=1.0, ge_auf=0.05, ge_mode=1,
    we_on=1, we_close=16.75, we_reentry=1, we_reif=1, we_stopmaxr=2.0, we_spreadr=0.15,
    slip_frac=0.0, stopmode=0,
    bank_on=1, bank_last=5, bank_minr=0.3, bank_from=0.0, bank_to=17.0, bank_margin=0.05, bank_mods=15, bank_prof=0.0,
    cool_n=3, cool_days=0,
    float_losers=1, rule_losers=1, idea_cap=0.9, lev=10.0, idea_margin=70.0, swap_guard=0.80, minlottol=2.0,
    gs_on=1, gs_r21_from=13.0,
)


def pv(**kw):
    c = dict(V8); c.update(kw)
    return E.params(**c)


# ------------------------------------------------------------------ handelsfreie US-Tage (NzFreierTag)
def _ostern(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4; f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; mo = (h + l - 7 * m + 114) // 31; da = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(y, mo, da)


def _nter(y, mo, wd, n):
    d = dt.date(y, mo, 1)
    d += dt.timedelta(days=(wd - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def _letzter(y, mo, wd):
    d = dt.date(y + (mo == 12), mo % 12 + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)


def _beob(d):
    return d - dt.timedelta(days=1) if d.weekday() == 5 else (d + dt.timedelta(days=1) if d.weekday() == 6 else d)


def us_freie_tage(y0=2009, y1=2027):
    """NYSE-Feiertage und verkuerzte Tage (Tag nach Thanksgiving, 24.12., 3.7.) wie die Liste NzFreierTag im EA,
    hier fuer alle Jahre nach Regel; vereinigt mit der EA-Liste 2019-2027 (sig5.FREI_DAYS)."""
    out = set()
    for y in range(y0, y1 + 1):
        tage = [_beob(dt.date(y, 1, 1)), _nter(y, 1, 0, 3), _nter(y, 2, 0, 3), _ostern(y) - dt.timedelta(days=2),
                _letzter(y, 5, 0), _beob(dt.date(y, 7, 4)), _nter(y, 9, 0, 1), _nter(y, 11, 3, 4), _beob(dt.date(y, 12, 25))]
        if y >= 2022:
            tage.append(_beob(dt.date(y, 6, 19)))
        tg = _nter(y, 11, 3, 4)
        tage += [tg + dt.timedelta(days=1), dt.date(y, 12, 24), dt.date(y, 7, 3)]
        for d in tage:
            if d.weekday() < 5:
                out.add((d - dt.date(1970, 1, 1)).days)
    import sig5
    return out | set(sig5.FREI_DAYS)


# ------------------------------------------------------------------ Signalbloecke fuer eng9
def gp_v8(module, teilziel=False):
    """Je Modul ein generischer Strom: Risiko, 1 Trade je Tag, Ziel ab der Folgekerze, Abschluss-Ernte, bei Reife schliessen.
    teilziel (V9-Test): die Haelfte am Teilziel je Signal schliessen, Stop danach auf Einstand + 0,05 R."""
    return E.gparams([dict(on=1, risk=m["risk"], maxtrades=1, harv=1, ripeclose=1, usefak=1, tpdelay=1,
                           minbuf=m.get("minbuf", 0.0), gsfrei=1.0 if m.get("frei") else 0.0,
                           **(dict(tp1f=0.5, be=0.05) if teilziel and m["typ"] == 0 else {})) for m in module])


def bloecke(sigs, frei, min_stop_spreads=6.0, D=None, maske=None, gewicht=None):
    """Live-Signale (Waechter, Feiertage, Stop >= 6 Spreads) als Bloecke fuer Market.set_generic.
    maske/gewicht: optional je Modulname ein bool-/float-Array ueber alle Signale (V9-Filter, halbe Groesse)."""
    out = []
    for s_, s in enumerate(sigs):
        n = len(s["t_entry"])
        ok = s["live"].copy()
        dE = s["t_entry"] // 1440; dX = s["xm"] // 1440
        ok &= ~np.isin(dE, list(frei)) & ~np.isin(dX, list(frei))
        if min_stop_spreads > 0 and D is not None:
            spE = D[s["sym"]]["sp"][s["i_entry"]]
            ok &= s["rd"] >= min_stop_spreads * spE
        if maske is not None and s["name"] in maske:
            ok &= maske[s["name"]]
        w = np.ones(n)
        if gewicht is not None and s["name"] in gewicht:
            w = w * gewicht[s["name"]]
        ok &= w > 0
        tp = np.where(s["goal"] > 0, (s["goal"] - s["ent"]) * s["dir"] / s["rd"], 0.0)
        tp1 = np.where(s["t1"] > 0, (s["t1"] - s["ent"]) * s["dir"] / s["rd"], 0.0)          # V9: Teilziel in R
        out.append(dict(str=s_, sym=np.full(ok.sum(), G.SYMI[s["sym"]], np.int64), dir=s["dir"][ok], t_entry=s["t_entry"][ok],
                        rd=s["rd"][ok], tp=tp[ok], t_exit=s["xm"][ok], w=w[ok], tp1=tp1[ok]))
    return out
