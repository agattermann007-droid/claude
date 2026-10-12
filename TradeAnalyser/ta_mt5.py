#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trade-Analyser MT5: liest die Kerzen aus dem MT5-Exporter (TA_Export) und
rechnet Regime, Entry, Stop, Target, CRV und Begruendung deterministisch.
Portierung des TradingView-Scripts (Pruefsumme 6bbd3904), Datenquelle MT5.

mt5-1.4: JEDES Signal ist eine Market-Order zum aktuellen Kurs (keine Limits mehr). Regime wie bisher (30min-Supertrend
+ Seite zum 30min-VWAP, Range ueber 5min-VWAP-Kreuzungen). Gehandelt wird nur im Trend und nur in der Haupthandelszeit:
Einstieg, wenn die letzte geschlossene 5min-Kerze gegen den Trend geschlossen hat (Ruecksetzer) und der Kurs
RS_MIN_ATR..RS_MAX_ATR x ATR5 vom Hoch (Long) / Tief (Short) der letzten RS_KERZEN Kerzen entfernt ist.
Stop STOP_ATR x ATR5 hinter dem Entry, Target ZIEL_R x Risiko (mindestens MINZIEL). Range: kein Trade.
Die Regeln von mt5-1.3 (Limit-Leiter) rechnet jeder Lauf weiter im Schatten mit (SET_ALT, Regelvergleich in --auswerten).

Aufruf:
  python3 ta_mt5.py --zeit 2026-10-01T14:03:12+02:00 --news '[["CPI","08:30","ET"]]' [--nur NAS100|GER40|ETH]
  python3 ta_mt5.py --zeit 2026-10-01T14:03:12+02:00 --auswerten      (Signal-Log gegen die M5-Kerzen auswerten, Form L)
Ausgabe: JSON auf stdout mit "form" (A/B/C, bei --auswerten L), "ausgabe" (fertiger Antworttext),
"chart" (PNG-Pfad oder null) und "ergebnisse" (Rohdaten je Instrument).
"""
import argparse
import json
import math
import os
import re
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

TA_VERSION = 'mt5-1.4'
ALT_VERSION = 'mt5-1.3'  # Regelvergleich: jeder Lauf rechnet zusaetzlich die Regeln dieser Fassung (Schatten-Spur)

# STELLSCHRAUBEN: Regelwerte nur hier aendern.
SET = dict(MIN_CRV=1.5, MIN_STOP_ATR=1.0, ZIEL_STUFEN=2, PUFFER_INDEX_PCT=0.05, PUFFER_ETH_PCT=0.15,
           MINZIEL_INDEX_PCT=0.2, MINZIEL_ETH_PCT=0.3, RANGE_KREUZUNGEN=4, RESET_MIN=60, FLAG_AB_MIN=30,
           GESCHLOSSEN_MIN=15, NEWS_VOR_MIN=30, NEWS_NACH_MIN=15, LIMIT_MIN_GUELTIG=0, KERZENABGLEICH_PCT=0.1,
           SPERRE_NAS_NY=('09:25', '09:45'), SPERRE_DAX_WIEN=('08:55', '09:15'),
           EXPORT_MAX_ALT_S=120, AUSWERT_HORIZONT_MIN=480, KNAPP_ATR=0.1, WDH_ATR=0.5, ST_ATR=10, ST_FAKTOR=3.0, CHART_KERZEN=212,
           ZIEL_VOR_KURS=True, ZIELVORLAUF_MIN=0.25, MARKT_LEVELKERZE=True,  # neu in mt5-1.3: zwei Schalter und der Mindest-Zielvorlauf
           PRUEF_TRADES=(50, 100, 150), PRUEF_Z_ZURUECK=(2.0, 1.8, 1.65), PRUEF_Z_BESSER=1.96,  # Regelvergleich: feste Pruefpunkte statt Dauertest
           # neu in mt5-1.4: nur Market-Orders (MARKT_MODUS=False = Regeln von mt5-1.3; MIN_CRV, ZIEL_STUFEN, ZIEL_VOR_KURS, ZIELVORLAUF_MIN, MARKT_LEVELKERZE gelten nur dort)
           MARKT_MODUS=True,
           HANDELSZEIT_NAS_NY=('09:45', '15:30'), HANDELSZEIT_DAX_WIEN=('09:15', '17:00'), HANDELSZEIT_ETH_NY=('09:45', '15:30'),  # Einstieg nur Mo-Fr von..bis (bis exklusiv)
           RS_KERZEN=12, RS_MIN_ATR=0.25, RS_MAX_ATR=1.5,  # Ruecksetzer: Kurs RS_MIN_ATR..RS_MAX_ATR x ATR5 unter dem Hoch (Long) / ueber dem Tief (Short) der letzten RS_KERZEN geschlossenen 5min-Kerzen
           STOP_ATR=3.0, ZIEL_R=0.75)  # Stop STOP_ATR x ATR5 hinter dem Entry (mindestens MIN_STOP_ATR); Target ZIEL_R x Risiko, mindestens MINZIEL
SET_ALT = dict(SET, MARKT_MODUS=False)  # Regeln von mt5-1.3 (Limit-Leiter), nur fuer den Schatten-Vergleich

INSTR = [('NAS100', 'INDEX'), ('GER40', 'INDEX'), ('ETH', 'ETH')]
ALIAS = {'NAS100': 'NAS100', 'NAS': 'NAS100', 'NASDAQ': 'NAS100', 'US100': 'NAS100',
         'GER40': 'GER40', 'DAX': 'GER40', 'ETH': 'ETH', 'ETHUSD': 'ETH'}
ZONEN = {'ET': 'America/New_York', 'EST': 'America/New_York', 'EDT': 'America/New_York',
         'CET': 'Europe/Vienna', 'CEST': 'Europe/Vienna', 'MEZ': 'Europe/Vienna', 'MESZ': 'Europe/Vienna',
         'WIEN': 'Europe/Vienna', 'GMT': 'UTC', 'UTC': 'UTC', 'BST': 'Europe/London'}
WIEN = ZoneInfo('Europe/Vienna')
NY = ZoneInfo('America/New_York')
SIG = 'σ'


# ---------- kleine Helfer (verhalten sich wie im JS-Original) ----------
def jsround(x):
    return int(math.floor(x + 0.5))


def f(x):
    return str(jsround(x))


def fc(x):
    return ('%.1f' % (math.floor(x * 10) / 10)).replace('.', ',')


def jsfixed(x, n):
    """Wie JS (x).toFixed(n): exakter Binaerwert, bei Gleichstand aufrunden (vom Null weg)."""
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(x).quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP))


def jsnum(x):
    return str(int(x)) if float(x).is_integer() else repr(float(x))


def hm_wien(ms):
    return datetime.fromtimestamp(ms / 1000, WIEN).strftime('%H:%M')


def hhmm(s):
    m = re.match(r'^(\d{1,2}):(\d{2})$', str(s))
    return int(m.group(1)) * 60 + int(m.group(2)) if m and int(m.group(1)) < 24 and int(m.group(2)) < 60 else None


def min_of_day(ms, tz):
    d = datetime.fromtimestamp(ms / 1000, tz)
    return d.hour * 60 + d.minute


def news_events(news, zeit_ms):
    """NEWS-Liste [['Name','HH:MM','ZONE'], ...] -> sortierte Termine (UTC-ms). Datum = heutiger Wiener Tag."""
    ev = []
    heute = datetime.fromtimestamp(zeit_ms / 1000, WIEN)
    for n in news or []:
        tz = ZONEN.get(str(n[2] if isinstance(n, (list, tuple)) and len(n) > 2 else '').upper())
        m = re.match(r'^(\d{1,2}):(\d{2})$', str(n[1] if isinstance(n, (list, tuple)) and len(n) > 1 else ''))
        if not tz or not m or int(m.group(1)) > 23 or int(m.group(2)) > 59:
            raise ValueError('News-Angabe ungueltig: ' + json.dumps(n, ensure_ascii=False))
        t = datetime(heute.year, heute.month, heute.day, int(m.group(1)), int(m.group(2)), tzinfo=ZoneInfo(tz))
        name = re.sub(r'[.!?;]', '', str(n[0])).strip() or 'Termin'
        ev.append({'name': name, 't': t.timestamp() * 1000})
    return sorted(ev, key=lambda e: e['t'])


# ---------- Indikatoren ----------
def vwap_baender(B, daykey):
    """Session-VWAP (hlc3, Volumen) mit +-1/2/3 Standardabweichung, Reset bei neuem daykey.
    Rueckgabe: Liste je Kerze [vwap, up1, lo1, up2, lo2, up3, lo3] (Reihenfolge wie TradingView)."""
    out, pv, v, pv2, cur = [], 0.0, 0.0, 0.0, None
    for b in B:
        k = daykey(b)
        if k != cur:
            pv = v = pv2 = 0.0
            cur = k
        src = (b[2] + b[3] + b[4]) / 3
        vol = b[5] if len(b) > 5 and b[5] > 0 else 1.0
        pv += src * vol
        v += vol
        pv2 += src * src * vol
        vw = pv / v
        sd = math.sqrt(max(pv2 / v - vw * vw, 0.0))
        if sd < abs(vw) * 1e-9:
            sd = 0.0
        out.append([vw, vw + sd, vw - sd, vw + 2 * sd, vw - 2 * sd, vw + 3 * sd, vw - 3 * sd])
    return out


def supertrend(B, laenge, faktor):
    """ta.supertrend wie in TradingView (hl2, ATR als RMA). Rueckgabe je Kerze (dir, wert), dir 1 = Long."""
    n = len(B)
    tr = [B[0][2] - B[0][3]] + [max(B[i][2] - B[i][3], abs(B[i][2] - B[i - 1][4]), abs(B[i][3] - B[i - 1][4])) for i in range(1, n)]
    atr = [None] * n
    for i in range(n):
        if i == laenge - 1:
            atr[i] = sum(tr[:laenge]) / laenge
        elif i >= laenge:
            atr[i] = (atr[i - 1] * (laenge - 1) + tr[i]) / laenge
    res, pu, pl, pst, pdir = [], None, None, None, 1
    for i in range(n):
        if atr[i] is None:
            res.append((None, None))
            continue
        hl2 = (B[i][2] + B[i][3]) / 2
        up, lo = hl2 + faktor * atr[i], hl2 - faktor * atr[i]
        if pl is not None and not (lo > pl or B[i - 1][4] < pl):
            lo = pl
        if pu is not None and not (up < pu or B[i - 1][4] > pu):
            up = pu
        if i == 0 or atr[i - 1] is None:
            tvdir = 1  # TradingView: erste Kerze mit ATR -> dir = 1 (Short)
        elif pst == pu:
            tvdir = -1 if B[i][4] > up else 1
        else:
            tvdir = 1 if B[i][4] < lo else -1
        st = lo if tvdir == -1 else up
        res.append((1 if tvdir == -1 else -1, st))
        pu, pl, pst = up, lo, st
    return res


# ---------- Datenaufbereitung ----------
def baue(B, V, sec, st=None):
    """B: Kerzen [t_utc, o, h, l, c, (vol)] aufsteigend, letzte = laufende Kerze. V: Liste der VWAP-Werte je Kerze.
    Bildet dieselbe Struktur wie load() im JS-Original."""
    if len(B) < 60:
        raise RuntimeError('zu wenige Kerzen')
    last = B[-1]
    r = -1
    for i in range(len(B) - 1, -1, -1):
        v = V[i]
        if abs(v[1] - v[2]) <= B[i][4] * 1e-6:
            r = i
            break
    if r < 0:
        raise RuntimeError('VWAP-Reset nicht gefunden')
    day = B[r:]
    hi = max(b[2] for b in day)
    lo = min(b[3] for b in day)
    Vm = {B[i][0]: V[i] for i in range(len(B))}
    o = {'B': B, 'V': Vm, 'r': r, 'day': day, 'hi': hi, 'lo': lo, 'v': V[-1], 'last': last}
    if st is not None:
        d, w = st[-2]
        if d is None:
            raise RuntimeError('Supertrend-Werte fehlen')
        o['st'] = {'dir': d, 'wert': w}
    return o


# ---------- Regelwerk (1:1 aus dem JS-Original) ----------
def analysiere(NAME, KL, A, F, now_ms, ev, Z=SET):
    """A = 30min-Daten (mit st), F = 5min-Daten. ev = sortierte News-Termine. Ergebnis wie window.__TA."""
    MIN_CRV, MIN_STOP_ATR, ZIEL_STUFEN = Z['MIN_CRV'], Z['MIN_STOP_ATR'], Z['ZIEL_STUFEN']
    FLAG_AB_MIN, LIMIT_MIN_GUELTIG = Z['FLAG_AB_MIN'], Z['LIMIT_MIN_GUELTIG']
    NEWS_VOR_MIN = Z['NEWS_VOR_MIN']
    PUF = (Z['PUFFER_ETH_PCT'] if KL == 'ETH' else Z['PUFFER_INDEX_PCT']) / 100
    MINZ = (Z['MINZIEL_ETH_PCT'] if KL == 'ETH' else Z['MINZIEL_INDEX_PCT']) / 100
    now = now_ms / 1000
    ZU = Z['GESCHLOSSEN_MIN'] * 60

    def zu(t):
        return {'instrument': NAME, 'status': 'geschlossen', 'grund': NAME + '-Markt geschlossen, letzte Kerze ' + hm_wien(t * 1000) + ' Wiener Zeit'}

    if now - (A['last'][0] + 1800) > ZU:
        return zu(A['last'][0])
    if now - (F['last'][0] + 300) > ZU:
        return zu(F['last'][0])
    abw = 0
    for k in A['B'][-4:-1]:
        g = [b for b in F['B'] if k[0] <= b[0] < k[0] + 1800]
        if len(g) != 6:
            continue
        h = max(b[2] for b in g)
        l = min(b[3] for b in g)
        if abs(h - k[2]) > k[2] * Z['KERZENABGLEICH_PCT'] / 100 or abs(l - k[3]) > k[3] * Z['KERZENABGLEICH_PCT'] / 100:
            abw += 1
    if abw:
        return {'instrument': NAME, 'fehler': '30min- und 5min-Kerzen passen nicht zusammen (' + NAME + ')'}

    B = F['B']
    C = B[:-1]
    lc = C[-1]
    kurs = F['last'][4]
    P = PUF * kurs
    vwap, up1, lo1, up2, lo2, up3, lo3 = F['v']
    LV = [lo3, lo2, lo1, vwap, up1, up2, up3]
    LB = ['-3' + SIG, '-2' + SIG, '-1' + SIG, 'VWAP', '+1' + SIG, '+2' + SIG, '+3' + SIG]
    LN = ['5min-VWAP' if i == 3 else '5min-Band ' + b for i, b in enumerate(LB)]
    kreuz, prev, unterUp1, ueberLo1 = 0, None, False, False
    for b in F['day'][:-1]:
        v = F['V'].get(b[0])
        if not v:
            continue
        side = 1 if b[4] > v[0] else -1
        if prev is not None and side != prev:
            kreuz += 1
        prev = side
        if b[0] - F['day'][0][0] < FLAG_AB_MIN * 60:
            continue
        if b[4] < v[1]:
            unterUp1 = True
        if b[4] > v[2]:
            ueberLo1 = True
    L = C[-80:]
    sh, sl = [], []
    for i in range(2, len(L) - 2):
        if L[i][2] > L[i - 1][2] and L[i][2] > L[i - 2][2] and L[i][2] >= L[i + 1][2] and L[i][2] >= L[i + 2][2]:
            sh.append(L[i][2])
        if L[i][3] < L[i - 1][3] and L[i][3] < L[i - 2][3] and L[i][3] <= L[i + 1][3] and L[i][3] <= L[i + 2][3]:
            sl.append(L[i][3])
    trs = 0.0
    for i in range(len(C) - 14, len(C)):
        trs += max(C[i][2] - C[i][3], abs(C[i][2] - C[i - 1][4]), abs(C[i][3] - C[i - 1][4]))
    atr = trs / 14
    minReset = math.floor((now - B[F['r']][0]) / 60)
    wien, ny = min_of_day(now_ms, WIEN), min_of_day(now_ms, NY)

    def inF(x, w):
        return hhmm(w[0]) <= x <= hhmm(w[1])
    marketGesperrt = (NAME == 'NAS100' and inF(ny, Z['SPERRE_NAS_NY'])) or (NAME == 'GER40' and inF(wien, Z['SPERRE_DAX_WIEN']))
    k30, v30, stDir = A['last'][4], A['v'][0], A['st']['dir']
    seite = 1 if k30 > v30 else -1 if k30 < v30 else 0
    rangeWegen = 'W' if seite != stDir else ('K' if (kreuz >= Z['RANGE_KREUZUNGEN'] and lo1 < kurs < up1) else None)
    daten = {
        'zeitUTC': datetime.utcfromtimestamp(F['last'][0]).strftime('%Y-%m-%dT%H:%M'),
        'wien': '%02d:%02d' % (wien // 60, wien % 60), 'kurs': kurs,
        'regime30': {'supertrend': 'LONG' if stDir > 0 else 'SHORT', 'stWert': jsfixed(A['st']['wert'], 2), 'kurs30': k30, 'vwap30': jsfixed(v30, 2)},
        'vwap5': {b: jsfixed(LV[i], 2) for i, b in enumerate(LB)}, 'kerze5': lc[1:5],
        'kreuz': kreuz, 'unterUp1': unterUp1, 'ueberLo1': ueberLo1, 'minReset': minReset, 'atr5': jsfixed(atr, 2),
        'tagesHoch': F['hi'], 'tagesTief': F['lo'], 'swingHochs': sh[-6:], 'swingTiefs': sl[-6:], 'marketGesperrt': marketGesperrt}
    if Z['MARKT_MODUS']:  # mt5-1.4: eigene Reihenfolge (Sperre und Handelszeit vor dem VWAP-Reset), sonst wie unten
        return markt_signal(NAME, KL, Z, daten, kurs, atr, C, lc, MINZ, A, stDir, rangeWegen, k30, v30, seite, kreuz, lo1, up1, now_ms,
                            next((e for e in ev if e['t'] > now_ms), None), minReset)
    if minReset < Z['RESET_MIN']:
        return {'instrument': NAME, 'status': 'Kein Trade', 'grund': 'VWAP-Reset erst vor ' + str(minReset) + ' Minuten', 'daten': daten}

    fails = []
    naechste = next((e for e in ev if e['t'] > now_ms), None)

    def pruefe(d, klasse, E0, markt, S0, sTxt, tg, zs):
        E = jsround(E0) if markt else (math.ceil(E0) if d > 0 else math.floor(E0))
        if not markt and not (E < kurs if d > 0 else E > kurs):
            fails.append('Limit auf falscher Kursseite')
            return None
        if not markt and marketGesperrt and abs(E0 - kurs) <= P:
            fails.append('Limit in der Eröffnungssperre zu nah am Kurs')
            return None
        if not markt and naechste and naechste['t'] - NEWS_VOR_MIN * 60000 - now_ms < LIMIT_MIN_GUELTIG * 60000:
            fails.append('Limit wäre vor ' + naechste['name'] + ' kaum noch gültig')
            return None
        S = S0
        if d * (E - S) < MIN_STOP_ATR * atr:
            S = E - d * MIN_STOP_ATR * atr
            sTxt = 'auf Mindestabstand ' + jsnum(MIN_STOP_ATR).replace('.', ',') + ' ATR5 (' + f(atr) + ')'
        S = math.floor(S) if d > 0 else math.ceil(S)
        TT = [[b, math.floor(x) if d > 0 else math.ceil(x)] for b, x in tg]
        TT = sorted([t for t in TT if d * (t[1] - E) >= MINZ * E], key=lambda t: d * t[1])
        if not TT:
            fails.append('kein Target mit Mindestdistanz')
            return None
        ti0, weg = 0, ''  # ti0: weggefilterte Targets; 'zielstufe' zaehlt wie in mt5-1.1 ab dem ersten Target hinter dem Entry und bleibt <= zs (ZIEL_STUFEN)
        if not markt and Z['ZIEL_VOR_KURS']:  # mt5-1.3: Target muss noch vor dem Kurs liegen, sonst ist das Limit laut eigener Streich-Regel sofort tot
            # Target mehr als max(1 Puffer, ZIELVORLAUF_MIN x Abstand Kurs->Entry) vor dem Kurs. Grund: Ohne Drift wird ein Limit nur mit
            # Wahrscheinlichkeit v/(1+v) gefuellt, bevor der Kurs das Target erreicht (v = Abstand Kurs->Target / Abstand Kurs->Entry); bei 0,25 also 20 %.
            vor = max(P, Z['ZIELVORLAUF_MIN'] * d * (kurs - E))
            ti0 = len([t for t in TT if not d * (t[1] - kurs) > vor])
            weg = (' (' + TT[ti0 - 1][0] + ' ' + str(TT[ti0 - 1][1]) + (' schon vom Kurs erreicht)' if d * (TT[ti0 - 1][1] - kurs) <= P else ' zu nah am Kurs)')) if ti0 else ''
            TT = TT[ti0:]
            if not TT or ti0 > zs:  # Deckel ZIEL_STUFEN gilt weiter ab dem ersten Target hinter dem Entry, auch fuer weggefilterte Targets
                fails.append('Target schon vom Kurs erreicht oder zu nah')
                return None
        risk = d * (E - S)
        if not risk > 0:
            fails.append('kein Stop')
            return None
        ti = 0
        k = 1
        while k <= zs - ti0 and k < len(TT) and d * (TT[ti][1] - E) / risk < MIN_CRV:
            ti = k
            k += 1
        T = TT[ti]
        crv = d * (T[1] - E) / risk
        if crv < MIN_CRV:
            fails.append('CRV unter ' + fc(MIN_CRV))
            return None
        zTxt = weg + ('' if ti == 0 else ' (' + TT[0][0] + ' ' + str(TT[0][1]) + ' hätte nur CRV ' + fc(d * (TT[0][1] - E) / risk) + ')')
        return {'d': d, 'klasse': klasse, 'markt': markt, 'E': E, 'S': S, 'T': T, 'crv': crv, 'sTxt': sTxt, 'zTxt': zTxt, 'ti': ti + ti0}

    best, satz1 = None, ''
    if not rangeWegen:
        d = stDir
        R = 'Long' if d > 0 else 'Short'
        ladder = (([] if unterUp1 else [4]) + [3, 2]) if d > 0 else (([] if ueberLo1 else [2]) + [3, 4])
        tg = [[LN[i], LV[i]] for i in range(7)] + [['Tageshoch' if d > 0 else 'Tagestief', F['hi'] if d > 0 else F['lo']]]
        for zs in ([0, ZIEL_STUFEN] if ZIEL_STUFEN > 0 else [0]):
            for li in ladder:
                if best:
                    break
                lvl, bi = LV[li], li - d
                band = LV[bi]

                def stopFor(E):
                    sw = [x for x in sl if band <= x < E] if d > 0 else [x for x in sh if E < x <= band]
                    if sw:
                        x = max(sw) if d > 0 else min(sw)
                        return x - d * P, ('unter Swing-Tief ' if d > 0 else 'über Swing-Hoch ') + f(x) + (' minus' if d > 0 else ' plus') + ' Puffer'
                    return band - d * P, ('unter ' if d > 0 else 'über ') + LN[bi] + ' ' + f(band) + (' minus' if d > 0 else ' plus') + ' Puffer'
                amLevel = abs(kurs - lvl) <= P
                bestaetigt = lc[4] > lc[1] if d > 0 else lc[4] < lc[1]
                if Z['MARKT_LEVELKERZE']:  # mt5-1.3: die Kerze muss am Level abgelehnt haben (Docht in der Level-Zone, Schluss auf der Trendseite)
                    bestaetigt = bestaetigt and ((lc[3] <= lvl + P and lc[4] > lvl) if d > 0 else (lc[2] >= lvl - P and lc[4] < lvl))
                if amLevel and bestaetigt and not marketGesperrt:
                    best = pruefe(d, 'TREND', kurs, True, *stopFor(kurs), tg, zs)
                if not best:
                    best = pruefe(d, 'TREND', lvl, False, *stopFor(lvl), tg, zs)
                if best:
                    best['lab'], best['lvl'] = LN[li], lvl
        if best:
            satz1 = ('Trend ' + R + ', weil der 30min-Supertrend ' + R + ' bei ' + f(A['st']['wert']) + ' steht und der Kurs ' + f(k30)
                     + (' über' if d > 0 else ' unter') + ' dem 30min-VWAP ' + f(v30) + ' liegt; Setup ist ein Pullback an '
                     + best['lab'] + ' ' + f(best['lvl']) + (' mit bestätigender 5min-Kerze' + (' am Level' if Z['MARKT_LEVELKERZE'] else '') if best['markt'] else '') + '.')
    else:
        d = -1 if kurs >= vwap else 1
        R = 'Long' if d > 0 else 'Short'
        ladder = [[LN[1], lo2], ['Mitte 5min -2' + SIG + '/-3' + SIG, (lo2 + lo3) / 2]] if d > 0 else [[LN[5], up2], ['Mitte 5min +2' + SIG + '/+3' + SIG, (up2 + up3) / 2]]
        S0 = lo3 - P if d > 0 else up3 + P
        sTxt = ('unter ' + LN[0] + ' ' + f(lo3) + ' minus' if d > 0 else 'über ' + LN[6] + ' ' + f(up3) + ' plus') + ' Puffer'
        for lab, lvl in ladder:
            best = pruefe(d, 'RANGE', lvl, False, S0, sTxt, [['5min-VWAP', vwap]], 0)
            if best:
                best['lab'], best['lvl'] = lab, lvl
                break
        if best:
            if rangeWegen == 'W':
                why = ('der 30min-Supertrend ' + ('Long' if stDir > 0 else 'Short') + ' steht, der Kurs ' + f(k30) + ' aber '
                       + ('über' if seite > 0 else 'unter' if seite < 0 else 'auf') + ' dem 30min-VWAP ' + f(v30) + ' liegt')
            else:
                why = 'der Kurs heute ' + str(kreuz) + '-mal den 5min-VWAP gekreuzt hat und zwischen -1' + SIG + ' ' + f(lo1) + ' und +1' + SIG + ' ' + f(up1) + ' liegt'
            satz1 = 'Range, weil ' + why + '; Setup ist Mean Reversion ' + R + ' an ' + best['lab'] + ' ' + f(best['lvl']) + '.'
    if not best:
        return {'instrument': NAME, 'status': 'Kein Trade',
                'grund': ('Range' if rangeWegen else 'Trend') + '-Setup ohne gültigen Einstieg (' + ', '.join(dict.fromkeys(fails)) + ')', 'daten': daten}
    R = 'Long' if best['d'] > 0 else 'Short'
    dd, E, S, T = best['d'], best['E'], best['S'], best['T'][1]
    if not (dd * (E - S) > 0 and dd * (T - E) >= MINZ * E and dd * (T - E) / (dd * (E - S)) >= MIN_CRV and (best['markt'] or dd * (kurs - E) > 0)):
        return {'instrument': NAME, 'fehler': 'Script-Selbstpruefung fehlgeschlagen (' + '/'.join(map(str, [S, E, T])) + ')'}
    if not naechste:
        newsTxt = ''
    elif best['markt']:
        newsTxt = '; nächster News-Termin ' + naechste['name'] + ' um ' + hm_wien(naechste['t']) + ' Wiener Zeit'
    else:
        newsTxt = '; Limit gilt nur bis ' + hm_wien(naechste['t'] - NEWS_VOR_MIN * 60000) + ' Wiener Zeit wegen ' + naechste['name'] + ' um ' + hm_wien(naechste['t'])
    if not best['markt']:
        newsTxt = '; Limit streichen, wenn ' + str(T) + ' vor der Füllung erreicht wird' + newsTxt
    art = 'Market' if best['markt'] else 'Limit'
    return {
        'instrument': NAME, 'status': 'Trade', 'klasse': best['klasse'], 'orderart': art,
        'distanzPct': 0 if best['markt'] else jsfixed(abs(E - kurs) / kurs * 100, 3), 'crv': jsfixed(best['crv'], 2), 'crvTxt': fc(best['crv']),
        'grenzen': {'minCrv': MIN_CRV, 'minZielPct': jsfixed(MINZ * 100, 4)},
        'distanzATR': 0 if best['markt'] else jsfixed(abs(E - kurs) / max(atr, 1e-9), 2),
        'signal': {'d': dd, 'E': E, 'S': S, 'T': T, 'level': best['lab'], 'zielstufe': best['ti'], 'kurs': kurs, 'atr5': jsfixed(atr, 2),
                   'verfall': None if best['markt'] or not naechste else (naechste['t'] - NEWS_VOR_MIN * 60000) / 1000},
        'zeilen': [
            'Entry: ' + NAME + ' ' + R + ' ' + art + ' @ ' + str(E),
            'Target: ' + str(T),
            'Stop: ' + str(S),
            'Begründung: ' + satz1 + ' Stop ' + best['sTxt'] + ' bei ' + str(S) + ', Target ' + best['T'][0] + ' ' + str(T) + best['zTxt'] + ', CRV ' + fc(best['crv']) + newsTxt + '.'],
        'daten': daten}


def markt_signal(NAME, KL, Z, daten, kurs, atr, C, lc, MINZ, A, stDir, rangeWegen, k30, v30, seite, kreuz, lo1, up1, now_ms, naechste, minReset):
    """mt5-1.4: Market-Order zum aktuellen Kurs. Nur Trend, nur Haupthandelszeit, Einstieg im Ruecksetzer: die letzte geschlossene
    5min-Kerze schloss gegen den Trend und der Kurs liegt RS_MIN_ATR..RS_MAX_ATR x ATR5 vom Extrem der letzten RS_KERZEN Kerzen.
    Stop STOP_ATR x ATR5 hinter dem Entry, Target ZIEL_R x Risiko (mindestens MINZIEL). Rundung wie bisher: Long Stop und Target ab, Short auf."""
    def kein(grund):
        return {'instrument': NAME, 'status': 'Kein Trade', 'grund': grund, 'daten': daten}
    hz, tz, zone = ((Z['HANDELSZEIT_DAX_WIEN'], WIEN, ' Wiener Zeit') if NAME == 'GER40' else
                    (Z['HANDELSZEIT_ETH_NY'] if NAME == 'ETH' else Z['HANDELSZEIT_NAS_NY'], NY, ' New York'))
    jetzt = datetime.fromtimestamp(now_ms / 1000, tz)
    hm = jetzt.hour * 60 + jetzt.minute
    sp = Z['SPERRE_NAS_NY'] if NAME == 'NAS100' else Z['SPERRE_DAX_WIEN'] if NAME == 'GER40' else None
    if sp and hhmm(sp[0]) <= hm < hhmm(sp[1]):  # jede Order ist eine Market-Order: in der Eroeffnungssperre gar kein Trade (Ende exklusiv, die Handelszeit beginnt dort)
        return kein('Eröffnungssperre ' + sp[0] + '-' + sp[1] + zone + ', kein Market-Einstieg')
    if jetzt.weekday() > 4 or not hhmm(hz[0]) <= hm < hhmm(hz[1]):  # ausserhalb der Haupthandelszeit war der Trend im Test zu schwach und der Spread zu teuer
        return kein('außerhalb der Handelszeit (Einstiege nur Mo-Fr ' + hz[0] + '-' + hz[1] + zone + ')')
    if minReset < Z['RESET_MIN']:
        return kein('VWAP-Reset erst vor ' + str(minReset) + ' Minuten')
    if not atr > 0:
        return kein('ATR5 ist null')
    if rangeWegen:
        if rangeWegen == 'W':
            why = ('der 30min-Supertrend ' + ('Long' if stDir > 0 else 'Short') + ' steht, der Kurs ' + f(k30) + ' aber '
                   + ('über' if seite > 0 else 'unter' if seite < 0 else 'auf') + ' dem 30min-VWAP ' + f(v30) + ' liegt')
        else:
            why = 'der Kurs heute ' + str(kreuz) + '-mal den 5min-VWAP gekreuzt hat und zwischen -1' + SIG + ' ' + f(lo1) + ' und +1' + SIG + ' ' + f(up1) + ' liegt'
        return kein('Range-Phase, weil ' + why + ' (in Range-Phasen kein Trade)')
    d = stDir
    R = 'Long' if d > 0 else 'Short'
    N = Z['RS_KERZEN']
    ext = max(b[2] for b in C[-N:]) if d > 0 else min(b[3] for b in C[-N:])
    rs = d * (ext - kurs) / atr
    extTxt = ('Hoch' if d > 0 else 'Tief') + ' der letzten ' + str(N) + ' 5min-Kerzen ' + f(ext)
    rsTxt = ('%.2f' % max(rs, 0.0)).replace('.', ',')  # zwei Stellen, damit die Anzeige die Grenzen RS_MIN_ATR/RS_MAX_ATR nicht scheinbar verletzt
    if rs <= Z['RS_MIN_ATR']:
        return kein('Trend-Setup ohne gültigen Einstieg (kein Rücksetzer, Kurs nur ' + rsTxt + ' ATR5 vom ' + extTxt + ')')
    if rs > Z['RS_MAX_ATR']:
        return kein('Trend-Setup ohne gültigen Einstieg (Rücksetzer zu tief, Kurs ' + rsTxt + ' ATR5 vom ' + extTxt + ')')
    if not (lc[4] < lc[1] if d > 0 else lc[4] > lc[1]):
        return kein('Trend-Setup ohne gültigen Einstieg (letzte 5min-Kerze schloss nicht gegen den Trend)')
    E = jsround(kurs)
    sa = max(Z['STOP_ATR'], Z['MIN_STOP_ATR'])
    S = math.floor(E - d * sa * atr) if d > 0 else math.ceil(E - d * sa * atr)
    risk = d * (E - S)
    zr, mz = Z['ZIEL_R'] * risk, math.ceil(MINZ * E)  # Mindestziel in ganzen Punkten, nie darunter
    T = math.floor(E + max(zr, mz)) if d > 0 else math.ceil(E - max(zr, mz))
    if not risk > 0:
        return kein('Trend-Setup ohne gültigen Einstieg (kein Stop)')
    crv = d * (T - E) / risk
    if not (d * (T - E) >= MINZ * E and (S < E < T if d > 0 else T < E < S) and E == jsround(kurs)):
        return {'instrument': NAME, 'fehler': 'Script-Selbstpruefung fehlgeschlagen (' + '/'.join(map(str, [S, E, T])) + ')'}
    mzPct = Z['MINZIEL_ETH_PCT'] if KL == 'ETH' else Z['MINZIEL_INDEX_PCT']
    tTxt = (jsnum(Z['ZIEL_R']).replace('.', ',') + ' x Risiko') if zr >= mz else ('Mindestziel ' + jsnum(mzPct).replace('.', ',') + ' %')
    satz1 = ('Trend ' + R + ', weil der 30min-Supertrend ' + R + ' bei ' + f(A['st']['wert']) + ' steht und der Kurs ' + f(k30)
             + (' über' if d > 0 else ' unter') + ' dem 30min-VWAP ' + f(v30) + ' liegt; Setup ist ein Rücksetzer im Trend: die letzte 5min-Kerze schloss gegen den Trend und der Kurs liegt '
             + rsTxt + ' ATR5 ' + ('unter dem ' if d > 0 else 'über dem ') + extTxt + ', Einstieg sofort zum Marktpreis.')
    sTxt = jsnum(sa).replace('.', ',') + ' ATR5 = ' + str(risk) + ' Punkte ' + ('unter' if d > 0 else 'über') + ' dem Entry'
    newsTxt = ('; nächster News-Termin ' + naechste['name'] + ' um ' + hm_wien(naechste['t']) + ' Wiener Zeit') if naechste else ''
    return {
        'instrument': NAME, 'status': 'Trade', 'klasse': 'TREND', 'orderart': 'Market',
        'distanzPct': 0, 'crv': jsfixed(crv, 2), 'crvTxt': fc(crv), 'zielR': Z['ZIEL_R'],
        'grenzen': {'zielR': Z['ZIEL_R'], 'minZielPct': jsfixed(MINZ * 100, 4)},
        'distanzATR': 0,
        'signal': {'d': d, 'E': E, 'S': S, 'T': T, 'level': 'Rücksetzer vom ' + ('Hoch' if d > 0 else 'Tief'), 'zielstufe': -1, 'kurs': kurs,
                   'atr5': jsfixed(atr, 2), 'verfall': None},
        'zeilen': [
            'Entry: ' + NAME + ' ' + R + ' Market @ ' + str(E),
            'Target: ' + str(T),
            'Stop: ' + str(S),
            'Begründung: ' + satz1 + ' Stop ' + sTxt + ' bei ' + str(S) + ', Target ' + tTxt + ' bei ' + str(T) + ', CRV ' + fc(crv) + newsTxt + '.'],
        'daten': daten}


def instrument(NAME, KL, A, F, now_ms, ev, Z=SET):
    """News-Sperre zuerst (wie im Original), dann das Regelwerk."""
    sperre = next((e for e in ev if e['t'] - Z['NEWS_VOR_MIN'] * 60000 <= now_ms <= e['t'] + Z['NEWS_NACH_MIN'] * 60000), None)
    if sperre:
        return {'instrument': NAME, 'status': 'Kein Trade', 'grund': 'News-Sperre wegen ' + sperre['name'] + ' um ' + hm_wien(sperre['t']) + ' Wiener Zeit'}
    if isinstance(A, str) or isinstance(F, str):
        return {'instrument': NAME, 'fehler': A if isinstance(A, str) else F}
    return analysiere(NAME, KL, A, F, now_ms, ev, Z)


# ---------- Auswahl und Antworttext ----------
def auswahl(ergebnisse, einzel):
    ok = [e for e in ergebnisse if 'fehler' not in e]
    if not ok:
        return 'C', 'Technischer Fehler: ' + ergebnisse[0]['fehler'], None
    # Ausgefallene Instrumente nicht verschweigen (nur bei "setup"; einzeln gibt es Form C)
    hinweis = ''
    if not einzel and len(ok) < len(ergebnisse):
        hinweis = ' Nicht auswertbar (technischer Fehler): ' + ', '.join(e['instrument'] for e in ergebnisse if 'fehler' in e) + '.'
    kand = [e for e in ok if e.get('status') == 'Trade']
    if kand:
        reihen = [n for n, _ in INSTR]
        # mt5-1.4 (Feld zielR): das CRV am naechsten an ZIEL_R zuerst; ein hoeheres CRV entsteht nur, wenn das Mindestziel greift, und trifft seltener
        w = sorted(kand, key=lambda e: (e['klasse'] != 'TREND', e['orderart'] != 'Market', e['distanzPct'],
                                        abs(e['crv'] - e['zielR']) if 'zielR' in e else -e['crv'], reihen.index(e['instrument'])))[0]
        zeilen = list(w['zeilen'])
        zeilen[-1] += hinweis
        return 'A', '\n'.join(zeilen), w
    if einzel:
        return 'B', 'Kein Trade: ' + ok[0]['grund'] + '.', None
    gruende = [e['grund'] for e in ok]
    if len(set(gruende)) == 1:
        satz = gruende[0]
    else:
        satz = '; '.join(e['instrument'] + ' ' + (e['grund'] if not e['grund'].startswith(e['instrument']) else e['grund'][len(e['instrument']) + 1:]) for e in ok)
    return 'B', 'Kein Trade: ' + satz + '.' + hinweis, None


# ---------- Signal-Log und Auswertung (neu in mt5-1.1) ----------
SIGNALDATEI = 'signale.jsonl'
ERGEBNISDATEI = 'auswertung.jsonl'  # je bewertetem Signal eine angehaengte Zeile {"id", "ergebnis"}; beide Dateien werden nur ANGEHAENGT, nie ersetzt


def lies_jsonl(pfad):
    recs = []
    if os.path.exists(pfad):
        with open(pfad, encoding='utf-8') as fh:
            for z in fh:
                try:
                    x = json.loads(z)
                    if isinstance(x, dict):
                        recs.append(x)
                except ValueError:
                    pass  # halbe Zeile (Abbruch beim Schreiben) ueberspringen
    return recs


def lies_signale(d):
    """Signale mit ihrem Ergebnis (falls schon bewertet; bei mehreren Zeilen je id gilt die letzte)."""
    erg = {x['id']: x['ergebnis'] for x in lies_jsonl(os.path.join(d, ERGEBNISDATEI)) if 'id' in x and 'ergebnis' in x}
    recs = lies_jsonl(os.path.join(d, SIGNALDATEI))
    for r in recs:
        if r.get('id') in erg:
            r['ergebnis'] = erg[r['id']]
    return recs


def haenge_an(pfad, obj):
    """Haengt EINE Zeile an. Nie ersetzen oder loeschen (in verbundenen Ordnern blockt device_bash das Loeschen). Endet die Datei ohne
    Zeilenumbruch (abgebrochener Schreibvorgang), kommt zuerst ein Umbruch, sonst klebt die neue Zeile an der halben und beide gehen verloren."""
    pre = ''
    if os.path.exists(pfad) and os.path.getsize(pfad) > 0:
        with open(pfad, 'rb') as fh:
            fh.seek(-1, os.SEEK_END)
            if fh.read(1) != b'\n':
                pre = '\n'
    with open(pfad, 'a', encoding='utf-8') as fh:
        fh.write(pre + json.dumps(obj, ensure_ascii=False) + '\n')


def logge_signal(d, w, now_ms, offset, quelle, extra=None):
    """Haengt jedes ausgegebene Trade-Signal an signale.jsonl an (Grundlage fuer --auswerten). Rueckgabe: ('' oder Fehlertext, id oder None, 'vergleich' der geschriebenen bzw. schon vorhandenen Zeile).
    quelle 'schatten' = was die Regeln von ALT_VERSION im selben Lauf gewaehlt haetten (nur wenn abweichend; nicht ausgegeben, nur fuer den Regelvergleich).
    Alte Spur = echte Signale mit vergleich 'gleich' + Schatten-Zeilen; neue Spur = echte Signale mit vergleich gleich/anders/alt_kein.
    extra: Zusatzfelder (echtes Signal: 'vergleich' = gleich/anders/alt_kein/fehler; Schatten: 'paar' = id des echten Signals oder None. mt5-1.3 schrieb zusaetzlich 'grund')."""
    try:
        rec = {'id': ('schatten_' if quelle == 'schatten' else '') + w['instrument'] + '_' + datetime.fromtimestamp(now_ms / 1000, WIEN).strftime('%Y%m%d_%H%M%S'), 'version': TA_VERSION,
               'zeit': now_ms / 1000, 'inst': w['instrument'], 'art': w['orderart'], 'klasse': w['klasse'], 'crv': w['crv'],
               'distanzATR': w['distanzATR'], 'minReset': w['daten']['minReset'], 'offset': offset, 'quelle': quelle}
        rec.update(extra or {})
        rec.update(w['signal'])
        for r in lies_signale(d)[-40:]:  # Doppelaufruf kurz hintereinander nicht doppelt zaehlen. Echte gegen echte; Schatten gegen die alte Spur (Schatten + echte 'gleich')
            spur = (r.get('quelle') == 'schatten' or r.get('vergleich') == 'gleich') if quelle == 'schatten' else r.get('quelle') != 'schatten'
            if (spur and 'ergebnis' not in r and rec['zeit'] - r['zeit'] < 1800
                    and all(r.get(k) == rec[k] for k in ('inst', 'art', 'E', 'S', 'T'))):
                return '', r.get('id'), r.get('vergleich')
        haenge_an(os.path.join(d, SIGNALDATEI), rec)
        return '', rec['id'], rec.get('vergleich')
    except Exception as e:
        return 'Signal-Log nicht geschrieben: ' + type(e).__name__ + ' ' + str(e), None, None


def bewerte(r, K, bis):
    """Bewertet ein Signal gegen die GESCHLOSSENEN M5-Kerzen K ([t_utc, o, h, l, c, v]). Ergebnis-dict oder None (noch offen).
    bis = Datenhorizont in UTC-Sekunden = min(jetzt, Zeit des Exports): nur Kerzen, die bis dahin geschlossen sind, zaehlen, und ein Ergebnis
    OHNE Treffer (verfallen/nicht gefuellt/Zeitablauf) entsteht erst, wenn der Export das Fenster bis 'ende' ueberdeckt; sonst bleibt das Signal offen.
    Regeln (bewusst einfach): Beruehrung = Fuellung, kein Spread -> die Fuellquote ist eine OBERGRENZE (OPTIMISTISCH; 'knapp' zaehlt
    Fuellungen, die den Entry um weniger als KNAPP_ATR x ATR5 durchstossen haben). Bei der Reihenfolge pessimistisch: Stop und
    Target in derselben Kerze = Stop; Fuellung und Target in derselben Kerze = 'unklar' (nicht in R gezaehlt). Limit verfaellt
    zum Verfall-Zeitpunkt; nach AUSWERT_HORIZONT_MIN Minuten wird zum letzten Schluss bewertet. 'ende' = Ende der Kerze, in der das
    Signal entschieden wurde (UTC-Sekunden; Grundlage fuer Haltedauer und Wiederholungs-Erkennung)."""
    d, E, S, T = r['d'], r['E'], r['S'], r['T']
    risk = d * (E - S)
    start = (int(r['zeit']) // 300 + 1) * 300  # erste vollstaendige Kerze nach dem Signal
    ende = r['zeit'] + SET['AUSWERT_HORIZONT_MIN'] * 60
    if not K:
        return None  # leere Datei: nichts beurteilbar, offen lassen
    if K[0][0] > start:
        return {'status': 'unbewertbar', 'R': None, 'hinweis': 'M5-Historie beginnt nach dem Signal'}
    gefuellt, letzte, knapp, fuell = r['art'] == 'Market', None, None, None
    for t, o, h, l, c, v in K:
        if t < start:
            continue
        if t + 300 > bis or t >= ende:
            break
        letzte = c
        lg = d > 0
        hs = (l <= S) if lg else (h >= S)
        ht = (h >= T) if lg else (l <= T)
        if not gefuellt:
            if r.get('verfall') and t >= r['verfall']:
                return {'status': 'verfallen', 'R': 0.0, 'ende': r['verfall']}
            if (l <= E) if lg else (h >= E):
                gefuellt, fuell = True, t
                tiefe = ((E - l) if lg else (h - E)) / max(float(r.get('atr5') or 0), 1e-9)
                knapp = tiefe < SET['KNAPP_ATR']
                if hs:
                    return {'status': 'Stop', 'R': -1.0, 'fuellung': t, 'ende': t + 300, 'knapp': knapp, 'hinweis': 'Fuellung und Stop in derselben Kerze'}
                if ht:
                    return {'status': 'unklar', 'R': None, 'fuellung': t, 'ende': t + 300, 'knapp': knapp, 'hinweis': 'Fuellung und Target in derselben Kerze'}
            elif ht:
                return {'status': 'verworfen', 'R': 0.0, 'ende': t + 300, 'hinweis': 'Target vor der Fuellung beruehrt'}
            continue
        if hs:
            return {'status': 'Stop', 'R': -1.0, 'knapp': knapp, 'fuellung': fuell, 'ende': t + 300, 'hinweis': 'Stop und Target in derselben Kerze' if ht else ''}
        if ht:
            return {'status': 'Target', 'R': round(d * (T - E) / risk, 2), 'knapp': knapp, 'fuellung': fuell, 'ende': t + 300}
    if bis >= ende:
        if letzte is None:
            return {'status': 'unbewertbar', 'R': None, 'hinweis': 'keine M5-Kerzen im Zeitfenster'}
        return {'status': 'Zeitablauf', 'R': round(d * (letzte - E) / risk, 2), 'knapp': knapp, 'fuellung': fuell, 'ende': ende} if gefuellt else {'status': 'nicht gefuellt', 'R': 0.0, 'ende': ende}
    return None


def wilson(k, n, z=1.96):
    """95%-Intervall fuer einen Anteil k/n (Wilson)."""
    p = k / n
    nenner = 1 + z * z / n
    mitte = (p + z * z / (2 * n)) / nenner
    hb = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / nenner
    return '%d/%d = %d%% (95%%-Intervall %d-%d%%)' % (k, n, round(100 * k / n), round(100 * max(0, mitte - hb)), round(100 * min(1, mitte + hb)))


def lade_export(d, inst):
    """Status und M5-Kerzen (UTC) der Instrumente 'inst'. Wie main() mit bis zu 4 Versuchen: der MQL-Dienst schreibt die Dateien laufend
    neu, ein Lauf im Schreibfenster sieht sonst 'unvollstaendig'. Rueckgabe (offset, export_gmt, {inst: kerzen}, {inst: fehlertext})."""
    letzter = ''
    for versuch in range(4):
        try:
            st = lies_status(d)
            offset, bis = int(st['offset']), float(st['export_gmt'])
            K, fehl = {}, {}
            for n in inst:
                pfad = os.path.join(d, n + '_M5.csv')
                if not os.path.exists(pfad):
                    fehl[n] = 'Exportdatei ' + n + '_M5.csv fehlt'
                else:
                    K[n] = [[t - offset, o, h, l, c, v] for t, o, h, l, c, v in lies_kerzen(pfad)]
            return offset, bis, K, fehl
        except (OSError, RuntimeError, ValueError, KeyError) as e:
            letzter = str(e)
            if versuch < 3:
                time.sleep(1.2)
    raise RuntimeError(letzter)


def auswerten(d, now_ms):
    """Wertet offene Signale aus signale.jsonl gegen die M5-Kerzen aus und liefert (Form, Text)."""
    try:
        recs = lies_signale(d)
    except OSError as e:
        return 'C', 'Technischer Fehler: ' + SIGNALDATEI + ' nicht lesbar (' + str(e) + ')'
    if not recs:
        return 'L', 'Auswertung: noch keine Signale in ' + SIGNALDATEI + ' (wird bei jedem ausgegebenen Trade angelegt).'
    now_s, fehler = now_ms / 1000, []
    offen = [r for r in recs if 'ergebnis' not in r]
    if offen:
        try:
            offset, bis, K, fehl = lade_export(d, sorted({r['inst'] for r in offen}))
        except RuntimeError as e:
            # gleicher Anfang wie der Lesefehler im Hauptpfad: SKILL.md wiederholt solche Laeufe einmal
            return 'C', 'Technischer Fehler: MT5-Export nicht lesbar (' + str(e) + ')'
        bis = min(now_s, bis)  # Datenhorizont: nie ueber den Stand des Exports hinaus (steht der Export, bleiben Zeitablauf-Signale offen)
        fehler += [n + ': ' + t for n, t in fehl.items()]
        for r in offen:
            if r['inst'] not in K:
                continue
            if int(r.get('offset', offset)) != offset:
                # Serverzeit-Umstellung seit dem Signal: die CSV-Zeiten vor und nach der Umstellung liegen um 1 h versetzt, ohne dass das Script den Zeitpunkt kennt
                res = {'status': 'unbewertbar', 'R': None, 'hinweis': 'Serverzeit-Umstellung (Offset %s -> %s) vor der Auswertung' % (r.get('offset'), offset)}
            else:
                try:
                    res = bewerte(r, K[r['inst']], bis)
                except (ValueError, KeyError, IndexError) as e:
                    fehler.append(r['inst'] + ': ' + type(e).__name__ + ' ' + str(e))
                    continue
            if res:
                try:
                    haenge_an(os.path.join(d, ERGEBNISDATEI), {'id': r['id'], 'ergebnis': res})
                except OSError as e:
                    fehler.append('Ergebnis nicht gespeichert (' + type(e).__name__ + ' ' + str(e) + '); gilt nur für diese Ausgabe')
                r['ergebnis'] = res
    # Wiederholungen (protokolliert, aber in keiner Statistik gezaehlt): gleiches Instrument und gleiche Richtung wie das letzte GEZAEHLTE Signal v, und
    # (a) v war zu diesem Zeitpunkt IM MARKT (gefuellt, noch nicht entschieden): gleiches Risiko; oder (b) v's Order lebte noch (nicht gefuellt/entschieden)
    # und der neue Entry liegt innerhalb WDH_ATR x ATR5 von v's Entry: dieselbe Order, nur neu angesagt. Ein wartendes oder nie gefuelltes Limit
    # macht ein Signal mit anderem Level NICHT zur Wiederholung (eigener Versuch). Keine Abhaengigkeit vom spaeteren Ausgang.
    imm = lambda v: 'ergebnis' in v and v['ergebnis']['status'] in ('Target', 'Stop', 'Zeitablauf', 'unklar')
    bis_v = lambda v: v['ergebnis'].get('ende', v['zeit']) if 'ergebnis' in v else 1e18

    def wiederholungen(liste):
        letzte, wdh = {}, set()
        for r in sorted(liste, key=lambda x: x['zeit']):
            k = (r['inst'], r['d'])
            v = letzte.get(k)
            if v is not None and v['zeit'] <= r['zeit'] < bis_v(v) and (
                    (imm(v) and (v['ergebnis'].get('fuellung') or v['zeit']) <= r['zeit'])
                    or abs(r['E'] - v['E']) <= SET['WDH_ATR'] * max(float(v.get('atr5') or 0), 1e-9)):
                wdh.add(r['id'])
            else:
                letzte[k] = r
        return wdh
    schatten = [r for r in recs if r.get('quelle') == 'schatten']  # mt5-1.3: Wahl der alten Regeln, eigene Spur, in keiner Hauptstatistik
    recs = [r for r in recs if r.get('quelle') != 'schatten']
    wdh = wiederholungen(recs)
    alle = len(recs)
    recs_w = recs
    recs = [r for r in recs if r['id'] not in wdh]
    reif_ab = now_s - SET['AUSWERT_HORIZONT_MIN'] * 60  # nur Signale, deren Auswertefenster zu ist: sonst steht ein schon gefuellter Gewinner im Nenner, ein noch wartendes Limit nicht
    erl = [r for r in recs if 'ergebnis' in r and r['zeit'] <= reif_ab]
    jung = [r for r in recs if r['zeit'] > reif_ab]
    st = lambda r: r['ergebnis']['status']
    fill = [r for r in erl if st(r) in ('Target', 'Stop', 'Zeitablauf', 'unklar')]
    rr = [r for r in fill if r['ergebnis']['R'] is not None]
    summe = sum(r['ergebnis']['R'] for r in rr)
    med = lambda xs: sorted(xs)[len(xs) // 2]
    z = ['Signale %d (davon %d Wiederholungen, nicht gezählt; %d aus Einzelabfragen) | gezählt und reif %d | noch nicht reif (jünger als %d min) %d | offen trotz Alter (Export deckt das Fenster noch nicht ab) %d | unbewertbar %d | unklar %d'
         % (alle, len(wdh), sum(r.get('quelle') == 'einzel' for r in recs_w), len(erl), SET['AUSWERT_HORIZONT_MIN'], len(jung),
            sum('ergebnis' not in r for r in recs if r['zeit'] <= reif_ab), sum(st(r) == 'unbewertbar' for r in erl), sum(st(r) == 'unklar' for r in erl))]
    lim = [r for r in erl if r['art'] == 'Limit' and st(r) != 'unbewertbar']
    if lim:
        z.append('Limit gefüllt (Obergrenze): ' + wilson(sum(st(r) in ('Target', 'Stop', 'Zeitablauf', 'unklar') for r in lim), len(lim)))
        for lab, lo, hi in (('unter 1', 0, 1), ('1 bis 2', 1, 2), ('2 bis 3', 2, 3), ('ab 3', 3, 1e9)):
            g = [r for r in lim if lo <= float(r.get('distanzATR', 0)) < hi]
            if g:
                z.append('  Entfernung %s ATR5: %d von %d gefüllt' % (lab, sum(st(r) in ('Target', 'Stop', 'Zeitablauf', 'unklar') for r in g), len(g)))
        zv = lambda r: r['d'] * (r['T'] - r['kurs']) / max(r['d'] * (r['kurs'] - r['E']), 1e-9)  # mt5-1.3: Zielvorlauf = Abstand Kurs->Target / Abstand Kurs->Entry beim Ansagen
        for lab, lo, hi in (('unter 0,25', -1e9, 0.25), ('0,25 bis 0,5', 0.25, 0.5), ('0,5 bis 1', 0.5, 1), ('ab 1', 1, 1e9)):
            g = [r for r in lim if 'kurs' in r and lo <= zv(r) < hi]
            if g:
                z.append('  Zielvorlauf %s: %d Limits, %d gefüllt, %d verworfen' % (lab, len(g), sum(st(r) in ('Target', 'Stop', 'Zeitablauf', 'unklar') for r in g), sum(st(r) == 'verworfen' for r in g)))
        wz = [(r['ergebnis']['fuellung'] - r['zeit']) / 60 for r in lim if st(r) in ('Target', 'Stop', 'Zeitablauf', 'unklar') and r['ergebnis'].get('fuellung')]
        if wz:
            z.append('  Wartezeit bis Füllung: Median %d min, Spanne %d bis %d min (%d Füllungen, auf die M5-Kerze genau)' % (med(wz), min(wz), max(wz), len(wz)))
    tz, sz = sum(st(r) == 'Target' for r in fill), sum(st(r) == 'Stop' for r in fill)
    if tz + sz:
        z.append('Target vor Stop: ' + wilson(tz, tz + sz))
        hd = [(r['ergebnis']['ende'] - (r['ergebnis'].get('fuellung') or r['zeit'])) / 60 for r in fill if st(r) in ('Target', 'Stop')]
        z.append('  Haltedauer bis Target/Stop: Median %d min, Spanne %d bis %d min' % (med(hd), min(hd), max(hd)))
    if rr:
        z.append('Summe %+.2f R aus %d gefüllten Trades (%+.2f R je Trade); Zeitablauf zählt zum letzten Schluss' % (summe, len(rr), summe / len(rr)))
    for kl in ('TREND', 'RANGE'):
        g = [r for r in rr if r['klasse'] == kl]
        if g:
            z.append('  %s: %d gefüllt, %+.2f R' % (kl, len(g), sum(r['ergebnis']['R'] for r in g)))
    for art in ('Market', 'Limit'):  # mt5-1.3: Market-Bestaetigung getrennt pruefbar
        g = [r for r in rr if r['art'] == art]
        if g:
            z.append('  %s: %d gefüllt, %+.2f R' % (art, len(g), sum(r['ergebnis']['R'] for r in g)))
    for ver in sorted({r.get('version', '?') for r in rr}):  # mt5-1.3: vor und nach der Regelaenderung getrennt; mt5-1.4: mit Trefferquote je Version
        g = [r for r in rr if r.get('version', '?') == ver]
        tv, sv = sum(st(r) == 'Target' for r in g), sum(st(r) == 'Stop' for r in g)
        z.append('  Version %s: %d gefüllt, %+.2f R' % (ver, len(g), sum(r['ergebnis']['R'] for r in g))
                 + ((', Target vor Stop ' + wilson(tv, tv + sv)) if tv + sv else ''))
    stufe = [r for r in rr if r.get('zielstufe', 0) >= 0]  # mt5-1.4 (Market zum Kurs) hat keine Zielstufe: -1 (nicht None, sonst stuerzt 'auswerten' von mt5-1.3 nach einem Zurueckrollen ab)
    for lab, g in (('Target auf erstem Level', [r for r in stufe if r.get('zielstufe', 0) == 0]), ('Target weiter gestreckt', [r for r in stufe if r.get('zielstufe', 0) > 0])):
        if g:
            z.append('  %s: %d gefüllt, %+.2f R' % (lab, len(g), sum(r['ergebnis']['R'] for r in g)))
    kn = [r for r in rr if r['art'] == 'Limit' and r['ergebnis'].get('knapp')]
    if kn:
        z.append('Davon Limit-Füllungen nur knapp (Durchstoß < %s ATR5): %d von %d. Die Füllquote ist eine Obergrenze (Berührung = Füllung, kein Spread).' % (SET['KNAPP_ATR'], len(kn), len([r for r in rr if r['art'] == 'Limit'])))
    if any('vergleich' in r and r.get('version') == TA_VERSION for r in recs_w):
        # Regelvergleich (seit mt5-1.3; ab mt5-1.4 gegen ALT_VERSION). Zwei vollstaendige Spuren ueber dieselben Laeufe und Kerzen:
        #   neu = jedes ausgegebene Signal der laufenden Version (vergleich gleich/anders/alt_kein; 'fehler' = alte Wahl unbekannt, Lauf faellt auf BEIDEN Seiten raus)
        #   alt = echte Signale mit vergleich 'gleich' (die alten Regeln haetten genau das gewaehlt) + Schatten-Zeilen (alte Wahl, wo sie abwich)
        # Gleiche Trades stehen so auf BEIDEN Seiten und heben sich auf. Je Spur dieselbe Wiederholungs-Regel. Nicht gefuellt/verworfen/verfallen = 0 R,
        # 'unklar' = 0 R. Statistik: Differenz je Handelstag (Wien), t-Wert ueber die Tage. Geprueft wird NUR an festen Pruefpunkten (50/100/150 gefuellte
        # Trades der neuen Spur, jeweils mit den Signalen bis zu diesem Punkt eingefroren), nicht bei jedem 'auswerten': sonst schlaegt der Test durch
        # wiederholtes Hinschauen viel zu oft zufaellig an. Schwellen 2,0 / 1,8 / 1,65: Fehlalarm ohne echten Unterschied ca. 8 % ueber alle drei Punkte.
        # nur Zeilen der laufenden Version: eine neue Fassung (z. B. eine Regel abgeschaltet) beginnt den Vergleich von vorn
        sp_neu = [r for r in recs_w if r.get('vergleich') in ('gleich', 'anders', 'alt_kein') and r.get('version') == TA_VERSION]
        sp_alt = [r for r in recs_w if r.get('vergleich') == 'gleich' and r.get('version') == TA_VERSION] + [r for r in schatten if r.get('version') == TA_VERSION]
        start = min([r['zeit'] for r in sp_neu + sp_alt] or [now_s])
        sp_alt = [r for r in sp_alt if r['zeit'] >= start]
        spuren = []
        for g in (sp_neu, sp_alt):
            ww = wiederholungen(g)
            spuren.append(sorted([r for r in g if r['id'] not in ww], key=lambda x: x['zeit']))
        sp_neu, sp_alt = spuren
        gefuellt = lambda r: 'ergebnis' in r and st(r) in ('Target', 'Stop', 'Zeitablauf', 'unklar')
        Rv = lambda r: (r['ergebnis'].get('R') or 0.0) if 'ergebnis' in r and st(r) != 'unbewertbar' else 0.0
        tag = lambda r: datetime.fromtimestamp(r['zeit'], WIEN).strftime('%Y-%m-%d')
        fertig = lambda r: r['zeit'] <= reif_ab and 'ergebnis' in r  # reif und bewertet: Ergebnis steht fest

        def stand(bis_t):  # Summen und Tagesdifferenzen mit allen Signalen bis bis_t
            n_, a_ = [r for r in sp_neu if r['zeit'] <= bis_t], [r for r in sp_alt if r['zeit'] <= bis_t]
            tage = {}
            for r in n_:
                tage[tag(r)] = tage.get(tag(r), 0.0) + Rv(r)
            for r in a_:
                tage[tag(r)] = tage.get(tag(r), 0.0) - Rv(r)
            x = list(tage.values())
            m = sum(x) / len(x) if x else 0.0
            se = math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1) / len(x)) if len(x) > 1 else 0.0
            return n_, a_, sum(Rv(r) for r in n_) - sum(Rv(r) for r in a_), (m / se if se > 0 else 0.0), len(x)
        teil = lambda lab, g: '%s %d Signale, %d gefüllt, %d verworfen, Summe %+.2f R' % (lab, len(g), sum(gefuellt(r) for r in g), sum('ergebnis' in r and st(r) == 'verworfen' for r in g), sum(Rv(r) for r in g))
        fest = []  # Fuellungen der neuen Spur in Zeitfolge, solange davor alles (beide Spuren) fertig bewertet ist
        ids_neu = {r['id'] for r in sp_neu}
        for r in sorted({r['id']: r for r in sp_neu + sp_alt}.values(), key=lambda x: x['zeit']):
            if not fertig(r):
                break
            if r['id'] in ids_neu and gefuellt(r):
                fest.append(r['zeit'])
        n_, a_, diff, tw, nt = stand(reif_ab)
        z.append('Regelvergleich ' + TA_VERSION + ' gegen ' + ALT_VERSION + ' (reif, gleiche Läufe, gleiche Kerzen): ' + teil('neu', [r for r in n_ if fertig(r)]) + ' | ' + teil('alt', [r for r in a_ if fertig(r)])
                 + ' | neu Trade statt alt Kein Trade: %d | neu Kein Trade statt alt Trade: %d' % (sum(r.get('vergleich') == 'alt_kein' for r in n_), sum(r.get('quelle') == 'schatten' and not r.get('paar') for r in a_)))
        z.append('  Zwischenstand (nur Information, KEIN Urteil): Differenz neu minus alt %+.2f R über %d Handelstage, t = %+.2f' % (diff, nt, tw))
        urteil, PT, ZR = None, SET['PRUEF_TRADES'], SET['PRUEF_Z_ZURUECK']
        for i, k in enumerate(PT):
            if len(fest) < k:
                urteil = urteil or ('nächster Prüfpunkt bei %d gefüllten Trades der neuen Regeln (jetzt %d fest bewertet); bis dahin nichts entscheiden' % (k, len(fest)))
                break
            _, _, dk, tk, ntk = stand(fest[k - 1])
            if tk < -ZR[i]:
                urteil = 'ZURÜCK AUF ' + ALT_VERSION + ' (Prüfpunkt %d: Differenz %+.2f R, t = %+.2f unter -%s über %d Tage)' % (k, dk, tk, ('%.2f' % ZR[i]).replace('.', ','), ntk)
                break
            z.append('  Prüfpunkt %d bestanden: Differenz %+.2f R, t = %+.2f über %d Tage (Schwelle zurück: -%s)' % (k, dk, tk, ntk, ('%.2f' % ZR[i]).replace('.', ',')))
            if i == len(PT) - 1:
                urteil = ('Endstand: ' + TA_VERSION + ' belegt besser (t über %s)' % ('%.2f' % SET['PRUEF_Z_BESSER']).replace('.', ',') if tk > SET['PRUEF_Z_BESSER']
                          else 'Endstand: kein Schaden belegt, ' + TA_VERSION + ' bleibt; besser ist nicht belegt')
        z.append('  Urteil: ' + urteil + '.')
    z.append('Aussagekraft: %d gefüllte, unabhängig gezählte Signale; jedes ausgegebene Signal gilt als platziert (ob Alex es gehandelt hat, weiß das Script nicht). Regeländerungen erst ab etwa 150 belastbar (Größenordnung, keine Garantie).' % len(rr))
    if fehler:
        z.append('Nicht lesbar: ' + '; '.join(fehler))
    return 'L', '\n'.join(z)


# ---------- MT5-Export lesen ----------
def lies_status(d):
    st = {}
    with open(os.path.join(d, 'status.txt'), encoding='utf-8-sig') as fh:
        for z in fh:
            z = z.strip()
            if '=' in z:
                k, v = z.split('=', 1)
                st[k.strip()] = v.strip()
    if st.get('END') != '1':
        raise RuntimeError('status.txt unvollstaendig')
    return st


def lies_kerzen(pfad):
    rows = []
    with open(pfad, encoding='utf-8-sig') as fh:
        zeilen = fh.read().split('\n')
    if 'END' not in [z.strip() for z in zeilen[-3:]]:
        raise RuntimeError(os.path.basename(pfad) + ' unvollstaendig')
    for z in zeilen[1:]:
        z = z.strip()
        if not z or z == 'END':
            continue
        p = z.split(',')
        rows.append([int(p[0]), float(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[5])])
    return rows


def lade_instrument(d, name, offset):
    """Liefert (A, F) oder Fehlertext. Kerzenzeiten im Export sind Serverzeit; Session = Broker-Tag 00:00."""
    out = []
    for tf, sec in (('M30', 1800), ('M5', 300)):
        pfad = os.path.join(d, name + '_' + tf + '.csv')
        if not os.path.exists(pfad):
            return 'Keine Exportdatei ' + name + '_' + tf + '.csv (Symbol im Exporter gefunden?)'
        raw = lies_kerzen(pfad)
        B = [[t - offset, o, h, l, c, v] for t, o, h, l, c, v in raw]
        V = vwap_baender(B, lambda b: (b[0] + offset) // 86400)
        st = supertrend(B, SET['ST_ATR'], SET['ST_FAKTOR']) if tf == 'M30' else None
        try:
            out.append(baue(B, V, sec, st))
        except RuntimeError as e:
            return str(e) + ' (' + name + ' ' + tf + ')'
        out[-1]['Vlist'] = V
    return out[0], out[1]


# ---------- Chart ----------
def zeichne(pfad, w, F, symbol):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    n = SET['CHART_KERZEN']
    B = F['B'][-n:]
    V = F['Vlist'][-n:]
    z = w['zeilen']
    E = float(z[0].rsplit('@', 1)[1])
    T = float(z[1].split(':')[1])
    S = float(z[2].split(':')[1])
    art = z[0].split(' ', 2)[2].rsplit(' @', 1)[0]
    up = T > E
    bg, ink, muted, grid = '#ffffff', '#1f1f1d', '#7a7974', '#ecebe6'
    gruen, rot, blau, ziel = '#1baf7a', '#e34948', '#2a78d6', '#0a8a3a'
    fig, ax = plt.subplots(figsize=(12, 6.6), dpi=150)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    m = len(B)
    xr = m + max(18, int(m * 0.2))
    lo = min(min(b[3] for b in B), E, S, T)
    hi = max(max(b[2] for b in B), E, S, T)
    pad = (hi - lo) * 0.06
    ax.set_xlim(-1, xr)
    ax.set_ylim(lo - pad, hi + pad)
    resets = [i for i in range(m) if abs(V[i][1] - V[i][2]) <= B[i][4] * 1e-6]
    for i in resets:
        ax.axvline(i - 0.5, color='#c9c7bf', lw=0.8, ls=(0, (3, 3)), zorder=1)
    farben = ['#eda100', '#1D9E75', '#1D9E75', '#7F77DD', '#7F77DD', '#9a9993', '#9a9993']
    for k in range(7):
        seg_x, seg_y = [], []
        for i in range(m):
            if i in resets and seg_x:
                ax.plot(seg_x, seg_y, color=farben[k], lw=1.6 if k == 0 else 1.0, ls='-' if k < 5 else (0, (4, 3)), zorder=2)
                seg_x, seg_y = [], []
            seg_x.append(i)
            seg_y.append(V[i][k])
        ax.plot(seg_x, seg_y, color=farben[k], lw=1.6 if k == 0 else 1.0, ls='-' if k < 5 else (0, (4, 3)), zorder=2)
    for i, b in enumerate(B):
        o, h, l, c = b[1:5]
        col = gruen if c >= o else rot
        ax.vlines(i, l, h, color=col, lw=0.7, zorder=3)
        ax.add_patch(Rectangle((i - 0.32, min(o, c)), 0.64, max(abs(c - o), (hi - lo) * 0.0008), color=col, zorder=4, lw=0))
    x0 = m - 0.2
    ax.add_patch(Rectangle((x0, min(E, S)), xr - x0, abs(E - S), color=rot, alpha=0.16, lw=0, zorder=1))
    ax.add_patch(Rectangle((x0, min(E, T)), xr - x0, abs(E - T), color=gruen, alpha=0.16, lw=0, zorder=1))
    gap = (hi - lo + 2 * pad) * 0.055
    lab = sorted([[S, rot, 'Stop'], [E, blau, art], [T, ziel, 'Target']], key=lambda q: q[0])
    pos = [q[0] for q in lab]
    for _ in range(3):
        for j in range(1, 3):
            if pos[j] - pos[j - 1] < gap:
                mitte = (pos[j] + pos[j - 1]) / 2
                pos[j - 1], pos[j] = mitte - gap / 2, mitte + gap / 2
    for (val, col, txt), yl in zip(lab, pos):
        ax.axhline(val, color=col, lw=0.8, ls=(0, (2, 3)), alpha=0.6, zorder=2)
        ax.hlines(val, x0, xr, color=col, lw=2.0, zorder=5)
        ax.annotate(txt + '  ' + ('%d' % val if float(val).is_integer() else str(val)), xy=(xr, val), xytext=(x0 + (xr - x0) * 0.06, yl),
                    textcoords='data', color='white', fontsize=9, va='center', ha='left', zorder=6,
                    bbox=dict(boxstyle='round,pad=0.3', fc=col, ec='none'))
    kurs = B[-1][4]
    ax.axhline(kurs, color=muted, lw=0.8, ls=(0, (1, 2)), zorder=2)
    ax.yaxis.tick_right()
    ax.tick_params(colors=muted, labelsize=9, length=0)
    ax.grid(axis='y', color=grid, lw=0.8)
    for s in ax.spines.values():
        s.set_visible(False)
    ticks, labels, lastday = [], [], None
    for i, b in enumerate(B):
        dt = datetime.fromtimestamp(b[0], WIEN)
        tag = dt.strftime('%d.%m.')
        if tag != lastday:
            if lastday is not None:
                ticks.append(i)
                labels.append(['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'][dt.weekday()] + ' ' + tag)
            lastday = tag
        elif dt.minute == 0 and dt.hour % 2 == 0 and all(abs(i - t) >= 10 for t in ticks):
            ticks.append(i)
            labels.append(dt.strftime('%H:%M'))
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    crv = w['crv']
    titel = z[0].split(': ', 1)[1]
    unter = '5min  ·  Stop %s  ·  Target %s  ·  CRV %s  ·  Wiener Zeit  ·  MT5 %s' % (z[2].split(': ')[1], z[1].split(': ')[1], w['crvTxt'], symbol)
    fig.text(0.012, 0.965, titel, fontsize=13, color=ink, weight='bold', ha='left', va='top')
    fig.text(0.012, 0.925, unter, fontsize=9.5, color=muted, ha='left', va='top')
    leg = [('VWAP', farben[0], '-'), ('±1σ', farben[1], '-'), ('±2σ', farben[3], '-'), ('±3σ', farben[5], '--')]
    xx = 0.988
    for name, col, ls in reversed(leg):
        t = fig.text(xx, 0.94, name, fontsize=9, color=muted, ha='right', va='center')
        fig.canvas.draw()
        bb = t.get_window_extent().transformed(fig.transFigure.inverted())
        fig.lines.append(matplotlib.lines.Line2D([bb.x0 - 0.028, bb.x0 - 0.006], [0.94, 0.94], color=col, lw=2, ls=ls, transform=fig.transFigure))
        xx = bb.x0 - 0.04
    fig.subplots_adjust(left=0.012, right=0.93, top=0.89, bottom=0.07)
    fig.savefig(pfad, facecolor=bg)
    plt.close(fig)


# ---------- Hauptprogramm ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--zeit', default='')
    ap.add_argument('--news', default='[]')
    ap.add_argument('--nur', default='')
    ap.add_argument('--dir', default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument('--kein-chart', action='store_true')
    ap.add_argument('--kein-log', action='store_true')
    ap.add_argument('--auswerten', action='store_true')
    a = ap.parse_args()

    def ende(form, text, chart=None, erg=None, log=''):
        home = os.path.expanduser('~')
        mnt = ('~' + chart[len(home):]) if chart and chart.startswith(home + os.sep) else chart
        print(json.dumps({'version': TA_VERSION, 'form': form, 'ausgabe': text, 'chart': mnt, 'ergebnisse': erg or [], 'log': log}, ensure_ascii=False, indent=1))
        sys.exit(0)

    try:
        if a.zeit:
            zt = datetime.fromisoformat(a.zeit.replace('Z', '+00:00'))
            if zt.tzinfo is None:
                raise ValueError('ohne Zeitzone')  # sonst wuerde die Uhr des Rechners die Zone raten
            now_ms = zt.timestamp() * 1000
        else:
            now_ms = time.time() * 1000
    except ValueError:
        ende('C', 'Technischer Fehler: Zeitreferenz ungueltig oder ohne Zeitzone (' + a.zeit + ')')
    if a.auswerten:
        try:
            form, text = auswerten(a.dir, now_ms)
        except Exception as e:  # nie ohne JSON enden (Schreibschutz, kaputte Zeile, ...)
            form, text = 'C', 'Technischer Fehler: Auswertung fehlgeschlagen (' + type(e).__name__ + ' ' + str(e) + ')'
        ende(form, text)
    try:
        ev = news_events(json.loads(a.news), now_ms)
    except (ValueError, TypeError, IndexError) as e:
        ende('C', 'Technischer Fehler: ' + (str(e) if str(e).startswith('News') else 'News-Angabe ungueltig: ' + a.news))
    if a.nur:
        key = ALIAS.get(a.nur.strip().upper())
        if not key:
            ende('C', 'Technischer Fehler: unbekanntes Instrument ' + a.nur)
        liste = [i for i in INSTR if i[0] == key]
    else:
        liste = INSTR

    st, daten, letzter = None, {}, ''
    for versuch in range(4):
        try:
            st = lies_status(a.dir)
            alt = time.time() - float(st['export_gmt'])
            if alt > SET['EXPORT_MAX_ALT_S']:
                ende('C', 'Technischer Fehler: MT5-Export ist %d s alt. MT5 offen, Dienst TA_Export gestartet und eingeloggt?' % alt)
            if st.get('verbunden') == '0':
                ende('C', 'Technischer Fehler: MT5 ist nicht mit dem Handelsserver verbunden.')
            offset = int(st['offset'])
            daten = {}
            for n, kl_n in liste:
                if not st.get('sym_' + n):
                    daten[n] = 'MT5-Symbol fuer ' + n + ' nicht gefunden (Dienst TA_Export: Eingabe Sym' + n[:3] + ' setzen, Namen in symbole.txt)'
                elif float(st.get('zeit_' + n, 0)) <= 0:
                    daten[n] = 'MT5 liefert keine Kerzen fuer ' + st['sym_' + n] + ' (Symbol in der Marktuebersicht? Historie geladen?)'
                elif kl_n == 'INDEX' and float(st['export_gmt']) - float(st['zeit_' + n]) > SET['GESCHLOSSEN_MIN'] * 60:
                    # Index ohne Tick seit > 15 min: Handelspause/Wochenende, kein technischer Fehler (ETH laeuft 24/7: dort bleibt es ein Fehler)
                    tk = float(st['zeit_' + n]) * 1000
                    tag = '' if datetime.fromtimestamp(tk / 1000, WIEN).date() == datetime.fromtimestamp(now_ms / 1000, WIEN).date() else datetime.fromtimestamp(tk / 1000, WIEN).strftime('%d.%m. ')
                    daten[n] = {'geschlossen': n + '-Markt geschlossen oder ohne Kurse, letzter Tick ' + tag + hm_wien(tk) + ' Wiener Zeit'}
                elif float(st['export_gmt']) - float(st['zeit_' + n]) > 60:
                    daten[n] = 'MT5 liefert keine frischen Kurse fuer ' + st['sym_' + n] + ' (letzter Tick vor ' + str(int(float(st['export_gmt']) - float(st['zeit_' + n]))) + ' s; Symbol in der Marktuebersicht?)'
                else:
                    daten[n] = lade_instrument(a.dir, n, offset)
            break
        except FileNotFoundError as e:
            letzter = ('keine status.txt: Dienst TA_Export im MT5 nicht gestartet?' if 'status.txt' in str(e) else str(e))
            time.sleep(1.2)
        except (OSError, RuntimeError, ValueError, KeyError, IndexError) as e:
            letzter = str(e)
            time.sleep(1.2)
    else:
        ende('C', 'Technischer Fehler: MT5-Export nicht lesbar (' + letzter + ')')

    def rechne(Z):
        erg = []
        for n, kl in liste:
            dat = daten[n]
            if isinstance(dat, dict):
                erg.append({'instrument': n, 'status': 'geschlossen', 'grund': dat['geschlossen']})
            elif isinstance(dat, str):
                erg.append(instrument(n, kl, dat, dat, now_ms, ev, Z))
            else:
                try:
                    erg.append(instrument(n, kl, dat[0], dat[1], now_ms, ev, Z))
                except Exception as e:  # Absicherung: ein kaputtes Instrument soll die anderen nicht blockieren
                    erg.append({'instrument': n, 'fehler': 'Scriptfehler ' + n + ': ' + type(e).__name__ + ' ' + str(e)})
        return erg
    erg = rechne(SET)
    form, text, w = auswahl(erg, bool(a.nur))
    chart = None
    log, sig_id, w_alt, vgl, zvgl = '', None, None, None, None
    if form in ('A', 'B') and not a.kein_log:
        try:  # Was ALT_VERSION (mt5-1.3) im selben Lauf gewaehlt haette (nur fuer den Regelvergleich). Darf die Ausgabe nie beeinflussen.
            w_alt = auswahl(rechne(SET_ALT), bool(a.nur))[2]
            gleich = lambda x, y: (x is None and y is None) or (x is not None and y is not None and x['instrument'] == y['instrument'] and x['orderart'] == y['orderart']
                                                                and all(x['signal'][k] == y['signal'][k] for k in ('E', 'S', 'T')))
            vgl = 'alt_kein' if w_alt is None else ('gleich' if gleich(w, w_alt) else 'anders')
        except Exception:
            w_alt, vgl = None, 'fehler'
    if form == 'A' and not a.kein_log:
        log, sig_id, zvgl = logge_signal(a.dir, w, now_ms, offset, 'einzel' if a.nur else 'setup', {'vergleich': vgl})
    # Schatten (alte Spur), wenn die alte Wahl abweicht ODER sie gleich ist, die echte Zeile aber schon frueher als 'anders' geloggt wurde (Doppelaufruf):
    # sonst fehlte der alten Spur dieser Trade. Doppelte Schatten verhindert logge_signal. Bei Log-Fehler kein Schatten (sonst fehlte die neue Seite).
    if form in ('A', 'B') and not a.kein_log and not log and w_alt is not None and vgl != 'fehler' and (vgl != 'gleich' or zvgl != 'gleich'):
        logge_signal(a.dir, w_alt, now_ms, offset, 'schatten', {'paar': sig_id})
    if form == 'A' and not a.kein_log:
        if log:  # VOR dem Chart-Block: die Meldung haengt am Ende der Begruendungszeile, ein Chart-Hinweis folgt in einer eigenen Zeile danach
            text += ' (' + log + ')'
    if form == 'A' and not a.kein_chart:
        stamp = datetime.fromtimestamp(now_ms / 1000, WIEN).strftime('%Y%m%d_%H%M%S')
        chart = os.path.join(a.dir, 'charts', '%s_5min_order_%s.png' % (w['instrument'].lower(), stamp))
        try:
            os.makedirs(os.path.join(a.dir, 'charts'), exist_ok=True)  # im try: ein schreibgeschuetzter Ordner darf den Trade nicht verschlucken
            zeichne(chart, w, daten[w['instrument']][1], st.get('sym_' + w['instrument'], ''))
        except Exception as e:
            chart = None
            text += '\n(Chart nicht erstellt: ' + type(e).__name__ + ' ' + str(e) + ')'
    for e in erg:
        e.pop('Vlist', None)
    ende(form, text, chart, erg, log)


if __name__ == '__main__':
    main()
