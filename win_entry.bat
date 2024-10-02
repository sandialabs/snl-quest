@echo off
SETLOCAL EnableDelayedExpansion

:: Set Input Variables
SET "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.37.3.windows.1/Git-2.37.3-64-bit.exe"
SET "GIT_INSTALLER_PATH=%TEMP%\Git-Installer.exe"
SET "PYTHON_VERSION=3.9.13"
SET "TARGET_PY_VERSION=Python %PYTHON_VERSION%"
SET "PYTHON_ARCH=amd64"
SET "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"
SET "PACKAGE_NAME=quest"
SET "QUEST_ENV=quest_20"
SET "INSTALL_DIR=%~dp0"

:: Check if Git is already installed
:check_git
git --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Git is already installed.
    GOTO check_python
)
:: Use PowerShell to download Git installer
ECHO Git has not been detected...
ECHO Downloading Git Installer from github.com...
PowerShell -Command "curl '%GIT_URL%' -o '%GIT_INSTALLER_PATH%'"
:: Install Git silently
ECHO Installing Git
START "" /WAIT %TEMP%\Git-Installer.exe /VERYSILENT /NORESTART
:: Delete the installer after installation
SETX PATH "%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd"
DEL %TEMP%\Git-Installer.exe

:: Check if Python 3.9.13 is installed
:check_python
SET "PYTHON_LOCAL=%INSTALL_DIR%Python39\python.exe"
IF EXIST "%PYTHON_LOCAL%" (
    "%PYTHON_LOCAL%" -V > temp.txt 2>&1
    SET /p LOCAL_PY_VERSION=<temp.txt
    DEL temp.txt
    IF "!LOCAL_PY_VERSION!"=="%TARGET_PY_VERSION%" (
        ECHO Python %PYTHON_VERSION% is already installed in the current directory.
        GOTO setup_virtualenv
    )
)
ECHO Python 3.9.13 is not installed...
ECHO Downloading Python Installer from python.org...
PowerShell -Command "curl '%PYTHON_URL%' -o '%TEMP%\python-installer.exe'"
ECHO Installing Python...
START "" /WAIT %TEMP%\python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 TargetDir="%INSTALL_DIR%Python39"
GOTO setup_virtualenv

:setup_virtualenv
ECHO Checking for existing virtual environment: %QUEST_ENV%
if not exist "%QUEST_ENV%\Scripts\activate" (
    ECHO Creating a virtual environment: %QUEST_ENV%
    "%INSTALL_DIR%Python39\python.exe" -m pip install --upgrade pip
    "%INSTALL_DIR%Python39\python.exe" -m pip install virtualenv
    "%INSTALL_DIR%Python39\python.exe" -m virtualenv "%QUEST_ENV%"
    ECHO Virtual environment created.
) else (
    ECHO Virtual environment already exists.
)
GOTO install_and_run_package

:install_and_run_package
ECHO Activating "%QUEST_ENV%"
CALL "%QUEST_ENV%\Scripts\activate"

:: Check if the package is already installed
pip show %PACKAGE_NAME% >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    :: Install Package
    ECHO Installing %PACKAGE_NAME% package...
    pip install -e .
) ELSE (
    ECHO %PACKAGE_NAME% package is already installed.
)

:: Run Package
ECHO Running %PACKAGE_NAME% package...
python -m %PACKAGE_NAME%
IF %ERRORLEVEL% NEQ 0 (
    GOTO run_error
)

GOTO finish

:run_error
ECHO Error encountered starting up %PACKAGE_NAME%.
GOTO end

:finish
ECHO %PACKAGE_NAME% ran successfully.
GOTO end

:end
ECHO Script execution completed.
CALL "%QUEST_ENV%\Scripts\deactivate"
ENDLOCAL
