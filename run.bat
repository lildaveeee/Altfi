@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PYTHON=python"
set "RPT_DIR=%SCRIPT_DIR%RPT"
set "OUTPUT_FILE=%SCRIPT_DIR%data\player_data.txt"
set "TMP_FILE=%TEMP%\player_data_tmp.txt"
set "TMP_SORTED=%TEMP%\player_data_tmp_sorted.txt"

echo [%TIME%] Running RPT.py…
"%PYTHON%" "%SCRIPT_DIR%RPT.py"
echo [%TIME%] RPT.py completed successfully.

if not exist "%SCRIPT_DIR%data\" mkdir "%SCRIPT_DIR%data"
if not exist "%OUTPUT_FILE%" type nul > "%OUTPUT_FILE%"

> "%TMP_FILE%" (
  for /r "%RPT_DIR%" %%F in (*.rpt) do (
    for /f "usebackq delims=" %%L in ('findstr /c:"[Login]: Adding" "%%F"') do (
      set "line=%%L"
      for /f "tokens=2,* delims= " %%A in ("!line!") do (
        set "rest=%%B"
        for /f "delims=(" %%X in ("!rest!") do echo %%X
      )
    )
  )
)

sort "%TMP_FILE%" /unique > "%TMP_SORTED%"

for /f "usebackq delims=" %%N in ("%TMP_SORTED%") do (
  findstr /x "%%N" "%OUTPUT_FILE%" > nul || echo %%N>> "%OUTPUT_FILE%"
)

del "%TMP_FILE%" "%TMP_SORTED%"

for /f %%C in ('find /v /c "" ^< "%OUTPUT_FILE%"') do set "TOTAL=%%C"
echo ✅ %TOTAL% unique players in "%OUTPUT_FILE%"

echo [%TIME%] Running xapi.py…
"%PYTHON%" "%SCRIPT_DIR%xapi.py"
echo [%TIME%] xapi.py completed successfully.

echo [%TIME%] Running format.py…
"%PYTHON%" "%SCRIPT_DIR%format.py"
echo [%TIME%] format.py completed successfully.

echo [%TIME%] Running bypass.py…
"%PYTHON%" "%SCRIPT_DIR%bypass.py"
echo [%TIME%] bypass.py completed successfully.

echo [%TIME%] Running webhook.py…
"%PYTHON%" "%SCRIPT_DIR%webhook.py"
echo [%TIME%] webhook.py completed successfully.

endlocal
