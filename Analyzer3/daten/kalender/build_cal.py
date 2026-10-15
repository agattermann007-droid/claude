"""Build macro event calendars in /home/user/data/cal from downloaded (untrusted) data files.
Only reads data files (csv/json/xlsx); never imports or runs downloaded code.
Run with: python3 -I build_cal.py
"""
import json, re, sys, datetime as dt
from pathlib import Path
import pandas as pd

RAW = Path('/home/user/data/raw')
OUT = Path('/home/user/data/cal')
OUT.mkdir(parents=True, exist_ok=True)
ASOF = pd.Timestamp('2026-10-15')
NY = 'America/New_York'
LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a); LOG.append(s); print(s)

def status(d):
    return 'past' if pd.Timestamp(d) <= ASOF else 'upcoming'

# ---------------------------------------------------------------- sources
JK = RAW/'cal__marekjarocinski__jkshocks_update_fed/source_data/fomc_surprises_jk.csv'
RR = RAW/'cal__returnandrisk__r-code/fomcdates_1936_2018.csv'
PFW = RAW/'cal__hackingthemarkets__pyfedwatch/data/fomc/fomc_data.xlsx'
INV = RAW/'cal__systamental__cryptodatapy/tests/data/ip_econ_cal.csv'
FF = RAW/'cal__ehsanrs2__forexfactory-scraper/high_impact_events_calendar.csv'
BJ = RAW/'cal__borisjoffe__FOMC-dates.js/dates.csv'
FP = RAW/'cal__helivan-research__fomc-personas/fomc_personas/macro.py'
VN = RAW/'cal__gitlab__vaughnn.noah-portfolio__market-aware/data/fomc_meetings_2000_2027.json'

# investing.com dump (times are UTC)
inv = pd.read_csv(INV, index_col=0)
inv = inv[(inv.zone == 'united states') & inv.time.astype(str).str.match(r'^\d\d:\d\d$')].copy()
inv['ev'] = inv.event.str.replace(r'\s+\(.*\)$', '', regex=True).str.strip()
inv['ref'] = inv.event.str.extract(r'\((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\)\s*$')[0]
inv['utc'] = pd.to_datetime(inv.date + ' ' + inv.time, format='%d/%m/%Y %H:%M').dt.tz_localize('UTC')
inv['et'] = inv.utc.dt.tz_convert(NY)
inv['d'] = inv.et.dt.strftime('%Y-%m-%d')
inv['placeholder'] = (inv.time == '09:00') & (inv.date.str[:2] == '01')  # monthly placeholder rows
INV_END = inv.d.max()

# ForexFactory high-impact (UTC timestamps)
ff = pd.read_csv(FF)
ff['et'] = pd.to_datetime(ff.DateTime, utc=True).dt.tz_convert(NY)
ff['d'] = ff.et.dt.strftime('%Y-%m-%d'); ff['t'] = ff.et.dt.strftime('%H:%M')
ff = ff[ff.Currency == 'USD']
FF_START, FF_END = ff.d.min(), ff.d.max()
log('INV coverage', inv.d.min(), INV_END, '| FF coverage', FF_START, FF_END)

# ================================================================ 1. FOMC
jk = pd.read_csv(JK, usecols=[0, 1])
jk['start'] = pd.to_datetime(jk.start)
jk = jk[(jk.start >= '2005-01-01')]
jk['d'] = jk.start.dt.strftime('%Y-%m-%d'); jk['t'] = jk.start.dt.strftime('%H:%M')

sched = jk[jk.Event.str.contains(r'Rate Decision \(Scheduled\)')].copy()
# JK labels 2020-03-03 as Scheduled; it was an unscheduled (intermeeting) cut -> move to unscheduled
sched = sched[sched.d != '2020-03-03']
UNSCHED = {  # date: (type, note)  -- statement/decision times taken from JK (Bloomberg)
    '2007-08-10': ('unscheduled_statement', 'FOMC statement on liquidity provision (conference call)'),
    '2007-08-17': ('unscheduled_statement', 'FOMC statement (call 2007-08-16) with Board discount-rate action'),
    '2008-01-22': ('unscheduled_rate_decision', 'intermeeting cut 75bp (call 2008-01-21)'),
    '2008-03-11': ('unscheduled_statement', 'FOMC statement: TSLF/swap lines (call 2008-03-10)'),
    '2008-10-08': ('unscheduled_rate_decision', 'coordinated intermeeting cut 50bp (call 2008-10-07)'),
    '2010-05-09': ('unscheduled_statement', 'FOMC statement: re-establishing USD swap lines (Sunday)'),
    '2019-10-11': ('unscheduled_statement', 'FOMC Statement Regarding Monetary Policy Implementation (T-bill purchases)'),
    '2020-03-03': ('unscheduled_rate_decision', 'intermeeting cut 50bp; press conference 11:00'),
    '2020-03-15': ('unscheduled_rate_decision', 'Sunday cut 100bp + QE; replaced scheduled 17-18 Mar meeting; press call 18:30'),
    '2020-03-23': ('unscheduled_statement', 'FOMC statement: open-ended asset purchases (with Board facilities)'),
}
uns = jk[jk.d.isin(UNSCHED)].drop_duplicates('d').copy()
assert len(uns) == len(UNSCHED), set(UNSCHED) - set(uns.d)

# future 2026 meetings: fomc-personas LIVE_DECISIONS (federalreserve.gov tentative calendar)
src = FP.read_text()
live = re.findall(r'"(20\d\d-\d\d-\d\d)"', src.split('LIVE_DECISIONS')[1].split(']')[0])
fp_hist = re.findall(r'"(20\d\d-\d\d-\d\d)"', src.split('FOMC_MEETINGS = [')[1].split(']')[0])
fut = [d for d in live if d.startswith('2026') and d > sched.d.max()]
log('FOMC future 2026 dates from fomc-personas LIVE_DECISIONS:', fut)

PRESS_2011_2018 = set()
rr = pd.read_csv(RR)
rr['e'] = pd.to_datetime(rr.enddate, format='%m/%d/%Y'); rr = rr[rr.e >= '2005-01-01']
rr['d'] = rr.e.dt.strftime('%Y-%m-%d')
PRESS_RR = set(rr[rr.pressconf == 1].d)
PRESS_INV = set(inv[inv.ev == 'FOMC Press Conference'].d)
PRESS_FF = set(ff[ff.Event == 'FOMC Press Conference'].d)
# 2011-2012 press-conference meetings: statement moved to 12:30 ET (JK / pyfedwatch / investing all show 12:30)
PRESS_1230 = set(sched[(sched.t == '12:30')].d)

rows = []
for _, r in sched.iterrows():
    d = r.d
    if d <= '2013-01-31':
        t = '12:30' if d in PRESS_1230 else '14:15'
    else:
        t = '14:00'
    pc = 1 if (d >= '2019-01-01' or d in PRESS_RR or d in PRESS_INV or d in PRESS_FF or d in PRESS_1230) else 0
    rows.append(dict(date=d, time_et=t, scheduled=1, press_conf=pc, type='scheduled_meeting',
                     jk_time=r.t, source='JK(Bloomberg)', note=''))
for d in fut:
    rows.append(dict(date=d, time_et='14:00', scheduled=1, press_conf=1, type='scheduled_meeting', jk_time='',
                     source='fomc-personas LIVE_DECISIONS (Fed tentative calendar) + web search; upcoming', note='tentative, not yet held as of 2026-10-15'))
for _, r in uns.iterrows():
    typ, note = UNSCHED[r.d]
    pc = 1 if r.d in ('2020-03-03', '2020-03-15') else 0
    rows.append(dict(date=r.d, time_et=r.t, scheduled=0, press_conf=pc, type=typ, jk_time=r.t,
                     source='JK(Bloomberg)', note=note))
fomc = pd.DataFrame(rows).sort_values('date').reset_index(drop=True)

# ---- cross-source verification (scheduled meetings)
srcsets = {}
srcsets['RR'] = (set(rr[rr.scheduled == 1].d), '2005-01-01', '2018-08-01')
pfw = pd.read_excel(PFW); pfw['d'] = pd.to_datetime(pfw.FOMCDate).dt.strftime('%Y-%m-%d')
srcsets['PFW'] = (set(pfw.d), '2005-01-01', '2023-12-31')     # 2024 rows are hand-entered (3 wrong) -> checked separately
srcsets['PFW2024'] = (set(pfw.d), '2024-01-01', '2024-12-31')
invf = inv[inv.ev.isin(['FOMC Statement', 'Fed Interest Rate Decision'])]
srcsets['INV'] = (set(invf.d), '2005-01-01', INV_END)
fff = ff[ff.Event.isin(['FOMC Statement', 'Federal Funds Rate'])]
srcsets['FF'] = (set(fff.d), FF_START, FF_END)
bj = pd.read_csv(BJ, header=None); srcsets['BJ'] = (set(bj[0]), '2021-01-01', '2024-12-31')
srcsets['FP'] = (set(fp_hist) | set(live), '2018-01-01', '2026-12-31')
vn = json.load(open(VN))['fomc_meetings']; srcsets['VN'] = ({x['date'] for x in vn}, '2005-01-01', '2026-12-31')

# unscheduled statements: RR statement URLs (e.g. .../20080122b.htm) and FF 'Fed Announcement'/'FOMC Statement'
rr_uns = rr[(rr.scheduled == 0) & rr.url.astype(str).str.contains('monetary')].url.str.extract(r'(\d{8})[ab]')[0].dropna()
srcsets['RRu'] = ({f'{x[:4]}-{x[4:6]}-{x[6:]}' for x in rr_uns}, '2005-01-01', '2018-08-01')
srcsets['FFa'] = (set(ff[ff.Event.isin(['Fed Announcement', 'FOMC Statement'])].d), FF_START, FF_END)
# future 2026 meetings: web search (Texas Bankers Assn. notice of Fed tentative 2026 schedule, finanzaonline, MEXC): Oct 27-28, Dec 8-9
srcsets['WEB'] = ({'2026-10-28', '2026-12-09'}, '2026-10-16', '2026-12-31')
conf = []
log('\n--- FOMC verification (scheduled meetings) ---')
sch = fomc[fomc.scheduled == 1]
for name, (s, a, b) in srcsets.items():
    inwin = sch[(sch.date >= a) & (sch.date <= b)]
    hit = inwin.date.isin(s)
    extra = sorted(x for x in s if a <= x <= b and x not in set(fomc.date))
    if name in ('RRu', 'FFa', 'WEB'):
        continue
    log(f'{name}: {hit.sum()}/{len(inwin)} scheduled dates in window {a}..{b}; missing={list(inwin.date[~hit])}; source dates not in our file={extra}')
fomc['confirmed_by'] = fomc.date.apply(lambda d: ','.join(['JK'] * (d <= '2026-09-16' and d not in fut) +
                                                         [n.rstrip('ua').replace('FF', 'FF') if n in ('RRu', 'FFa') else n for n, (s, a, b) in srcsets.items() if a <= d <= b and d in s and n != 'PFW2024']))
fomc['confirmed_by'] = fomc.confirmed_by.apply(lambda x: ','.join(dict.fromkeys(x.split(','))))
fomc['n_sources'] = fomc.confirmed_by.str.split(',').apply(lambda x: len([y for y in x if y]))
# time check vs JK
dev = fomc[(fomc.jk_time != '') & (fomc.jk_time != fomc.time_et)]
log('time_et vs JK minute deviations:', dev[['date', 'time_et', 'jk_time']].values.tolist())
# press conference check vs sources
pc_src = PRESS_RR | PRESS_INV | PRESS_FF
log('press_conf=1 rows', int(fomc.press_conf.sum()), '| first', fomc[fomc.press_conf == 1].date.min())
log('press_conf by year:', fomc[fomc.scheduled == 1].groupby(fomc.date.str[:4]).press_conf.agg(['sum', 'count']).T.to_dict())
log('pressers in sources not flagged:', sorted(x for x in pc_src if x >= '2005' and x not in set(fomc[fomc.press_conf == 1].date)))
fomc['status'] = fomc.date.apply(status)
fomc_out = fomc[['date', 'time_et', 'scheduled', 'press_conf', 'type', 'status', 'n_sources', 'confirmed_by', 'source', 'note']]
fomc_out.to_csv(OUT/'fomc.csv', index=False)
log('fomc.csv rows', len(fomc_out), 'scheduled', int(fomc_out.scheduled.sum()), 'unscheduled', int((fomc_out.scheduled == 0).sum()))

# ================================================================ 2./3. CPI & NFP
def prev_month(d):
    p = (pd.Timestamp(d).to_period('M') - 1); return str(p)

MON = {m: i for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}

def build_release(name, inv_events, ff_events, web_2026, start='2005-01-01', overrides_ref=None):
    e = inv[inv.ev.isin(inv_events) & ~inv.placeholder & (inv.d >= start)]
    g = e.groupby('d').agg(t=('et', lambda s: s.dt.strftime('%H:%M').iloc[0]), ref=('ref', lambda s: s.dropna().iloc[0] if s.notna().any() else None)).reset_index()
    log(name, 'INV dates without month label:', g[g.ref.isna()].d.tolist())
    g['ref'] = [r if isinstance(r, str) else pd.Timestamp(prev_month(d)).strftime('%b') for d, r in zip(g.d, g.ref)]
    g['ref_period'] = [f"{int(d[:4]) - (1 if MON[r] > int(d[5:7]) else 0)}-{MON[r]:02d}" for d, r in zip(g.d, g.ref)]
    f = ff[ff.Event.isin(ff_events)].groupby('d').agg(t=('t', 'first')).reset_index()
    # overlap check
    ov_i = set(g[g.d >= FF_START].d); ov_f = set(f[f.d <= INV_END].d)
    log(f'\n--- {name} verification ---')
    log(f'INV vs FF overlap {FF_START}..{INV_END}: INV={len(ov_i)} FF={len(ov_f)} agree={len(ov_i & ov_f)}; INV-only={sorted(ov_i - ov_f)}; FF-only={sorted(ov_f - ov_i)}')
    log(f'INV raw times (ET, after UTC->ET conversion): {g.t.value_counts().to_dict()}; FF times: {f.t.value_counts().to_dict()}')
    odd = g[g.t != '08:30']; log(f'INV non-08:30 rows (DST artefacts?): {odd[["d","t"]].values.tolist()}')
    rows = []
    for _, r in g.iterrows():
        rows.append(dict(date=r.d, time_et='08:30', ref_period=r.ref_period,
                         source='investing.com via systamental/cryptodatapy' + ('+FF(ehsanrs2)' if r.d in ov_f else ''),
                         n_sources=2 if r.d in ov_f else 1))
    web_d = {d for d, _ in web_2026}
    for _, r in f[f.d > INV_END].iterrows():
        rp = (overrides_ref or {}).get(r.d, prev_month(r.d))
        both = r.d in web_d
        rows.append(dict(date=r.d, time_et='08:30', ref_period=rp,
                         source='ForexFactory via ehsanrs2/forexfactory-scraper' + ('+web(BLS 2026 schedule)' if both else ''),
                         n_sources=2 if both else 1))
    for d, rp in web_2026:
        if d > FF_END:
            rows.append(dict(date=d, time_et='08:30', ref_period=rp,
                             source='BLS 2026 schedule as reported by web search (usinflationcalculator/therighttrader/fedratecalc; BLS pages); not on GitHub', n_sources=1))
    out = pd.DataFrame(rows).sort_values('date').reset_index(drop=True)
    # web list vs FF overlap for Jan 2026
    for d, rp in web_2026:
        if d <= FF_END:
            log(f'web 2026 date {d} in FF: {d in set(f.d)}')
    # sanity
    out['dow'] = pd.to_datetime(out.date).dt.day_name()
    dup = out.ref_period[out.ref_period.duplicated()].tolist()
    allm = pd.period_range('2004-12', '2026-11', freq='M').astype(str)
    miss = [m for m in allm if m not in set(out.ref_period) and m >= '2004-12']
    log(f'{name}: rows={len(out)} range {out.date.min()}..{out.date.max()}; dup ref={dup}; missing ref months={miss}; weekdays={out.dow.value_counts().to_dict()}')
    out['status'] = out.date.apply(status)
    return out

CPI_2026 = [('2026-01-13', '2025-12'), ('2026-02-13', '2026-01'), ('2026-03-11', '2026-02'), ('2026-04-10', '2026-03'),
            ('2026-05-12', '2026-04'), ('2026-06-10', '2026-05'), ('2026-07-14', '2026-06'), ('2026-08-12', '2026-07'),
            ('2026-09-11', '2026-08'), ('2026-10-14', '2026-09'), ('2026-11-10', '2026-10'), ('2026-12-10', '2026-11')]
NFP_2026 = [('2026-01-09', '2025-12'), ('2026-02-11', '2026-01'), ('2026-03-06', '2026-02'), ('2026-04-03', '2026-03'),
            ('2026-05-08', '2026-04'), ('2026-06-05', '2026-05'), ('2026-07-02', '2026-06'), ('2026-08-07', '2026-07'),
            ('2026-09-04', '2026-08'), ('2026-10-02', '2026-09'), ('2026-11-06', '2026-10'), ('2026-12-04', '2026-11')]
cpi = build_release('CPI', ['CPI'], ['CPI m/m', 'CPI y/y', 'Core CPI m/m'], CPI_2026)
nfp = build_release('NFP', ['Nonfarm Payrolls'], ['Non-Farm Employment Change', 'Unemployment Rate'], NFP_2026,
                    overrides_ref={'2025-11-20': '2025-09', '2025-12-16': '2025-11'})
# notes for known anomalies
CPI_NOTES = {'2013-10-30': 'Sep-2013 CPI delayed by government shutdown (orig. 2013-10-16)',
             '2025-10-24': 'Sep-2025 CPI delayed by government shutdown (orig. 2025-10-15)',
             '2025-12-18': 'Nov-2025 CPI after shutdown; Oct-2025 CPI was not published',
             '2026-02-13': 'Jan-2026 CPI moved from 2026-02-11 (lapse in appropriations 2026-01-31..02-03)'}
NFP_NOTES = {'2013-10-22': 'Sep-2013 report delayed by government shutdown (orig. 2013-10-04)',
             '2013-11-08': 'Oct-2013 report (shutdown-shifted schedule)',
             '2025-11-20': 'Sep-2025 report delayed by government shutdown (orig. 2025-10-03)',
             '2025-12-16': 'Nov-2025 report incl. Oct-2025 payrolls (Oct household survey not collected)',
             '2026-02-11': 'Jan-2026 report moved from 2026-02-06 (lapse in appropriations 2026-01-31..02-03)'}
cpi['note'] = cpi.date.map(CPI_NOTES).fillna(''); nfp['note'] = nfp.date.map(NFP_NOTES).fillna('')

# NFP independent rule check: BLS rule = 3rd Friday after the reference week (week incl. the 12th, Sun-Sat)
def nfp_rule(ref):
    p = pd.Period(ref, 'M'); d12 = pd.Timestamp(p.year, p.month, 12)
    sat = d12 + pd.Timedelta(days=(5 - d12.weekday()) % 7)
    return (sat + pd.Timedelta(days=6 + 14)).strftime('%Y-%m-%d')
nfp['rule_date'] = nfp.ref_period.apply(nfp_rule)
m = nfp.date == nfp.rule_date
log(f'NFP rule check (3rd Friday after reference week): {m.sum()}/{len(nfp)} match; mismatches:')
for _, r in nfp[~m].iterrows():
    log(f'   {r.date} ({pd.Timestamp(r.date).day_name()[:3]}) ref {r.ref_period} rule {r.rule_date} ({pd.Timestamp(r.rule_date).day_name()[:3]}) {r.note}')

cols = ['date', 'time_et', 'ref_period', 'status', 'n_sources', 'source', 'note']
cpi[cols].to_csv(OUT/'cpi.csv', index=False)
nfp[cols].to_csv(OUT/'nfp.csv', index=False)

# ================================================================ 4. EIA WPSR
from pandas.tseries.holiday import USFederalHolidayCalendar
fed_h = set(USFederalHolidayCalendar().holidays('2009-12-01', '2027-01-31').strftime('%Y-%m-%d'))
# ad-hoc federal closures (DC area) relevant for EIA (knowledge; most also visible in investing data)
ADHOC = {'2010-02-08', '2010-02-09', '2010-02-10', '2010-02-11',  # snowstorm closures
         '2012-10-29', '2012-10-30',  # Hurricane Sandy
         '2018-12-05',  # national day of mourning (G.H.W. Bush)
         '2013-01-21', '2017-01-20', '2021-01-20', '2025-01-20',  # Inauguration Day (DC area)
         '2012-12-24', '2018-12-24', '2019-12-24', '2024-12-24', '2025-01-09'}
closed = fed_h | ADHOC

def eia_rule(week_wed):
    """Rule for one report week (Mon..Sun around week_wed). Returns (date, time)."""
    mon = week_wed - pd.Timedelta(days=2)
    days = [(mon + pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]
    hol_mtw = [d for d in days[:3] if d in closed]
    if not hol_mtw:
        return days[2], '10:30'
    late = '11:00' if week_wed.year <= 2024 else '12:00'
    xmas_ny = any(d[5:] in ('12-24', '12-25', '12-26', '01-01', '01-02') for d in hol_mtw)
    if len(hol_mtw) >= 2 or (xmas_ny and week_wed.year <= 2024 and any(pd.Timestamp(d).weekday() in (1, 2) for d in hol_mtw)):
        return days[4], late
    if days[3] in closed:
        return days[4], late
    return days[3], late

e = inv[(inv.ev == 'Crude Oil Inventories') & ~inv.placeholder & (inv.d >= '2010-01-01')].copy()
e['t'] = e.et.dt.strftime('%H:%M')
e = e.sort_values('et').drop_duplicates('d')
e['wk'] = pd.to_datetime(e.d).dt.to_period('W-SUN')   # Mon..Sun weeks
inv_by_wk = e.groupby('wk').agg(d=('d', list), t=('t', list))
weeks = pd.period_range('2010-01-04', '2026-12-31', freq='W-SUN')
match = tot = 0; mism = []
for w in weeks:
    wed = w.start_time + pd.Timedelta(days=2)
    rd, rt = eia_rule(wed)
    if w in inv_by_wk.index and wed.strftime('%Y-%m-%d') <= INV_END:
        tot += 1
        di, ti = inv_by_wk.loc[w, 'd'][0], inv_by_wk.loc[w, 't'][0]
        ti_n = '10:30' if ti == '10:25' else ti
        if (di, ti_n) == (rd, rt): match += 1
        else: mism.append((str(w.start_time.date()), di, ti, rd, rt))
log(f'\n--- EIA verification ---\nRule vs investing.com 2010-01..{INV_END}: {match}/{tot} weeks identical (date+time); mismatches: {mism}')

EIA_OVERRIDE = {  # week Wednesday -> (date, time, evidence)  [web-search evidence, 2022-10..2026]
    '2024-12-25': ('2024-12-27', '13:00', 'Reuters poll / MarketNews: delayed to Fri 13:00 ET (Christmas, fed. closure 12-24/25)'),
    '2025-01-01': ('2025-01-02', '11:00', 'EIA WPSR schedule page (holiday table): Thu 2025-01-02 11:00'),
    '2025-01-22': ('2025-01-23', '12:00', 'EIA WPSR schedule page: MLK/Inauguration week Thu 12:00'),
    '2025-02-19': ('2025-02-20', '12:00', 'EIA WPSR schedule page: Presidents Day week Thu 12:00'),
    '2025-05-28': ('2025-05-29', '12:00', 'EIA WPSR schedule page: Memorial Day week Thu 12:00'),
    '2025-09-03': ('2025-09-04', '12:00', 'EIA WPSR page: released Thu 2025-09-04 12:00'),
    '2023-12-27': ('2023-12-28', '11:00', 'Reuters/BOE Report: Thu 11:00 EST (Christmas)'),
    '2026-10-14': ('2026-10-15', '12:00', 'Reuters/BOE Report 2026-10-09: delayed to Thu 2026-10-15 noon EDT (Columbus Day)'),
}
rows = []
for w in weeks:
    wed = w.start_time + pd.Timedelta(days=2); ws = wed.strftime('%Y-%m-%d')
    if ws <= INV_END and w in inv_by_wk.index:
        for di, ti in zip(inv_by_wk.loc[w, 'd'], inv_by_wk.loc[w, 't']):
            note = ''
            if ti == '10:25': ti, note = '10:30', 'investing shows 10:25; set to scheduled 10:30 (EIA system outage period: 2022-06-22 report postponed, released 2022-06-29)'
            if di == '2013-10-21': note = 'government-shutdown delayed release'
            rows.append(dict(date=di, time_et=ti, method='observed', source='investing.com via systamental/cryptodatapy', note=note))
    elif ws <= INV_END:
        rows.append(dict(date='', time_et='', method='no_release', source='investing.com via systamental/cryptodatapy',
                         note=f'no release in week of {ws} (gap in source; known disruption)'))
    else:
        if ws in EIA_OVERRIDE:
            d, t, ev = EIA_OVERRIDE[ws]
            rd, rt = eia_rule(wed)
            rows.append(dict(date=d, time_et=t, method='web_evidence', source='web search (EIA schedule page / Reuters)',
                             note=ev + ('' if (rd, rt) == (d, t) else f' [rule would give {rd} {rt}]')))
        else:
            rd, rt = eia_rule(wed)
            note = ''
            if ws in ('2025-12-24', '2025-12-31'):
                note = 'LOW CONFIDENCE: Christmas/New Year week (possible extra federal closures); not verified'
            if ws in ('2025-10-15', '2025-11-12'):
                note = 'holiday week during Oct-Nov 2025 shutdown; rule-based, not verified'
            rows.append(dict(date=rd, time_et=rt, method='rule', source='rule: Wed 10:30; fed. holiday Mon-Wed -> Thu (11:00 <=2024, 12:00 >=2025)', note=note))
eia = pd.DataFrame(rows)
eia = eia[eia.date != ''].sort_values('date').reset_index(drop=True)
eia['status'] = eia.date.apply(status)
eia = eia[eia.date <= '2026-12-31']
log('EIA rows', len(eia), eia.method.value_counts().to_dict(), 'times', eia.time_et.value_counts().to_dict())
eia[['date', 'time_et', 'status', 'method', 'source', 'note']].to_csv(OUT/'eia.csv', index=False)
# FF single Crude row check
for _, r in ff[ff.Event == 'Crude Oil Inventories'].iterrows():
    log('FF crude row', r.d, r.t, 'in eia.csv:', ((eia.date == r.d) & (eia.time_et == r.t)).any())

# ================================================================ 5. NYSE calendar
import pandas_market_calendars as pmc
import exchange_calendars as xc
nyse = pmc.get_calendar('NYSE')
s = nyse.schedule(start_date='2004-12-01', end_date='2027-01-31')
close_local = s.market_close.dt.tz_convert(NY)
s['early_close'] = (close_local.dt.strftime('%H:%M') <= '14:00').astype(int)  # planned half-days (13:00); 2005-06-01 15:56 systems-issue close not counted
td = pd.DatetimeIndex(s.index.normalize())
# all weekdays that are not trading days
wd = pd.bdate_range('2004-12-01', '2027-01-31')
closed_wd = wd.difference(td)
REG_HOL = set(pd.DatetimeIndex(nyse.holidays().holidays).strftime('%Y-%m-%d'))  # regular + ad-hoc in pmc
SPECIAL = {'2004-06-11', '2007-01-02', '2012-10-29', '2012-10-30', '2018-12-05', '2025-01-09'}
cal = pd.DataFrame({'date': td.strftime('%Y-%m-%d'), 'early_close': s.early_close.values,
                    'close_time_et': close_local.dt.strftime('%H:%M').values})
nxt = []
for d in td:
    n = d + pd.offsets.BDay(1)
    nxt.append(n.strftime('%Y-%m-%d') if n in closed_wd else '')
cal['next_closed_weekday'] = nxt
cal['pre_holiday'] = [1 if (x and x not in SPECIAL) else 0 for x in nxt]
cal['pre_special_closure'] = [1 if (x and x in SPECIAL) else 0 for x in nxt]
# opex: 3rd Friday; if not a trading day -> preceding trading day (Thursday)
tdset = set(cal.date)
opex = set()
for p in pd.period_range('2005-01', '2026-12', freq='M'):
    fr = pd.date_range(p.start_time, p.end_time, freq='W-FRI')[2]
    d = fr
    while d.strftime('%Y-%m-%d') not in tdset:
        d -= pd.Timedelta(days=1)
    opex.add(d.strftime('%Y-%m-%d'))
cal['opex'] = cal.date.isin(opex).astype(int)
cal = cal[(cal.date >= '2005-01-01') & (cal.date <= '2026-12-31')].reset_index(drop=True)
# cross-check with exchange_calendars XNYS and QuantConnect Lean market-hours DB
x = xc.get_calendar('XNYS', start='2005-01-01', end='2026-12-31')
xs = set(x.sessions.strftime('%Y-%m-%d'))
xe = set(x.early_closes.strftime('%Y-%m-%d'))
lean = json.load(open(RAW/'cal__QuantConnect__Lean/Data/market-hours/market-hours-database.json'))['entries']['Equity-usa-[*]']
lh = {pd.Timestamp(dt.datetime.strptime(h, '%m/%d/%Y')).strftime('%Y-%m-%d') for h in lean['holidays']}
le = {pd.Timestamp(dt.datetime.strptime(k, '%m/%d/%Y')).strftime('%Y-%m-%d') for k in lean['earlyCloses']}
pm_sessions = set(cal.date); pm_early = set(cal[cal.early_close == 1].date)
log('\n--- NYSE verification ---')
log('sessions pmc', len(pm_sessions), 'xcal', len(xs), 'diff pmc-x', sorted(pm_sessions - xs), 'x-pmc', sorted(xs - pm_sessions))
log('early closes pmc', len(pm_early), 'xcal', len(xe), 'diff', sorted(pm_early ^ xe))
wd05 = set(pd.bdate_range('2005-01-01', '2026-12-31').strftime('%Y-%m-%d'))
lean_closed = {d for d in lh if d in wd05}
log('Lean holidays (weekday, 2005-2026)', len(lean_closed), 'vs pmc closed weekdays', len(wd05 - pm_sessions),
    '| in Lean not pmc', sorted(lean_closed - (wd05 - pm_sessions)), '| in pmc not Lean', sorted((wd05 - pm_sessions) - lean_closed))
le05 = {d for d in le if '2005' <= d <= '2026-12-31'}
log('Lean early closes 2005-2026', len(le05), 'diff vs pmc', sorted(le05 ^ pm_early))
log('NYSE rows', len(cal), 'early', int(cal.early_close.sum()), 'pre_holiday', int(cal.pre_holiday.sum()),
    'pre_special', int(cal.pre_special_closure.sum()), 'opex', int(cal.opex.sum()))
log('opex not on Friday:', cal[(cal.opex == 1) & (pd.to_datetime(cal.date).dt.weekday != 4)].date.tolist())
cal[['date', 'early_close', 'pre_holiday', 'opex', 'close_time_et', 'pre_special_closure', 'next_closed_weekday']].to_csv(OUT/'us_market_calendar.csv', index=False)

Path('/tmp/claude-0/-home-user/c091d643-8b37-56a3-8434-e444d073761d/scratchpad/cal/build_log.txt').write_text('\n'.join(LOG))

# ---------------------------------------------------------------- provenance table
import subprocess
prov = []
for name, rel, used in [
    ('JK', 'cal__marekjarocinski__jkshocks_update_fed', 'source_data/fomc_surprises_jk.csv (FOMC announcement date+time, Bloomberg)'),
    ('RR', 'cal__returnandrisk__r-code', 'fomcdates_1936_2018.csv (Fed website scrape: meeting dates, scheduled, pressconf)'),
    ('PFW', 'cal__hackingthemarkets__pyfedwatch', 'data/fomc/fomc_data.xlsx (rate-decision dates/times, UTC-5)'),
    ('INV', 'cal__systamental__cryptodatapy', 'tests/data/ip_econ_cal.csv (investing.com calendar dump 1970..2022-09-21, UTC)'),
    ('FF', 'cal__ehsanrs2__forexfactory-scraper', 'high_impact_events_calendar.csv (ForexFactory high impact 2020-01..2026-01-30, UTC)'),
    ('BJ', 'cal__borisjoffe__FOMC-dates.js', 'dates.csv (FOMC 2021-2024)'),
    ('FP', 'cal__helivan-research__fomc-personas', 'fomc_personas/macro.py FOMC_MEETINGS 2018-2025 + LIVE_DECISIONS 2026-2027; paper/.cache/fomc_votes/* (statements scraped through 2026-09-16)'),
    ('VN', 'cal__gitlab__vaughnn.noah-portfolio__market-aware', 'data/fomc_meetings_2000_2027.json (cross-check only; contains errors)'),
    ('LEAN', 'cal__QuantConnect__Lean', 'Data/market-hours/market-hours-database.json (NYSE holidays/early closes cross-check)')]:
    d = RAW/rel
    sha = subprocess.run(['git', '-C', str(d), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    url = subprocess.run(['git', '-C', str(d), 'remote', 'get-url', 'origin'], capture_output=True, text=True).stdout.strip()
    prov.append(dict(code=name, repo=url, commit=sha, local=str(d), used=used))
prov.append(dict(code='PMC', repo='pypi:pandas_market_calendars', commit=pmc.__version__, local='', used='NYSE schedule (primary)'))
prov.append(dict(code='XC', repo='pypi:exchange_calendars', commit=xc.__version__, local='', used='XNYS sessions/early closes (cross-check)'))
prov.append(dict(code='WEB', repo='WebSearch results (bls.gov schedule pages, usinflationcalculator, therighttrader, fedratecalc, Reuters/BOE Report, EIA schedule page)', commit='as of 2026-10-15', local='', used='CPI/NFP Feb-Dec 2026 dates; EIA 2023-2026 holiday-week overrides'))
pd.DataFrame(prov).to_csv(OUT/'_sources.csv', index=False)
