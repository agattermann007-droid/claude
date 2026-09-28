"""Build 6.70, Signal-Ebene zu Z2 (Tagessperre der Fades je Symbol): Welche live gehandelten Fade-Signale fielen weg, und wie
liefen sie virtuell? Ein Signal faellt weg, wenn am selben Prop-Tag (17:00-17:00 NY) ein frueheres live-Signal desselben
Symbols mit Verlust endete und der EA das Ergebnis vor dem Einstieg kannte (known_time). Live = Portfolio-Waechter PF200 > 1,15
wie im EA (port_live_ea, Fenster 600 Tage). Je Periode: Signale je Jahr, Trefferquote und R je Signal der weggefallenen
Signale gegen alle uebrigen live-Signale; getrennt nach Symbol und nach gleicher / anderer Richtung als der Verlust.
Das Konto (Groesse, Budget, Schutz gueltiger Tage) ist hier nicht abgebildet.
Aufruf: python a70_sig.py [bis JJJJ-MM-TT]  (im Ordner mit den Daten; Zukunftstest in der Kopie DB26)"""
import numpy as np, sys, os
import pg_guard as PGd, pg_blocks as PB, x41

END = sys.argv[1] if len(sys.argv) > 1 else "2026-01-01"
ch = PGd.chain(x41.S70_OHNE)
# known_time je Signal (Kette ext bis 2021 + gft ab 2022 wie PGd.chain)
kts = []
for s_, nm in enumerate(PB.F10):
    per = {}
    for ds in ("ext", "gft"):
        f = PB.fi(ds, nm)
        keep, live, tp, w = PB.apply_rule(f, x41.S70_OHNE if nm not in set(x41.S70_OHNE.get("exempt", ())) else dict(kind="none"))
        per[ds] = (f, keep)
    (f1, k1), (f2, k2) = per["ext"], per["gft"]
    v1 = (f1["t_entry"] < PGd.LIM22) & k1
    kts.append(np.r_[PGd.known_time("ext", f1)[v1], PGd.known_time("gft", f2)[k2]])
te = np.concatenate([c["te"] for c in ch]); R = np.concatenate([c["R"] for c in ch]); mi = np.concatenate([c["s"] for c in ch])
kt = np.concatenate(kts)
live = PGd.port_live_ea(te, kt, mi, R, 200, 1.15, 600)
sym = np.array([PB.fi("gft", PB.F10[i])["sym"] for i in mi])
d = np.concatenate([PB.fi("ext", nm)["d"][(PB.fi("ext", nm)["t_entry"] < PGd.LIM22) & PB.apply_rule(PB.fi("ext", nm), x41.S70_OHNE if nm not in set(x41.S70_OHNE.get("exempt", ())) else dict(kind="none"))[0]].tolist()
                    + PB.fi("gft", nm)["d"][PB.apply_rule(PB.fi("gft", nm), x41.S70_OHNE if nm not in set(x41.S70_OHNE.get("exempt", ())) else dict(kind="none"))[0]].tolist()
                    for nm in PB.F10])
pday = (te + 420) // 1440
blk = np.zeros(len(te), bool); same = np.zeros(len(te), bool)
idx = np.nonzero(live)[0]
for i in idx:
    j = idx[(pday[idx] == pday[i]) & (sym[idx] == sym[i]) & (kt[idx] <= te[i]) & (R[idx] < 0) & (idx != i)]
    if len(j):
        blk[i] = True
        same[i] = np.any(d[j] == d[i])
end = np.datetime64(END, "m").astype(np.int64)
PER = [("2006-13", "2006-01-01", "2014-01-01"), ("2014-21", "2014-01-01", "2022-01-01"), ("2022-23", "2022-01-01", "2024-01-01"),
       ("2024-25", "2024-01-01", "2026-01-01"), ("2026 (bis Aug.)", "2026-01-01", "2026-09-03")]
lines = [f"Z2 auf Signal-Ebene (live-Signale, Portfolio-Waechter wie im EA), Daten bis {END}"]
for pn, a, b in PER:
    lo = np.datetime64(a, "m").astype(np.int64); hi = min(np.datetime64(b, "m").astype(np.int64), end)
    if hi <= lo:
        continue
    yrs = (hi - lo) / (365.25 * 1440)
    sel = live & (te >= lo) & (te < hi)
    for nm_s in ("alle", "NAS", "XAU"):
        s2 = sel if nm_s == "alle" else sel & (sym == nm_s)
        b_ = s2 & blk; o_ = s2 & ~blk
        def st(m):
            return f"{m.sum() / yrs:5.1f}/J WR {100 * np.mean(R[m] > 0) if m.any() else 0:5.1f} % R {R[m].mean() if m.any() else 0:+.3f}"
        extra = ""
        if nm_s == "XAU":
            extra = f" | davon gleiche Richtung {st(b_ & same)}, andere {st(b_ & ~same)}"
        lines.append(f"{pn:15s} {nm_s:4s} weggefallen {st(b_)} | uebrige live {st(o_)}{extra}")
txt = "\n".join(lines)
print(txt)
os.makedirs("ergebnisse", exist_ok=True)
open(os.path.join("ergebnisse", "a70_sig.txt"), "a").write(txt + "\n\n")
