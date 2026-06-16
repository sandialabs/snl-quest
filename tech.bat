@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Set the path to the virtual environment
for %%I in ("%~dp0..\..\..\app_envs") do set "APP_ENVS_PATH=%%~fI"
set "VENV_PATH=%APP_ENVS_PATH%\env_tech"

REM Install Tech Selection from the QuESt_Tech_Selection branch without requiring Git on the target machine.
set "TECH_BRANCH=QuESt_Tech_Selection"
set "TECH_PACKAGE_URL=https://github.com/sandialabs/snl-quest/archive/refs/heads/%TECH_BRANCH%.zip"

REM Legacy Tech Selection requires exactly Python 3.9.13 on Windows.
set "PYTHON_VERSION=3.9.13"
set "PYTHON_RUNTIME=%APP_ENVS_PATH%\btm_python_%PYTHON_VERSION%"
set "PYTHON_EXE=%PYTHON_RUNTIME%\python.exe"
set "PYTHON_INSTALLER=%TEMP%\quest-python-%PYTHON_VERSION%-amd64.exe"
set "PYTHON_INSTALL_LOG=%TEMP%\quest-python-%PYTHON_VERSION%-install.log"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"
set "VC_REDIST_INSTALLER=%TEMP%\quest-vc-redist-x64.exe"
set "VC_REDIST_LOG=%TEMP%\quest-vc-redist-x64-install.log"
set "VC_REDIST_URL=https://aka.ms/vs/17/release/vc_redist.x64.exe"
set "USE_PY_LAUNCHER="

py -3.9 -c "import sys; raise SystemExit(0 if sys.version_info[:3] == (3, 9, 13) else 1)" >nul 2>&1
if not errorlevel 1 set "USE_PY_LAUNCHER=1"

if not defined USE_PY_LAUNCHER (
    if exist "%PYTHON_EXE%" (
        "%PYTHON_EXE%" -c "import sys; raise SystemExit(0 if sys.version_info[:3] == (3, 9, 13) else 1)" >nul 2>&1
        if errorlevel 1 rmdir /s /q "%PYTHON_RUNTIME%"
    )
    if not exist "%PYTHON_EXE%" (
        if not exist "%APP_ENVS_PATH%" mkdir "%APP_ENVS_PATH%"
        echo Python %PYTHON_VERSION% was not detected. Downloading a private QuESt runtime...
        curl -fL --retry 3 --retry-delay 2 -o "%PYTHON_INSTALLER%" "%PYTHON_URL%"
        if errorlevel 1 exit /b 1
        start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 TargetDir="%PYTHON_RUNTIME%" Include_launcher=0 Include_test=0 Include_pip=1 Include_tcltk=1 Shortcuts=0 AssociateFiles=0 PrependPath=0 /log "%PYTHON_INSTALL_LOG%"
        set "PYTHON_INSTALL_RESULT=!ERRORLEVEL!"
        if not "!PYTHON_INSTALL_RESULT!"=="0" if not "!PYTHON_INSTALL_RESULT!"=="3010" (
            echo Python installation failed with exit code !PYTHON_INSTALL_RESULT!. Log: "%PYTHON_INSTALL_LOG%"
            exit /b !PYTHON_INSTALL_RESULT!
        )
        if exist "%PYTHON_INSTALLER%" del "%PYTHON_INSTALLER%"
    )
)

if not exist "%SystemRoot%\System32\MSVCP140.dll" (
    echo Microsoft Visual C++ runtime was not detected. Downloading it...
    curl -fL --retry 3 --retry-delay 2 -o "%VC_REDIST_INSTALLER%" "%VC_REDIST_URL%"
    if errorlevel 1 exit /b 1
    start /wait "" "%VC_REDIST_INSTALLER%" /install /quiet /norestart /log "%VC_REDIST_LOG%"
    set "VC_REDIST_RESULT=!ERRORLEVEL!"
    if not "!VC_REDIST_RESULT!"=="0" if not "!VC_REDIST_RESULT!"=="3010" if not "!VC_REDIST_RESULT!"=="1638" (
        echo Visual C++ runtime installation failed with exit code !VC_REDIST_RESULT!. Log: "%VC_REDIST_LOG%"
        exit /b !VC_REDIST_RESULT!
    )
    if exist "%VC_REDIST_INSTALLER%" del "%VC_REDIST_INSTALLER%"
)

REM Rebuild the environment if it exists but is incomplete or uses the wrong Python version.
if exist "%VENV_PATH%" (
    if not exist "%VENV_PATH%\Scripts\activate.bat" (
        echo Existing Tech Selection environment is incomplete. Recreating it...
        call :reset_venv
    ) else (
        "%VENV_PATH%\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info[:3] == (3, 9, 13) else 1)"
        if errorlevel 1 (
            echo Existing Tech Selection environment is not using Python %PYTHON_VERSION%. Recreating it...
            call :reset_venv
        )
    )
)

REM Create the virtual environment if it doesn't exist
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    if defined USE_PY_LAUNCHER (
        py -3.9 -m venv "%VENV_PATH%"
    ) else (
        "%PYTHON_EXE%" -m venv "%VENV_PATH%"
    )
    if errorlevel 1 (
        echo Failed to create the Tech Selection virtual environment.
        exit /b 1
    )
)

REM Activate the virtual environment
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate the Tech Selection virtual environment.
    exit /b 1
)

REM Allow this app installer to resolve packages from configured package indexes.
set "PIP_NO_INDEX=0"

REM Some Windows environments do not have the local CA chain configured for pip.
set "PIP_TRUSTED_HOST=files.pythonhosted.org pypi.org pypi.python.org"

REM Install the Python package from the selected GitHub branch.
python -m pip install --upgrade --force-reinstall --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host github.com --trusted-host codeload.github.com "%TECH_PACKAGE_URL%"
if errorlevel 1 (
    echo Failed to install QuESt Tech Selection from branch "%TECH_BRANCH%".
    exit /b 1
)

python -c "import numpy, matplotlib, tech_selection; print('Tech Selection Python imports verified:', numpy.__version__, matplotlib.__version__)"
if errorlevel 1 (
    echo QuESt Tech Selection installed, but its Python dependencies could not be imported.
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

:reset_venv
if exist "%VENV_PATH%\Scripts" rmdir /s /q "%VENV_PATH%\Scripts"
if exist "%VENV_PATH%\Include" rmdir /s /q "%VENV_PATH%\Include"
if exist "%VENV_PATH%\Lib" rmdir /s /q "%VENV_PATH%\Lib"
if exist "%VENV_PATH%\share" rmdir /s /q "%VENV_PATH%\share"
if exist "%VENV_PATH%\pyvenv.cfg" del "%VENV_PATH%\pyvenv.cfg"
exit /b 0
