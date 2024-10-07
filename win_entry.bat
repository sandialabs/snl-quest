@echo off
SETLOCAL EnableDelayedExpansion

:: Set Input Variables
SET "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.37.3.windows.1/Git-2.37.3-64-bit.exe"
SET "GIT_INSTALLER_PATH=%TEMP%\Git-Installer.exe"
SET "PACKAGE_NAME=quest"
SET "QUEST_ENV=quest_20"

:: Check if Git is already installed
:check_git
git --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Git is already installed.
    GOTO setup_virtualenv
)
:: Use PowerShell to download Git installer
ECHO Git has not been detected...
ECHO Downloading Git Installer from github.com...
PowerShell -Command "curl '%GIT_URL%' -o '%GIT_INSTALLER_PATH%'"
:: Install Git silently
ECHO Installing Git
START "" /WAIT %TEMP%\Git-Installer.exe
:: Delete the installer after installation
DEL %TEMP%\Git-Installer.exe

:setup_virtualenv
ECHO Checking for existing virtual environment: %QUEST_ENV%
if not exist "%QUEST_ENV%\Scripts\activate" (
    ECHO Creating a virtual environment: %QUEST_ENV%
    python -m pip install --upgrade pip
    python -m pip install virtualenv
    python -m virtualenv %QUEST_ENV%
) else (
    ECHO Virtual environment already exists.
)

:install_and_run_package
ECHO Activating "%~dp0%QUEST_ENV%"
CALL "%~dp0%QUEST_ENV%\Scripts\activate"

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
CALL "%~dp0%QUEST_ENV%\Scripts\deactivate"
ENDLOCAL
