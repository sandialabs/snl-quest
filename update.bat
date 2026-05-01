@echo off
setlocal
call "C:\work\quest210-py313\Scripts\activate.bat"
if errorlevel 1 exit /b %errorlevel%
cd /d "C:\work\quest210\snl-quest"
if errorlevel 1 exit /b %errorlevel%
git remote set-url origin "https://github.com/sandialabs/snl-quest.git"
if errorlevel 1 exit /b %errorlevel%
git pull origin HEAD
if errorlevel 1 exit /b %errorlevel%
"C:\work\quest210-py313\Scripts\python.exe" -m pip install --upgrade .
exit /b %errorlevel%
