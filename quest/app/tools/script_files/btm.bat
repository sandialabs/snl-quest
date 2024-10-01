@echo off

REM Set the path to the virtual environment
set VENV_PATH=%~dp0..\..\..\app_envs\env_btm

REM Set the path to the setup.py file
set SETUP_PATH=%~dp0..\..\..\snl_libraries\snl_btm

REM Create the virtual environment if it doesn't exist
if not exist "%VENV_PATH%" (
    python -m venv %VENV_PATH%
)

REM Activate the virtual environment
call "%VENV_PATH%\Scripts\activate"

REM Install the Python package within the virtual environment

pip install "%SETUP_PATH%"

REM Define the GLPK URL and destination
set URL=https://sourceforge.net/projects/winglpk/files/winglpk/GLPK-4.65/winglpk-4.65.zip/download
set OUTPUT=%VENV_PATH%\glpk.zip

REM Download GLPK using curl
curl -L --insecure -o %OUTPUT% %URL%

REM Check if the download was successful
if not exist %OUTPUT% (
    echo Failed to download GLPK
    exit /b 1
)

REM Extract GLPK
powershell -Command "Expand-Archive -Path %OUTPUT% -DestinationPath %VENV_PATH%\glpk"

REM Check if the extraction was successful
if errorlevel 1 (
    echo Failed to extract GLPK
    del %OUTPUT%
    exit /b 1
)

REM Clean up
del %OUTPUT%

echo GLPK installation successful
garden install matplotlib
echo Garden installation matplotlib succesful

set VENV_PACKAGES=%VENV_PATH%\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;%VENV_PACKAGES%
setx VENV_PACKAGES "%VENV_PACKAGES%"
setx PYTHONPATH "%PYTHONPATH%;%VENV_PACKAGES%"

REM Deactivate the virtual environment
deactivate
exit /b 0
