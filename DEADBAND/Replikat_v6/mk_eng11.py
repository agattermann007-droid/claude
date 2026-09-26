"""Erzeugt eng11.py aus eng10.py (Build 6.70): Ziel fuer den gueltigen Tag mit Gewinnsicherung (ext_*), Tagessperre der
Fades je Symbol nach Fade-Verlusten (fsym_block). Mit den Voreinstellungen rechnet eng11 wie eng10 (t_eng11.py).
Aufruf: python mk_eng11.py"""
import re

src = open("eng10.py").read()


def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:80])
    src = src.replace(old, new)


HEAD = '''"""DEADBAND Replikat v11 (Build 6.70) - eng10 plus:
Ziel fuer den gueltigen Tag mit Gewinnsicherung (ext_on): Erreicht ein Fade sein Ziel, wuerde das Schliessen den Tag aber
nicht gueltig machen (realisiert heute + Ergebnis < Schwelle), obwohl dem Zyklus noch gueltige Tage fehlen, wird die Position
nicht geschlossen: Stop auf Einstieg + ext_lock x Zielweite (Gewinn gesichert), neues Ziel dort, wo das Schliessen den Tag
gueltig macht (Schwelle x (1 + ext_margin)), hoechstens ext_max R vom Einstieg. Einmal je Position. Liegt das Tief (Long)
der Kerze des Ziel-Treffers schon unter dem neuen Stop, zaehlt der Stop in derselben Kerze (pessimistisch); das neue Ziel
gilt erst ab der naechsten Kerze.
Tagessperre der Fades je Symbol (fsym_block): nach N Fade-Verlusten im Symbol am selben Tag keine neuen Fade-Einstiege
in diesem Symbol bis 17:00 NY (Trendtag).
Noise-Tagespause (nz_maxloss): nach N Noise-Teilen mit Verlust am selben Tag keine neuen Noise-Einstiege bis 17:00 NY.
Regime-Groesse (reg_mult, Runde 2): RSI21 und Noise mit Faktor reg_mult, solange der Portfolio-Waechter die Fades nicht live
handeln laesst (Signalzeit; RSI21: r21["reg"], Noise: nz["reg"] = 0).
Trade-Protokoll Spalte 10 = Ausstiegszeit (NY-Minuten). Mit den Voreinstellungen rechnet eng11 wie eng10 (t_eng11.py).

'''
assert src.startswith('"""DEADBAND Replikat v10')
src = HEAD + src[3:]

rep('''    "cons_pct", "cons_res", "cons_cap", "cons_capfrac",
]''', '''    "cons_pct", "cons_res", "cons_cap", "cons_capfrac",
    # --- 6.70: Ziel fuer den gueltigen Tag, Tagessperre je Symbol (Voreinstellung = aus)
    "ext_on", "ext_lock", "ext_max", "ext_margin", "fsym_block", "nz_maxloss", "reg_mult",
]''')
rep('''             cons_pct=0.0, cons_res=0.5, cons_cap=0, cons_capfrac=1.0)''',
    '''             cons_pct=0.0, cons_res=0.5, cons_cap=0, cons_capfrac=1.0,
             ext_on=0, ext_lock=0.5, ext_max=1.2, ext_margin=0.05, fsym_block=0, nz_maxloss=0, reg_mult=1.0)''')
rep('''      "cons_wait", "cons_block", "open_end", "lim_cons"]''',
    '''      "cons_wait", "cons_block", "open_end", "lim_cons", "ext_n", "ext_hit", "fsym_blk", "nz_blk"]''')
rep('''    cons_pct = Pv[152]; cons_res = Pv[153]; cons_cap = int(Pv[154]); cons_capfrac = Pv[155]''',
    '''    cons_pct = Pv[152]; cons_res = Pv[153]; cons_cap = int(Pv[154]); cons_capfrac = Pv[155]
    ext_on = Pv[156] > 0.5; ext_lock = Pv[157]; ext_max = Pv[158]; ext_margin = Pv[159]; fsym_block = int(Pv[160])
    nz_maxloss = int(Pv[161]); reg_mult = Pv[162]''')
rep('''    p_fk = np.zeros(NSLOT)                           # 6.60: Groessenfaktor (Pufferkurve) beim Einstieg (Protokoll)''',
    '''    p_fk = np.zeros(NSLOT)                           # 6.60: Groessenfaktor (Pufferkurve) beim Einstieg (Protokoll)
    p_ext = np.zeros(NSLOT, np.bool_)                # 6.70: Ziel fuer den gueltigen Tag schon verlaengert''')
# Tagessperre je Symbol (nur Fade-Stroeme = generische Stroeme)
rep('''            if GP[s_, 6] > 0.5 and losses[k] >= int(GP[s_, 6]):
                continue
''', '''            if GP[s_, 6] > 0.5 and losses[k] >= int(GP[s_, 6]):
                continue
            if fsym_block > 0:
                nls = 0
                for q in range(NG):
                    nls += losses[G0 + 2 * q + sy]
                if nls >= fsym_block:
                    st[74] += 1
                    continue
''')
rep('''            p_xev[k] = g_xev[a]
''', '''            p_xev[k] = g_xev[a]
            p_ext[k] = False
''')
# Ziel-Treffer der generischen Stroeme: verlaengern statt schliessen
rep('''            elif hit_tp and (k < G0 or ii - p_i5[k] >= int(GP[(k - G0) // 2, 15])):
                px = p_tp[k]
                closed = True
''', '''            elif hit_tp and (k < G0 or ii - p_i5[k] >= int(GP[(k - G0) // 2, 15])):
                px = p_tp[k]
                closed = True
                if ext_on and k >= G0 and not p_ext[k] and mode == 0 and valid_days < needvalid \\
                        and not (day_had and day_real >= needday) and p_rd[k] > 0.0:
                    pnl_t = (p_tp[k] - p_entry[k]) * d * p_lots[k] * mpp[sy] + p_swap[k] - p_comm[k]
                    if day_real + pnl_t < needday:
                        need_g = needday * (1.0 + ext_margin) - day_real + p_comm[k] - p_swap[k]
                        dist_n = need_g / (p_lots[k] * mpp[sy])
                        tpr_n = (p_tp[k] - p_entry[k]) * d / p_rd[k]
                        if dist_n > 0.0 and dist_n <= ext_max * p_rd[k] and tpr_n > 0.0:
                            p_ext[k] = True
                            st[72] += 1
                            lock = p_entry[k] + d * ext_lock * tpr_n * p_rd[k]
                            if (lock - p_sl[k]) * d > 0.0:
                                p_sl[k] = lock
                            p_tp[k] = p_entry[k] + d * dist_n
                            closed = False
                            lost = (lo <= p_sl[k]) if d > 0 else (hi + sp >= p_sl[k])
                            if lost:                                  # pessimistisch: Stop in derselben Kerze
                                px = p_sl[k]
                                closed = True
                elif hit_tp and k >= G0 and p_ext[k]:
                    st[73] += 1
''')
rep('''        if zcur >= 0 and nz_on and entries_ok and not (vp_blk and (vp_mods & 4)) and z_entry[zcur] == 1 and nzd != 0 and not skipmask_z[zcur]:
            hed = False
''', '''        if zcur >= 0 and nz_on and nz_maxloss > 0 and nzd != 0 and z_entry[zcur] == 1:
            nzl = 0
            for q in range(nz_parts):
                nzl += losses[NZ0 + q]
            if nzl >= nz_maxloss:
                st[75] += 1
                nzd = 0
        if zcur >= 0 and nz_on and entries_ok and not (vp_blk and (vp_mods & 4)) and z_entry[zcur] == 1 and nzd != 0 and not skipmask_z[zcur]:
            hed = False
''')
# Regime-Groesse: Noise-Regime als neues Feld (nach z_LB), RSI21 ueber r_reg
rep("             z_ev, z_em, z_close, z_UB, z_LB, z_vw, z_dist, z_entry, z_next, ev_nzeod,",
    "             z_ev, z_em, z_close, z_UB, z_LB, z_reg, z_vw, z_dist, z_entry, z_next, ev_nzeod,")
rep('''                      mk.nz["LB"] if "LB" in mk.nz else np.zeros(len(mk.nz["ev"])),''',
    '''                      mk.nz["LB"] if "LB" in mk.nz else np.zeros(len(mk.nz["ev"])),
                      mk.nz["reg"] if "reg" in mk.nz else np.ones(len(mk.nz["ev"]), np.int64),''')
rep("            r = start * r21_risk / 100.0 * w * fak\n",
    "            r = start * r21_risk / 100.0 * w * fak\n            if reg_mult != 1.0 and r_reg[a] == 0:\n                r *= reg_mult\n")
rep("                    r = start * (nz_risk if nzd > 0 else nz_s_risk) / 100.0 * z_vw[zcur] / nz_parts * fak\n",
    "                    r = start * (nz_risk if nzd > 0 else nz_s_risk) / 100.0 * z_vw[zcur] / nz_parts * fak\n                    if reg_mult != 1.0 and z_reg[zcur] == 0:\n                        r *= reg_mult\n")

# Trade-Protokoll Spalte 10 = Ausstiegszeit (NY-Minuten, Kerze des Ausstiegs) fuer Diagnosen
n9 = src.count("out_tr[n_tr, 9] = float(p_dir[k])")
assert n9 == 13, n9
src = src.replace("out_tr[n_tr, 9] = float(p_dir[k])", "out_tr[n_tr, 9] = float(p_dir[k]); out_tr[n_tr, 10] = float(days[dayidx] * 1440 + nymin)")
rep("tr = np.zeros((MAXTR, 10))", "tr = np.zeros((MAXTR, 11))")
open("eng11.py", "w").write(src)
print("eng11.py geschrieben", len(src))
