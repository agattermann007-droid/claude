//+------------------------------------------------------------------+
//|  DEADBAND LIVE 4  -  Build 6.50 NETTO, 25.09.2026                |
//|  BUILD 6.50: MEHR NETTO, NICHT WENIGER AUSZAHLUNGEN, NICHT MEHR  |
//|  BUST-RISIKO. Handelslogik = 6.40, dazu (Replikat eng9, x48/x49):|
//|  1) Schutz gueltiger Tage je Modul: Noise und Fades wie 6.40,    |
//|     RSI21 nur fuer Einstiege vor 13:00 NY sowie ganztags, solange|
//|     der Portfolio-Waechter die Fades NICHT live handeln laesst   |
//|     (GueltigSchutzR21BisNY, GueltigSchutzR21Regime). Spaetere    |
//|     RSI21-Trades schliessen meist erst an einem Folgetag - sie   |
//|     gefaehrden den gueltigen Tag kaum und tragen Gewinn in die   |
//|     naechsten Tage. Im alten Regime bleibt RSI21 geschuetzt.     |
//|  2) Die NAS-Nachmittags-Fades N1330 und N1300 (Einstieg ab 14:30 |
//|     NY, Trefferquote ~80 %) handeln auch an einem schon gueltigen|
//|     Tag (GueltigSchutzFrei).                                     |
//|  3) Fade-Risiko 0,70 statt 0,75 % (FadeRiskPct): mehr Luft zur   |
//|     Floating-Bremse bei -0,8 %.                                  |
//|  Replikat GFT-Ersatz 2022-25 (16 Stoerungen), GFT-nahe / breite  |
//|  Spreads: Netto 2510 / 2319 $ je Jahr statt 2232 / 2051 $        |
//|  (+12,5 / +13,1 %), Auszahlungen 12,12 / 11,66 statt 12,06 /     |
//|  11,25, Busts 0, kleinster Abstand zum Boden 261 / 262 $ statt   |
//|  248 / 255 $. Fremddaten 2006-21: 2,14 Auszahlungen (6.40 2,16), |
//|  0,034 Busts je Jahr (6.40 0,035). Bericht                       |
//|  DEADBAND_LIVE4_650_Bericht.md. Zurueck: rollback_6.40/.         |
//|                                                                  |
//|  Build 6.40 TAKT, 25.09.2026                                     |
//|  BUILD 6.40: AUSZAHLUNG ALLE ~30 TAGE, NICHT MEHR BUST-RISIKO    |
//|  Handelslogik = 6.30, dazu (Replikat eng8, x44/x46):             |
//|  1) Auszahlung ab dem GFT-Minimum (MinProfitPct 0: 131,25 $      |
//|     Gewinn statt 300 $). Engpass sind dann die gueltigen Tage.   |
//|  2) Abschluss-Ernte immer (AbschlussLetzte 5): offener Gewinn    |
//|     macht den Tag gueltig, sobald er reicht.                     |
//|  3) Schutz gueltiger Tage (GueltigSchutz): ist heute gueltig und |
//|     fehlen dem Zyklus noch gueltige Tage, keine neuen Einstiege  |
//|     bis 17:00 NY (ein Verlust kippte den Tag sonst zurueck).     |
//|  4) Regime-Waechter der Fades ueber das PORTFOLIO: PF der        |
//|     letzten 200 virtuellen Signale aller Fade-Module > 1,15      |
//|     (FadeWaechterModus 1) statt PF30 je Modul. Schaltet im alten |
//|     Regime (2006-21) besser ab, laesst im heutigen ~30 % mehr    |
//|     Signale durch.                                               |
//|  5) Pufferkurve: volle Groesse nur bis 1 % Rueckgang (DDFullPct  |
//|     5), dann kleiner bis x0,2 bei 3,5 % Rueckgang (DDMinPct 2,5, |
//|     DDMinFactor 0,2; bis 6.30: ab 2 % Rueckgang, x0,6 bei 4,5 %).|
//|     Der Waechter handelt mehr, die Kurve haelt die Konten so     |
//|     weit vom Boden wie 6.30 (Episode Maerz 2025).                |
//|  6) Fades ohne Teilgewinn (FadeT1R 0: kleine Gewinne machten     |
//|     Tage ungueltig), Noise 0,45 % je Signal.                     |
//|  Replikat GFT-Ersatz 2022-25, GFT-nahe Spreads: Auszahlung alle  |
//|  30,3 statt 44,1 Tage (breite Spreads: 32,5 statt 49,9), Busts 0 |
//|  wie 6.30, kleinster Abstand zum Boden mindestens wie 6.30;      |
//|  Fremddaten 2006-21: 0,035 statt 0,347 Busts je Jahr. Zahlen im  |
//|  Bericht DEADBAND_LIVE4_640_Bericht.md. Zurueck: rollback_6.30/. |
//|                                                                  |
//|  Build 6.30 TREFFER, 25.09.2026                                  |
//|  BUILD 6.30: HOEHERE TREFFERQUOTE (TEILGEWINN / EINSTAND)        |
//|  Handelslogik = 6.20, dazu (Replikat eng7, x42/x43):             |
//|  1) Fades: ab FadeT1R = 0,6 R wird FadeT1Anteil = 50 % der       |
//|     Position geschlossen (Stop und Ziel bleiben).                |
//|  2) RSI21 und jeder Noise-Teil: Stop auf Einstand + 0,05 R,      |
//|     sobald der Kurs 1 R im Plus war (R21/NzEinstandAbR).         |
//|     RSI21 nicht nach einer Wochenend-Wiederaufnahme.             |
//|  3) Alles erst ab der M5-Kerze nach der Einstiegskerze und       |
//|     nach MinHalteSek; Teilgewinn nach der Gewinn-/News-Regel.    |
//|     Zustand aus Stop und Deal-Historie (auch nach Neustart).     |
//|  Replikat GFT-Ersatz 2022-25: Trefferquote 65,0 statt 63,1 %,    |
//|  Auszahlungen gleich, Busts 0, Serien >= 6 ein Drittel seltener; |
//|  Zahlen im Bericht DEADBAND_LIVE4_630_Bericht.md.                |
//|  Zurueck auf 6.20: FadeT1R=0, R21EinstandAbR=0, NzEinstandAbR=0  |
//|  oder rollback_6.20/.                                            |
//|                                                                  |
//|  Build 6.20 GRID, 24.09.2026                                     |
//|  BUILD 6.20: PROBABILITY GRID ALS FADE-FILTER                    |
//|  Handelslogik = 6.10, dazu (Konzept: LuxAlgo "Probability Grid", |
//|  CC BY-NC-SA 4.0, eigene Umsetzung):                             |
//|  1) Schwung-Statistik je Symbol auf M5 (GridTF): Laufrichtung    |
//|     wie LuxAlgo aus Kerzenkoerpern (Swing Length 15), jeder      |
//|     Schenkel Pivot -> Pivot mit Groesse und Dauer, je Richtung   |
//|     die letzten 1000 Schenkel.                                   |
//|  2) Fade GEGEN den laufenden Schwung: Grid-Chance, dass der Lauf |
//|     bis zum Stop weiterlaeuft = Anteil der Schenkel ueber der    |
//|     Groesse bis zum Stop / Anteil ueber der bisherigen Groesse.  |
//|     Ab 70 % (GridMaxStopChance) kein Signal - auch nicht         |
//|     virtuell, der Regime-Waechter sieht den gefilterten Strom.   |
//|     Wirkt vor allem bei engen Stops (X0300S, X0400, N1030);      |
//|     Fades in Laufrichtung bleiben wie 6.10. N1800 ohne Grid      |
//|     (GridOhne): mit Grid blieben ihm < 30 Signale in 600 Tagen,  |
//|     der Waechter liesse es nie live handeln.                     |
//|  3) RSI21 und Noise unveraendert (Grid dort ohne stabilen Effekt)|
//|  Replikat: Kurse 2022-2025 aus Fremddaten (GFT-Exporte fehlten), |
//|  Vorstudie aller Fade-Signale 2006-2025, Konto mit allen GFT-    |
//|  Regeln; Zahlen im Bericht DEADBAND_LIVE4_620_Bericht.md.        |
//|  Zurueck auf 6.10: rollback_6.10/ oder GridAktiv=false.          |
//|                                                                  |
//|  Build 6.10 FADE, 24.09.2026                                     |
//|  BUILD 6.10: ECHTBETRIEB - ERNTE ALLER MODULE, KONTOERKENNUNG    |
//|  Handelslogik = 6.00, dazu:                                      |
//|  1) Abschluss-Ernte fuer ALLE Module (AbschlussModule 15):       |
//|     fehlen nur noch <= 3 gueltige Tage, wird offener Gewinn      |
//|     (Vorlauf >= 0,3 R) so weit realisiert, dass der Tag gueltig  |
//|     wird. Bis 6.00 nur DEADBAND - bei DbAktiv=false wirkungslos. |
//|  2) Fade-Ziel erst ab der Kerze nach der Einstiegskerze (wie im  |
//|     getesteten Replikat), Kommission Hin- und Rueckweg.          |
//|  3) Kontoerkennung (Audit): Start erst, wenn die Deal-Historie   |
//|     den Saldo erklaert; Auszahlung nur, wenn der Saldo danach    |
//|     auf den Startsaldo faellt (Korrekturen/Abzuege sind keine,   |
//|     mehrteilige Buchungen binnen 1 h zaehlen zusammen,           |
//|     Teilauszahlung ueber AuszahlungZeiten); gueltige Tage in 2   |
//|     Lesarten + 0,50 $ Reserve; Tagesreferenz 17:00 NY als obere  |
//|     Schranke aus synchronen Kursen (sonst keine Einstiege, neuer |
//|     Versuch je Minute); Equity-Spitze aus M5 laufend nachgeholt  |
//|     (auch nach Verbindungsluecken); Kontowechsel erkannt;        |
//|     10-Tage-Frist volle 10 x 24 h; kein Einstieg, dessen Stop die|
//|     Equity unter den Boden braechte, wenn auch alle offenen      |
//|     Positionen an ihrem Stop schliessen; kein Einstieg, dessen   |
//|     Kommission einen heute gueltigen Tag ungueltig machte;       |
//|     NY-Versatz fest 7 h; Kontozustand ins Journal und nach       |
//|     MQL5/Files/DEADBAND4_Konto_<Login>.txt.                      |
//|  Replikat GFT-Daten 2022-26 (16 Stoerungen), Ausz / Busts /      |
//|  Netto je Jahr, Serien >= 6 je Jahr, laengste Serie Mittel/max:  |
//|    6.00 Ertrag:        7,20 / 0,00 / 2158 / 0,49 / 6,4/10        |
//|    6.10 Ertrag (Set):  7,51 / 0,00 / 2143 / 0,36 / 5,9/10        |
//|    6.10 Sicher:        5,86 / 0,00 / 1603 / 0,07 / 5,0/10        |
//|  Startjahr 2022: Ertrag 10,1 Auszahlungen. Fremddaten 2006-21:   |
//|  Ertrag 2,02/0,40/503, Sicher 0,56/0,33/104.                     |
//|  Bericht DEADBAND_LIVE4_610_Bericht.md. Zurueck: rollback_6.00/. |
//|                                                                  |
//|  Build 6.00 FADE, 24.09.2026                                     |
//|  BUILD 6.00: FEHLAUSBRUCH-FADES MIT REGIME-WAECHTER              |
//|  Ziel: Auszahlungen >= 3 % (300 $ auf 10k), mehr Ertrag, keine   |
//|  zusaetzlichen Busts, kurze Verlustserien.                       |
//|  1) NEU: bis zu 10 Fade-Module (FadeListe). Je Modul eine        |
//|     Sitzungs-Range; handelt eine M5-Kerze darueber/darunter und  |
//|     schliesst wieder innen -> Gegenrichtung zur Range-Mitte oder |
//|     Gegenseite, Stop hinter dem Extrem + Puffer, Zeit-Ausstieg,  |
//|     max. 1 Signal je Tag, 0,75 % Risiko x Pufferkurve.           |
//|     Voreinstellung: 6 NAS- und 4 Gold-Fades (Trefferquote im     |
//|     Replikat 57-78 %).                                           |
//|  2) Regime-Waechter je Modul: jedes Signal wird virtuell mit-    |
//|     gerechnet; live nur, wenn der Profitfaktor der letzten 30    |
//|     virtuellen Signale > 1,2 ist. Die Historie wird beim Start   |
//|     aus den M5-Kursen rekonstruiert (Max. Balken im Chart:       |
//|     Unbegrenzt). Die Fades verdienen 2022-26, vor 2022 NICHT -   |
//|     der Waechter begrenzt dann die Verluste.                     |
//|  3) DEADBAND-Einstiege aus (DbAktiv=false): ~300 Trades/J mit    |
//|     43 % Treffern erzeugen die langen Verlustserien, 2006-21     |
//|     im Replikat negativ. Verwaltung offener Positionen bleibt.   |
//|  4) Auszahlung erst ab 3 % Gewinn (MinProfitPct 3.0).            |
//|  5) Gesamtbudget und Risiko je Idee 0,9 % (Floating-Regel -1 %), |
//|     RSI21 0,50 %, Noise 0,35 %, Serien-Stopp nach 3 Verlusten.   |
//|  6) Schutz (Code-Review): eben eroeffnete Positionen aller Module|
//|     zaehlen im Fade-Budget, Fade-Stop >= 6 Spreads, keine Fades  |
//|     an US-Feiertagen/verkuerzten Tagen, Fade-Zeiten fest NY+7 h. |
//|  Replikat GFT-Daten 2022-26 (16 Stoerungen, rollierend 1/2/3 J), |
//|  alle mit Auszahlung ab 3 %; Ausz / Busts / Netto je Jahr,       |
//|  Serien >= 6 je Jahr, laengste Serie Mittel/max:                 |
//|    5.10 (Ausz >= 3 %): 5,51 / 0,17  / 1517 / 6,15 / 9,4/13       |
//|    6.00 Sicher:        5,89 / 0,00  / 1601 / 0,06 / 4,9/10       |
//|    6.00 Ertrag (Set):  7,20 / 0,00  / 2158 / 0,49 / 6,4/10       |
//|  Fremddaten 2006-21 (anderes Regime): 5.10 3,18/1,30/765,        |
//|  Sicher 0,56/0,33/104, Ertrag 2,00/0,43/524.                     |
//|  10 Auszahlungen/J, 0 Busts und nie > 5 Verluste in Folge        |
//|  zugleich erreicht KEINE gepruefte Variante robust.              |
//|  Presets: DEADBAND_LIVE4_Echtbetrieb.set (= Ertrag),             |
//|  DEADBAND_LIVE4_600_Sicher.set. Zurueck: rollback_5.10/.         |
//|  Bericht DEADBAND_LIVE4_600_Bericht.md.                          |
//|                                                                  |
//|  Build 5.10 KOMBI, 24.09.2026                                    |
//|  BUILD 5.10: AUSZAHLUNGSTAKT, WENIGER BUSTS, KUERZERE SERIEN     |
//|  Signale aller drei Module = 5.00. Ziel: mehr und regelmaessi-   |
//|  gere kleine Auszahlungen, weit weniger Busts, kuerzere Ver-     |
//|  lustserien; Netto ist zweitrangig.                              |
//|  A) GFT-REGELSCHUTZ (strenge Lesart, Help-Center 24.09.2026)     |
//|  1) Floating-Bremse und Notbremse auf die SUMME DER VERLUST-     |
//|     POSITIONEN inkl. Swap und Kommission (FloatNurVerlierer).    |
//|     Zaehlt GFT die -1-%-Regel nur ueber Verlierer, haette 5.00   |
//|     im Replikat 3,6 statt 1,1 Busts/J (Gewinner verdecken        |
//|     Verlierer, Gesamtbudget 2 %).                                |
//|  2) Swap-Vorsorge vor dem Rollover (SwapVorsorgePct 0,8): Ver-   |
//|     lierer plus erwarteter Swap (dreifach am Swap-3-Tag) unter   |
//|     der Bremse -> groesste Verlierer vorher schliessen. Der Swap |
//|     wird um 17:00 NY gebucht, wenn keine Bremse mehr greift.     |
//|  3) Risiko je Handelsidee (Symbol + Richtung, alle Module)       |
//|     hoechstens 1,25 % (IdeeMaxRisikoPct; GFT kann 1 % fordern).  |
//|  4) Tagesregel-Notbremse auf min(Startsaldo, Tagesreferenz).     |
//|  5) Teilverkauf erst nach 130 s Haltedauer (2-Minuten-Regel).    |
//|  6) NurAufPcPfad: Start nur auf dem eigenen PC (VPS verboten).   |
//|  B) AUSZAHLUNGSTAKT UND SERIENSCHUTZ                             |
//|  7) DEADBAND: 50 % bei 1,5 R realisieren, Stop auf +0,05 R       |
//|     (Tp1R 1,5 / Tp1F 0,5 / BeAfterT1R 0,05; 5.00: 2,0/0/0,3).    |
//|     Laeufer geben weniger Buchgewinn zurueck -> der trailende    |
//|     Boden (Equity-Hoch inkl. Buchgewinn) zieht weniger nach.     |
//|  8) Abschluss-Ernte: fehlen nur noch <= 2 gueltige Tage, wird    |
//|     DEADBAND-Gewinn (bester Kurs >= 0,5 R) jederzeit so weit     |
//|     realisiert, dass der Tag gueltig wird (AbschlussLetzte).     |
//|  9) Gewinn-Ernte ohne Rueckgang-Bedingung (GeRueckgangR 0).      |
//| 10) Serien-Stopp: nach 4 Verlusttrades in Folge keine neuen      |
//|     Einstiege bis 17:00 NY (Noise-Teile eines Signals = 1 Trade).|
//| 11) RSI21 0,63 % (5.00: 0,70), Noise 0,45 % (5.00: 0,30).        |
//|  Replikat (GFT-Daten 2022-26, 16 Stoerungen, rollierend 1/2/3 J, |
//|  strenge Regel-Lesart); Ausz / Busts / Netto je Jahr:            |
//|    5.00 wie ist: 7,06 / 1,05 / 1911 (Verlierer-Lesart: 3,59 B.)  |
//|    5.10:         7,96 / 0,05 / 1571                              |
//|  Serien >= 5 / >= 8 Verluste je Jahr 15,6 / 3,3 -> 11,1 / 1,6,   |
//|  laengste Serie 11,5 -> 9,5 Trades, Bust im ersten Jahr 70 % ->  |
//|  4 % der Konten. Jedes Startjahr 2022-2025: mehr Auszahlungen,   |
//|  weniger Busts (Netto je Jahr -18 %, Auszahlung 378 -> 256 $).   |
//|  Pfad ab 03.01.2022: 34,8 Ausz / 3,8 Busts -> 37,3 / 0,1.        |
//|  Zurueck auf 5.00: rollback_5.00/ (mq5 + set).                   |
//|  Bericht DEADBAND_LIVE4_510_Bericht.md.                          |
//|                                                                  |
//|  Build 5.00 KOMBI, 24.09.2026                                    |
//|  BUILD 5.00: DRITTES MODUL NAS-NOISE (aus NAS100 Flip v4)        |
//|   DEADBAND-Ausbruch und RSI21 = 4.90 (Signale, Stops, Ziele,     |
//|   Groessen, Bremsen, GFT-Schutz unveraendert). Neu im selben     |
//|   Konto: Noise-Area-Momentum auf NAS100 (Zarattini/Aziz/Barbon   |
//|   2024), nur Long, nur intraday. Pruefung 10:00-15:00 NY zur     |
//|   vollen Stunde: Long, wenn der Schluss ueber UB = max(Eroeff-   |
//|   nung 9:30, Vortagesschluss) x (1 + uebliche Bewegung) liegt.   |
//|   Ausstieg an der naechsten Pruefung unter UB, spaetestens       |
//|   15:55 NY. Drei Teilpositionen (Stops 0,35/0,5/0,75 Tages-      |
//|   Sigma x Wurzel der Restzeit), Risiko 0,30 % je Signal x Vola-  |
//|   Gewicht, Puffer-Kurve wie DEADBAND/RSI21, im Gesamtbudget      |
//|   2,0 %. Hedging-, News- und 130-s-Regel, bei Auszahlungsreife   |
//|   schliessen, US-Feiertage/verkuerzte Tage handelsfrei.          |
//|   Replikat (GFT-Regeln, 8 Stoerungen, rollierend 1/2/3 J);       |
//|   Ausz / Busts / Netto je Jahr, 4.90 -> 5.00:                    |
//|     alte Daten 22-26: 8,39/1,59/2183 -> 8,94/1,25/2586           |
//|     alte Daten 16-21: 5,88/1,53/1718 -> 6,12/1,47/1859           |
//|     GFT-Daten  22-26: 7,04/1,39/1915 -> 8,22/1,22/2352           |
//|   Pfad ab 03.01.2022 (GFT-Daten): 37/5/9522 -> 42/4/11606 $.     |
//|   Grenze: Startjahr 2025 ohne Vorteil (GFT-Daten -164 $/J).      |
//|   Zurueck auf 4.90: NzAktiv=false oder DEADBAND_LIVE4_490.*.     |
//|   Bericht DEADBAND_LIVE4_500_Bericht.md.                         |
//|                                                                  |
//|  Build 4.90, 22.09.2026                                          |
//|  BUILD 4.90: GFT-REGELN UND BETRIEBSSICHERHEIT                   |
//|   Signale, Stops, Ziele, Groessen und Bremsen-Schwellen = 4.80.  |
//|   GFT-Regeln (Help-Center, geprueft 21./22.09.2026):             |
//|   1) Hedging-Sperre: kein Einstieg und keine Wiederaufnahme      |
//|      gegen eine offene Position im selben Symbol (GFT: zwei      |
//|      Gegenpositionen = Konto weg). 4.80 konnte DEADBAND-NAS      |
//|      short und RSI21-NAS long gleichzeitig halten (~0,4x/J).     |
//|   2) News: +-6 min um rote USD-Termine keine Einstiege und       |
//|      keine eigenen Gewinnschliessungen ueber 1 % (Kalender).     |
//|   3) Eigene Gewinnschliessungen erst nach 130 s Haltedauer,      |
//|      keine Einstiege in den 5 min vor der Freitags-Schliessung.  |
//|   4) Margin je Idee (Symbol+Richtung) <= 70 % der Equity.        |
//|   5) Start auf VPS verweigert, Push bei 20 Tagen ohne Trade.     |
//|   6) Sondertage (Feiertage, frueher Schluss) wie Freitag.        |
//|   Betriebssicherheit (Audit, 28 bestaetigte Fundstellen):        |
//|   Start vor Verbindung/Historie, Equity-Spitze gesichert und     |
//|   nachgeholt, Positionen nachtraeglich uebernommen, Notbremse    |
//|   wiederholt alle 0,5 s, innere Bremsen gedrosselt, Waechter     |
//|   fuer Algo-Knopf/Verbindung, Auszahlung beim Tageswechsel       |
//|   erkannt, Saldo-Buchungen unterschieden, Tagesreferenz          |
//|   max(Saldo, Equity), Magic beim Schliessen, Tageszaehler und    |
//|   Vormerkungen ueberleben Neustarts, NY-Versatz nur mit          |
//|   Verbindung, RSI21-Plaetze auch bei ausgeschaltetem Modul       |
//|   verwaltet. Mindestauszahlung 105 $ (3 % Gebuehr).              |
//|   Bericht DEADBAND_LIVE4_490_Bericht.md.                         |
//|                                                                  |
//|  Build 4.80, 18.09.2026                                          |
//|  BUILD 4.80: RISIKO VON DEADBAND ZU RSI21 VERSCHOBEN             |
//|   Handelslogik, Bremsen und Kontoregeln = 4.70. Geaendert sind   |
//|   nur zwei Voreinstellungen:                                     |
//|   1) RiskMult 1,0 -> 0,9 (DEADBAND-Positionen 10 % kleiner)      |
//|   2) R21RiskPct 0,60 -> 0,70 (RSI21-Positionen 17 % groesser)    |
//|   Grund (Runde 4.80, drei Datensaetze, rollierend, 8 Stoerungen):|
//|   DEADBAND ist beim Einstieg ein Zufallslauf und lebt nur von    |
//|   seinen Laeufern; RSI21 hat echten Richtungsvorteil. Auf den    |
//|   Kursdaten des GFT-Terminals verdient DEADBAND nur halb so viel.|
//|   Ausz / Busts / Netto je Jahr, 4.70 -> 4.80:                    |
//|     alte Daten 22-26: 8,08/1,67/2271 -> 8,57/1,57/2292           |
//|     alte Daten 16-21: 6,00/1,74/1770 -> 5,89/1,52/1700           |
//|     GFT-Daten  22-26: 7,25/1,98/1684 -> 7,04/1,39/1914           |
//|   Pfad ab 03.01.2022 (Tester 4.70: 41/7/9760): alte Daten        |
//|   39/6/11465 -> 42/6/11014, GFT-Daten 38/8/9105 -> 37/5/9526.    |
//|   Zurueck auf 4.70: RiskMult 1.0, R21RiskPct 0.60.               |
//|   Weniger Busts (bust-arm): RiskMult 0.8, R21RiskPct 0.70.       |
//|   Bericht DEADBAND_LIVE4_480_Bericht.md, Abschnitt 12.           |
//|                                                                  |
//|  Build 4.70, 17.09.2026                                          |
//|  BUILD 4.70: MEHR ABSTAND ZUR FLOATING-REGEL (SICHERHEITS-BUILD) |
//|   Die Floating-Regel der Firma ist ein harter Regelbruch: bei    |
//|   -1,0 % Buchverlust wird das Konto geschlossen (GFT-FAQ Instant |
//|   Premium). Handelslogik unveraendert.                           |
//|   1) FloatStopPct 0,85 -> 0,80: Abstand der eigenen Bremse zur   |
//|      Firmengrenze 15 $ -> 20 $ (10k). Im Replikat ohne messbaren |
//|      Preis (Netto -16 / -6 $/J, Rauschen +-100).                 |
//|   2) FloatBasisMinSaldo: Bremse und Firmengrenze rechnen auf     |
//|      min(Startsaldo, aktueller Saldo). Die FAQ sagt "of your     |
//|      account balance"; liegt der Saldo unter dem Startsaldo, ist |
//|      die strengere Lesart damit abgedeckt. Replikat: +20 / -1 $/J.|
//|   Beides zusammen im Replikat: 2271 / 1770 $/J gegen 2261 / 1819 |
//|   (4.60), Busts 1,67 / 1,74 gegen 1,69 / 1,64 - also neutral.    |
//|   Zurueck auf 4.60: FloatStopPct 0.85, FloatBasisMinSaldo false. |
//|   Bericht DEADBAND_LIVE4_470_Bericht.md.                         |
//|                                                                  |
//|  Build 4.60, 17.09.2026                                          |
//|  BUILD 4.60: RSI21-AUSSTIEG ENGER, GESTUFTE FLOATING-BREMSE      |
//|   1) RSI21-Stop 2,0 ATR statt 3,5 ATR, Ziel in gleicher          |
//|      Entfernung (4,4 ATR NAS / 5,3 ATR Gold = 2,2 R / 2,64 R     |
//|      statt 1,25 R / 1,5 R). Gleiches Geldrisiko je Trade,        |
//|      groessere Lots. Trade-Ebene Folgesignale 2016-21 / 2022-26: |
//|      +0,55 / +0,60 R -> +0,62 / +0,70 R je Trade (Treffer        |
//|      64-67 % -> 47-50 %), in 9 von 11 Jahren besser. Der weite   |
//|      Stop wurde im Konto ohnehin meist von der Floating-Bremse   |
//|      (-0,85 %) vorweggenommen.                                   |
//|   2) RSI21-Risiko 0,7 -> 0,6 % (haelt die Busts auf 4.50-Stand). |
//|   3) Gestufte Floating-Bremse (FloatGestuft): bei -0,85 %        |
//|      Buchverlust wird nur die eigene Position mit dem groessten  |
//|      Verlust geschlossen (wiederholt, bis der Buchverlust wieder |
//|      ueber der Schwelle liegt) statt aller. Aeussere Notbremse   |
//|      an der Firmengrenze (-1,0 %) unveraendert: schliesst alles. |
//|   Replikat (Ausz/J, Busts/J, Netto/J; 8 Stoerungen, 1/2/3 J):    |
//|   2022-26 4.50 8,00 / 1,64 / 1871 -> 4.60 8,31 / 1,69 / 2261;    |
//|   2016-21 5,56 / 1,41 / 1198 -> 6,06 / 1,64 / 1819. Netto in 9   |
//|   von 10 Startjahren hoeher. Mit -0,2 R Abschlag je RSI21-Trade  |
//|   2035 / 1488 (weiter ueber 4.50 ohne Abschlag).                 |
//|   Zurueck auf 4.50: R21StopATR 3.5, R21NasRR 1.25, R21GoldRR 1.5,|
//|   R21RiskPct 0.7, FloatGestuft false.                            |
//|   Bericht DEADBAND_LIVE4_460_Bericht.md.                         |
//|                                                                  |
//|  Build 4.50, 17.09.2026                                          |
//|  BUILD 4.50: RSI21-MODUL AUSGEBAUT                                |
//|   1) Folgesignal (R21FolgeMin 240): ein RSI21-Signal wird nur     |
//|      gehandelt, wenn es auf demselben Symbol in derselben         |
//|      Richtung in den letzten 240 Minuten schon ein gueltiges      |
//|      RSI21-Signal gab (fruehere Kerze, egal welche Zeitebene).    |
//|      Das erste Signal einer Bewegung wird nur gemerkt. Trade-     |
//|      Ebene 2016-26: erstes Signal +0,35 R / 57 % Treffer,         |
//|      Folgesignale +0,55 bis +0,66 R / 65-69 %, in 9 von 11 Jahren |
//|      besser, beide Symbole, alle Zeitebenen.                      |
//|   2) Zweiter RSI21-Platz je Symbol (R21ZweiterPlatz): laeuft die  |
//|      erste RSI21-Position in dieselbe Richtung, darf ein weiteres |
//|      Folgesignal eine zweite eroeffnen (Magic MagicBase+Offset+8+ |
//|      Index). Alle Kontoregeln, Ernte, Gewinn-Ernte, Wochenend-    |
//|      Pause und Reife-Schluss gelten fuer beide Plaetze.           |
//|   3) Budgets: RSI21 0,8 -> 1,2 %, gesamt 1,2 -> 2,0 %; RSI21-      |
//|      Risiko 0,5 -> 0,7 %.                                         |
//|   4) Stop ins Plus ab 2,0 R (+0,3 R) statt ab 1,75 R (4.41).      |
//|      Serien-Fassung wie 4.41: Tp1R 1.75.                          |
//|   Replikat (Ausz/J, Busts/J, Netto/J; 8 Stoerungen, 1/2/3 J):     |
//|   2022-26 4.41 7,17 / 1,94 / 1631 -> 4.50 8,00 / 1,64 / 1871;     |
//|   2016-21 4,25 / 1,10 / 856 -> 5,56 / 1,41 / 1198. Netto in 8 von |
//|   10 Startjahren hoeher. Serien >= 8 Verluste je Jahr 1,7 / 3,0   |
//|   -> 2,9 / 4,0 (4.40: 5,8 / 5,9).                                 |
//|   Zurueck auf 4.41: R21FolgeMin 0, R21ZweiterPlatz false,         |
//|   R21BudgetPct 0.8, GesamtBudgetPct 1.2, R21RiskPct 0.5,          |
//|   Tp1R 1.75.                                                      |
//|   Bericht DEADBAND_LIVE4_450_Bericht.md.                          |
//|                                                                  |
//|  Build 4.41, 17.09.2026                                           |
//|  BUILD 4.41: SERIEN-FASSUNG - Stop ins Plus ab 1,75 R (+0,3 R)    |
//|   statt ab 3,5 R (+0,5 R). Einzige Aenderung gegen 4.40 (Tp1R,   |
//|   BeAfterT1R). Replikat 2022-26 / 2016-21: Verlustquote 70/73 %  |
//|   -> 62/66 %, Serien >= 8 Verluste 7,0/7,0 -> 2,3/3,7 je Jahr,    |
//|   Busts 2,11/1,54 -> 1,94/1,10, Netto 1704/909 -> 1631/856 $/J.   |
//|   Kostet Netto (Laeufer werden frueher ausgestoppt), gewaehlt     |
//|   wegen kuerzerer Verlustserien. 4.40 = Tp1R 3.5, BeAfterT1R 0.5. |
//|  17.09.2026: Selbsttest ausgebaut (Handelslogik unveraendert)    |
//|  GFT Instant Premium (Konten ab 02.09.2026). Ein EA, ein Chart,   |
//|  zwei Instrumente (XAUUSD.x + NAS100.x auf M15).                  |
//|                                                                  |
//|  BUILD 4.40 (17.09.2026): RSI21-MODUL                            |
//|   Zweite Signalquelle im selben EA, auf demselben Konto und unter|
//|   denselben Kontoregeln: RSI21 Continuation mit den Regeln aus   |
//|   RSI21 v3.4. Long, wenn RSI(21) der letzten Kerze > 75 (Short   |
//|   < 25) auf M15, M30 oder H1, Kerzenbeginn NY 9:30-13:00 (NAS)   |
//|   bzw. 9:30-17:00 (Gold, ohne H1). Bestaetigung: RSI(21) des     |
//|   anderen Symbols > 55 (< 45); Gold alternativ Tagesschluss ueber|
//|   SMA200 und SMA100. Shorts nur unter SMA200 oder SMA100, NAS-   |
//|   Longs nur ueber SMA200, kein Einstieg gegen eine bestaetigte   |
//|   H4-RSI-Divergenz. Stop 3,5 ATR(14) der Signal-Zeitebene, Ziel  |
//|   1,25 R (NAS) / 1,5 R (Gold), Zeit-Exit 1152 M5-Kerzen oder 8   |
//|   Tage. Je Symbol hoechstens eine RSI21-Position (eigene Magic   |
//|   MagicBase+10+Index). Groesse = R21RiskPct 0,5 % x Gewicht      |
//|   (M15 1,25 / M30 1,0 / H1 0,75) x Gold 0,7 x Pufferkurve x      |
//|   unter-Start-Faktor. Budgets getrennt: DEADBAND 0,8 %, RSI21    |
//|   0,8 %, zusammen hoechstens 1,2 % offenes Stop-Risiko.          |
//|   Tagesernte: Bedingung nur auf das DEADBAND-Floating, Kandidaten|
//|   sind alle eigenen Positionen. Gewinn-Ernte und Wochenend-Pause |
//|   gelten fuer beide. Bei Auszahlungsreife werden RSI21-Positionen|
//|   geschlossen (keine Wiederaufnahme im Reife-Zustand).           |
//|   DEADBAND-Risiko RiskMult 1,1 -> 1,0.                           |
//|   Replikat (rollierend, jeder Handelstag ein 10k-Konto, Laufzeit |
//|   1/2/3 Jahre, Mittel ueber 8 Mini-Stoerungen; Ausz/J, Busts/J,  |
//|   Netto/J): 2022-26 4.30 7,73 / 2,27 / 1419 -> 4.40 7,77 / 2,11 /|
//|   1703; 2016-21 4,87 / 1,93 / 837 -> 4,60 / 1,54 / 909. Netto in |
//|   9 von 10 Startjahren hoeher, Busts in 9 von 10 niedriger.      |
//|   Aus mit R21Aktiv=false (dann RiskMult wieder 1.1 = 4.30).      |
//|   Bericht DEADBAND_LIVE4_440_Bericht.md.                         |
//|                                                                  |
//|  BUILD 4.30 (14.09.2026): WOCHENEND-PAUSE                         |
//|   Freitag ab WeSchlussNY (16:45 NY) werden alle eigenen Positionen |
//|   geschlossen - das Konto steht ueber das Wochenende flach, kein   |
//|   Sonntags-Gap kann Floating-, Tages- oder Bodenregel reissen.     |
//|   Sonntag ab WeAufnahmeAbNY (18:00 NY, sonst Montag) nimmt der EA  |
//|   dieselbe Position wieder auf: gleiche Richtung, Lots, Ziel,      |
//|   alter Stop (hoechstens WeStopMaxR = 2 R vom neuen Einstieg),     |
//|   alter R-Bezug (Einstiegskurs vor der Pause) fuer Stop-Nachzug,   |
//|   Ernte und Gewinn-Ernte, alter Zeitzaehler. Hat der Kurs Stop    |
//|   oder Ziel uebersprungen, wird nicht wieder aufgenommen.          |
//|   Bei Auszahlungsreife wird ebenfalls wieder aufgenommen, die      |
//|   Auszahlung wartet, bis die Position ausgelaufen ist              |
//|   (WeAufnahmeReif). Vormerkung ueberlebt einen Neustart            |
//|   (Terminal-Globalvariablen) und verfaellt ab Dienstag.            |
//|   Replikat (rollierend 1/2/3 Jahre, jeder Handelstag ein Start,   |
//|   Mittel): nur schliessen ohne Wiederaufnahme kostet -462 $/J     |
//|   (2022-26) bzw. -86 $/J (2016-21) Netto. Mit Wiederaufnahme und  |
//|   Stop max 2 R: -13 / +3 $/J bei Basis 1495 / 862 $/J, Busts     |
//|   -0,3 / -0,2 je Jahr - Netto gehalten, Rauschpegel +-50 $/J.     |
//|   Bericht DEADBAND_LIVE4_430_Bericht.md.                           |
//|                                                                  |
//|  BUILD 4.20 (Forschungsrunde 4): GEWINN-ERNTE                     |
//|   Zeitbudget von 4.11: 54-80 Handelstage je Jahr steht das Konto  |
//|   mit 5 gueltigen Tagen und erfuellter 10-Tage-Frist nur deshalb  |
//|   ohne Auszahlung, weil der Saldo unter Start + Mindestgewinn     |
//|   liegt. In diesem Zustand realisiert der EA den offenen Gewinn   |
//|   einer Position, die schon GeRueckgangR (1,25 R) von ihrem       |
//|   besten Kurs zurueckgekommen ist, sobald er den Mindestgewinn    |
//|   freischaltet - ganze Position, damit das Konto flach wird und   |
//|   die Auszahlung sofort beantragt werden kann. Positionen, die   |
//|   noch an ihrem Hoch laufen, bleiben unangetastet.                |
//|   Rollierend gegen 4.11 (1 und 2 Jahre): Auszahlungen +1 bis     |
//|   +10 %, Busts -1 bis -5 %, Netto 2016-21 +11 bis +22 %,          |
//|   2022-26 unveraendert (-2 bis 0 %). Bericht Abschnitt 11.         |
//|   Dort auch verworfen: MFE-Trailing, zweite Teilgewinnstufe,      |
//|   Abschluss-Ernte, Wartephasen-Faktor, Reife-Trailing, Fuell-     |
//|   groesse, Groessenfaktor im Mindestgewinn-Zustand.               |
//|                                                                  |
//|  BUILD 4.21 (13.09.2026, Echtbetrieb): Journalzeile und Push      |
//|   "KONTO ERKANNT" beim Laden und nach jeder erkannten Auszahlung  |
//|   (Startsaldo, Einzahlung, Auszahlungen, Zyklus, gueltige Tage,    |
//|   Boden, Puffer, Mindestgewinn, Modus). Preset                    |
//|   DEADBAND_LIVE4_Echtbetrieb.set = alle Echtbetriebs-Werte.       |
//|   Handelslogik = 4.20.                                            |
//|                                                                  |
//|  BUILD 4.10 (Forschungsrunde 2, rollierende Bewertung):          |
//|   - Session bis 13:00 NY (12-13 NY: +0,05 / +0,20 R je Trade,    |
//|     positiv in 10 von 11 Jahren)                                  |
//|   - zweistufige Ernte: ab 16 NY darf auch eine Position mit nur   |
//|     0,5 R Vorlauf den Tag auffuellen, wenn hoechstens 30 % der   |
//|     Schwelle fehlen (HarvestMinR2 / HarvestGapFrac)               |
//|   Rollierend (jeder 3. Handelstag ein frisches Konto, 1 und 2     |
//|   Jahre Laufzeit) gegen LIVE 3.00: Busts -10 bis -39 %, Netto    |
//|   +14 bis +28 % auf beiden Fenstern. Bericht Abschnitt 9.         |
//|                                                                  |
//|  WAS 4.00 GEGENUEBER LIVE 3.00 AENDERT                            |
//|   1) KONTOZUSTAND WIRD GELESEN, NICHT ANGENOMMEN. Beim Laden      |
//|      rekonstruiert der EA aus der Kontohistorie: Startsaldo       |
//|      (Einzahlungs-Deals), letzte Auszahlung, Zyklusbeginn         |
//|      (erster Trade nach der Auszahlung), gueltige Tage, heute     |
//|      realisiert, Tagesstartsaldo (17:00 NY) und die Equity-       |
//|      Spitze fuer den trailenden Boden (aus Deals + M5-Kursen,     |
//|      plus Sicherheitsaufschlag). Ein 10k-Konto mit 200 $ Minus    |
//|      wird also als solches erkannt: Ziel = Startsaldo + Mindest-  |
//|      gewinn, Risiko nach Restpuffer zum Boden.                    |
//|   2) RISIKO NACH PUFFER. Groesse = Basisrisiko x1,1 x Kurve:      |
//|      voll ab 4,0 % Puffer zum Boden, linear bis 0,6 bei 1,5 %,    |
//|      darunter konstant; unter dem Startsaldo zusaetzlich x0,8.    |
//|      Ersetzt Barreserve-Profile, Sicherheitsbremse v19, BufScale. |
//|      Dazu: Ernte-jederzeit aus (HarvestAnyR 0), Stundenfaktor 1,5.|
//|   3) REGELWERK 2026 VOLLSTAENDIG: Floating -1,0 %, Tag -3 %,      |
//|      Boden 6 % trailing auf Equity, 5 gueltige Tage a 0,5 %,     |
//|      10 Tage ab erstem Trade, Mindestauszahlung 100 $ (Gewinn     |
//|      >= 100 / 0,80 = 125 $), Deckel 6 % fuer die ersten zwei     |
//|      Auszahlungen je Konto, Auszahlung nur bei flachem Konto.     |
//|   4) STOPP BEI REIFE: keine neuen Einstiege, offene Positionen    |
//|      laufen aus (StopMode 0, im Replikat die beste Variante).     |
//|      Sobald das Konto flach ist: Meldung "AUSZAHLUNG BEANTRAGEN"  |
//|      mit Betrag, taeglich wiederholt, KEIN Handel bis der         |
//|      Auszahlungs-Deal in der Historie steht. Dann startet der     |
//|      naechste Zyklus von selbst.                                  |
//|   5) Regeln kontoweit gemessen (alle Positionen, auch fremde),    |
//|      gesteuert werden nur eigene (CountForeignPositions).         |
//|   6) NY-Versatz automatisch aus Server- und GMT-Zeit.             |
//|   7) (Selbsttest der Rekonstruktion - am 17.09.2026 ausgebaut)   |
//|                                                                  |
//|  Handelslogik (Signal, Stop, dynamische Groesse, Ausstiege,       |
//|  Ernte, Notbremsen) = LIVE 3.00 / v25, unveraendert bis auf die   |
//|  Groessenkurve. Pyramide, Profile, BufScale, ProtectMode, Tp1Mode |
//|  sind entfernt (auf GFT nie aktiv).                               |
//|                                                                  |
//|  REPLIKAT (Python, GFT-M5-Daten 2022-26 + 2016-21, 40 Start-      |
//|  versaetze, Regeln 2026, Auszahlung erst bei flachem Konto):      |
//|    siehe DEADBAND_v4_Bericht.md - Zahlen im Bericht, nicht hier,  |
//|    damit Header und Bericht nicht auseinanderlaufen.              |
//|                                                                  |
//|  INBETRIEBNAHME                                                   |
//|   1) EINEN XAUUSD.x-M15-Chart, Algo Trading an. Nie zwei Charts.  |
//|   2) Journal pruefen: "KONTO ERKANNT" mit Startsaldo, Zyklus,     |
//|      gueltigen Tagen, Boden und Modus. Stimmt der Startsaldo      |
//|      nicht (z. B. Skalierung), StartBalanceOverride setzen.       |
//|   3) Zeigt das GFT-Dashboard einen anderen Max-Loss-Level als das |
//|      Panel, FloorOverride auf den Dashboard-Wert setzen.          |
//|   4) MetaQuotes ID im Terminal, sonst kein Push.                  |
//|   5) Bei "AUSZAHLUNG BEANTRAGEN" im Dashboard den vollen Gewinn   |
//|      anfordern. Der EA wartet auf den Saldo-Deal und laeuft dann  |
//|      weiter. Nichts neu laden.                                    |
//+------------------------------------------------------------------+
#property copyright "DEADBAND LIVE 4"
#property version   "6.50"
#include <Trade\Trade.mqh>
CTrade trade;

input group             "=== Instrumente ==="
input string SymbolList    = "XAUUSD.x,NAS100.x";  // Komma-getrennt, exakte Broker-Namen
input group             "=== Signal ==="
input double SessStartNY   = 3.0;    // Session Start (NY-Stunde)
input double SessEndNY     = 13.0;   // Session Ende  (NY-Stunde); 3.00: 12, Build 4.10: 13
input bool   AutoNYOffset  = false;  // NY-Versatz aus Server- und GMT-Zeit bestimmen (6.10: aus - GFT-Server = NY + 7 h in allen Sommerzeit-Phasen, geprueft; so verschiebt eine falsche PC-Uhr die Tagesgrenze nicht)
input int    NYOffsetHours = 7;      // Serverzeit minus X = NY-Zeit (Rueckfall, wenn Auto aus/unplausibel)
input group             "=== Filter ==="
input bool   UseTrend      = true;   // Trendfilter EMA auf Tagesbasis
input int    EmaLen        = 50;     // EMA-Laenge (Tage)
input bool   UseVwap       = true;   // VWAP-Bestaetigung
input bool   UseRsi        = true;   // RSI-Bestaetigung
input int    RsiLen        = 14;     // RSI-Laenge
input double RsiLvl        = 50.0;   // RSI-Schwelle
input bool   UseCls        = true;   // Schlusskurs-Position in der Signalkerze
input string ClsMinList    = "0.70,0.65"; // Kerzenqualitaet je Symbol, Reihenfolge wie SymbolList
input bool   UseMacd       = true;   // MACD-Histogramm muss in Handelsrichtung zeigen
input int    MacdFast      = 12;
input int    MacdSlow      = 26;
input int    MacdSignal    = 9;
input bool   UseVolume     = true;   // nur Kerzen mit ueberdurchschnittlichem Volumen
input int    VolLen        = 50;
input double VolMin        = 1.00;
input group             "=== Stop ==="
input bool   UseAtrStop    = true;   // Stop auf ATR statt Range-Gegenkante
input int    AtrLen        = 14;
input double AtrMult       = 3.00;
input group             "=== Dynamische Groesse ==="
input bool   UseDynRisk     = true;
input int    VolaRankLen    = 500;
input double DynA           = 1.40;
input double DynB           = 0.80;
input double DynMin         = 0.35;
input double DynMax         = 2.00;
input bool   UseStochRisk   = true;
input int    StochK         = 14;
input int    StochSlow      = 3;
input int    StochD         = 3;
input double StochWeight    = 0.20;
input group             "=== Exit ==="
input string RiskPctList   = "0.259,0.288"; // Basisrisiko je Symbol in % vom Startsaldo
input double RiskMult      = 0.9;    // Faktor auf das DEADBAND-Basisrisiko (4.80: 0,9; 4.40-4.70: 1,0; 4.30: 1,1)
input double Tp1R          = 1.5;   // ab X R: Teilverkauf Tp1F und Stop auf +BeAfterT1R (5.10: 1,5; 5.00: 2,0; 4.41: 1,75; 4.40: 3,5)
input double Tp1F          = 0.50;   // Teilverkauf an Tp1R (Anteil, 0 = keiner; 5.10: 0,5; bis 5.00: 0)
input double Tp2R          = 5.0;
input double Tp2F          = 0.00;
input string TpFinalList   = "8,10"; // Endziel in R je Symbol
input bool   UseBeAfterT1  = true;
input double BeAfterT1R    = 0.05;   // Stop nach Tp1R auf +X R (5.10: 0,05; 4.41-5.00: 0,3; 4.40: 0,5)
input int    MaxHoldBars   = 192;    // Zeit-Exit nach N M15-Kerzen
input group             "=== Schutz (EA-Bremsen, innen) ==="
input int    MaxTradesDay  = 1;      // max. Trades pro Tag und Symbol
input int    MaxLossDay    = 2;      // Stopp nach N Verlusten am Tag und Symbol
input double DayStopPct    = 2.4;    // Tagesstopp (Equity gegen Tagesstartsaldo) in % vom Startsaldo
input double FloatStopPct  = 0.80;   // Not-Exit bei Buchverlust in % (4.70: 0,80; bis 4.60: 0,85) - Basis siehe FloatBasisMinSaldo
input bool   FloatBasisMinSaldo = true; // 4.70: Floating-Bremse und Firmengrenze auf min(Startsaldo, aktueller Saldo) statt nur Startsaldo
input bool   FloatGestuft  = true;   // 4.60: am FloatStopPct nur die eigene Position mit dem groessten Verlust schliessen (wiederholt), nicht alle
input double MinLotRiskTol = 2.0;    // Signal auslassen, wenn das Mindestlot > X-faches des Sollrisikos
input double RiskBudgetPct = 0.80;   // Summe offener Stop-Risiken in % vom Startsaldo
input long   MagicBase     = 230250; // je Symbol +Index
input group             "=== GFT-Regelwerk (aussen, Firmengrenzen) ==="
input bool   KontoAb20260902 = true;  // Konto ab 02.09.2026: Floating -1,0 % (sonst -1,5 %)
input bool   KontoAb20260730 = true;  // Konto ab 30.07.2026: Mindestauszahlung 100 $
input double MaxLossPct     = 6.00;   // trailender Maximalverlust (Equity-Hoch) in % vom Startsaldo
input double RuleDayLossPct = 3.0;    // Tagesverlust in % vom Tagesstartsaldo (17:00 NY)
input double ValidDayPct    = 0.50;   // gueltiger Tag ab X % vom Startsaldo, realisiert
input int    NeedValidDays  = 5;
input int    CycleDays      = 10;     // Kalendertage ab erstem Trade des Zyklus
input double ProfitSplit    = 0.80;
input double MinPayoutUSD   = 105.0;  // Mindestauszahlung (Anteil des Traders); 4.90: 105 statt 100 (Reserve fuer 3 % Auszahlungsgebuehr)
input double MinProfitPct   = 0.0;    // Mindestgewinn fuer die Auszahlung in % vom Startsaldo (6.40: 0 = nur GFT-Mindestauszahlung, 131,25 $ Gewinn; 6.00-6.30: 3,0 = 300 $ auf 10k)
input double PayoutCapPct   = 6.0;    // Deckel je Auszahlung in % vom Startsaldo ...
input int    PayoutCapCount = 2;      // ... fuer die ersten N Auszahlungen je Konto
input group             "=== Auszahlungs-Logik ==="
input int    StopMode       = 0;      // bei Reife: 0 offene laufen aus | 1 sofort alles schliessen | 2 nur Gewinner schliessen
input int    ReminderHours  = 24;     // Erinnerung "Auszahlung beantragen" alle X Stunden
input bool   UsePush        = true;
input group             "=== Kontozustand ==="
input double StartBalanceOverride = 0.0;  // 0 = Startsaldo aus Einzahlungs-Deals
input double FloorOverride        = 0.0;  // 0 = Boden rekonstruieren, sonst Max-Loss-Level laut Dashboard (Equity)
input double PeakSafetyPct        = 0.10; // Sicherheitsaufschlag auf die rekonstruierte Equity-Spitze in % vom Startsaldo
input string CycleStartOverride   = "";   // "YYYY.MM.DD" erzwingt den Zyklusbeginn (leer = automatisch)
input bool   CountForeignPositions= true; // Regeln und Flach-Pruefung ueber ALLE Positionen (auch fremde)
input int    HistoryDaysMax       = 400;  // Rekonstruktion hoechstens so weit zurueck (ohne Einzahlung im Fenster: ganze Historie)
input string FloorOverrideZeit    = "";   // 6.10: Serverzeit der Dashboard-Ablesung fuer FloorOverride "JJJJ.MM.TT HH:MI" (Pflicht mit FloorOverride); gilt nur bis zur naechsten Auszahlung
input string AuszahlungKennung    = "";   // 6.10: Stichworte im Kommentar der GFT-Auszahlungsbuchung, z. B. "withdraw;payout" (leer = Saldo-Test: Saldo faellt auf den Startsaldo)
input string KeineAuszahlung      = "";   // 6.10: negative Saldo-Buchungen, die KEINE Auszahlung sind: "JJJJ.MM.TT HH:MI;..." (Serverzeit)
input string AuszahlungZeiten     = "";   // 6.10: Abbuchungen, die Auszahlungen SIND (z. B. Teilauszahlung): "JJJJ.MM.TT HH:MI;..." (Serverzeit)
input string AuszahlungAngefordertAm = ""; // 6.10: Auszahlung beantragt am "JJJJ.MM.TT HH:MI" (Serverzeit): keine Einstiege, bis die Auszahlung gebucht ist
input double ValidDayReserveUSD   = 0.5;  // 6.10: gueltiger Tag erst ab 0,5 % + X $ Rundungsreserve; zusaetzlich muessen beide Lesarten der Kommissions-Zuordnung reichen
input bool   GueltigHeuteZaehlt   = true; // 6.10: der laufende Tag zaehlt schon mit, sobald er die Schwelle erreicht (false = erst nach 17:00 NY)
input group             "=== Risiko nach Puffer (v4) ==="
input double DDFullPct      = 5.0;    // ab X % Puffer zum Boden volle Groesse (Puffer an der Equity-Spitze = MaxLossPct 6 %; 6.40: 5,0 = Verkleinerung ab 1 % Rueckgang; bis 6.30: 4,0)
input double DDMinPct       = 2.5;    // bei X % Puffer ist der Faktor DDMinFactor, darunter konstant (6.40: 2,5 = ab 3,5 % Rueckgang; bis 6.30: 1,5)
input double DDMinFactor    = 0.2;    // Faktor bei DDMinPct und darunter (6.40: 0,2 - haelt die Konten vom Boden fern; bis 6.30: 0,6)
input double PeakUnsicherFaktor = 0.6; // 6.40: Groessenfaktor, solange die Equity-Spitze (Boden) nicht sicher rekonstruiert ist (bis 6.30 = DDMinFactor 0,6)
input double BelowStartMult = 0.8;    // Faktor, solange die Equity unter dem Startsaldo liegt
input bool   UseSafety      = false;  // v19-Bremse (Groesse x SafetyFactor unter SafetyBufPct Puffer)
input double SafetyBufPct   = 1.30;
input double SafetyFactor   = 0.50;
input group             "=== v25: Shorts, Stundenfaktor, Ernte ==="
input string AllowShortList = "0,1";  // Shorts je Symbol (Gold: kein Edge)
input double HourBoostFromNY= 9.0;
input double HourBoost      = 1.50;   // Groesse ab HourBoostFromNY (v25: 1.3, Replikat v4: 1.5)
input int    HarvestMode    = 2;      // Tag ernten: 0 aus | 1 jederzeit | 2 nur ab HarvestFromNY
input double HarvestMinR    = 2.0;
input double HarvestMargin  = 0.05;
input double HarvestFromNY  = 16.0;
input bool   HarvestPartial = true;
input double HarvestAnyR    = 0.0;    // zusaetzlich jederzeit ernten ab X R Vorlauf (0 = aus; v25 Sicher: 4)
input double HarvestMinR2   = 0.5;    // 4.10: im Erntefenster reicht X R Vorlauf, wenn nur noch wenig zur Schwelle fehlt (0 = aus)
input double HarvestGapFrac = 0.3;    // 4.10: ... hoechstens X * Schwelle darf fehlen
input group             "=== 4.20: Gewinn-Ernte (nur der Mindestgewinn fehlt) ==="
input bool   GeAktiv       = true;   // offenen Gewinn realisieren, sobald nur noch der Mindestgewinn zur Auszahlung fehlt
input double GeRueckgangR  = 0.0;    // Position muss X R von ihrem besten Kurs zurueckgekommen sein (5.10: 0 = ohne Bedingung; bis 5.00: 1,25)
input double GeMinR        = 1.0;    // Mindest-Vorlauf (bester Kurs) in R
input double GeAufschlag   = 0.05;   // Aufschlag auf den Mindestgewinn (Kommission, Slippage)
input double GeAbNY        = 0.0;    // Erntefenster ab X NY ...
input double GeBisNY       = 17.0;   // ... bis X NY (Tageswechsel)
input group             "=== 4.30: Wochenend-Pause ==="
input bool   WeAktiv         = true;   // Freitag alle eigenen Positionen schliessen (Wochenende flach)
input double WeSchlussNY     = 16.75;  // Freitag ab dieser NY-Stunde schliessen (16.75 = 16:45)
input bool   WeAufnahme      = true;   // nach dem Wochenende dieselbe Position wieder aufnehmen
input double WeAufnahmeAbNY  = 18.0;   // Sonntag ab dieser NY-Stunde (Montag: erste Gelegenheit)
input bool   WeAufnahmeReif  = true;   // auch bei Auszahlungsreife (Auszahlung wartet, bis die Position ausgelaufen ist)
input double WeStopMaxR      = 2.0;    // Stop bei Wiederaufnahme hoechstens X R vom neuen Einstieg (0 = alter Stop)
input bool   WeGroesseBudget = false;  // Lots bei Wiederaufnahme kuerzen, bis das Stop-Risiko ins Risikobudget passt
input string WeSpreadMaxList = "0,0";  // Wiederaufnahme nur bei Spread <= X Punkte je Symbol (0 = ohne Pruefung)
input group             "=== 4.40: RSI21-Modul ==="
input bool   R21Aktiv        = true;   // zweite Signalquelle RSI21 Continuation (Regeln RSI21 v3.4)
input double R21RiskPct      = 0.50;   // 6.00: 0,50 (5.10: 0,63; 4.80-5.00: 0,7; 4.60/4.70: 0,6) - Risiko je RSI21-Trade in % vom Startsaldo (x Zeitebenen-Gewicht, x Gold-Faktor, x Pufferkurve)
input double R21GoldMult     = 0.70;   // Gold-Faktor (RSI21 v3.4 Risikoparitaet)
input string R21Gewichte     = "1.25,1.0,0.75"; // Gewicht je Zeitebene M15, M30, H1
input string R21GoldSymbol   = "XAUUSD.x";
input string R21NasSymbol    = "NAS100.x";
input bool   R21GoldOhneH1   = true;   // Gold nicht auf H1 (RSI21 v3.4)
input double R21AbNY         = 9.5;    // Signal-Kerzen ab dieser NY-Stunde (9.5 = 9:30)
input double R21NasBisNY     = 13.0;   // NAS-Signal-Kerzen bis (NY-Stunde)
input double R21GoldBisNY    = 17.0;   // Gold-Signal-Kerzen bis (NY-Stunde)
input int    R21RsiLen       = 21;
input double R21Oben         = 75.0;   // Long ueber
input double R21Unten        = 25.0;   // Short unter
input double R21CrossThr     = 55.0;   // Bestaetigung: RSI des anderen Symbols (gleiche Zeitebene) ueber X bzw. unter 100-X
input int    R21MaLang       = 200;    // Tages-SMA fuer Regime, NAS-Longs, Gold-Gate
input int    R21MaSchnell    = 100;    // Tages-SMA schnell fuer Short-Regime und Gold-Gate
input bool   R21DivH4        = true;   // kein Einstieg gegen eine bestaetigte H4-RSI-Divergenz
input int    R21DivRadius    = 2;
input double R21DivGap       = 2.0;
input int    R21DivHistoryH1 = 6000;
input double R21StopATR      = 2.0;    // Stop in ATR(14) der Signal-Zeitebene (4.60: 2,0; bis 4.50: 3,5)
input double R21NasRR        = 2.2;    // Ziel NAS in R (4.60: 2,2 = 4,4 ATR; bis 4.50: 1,25)
input double R21GoldRR       = 2.64;   // Ziel Gold in R (4.60: 2,64 = 5,3 ATR; bis 4.50: 1,5)
input int    R21ExitBarsM5   = 1152;   // Zeit-Exit nach N M5-Kerzen ...
input int    R21ExitTage     = 8;      // ... oder nach N Kalendertagen
input double R21BudgetPct    = 1.20;   // Summe offener RSI21-Stop-Risiken in % vom Startsaldo (4.50: 1,2; 4.40: 0,8)
input double GesamtBudgetPct = 0.90;   // 6.00: 0,9 (5.10: 2,0; 4.40: 1,2) - Summe ALLER offenen Stop-Risiken (alle Module) in % vom Startsaldo
input int    R21MaxLossDay   = 2;      // keine RSI21-Einstiege mehr nach N Verlusten am Tag je Symbol
input bool   R21ReifeSchliessen = true; // bei Auszahlungsreife RSI21-Positionen schliessen
input long   R21MagicOffset  = 10;     // RSI21-Magic = MagicBase + Offset + Symbolindex (>= 8); zweiter Platz + 8
input group             "=== 4.50: RSI21 Folgesignal, zweiter Platz ==="
input int    R21FolgeMin     = 240;    // RSI21 nur als Folgesignal: frueheres gueltiges Signal (Symbol, Richtung) hoechstens X Minuten alt (0 = aus, wie 4.40)
input bool   R21ZweiterPlatz = true;   // zweite RSI21-Position je Symbol, wenn die erste in dieselbe Richtung laeuft
input group             "=== 4.90: GFT-Regeln und Betriebssicherheit ==="
input bool   HedgeSperre      = true;   // kein Einstieg/keine Wiederaufnahme gegen eine offene Position im selben Symbol (GFT: Hedging = Konto weg)
input int    NewsSperreMin    = 6;      // +-X min um rote USD-Termine: keine Einstiege, keine eigenen Gewinnschliessungen > 1 % (0 = aus; nur live)
input int    MinHalteSek      = 130;    // eigene Gewinnschliessungen erst nach X s Haltedauer (GFT: Gewinne aus Trades < 120 s werden gestrichen)
input int    SchlussVorlaufMin= 5;      // keine Einstiege in den letzten X min vor der Freitags-/Sondertag-Schliessung
input string WeSonderTage     = "2026.11.27 12.5;2026.12.24 12.5;2026.12.31 16.0;2027.03.25 16.5;2027.11.26 12.5;2027.12.23 16.5"; // Tage mit fruehem Schluss oder Feiertag danach: "JJJJ.MM.TT NY-Stunde" (wie Freitag behandeln)
input double MaxIdeeMarginPct = 70.0;   // Margin je Handelsidee (Symbol + Richtung) hoechstens X % der Equity (GFT: > 80 % = Gambling), 0 = aus
input double WeSpreadMaxR     = 0.15;   // Wiederaufnahme erst bei Spread <= X x R-Abstand, wenn WeSpreadMaxList 0 ist (0 = aus)
input bool   VpsSperre        = true;   // auf einem VPS nicht starten (GFT Instant Premium: VPS verboten)
input int    InaktivWarnTage  = 20;     // Push, wenn seit X Tagen kein Einstieg (GFT: 30 Tage ohne Trade = Konto weg), 0 = aus
input bool   TagesRefEquity   = true;   // Tagesverlust gegen max(Saldo, Equity) um 17:00 NY (vorsichtige Lesart der 3-%-Regel)
input double PayoutErkennMinUSD = 50.0; // negative Saldo-Buchung ab X $ = Auszahlung (neuer Zyklus), darunter Gebuehr/Korrektur
input int    R21ReifeModus    = 2;      // bei Reife RSI21: 2 alle schliessen (4.80) | 3 Verlierer nur, wenn Reife danach bleibt | 1 nur Gewinner
input group             "=== 5.00: NAS-Noise-Modul (aus NAS100 Flip v4) ==="
input bool   NzAktiv          = true;   // dritte Signalquelle: Noise-Area-Momentum NAS100, nur Long, intraday (false = keine neuen Noise-Einstiege, offene werden verwaltet)
input string NzSymbol         = "NAS100.x"; // muss in der SymbolList stehen
input double NzRiskPct        = 0.45;   // Risiko je Signal in % vom Startsaldo (x Vola-Gewicht, x Pufferkurve), gleich verteilt auf die Teilpositionen (6.40: 0,45; 6.00-6.30: 0,35; 5.10: 0,45; 5.00: 0,30)
input string NzStops          = "0.35,0.5,0.75"; // Stops der Teilpositionen in Tages-Sigma (Drei-Stop-Ensemble); "0.5" = eine Position
input double NzBudgetPct      = 0.0;    // Summe offener Noise-Stop-Risiken in % vom Startsaldo (0 = nur GesamtBudgetPct)
input int    NzTage           = 14;     // Tage fuer die uebliche Bewegung je Uhrzeit und fuer das Tages-Sigma (5-60)
input double NzK              = 1.0;    // Bandbreite (x uebliche Bewegung)
input int    NzErstePruefung  = 600;    // erste Pruefung (NY-Minute, 600 = 10:00)
input int    NzLetzterEinstieg= 930;    // letzte Einstiegspruefung (NY-Minute; bei Pruefung zur vollen Stunde ist 15:00 die letzte)
input int    NzPruefAlle      = 60;     // Pruefung alle X Minuten (ab NzErstePruefung)
input int    NzSchlussMin     = 955;    // alle Noise-Positionen schliessen ab NY-Minute (955 = 15:55)
input double NzStopZeitPow    = 0.5;    // Stop x (Restzeit bis Schluss / Restzeit ab erster Pruefung)^X (v4: 0,5; 0 = aus)
input bool   NzVolaGewicht    = true;   // Risiko nach heutiger 5-min-RV bis zur Pruefung gewichten (v4)
input double NzVolaPow        = 0.5;    // Gewicht = Verhaeltnis^-X
input double NzVolaMin        = 0.5;    // Verhaeltnis unten kappen
input double NzVolaMax        = 2.0;    // Verhaeltnis oben kappen
input int    NzReifeModus     = 2;      // bei Auszahlungsreife: 2 alle Noise-Positionen schliessen | 1 nur Gewinner | 0 laufen bis 15:55
input long   NzMagicOffset    = 30;     // Noise-Magic = MagicBase + Offset + Teil (0..7), mindestens R21MagicOffset + 16
input string NzFreieTage      = "";     // zusaetzliche handelsfreie NY-Tage "JJJJ.MM.TT;JJJJ.MM.TT" (US-Feiertage/verkuerzte Tage 2019-2027 sind eingebaut)
input group             "=== 5.10: GFT-Regelschutz (strenge Lesart) ==="
input bool   FloatNurVerlierer = true;  // Floating-Bremse und Notbremse auf die SUMME DER VERLUSTPOSITIONEN inkl. Swap und Einstiegskommission (Gewinner verrechnen nicht) - strenge Lesart der -1-%-Regel
input double SwapVorsorgePct  = 0.80;   // vor dem Rollover (Mitternacht Serverzeit = 17:00 NY): Verlierer + erwarteter Swap <= -X % -> groesste Verlierer vorher schliessen (0 = aus)
input int    SwapVorsorgeMin  = 10;     // ... in den letzten X Minuten vor dem Rollover
input double IdeeMaxRisikoPct = 0.90;   // Summe offener Stop-Risiken je Idee (Symbol + Richtung, alle Module) in % vom Startsaldo (0 = aus; 6.00: 0,9; 5.10: 1,25)
input string NurAufPcPfad     = "";     // nicht leer: Start nur, wenn der Terminal-Datenpfad diesen Text enthaelt (z. B. Windows-Benutzername des Heim-PCs) - Schutz gegen Start auf Server/VPS
input group             "=== 5.10: Auszahlungstakt und Serienschutz ==="
input int    AbschlussLetzte  = 5;      // fehlen nur noch <= X gueltige Tage: offenen Gewinn jederzeit so weit realisieren, dass heute gueltig wird (0 = aus, >= 5 = immer; 6.40: 5, 6.10-6.30: 3, bis 6.00: 2)
input double AbschlussMinR    = 0.3;    // ... nur Positionen, deren bester Kurs >= X R erreicht hat (6.10: 0,3; bis 6.00: 0,5)
input double AbschlussAbNY    = 0.0;    // ... Fenster ab X NY
input double AbschlussBisNY   = 17.0;   // ... bis X NY (Tageswechsel)
input int    AbschlussModule  = 15;     // 6.10: ... aus diesen Modulen (Summe): 1 DEADBAND, 2 RSI21, 4 Noise, 8 Fades (15 = alle; bis 6.00: 1)
input int    SerienStopp      = 3;      // nach N Verlusttrades in Folge (alle Module, Noise-Signal = 1 Trade) keine neuen Einstiege bis 17:00 NY (0 = aus; 6.00: 3, 5.10: 4)
input int    SerienPauseTage  = 0;      // ... zusaetzlich X weitere Prop-Tage Pause (0 = nur Rest des Tages)
input group             "=== 6.00: Fade-Module (Fehlausbruch einer Sitzungs-Range, Regime-Waechter) ==="
input bool   DbAktiv          = false;  // DEADBAND-Ausbruch: neue Einstiege (6.00: aus; offene Positionen werden immer verwaltet)
input bool   FadeAktiv        = true;   // Fade-Module: neue Einstiege (false = nur virtuell mitrechnen, offene verwalten)
input string FadeListe        = "";     // leer = Standard-Liste (10 Module, siehe FADE_STANDARD im Code). Eigene Liste: je Modul "Symbol,r0,L,tlen,xoff,buf,tgt,dir,mx,Name" getrennt mit ; (r0 = Range-Beginn NY-Minute, negativ = Vortag; L/tlen/xoff Minuten; tgt 0 Mitte, 1 Gegenseite; dir 1 long, -1 short, 0 beide; mx = Range hoechstens mx x ATR14 D1)
input string FadeAus          = "";     // Namen von Modulen, die nicht handeln sollen (rechnen virtuell weiter), getrennt mit ; z. B. "N1800;X0300S" (leer = alle handeln)
input double FadeRiskPct      = 0.70;   // Risiko je Fade-Trade in % vom Startsaldo (x Pufferkurve), gedeckelt durch GesamtBudgetPct und IdeeMaxRisikoPct (6.50: 0,70 - mehr Luft zur Floating-Bremse; 6.00-6.40: 0,75)
input int    FadeWaechterN    = 30;     // Regime-Waechter: Profitfaktor der letzten N virtuellen Signale je Modul ...
input double FadeWaechterPF   = 1.20;   // ... muss ueber X liegen, sonst nur virtuell (0 = Waechter aus)
input int    FadeWaechterMin  = 30;     // ... und mindestens so viele Signale vorliegen (Replikat: 30 = volles Fenster)
input int    FadeHistTage     = 600;    // Historie fuer den Waechter beim Start (Kalendertage M5; Max. Balken im Chart auf Unbegrenzt stellen)
input int    FadeZielAbSek    = 130;    // Ziel erst nach X s Haltedauer setzen (mind. 120; GFT: Gewinne aus Trades < 120 s werden gestrichen)
input double FadeMinStopSpreads = 6.0;  // Einstieg nur, wenn der Stop mind. X aktuelle Spreads entfernt ist (Reserve der -1-%-Regel bei Kursspruengen; 0 = aus)
input long   FadeMagicOffset  = 50;     // Fade-Magic = MagicBase + Offset + Modul (0..9), mindestens NzMagicOffset + 8
input group             "=== 6.20: Probability Grid (Schwung-Statistik als Fade-Filter, Konzept LuxAlgo) ==="
input bool   GridAktiv        = true;       // Fade-Signale GEGEN den laufenden Schwung nur, wenn die Schwung-Statistik es erlaubt (false = Fades wie 6.10)
input ENUM_TIMEFRAMES GridTF  = PERIOD_M5;  // Zeitebene der Schwuenge, aus M5 gebildet: M5, M10, M15, M20, M30 oder H1 (Replikat: M5 am besten)
input int    GridLaenge       = 15;         // Swing Length: neue Laufrichtung, wenn der Kerzenkoerper das Hoch/Tief der letzten X Kerzen bildet (LuxAlgo 20; 6.20: 15)
input int    GridMaxSchenkel  = 1000;       // Maximum Reversals: je Richtung zaehlen die letzten X Schenkel (LuxAlgo 1000)
input int    GridMinSchenkel  = 30;         // weniger Schenkel je Richtung: Grid filtert nicht (wie 6.10)
input double GridMaxStopChance= 0.70;       // Regel S: kein Fade gegen den Lauf, wenn die Grid-Chance, dass der Lauf bis zum Stop weiterlaeuft, >= X ist (0 = aus)
input double GridMinReife     = 0.0;        // Regel A: kein Fade gegen einen Lauf, der kleiner ist als das X-Perzentil der Schenkel (0 = aus; getestet 0,33)
input int    GridVorlaufTage  = 300;        // M5-Historie vor der Fade-Historie fuer die Schenkel-Statistik (Kalendertage; Max. Balken im Chart = Unbegrenzt)
input string GridOhne         = "N1800";    // Fade-Module ohne Grid, getrennt mit ; (N1800: mit Grid blieben < 30 Signale in FadeHistTage - der Waechter liesse es nie live)
input bool   GridNurLive      = false;      // true = Grid sperrt nur den Live-Einstieg, der Regime-Waechter zaehlt alle Signale wie 6.10 (weniger Zusatz-Ertrag, Serien wie 6.10)
input group             "=== 6.30: Trefferquote (Teilgewinn der Fades, Einstand fuer RSI21 und Noise) ==="
input double FadeT1R          = 0.0;        // Fade: ab X R (R = Stop-Abstand beim Einstieg) FadeT1Anteil der Position schliessen; Stop und Ziel bleiben (0 = aus, wie 6.20 und 6.40; 6.30: 0,6)
input double FadeT1Anteil     = 0.5;        // Anteil der Fade-Position, der bei FadeT1R geschlossen wird (0,1-0,9)
input double R21EinstandAbR   = 1.0;        // RSI21: Stop auf Einstand + EinstandPlusR, sobald der Kurs X R im Plus war (0 = aus; nicht nach Wochenend-Wiederaufnahme)
input double NzEinstandAbR    = 1.0;        // Noise: je Teil Stop auf Einstand + EinstandPlusR ab X R (R = Stop-Abstand des Teils; 0 = aus)
input double EinstandPlusR    = 0.05;       // neuer Stop = Einstieg + X R (deckt Spread/Kosten: der Trade endet als kleiner Treffer)
input group             "=== 6.40: Auszahlungstakt (gueltige Tage schuetzen, Regime-Waechter ueber das Fade-Portfolio) ==="
input bool   GueltigSchutz    = true;       // heute schon gueltig und dem Zyklus fehlen (ohne heute) noch gueltige Tage: keine neuen Einstiege bis 17:00 NY (Wochenend-Wiederaufnahmen ausgenommen; 6.50: Umfang je Modul siehe GueltigSchutzR21BisNY/-Regime/-Frei; false = wie 6.30)
input int    FadeWaechterModus= 1;          // Regime-Waechter der Fades: 1 = Portfolio (PF der letzten FadePortN virtuellen Signale ALLER Fade-Module), 0 = je Modul (FadeWaechterN/PF/Min wie 6.00-6.30)
input int    FadePortN        = 200;        // Portfolio-Waechter: Zahl der letzten abgeschlossenen virtuellen Fade-Signale (alle Module, innerhalb FadeHistTage)
input double FadePortPF       = 1.15;       // Portfolio-Waechter: Fades live nur, wenn deren Profitfaktor > X (0 = Waechter aus: Fades immer live, auch vor dem Laden der Historie)
input group             "=== 6.50: Netto (Schutz gueltiger Tage je Modul) ==="
input double GueltigSchutzR21BisNY = 13.0;  // RSI21: Schutz gueltiger Tage fuer Einstiege vor X NY, danach handelt RSI21 auch an einem schon gueltigen Tag, solange das Fade-Regime live ist (24 = immer geschuetzt wie 6.40; 0 = nach Uhrzeit nie, nur noch ohne Fade-Regime; 11 = mehr Netto, aber mehr Busts im alten Regime 2010)
input string GueltigSchutzFrei     = "N1330;N1300"; // Fade-Module ohne Schutz gueltiger Tage (handeln auch an einem schon gueltigen Tag), getrennt mit ; (leer = alle Fades geschuetzt wie 6.40)
input bool   GueltigSchutzR21Regime = true;  // RSI21 ab GueltigSchutzR21BisNY nur frei, solange der Portfolio-Waechter die Fades live handeln laesst (PF der letzten FadePortN > FadePortPF, gerechnet zur Signalzeit = Open der Einstiegskerze) - im alten Regime bleibt RSI21 geschuetzt wie 6.40 (false = ab GueltigSchutzR21BisNY immer frei)
input group             "=== Anzeige, Leiter, Test ==="
input bool   ShowPanel     = true;
input bool   ShowLeiter    = true;
input double Barreserve    = 0.0;    // ausgezahltes Geld, das zum Kauf bereitliegt (nur Anzeige)
input double KaufPuffer    = 2.0;

#define MAXSYM 8
#define MAXSLOT 16            // 4.40: DEADBAND-Plaetze 0..nSym-1, RSI21-Plaetze nSym..nSlot-1
#define MAXFADE 10            // 6.00: Fade-Module (vor der ersten Verwendung in AbschlussErntePruefen)
#define FADEHIST 256          // 6.40: 256 (>= FadePortN, der Portfolio-Waechter braucht bis zu FadePortN Ergebnisse je Modul)
struct SymState
  {
   string   sym;
   long     magic;
   int      hEma, hRsi, hAtr, hSto, hMacd;
   double   pt;
   datetime lastBar, entryBarTime, curDay, lastCloseTry;
   double   slPx, rDist, entryPx, vol0, vol1, vol2;
   bool     t1Done, t2Done, beDone;
   datetime lastBeTry;
   double   tpF;
   int      tradesToday, closeFails;
   double   riskPct, clsMin;
   double   mfeR;
   bool     allowShort;
   datetime lastHarvTry;
   double   refPx;          // 4.30: Bezugskurs fuer R-Stufen (Einstieg vor einer Wochenend-Pause)
   double   weSpreadMax;    // 4.30: Spread-Grenze fuer die Wiederaufnahme (Punkte, 0 = keine)
   // 4.40: RSI21-Modul
   bool     r21;            // Platz ist ein RSI21-Platz
   int      basis;          // Index des DEADBAND-Platzes desselben Symbols
   bool     istGold;
   double   rr;             // Ziel in R
   datetime entryTime;      // Eroeffnung (Zeit-Exit, bleibt ueber eine Wochenend-Pause erhalten)
   int      tfMin;          // Zeitebene des Signals in Minuten
   int      hR21Rsi[3];     // RSI(21) M15, M30, H1
   int      hR21Atr[3];     // ATR(14) M15, M30, H1
   int      hMaLang, hMaSchnell;
   datetime r21Bar[3];
   bool     zweit;          // 4.50: zweiter RSI21-Platz des Symbols (Einstieg ueber den ersten Platz)
   int      partner;        // 4.50: erster Platz -> Index des zweiten (-1 = keiner), zweiter Platz -> Index des ersten
   ulong    posTk;          // 4.90: Ticket der Position, zu der der Platz-Zustand gehoert (0 = keiner)
   bool     r21Be;          // 6.30: RSI21-Einstand erledigt oder nicht vorgesehen (Wiederaufnahme, ohne R)
  };
SymState S[MAXSLOT];

// 4.30: vorgemerkte Wiederaufnahme nach dem Wochenende
struct WePend
  {
   bool     aktiv;
   int      dir;            // +1 long, -1 short
   double   sl, tp, lots, rd, ref, mfe;
   bool     t1, be;
   datetime entryBar;       // Einstiegskerze vor der Pause (Zeit-Exit zaehlt weiter)
   long     fri;            // NY-Kalendertag des Freitags
   datetime lastTry;
  };
WePend   W[MAXSLOT];
int      nSym = 0;
int      nSlot = 0;                  // 4.40: DEADBAND- plus RSI21-Plaetze
double   r21w[3];                    // 4.40: Gewichte M15, M30, H1
datetime r21DivBucket[MAXSLOT];      // 4.40: H4-Divergenz-Cache je Platz
int      r21DivDir[MAXSLOT];
datetime r21LastSig[MAXSLOT][2];     // 4.50: Kerzenzeit des letzten gueltigen RSI21-Signals je erstem Platz, [0] long, [1] short
int      nyOff = 7;                  // wirksamer NY-Versatz in Stunden

// ---- Kontozustand (rekonstruiert, dann live fortgeschrieben) ----
double   kStart = 0.0;               // Startsaldo
datetime kAccountFrom = 0;           // erste Einzahlung
datetime kLastPayout = 0;            // letzter Auszahlungs-Deal
int      kPayouts = 0;               // Auszahlungen seit Kontostart
datetime kCycleStart = 0;            // erster Trade nach der letzten Auszahlung
int      kValidDays = 0, kTradeDays = 0;
double   kCycleReal = 0.0;           // realisiert seit Zyklusbeginn (abgeschlossene Tage + heute)
double   kTodayReal = 0.0;
long     kTodayRealTag = -1;            // 6.40: Prop-Tag, fuer den kTodayReal zuletzt berechnet wurde
bool     gGueltigSchutz = false;        // 6.40: Schutz gueltiger Tage aktiv (keine neuen Einstiege bis 17:00 NY; 6.50: je Modul, GueltigSchutzUmfang)
long     gGsTag = -1;                   // 6.40: Tag der letzten Journal-Meldung dazu
long     kTagIdx[]; double kTagErg[]; int kTagN = 0;   // 6.10: realisiert je Prop-Tag im Zyklus (Kontobericht)
double   kPeakEq = 0.0;              // Equity-Spitze seit letzter Auszahlung (mit Aufschlag)
double   kDayStartBal = 0.0;         // Saldo um 17:00 NY
long     kDayIdx = -1;               // laufender Prop-Tag
int      kMode = 0;                  // 0 handeln | 1 reif, keine Einstiege | 2 flach und reif: Auszahlung beantragen
datetime kLastRecalc = 0, kLastReminder = 0, kFlatSince = 0;
double   kRuleFloatPct = 1.0;
double   kMinProfit = 125.0;
datetime letzteNotbremse = 0;
bool     reifGemeldet = false, kStartWarnung = false;

// ---- Deal-Puffer (Historie) ----
struct DealRec
  {
   datetime time;
   int      type;      // DEAL_TYPE_*
   int      entry;     // DEAL_ENTRY_*
   long     posid;
   long     magic;
   string   sym;
   double   volume, price, profit, swap, comm, fee;
   string   cmt;       // 6.10: Kommentar (Auszahlungs-Kennung)
   bool     pay;       // 6.10: als Auszahlung eingestuft
  };
DealRec  D[];
int      nD = 0;

// ---- 4.90: Betriebssicherheit und GFT-Regeln ----
bool     kBereit = false;            // Kontodaten (Verbindung, Saldo, Historie) liegen vor
uint     kWarteMs = 0;               // Beginn des Wartens auf die Historie (GetTickCount)
bool     histOk = false;             // 6.10: Deal-Historie erklaert den Saldo (Summe aller Buchungen = Saldo)
long     kLogin = 0;                 // 6.10: Konto, fuer das der Zustand gilt
bool     kAuszahlungHeute = false;   // 6.10: heute wurde ausgezahlt (keine Einstiege bis 17:00 NY)
bool     tagesRefUnsicher = false;   // 6.10: Tagesreferenz ohne Kurse nicht bestimmbar (keine Einstiege bis 17:00 NY)
double   kTodayRealSchaetz = -DBL_MAX; // 6.10: Schaetzung nach eigener Ernte, bis die Deals da sind (nicht fuer die Reife)
datetime kSchaetzZeit = 0;
bool     kVollHistorie = false;      // 6.10: Einzahlung ausserhalb des Fensters - ganze Historie laden
bool     kFloorOvWarn = false, kCreditWarn = false;
datetime kKeinePayGemeldet = 0, kEaStart = 0;
datetime kPayoutVerarbeitet = 0;     // 6.10: letzte Auszahlung, fuer die Zyklus und Boden schon neu gesetzt sind
bool     kPeakVorlaeufig = false;    // 6.10: Spitze aus einer Historie, die den Saldo nicht erklaerte (wird ersetzt, sobald sie stimmt)
int      refFehl = 0;                // 6.10: Fehlversuche der Tagesreferenz seit 17:00 NY
datetime refVersuch = 0;
double   kEqMaxZyklus = 0.0;         // 6.10: hoechste selbst gesehene Equity seit Start bzw. seit der letzten verarbeiteten Auszahlung
double   kBalRecalc = 0.0, kPosSigRecalc = -1.0;   // 6.10: Saldo und Positionen beim letzten Neuberechnen
int      nDgut = 0;                  // Deal-Zahl des letzten guten Ladens
datetime histKleinSeit = 0;          // seit wann liefert die Historie weniger Deals als zuvor
bool     kBuchWarn = false, kGebWarn = false;
bool     gHandelOk = true;           // Handel erlaubt (Terminal, EA, Konto, Verbindung)
datetime gHandelWarn = 0, gVerbWegSeit = 0;
uint     bremseNextMs = 0;           // naechster erlaubter Versuch der inneren Bremsen (GetTickCount)
int      bremseFehl = 0;
datetime bremseLog = 0;
uint     notbremseMs = 0;            // letzter Schliessversuch der Notbremse (GetTickCount)
double   kDayRefPlus = 0.0;          // Buchgewinn (Equity - Saldo, >= 0) beim Tageswechsel 17:00 NY
long     kRefTag = -1;               // Prop-Tag, fuer den kDayRefPlus gilt
datetime kBereitAb = 0;              // Serverzeit, ab der die Kontodaten vorlagen
long     weSdTag[]; double weSdStd[];// Sondertage: NY-Kalendertag, Schlussstunde NY
datetime nyOffChk = 0; int nyOffKand = 0, nyOffKandN = 0;
bool     weNachladen = false;        // Vormerkungen/Signal-Gedaechtnis mit gueltiger Serverzeit erneut laden
int      ordDir[MAXSYM];             // letzte eigene Einstiegsorder je Symbol (die Positionsliste kann nachhinken)
uint     ordMs[MAXSYM];
datetime newsT[]; int nNews = 0; datetime newsGeladen = 0; bool newsWarn = false;
datetime inaktivWarn = 0;
double   peakGespeichert = 0.0; datetime peakPayGesp = -1, peakSpeicherZeit = 0;
bool     peakOk = true; datetime peakVersuch = 0; int peakFehl = 0;
datetime hedgeLog[MAXSLOT];
// ---- 5.00: NAS-Noise-Modul ----
bool     nzOk = false;               // Modul angelegt (Symbol in der Liste, Hedging-Konto, Eingaben gueltig)
string   nzSym = "";
double   nzStops[8]; int nzN = 0;    // Stops der Teilpositionen (Tages-Sigma)
datetime nzLastM1 = 0, nzLastSeen0 = 0;
long     nzDay = -1;                 // NY-Kalendertag der Noise-Statistik
bool     nzDayOk = false, nzHaveO = false, nzStatsOk = false, nzReplay = false, nzExitPending = false, nzSperreTag = false;
double   nzO = 0.0, nzPC = 0.0, nzSd = 0.0;   // Eroeffnung 9:30, Vortagesschluss, Tages-Sigma
double   nzSig[390];                 // uebliche Bewegung je NY-Minute ab 9:30 (Index = Minute - 570), < 0 = unbekannt
double   nzHistCR[78], nzTodCR[78];  // kumulierte 5-min-RV je Block: Mittel der letzten NzTage Tage / heute (< 0 = unbekannt)
double   nzTodPrev5 = 0.0, nzTodAcc5 = 0.0;
datetime nzStatsNext = 0, nzSchliessVersuch = 0, nzReifeVersuch = 0;
long     nzFrei[]; int nNzFrei = 0;  // handelsfreie NY-Tage
int      nzSigHeute = 0, nzEinHeute = 0;
string   nzLetzte = "";
// ---- 5.10: Serien-Stopp, Swap-Vorsorge ----
int      serN = 0;                   // Verlusttrades in Folge seit dem letzten Serien-Stopp (aus der Deal-Historie)
datetime serStoppZeit = 0;           // Schliesszeit des Trades, der den letzten Serien-Stopp ausgeloest hat
datetime serGemeldet = 0;            // zuletzt gemeldeter Serien-Stopp
int      serNDeals = -1;             // Deal-Zahl der letzten Auswertung (Cache)
datetime serLetzt = 0;
datetime swapLog = 0;                // letzte Meldung der Swap-Vorsorge

//+------------------------------------------------------------------+
//| Zeit: Prop-Tag = 17:00 NY bis 17:00 NY                            |
//+------------------------------------------------------------------+
long PropDayIndex(datetime t)
  {
   // 17:00 NY = 00:00 des Prop-Tages. Serverzeit - (nyOff-7) h verschiebt 17:00 NY auf Mitternacht.
   return (long)MathFloor((double)(t - (nyOff - 7) * 3600) / 86400.0);
  }
datetime PropDayStart(long idx) { return (datetime)(idx * 86400 + (nyOff - 7) * 3600); }
double NYHour(datetime t)
  {
   MqlDateTime st; TimeToStruct(t - nyOff * 3600, st);
   return st.hour + st.min / 60.0;
  }
// 4.30: Wochentag und Kalendertag in NY-Zeit (0 = Sonntag ... 5 = Freitag, 6 = Samstag)
int  NYWeekday(datetime t) { MqlDateTime st; TimeToStruct(t - nyOff * 3600, st); return st.day_of_week; }
long NYDayIndex(datetime t) { return (long)MathFloor((double)(t - nyOff * 3600) / 86400.0); }

// US-Sommerzeit: zweiter Sonntag im Maerz 2:00 bis erster Sonntag im November 2:00 (Ortszeit)
bool UsDst(datetime gmt)
  {
   MqlDateTime st; TimeToStruct(gmt, st);
   int y = st.year;
   // zweiter Sonntag im Maerz
   MqlDateTime m; m.year = y; m.mon = 3; m.day = 1; m.hour = 0; m.min = 0; m.sec = 0;
   datetime mar1 = StructToTime(m); TimeToStruct(mar1, m);
   int dowMar1 = m.day_of_week;                       // 0 = Sonntag
   int secondSun = 1 + ((7 - dowMar1) % 7) + 7;
   MqlDateTime n; n.year = y; n.mon = 11; n.day = 1; n.hour = 0; n.min = 0; n.sec = 0;
   datetime nov1 = StructToTime(n); TimeToStruct(nov1, n);
   int firstSun = 1 + ((7 - n.day_of_week) % 7);
   m.day = secondSun; m.hour = 7;                     // 2:00 EST = 7:00 GMT
   datetime dstStart = StructToTime(m);
   n.day = firstSun; n.hour = 6;                      // 2:00 EDT = 6:00 GMT
   datetime dstEnd = StructToTime(n);
   return (gmt >= dstStart && gmt < dstEnd);
  }

int AutoOffset()
  {
   // Im Tester ist TimeGMT() gleich der simulierten Serverzeit - dort gilt der Input.
   if(MQLInfoInteger(MQL_TESTER)) return NYOffsetHours;
   if(!TerminalInfoInteger(TERMINAL_CONNECTED)) return (nyOff > 0 ? nyOff : NYOffsetHours);   // 4.90: ohne Verbindung ist die Serverzeit nur PC-Zeit
   datetime gmt = TimeGMT(), srv = TimeTradeServer();
   if(gmt <= 0 || srv <= 0) return NYOffsetHours;
   int srvOff = (int)MathRound((double)(srv - gmt) / 3600.0);
   int nyGmt  = UsDst(gmt) ? -4 : -5;
   int off = srvOff - nyGmt;
   if(off < 6 || off > 8)
     {
      PrintFormat("DEADBAND4: automatischer NY-Versatz %d unplausibel (Server %+d h GMT), Rueckfall auf %d", off, srvOff, NYOffsetHours);
      return NYOffsetHours;
     }
   return off;
  }

//+------------------------------------------------------------------+
int OnInit()
  {
   string parts[], rparts[], cparts[], tparts[], sparts[], wparts[];
   nSym = StringSplit(SymbolList, StringGetCharacter(",",0), parts);
   if(nSym<1 || nSym>MAXSYM) { Print("DEADBAND4: Symbolliste ungueltig"); return(INIT_FAILED); }
   int nr = StringSplit(RiskPctList, StringGetCharacter(",",0), rparts);
   int nc = StringSplit(ClsMinList , StringGetCharacter(",",0), cparts);
   int nt = StringSplit(TpFinalList, StringGetCharacter(",",0), tparts);
   int ns = StringSplit(AllowShortList, StringGetCharacter(",",0), sparts);
   int nw = StringSplit(WeSpreadMaxList, StringGetCharacter(",",0), wparts);
   if(nr!=nSym || nc!=nSym || nt!=nSym || ns!=nSym || nw!=nSym)
     { Print("DEADBAND4: RiskPctList/ClsMinList/TpFinalList/AllowShortList/WeSpreadMaxList brauchen genau einen Wert je Symbol"); return(INIT_FAILED); }
   if(WeAktiv && (WeSchlussNY < 13.0 || WeSchlussNY >= 17.0)) { Print("DEADBAND4: WeSchlussNY muss zwischen 13 und 17 (NY) liegen"); return(INIT_FAILED); }
   if(DDFullPct > 0.0 && DDMinPct >= DDFullPct) { Print("DEADBAND4: DDMinPct muss unter DDFullPct liegen"); return(INIT_FAILED); }

   if(VpsSperre && !MQLInfoInteger(MQL_TESTER) && TerminalInfoInteger(TERMINAL_VPS))
     {
      Print("DEADBAND4: START VERWEIGERT - das Terminal laeuft auf einem VPS. GFT Instant Premium (Kauf ab 12.08.2026) verbietet VPS. VpsSperre=false nur, wenn der Kontotyp VPS erlaubt.");
      return(INIT_FAILED);
     }
   if(!MQLInfoInteger(MQL_TESTER))                                           // 5.10: Start nur auf dem eigenen PC (TERMINAL_VPS erkennt nur den MetaQuotes-VPS)
     {
      string pfad = TerminalInfoString(TERMINAL_DATA_PATH);
      PrintFormat("DEADBAND4: Terminal-Datenpfad %s", pfad);
      if(StringLen(NurAufPcPfad) > 0)
        {
         string a = pfad, b = NurAufPcPfad;
         StringToLower(a); StringToLower(b);
         if(StringFind(a, b) < 0)
           {
            PrintFormat("DEADBAND4: START VERWEIGERT - der Terminal-Datenpfad enthaelt \"%s\" nicht (NurAufPcPfad). GFT Instant Premium: VPS/Server verboten - nur auf dem eigenen PC starten.", NurAufPcPfad);
            return(INIT_FAILED);
           }
        }
     }
   if(SwapVorsorgeMin < 0 || SwapVorsorgeMin > 120) { Print("DEADBAND4: SwapVorsorgeMin muss zwischen 0 und 120 liegen"); return(INIT_FAILED); }
   if(AbschlussLetzte < 0 || SerienStopp < 0 || SerienPauseTage < 0) { Print("DEADBAND4: AbschlussLetzte, SerienStopp und SerienPauseTage duerfen nicht negativ sein"); return(INIT_FAILED); }
   if(FadeT1R < 0.0 || (FadeT1R > 0.0 && (FadeT1Anteil < 0.1 || FadeT1Anteil > 0.9)) || R21EinstandAbR < 0.0 || NzEinstandAbR < 0.0
      || EinstandPlusR < 0.0 || ((R21EinstandAbR > 0.0 || NzEinstandAbR > 0.0) && EinstandPlusR >= MathMin(R21EinstandAbR > 0.0 ? R21EinstandAbR : 99.0, NzEinstandAbR > 0.0 ? NzEinstandAbR : 99.0)))   // 6.30
     { Print("DEADBAND4: 6.30-Eingaben ungueltig (FadeT1R >= 0, FadeT1Anteil 0,1-0,9, R21EinstandAbR/NzEinstandAbR >= 0, 0 <= EinstandPlusR < EinstandAbR)"); return(INIT_PARAMETERS_INCORRECT); }
   if(GueltigSchutzR21BisNY < 0.0 || GueltigSchutzR21BisNY > 24.0)                                       // 6.50
     { Print("DEADBAND4: GueltigSchutzR21BisNY muss zwischen 0 und 24 (NY-Stunde) liegen"); return(INIT_PARAMETERS_INCORRECT); }
   if(FloorOverride > 0.0 && (StringLen(FloorOverrideZeit) < 10 || StringToTime(FloorOverrideZeit) < D'2020.01.01'))   // 6.10: ohne Ablesezeit ginge die Spitze bis zum Neustart verloren
     { Print("DEADBAND4: FloorOverride braucht FloorOverrideZeit = Serverzeit der Ablesung im GFT-Dashboard (\"JJJJ.MM.TT HH:MI\")"); return(INIT_PARAMETERS_INCORRECT); }
   if(FloorOverride > 0.0 && TimeCurrent() > D'2020.01.01' && StringToTime(FloorOverrideZeit) > TimeCurrent() + 3600)
      PrintFormat("DEADBAND4: WARNUNG FloorOverrideZeit %s liegt nach der Serverzeit %s - Serverzeit der Ablesung eintragen (nicht die PC-Zeit)", FloorOverrideZeit, TimeToString(TimeCurrent()));
   if(!WeSonderTageLesen()) { Print("DEADBAND4: WeSonderTage ungueltig (Format \"JJJJ.MM.TT Stunde\", Stunde 9-17, getrennt mit ;)"); return(INIT_FAILED); }
   for(int q=0;q<MAXSYM;q++) { ordDir[q] = 0; ordMs[q] = 0; }
   nyOff = NYOffsetHours;                                                  // 4.90: sicherer Ausgangswert, Messung nur mit Verbindung
   if(AutoNYOffset) nyOff = AutoOffset();
   kRuleFloatPct = KontoAb20260902 ? 1.0 : 1.5;
   double minProfitPay = MinGewinnAuszahlung();                        // 6.40: nie unter der Mindestauszahlung

   for(int k=0;k<nSym;k++)
     {
      string s = parts[k];
      StringTrimLeft(s); StringTrimRight(s);
      if(!SymbolSelect(s, true)) { PrintFormat("DEADBAND4: Symbol %s nicht verfuegbar", s); return(INIT_FAILED); }
      S[k].sym   = s;
      S[k].magic = MagicBase + k;
      S[k].hEma  = iMA (s, PERIOD_D1, EmaLen, 0, MODE_EMA, PRICE_CLOSE);
      S[k].hRsi  = iRSI(s, PERIOD_M15, RsiLen, PRICE_CLOSE);
      S[k].hAtr  = iATR(s, PERIOD_M15, AtrLen);
      S[k].hSto  = iStochastic(s, PERIOD_M15, StochK, StochD, StochSlow, MODE_SMA, STO_LOWHIGH);
      S[k].hMacd = iMACD(s, PERIOD_M15, MacdFast, MacdSlow, MacdSignal, PRICE_CLOSE);
      if(S[k].hEma==INVALID_HANDLE || S[k].hRsi==INVALID_HANDLE || S[k].hAtr==INVALID_HANDLE
         || S[k].hSto==INVALID_HANDLE || S[k].hMacd==INVALID_HANDLE)
        { PrintFormat("DEADBAND4: Indikator-Handle fuer %s fehlgeschlagen", s); return(INIT_FAILED); }
      S[k].pt = SymbolInfoDouble(s, SYMBOL_POINT);
      S[k].riskPct = StringToDouble(rparts[k]);
      S[k].clsMin  = StringToDouble(cparts[k]);
      S[k].tpF     = StringToDouble(tparts[k]);
      S[k].allowShort = (StringToInteger(sparts[k]) != 0);
      S[k].weSpreadMax = StringToDouble(wparts[k]);
      S[k].refPx = 0.0;
      S[k].r21 = false; S[k].zweit = false; S[k].partner = -1; S[k].basis = k; S[k].istGold = false; S[k].rr = 0.0; S[k].entryTime = 0; S[k].tfMin = 0;
      W[k].aktiv = false; W[k].lastTry = 0;
      if(S[k].riskPct<=0.0 || S[k].clsMin<=0.0 || S[k].tpF<=0.0)
        { PrintFormat("DEADBAND4: ungueltige Risk/Cls/TpFinal-Werte fuer %s", s); return(INIT_FAILED); }
      S[k].lastBar=0; S[k].curDay=0; S[k].tradesToday=0; S[k].closeFails=0;
      S[k].lastCloseTry=0; S[k].t1Done=false; S[k].t2Done=false; S[k].beDone=false; S[k].lastBeTry=0; S[k].lastHarvTry=0;
      S[k].vol0=0; S[k].vol1=0; S[k].vol2=0; S[k].entryBarTime=0; S[k].mfeR=0.0;
      S[k].posTk = 0; hedgeLog[k] = 0; S[k].r21Be = true;
      TdLaden(k);                                                          // 4.90: Tageszaehler ueberlebt einen Neustart
      { datetime b0 = iTime(s, PERIOD_M15, 0); if(b0 > 0 && TimeCurrent() - b0 >= 20) S[k].lastBar = b0; }   // 4.90: kein verspaeteter Einstieg nach Neustart
      UebernehmePosition(k);
      if(WeAktiv && WeAufnahme) WeLaden(k);
     }

   // 4.40: RSI21-Plaetze anlegen
   nSlot = nSym;
   if(!R21PlaetzeAnlegen() && R21Aktiv) return(INIT_FAILED);          // 4.90: Plaetze immer anlegen (Verwaltung), Schalter nur fuer Einstiege
   if(!NzAnlegen() && NzAktiv) return(INIT_FAILED);                   // 5.00: Noise-Modul (Symbol fehlt/kein Hedging-Konto -> Modul aus)
   if(!FadeAnlegen() && FadeAktiv) return(INIT_FAILED);               // 6.00: Fade-Module (Historie des Waechters wird im Durchlauf geladen)
   GueltigSchutzFreiPruefen();                                          // 6.50: Namen in GueltigSchutzFrei, Regime-Schalter

   ResetKontoZustand(); kEaStart = TimeCurrent();                      // 6.10: kein Zustand aus einem frueheren Konto/Lauf
   kBereit = KontoStart();                                              // 4.90: nur mit Verbindung und Historie
   if(kBereit) NachKontoStart();
   else Print("DEADBAND4: Kontodaten noch nicht verfuegbar (Verbindung/Historie) - keine Einstiege, bis sie geladen sind");
   kMinProfit = MathMax(minProfitPay, kStart * MinProfitPct / 100.0);

   for(int k=0;k<nSym;k++)
     {
      double stp = SymbolInfoDouble(S[k].sym, SYMBOL_VOLUME_STEP);
      double mnv = SymbolInfoDouble(S[k].sym, SYMBOL_VOLUME_MIN);
      PrintFormat("DEADBAND4: %s | Magic %d | Risiko %.3f%% x%.2f | ClsMin %.2f | Endziel %.1f R | Shorts %s | Lot min %.2f step %.2f | %.2f $/Lot | Kommission %.2f/Lot",
                  S[k].sym, (int)S[k].magic, S[k].riskPct, RiskMult, S[k].clsMin, S[k].tpF, (S[k].allowShort ? "ja" : "NEIN"),
                  mnv, stp, MoneyPerPricePerLot(S[k].sym), KommissionJeLot(S[k].sym));
     }
   PrintFormat("DEADBAND4: NY-Versatz %d h (%s) | Floating-Regel %.2f %% | Mindestgewinn fuer Auszahlung %.2f $ | Puffer-Kurve voll ab %.1f %%, %.2f bei %.1f %% | Netting %s",
               nyOff, (AutoNYOffset ? "automatisch" : "Input"), kRuleFloatPct, kMinProfit, DDFullPct, DDMinFactor, DDMinPct,
               (AccountInfoInteger(ACCOUNT_MARGIN_MODE)==ACCOUNT_MARGIN_MODE_RETAIL_HEDGING ? "nein (Hedging)" : "ja"));
   PrintFormat("DEADBAND4: Gewinn-Ernte %s | Rueckgang >= %.2f R | Vorlauf >= %.2f R | Ziel Start + Mindestgewinn x %.2f | Fenster %.0f-%.0f NY",
               (GeAktiv ? "AN" : "aus"), GeRueckgangR, GeMinR, 1.0+GeAufschlag, GeAbNY, GeBisNY);
   PrintFormat("DEADBAND4: Wochenend-Pause %s | Freitag ab %s NY schliessen | Wiederaufnahme %s ab %s NY (Sonntag), auch bei Reife %s | Stop max %.1f R | Lots ans Budget %s",
               (WeAktiv ? "AN" : "aus"), NYStundeText(WeSchlussNY), (WeAufnahme ? "AN" : "aus"), NYStundeText(WeAufnahmeAbNY),
               (WeAufnahmeReif ? "ja" : "nein"), WeStopMaxR, (WeGroesseBudget ? "ja" : "nein"));
   if(R21Aktiv)
      PrintFormat("DEADBAND4: RSI21-Modul %s | Risiko %.2f %% x Gewicht (M15 %.2f, M30 %.2f, H1 %.2f), Gold x%.2f | Budget RSI21 %.2f %%, DEADBAND %.2f %%, gesamt %.2f %% | Stop %.1f ATR, Ziel NAS %.2f R / Gold %.2f R | Zeit-Exit %d M5 oder %d Tage | bei Reife schliessen %s",
                  (nSlot > nSym ? "AN" : "AUS (Symbole fehlen)"), R21RiskPct, r21w[0], r21w[1], r21w[2], R21GoldMult, R21BudgetPct, RiskBudgetPct, GesamtBudgetPct,
                  R21StopATR, R21NasRR, R21GoldRR, R21ExitBarsM5, R21ExitTage, (R21ReifeSchliessen ? "ja" : "nein"));
   PrintFormat("DEADBAND4: 4.90 GFT-Schutz: Hedging-Sperre %s | News +-%d min (%s) | Gewinnschluss ab %d s | Einstiegsstopp %d min vor Schluss | Margin je Idee %.0f %% | Sondertage %d | VPS-Sperre %s | Tagesreferenz %s | RSI21 bei Reife Modus %d",
               (HedgeSperre ? "AN" : "aus"), NewsSperreMin, (MQLInfoInteger(MQL_TESTER) ? "im Tester ohne Kalender" : "Kalender"), MinHalteSek, SchlussVorlaufMin,
               MaxIdeeMarginPct, ArraySize(weSdTag), (VpsSperre ? "an" : "aus"), (TagesRefEquity ? "max(Saldo, Equity)" : "Saldo"), R21ReifeModus);
   PrintFormat("DEADBAND4: 4.80 Risiko DEADBAND x%.2f | RSI21 %.2f %% je Trade (Voreinstellung 6.00: x0.90 / 0.50 %%) | DEADBAND-Einstiege %s", RiskMult, R21RiskPct, (DbAktiv ? "AN" : "AUS (6.00)"));
   PrintFormat("DEADBAND4: 5.10 Regelschutz: Floating-Bremse/Notbremse auf %s | Swap-Vorsorge %s | Risiko je Idee %s | Tagesregel-Notbremse auf min(Startsaldo, Tagesreferenz) | PC-Pfad-Sperre %s",
               (FloatNurVerlierer ? "Summe der VERLIERER" : "netto (Gewinner verrechnet)"),
               (SwapVorsorgePct > 0.0 && SwapVorsorgeMin > 0 ? StringFormat("-%.2f %% in den %d min vor dem Rollover", SwapVorsorgePct, SwapVorsorgeMin) : "aus"),
               (IdeeMaxRisikoPct > 0.0 ? StringFormat("%.2f %%", IdeeMaxRisikoPct) : "aus"), (StringLen(NurAufPcPfad) > 0 ? "\"" + NurAufPcPfad + "\"" : "aus"));
   PrintFormat("DEADBAND4: 5.10 Auszahlungstakt: DEADBAND Teilverkauf %.0f %% bei %.2f R, Stop auf +%.2f R | Abschluss-Ernte %s | Gewinn-Ernte Rueckgang %.2f R | Serien-Stopp %s | Noise %.2f %%",
               Tp1F*100.0, Tp1R, BeAfterT1R,
               (AbschlussLetzte > 0 ? StringFormat("ab %d fehlenden gueltigen Tagen, Vorlauf >= %.2f R, %s-%s NY, Module%s%s%s%s", AbschlussLetzte, AbschlussMinR, NYStundeText(AbschlussAbNY), NYStundeText(AbschlussBisNY),
                                                    ((AbschlussModule & 1) != 0 ? " DEADBAND" : ""), ((AbschlussModule & 2) != 0 ? " RSI21" : ""), ((AbschlussModule & 4) != 0 ? " Noise" : ""), ((AbschlussModule & 8) != 0 ? " Fades" : "")) : "aus"),
               GeRueckgangR, (SerienStopp > 0 ? StringFormat("nach %d Verlusten in Folge bis 17:00 NY%s", SerienStopp, (SerienPauseTage > 0 ? StringFormat(" + %d Tag(e)", SerienPauseTage) : "")) : "aus"), NzRiskPct);
   NzInitMeldung();                                                     // 5.00
   FadeInitMeldung();                                                   // 6.00
   PrintFormat("DEADBAND4: 6.40 Auszahlungstakt | Mindestgewinn %.2f $ (MinProfitPct %.2f %%) | Abschluss-Ernte %s | Schutz gueltiger Tage %s | Fade-Waechter %s | Pufferkurve voll ab %.1f %%, x%.2f bei <= %.1f %% Puffer | Noise %.2f %%",
               kMinProfit, MinProfitPct, (AbschlussLetzte >= NeedValidDays ? "immer" : (AbschlussLetzte > 0 ? StringFormat("ab %d fehlenden Tagen", AbschlussLetzte) : "aus")),
               (GueltigSchutz ? "AN (6.50: " + GueltigSchutzUmfang() + ")" : "aus"),
               (FadeWaechterModus == 1 ? StringFormat("Portfolio PF > %.2f aus %d", FadePortPF, FadePortN) : StringFormat("je Modul PF > %.2f aus %d", FadeWaechterPF, FadeWaechterN)),
               DDFullPct, DDMinFactor, DDMinPct, NzRiskPct);
   PrintFormat("DEADBAND4: 6.30 Trefferquote | Fade-Teilgewinn %s | Einstand RSI21 %s, Noise %s (neuer Stop Einstieg + %.2f R) | erst ab der M5-Kerze nach der Einstiegskerze und nach %d s",
               (FadeT1R > 0.0 ? StringFormat("%.0f %% ab %.2f R (Stop und Ziel bleiben)", FadeT1Anteil*100.0, FadeT1R) : "aus"),
               (R21EinstandAbR > 0.0 ? StringFormat("ab %.2f R", R21EinstandAbR) : "aus"), (NzEinstandAbR > 0.0 ? StringFormat("ab %.2f R je Teil", NzEinstandAbR) : "aus"),
               EinstandPlusR, MinHalteSek);
   PrintFormat("DEADBAND4: 4.70 Floating-Bremse %.2f %% auf %s (jetzt %.2f, Firmengrenze %.2f)",
               FloatStopPct, (FloatBasisMinSaldo ? "min(Startsaldo, Saldo)" : "Startsaldo"), -FloatBasis()*FloatStopPct/100.0, -FloatBasis()*kRuleFloatPct/100.0);
   if(R21Aktiv)
      PrintFormat("DEADBAND4: 4.60 RSI21 Folgesignal %s | zweiter Platz %s (%d RSI21-Plaetze) | Floating-Bremse %s",
                  (R21FolgeMin > 0 ? StringFormat("AN (frueheres Signal hoechstens %d min alt)", R21FolgeMin) : "aus"),
                  (R21ZweiterPlatz ? "AN" : "aus"), nSlot - nSym, (FloatGestuft ? "gestuft (groesster Verlierer zuerst)" : "alles schliessen"));
   if(kBereit) KontoMeldung("beim Laden");                             // 6.10: erst mit Kontodaten
   EventSetTimer(1);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   Comment("");
   for(int k=0;k<nSym;k++)
     { IndicatorRelease(S[k].hEma); IndicatorRelease(S[k].hRsi); IndicatorRelease(S[k].hAtr);
       IndicatorRelease(S[k].hSto); IndicatorRelease(S[k].hMacd); }
   for(int k=nSym;k<nSlot;k++)
     {
      for(int t=0;t<3;t++) { IndicatorRelease(S[k].hR21Rsi[t]); IndicatorRelease(S[k].hR21Atr[t]); }
      IndicatorRelease(S[k].hMaLang); IndicatorRelease(S[k].hMaSchnell);
     }
   FadeFreigeben();                                                     // 6.00
  }

//+------------------------------------------------------------------+
//| Laufende eigene Position nach Neustart uebernehmen (wie 3.00)     |
//+------------------------------------------------------------------+
void UebernehmePosition(int k)
  {
   ulong tk=0;
   if(!(HavePosition(k,tk) && PositionSelectByTicket(tk))) return;
   S[k].posTk = (ulong)PositionGetInteger(POSITION_IDENTIFIER);            // 4.90: Kennung der Position (bleibt bei Swap-Neueroeffnung gleich)
   string s = S[k].sym;
   if(S[k].r21)
     {
      // 4.40: RSI21-Position - Stop und Ziel liegen beim Broker; Bezug, R und Eroeffnung rekonstruieren
      S[k].entryPx   = PositionGetDouble(POSITION_PRICE_OPEN);
      S[k].slPx      = PositionGetDouble(POSITION_SL);
      S[k].rDist     = (S[k].slPx > 0.0 ? MathAbs(S[k].entryPx - S[k].slPx) : 0.0);
      S[k].entryTime = (datetime)PositionGetInteger(POSITION_TIME);
      S[k].entryBarTime = S[k].entryTime;
      S[k].refPx = S[k].entryPx; S[k].mfeR = 0.0; S[k].t1Done = true; S[k].beDone = true; S[k].vol1 = 0.0; S[k].vol2 = 0.0;
      {                                                                      // 6.30: Stop schon auf Einstand -> R aus der Eroeffnungs-Order
       int dd = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1);
       bool imPlus = (S[k].slPx > 0.0 && (S[k].slPx - S[k].entryPx)*dd >= 0.0);
       if(imPlus) { double ur = UrStopAbstand(tk); if(ur > 0.0) S[k].rDist = ur; }
       S[k].r21Be = imPlus || (R21EinstandAbR <= 0.0);
       PositionSelectByTicket(tk);
      }
      string ga = WeGvName(k, "A_");
      if(GlobalVariableCheck(ga + "ticket") && (ulong)GlobalVariableGet(ga + "ticket") == tk)
        {
         S[k].r21Be = true;                                                 // 6.30: wiederaufgenommene Position: kein Einstand
         S[k].refPx = GlobalVariableGet(ga + "ref");
         double rd1 = GlobalVariableGet(ga + "rd"); if(rd1 > 0.0) S[k].rDist = rd1;
         S[k].mfeR = GlobalVariableGet(ga + "mfe");
         datetime e1 = (datetime)GlobalVariableGet(ga + "bar"); if(e1 > 0) { S[k].entryTime = e1; S[k].entryBarTime = e1; }
        }
      if(S[k].mfeR <= 0.0 && S[k].rDist > 0.0)                              // 6.10: Vorlauf aus den M5-Kerzen seit dem Einstieg (Abschluss-Ernte)
        {
         MqlRates r[];
         int n = CopyRates(s, PERIOD_M5, S[k].entryTime, TimeCurrent(), r);
         double pt = SymbolInfoDouble(s, SYMBOL_POINT);
         bool lang = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
         for(int j=0;j<n;j++)
           {
            double f = lang ? (r[j].high - S[k].refPx) : (S[k].refPx - (r[j].low + r[j].spread*pt));
            if(f/S[k].rDist > S[k].mfeR) S[k].mfeR = f/S[k].rDist;
           }
        }
      PrintFormat("DEADBAND4: offene RSI21-Position auf %s uebernommen (R %.5f, eroeffnet %s, Vorlauf %.2f R)", s, S[k].rDist, TimeToString(S[k].entryTime), S[k].mfeR);
      return;
     }
   S[k].entryPx = PositionGetDouble(POSITION_PRICE_OPEN);
   S[k].slPx    = PositionGetDouble(POSITION_SL);
   S[k].rDist   = MathAbs(S[k].entryPx - S[k].slPx);
   double v     = PositionGetDouble(POSITION_VOLUME);
   double stp   = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP);
   S[k].vol1 = MathFloor(v*Tp1F/stp)*stp;
   S[k].vol2 = MathFloor(v*(Tp1F+Tp2F)/stp)*stp - S[k].vol1;
   S[k].entryBarTime = (datetime)PositionGetInteger(POSITION_TIME);
   long ptype = PositionGetInteger(POSITION_TYPE);
   bool slImPlus = (ptype==POSITION_TYPE_BUY) ? (S[k].slPx >= S[k].entryPx) : (S[k].slPx <= S[k].entryPx);
   double ptp = PositionGetDouble(POSITION_TP);
   if(slImPlus || S[k].slPx<=0.0)
     {
      S[k].t1Done=true; S[k].beDone=slImPlus; S[k].vol1=0.0;
      S[k].rDist = (ptp>0.0 && S[k].tpF>0.0) ? MathAbs(ptp - S[k].entryPx)/S[k].tpF : 0.0;
     }
   else if(ptp>0.0 && S[k].tpF>0.0)
     {
      double rTp = MathAbs(ptp - S[k].entryPx)/S[k].tpF;
      double px  = (ptype==POSITION_TYPE_BUY) ? SymbolInfoDouble(s, SYMBOL_BID) : SymbolInfoDouble(s, SYMBOL_ASK);
      bool jenseits = (ptype==POSITION_TYPE_BUY) ? (px >= S[k].entryPx + Tp1R*rTp) : (px <= S[k].entryPx - Tp1R*rTp);
      if(jenseits) { S[k].t1Done=true; S[k].vol1=0.0; }
     }
   if(S[k].rDist<=0.0) PrintFormat("DEADBAND4: %s - R-Abstand nicht rekonstruierbar, Position wird nur vom Server-Stop/TP verwaltet", s);
   // 5.10: Teilverkauf schon erfolgt (Ausstiegs-Deal dieser Position in der Historie) -> Tranche 1 erledigt, kein zweiter Teilverkauf
   if(!S[k].t1Done && S[k].vol1 > 0.0 && HistorySelectByPosition(PositionGetInteger(POSITION_IDENTIFIER)))
     {
      for(int i=HistoryDealsTotal()-1;i>=0;i--)
        {
         ulong dt = HistoryDealGetTicket(i);
         if(dt > 0 && HistoryDealGetInteger(dt, DEAL_ENTRY) == DEAL_ENTRY_OUT) { S[k].t1Done = true; S[k].vol1 = 0.0; break; }
        }
     }
   S[k].mfeR = S[k].t1Done ? Tp1R : 0.0;
   S[k].refPx = S[k].entryPx;
   // 4.30: nach einer Wiederaufnahme gilt der alte Bezugskurs weiter (aus den Globalvariablen)
   string g = WeGvName(k, "A_");
   if(GlobalVariableCheck(g + "ticket") && (ulong)GlobalVariableGet(g + "ticket") == tk)
     {
      S[k].refPx = GlobalVariableGet(g + "ref");
      double rd0 = GlobalVariableGet(g + "rd"); if(rd0 > 0.0) S[k].rDist = rd0;
      S[k].mfeR = MathMax(S[k].mfeR, GlobalVariableGet(g + "mfe"));
      S[k].t1Done = S[k].t1Done || (GlobalVariableGet(g + "t1") > 0.5);
      S[k].beDone = S[k].beDone || (GlobalVariableGet(g + "be") > 0.5);
      S[k].vol1 = 0.0; S[k].vol2 = 0.0;                                     // 5.10: wie nach der Wiederaufnahme ohne Neustart (kein Teilverkauf)
      datetime eb = (datetime)GlobalVariableGet(g + "bar"); if(eb > 0) S[k].entryBarTime = eb;
      PrintFormat("DEADBAND4: %s - wiederaufgenommene Position erkannt, Bezugskurs %.*f, R %.*f, Einstiegskerze %s",
                  s, _Digits, S[k].refPx, _Digits, S[k].rDist, TimeToString(S[k].entryBarTime));
     }
   PrintFormat("DEADBAND4: offene Position auf %s uebernommen (Tranche1 %s, Stop-Nachzug %s)", s,
               (S[k].t1Done ? "erledigt" : "offen"), (S[k].beDone ? "erledigt" : "offen"));
  }

//+------------------------------------------------------------------+
//| Hilfsfunktionen                                                   |
//+------------------------------------------------------------------+
double ContractSize(string s) { return SymbolInfoDouble(s, SYMBOL_TRADE_CONTRACT_SIZE); }

double MoneyPerPricePerLot(string s)
  {
   double ts = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_SIZE);
   double tv = SymbolInfoDouble(s, SYMBOL_TRADE_TICK_VALUE);
   if(ts>0.0 && tv>0.0) { double m = tv/ts; if(m>0.0) return m; }
   double cs = ContractSize(s);
   return (cs>0.0 ? cs : 1.0);
  }

// Kommission je Lot aus der Historie schaetzen (Einstiegs-Deals dieses Symbols)
double KommissionJeLot(string s)
  {
   double c=0.0, v=0.0;
   for(int i=0;i<nD;i++)
      if(D[i].sym==s && D[i].entry==DEAL_ENTRY_IN && D[i].volume>0.0) { c += -D[i].comm; v += D[i].volume; }
   return (v>0.0 ? c/v : 0.0);
  }

// 5.10: Kommission je Lot aus der Historie, je Symbol zwischengespeichert (Floating-Regel wird je Tick geprueft)
double   komCache[MAXSYM];
datetime komZeit = 0, komRundZeit = 0;     // 6.10: Kommissions-Caches (0 = neu rechnen)
double KomJeLotCache(const string s)
  {
   int si = SymIndex(s);
   if(si < 0) return 0.0;                                                     // fremdes Symbol: unbekannt
   if(komZeit == 0 || TimeCurrent() - komZeit >= 300)
     {
      komZeit = TimeCurrent();
      for(int i=0;i<nSym;i++) komCache[i] = KommissionJeLot(S[i].sym);
     }
   return komCache[si];
  }

double NormLot(string s, double lots)
  {
   double stp = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP);
   double mnv = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN);
   double mxv = SymbolInfoDouble(s, SYMBOL_VOLUME_MAX);
   if(stp<=0.0) stp=0.01;
   double v = MathFloor(lots/stp+0.5)*stp;
   v = MathMax(mnv, MathMin(mxv, v));
   return NormalizeDouble(v, 2);
  }

//+------------------------------------------------------------------+
//| 4.90 Hilfsfunktionen: Schliessen mit der Magic der Position,      |
//| Hedging-Sperre, Margin je Idee, 2-Minuten- und News-Regel,        |
//| Sondertage, Bereitschaft, Waechter, gesicherte Zustaende          |
//+------------------------------------------------------------------+
string KontoGv(string was) { return "DEADBAND4_" + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN)) + "_" + was; }

// Schliess-Order mit der Magic der Position -> der OUT-Deal traegt die richtige Magic (Verlustzaehler je Platz)
bool Schliesse(const ulong tk)
  {
   if(!PositionSelectByTicket(tk)) return false;
   trade.SetExpertMagicNumber((ulong)PositionGetInteger(POSITION_MAGIC));
   return trade.PositionClose(tk);
  }
bool SchliesseTeil(const ulong tk, const double lots)
  {
   if(!PositionSelectByTicket(tk)) return false;
   trade.SetExpertMagicNumber((ulong)PositionGetInteger(POSITION_MAGIC));
   return trade.PositionClosePartial(tk, lots);
  }

int SymIndex(const string sym) { for(int i=0;i<nSym;i++) if(S[i].sym==sym) return i; return -1; }
void OrderMerken(const string sym, const int dir) { int si = SymIndex(sym); if(si>=0) { ordDir[si] = dir; ordMs[si] = GetTickCount(); } }

// Richtung aller offenen Positionen im Symbol (kontoweit, auch fremde): 0 keine, +1 nur long, -1 nur short, 2 beide.
// Vorgemerkte Wiederaufnahmen anderer Plaetze und eigene Einstiegsorders der letzten 10 s zaehlen mit.
int SymbolRichtung(const string sym, const int ohneSlot)
  {
   bool l=false, sh=false;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk=PositionGetTicket(i); if(tk==0) continue;
      if(PositionGetString(POSITION_SYMBOL)!=sym) continue;
      if(PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY) l=true; else sh=true;
     }
   if(WeAktiv)
      for(int j=0;j<nSlot;j++)
        {
         if(j==ohneSlot || !W[j].aktiv || S[j].sym!=sym) continue;
         if(W[j].dir>0) l=true; else if(W[j].dir<0) sh=true;
        }
   int si = SymIndex(sym);
   if(si>=0 && ordDir[si]!=0 && !MQLInfoInteger(MQL_TESTER) && GetTickCount()-ordMs[si] < 10000)
     { if(ordDir[si]>0) l=true; else sh=true; }
   if(l && sh) return 2;
   return (l ? 1 : (sh ? -1 : 0));
  }

// true = Einstieg in Richtung dir erlaubt (keine Gegenposition im Symbol; GFT: Hedging auch im selben Konto verboten)
bool HedgeFrei(const int k, const int dir)
  {
   if(!HedgeSperre) return true;
   int r = SymbolRichtung(S[k].sym, k);
   if(r==0 || r==dir) return true;
   if(TimeCurrent()-hedgeLog[k] >= 900)
     {
      hedgeLog[k] = TimeCurrent();
      PrintFormat("DEADBAND4 %s%s: %s-Signal ausgelassen - Gegenposition im Symbol offen oder vorgemerkt (GFT: Hedging verboten)",
                  S[k].sym, (S[k].r21 ? " RSI21" : ""), (dir>0 ? "LONG" : "SHORT"));
     }
   return false;
  }

// Margin: neue Order hoechstens 80 % der freien Margin, Idee (Symbol + Richtung) hoechstens MaxIdeeMarginPct % der Equity
bool MarginOk(const string sym, const int dir, const double vol, const double px, string &grund)
  {
   double mNeu = 0.0;
   if(!OrderCalcMargin(dir>0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, sym, vol, px, mNeu) || mNeu <= 0.0) return true;   // ohne Ergebnis wie 4.80
   double frei = AccountInfoDouble(ACCOUNT_MARGIN_FREE), eq = AccountInfoDouble(ACCOUNT_EQUITY);
   if(mNeu > frei*0.8) { grund = StringFormat("Margin %.2f > 80 %% der freien Margin %.2f", mNeu, frei); return false; }
   if(MaxIdeeMarginPct > 0.0 && eq > 0.0)
     {
      double idee = mNeu;
      for(int i=PositionsTotal()-1;i>=0;i--)
        {
         ulong tk=PositionGetTicket(i); if(tk==0) continue;
         if(PositionGetString(POSITION_SYMBOL)!=sym) continue;
         int d = (PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY ? 1 : -1);
         if(d!=dir) continue;
         double m=0.0;
         if(OrderCalcMargin(d>0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, sym, PositionGetDouble(POSITION_VOLUME), PositionGetDouble(POSITION_PRICE_OPEN), m)) idee += m;
        }
      if(idee > eq*MaxIdeeMarginPct/100.0) { grund = StringFormat("Margin der Idee %.2f > %.0f %% der Equity %.2f", idee, MaxIdeeMarginPct, eq); return false; }
     }
   return true;
  }

// Wirtschaftskalender: rote USD-Termine der naechsten 36 h (nur live, der Tester hat keinen Kalender)
void NewsLaden()
  {
   if(NewsSperreMin <= 0 || MQLInfoInteger(MQL_TESTER)) return;
   datetime jetzt = TimeTradeServer();
   if(jetzt <= 0 || (newsGeladen > 0 && jetzt - newsGeladen < 1800)) return;
   newsGeladen = jetzt;
   MqlCalendarValue v[];
   int n = CalendarValueHistory(v, jetzt - 3600, jetzt + 36*3600, NULL, "USD");
   if(n <= 0)
     {
      if(!newsWarn) { newsWarn = true; PrintFormat("DEADBAND4: Wirtschaftskalender nicht verfuegbar (Fehler %d) - News-Sperre wirkt, sobald er geladen ist", GetLastError()); }
      newsGeladen = jetzt - 1800 + 120;                                  // in 2 min erneut
      return;
     }
   ArrayResize(newsT, 0); nNews = 0;
   for(int i=0;i<n;i++)
     {
      MqlCalendarEvent e;
      if(!CalendarEventById(v[i].event_id, e)) continue;
      if(e.importance != CALENDAR_IMPORTANCE_HIGH) continue;
      ArrayResize(newsT, nNews+1); newsT[nNews++] = v[i].time;
     }
   newsWarn = false;
  }
bool NewsFenster(const datetime t)
  {
   if(NewsSperreMin <= 0 || MQLInfoInteger(MQL_TESTER)) return false;
   for(int i=0;i<nNews;i++) if(MathAbs((double)(t - newsT[i])) <= NewsSperreMin*60.0) return true;
   return false;
  }
string NewsText()
  {
   if(NewsSperreMin <= 0) return "News-Sperre aus";
   if(MQLInfoInteger(MQL_TESTER)) return "News-Sperre (nur live)";
   if(newsWarn) return "Kalender FEHLT";
   datetime nxt = 0, jetzt = TimeCurrent();
   for(int i=0;i<nNews;i++) if(newsT[i] >= jetzt - NewsSperreMin*60 && (nxt == 0 || newsT[i] < nxt)) nxt = newsT[i];
   if(nxt == 0) return "keine roten USD-Termine in 36 h";
   return StringFormat("naechster roter USD-Termin %s%s", TimeToString(nxt, TIME_DATE|TIME_MINUTES), (NewsFenster(jetzt) ? " - SPERRE AKTIV" : ""));
  }

// GFT: Gewinne aus Trades unter 120 s werden gestrichen, Gewinne ueber 1 % im News-Fenster gekappt.
// true = eine EIGENE Gewinnschliessung dieser Position ist jetzt unbedenklich (Verluste und Schutzschliessungen immer erlaubt).
bool GewinnSchlussOk(const ulong tk, const double p)
  {
   if(p <= 0.0) return true;
   if(!PositionSelectByTicket(tk)) return false;
   if(MinHalteSek > 0 && TimeCurrent() - (datetime)PositionGetInteger(POSITION_TIME) < MinHalteSek) return false;
   if(p > kStart*0.01 && NewsFenster(TimeCurrent())) return false;
   return true;
  }

// Sondertage (frueher Schluss, Feiertag am Folgetag): wie ein Freitag behandeln
bool WeSonderTageLesen()
  {
   ArrayResize(weSdTag,0); ArrayResize(weSdStd,0);
   string teile[]; int n = StringSplit(WeSonderTage, StringGetCharacter(";",0), teile);
   for(int i=0;i<n;i++)
     {
      string e = teile[i]; StringTrimLeft(e); StringTrimRight(e);
      if(StringLen(e)==0) continue;
      string p[]; if(StringSplit(e, StringGetCharacter(" ",0), p) != 2) return false;
      datetime d = StringToTime(p[0]); double h = StringToDouble(p[1]);
      if(d <= 0 || h < 9.0 || h >= 17.0) return false;
      int m = ArraySize(weSdTag); ArrayResize(weSdTag,m+1); ArrayResize(weSdStd,m+1);
      weSdTag[m] = (long)MathFloor((double)d/86400.0); weSdStd[m] = h;
     }
   return true;
  }
// Schlussstunde (NY) des NY-Kalendertags von t: Sondertag -> dessen Stunde, Freitag -> WeSchlussNY, sonst -1
double WeSchlussStunde(const datetime t)
  {
   long idx = NYDayIndex(t);
   for(int i=0;i<ArraySize(weSdTag);i++) if(weSdTag[i]==idx) return weSdStd[i];
   return (NYWeekday(t)==5 ? WeSchlussNY : -1.0);
  }
bool WeSchlussJetzt(const datetime t) { double h = WeSchlussStunde(t); return (h > 0.0 && NYHour(t) >= h); }
bool KurzVorSchluss(const datetime t) { double h = WeSchlussStunde(t); return (h > 0.0 && NYHour(t) >= h - SchlussVorlaufMin/60.0); }

// Handel erlaubt? Sonst Push (Bremsen und Wochenend-Pause koennten nicht schliessen)
string HandelSperrGrund()
  {
   string g = "";
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED)) g += "Algo-Trading im Terminal AUS; ";
   if(!MQLInfoInteger(MQL_TRADE_ALLOWED))           g += "EA darf nicht handeln (Eigenschaften); ";
   if(!AccountInfoInteger(ACCOUNT_TRADE_EXPERT))    g += "Server sperrt EA-Handel; ";
   if(!AccountInfoInteger(ACCOUNT_TRADE_ALLOWED))   g += "Konto handelsgesperrt (Investor-Login?); ";
   if(!TerminalInfoInteger(TERMINAL_CONNECTED))
     {
      if(gVerbWegSeit == 0) gVerbWegSeit = TimeLocal();
      if(TimeLocal() - gVerbWegSeit >= 120) g += "keine Serververbindung seit 2 min; ";
     }
   else gVerbWegSeit = 0;
   return g;
  }
void HandelWaechter()
  {
   if(MQLInfoInteger(MQL_TESTER)) return;
   string g = HandelSperrGrund();
   bool ok = (g == "");
   if(!ok && (gHandelOk || TimeLocal() - gHandelWarn >= 1800))
     {
      gHandelWarn = TimeLocal();
      int offen = 0;
      for(int i=PositionsTotal()-1;i>=0;i--) { ulong tk=PositionGetTicket(i); if(tk!=0 && IsOurMagic(PositionGetInteger(POSITION_MAGIC))) offen++; }
      Meldung(StringFormat("WARNUNG HANDEL BLOCKIERT: %s%d eigene Positionen offen - Bremsen und Wochenend-Pause koennen nicht schliessen!", g, offen));
     }
   if(ok && !gHandelOk) Meldung("Handel wieder moeglich");
   gHandelOk = ok;
  }

// Innere Bremsen: gedrosselte Wiederholung, Push nach wiederholtem Scheitern
bool BremseDarf()
  {
   if(MQLInfoInteger(MQL_TESTER) || bremseNextMs == 0) return true;
   return ((int)(GetTickCount() - bremseNextMs) >= 0);
  }
void BremseErgebnis(const int fehl, const string grund)
  {
   if(fehl <= 0) { bremseFehl = 0; bremseNextMs = 0; return; }
   if(!MQLInfoInteger(MQL_TESTER) && (!TerminalInfoInteger(TERMINAL_CONNECTED) || trade.ResultRetcode() == TRADE_RETCODE_MARKET_CLOSED))
     { bremseNextMs = GetTickCount() + 1000; if(bremseNextMs == 0) bremseNextMs = 1; return; }
   bremseFehl++;
   uint warte = (bremseFehl < 5 ? 300 : (bremseFehl < 20 ? 2000 : (bremseFehl < 40 ? 15000 : 60000)));
   bremseNextMs = GetTickCount() + warte; if(bremseNextMs == 0) bremseNextMs = 1;
   if(bremseFehl == 5 || bremseFehl % 100 == 0)
      Meldung(StringFormat("SCHLIESSEN SCHEITERT WIEDERHOLT (%s, Code %d %s) - bitte pruefen und ggf. von Hand schliessen", grund, trade.ResultRetcode(), trade.ResultRetcodeDescription()));
  }

// Kontodaten vorhanden? (Kaltstart vor Login liefert Saldo 0, Serverzeit 0, leere Historie)
bool KontoDatenDa()
  {
   if(MQLInfoInteger(MQL_TESTER)) return true;
   if(!TerminalInfoInteger(TERMINAL_CONNECTED)) return false;
   if(AccountInfoDouble(ACCOUNT_BALANCE) <= 0.0) return false;
   if(TimeCurrent() < D'2020.01.01') return false;
   return true;
  }
// Kontozustand erstmals aufbauen; false = noch nicht moeglich (Durchlauf versucht es erneut)
bool KontoStart()
  {
   if(!KontoDatenDa()) { kWarteMs = 0; return false; }                    // 6.10: Wartezeit zaehlt erst mit Verbindung
   bool ok = LadeDeals(0);
   if(!ok && !MQLInfoInteger(MQL_TESTER))
     {
      if(kWarteMs == 0) kWarteMs = GetTickCount();
      if(GetTickCount() - kWarteMs < 120000) return false;               // bis 2 min auf die Historie warten
      static uint leerGemeldet = 0;
      if(leerGemeldet != kWarteMs) { leerGemeldet = kWarteMs; Print("DEADBAND4: Deal-Historie nach 2 min noch leer - Rueckfall auf den Saldo (StartBalanceOverride pruefen!)"); }
     }
   RekonstruiereKonto(false);
   // 6.10: Einzahlung ausserhalb des Fensters -> einmal die ganze Historie laden
   if(ok && !kVollHistorie && kAccountFrom == 0 && StartBalanceOverride <= 0.0 && !MQLInfoInteger(MQL_TESTER))
     {
      kVollHistorie = true; nDgut = 0;
      if(LadeDeals(0)) RekonstruiereKonto(false);
     }
   // 6.10: Kontozustand erst uebernehmen, wenn die Historie den Saldo erklaert (Summe aller Buchungen = Saldo) - sonst fehlen
   // noch Deals (Synchronisation nach dem Start) und Boden, Startsaldo und gueltige Tage waeren falsch. Hoechstens 3 min warten
   // (so lange verwaltet der EA nichts - Stops und Ziele liegen beim Broker).
   histOk = ok && HistorieKonsistent();
   if(!histOk && !MQLInfoInteger(MQL_TESTER))
     {
      if(kWarteMs == 0) kWarteMs = GetTickCount();
      if(GetTickCount() - kWarteMs < 180000)
        {
         static uint hinweis = 0;
         if(hinweis == 0 || GetTickCount() - hinweis > 60000)
           { hinweis = GetTickCount(); Print("DEADBAND4: Deal-Historie erklaert den Saldo noch nicht (Synchronisation) - warte bis 3 min, keine Einstiege"); }
         return false;
        }
      Meldung(StringFormat("Deal-Historie erklaert den Saldo nicht (Saldo %.2f) - Start mit gesicherter Equity-Spitze. Startsaldo, gueltige Tage und Boden mit dem GFT-Dashboard vergleichen (ggf. StartBalanceOverride/FloorOverride)",
              AccountInfoDouble(ACCOUNT_BALANCE)));
     }
   RekonstruiereKonto(true);
   if(!histOk && !MQLInfoInteger(MQL_TESTER)) { kPeakVorlaeufig = true; peakOk = false; }   // vorlaeufig: kleinere Groesse, voll neu, sobald die Historie stimmt
   kLogin = AccountInfoInteger(ACCOUNT_LOGIN);
   kPayoutVerarbeitet = kLastPayout;                                       // diese Auszahlung ist mit dem Start verarbeitet
   if(AccountInfoDouble(ACCOUNT_CREDIT) != 0.0 && !kCreditWarn)
     { kCreditWarn = true; PrintFormat("DEADBAND4: Konto hat Kredit %.2f - die Equity enthaelt ihn, GFT-Grenzen evtl. anders berechnet", AccountInfoDouble(ACCOUNT_CREDIT)); }
   return (kStart > 0.0);
  }


// Equity-Spitze je Konto sichern (ein Neustart darf den Boden nicht senken)
void PeakSichern(const bool sofort)
  {
   if(MQLInfoInteger(MQL_TESTER) || !kBereit || !histOk) return;         // 6.10: unvollstaendige Historie ueberschreibt nichts
   if(kLastPayout != kPayoutVerarbeitet || kPeakVorlaeufig) return;        // 6.10: Spitze gehoert noch zum alten Zyklus / ist vorlaeufig
   bool neu = (kPeakEq > peakGespeichert + 0.5) || (kLastPayout != peakPayGesp) || (TimeCurrent() - peakSpeicherZeit >= 86400);   // 6.10: taeglich auffrischen (Terminal loescht alte Variablen)
   if(!neu) return;
   if(!sofort && kLastPayout == peakPayGesp && TimeCurrent() - peakSpeicherZeit < 10) return;
   GlobalVariableSet(KontoGv("PEAK"), kPeakEq); GlobalVariableSet(KontoGv("PEAKPAY"), (double)kLastPayout);
   GlobalVariablesFlush();
   peakGespeichert = kPeakEq; peakPayGesp = kLastPayout; peakSpeicherZeit = TimeCurrent();
  }

// Tagesreferenz: Buchgewinn zum Tageswechsel 17:00 NY merken (Lesart "balance or equity" -> der hoehere Wert)
void TagesRefSetzen(const long tag, const double plus, const bool unsicher)
  {
   kDayRefPlus = MathMax(0.0, plus);
   if(MQLInfoInteger(MQL_TESTER)) return;
   GlobalVariableSet(KontoGv("DAYIDX"), (double)tag); GlobalVariableSet(KontoGv("DAYPLUS"), unsicher ? -1.0 : kDayRefPlus);   // -1 = unbekannt (Sperre ueberlebt einen Neustart)
   GlobalVariableSet(KontoGv("DAYPLUSV"), kDayRefPlus);                    // auch vorlaeufig (Tagesbremse vor dem Laden)
   GlobalVariableSet(KontoGv("DAYBAL"), kDayStartBal); GlobalVariableSet(KontoGv("START"), kStart);   // 6.10: Tagesbremse auch vor dem Laden der Kontodaten
   GlobalVariablesFlush();
   if(kDayRefPlus > 0.0) PrintFormat("DEADBAND4: Tagesreferenz 17:00 NY = Saldo + Buchgewinn %.2f (vorsichtige Lesart der Tagesverlust-Regel)", kDayRefPlus);
  }
void TagesRefLaden()
  {
   kDayRefPlus = 0.0; kRefTag = kDayIdx; tagesRefUnsicher = false;
   if(MQLInfoInteger(MQL_TESTER)) return;
   double gv = -1.0, gvV = 0.0;                                            // -1 = kein gesicherter Wert fuer heute (oder als unbekannt gesichert)
   if(GlobalVariableCheck(KontoGv("DAYIDX")) && (long)GlobalVariableGet(KontoGv("DAYIDX")) == kDayIdx)
     {
      gv = GlobalVariableGet(KontoGv("DAYPLUS"));
      if(GlobalVariableCheck(KontoGv("DAYPLUSV"))) gvV = MathMax(0.0, GlobalVariableGet(KontoGv("DAYPLUSV")));   // vorlaeufiger Wert
     }
   // 6.10: obere Schranke des Buchgewinns um 17:00 NY aus Deals und Kursen (falls der EA zum Tageswechsel nicht lief oder zu spaet)
   double f = 0.0;
   bool ok = BuchObergrenzeZu(PropDayStart(kDayIdx), f);
   tagesRefUnsicher = (gv < 0.0 && !ok);
   // bekannter Wert: nur mit sicheren Kursen erhoehen; unsicher: vorlaeufig der Wert aus den vorhandenen Kursen (die Bremsen
   // messen nicht vom blossen Saldo), Einstiege gesperrt
   TagesRefSetzen(kDayIdx, (gv >= 0.0 ? MathMax(gv, ok ? f : 0.0) : MathMax(gvV, f)), tagesRefUnsicher);
   refFehl = 0; refVersuch = TimeCurrent();
   if(tagesRefUnsicher) PrintFormat("DEADBAND4: Tagesreferenz 17:00 NY noch nicht sicher bestimmbar (Kurse werden geladen) - vorlaeufig Buchgewinn %.2f, keine neuen Einstiege, neuer Versuch jede Minute", kDayRefPlus);
  }

// 6.10: obere Schranke des Buchergebnisses aller gezaehlten Positionen zum Zeitpunkt tb (Serverzeit): Volumen offen vor tb, bester
// Kurs der M1-Kerzen der letzten 2 Minuten vor tb (sonst der letzten M5-Kerze); Short zum Bid-Tief. false = Kurse fehlen.
bool BuchObergrenzeZu(const datetime tb, double &f)
  {
   f = 0.0;
   long ids[]; double vol[], px[]; int dir[]; string sy[]; int np = 0;
   for(int i=0;i<nD;i++)
     {
      if(!IstHandel(i) || !ZaehltDeal(i) || D[i].time >= tb) continue;
      int j=-1; for(int q=0;q<np;q++) if(ids[q]==D[i].posid) { j=q; break; }
      if(D[i].entry == DEAL_ENTRY_IN)
        {
         if(j < 0)
           {
            ArrayResize(ids,np+1); ArrayResize(vol,np+1); ArrayResize(px,np+1); ArrayResize(dir,np+1); ArrayResize(sy,np+1);
            ids[np] = D[i].posid; vol[np] = 0.0; px[np] = D[i].price; dir[np] = (D[i].type==DEAL_TYPE_BUY ? 1 : -1); sy[np] = D[i].sym; j = np; np++;
           }
         else px[j] = (px[j]*vol[j] + D[i].price*D[i].volume)/MathMax(vol[j] + D[i].volume, 1e-9);
         vol[j] += D[i].volume;
        }
      else if(j >= 0) vol[j] -= D[i].volume;
     }
   bool alle = true;
   for(int q=0;q<np;q++)
     {
      if(vol[q] <= 1e-9) continue;
      MqlRates r[];
      int n = CopyRates(sy[q], PERIOD_M1, tb - 120, tb - 1, r);
      bool imFenster = (n > 0);                                            // Kerzen der 2 min vor tb (nie veraltet)
      if(n <= 0)
        {
         int sh = iBarShift(sy[q], PERIOD_M5, tb - 1, false);
         n = (sh >= 0 ? CopyRates(sy[q], PERIOD_M5, sh, 1, r) : 0);
        }
      // 6.10: nicht synchrone Historie kann eine Luecke vor tb haben (iBarShift liefert dann eine Stunden alte Kerze) ->
      //       Ergebnis nur vorlaeufig, spaeter erneut; vorlaeufig zaehlen nur Kerzen aus dem Fenster
      if(!MQLInfoInteger(MQL_TESTER) && (!SeriesInfoInteger(sy[q], PERIOD_M1, SERIES_SYNCHRONIZED) || !SeriesInfoInteger(sy[q], PERIOD_M5, SERIES_SYNCHRONIZED)))
        { alle = false; if(!imFenster) continue; }
      if(n <= 0) { alle = false; continue; }
      double best = -DBL_MAX;
      for(int k=0;k<n;k++) best = MathMax(best, dir[q] > 0 ? r[k].high - px[q] : px[q] - r[k].low);
      f += best*vol[q]*MoneyPerPricePerLot(sy[q]);
     }
   return alle;
  }


// Tageszaehler DEADBAND ueberlebt einen Neustart
string TdGv(const int k, const string was) { return KontoGv("TD_" + IntegerToString(S[k].magic) + "_" + was); }
void TdSichern(const int k)
  {
   if(MQLInfoInteger(MQL_TESTER)) return;
   GlobalVariableSet(TdGv(k,"day"), (double)(long)S[k].curDay); GlobalVariableSet(TdGv(k,"n"), (double)S[k].tradesToday);
   GlobalVariablesFlush();
  }
void TdLaden(const int k)
  {
   if(MQLInfoInteger(MQL_TESTER) || AccountInfoInteger(ACCOUNT_LOGIN) <= 0) return;
   if(!GlobalVariableCheck(TdGv(k,"day")) || !GlobalVariableCheck(TdGv(k,"n"))) return;
   S[k].curDay = (datetime)(long)GlobalVariableGet(TdGv(k,"day"));
   S[k].tradesToday = (int)GlobalVariableGet(TdGv(k,"n"));
  }

// NY-Versatz: je Minute messen, erst nach drei gleichen Messungen mit Verbindung uebernehmen
void NYOffsetWaechter()
  {
   if(!AutoNYOffset || MQLInfoInteger(MQL_TESTER)) return;
   if(TimeLocal() - nyOffChk < 60) return;
   nyOffChk = TimeLocal();
   if(!TerminalInfoInteger(TERMINAL_CONNECTED)) { nyOffKandN = 0; return; }
   int m = AutoOffset();
   if(m == nyOff) { nyOffKandN = 0; return; }
   if(m != nyOffKand) { nyOffKand = m; nyOffKandN = 1; return; }
   if(++nyOffKandN < 3) return;
   Meldung(StringFormat("NY-Versatz %d -> %d h (dreimal gemessen)%s", nyOff, m, (m != NYOffsetHours ? " - bitte pruefen (PC-Uhr, Zeitzone, Broker-Serverzeit)" : "")));
   nyOff = m; nyOffKandN = 0;
  }

// GFT: 30 Tage ohne Trade = Konto weg. Push ab InaktivWarnTage (alle 6 h)
void InaktivWaechter()
  {
   if(InaktivWarnTage <= 0 || MQLInfoInteger(MQL_TESTER)) return;
   if(inaktivWarn > 0 && TimeLocal() - inaktivWarn < 6*3600) return;
   inaktivWarn = TimeLocal();
   datetime letzte = 0;
   for(int i=nD-1;i>=0;i--) if(IstHandel(i) && D[i].entry==DEAL_ENTRY_IN) { letzte = D[i].time; break; }
   if(letzte == 0) letzte = kAccountFrom;
   if(letzte <= 0) return;
   datetime jetzt = (MQLInfoInteger(MQL_TESTER) ? TimeCurrent() : TimeTradeServer());   // 6.10: laeuft auch ohne Kurse (Wochenende) weiter
   double tage = (double)(jetzt - letzte)/86400.0;
   if(tage >= InaktivWarnTage)
      Meldung(StringFormat("INAKTIVITAET: seit %.0f Tagen kein Einstieg (GFT: 30 Tage ohne Trade = Konto weg) - bitte pruefen, ggf. von Hand einen kleinen Trade setzen", tage));
  }

// Positionen, die beim Start noch nicht sichtbar waren oder deren Order-Antwort verloren ging, nachtraeglich uebernehmen
void UebernahmeNachholen()
  {
   for(int k=0;k<nSlot;k++)
     {
      ulong tk=0;
      if(!HavePosition(k,tk) || !PositionSelectByTicket(tk)) continue;       // nicht sichtbar: Zustand behalten (Liste kann nachhinken)
      ulong pid = (ulong)PositionGetInteger(POSITION_IDENTIFIER);
      if(pid == S[k].posTk) continue;
      PrintFormat("DEADBAND4 %s%s: Position #%I64u ohne Platz-Zustand (Start vor der Synchronisation oder Order-Antwort verloren) - wird uebernommen",
                  S[k].sym, (S[k].r21 ? " RSI21" : ""), tk);
      S[k].t1Done=false; S[k].t2Done=false; S[k].beDone=false; S[k].lastBeTry=0; S[k].closeFails=0; S[k].lastCloseTry=0; S[k].mfeR=0.0; S[k].entryTime=0;
      UebernehmePosition(k);
      S[k].posTk = pid;
     }
  }

string SchutzStatusText()
  {
   return StringFormat("Handel %s | Hedging-Sperre %s | %s | Spitze %s | Halten >= %d s",
                       (gHandelOk ? "ok" : "BLOCKIERT"), (HedgeSperre ? "an" : "AUS"), NewsText(), (peakOk ? "ok" : "wird nachgeholt"), MinHalteSek);
  }

bool IsDbMagic(long mg)  { return (mg>=MagicBase && mg<MagicBase+nSym); }
bool IsR21Magic(long mg)                                                                                                // 4.40, 4.50: zweiter Platz
  {
   long o = mg - MagicBase - R21MagicOffset;                                // 4.90: auch bei ausgeschaltetem Modul eigene Position
   return ((o >= 0 && o < nSym) || (o >= MAXSYM && o < MAXSYM + nSym));
  }
bool IsNzMagic(long mg)                                                                                                 // 5.00: Noise-Teilpositionen
  {
   if(NzMagicOffset < R21MagicOffset + 2*MAXSYM) return false;              // ungueltiger Offset: keine Ueberschneidung mit RSI21
   long o = mg - MagicBase - NzMagicOffset;                                 // auch bei ausgeschaltetem Modul eigene Position
   return (o >= 0 && o < 8);
  }
bool IsOurMagic(long mg) { return IsDbMagic(mg) || IsR21Magic(mg) || IsNzMagic(mg) || IsFadeMagic(mg); }   // 6.00: Fade-Module

bool HavePosition(int k, ulong &ticket)
  {
   for(int i=PositionsTotal()-1; i>=0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk==0) continue;
      if(PositionGetString(POSITION_SYMBOL)==S[k].sym && PositionGetInteger(POSITION_MAGIC)==S[k].magic)
        { ticket = tk; return true; }
     }
   return false;
  }

// Buchgewinn: kontoweit (Firmenregeln) oder nur eigene
double FloatingPnl(bool alle)
  {
   double f=0.0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk=PositionGetTicket(i); if(tk==0) continue;
      if(!alle && !IsOurMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      f += PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
     }
   return f;
  }

// 5.10: Buchergebnis der selektierten Position fuer die Floating-Regel. Strenge Lesart (FloatNurVerlierer):
// Gewinn + Swap - Einstiegskommission (GFT: Floating-Verlust inkl. Swap und Kommission), sonst Gewinn + Swap wie 5.00.
double PosBuch()
  {
   double p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
   if(FloatNurVerlierer) p -= KomJeLotCache(PositionGetString(POSITION_SYMBOL))*PositionGetDouble(POSITION_VOLUME);
   return p;
  }

// 5.10: Summe der VERLUSTPOSITIONEN (<= 0). Strenge Lesart der Floating-Regel: Gewinner verrechnen nicht mit Verlierern.
double FloatingVerlierer(bool alle)
  {
   double f=0.0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk=PositionGetTicket(i); if(tk==0) continue;
      if(!alle && !IsOurMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      double p = PosBuch();
      if(p < 0.0) f += p;
     }
   return f;
  }

// 5.10: Buchverlust, auf den Floating-Bremse und Notbremse schauen (FloatNurVerlierer: nur Verlierer, sonst netto)
double FloatingRegel(bool alle) { return FloatNurVerlierer ? FloatingVerlierer(alle) : FloatingPnl(alle); }

// 4.40: Buchgewinn nur der DEADBAND-Positionen (Bedingung der Tagesernte)
double FloatingPnlDb()
  {
   double f=0.0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk=PositionGetTicket(i); if(tk==0) continue;
      if(!IsDbMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      f += PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
     }
   return f;
  }

// 4.90: liefert die Zahl der abgelehnten Schliessungen, loggt jeden Fehler mit Code
int CloseAll(string grund)
  {
   int zu = 0, fehl = 0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk=PositionGetTicket(i); if(tk==0) continue;
      if(!IsOurMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      string sy = PositionGetString(POSITION_SYMBOL);
      if(Schliesse(tk)) zu++;
      else { fehl++; PrintFormat("DEADBAND4: Not-Exit %s #%I64u ABGELEHNT (%d %s)", sy, tk, trade.ResultRetcode(), trade.ResultRetcodeDescription()); }
     }
   if(zu > 0 || fehl > 0 || TimeCurrent() - bremseLog >= 60)
     { bremseLog = TimeCurrent(); PrintFormat("DEADBAND4: Not-Exit - %s (geschlossen %d, abgelehnt %d)", grund, zu, fehl); }
   return fehl;
  }

// 4.70: Basis der Floating-Grenzen. Die Firma misst "of your account balance"; unter dem Startsaldo ist der Saldo die strengere Basis.
double FloatBasis()
  {
   double b = kStart;
   if(FloatBasisMinSaldo)
     {
      double saldo = AccountInfoDouble(ACCOUNT_BALANCE);
      if(saldo > 0.0 && saldo < b) b = saldo;
     }
   return b;
  }

// 4.60: gestufte Floating-Bremse - die eigene Position mit dem groessten Buchverlust zuerst, bis der Buchverlust
// wieder ueber -FloatStopPct liegt. Gibt es keine eigene Verlustposition (nur fremde), wie bisher alles schliessen.
// 5.10: flt ist bei FloatNurVerlierer die Summe der Verlustpositionen; geschlossen werden ohnehin nur Verlierer.
int FloatBremseGestuft(double flt)
  {
   double grenze = -FloatBasis()*FloatStopPct/100.0;
   ulong zu[]; int nzu = 0;
   for(int runde=0; runde<MAXSLOT && flt <= grenze; runde++)
     {
      ulong wTk = 0; double wPl = 0.0; string wSym = "";
      for(int i=PositionsTotal()-1;i>=0;i--)
        {
         ulong tk=PositionGetTicket(i); if(tk==0) continue;
         if(!IsOurMagic(PositionGetInteger(POSITION_MAGIC))) continue;
         bool schon = false;
         for(int j=0;j<nzu;j++) if(zu[j]==tk) { schon = true; break; }
         if(schon) continue;
         double pl = PosBuch();                                             // 5.10: wie in der Summe (strenge Lesart inkl. Kommission)
         if(pl < wPl) { wPl = pl; wTk = tk; wSym = PositionGetString(POSITION_SYMBOL); }
        }
      if(wTk == 0)
        {
         if(nzu == 0) return CloseAll("Buchverlust am Limit (keine eigene Verlustposition)");
         return 0;
        }
      if(!Schliesse(wTk))
        {
         PrintFormat("DEADBAND4: gestufte Bremse - Schliessen %s abgelehnt (%d %s), schliesse alles", wSym, trade.ResultRetcode(), trade.ResultRetcodeDescription());
         return CloseAll("Buchverlust am Limit") + 1;
        }
      ArrayResize(zu, nzu+1); zu[nzu++] = wTk;
      flt -= wPl;
      PrintFormat("DEADBAND4: Not-Exit gestuft - Buchverlust am Limit: %s (%.2f) geschlossen, verbleibender Buchverlust %.2f (Grenze %.2f)", wSym, wPl, flt, grenze);
     }
   return 0;
  }

//+------------------------------------------------------------------+
//| 5.10 Swap-Vorsorge                                                |
//|  Der Swap wird beim Rollover (Mitternacht Serverzeit = 17:00 NY)  |
//|  in einem Schritt gebucht - am Swap-3-Tag dreifach. Liegen die    |
//|  Verlustpositionen kurz davor schon nahe an der Bremse, kann der  |
//|  Swap die Floating-Regel verletzen, ohne dass eine Bremse noch    |
//|  dazwischen greift. In den letzten SwapVorsorgeMin Minuten vor    |
//|  dem Rollover: Summe der Verlierer inkl. erwartetem Swap <=       |
//|  -SwapVorsorgePct % -> groesste Verlierer (inkl. Swap) schliessen,|
//|  bis die Summe wieder darueber liegt.                             |
//+------------------------------------------------------------------+
bool SwapFenster(const datetime t)
  {
   MqlDateTime st; TimeToStruct(t, st);                                       // Serverzeit: Rollover um 00:00
   if(st.day_of_week == 0 || st.day_of_week == 6) return false;
   return (st.hour*60 + st.min >= 1440 - SwapVorsorgeMin);
  }

// Waehrungsbetrag des Symbols grob in die Kontowaehrung (Basis -> Preis, sonst 1:1)
double SwapUmrechnung(const string s, const string waehrung)
  {
   string konto = AccountInfoString(ACCOUNT_CURRENCY);
   if(waehrung == "" || waehrung == konto) return 1.0;
   if(waehrung == SymbolInfoString(s, SYMBOL_CURRENCY_BASE) && SymbolInfoString(s, SYMBOL_CURRENCY_PROFIT) == konto)
     { double px = SymbolInfoDouble(s, SYMBOL_BID); return (px > 0.0 ? px : 1.0); }
   return 1.0;
  }

// erwarteter Swap der selektierten Position beim naechsten Rollover (negativ = Belastung), am Swap-3-Tag dreifach
double SwapErwartet()
  {
   string s = PositionGetString(POSITION_SYMBOL);
   bool lang = (PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY);
   double rate = SymbolInfoDouble(s, lang ? SYMBOL_SWAP_LONG : SYMBOL_SWAP_SHORT);
   double vol  = PositionGetDouble(POSITION_VOLUME);
   double sw = 0.0;
   ENUM_SYMBOL_SWAP_MODE md = (ENUM_SYMBOL_SWAP_MODE)SymbolInfoInteger(s, SYMBOL_SWAP_MODE);
   switch(md)
     {
      case SYMBOL_SWAP_MODE_POINTS:           sw = rate*SymbolInfoDouble(s, SYMBOL_POINT)*MoneyPerPricePerLot(s)*vol; break;
      case SYMBOL_SWAP_MODE_CURRENCY_SYMBOL:  sw = rate*vol*SwapUmrechnung(s, SymbolInfoString(s, SYMBOL_CURRENCY_BASE)); break;
      case SYMBOL_SWAP_MODE_CURRENCY_MARGIN:  sw = rate*vol*SwapUmrechnung(s, SymbolInfoString(s, SYMBOL_CURRENCY_MARGIN)); break;
      case SYMBOL_SWAP_MODE_CURRENCY_DEPOSIT: sw = rate*vol; break;
      case SYMBOL_SWAP_MODE_INTEREST_CURRENT: sw = PositionGetDouble(POSITION_PRICE_CURRENT)*MoneyPerPricePerLot(s)*vol*rate/100.0/360.0; break;
      case SYMBOL_SWAP_MODE_INTEREST_OPEN:    sw = PositionGetDouble(POSITION_PRICE_OPEN)*MoneyPerPricePerLot(s)*vol*rate/100.0/360.0; break;
      default: sw = 0.0;
     }
   MqlDateTime st; TimeToStruct(TimeCurrent(), st);
   if(st.day_of_week == (int)SymbolInfoInteger(s, SYMBOL_SWAP_ROLLOVER3DAYS)) sw *= 3.0;
   return sw;
  }

// -1 = nichts zu tun, sonst Zahl der abgelehnten Schliessungen (0 = alles angenommen)
int SwapVorsorge(const double fBasis)
  {
   double grenze = -fBasis*SwapVorsorgePct/100.0;
   double summe = 0.0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk=PositionGetTicket(i); if(tk==0) continue;
      if(!CountForeignPositions && !IsOurMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      double v = PosBuch()+SwapErwartet();
      if(v < 0.0) summe += v;
     }
   if(summe > grenze) return -1;
   int fehl = 0, zu = 0;
   ulong erledigt[]; int ne = 0;
   for(int runde=0; runde<MAXSLOT+8 && summe <= grenze; runde++)
     {
      ulong wTk = 0; double wV = 0.0; string wSym = "";
      for(int i=PositionsTotal()-1;i>=0;i--)
        {
         ulong tk=PositionGetTicket(i); if(tk==0) continue;
         if(!IsOurMagic(PositionGetInteger(POSITION_MAGIC))) continue;
         bool schon = false;
         for(int j=0;j<ne;j++) if(erledigt[j]==tk) { schon = true; break; }
         if(schon) continue;
         double p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
         double v = PosBuch() + SwapErwartet();
         if(v >= wV) continue;
         if(p > 0.0 && !GewinnSchlussOk(tk, p)) continue;                     // Gewinner nur nach der 2-Minuten-Regel
         wV = v; wTk = tk; wSym = PositionGetString(POSITION_SYMBOL);
        }
      if(wTk == 0) break;                                                    // keine eigene Verlustposition mehr
      ArrayResize(erledigt, ne+1); erledigt[ne++] = wTk;
      if(Schliesse(wTk)) { zu++; summe -= wV; PrintFormat("DEADBAND4: SWAP-VORSORGE - %s (%.2f inkl. erwartetem Swap) vor dem Rollover geschlossen, Verlierer danach %.2f (Grenze %.2f)", wSym, wV, summe, grenze); }
      else { fehl++; PrintFormat("DEADBAND4: Swap-Vorsorge - Schliessen %s abgelehnt (%d %s)", wSym, trade.ResultRetcode(), trade.ResultRetcodeDescription()); }
     }
   if(zu > 0 && TimeCurrent() - swapLog >= 600)
     {
      swapLog = TimeCurrent();
      Meldung(StringFormat("SWAP-VORSORGE: %d Verlustposition(en) vor dem Rollover geschlossen (Verlierer + Swap unter -%.2f %%)", zu, SwapVorsorgePct));
     }
   if(zu == 0 && fehl == 0) return -1;                                       // nur fremde Verlierer: nichts zu schliessen
   return fehl;
  }

// Konto flach? (kontoweit, wenn CountForeignPositions)
bool KontoFlach()
  {
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk=PositionGetTicket(i); if(tk==0) continue;
      if(CountForeignPositions || IsOurMagic(PositionGetInteger(POSITION_MAGIC))) return false;
     }
   for(int i=OrdersTotal()-1;i>=0;i--)
     {
      ulong tk=OrderGetTicket(i); if(tk==0) continue;
      if(CountForeignPositions || IsOurMagic(OrderGetInteger(ORDER_MAGIC))) return false;
     }
   return true;
  }

double SessionVwap(string s)
  {
   MqlRates r[]; ArraySetAsSeries(r, true);
   int n = CopyRates(s, PERIOD_M15, 0, 200, r);
   if(n<=1) return 0.0;
   long d0 = PropDayIndex(r[1].time);
   double pv=0.0, vv=0.0;
   for(int i=1; i<n; i++)
     {
      if(PropDayIndex(r[i].time) != d0) break;
      double tp = (r[i].high+r[i].low+r[i].close)/3.0;
      double v  = (double)r[i].tick_volume;
      pv += tp*v; vv += v;
     }
   return (vv>0.0 ? pv/vv : 0.0);
  }

double VolRel(string s, int len)
  {
   if(len<2) return(1.0);
   long v[]; ArraySetAsSeries(v, true);
   int got = CopyTickVolume(s, PERIOD_M15, 1, len, v);
   if(got < len) return(-1.0);
   double sum=0.0;
   for(int i=0;i<got;i++) sum += (double)v[i];
   if(sum<=0.0) return(-1.0);
   return((double)v[0] / (sum/got));
  }

double AtrPerzentil(int k, int len)
  {
   string s = S[k].sym;
   if(len < 20) return(0.5);
   double a[]; ArraySetAsSeries(a, true);
   double c[]; ArraySetAsSeries(c, true);
   if(CopyBuffer(S[k].hAtr, 0, 1, len, a) < len) return(-1.0);
   if(CopyClose(s, PERIOD_M15, 1, len, c)  < len) return(-1.0);
   if(c[0] <= 0.0) return(-1.0);
   double jetzt = a[0]/c[0];
   int kleiner = 0, gueltig = 0;
   for(int i=0;i<len;i++)
     {
      if(c[i] <= 0.0) continue;
      gueltig++;
      if(a[i]/c[i] < jetzt) kleiner++;
     }
   if(gueltig < 20) return(-1.0);
   return((double)kleiner/(double)gueltig);
  }

// Verluste heute je Symbol (aus dem Deal-Puffer)
int LossesToday(int k, long dayIdx)
  {
   int losses=0;
   for(int i=nD-1;i>=0;i--)
     {
      if(PropDayIndex(D[i].time) < dayIdx) break;
      if(D[i].magic!=S[k].magic || D[i].entry!=DEAL_ENTRY_OUT) continue;
      if(D[i].profit < 0.0) losses++;
     }
   return losses;
  }

// Summe der Verluste, die offene Positionen an ihren Stops noch erleiden koennen.
// Ohne Stop zaehlt der volle Abstand zum Kurs als Mindestannahme (3.00 zaehlte 0).
// 4.40: art 0 = alle gezaehlten Positionen, 1 = ohne RSI21 (DEADBAND-Budget), 2 = ohne DEADBAND (RSI21-Budget)
// 5.00: Noise zaehlt nur in art 0 (Gesamtbudget) und art 3 (nur Noise); 6.00: Fades nur in art 0
double OffenesRisiko(int art=0)
  {
   double r=0.0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk=PositionGetTicket(i); if(tk==0) continue;
      long mg = PositionGetInteger(POSITION_MAGIC);
      if(!CountForeignPositions && !IsOurMagic(mg)) continue;
      if(art==1 && (IsR21Magic(mg) || IsNzMagic(mg) || IsFadeMagic(mg))) continue;
      if(art==2 && (IsDbMagic(mg) || IsNzMagic(mg) || IsFadeMagic(mg))) continue;
      if(art==3 && !IsNzMagic(mg)) continue;
      string ps = PositionGetString(POSITION_SYMBOL);
      double sl = PositionGetDouble(POSITION_SL), op = PositionGetDouble(POSITION_PRICE_OPEN), v = PositionGetDouble(POSITION_VOLUME);
      long   pt = PositionGetInteger(POSITION_TYPE);
      double dist = (sl<=0.0) ? 0.0 : ((pt==POSITION_TYPE_BUY) ? (op-sl) : (sl-op));
      if(sl<=0.0) dist = op * 0.01;          // ohne Stop: 1 % Kursweg als Annahme
      if(dist>0.0) r += v*dist*MoneyPerPricePerLot(ps);
     }
   return r;
  }

// 4.40: freies Risikobudget fuer einen neuen Einstieg (eigenes Budget, gedeckelt durch das Gesamtbudget)
// 5.00: freies Risikobudget fuer eine Noise-Teilposition (eigenes Budget, falls gesetzt, gedeckelt durch das Gesamtbudget)
double BudgetRestNz()
  {
   double rest = (NzBudgetPct > 0.0) ? kStart*NzBudgetPct/100.0 - OffenesRisiko(3) : DBL_MAX;
   if(GesamtBudgetPct > 0.0) rest = MathMin(rest, kStart*GesamtBudgetPct/100.0 - OffenesRisiko(0));
   return rest;
  }

double BudgetRest(bool r21)
  {
   double rest = r21 ? kStart*R21BudgetPct/100.0 - OffenesRisiko(2) : kStart*RiskBudgetPct/100.0 - OffenesRisiko(1);
   if(nSlot > nSym && GesamtBudgetPct > 0.0)
      rest = MathMin(rest, kStart*GesamtBudgetPct/100.0 - OffenesRisiko(0));
   return rest;
  }

// 5.10: offenes Stop-Risiko einer Handelsidee = Symbol + Richtung, ueber alle Module und Plaetze (Zaehlweise wie OffenesRisiko:
// Stop im Plus = 0, ohne Stop 1 % Kursweg). GFT kann ein Risiko je Idee vorschreiben (1 %), mehrere Positionen einer Idee zaehlen zusammen.
double IdeeRisiko(const string sym, const int dir)
  {
   double r=0.0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk=PositionGetTicket(i); if(tk==0) continue;
      if(!CountForeignPositions && !IsOurMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      if(PositionGetString(POSITION_SYMBOL) != sym) continue;
      long pt = PositionGetInteger(POSITION_TYPE);
      if((pt==POSITION_TYPE_BUY ? 1 : -1) != dir) continue;
      double sl = PositionGetDouble(POSITION_SL), op = PositionGetDouble(POSITION_PRICE_OPEN), v = PositionGetDouble(POSITION_VOLUME);
      double dist = (sl<=0.0) ? op*0.01 : ((pt==POSITION_TYPE_BUY) ? (op-sl) : (sl-op));
      if(dist>0.0) r += v*dist*MoneyPerPricePerLot(sym);
     }
   return r;
  }
// freies Risiko der Idee (DBL_MAX = keine Grenze)
double IdeeRest(const string sym, const int dir)
  {
   if(IdeeMaxRisikoPct <= 0.0) return DBL_MAX;
   return kStart*IdeeMaxRisikoPct/100.0 - IdeeRisiko(sym, dir);
  }

//+------------------------------------------------------------------+
//| Deal-Puffer aus der Historie                                      |
//+------------------------------------------------------------------+
// 4.90: false = Historie nicht (plausibel) verfuegbar; D[] und nD bleiben dann unveraendert
bool LadeDeals(datetime von)
  {
   datetime jetzt = TimeCurrent();
   if(jetzt <= 0) return false;
   if(!MQLInfoInteger(MQL_TESTER) && !TerminalInfoInteger(TERMINAL_CONNECTED)) return false;
   datetime lim = kVollHistorie ? 0 : jetzt - (datetime)HistoryDaysMax*86400;   // 6.10: ohne Einzahlung im Fenster die ganze Historie
   if(kAccountFrom > 0 && kAccountFrom < lim) lim = kAccountFrom;          // 6.10: die bekannte Einzahlung bleibt im Fenster (Dauerlauf)
   if(von < lim) von = lim;
   if(!HistorySelect(von, jetzt+86400)) return false;
   int n = HistoryDealsTotal();
   if(n <= 0) return false;                                                // ein Konto mit Saldo hat mindestens den Einzahlungs-Deal
   if(n < nDgut && !MQLInfoInteger(MQL_TESTER))                            // Historie schrumpft nicht; nur am Fensterrand (nach 120 s) akzeptieren
     {
      if(histKleinSeit == 0) histKleinSeit = jetzt;
      if(jetzt - histKleinSeit < 120) return false;
     }
   histKleinSeit = 0;
   nD = 0;
   ArrayResize(D, n);
   for(int i=0;i<n;i++)
     {
      ulong d = HistoryDealGetTicket(i);
      if(d==0) continue;
      D[nD].time   = (datetime)HistoryDealGetInteger(d, DEAL_TIME);
      D[nD].type   = (int)HistoryDealGetInteger(d, DEAL_TYPE);
      D[nD].entry  = (int)HistoryDealGetInteger(d, DEAL_ENTRY);
      D[nD].posid  = HistoryDealGetInteger(d, DEAL_POSITION_ID);
      D[nD].magic  = HistoryDealGetInteger(d, DEAL_MAGIC);
      D[nD].sym    = HistoryDealGetString(d, DEAL_SYMBOL);
      D[nD].volume = HistoryDealGetDouble(d, DEAL_VOLUME);
      D[nD].price  = HistoryDealGetDouble(d, DEAL_PRICE);
      D[nD].profit = HistoryDealGetDouble(d, DEAL_PROFIT);
      D[nD].swap   = HistoryDealGetDouble(d, DEAL_SWAP);
      D[nD].comm   = HistoryDealGetDouble(d, DEAL_COMMISSION);
      D[nD].fee    = HistoryDealGetDouble(d, DEAL_FEE);                      // 6.10: Gebuehren gehoeren zum Saldo
      D[nD].cmt    = HistoryDealGetString(d, DEAL_COMMENT);
      D[nD].pay    = false;
      nD++;
     }
   ArrayResize(D, nD);
   nDgut = n;
   return true;
  }

bool IstHandel(int i) { return (D[i].type==DEAL_TYPE_BUY || D[i].type==DEAL_TYPE_SELL); }
bool ZaehltDeal(int i) { return CountForeignPositions || IsOurMagic(D[i].magic); }
double DealGeld(int i) { return (D[i].type == DEAL_TYPE_CREDIT ? 0.0 : D[i].profit + D[i].swap + D[i].comm + D[i].fee); }   // 6.10: Kredit ist kein Saldo, Gebuehren schon

// 6.10: Hilfen der Kontoerkennung
double GueltigSchwelle() { return kStart*ValidDayPct/100.0 + MathMax(0.0, ValidDayReserveUSD); }
// Ein Einstieg darf einen heute schon gueltigen Tag nicht ungueltig machen: Lesart B bucht die Einstiegskommission am Einstiegstag
bool EinstiegKostetTag(const string sym, const double lots, const string modul)
  {
   static double res = 0.0; static datetime resZeit = 0;                  // Kommission eben erlaubter Einstiege (Deals noch nicht geladen)
   if(TimeCurrent() - resZeit > 10) res = 0.0;
   double schwelle = GueltigSchwelle();
   double heute = MathMax(kTodayReal, kTodayRealSchaetz);
   if(heute < schwelle) return false;
   double kom = KomJeLotCache(sym)*lots;
   if(kom <= 0.0) return false;
   if(heute - res - kom >= schwelle) { res += kom; resZeit = TimeCurrent(); return false; }
   static string gemMod = ""; static datetime gemeldet = 0;
   if(modul != gemMod || TimeCurrent() - gemeldet >= 300)
     { gemMod = modul; gemeldet = TimeCurrent(); PrintFormat("DEADBAND4 %s %s: Einstieg ausgelassen - Kommission %.2f wuerde den heute gueltigen Tag (%.2f, Schwelle %.2f) ungueltig machen", sym, modul, kom + res, heute, schwelle); }
   return true;
  }
bool KennungPasst(string c)
  {
   StringToLower(c);
   string w[]; int n = StringSplit(AuszahlungKennung, StringGetCharacter(";",0), w);
   for(int q=0;q<n;q++) { string x = w[q]; StringTrimLeft(x); StringTrimRight(x); StringToLower(x); if(StringLen(x) > 0 && StringFind(c, x) >= 0) return true; }
   return false;
  }
// Liste "JJJJ.MM.TT HH:MI;..." enthaelt die Minute von t
bool ListeHatZeit(const string liste, const datetime t)
  {
   if(StringLen(liste) == 0) return false;
   string w[]; int n = StringSplit(liste, StringGetCharacter(";",0), w);
   for(int q=0;q<n;q++)
     {
      string x = w[q]; StringTrimLeft(x); StringTrimRight(x);
      if(StringLen(x) < 16) continue;
      datetime z = StringToTime(x);
      if(z > 0 && MathAbs((double)((long)t - (long)z)) < 60.0) return true;
     }
   return false;
  }
// Summe aller Buchungen seit der ersten Einzahlung = Saldo? (sonst fehlen Deals in der lokalen Historie)
bool HistorieKonsistent()
  {
   if(MQLInfoInteger(MQL_TESTER)) return true;
   if(kAccountFrom <= 0) return (kLastPayout > 0 || StartBalanceOverride > 0.0);   // Einzahlung nicht im Fenster: nicht pruefbar
   double sum = 0.0;
   for(int i=0;i<nD;i++) sum += DealGeld(i);
   return (MathAbs(sum - AccountInfoDouble(ACCOUNT_BALANCE)) <= 0.05);
  }
// Auszahlung beantragt und noch nicht gebucht (Eingabe AuszahlungAngefordertAm)
bool AuszahlungAngefordert()
  {
   if(StringLen(AuszahlungAngefordertAm) < 10) return false;
   datetime t = StringToTime(AuszahlungAngefordertAm);
   return (t > 0 && t > kLastPayout);
  }
// Zeitpunkt, ab dem FloorOverride gilt (0 = kein Override)
datetime FloorOverrideZeitWert()
  {
   if(FloorOverride <= 0.0) return 0;
   datetime t = (StringLen(FloorOverrideZeit) >= 10 ? StringToTime(FloorOverrideZeit) : kEaStart);
   return (t > 0 ? t : kEaStart);
  }
// Luft bis zum Boden (mit 0,2 % Reserve): Equity, wenn jede Position an ihrem Stop schliesst (ohne Stop: 1 % Kursweg wie
// OffenesRisiko), minus Boden. Auch Buchgewinne, die bis zum Stop zurueckgegeben werden koennen, zaehlen nicht als Luft.
double BodenLuft()
  {
   double boden = kPeakEq - kStart*MaxLossPct/100.0;
   double worst = AccountInfoDouble(ACCOUNT_EQUITY);
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      if(!CountForeignPositions && !IsOurMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      string ps = PositionGetString(POSITION_SYMBOL);
      int    d  = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1);
      double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL), v = PositionGetDouble(POSITION_VOLUME);
      double mpp = MoneyPerPricePerLot(ps);
      double stopPx = (sl > 0.0 ? sl : op - d*op*0.01);
      double weiter = PositionGetDouble(POSITION_PROFIT) - (stopPx - op)*d*v*mpp;   // was bis zum Stop noch verloren gehen kann
      if(sl <= 0.0) weiter = MathMax(weiter, PositionGetDouble(POSITION_PRICE_CURRENT)*0.01*v*mpp);   // ohne Stop: mind. 1 % ab jetzt
      worst -= MathMax(0.0, weiter);                                        // Stop schon ueberschritten (Luecke): nie Luft gutschreiben
     }
   return worst - boden - kStart*0.002;
  }
// Tagesergebnisse sammeln (zwei Lesarten)
void TagAdd(long &tage[], double &a[], double &b[], int &nt, const long tag, const double va, const double vb)
  {
   int k = -1;
   for(int j=nt-1;j>=0;j--) if(tage[j] == tag) { k = j; break; }
   if(k < 0) { ArrayResize(tage,nt+1); ArrayResize(a,nt+1); ArrayResize(b,nt+1); tage[nt] = tag; a[nt] = 0.0; b[nt] = 0.0; k = nt; nt++; }
   a[k] += va; b[k] += vb;
  }
// Kontozustand zuruecksetzen (Laden, Kontowechsel): MT5 behaelt globale Variablen ueber OnDeinit/OnInit
void ResetKontoZustand()
  {
   nD = 0; ArrayResize(D, 0); nDgut = 0; histKleinSeit = 0; kWarteMs = 0; histOk = false; kVollHistorie = false;
   kStart = 0.0; kPeakEq = 0.0; kAccountFrom = 0; kLastPayout = 0; kPayouts = 0; kCycleStart = 0;
   kValidDays = 0; kTradeDays = 0; kCycleReal = 0.0; kTodayReal = 0.0; kTagN = 0; kTodayRealSchaetz = -DBL_MAX; kSchaetzZeit = 0; kTodayRealTag = -1;
   gGueltigSchutz = false; gGsTag = -1;                                    // 6.40
   kDayIdx = -1; kRefTag = -1; kDayRefPlus = 0.0; kDayStartBal = 0.0; kMode = 0; reifGemeldet = false; kLastReminder = 0; kLastRecalc = 0; kFlatSince = 0;
   peakGespeichert = 0.0; peakPayGesp = -1; peakSpeicherZeit = 0; peakOk = true; peakFehl = 0; peakVersuch = 0;
   serNDeals = -1; serN = 0; serStoppZeit = 0; kBereitAb = 0; kStartWarnung = false; kBuchWarn = false; kGebWarn = false; kLogin = 0;
   kAuszahlungHeute = false; tagesRefUnsicher = false; kFloorOvWarn = false; kCreditWarn = false; kKeinePayGemeldet = 0; kPayoutVerarbeitet = 0; kPeakVorlaeufig = false; refFehl = 0; refVersuch = 0; kEqMaxZyklus = 0.0; kBalRecalc = 0.0; kPosSigRecalc = -1.0;
  }

//+------------------------------------------------------------------+
//| Kontozustand aus dem Deal-Puffer                                  |
//+------------------------------------------------------------------+
void RekonstruiereKonto(bool mitBoden)
  {
   datetime now = TimeCurrent();
   // 1) Einzahlungen und Auszahlungen. 6.10: Buchungen vor dem ersten Trade netto (Einzahlung); danach ist eine Abbuchung ab
   //    PayoutErkennMinUSD nur dann eine Auszahlung, wenn der Saldo danach auf den Startsaldo faellt (bzw. Start + Rest ueber dem
   //    Deckel) oder der Kommentar zu AuszahlungKennung passt. Andere Abbuchungen (gestrichene Gewinne, Korrekturen, Gebuehren)
   //    lassen Zyklus und Boden unberuehrt und zaehlen als Tagesergebnis.
   //    Mehrere Abbuchungen binnen 1 h ohne Handel dazwischen gelten zusammen (Auszahlung in Teilen); AuszahlungZeiten erzwingt
   //    eine Auszahlung (Teilauszahlung), KeineAuszahlung schliesst eine aus.
   double deposits = 0.0; kAccountFrom = 0; kLastPayout = 0; kPayouts = 0;
   bool gehandelt = false;
   bool kennung = (StringLen(AuszahlungKennung) > 0);
   double lauf = 0.0;                                                      // Saldo nach jedem Deal (ab Beginn der geladenen Historie)
   int grpEnde = -1;                                                       // letzte Buchung einer schon bewerteten Gruppe
   for(int i=0;i<nD;i++) D[i].pay = false;
   for(int i=0;i<nD;i++)
     {
      if(IstHandel(i)) { gehandelt = true; lauf += DealGeld(i); continue; }
      if(D[i].type == DEAL_TYPE_CREDIT) continue;
      bool saldo = (D[i].type == DEAL_TYPE_BALANCE);
      if(!gehandelt || MQLInfoInteger(MQL_TESTER))
        {
         if(saldo) { deposits += D[i].profit; if(kAccountFrom == 0 && D[i].profit > 0.0) kAccountFrom = D[i].time; }
         lauf += DealGeld(i);
         continue;
        }
      if(D[i].pay || i <= grpEnde) { lauf += DealGeld(i); continue; }     // weiterer Teil einer schon bewerteten Gruppe (Auszahlung oder nicht)
      bool neg = (D[i].profit < 0.0);
      int bis = i; double summe = D[i].profit;
      if(saldo && neg && !kennung)                                          // Teile binnen 1 h ohne Handel dazwischen
         for(int j=i+1;j<nD;j++)
           {
            if(D[j].time - D[i].time > 3600 || IstHandel(j)) break;
            if(D[j].type == DEAL_TYPE_BALANCE && D[j].profit < 0.0) { bis = j; summe += D[j].profit; }
           }
      bool manuell = false, keine = false;
      if(neg)
         for(int j=i;j<=bis;j++)
           {
            if(ListeHatZeit(AuszahlungZeiten, D[j].time)) manuell = true;
            if(ListeHatZeit(KeineAuszahlung, D[j].time)) keine = true;
           }
      if(neg && (manuell || (summe <= -PayoutErkennMinUSD && (saldo || kennung)) || (kennung && KennungPasst(D[i].cmt))))
        {
         grpEnde = bis;                                                     // KeineAuszahlung auf einem Teil gilt fuer die ganze Gruppe
         double basis  = (StartBalanceOverride > 0.0 ? StartBalanceOverride : deposits);
         double gewinn = lauf - basis;
         double rest   = (kPayouts < PayoutCapCount && PayoutCapPct > 0.0) ? MathMax(0.0, gewinn - basis*PayoutCapPct/100.0) : 0.0;
         double nach   = lauf;                                               // Saldo nach der ganzen Gruppe
         for(int j=i;j<=bis;j++) nach += DealGeld(j);
         double minG   = (ProfitSplit > 0.0 ? MinPayoutUSD/ProfitSplit : MinPayoutUSD) - 1.0;
         bool pay;
         if(manuell) pay = true;
         else if(kennung) pay = KennungPasst(D[i].cmt);
         else if(basis > 0.0 && kAccountFrom > 0)
            pay = saldo && (gewinn >= minG) && (nach <= basis + rest + basis*0.002);
         else pay = saldo;                                                  // Einzahlung ausserhalb der Historie: wie bis 6.00
         if(pay && keine) pay = false;
         if(pay)
           {
            for(int j=i;j<=bis;j++) if(j == i || (D[j].type == DEAL_TYPE_BALANCE && D[j].profit < 0.0)) D[j].pay = true;
            if(kLastPayout == 0 || D[i].time - kLastPayout > 3600) kPayouts++;   // eine Auszahlung in mehreren Buchungen zaehlt einmal
            kLastPayout = D[bis].time;
           }
         else if(D[i].time > kKeinePayGemeldet)
           {
            kKeinePayGemeldet = D[bis].time;
            string txt = StringFormat("Abbuchung %.2f am %s (\"%s\") ist KEINE Auszahlung (Saldo danach %.2f, Startsaldo %.2f) - Zyklus und Boden laufen weiter. War es eine Auszahlung (z. B. Teilauszahlung): AuszahlungZeiten setzen",
                                      summe, TimeToString(D[i].time, TIME_DATE|TIME_MINUTES), D[i].cmt, nach, basis);
            if(kBereitAb > 0 && D[i].time >= kBereitAb - 60) Meldung(txt); else Print("DEADBAND4: ", txt);
           }
        }
      else if(saldo && D[i].profit > 0.0 && !kBuchWarn)
        { kBuchWarn = true; PrintFormat("DEADBAND4: positive Saldo-Buchung %.2f am %s nach Handelsbeginn - zaehlt NICHT als Einzahlung (sonst StartBalanceOverride setzen)", D[i].profit, TimeToString(D[i].time)); }
      else if(saldo && neg && !kGebWarn)
        { kGebWarn = true; PrintFormat("DEADBAND4: kleine Saldo-Abbuchung %.2f am %s als Gebuehr/Korrektur gewertet, nicht als Auszahlung", D[i].profit, TimeToString(D[i].time)); }
      lauf += DealGeld(i);
     }
   kStart = (StartBalanceOverride > 0.0) ? StartBalanceOverride : deposits;
   if(kStart <= 0.0)
     {
      // Kein Einzahlungs-Deal (Konto aelter als die Historie oder Historie noch nicht geladen):
      // Rueckfall = Saldo unmittelbar nach der letzten Auszahlung, sonst Saldo am Anfang des Fensters.
      datetime ab = kLastPayout;
      kStart = AccountInfoDouble(ACCOUNT_BALANCE);
      for(int i=nD-1;i>=0;i--) { if(D[i].time <= ab) break; kStart -= DealGeld(i); }
      if(kStart <= 0.0) kStart = AccountInfoDouble(ACCOUNT_BALANCE);
      if(!kStartWarnung)
        {
         kStartWarnung = true;
         PrintFormat("DEADBAND4: KEINE Einzahlung in der Historie - Startsaldo %.2f aus dem Saldo %s abgeleitet (StartBalanceOverride pruefen!)",
                     kStart, (ab > 0 ? "nach der letzten Auszahlung" : "am Anfang des Historienfensters"));
        }
     }
   kMinProfit = MathMax(MinGewinnAuszahlung(), kStart * MinProfitPct / 100.0);   // 6.40: nie unter der Mindestauszahlung
   // 2) Zyklusbeginn = erster Trade nach der letzten Auszahlung (6.10: CycleStartOverride nur im laufenden Zyklus)
   datetime von = (kLastPayout > 0 ? kLastPayout : kAccountFrom);
   datetime ov = (StringLen(CycleStartOverride) >= 8 ? StringToTime(CycleStartOverride) : 0);
   kCycleStart = 0;
   if(ov > von) kCycleStart = ov;
   else
      for(int i=0;i<nD;i++)
         if(IstHandel(i) && D[i].entry==DEAL_ENTRY_IN && D[i].time > von && ZaehltDeal(i)) { kCycleStart = D[i].time; break; }
   // 3) realisiert je Prop-Tag seit Zyklusbeginn in zwei Lesarten (6.10), gueltig nur, wenn BEIDE die Schwelle + Reserve erreichen:
   //    A) Positionsergebnis am Tag des Ausstiegs, Einstiegskommission beim ersten Ausstieg (bis 6.00)
   //    B) jeder Deal an seinem Tag (Einstiegskommission am Einstiegstag) plus Kommissions-Buchungen
   long today = PropDayIndex(now);
   kValidDays = 0; kTradeDays = 0; kCycleReal = 0.0; kTodayReal = 0.0; kTagN = 0; kTodayRealTag = today;
   if(TimeCurrent() - kSchaetzZeit > 30) kTodayRealSchaetz = -DBL_MAX;   // 6.10: eigene Ernte, deren Deals evtl. noch fehlen
   if(kCycleStart > 0)
     {
      long tage[]; double ergA[], ergB[]; int nt = 0;
      long posIds[]; double posComm[]; int np = 0;
      for(int i=0;i<nD;i++)
        {
         if(D[i].time < von) continue;
         bool handel = IstHandel(i);
         bool kom = (D[i].type == DEAL_TYPE_COMMISSION || D[i].type == DEAL_TYPE_COMMISSION_DAILY || D[i].type == DEAL_TYPE_COMMISSION_MONTHLY);
         if(!handel && !kom)
           {
            // 6.10: Abbuchungen, die keine Auszahlung sind (gestrichene Gewinne, Korrekturen, Gebuehren), mindern den Tag in beiden Lesarten
            if(D[i].type != DEAL_TYPE_CREDIT && !D[i].pay && DealGeld(i) < 0.0 && D[i].time >= kCycleStart)
               TagAdd(tage, ergA, ergB, nt, PropDayIndex(D[i].time), DealGeld(i), DealGeld(i));
            continue;
           }
         if(handel && !ZaehltDeal(i)) continue;
         if(D[i].time >= kCycleStart) TagAdd(tage, ergA, ergB, nt, PropDayIndex(D[i].time), 0.0, DealGeld(i));
         if(!handel) continue;
         if(D[i].entry==DEAL_ENTRY_IN)
           {
            int j=-1; for(int q=0;q<np;q++) if(posIds[q]==D[i].posid) { j=q; break; }
            if(j<0) { ArrayResize(posIds, np+1); ArrayResize(posComm, np+1); posIds[np]=D[i].posid; posComm[np]=0.0; j=np; np++; }
            posComm[j] += D[i].comm + D[i].fee;
            continue;
           }
         if(D[i].time < kCycleStart) continue;
         double p = DealGeld(i);
         for(int q=0;q<np;q++) if(posIds[q]==D[i].posid) { p += posComm[q]; posComm[q]=0.0; break; }
         TagAdd(tage, ergA, ergB, nt, PropDayIndex(D[i].time), p, 0.0);
        }
      double schwelle = GueltigSchwelle();
      ArrayResize(kTagIdx, nt); ArrayResize(kTagErg, nt); kTagN = nt;
      for(int i=0;i<nt;i++)
        {
         double e = MathMin(ergA[i], ergB[i]);
         kTagIdx[i] = tage[i]; kTagErg[i] = e;
         kCycleReal += ergA[i];
         if(tage[i]==today) { kTodayReal = e; continue; }
         kTradeDays++;
         if(e >= schwelle) kValidDays++;
        }
     }
   // 4) Tagesstartsaldo: Saldo minus alles, was seit 17:00 NY gebucht wurde. Auszahlungen und Einzahlungen verschieben die
   //    Bezugsgroesse mit; 6.10: andere Abbuchungen (Korrekturen, Gebuehren) zaehlen wie bei GFT als Tagesverlust.
   double seit = 0.0; kAuszahlungHeute = false;
   for(int i=nD-1;i>=0;i--)
     {
      if(PropDayIndex(D[i].time) < today) break;
      if(D[i].type == DEAL_TYPE_CREDIT) continue;
      if(D[i].pay) { kAuszahlungHeute = true; continue; }
      if(!IstHandel(i) && D[i].profit > 0.0) continue;                     // Gutschrift hebt die Bezugsgroesse (vorsichtig)
      seit += DealGeld(i);
     }
   kDayStartBal = AccountInfoDouble(ACCOUNT_BALANCE) - seit;
   kDayIdx = today;
   // 6.10: gesicherte Bezugsgroesse der Tagesbremse (vor dem Laden der Kontodaten) nach Buchungen im Tag nachziehen
   if(!MQLInfoInteger(MQL_TESTER) && kBereit && kRefTag == today && AccountInfoInteger(ACCOUNT_LOGIN) > 0
      && MathAbs(GlobalVariableGet(KontoGv("DAYBAL")) - kDayStartBal) > 0.005)
     { GlobalVariableSet(KontoGv("DAYBAL"), kDayStartBal); GlobalVariablesFlush(); }
   // 5) Equity-Spitze seit der letzten Auszahlung
   if(mitBoden)
     {
      kPeakEq = PeakRekonstruktion(true);
      kPeakEq = MathMax(kPeakEq, MathMax(AccountInfoDouble(ACCOUNT_BALANCE), AccountInfoDouble(ACCOUNT_EQUITY)));
      // gesicherte Spitze desselben Zyklus (ein Neustart oder fehlende Kurse duerfen den Boden nicht senken);
      // 6.10: solange die Historie den Saldo nicht erklaert, gilt auch die gesicherte Spitze eines spaeteren Zyklus
      // (die Auszahlung fehlt dann noch in der Historie) - nie die eines frueheren
      if(FloorOverrideZeitWert() <= kLastPayout && !MQLInfoInteger(MQL_TESTER) && AccountInfoInteger(ACCOUNT_LOGIN) > 0 && GlobalVariableCheck(KontoGv("PEAK")))
        {
         datetime gvp = (datetime)(long)GlobalVariableGet(KontoGv("PEAKPAY"));
         if(gvp == kLastPayout || (!histOk && gvp > kLastPayout)) kPeakEq = MathMax(kPeakEq, GlobalVariableGet(KontoGv("PEAK")));
        }
     }
   kLastRecalc = now;
   kBalRecalc = AccountInfoDouble(ACCOUNT_BALANCE); kPosSigRecalc = PosSignatur();   // 6.10: Saldo-Spruenge ohne Handel erkennen
   SerienStand();                                                            // 5.10
  }
// 6.10: Kennung der offenen Positionen (Tickets + Volumen, ganzzahlig) - aendert sich bei jedem Oeffnen, Schliessen, Teilschliessen
double PosSignatur()
  {
   double sig = 0.0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      sig += (double)tk + MathRound(PositionGetDouble(POSITION_VOLUME)*1000.0);
     }
   return sig;
  }
// 6.10: Saldo seit dem letzten Neuberechnen ohne Positionsaenderung veraendert (Auszahlung, Abbuchung, Gutschrift)?
bool SaldoSprung()
  {
   return (kLastRecalc > 0 && MathAbs(AccountInfoDouble(ACCOUNT_BALANCE) - kBalRecalc) > 0.005 && MathAbs(PosSignatur() - kPosSigRecalc) < 0.5);
  }

// 6.10: Equity-Spitze aus der Historie; mit FloorOverride (Ablesung nach der letzten Auszahlung) ab dem Ablesezeitpunkt
double PeakRekonstruktion(const bool pruefen)                          // pruefen = fehlende Kurse melden (peakOk = false)
  {
   datetime von = (kLastPayout > 0 ? kLastPayout : kAccountFrom);
   datetime fz = FloorOverrideZeitWert();
   if(FloorOverride > 0.0 && fz > kLastPayout)
      return MathMax(FloorOverride + kStart*MaxLossPct/100.0, RekonstruierePeak(fz, pruefen));
   if(FloorOverride > 0.0 && !kFloorOvWarn)
     { kFloorOvWarn = true; Print("DEADBAND4: FloorOverride gilt nicht mehr (Auszahlung nach der Ablesung) - Boden wieder aus der Historie"); }
   return RekonstruierePeak(von, pruefen) + kStart*PeakSafetyPct/100.0;
  }


//+------------------------------------------------------------------+
//| 5.10 Serien-Stopp                                                 |
//|  Verlusttrades in Folge aus der Deal-Historie (eigene Magics, in  |
//|  der Reihenfolge der Schliessungen). Ein Trade = eine Position    |
//|  mit allen Teilschliessungen, Einstiegs- und Schlusskommission    |
//|  und Swap; die Noise-Teile eines Signals (Einstieg binnen 5 min)  |
//|  zaehlen zusammen als EIN Trade, sobald der letzte Teil zu ist.   |
//|  Eine Wochenend-Schliessung beendet den Trade (die Wieder-        |
//|  aufnahme ist ein neuer). Nach SerienStopp Verlusten in Folge:    |
//|  keine neuen Einstiege bis 17:00 NY (+ SerienPauseTage), Zaehler  |
//|  zurueck auf 0. Wiederaufnahmen nach dem Wochenende laufen        |
//|  weiter. Aus der Historie berechnet -> gleich nach Neustart.      |
//+------------------------------------------------------------------+
void SerienStand()
  {
   if(SerienStopp <= 0) return;
   if(nD == serNDeals && (nD == 0 || D[nD-1].time == serLetzt)) return;    // keine neuen Deals
   serNDeals = nD; serLetzt = (nD > 0 ? D[nD-1].time : 0);
   long ids[]; double sum[], vin[], vout[]; bool nz[]; int grp[]; int np = 0;
   datetime gT[]; int gOffen[]; double gSum[]; int ng = 0;
   int n = 0; datetime stopZeit = 0;
   for(int i=0;i<nD;i++)
     {
      if(!IstHandel(i) || !IsOurMagic(D[i].magic)) continue;
      int j = -1;
      for(int q=np-1;q>=0;q--) if(ids[q]==D[i].posid) { j=q; break; }
      if(D[i].entry==DEAL_ENTRY_IN)
        {
         if(j >= 0) { sum[j] += DealGeld(i); vin[j] += D[i].volume; continue; }
         ArrayResize(ids,np+1); ArrayResize(sum,np+1); ArrayResize(vin,np+1); ArrayResize(vout,np+1); ArrayResize(nz,np+1); ArrayResize(grp,np+1);
         ids[np] = D[i].posid; sum[np] = DealGeld(i); vin[np] = D[i].volume; vout[np] = 0.0; nz[np] = IsNzMagic(D[i].magic); grp[np] = -1;
         if(nz[np])
           {
            if(ng > 0 && D[i].time - gT[ng-1] <= 300) gOffen[ng-1]++;            // Teil desselben Signals
            else { ArrayResize(gT,ng+1); ArrayResize(gOffen,ng+1); ArrayResize(gSum,ng+1); gT[ng] = D[i].time; gOffen[ng] = 1; gSum[ng] = 0.0; ng++; }
            grp[np] = ng-1;
           }
         np++;
         continue;
        }
      if(j < 0) continue;                                                     // Einstieg vor dem Historienfenster
      sum[j] += DealGeld(i); vout[j] += D[i].volume;
      if(vout[j] < vin[j] - 1e-6) continue;                                  // Teilschliessung: Trade laeuft weiter
      double erg = sum[j];
      if(nz[j])
        {
         int g = grp[j];
         gSum[g] += erg; gOffen[g]--;
         if(gOffen[g] > 0) continue;                                          // weitere Teile des Signals noch offen
         erg = gSum[g];
        }
      if(erg < 0.0)
        {
         n++;
         if(n >= SerienStopp) { stopZeit = D[i].time; n = 0; }
        }
      else n = 0;
     }
   serN = n; serStoppZeit = stopZeit;
   if(serStoppZeit > 0 && serStoppZeit != serGemeldet && SerienPause())
     {
      serGemeldet = serStoppZeit;
      Meldung(StringFormat("SERIEN-STOPP: %d Verlusttrades in Folge (letzter %s) - keine neuen Einstiege bis 17:00 NY%s",
              SerienStopp, TimeToString(serStoppZeit, TIME_DATE|TIME_MINUTES), (SerienPauseTage > 0 ? StringFormat(" + %d Tag(e)", SerienPauseTage) : "")));
     }
  }

// true = Serien-Stopp aktiv (keine neuen Einstiege; Verwaltung, Bremsen und Wochenend-Wiederaufnahmen laufen weiter)
bool SerienPause()
  {
   if(SerienStopp <= 0 || serStoppZeit <= 0) return false;
   return (PropDayIndex(TimeCurrent()) <= PropDayIndex(serStoppZeit) + SerienPauseTage);
  }

string SerienText()
  {
   if(SerienStopp <= 0) return "Serien-Stopp aus";
   if(SerienPause()) return StringFormat("SERIEN-STOPP aktiv (seit %s)", TimeToString(serStoppZeit, TIME_DATE|TIME_MINUTES));
   return StringFormat("Verluste in Folge %d/%d", serN, SerienStopp);
  }

// Equity-Spitze: Saldo-Pfad plus beste Kurse aller Positionen je M5-Kerze seit 'von'
double RekonstruierePeak(datetime von, const bool pruefen)         // 6.10: pruefen = false beim laufenden Nachholen (Marktpausen ohne Kerzen)
  {
   // 6.10: obere Schranke der Equity je M5-Kerze, aber enger als bis 6.00: je Position nur die Kerzen, in denen sie offen war,
   // mit dem in der Kerze offenen Volumen und dem bestmoeglichen Ergebnis der Position in dieser Kerze (auch negativ).
   // Saldo zu Kerzenbeginn + Summe der Bestwerte >= Equity zu jedem Zeitpunkt der Kerze -> der Boden liegt nie zu tief.
   datetime now = TimeCurrent();
   double bal0 = AccountInfoDouble(ACCOUNT_BALANCE);
   // Saldo VOR allen Deals ab 'von' (rueckwaerts abziehen)
   for(int i=nD-1;i>=0;i--) { if(D[i].time <= von) break; bal0 -= DealGeld(i); }
   double peak = bal0;
   datetime t0 = von; if(t0 <= 0) t0 = (nD > 0 ? D[0].time : now - 86400);   // 6.10: ohne Anker ab dem ersten Deal
   t0 = (datetime)((long)t0 - (long)t0 % 300);
   long nGrid = (now - t0)/300 + 2;
   if(nGrid > 120000) { t0 = (datetime)((long)(now - 120000*300) - (long)(now - 120000*300) % 300); nGrid = 120002; }
   double fav[]; ArrayResize(fav, (int)nGrid); ArrayInitialize(fav, 0.0);
   bool   hat[]; ArrayResize(hat, (int)nGrid); ArrayInitialize(hat, false);
   // Positionen aus Deals: Einstieg, Durchschnittskurs, Volumenverlauf (6.10: auch vor 'von' eroeffnete, die danach noch offen waren)
   long ids[]; datetime tin[], tout[]; int dir[]; double vol[], px[]; string sy[]; int np=0;
   for(int i=0;i<nD;i++)
     {
      if(!IstHandel(i)) continue;
      int j=-1; for(int q=0;q<np;q++) if(ids[q]==D[i].posid) { j=q; break; }
      if(D[i].entry==DEAL_ENTRY_IN)
        {
         if(j<0)
           {
            ArrayResize(ids,np+1); ArrayResize(tin,np+1); ArrayResize(tout,np+1); ArrayResize(dir,np+1);
            ArrayResize(vol,np+1); ArrayResize(px,np+1); ArrayResize(sy,np+1);
            ids[np]=D[i].posid; tin[np]=D[i].time; tout[np]=now; dir[np]=(D[i].type==DEAL_TYPE_BUY ? 1 : -1);
            vol[np]=D[i].volume; px[np]=D[i].price; sy[np]=D[i].sym; np++;
           }
         else { px[j] = (px[j]*vol[j] + D[i].price*D[i].volume)/(vol[j]+D[i].volume); vol[j] += D[i].volume; }
        }
      else if(j>=0) tout[j] = D[i].time;     // letzter (Teil-)Ausstieg
     }
   for(int q=0;q<np;q++)
     {
      if(tout[q] <= t0) continue;                                            // vor dem Fenster geschlossen
      double mpp = MoneyPerPricePerLot(sy[q]);
      // Volumen, das zu Beginn jeder Kerze noch offen war (Teilschliessungen verringern es erst ab der Kerze danach)
      double outV[]; datetime outT[]; int no = 0;
      for(int i=0;i<nD;i++)
         if(IstHandel(i) && D[i].posid == ids[q] && D[i].entry != DEAL_ENTRY_IN) { ArrayResize(outV,no+1); ArrayResize(outT,no+1); outV[no]=D[i].volume; outT[no]=D[i].time; no++; }
      MqlRates r[];
      datetime ab = (tin[q] > t0 ? tin[q] : t0);
      ab = (datetime)((long)ab - (long)ab % 300);
      int n = CopyRates(sy[q], PERIOD_M5, ab, tout[q], r);
      if(n <= 0) { if(pruefen) { if(peakOk) PrintFormat("DEADBAND4: M5-Kurse %s fuer die Equity-Spitze nicht verfuegbar (Fehler %d) - wird nachgeholt, bis dahin kleinere Groesse", sy[q], GetLastError()); peakOk = false; } continue; }
      datetime bisK = (datetime)MathMin((double)tout[q], (double)iTime(sy[q], PERIOD_M5, 0));   // 6.10: Luecken am Anfang/Ende = Kurse noch nicht geladen
      if(pruefen && ((tin[q] >= t0 && r[0].time > ab + 3600) || r[n-1].time < bisK - 3600))
        { if(peakOk) PrintFormat("DEADBAND4: M5-Kurse %s %s-%s fuer die Equity-Spitze unvollstaendig - wird nachgeholt", sy[q], TimeToString(ab), TimeToString(bisK)); peakOk = false; }
      // 6.10: nicht synchrone Historie kann Luecken in der Mitte haben (nach einer Offline-Zeit) -> nachholen, bis sie synchron ist
      if(pruefen && !MQLInfoInteger(MQL_TESTER) && !SeriesInfoInteger(sy[q], PERIOD_M5, SERIES_SYNCHRONIZED))
        { if(peakOk) PrintFormat("DEADBAND4: M5-Kurse %s noch nicht synchron - Equity-Spitze wird nachgeholt", sy[q]); peakOk = false; }
      for(int i=0;i<n;i++)
        {
         if(r[i].time + 300 <= tin[q] || r[i].time > tout[q]) continue;          // Position in dieser Kerze nicht offen
         long g = (r[i].time - t0)/300;
         if(g < 0 || g >= nGrid) continue;
         double v = vol[q];
         for(int o=0;o<no;o++) if(outT[o] < r[i].time) v -= outV[o];             // vor Kerzenbeginn geschlossen
         if(v <= 1e-9) continue;
         double f = (dir[q]>0 ? (r[i].high - px[q]) : (px[q] - r[i].low)) * v * mpp;   // Short zum Bid-Tief: obere Schranke
         if(r[i].time < tin[q] && f < 0.0) f = 0.0;                              // Einstiegskerze: vor dem Einstieg gab es die Position noch nicht
         fav[(int)g] += f; hat[(int)g] = true;
        }
     }
   // Saldo-Pfad ueber das Gitter (Saldo zu Kerzenbeginn)
   double bal = bal0; int di = 0;
   while(di < nD && D[di].time <= von) di++;
   for(long g=0; g<nGrid; g++)
     {
      datetime tg = t0 + (datetime)(g*300);
      while(di < nD && D[di].time <= tg) { bal += DealGeld(di); di++; }
      double e = bal + (hat[(int)g] ? fav[(int)g] : 0.0);
      if(e > peak) peak = e;
     }
   return peak;
  }


//+------------------------------------------------------------------+
//| Zyklusstand / Modus                                               |
//+------------------------------------------------------------------+
int GueltigeTageMitHeute() { return kValidDays + ((GueltigHeuteZaehlt && kTodayReal >= GueltigSchwelle()) ? 1 : 0); }   // 6.10: Schwelle + Reserve

// 6.40 Schutz gueltiger Tage: Ist heute schon gueltig (realisiert >= 0,5 % + Reserve, auch die eigene Ernte der letzten 30 s)
// und fehlen dem Zyklus OHNE heute noch gueltige Tage, oeffnet der EA bis 17:00 NY keine neuen Positionen (6.40: RSI21, Noise,
// Fades, DEADBAND; 6.50: Noise, DEADBAND, Fades ausser GueltigSchutzFrei, RSI21 vor GueltigSchutzR21BisNY oder ohne
// Fade-Regime). Ein Verlust kippte den gueltigen Tag sonst wieder - im Replikat waren das 8 von 50 gueltigen Tagen je Jahr.
// Wochenend-Wiederaufnahmen, Verwaltung, Ernten und Ausstiege laufen weiter. Fehlen keine gueltigen Tage mehr (nur noch
// Mindestgewinn oder 10-Tage-Frist), wird normal gehandelt.
// 6.40: Gewinn, ab dem die Mindestauszahlung (Anteil MinPayoutUSD) moeglich ist. Gilt auch ohne KontoAb20260730, sobald
// MinProfitPct <= 0 ist - sonst waere der Zyklus schon bei 0 $ Gewinn reif (Auszahlung ueber wenige Dollar, Konto flach).
double MinGewinnAuszahlung()
  {
   if(ProfitSplit <= 0.0) return MathMax(MinPayoutUSD, 0.0);
   return (KontoAb20260730 || MinProfitPct <= 0.0) ? MinPayoutUSD / ProfitSplit : 0.0;
  }

double GueltigHeuteReal()                                                  // realisiert heute: Deals, oder eigene Ernte der letzten 30 s
  {
   long heute = PropDayIndex(TimeCurrent());
   if(kTodayRealTag != heute) return -DBL_MAX;                               // Tageswechsel, Historie noch nicht neu gerechnet
   bool sOk = (TimeCurrent() - kSchaetzZeit <= 30 && PropDayIndex(kSchaetzZeit) == heute);
   return MathMax(kTodayReal, sOk ? kTodayRealSchaetz : -DBL_MAX);
  }
void GueltigSchutzPruefen(const long today)
  {
   // Positionen seit dem letzten Neuberechnen geoeffnet/geschlossen (eigener Ausstieg, Broker-Stop/-Ziel): Deals neu laden,
   // damit ein eben realisierter Gewinn schon zaehlt (sonst bis zu 5 s spaeter)
   if(GueltigSchutz && kBereit && kLastRecalc > 0 && MathAbs(PosSignatur() - kPosSigRecalc) > 0.5 && LadeDeals(0)) RekonstruiereKonto(false);
   gGueltigSchutz = GueltigSchutz && kBereit && kCycleStart > 0 && kValidDays < NeedValidDays && GueltigHeuteReal() >= GueltigSchwelle();
   if(gGueltigSchutz && gGsTag != today)
     {
      gGsTag = today;
      PrintFormat("DEADBAND4: SCHUTZ GUELTIGER TAG - heute realisiert %.2f >= %.2f, gueltige Tage %d/%d: keine neuen Einstiege (%s) bis 17:00 NY (offene Positionen laufen weiter)",
                  GueltigHeuteReal(), GueltigSchwelle(), kValidDays + 1, NeedValidDays, GueltigSchutzUmfang());
     }
  }
string GueltigSchutzText()
  {
   return StringFormat("Tag schon gueltig (%.2f), noch %d gueltige Tage bis zur Auszahlung - Schutz gueltiger Tage bis 17:00 NY", GueltigHeuteReal(), MathMax(NeedValidDays - kValidDays - 1, 0));
  }
// 6.50: RSI21 ist an einem gueltigen Tag nur fuer Einstiege vor GueltigSchutzR21BisNY geschuetzt sowie ganztags, solange der
//       Portfolio-Waechter die Fades nicht live handeln laesst (spaetere RSI21-Trades schliessen meist erst an einem Folgetag
//       und gefaehrden den gueltigen Tag kaum). t = Zeit des Signals = Open der Einstiegskerze (wie das Replikat); Aufruf in
//       HandleR21 mit sigZeit. Noise, DEADBAND und die Fades ausser GueltigSchutzFrei wie 6.40.
bool R21GueltigSchutzJetzt(const datetime t)
  {
   datetime t5 = (datetime)((long)t - (long)t % 300);                     // Open der M5-Kerze des Einstiegs
   if(NYHour(t5) < GueltigSchutzR21BisNY) return true;
   return (GueltigSchutzR21Regime && !FadeRegimeLive(t5));
  }
string R21SchutzGrund(const datetime t)
  {
   datetime t5 = (datetime)((long)t - (long)t % 300);
   if(NYHour(t5) < GueltigSchutzR21BisNY)
      return StringFormat("Tag schon gueltig (%.2f), RSI21 vor %s NY geschuetzt", GueltigHeuteReal(), NYStundeText(GueltigSchutzR21BisNY));
   return StringFormat("Tag schon gueltig (%.2f), Fade-Regime nicht live (%s) - RSI21 geschuetzt bis 17:00 NY", GueltigHeuteReal(), FadeRegimeText(t5));
  }

// Tage und Frist erfuellt?
bool TageUndFristErfuellt()
  {
   if(GueltigeTageMitHeute() < NeedValidDays || kCycleStart <= 0) return false;
   return (PropDayIndex(TimeCurrent()) - PropDayIndex(kCycleStart) >= CycleDays)
          && ((long)(TimeCurrent() - kCycleStart) >= (long)CycleDays*86400);   // 6.10: auch volle 10 x 24 h (strenge Lesart)
  }

bool ZyklusReif()
  {
   if(!TageUndFristErfuellt()) return false;
   double profit = AccountInfoDouble(ACCOUNT_BALANCE) - kStart;
   return (profit >= kMinProfit);
  }

// 4.20: Zustand der Gewinn-Ernte - alles erfuellt bis auf den Mindestgewinn
bool NurMindestgewinnFehlt()
  {
   if(!TageUndFristErfuellt()) return false;
   return (AccountInfoDouble(ACCOUNT_BALANCE) - kStart < kMinProfit);
  }

double AuszahlbarJetzt()
  {
   double profit = AccountInfoDouble(ACCOUNT_BALANCE) - kStart;
   if(kPayouts < PayoutCapCount && PayoutCapPct > 0.0) profit = MathMin(profit, kStart*PayoutCapPct/100.0);
   return MathMax(profit, 0.0);
  }

double PufferPct()
  {
   double boden = kPeakEq - kStart*MaxLossPct/100.0;
   return (kStart>0.0 ? (AccountInfoDouble(ACCOUNT_EQUITY) - boden)/kStart*100.0 : 0.0);
  }

double DDFaktor(double bufPct)
  {
   if(DDFullPct <= 0.0) return 1.0;
   if(bufPct >= DDFullPct) return 1.0;
   if(bufPct <= DDMinPct) return DDMinFactor;
   return DDMinFactor + (1.0-DDMinFactor)*(bufPct-DDMinPct)/(DDFullPct-DDMinPct);
  }

void Meldung(string txt)
  {
   Print("DEADBAND4: ", txt);
   if(UsePush && !MQLInfoInteger(MQL_TESTER))
     {
      if(!SendNotification("DEADBAND4: " + txt))
         Print("DEADBAND4: Push nicht gesendet (MetaQuotes ID pruefen), Fehler ", GetLastError());
     }
  }

// 4.21: Kontozustand ins Journal (voll) und als Push (kurz, unter 255 Zeichen)
// 6.10: Schritte, sobald die Kontodaten vollstaendig sind (Start oder nach Verbindungsaufbau)
void NachKontoStart()
  {
   kBereitAb = TimeCurrent();
   komZeit = 0; komRundZeit = 0;                                         // Kommissionen aus der jetzt geladenen Historie
   TagesRefLaden();
   for(int k=0;k<nSym;k++) TdLaden(k);                                   // Tageszaehler mit bekanntem Konto
   for(int k=0;k<nSlot;k++)                                             // Vormerkungen aus dem Zyklus vor einer inzwischen gebuchten Auszahlung verwerfen
      if(W[k].aktiv && kLastPayout > 0 && NYDayIndex(kLastPayout) >= W[k].fri) WeLoeschen(k, "Auszahlung nach der Vormerkung");
  }

void KontoMeldung(string anlass)
  {
   double bal = AccountInfoDouble(ACCOUNT_BALANCE), eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double boden = kPeakEq - kStart*MaxLossPct/100.0;
   long zykTag = (kCycleStart>0 ? PropDayIndex(TimeCurrent()) - PropDayIndex(kCycleStart) : 0);
   string modus = ZyklusReif() ? "REIF - Auszahlung beantragen, sobald flach"
                  : (NurMindestgewinnFehlt() ? "nur Mindestgewinn fehlt (Gewinn-Ernte bereit)" : "sammeln");
   PrintFormat("DEADBAND4: KONTO ERKANNT (%s): Startsaldo %.2f (Einzahlung %s, %d Auszahlungen%s) | Saldo %.2f, Equity %.2f, Gewinn %.2f, Mindestgewinn %.2f | Zyklus seit %s, Tag %d/%d, gueltige Tage %d/%d | Boden %.2f, Puffer %.2f %% | Modus: %s",
               anlass, kStart, (kAccountFrom>0 ? TimeToString(kAccountFrom, TIME_DATE) : "?"), kPayouts,
               (kLastPayout>0 ? ", letzte " + TimeToString(kLastPayout, TIME_DATE) : ""),
               bal, eq, bal-kStart, kMinProfit,
               (kCycleStart>0 ? TimeToString(kCycleStart, TIME_DATE) : "noch kein Trade"), (int)zykTag, CycleDays,
               GueltigeTageMitHeute(), NeedValidDays, boden, PufferPct(), modus);
   // 6.10: vollstaendiger Kontozustand zum Abgleich mit dem GFT-Dashboard (Journal + Datei MQL5/Files)
   string z[]; int nz = 0;
   ArrayResize(z, 64);
   z[nz++] = StringFormat("DEADBAND LIVE 6.50 - Kontozustand %s (%s), Konto %I64d, Server %s", TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS), anlass,
                          AccountInfoInteger(ACCOUNT_LOGIN), AccountInfoString(ACCOUNT_SERVER));
   z[nz++] = StringFormat("Startsaldo %.2f (%s) | Einzahlung %s | Auszahlungen %d%s | Deckel %s", kStart, (StartBalanceOverride > 0.0 ? "StartBalanceOverride" : (kAccountFrom > 0 ? "aus Einzahlung" : "aus Saldo abgeleitet")),
                          (kAccountFrom>0 ? TimeToString(kAccountFrom, TIME_DATE|TIME_MINUTES) : "?"), kPayouts, (kLastPayout>0 ? ", letzte " + TimeToString(kLastPayout, TIME_DATE|TIME_MINUTES) : ""),
                          (kPayouts < PayoutCapCount ? StringFormat("%.0f %% (%.2f)", PayoutCapPct, kStart*PayoutCapPct/100.0) : "keiner"));
   z[nz++] = StringFormat("Saldo %.2f | Equity %.2f | Gewinn %.2f | Mindestgewinn fuer die Auszahlung %.2f (%.1f %%) | auszahlbar jetzt %.2f", bal, eq, bal-kStart, kMinProfit, kStart > 0.0 ? kMinProfit/kStart*100.0 : 0.0, AuszahlbarJetzt());
   z[nz++] = StringFormat("Zyklus seit %s (%s) | Zyklustag %d von mind. %d | gueltige Tage %d/%d (Schwelle %.2f), Handelstage %d | realisiert im Zyklus %.2f, heute %.2f",
                          (kCycleStart>0 ? TimeToString(kCycleStart, TIME_DATE|TIME_MINUTES) : "noch kein Trade"), (StringLen(CycleStartOverride) >= 8 ? "CycleStartOverride" : "erster Trade nach der letzten Auszahlung"),
                          (int)zykTag, CycleDays, GueltigeTageMitHeute(), NeedValidDays, GueltigSchwelle(), kTradeDays, kCycleReal, kTodayReal);
   string tl = "Tage im Zyklus (Prop-Tag ab 17:00 NY, realisiert inkl. Swap/Kommission):";
   for(int i=0;i<kTagN;i++)
      tl += StringFormat(" %s %+.2f%s", TimeToString(PropDayStart(kTagIdx[i]), TIME_DATE), kTagErg[i],
                         (kTagErg[i] >= GueltigSchwelle() ? (kTagIdx[i] == PropDayIndex(TimeCurrent()) ? "*heute" : "*") : ""));
   if(kTagN == 0) tl += " keine";
   z[nz++] = tl;
   z[nz++] = StringFormat("Equity-Spitze %.2f (%s) | Boden %.2f | Puffer %.2f (%.2f %%) | Groessenfaktor %.2f", kPeakEq,
                          (FloorOverride > 0.0 ? "FloorOverride" : (peakOk ? "rekonstruiert + Sicherheitsaufschlag" : "UNVOLLSTAENDIG - wird nachgeholt")),
                          boden, eq - boden, PufferPct(), DDFaktor(PufferPct())*(eq < kStart ? BelowStartMult : 1.0));
   z[nz++] = StringFormat("Tagesstart (17:00 NY) Saldo %.2f + Buchgewinn %.2f = Referenz %.2f%s | Tagesverlust-Grenze %.2f (Bremse %.2f)%s", kDayStartBal, kDayRefPlus, kDayStartBal + kDayRefPlus,
                          (tagesRefUnsicher ? " (Buchgewinn UNBEKANNT - keine Einstiege, bis er bestimmt ist)" : ""),
                          -MathMin(kDayStartBal + kDayRefPlus, kStart)*RuleDayLossPct/100.0, -kStart*DayStopPct/100.0,
                          (kAuszahlungHeute ? " | heute ausgezahlt: keine Einstiege bis 17:00 NY" : ""));
   z[nz++] = StringFormat("Buchverlust Verlierer %.2f (Firmengrenze %.2f, Bremse %.2f) | offenes Stop-Risiko %.2f von %.2f", FloatingVerlierer(CountForeignPositions),
                          -FloatBasis()*kRuleFloatPct/100.0, -FloatBasis()*FloatStopPct/100.0, OffenesRisiko(0), kStart*GesamtBudgetPct/100.0);
   int nPos = 0;
   for(int i=PositionsTotal()-1;i>=0 && nz < 60;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      long mg = PositionGetInteger(POSITION_MAGIC);
      string modul = IsDbMagic(mg) ? "DEADBAND" : (IsR21Magic(mg) ? "RSI21" : (IsNzMagic(mg) ? "Noise" : (IsFadeMagic(mg) ? "Fade " + PositionGetString(POSITION_COMMENT) : "FREMD")));
      z[nz++] = StringFormat("Position #%I64u %s %s %.2f Lot zu %.5g, Stop %.5g, Ziel %.5g, seit %s, Ergebnis %.2f (%s)", tk, PositionGetString(POSITION_SYMBOL),
                             (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? "LONG" : "SHORT"), PositionGetDouble(POSITION_VOLUME), PositionGetDouble(POSITION_PRICE_OPEN),
                             PositionGetDouble(POSITION_SL), PositionGetDouble(POSITION_TP), TimeToString((datetime)PositionGetInteger(POSITION_TIME), TIME_DATE|TIME_MINUTES),
                             PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP), modul);
      nPos++;
     }
   if(nPos == 0) z[nz++] = "keine offenen Positionen";
   z[nz++] = StringFormat("%s | Modus: %s | NY-Versatz %d h | Kontodaten %s", SerienText(), modus, nyOff, (kBereit ? "vollstaendig" : "unvollstaendig"));
   ArrayResize(z, nz);
   for(int i=0;i<nz;i++) Print("DEADBAND4:   ", z[i]);
   if(!MQLInfoInteger(MQL_TESTER))
     {
      string fn = StringFormat("DEADBAND4_Konto_%I64d.txt", AccountInfoInteger(ACCOUNT_LOGIN));
      int fh = FileOpen(fn, FILE_WRITE|FILE_TXT|FILE_ANSI);
      if(fh != INVALID_HANDLE) { for(int i=0;i<nz;i++) FileWriteString(fh, z[i] + "\r\n"); FileClose(fh); PrintFormat("DEADBAND4: Kontozustand gespeichert in MQL5\\Files\\%s", fn); }
     }
   if(UsePush && !MQLInfoInteger(MQL_TESTER))
     {
      string kurz = StringFormat("DEADBAND4 KONTO ERKANNT (%s): Start %.0f, Saldo %.0f, Zyklus Tag %d/%d, gueltig %d/%d, Puffer %.1f %%, %s",
                                 anlass, kStart, bal, (int)zykTag, CycleDays, GueltigeTageMitHeute(), NeedValidDays, PufferPct(), modus);
      if(!SendNotification(kurz)) Print("DEADBAND4: Push nicht gesendet (MetaQuotes ID pruefen), Fehler ", GetLastError());
     }
  }


// 4.90: Schliessversuche alle 0,5 s (Wanduhr), Meldung hoechstens je Minute
void Notbremse(string grund)
  {
   int fehl = 0;
   if(MQLInfoInteger(MQL_TESTER) || notbremseMs == 0 || GetTickCount() - notbremseMs >= 500)
     {
      notbremseMs = GetTickCount(); if(notbremseMs == 0) notbremseMs = 1;
      fehl = CloseAll("NOTBREMSE - " + grund);
     }
   if(letzteNotbremse>0 && TimeCurrent()-letzteNotbremse < 60) return;
   letzteNotbremse = TimeCurrent();
   for(int k=0;k<nSlot;k++) WeLoeschen(k, "Notbremse");
   Meldung(StringFormat("NOTBREMSE an der Firmengrenze: %s | Saldo %.2f | Equity %.2f%s",
           grund, AccountInfoDouble(ACCOUNT_BALANCE), AccountInfoDouble(ACCOUNT_EQUITY), (fehl > 0 ? StringFormat(" | %d Schliessungen ABGELEHNT", fehl) : "")));
  }

//+------------------------------------------------------------------+
void OnTick()  { Durchlauf(); }
void OnTimer() { Durchlauf(); }

void Durchlauf()
  {
   datetime now = TimeCurrent();
   HandelWaechter();                                                       // 4.90: Algo-Knopf, Konto, Verbindung
   if(kBereit && kLogin != 0 && AccountInfoInteger(ACCOUNT_LOGIN) > 0 && AccountInfoInteger(ACCOUNT_LOGIN) != kLogin)   // 6.10: Kontowechsel
     {
      PrintFormat("DEADBAND4: Konto gewechselt (%I64d -> %I64d) - Kontodaten werden neu geladen, bis dahin keine Einstiege", kLogin, AccountInfoInteger(ACCOUNT_LOGIN));
      ResetKontoZustand(); kBereit = false;
      for(int k=0;k<nSlot;k++) { W[k].aktiv = false; S[k].tradesToday = 0; S[k].curDay = 0; }   // Stand des alten Kontos verwerfen (neues laedt nach)
      weNachladen = true; komZeit = 0; komRundZeit = 0;
     }
   if(!kBereit)
     {
      // 4.90: Kontodaten fehlen noch (Kaltstart vor Login) - keine Einstiege, nur die Floating-Bremse auf den Saldo
      static uint kVersuchMs = 0;
      if(kVersuchMs == 0 || GetTickCount() - kVersuchMs >= 2000)
        {
         kVersuchMs = GetTickCount(); if(kVersuchMs == 0) kVersuchMs = 1;
         kBereit = KontoStart();
         if(kBereit) { NachKontoStart(); KontoMeldung("nach Verbindungsaufbau"); }
        }
      if(!kBereit)
        {
         double b0 = AccountInfoDouble(ACCOUNT_BALANCE);
         double f0 = FloatingRegel(CountForeignPositions);                    // 5.10: bei FloatNurVerlierer nur Verlierer
         if(b0 > 0.0 && FloatStopPct > 0.0 && f0 <= -b0*FloatStopPct/100.0 && BremseDarf())
            BremseErgebnis(CloseAll("Buchverlust am Limit (Kontodaten noch nicht geladen)"), "Floating-Bremse ohne Kontodaten");
         // 6.10: Tagesbremse mit der gesicherten Tagesreferenz desselben Prop-Tags
         if(!MQLInfoInteger(MQL_TESTER) && AccountInfoInteger(ACCOUNT_LOGIN) > 0 && b0 > 0.0 && AccountInfoDouble(ACCOUNT_EQUITY) > 0.0
            && GlobalVariableCheck(KontoGv("DAYIDX")) && GlobalVariableCheck(KontoGv("DAYBAL"))
            && GlobalVariableCheck(KontoGv("START")) && (long)GlobalVariableGet(KontoGv("DAYIDX")) == PropDayIndex(now))
           {
            double plus0 = GlobalVariableGet(KontoGv("DAYPLUS"));
            if(plus0 < 0.0 && GlobalVariableCheck(KontoGv("DAYPLUSV"))) plus0 = GlobalVariableGet(KontoGv("DAYPLUSV"));   // unsicher: vorlaeufiger Wert
            double ref0 = GlobalVariableGet(KontoGv("DAYBAL")) + MathMax(0.0, plus0);
            double st0  = GlobalVariableGet(KontoGv("START"));
            if(ref0 > 0.0 && st0 > 0.0 && AccountInfoDouble(ACCOUNT_EQUITY) - ref0 <= -st0*DayStopPct/100.0 && FloatingPnl(CountForeignPositions) < 0.0 && BremseDarf())
               BremseErgebnis(CloseAll("Tagesverlust am Limit (Kontodaten noch nicht geladen)"), "Tagesstopp ohne Kontodaten");
           }
         return;
        }
     }
   if(weNachladen && now >= D'2020.01.01')                                 // 4.90: Vormerkungen mit gueltiger Serverzeit laden
     {
      weNachladen = false;
      for(int k=0;k<nSlot;k++)
        {
         if(S[k].r21 && !S[k].zweit && r21LastSig[k][0]==0 && r21LastSig[k][1]==0) R21SigLaden(k);
         if(WeAktiv && WeAufnahme && !W[k].aktiv)
           {
            WeLaden(k);
            if(W[k].aktiv && kLastPayout > 0 && NYDayIndex(kLastPayout) >= W[k].fri) WeLoeschen(k, "Auszahlung nach der Vormerkung");   // 6.10 wie NachKontoStart
           }
        }
     }
   NYOffsetWaechter();
   NewsLaden();
   double eqNow = AccountInfoDouble(ACCOUNT_EQUITY);
   if(eqNow > kPeakEq) kPeakEq = eqNow;
   if(eqNow > kEqMaxZyklus) kEqMaxZyklus = eqNow;                          // 6.10: gesehene Hochs (Ersatz einer vorlaeufigen Spitze)
   long today = PropDayIndex(now);
   bool neuGerechnet = false;
   if(today != kDayIdx)
     {
      // NY-Versatz taeglich neu (EU- und US-Sommerzeit wechseln an verschiedenen Tagen)
      int offNeu = AutoNYOffset ? AutoOffset() : NYOffsetHours;
      if(offNeu != nyOff) { PrintFormat("DEADBAND4: NY-Versatz %d -> %d h", nyOff, offNeu); nyOff = offNeu; today = PropDayIndex(now); }
      if(!AutoNYOffset && !MQLInfoInteger(MQL_TESTER) && TerminalInfoInteger(TERMINAL_CONNECTED))   // 6.10: nur Hinweis, gerechnet wird fest
        {
         int gem = AutoOffset();
         if(gem != NYOffsetHours) Meldung(StringFormat("Hinweis: gemessener NY-Versatz %d h weicht von NYOffsetHours %d h ab - PC-Uhr/Zeitzone oder Broker-Serverzeit pruefen (der EA rechnet weiter mit %d h)", gem, NYOffsetHours, NYOffsetHours));
        }
      kDayIdx = today;
      if(LadeDeals(0)) { RekonstruiereKonto(false); neuGerechnet = true; }   // schliesst den Tag ab, setzt Tagesstartsaldo
     }
   // 6.10: Saldo ohne Handel veraendert (Auszahlung, Abbuchung): sofort neu laden - sonst misst die Tagesgrenze bis zum
   //       naechsten Laden von der alten Tagesreferenz (falscher Notbremse-Alarm nach jeder Auszahlung)
   static uint sprungMs = 0;                                              // Sprung gesehen, Historie erklaert ihn noch nicht
   if(SaldoSprung()) { kLastRecalc = 0; sprungMs = GetTickCount(); if(sprungMs == 0) sprungMs = 1; }
   // Historie alle 5 s: Auszahlung erkannt? Tagesstand?
   if(now - kLastRecalc >= 5)
     {
      if(LadeDeals(0)) { RekonstruiereKonto(false); neuGerechnet = true; }
      else kLastRecalc = now;                                              // 4.90: Historie fehlt - Zustand bleibt, spaeter erneut
     }
   if(neuGerechnet)                                                        // 6.10: Historie gewachsen oder jetzt vollstaendig -> Spitze nachrechnen (senkt nie)
     {
      static int nDPeak = -1;
      bool vorher = histOk;
      histOk = HistorieKonsistent();
      if(histOk) sprungMs = 0;                                             // Saldo erklaert -> Tagesreferenz stimmt
      if(histOk && kLastPayout < kPayoutVerarbeitet)                       // 6.10: im Rueckfall verarbeitete Auszahlung ist mit stimmiger
        {                                                                  //       Historie keine mehr -> Zyklus und Spitze neu
         PrintFormat("DEADBAND4: Auszahlung %s ist nach vollstaendiger Historie keine - Zyklus ab %s, Equity-Spitze wird neu bestimmt",
                     TimeToString(kPayoutVerarbeitet, TIME_DATE|TIME_MINUTES), (kLastPayout > 0 ? TimeToString(kLastPayout, TIME_DATE|TIME_MINUTES) : "Einzahlung"));
         kPayoutVerarbeitet = kLastPayout; kPeakVorlaeufig = true; nDPeak = -1;
        }
      if(histOk && (nD != nDPeak || !vorher))                              // nur mit einer Historie, die den Saldo erklaert (sonst doppelt gezaehlte Deals)
        {
         nDPeak = nD;
         if(kPeakVorlaeufig && kLastPayout == kPayoutVerarbeitet)
           {
            // 6.10: Start lief mit einer Historie, die den Saldo nicht erklaerte - Spitze jetzt vollstaendig neu (darf sinken:
            // die Rekonstruktion aus M5 umfasst jede seither gesehene Equity), gesicherte Spitze nur aus demselben Zyklus
            double alt = kPeakEq;
            kPeakVorlaeufig = false; peakOk = true;
            RekonstruiereKonto(true);
            kPeakEq = MathMax(kPeakEq, kEqMaxZyklus);                         // nie unter eine selbst gesehene Equity
            PrintFormat("DEADBAND4: Historie erklaert den Saldo jetzt - Equity-Spitze neu bestimmt %.2f -> %.2f (Boden %.2f)", alt, kPeakEq, kPeakEq - kStart*MaxLossPct/100.0);
           }
         else
           {
            double pk = PeakRekonstruktion(false);
            if(pk > kPeakEq + 0.01) { PrintFormat("DEADBAND4: Equity-Spitze aus der Historie angehoben %.2f -> %.2f", kPeakEq, pk); kPeakEq = pk; }
           }
        }
     }
   datetime gvPay = 0;
   if(!MQLInfoInteger(MQL_TESTER) && GlobalVariableCheck(KontoGv("PEAKPAY"))) gvPay = (datetime)(long)GlobalVariableGet(KontoGv("PEAKPAY"));
   // 6.10: Auszahlung gegen den zuletzt verarbeiteten Stand pruefen (auch wenn eine andere Stelle die Historie neu geladen hat).
   //       Erst verarbeiten, wenn die frisch geladene Historie den Saldo erklaert und Auszahlung + Saldo seit 5 s unveraendert
   //       sind: MT5 kann den Deal vor dem neuen Saldo zeigen - dann laege die neue Spitze beim alten Saldo (Boden zu hoch).
   //       Erklaert die Historie den Saldo auch nach 3 min nicht, wird trotzdem verarbeitet (Spitze vorlaeufig, Meldung).
   bool payBereit = false, payOhneHist = false;
   if(kLastPayout > kPayoutVerarbeitet && neuGerechnet)
     {
      static datetime payKand = 0, payKandZeit = 0, payErstZeit = 0; static double payKandBal = 0.0;
      double bNow = AccountInfoDouble(ACCOUNT_BALANCE);
      if(payKand != kLastPayout) payErstZeit = now;
      if(payKand != kLastPayout || MathAbs(payKandBal - bNow) > 0.005) { payKand = kLastPayout; payKandBal = bNow; payKandZeit = now; }
      bool stabil = (MQLInfoInteger(MQL_TESTER) || now - payKandZeit >= 5);
      payOhneHist = (!histOk && now - payErstZeit >= 180);
      payBereit = stabil && (histOk || payOhneHist);
     }
   if(payBereit && !MQLInfoInteger(MQL_TESTER) && gvPay > 0 && kLastPayout <= gvPay)
     {
      // 6.10: die Auszahlung war schon bekannt (Historie war beim Start unvollstaendig) - nur den Boden des Zyklus neu bestimmen
      kPayoutVerarbeitet = kLastPayout; kPeakVorlaeufig = payOhneHist;
      if(payOhneHist) peakOk = false;
      kPeakEq = MathMax(PeakRekonstruktion(true), MathMax(AccountInfoDouble(ACCOUNT_BALANCE), AccountInfoDouble(ACCOUNT_EQUITY)));
      if(GlobalVariableCheck(KontoGv("PEAK"))) kPeakEq = MathMax(kPeakEq, GlobalVariableGet(KontoGv("PEAK")));
      kPeakEq = MathMax(kPeakEq, kEqMaxZyklus);                            // Auszahlung lag vor dieser Sitzung: gesehene Hochs zaehlen
      PrintFormat("DEADBAND4: Historie vervollstaendigt - letzte Auszahlung %s, Equity-Spitze %.2f", TimeToString(kLastPayout, TIME_DATE|TIME_MINUTES), kPeakEq);
     }
   else if(payBereit)
     {
      kPayoutVerarbeitet = kLastPayout;
      if(payOhneHist) Meldung("Auszahlung verarbeitet, obwohl die Deal-Historie den Saldo nicht erklaert - Equity-Spitze vorlaeufig (kleinere Groesse). Boden mit dem GFT-Dashboard vergleichen (ggf. FloorOverride)");
      Meldung(StringFormat("Auszahlung erkannt (%s) - neuer Zyklus, Startsaldo %.2f, Saldo %.2f",
              TimeToString(kLastPayout, TIME_DATE|TIME_MINUTES), kStart, AccountInfoDouble(ACCOUNT_BALANCE)));
      RekonstruiereKonto(true);            // Boden neu (Equity-Hoch = jetzt)
      kPeakVorlaeufig = payOhneHist; if(payOhneHist) peakOk = false;
      kEqMaxZyklus = AccountInfoDouble(ACCOUNT_EQUITY);
      eqNow = AccountInfoDouble(ACCOUNT_EQUITY);
      kMode = 0; reifGemeldet = false; kLastReminder = 0;
      for(int k=0;k<nSlot;k++) WeLoeschen(k, "neuer Zyklus nach Auszahlung");
      PeakSichern(true);
      KontoMeldung("nach Auszahlung");
     }
   if(today != kRefTag)                                                    // 6.10: Buchgewinn um 17:00 NY als obere Schranke (die Maerkte pausieren 17-18 NY)
     {
      double f = 0.0;
      bool ok = BuchObergrenzeZu(PropDayStart(today), f);
      double live = (now - PropDayStart(today) <= 30) ? eqNow - AccountInfoDouble(ACCOUNT_BALANCE) : 0.0;
      tagesRefUnsicher = !ok;                                              // auch in den ersten 30 s: live nur vorlaeufig, spaeter aus Kursen
      TagesRefSetzen(today, MathMax(f, live), tagesRefUnsicher);
      if(tagesRefUnsicher) PrintFormat("DEADBAND4: Tagesreferenz 17:00 NY noch nicht sicher bestimmbar (Kurse werden geladen) - vorlaeufig Buchgewinn %.2f, keine neuen Einstiege, neuer Versuch jede Minute", kDayRefPlus);
      kRefTag = today; refFehl = 0; refVersuch = now;
     }
   if(tagesRefUnsicher && now - refVersuch >= 60)                          // 6.10: unbekannte Tagesreferenz jede Minute erneut bestimmen
     {
      refVersuch = now;
      double f2 = 0.0;
      if(BuchObergrenzeZu(PropDayStart(kRefTag), f2))
        {
         tagesRefUnsicher = false; refFehl = 0;
         TagesRefSetzen(kRefTag, MathMax(kDayRefPlus, f2), false);
         Print("DEADBAND4: Tagesreferenz 17:00 NY nachtraeglich bestimmt - Einstiege wieder frei");
        }
      else if(++refFehl == 15)
         Meldung("Tagesreferenz 17:00 NY seit 15 min nicht bestimmbar (M1/M5-Kurse fehlen) - heute keine neuen Einstiege. Kursverlauf der offenen Symbole im Terminal laden");
     }
   if(!peakOk && neuGerechnet && histOk && now - peakVersuch >= 60)        // 4.90: Spitze unvollstaendig rekonstruiert - nachholen (6.10: mit frischer, stimmiger Historie)
     {
      peakVersuch = now; peakOk = true;
      double pk = PeakRekonstruktion(true);
      if(pk > kPeakEq) { PrintFormat("DEADBAND4: Equity-Spitze nachtraeglich korrigiert %.2f -> %.2f", kPeakEq, pk); kPeakEq = pk; }
      if(peakOk) { peakFehl = 0; Print("DEADBAND4: Equity-Spitze vollstaendig rekonstruiert"); }
      else if(++peakFehl >= 10)
        {
         peakOk = true; peakFehl = 0;
         Meldung(StringFormat("Equity-Spitze nicht vollstaendig rekonstruierbar (M5-Kurse fehlen) - Boden %.2f bitte mit dem GFT-Dashboard vergleichen, ggf. FloorOverride setzen",
                 kPeakEq - kStart*MaxLossPct/100.0));
        }
     }
   {                                                                       // 6.10: Equity-Spitze laufend aus M5-Hochs nachholen (wie das Replikat)
    static datetime pkZeit = 0, pkOffenAb = 0;                            // ab pkOffenAb noch nicht mit synchronen Kursen nachgeholt
    bool verb = (MQLInfoInteger(MQL_TESTER) || TerminalInfoInteger(TERMINAL_CONNECTED) != 0);
    // nur direkt nach dem Laden der Historie (Saldo und Deals passen zusammen) - sonst zaehlt ein gerade geschlossener Trade doppelt
    if(verb && neuGerechnet && histOk && now - pkZeit >= 60)
      {
       datetime anker = (kLastPayout > 0 ? kLastPayout : kAccountFrom);
       datetime ab = now - 3600;
       if(pkOffenAb > 0 && pkOffenAb < ab) ab = pkOffenAb;                // Verbindungsluecke oder noch nicht synchrone Kurse: ab dort
       if(ab < anker) ab = anker;
       double pk = RekonstruierePeak(ab, false);
       if(pk > kPeakEq + 0.01) { PrintFormat("DEADBAND4: Equity-Spitze aus M5 nachgeholt %.2f -> %.2f", kPeakEq, pk); kPeakEq = pk; }
       bool sync = true;
       if(!MQLInfoInteger(MQL_TESTER))
         {
          for(int k=0;k<nSym;k++) if(!SeriesInfoInteger(S[k].sym, PERIOD_M5, SERIES_SYNCHRONIZED)) sync = false;
          for(int i=PositionsTotal()-1;i>=0;i--)                            // auch fremde Symbole offener Positionen
            {
             ulong tk = PositionGetTicket(i); if(tk == 0) continue;
             if(!SeriesInfoInteger(PositionGetString(POSITION_SYMBOL), PERIOD_M5, SERIES_SYNCHRONIZED)) sync = false;
            }
         }
       pkOffenAb = (sync ? now - 600 : ab);
       pkZeit = now;
      }
   }
   PeakSichern(false);
   UebernahmeNachholen();                                                  // 4.90
   InaktivWaechter();                                                      // 4.90

   double fltAll = FloatingPnl(CountForeignPositions);
   double fltRegel = FloatingRegel(CountForeignPositions);                 // 5.10: strenge Lesart - nur Verlustpositionen
   // --- aeussere Notbremsen genau dort, wo die Firma misst ---
   double fBasis = FloatBasis();
   if(kRuleFloatPct>0.0 && fltRegel <= -fBasis*kRuleFloatPct/100.0)
     { Notbremse(StringFormat("Buchverlust%s %.2f bei Firmengrenze %.2f", (FloatNurVerlierer ? " (Verlierer)" : ""), fltRegel, -fBasis*kRuleFloatPct/100.0)); return; }
   double dayRef = kDayStartBal + (TagesRefEquity ? kDayRefPlus : 0.0);   // 4.90: max(Saldo, Equity) um 17:00 NY
   double dayEq = eqNow - dayRef;
   double dayBasis = (kStart > 0.0 ? MathMin(dayRef, kStart) : dayRef);    // 5.10: 3 % auf die kleinere Basis (Startsaldo oder Tagesreferenz)
   // 6.10: Tagesreferenz veraltet (Saldo-Sprung ohne Handel, die Historie erklaert ihn noch nicht): Tagesgrenzen hoechstens
   //       10 s aufschieben, keine Einstiege
   static uint refAltMs = 0;
   bool refAlt = SaldoSprung() || (sprungMs != 0 && GetTickCount() - sprungMs < 10000);   // auch nach dem Neuladen, bis der Deal da ist
   if(!refAlt) refAltMs = 0; else if(refAltMs == 0) { refAltMs = GetTickCount(); if(refAltMs == 0) refAltMs = 1; }
   bool tagAufschub = refAlt && GetTickCount() - refAltMs < 10000;
   if(!tagAufschub && RuleDayLossPct>0.0 && dayRef>0.0 && dayEq <= -dayBasis*RuleDayLossPct/100.0)
     { Notbremse(StringFormat("Tagesverlust %.2f bei Firmengrenze %.2f", dayEq, -dayBasis*RuleDayLossPct/100.0)); return; }
   // --- innere Bremsen (4.90: gedrosselt, Push bei wiederholtem Scheitern) ---
   if(FloatStopPct>0.0 && fltRegel <= -fBasis*FloatStopPct/100.0)
     {
      if(BremseDarf()) BremseErgebnis(FloatGestuft ? FloatBremseGestuft(fltRegel) : CloseAll("Buchverlust am Limit"), "Floating-Bremse");
      return;
     }
   bool dayLocked = (dayEq <= -kStart*DayStopPct/100.0);
   if(dayLocked && fltAll < 0.0 && !tagAufschub) { if(BremseDarf()) BremseErgebnis(CloseAll("Tagesverlust am Limit"), "Tagesstopp"); return; }
   bool payOffen = (kLastPayout > kPayoutVerarbeitet);                     // 6.10: Auszahlung gebucht, Boden noch nicht neu gesetzt
   bool keineEinstiege = dayLocked || tagesRefUnsicher || kAuszahlungHeute || payOffen || refAlt;   // 6.10: keine Einstiege bis 17:00 NY bzw. bis verarbeitet
   GueltigSchutzPruefen(today);                                            // 6.40: heute gueltig, dem Zyklus fehlen noch gueltige Tage -> keine neuen Einstiege
   // 5.10: Swap-Vorsorge vor dem Rollover (der Swap wird gebucht, wenn keine Bremse mehr dazwischen greifen kann)
   if(SwapVorsorgePct > 0.0 && SwapVorsorgeMin > 0 && SwapFenster(now) && BremseDarf())
     {
      int fehlS = SwapVorsorge(fBasis);                                    // -1 = nichts zu tun, sonst Zahl der abgelehnten Schliessungen
      if(fehlS >= 0) { BremseErgebnis(fehlS, "Swap-Vorsorge"); return; }
     }

   // --- Modus ---
   bool reif = ZyklusReif() || AuszahlungAngefordert();                   // 6.10: beantragte Auszahlung haelt das Konto flach
   bool flach = KontoFlach();
   if(kMode==0 && reif)
     {
      kMode = 1;
      if(!reifGemeldet)
        {
         reifGemeldet = true;
         Meldung(StringFormat("AUSZAHLUNGSREIF: %d gueltige Tage, Gewinn %.2f - keine neuen Einstiege, offene %s",
                 GueltigeTageMitHeute(), AccountInfoDouble(ACCOUNT_BALANCE)-kStart,
                 (StopMode==0 ? "laufen aus" : (StopMode==1 ? "werden geschlossen" : "Gewinner werden geschlossen"))));
        }
     }
   if(kMode==1)
     {
      if(R21ReifeSchliessen) R21BeiReifeSchliessen();                  // 4.40 (4.90: auch bei ausgeschaltetem Modul)
      NzBeiReifeSchliessen();                                          // 5.00: Noise-Positionen bei Reife (NzReifeModus)
      FadeBeiReifeSchliessen();                                        // 6.00: Fade-Positionen bei Reife schliessen
      if(!flach && StopMode>=1) ReifeSchliessen();
      flach = KontoFlach();
      if(flach && !(WeAufnahmeReif && WeWartet()))     // 4.30: wartet eine Wiederaufnahme, ist das Konto nur scheinbar flach
        {
         if(LadeDeals(0)) RekonstruiereKonto(false);
         if(ZyklusReif() || AuszahlungAngefordert()) { kMode = 2; kFlatSince = now; kLastReminder = 0; }
         else { kMode = 0; reifGemeldet = false; }     // Reife durch den letzten Deal verloren
        }
     }
   if(kMode==2 && !reif && !payOffen && !refAlt)
     {
      // Reife verloren (z. B. fremder Trade, Korrekturbuchung): zurueck in den Handel
      kMode = 0; reifGemeldet = false;
      Meldung("Reife im Wartemodus verloren - Handel wird fortgesetzt");
     }
   if(kMode==2 && !payOffen)
     {
      if(kLastReminder==0 || now - kLastReminder >= (datetime)ReminderHours*3600)
        {
         kLastReminder = now;
         double p = AccountInfoDouble(ACCOUNT_BALANCE) - kStart;
         if(AuszahlungAngefordert())
            Meldung(StringFormat("KONTO FLACH - Auszahlung beantragt am %s, noch nicht gebucht: Gewinn %.2f, auszahlbar %.2f. EA bleibt flach, bis der Saldo-Deal da ist (danach AuszahlungAngefordertAm leeren).",
                    AuszahlungAngefordertAm, p, AuszahlbarJetzt()));
         else
            Meldung(StringFormat("KONTO FLACH - JETZT AUSZAHLUNG BEANTRAGEN: Gewinn %.2f, auszahlbar %.2f (Deckel %s), Anteil %.2f. EA wartet auf den Saldo-Deal.",
                    p, AuszahlbarJetzt(), (kPayouts < PayoutCapCount ? "aktiv" : "keiner"), AuszahlbarJetzt()*ProfitSplit));
        }
     }

   if(WeAktiv) WochenendePruefen(keineEinstiege);

   // 6.40: Schutz gueltiger Tage vor JEDEM Modul neu bewerten - ein Ausstieg eines vorher laufenden Moduls (oder ein
   //       Broker-Stop/-Ziel) kann den Tag eben gueltig gemacht haben (nach einer Positionsaenderung wird die Historie neu geladen)
   GueltigSchutzPruefen(today);
   for(int k=0;k<nSym;k++) HandleSymbol(k, today, keineEinstiege || gGueltigSchutz);   // 6.40: Schutz gueltiger Tage (Verwaltung laeuft weiter)
   GueltigSchutzPruefen(today);
   for(int k=nSym;k<nSlot;k++) HandleR21(k, today, keineEinstiege);   // 4.40; Folgesignale werden weiter gemerkt (6.50: Schutz gueltiger Tage in HandleR21 zur Signalzeit)
   GueltigSchutzPruefen(today);
   NzDurchlauf(keineEinstiege);                                        // 5.00: NAS-Noise-Modul (6.40: Schutz ueber gGueltigSchutz in NzBar)
   GueltigSchutzPruefen(today);
   FadeDurchlauf(keineEinstiege);                                      // 6.00: Fade-Module (virtuell + live, Zeit-Ausstieg, Ziel; 6.40: Schutz in FadeLive)

   if(HarvestMode>0 && !dayLocked)
     {
      double flt2 = FloatingPnlDb();                                     // 4.40: Bedingung nur auf DEADBAND-Floating
      if(flt2 > 0.0) HarvestPruefen(today, flt2);
     }
   MfeAktualisieren();                                                 // 6.10: Kursvorlauf der Noise-/Fade-Positionen (Abschluss-Ernte)
   if(AbschlussLetzte > 0 && !dayLocked) AbschlussErntePruefen();      // 5.10: Auszahlungstakt (letzte gueltige Tage); 6.10 alle Module
   if(GeAktiv && kMode==0) GewinnErntePruefen();
   ZyklusPanel();
  }

// StopMode 1/2: bei Reife eigene Positionen schliessen, wenn die Reife danach noch steht
void ReifeSchliessen()
  {
   double pnl = 0.0;
   for(int k=0;k<nSym;k++)
     {
      ulong tk=0; if(!HavePosition(k,tk) || !PositionSelectByTicket(tk)) continue;
      double p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
      if(StopMode==2 && p<=0.0) continue;
      pnl += p;
     }
   double schwelle = GueltigSchwelle();                                  // 6.10: 0,5 % + Reserve
   int v = kValidDays + ((GueltigHeuteZaehlt && kTodayReal + pnl >= schwelle) ? 1 : 0);
   if(v < NeedValidDays || AccountInfoDouble(ACCOUNT_BALANCE) + pnl - kStart < kMinProfit) return;
   for(int k=0;k<nSym;k++)
     {
      ulong tk=0; if(!HavePosition(k,tk) || !PositionSelectByTicket(tk)) continue;
      double p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
      if(StopMode==2 && p<=0.0) continue;
      if(!Schliesse(tk))
         PrintFormat("DEADBAND4 %s: Schliessen bei Reife abgelehnt (%d %s)", S[k].sym, trade.ResultRetcode(), trade.ResultRetcodeDescription());
     }
  }

//+------------------------------------------------------------------+
//| Ernte (wie 3.00 / Build 2.52)                                     |
//+------------------------------------------------------------------+
bool ErnteMoeglich(int k)
  {
   if(S[k].lastHarvTry>0 && TimeCurrent()-S[k].lastHarvTry < 60) return false;
   long tmode = SymbolInfoInteger(S[k].sym, SYMBOL_TRADE_MODE);
   if(tmode==SYMBOL_TRADE_MODE_DISABLED) return false;
   datetime lastTick = (datetime)SymbolInfoInteger(S[k].sym, SYMBOL_TIME);
   if(lastTick>0 && TimeCurrent()-lastTick > 120) return false;
   return true;
  }

void HarvestPruefen(long today, double flt)
  {
   double schwelle = GueltigSchwelle();                                  // 6.10: 0,5 % + Reserve
   double need     = schwelle*(1.0+HarvestMargin);
   double real     = MathMax(kTodayReal, kTodayRealSchaetz);             // 6.10: eigene Ernte zaehlt, bis die Deals da sind
   if(real >= schwelle) return;
   if(real + flt < need) return;
   bool fenster = (HarvestMode==1);
   if(HarvestMode==2)
     {
      double nyH = NYHour(TimeCurrent());
      fenster = (nyH >= HarvestFromNY && nyH < 17.0);
     }
   if(!fenster && HarvestAnyR<=0.0) return;
   // 4.10: zweite Stufe - im Fenster reicht HarvestMinR2 Vorlauf, wenn nur noch HarvestGapFrac * Schwelle fehlt
   bool stufe2 = (fenster && HarvestMinR2>0.0 && (need-real) <= HarvestGapFrac*schwelle);
   double gain=0.0;
   for(int k=0;k<nSlot;k++)
     {
      ulong tk=0; if(!HavePosition(k,tk) || !PositionSelectByTicket(tk)) continue;
      if(!ErnteMoeglich(k)) continue;
      double p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
      bool kand = (fenster && S[k].mfeR>=HarvestMinR) || (HarvestAnyR>0.0 && S[k].mfeR>=HarvestAnyR) || (stufe2 && S[k].mfeR>=HarvestMinR2);
      if(p>0.0 && kand && GewinnSchlussOk(tk, p)) gain+=p;                 // 4.90: 2-Minuten- und News-Regel
     }
   if(real + gain < need) return;
   for(int k=0;k<nSlot;k++)
     {
      ulong tk=0; if(!HavePosition(k,tk) || !PositionSelectByTicket(tk)) continue;
      if(!ErnteMoeglich(k)) continue;
      double p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
      bool kand = (fenster && S[k].mfeR>=HarvestMinR) || (HarvestAnyR>0.0 && S[k].mfeR>=HarvestAnyR) || (stufe2 && S[k].mfeR>=HarvestMinR2);
      if(p<=0.0 || !kand) continue;
      if(!GewinnSchlussOk(tk, p)) continue;                                // 4.90
      double vol = PositionGetDouble(POSITION_VOLUME);
      double lots = vol;
      if(HarvestPartial)
        {
         double stp = SymbolInfoDouble(S[k].sym, SYMBOL_VOLUME_STEP); if(stp<=0.0) stp=0.01;
         double perLot = p/vol;
         lots = MathCeil((need-real)/perLot/stp - 1e-9)*stp;
         if(lots < stp) lots = stp;
         if(lots > vol - stp) lots = vol;
         double mnvH = SymbolInfoDouble(S[k].sym, SYMBOL_VOLUME_MIN);     // 4.90: Teil- und Restvolumen nie unter dem Mindestlot
         if(mnvH > 0.0 && lots < mnvH) lots = mnvH;
         if(mnvH > 0.0 && vol - lots < mnvH - 1e-9) lots = vol;
         lots = NormalizeDouble(lots, 2);
        }
      bool ok = (lots>=vol) ? Schliesse(tk) : SchliesseTeil(tk, lots);
      if(ok)
        {
         PrintFormat("DEADBAND4 %s: Ernte %.2f von %.2f Lot - Tag realisiert %.2f, Buchgewinn %.2f, Schwelle %.2f", S[k].sym, lots, vol, real, p, schwelle);
         real += p*(lots/vol);
         kTodayRealSchaetz = real; kSchaetzZeit = TimeCurrent();          // 6.10: Reife nur aus bestaetigten Deals, Schaetzung 30 s gueltig
         if(real >= need) break;
        }
      else
        {
         S[k].lastHarvTry = TimeCurrent();
         PrintFormat("DEADBAND4 %s: Ernte abgelehnt (%d %s) - 60 s Pause", S[k].sym, trade.ResultRetcode(), trade.ResultRetcodeDescription());
        }
     }
  }

//+------------------------------------------------------------------+
//| 5.10 Abschluss-Ernte (Auszahlungstakt)                            |
//|  Die gueltigen Tage sind der Engpass des Zyklus. Fehlen nur noch  |
//|  AbschlussLetzte gueltige Tage (Zyklus laeuft, Saldo >= Start-    |
//|  saldo) und ist heute noch nicht gueltig, wird DEADBAND-Gewinn    |
//|  (bester Kurs >= AbschlussMinR) im Fenster JEDERZEIT so weit      |
//|  realisiert (Teilverkauf), dass der Tag gueltig wird - wie die    |
//|  Tagesernte, aber ohne 16:00-Fenster und ohne 2-R-Vorlauf.        |
//+------------------------------------------------------------------+
datetime abFehl[MAXSYM];                  // 6.10: letzte abgelehnte Ernte je Symbol (Positionen ohne Platz)
void AbschlussErntePruefen()
  {
   if(AbschlussLetzte <= 0 || kMode > 1 || kCycleStart <= 0 || kStart <= 0.0) return;
   double schwelle = GueltigSchwelle();                                  // 6.10: 0,5 % + Reserve
   double real     = MathMax(kTodayReal, kTodayRealSchaetz);             // 6.10: eigene Ernte zaehlt, bis die Deals da sind
   if(real >= schwelle) return;
   if(GueltigeTageMitHeute() < NeedValidDays - AbschlussLetzte) return;
   if(AccountInfoDouble(ACCOUNT_BALANCE) < kStart) return;
   double nyH = NYHour(TimeCurrent());
   if(nyH < AbschlussAbNY || nyH >= AbschlussBisNY) return;
   double need = schwelle*(1.0+HarvestMargin);
   // 6.10: Kandidaten aller gewaehlten Module in der Reihenfolge des Replikats: DEADBAND, RSI21, Noise, Fades
   ulong ktk[]; double kp[], kmfe[]; int kslot[]; int nk = 0;
   double gain = 0.0;
   for(int k=0;k<nSlot;k++)                                                 // DEADBAND- und RSI21-Plaetze
     {
      bool db = (k < nSym);
      if(( db && (AbschlussModule & 1) == 0) || (!db && (AbschlussModule & 2) == 0)) continue;
      ulong tk=0; if(!HavePosition(k,tk) || !PositionSelectByTicket(tk)) continue;
      if(!ErnteMoeglich(k)) continue;
      double p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP)
                 - KomRundJeLot(S[k].sym)*PositionGetDouble(POSITION_VOLUME);         // netto: GFT rechnet die Kommission dem Tag an
      if(p<=0.0 || S[k].mfeR<AbschlussMinR || !GewinnSchlussOk(tk, p)) continue;
      ArrayResize(ktk,nk+1); ArrayResize(kp,nk+1); ArrayResize(kmfe,nk+1); ArrayResize(kslot,nk+1);
      ktk[nk] = tk; kp[nk] = p; kmfe[nk] = S[k].mfeR; kslot[nk] = k; nk++; gain += p;
     }
   for(int art=0;art<2;art++)                                               // Noise-Teile, dann Fades (Modul-Reihenfolge)
     {
      if(art == 0 && (AbschlussModule & 4) == 0) continue;
      if(art == 1 && (AbschlussModule & 8) == 0) continue;
      int nMax = (art == 0 ? 8 : MAXFADE);
      for(int q=0;q<nMax;q++)
        {
         long mg = (art == 0 ? NzMagic(q) : FadeMagic(q));
         for(int i=PositionsTotal()-1;i>=0;i--)
           {
            ulong tk = PositionGetTicket(i); if(tk == 0) continue;
            if(PositionGetInteger(POSITION_MAGIC) != mg) continue;
            if(art == 0 ? !IsNzMagic(mg) : !IsFadeMagic(mg)) continue;
            string sy = PositionGetString(POSITION_SYMBOL);
            if(!SchliessenMoeglich(sy)) continue;
            double p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP)
                       - KomRundJeLot(sy)*PositionGetDouble(POSITION_VOLUME);
            double mf = PosMfe(tk);
            if(!PositionSelectByTicket(tk)) continue;
            if(p<=0.0 || mf<AbschlussMinR || !GewinnSchlussOk(tk, p)) continue;
            ArrayResize(ktk,nk+1); ArrayResize(kp,nk+1); ArrayResize(kmfe,nk+1); ArrayResize(kslot,nk+1);
            ktk[nk] = tk; kp[nk] = p; kmfe[nk] = mf; kslot[nk] = -1; nk++; gain += p;
           }
        }
     }
   if(nk == 0 || real + gain < need) return;
   for(int c=0;c<nk;c++)
     {
      ulong tk = ktk[c];
      if(!PositionSelectByTicket(tk)) continue;
      string sy = PositionGetString(POSITION_SYMBOL);
      double p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP) - KomRundJeLot(sy)*PositionGetDouble(POSITION_VOLUME);
      if(p <= 0.0 || !GewinnSchlussOk(tk, p) || !PositionSelectByTicket(tk)) continue;
      double vol = PositionGetDouble(POSITION_VOLUME);
      double stp = SymbolInfoDouble(sy, SYMBOL_VOLUME_STEP); if(stp<=0.0) stp=0.01;
      double perLot = p/vol;
      double lots = MathCeil((need-real)/perLot/stp - 1e-9)*stp;
      if(lots < stp) lots = stp;
      if(lots > vol - stp) lots = vol;
      double mnv = SymbolInfoDouble(sy, SYMBOL_VOLUME_MIN);                  // Teil- und Restvolumen nie unter dem Mindestlot
      if(mnv > 0.0 && lots < mnv) lots = mnv;
      if(mnv > 0.0 && vol - lots < mnv - 1e-9) lots = vol;
      lots = NormalizeDouble(lots, 2);
      bool ok = (lots>=vol) ? Schliesse(tk) : SchliesseTeil(tk, lots);
      if(ok)
        {
         PrintFormat("DEADBAND4 %s: ABSCHLUSS-ERNTE %.2f von %.2f Lot (%s, Vorlauf %.2f R) - Tag realisiert %.2f, Buchgewinn %.2f, Schwelle %.2f, gueltige Tage %d/%d",
                     sy, lots, vol, (kslot[c] >= 0 ? (kslot[c] < nSym ? "DEADBAND" : "RSI21") : (IsFadeMagic(PositionGetInteger(POSITION_MAGIC)) ? "Fade" : "Noise")),
                     kmfe[c], real, p, schwelle, GueltigeTageMitHeute(), NeedValidDays);
         real += p*(lots/vol);
         kTodayRealSchaetz = real; kSchaetzZeit = TimeCurrent();          // 6.10: Reife nur aus bestaetigten Deals, Schaetzung 30 s gueltig
         if(real >= need) break;
        }
      else
        {
         if(kslot[c] >= 0) S[kslot[c]].lastHarvTry = TimeCurrent();
         else { int si = SymIndex(sy); if(si >= 0) abFehl[si] = TimeCurrent(); }
         PrintFormat("DEADBAND4 %s: Abschluss-Ernte abgelehnt (%d %s) - 60 s Pause", sy, trade.ResultRetcode(), trade.ResultRetcodeDescription());
        }
     }
  }

// 6.10: Schliessen im Symbol moeglich (Handel erlaubt, Kurse frisch, nach Ablehnung 60 s Pause) - fuer Positionen ohne Platz
bool SchliessenMoeglich(const string sy)
  {
   int si = SymIndex(sy);
   if(si >= 0 && abFehl[si] > 0 && TimeCurrent() - abFehl[si] < 60) return false;
   if(SymbolInfoInteger(sy, SYMBOL_TRADE_MODE) == SYMBOL_TRADE_MODE_DISABLED) return false;
   datetime lastTick = (datetime)SymbolInfoInteger(sy, SYMBOL_TIME);
   if(lastTick > 0 && TimeCurrent() - lastTick > 120) return false;
   return true;
  }

// 6.10: bester Kursvorlauf (MFE in R) je Position ohne Platz (Noise, Fades), wie p_mfe im Replikat. R = Stop-Abstand beim
// ersten Sehen; nach einem Neustart aus den M5-Kerzen seit dem Einstieg rekonstruiert. MfeAktualisieren() laeuft je Durchlauf.
#define MFEMAX 64
ulong    gMfeTk[MFEMAX]; double gMfeR[MFEMAX], gMfeRd[MFEMAX]; int gMfeN = 0;
double PosMfe(const ulong tk)
  {
   if(!PositionSelectByTicket(tk)) return 0.0;
   string sy = PositionGetString(POSITION_SYMBOL);
   double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL);
   int d = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1);
   int i = -1;
   for(int q=0;q<gMfeN;q++) if(gMfeTk[q] == tk) { i = q; break; }
   if(i < 0)
     {
      double rd = (sl > 0.0 ? MathAbs(op - sl) : 0.0);
      if(sl > 0.0 && (sl - op)*d >= 0.0) { rd = UrStopAbstand(tk); if(!PositionSelectByTicket(tk)) return 0.0; }   // 6.30: Stop auf Einstand -> R der Eroeffnung
      if(rd <= 0.0) return 0.0;
      if(gMfeN >= MFEMAX) MfeAufraeumen();
      if(gMfeN >= MFEMAX) return 0.0;
      double best = 0.0;
      datetime t0 = (datetime)PositionGetInteger(POSITION_TIME);
      double pt = SymbolInfoDouble(sy, SYMBOL_POINT);
      MqlRates r[];
      int n = (TimeCurrent() - t0 > 60) ? CopyRates(sy, PERIOD_M5, t0, TimeCurrent(), r) : 0;
      for(int j=0;j<n;j++)
        {
         double f = (d > 0) ? (r[j].high - op) : (op - (r[j].low + r[j].spread*pt));
         if(f/rd > best) best = f/rd;
        }
      i = gMfeN; gMfeTk[i] = tk; gMfeRd[i] = rd; gMfeR[i] = best; gMfeN++;
      if(!PositionSelectByTicket(tk)) return best;
     }
   double bid = SymbolInfoDouble(sy, SYMBOL_BID), ask = SymbolInfoDouble(sy, SYMBOL_ASK);
   if(bid > 0.0 && ask > 0.0)
     {
      double fav = (d > 0) ? (bid - op) : (op - ask);
      if(fav/gMfeRd[i] > gMfeR[i]) gMfeR[i] = fav/gMfeRd[i];
     }
   return gMfeR[i];
  }
void MfeAufraeumen()
  {
   int w = 0;
   for(int q=0;q<gMfeN;q++)
      if(PositionSelectByTicket(gMfeTk[q])) { gMfeTk[w] = gMfeTk[q]; gMfeR[w] = gMfeR[q]; gMfeRd[w] = gMfeRd[q]; w++; }
   gMfeN = w;
  }
void MfeAktualisieren()
  {
   static datetime aufr = 0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      long mg = PositionGetInteger(POSITION_MAGIC);
      if(IsNzMagic(mg) || IsFadeMagic(mg)) PosMfe(tk);
     }
   if(TimeCurrent() - aufr >= 60) { aufr = TimeCurrent(); MfeAufraeumen(); }
  }


//+------------------------------------------------------------------+
//| 4.20 Gewinn-Ernte: nur der Mindestgewinn fehlt zur Auszahlung.     |
//| Kandidat = eigene Position im Plus, bester Kurs >= GeMinR und      |
//| GeRueckgangR vom besten Kurs zurueck. Reicht der Buchgewinn der    |
//| Kandidaten fuer Start + Mindestgewinn x (1 + Aufschlag), werden   |
//| sie GANZ geschlossen, bis das Ziel steht (Konto flach -> Reife).  |
//+------------------------------------------------------------------+
double GeZiel() { return kStart + kMinProfit*(1.0+GeAufschlag); }

// Kandidat? Liefert den Buchgewinn (Profit + Swap - geschaetzte Schlusskommission), sonst 0.
double GeKandidat(int k)
  {
   ulong tk=0;
   if(!HavePosition(k,tk) || !PositionSelectByTicket(tk)) return 0.0;
   if(S[k].rDist <= 0.0) return 0.0;
   long   type = PositionGetInteger(POSITION_TYPE);
   double bid  = SymbolInfoDouble(S[k].sym, SYMBOL_BID);
   double ask  = SymbolInfoDouble(S[k].sym, SYMBOL_ASK);
   double favR = (type==POSITION_TYPE_BUY) ? (bid - S[k].refPx)/S[k].rDist : (S[k].refPx - ask)/S[k].rDist;
   if(favR > S[k].mfeR) S[k].mfeR = favR;
   double p = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP)
              - KommissionJeLot(S[k].sym)*PositionGetDouble(POSITION_VOLUME);
   if(p <= 0.0) return 0.0;
   if(S[k].mfeR < GeMinR) return 0.0;
   if(S[k].mfeR - favR < GeRueckgangR) return 0.0;
   return p;
  }

void GewinnErntePruefen()
  {
   if(!NurMindestgewinnFehlt()) return;
   double nyH = NYHour(TimeCurrent());
   if(nyH < GeAbNY || nyH >= GeBisNY) return;
   double bal   = AccountInfoDouble(ACCOUNT_BALANCE);
   double fehlt = GeZiel() - bal;
   if(fehlt <= 0.0) return;
   double pk[MAXSLOT]; double gain = 0.0;
   for(int k=0;k<nSlot;k++)
     {
      pk[k] = 0.0;
      if(!ErnteMoeglich(k)) continue;
      pk[k] = GeKandidat(k);
      if(pk[k] > 0.0) { ulong tq=0; if(HavePosition(k,tq) && !GewinnSchlussOk(tq, pk[k])) pk[k] = 0.0; }   // 4.90
      gain += pk[k];
     }
   if(gain < fehlt) return;
   for(int k=0;k<nSlot;k++)
     {
      if(pk[k] <= 0.0) continue;
      ulong tk=0; if(!HavePosition(k,tk)) continue;
      if(Schliesse(tk))
        {
         PrintFormat("DEADBAND4 %s: GEWINN-ERNTE %.2f (Vorlauf %.2f R, Rueckgang-Regel %.2f R) - Saldo %.2f, Ziel %.2f, Gewinn danach %.2f",
                     S[k].sym, pk[k], S[k].mfeR, GeRueckgangR, bal, GeZiel(), bal + pk[k] - kStart);
         bal += pk[k];
         if(bal >= GeZiel()) break;
        }
      else
        {
         S[k].lastHarvTry = TimeCurrent();
         PrintFormat("DEADBAND4 %s: Gewinn-Ernte abgelehnt (%d %s) - 60 s Pause", S[k].sym, trade.ResultRetcode(), trade.ResultRetcodeDescription());
        }
     }
  }

string GeStatusText()
  {
   if(!GeAktiv) return "aus";
   if(kMode!=0) return "-";
   if(NurMindestgewinnFehlt()) return StringFormat("BEREIT (fehlen %.2f)", GeZiel() - AccountInfoDouble(ACCOUNT_BALANCE));
   return StringFormat("wartet (%.2f R Rueckgang)", GeRueckgangR);
  }

//+------------------------------------------------------------------+
//| Panel                                                             |
//+------------------------------------------------------------------+
void ZyklusPanel()
  {
   if(!ShowPanel) return;
   double bal = AccountInfoDouble(ACCOUNT_BALANCE), eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double schwelle = GueltigSchwelle();                                  // 6.10: 0,5 % + Reserve
   double boden = kPeakEq - kStart*MaxLossPct/100.0;
   double buf = PufferPct();
   int vHeute = ((GueltigHeuteZaehlt && kTodayReal >= schwelle) ? 1 : 0);
   long zykTag = (kCycleStart>0 ? PropDayIndex(TimeCurrent()) - PropDayIndex(kCycleStart) : 0);
   string status = (kMode==0 ? "sammeln" : (kMode==1 ? "REIF - keine neuen Einstiege, offene laufen aus" : "AUSZAHLUNG BEANTRAGEN - EA wartet auf den Saldo-Deal"));
   double fltAll = FloatingPnl(CountForeignPositions);
   string txt = "";
   if(kMode==2)
      txt += StringFormat("=== AUSZAHLUNG BEANTRAGEN: Konto flach, Gewinn %.2f, auszahlbar %.2f, Anteil %.2f ===\n", bal-kStart, AuszahlbarJetzt(), AuszahlbarJetzt()*ProfitSplit);
   if(SerienPause()) status += " | SERIEN-STOPP bis 17:00 NY";
   if(gGueltigSchutz) status += " | TAG GUELTIG - Schutz bis 17:00 NY (Umfang: Auszahlungstakt)";   // 6.40 (6.50: je Modul)
   txt += StringFormat(
      "DEADBAND LIVE 6.50 NETTO   %s\n"
      "  Startsaldo        %.2f   (Einzahlung %s, %d Auszahlungen, Deckel %s)\n"
      "  Saldo / Equity    %.2f / %.2f   Gewinn %.2f   (Mindestgewinn %.2f)\n"
      "  Zyklus seit       %s   Tag %d / %d\n"
      "  gueltige Tage     %d / %d   (+%d heute, ab %.2f)   Handelstage %d\n"
      "  heute realisiert  %.2f   Tagesstart %.2f   Tag %.2f / Grenze %.2f\n"
      "  Buchgewinn        %.2f   Grenze %.2f   (Bremse %.2f)\n"
      "  Boden             %.2f   Puffer %.2f (%.2f %%)   Groesse x%.2f%s\n"
      "  Ernte %s   Gewinn-Ernte %s   NY-Versatz %d h   Regeln auf %s Positionen",
      status, kStart, (kAccountFrom>0 ? TimeToString(kAccountFrom, TIME_DATE) : "?"), kPayouts, (kPayouts<PayoutCapCount ? StringFormat("%.0f%%", PayoutCapPct) : "keiner"),
      bal, eq, bal-kStart, kMinProfit,
      (kCycleStart>0 ? TimeToString(kCycleStart, TIME_DATE) : "noch kein Trade"), (int)zykTag, CycleDays,
      kValidDays, NeedValidDays, vHeute, schwelle, kTradeDays,
      kTodayReal, kDayStartBal, eq-kDayStartBal, -kDayStartBal*RuleDayLossPct/100.0,
      fltAll, -FloatBasis()*kRuleFloatPct/100.0, -FloatBasis()*FloatStopPct/100.0,
      boden, eq-boden, buf, DDFaktor(buf)*(eq<kStart ? BelowStartMult : 1.0)*RiskMult, (eq<kStart && BelowStartMult!=1.0 ? " (unter Start)" : ""),
      (HarvestMode==0 ? "aus" : (HarvestMode==1 ? "jederzeit" : StringFormat("ab %.0f NY", HarvestFromNY))), GeStatusText(), nyOff,
      (CountForeignPositions ? "alle" : "eigene"));
   txt += "\n  Wochenend-Pause   " + WeStatusText();
   txt += "\n  RSI21-Modul       " + R21StatusText();
   txt += "\n  NAS-Noise-Modul   " + NzStatusText();                     // 5.00
   txt += "\n  Fade-Module       " + FadeStatusText();                   // 6.00
   txt += "\n  Probability Grid  " + GridStatusText();                   // 6.20
   txt += "\n  Trefferquote      " + TrefferStatusText();                // 6.30
   txt += "\n  Auszahlungstakt   " + TaktStatusText();                   // 6.40
   txt += "\n  DEADBAND          " + (DbAktiv ? "Einstiege an" : "Einstiege AUS (DbAktiv=false, offene werden verwaltet)");
   txt += "\n  GFT-Schutz        " + SchutzStatusText();                    // 4.90
   txt += StringFormat("\n  5.10              Verlierer %.2f (Bremse %s) | Idee max %s | Swap-Vorsorge %s | %s | Abschluss-Ernte %s",
                       FloatingVerlierer(CountForeignPositions), (FloatNurVerlierer ? "auf Verlierer" : "netto"),
                       (IdeeMaxRisikoPct > 0.0 ? StringFormat("%.2f %%", IdeeMaxRisikoPct) : "aus"),
                       (SwapVorsorgePct > 0.0 && SwapVorsorgeMin > 0 ? StringFormat("-%.2f %%", SwapVorsorgePct) : "aus"), SerienText(),
                       (AbschlussLetzte <= 0 ? "aus" : (kCycleStart > 0 && GueltigeTageMitHeute() >= NeedValidDays - AbschlussLetzte && vHeute == 0 && bal >= kStart ? "BEREIT" : "wartet")));
   if(ShowLeiter)
     {
      double stufen[6] = {10000,15000,25000,50000,100000,150000};
      double preise[6] = {148.50,198.50,281.50,406.50,656.50,1065.00};
      int hier = 0;
      for(int q=0;q<6;q++) if(MathAbs(kStart-stufen[q]) < stufen[q]*0.10) hier = q;
      int ziel = -1;
      for(int q=5;q>hier;q--) if(Barreserve >= preise[q]*(1.0+KaufPuffer)) { ziel = q; break; }
      if(ziel >= 0)
         txt += StringFormat("\nLeiter: %.0f $ Reserve traegt die %.0fk-Stufe (%.2f $) plus %.0f Neukaeufe -> KAUFEN", Barreserve, stufen[ziel]/1000.0, preise[ziel], KaufPuffer);
      else if(hier < 5)
         txt += StringFormat("\nLeiter: %.0f $ Reserve. Fuer %.0fk fehlen %.2f $ (Preis %.2f + %.0f Neukaeufe)",
                             Barreserve, stufen[hier+1]/1000.0, preise[hier+1]*(1.0+KaufPuffer)-Barreserve, preise[hier+1], KaufPuffer);
      else
         txt += "\nLeiter: groesste Einzelstufe erreicht.";
     }
   Comment(txt);
  }

//+------------------------------------------------------------------+
//| Handel je Symbol (Kern wie 3.00, Groesse nach Puffer)             |
//+------------------------------------------------------------------+
void HandleSymbol(int k, long today, bool dayLocked)
  {
   string s = S[k].sym;
   ulong  ticket=0;
   bool   inPos = HavePosition(k, ticket);

   if(inPos && PositionSelectByTicket(ticket))
     {
      bool mayTry = (S[k].closeFails==0) || (TimeCurrent()-S[k].lastCloseTry >= 60);
      long tmode  = SymbolInfoInteger(s, SYMBOL_TRADE_MODE);
      if(tmode==SYMBOL_TRADE_MODE_DISABLED) mayTry=false;                // 4.90: CLOSEONLY erlaubt Schliessen und Stop-Nachzug
      if(mayTry && S[k].rDist>0.0)
        {
         long   type   = PositionGetInteger(POSITION_TYPE);
         double bid    = SymbolInfoDouble(s, SYMBOL_BID);
         double ask    = SymbolInfoDouble(s, SYMBOL_ASK);
         double volNow = PositionGetDouble(POSITION_VOLUME);
         bool   acted=false, failed=false;
         double ref = (S[k].refPx > 0.0 ? S[k].refPx : S[k].entryPx);   // 4.30: R-Stufen vom Bezugskurs
         double favR = (type==POSITION_TYPE_BUY) ? (bid - ref)/S[k].rDist : (ref - ask)/S[k].rDist;
         if(favR > S[k].mfeR) S[k].mfeR = favR;
         bool tp1Ok = GewinnSchlussOk(ticket, PositionGetDouble(POSITION_PROFIT));  // 5.10: Teilverkauf erst nach MinHalteSek (2-Minuten-Regel) und ausserhalb der News
         if(!PositionSelectByTicket(ticket)) return;
         if(type==POSITION_TYPE_BUY)
           {
            if(!S[k].t1Done && S[k].vol1>0.0 && bid >= ref + Tp1R*S[k].rDist && volNow>S[k].vol1 && tp1Ok)
              { acted=true; if(SchliesseTeil(ticket, S[k].vol1)) { S[k].t1Done=true; volNow-=S[k].vol1; } else failed=true; }
            if(!S[k].t2Done && S[k].vol2>0.0 && bid >= ref + Tp2R*S[k].rDist && volNow>S[k].vol2)
              { acted=true; if(SchliesseTeil(ticket, S[k].vol2)) { S[k].t2Done=true; volNow-=S[k].vol2; } else failed=true; }
           }
         else
           {
            if(!S[k].t1Done && S[k].vol1>0.0 && ask <= ref - Tp1R*S[k].rDist && volNow>S[k].vol1 && tp1Ok)
              { acted=true; if(SchliesseTeil(ticket, S[k].vol1)) { S[k].t1Done=true; volNow-=S[k].vol1; } else failed=true; }
            if(!S[k].t2Done && S[k].vol2>0.0 && ask <= ref - Tp2R*S[k].rDist && volNow>S[k].vol2)
              { acted=true; if(SchliesseTeil(ticket, S[k].vol2)) { S[k].t2Done=true; volNow-=S[k].vol2; } else failed=true; }
           }
         bool t1Level = (type==POSITION_TYPE_BUY) ? (bid >= ref + Tp1R*S[k].rDist) : (ask <= ref - Tp1R*S[k].rDist);
         if(UseBeAfterT1 && (S[k].t1Done || t1Level) && !S[k].beDone && !failed
            && (S[k].lastBeTry==0 || TimeCurrent()-S[k].lastBeTry >= 60))
           {
            int    dg2   = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
            double pt2   = SymbolInfoDouble(s, SYMBOL_POINT);
            long   stl   = SymbolInfoInteger(s, SYMBOL_TRADE_STOPS_LEVEL);
            double minD  = (stl>0 ? stl*pt2 : 0.0);
            double curSl = PositionGetDouble(POSITION_SL);
            double curTp = PositionGetDouble(POSITION_TP);
            double newSl = (type==POSITION_TYPE_BUY) ? ref + BeAfterT1R*S[k].rDist : ref - BeAfterT1R*S[k].rDist;
            newSl = NormalizeDouble(newSl, dg2);
            bool besser = (curSl <= 0.0) || ((type==POSITION_TYPE_BUY) ? (newSl > curSl) : (newSl < curSl));
            bool erlaubt = (type==POSITION_TYPE_BUY) ? (newSl <= bid - minD) : (newSl >= ask + minD);
            if(!besser) S[k].beDone = true;
            else if(erlaubt)
              {
               S[k].lastBeTry = TimeCurrent();
               if(trade.PositionModify(ticket, newSl, curTp)) { S[k].beDone = true; S[k].slPx = newSl; }
               else PrintFormat("DEADBAND4 %s: Stop-Nachzug abgelehnt (%d %s) - 60 s Pause", s, trade.ResultRetcode(), trade.ResultRetcodeDescription());
              }
           }
         int held = iBarShift(s, PERIOD_M15, S[k].entryBarTime, false);
         if(held < 0) held = 0;
         long maxSek = (long)MaxHoldBars*PeriodSeconds(PERIOD_M15)*3;
         bool zuLang = (held >= MaxHoldBars) || (TimeCurrent() - S[k].entryBarTime >= maxSek);
         if(!failed && MaxHoldBars>0 && zuLang && GewinnSchlussOk(ticket, PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP)))   // 4.90
           { acted=true; if(!Schliesse(ticket)) failed=true; else return; }
         if(acted)
           {
            S[k].lastCloseTry = TimeCurrent();
            S[k].closeFails   = failed ? S[k].closeFails+1 : 0;
            if(S[k].closeFails==1)
               PrintFormat("DEADBAND4 %s: Schliessung fehlgeschlagen (%d %s) - 60 s Pause", s, trade.ResultRetcode(), trade.ResultRetcodeDescription());
           }
        }
     }

   // --- ab hier nur einmal je neuer M15-Kerze ----
   datetime bt = iTime(s, PERIOD_M15, 0);
   if(bt<=0 || bt==S[k].lastBar) return;
   S[k].lastBar = bt;
   if(!MQLInfoInteger(MQL_TESTER) && kBereitAb > 0 && bt < kBereitAb - 30) return;   // 4.90: Kerze lief schon vor der Bereitschaft (Kaltstart) - kein verspaeteter Einstieg
   long bday = PropDayIndex(bt);
   if((datetime)bday != S[k].curDay) { S[k].curDay=(datetime)bday; S[k].tradesToday=0; }

   if(inPos || HavePosition(k, ticket)) return;
   if(!inPos) WeAktivLoeschen(k);                      // 4.30: Merkmale der wiederaufgenommenen Position sind erledigt
   if(dayLocked) return;
   if(kMode != 0) return;                              // reif oder wartend: keine Einstiege
   if(!DbAktiv) return;                                // 6.00: DEADBAND-Einstiege abschaltbar (Verwaltung oben laeuft weiter)
   if(SerienPause()) return;                           // 5.10: Serien-Stopp nach SerienStopp Verlusttrades in Folge
   if(WeAktiv && W[k].aktiv) return;                   // 4.30: Wiederaufnahme wartet - kein Neueinstieg auf diesem Symbol
   if(WeAktiv && KurzVorSchluss(bt)) return;          // 4.30/4.90: Freitag/Sondertag ab SchlussVorlaufMin vor der Schliessung
   if(NewsFenster(TimeCurrent())) return;             // 4.90: GFT-News-Regel (Einstieg im Fenster = Gewinn gekappt)
   if(S[k].tradesToday >= MaxTradesDay) return;
   if(LossesToday(k, bday) >= MaxLossDay) return;

   double nyH = NYHour(bt);
   if(nyH < SessStartNY || nyH >= SessEndNY) return;

   double h1 = iHigh(s, PERIOD_H1, 1);
   double l1 = iLow (s, PERIOD_H1, 1);
   if(h1<=0.0 || l1<=0.0) return;
   double emaBuf[]; if(CopyBuffer(S[k].hEma, 0, 1, 1, emaBuf)<1) return;
   double rsiBuf[]; if(CopyBuffer(S[k].hRsi, 0, 1, 1, rsiBuf)<1) return;
   double emaD=emaBuf[0], rsiV=rsiBuf[0];
   double vw = UseVwap ? SessionVwap(s) : 0.0;
   if(UseVwap && vw<=0.0) return;
   double h=iHigh(s,PERIOD_M15,1), l=iLow(s,PERIOD_M15,1), c=iClose(s,PERIOD_M15,1);
   double rng = h-l;
   double clsP = (rng>0.0 ? (c-l)/rng : 0.5);
   bool trendL=(!UseTrend||c>emaD), trendS=(!UseTrend||c<emaD);
   bool vwapL =(!UseVwap ||c>vw  ), vwapS =(!UseVwap ||c<vw  );
   bool rsiL  =(!UseRsi  ||rsiV>RsiLvl), rsiS=(!UseRsi||rsiV<RsiLvl);
   bool macdL = true, macdS = true;
   if(UseMacd)
     {
      double mMain[], mSig[];
      if(CopyBuffer(S[k].hMacd, 0, 1, 1, mMain)<1) return;
      if(CopyBuffer(S[k].hMacd, 1, 1, 1, mSig )<1) return;
      double hist = mMain[0] - mSig[0];
      macdL = (hist > 0.0); macdS = (hist < 0.0);
     }
   double cm = S[k].clsMin;
   bool qualL =(!UseCls  ||clsP>=cm), qualS=(!UseCls||(1.0-clsP)>=cm);
   if(UseVolume)
     {
      double vr = VolRel(s, VolLen);
      if(vr < 0.0) return;
      if(vr < VolMin) return;
     }
   bool sigL = (c>h1) && trendL && vwapL && rsiL && qualL && macdL;
   bool sigS = (c<l1) && trendS && vwapS && rsiS && qualS && macdS;
   if(sigS && !S[k].allowShort) sigS = false;
   if(!sigL && !sigS) return;
   if(!HedgeFrei(k, sigL ? 1 : -1)) return;           // 4.90: GFT-Hedging-Verbot

   // --- Sizing ---
   double ask = SymbolInfoDouble(s, SYMBOL_ASK);
   double bid = SymbolInfoDouble(s, SYMBOL_BID);
   double ent = sigL ? ask : bid;
   double sl;
   if(UseAtrStop)
     {
      double atrBuf[]; if(CopyBuffer(S[k].hAtr, 0, 1, 1, atrBuf)<1) return;
      double d = AtrMult*atrBuf[0];
      if(d<=0.0) return;
      sl = sigL ? ent-d : ent+d;
     }
   else sl = sigL ? l1 : h1;
   double rd  = MathAbs(ent-sl);
   double minMove = 50.0*SymbolInfoDouble(s, SYMBOL_POINT);
   if(rd <= minMove) return;
   long stopLvl = SymbolInfoInteger(s, SYMBOL_TRADE_STOPS_LEVEL);
   if(stopLvl>0 && rd < stopLvl*SymbolInfoDouble(s, SYMBOL_POINT)) return;

   double risk = kStart*S[k].riskPct/100.0*RiskMult;
   if(HourBoost > 0.0 && HourBoost != 1.0 && nyH >= HourBoostFromNY) risk *= HourBoost;
   if(UseDynRisk)
     {
      double pz = AtrPerzentil(k, VolaRankLen);
      if(pz < 0.0) return;
      double f = DynA - DynB*pz;
      if(f < DynMin) f = DynMin;
      if(f > DynMax) f = DynMax;
      if(UseStochRisk)
        {
         double sk[], sd[];
         ArraySetAsSeries(sk, true); ArraySetAsSeries(sd, true);
         if(CopyBuffer(S[k].hSto, 0, 1, 1, sk) < 1) return;
         if(CopyBuffer(S[k].hSto, 1, 1, 1, sd) < 1) return;
         bool passt = sigL ? (sk[0] > sd[0]) : (sk[0] < sd[0]);
         f *= passt ? (1.0+StochWeight) : (1.0-StochWeight);
        }
      risk *= f;
     }
   // --- v4: Groesse nach Restpuffer zum Boden ---
   double buf = PufferPct();
   risk *= DDFaktor(buf);
   if(!peakOk) risk *= PeakUnsicherFaktor;            // 4.90: Boden unsicher (Spitze nicht vollstaendig rekonstruiert); 6.40 eigener Faktor
   if(AccountInfoDouble(ACCOUNT_EQUITY) < kStart) risk *= BelowStartMult;
   if(UseSafety && buf < SafetyBufPct) risk *= SafetyFactor;
   double restB = (RiskBudgetPct>0.0) ? BudgetRest(false) : DBL_MAX;   // 4.40: eigenes Budget, Gesamtdeckel
   restB = MathMin(restB, IdeeRest(s, sigL ? 1 : -1));               // 5.10: Risiko je Idee (Symbol + Richtung, alle Module)
   restB = MathMin(restB, BodenLuft());                              // 6.10: kein Stop darf die Equity unter den Boden bringen
   if(restB < DBL_MAX) risk = MathMin(risk, restB);
   if(risk <= 0.0) return;

   double mpp  = MoneyPerPricePerLot(s);
   double mnv  = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN);
   double riskAtMin = mnv*rd*mpp;
   if(riskAtMin > risk*MinLotRiskTol) return;
   double vol = NormLot(s, risk/(rd*mpp));
   if(vol < mnv) return;
   if(restB < DBL_MAX)
     {
      double stpB  = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP); if(stpB<=0.0) stpB=0.01;
      double rest  = restB;
      if(vol*rd*mpp > rest + 1e-9)
        {
         vol = NormalizeDouble(MathFloor(rest/(rd*mpp)/stpB + 1e-9)*stpB, 2);
         if(vol < mnv) return;
        }
     }
   // Margin (4.90: neue Order <= 80 % der freien Margin, Idee <= MaxIdeeMarginPct % der Equity)
   { string mg = ""; if(!MarginOk(s, sigL ? 1 : -1, vol, ent, mg)) { PrintFormat("DEADBAND4 %s: %s - Signal ausgelassen", s, mg); return; } }

   double stp = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP); if(stp<=0.0) stp=0.01;
   double v1 = MathFloor(vol*Tp1F/stp + 1e-9)*stp;
   double v2 = MathFloor(vol*(Tp1F+Tp2F)/stp + 1e-9)*stp - v1;
   if(v1 < stp) v1=0.0;
   if(v2 < stp) v2=0.0;
   if(vol-v1-v2 < stp) { v2=0.0; if(vol-v1 < stp) v1=0.0; }
   if(Tp1F >= 1.0) v1 = vol;

   double tpF = sigL ? ent + S[k].tpF*rd : ent - S[k].tpF*rd;
   int dg = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
   sl  = NormalizeDouble(sl , dg);
   tpF = NormalizeDouble(tpF, dg);
   if(EinstiegKostetTag(s, vol, "DEADBAND")) return;                   // 6.10: gueltigen Tag nicht verlieren
   trade.SetExpertMagicNumber(S[k].magic);
   OrderMerken(s, sigL ? 1 : -1);                                        // 5.00: vor dem Senden (Hedging-Sperre der anderen Module)
   bool ok = sigL ? trade.Buy (vol, s, 0.0, sl, tpF, "DEADBAND L") : trade.Sell(vol, s, 0.0, sl, tpF, "DEADBAND S");
   if(ok)
     {
      NeuMerken(s, sigL ? 1 : -1, vol*rd*mpp);                              // 6.00: Budget der Fades im selben Durchlauf
      S[k].tradesToday++;
      TdSichern(k);                                                         // 4.90
      OrderMerken(s, sigL ? 1 : -1);
      S[k].posTk = trade.ResultOrder();
      S[k].entryPx = trade.ResultPrice();
      if(S[k].entryPx<=0.0) S[k].entryPx = ent;
      S[k].refPx = S[k].entryPx;
      S[k].slPx = sl;
      S[k].rDist = MathAbs(S[k].entryPx - sl);
      S[k].vol0 = vol;
      S[k].vol1 = NormalizeDouble(v1,2);
      S[k].vol2 = NormalizeDouble(v2,2);
      S[k].t1Done=false; S[k].t2Done=false; S[k].beDone=false; S[k].lastBeTry=0;
      S[k].entryBarTime = bt;
      S[k].closeFails=0;
      if(kCycleStart<=0) kCycleStart = TimeCurrent();
      PrintFormat("DEADBAND4 %s: Einstieg %s %.2f Lot, Risiko %.2f (Puffer %.2f %%, Faktor %.2f)", s, (sigL?"LONG":"SHORT"), vol, vol*rd*mpp, buf, DDFaktor(buf));
     }
   else
      PrintFormat("DEADBAND4 %s: Einstieg abgelehnt (%d %s) Lot %.2f SL %.*f", s, trade.ResultRetcode(), trade.ResultRetcodeDescription(), vol, dg, sl);
  }

//+------------------------------------------------------------------+
//| 4.30 Wochenend-Pause                                              |
//|  Freitag ab WeSchlussNY: eigene Positionen schliessen, Wieder-    |
//|  aufnahme vormerken (Globalvariablen). Sonntag ab WeAufnahmeAbNY  |
//|  bzw. Montag: dieselbe Position wieder eroeffnen, wenn der Kurs   |
//|  Stop und Ziel nicht uebersprungen hat. Vormerkung verfaellt ab   |
//|  Dienstag, nach Auszahlung und nach einer Notbremse.              |
//+------------------------------------------------------------------+
string NYStundeText(double h) { int hh = (int)MathFloor(h); int mm = (int)MathRound((h - hh) * 60.0); return StringFormat("%02d:%02d", hh, mm); }
string WeGvName(int k, string teil) { return "DEADBAND4_WE_" + teil + S[k].sym + "_" + (S[k].r21 ? (S[k].zweit ? "R21B_" : "R21_") : ""); }

bool WeWartet() { for(int k=0;k<nSlot;k++) if(W[k].aktiv) return true; return false; }

void WeSpeichern(int k)
  {
   string g = WeGvName(k, "P_");
   GlobalVariableSet(g + "dir",  W[k].dir);   GlobalVariableSet(g + "sl",   W[k].sl);   GlobalVariableSet(g + "tp",  W[k].tp);
   GlobalVariableSet(g + "lots", W[k].lots);  GlobalVariableSet(g + "rd",   W[k].rd);   GlobalVariableSet(g + "ref", W[k].ref);
   GlobalVariableSet(g + "mfe",  W[k].mfe);   GlobalVariableSet(g + "t1",   W[k].t1 ? 1.0 : 0.0); GlobalVariableSet(g + "be", W[k].be ? 1.0 : 0.0);
   GlobalVariableSet(g + "bar",  (double)W[k].entryBar); GlobalVariableSet(g + "fri", (double)W[k].fri);
   GlobalVariableSet(g + "acc",  (double)AccountInfoInteger(ACCOUNT_LOGIN));   // 4.90: an das Konto gebunden
   GlobalVariablesFlush();                                                     // 4.90: sofort auf Platte (Stromausfall, Windows-Update)
  }

void WeLoeschen(int k, string grund)
  {
   if(W[k].aktiv && StringLen(grund) > 0) PrintFormat("DEADBAND4 %s: Wiederaufnahme verworfen - %s", S[k].sym, grund);
   W[k].aktiv = false;
   string g = WeGvName(k, "P_");
   string f[] = {"dir","sl","tp","lots","rd","ref","mfe","t1","be","bar","fri","acc"};
   bool weg = false;
   for(int i=0;i<ArraySize(f);i++) if(GlobalVariableCheck(g + f[i])) { GlobalVariableDel(g + f[i]); weg = true; }
   if(weg) GlobalVariablesFlush();
  }

// Merkmale der laufenden wiederaufgenommenen Position (fuer einen Neustart)
void WeAktivSpeichern(int k, ulong ticket)
  {
   string g = WeGvName(k, "A_");
   GlobalVariableSet(g + "ticket", (double)ticket); GlobalVariableSet(g + "ref", S[k].refPx); GlobalVariableSet(g + "rd", S[k].rDist);
   GlobalVariableSet(g + "mfe", S[k].mfeR); GlobalVariableSet(g + "t1", S[k].t1Done ? 1.0 : 0.0); GlobalVariableSet(g + "be", S[k].beDone ? 1.0 : 0.0);
   GlobalVariableSet(g + "bar", (double)S[k].entryBarTime);
   GlobalVariablesFlush();                                                     // 4.90
  }
void WeAktivLoeschen(int k)
  {
   string g = WeGvName(k, "A_");
   if(!GlobalVariableCheck(g + "ticket")) return;
   string f[] = {"ticket","ref","rd","mfe","t1","be","bar"};
   for(int i=0;i<ArraySize(f);i++) if(GlobalVariableCheck(g + f[i])) GlobalVariableDel(g + f[i]);
   GlobalVariablesFlush();                                                     // 4.90
  }

void WeLaden(int k)
  {
   string g = WeGvName(k, "P_");
   if(!GlobalVariableCheck(g + "fri")) return;
   W[k].fri = (long)GlobalVariableGet(g + "fri");
   if(GlobalVariableCheck(g + "acc") && AccountInfoInteger(ACCOUNT_LOGIN) > 0 && (long)GlobalVariableGet(g + "acc") != AccountInfoInteger(ACCOUNT_LOGIN))
     { PrintFormat("DEADBAND4 %s: Vormerkung gehoert zu Konto %.0f - wird ignoriert", S[k].sym, GlobalVariableGet(g + "acc")); return; }   // 4.90
   datetime tSrv = TimeCurrent();
   if(tSrv < D'2020.01.01') { weNachladen = true; return; }                   // 4.90: Serverzeit noch ungueltig - nicht loeschen, spaeter laden
   long heute = NYDayIndex(tSrv);
   if(heute < W[k].fri) { weNachladen = true; return; }
   if(heute - W[k].fri > 4) { W[k].aktiv = true; WeLoeschen(k, "Vormerkung veraltet"); return; }
   W[k].dir = (int)GlobalVariableGet(g + "dir"); W[k].sl = GlobalVariableGet(g + "sl"); W[k].tp = GlobalVariableGet(g + "tp");
   W[k].lots = GlobalVariableGet(g + "lots"); W[k].rd = GlobalVariableGet(g + "rd"); W[k].ref = GlobalVariableGet(g + "ref");
   W[k].mfe = GlobalVariableGet(g + "mfe"); W[k].t1 = (GlobalVariableGet(g + "t1") > 0.5); W[k].be = (GlobalVariableGet(g + "be") > 0.5);
   W[k].entryBar = (datetime)GlobalVariableGet(g + "bar"); W[k].lastTry = 0;
   W[k].aktiv = (W[k].dir != 0 && W[k].lots > 0.0 && W[k].rd > 0.0);
   if(W[k].aktiv) PrintFormat("DEADBAND4 %s: Wiederaufnahme aus Globalvariablen geladen (%s %.2f Lot, Stop %.*f, Ziel %.*f)",
                              S[k].sym, (W[k].dir > 0 ? "LONG" : "SHORT"), W[k].lots, _Digits, W[k].sl, _Digits, W[k].tp);
  }

string WeStatusText()
  {
   if(!WeAktiv) return "aus";
   string t = StringFormat("Fr ab %s NY flach", NYStundeText(WeSchlussNY));
   if(!WeAufnahme) return t + ", keine Wiederaufnahme";
   t += StringFormat(", Wiederaufnahme So ab %s NY", NYStundeText(WeAufnahmeAbNY));
   for(int k=0;k<nSlot;k++)
      if(W[k].aktiv) t += StringFormat(" | wartet: %s%s %s %.2f Lot (Stop %.*f, Ziel %.*f)", S[k].sym, (S[k].r21 ? " RSI21" : ""), (W[k].dir > 0 ? "LONG" : "SHORT"), W[k].lots, _Digits, W[k].sl, _Digits, W[k].tp);
   return t;
  }

void WochenendePruefen(bool dayLocked)
  {
   datetime now = TimeCurrent();
   int wd = NYWeekday(now);
   double nyH = NYHour(now);
   // Vormerkung verfaellt ab Dienstag (4.90: gezaehlt ab dem Schliesstag, Sondertage am Donnerstag)
   for(int k=0;k<nSlot;k++)
     {
      if(!W[k].aktiv) continue;
      long seit = NYDayIndex(now) - W[k].fri;
      if((wd >= 2 && wd <= 4 && seit >= 2) || seit >= 5) WeLoeschen(k, "Woche laeuft, Wochenende vorbei");
     }
   // Freitag oder Sondertag: schliessen
   if(WeSchlussJetzt(now))
     {
      for(int k=0;k<nSlot;k++)
        {
         ulong tk=0; if(!HavePosition(k,tk) || !PositionSelectByTicket(tk)) continue;
         if(S[k].lastCloseTry > 0 && now - S[k].lastCloseTry < 30) continue;
         long type = PositionGetInteger(POSITION_TYPE);
         double vol = PositionGetDouble(POSITION_VOLUME), p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
         double sl = PositionGetDouble(POSITION_SL), tp = PositionGetDouble(POSITION_TP);
         S[k].lastCloseTry = now;
         if(!Schliesse(tk))
           {
            PrintFormat("DEADBAND4 %s: Wochenend-Schliessung abgelehnt (%d %s) - neuer Versuch in 30 s", S[k].sym, trade.ResultRetcode(), trade.ResultRetcodeDescription());
            continue;
           }
         bool vormerken = WeAufnahme && (kMode == 0 || WeAufnahmeReif) && S[k].rDist > 0.0;
         if(vormerken)
           {
            W[k].aktiv = true; W[k].dir = (type==POSITION_TYPE_BUY ? 1 : -1); W[k].sl = sl; W[k].tp = tp; W[k].lots = vol;
            W[k].rd = S[k].rDist; W[k].ref = (S[k].refPx > 0.0 ? S[k].refPx : S[k].entryPx); W[k].mfe = S[k].mfeR;
            W[k].t1 = S[k].t1Done; W[k].be = S[k].beDone; W[k].entryBar = S[k].entryBarTime; W[k].fri = NYDayIndex(now); W[k].lastTry = 0;
            WeSpeichern(k);
           }
         WeAktivLoeschen(k);
         Meldung(StringFormat("WOCHENEND-PAUSE %s%s: %s %.2f Lot geschlossen, Ergebnis %.2f%s", S[k].sym, (S[k].r21 ? " RSI21" : ""), (type==POSITION_TYPE_BUY ? "LONG" : "SHORT"), vol, p,
                 (vormerken ? StringFormat(" - Wiederaufnahme So ab %s NY vorgemerkt (Stop %.*f, Ziel %.*f)", NYStundeText(WeAufnahmeAbNY), _Digits, sl, _Digits, tp) : " - keine Wiederaufnahme")));
        }
      return;
     }
   // Sonntag ab WeAufnahmeAbNY oder Montag: wieder aufnehmen
   if(!WeAufnahme || !WeWartet()) return;
   bool faellig = (wd == 0 && nyH >= WeAufnahmeAbNY) || (wd == 1);
   if(!faellig) return;
   if(dayLocked) return;
   if(kMode == 2) { for(int k=0;k<nSlot;k++) WeLoeschen(k, "Auszahlung wartet"); return; }
   if(kMode != 0 && !WeAufnahmeReif) { for(int k=0;k<nSlot;k++) WeLoeschen(k, "Konto reif"); return; }
   for(int k=0;k<nSlot;k++)
     {
      if(!W[k].aktiv) continue;
      if(S[k].r21 && kMode != 0 && R21ReifeSchliessen) { WeLoeschen(k, "Konto reif - RSI21 wird bei Reife nicht wieder aufgenommen"); continue; }   // 4.40
      ulong tk=0;
      if(HavePosition(k,tk)) { WeLoeschen(k, "Position bereits offen"); continue; }
      if(W[k].lastTry > 0 && now - W[k].lastTry < 30) continue;
      string s = S[k].sym;
      long tmode = SymbolInfoInteger(s, SYMBOL_TRADE_MODE);
      if(tmode != SYMBOL_TRADE_MODE_FULL) continue;                          // Markt noch zu
      datetime lastTick = (datetime)SymbolInfoInteger(s, SYMBOL_TIME);
      if(lastTick <= 0 || now - lastTick > 120) continue;                     // kein frischer Kurs
      double bid = SymbolInfoDouble(s, SYMBOL_BID), ask = SymbolInfoDouble(s, SYMBOL_ASK);
      if(bid <= 0.0 || ask <= 0.0) continue;
      double pt = SymbolInfoDouble(s, SYMBOL_POINT);
      double sprMax = (S[k].weSpreadMax > 0.0 ? S[k].weSpreadMax*pt : (WeSpreadMaxR > 0.0 ? WeSpreadMaxR*W[k].rd : 0.0));   // 4.90: Rueckfall in R
      if(sprMax > 0.0 && ask - bid > sprMax && S[k].weSpreadMax <= 0.0 && wd == 0 && nyH < WeAufnahmeAbNY + 1.0) continue;   // 4.90: Sonntags-Spread, hoechstens 1 h warten
      if(S[k].weSpreadMax > 0.0 && ask - bid > sprMax) continue;              // Spread-Grenze in Punkten (Eingabe) wie 4.80
      int d = W[k].dir;
      if(!HedgeFrei(k, d)) continue;                                           // 4.90: GFT-Hedging-Verbot
      double ent = (d > 0 ? ask : bid);
      double chk = (d > 0 ? bid : ask);
      bool stopWeg = (d > 0) ? (W[k].sl > 0.0 && chk <= W[k].sl) : (W[k].sl > 0.0 && chk >= W[k].sl);
      bool zielWeg = (d > 0) ? (W[k].tp > 0.0 && chk >= W[k].tp) : (W[k].tp > 0.0 && chk <= W[k].tp);
      if(stopWeg) { WeLoeschen(k, StringFormat("Kurs %.*f hat den Stop %.*f uebersprungen", _Digits, chk, _Digits, W[k].sl)); continue; }
      if(zielWeg) { WeLoeschen(k, StringFormat("Kurs %.*f hat das Ziel %.*f uebersprungen", _Digits, chk, _Digits, W[k].tp)); continue; }
      // Stop: alter Stop, hoechstens WeStopMaxR vom neuen Einstieg
      int dg = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
      double nsl = W[k].sl;
      if(WeStopMaxR > 0.0)
        {
         double tight = ent - d*WeStopMaxR*W[k].rd;
         if(nsl <= 0.0 || (d > 0 && tight > nsl) || (d < 0 && tight < nsl)) nsl = tight;
        }
      long stl = SymbolInfoInteger(s, SYMBOL_TRADE_STOPS_LEVEL);
      double minD = (stl > 0 ? stl*pt : 0.0);
      if(nsl > 0.0 && ((d > 0 && nsl > bid - minD) || (d < 0 && nsl < ask + minD)))
        { WeLoeschen(k, "Stop liegt zu nah am Kurs"); continue; }
      nsl = NormalizeDouble(nsl, dg);
      // Lots: alt, bei Bedarf ans Risikobudget gekuerzt
      double mpp = MoneyPerPricePerLot(s);
      double nlots = W[k].lots;
      if(WeGroesseBudget && RiskBudgetPct > 0.0 && nsl > 0.0)
        {
         double rest = BudgetRest(S[k].r21);
         double dist = (ent - nsl)*d;
         if(dist > 0.0 && dist*nlots*mpp > rest + 1e-9)
           {
            double stp = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP); if(stp <= 0.0) stp = 0.01;
            nlots = NormalizeDouble(MathFloor(rest/(dist*mpp)/stp + 1e-9)*stp, 2);
            if(nlots < SymbolInfoDouble(s, SYMBOL_VOLUME_MIN)) { WeLoeschen(k, "Risikobudget reicht nicht fuer die Wiederaufnahme"); continue; }
           }
        }
      nlots = NormLot(s, nlots);
      { double dist0 = (nsl > 0.0 ? MathAbs(ent - nsl) : W[k].rd);                                      // 6.10: Luft bis zum Boden
        if(BodenLuft() < nlots*dist0*mpp) { WeLoeschen(k, "Puffer zum Boden reicht nicht fuer die Wiederaufnahme"); continue; } }
      { string mg = ""; if(!MarginOk(s, d, nlots, ent, mg)) { WeLoeschen(k, "Margin: " + mg); continue; } }   // 4.90
      double ntp = (W[k].tp > 0.0 ? NormalizeDouble(W[k].tp, dg) : 0.0);
      if(EinstiegKostetTag(s, nlots, "Wiederaufnahme")) continue;          // 6.10: gueltigen Tag nicht verlieren (Vormerkung bleibt)
      trade.SetExpertMagicNumber(S[k].magic);
      W[k].lastTry = now;
      string kom = (S[k].r21 ? "RSI21 WE" : "DEADBAND WE");
      OrderMerken(s, d);                                                    // 5.00: vor dem Senden
      bool ok = (d > 0) ? trade.Buy(nlots, s, 0.0, nsl, ntp, kom) : trade.Sell(nlots, s, 0.0, nsl, ntp, kom);
      if(!ok)
        {
         PrintFormat("DEADBAND4 %s: Wiederaufnahme abgelehnt (%d %s) - neuer Versuch in 30 s", s, trade.ResultRetcode(), trade.ResultRetcodeDescription());
         continue;
        }
      NeuMerken(s, d, nlots*(nsl > 0.0 ? MathAbs(ent - nsl) : W[k].rd)*mpp);   // 6.00: Budget der Fades
      S[k].entryPx = trade.ResultPrice(); if(S[k].entryPx <= 0.0) S[k].entryPx = ent;
      OrderMerken(s, d); S[k].posTk = trade.ResultOrder();                     // 4.90
      S[k].refPx = W[k].ref; S[k].slPx = nsl; S[k].rDist = W[k].rd;
      S[k].vol0 = nlots; S[k].vol1 = 0.0; S[k].vol2 = 0.0;
      S[k].t1Done = W[k].t1; S[k].t2Done = true; S[k].beDone = W[k].be; S[k].lastBeTry = 0;
      S[k].entryBarTime = W[k].entryBar; S[k].mfeR = W[k].mfe; S[k].closeFails = 0;
      if(S[k].r21) S[k].entryTime = W[k].entryBar;                           // 4.40: Zeit-Exit zaehlt ab der ersten Eroeffnung
      S[k].r21Be = true;                                                     // 6.30: kein Einstand nach der Wiederaufnahme (wie das Replikat)
      ulong ntk = 0; if(HavePosition(k, ntk)) WeAktivSpeichern(k, ntk);
      Meldung(StringFormat("WIEDERAUFNAHME %s%s: %s %.2f Lot zu %.*f (Bezug %.*f, Stop %.*f, Ziel %.*f, %.1f R Vorlauf)",
              s, (S[k].r21 ? " RSI21" : ""), (d > 0 ? "LONG" : "SHORT"), nlots, dg, S[k].entryPx, dg, S[k].refPx, dg, nsl, dg, ntp, W[k].mfe));
      WeLoeschen(k, "");
     }
  }

//+------------------------------------------------------------------+
//| 4.40 RSI21-Modul                                                  |
//|  Signal- und Filterlogik wie RSI21 Continuation v3.4, Einstieg,   |
//|  Groesse und Verwaltung unter den Kontoregeln dieses EA.          |
//+------------------------------------------------------------------+
ENUM_TIMEFRAMES R21Tf(int t) { return (t==0 ? PERIOD_M15 : (t==1 ? PERIOD_M30 : PERIOD_H1)); }
int R21TfMin(int t) { return (t==0 ? 15 : (t==1 ? 30 : 60)); }

bool R21PlaetzeAnlegen()
  {
   string wp[];
   if(StringSplit(R21Gewichte, StringGetCharacter(",",0), wp) != 3) { Print("DEADBAND4: R21Gewichte braucht drei Werte (M15,M30,H1)"); return false; }
   for(int t=0;t<3;t++) r21w[t] = StringToDouble(wp[t]);
   if(R21MagicOffset < MAXSYM) { Print("DEADBAND4: R21MagicOffset muss mindestens 8 sein"); return false; }
   if(R21RiskPct <= 0.0 || R21StopATR <= 0.0 || R21NasRR <= 0.0 || R21GoldRR <= 0.0) { Print("DEADBAND4: RSI21-Risiko, Stop und Ziele muessen > 0 sein"); return false; }
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
     {
      Print("DEADBAND4: RSI21-Modul AUS - Konto ist kein Hedging-Konto (DEADBAND- und RSI21-Position auf demselben Symbol wuerden verschmelzen)");
      return true;
     }
   int ig = -1, inas = -1;
   for(int k=0;k<nSym;k++) { if(S[k].sym == R21GoldSymbol) ig = k; if(S[k].sym == R21NasSymbol) inas = k; }
   if(ig < 0 || inas < 0)
     {
      PrintFormat("DEADBAND4: RSI21-Modul AUS - %s und %s muessen beide in der SymbolList stehen", R21GoldSymbol, R21NasSymbol);
      return true;
     }
   for(int k=0;k<nSym;k++)
     {
      if(k != ig && k != inas) continue;
      int j = nSlot;
      string s = S[k].sym;
      S[j].sym = s; S[j].magic = MagicBase + R21MagicOffset + k; S[j].pt = S[k].pt;
      S[j].r21 = true; S[j].zweit = false; S[j].partner = -1; S[j].basis = k; S[j].istGold = (k == ig); S[j].rr = (k == ig ? R21GoldRR : R21NasRR);
      S[j].riskPct = R21RiskPct; S[j].clsMin = S[k].clsMin; S[j].tpF = S[j].rr; S[j].allowShort = true; S[j].weSpreadMax = S[k].weSpreadMax;
      S[j].hEma = INVALID_HANDLE; S[j].hRsi = INVALID_HANDLE; S[j].hAtr = INVALID_HANDLE; S[j].hSto = INVALID_HANDLE; S[j].hMacd = INVALID_HANDLE;
      for(int t=0;t<3;t++)
        {
         S[j].hR21Rsi[t] = iRSI(s, R21Tf(t), R21RsiLen, PRICE_CLOSE);
         S[j].hR21Atr[t] = iATR(s, R21Tf(t), 14);
         S[j].r21Bar[t]  = 0;
         if(S[j].hR21Rsi[t]==INVALID_HANDLE || S[j].hR21Atr[t]==INVALID_HANDLE)
           { PrintFormat("DEADBAND4: RSI21-Handle fuer %s fehlgeschlagen", s); return false; }
        }
      S[j].hMaLang    = iMA(s, PERIOD_D1, R21MaLang, 0, MODE_SMA, PRICE_CLOSE);
      S[j].hMaSchnell = iMA(s, PERIOD_D1, R21MaSchnell, 0, MODE_SMA, PRICE_CLOSE);
      if(S[j].hMaLang==INVALID_HANDLE || S[j].hMaSchnell==INVALID_HANDLE)
        { PrintFormat("DEADBAND4: Tages-SMA fuer %s fehlgeschlagen", s); return false; }
      S[j].lastBar=0; S[j].curDay=0; S[j].tradesToday=0; S[j].closeFails=0; S[j].lastCloseTry=0;
      S[j].t1Done=true; S[j].t2Done=true; S[j].beDone=true; S[j].lastBeTry=0; S[j].lastHarvTry=0;
      S[j].vol0=0.0; S[j].vol1=0.0; S[j].vol2=0.0; S[j].entryBarTime=0; S[j].entryTime=0; S[j].tfMin=0; S[j].mfeR=0.0;
      S[j].refPx=0.0; S[j].entryPx=0.0; S[j].slPx=0.0; S[j].rDist=0.0; S[j].posTk=0; hedgeLog[j]=0; S[j].r21Be=true;
      r21DivBucket[j] = 0; r21DivDir[j] = 0;
      W[j].aktiv = false; W[j].lastTry = 0;
      r21LastSig[j][0] = 0; r21LastSig[j][1] = 0;
      R21SigLaden(j);
      nSlot++;
      UebernehmePosition(j);
      if(WeAktiv && WeAufnahme) WeLaden(j);
     }
   // 4.50: zweiter RSI21-Platz je Symbol (eigene Magic, keine eigenen Indikatoren - Signale kommen vom ersten Platz)
   // 4.90: immer anlegen (Verwaltung offener Zweitplatz-Positionen); R21ZweiterPlatz steuert nur neue Einstiege
     {
      int erste = nSlot;
      for(int j1=nSym;j1<erste;j1++)
        {
         if(nSlot >= MAXSLOT) break;
         int j = nSlot;
         S[j] = S[j1];
         S[j].magic = MagicBase + R21MagicOffset + MAXSYM + S[j1].basis;
         S[j].zweit = true; S[j].partner = j1; S[j1].partner = j;
         for(int t=0;t<3;t++) { S[j].hR21Rsi[t] = INVALID_HANDLE; S[j].hR21Atr[t] = INVALID_HANDLE; S[j].r21Bar[t] = 0; }
         S[j].hMaLang = INVALID_HANDLE; S[j].hMaSchnell = INVALID_HANDLE;
         S[j].lastBar=0; S[j].curDay=0; S[j].tradesToday=0; S[j].closeFails=0; S[j].lastCloseTry=0;
         S[j].t1Done=true; S[j].t2Done=true; S[j].beDone=true; S[j].lastBeTry=0; S[j].lastHarvTry=0;
         S[j].vol0=0.0; S[j].vol1=0.0; S[j].vol2=0.0; S[j].entryBarTime=0; S[j].entryTime=0; S[j].tfMin=0; S[j].mfeR=0.0;
         S[j].refPx=0.0; S[j].entryPx=0.0; S[j].slPx=0.0; S[j].rDist=0.0; S[j].posTk=0; hedgeLog[j]=0; S[j].r21Be=true;
         r21DivBucket[j] = 0; r21DivDir[j] = 0;
         r21LastSig[j][0] = 0; r21LastSig[j][1] = 0;
         W[j].aktiv = false; W[j].lastTry = 0;
         nSlot++;
         UebernehmePosition(j);
         if(WeAktiv && WeAufnahme) WeLaden(j);
        }
     }
   return true;
  }

// 4.50: Signal-Gedaechtnis (Kerzenzeit des letzten gueltigen Signals) ueberlebt einen Neustart
string R21SigGv(int k, int di) { return "DEADBAND4_R21SIG_" + S[k].sym + (di == 0 ? "_L" : "_S"); }
void R21SigLaden(int k)
  {
   for(int di=0;di<2;di++)
     {
      string g = R21SigGv(k, di);
      if(!GlobalVariableCheck(g)) continue;
      datetime t = (datetime)(long)GlobalVariableGet(g);
      datetime jetzt = TimeCurrent();
      if(jetzt < D'2020.01.01') { weNachladen = true; continue; }             // 4.90: Serverzeit noch ungueltig
      if(t > 0 && t <= jetzt && jetzt - t <= 86400) r21LastSig[k][di] = t;
     }
  }

int R21AnderSlot(int k)
  {
   for(int j=nSym;j<nSlot;j++) if(j != k && S[j].r21 && !S[j].zweit && S[j].basis != S[k].basis) return j;
   return -1;
  }

// Tagesregime: Vortagesschluss gegen Vortages-SMA. 1 = ueber SMA lang, -1 = darunter, 0 = unbekannt.
int R21Regime(int k, int &shortOk, int &gateL, int &gateS)
  {
   double maL[], maS[];
   if(CopyBuffer(S[k].hMaLang, 0, 1, 1, maL) != 1) return 0;
   if(CopyBuffer(S[k].hMaSchnell, 0, 1, 1, maS) != 1) return 0;
   double c = iClose(S[k].sym, PERIOD_D1, 1);
   if(c <= 0.0 || maL[0] <= 0.0 || maS[0] <= 0.0) return 0;
   shortOk = (c < maL[0] || c < maS[0]) ? 1 : 0;
   gateL   = (c > maL[0] && c > maS[0]) ? 1 : 0;
   gateS   = (c < maL[0] && c < maS[0]) ? 1 : 0;
   return (c > maL[0]) ? 1 : -1;
  }

int R21SonntagImMonat(int jahr, int monat, int nr)
  {
   MqlDateTime d; ZeroMemory(d);
   d.year = jahr; d.mon = monat; d.day = 1;
   datetime first = StructToTime(d);
   TimeToStruct(first, d);
   return 1 + (7 - d.day_of_week) % 7 + 7*(nr - 1);
  }

// Serverzeit -> UTC wie RSI21 v3.4 (Server = NY + NYOffsetHours, US-Sommerzeit aus dem NY-Datum)
datetime R21UTC(datetime serverTime)
  {
   datetime ny = (datetime)((long)serverTime - (long)NYOffsetHours*3600);
   MqlDateTime d; TimeToStruct(ny, d);
   bool dst = (d.mon > 3 && d.mon < 11);
   if(d.mon == 3)  { int st = R21SonntagImMonat(d.year, 3, 2);  dst = (d.day > st || (d.day == st && d.hour >= 2)); }
   if(d.mon == 11) { int en = R21SonntagImMonat(d.year, 11, 1); dst = (d.day < en || (d.day == en && d.hour < 2)); }
   return (datetime)(ny + (dst ? 4 : 5)*3600);
  }

// Bestaetigte RSI-Divergenz auf UTC-H4 (aus H1 rekonstruiert, wie RSI21 v3.4): +1 bullisch, -1 baerisch, 0 keine/beide
bool R21Divergenz(int k, int &direction)
  {
   long sek = 14400;
   string sym = S[k].sym;
   datetime current = (datetime)(((long)R21UTC(TimeCurrent())/sek)*sek);
   if(r21DivBucket[k] == current && current > 0) { direction = r21DivDir[k]; return true; }
   if(!SeriesInfoInteger(sym, PERIOD_H1, SERIES_SYNCHRONIZED)) return false;
   MqlRates rates[];
   ArraySetAsSeries(rates, false);
   int got = CopyRates(sym, PERIOD_H1, 1, R21DivHistoryH1, rates);
   if(got < 2000) return false;
   double closes[]; ArrayResize(closes, got);
   int n = 0; datetime last = 0;
   for(int i=0;i<got;i++)
     {
      datetime utc = R21UTC(rates[i].time);
      datetime bucket = (datetime)(((long)utc/sek)*sek);
      if(bucket >= current) continue;                 // keine laufende H4-Kerze
      if(n == 0 || bucket != last) { closes[n] = rates[i].close; n++; last = bucket; }
      else closes[n-1] = rates[i].close;
     }
   if(n < 500) return false;
   double rsi[]; ArrayResize(rsi, n); ArrayInitialize(rsi, EMPTY_VALUE);
   int period = R21RsiLen;
   double gain = 0.0, loss = 0.0;
   for(int i=1;i<=period;i++)
     { double delta = closes[i]-closes[i-1]; gain += MathMax(delta, 0.0); loss += MathMax(-delta, 0.0); }
   gain /= period; loss /= period;
   for(int i=period;i<n;i++)
     {
      if(i > period)
        {
         double delta = closes[i]-closes[i-1];
         gain = (gain*(period-1) + MathMax(delta, 0.0))/period;
         loss = (loss*(period-1) + MathMax(-delta, 0.0))/period;
        }
      rsi[i] = (loss == 0.0) ? (gain == 0.0 ? 50.0 : 100.0) : 100.0 - 100.0/(1.0 + gain/loss);
     }
   double high=0, prevHigh=0, highRsi=0, prevHighRsi=0, low=0, prevLow=0, lowRsi=0, prevLowRsi=0;
   int highs=0, lows=0, radius=R21DivRadius;
   for(int j=MathMax(radius, period); j+radius<n; j++)        // Pivot erst nach radius geschlossenen Kerzen bekannt
     {
      bool isHigh=true, isLow=true;
      for(int q=j-radius;q<=j+radius;q++)
        { if(closes[q] > closes[j]) isHigh=false; if(closes[q] < closes[j]) isLow=false; }
      if(isHigh) { prevHigh=high; prevHighRsi=highRsi; high=closes[j]; highRsi=rsi[j]; highs++; }
      if(isLow)  { prevLow=low;   prevLowRsi=lowRsi;   low=closes[j];  lowRsi=rsi[j];  lows++; }
     }
   if(highs < 2 || lows < 2) return false;
   bool bearish = (high > prevHigh && highRsi < prevHighRsi - R21DivGap);
   bool bullish = (low < prevLow && lowRsi > prevLowRsi + R21DivGap);
   direction = (bullish ? 1 : 0) - (bearish ? 1 : 0);
   r21DivBucket[k] = current; r21DivDir[k] = direction;
   return true;
  }

// 4.90: R21ReifeModus 2 = alle schliessen (wie 4.80), 1 = nur Gewinner, 3 = Verlierer nur, wenn gueltige Tage und
// Mindestgewinn danach noch stehen (sonst laeuft er mit Stop, Ziel und Zeit-Exit aus). Gewinner: 2-Minuten- und News-Regel.
void R21BeiReifeSchliessen()
  {
   datetime now = TimeCurrent();
   double schwelle = GueltigSchwelle(), reserve = schwelle*MathMax(HarvestMargin, 0.05), zusatz = 0.0;
   for(int k=nSym;k<nSlot;k++)
     {
      ulong tk=0; if(!HavePosition(k,tk) || !PositionSelectByTicket(tk)) continue;
      if(S[k].lastCloseTry > 0 && now - S[k].lastCloseTry < 30) continue;
      double p = PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);
      if(p > 0.0 && !GewinnSchlussOk(tk, p)) continue;
      if(p <= 0.0 && R21ReifeModus == 1) continue;
      if(p <= 0.0 && R21ReifeModus == 3)
        {
         int v = kValidDays + ((GueltigHeuteZaehlt && kTodayReal + zusatz + p - reserve >= schwelle) ? 1 : 0);
         if(v < NeedValidDays || AccountInfoDouble(ACCOUNT_BALANCE) + zusatz + p - reserve - kStart < kMinProfit) continue;
        }
      S[k].lastCloseTry = now;
      if(Schliesse(tk)) { zusatz += p; PrintFormat("DEADBAND4 %s RSI21: bei Auszahlungsreife geschlossen, Ergebnis %.2f", S[k].sym, p); }
      else PrintFormat("DEADBAND4 %s RSI21: Schliessen bei Reife abgelehnt (%d %s) - neuer Versuch in 30 s", S[k].sym, trade.ResultRetcode(), trade.ResultRetcodeDescription());
     }
  }

string R21StatusText()
  {
   if(!R21Aktiv) return "aus (keine neuen Einstiege; offene RSI21-Positionen werden weiter verwaltet)";
   if(nSlot <= nSym) return "AUS (Gold- oder NAS-Symbol fehlt in der SymbolList)";
   string t = StringFormat("Risiko %.2f %% x Gewicht, Budget %.2f %% (gesamt %.2f %%), Folgesignal %s, 2. Platz %s", R21RiskPct, R21BudgetPct, GesamtBudgetPct,
                           (R21FolgeMin > 0 ? IntegerToString(R21FolgeMin) + " min" : "aus"), (R21ZweiterPlatz ? "an" : "aus"));
   for(int k=nSym;k<nSlot;k++)
     {
      ulong tk=0;
      if(HavePosition(k,tk) && PositionSelectByTicket(tk))
         t += StringFormat(" | %s%s %s M%d %.2f Lot, bester Kurs %.1f R", S[k].sym, (S[k].zweit ? " (2)" : ""), (PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY ? "LONG" : "SHORT"),
                           S[k].tfMin, PositionGetDouble(POSITION_VOLUME), S[k].mfeR);
     }
   return t;
  }

void HandleR21(int k, long today, bool dayLocked)
  {
   string s = S[k].sym;
   datetime now = TimeCurrent();
   ulong ticket = 0;
   bool inPos = HavePosition(k, ticket);

   // --- offene Position: bester Kurs (fuer Ernte/Gewinn-Ernte), Zeit-Exit ---
   if(inPos && PositionSelectByTicket(ticket))
     {
      long type = PositionGetInteger(POSITION_TYPE);
      double bid = SymbolInfoDouble(s, SYMBOL_BID), ask = SymbolInfoDouble(s, SYMBOL_ASK);
      if(S[k].rDist > 0.0 && bid > 0.0 && ask > 0.0)
        {
         double ref = (S[k].refPx > 0.0 ? S[k].refPx : S[k].entryPx);
         double favR = (type==POSITION_TYPE_BUY) ? (bid - ref)/S[k].rDist : (ref - ask)/S[k].rDist;
         if(favR > S[k].mfeR) S[k].mfeR = favR;
        }
      if(!S[k].r21Be && R21EinstandAbR > 0.0 && now - S[k].lastBeTry >= 5)    // 6.30: Stop auf Einstand ab R21EinstandAbR
        {
         double ref = (S[k].refPx > 0.0 ? S[k].refPx : S[k].entryPx);
         int e = EinstandSetzen(ticket, ref, S[k].rDist, R21EinstandAbR, "RSI21" + (S[k].zweit ? " (2)" : ""));
         if(e != 0) S[k].lastBeTry = now;
         if(e == 1) S[k].r21Be = true;
         if(!PositionSelectByTicket(ticket)) return;
        }
      datetime t0 = (S[k].entryTime > 0 ? S[k].entryTime : (datetime)PositionGetInteger(POSITION_TIME));
      int shift = iBarShift(s, PERIOD_M5, t0, false);
      bool zeit = (R21ExitBarsM5 > 0 && shift >= R21ExitBarsM5) || (R21ExitTage > 0 && now - t0 >= (long)R21ExitTage*86400);
      long tmode = SymbolInfoInteger(s, SYMBOL_TRADE_MODE);
      bool mayTry = ((S[k].closeFails==0) || (now - S[k].lastCloseTry >= 60)) && tmode != SYMBOL_TRADE_MODE_DISABLED;
      if(zeit && mayTry && GewinnSchlussOk(ticket, PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP)))   // 4.90
        {
         S[k].lastCloseTry = now;
         if(Schliesse(ticket)) { S[k].closeFails = 0; PrintFormat("DEADBAND4 %s RSI21: Zeit-Exit (%d M5-Kerzen seit %s)", s, shift, TimeToString(t0)); }
         else
           {
            S[k].closeFails++;
            if(S[k].closeFails==1) PrintFormat("DEADBAND4 %s RSI21: Zeit-Exit abgelehnt (%d %s) - 60 s Pause", s, trade.ResultRetcode(), trade.ResultRetcodeDescription());
           }
        }
     }

   if(S[k].zweit) return;                                        // 4.50: Einstiege des zweiten Platzes laufen ueber den ersten
   if(!R21Aktiv)                                                 // 4.90: Modul aus - nur Verwaltung, keine Signale
     {
      if(!inPos && !HavePosition(k, ticket)) WeAktivLoeschen(k);
      if(S[k].partner >= 0) { ulong tkp = 0; if(!HavePosition(S[k].partner, tkp)) WeAktivLoeschen(S[k].partner); }
      return;
     }

   // --- neue Kerzen je Zeitebene (auch bei offener Position mitzaehlen) ---
   bool neu[3];
   for(int t=0;t<3;t++)
     {
      neu[t] = false;
      datetime bt = iTime(s, R21Tf(t), 0);
      if(bt > 0 && bt != S[k].r21Bar[t]) { neu[t] = true; S[k].r21Bar[t] = bt; }
     }
   if(!inPos && !HavePosition(k, ticket)) WeAktivLoeschen(k);
   int k2 = (R21ZweiterPlatz ? S[k].partner : -1);
   if(S[k].partner >= 0) { ulong tk2 = 0; if(!HavePosition(S[k].partner, tk2)) WeAktivLoeschen(S[k].partner); }   // 4.90: unabhaengig vom Schalter
   if(!(neu[0] || neu[1] || neu[2])) return;

   // --- 4.50: Signale bewerten - unabhaengig von Position und Kontozustand (Signal-Gedaechtnis fuer das Folgesignal) ---
   int ko = R21AnderSlot(k);
   int shortOk = 0, gateL = 0, gateS = 0;
   int reg = R21Regime(k, shortOk, gateL, gateS);
   if(reg == 0) return;                                          // Regime unbekannt
   int div = 0;
   bool divOk = (!R21DivH4) || R21Divergenz(k, div);
   int    sigDir[3]; double sigRsi[3]; datetime sigZeit = 0;
   bool   hatSig[2]; hatSig[0] = false; hatSig[1] = false;
   for(int t=0;t<3;t++)
     {
      sigDir[t] = 0; sigRsi[t] = 0.0;
      if(!neu[t]) continue;
      if(t==2 && S[k].istGold && R21GoldOhneH1) continue;
      double nyH = NYHour(S[k].r21Bar[t]);
      double bis = (S[k].istGold ? R21GoldBisNY : R21NasBisNY);
      if(nyH < R21AbNY || nyH >= bis) continue;
      double r[]; if(CopyBuffer(S[k].hR21Rsi[t], 0, 1, 1, r) != 1) continue;
      int dir = (r[0] > R21Oben ? 1 : (r[0] < R21Unten ? -1 : 0));
      if(dir == 0) continue;
      if(dir < 0 && shortOk == 0) continue;                      // Short-Regime: unter SMA lang ODER schnell
      if(dir > 0 && !S[k].istGold && reg < 0) continue;          // NAS-Longs nur ueber SMA lang
      bool crossOk = false;
      if(ko >= 0)
        {
         double ro[]; if(CopyBuffer(S[ko].hR21Rsi[t], 0, 1, 1, ro) != 1) continue;
         crossOk = (dir > 0) ? (ro[0] > R21CrossThr) : (ro[0] < 100.0 - R21CrossThr);
        }
      if(S[k].istGold) { bool gate = (dir > 0 ? gateL==1 : gateS==1); if(!crossOk && !gate) continue; }
      else if(!crossOk) continue;
      if(R21DivH4) { if(!divOk) continue; if(dir*div < 0) continue; }
      sigDir[t] = dir; sigRsi[t] = r[0];
      hatSig[dir > 0 ? 0 : 1] = true;
      if(S[k].r21Bar[t] > sigZeit) sigZeit = S[k].r21Bar[t];
     }
   if(!hatSig[0] && !hatSig[1]) return;
   // Folgesignal: vorher (fruehere Kerzenzeit) gab es in dieselbe Richtung schon ein gueltiges Signal, hoechstens R21FolgeMin alt
   bool folge[2];
   for(int di=0;di<2;di++)
     {
      datetime vor = r21LastSig[k][di];
      folge[di] = (R21FolgeMin <= 0) || (vor > 0 && vor < sigZeit && (long)(sigZeit - vor) <= (long)R21FolgeMin*60);
      if(hatSig[di] && sigZeit > vor)
        {
         if(R21FolgeMin > 0 && !folge[di])
            PrintFormat("DEADBAND4 %s RSI21: erstes %s-Signal gemerkt (kein Einstieg, wartet auf Folgesignal binnen %d min)", s, (di == 0 ? "LONG" : "SHORT"), R21FolgeMin);
         r21LastSig[k][di] = sigZeit;
         GlobalVariableSet(R21SigGv(k, di), (double)(long)sigZeit);
         if(!MQLInfoInteger(MQL_TESTER)) GlobalVariablesFlush();          // 4.90
        }
     }

   // --- Kontozustand ---
   if(dayLocked || kMode != 0) return;
   if(gGueltigSchutz && R21GueltigSchutzJetzt(sigZeit))           // 6.50: Schutz gueltiger Tage - vor GueltigSchutzR21BisNY oder ohne Fade-Regime
     {
      bool einst = false;
      for(int t=0;t<3;t++) if(sigDir[t] != 0 && folge[sigDir[t] > 0 ? 0 : 1]) einst = true;
      if(einst) PrintFormat("DEADBAND4 %s RSI21: Folgesignal ausgelassen - %s", s, R21SchutzGrund(sigZeit));
      return;
     }
   if(SerienPause()) return;                                      // 5.10: Serien-Stopp
   if(WeAktiv && KurzVorSchluss(now)) return;                    // 4.90: auch Sondertage und SchlussVorlaufMin
   if(NewsFenster(now)) return;                                   // 4.90: GFT-News-Regel
   if(SymbolInfoInteger(s, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_FULL) return;
   if(R21MaxLossDay > 0)
     {
      int verl = LossesToday(k, PropDayIndex(now));
      if(k2 >= 0) verl += LossesToday(k2, PropDayIndex(now));
      if(verl >= R21MaxLossDay) return;
     }

   bool neuK = false, neuK2 = false; int neuDir = 0; double neuRiskK = 0.0, neuRiskK2 = 0.0;   // 4.90: in diesem Durchlauf eroeffnet
   for(int t=0;t<3;t++)
     {
      int dir = sigDir[t];
      if(dir == 0) continue;
      if(!folge[dir > 0 ? 0 : 1]) continue;
      // Platzwahl: erster Platz, sonst zweiter (nur wenn der erste in dieselbe Richtung laeuft)
      int ke = -1;
      ulong tkA = 0;
      bool hatA = HavePosition(k, tkA) || neuK;                    // 4.90: eben eroeffnete Position zaehlt, auch wenn die Liste nachhinkt
      if(!hatA)
        {
         if(!(WeAktiv && W[k].aktiv)) ke = k;
        }
      else if(k2 >= 0)
        {
         int dirA = neuDir;
         if(tkA != 0 && PositionSelectByTicket(tkA)) dirA = (PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY ? 1 : -1);
         ulong tkB = 0;
         if(dirA == dir && !neuK2 && !HavePosition(k2, tkB) && !(WeAktiv && W[k2].aktiv)) ke = k2;
        }
      if(ke < 0) continue;
      if(!HedgeFrei(ke, dir)) continue;                            // 4.90: GFT-Hedging-Verbot
      double unsicht = 0.0;                                        // 4.90: Risiko eben eroeffneter, noch nicht sichtbarer Positionen
      { ulong tx = 0; if(neuK && !HavePosition(k, tx)) unsicht += neuRiskK; if(neuK2 && k2 >= 0 && !HavePosition(k2, tx)) unsicht += neuRiskK2; }
      double a[]; if(CopyBuffer(S[k].hR21Atr[t], 0, 1, 1, a) != 1 || a[0] <= 0.0) continue;
      double rd = R21StopATR*a[0];
      double pt = SymbolInfoDouble(s, SYMBOL_POINT);
      long stl = SymbolInfoInteger(s, SYMBOL_TRADE_STOPS_LEVEL);
      if(stl > 0 && rd < stl*pt*1.2) continue;

      // --- Groesse ---
      double w = r21w[t]*(S[k].istGold ? R21GoldMult : 1.0);
      double risk = kStart*R21RiskPct/100.0*w;
      double buf = PufferPct();
      risk *= DDFaktor(buf);
      if(!peakOk) risk *= PeakUnsicherFaktor;                    // 4.90: Boden unsicher (6.40: eigener Faktor)
      if(AccountInfoDouble(ACCOUNT_EQUITY) < kStart) risk *= BelowStartMult;
      double restR = (R21BudgetPct > 0.0) ? BudgetRest(true) - unsicht : DBL_MAX;
      double restI = IdeeRest(s, dir);                            // 5.10: Risiko je Idee (Symbol + Richtung, alle Module)
      if(restI < DBL_MAX && neuDir == dir) restI -= unsicht;      // eben eroeffnete Position derselben Idee
      bool ideeVoll = false;
      if(restI < restR) { restR = restI; ideeVoll = true; }
      { double luft = BodenLuft() - unsicht; if(luft < restR) { restR = luft; ideeVoll = false; } }   // 6.10: Luft bis zum Boden
      if(restR < DBL_MAX) risk = MathMin(risk, restR);
      if(risk <= 0.0) { if(ideeVoll) continue; return; }         // Budget voll (5.10: nur die Idee voll -> naechste Zeitebene)
      double mpp = MoneyPerPricePerLot(s);
      double mnv = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN);
      if(mnv*rd*mpp > risk*MinLotRiskTol) continue;
      double vol = NormLot(s, risk/(rd*mpp));
      if(vol < mnv) continue;
      if(restR < DBL_MAX)
        {
         double stpB = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP); if(stpB <= 0.0) stpB = 0.01;
         double rest = restR;
         if(vol*rd*mpp > rest + 1e-9)
           {
            vol = NormalizeDouble(MathFloor(rest/(rd*mpp)/stpB + 1e-9)*stpB, 2);
            if(vol < mnv) continue;
           }
        }
      double ask = SymbolInfoDouble(s, SYMBOL_ASK), bid = SymbolInfoDouble(s, SYMBOL_BID);
      if(ask <= 0.0 || bid <= 0.0) return;
      double ent = (dir > 0 ? ask : bid);
      { string mg = ""; if(!MarginOk(s, dir, vol, ent, mg)) { PrintFormat("DEADBAND4 %s RSI21: %s - Signal ausgelassen", s, mg); return; } }   // 4.90
      int dg = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
      double sl = NormalizeDouble(ent - dir*rd, dg);
      double tp = NormalizeDouble(ent + dir*S[ke].rr*rd, dg);
      double minD = (stl > 0 ? stl*pt : 0.0);
      if(dir > 0 && (bid - sl < minD || tp - bid < minD)) continue;
      if(dir < 0 && (sl - ask < minD || ask - tp < minD)) continue;
      if(EinstiegKostetTag(s, vol, "RSI21")) return;                      // 6.10: gueltigen Tag nicht verlieren
      trade.SetExpertMagicNumber(S[ke].magic);
      OrderMerken(s, dir);                                                  // 5.00: vor dem Senden
      bool ok = (dir > 0) ? trade.Buy(vol, s, 0.0, sl, tp, (ke == k ? "RSI21 L" : "RSI21 L2")) : trade.Sell(vol, s, 0.0, sl, tp, (ke == k ? "RSI21 S" : "RSI21 S2"));
      if(ok)
        {
         NeuMerken(s, dir, vol*rd*mpp);                                   // 6.00: Budget der Fades im selben Durchlauf
         S[ke].entryPx = trade.ResultPrice(); if(S[ke].entryPx <= 0.0) S[ke].entryPx = ent;
         S[ke].posTk = trade.ResultOrder(); OrderMerken(s, dir);           // 4.90
         if(ke == k) { neuK = true; neuDir = dir; neuRiskK = vol*rd*mpp; } else { neuK2 = true; neuRiskK2 = vol*rd*mpp; }
         S[ke].refPx = S[ke].entryPx; S[ke].slPx = sl; S[ke].rDist = MathAbs(S[ke].entryPx - sl);
         S[ke].entryTime = now; S[ke].entryBarTime = now; S[ke].tfMin = R21TfMin(t);
         S[ke].mfeR = 0.0; S[ke].t1Done = true; S[ke].beDone = true; S[ke].vol0 = vol; S[ke].vol1 = 0.0; S[ke].vol2 = 0.0; S[ke].closeFails = 0;
         S[ke].r21Be = (R21EinstandAbR <= 0.0); S[ke].lastBeTry = 0;                   // 6.30
         if(kCycleStart <= 0) kCycleStart = now;
         PrintFormat("DEADBAND4 %s RSI21: Einstieg %s M%d%s (RSI %.1f, Divergenz %d, Regime %d), %.2f Lot, Risiko %.2f (Puffer %.2f %%), Stop %.*f, Ziel %.*f (%.2f R)",
                     s, (dir > 0 ? "LONG" : "SHORT"), R21TfMin(t), (ke == k ? "" : " [2. Platz]"), sigRsi[t], div, reg, vol, vol*rd*mpp, buf, dg, sl, dg, tp, S[ke].rr);
        }
      else
        {
         PrintFormat("DEADBAND4 %s RSI21: Einstieg abgelehnt (%d %s) Lot %.2f SL %.*f TP %.*f", s, trade.ResultRetcode(), trade.ResultRetcodeDescription(), vol, dg, sl, dg, tp);
         return;
        }
      if(k2 < 0) return;                                         // ohne zweiten Platz: ein Einstieg je Kerze (wie 4.40)
     }
  }

//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| 5.00 NAS-Noise-Modul (Signal-Logik aus NAS100_Flip_v4)            |
//|  Noise-Area-Momentum (Zarattini/Aziz/Barbon 2024) auf NAS100,     |
//|  nur Long, nur intraday. Am Schluss der M1-Kerze vor 10:00,       |
//|  11:00 ... 15:00 NY: Long, wenn Schluss > UB mit                  |
//|  UB = max(Eroeffnung 9:30, Vortagesschluss) x (1 + NzK x sigma),  |
//|  sigma = Mittel |Schluss/Eroeffnung - 1| derselben Minute der     |
//|  letzten NzTage gueltigen Tage. Ausstieg aller Teile an der       |
//|  naechsten Pruefung mit Schluss < UB, spaetestens NzSchlussMin.   |
//|  Teilposition q: Stop NzStops[q] x Tages-Sigma x Eroeffnung x     |
//|  (Restzeit / Restzeit ab erster Pruefung)^NzStopZeitPow; Risiko   |
//|  je Signal NzRiskPct x Vola-Gewicht / Teile x Puffer-Kurve, im    |
//|  Gesamtbudget. Hedging-, News- und 130-s-Regel wie DEADBAND/RSI21.|
//|  Jede flache Teilposition steigt bei einem Signal (neu) ein.      |
//+------------------------------------------------------------------+
#define NZMAXDAYS 90
#define NZLOOKBACK 60
// US-Feiertage und verkuerzte Tage (NY-Datum) 2019-2027 wie NAS100_Flip_v4 (Replikat: Tage mit < 5 h Handel ausgelassen)
string NZ_FREI[] =
  {
   "2019.01.01;2019.01.21;2019.02.18;2019.04.19;2019.05.27;2019.07.03;2019.07.04;2019.09.02;2019.11.28;2019.11.29;2019.12.24;2019.12.25;",
   "2020.01.01;2020.01.20;2020.02.17;2020.04.10;2020.05.25;2020.07.03;2020.09.07;2020.11.26;2020.11.27;2020.12.24;2020.12.25;",
   "2021.01.01;2021.01.18;2021.02.15;2021.04.02;2021.05.31;2021.07.05;2021.09.06;2021.11.25;2021.11.26;2021.12.24;",
   "2022.01.17;2022.02.21;2022.04.15;2022.05.30;2022.06.20;2022.07.04;2022.09.05;2022.11.24;2022.11.25;2022.12.26;",
   "2023.01.02;2023.01.16;2023.02.20;2023.04.07;2023.05.29;2023.06.19;2023.07.03;2023.07.04;2023.09.04;2023.11.23;2023.11.24;2023.12.25;",
   "2024.01.01;2024.01.15;2024.02.19;2024.03.29;2024.05.27;2024.06.19;2024.07.03;2024.07.04;2024.09.02;2024.11.28;2024.11.29;2024.12.24;2024.12.25;",
   "2025.01.01;2025.01.09;2025.01.20;2025.02.17;2025.04.18;2025.05.26;2025.06.19;2025.07.03;2025.07.04;2025.09.01;2025.11.27;2025.11.28;2025.12.24;2025.12.25;",
   "2026.01.01;2026.01.19;2026.02.16;2026.04.03;2026.05.25;2026.06.19;2026.07.03;2026.09.07;2026.11.26;2026.11.27;2026.12.24;2026.12.25;",
   "2027.01.01;2027.01.18;2027.02.15;2027.03.26;2027.05.31;2027.06.18;2027.07.05;2027.09.06;2027.11.25;2027.11.26;2027.12.24"
  };

int      NzMinute(const datetime t) { MqlDateTime st; TimeToStruct(t - (long)nyOff*3600, st); return st.hour*60 + st.min; }
datetime NzSrvZeit(const long nyTag, const int nyMin) { return (datetime)(nyTag*86400 + (long)nyMin*60 + (long)nyOff*3600); }
long     NzMagic(const int q) { return MagicBase + NzMagicOffset + q; }
string   NzHHMM(const int m) { return StringFormat("%02d:%02d", m/60, m%60); }

bool NzTageLesen(const string liste)
  {
   string teile[]; int n = StringSplit(liste, StringGetCharacter(";",0), teile);
   for(int i=0;i<n;i++)
     {
      string e = teile[i]; StringTrimLeft(e); StringTrimRight(e);
      if(StringLen(e) == 0) continue;
      datetime d = StringToTime(e);
      if(d <= 0) return false;
      ArrayResize(nzFrei, nNzFrei+1); nzFrei[nNzFrei++] = (long)MathFloor((double)d/86400.0);
     }
   return true;
  }

bool NzFreierTag(const long nyTag)
  {
   for(int i=0;i<nNzFrei;i++) if(nzFrei[i] == nyTag) return true;
   for(int i=0;i<ArraySize(weSdTag);i++)                                     // Sondertage nur, wenn sie vor dem Noise-Schluss enden
      if(weSdTag[i] == nyTag && weSdStd[i]*60.0 < NzSchlussMin + 5) return true;
   return false;
  }

// Eingaben pruefen, Symbol und Kontoart; false nur bei ungueltigen Eingaben
bool NzAnlegen()
  {
   nzOk = false; nzSym = ""; nzN = 0;
   // Zustand zuruecksetzen: bei Eingabe- oder Zeitrahmenwechsel behaelt MT5 die globalen Variablen (erster Durchlauf liest den Tag nach)
   nzDay = -1; nzDayOk = false; nzHaveO = false; nzStatsOk = false; nzStatsNext = 0; nzExitPending = false;
   nzLastM1 = 0; nzLastSeen0 = 0; nzO = 0.0; nzPC = 0.0; nzSd = 0.0; nzTodPrev5 = 0.0; nzTodAcc5 = 0.0;
   nzSigHeute = 0; nzEinHeute = 0; nzLetzte = "";
   for(int q=0;q<390;q++) nzSig[q] = -1.0;
   for(int s5=0;s5<78;s5++) { nzHistCR[s5] = -1.0; nzTodCR[s5] = -1.0; }
   if(NzRiskPct <= 0.0 || NzK <= 0.0 || NzTage < 5 || NzTage > 60 || NzPruefAlle < 5 || NzErstePruefung < 575 || NzLetzterEinstieg < NzErstePruefung
      || NzSchlussMin <= NzLetzterEinstieg || NzSchlussMin > 959 || NzMagicOffset < R21MagicOffset + 2*MAXSYM || NzVolaMin <= 0.0 || NzVolaMax < NzVolaMin
      || NzStopZeitPow < 0.0 || NzBudgetPct < 0.0)
     {
      Print("DEADBAND4: Noise-Eingaben ungueltig (NzRiskPct/NzK > 0, NzTage 5-60, 575 <= NzErstePruefung <= NzLetzterEinstieg < NzSchlussMin <= 959, NzMagicOffset >= R21MagicOffset + 16, NzVolaMin > 0, NzVolaMax >= NzVolaMin)");
      return false;
     }
   string t[]; int n = StringSplit(NzStops, StringGetCharacter(",",0), t);
   if(n < 1 || n > 8) { Print("DEADBAND4: NzStops braucht 1 bis 8 Werte (Tages-Sigma, Komma-getrennt)"); return false; }
   for(int q=0;q<n;q++)
     {
      string e = t[q]; StringTrimLeft(e); StringTrimRight(e);
      double v = StringToDouble(e);
      if(v <= 0.0 || v > 3.0) { PrintFormat("DEADBAND4: NzStops-Wert '%s' ungueltig (0 < Stop <= 3 Tages-Sigma)", e); return false; }
      nzStops[q] = v;
     }
   nzN = n;
   nNzFrei = 0; ArrayResize(nzFrei, 0);
   for(int i=0;i<ArraySize(NZ_FREI);i++) if(!NzTageLesen(NZ_FREI[i])) { Print("DEADBAND4: interne Noise-Feiertagsliste ungueltig"); return false; }
   if(!NzTageLesen(NzFreieTage)) { Print("DEADBAND4: NzFreieTage ungueltig (Format JJJJ.MM.TT;JJJJ.MM.TT)"); return false; }
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
     { Print("DEADBAND4: Noise-Modul AUS - Konto ist kein Hedging-Konto (Teilpositionen wuerden verschmelzen)"); return true; }
   if(SymIndex(NzSymbol) < 0)
     { PrintFormat("DEADBAND4: Noise-Modul AUS - %s steht nicht in der SymbolList", NzSymbol); return true; }
   nzSym = NzSymbol;
   nzOk = true;
   return true;
  }

void NzInitMeldung()
  {
   string st = "";
   for(int q=0;q<nzN;q++) st += (q > 0 ? "/" : "") + DoubleToString(nzStops[q], 2);
   PrintFormat("DEADBAND4: 5.00 NAS-Noise-Modul %s | %s | Risiko %.2f %% je Signal x Vola-Gewicht (%s), %d Teil(e), Stops %s Tages-Sigma x Restzeit^%.2f | Pruefung %s-%s alle %d min, Schluss %s NY | Budget %s, gesamt %.2f %% | bei Reife Modus %d | Magic %I64d-%I64d | %d handelsfreie Tage",
               (nzOk ? (NzAktiv ? "AN" : "aus (nur Verwaltung offener Positionen)") : "AUS"), NzSymbol, NzRiskPct,
               (NzVolaGewicht ? StringFormat("Verhaeltnis %.2f-%.2f hoch -%.2f", NzVolaMin, NzVolaMax, NzVolaPow) : "aus"), nzN, st, NzStopZeitPow,
               NzHHMM(NzErstePruefung), NzHHMM(NzLetzterEinstieg), NzPruefAlle, NzHHMM(NzSchlussMin),
               (NzBudgetPct > 0.0 ? StringFormat("Noise %.2f %%", NzBudgetPct) : "ohne eigenes"), GesamtBudgetPct, NzReifeModus,
               NzMagic(0), NzMagic(MathMax(nzN - 1, 0)), nNzFrei);
  }

void NzNeuerTag(const long d)
  {
   nzDay = d;
   nzHaveO = false; nzO = 0.0; nzStatsOk = false; nzStatsNext = 0; nzExitPending = false;
   for(int s5=0;s5<78;s5++) nzTodCR[s5] = -1.0;
   nzTodPrev5 = 0.0; nzTodAcc5 = 0.0;
   nzSigHeute = 0; nzEinHeute = 0; nzLetzte = "";
   int dow = (int)((d + 4) % 7);                                            // 1970-01-01 war Donnerstag -> 0 = Sonntag
   nzDayOk = !(dow == 0 || dow == 6) && !NzFreierTag(d);
  }

// Noise-Statistik aus M1: letzte NzTage gueltige Tage (Werktag, >= 300 M1-Kerzen 9:30-16:00 NY), wie ComputeNoiseStats (Flip v4)
bool NzStats(const long today)
  {
   nzStatsOk = false;
   for(int q=0;q<390;q++) nzSig[q] = -1.0;
   for(int s5=0;s5<78;s5++) nzHistCR[s5] = -1.0;
   int need = NzTage + 1;
   datetime from = NzSrvZeit(today - NZLOOKBACK, 0);
   datetime to = NzSrvZeit(today, 0);
   MqlRates r[];
   ArraySetAsSeries(r, false);
   int n = CopyRates(nzSym, PERIOD_M1, from, to - 1, r);
   if(n <= 0) { PrintFormat("DEADBAND4 %s NOISE: keine M1-Historie (Fehler %d) - neuer Versuch in 5 min", nzSym, GetLastError()); return false; }
   long   dId[NZMAXDAYS]; double dOpen[NZMAXDAYS], dClose[NZMAXDAYS]; int dCnt[NZMAXDAYS], dLastM[NZMAXDAYS];
   static double dC[NZMAXDAYS][390];
   int nd = 0; long last = -1;
   for(int i=0;i<n;i++)
     {
      long d = NYDayIndex(r[i].time);
      int m = NzMinute(r[i].time);
      if(d >= today) break;
      if(d != last)
        {
         if(nd >= NZMAXDAYS) break;
         last = d;
         dId[nd] = d; dOpen[nd] = 0.0; dClose[nd] = 0.0; dCnt[nd] = 0; dLastM[nd] = -1;
         for(int q=0;q<390;q++) dC[nd][q] = -1.0;
         nd++;
        }
      int k = nd - 1;
      if(m >= 570 && m < 960)
        {
         if(dCnt[k] == 0) dOpen[k] = (m <= 575) ? r[i].open : -1.0;
         dCnt[k]++;
         dC[k][m - 570] = r[i].close;
         dClose[k] = r[i].close;
         dLastM[k] = m;
        }
     }
   // Review 5.00 (M3): die Historie muss den letzten Handelstag bis zum Schluss enthalten, sonst waere der Vortagesschluss veraltet
   long erw = today - 1;
   for(int g=0; g<10; g++)
     {
      int dw = (int)((erw + 4) % 7);
      if(dw != 0 && dw != 6 && !NzFreierTag(erw)) break;
      erw--;
     }
   bool da = false;
   for(int k=0;k<nd;k++) if(dId[k] == erw && dLastM[k] >= 950) { da = true; break; }
   if(!da) { PrintFormat("DEADBAND4 %s NOISE: M1-Historie reicht nicht bis zum Schluss am %s - neuer Versuch in 5 min", nzSym, TimeToString((datetime)(erw*86400), TIME_DATE)); return false; }
   int vi[NZMAXDAYS]; int nv = 0;
   for(int k=0;k<nd;k++)
     {
      int dow = (int)((dId[k] + 4) % 7);
      if(dow == 0 || dow == 6) continue;
      if(dCnt[k] >= 300) vi[nv++] = k;
     }
   if(nv < need) { PrintFormat("DEADBAND4 %s NOISE: nur %d gueltige Tage in der Historie (brauche %d) - neuer Versuch in 5 min", nzSym, nv, need); return false; }
   nzPC = dClose[vi[nv - 1]];
   double rs[64]; int nr = 0;
   for(int j=nv-NzTage;j<nv;j++)
     {
      double c1 = dClose[vi[j]], c0 = dClose[vi[j - 1]];
      if(c1 > 0 && c0 > 0) rs[nr++] = MathLog(c1/c0);
     }
   if(nr < NzTage/2) { PrintFormat("DEADBAND4 %s NOISE: zu wenige Tagesrenditen", nzSym); return false; }
   double mu = 0.0; for(int j=0;j<nr;j++) mu += rs[j]; mu /= nr;
   double vv = 0.0; for(int j=0;j<nr;j++) vv += (rs[j] - mu)*(rs[j] - mu);
   nzSd = MathSqrt(vv/nr);
   for(int q=0;q<390;q++)
     {
      double sm = 0.0; int c = 0;
      for(int j=nv-NzTage;j<nv;j++)
        {
         int k = vi[j];
         if(dC[k][q] > 0 && dOpen[k] > 0) { sm += MathAbs(dC[k][q]/dOpen[k] - 1.0); c++; }
        }
      nzSig[q] = (c >= NzTage/2) ? sm/c : -1.0;
     }
   // v4: kumulierte 5-min-RV je Block, Mittel ueber dieselben Tage (fehlender Block = Wert des vorigen)
   double sumCR[78]; int cntCR[78];
   for(int s5=0;s5<78;s5++) { sumCR[s5] = 0.0; cntCR[s5] = 0; }
   for(int j=nv-NzTage;j<nv;j++)
     {
      int k = vi[j];
      if(dOpen[k] <= 0) continue;
      double prev = dOpen[k], acc = 0.0;
      bool seen = false;
      for(int s5=0;s5<78;s5++)
        {
         double v = dC[k][5*s5 + 4];
         if(v > 0) { double lr = MathLog(v/prev); acc += lr*lr; prev = v; seen = true; }
         if(seen) { sumCR[s5] += acc; cntCR[s5]++; }
        }
     }
   for(int s5=0;s5<78;s5++) if(cntCR[s5] > 0) nzHistCR[s5] = sumCR[s5]/cntCR[s5];
   nzStatsOk = (nzPC > 0 && nzSd > 0);
   if(!nzReplay)
      PrintFormat("DEADBAND4 %s NOISE: Statistik %s - %d gueltige Tage, Vortagesschluss %.2f, Tages-Sigma %.3f %%, sigma(10:00) %.3f %%",
                  nzSym, TimeToString((datetime)(today*86400), TIME_DATE), nv, nzPC, nzSd*100.0, nzSig[29]*100.0);
   return nzStatsOk;
  }

// v4: Stopfaktor nach Restzeit (Wurzel-Zeit-Regel)
double NzStopFaktor(const int endMin)
  {
   double span = (double)(NzSchlussMin - NzErstePruefung);
   if(NzStopZeitPow == 0.0 || span <= 0) return 1.0;
   double fr = MathMax(0.1, (double)(NzSchlussMin - endMin)/span);
   return MathPow(fr, NzStopZeitPow);
  }

// v4: Risiko-Gewicht nach heutiger Vola bis zur Pruefung (1 = ohne Daten)
double NzVolaGewichtWert(const int endMin, double &ratio)
  {
   ratio = -1.0;
   if(!NzVolaGewicht) return 1.0;
   int s5 = (endMin - 570)/5 - 1;
   if(s5 < 0 || s5 >= 78 || nzHistCR[s5] <= 0) return 1.0;
   double tv = -1.0;
   for(int q=s5;q>=0;q--) if(nzTodCR[q] >= 0) { tv = nzTodCR[q]; break; }
   if(tv < 0) return 1.0;
   ratio = MathSqrt(tv/nzHistCR[s5]);
   double x = MathMax(NzVolaMin, MathMin(NzVolaMax, ratio));
   return MathPow(x, -NzVolaPow);
  }

// offene Noise-Positionen (vor > 0: nur die vor diesem Zeitpunkt eroeffneten)
int NzZahl(const datetime vor = 0)
  {
   int c = 0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      if(!IsNzMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      if(vor > 0 && (datetime)PositionGetInteger(POSITION_TIME) >= vor) continue;
      c++;
     }
   return c;
  }

// Noise-Position aus einem frueheren NY-Tag offen? (Neustart, gescheiterte Schliessung)
bool NzAltePosition(const long heute)
  {
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      if(!IsNzMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      if(NYDayIndex((datetime)PositionGetInteger(POSITION_TIME)) < heute) return true;
     }
   return false;
  }

bool NzTeilOffen(const int q)
  {
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) == NzMagic(q) && PositionGetString(POSITION_SYMBOL) == nzSym) return true;
     }
   return false;
  }

// alle Noise-Positionen schliessen (vor > 0: nur die vor diesem Zeitpunkt eroeffneten); gewinnRegel = eigene Gewinnschliessung nur,
// wenn 130-s- und News-Regel es erlauben. true = alle betroffenen geschlossen (bzw. Schliessungen angenommen)
bool NzAlleSchliessen(const string grund, const bool gewinnRegel, const datetime vor = 0)
  {
   bool alle = true;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      if(!IsNzMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      if(vor > 0 && (datetime)PositionGetInteger(POSITION_TIME) >= vor) continue;
      double p = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
      if(gewinnRegel && p > 0.0 && !GewinnSchlussOk(tk, p)) { alle = false; continue; }
      if(Schliesse(tk)) PrintFormat("DEADBAND4 %s NOISE: %s - Teil #%I64u geschlossen, Ergebnis %.2f", PositionGetString(POSITION_SYMBOL), grund, tk, p);
      else
        {
         alle = false;
         PrintFormat("DEADBAND4 %s NOISE: %s - Schliessen #%I64u abgelehnt (%d %s)", NzSymbol, grund, tk, trade.ResultRetcode(), trade.ResultRetcodeDescription());
        }
     }
   nzSchliessVersuch = TimeCurrent();
   return alle;
  }

// GFT: kein Long, solange eine Short-Position im Symbol offen oder vorgemerkt ist
bool NzHedgeFrei()
  {
   if(!HedgeSperre) return true;
   int r = SymbolRichtung(nzSym, -1);
   return (r == 0 || r == 1);
  }

// Pruefung am Schluss der M1-Kerze, die um endMin endet (wie NoiseCheck in NAS100_Flip_v4, nur Long). chkEnd = Kerzenende.
// Nachgelesene (verpasste) Pruefungen holen nur den Ausstieg der damals offenen Teile nach, nie einen Einstieg.
void NzPruefung(const int endMin, const double close, const datetime chkEnd)
  {
   if(!nzHaveO || !nzStatsOk) return;
   int slot = endMin - 1 - 570;
   if(slot < 0 || slot >= 390 || nzSig[slot] < 0) return;
   double refU = MathMax(nzO, nzPC);
   double UB = refU*(1.0 + NzK*nzSig[slot]);
   int nOffen = NzZahl(chkEnd);
   // Ausstieg aller (vor der Pruefung eroeffneten) Teile, wenn der Schluss unter UB liegt
   if(nOffen > 0 && close < UB)
     {
      nzExitPending = true;
      nzLetzte = StringFormat("%s Ausstieg (Schluss %.2f < UB %.2f)%s", NzHHMM(endMin), close, UB, (nzReplay ? " nachgeholt" : ""));
      if(NzAlleSchliessen(StringFormat("Ausstieg %s%s: Schluss %.2f < UB %.2f", NzHHMM(endMin), (nzReplay ? " (nachgeholt)" : ""), close, UB), true, chkEnd)) nzExitPending = false;
      return;
     }
   nzExitPending = false;                                                    // Schluss >= UB: ein alter, gescheiterter Ausstieg ist ueberholt
   if(nzReplay) return;                                                      // verpasste Pruefung: kein Einstieg
   if(endMin > NzLetzterEinstieg || endMin >= NzSchlussMin) return;
   if(!(close > UB)) return;
   nzSigHeute++;
   string grund = "";
   if(!NzAktiv) grund = "Modul aus";
   else if(nzSperreTag) grund = "Einstiegssperre (Tagesstopp, Tagesreferenz offen oder Auszahlung heute)";
   else if(kMode != 0) grund = "Auszahlungsreife";
   else if(gGueltigSchutz) grund = GueltigSchutzText();                                    // 6.40
   else if(SerienPause()) grund = "Serien-Stopp (Verlustserie)";                          // 5.10
   else if(WeAktiv && KurzVorSchluss(TimeCurrent())) grund = "kurz vor Freitags-/Sondertag-Schluss";
   else if(NewsFenster(TimeCurrent())) grund = "News-Fenster (rote USD-Termine)";
   else if(SymbolInfoInteger(nzSym, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_FULL) grund = "Handel im Symbol eingeschraenkt";
   else if(!NzHedgeFrei()) grund = "Gegenposition im Symbol offen oder vorgemerkt (GFT: Hedging verboten)";
   if(grund != "")
     {
      nzLetzte = StringFormat("%s Signal ausgelassen: %s", NzHHMM(endMin), grund);
      PrintFormat("DEADBAND4 %s NOISE: Signal %s (Schluss %.2f > UB %.2f) ausgelassen - %s", nzSym, NzHHMM(endMin), close, UB, grund);
      return;
     }
   double tf = NzStopFaktor(endMin);
   double vratio = -1.0;
   double vw = NzVolaGewichtWert(endMin, vratio);
   double ask = SymbolInfoDouble(nzSym, SYMBOL_ASK), bid = SymbolInfoDouble(nzSym, SYMBOL_BID);
   if(ask <= 0.0 || bid <= 0.0) return;
   double mpp = MoneyPerPricePerLot(nzSym);
   double mnv = SymbolInfoDouble(nzSym, SYMBOL_VOLUME_MIN);
   double stpV = SymbolInfoDouble(nzSym, SYMBOL_VOLUME_STEP); if(stpV <= 0.0) stpV = 0.01;
   double pt = SymbolInfoDouble(nzSym, SYMBOL_POINT);
   long   stl = SymbolInfoInteger(nzSym, SYMBOL_TRADE_STOPS_LEVEL);
   double minD = (stl > 0 ? stl*pt : 0.0);
   int    dg = (int)SymbolInfoInteger(nzSym, SYMBOL_DIGITS);
   double buf = PufferPct();
   double fak = DDFaktor(buf);
   if(!peakOk) fak *= PeakUnsicherFaktor;                                    // Boden unsicher (wie DEADBAND/RSI21)
   if(AccountInfoDouble(ACCOUNT_EQUITY) < kStart) fak *= BelowStartMult;
   bool   neuQ[8]; double neuR[8];                                           // eben eroeffnete Teile (die Positionsliste kann nachhinken)
   for(int j=0;j<8;j++) { neuQ[j] = false; neuR[j] = 0.0; }
   int offen = 0;
   string info = "";
   for(int q=0;q<nzN;q++)
     {
      if(NzTeilOffen(q)) continue;
      double dist = nzStops[q]*nzO*nzSd*tf;
      if(dist <= 0.0 || dist < minD*1.2) { info += StringFormat(" [%.2f: Stop zu eng]", nzStops[q]); continue; }
      double unsicht = 0.0;                                                  // nur eben eroeffnete, noch nicht sichtbare Teile abziehen
      for(int j=0;j<q;j++) if(neuQ[j] && !NzTeilOffen(j)) unsicht += neuR[j];
      double rest = BudgetRestNz() - unsicht;
      double restI = IdeeRest(nzSym, 1);                                     // 5.10: Risiko je Idee (NAS long, alle Module)
      if(restI < DBL_MAX) rest = MathMin(rest, restI - unsicht);
      rest = MathMin(rest, BodenLuft() - unsicht);                           // 6.10: Luft bis zum Boden
      double risk = MathMin(kStart*NzRiskPct/100.0*vw/nzN*fak, rest);
      if(risk <= 0.0) { info += StringFormat(" [%.2f: Budget voll]", nzStops[q]); continue; }
      if(mnv*dist*mpp > risk*MinLotRiskTol) { info += StringFormat(" [%.2f: Mindestlot zu gross]", nzStops[q]); continue; }
      double vol = NormLot(nzSym, risk/(dist*mpp));
      if(vol < mnv) continue;
      if(vol*dist*mpp > rest + 1e-9)
        {
         vol = NormalizeDouble(MathFloor(rest/(dist*mpp)/stpV + 1e-9)*stpV, 2);
         if(vol < mnv) { info += StringFormat(" [%.2f: Budget voll]", nzStops[q]); continue; }
        }
      string mg = "";
      if(!MarginOk(nzSym, 1, vol, ask, mg)) { info += StringFormat(" [%.2f: %s]", nzStops[q], mg); continue; }
      double sl = NormalizeDouble(ask - dist, dg);
      if(bid - sl < minD) { info += StringFormat(" [%.2f: Stop am Stops-Level]", nzStops[q]); continue; }
      if(EinstiegKostetTag(nzSym, vol, "Noise")) { info += StringFormat(" [%.2f: gueltiger Tag]", nzStops[q]); continue; }   // 6.10
      trade.SetExpertMagicNumber(NzMagic(q));
      OrderMerken(nzSym, 1);                                                 // vor dem Senden (Hedging-Sperre der anderen Module)
      if(trade.Buy(vol, nzSym, 0.0, sl, 0.0, StringFormat("NOISE %.2f", nzStops[q])))
        {
         NeuMerken(nzSym, 1, vol*dist*mpp);                                  // 6.00: Budget der Fades im selben Durchlauf
         offen++; neuQ[q] = true; neuR[q] = vol*dist*mpp;
         if(kCycleStart <= 0) kCycleStart = TimeCurrent();
         info += StringFormat(" [%.2f: %.2f Lot, Stop %.*f, Risiko %.2f]", nzStops[q], vol, dg, sl, vol*dist*mpp);
        }
      else
         info += StringFormat(" [%.2f: abgelehnt %d %s]", nzStops[q], trade.ResultRetcode(), trade.ResultRetcodeDescription());
     }
   if(offen > 0) nzEinHeute++;
   nzLetzte = StringFormat("%s LONG %d Teil(e), Stopfaktor %.2f, Gewicht %.2f", NzHHMM(endMin), offen, tf, vw);
   PrintFormat("DEADBAND4 %s NOISE: LONG %s - Schluss %.2f > UB %.2f (O %.2f, Vortag %.2f, sigma %.3f %%) | Stopfaktor %.3f, Vola-Verh. %.2f, Gewicht %.3f | Puffer %.2f %% x%.2f | %d Teil(e) eroeffnet%s",
               nzSym, NzHHMM(endMin), close, UB, nzO, nzPC, nzSig[slot]*100.0, tf, vratio, vw, buf, fak, offen, info);
  }

// abgeschlossene M1-Kerze des NAS-Symbols (wie OnM1Closed in NAS100_Flip_v4, ohne Silver Bullet)
void NzBar(const MqlRates &b)
  {
   long d = NYDayIndex(b.time);
   int m = NzMinute(b.time);
   if(d != nzDay) NzNeuerTag(d);
   if(!nzDayOk) return;
   int endMin = m + 1;
   if(!nzHaveO && m >= 570 && m <= 575)
     {
      nzO = b.open; nzHaveO = true;
      nzTodPrev5 = nzO; nzTodAcc5 = 0.0;
      NzStats(d); nzStatsNext = b.time + 300;
     }
   if(nzHaveO && m >= 570 && m < 960 && (endMin % 5) == 0 && nzTodPrev5 > 0 && b.close > 0)
     {
      double lr = MathLog(b.close/nzTodPrev5);
      nzTodAcc5 += lr*lr; nzTodPrev5 = b.close;
      int s5 = (endMin - 570)/5 - 1;
      if(s5 >= 0 && s5 < 78) nzTodCR[s5] = nzTodAcc5;
     }
   if(endMin >= NzErstePruefung && ((endMin - NzErstePruefung) % NzPruefAlle) == 0 && endMin < NzSchlussMin)
      NzPruefung(endMin, b.close, b.time + 60);
  }

// je Durchlauf: neue M1-Kerzen, Tagesende, wiederholte Ausstiege
void NzDurchlauf(const bool dayLocked)
  {
   if(!nzOk)
     {
      // Modul aus (Symbol fehlt, kein Hedging-Konto, ungueltige Eingaben): vorhandene Noise-Positionen trotzdem zum Tagesende schliessen
      datetime t = TimeCurrent();
      int mm = NzMinute(t);
      if(t > 0 && NzZahl() > 0 && t - nzSchliessVersuch >= 5 && (mm >= NzSchlussMin || mm < 570 || (WeAktiv && WeSchlussJetzt(t))))
         NzAlleSchliessen("Tagesende (Modul aus)", !(mm >= NzSchlussMin + 15 || mm < 570));
      return;
     }
   nzSperreTag = dayLocked;
   datetime now = TimeCurrent();
   if(now <= 0) return;
   datetime cur0 = iTime(nzSym, PERIOD_M1, 0);
   if(cur0 > 0 && cur0 != nzLastSeen0)
     {
      bool first = (nzLastM1 == 0);
      datetime from = first ? NzSrvZeit(NYDayIndex(cur0), 0) : nzLastM1 + 60;
      MqlRates r[];
      ArraySetAsSeries(r, false);
      int n = (cur0 - 1 >= from) ? CopyRates(nzSym, PERIOD_M1, from, cur0 - 1, r) : 0;
      if(n >= 0)
        {
         nzLastSeen0 = cur0;
         datetime nowSrv = MQLInfoInteger(MQL_TESTER) ? TimeCurrent() : TimeTradeServer();
         bool conn = MQLInfoInteger(MQL_TESTER) || TerminalInfoInteger(TERMINAL_CONNECTED);
         for(int i=0;i<n;i++)
           {
            if(r[i].time <= nzLastM1 || r[i].time >= cur0) continue;
            datetime nextOpen = (i < n - 1) ? r[i + 1].time : cur0;
            nzReplay = first || !conn || (nextOpen < nowSrv - 90);          // verpasste Kerzen (Neustart, Abbruch) nur nachlesen
            NzBar(r[i]);
            nzLastM1 = r[i].time;
           }
         nzReplay = false;
         if(first && nzLastM1 == 0) nzLastM1 = cur0 - 60;
        }
     }
   long d = NYDayIndex(now);
   if(d != nzDay) NzNeuerTag(d);
   int m = NzMinute(now);
   if(nzDayOk && nzHaveO && !nzStatsOk && m < NzSchlussMin && now >= nzStatsNext) { nzStatsNext = now + 300; NzStats(nzDay); }
   int offen = NzZahl();
   if(offen == 0) { nzExitPending = false; return; }
   if(NzEinstandAbR > 0.0) NzEinstand();                                        // 6.30: je Teil Stop auf Einstand ab NzEinstandAbR
   if(now - nzSchliessVersuch < 5) return;                                     // hoechstens alle 5 s ein Schliessversuch
   // Tagesende (15:55 NY), ausserhalb der Sitzung, Freitag/Sondertag-Schluss, handelsfreier Tag oder Position aus einem Vortag: alles schliessen
   bool ende = (m >= NzSchlussMin || m < 570 || !nzDayOk || NzAltePosition(d) || (WeAktiv && WeSchlussJetzt(now)));
   if(ende)
     {
      bool erzwingen = (m >= NzSchlussMin + 15 || m < 570);                      // ab 16:10 NY ohne Gewinn-Regel
      if(NzAlleSchliessen("Tagesende " + NzHHMM(NzSchlussMin), !erzwingen)) nzExitPending = false;
      return;
     }
   if(nzExitPending)
      if(NzAlleSchliessen("Ausstieg (Wiederholung)", true)) nzExitPending = false;
  }

// bei Auszahlungsreife: Noise-Positionen schliessen (NzReifeModus 2 alle, 1 nur Gewinner)
void NzBeiReifeSchliessen()
  {
   if(NzReifeModus <= 0) return;                                             // auch bei ausgeschaltetem Modul (offene Positionen)
   datetime now = TimeCurrent();
   if(nzReifeVersuch > 0 && now - nzReifeVersuch < 30) return;
   bool versucht = false;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      if(!IsNzMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      double p = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
      if(p <= 0.0 && NzReifeModus == 1) continue;
      if(p > 0.0 && !GewinnSchlussOk(tk, p)) continue;
      versucht = true;
      if(Schliesse(tk)) PrintFormat("DEADBAND4 %s NOISE: bei Auszahlungsreife geschlossen, Ergebnis %.2f", NzSymbol, p);
      else PrintFormat("DEADBAND4 %s NOISE: Schliessen bei Reife abgelehnt (%d %s) - neuer Versuch in 30 s", NzSymbol, trade.ResultRetcode(), trade.ResultRetcodeDescription());
     }
   if(versucht) nzReifeVersuch = now;
  }

string NzStatusText()
  {
   if(!nzOk) return "AUS (Symbol fehlt, kein Hedging-Konto oder Eingaben ungueltig)";
   string t = StringFormat("%s | %.2f %% je Signal x Vola-Gewicht, %d Teil(e) | ", (NzAktiv ? "an" : "aus (nur Verwaltung)"), NzRiskPct, nzN);
   if(!nzDayOk) t += "heute kein Handelstag";
   else if(!nzHaveO) t += "wartet auf 9:30 NY";
   else if(!nzStatsOk) t += "Statistik fehlt";
   else t += StringFormat("O %.2f, Vortag %.2f, Tages-Sigma %.2f %%", nzO, nzPC, nzSd*100.0);
   int n = 0; double lots = 0.0, pl = 0.0;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      if(!IsNzMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      n++; lots += PositionGetDouble(POSITION_VOLUME); pl += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
     }
   t += StringFormat(" | offen %d (%.2f Lot, %.2f) | heute Signale %d, Einstiege %d", n, lots, pl, nzSigHeute, nzEinHeute);
   if(nzLetzte != "") t += " | " + nzLetzte;
   return t;
  }

//+------------------------------------------------------------------+
//| 6.00 Fade-Module: Fehlausbruch einer Sitzungs-Range              |
//|  Je Modul und NY-Tag D: Range = Hoch/Tief der M5-Kerzen mit      |
//|  Beginn in [D+r0, D+r0+L) (NY-Minuten, r0 negativ = Vortag).     |
//|  Im Handelsfenster danach (tlen Minuten): handelt eine Kerze     |
//|  ueber das Range-Hoch und schliesst wieder innen -> Short (unter |
//|  das Tief und wieder innen -> Long), sofern die Richtung erlaubt.|
//|  Einstieg an der naechsten Kerze, Stop hinter dem Extrem seit    |
//|  Range-Beginn plus buf x Range, Ziel Range-Mitte (tgt 0) oder    |
//|  Gegenseite (1), Ausstieg spaetestens D+r0+L+tlen+xoff (hoechs-  |
//|  tens 16:40 NY). Schliesst eine Kerze ausserhalb der Range, ist  |
//|  der Tag fuer das Modul vorbei. Hoechstens ein Signal je Tag.    |
//|  Tage nur mit Range <= mx x ATR14 (Servertage, SMA der True      |
//|  Range, letzter abgeschlossener Servertag vor Range-Beginn).     |
//|  Regime-Waechter: jedes Signal wird virtuell mitgerechnet (auch  |
//|  ohne Live-Trade). Live nur, wenn der Profitfaktor der letzten   |
//|  FadeWaechterN virtuellen Signale > FadeWaechterPF ist (mind.    |
//|  FadeWaechterMin Signale). Beim Start wird die Historie aus den  |
//|  M5-Kursen der letzten FadeHistTage Tage rekonstruiert.          |
//|  Replikat: jedes Modul auf 2022-2026 in beiden Haelften          |
//|  profitabel, vor 2022 (Fremddaten 2006-2021) NICHT -> Waechter.  |
//+------------------------------------------------------------------+
// 6.20 Probability Grid: Zustand je Symbol (Funktionen am Ende der Datei)
struct GridSer
  {
   bool     an;                // Symbol wird gefuehrt (mind. ein Fade-Modul)
   int      tfSek;             // Sekunden der Zeitebene
   bool     fertig;            // Historie geladen
   int      histFehl;
   datetime histVersuch, histAb, lastM5, b0Seen;
   bool     aggOn;             // laufende (noch offene) Zeitebenen-Kerze aus M5
   datetime aggT;
   double   aggO, aggC;
   int      n;                 // abgeschlossene Zeitebenen-Kerzen
   datetime t[];
   double   bo[], bc[];        // Open/Close (Kerzenkoerper)
   int      bias[], pivBar[], curBar[];
   double   pivPx[], curPx[];  // Zustand NACH der Kerze: letzter Pivot, laufender Extrempunkt
   int      nLeg;
   int      legConf[], legDir[], legBars[];
   double   legSz[];
   int      b, cbar, pbar, lbar;   // fetchPivot/fetchData: Richtung, Kerzen von Extrem/Pivot/letztem Pivot
   double   cpx, ppx, lpx;         // Preise dazu
  };
GridSer GR[MAXSYM];
bool    gridOk = false;
// Standard-Liste Build 6.00 (im Code, weil MT5 lange Text-Eingaben kuerzen kann): Symbol,r0,L,tlen,xoff,buf,tgt,dir,mx,Name
const string FADE_STANDARD = "NAS,630,120,60,120,0.3,0,1,0.6,N1030;NAS,810,60,120,120,1.0,0,1,0.6,N1330;XAU,390,120,180,240,1.0,1,-1,0.6,X0630;XAU,240,180,60,240,0.3,0,1,0.6,X0400;NAS,-360,180,60,120,0.3,0,1,0.6,N1800;NAS,570,180,60,120,0.3,0,1,99,N0930;NAS,660,90,60,240,0.6,1,1,0.6,N1100;NAS,780,90,60,120,0.6,0,1,0.6,N1300;XAU,180,90,60,120,0.3,0,-1,0.6,X0300S;XAU,600,180,60,240,0.3,0,-1,0.6,X1000S";
struct FadeDef
  {
   int      k;               // Symbol-Index in S[]
   int      r0, L, tlen, xoff, dir, tgt;
   double   buf, mx, pt;
   string   name;
   bool     aus;             // per FadeAus abgeschaltet (nur virtuell)
   bool     schutzFrei;      // 6.50: per GueltigSchutzFrei vom Schutz gueltiger Tage ausgenommen
   long     day;             // NY-Tag D, fuer den der Tageszustand gilt
   int      nbar;
   double   hh, ll, rng, exHi, exLo;
   bool     ready, done, skip;
   bool     vOn;             // virtueller Trade offen
   int      vDir;
   double   vEnt, vSl, vTp, vRd;
   datetime vBar;            // Einstiegskerze (Serverzeit)
   long     vX;              // Ausstieg (NY-Minute)
   double   hist[FADEHIST];  // Ergebnisse der virtuellen Trades in R (Ringpuffer)
   datetime histT[FADEHIST]; // 6.40: Zeitpunkt, ab dem das Ergebnis feststeht (Ende der Kerze = Open der naechsten), Portfolio-Waechter
   int      nh, ph, nSig;
   bool     histFertig;      // Historie rekonstruiert
   int      histFehl;
   datetime histVersuch, histAb;
   datetime lastBar;         // zuletzt gesehene (laufende) M5-Kerze
   int      sigHeute, einHeute;
   long     liveDay;         // Tag des letzten Live-Einstiegs
   double   liveGoal;        // Ziel des Live-Trades (Preis)
   datetime logZeit;         // letzte Fehlermeldung (gedrosselt)
   datetime tpVersuch, schlussVersuch;
   int      nGrid;           // 6.20: vom Probability Grid ausgelassene Signale (Historie + live)
   bool     gridAus;         // 6.20: Modul steht in GridOhne (kein Grid-Filter)
   ulong    t1Tk;            // 6.30: Position, deren Teilgewinn erledigt (oder nicht moeglich) ist
   ulong    t1Chk;           // 6.30: Position, deren Deal-Historie schon geprueft wurde
   datetime t1Versuch;       // 6.30: letzter Versuch des Teilgewinns
   int      nT1;             // 6.30: Teilgewinne seit dem Start (Panel)
  };
FadeDef  F[MAXFADE];
int      nFade = 0;
bool     fadeOk = false;
bool     fadeSperreTag = false;
bool     fadeAtrAngelegt = false;
int      fadeAtr[MAXSYM];            // nur fuer die Anzeige/den Tester (die Rechnung nutzt FadeAtr aus D1-Kerzen)
datetime fadeWaisenVersuch = 0, fadeReifeVersuch = 0;
string   fadeLetzte = "";
// eben eroeffnete Positionen ALLER Module, bis sie in der Positionsliste stehen (Budget der Fades im selben Durchlauf)
#define NEUMAX 32
string   gNeuSym[NEUMAX]; int gNeuDir[NEUMAX]; double gNeuRisk[NEUMAX]; uint gNeuMs[NEUMAX]; ulong gNeuTk[NEUMAX]; int gNeuPos = 0;
// nach JEDEM erfolgreichen Einstieg (trade.Buy/Sell) aufrufen: Symbol, Richtung, Stop-Risiko in Kontowaehrung
void NeuMerken(const string sym, const int dir, const double risk)
  {
   if(risk <= 0.0) return;
   gNeuSym[gNeuPos] = sym; gNeuDir[gNeuPos] = dir; gNeuRisk[gNeuPos] = risk; gNeuMs[gNeuPos] = GetTickCount(); gNeuTk[gNeuPos] = trade.ResultOrder();
   gNeuPos = (gNeuPos + 1) % NEUMAX;
  }

long     FadeMagic(const int m) { return MagicBase + FadeMagicOffset + m; }
bool     FadeOffsetOk() { return (FadeMagicOffset >= NzMagicOffset + 8 && FadeMagicOffset >= R21MagicOffset + 2*MAXSYM); }
bool     IsFadeMagic(const long mg)
  {
   if(!FadeOffsetOk()) return false;                                           // ungueltiger Offset: keine Ueberschneidung mit Noise/RSI21
   long o = mg - MagicBase - FadeMagicOffset;                                  // auch bei ausgeschaltetem Modul eigene Position
   return (o >= 0 && o < MAXFADE);
  }
// Fade-Zeiten mit FESTEM Versatz NYOffsetHours (wie Replikat und RSI21): Der GFT-Server laeuft in allen Sommerzeit-Phasen
// auf NY + 7 h (geprueft: Gold-Tagespause 2022-2026 immer 00:00-01:00 Serverzeit, auch in den Wochen mit abweichender
// EU-/US-Umstellung). So rechnen Historie und Live-Kerzen gleich, unabhaengig von PC-Uhr und AutoOffset.
long     FadeNyMin(const datetime t) { return (long)MathFloor((double)((long)t - (long)NYOffsetHours*3600) / 60.0); }
long     FadeFloorDiv(const long a, const long b) { return (long)MathFloor((double)a / (double)b); }
datetime FadeSrvZeit(const long nyMin) { return (datetime)(nyMin*60 + (long)NYOffsetHours*3600); }
string   FadeName(const int m) { return (StringLen(F[m].name) > 0 ? F[m].name : StringFormat("F%d", m)); }
string   FadeUhr(const long nyMin) { return NzHHMM((int)(((nyMin % 1440) + 1440) % 1440)); }

// Zeiten eines Modul-Tages (NY-Minuten seit Epoche): Range-Beginn, Range-Ende, Ende Handelsfenster, Ausstieg
void FadeZeiten(const int m, const long Dt, long &rs, long &re, long &te, long &xm)
  {
   rs = Dt*1440 + F[m].r0; re = rs + F[m].L; te = re + F[m].tlen;
   xm = MathMin(re + F[m].tlen + F[m].xoff, Dt*1440 + 1000);                   // spaetestens 16:40 NY
   if(xm <= te) te = xm - 5;
  }

// true = name steht in der ;-getrennten Liste (Gross-/Kleinschreibung egal)
bool FadeNameInListe(const string name, const string liste)
  {
   string t[]; int n = StringSplit(liste, StringGetCharacter(";",0), t);
   string a = name; StringToUpper(a);
   for(int i=0;i<n;i++) { string b = t[i]; StringTrimLeft(b); StringTrimRight(b); StringToUpper(b); if(StringLen(b) > 0 && b == a) return true; }
   return false;
  }

bool FadeListeLesen()
  {
   nFade = 0;
   string liste = FadeListe; StringTrimLeft(liste); StringTrimRight(liste);
   if(StringLen(liste) == 0) liste = FADE_STANDARD;
   string teile[]; int n = StringSplit(liste, StringGetCharacter(";",0), teile);
   for(int i=0;i<n;i++)
     {
      string x = teile[i]; StringTrimLeft(x); StringTrimRight(x);
      if(StringLen(x) == 0) continue;
      if(nFade >= MAXFADE) { PrintFormat("DEADBAND4: FadeListe hat mehr als %d Eintraege", MAXFADE); return false; }
      string f[]; int nf = StringSplit(x, StringGetCharacter(",",0), f);
      if(nf != 10) { PrintFormat("DEADBAND4: FadeListe Eintrag %d hat %d statt 10 Felder (Symbol,r0,L,tlen,xoff,buf,tgt,dir,mx,Name): %s", i+1, nf, x); return false; }
      for(int q=0;q<nf;q++) { StringTrimLeft(f[q]); StringTrimRight(f[q]); }
      string sy = f[0]; StringToUpper(sy);
      int k = -1;
      for(int q=0;q<nSym && StringLen(sy) > 0;q++) { string u = S[q].sym; StringToUpper(u); if(StringFind(u, sy) >= 0) { k = q; break; } }
      if(k < 0) { PrintFormat("DEADBAND4: FadeListe Eintrag %d - Symbol %s nicht in der SymbolList", i+1, f[0]); return false; }
      int m = nFade;
      F[m].k = k; F[m].r0 = (int)StringToInteger(f[1]); F[m].L = (int)StringToInteger(f[2]); F[m].tlen = (int)StringToInteger(f[3]);
      F[m].xoff = (int)StringToInteger(f[4]); F[m].buf = StringToDouble(f[5]); F[m].tgt = (int)StringToInteger(f[6]);
      F[m].dir = (int)StringToInteger(f[7]); F[m].mx = StringToDouble(f[8]); F[m].name = f[9];
      F[m].pt = SymbolInfoDouble(S[k].sym, SYMBOL_POINT);
      if(F[m].L < 15 || F[m].L > 600 || F[m].tlen < 5 || F[m].tlen > 600 || F[m].xoff < 0 || F[m].buf < 0.0 || (F[m].tgt != 0 && F[m].tgt != 1)
         || (F[m].dir != 1 && F[m].dir != -1 && F[m].dir != 0) || F[m].mx <= 0.0 || F[m].r0 < -420 || F[m].r0 + F[m].L > 990 || F[m].pt <= 0.0)
        { PrintFormat("DEADBAND4: FadeListe Eintrag %d ungueltig (L 15-600, tlen 5-600, xoff >= 0, buf >= 0, tgt 0/1, dir -1/0/1, mx > 0, -420 <= r0, r0+L <= 990): %s", i+1, x); return false; }
      for(int q=0;q<m;q++) if(F[q].name == F[m].name) { PrintFormat("DEADBAND4: FadeListe Name %s doppelt", F[m].name); return false; }
      F[m].aus = FadeNameInListe(F[m].name, FadeAus);
      F[m].schutzFrei = FadeNameInListe(F[m].name, GueltigSchutzFrei);             // 6.50
      F[m].gridAus = FadeNameInListe(F[m].name, GridOhne);                          // 6.20
      F[m].day = -1; F[m].nbar = 0; F[m].hh = -DBL_MAX; F[m].ll = DBL_MAX; F[m].rng = 0.0; F[m].exHi = 0.0; F[m].exLo = 0.0;
      F[m].ready = false; F[m].done = false; F[m].skip = false; F[m].vOn = false; F[m].vDir = 0;
      F[m].vEnt = 0.0; F[m].vSl = 0.0; F[m].vTp = 0.0; F[m].vRd = 0.0; F[m].vBar = 0; F[m].vX = 0;
      for(int q=0;q<FADEHIST;q++) { F[m].hist[q] = 0.0; F[m].histT[q] = 0; }
      F[m].nh = 0; F[m].ph = 0; F[m].nSig = 0; F[m].histFertig = false; F[m].histFehl = 0; F[m].histVersuch = 0; F[m].histAb = 0;
      F[m].lastBar = 0; F[m].sigHeute = 0; F[m].einHeute = 0; F[m].liveDay = -1; F[m].liveGoal = 0.0;
      F[m].logZeit = 0; F[m].tpVersuch = 0; F[m].schlussVersuch = 0; F[m].nGrid = 0;
      F[m].t1Tk = 0; F[m].t1Chk = 0; F[m].t1Versuch = 0; F[m].nT1 = 0;                  // 6.30
      nFade++;
     }
   return true;
  }

// ATR14 der Servertage (einfacher Schnitt der True Range, wie iATR) des letzten abgeschlossenen Servertags vor tSrv; 0 = unbekannt
double FadeAtr(const int m, const datetime tSrv)
  {
   string s = S[F[m].k].sym;
   int sh = iBarShift(s, PERIOD_D1, tSrv, false);
   if(sh < 0) return 0.0;
   MqlRates d[];
   ArraySetAsSeries(d, false);
   if(CopyRates(s, PERIOD_D1, sh + 1, 15, d) != 15) return 0.0;
   double sum = 0.0;
   for(int i=1;i<15;i++) sum += MathMax(d[i].high, d[i-1].close) - MathMin(d[i].low, d[i-1].close);
   return sum/14.0;
  }

double FadeKommPx(const int m)
  {
   string s = S[F[m].k].sym;
   double mpp = MoneyPerPricePerLot(s);
   return (mpp > 0.0 ? KomRundJeLot(s)/mpp : 0.0);                            // 6.10: Einstieg + Ausstieg wie gebucht
  }

// 6.10: Kommission je Lot fuer Hin- UND Rueckweg aus der Historie (Einstiegs- plus Ausstiegs-Deals); ohne Ausstiege = 2 x Einstieg
double KomRundJeLot(const string s)
  {
   static double cache[MAXSYM];
   int si = SymIndex(s);
   if(si < 0) return 0.0;
   if(komRundZeit == 0 || TimeCurrent() - komRundZeit >= 300)
     {
      komRundZeit = TimeCurrent();
      for(int q=0;q<nSym;q++)
        {
         double ci = 0.0, vi = 0.0, co = 0.0, vo = 0.0;
         for(int i=0;i<nD;i++)
           {
            if(D[i].sym != S[q].sym || !IstHandel(i) || D[i].volume <= 0.0) continue;
            if(D[i].entry == DEAL_ENTRY_IN) { ci += -D[i].comm; vi += D[i].volume; }
            else { co += -D[i].comm; vo += D[i].volume; }
           }
         double kin = (vi > 0.0 ? ci/vi : 0.0);
         cache[q] = kin + (vo > 0.0 ? co/vo : kin);
        }
     }
   return cache[si];
  }

// tBekannt: Ende der verarbeiteten Kerze (= Open der naechsten), ab dann kennt der EA das Ergebnis (6.40: Portfolio-Waechter)
void FadeVirtSchluss(const int m, const double px, const datetime tBekannt)
  {
   if(!F[m].vOn) return;
   F[m].vOn = false;
   if(F[m].vRd <= 0.0) return;
   double R = ((px - F[m].vEnt)*F[m].vDir - FadeKommPx(m)) / F[m].vRd;
   F[m].hist[F[m].ph] = R; F[m].histT[F[m].ph] = tBekannt; F[m].ph = (F[m].ph + 1) % FADEHIST; if(F[m].nh < FADEHIST) F[m].nh++;
  }

// Profitfaktor der letzten FadeWaechterN virtuellen Signale (n = Anzahl)
double FadePF(const int m, int &n)
  {
   n = MathMin(F[m].nh, MathMax(MathMin(FadeWaechterN, FADEHIST), 1));
   double pos = 0.0, neg = 0.0;
   for(int i=1;i<=n;i++)
     {
      double r = F[m].hist[(F[m].ph - i + FADEHIST) % FADEHIST];
      if(r > 0.0) pos += r; else neg -= r;
     }
   if(n == 0) return 0.0;
   return (neg > 0.0 ? pos/neg : 9.9);
  }

// 6.40: Portfolio-Waechter - Profitfaktor der letzten FadePortN virtuellen Signale ALLER Fade-Module, deren Ergebnis vor tSig
// feststand (Reihenfolge: Zeitpunkt, dann Modul - wie pg_guard.port_live_ea im Replikat). Die Signale muessen innerhalb der
// letzten FadeHistTage vor tSig liegen (so weit reicht die Historie beim Start). n = Zahl der verwendeten Signale (< FadePortN:
// zu wenige), alle = die Historien aller Module sind rekonstruiert.
double FadePortfolioPF(const datetime tSig, int &n, bool &alle)
  {
   n = 0; alle = true;
   long key[]; int nk = 0;
   ArrayResize(key, MathMax(nFade, 1)*FADEHIST);
   for(int m=0;m<nFade;m++)
     {
      if(!F[m].histFertig) alle = false;
      for(int i=0;i<F[m].nh;i++)
        {
         int slot = (F[m].ph - 1 - i + 2*FADEHIST) % FADEHIST;
         datetime t = F[m].histT[slot];
         if(t <= 0 || t >= tSig) continue;
         key[nk++] = ((long)t*16 + m)*4096 + slot;                             // Zeitpunkt, Modul (< 16), Platz (< 4096)
        }
     }
   if(nk == 0) return 0.0;
   ArrayResize(key, nk);
   ArraySort(key);
   long tMin = (long)tSig - (long)FadeHistTage*86400;
   for(int m=0;m<nFade;m++)                                                    // kuerzere M5-Historie eines Symbols: nur die Zeit, in der
      if(F[m].histFertig && (long)F[m].histAb + 86400 > tMin) tMin = (long)F[m].histAb + 86400;   // ALLE Module Ergebnisse haben
   double pos = 0.0, neg = 0.0;
   for(int i=nk-1;i>=0 && n<FadePortN;i--)
     {
      long k = key[i];
      if((k/4096)/16 < tMin) break;                                            // aelter als die Historie beim Start: zaehlt nicht
      int slot = (int)(k % 4096), m = (int)((k/4096) % 16);
      double r = F[m].hist[slot];
      if(r > 0.0) pos += r; else neg -= r;
      n++;
     }
   if(n == 0) return 0.0;
   return (neg > 0.0 ? pos/neg : 9.9);
  }

// 6.50: Regime fuer den Schutz gueltiger Tage bei RSI21 - Portfolio-Waechter der Fades zur Zeit t (Open der laufenden
//       M5-Kerze) live? Gleiche Rechnung wie FadeWaechterOk im Portfolio-Modus (unabhaengig von FadeWaechterModus), zaehlt
//       Ergebnisse, die vor t feststanden. Fades nicht geladen / Historie unvollstaendig: nicht live (RSI21 bleibt geschuetzt).
datetime fadeRegZeit = 0;
bool     fadeRegLive = false;
bool FadeRegimeLive(const datetime t)
  {
   if(FadePortPF <= 0.0) return true;                                           // Waechter aus: kein Regime-Filter
   if(!fadeOk || nFade == 0) return false;
   if(t == fadeRegZeit) return fadeRegLive;
   int n = 0; bool alle = true; double pf = FadePortfolioPF(t, n, alle);
   fadeRegZeit = t; fadeRegLive = (alle && n >= FadePortN && pf > FadePortPF);
   return fadeRegLive;
  }

string FadeRegimeText(const datetime t)
  {
   if(FadePortPF <= 0.0) return "Waechter aus";
   if(!fadeOk || nFade == 0) return "Fade-Module nicht angelegt";
   int n = 0; bool alle = true; double pf = FadePortfolioPF(t, n, alle);
   if(!alle) return "Fade-Historie noch nicht fuer alle Module geladen";
   return StringFormat("PF %.2f aus %d Signalen, live ab > %.2f aus %d", pf, n, FadePortPF, FadePortN);
  }

// Regime-Waechter: darf Modul m ein Signal mit Einstieg zur Zeit tSig live handeln?
bool FadeWaechterOk(const int m, const datetime tSig)
  {
   if(FadeWaechterModus == 1)                                                   // 6.40: Portfolio
     {
      if(FadePortPF <= 0.0) return true;
      int n = 0; bool alle = true; double pf = FadePortfolioPF(tSig, n, alle);
      return (alle && n >= FadePortN && pf > FadePortPF);
     }
   if(FadeWaechterPF <= 0.0) return true;                                      // Waechter aus
   int n = 0; double pf = FadePF(m, n);
   return (n >= FadeWaechterMin && pf > FadeWaechterPF);
  }

// Text zum Waechter-Zustand (Journal, Panel)
string FadeWaechterText(const int m, const datetime tSig)
  {
   if(FadeWaechterModus == 1)
     {
      int n = 0; bool alle = true; double pf = FadePortfolioPF(tSig, n, alle);
      if(!alle) return "Portfolio-Waechter: Historie noch nicht fuer alle Module geladen";
      return StringFormat("Portfolio-Waechter: PF %.2f aus %d Signalen aller Module (live ab > %.2f aus %d)", pf, n, FadePortPF, FadePortN);
     }
   int n = 0; double pf = FadePF(m, n);
   return StringFormat("Regime-Waechter: PF %.2f aus %d Signalen", pf, n);
  }

// Eine abgeschlossene M5-Kerze b des Modul-Symbols verarbeiten; nx = folgende Kerze (Einstieg am Open).
// live = true: ein Signal darf live gehandelt werden (nur die eben abgeschlossene Kerze, frisch).
void FadeKerze(const int m, const MqlRates &b, const MqlRates &nx, const bool live)
  {
   double pt = F[m].pt;
   long t = FadeNyMin(b.time), tn = FadeNyMin(nx.time);
   // 1) virtueller Trade: Stop vor Ziel, Ziel nicht in der Einstiegskerze, dann Zeit-Ausstieg am Open der naechsten Kerze
   if(F[m].vOn && b.time >= F[m].vBar)
     {
      double sp = b.spread*pt;
      bool slHit = false, tpHit = false;
      if(F[m].vDir > 0) { slHit = (b.low <= F[m].vSl); tpHit = (b.high >= F[m].vTp); }
      else              { slHit = (b.high + sp >= F[m].vSl); tpHit = (b.low + sp <= F[m].vTp); }
      if(slHit)
        {
         double px = F[m].vSl;
         if(F[m].vDir > 0 && b.open < F[m].vSl) px = b.open;
         if(F[m].vDir < 0 && b.open + sp > F[m].vSl) px = b.open + sp;
         FadeVirtSchluss(m, px, nx.time);
        }
      else if(tpHit && b.time > F[m].vBar) FadeVirtSchluss(m, F[m].vTp, nx.time);
     }
   if(F[m].vOn && tn >= F[m].vX)
      FadeVirtSchluss(m, F[m].vDir > 0 ? nx.open : nx.open + nx.spread*pt, nx.time);
   // 2) Tageszustand und Signal
   long Dt = FadeFloorDiv(t - F[m].r0, 1440);
   long rs, re, te, xm; FadeZeiten(m, Dt, rs, re, te, xm);
   if(Dt != F[m].day)
     {
      F[m].day = Dt; F[m].nbar = 0; F[m].hh = -DBL_MAX; F[m].ll = DBL_MAX; F[m].ready = false; F[m].done = false; F[m].skip = false;
      F[m].sigHeute = 0; F[m].einHeute = 0;
     }
   int dow = (int)(((Dt + 4) % 7 + 7) % 7);                                     // 0 = Sonntag (NY); 01.01.1970 war Donnerstag
   if(dow < 1 || dow > 5) return;
   if(t >= rs && t < re)
     {
      F[m].nbar++;
      if(b.high > F[m].hh) F[m].hh = b.high;
      if(b.low < F[m].ll) F[m].ll = b.low;
      return;
     }
   if(t < re || F[m].done || F[m].skip) return;
   if(!F[m].ready)
     {
      double a = FadeAtr(m, FadeSrvZeit(rs));
      F[m].rng = F[m].hh - F[m].ll;
      if(F[m].nbar < (F[m].L/5)*0.6 || !(a > 0.0) || F[m].rng <= 0.0 || F[m].rng > F[m].mx*a) { F[m].skip = true; return; }
      F[m].exHi = F[m].hh; F[m].exLo = F[m].ll; F[m].ready = true;
     }
   if(t >= te) { F[m].done = true; return; }
   if(b.high > F[m].exHi) F[m].exHi = b.high;
   if(b.low < F[m].exLo) F[m].exLo = b.low;
   int d = 0;
   if(b.high > F[m].hh && b.close < F[m].hh && b.close > F[m].ll) d = -1;
   else if(b.low < F[m].ll && b.close > F[m].ll && b.close < F[m].hh) d = 1;
   if(d == 0) { if(b.close > F[m].hh || b.close < F[m].ll) F[m].done = true; return; }
   F[m].done = true;                                                            // hoechstens ein Signal je Tag
   if(F[m].dir != 0 && d != F[m].dir) return;
   if(tn >= xm) return;
   double ent = nx.open + (d > 0 ? nx.spread*pt : 0.0);
   double st  = (d > 0) ? F[m].exLo - F[m].buf*F[m].rng : F[m].exHi + F[m].buf*F[m].rng;
   double goal = (F[m].tgt == 0) ? 0.5*(F[m].hh + F[m].ll) : (d > 0 ? F[m].hh : F[m].ll);
   double r = (ent - st)*d, g = (goal - ent)*d;
   if(r <= 0.0 || g <= 0.0) return;
   bool gridSperre = false;
   string gg = "";
   if(GridAktiv && !F[m].gridAus && !GridFadeOk(F[m].k, nx.time, d, st, gg))   // 6.20: Probability Grid
     {
      F[m].nGrid++;
      gridSperre = true;
      if(!GridNurLive)                                                          // Signal entfaellt ganz (auch virtuell, wie im Replikat)
        {
         if(live)
           {
            fadeLetzte = StringFormat("%s %s %s ausgelassen: Grid - %s", FadeName(m), FadeUhr(FadeNyMin(TimeCurrent())), (d > 0 ? "LONG" : "SHORT"), gg);
            PrintFormat("DEADBAND4 %s FADE %s: %s-Signal ausgelassen (auch virtuell) - Probability Grid: %s", S[F[m].k].sym, FadeName(m), (d > 0 ? "LONG" : "SHORT"), gg);
           }
         return;
        }
     }
   F[m].vOn = true; F[m].vDir = d; F[m].vEnt = ent; F[m].vSl = st; F[m].vTp = goal; F[m].vRd = r; F[m].vBar = nx.time; F[m].vX = xm;
   F[m].nSig++;
   if(live)
     {
      F[m].sigHeute++;
      if(gridSperre)                                                            // GridNurLive: nur virtuell (Waechter zaehlt es mit)
        {
         fadeLetzte = StringFormat("%s %s %s nur virtuell: Grid - %s", FadeName(m), FadeUhr(FadeNyMin(TimeCurrent())), (d > 0 ? "LONG" : "SHORT"), gg);
         PrintFormat("DEADBAND4 %s FADE %s: %s-Signal nur virtuell - Probability Grid: %s", S[F[m].k].sym, FadeName(m), (d > 0 ? "LONG" : "SHORT"), gg);
        }
      else FadeLive(m, d, st, goal, xm, nx.time);
     }
  }

// offene Fade-Position des Moduls (Ticket), 0 = keine
ulong FadePosition(const int m)
  {
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) == FadeMagic(m) && PositionGetString(POSITION_SYMBOL) == S[F[m].k].sym && FadeKommentarOk(m)) return tk;
     }
   return 0;
  }

// Kommentar der selektierten Position passt zum Modul (leer = unbekannt, gilt als passend). Nach einer Aenderung der
// FadeListe verwaltet so kein fremdes Modul die Position; sie wird als Waise geschlossen.
bool FadeKommentarOk(const int m)
  {
   string c = PositionGetString(POSITION_COMMENT);
   return (StringLen(c) == 0 || c == "FADE " + FadeName(m));
  }

// Stop-Risiko, das OffenesRisiko/IdeeRisiko noch nicht sehen (gesamt / gleiche Idee): eben eroeffnete Positionen aller
// Module (Register NeuMerken) und vorgemerkte Wochenend-Wiederaufnahmen (Obergrenze WeStopMaxR x R).
double FadeUnsichtbar(const string s, const int d, double &idee)
  {
   double r = 0.0; idee = 0.0;
   uint jetzt = GetTickCount();
   for(int i=0;i<NEUMAX;i++)
     {
      if(gNeuRisk[i] <= 0.0) continue;
      if(jetzt - gNeuMs[i] > 10000 || (gNeuTk[i] > 0 && PositionSelectByTicket(gNeuTk[i]))) { gNeuRisk[i] = 0.0; continue; }   // Hedging-Konto: Positions-Ticket = Order-Ticket
      r += gNeuRisk[i];
      if(gNeuSym[i] == s && gNeuDir[i] == d) idee += gNeuRisk[i];
     }
   if(WeAktiv)
      for(int k=0;k<nSlot;k++)
        {
         if(!W[k].aktiv || W[k].lots <= 0.0) continue;
         double mpp = MoneyPerPricePerLot(S[k].sym);
         double px = (W[k].dir > 0 ? SymbolInfoDouble(S[k].sym, SYMBOL_ASK) : SymbolInfoDouble(S[k].sym, SYMBOL_BID));
         double dist = (W[k].sl > 0.0 && px > 0.0) ? (px - W[k].sl)*W[k].dir : 0.0;
         double cap  = (WeStopMaxR > 0.0 ? WeStopMaxR*W[k].rd : 0.0);
         if(dist <= 0.0 || (cap > 0.0 && dist > cap)) dist = (cap > 0.0 ? cap : W[k].rd);
         double wr = W[k].lots*dist*mpp;
         r += wr;
         if(S[k].sym == s && W[k].dir == d) idee += wr;
        }
   return r;
  }

// Hedging-Sperre fuer Fades (wie HedgeFrei, ohne Platz-Bezug)
bool FadeHedgeFrei(const int k, const int d)
  {
   if(!HedgeSperre) return true;
   int r = SymbolRichtung(S[k].sym, -1);
   return (r == 0 || r == d);
  }

void FadeLive(const int m, const int d, const double st, const double goal, const long xm, const datetime tSig)
  {
   int k = F[m].k; string s = S[k].sym;
   string grund = "";
   if(!FadeAktiv) grund = "Modul aus";
   else if(F[m].aus) grund = "Modul per FadeAus abgeschaltet";
   else if(!kBereit) grund = "Kontodaten fehlen";
   else if(fadeSperreTag) grund = "Einstiegssperre (Tagesstopp, Tagesreferenz offen oder Auszahlung heute)";
   else if(kMode != 0) grund = "Auszahlungsreife";
   else if(gGueltigSchutz && !F[m].schutzFrei) grund = GueltigSchutzText();              // 6.40 (6.50: GueltigSchutzFrei ausgenommen)
   else if(SerienPause()) grund = "Serien-Stopp (Verlustserie)";
   else if(!FadeWaechterOk(m, tSig)) grund = FadeWaechterText(m, tSig);
   else if(WeAktiv && KurzVorSchluss(TimeCurrent())) grund = "kurz vor Freitags-/Sondertag-Schluss";
   else if(NewsFenster(TimeCurrent())) grund = "News-Fenster (rote USD-Termine)";
   else if(NzFreierTag(FadeFloorDiv(FadeNyMin(TimeCurrent()), 1440)) || NzFreierTag(FadeFloorDiv(xm, 1440))) grund = "US-Feiertag/verkuerzter Handelstag (Ausstieg koennte in die Schliessung fallen)";
   else if(SymbolInfoInteger(s, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_FULL) grund = "Handel im Symbol eingeschraenkt";
   else if(FadePosition(m) != 0 || F[m].liveDay == F[m].day) grund = "Modul hat heute schon gehandelt";
   else if(!FadeHedgeFrei(k, d)) grund = "Gegenposition im Symbol offen oder vorgemerkt (GFT: Hedging verboten)";
   if(grund != "")
     {
      fadeLetzte = StringFormat("%s %s %s ausgelassen: %s", FadeName(m), FadeUhr(FadeNyMin(TimeCurrent())), (d > 0 ? "LONG" : "SHORT"), grund);
      PrintFormat("DEADBAND4 %s FADE %s: %s-Signal ausgelassen - %s", s, FadeName(m), (d > 0 ? "LONG" : "SHORT"), grund);
      return;
     }
   double ask = SymbolInfoDouble(s, SYMBOL_ASK), bid = SymbolInfoDouble(s, SYMBOL_BID);
   if(ask <= 0.0 || bid <= 0.0) return;
   double ent = (d > 0 ? ask : bid);
   double rd = (ent - st)*d, g = (goal - ent)*d;
   double pt = F[m].pt;
   long stl = SymbolInfoInteger(s, SYMBOL_TRADE_STOPS_LEVEL);
   double minD = (stl > 0 ? stl*pt : 0.0);
   if(rd <= 0.0 || g <= 0.0 || rd <= minD*1.2)
     { PrintFormat("DEADBAND4 %s FADE %s: Kurs schon jenseits von Stop/Ziel oder Stop zu eng - ausgelassen", s, FadeName(m)); return; }
   if(FadeMinStopSpreads > 0.0 && rd < FadeMinStopSpreads*(ask - bid))
     {
      fadeLetzte = StringFormat("%s %s ausgelassen: Stop %.1f Spreads (< %.1f)", FadeName(m), FadeUhr(FadeNyMin(TimeCurrent())), rd/MathMax(ask - bid, 1e-10), FadeMinStopSpreads);
      PrintFormat("DEADBAND4 %s FADE %s: Stop nur %.1f Spreads entfernt (< %.1f) - ausgelassen (Reserve der -1-%%-Regel bei Kursspruengen)", s, FadeName(m), rd/MathMax(ask - bid, 1e-10), FadeMinStopSpreads);
      return;
     }
   // Groesse: Risiko x Pufferkurve (wie Noise/RSI21), gedeckelt durch Gesamtbudget und Risiko je Idee
   double buf = PufferPct();
   double fak = DDFaktor(buf);
   if(!peakOk) fak *= PeakUnsicherFaktor;                                     // Boden unsicher
   if(AccountInfoDouble(ACCOUNT_EQUITY) < kStart) fak *= BelowStartMult;
   double risk = kStart*FadeRiskPct/100.0*fak;
   double ideeU = 0.0;
   double unsicht = FadeUnsichtbar(s, d, ideeU);                              // eben eroeffnete (alle Module) und vorgemerkte Positionen
   double rest = (GesamtBudgetPct > 0.0) ? kStart*GesamtBudgetPct/100.0 - OffenesRisiko(0) - unsicht : DBL_MAX;
   double restI = IdeeRest(s, d);
   if(restI < DBL_MAX) rest = MathMin(rest, restI - ideeU);
   rest = MathMin(rest, BodenLuft() - unsicht);                                // 6.10: Luft bis zum Boden
   if(rest < DBL_MAX) risk = MathMin(risk, rest);
   if(risk <= 0.0) { PrintFormat("DEADBAND4 %s FADE %s: Risikobudget oder Luft bis zum Boden voll - ausgelassen", s, FadeName(m)); return; }
   double mpp = MoneyPerPricePerLot(s);
   double mnv = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN);
   double stpV = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP); if(stpV <= 0.0) stpV = 0.01;
   if(mpp <= 0.0) return;
   if(mnv*rd*mpp > risk*MinLotRiskTol) { PrintFormat("DEADBAND4 %s FADE %s: Mindestlot zu gross fuer das Risiko - ausgelassen", s, FadeName(m)); return; }
   double vol = NormLot(s, risk/(rd*mpp));
   if(vol < mnv) return;
   if(rest < DBL_MAX && vol*rd*mpp > rest + 1e-9)
     {
      vol = NormalizeDouble(MathFloor(rest/(rd*mpp)/stpV + 1e-9)*stpV, 2);
      if(vol < mnv) { PrintFormat("DEADBAND4 %s FADE %s: Risikobudget voll - ausgelassen", s, FadeName(m)); return; }
     }
   { string mg = ""; if(!MarginOk(s, d, vol, ent, mg)) { PrintFormat("DEADBAND4 %s FADE %s: %s - ausgelassen", s, FadeName(m), mg); return; } }
   int dg = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
   double sl = NormalizeDouble(st, dg);
   if((d > 0 && bid - sl < minD) || (d < 0 && sl - ask < minD)) { PrintFormat("DEADBAND4 %s FADE %s: Stop am Stops-Level - ausgelassen", s, FadeName(m)); return; }
   if(EinstiegKostetTag(s, vol, "FADE " + FadeName(m))) return;               // 6.10: gueltigen Tag nicht verlieren
   trade.SetExpertMagicNumber((ulong)FadeMagic(m));
   OrderMerken(s, d);                                                          // vor dem Senden (Hedging-Sperre der anderen Module)
   bool ok = (d > 0) ? trade.Buy(vol, s, 0.0, sl, 0.0, "FADE " + FadeName(m)) : trade.Sell(vol, s, 0.0, sl, 0.0, "FADE " + FadeName(m));
   if(ok)
     {
      OrderMerken(s, d);
      NeuMerken(s, d, vol*rd*mpp);
      F[m].liveDay = F[m].day; F[m].liveGoal = goal; F[m].einHeute++; F[m].tpVersuch = 0; F[m].schlussVersuch = 0;
      if(kCycleStart <= 0) kCycleStart = TimeCurrent();
      fadeLetzte = StringFormat("%s %s %s %.2f Lot, Stop %.*f, Ziel %.*f (%.2f R) ab %d s, Ausstieg %s NY", FadeName(m), FadeUhr(FadeNyMin(TimeCurrent())),
                                (d > 0 ? "LONG" : "SHORT"), vol, dg, sl, dg, goal, g/rd, FadeZielAbSek, FadeUhr(xm));
      PrintFormat("DEADBAND4 %s FADE %s | Risiko %.2f (Puffer %.2f %% x%.2f), Range %.*f-%.*f", s, fadeLetzte, vol*rd*mpp, buf, fak, dg, F[m].ll, dg, F[m].hh);
     }
   else
      PrintFormat("DEADBAND4 %s FADE %s: Einstieg abgelehnt (%d %s)", s, FadeName(m), trade.ResultRetcode(), trade.ResultRetcodeDescription());
  }

// Verwaltung der Live-Position: Ziel nach FadeZielAbSek setzen, Zeit-Ausstieg, Freitag/Sondertag
void FadeVerwalten(const int m)
  {
   ulong tk = FadePosition(m);
   if(tk == 0 || !PositionSelectByTicket(tk)) return;
   string s = S[F[m].k].sym;
   datetime now = TimeCurrent();
   long nyNow = FadeNyMin(now);
   datetime tOpen = (datetime)PositionGetInteger(POSITION_TIME);
   int d = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1);
   double tpAlt = PositionGetDouble(POSITION_TP), slAlt = PositionGetDouble(POSITION_SL);
   double p = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
   // Ausstieg und Ziel aus dem Eroeffnungstag (auch nach Neustart)
   long Dt = FadeFloorDiv(FadeNyMin(tOpen) - F[m].r0, 1440);
   long rs, re, te, xm; FadeZeiten(m, Dt, rs, re, te, xm);
   bool schluss = (nyNow >= xm) || (WeAktiv && WeSchlussJetzt(now));
   if(schluss)
     {
      if(now - F[m].schlussVersuch < 5) return;
      if(p > 0.0 && !GewinnSchlussOk(tk, p) && nyNow < xm + 15) return;           // 2-Minuten-/News-Regel: Gewinnschluss bis 15 min verschieben
      F[m].schlussVersuch = now;
      if(Schliesse(tk)) { fadeLetzte = StringFormat("%s Zeit-Ausstieg %s NY, Ergebnis %.2f", FadeName(m), FadeUhr(nyNow), p); PrintFormat("DEADBAND4 %s FADE %s", s, fadeLetzte); }
      else if(now - F[m].logZeit >= 60) { F[m].logZeit = now; PrintFormat("DEADBAND4 %s FADE %s: Zeit-Ausstieg abgelehnt (%d %s) - neuer Versuch alle 5 s", s, FadeName(m), trade.ResultRetcode(), trade.ResultRetcodeDescription()); }
      return;
     }
   if(FadeT1R > 0.0 && F[m].t1Tk != tk && FadeTeilgewinn(m, tk)) return;       // 6.30: Teilgewinn ab FadeT1R (Ziel im naechsten Durchlauf)
   if(!PositionSelectByTicket(tk)) return;
   if(tpAlt > 0.0) return;
   double goal = 0.0;
   if(F[m].liveDay == Dt && F[m].liveGoal > 0.0) goal = F[m].liveGoal;
   else if(F[m].day == Dt && F[m].ready) goal = (F[m].tgt == 0) ? 0.5*(F[m].hh + F[m].ll) : (d > 0 ? F[m].hh : F[m].ll);   // nach Neustart aus der Historie
   if(goal <= 0.0) return;
   if(now - tOpen < MathMax(FadeZielAbSek, 120)) return;
   {                                                                           // 6.10: wie im Replikat erst ab der Kerze nach der Einstiegskerze
    int ps = PeriodSeconds(PERIOD_M5);
    datetime b0 = iTime(s, PERIOD_M5, 0);
    datetime naechste = (datetime)((long)tOpen - (long)tOpen % ps + ps);
    if(b0 <= 0 || b0 < naechste) return;
   }
   if(now - F[m].tpVersuch < 10) return;
   F[m].tpVersuch = now;
   double bid = SymbolInfoDouble(s, SYMBOL_BID), ask = SymbolInfoDouble(s, SYMBOL_ASK);
   if(bid <= 0.0 || ask <= 0.0) return;
   bool erreicht = (d > 0) ? (bid >= goal) : (ask <= goal);
   if(erreicht)
     {
      if(GewinnSchlussOk(tk, p) && Schliesse(tk)) { fadeLetzte = StringFormat("%s Ziel erreicht, geschlossen, Ergebnis %.2f", FadeName(m), p); PrintFormat("DEADBAND4 %s FADE %s", s, fadeLetzte); }
      return;
     }
   int dg = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
   long stl = SymbolInfoInteger(s, SYMBOL_TRADE_STOPS_LEVEL);
   double minD = (stl > 0 ? stl*F[m].pt : 0.0);
   double tp = NormalizeDouble(goal, dg);
   if((d > 0 && tp - bid < minD) || (d < 0 && ask - tp < minD)) return;
   trade.SetExpertMagicNumber((ulong)FadeMagic(m));
   if(trade.PositionModify(tk, slAlt, tp)) PrintFormat("DEADBAND4 %s FADE %s: Ziel %.*f gesetzt", s, FadeName(m), dg, tp);
   else if(now - F[m].logZeit >= 60) { F[m].logZeit = now; PrintFormat("DEADBAND4 %s FADE %s: Ziel setzen abgelehnt (%d %s) - neuer Versuch alle 10 s", s, FadeName(m), trade.ResultRetcode(), trade.ResultRetcodeDescription()); }
  }

// Fade-Positionen ohne passendes Modul (Liste geaendert oder ungueltig): spaetestens nach 8 h, ab 16:40 NY oder
// zum Freitags-/Sondertag-Schluss schliessen (Gewinner nach der 2-Minuten-/News-Regel)
void FadeWaisen()
  {
   static datetime waisenLog = 0;
   datetime now = TimeCurrent();
   if(now <= 0 || now - fadeWaisenVersuch < 5) return;
   long nyNow = FadeNyMin(now);
   int mNy = (int)(((nyNow % 1440) + 1440) % 1440);
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      long mg = PositionGetInteger(POSITION_MAGIC);
      if(!IsFadeMagic(mg)) continue;
      int m = (int)(mg - MagicBase - FadeMagicOffset);
      if(fadeOk && m < nFade && PositionGetString(POSITION_SYMBOL) == S[F[m].k].sym && FadeKommentarOk(m)) continue;   // wird vom Modul verwaltet
      datetime tOpen = (datetime)PositionGetInteger(POSITION_TIME);
      bool faellig = (now - tOpen >= 8*3600) || (mNy >= 1000 && mNy < 1020) || (WeAktiv && WeSchlussJetzt(now));
      if(!faellig) continue;
      double p = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
      if(p > 0.0 && !GewinnSchlussOk(tk, p) && now - tOpen < 9*3600) continue;
      fadeWaisenVersuch = now;
      if(Schliesse(tk)) PrintFormat("DEADBAND4 FADE: Position #%I64u ohne Modul (Magic %I64d) geschlossen, Ergebnis %.2f", tk, mg, p);
      else if(now - waisenLog >= 60) { waisenLog = now; PrintFormat("DEADBAND4 FADE: Position #%I64u ohne Modul - Schliessen abgelehnt (%d %s)", tk, trade.ResultRetcode(), trade.ResultRetcodeDescription()); }
     }
  }

// Historie rekonstruieren (virtuelle Signale der letzten FadeHistTage Tage); false = Kurse noch nicht (vollstaendig) da
bool FadeHistorie(const int m)
  {
   string s = S[F[m].k].sym;
   if(!F[m].gridAus && !GridBereit(F[m].k)) return false;                        // 6.20: erst die Schenkel-Statistik (GridHistorie gibt nach 20 Versuchen selbst auf)
   datetime bis = iTime(s, PERIOD_M5, 0);
   if(bis <= 0) return false;
   datetime von = bis - (datetime)FadeHistTage*86400;
   MqlRates r[];
   ArraySetAsSeries(r, false);
   int n = CopyRates(s, PERIOD_M5, von, bis, r);
   int maxBars = TerminalInfoInteger(TERMINAL_MAXBARS);
   bool genug = false;
   if(n >= 3 && r[n-1].time == bis)
     {
      datetime ab = (r[0].time > von ? r[0].time : von);
      int nd = Bars(s, PERIOD_D1);
      datetime d1Ab = (nd > 0 ? iTime(s, PERIOD_D1, nd - 1) : 0);                // Tageskerzen fuer die ATR ab Beginn der M5-Historie
      datetime srvAb = (datetime)SeriesInfoInteger(s, PERIOD_M5, SERIES_SERVER_FIRSTDATE);   // aeltestes Datum des Symbols auf dem Server
      bool m5Ok = (r[0].time <= von + 20*86400 || (maxBars > 0 && n >= maxBars - 1000) || (srvAb > 0 && r[0].time <= srvAb + 3*86400));
      bool d1Ok = (d1Ab > 0 && (d1Ab <= ab - 20*86400 || (srvAb > 0 && d1Ab <= srvAb + 3*86400)));
      genug = m5Ok && d1Ok;
     }
   if(!genug && F[m].histFehl < 20) { F[m].histFehl++; return false; }        // Kurse werden noch geladen: spaeter erneut (bis 20 Versuche)
   // Zustand zuruecksetzen und nachrechnen
   F[m].day = -1; F[m].vOn = false; F[m].nh = 0; F[m].ph = 0; F[m].nSig = 0; F[m].nGrid = 0;
   if(n >= 3)
     {
      for(int i=0;i<n-1;i++) FadeKerze(m, r[i], r[i+1], false);
      F[m].lastBar = r[n-1].time; F[m].histAb = r[0].time;
     }
   else { F[m].lastBar = bis; F[m].histAb = bis; }
   F[m].histFertig = true;
   int nn = 0; double pf = FadePF(m, nn);
   PrintFormat("DEADBAND4 FADE %s (%s, Range %s + %d min, Fenster %d, Ausstieg +%d, Puffer %.2f, Ziel %s, %s, Range <= %.2f ATR): Historie ab %s (%d M5), %d Signale, PF der letzten %d = %.2f -> %s",
               FadeName(m), s, FadeUhr(F[m].r0), F[m].L, F[m].tlen, F[m].xoff, F[m].buf,
               (F[m].tgt == 0 ? "Mitte" : "Gegenseite"), (F[m].dir > 0 ? "long" : (F[m].dir < 0 ? "short" : "beide")), F[m].mx,
               TimeToString(F[m].histAb, TIME_DATE), n, F[m].nSig, nn, pf,
               (FadeWaechterModus == 1 ? "Portfolio-Waechter (Stand nach dem Laden aller Module)" : (FadeWaechterOk(m, TimeCurrent()) ? "LIVE" : "nur virtuell")));
   if(FadeWaechterModus == 0 && FadeWaechterPF > 0.0 && nn < FadeWaechterMin)
      PrintFormat("DEADBAND4 FADE %s: nur %d virtuelle Signale in der Historie (Waechter braucht %d) - Modul bleibt virtuell, bis genug Signale da sind. Abhilfe: Extras > Optionen > Charts > Max. Balken im Chart = Unbegrenzt, Terminal neu starten.%s",
                  FadeName(m), nn, FadeWaechterMin,
                  (F[m].nGrid > 0 && !GridNurLive ? StringFormat(" Das Probability Grid hat %d Signale ausgelassen - Modul in GridOhne eintragen oder GridNurLive=true.", F[m].nGrid) : ""));
   if(FadeWaechterModus == 1)                                                  // 6.40: Stand des Portfolio-Waechters, sobald alle Module geladen sind
     {
      bool alleFertig = true;
      for(int q=0;q<nFade;q++) if(!F[q].histFertig) alleFertig = false;
      if(alleFertig)
        {
         int np = 0; bool alle = true; double pfp = FadePortfolioPF(TimeCurrent(), np, alle);
         PrintFormat("DEADBAND4 FADE Portfolio-Waechter: PF %.2f aus den letzten %d virtuellen Signalen aller %d Module (innerhalb %d Tagen) -> %s",
                     pfp, np, nFade, FadeHistTage, (FadeWaechterOk(0, TimeCurrent()) ? "Fades LIVE" : "Fades nur virtuell"));
         if(np < FadePortN)
            PrintFormat("DEADBAND4 FADE: nur %d virtuelle Signale in %d Tagen (Portfolio-Waechter braucht %d) - Fades bleiben virtuell, bis genug Signale da sind. Abhilfe: Extras > Optionen > Charts > Max. Balken im Chart = Unbegrenzt, Terminal neu starten.",
                        np, FadeHistTage, FadePortN);
        }
     }
   return true;
  }

void FadeDurchlauf(const bool dayLocked)
  {
   FadeWaisen();
   if(!fadeOk) return;
   GridDurchlauf();                                                            // 6.20: Schenkel-Statistik vor den Fade-Kerzen aktualisieren
   fadeSperreTag = dayLocked;
   datetime now = TimeCurrent();
   for(int m=0;m<nFade;m++)
     {
      string s = S[F[m].k].sym;
      if(!F[m].histFertig)
        {
         if(now - F[m].histVersuch >= 15) { F[m].histVersuch = now; FadeHistorie(m); }
         FadeVerwalten(m);                                                     // Zeit-Ausstieg auch ohne Historie
         continue;
        }
      datetime b0 = iTime(s, PERIOD_M5, 0);
      if(b0 > 0 && b0 > F[m].lastBar)
        {
         MqlRates r[];
         ArraySetAsSeries(r, false);
         int n = CopyRates(s, PERIOD_M5, F[m].lastBar, b0, r);
         if(n >= 2 && r[n-1].time == b0 && (F[m].gridAus || GridAktuell(F[m].k, r[n-2].time)))   // 6.20: das Grid muss die Kerze vor b0 kennen
           {
            bool frisch = (TimeCurrent() - b0 < 60) && (b0 - r[n-2].time == PeriodSeconds(PERIOD_M5));   // nur die unmittelbar vorige Kerze, sofort nach Beginn der neuen (nach Datenluecken nie live)
            for(int i=0;i<n-1;i++)
               if(r[i].time >= F[m].lastBar) FadeKerze(m, r[i], r[i+1], frisch && i == n-2);
            F[m].lastBar = b0;
           }
        }
      FadeVerwalten(m);
     }
  }

// bei Auszahlungsreife: alle Fade-Positionen schliessen (Gewinner nach der 2-Minuten-/News-Regel)
void FadeBeiReifeSchliessen()
  {
   datetime now = TimeCurrent();
   if(fadeReifeVersuch > 0 && now - fadeReifeVersuch < 30) return;
   bool v = false;
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      if(!IsFadeMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      double p = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
      if(p > 0.0 && !GewinnSchlussOk(tk, p)) continue;
      v = true;
      string sy = PositionGetString(POSITION_SYMBOL);
      if(Schliesse(tk)) PrintFormat("DEADBAND4 %s FADE: bei Auszahlungsreife geschlossen, Ergebnis %.2f", sy, p);
      else PrintFormat("DEADBAND4 %s FADE: Schliessen bei Reife abgelehnt (%d %s) - neuer Versuch in 30 s", sy, trade.ResultRetcode(), trade.ResultRetcodeDescription());
     }
   if(v) fadeReifeVersuch = now;
  }

bool FadeAnlegen()
  {
   fadeOk = false; nFade = 0; fadeSperreTag = false; fadeWaisenVersuch = 0; fadeReifeVersuch = 0; fadeLetzte = "";
   fadeRegZeit = 0; fadeRegLive = false;                                 // 6.50
   gridOk = false; for(int k=0;k<MAXSYM;k++) GridReset(k);                   // 6.20: kein Grid-Zustand aus einem frueheren Lauf
   for(int i=0;i<NEUMAX;i++) { gNeuRisk[i] = 0.0; gNeuTk[i] = 0; gNeuMs[i] = 0; gNeuSym[i] = ""; gNeuDir[i] = 0; }
   gNeuPos = 0;
   for(int k=0;k<MAXSYM;k++) fadeAtr[k] = INVALID_HANDLE;
   fadeAtrAngelegt = true;
   if(!FadeOffsetOk()) { PrintFormat("DEADBAND4: FadeMagicOffset muss >= NzMagicOffset + 8 und >= R21MagicOffset + %d sein - Fade-Module AUS", 2*MAXSYM); return false; }
   if(FadeRiskPct <= 0.0 || FadeRiskPct > 1.0 || FadeWaechterN < 1 || FadeWaechterN > FADEHIST || FadeWaechterMin < 1 || FadeWaechterMin > FadeWaechterN
      || FadeHistTage < 30 || FadeHistTage > 2000 || FadeZielAbSek < 120 || FadeMinStopSpreads < 0.0
      || (FadeWaechterModus != 0 && FadeWaechterModus != 1) || FadePortN < 10 || FadePortN > FADEHIST || FadePortPF < 0.0)   // 6.40
     { PrintFormat("DEADBAND4: Fade-Eingaben ungueltig (0 < FadeRiskPct <= 1, 1 <= FadeWaechterMin <= FadeWaechterN <= %d, FadeHistTage 30-2000, FadeZielAbSek >= 120, FadeMinStopSpreads >= 0, FadeWaechterModus 0/1, 10 <= FadePortN <= %d, FadePortPF >= 0) - Fade-Module AUS", FADEHIST, FADEHIST); return false; }
   if(!FadeListeLesen()) { Print("DEADBAND4: FadeListe ungueltig - Fade-Module AUS"); nFade = 0; return false; }
   if(nFade == 0) { Print("DEADBAND4: FadeListe leer - Fade-Module AUS"); return true; }
   for(int m=0;m<nFade;m++)
     {
      int k = F[m].k;
      if(fadeAtr[k] == INVALID_HANDLE) fadeAtr[k] = iATR(S[k].sym, PERIOD_D1, 14);   // laedt die D1-Historie vor (Rechnung in FadeAtr)
     }
   if(!GridAnlegen()) { Print("DEADBAND4: Probability Grid - Eingaben ungueltig, der EA startet nicht (Eingaben korrigieren oder GridAktiv=false)"); nFade = 0; return false; }   // 6.20
   fadeOk = true;
   return true;
  }

void FadeFreigeben()
  {
   if(!fadeAtrAngelegt) return;
   for(int k=0;k<MAXSYM;k++) if(fadeAtr[k] != INVALID_HANDLE) { IndicatorRelease(fadeAtr[k]); fadeAtr[k] = INVALID_HANDLE; }
  }

void FadeInitMeldung()
  {
   string t = "";
   for(int m=0;m<nFade;m++)
      t += StringFormat("%s%s %s %s+%d/%d/+%d %s%s", (m > 0 ? "; " : ""), FadeName(m), S[F[m].k].sym, FadeUhr(F[m].r0), F[m].L, F[m].tlen, F[m].xoff,
                        (F[m].dir > 0 ? "long" : (F[m].dir < 0 ? "short" : "beide")), (F[m].aus ? " (AUS)" : ""));
   string wt = (FadeWaechterModus == 1 ? StringFormat("Portfolio-Waechter (6.40): PF > %.2f aus den letzten %d virtuellen Signalen ALLER Module", FadePortPF, FadePortN)
                                        : StringFormat("Waechter je Modul: PF > %.2f aus den letzten %d virtuellen Signalen (mind. %d)", FadeWaechterPF, FadeWaechterN, FadeWaechterMin));
   PrintFormat("DEADBAND4: 6.00 Fade-Module %s | %d Modul(e): %s | Risiko %.2f %% je Trade x Pufferkurve | %s | Historie %d Tage (Max. Balken im Chart %d) | Ziel ab %d s | Stop mind. %.1f Spreads | Zeiten NY = Server - %d h (fest) | Magic %I64d-%I64d | DEADBAND-Einstiege %s",
               (fadeOk ? (FadeAktiv ? "AN" : "aus (nur Verwaltung, virtuell)") : "AUS"), nFade, (StringLen(FadeListe) > 0 ? "eigene Liste: " : "Standard: ") + t, FadeRiskPct, wt,
               FadeHistTage, TerminalInfoInteger(TERMINAL_MAXBARS), FadeZielAbSek, FadeMinStopSpreads, NYOffsetHours, FadeMagic(0), FadeMagic(MAXFADE - 1), (DbAktiv ? "AN" : "AUS (DbAktiv=false)"));
   PrintFormat("DEADBAND4: 6.20 Probability Grid %s | Zeitebene M%d aus M5, Swing Length %d, je Richtung die letzten %d Schenkel (mind. %d) | Regel S: kein Fade gegen den Lauf ab %.0f %% Stop-Chance%s | Regel A: %s | Vorlauf %d Tage vor der Fade-Historie | %s",
               (GridAktiv ? (gridOk ? "AN" : "AUS (Eingaben ungueltig)") : "aus (Fades wie 6.10)"), PeriodSeconds(GridTF)/60, GridLaenge, GridMaxSchenkel, GridMinSchenkel,
               GridMaxStopChance*100.0, (GridMaxStopChance > 0.0 ? "" : " (aus)"), (GridMinReife > 0.0 ? StringFormat("Lauf mind. %.0f. Perzentil", GridMinReife*100.0) : "aus"), GridVorlaufTage,
               (GridNurLive ? "gesperrte Signale zaehlen im Waechter mit (GridNurLive)" : "gesperrte Signale entfallen auch im Waechter") + (StringLen(GridOhne) > 0 ? " | ohne Grid: " + GridOhne : ""));
   if(fadeOk && nyOff != NYOffsetHours)
      PrintFormat("DEADBAND4: ACHTUNG - gemessener NY-Versatz %d h, die Fade-Module rechnen fest mit NYOffsetHours=%d h (GFT: Server = NY + 7 h). Broker-Serverzeit und PC-Uhr pruefen.", nyOff, NYOffsetHours);
  }

string FadeStatusText()
  {
   if(!fadeOk) return "AUS";
   string t = StringFormat("%s | %.2f %% je Trade, Waechter PF > %.2f aus %d |", (FadeAktiv ? "an" : "aus (nur Verwaltung)"), FadeRiskPct, FadeWaechterPF, FadeWaechterN);
   bool port = (FadeWaechterModus == 1);
   if(port)                                                                    // 6.40: Portfolio-Waechter einmal rechnen; je Modul nur Information
     {
      int np = 0; bool alle = true; double pfp = FadePortfolioPF(TimeCurrent(), np, alle);
      bool ok = (FadePortPF <= 0.0) || (alle && np >= FadePortN && pfp > FadePortPF);
      t = StringFormat("%s | %.2f %% je Trade, Portfolio-Waechter %s: PF %.2f aus %d (live ab > %.2f aus %d) | PF%d je Modul (Info):",
                       (FadeAktiv ? "an" : "aus (nur Verwaltung)"), FadeRiskPct, (!alle ? "laedt" : (ok ? "LIVE" : "nur virtuell")), pfp, np, FadePortPF, FadePortN, FadeWaechterN);
     }
   for(int m=0;m<nFade;m++)
     {
      if(!F[m].histFertig) { t += StringFormat(" %s ?", FadeName(m)); continue; }
      int n = 0; double pf = FadePF(m, n);
      string z = (F[m].aus ? "x" : (port ? "" : (FadeWaechterOk(m, TimeCurrent()) ? "+" : "-")));
      t += StringFormat(" %s %s%.1f/%d", FadeName(m), z, pf, n);
      if(FadePosition(m) != 0) t += "*";
     }
   if(fadeLetzte != "") t += " | " + fadeLetzte;
   return t;
  }

//+------------------------------------------------------------------+
//| 6.20 Probability Grid (Konzept: LuxAlgo "Probability Grid",      |
//|  CC BY-NC-SA 4.0) - Schwung-Statistik je Symbol als Fade-Filter. |
//|  Zeitebene GridTF, gebildet aus den M5-Kerzen (wie im Replikat): |
//|  - Laufrichtung: Kerzenkoerper-Hoch (max Open/Close) ist das     |
//|    hoechste der letzten GridLaenge Kerzen -> aufwaerts, Koerper- |
//|    Tief das tiefste -> abwaerts (aufwaerts hat Vorrang). Wechselt|
//|    die Richtung, ist der bis dahin gelaufene Extrempunkt ein     |
//|    bestaetigter Pivot.                                           |
//|  - Schenkel Pivot -> Pivot: Groesse |Differenz|/Preis des vorigen |
//|    Pivots und Dauer in Kerzen, getrennt nach steigend/fallend;   |
//|    gezaehlt werden die letzten GridMaxSchenkel je Richtung.      |
//|  - Am Fade-Einstieg (Fade GEGEN den laufenden Schwung):          |
//|    p = Anteil der Schenkel, die kleiner sind als der Lauf bisher;|
//|    Chance(Stop) = Anteil der Schenkel ueber der Groesse bis zum  |
//|    Stop / Anteil ueber der bisherigen Groesse = Grid-Chance, dass|
//|    der Lauf bis zum Stop weiterlaeuft. Regel S: kein Fade ab     |
//|    GridMaxStopChance; Regel A: kein Fade, solange p < GridMinReife|
//|  - Fades IN Laufrichtung und Signale ohne genug Schenkel         |
//|    (GridMinSchenkel) bleiben wie in 6.10.                        |
//|  - Das Grid filtert das Signal selbst: auch der virtuelle Trade  |
//|    (Regime-Waechter) entfaellt - wie im getesteten Replikat.     |
//|  Abgleich mit dem Replikat: Replikat_v6/t_port_grid.py.          |
//+------------------------------------------------------------------+

void GridReset(const int k)
  {
   GR[k].an = false; GR[k].tfSek = PeriodSeconds(GridTF); GR[k].fertig = false; GR[k].histFehl = 0;
   GR[k].histVersuch = 0; GR[k].histAb = 0; GR[k].lastM5 = 0; GR[k].b0Seen = 0;
   GR[k].aggOn = false; GR[k].aggT = 0; GR[k].aggO = 0.0; GR[k].aggC = 0.0;
   GR[k].n = 0; GR[k].nLeg = 0; GR[k].b = 0; GR[k].cbar = -1; GR[k].pbar = -1; GR[k].lbar = -1;
   GR[k].cpx = 0.0; GR[k].ppx = 0.0; GR[k].lpx = 0.0;
   ArrayResize(GR[k].t, 0); ArrayResize(GR[k].bo, 0); ArrayResize(GR[k].bc, 0); ArrayResize(GR[k].bias, 0);
   ArrayResize(GR[k].pivBar, 0); ArrayResize(GR[k].curBar, 0); ArrayResize(GR[k].pivPx, 0); ArrayResize(GR[k].curPx, 0);
   ArrayResize(GR[k].legConf, 0); ArrayResize(GR[k].legDir, 0); ArrayResize(GR[k].legBars, 0); ArrayResize(GR[k].legSz, 0);
  }

// eine abgeschlossene Zeitebenen-Kerze (Beginn t, Open o, Close c): fetchPivot + fetchData (LuxAlgo)
void GridKerze(const int k, const datetime t, const double o, const double c)
  {
   if(GR[k].n > 0 && t <= GR[k].t[GR[k].n - 1]) return;                         // nie doppelt oder rueckwaerts (nachgeladene Kurse)
   int i = GR[k].n;
   if(i >= ArraySize(GR[k].t))
     {
      int nn = i + 8192;
      ArrayResize(GR[k].t, nn); ArrayResize(GR[k].bo, nn); ArrayResize(GR[k].bc, nn); ArrayResize(GR[k].bias, nn);
      ArrayResize(GR[k].pivBar, nn); ArrayResize(GR[k].curBar, nn); ArrayResize(GR[k].pivPx, nn); ArrayResize(GR[k].curPx, nn);
     }
   GR[k].t[i] = t; GR[k].bo[i] = o; GR[k].bc[i] = c; GR[k].n = i + 1;
   if(i == 0) { GR[k].cpx = c; GR[k].cbar = 0; GR[k].lpx = c; GR[k].lbar = 0; }
   if(i >= GridLaenge - 1)
     {
      double up = -DBL_MAX, lo = DBL_MAX;
      for(int j=i-GridLaenge+1;j<=i;j++)
        {
         double a = MathMax(GR[k].bo[j], GR[k].bc[j]), z = MathMin(GR[k].bo[j], GR[k].bc[j]);
         if(a > up) up = a;
         if(z < lo) lo = z;
        }
      double mx = MathMax(o, c), mn = MathMin(o, c);
      int b = GR[k].b, nb = b;
      if(mx == up) nb = 1;
      else if(mn == lo) nb = -1;
      bool neu = false;
      if(nb != b && nb != 0)
        {
         if(b != 0) { neu = true; GR[k].ppx = GR[k].cpx; GR[k].pbar = GR[k].cbar; }
         GR[k].cpx = (nb == 1 ? up : lo); GR[k].cbar = i; GR[k].b = nb;
        }
      else if(b != 0)
        {
         double alt = GR[k].cpx;
         GR[k].cpx = (b == 1 ? MathMax(up, GR[k].cpx) : MathMin(lo, GR[k].cpx));
         if(GR[k].cpx != alt) GR[k].cbar = i;
        }
      if(neu && GR[k].lpx > 0.0)
        {
         int bd = GR[k].pbar - GR[k].lbar;
         if(bd != 0)
           {
            int q = GR[k].nLeg;
            if(q >= ArraySize(GR[k].legSz))
              { int nn = q + 2048; ArrayResize(GR[k].legConf, nn); ArrayResize(GR[k].legDir, nn); ArrayResize(GR[k].legBars, nn); ArrayResize(GR[k].legSz, nn); }
            GR[k].legConf[q] = i; GR[k].legDir[q] = (GR[k].ppx > GR[k].lpx ? 1 : -1);
            GR[k].legSz[q] = MathAbs(GR[k].ppx - GR[k].lpx)/GR[k].lpx; GR[k].legBars[q] = bd; GR[k].nLeg = q + 1;
            GR[k].lpx = GR[k].ppx; GR[k].lbar = GR[k].pbar;
           }
        }
     }
   GR[k].bias[i] = GR[k].b; GR[k].pivPx[i] = GR[k].ppx; GR[k].pivBar[i] = GR[k].pbar; GR[k].curPx[i] = GR[k].cpx; GR[k].curBar[i] = GR[k].cbar;
  }

// abgeschlossene M5-Kerze b (die naechste Kerze beginnt bei tn) in die Zeitebene einrechnen. Beginnt tn eine neue
// Zeitebenen-Kerze, ist die bisherige abgeschlossen (Replikat: pgrid.tf_bars).
void GridM5(const int k, const MqlRates &b, const datetime tn)
  {
   long ts = GR[k].tfSek;
   datetime kb = (datetime)((long)b.time - (long)b.time % ts);
   if(!GR[k].aggOn || kb != GR[k].aggT) { GR[k].aggOn = true; GR[k].aggT = kb; GR[k].aggO = b.open; }
   GR[k].aggC = b.close;
   datetime kn = (datetime)((long)tn - (long)tn % ts);
   if(kn != kb) { GridKerze(k, GR[k].aggT, GR[k].aggO, GR[k].aggC); GR[k].aggOn = false; }
   GR[k].lastM5 = b.time;
  }

// Index der letzten abgeschlossenen Zeitebenen-Kerze VOR der Zeitebenen-Kerze, in der tEntry liegt (-1 = keine)
int GridIndex(const int k, const datetime tEntry)
  {
   long ts = GR[k].tfSek;
   datetime kb = (datetime)((long)tEntry - (long)tEntry % ts);
   int lo = 0, hi = GR[k].n - 1, r = -1;
   while(lo <= hi)
     {
      int mid = (lo + hi)/2;
      if(GR[k].t[mid] < kb) { r = mid; lo = mid + 1; } else hi = mid - 1;
     }
   return r;
  }

// Anteil der Schenkel mit Groesse <= x unter den letzten GridMaxSchenkel Schenkeln der Richtung d, die bis zur
// Kerze i bestaetigt waren (n = Anzahl dieser Schenkel)
double GridRang(const int k, const int i, const int d, const double x, int &n)
  {
   n = 0;
   int lo = 0, hi = GR[k].nLeg - 1, q0 = -1;                                 // letzter Schenkel mit Bestaetigung <= i
   while(lo <= hi) { int mid = (lo + hi)/2; if(GR[k].legConf[mid] <= i) { q0 = mid; lo = mid + 1; } else hi = mid - 1; }
   int cnt = 0;
   for(int q=q0;q>=0 && n<GridMaxSchenkel;q--)
     {
      if(GR[k].legDir[q] != d) continue;
      n++;
      if(GR[k].legSz[q] <= x) cnt++;
     }
   return (n > 0 ? (double)cnt/n : 0.0);
  }

// Grid-Regel fuer ein Fade-Signal in Richtung d mit Stop st und Einstieg zu Beginn der Kerze tEntry.
// true = handeln (auch: Grid aus, keine Daten, Fade in Laufrichtung); grund = Text bei false
bool GridFadeOk(const int k, const datetime tEntry, const int d, const double st, string &grund)
  {
   grund = "";
   if(!GridAktiv || !gridOk || k < 0 || k >= MAXSYM || !GR[k].an || !GR[k].fertig) return true;
   int i = GridIndex(k, tEntry);
   if(i < 0 || GR[k].bias[i] == 0 || GR[k].pivBar[i] < 0 || GR[k].pivPx[i] <= 0.0) return true;
   int b = GR[k].bias[i];
   if(d == b) return true;                                                    // Fade in Laufrichtung: wie 6.10
   int n = 0, n2 = 0;
   double ext = MathAbs(GR[k].curPx[i] - GR[k].pivPx[i])/GR[k].pivPx[i];
   double pe = GridRang(k, i, b, ext, n);
   if(n < GridMinSchenkel) return true;                                       // zu wenige Schenkel: wie 6.10
   if(GridMinReife > 0.0 && pe < GridMinReife)
     {
      grund = StringFormat("Lauf %s erst beim %.0f. Perzentil der letzten %d Schenkel (Regel A: mind. %.0f.)", (b > 0 ? "aufwaerts" : "abwaerts"), pe*100.0, n, GridMinReife*100.0);
      return false;
     }
   if(GridMaxStopChance > 0.0)
     {
      double xs = MathAbs(st - GR[k].pivPx[i])/GR[k].pivPx[i];
      double sJetzt = 1.0 - pe, sStop = 1.0 - GridRang(k, i, b, xs, n2);
      double ch = (sJetzt > 0.0 ? sStop/sJetzt : 0.0);
      if(ch >= GridMaxStopChance)
        {
         grund = StringFormat("Lauf %s (%.0f. Perzentil), Chance %.0f %%, dass er bis zum Stop weiterlaeuft (Regel S: ab %.0f %% kein Fade)", (b > 0 ? "aufwaerts" : "abwaerts"), pe*100.0, ch*100.0, GridMaxStopChance*100.0);
         return false;
        }
     }
   return true;
  }

// Grid bereit (oder nicht in Gebrauch)
bool GridBereit(const int k)
  {
   if(!GridAktiv || !gridOk || k < 0 || k >= MAXSYM || !GR[k].an) return true;
   return GR[k].fertig;
  }

// Grid kennt die M5-Kerze t (oder ist nicht in Gebrauch/noch nicht geladen)
bool GridAktuell(const int k, const datetime t)
  {
   if(!GridAktiv || !gridOk || k < 0 || k >= MAXSYM || !GR[k].an || !GR[k].fertig) return true;
   return (GR[k].lastM5 >= t);
  }

// Historie: M5-Kurse der letzten FadeHistTage + GridVorlaufTage Tage; false = Kurse noch nicht (vollstaendig) da
bool GridHistorie(const int k)
  {
   string s = S[k].sym;
   datetime bis = iTime(s, PERIOD_M5, 0);
   if(bis <= 0) return false;
   datetime von = bis - (datetime)((long)(FadeHistTage + GridVorlaufTage)*86400);
   MqlRates r[];
   ArraySetAsSeries(r, false);
   int n = CopyRates(s, PERIOD_M5, von, bis, r);
   bool genug = false;
   if(n >= 3 && r[n-1].time == bis)                                            // wie FadeHistorie: Kurse bis zum Beginn des Fensters (oder Grenze erreicht)
     {
      int maxBars = TerminalInfoInteger(TERMINAL_MAXBARS);
      datetime srvAb = (datetime)SeriesInfoInteger(s, PERIOD_M5, SERIES_SERVER_FIRSTDATE);
      genug = (r[0].time <= von + 20*86400 || (maxBars > 0 && n >= maxBars - 1000) || (srvAb > 0 && r[0].time <= srvAb + 3*86400));
     }
   if(!genug && GR[k].histFehl < 20) { GR[k].histFehl++; return false; }       // Kurse werden noch geladen: spaeter erneut (bis 20 Versuche)
   if(n >= 3 && r[0].time > von + 20*86400)
      PrintFormat("DEADBAND4 GRID %s: WARNUNG - M5-Historie erst ab %s statt %s (Max. Balken im Chart %d). Die Schenkel-Statistik ist anfangs duenner als im Replikat; Max. Balken im Chart = Unbegrenzt setzen.",
                  s, TimeToString(r[0].time, TIME_DATE), TimeToString(von, TIME_DATE), TerminalInfoInteger(TERMINAL_MAXBARS));
   bool an = GR[k].an;
   GridReset(k);
   GR[k].an = an;
   if(n >= 3)
     {
      for(int i=0;i<n-1;i++) GridM5(k, r[i], r[i+1].time);
      GR[k].histAb = r[0].time; GR[k].b0Seen = r[n-1].time;
     }
   GR[k].fertig = true;
   int nAuf = 0, nAb = 0;
   for(int q=0;q<GR[k].nLeg;q++) { if(GR[k].legDir[q] > 0) nAuf++; else nAb++; }
   PrintFormat("DEADBAND4 GRID %s: Historie ab %s (%d M5, %d Kerzen M%d), %d steigende / %d fallende Schenkel (gezaehlt je Richtung hoechstens %d)%s",
               s, (n >= 3 ? TimeToString(r[0].time, TIME_DATE) : "-"), (n > 0 ? n : 0), GR[k].n, GR[k].tfSek/60, nAuf, nAb, GridMaxSchenkel,
               (MathMin(nAuf, nAb) < GridMinSchenkel ? " - noch zu wenige Schenkel, Grid filtert erst ab " + IntegerToString(GridMinSchenkel) : ""));
   return true;
  }

// laufend: neue abgeschlossene M5-Kerzen je Symbol einrechnen (vor den Fade-Kerzen desselben Durchlaufs)
void GridDurchlauf()
  {
   if(!GridAktiv || !gridOk) return;
   datetime now = TimeCurrent();
   for(int k=0;k<nSym;k++)
     {
      if(!GR[k].an) continue;
      if(!GR[k].fertig)
        {
         if(now - GR[k].histVersuch >= 15) { GR[k].histVersuch = now; GridHistorie(k); }
         continue;
        }
      string s = S[k].sym;
      datetime b0 = iTime(s, PERIOD_M5, 0);
      if(b0 <= 0 || b0 == GR[k].b0Seen) continue;
      if(!SeriesInfoInteger(s, PERIOD_M5, SERIES_SYNCHRONIZED)) continue;      // nach Verbindungsluecken erst mit vollstaendigen Kursen weiter (Fade-Kerzen warten mit, Ausstiege nicht)
      if(GR[k].lastM5 <= 0) { GR[k].lastM5 = iTime(s, PERIOD_M5, 1); GR[k].b0Seen = b0; continue; }   // ohne Historie: ab jetzt fortschreiben
      MqlRates r[];
      ArraySetAsSeries(r, false);
      int n = CopyRates(s, PERIOD_M5, GR[k].lastM5, b0, r);
      if(n < 2 || r[n-1].time != b0) continue;
      for(int i=0;i<n-1;i++)
         if(r[i].time > GR[k].lastM5) GridM5(k, r[i], r[i+1].time);
      GR[k].b0Seen = b0;
     }
  }

// Anlegen (aus FadeAnlegen): Eingaben pruefen, Symbole der Fade-Module fuehren
bool GridAnlegen()
  {
   gridOk = false;
   for(int k=0;k<MAXSYM;k++) GridReset(k);
   if(!GridAktiv) return true;
   int tfs = PeriodSeconds(GridTF);
   if(GridTF == PERIOD_CURRENT || tfs < 300 || tfs > 3600 || tfs % 300 != 0 || 3600 % tfs != 0)
     { Print("DEADBAND4: GridTF muss M5, M10, M15, M20, M30 oder H1 sein (wird aus M5 gebildet) - Probability Grid AUS"); return false; }
   if(GridLaenge < 2 || GridLaenge > 500 || GridMaxSchenkel < 10 || GridMaxSchenkel > 5000 || GridMinSchenkel < 1 || GridMinSchenkel > GridMaxSchenkel
      || GridMaxStopChance < 0.0 || GridMaxStopChance >= 1.0 || GridMinReife < 0.0 || GridMinReife >= 1.0 || GridVorlaufTage < 0 || GridVorlaufTage > 2000)
     { Print("DEADBAND4: Grid-Eingaben ungueltig (GridLaenge 2-500, GridMaxSchenkel 10-5000, 1 <= GridMinSchenkel <= GridMaxSchenkel, 0 <= GridMaxStopChance/GridMinReife < 1, GridVorlaufTage 0-2000) - Probability Grid AUS"); return false; }
   for(int m=0;m<nFade;m++) if(!F[m].gridAus) GR[F[m].k].an = true;
   gridOk = true;
   return true;
  }

// Anzeige: je Symbol Laufrichtung und Rang des Laufs, Zahl der vom Grid ausgelassenen Signale
string GridStatusText()
  {
   if(!GridAktiv) return "aus (Fades wie 6.10)";
   if(!gridOk) return "AUS (Eingaben ungueltig)";
   string regel = "";
   if(GridMaxStopChance > 0.0) regel += StringFormat(" S: Stop-Chance < %.0f %%", GridMaxStopChance*100.0);
   if(GridMinReife > 0.0) regel += StringFormat(" A: Reife >= %.0f.", GridMinReife*100.0);
   if(regel == "") regel = " keine Regel aktiv";
   if(GridNurLive) regel += " (nur live, Waechter zaehlt alle)";
   string t = StringFormat("M%d L%d, %d Schenkel |%s |", PeriodSeconds(GridTF)/60, GridLaenge, GridMaxSchenkel, regel);
   for(int k=0;k<nSym;k++)
     {
      if(!GR[k].an) continue;
      if(!GR[k].fertig) { t += " " + S[k].sym + " ?"; continue; }
      int i = GR[k].n - 1;
      if(i < 0 || GR[k].bias[i] == 0 || GR[k].pivPx[i] <= 0.0) { t += " " + S[k].sym + " -"; continue; }
      int n = 0;
      double pe = GridRang(k, i, GR[k].bias[i], MathAbs(GR[k].curPx[i] - GR[k].pivPx[i])/GR[k].pivPx[i], n);
      t += StringFormat(" %s %s %.0f.P (%d)", S[k].sym, (GR[k].bias[i] > 0 ? "auf" : "ab"), pe*100.0, n);
     }
   int ns = 0;
   for(int m=0;m<nFade;m++) ns += F[m].nGrid;
   t += StringFormat(" | %s %d (Historie + live)", (GridNurLive ? "nur virtuell" : "ausgelassen"), ns);
   if(StringLen(GridOhne) > 0) t += " | ohne Grid: " + GridOhne;
   return t;
  }

//+------------------------------------------------------------------+
//| 6.30 Trefferquote (Replikat eng7, x42/x43)                        |
//|  Fades: ab FadeT1R (R = Stop-Abstand beim Einstieg) wird          |
//|  FadeT1Anteil geschlossen, Stop und Ziel bleiben.                 |
//|  RSI21 und jeder Noise-Teil: Stop auf Einstand + EinstandPlusR,   |
//|  sobald der Kurs R21/NzEinstandAbR im Plus ist.                   |
//|  Erst ab der M5-Kerze nach der Einstiegskerze (wie das Replikat)  |
//|  und nach MinHalteSek; Teilgewinn nach der Gewinn-/News-Regel.    |
//|  Der Zustand steckt im Stop (Einstand) bzw. in der Deal-Historie  |
//|  (Teilschliessung) - er gilt auch nach einem Neustart.            |
//+------------------------------------------------------------------+
// true, wenn die M5-Kerze nach der Einstiegskerze begonnen hat
bool NachEinstiegsKerze(const string s, const datetime tOpen)
  {
   int ps = PeriodSeconds(PERIOD_M5);
   datetime b0 = iTime(s, PERIOD_M5, 0);
   datetime naechste = (datetime)((long)tOpen - (long)tOpen % ps + ps);
   return (b0 > 0 && b0 >= naechste);
  }

// urspruenglicher Stop-Abstand einer Position aus der Eroeffnungs-Order (der Stop kann auf Einstand stehen)
double UrStopAbstand(const ulong tk)
  {
   if(!PositionSelectByTicket(tk)) return 0.0;
   double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL);
   long pid = PositionGetInteger(POSITION_IDENTIFIER);
   double rd = (sl > 0.0 ? MathAbs(op - sl) : 0.0);
   if(HistorySelectByPosition(pid))
     {
      for(int i=0;i<HistoryDealsTotal();i++)
        {
         ulong dt = HistoryDealGetTicket(i);
         if(dt == 0 || HistoryDealGetInteger(dt, DEAL_ENTRY) != DEAL_ENTRY_IN) continue;
         ulong ot = (ulong)HistoryDealGetInteger(dt, DEAL_ORDER);
         double osl = (ot > 0 && HistoryOrderSelect(ot)) ? HistoryOrderGetDouble(ot, ORDER_SL) : 0.0;
         double px = HistoryDealGetDouble(dt, DEAL_PRICE);
         if(osl > 0.0 && px > 0.0) rd = MathAbs(px - osl);
         break;
        }
     }
   PositionSelectByTicket(tk);
   return rd;
  }

// Stop auf ref + EinstandPlusR*rd, sobald der Kurs abR*rd im Plus ist.
// 1 = gesetzt oder schon dort (bzw. ohne R nicht moeglich), 0 = noch nicht, -1 = abgelehnt (spaeter erneut)
int EinstandSetzen(const ulong tk, const double ref, const double rd, const double abR, const string wer)
  {
   if(!PositionSelectByTicket(tk)) return -1;
   if(rd <= 0.0 || ref <= 0.0) return 1;
   string s = PositionGetString(POSITION_SYMBOL);
   int d = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1);
   double sl = PositionGetDouble(POSITION_SL), tp = PositionGetDouble(POSITION_TP);
   int dg = (int)SymbolInfoInteger(s, SYMBOL_DIGITS);
   double pt = SymbolInfoDouble(s, SYMBOL_POINT);
   double nsl = NormalizeDouble(ref + d*EinstandPlusR*rd, dg);
   if(sl > 0.0 && (sl - nsl)*d >= -0.5*pt) return 1;                         // Stop steht schon auf Einstand oder besser
   datetime tOpen = (datetime)PositionGetInteger(POSITION_TIME);
   if(!NachEinstiegsKerze(s, tOpen)) return 0;
   if(MinHalteSek > 0 && TimeCurrent() - tOpen < MinHalteSek) return 0;      // kein Gewinnschluss am Einstand-Stop vor der Haltezeit
   double bid = SymbolInfoDouble(s, SYMBOL_BID), ask = SymbolInfoDouble(s, SYMBOL_ASK);
   if(bid <= 0.0 || ask <= 0.0) return 0;
   double lvl = ref + d*abR*rd;
   if(!((d > 0) ? (bid >= lvl) : (ask <= lvl))) return 0;
   long stl = SymbolInfoInteger(s, SYMBOL_TRADE_STOPS_LEVEL);
   double minD = (stl > 0 ? stl*pt : 0.0);
   if((d > 0 && bid - nsl < minD) || (d < 0 && nsl - ask < minD)) return 0;
   trade.SetExpertMagicNumber((ulong)PositionGetInteger(POSITION_MAGIC));
   if(trade.PositionModify(tk, nsl, tp))
     {
      PrintFormat("DEADBAND4 %s %s: Stop auf Einstand %.*f (Einstieg + %.2f R) - Kurs war %.2f R im Plus", s, wer, dg, nsl, EinstandPlusR, abR);
      return 1;
     }
   PrintFormat("DEADBAND4 %s %s: Stop auf Einstand abgelehnt (%d %s) - neuer Versuch", s, wer, trade.ResultRetcode(), trade.ResultRetcodeDescription());
   return -1;
  }

// Noise: je Teil Stop auf Einstand ab NzEinstandAbR (R = Abstand zum Stop der Eroeffnung; steht der Stop im Plus, ist es erledigt)
void NzEinstand()
  {
   static datetime letzter = 0;
   datetime now = TimeCurrent();
   for(int i=PositionsTotal()-1;i>=0;i--)
     {
      ulong tk = PositionGetTicket(i); if(tk == 0) continue;
      if(!IsNzMagic(PositionGetInteger(POSITION_MAGIC))) continue;
      double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL);
      int d = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1);
      if(sl <= 0.0 || (sl - op)*d >= 0.0) continue;                           // ohne Stop oder schon auf Einstand
      double rd = (op - sl)*d;
      double lvl = op + d*NzEinstandAbR*rd;
      string sy = PositionGetString(POSITION_SYMBOL);
      double px = (d > 0) ? SymbolInfoDouble(sy, SYMBOL_BID) : SymbolInfoDouble(sy, SYMBOL_ASK);
      if(px <= 0.0 || (px - lvl)*d < 0.0) continue;
      if(now - letzter < 3) return;                                             // Aenderungen gedrosselt (alle 3 s)
      letzter = now;
      EinstandSetzen(tk, op, rd, NzEinstandAbR, StringFormat("NOISE Teil #%I64u", tk));
     }
  }

// Fade-Teilschliessung schon erfolgt? (Ausstiegs-Deal dieser Position in der Historie - auch nach einem Neustart)
bool FadeTeilSchonZu(const ulong tk)
  {
   if(!PositionSelectByTicket(tk)) return false;
   long pid = PositionGetInteger(POSITION_IDENTIFIER);
   bool ja = false;
   if(HistorySelectByPosition(pid))
      for(int i=HistoryDealsTotal()-1;i>=0;i--)
        {
         ulong dt = HistoryDealGetTicket(i);
         if(dt > 0 && HistoryDealGetInteger(dt, DEAL_ENTRY) == DEAL_ENTRY_OUT) { ja = true; break; }
        }
   PositionSelectByTicket(tk);
   return ja;
  }

// Fade: FadeT1Anteil der Position schliessen, sobald der Kurs FadeT1R im Plus ist. true = Teilschliessung gesendet
bool FadeTeilgewinn(const int m, const ulong tk)
  {
   if(FadeT1R <= 0.0 || FadeT1Anteil <= 0.0) return false;
   if(!PositionSelectByTicket(tk)) return false;
   string s = S[F[m].k].sym;
   datetime now = TimeCurrent();
   if(F[m].t1Chk != tk)                                                        // einmal je Position: schon teilweise geschlossen?
     {
      F[m].t1Chk = tk;
      if(FadeTeilSchonZu(tk)) { F[m].t1Tk = tk; return false; }
      if(!PositionSelectByTicket(tk)) return false;
     }
   double op = PositionGetDouble(POSITION_PRICE_OPEN), sl = PositionGetDouble(POSITION_SL);
   double vol = PositionGetDouble(POSITION_VOLUME);
   int d = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? 1 : -1);
   datetime tOpen = (datetime)PositionGetInteger(POSITION_TIME);
   double rd = (op - sl)*d;
   if(sl <= 0.0 || rd <= 0.0) { F[m].t1Tk = tk; return false; }              // ohne Stop im Minus kein R: kein Teilgewinn
   if(!NachEinstiegsKerze(s, tOpen)) return false;
   double bid = SymbolInfoDouble(s, SYMBOL_BID), ask = SymbolInfoDouble(s, SYMBOL_ASK);
   if(bid <= 0.0 || ask <= 0.0) return false;
   double lvl = op + d*FadeT1R*rd;
   if(!((d > 0) ? (bid >= lvl) : (ask <= lvl))) return false;
   double stp = SymbolInfoDouble(s, SYMBOL_VOLUME_STEP); if(stp <= 0.0) stp = 0.01;
   double mnv = SymbolInfoDouble(s, SYMBOL_VOLUME_MIN);
   double v1 = NormalizeDouble(MathFloor(vol*FadeT1Anteil/stp + 1e-9)*stp, 2);
   if(v1 < mnv - 1e-9 || vol - v1 < mnv - 1e-9) { F[m].t1Tk = tk; return false; }   // zu klein fuer eine Teilschliessung (Replikat ebenso)
   double p = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
   if(!GewinnSchlussOk(tk, p)) return false;                                   // 130-s-/News-Regel
   if(now - F[m].t1Versuch < 10) return false;
   F[m].t1Versuch = now;
   if(SchliesseTeil(tk, v1))
     {
      F[m].t1Tk = tk; F[m].nT1++;
      fadeLetzte = StringFormat("%s Teilgewinn %.2f von %.2f Lot bei %.2f R", FadeName(m), v1, vol, FadeT1R);
      PrintFormat("DEADBAND4 %s FADE %s (Stop und Ziel bleiben)", s, fadeLetzte);
      return true;
     }
   if(now - F[m].logZeit >= 60) { F[m].logZeit = now; PrintFormat("DEADBAND4 %s FADE %s: Teilgewinn abgelehnt (%d %s) - neuer Versuch alle 10 s", s, FadeName(m), trade.ResultRetcode(), trade.ResultRetcodeDescription()); }
   return false;
  }

// 6.50: Start-Pruefung - Namen in GueltigSchutzFrei, die kein Fade-Modul sind (Tippfehler), und ein Regime-Schalter ohne
//       Grundlage (Waechter aus bzw. Fade-Module nicht angelegt) melden
void GueltigSchutzFreiPruefen()
  {
   if(GueltigSchutz && R21Aktiv && GueltigSchutzR21Regime && GueltigSchutzR21BisNY < 24.0)   // Regime-Schalter ohne Grundlage
     {
      if(FadePortPF <= 0.0)
         Print("DEADBAND4: WARNUNG GueltigSchutzR21Regime ohne Wirkung - FadePortPF <= 0 (Portfolio-Waechter aus): RSI21 gilt immer als im Fade-Regime");
      else if(!fadeOk || nFade == 0)
         Print("DEADBAND4: WARNUNG Fade-Module nicht angelegt - das Fade-Regime ist unbekannt: RSI21 bleibt an gueltigen Tagen ganztags geschuetzt (wie 6.40)");
     }
   if(!fadeOk || nFade == 0) return;                                            // ohne Fade-Module keine Namen zu pruefen
   string t[]; int n = StringSplit(GueltigSchutzFrei, StringGetCharacter(";",0), t);
   for(int i=0;i<n;i++)
     {
      string b = t[i]; StringTrimLeft(b); StringTrimRight(b);
      if(StringLen(b) == 0) continue;
      bool da = false;
      for(int m=0;m<nFade;m++) if(FadeNameInListe(F[m].name, b)) da = true;
      if(!da) PrintFormat("DEADBAND4: WARNUNG GueltigSchutzFrei - '%s' ist kein Fade-Modul dieser Liste (ohne Wirkung)", b);
     }
  }

// 6.50: Kurzbeschreibung, welche Module der Schutz sperrt (Journal, Panel)
string GueltigSchutzUmfang()
  {
   string teile = "";
   if(NzAktiv && nzOk) teile += "Noise";
   if(FadeAktiv && fadeOk && nFade > 0)
     {
      string frei = "";
      for(int m=0;m<nFade;m++) if(F[m].schutzFrei) frei += (StringLen(frei) > 0 ? "," : "") + F[m].name;
      teile += (StringLen(teile) > 0 ? ", " : "") + "Fades" + (StringLen(frei) > 0 ? " ausser " + frei : "");
     }
   if(R21Aktiv && nSlot > nSym)
     {
      string r21 = "";
      if(GueltigSchutzR21BisNY >= 24.0) r21 = "RSI21";
      else
        {
         string teil = (GueltigSchutzR21BisNY > 0.0 ? "vor " + NYStundeText(GueltigSchutzR21BisNY) + " NY" : "");
         if(GueltigSchutzR21Regime && FadePortPF > 0.0) teil += (StringLen(teil) > 0 ? " oder " : "") + "ohne Fade-Regime";
         if(StringLen(teil) > 0) r21 = "RSI21 " + teil;
        }
      if(StringLen(r21) > 0) teile += (StringLen(teile) > 0 ? ", " : "") + r21;
     }
   if(DbAktiv) teile += (StringLen(teile) > 0 ? ", " : "") + "DEADBAND";
   return (StringLen(teile) > 0 ? teile : "keine aktiven Module");
  }

// 6.40: Auszahlungstakt (Panel)
string TaktStatusText()
  {
   return StringFormat("Mindestgewinn %.2f $ | Abschluss-Ernte %s | Schutz gueltiger Tage %s | Fade-Waechter %s | Pufferkurve voll ab %.1f %%, x%.2f bei <= %.1f %%",
                       kMinProfit, (AbschlussLetzte >= NeedValidDays ? "immer" : (AbschlussLetzte > 0 ? StringFormat("ab %d fehlenden", AbschlussLetzte) : "aus")),
                       (!GueltigSchutz ? "aus" : (gGueltigSchutz ? "AKTIV (heute gueltig): " : "bereit: ") + GueltigSchutzUmfang()),
                       (FadeWaechterModus == 1 ? "Portfolio" : "je Modul"), DDFullPct, DDMinFactor, DDMinPct);
  }

string TrefferStatusText()
  {
   int n = 0;
   for(int m=0;m<nFade;m++) n += F[m].nT1;
   return StringFormat("Fade-Teilgewinn %s | Einstand RSI21 %s, Noise %s (+%.2f R) | Teilgewinne seit Start %d",
                       (FadeT1R > 0.0 ? StringFormat("%.0f %% ab %.2f R", FadeT1Anteil*100.0, FadeT1R) : "aus"),
                       (R21EinstandAbR > 0.0 ? StringFormat("ab %.2f R", R21EinstandAbR) : "aus"),
                       (NzEinstandAbR > 0.0 ? StringFormat("ab %.2f R", NzEinstandAbR) : "aus"), EinstandPlusR, n);
  }
