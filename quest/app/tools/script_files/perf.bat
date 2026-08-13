@echo off

REM Install Performance from the QuESt_Performance branch without requiring Git on the target machine.
set PERF_BRANCH=QuESt_Performance
set PERF_PACKAGE_URL=https://github.com/sandialabs/snl-quest/archive/refs/heads/%PERF_BRANCH%.zip

REM Set the path to the virtual environment
set VENV_PATH=%~dp0..\..\..\app_envs\env_perf

REM Create the virtual environment if it doesn't exist
if not exist "%VENV_PATH%" (
    python -m venv %VENV_PATH%
)

REM Activate the virtual environment
call "%VENV_PATH%\Scripts\activate"

REM Allow this app installer to resolve packages from configured package indexes.
set "PIP_NO_INDEX=0"

REM Some Windows environments do not have the local CA chain configured for pip.
set "PIP_TRUSTED_HOST=files.pythonhosted.org pypi.org pypi.python.org"

REM Install the Python package from the selected GitHub branch.
python -m pip install --upgrade --force-reinstall --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host github.com --trusted-host codeload.github.com "%PERF_PACKAGE_URL%"
if errorlevel 1 (
    echo Failed to install QuESt Performance from branch "%PERF_BRANCH%".
    exit /b 1
)

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

REM Install matplotlib using garden
garden install matplotlib
echo Garden installation matplotlib successful

REM Deactivate the virtual environment
deactivate
exit /b 0
