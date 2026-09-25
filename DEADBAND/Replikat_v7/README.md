# Replikat v7: RSI21-Labor und Build 6.20

Suche nach Verbesserungen des RSI21-Moduls: erst **ohne Konto** (RSI21 allein, schnell, 2006–2025), dann **im
Kontomotor** von Replikat v6 (`eng6`/`evl6`, alle Module, GFT-Regeln). Kursdaten und Zwischenstände liegen **nicht**
im Repo (`cache/` ist ausgeschlossen).

## Daten

| Datensatz | Inhalt | Erzeugung |
|---|---|---|
| `../extdata/*_ext_M5.csv` | Fremddaten Gold 2006–2026, NAS100 2005–2025 | `../extdata/scripts/run_all.sh` (Quellen siehe `../extdata/DATEN_BERICHT.md`, Abschnitt 9). Neu aufgebaut am 25.09.2026, SHA-256 identisch mit dem Datenbericht |
| `cache/DA.pkl` | beide Symbole 2006-01 … 2025-12 im Format von `prep5` | `r7data.py` |
| `../data/*.csv` („gft“) | **Ersatz** für die GFT-Exporte (nicht im Repo): Fremddaten 2022-01-03 … 2025-12-31, Gold-Spread je Jahr auf den GFT-Median skaliert (7/8/9/22 statt 30/30/33/51 Punkte) | `mk_ersatz_gft.py`, danach `../Replikat_v6/sig5.py` |
| „ext“ | Fremddaten 2006–2021 wie in v6 | `../Replikat_v6/sig_ext.py` |

Gegenprobe: 6.10 Ertrag auf „ext“ neu gerechnet 1,99 Ausz / 0,34 Busts / 511 $ je Jahr, `x39_ext.json` 2,02 / 0,40 / 503 $
(`t_repro.py`; gleiche Daten, andere Bibliotheksversionen).

## Dateien

| Datei | Inhalt |
|---|---|
| `r7data.py` | Kursdaten 2006–2025 (Aggregate M15/M30/H1/D1 wie `prep5`) |
| `r7sig.py` | RSI21-Kandidaten mit Merkmalen (vektorisiert), Filter und Folgesignal wie die EA; `r21_dict` = Signalliste für `eng6`. `t_basis.py` prüft: identisch mit `sig5.r21_signals` (4632/4632 Signale) |
| `r7sim.py` | Positions-Simulator je Symbol ohne Konto (Platz A/B, Verlustgrenze je Tag, Wochenend-Pause und Wiederaufnahme, Swap, Kommission, Zeit-Exit, Zeit-Stop, Break-even, Nachzug) und Kennzahlen (R x Gewicht, Sharpe der Wochen, Bust-Ersatz, Risiko-Parität) |
| `r7lim.py` | Einzelsignal-Simulation für Einstiegsvarianten (Markt gegen Limit-Rückzug) |
| `r7kand.py` | Regel-Sätze (Basis, NAS ohne Kreuz, Gold nur M15, Volumen-Bestätigung …) |
| `r7lab.py` | gemeinsame Helfer der Screenings |
| `r7konto.py` | Kontobewertung wie x39 (6.10 Ertrag) mit beliebiger RSI21-Signalliste |
| `s1_ablation.py` … `s18_volumen.py` | Screenings ohne Konto (Regeln, Ausstiege, Filter, Kreuz, Zeitfenster, Rückzug, Wächter, Zeitebenen, RSI-Länge, Volumen) |
| `a1_konto.py`, `a3_konto.py`, `a4_raster.py`, `a5_fein.py` | Screenings im Kontomotor (beide Datensätze) |
| `t_bust.py`, `t_bustpfad.py`, `t_skip.py` | Diagnose: Bust-Ursache (immer der Boden), Bust-Episoden, ausgelassene RSI21-Signale |
| `e1_final.py` | **Endbewertung 6.10 gegen 6.20** (gft 16 Störungen mit Startjahren, ext 8 Störungen, RSI21 allein) |
| `e3_jahre.py` | 6.10 gegen 6.20 je Startjahr auf den Fremddaten 2006–2021 |
| `e2_tabellen.py` | Tabellen „RSI21 allein“ für den Bericht |
| `ergebnisse/*.json` | Ergebnisse (e1 = Endzahlen, e2 = RSI21 allein, e3 = Startjahre Fremddaten, a1/a4/a5 = Konto-Screenings) |

## Ablauf

```
pip install numpy pandas numba
(cd ../extdata/scripts && ./run_all.sh)       # Fremddaten (Downloads siehe Datenbericht; quality/rolljumps brauchen GFT-Daten)
python mk_ersatz_gft.py                        # ../data = Ersatz-GFT 2022-25
(cd ../Replikat_v6 && python sig5.py && python sig_ext.py)
python r7data.py && python t_basis.py          # Labor-Daten, Gleichheit mit sig5
python e1_final.py                             # Endbewertung 6.10 / 6.20 (~5 min, 4 Prozesse)
python e2_tabellen.py                          # RSI21 allein
```

## Grenzen

- Die GFT-Originaldaten 2022–2026 fehlen; „gft“ ist ein Ersatz aus Dukascopy-Gold und einem MT5-US100-Export (NAS
  endet 2025-12-31). Tick-Volumen: Gold ab 2016 Proxy aus dem Dukascopy-Volumen, NAS 2020-05…12 ohne Volumen (dort
  lässt der Filter alles durch, wie die EA bei fehlendem Volumen).
- Kein Tick-Replay, keine News-Sperre im Nachbau. Busts hängen an wenigen Marktphasen (auf „gft“ fast nur Juni 2025);
  belastbar ist der Vergleich unter gleichen Annahmen, nicht die absolute Zahl.
