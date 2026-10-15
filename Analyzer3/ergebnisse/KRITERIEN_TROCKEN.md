# Probelauf (nur dev-Daten, kein Urteil)
```json
{"schwellen": {"t_pool_min": 2.5, "t_vs_null_min": 2.0, "muss_positiv": ["Val2024"]},
 "kandidaten": [
  {"name": "noise-1.0", "modul": "familien/referenz/kandidat_noise10.py", "instrumente": ["NAS100"],
   "zeitraeume": [{"name": "Train", "von": "2021-01-01", "bis": "2024-01-01"}, {"name": "Val2024", "von": "2024-01-01", "bis": "2025-01-01"}],
   "kurve": [0.5, 1.0, 2.0, null]},
  {"name": "ausstiege-C", "modul": "familien/ausstiege/kandidat_C_pap0_tp10paper.py", "instrumente": ["NAS100", "US500"],
   "zeitraeume": [{"name": "Val2024", "von": "2024-01-01", "bis": "2025-01-01"}], "kurve": []},
  {"name": "ereignis-fade930", "modul": "familien/ereignisse/kandidat_fade930.py", "instrumente": ["NAS100"],
   "zeitraeume": [{"name": "Val2024", "von": "2024-01-01", "bis": "2025-01-01"}], "kurve": [0.5, null]}
 ]}
```
