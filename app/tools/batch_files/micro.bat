@echo off

set VENV_PATH=%~dp0..\..\..\app_envs\env_micro

set REQ_PATH=%~dp0..\reqs\micro_reqs.txt

call "%VENV_PATH%\Scripts\activate"

pip install -r "%REQ_PATH%"


deactivate


exit /b 0