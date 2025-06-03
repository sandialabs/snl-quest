@echo off

REM Set the repository URL and branch name
set REPO_URL=https://github.com/sandialabs/snl-quest.git
set BRANCH_NAME=snl_libraries

REM Set the sparse checkout directory
set SPARSE_DIR=snl_libraries/snl_btm

REM Set the path to the virtual environment
set VENV_PATH=%~dp0..\..\..\app_envs\env_btm

REM Set the path to the sparse checkout directory within the virtual environment
set CHECKOUT_PATH=%VENV_PATH%\snl-quest\%SPARSE_DIR%

REM Create the virtual environment if it doesn't exist
if not exist "%VENV_PATH%" (
    python -m venv %VENV_PATH%
)

REM Activate the virtual environment
call "%VENV_PATH%\Scripts\activate"

REM Clone the repository without checking out files into the virtual environment directory
if not exist "%VENV_PATH%\snl-quest" (
    git clone --no-checkout -b %BRANCH_NAME% %REPO_URL% "%VENV_PATH%\snl-quest"
)

REM Navigate to the cloned repository
cd "%VENV_PATH%\snl-quest"

REM Enable sparse checkout
git sparse-checkout init

REM Set sparse checkout path to include only the desired directory
git sparse-checkout set %SPARSE_DIR%

REM Check out the branch
git checkout %BRANCH_NAME%

REM Ensure the sparse checkout directory exists
if not exist "%CHECKOUT_PATH%" (
    echo Sparse checkout failed. Directory %SPARSE_DIR% does not exist.
    exit /b 1
)

REM Install the Python package within the virtual environment
pip install "%CHECKOUT_PATH%"

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
