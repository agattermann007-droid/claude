"""Pruefung: Voreinstellungen des EA RSI21_EK.mq5 = Preset RSI21_EK.set = Endstand des Replikats (ergebnisse/ek_final.json).
1. Jede Eingabe des EA steht im Set mit genau der Voreinstellung (kein Eintrag fehlt oder ist unbekannt).
2. Die handelsrelevanten Eingaben entsprechen den Replikat-Parametern (sel fuer ek_sig.select, sim fuer ek_sim.params).
Aufruf: python t_ek_set.py [--schreiben]   (--schreiben erzeugt die Wertezeilen des Sets aus den EA-Voreinstellungen neu,
der Kommentarkopf bleibt)."""
import re, sys, os, json

HERE = os.path.dirname(os.path.abspath(__file__))
MQ = os.path.join(HERE, "RSI21_EK.mq5")
SET = os.path.join(HERE, "RSI21_EK.set")
FIN = os.path.join(HERE, "ergebnisse", "ek_final.json")

mq = open(MQ, encoding="utf-8").read()
inp = {}
for m in re.finditer(r'^input\s+(?!group)(\w+)\s+(\w+)\s*=\s*("[^"]*"|[^;]+);', mq, re.M):
    typ, name, val = m.group(1), m.group(2), m.group(3).strip()
    if typ == "string":
        val = val[1:-1]
    inp[name] = (typ, val)


def same(typ, a, b):
    if typ == "double":
        return abs(float(a) - float(b)) < 1e-12
    if typ in ("int", "long"):
        return int(float(a)) == int(float(b))
    if typ == "bool":
        return str(a).lower() == str(b).lower()
    return str(a) == str(b)


if "--schreiben" in sys.argv:
    kopf = [l.rstrip("\n") for l in open(SET, encoding="utf-8") if l.startswith(";")] if os.path.exists(SET) else []
    with open(SET, "w", encoding="utf-8") as f:
        for l in kopf:
            f.write(l + "\n")
        for k, (typ, v) in inp.items():
            f.write(f"{k}={v}\n")
    print("Set geschrieben:", SET)

st = {}
for l in open(SET, encoding="utf-8"):
    l = l.strip()
    if not l or l.startswith(";") or "=" not in l:
        continue
    k, v = l.split("=", 1)
    st[k] = v.split("||")[0]
fehlt = [k for k in inp if k not in st]
fremd = [k for k in st if k not in inp]
abw = [(k, inp[k][1], st[k]) for k in inp if k in st and not same(inp[k][0], inp[k][1], st[k])]
ok1 = not fehlt and not fremd and not abw
print(f"1. Set: {len(inp)} Eingaben im EA, {len(st)} im Set | fehlen {fehlt} | unbekannt {fremd} | abweichend {abw} -> "
      f"{'OK' if ok1 else 'FEHLER'}")

# 2. EA-Voreinstellungen gegen den Endstand des Replikats
fin = json.load(open(FIN))
sel, sim = fin["sel"], fin["sim"]
sys.path.insert(0, HERE)
import ek_sim                                                       # noqa: E402
P = dict(zip(ek_sim.PN, ek_sim.params(**{k: v for k, v in sim.items() if not k.startswith("_")})))
S = dict(oben=75.0, unten=None, cross=55.0, ab=9.5, nas_bis=13.0, gold_bis=17.0, gold_ohne_h1=True, use_div=True,
         stop_atr=2.0, folge_min=240, tf_gold=(0, 1, 2), tf_nas=(0, 1, 2), longs=True, shorts=True, short_regime=True,
         nas_long_regime=True, gold_gate=True, cross_on=True)
S.update(sel)
unten = S["unten"] if S["unten"] is not None else 100.0 - S["oben"]
tg = set(S["tf_gold"]) - ({2} if S["gold_ohne_h1"] else set())
tn = set(S["tf_nas"])
soll = {
    "RiskPct": P["risk"], "RisikoVomSaldo": P["size_mode"] == 2, "GewichtM15": P["w0"], "GewichtM30": P["w1"],
    "GewichtH1": P["w2"], "GoldFaktor": P["goldmult"], "MarginMaxPct": 100.0 * P["margin_cap"], "MaxLotsJePos": P["maxlots"],
    "MinLotToleranz": P["minlottol"], "Oben": S["oben"], "Unten": unten, "Longs": S["longs"], "Shorts": S["shorts"],
    "KreuzAn": S["cross_on"], "KreuzSchwelle": S["cross"], "AbNY": S["ab"], "NasBisNY": S["nas_bis"], "GoldBisNY": S["gold_bis"],
    "NasM15": 0 in tn, "NasM30": 1 in tn, "NasH1": 2 in tn, "GoldM15": 0 in tg, "GoldM30": 1 in tg, "GoldH1": 2 in tg,
    "ShortRegime": S["short_regime"], "NasLongRegime": S["nas_long_regime"], "GoldTor": S["gold_gate"], "DivH4": S["use_div"],
    "FolgeMin": S["folge_min"], "ErstesSignalFaktor": P["first_mult"], "StopATR": S["stop_atr"] * P["stopmult"],
    "ZielNasR": P["rr_nas"], "ZielGoldR": P["rr_gold"], "EinstandAbR": P["be_at"], "EinstandPlusR": P["be_plus"],
    "NachzugAbR": P["trail_from"], "NachzugAbstandR": P["trail_dist"], "TeilAbR": P["tp1r"], "TeilAnteil": P["tp1f"],
    "ZeitExitM5": P["exitbars"], "ZeitExitTage": P["exitdays"], "Plaetze": P["nslots"] if P["second"] > 0.5 else 1,
    "MaxVerlusteTag": P["maxloss"], "WeSchlussNY": P["we_close"], "RsiLen": fin.get("fkw", {}).get("rsi_len", 21),
}
abw2 = []
for k, v in soll.items():
    typ, ea = inp[k]
    if isinstance(v, bool):
        v = "true" if v else "false"
    if not same(typ, ea, v):
        abw2.append((k, ea, v))
if not S["cross_on"]:
    abw2 = [a for a in abw2 if a[0] != "KreuzSchwelle"]
ok2 = not abw2
print(f"2. EA-Voreinstellungen gegen Replikat-Endstand ({len(soll)} Groessen): {'OK' if ok2 else 'ABWEICHUNG ' + str(abw2)}")
sys.exit(0 if ok1 and ok2 else 1)
