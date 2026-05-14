@echo off
setlocal

REM Set the path to the virtual environment
set VENV_PATH=%~dp0..\..\..\app_envs\env_progress

REM Clone the PROGRESS sources inside the app environment so pip can install from git-managed sources.
set PROGRESS_REPO_PATH=%VENV_PATH%\snl_quest_progress
set PROGRESS_REPO_URL=https://github.com/sandialabs/snl-progress.git

REM Legacy PROGRESS currently relies on Python 3.9 on Windows.
set PYTHON_CMD=py -3.9

%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.9 is required to install QuESt Progress but was not found via the py launcher.
    exit /b 1
)

REM Rebuild the environment if it exists but is incomplete or uses the wrong Python version.
if exist "%VENV_PATH%" (
    if not exist "%VENV_PATH%\Scripts\activate.bat" (
        echo Existing Progress environment is incomplete. Recreating it...
        rmdir /s /q "%VENV_PATH%"
    ) else (
        "%VENV_PATH%\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 9) else 1)"
        if errorlevel 1 (
            echo Existing Progress environment is not using Python 3.9. Recreating it...
            rmdir /s /q "%VENV_PATH%"
        )
    )
)

REM Create the virtual environment if it doesn't exist
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    %PYTHON_CMD% -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo Failed to create the Progress virtual environment.
        exit /b 1
    )
)

REM Activate the virtual environment
call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate the Progress virtual environment.
    exit /b 1
)

REM Allow this app installer to resolve packages from configured package indexes.
set "PIP_NO_INDEX=0"

REM Some Windows environments do not have the local CA chain configured for pip.
set "PIP_TRUSTED_HOST=files.pythonhosted.org pypi.org pypi.python.org"

REM Refresh the local git checkout used for the editable install.
if exist "%PROGRESS_REPO_PATH%\.git" (
    echo Refreshing existing Progress repository...
    git -C "%PROGRESS_REPO_PATH%" fetch --all --tags --prune
    if errorlevel 1 (
        echo Failed to fetch the latest Progress repository changes.
        exit /b 1
    )
    git -C "%PROGRESS_REPO_PATH%" reset --hard origin/master
    if errorlevel 1 (
        echo Failed to reset the Progress repository to origin/master.
        exit /b 1
    )
) else (
    if exist "%PROGRESS_REPO_PATH%" (
        rmdir /s /q "%PROGRESS_REPO_PATH%"
    )
    git clone "%PROGRESS_REPO_URL%" "%PROGRESS_REPO_PATH%"
    if errorlevel 1 (
        echo Failed to clone Progress from "%PROGRESS_REPO_URL%".
        exit /b 1
    )
)

REM Ensure the cloned PROGRESS repository is present.
if not exist "%PROGRESS_REPO_PATH%\setup.py" (
    echo Failed to locate Progress sources at "%PROGRESS_REPO_PATH%".
    exit /b 1
)

REM Install the Python package within the virtual environment from the git checkout.
pip install --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org "%PROGRESS_REPO_PATH%"
if errorlevel 1 (
    echo Failed to install QuESt Progress from "%PROGRESS_REPO_PATH%".
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
