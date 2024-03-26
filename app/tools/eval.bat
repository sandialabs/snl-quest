@echo off

set VENV_PATH=%~dp0..\..\app_envs\env_eval

set REQ_PATH=%~dp0reqs\eval_reqs.txt

call "%VENV_PATH%\Scripts\activate"

pip install -r "%REQ_PATH%"


deactivate


exit /b 0
