@echo off

set VENV_PATH=%~dp0..\..\..\app_envs\env_planning

REM Set the path to the setup.py file
set SETUP_PATH=%~dp0..\..\..\app_envs\env_planning\snl_quest_planning

set planning_dir=snl_quest_planning
set PLANNING_REPO_URL=https://github.com/sandialabs/quest_planning.git
set PLANNING_BRANCH=reliability
set PLANNING_REPO_PATH=%VENV_PATH%\%planning_dir%
python -m venv %VENV_PATH%
call "%VENV_PATH%\Scripts\activate"

if exist "%PLANNING_REPO_PATH%" rmdir /s /q "%PLANNING_REPO_PATH%"
git clone --branch %PLANNING_BRANCH% --single-branch %PLANNING_REPO_URL% "%PLANNING_REPO_PATH%"

REM gurobipy==11.0.1 is not available for this Python build, so install the package
REM without dependency resolution and let the existing environment dependencies be reused.
pip install -e "%SETUP_PATH%" --no-deps
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
powershell -Command "Expand-Archive -Path %OUTPUT% -DestinationPath %VENV_PATH%\glpk -Force"

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
