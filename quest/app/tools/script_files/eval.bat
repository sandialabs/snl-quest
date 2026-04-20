@echo off
setlocal

REM Set the path to the virtual environment
set VENV_PATH=%~dp0..\..\..\app_envs\env_eval

REM Set the path to the bundled Valuation package in this QuESt installation
set LOCAL_EVAL_PATH=%~dp0..\..\..\snl_libraries\snl_valuation

REM Rebuild the environment if it exists but is incomplete.
if exist "%VENV_PATH%" (
    if not exist "%VENV_PATH%\Scripts\activate.bat" (
        echo Existing Valuation environment is incomplete. Recreating it...
        rmdir /s /q "%VENV_PATH%"
    )
)

REM Create the virtual environment if it doesn't exist
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo Failed to create the Valuation virtual environment.
        exit /b 1
    )
)

REM Activate the virtual environment
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate the Valuation virtual environment.
    exit /b 1
)

REM Allow this app installer to resolve packages from configured package indexes.
set "PIP_NO_INDEX=0"

REM Ensure the bundled Valuation package exists
if not exist "%LOCAL_EVAL_PATH%\setup.py" (
    echo Failed to locate bundled Valuation sources at "%LOCAL_EVAL_PATH%".
    exit /b 1
)

REM Install the Python package within the virtual environment from the local source bundle
pip install "%LOCAL_EVAL_PATH%"
if errorlevel 1 (
    echo Failed to install QuESt Valuation from "%LOCAL_EVAL_PATH%".
    exit /b 1
)

REM Define the GLPK URL and destination
set "URL=https://downloads.sourceforge.net/project/winglpk/winglpk/GLPK-4.65/winglpk-4.65.zip"
set "OUTPUT=%VENV_PATH%\glpk.zip"
set "GLPK_DEST=%VENV_PATH%\glpk"

REM Download GLPK using curl
curl -fL --retry 3 --retry-delay 2 --insecure -o "%OUTPUT%" "%URL%"
if errorlevel 1 (
    echo Failed to download GLPK from "%URL%".
    if exist "%OUTPUT%" del "%OUTPUT%"
    exit /b 1
)

REM Check if the download was successful
if not exist "%OUTPUT%" (
    echo Failed to download GLPK
    exit /b 1
)

if exist "%GLPK_DEST%" (
    rmdir /s /q "%GLPK_DEST%"
)

REM Extract GLPK
powershell -NoProfile -Command "try { Expand-Archive -LiteralPath '%OUTPUT%' -DestinationPath '%GLPK_DEST%' -Force -ErrorAction Stop } catch { Write-Error $_; exit 1 }"

REM Check if the extraction was successful
if errorlevel 1 (
    echo Failed to extract GLPK
    if exist "%OUTPUT%" del "%OUTPUT%"
    exit /b 1
)

set "GLPSOL_EXE="
for /r "%GLPK_DEST%" %%F in (glpsol.exe) do (
    set "GLPSOL_EXE=%%F"
    goto :glpk_found
)

:glpk_found
if not defined GLPSOL_EXE (
    echo GLPK extraction completed, but glpsol.exe was not found.
    if exist "%OUTPUT%" del "%OUTPUT%"
    exit /b 1
)

REM Clean up
del "%OUTPUT%"

echo GLPK installation successful: %GLPSOL_EXE%

REM Deactivate the virtual environment
deactivate
exit /b 0
