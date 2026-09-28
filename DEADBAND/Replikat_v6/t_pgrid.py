"""Pruefung pgrid.lux_pivots gegen eine woertliche Python-Uebertragung von fetchPivot/fetchData (LuxAlgo, Pine v6) auf
Zufallskursen: gleiche Pivots, gleiche Schenkel (Richtung, Groesse, Dauer)."""
import numpy as np, pgrid as PG


def pine_literal(o, c, length):
    HIGH, LOW = 1, -1
    currentPrice = c[0]; currentBar = 0; bias = None; bias_prev = None
    piv = dict(price=c[0], bar=0, bias=1)
    lastPrice = c[0]; lastBar = 0
    bull, bear = [], []
    cp_prev = currentPrice
    states = []
    for i in range(len(c)):
        mx = max(c[i], o[i]); mn = min(c[i], o[i])
        if i >= length - 1:
            upper = max(max(c[j], o[j]) for j in range(i - length + 1, i + 1))
            lower = min(min(c[j], o[j]) for j in range(i - length + 1, i + 1))
        else:
            upper = lower = None                                  # ta.highest/lowest: na
        nb = HIGH if (upper is not None and mx == upper) else (LOW if (lower is not None and mn == lower) else bias)
        bias_prev = bias; bias = nb
        newPivot = False
        cp_prev = currentPrice
        if bias is not None and bias_prev is not None and bias != bias_prev:
            newPivot = True
            piv = dict(price=currentPrice, bar=currentBar, bias=HIGH if bias == LOW else LOW)
            currentPrice = upper if bias == HIGH else lower
            currentBar = i
        elif bias is not None and bias_prev is None:
            # erster Wechsel von na (Pine: na != x ergibt kein true): wie pgrid - Start des ersten Laufs ohne Pivot
            currentPrice = upper if bias == HIGH else lower
            currentBar = i
        elif bias is not None:
            currentPrice = max(upper, currentPrice) if bias == HIGH else min(lower, currentPrice)
            currentBar = i if currentPrice != cp_prev else currentBar
        # fetchData
        bullish = piv["price"] > lastPrice
        priceDelta = abs(piv["price"] - lastPrice) / lastPrice
        barsDelta = piv["bar"] - lastBar
        if newPivot and barsDelta != 0:
            (bull if bullish else bear).append((i, priceDelta, barsDelta))
            lastPrice = piv["price"]; lastBar = piv["bar"]
        states.append((0 if bias is None else bias, piv["price"], piv["bar"], currentPrice, currentBar))
    return states, bull, bear


rng = np.random.default_rng(7)
ok = True
for trial in range(6):
    n = 3000
    c = 1000 + np.cumsum(rng.normal(0, 1, n)); o = np.r_[c[0], c[:-1]] + rng.normal(0, 0.3, n)
    if trial % 2:
        c = np.round(c, 0); o = np.round(o, 0)            # viele Gleichstaende
    L = [5, 10, 20][trial % 3]
    st, bull, bear = pine_literal(o, c, L)
    b, ppx, pbar, pbias, cpx, cbar, lc, ld, ls, lb = PG.lux_pivots(o, c, L)
    legs = sorted([(x[0], 1, x[1], x[2]) for x in bull] + [(x[0], -1, x[1], x[2]) for x in bear])
    same_legs = len(legs) == len(lc) and all(a[0] == lc[k] and a[1] == ld[k] and abs(a[2] - ls[k]) < 1e-12 and a[3] == lb[k] for k, a in enumerate(legs))
    first = next(i for i, s in enumerate(st) if s[0] != 0)
    same_state = all(st[i][0] == b[i] and st[i][3] == cpx[i] and st[i][4] == cbar[i] for i in range(first, n))
    # Pivot-Zustand erst ab dem ersten echten Pivot vergleichbar (vorher Startwert)
    k0 = lc[0] if len(lc) else n
    same_piv = all(st[i][1] == ppx[i] and st[i][2] == pbar[i] for i in range(k0, n))
    print(f"Versuch {trial} L={L}: Schenkel {len(legs)} / {len(lc)} {'gleich' if same_legs else 'ABWEICHUNG'}, Zustand {'gleich' if same_state else 'ABWEICHUNG'}, Pivot {'gleich' if same_piv else 'ABWEICHUNG'}")
    ok &= same_legs and same_state and same_piv
print("GESAMT", "IDENTISCH" if ok else "ABWEICHUNG")
