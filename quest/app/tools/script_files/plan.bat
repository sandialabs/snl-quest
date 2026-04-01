@echo off

set VENV_PATH=%~dp0..\..\..\app_envs\env_planning

REM Set the path to the setup.py file
set SETUP_PATH=%~dp0..\..\..\app_envs\env_planning\snl_quest_planning

set planning_dir=snl_quest_planning
python -m venv %VENV_PATH%
call "%VENV_PATH%\Scripts\activate"

mkdir "%VENV_PATH%\%planning_dir%"

git clone https://github.com/sandialabs/quest_planning.git "%VENV_PATH%\snl_quest_planning"

pip install -e "%SETUP_PATH%"
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

deactivate
exit /b 0