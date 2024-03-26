@echo off

set VENV_PATH=%~dp0..\..\app_envs\env_energy

set REQ_PATH=%~dp0reqs\energy_reqs.txt

set equity_dir=equity

call "%VENV_PATH%\Scripts\activate"

pip install -r "%REQ_PATH%"


mkdir "%VENV_PATH%\%equity_dir%"

git clone https://github.com/sandialabs/snl-quest-equity.git "%VENV_PATH%\equity"

deactivate


exit /b 0
