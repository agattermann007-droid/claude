"""Baut research/patch_sidecar_lesen.mq5 (+ .diff) aus DEADBAND_V8.mq5 (Build 8.10). PLAN.md 9.2.

Der Patch liest die Zustandsdatei des Sidecars im Durchlauf (OnTick/OnTimer, hoechstens alle 10 s):
  - SidecarLesen = false (Standard): kein Dateizugriff, handelsidentisch zu V8.10.
  - Datei fehlt, kaputt oder aelter als SidecarMaxAlterS -> fail-open: EA handelt wie V8.10, EINE Journalzeile und
    EIN Push je Ausfall (5 min Schonfrist nach dem EA-Start, weil der Sidecar 90 s nach dem Anmelden startet).
  - Neue Alarmnummer des Sidecars -> Push (SidecarPush), damit Alarme auch ohne ntfy-App ankommen.
  - SidecarSperre = false (Standard): Nachrichtenfenster des Sidecars zusaetzlich als News-Fenster (wirkt wie die
    eingebaute News-Sperre: keine Einstiege, keine eigenen Gewinnschliessungen > 1 %). Nur bei gueltigem Zustand.
Aufruf: python werkzeuge/patch_sidecar_bauen.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patch_bauen as PB  # noqa: E402

RESEARCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KOPF = """//+------------------------------------------------------------------+
//| PATCH sidecar_lesen (research/patch_sidecar_lesen.mq5)            |
//| = DEADBAND_V8.mq5 Build 8.10 + Lesen der Sidecar-Zustandsdatei.   |
//| Standard: SidecarLesen=false -> handelsidentisch zu V8.10.        |
//| Fail-open: fehlt der Sidecar, handelt der EA unveraendert weiter. |
//| Aenderungen: siehe patch_sidecar_lesen.diff                       |
//+------------------------------------------------------------------+
"""

INPUTS = """input group             "=== Sidecar-Patch (research/sidecar) ==="
input bool   SidecarLesen     = false;  // Sidecar: Zustandsdatei MQL5\\Files\\deadband_sidecar.txt lesen (aus = handelsidentisch zu 8.10)
input int    SidecarMaxAlterS = 180;    // Sidecar: fehlt/kaputt/aelter als X s -> fail-open (EA handelt wie ohne Sidecar), 1 Journalzeile + 1 Push je Ausfall
input bool   SidecarPush      = true;   // Sidecar: neue Alarme des Sidecars als Push weitergeben (nur mit SidecarLesen)
input bool   SidecarSperre    = false;  // Sidecar: Nachrichtenfenster des Sidecars zusaetzlich als News-Fenster werten (nur mit SidecarLesen)
"""

FUNKTIONEN = """// ---- Sidecar-Patch: Zustand des Python-Sidecars (research/sidecar). Ohne SidecarLesen wird nichts gelesen.
bool     scOk = false;                  // letzte Lesung gueltig und frisch
bool     scAusfall = false;             // Ausfall gemeldet (Journal + 1 Push), bis die Datei wieder gueltig ist
uint     scLeseMs = 0;
datetime scStart = 0;
long     scAlarmNr = -1;                // -1 = noch nie gelesen (alte Alarme nach dem Start nicht wiederholen)
datetime scVon[];
datetime scBis[];
int      nScFenster = 0;
string   scGrund = "nie gelesen";

string ScWert(const string &k[], const string &v[], const int n, const string key)
  {
   for(int i=0;i<n;i++) if(k[i] == key) return v[i];
   return "";
  }

void SidecarPruefen()
  {
   if(!SidecarLesen || MQLInfoInteger(MQL_TESTER)) return;
   if(scStart == 0) scStart = TimeLocal();
   uint ms = GetTickCount();
   if(scLeseMs != 0 && ms - scLeseMs < 10000) return;
   scLeseMs = ms; if(scLeseMs == 0) scLeseMs = 1;
   string k[], v[];
   int n = 0;
   string grund = "";
   int h = FileOpen("deadband_sidecar.txt", FILE_READ|FILE_TXT|FILE_ANSI|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(h == INVALID_HANDLE) grund = "Datei fehlt";
   else
     {
      while(!FileIsEnding(h) && n < 300)
        {
         string z = FileReadString(h);
         int p = StringFind(z, "=");
         if(p <= 0) continue;
         ArrayResize(k, n+1); ArrayResize(v, n+1);
         k[n] = StringSubstr(z, 0, p); v[n] = StringSubstr(z, p+1);
         StringTrimLeft(v[n]); StringTrimRight(v[n]);
         n++;
        }
      FileClose(h);
      if(ScWert(k, v, n, "ende") != "1") grund = "Datei unvollstaendig";
      else if(ScWert(k, v, n, "version") != "1") grund = "falsche Version";
      else
        {
         long zu = StringToInteger(ScWert(k, v, n, "zeit_utc"));
         long alter = (long)TimeGMT() - zu;
         if(zu <= 0) grund = "ohne Zeitstempel";
         else if(alter > SidecarMaxAlterS || alter < -60) grund = StringFormat("Datenalter %I64d s", alter);
        }
     }
   if(grund != "")
     {
      scOk = false; nScFenster = 0; scGrund = grund;
      if(!scAusfall && TimeLocal() - scStart >= 300)                    // 5 min Schonfrist nach dem EA-Start
        {
         scAusfall = true;
         PrintFormat("DEADBAND4: SIDECAR AUSGEFALLEN (%s) - EA handelt unveraendert weiter (fail-open)", grund);
         if(UsePush && !SendNotification("DEADBAND4: Sidecar ausgefallen (" + grund + ") - EA handelt unveraendert weiter"))
            PrintFormat("DEADBAND4: Sidecar-Push nicht gesendet, Fehler %d", GetLastError());
        }
      return;
     }
   if(scAusfall) { scAusfall = false; Print("DEADBAND4: Sidecar wieder da - Zustand gueltig"); }
   scOk = true; scGrund = "ok";
   long nr = StringToInteger(ScWert(k, v, n, "alarm_nr"));
   string txt = ScWert(k, v, n, "alarm_text");
   if(scAlarmNr >= 0 && nr != scAlarmNr && StringLen(txt) > 0)
     {
      PrintFormat("DEADBAND4: Sidecar-Alarm %I64d: %s", nr, txt);
      if(SidecarPush && UsePush && !SendNotification("DEADBAND Sidecar: " + txt))
         PrintFormat("DEADBAND4: Sidecar-Push nicht gesendet, Fehler %d", GetLastError());
     }
   scAlarmNr = nr;
   nScFenster = 0;
   for(int i=0;i<n;i++)
     {
      if(StringFind(k[i], "fenster_von_") != 0) continue;
      string sym = StringSubstr(k[i], 12);
      datetime a = StringToTime(v[i]);
      datetime b = StringToTime(ScWert(k, v, n, "fenster_bis_" + sym));
      if(a <= 0 || b <= 0) continue;
      ArrayResize(scVon, nScFenster+1); ArrayResize(scBis, nScFenster+1);
      scVon[nScFenster] = a; scBis[nScFenster] = b; nScFenster++;
     }
  }

bool SidecarNewsFenster(const datetime t)
  {
   if(!SidecarLesen || !SidecarSperre || !scOk || MQLInfoInteger(MQL_TESTER)) return false;
   for(int i=0;i<nScFenster;i++) if(t >= scVon[i] && t <= scBis[i]) return true;
   return false;
  }

"""

NEWS_ALT = """bool NewsFenster(const datetime t)
  {
   if(NewsSperreMin <= 0 || MQLInfoInteger(MQL_TESTER)) return false;"""
NEWS_NEU = """bool NewsFenster(const datetime t)
  {
   if(SidecarNewsFenster(t)) return true;                                // Sidecar-Patch (SidecarSperre, Standard aus)
   if(NewsSperreMin <= 0 || MQLInfoInteger(MQL_TESTER)) return false;"""

DURCHLAUF = """   Lebenszeichen();                                                        // Final: stuendlicher Push-Check
"""
INIT_ANKER = """   PrintFormat("DEADBAND4: 4.90 GFT-Schutz: Hedging-Sperre %s"""
INIT_ZEILE = """   if(SidecarLesen) PrintFormat("DEADBAND4: Sidecar-Patch: lese MQL5\\\\Files\\\\deadband_sidecar.txt, fail-open ab %d s, Push %s, Nachrichtenfenster %s",
                                SidecarMaxAlterS, (SidecarPush ? "an" : "aus"), (SidecarSperre ? "an" : "aus"));
"""

EINGRIFFE = [
    ("input double KaufPuffer    = 2.0;\n", "nach", INPUTS),
    ("// Wirtschaftskalender: rote USD-Termine der naechsten 36 h", "vor", FUNKTIONEN),
    (NEWS_ALT, "ersetze", NEWS_NEU),
    (DURCHLAUF, "nach", "   SidecarPruefen();                                                       // Sidecar-Patch: Zustandsdatei (Standard aus)\n"),
    (INIT_ANKER, "vor", INIT_ZEILE),
]

if __name__ == "__main__":
    aus = os.path.join(RESEARCH, "patch_sidecar_lesen.mq5")
    PB.bauen(EINGRIFFE, aus, os.path.join(RESEARCH, "patch_sidecar_lesen.diff"), KOPF)
    print("geschrieben:", aus)
