"""Grid-Studie Teil 4: Haengt der Vorteil der Grid-Regel S von den Kosten ab? Virtuelle Fade-Signale 2006-2025 mit
Spread x Faktor (0,3 / 0,6 / 1,0 des Fremddaten-Spreads; GFT-Exporte hatten engere Spreads), alle Signale gegen Regel S
(M5, Laenge 15, 1000 Schenkel, Stop-Chance >= 70 % -> kein Fade)."""
import numpy as np, sys
import pg_data as PD, gsig as G, cands as K
import pg_fade as PF
from pg_study import F10, PER

YRS = {"06-13": 8.0, "14-21": 8.0, "22-23": 2.0, "24-25": 2.0}


def stats(R, yr, keep):
    out = []
    for nm, a, b in PER:
        k = keep & (yr >= a) & (yr < b)
        r = R[k]; w = r[r > 0].sum(); l = -r[r < 0].sum()
        out.append(f"{k.sum() / YRS[nm]:4.0f}/J {100 * (r > 0).mean():3.0f}% PF{(w / l if l > 0 else 9.9):4.2f} {r.sum() / YRS[nm]:+6.1f}R")
    return " | ".join(out)


def main(tf=5, L=15, mp=1000, th=0.70):
    base = PD.data_all()
    for fac in (0.3, 0.6, 1.0):
        D = {s: dict(d, sp=d["sp"] * fac) for s, d in base.items()}
        G._D = D; K._CACHE.clear(); PF._PIV.clear()
        fis = {nm: PF.fade_info(nm) for nm in F10}
        R = np.concatenate([fis[nm]["R"] for nm in F10])
        yr = PD.year_of(np.concatenate([fis[nm]["t_entry"] for nm in F10]))
        X = np.concatenate([PF.grid_features(fis[nm], tf, L, mp, 30) for nm in F10])
        keep = ~(np.isfinite(X[:, 2]) & (X[:, 1] < 0) & (X[:, 6] >= th))
        print(f"Spread x{fac}: alle     {stats(R, yr, np.ones(len(R), bool))}")
        print(f"Spread x{fac}: Regel S  {stats(R, yr, keep)}")
        print(f"Spread x{fac}: nur die ausgelassenen {stats(R, yr, ~keep)}", flush=True)


if __name__ == "__main__":
    main()
