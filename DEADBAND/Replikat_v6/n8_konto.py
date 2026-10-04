"""Neues Konzept (Stufe 8): eigenstaendige Strategien im Konto-Replikat (eng6, alle GFT-Regeln, strenge Lesart),
ALTE MODULE AUS (DEADBAND, RSI21, Noise, Fades). Zeitraum 2022-03-21 bis 2025-12-31 (rollierende 10k-Konten).
Ein Strom = (Symbol, Generator, Argumente, Strom-Parameter GP). Bewertet: Auszahlungen/J, netto/J, Pleiten, Zyklus."""
import sys, json, numpy as np
import eng6 as E, evl6 as V, gsig as G, scan6 as S, cands as K
import x35 as X, r6

BASEN = dict(r6.SAFE, validpct=0.505, minpayout=105.0, db_on=0, r21_on=0, nz_on=0, cool_n=3, gesamtbudget=0.9, idea_cap=0.9,
             bank_on=1, bank_last=5, bank_minr=0.3, bank_mods=15, ddfull=5.0, ddmin=2.5, ddfmin=0.2, belowstart=0.95,
             valid_stop=1, ge_mode=1, ge_rueck=0.0, db_tp1r=1.5, db_be=0.05, db_tp1f=0.5)


def block(sym, gen, args, s_):
    """Signale eines Generators als eng6-Block (Feiertage und Stop >= 6 Spreads wie der EA)."""
    D, ny, days, t_end, atr = S.prep(sym)
    ie, d, rd, tp, ix = gen(ny, D["o"], D["h"], D["l"], D["c"], D["sp"], days, t_end, atr, *args)
    te = ny[ie]; tx = ny[np.minimum(ix, len(ny) - 1)]
    keep = np.array([(int(a // 1440) not in X.FREI) and (int(b // 1440) not in X.FREI) for a, b in zip(te, tx)], bool)
    if len(ie):
        keep &= rd >= X.MINSP * D["sp"][ie]
    return K.block(sym, ie[keep], d[keep], rd[keep], tp[keep], ix[keep], s_)


def konto(streams, kw=None, seeds=tuple(range(8)), step=3, horizons=(250, 500), end="2025-12-31", base=None):
    blks = []; gps = []
    for s_, (sym, gen, args, gp) in enumerate(streams):
        blks.append(block(sym, gen, args, s_))
        gps.append(dict(dict(on=1, risk=0.75, maxtrades=1, harv=1), **gp))
    GP = E.gparams(gps)
    V.set_generic(blks, GP)
    Pv = E.params(**dict(base or BASEN, **(kw or {})))
    return V.evaluate(Pv, GP=GP, horizons=horizons, step=step, seeds=seeds, skip=0.05, end=end)


def line(lbl, m):
    return (f"{lbl:<48s} Ausz {m['pay']:5.2f} Ø{m['paymean']:4.0f}$ netto {m['net']:5.0f} Pleiten {m['bust']:.3f} "
            f"Zyklus {m['cyc']:4.1f}T gültig/J {m['valid']:4.1f} Tr/J {m['tr']:4.0f} WR {m['wr']:4.1f} S6 {m['s6']:4.2f} maxDD {m['maxdd']:4.0f}")
