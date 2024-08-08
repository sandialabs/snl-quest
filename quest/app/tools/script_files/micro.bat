@echo off

set VENV_PATH=%~dp0..\..\..\app_envs\env_micro

python -m venv %VENV_PATH%
call "%VENV_PATH%\Scripts\activate"

pip install quest-ssim==1.0.0b3

garden install matplotlib
echo Garden installation matplotlib succesful
deactivate


exit /b 0