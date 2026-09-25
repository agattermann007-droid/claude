"""Reproduktion: 6.10 Ertrag auf den Fremddaten 2006-21 muss x39_ext.json treffen (gleiche Daten, gleicher Code)."""
import json, os, sys
import r7konto as K, evl6 as V

ref = json.load(open(os.path.join(K.V6, "ergebnisse", "x39_ext.json")))["6.10 Ertrag"]
r = K.evaluate("ext")
print(V.line("ext 6.10 Ertrag (neu gerechnet)", r))
print(V.line("ext 6.10 Ertrag (x39_ext.json)", ref))
for k in ("pay", "bust", "net", "tr", "wr"):
    print(f"  {k}: {r[k]:.4f} vs {ref[k]:.4f}")
print("  RSI21-Modul:", r["mods"].get("r21"), "vs", ref["mods"].get("r21"))
