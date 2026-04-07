@echo off
REM Set Python 3.12 launcher explicitly
set PYTHON_EXE=py -3.12

REM Set virtual environment path
set VENV_PATH=%~dp0..\..\..\app_envs\env_pcm

REM Set path to cloned repo inside venv
set REPO_PATH=%VENV_PATH%\snl_quest_pcm

REM Remove existing cloned repo folder if exists
if exist "%REPO_PATH%" (
    echo Removing existing repo folder...
    rmdir /S /Q "%REPO_PATH%"
)

REM Create virtual environment (force recreate)
if exist "%VENV_PATH%" (
    echo Removing existing virtual environment...
    rmdir /S /Q "%VENV_PATH%"
)
echo Creating Python 3.12 virtual environment...
%PYTHON_EXE% -m venv "%VENV_PATH%"

REM Activate virtual environment
call "%VENV_PATH%\Scripts\activate.bat"

echo Ensuring pip is installed...
python -m ensurepip --upgrade

REM Verify pip works
python -m pip --version || (
    echo ERROR: pip is not working
    exit /b 1
)

REM Clone repo into the env folder
echo Cloning quest_PCM repo...
git clone https://github.com/ercabrer/quest_PCM "%REPO_PATH%"

REM Install the package in editable mode
echo Installing quest_PCM package...
python -m pip install --upgrade pip
python -m pip install -e "%REPO_PATH%" || (
    echo ERROR: quest_PCM install failed
    exit /b 1
)

REM Download and extract GLPK
set URL=https://sourceforge.net/projects/winglpk/files/winglpk/GLPK-4.65/winglpk-4.65.zip/download
set OUTPUT=%VENV_PATH%\glpk.zip

echo Downloading GLPK...
curl -L --insecure -o %OUTPUT% %URL%

if not exist %OUTPUT% (
    echo Failed to download GLPK
    exit /b 1
)

echo Extracting GLPK...
powershell -Command "Expand-Archive -Path %OUTPUT% -DestinationPath %VENV_PATH%\glpk"

if errorlevel 1 (
    echo Failed to extract GLPK
    del %OUTPUT%
    exit /b 1
)

del %OUTPUT%

echo GLPK installation successful.

REM Deactivate virtual environment
deactivate

echo Setup complete.
exit /b 0