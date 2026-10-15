# Probelauf auf dev-Daten (Zwischenstand, kein Urteil)
```json
{
 "schwellen": {
  "t_pool_min": 2.5,
  "t_vs_null_min": 2.0,
  "muss_positiv": [
   "Val2024"
  ]
 },
 "kandidaten": [
  {
   "name": "noise-1.0",
   "modul": "familien/referenz/kandidat_noise10.py",
   "instrumente": [
    "NAS100"
   ],
   "zeitraeume": [
    {
     "name": "Train",
     "von": "2020-01-01",
     "bis": "2024-01-01"
    },
    {
     "name": "Val2024",
     "von": "2024-01-01",
     "bis": "2025-01-01"
    }
   ],
   "kurve": [
    0.5,
    1.0,
    1.5,
    2.0,
    null
   ]
  },
  {
   "name": "aus-A",
   "modul": "familien/ausstiege/kandidat_A_n10_ziel15.py",
   "instrumente": [
    "NAS100"
   ],
   "zeitraeume": [
    {
     "name": "Train",
     "von": "2020-01-01",
     "bis": "2024-01-01"
    },
    {
     "name": "Val2024",
     "von": "2024-01-01",
     "bis": "2025-01-01"
    }
   ],
   "kurve": [
    0.5,
    1.0,
    1.5,
    2.0,
    null
   ]
  },
  {
   "name": "aus-B",
   "modul": "familien/ausstiege/kandidat_B_paps_tp05be.py",
   "instrumente": [
    "NAS100"
   ],
   "zeitraeume": [
    {
     "name": "Train",
     "von": "2020-01-01",
     "bis": "2024-01-01"
    },
    {
     "name": "Val2024",
     "von": "2024-01-01",
     "bis": "2025-01-01"
    }
   ],
   "kurve": []
  },
  {
   "name": "aus-C",
   "modul": "familien/ausstiege/kandidat_C_pap0_tp10paper.py",
   "instrumente": [
    "NAS100",
    "US500"
   ],
   "zeitraeume": [
    {
     "name": "Train",
     "von": "2020-01-01",
     "bis": "2024-01-01"
    },
    {
     "name": "Val2024",
     "von": "2024-01-01",
     "bis": "2025-01-01"
    }
   ],
   "kurve": []
  },
  {
   "name": "ni-A_s1",
   "modul": "familien/noise_indizes/kandidat_A_s1.py",
   "instrumente": [
    "NAS100",
    "US500",
    "GER40",
    "JPN225",
    "HK50"
   ],
   "zeitraeume": [
    {
     "name": "Train",
     "von": "2020-01-01",
     "bis": "2024-01-01"
    },
    {
     "name": "Val2024",
     "von": "2024-01-01",
     "bis": "2025-01-01"
    }
   ],
   "kurve": [
    0.5,
    1.0,
    1.5,
    2.0,
    null
   ]
  },
  {
   "name": "ni-B_s1",
   "modul": "familien/noise_indizes/kandidat_B_s1.py",
   "instrumente": [
    "NAS100",
    "US500",
    "GER40",
    "JPN225",
    "HK50"
   ],
   "zeitraeume": [
    {
     "name": "Train",
     "von": "2020-01-01",
     "bis": "2024-01-01"
    },
    {
     "name": "Val2024",
     "von": "2024-01-01",
     "bis": "2025-01-01"
    }
   ],
   "kurve": []
  },
  {
   "name": "ni-n10eod_s1",
   "modul": "familien/noise_indizes/kandidat_n10eod_s1.py",
   "instrumente": [
    "NAS100",
    "US500",
    "JPN225",
    "HK50"
   ],
   "zeitraeume": [
    {
     "name": "Train",
     "von": "2020-01-01",
     "bis": "2024-01-01"
    },
    {
     "name": "Val2024",
     "von": "2024-01-01",
     "bis": "2025-01-01"
    }
   ],
   "kurve": []
  },
  {
   "name": "ev-fade930",
   "modul": "familien/ereignisse/kandidat_fade930.py",
   "instrumente": [
    "NAS100"
   ],
   "zeitraeume": [
    {
     "name": "Train",
     "von": "2020-01-01",
     "bis": "2024-01-01"
    },
    {
     "name": "Val2024",
     "von": "2024-01-01",
     "bis": "2025-01-01"
    }
   ],
   "kurve": [
    0.5,
    1.0,
    1.5,
    2.0,
    null
   ]
  },
  {
   "name": "kal-tom-preh",
   "modul": "familien/kalender/grenzfall_tom_preh.py",
   "instrumente": [
    "US500"
   ],
   "zeitraeume": [
    {
     "name": "Train",
     "von": "2020-01-01",
     "bis": "2024-01-01"
    },
    {
     "name": "Val2024",
     "von": "2024-01-01",
     "bis": "2025-01-01"
    }
   ],
   "kurve": [
    0.5,
    1.0,
    1.5,
    2.0,
    null
   ]
  }
 ]
}
```
