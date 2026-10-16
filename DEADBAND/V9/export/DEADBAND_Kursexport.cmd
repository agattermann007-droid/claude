@echo off
rem DEADBAND V9 - Kursexport aus dem laufenden GFT-MT5 (NAS100.x, XAUUSD.x, M1+M5, ab 2010).
rem Handelt nicht, ueberschreibt nichts. GFT-MT5 vorher starten und einloggen.
cd /d "%~dp0"
set "PY=python"
where py >nul 2>nul
if %errorlevel%==0 set "PY=py -3"
%PY% -c "import MetaTrader5, pandas" >nul 2>nul
if not %errorlevel%==0 (
  echo Installiere MetaTrader5 und pandas ...
  %PY% -m pip install --user MetaTrader5 pandas
)
%PY% "%~dp0DEADBAND_Kursexport.py" %*
echo.
pause
