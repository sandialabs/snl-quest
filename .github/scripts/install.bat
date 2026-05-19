@REM @echo off
@REM setlocal

@REM REM Check if Git is installed
@REM git --version >nul 2>&1
@REM if %errorlevel% neq 0 (
@REM     echo Git is not installed. Installing Git...
@REM     REM Download and install Git (adjust the URL to the latest Git installer if necessary)
@REM     powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.48.1.windows.1/Git-2.48.1-64-bit.exe' -OutFile 'Git-2.48.1-64-bit.exe'; Start-Process -FilePath '.\Git-2.48.1-64-bit.exe' -Wait"
@REM     if %errorlevel% neq 0 (
@REM         echo Failed to install Git.
@REM         exit /b 1
@REM     )
@REM     echo Git installed successfully.
@REM ) else (
@REM     echo Git is already installed.
@REM )

@REM REM Set the path to the directory containing the bundled Python executable
@REM set BUNDLED_PATH=%~dp0Python39

@REM REM Debugging statement to print the bundled path
@REM echo Bundled path: %BUNDLED_PATH%

@REM REM Check if the virtual environment exists, if not, create it
@REM if not exist "venv\Scripts\activate" (
@REM     echo Virtual environment not found. Creating virtual environment...
@REM     "%BUNDLED_PATH%\python.exe" -m venv venv
@REM     if %errorlevel% neq 0 (
@REM         echo Failed to create virtual environment.
@REM         exit /b 1
@REM     )
@REM     echo Virtual environment created successfully.
@REM )

@REM REM Path to the pyvenv.cfg file
@REM set PYVENV_CFG=venv\pyvenv.cfg

@REM REM Update the pyvenv.cfg file to set the home path to the bundled Python executable
@REM if exist "%PYVENV_CFG%" (
@REM     > "%PYVENV_CFG%" (
@REM         echo home = %BUNDLED_PATH%
@REM         echo include-system-site-packages = false
@REM         echo version = 3.9.13
@REM     )
@REM     echo Updated pyvenv.cfg with home path: %BUNDLED_PATH%
@REM ) else (
@REM     echo pyvenv.cfg not found.
@REM )

@REM REM Activate the virtual environment
@REM call venv\Scripts\activate

@REM REM Check if the quest package is installed using the virtual environment's pip
@REM venv\Scripts\pip show quest >nul 2>&1
@REM if %errorlevel% neq 0 (
@REM     echo quest package is not installed. Installing quest...
@REM     REM Run pip install -e . using the virtual environment's pip
@REM     venv\Scripts\pip install -e .
@REM ) else (
@REM     echo quest package is already installed.
@REM )

@REM REM Add the Scripts directory to the PATH
@REM set PATH=%BUNDLED_PATH%\Scripts;%PATH%
@REM set PATH=%PATH%;%~dp0glpk\glpk-4.65\w64

@REM REM Run the quest module using the virtual environment's Python interpreter
@REM venv\Scripts\python -m quest

@REM endlocal
@REM exit /b 0

REM Windows install test