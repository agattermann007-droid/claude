import pickle, statistics, sys
import bt
def lade(f):
    d = pickle.load(open(f, 'rb'))
    return d if isinstance(d, dict) else {0: d}
def zeile(name, sig, sp):
    k = bt.kennzahlen(sig, sp)
    st = lambda r: r['ergebnis']['status']
    fill = [r for r in sig if st(r) in ('Target', 'Stop', 'Zeitablauf', 'unklar')]
    rr = [r for r in fill if r['ergebnis']['R'] is not None]
    risk = [r['d'] * (r['E'] - r['S']) for r in fill]
    pos = sum(1 for r in rr if r['ergebnis']['R'] > 0) / max(1, len(rr))
    tq = sum(st(r) == 'Target' for r in fill) / max(1, len(fill))
    za = sum(st(r) == 'Zeitablauf' for r in fill) / max(1, len(fill))
    # Spread, bei dem netto = 0 waere: Summe R brutto = Summe sp/risk
    inv = sum(1 / (r['d'] * (r['E'] - r['S'])) for r in rr)
    be = k['summeR'] / inv if inv else 0
    return '| %s | %d | %.0f %% | %.1f %% | %.0f %% | %.0f %% | %+.3f | %+.3f | %.0f %% | %d | %.0f | %.1f |' % (
        name, k['signale'], 100 * k['fuellquote'], 100 * k['winrate_TvS'], 100 * tq, 100 * pos, k['R_je_trade'], k['R_netto_je_trade'], 100 * za,
        k['haltedauer_median_min'], statistics.median(risk) if risk else 0, be)
print('| Lauf | Signale | gefüllt | Target vor Stop | Target erreicht (alle gefüllten) | R > 0 | R je Trade brutto | R je Trade nach Spread | Zeitablauf | Haltedauer Median (min) | Stop-Abstand Median | Spread für ±0 |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for lab, f13, f14, sp, jahre in (
        ('NAS100 2021-23 (Abstimmung)', 'r13_nas.pkl', 'r14_nas.pkl', 1.5, (2021, 2022, 2023)),
        ('NAS100 2024 (Kontrolle)', 'r13_nas.pkl', 'r14_nas.pkl', 1.5, (2024,)),
        ('NAS100 2025 (zurückgehalten)', 'r13_nas.pkl', 'r14_nas.pkl', 1.5, (2025,)),
        ('GER40 Feb-Sep 2026 (zurückgehalten)', 'r13_ger26.pkl', 'r14_ger26.pkl', 1.5, None),
        ('GER40 2021-23 Dukascopy (zurückgehalten)', 'r13_gerduk.pkl', 'r14_gerduk.pkl', 1.5, None),
        ('ETH 2021-26 (zurückgehalten)', 'r13_eth.pkl', 'r14_eth.pkl', 2.0, None)):
    for ver, f in (('mt5-1.3', f13), ('mt5-1.4', f14)):
        d = lade(f)
        sig = [r for y, v in d.items() if jahre is None or y in jahre for r in v]
        print(zeile(lab + ' ' + ver, sig, sp))
