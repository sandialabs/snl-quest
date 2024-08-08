@echo off

set VENV_PATH=%~dp0..\..\..\app_envs\env_energy

set REQ_PATH=%~dp0..\reqs\energy_reqs.txt

set equity_dir=equity
python -m venv %VENV_PATH%
call "%VENV_PATH%\Scripts\activate"

pip install -r "%REQ_PATH%"


mkdir "%VENV_PATH%\%equity_dir%"

git clone https://github.com/sandialabs/snl-quest-equity.git "%VENV_PATH%\equity"

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
deactivate
exit /b 0