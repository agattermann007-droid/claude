"""Replikat 9 - Abgleich Nachbau <-> Live-Trades 01.-16.10.2026 (Serverzeit, aus dem Auftrag).

Je Live-Trade: Modulkandidaten nach Uhrzeit/Symbol/Richtung, passendes Signal im Nachbau (gleiche Einstiegskerze),
Einstieg/Stop/Ziel im Vergleich (Punkte), Waechter-Status. Aufruf: python3 check_live9.py NAME
"""
import sys
import numpy as np
import aufbau9 as AU

# Einstieg (Server), Symbol, Richtung, Lot, Preis, SL, TP (0 = keins), Ausstieg (Server), Preis, Ergebnis $, Modul laut Zuordnung
LIVE = [
    ("2026-10-01 20:25", "XAU", -1, 0.07, 4176.21, 4184.91, 4163.22, "2026-10-01 20:30:42", 4185.97, -68.32, "X1000S"),
    ("2026-10-05 18:00", "NAS", 1, 0.04, 30997.0, 0.0, 0.0, "2026-10-05 22:55", 31050.0, 21.34, "Noise"),
    ("2026-10-06 11:35", "XAU", -1, 0.08, 4146.24, 4155.42, 4137.74, "2026-10-06 11:59:21", 4155.58, -74.72, "X0300S"),
    ("2026-10-06 19:35", "NAS", 1, 0.07, 31293.22, 31208.31, 31365.39, "2026-10-06 23:40", 31245.24, -33.59, "N1100"),
    ("2026-10-06 21:40", "NAS", 1, 0.05, 31265.82, 31207.99, 31282.49, "2026-10-06 21:55:30", 31282.93, 8.56, "N1300/N1330"),
    ("2026-10-07 04:10", "NAS", 1, 0.20, 31248.27, 31220.27, 31253.89, "2026-10-07 04:30:45", 31254.24, 11.94, "N1800"),
    ("2026-10-07 22:10", "NAS", 1, 0.09, 31105.52, 31040.09, 31121.64, "2026-10-07 22:18:11", 31121.59, 14.46, "N1300/N1330"),
    ("2026-10-08 16:55", "XAU", -1, 0.03, 4131.39, 4155.97, 4109.81, "2026-10-08 19:01:28", 4109.82, 64.71, "X0630"),
    ("2026-10-09 14:05", "XAU", 1, 0.09, 4179.62, 4171.86, 4190.38, "2026-10-09 15:30:50", 4189.12, 85.50, "X0400"),
    ("2026-10-12 16:35", "NAS", -1, 0.10, 30727.04, 30772.34, 0.0, "2026-10-12 16:35:49", 30772.51, -45.47, "LW"),
    ("2026-10-12 19:55", "NAS", 1, 0.08, 30676.75, 30590.87, 30752.19, "2026-10-12 23:40", 30647.40, -23.48, "N1100"),
    ("2026-10-13 04:05", "NAS", 1, 0.09, 30504.42, 30422.15, 30581.49, "2026-10-13 05:04:43", 30420.34, -75.67, "N1800"),
    ("2026-10-14 16:00", "NAS", 1, 0.05, 30343.32, 30216.05, 30475.09, "2026-10-14 17:52:53", 30213.39, -64.97, "S0830"),
    ("2026-10-14 19:35", "NAS", 1, 0.03, 30025.82, 29844.06, 30219.04, "2026-10-14 22:30", 29974.93, -15.27, "N1030/N0930"),
    ("2026-10-15 19:35", "NAS", 1, 0.03, 29729.22, 29605.89, 29844.69, "2026-10-15 20:40:41", 29844.79, 34.67, "N1030/N0930/N1100"),
    ("2026-10-16 19:50", "NAS", 1, 0.04, 29409.57, 29265.42, 29621.84, "2026-10-16 20:16:01", 29263.69, -58.35, "Fade"),
    ("2026-10-16 19:50", "NAS", 1, 0.01, 29408.85, 29243.61, 29658.19, "2026-10-16 20:19:29", 29243.74, -16.51, "Fade"),
]


def ny_min(s):
    return int((np.datetime64(s.replace(" ", "T"), "m") - np.timedelta64(7, "h")).astype(np.int64))


def abgleich(A, out=print):
    sigs = A["sigs"]; D = A["D"]
    zeilen = []
    for (te, sy, d, lot, px, sl, tp, tx, pxx, usd, mod) in LIVE:
        t = ny_min(te) // 5 * 5
        datenende = D[sy]["ny"][-1]
        kand = []
        for s in sigs:
            if s["sym"] != sy:
                continue
            j = np.nonzero((s["t_entry"] == t) & (s["dir"] == d))[0]
            for q in j:
                kand.append((s["name"], s, q))
        if mod == "Noise":
            out(f"{te} {sy} {'buy' if d > 0 else 'sell'} {mod:18s}: Noise-Pruefung 11:00 NY - Abgleich ueber sig5 (nicht Teil der Fade-Liste)")
            continue
        if t > datenende:
            out(f"{te} {sy} {'buy' if d > 0 else 'sell'} {mod:18s}: KEINE KURSE (Daten enden {np.datetime64(int(datenende), 'm')} NY)")
            zeilen.append((te, mod, None))
            continue
        if not kand:
            out(f"{te} {sy} {'buy' if d > 0 else 'sell'} {mod:18s}: kein Signal im Nachbau an dieser Kerze")
            zeilen.append((te, mod, None))
            continue
        for nm, s, q in kand:
            ent, st, goal = s["ent"][q], s["st"][q], s["goal"][q]
            out(f"{te} {sy} {'buy' if d > 0 else 'sell'} {mod:18s} -> {nm:6s} live={bool(s['live'][q])} PF {s['pf'][q]:.2f}/{s['npf'][q]} | "
                f"Einstieg {ent:9.2f} ({ent - px:+7.2f}) Stop {st:9.2f} ({st - sl:+7.2f}) Ziel {goal:9.2f} ({(goal - tp) if tp > 0 else 0.0:+7.2f}) "
                f"| R virt {s['R'][q]:+.2f}")
            zeilen.append((te, nm, dict(ent=ent, st=st, goal=goal, d_ent=ent - px, d_st=st - sl, d_goal=(goal - tp) if tp > 0 else np.nan)))
    return zeilen


if __name__ == "__main__":
    A = AU.baue(sys.argv[1] if len(sys.argv) > 1 else "frei")
    abgleich(A)
