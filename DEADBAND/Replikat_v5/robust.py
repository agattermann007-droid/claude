"""Robuste Bewertung: 16 Stoerungen (8 % Signale ausgelassen, Schlupf), rollierend 1/2/3 J."""
import json, os, time
import eng5 as E, evl5 as V, batch as B


def run(configs, outfile, seeds=tuple(range(16)), skip=0.08, slip=0.3):
    res = json.load(open(outfile)) if os.path.exists(outfile) else {}
    for lbl, kw in configs:
        if lbl in res:
            continue
        kw2 = dict(B.SAFE); kw2.update(kw)
        t = time.time()
        r = V.evaluate(E.params(**kw2), horizons=(250, 500, 750), step=3, seeds=seeds, skip=skip, slip=slip)
        res[lbl] = dict(kw=kw2, mean=r["mean"], by={str(h): r[h] for h in (250, 500, 750)})
        json.dump(res, open(outfile, "w"), indent=1)
        print(f"{lbl} [{time.time()-t:.0f}s]", flush=True)
    return res


def show(res, keys=None):
    rows = [(k, v) for k, v in res.items() if keys is None or k in keys]
    rows.sort(key=lambda kv: -(kv[1]["mean"]["pay"] - 3*kv[1]["mean"]["bust"] - 0.1*kv[1]["mean"]["s5"] - 0.3*kv[1]["mean"]["s8"]))
    print(f"{'Konfig':<42s} {'Ausz':>5s} {'Bust':>5s} {'Netto':>6s} {'$/A':>4s} {'Luecke':>6s} {'S5':>5s} {'S8':>5s} {'maxS':>5s} {'VT3':>5s} {'WR':>5s} {'DD':>4s} {'P(B)':>5s} {'P(B)1J':>6s}")
    for k, v in rows:
        m = v["mean"]; b1 = v["by"]["250"]
        print(f"{k:<42s} {m['pay']:5.2f} {m['bust']:5.2f} {m['net']:6.0f} {m['paymean']:4.0f} {m['gapmax']:6.1f} {m['s5']:5.1f} {m['s8']:5.2f} {m['mx']:5.1f} {m['d3']:5.1f} {m['wr']:5.1f} {m['maxdd']:4.0f} {m['p_bust']:5.2f} {b1['p_bust']:6.2f}")
