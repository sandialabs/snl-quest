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
SET "INSTALL_DIR=%~dp0%QUEST_ENV%\Python_3.9.13"

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
START "" /WAIT %TEMP%\Git-Installer.exe
:: Delete the installer after installation
SETX PATH "%PATH%;C:\Program Files\Git\bin;C:\Program Files\Git\cmd"
DEL %TEMP%\Git-Installer.exe

:: Check if Python is installed system-wide
:check_python
where python >nul 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO install_system_wide_Python

:: Python is installed, proceeding with virtual environment
ECHO Python is installed, checking virtual environment...
python.exe -V > temp.txt 2>&1
SET /p SYS_PY_VERSION=<temp.txt
DEL temp.txt
ECHO Current Python: !SYS_PY_VERSION!
ECHO Target Python: %TARGET_PY_VERSION%
IF NOT "!SYS_PY_VERSION!"=="%TARGET_PY_VERSION%" (
    GOTO install_local_Python
) else (
    GOTO setup_virtualenv_from_system_python
)
:install_system_wide_Python
ECHO Python is not installed...
ECHO Downloading Python Installer from python.org...
PowerShell -Command "curl '%PYTHON_URL%' -o '%TEMP%\python-installer.exe'"
ECHO Installing Python...
START "" /WAIT %TEMP%\python-installer.exe InstallAllUsers=1 PrependPath=1 Include_test=0
GOTO setup_virtualenv_from_system_python

:install_local_Python
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo Directory created: %INSTALL_DIR%
) else (
    echo Directory already exists: %INSTALL_DIR%
)
:: Retrieve the current Python version
if exist "%~dp0%QUEST_ENV%\Scripts\python.exe" (
    %~dp0%QUEST_ENV%\Scripts\python.exe -V > temp.txt 2>&1
    SET /p PY_VERSION=<temp.txt
    DEL temp.txt
    ECHO Current Python: !PY_VERSION!
    ECHO Target Python: %TARGET_PY_VERSION%
    IF NOT "!PY_VERSION!"=="%TARGET_PY_VERSION%" (
        ECHO %TARGET_PY_VERSION% is not found in virtual environment. Installing %TARGET_PY_VERSION%.
        :: Download the Python installer (using PowerShell)
        PowerShell -Command "curl '%PYTHON_URL%' -o '%TEMP%\python-installer.exe'"
        :: Install Python to the specified directory
        START /WAIT %TEMP%\python_installer.exe InstallAllUsers=0 TargetDir="%INSTALL_DIR%"
    ) ELSE (
        ECHO Python version is already %TARGET_PY_VERSION%. No installation needed.
        
    )
) else (
    ECHO %TARGET_PY_VERSION% is not found in virtual environment. Installing %TARGET_PY_VERSION%.
    :: Download the Python installer (using PowerShell)
    PowerShell -Command "curl '%PYTHON_URL%' -o '%TEMP%\python-installer.exe'"
    :: Install Python to the specified directory
    START /WAIT %TEMP%\python-installer.exe InstallAllUsers=0 TargetDir="%INSTALL_DIR%"
)
GOTO setup_virtualenv_from_local_python

:setup_virtualenv_from_system_python
ECHO Checking for existing virtual environment: %QUEST_ENV%
if not exist "%QUEST_ENV%\Scripts\activate" (
    ECHO Creating a virtual environment: %QUEST_ENV%
    python -m pip install --upgrade pip
    python -m pip install virtualenv
    python -m virtualenv %QUEST_ENV%
) else (
    ECHO Virtual environment already exists.
)
GOTO install_and_run_package

:setup_virtualenv_from_local_python
ECHO Checking for existing virtual environment: %QUEST_ENV%
if not exist "%QUEST_ENV%\Scripts\activate" (
    ECHO Creating a virtual environment: %QUEST_ENV%
    python -m pip install --upgrade pip
    python -m pip install virtualenv
    python -m virtualenv --python=%INSTALL_DIR%\python.exe %QUEST_ENV%
) else (
    ECHO Virtual environment already exists.
)
GOTO install_and_run_package

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
