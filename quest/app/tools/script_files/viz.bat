@echo off

set VENV_PATH=%~dp0..\..\..\app_envs\env_viz
set REQ_PATH=%~dp0..\reqs\viz_requirements.txt
python -m venv %VENV_PATH%
call "%VENV_PATH%\Scripts\activate"


pip install -r "%REQ_PATH%"

deactivate


exit /b 0