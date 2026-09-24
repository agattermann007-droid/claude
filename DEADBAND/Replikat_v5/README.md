# Replikat v5: DEADBAND LIVE 4, Build 5.00 / 5.10 KOMBI

Python-Nachbau des EA auf den M5-Kursen des GFT-Terminals (XAUUSD.x, NAS100.x, 03.01.2022 bis 02.09.2026).
Damit wurden die Änderungen von Build 5.10 ausgewählt und geprüft. Kursdaten und Zwischenstände liegen
**nicht** im Repo.

## Dateien

| Datei | Inhalt |
|---|---|
| `prep5.py` | lädt die MT5-Exporte, NY-Zeit (Server − 7 h), Indikatoren wie MT5 (RSI Wilder, ATR, Stochastik, MACD, EMA), M15/H1/D1 |
| `sig5.py` | Signalströme der drei Module (DEADBAND, RSI21, NAS-Noise), unabhängig vom Kontozustand → `cache/sig5.pkl` |
| `eng5.py` | numba-Kern: ein Konto über die Laufzeit (GFT-Regeln, EA-Bremsen, Auszahlungen, Neukauf nach Bust). Alle Schalter in `PN`/`params()` |
| `evl5.py` | Bewertung: rollierende Starts (alle 3 Handelstage ein neues 10k-Konto, Laufzeit 1/2/3 Jahre), Störungen, Serien aus dem Trade-Protokoll |
| `batch.py`, `robust.py` | Stapelläufe; `robust.py` = 16 Störungen (8 % Signale ausgelassen, Einstiegsschlupf 0,3 × Spread) |
| `split.py` | Kennzahlen nach Startjahr |
| `final.py` | Schlussvergleich 5.00 ↔ 5.10 (beide Regel-Lesarten, EOD-Boden), Startjahre, Pfad ab 03.01.2022 |
| `streuung.py` | Streuung der Kennzahlen über die 16 Störungen (Standardabweichung, Standardfehler) |
| `ergebnisse/*.json` | Ergebnisse von `final.py` (`final.json`, `final_all.json`) und `streuung.py` (`streuung.json`) |

## Ablauf

```
pip install numpy pandas numba
mkdir ../data
# MT5-Exporte (Tab-getrennt, M5) als ../data/XAUUSD.x_M5.csv und ../data/NAS100.x_M5.csv ablegen
python prep5.py        # Datenaufbereitung -> cache/
python sig5.py         # Signale -> cache/sig5.pkl
python final.py        # Schlussvergleich (rechnet mit 4 Prozessen)
```

## Konventionen (vorsichtig gewählt)

- Einstieg am Open der M5-Kerze nach dem Signal, Long zum Ask; in derselben Kerze zählt der Stop vor dem Ziel.
- Firmenregeln: Boden am schlechtesten Kurs der Kerze, Floating- und Tagesregel am Open (die EA-Bremsen
  wirken live tickgenau), Equity-Hoch am besten Kurs.
- Strenge Lesart der Floating-Regel (`rule_losers=1`): GFT zählt nur die **Verlustpositionen**, ein Gewinner
  verdeckt keinen Verlierer. Swap wird zum Rollover gebucht (Mittwoch dreifach).
- Auszahlung: 5 gültige Tage (≥ 0,5 %), 10 Tage Zyklus, Mindestgewinn 131,25 $ (105 $ Anteil), 80 % Anteil,
  3 % Gebühr, Deckel 6 % für die ersten 2 Auszahlungen. Bust kostet 148,50 $ (Neukauf).
- Netto je Jahr = 0,8 × 0,97 × Auszahlungen − 148,50 × Busts.

## Grenzen

- Nur 4,7 Jahre Daten, darin ein NAS-Datenloch 2024 (Positionen werden davor neutral geschlossen).
- Kein Tick-Replay: Reihenfolge innerhalb einer M5-Kerze ist angenommen, Spreads aus dem Export.
- Die News-Sperre (±6 min um rote USD-Termine) ist nicht abgebildet (kein Kalender in den Daten), ebenso die
  130-s-Haltedauer vor Gewinnschliessungen; Wochenend-Spreads und Ausführungsfehler nur näherungsweise.
- v5 liegt im Niveau etwa 10–15 % unter den Zahlen im Kopf von 5.00 (früheres Replikat, mildere Konventionen);
  die Richtung stimmt. Ein Abgleich mit dem MT5-Strategietester steht für 5.10 noch aus. Absolute Zahlen sind
  Schätzungen; aussagekräftig ist der Vergleich 5.00 ↔ 5.10 unter gleichen Bedingungen.
