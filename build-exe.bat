@echo off
REM Build RushCut.exe (Windows) - double-cliquer pour lancer
pip install -r requirements.txt
pyinstaller --onefile --windowed --name RushCut app\main.py
echo.
echo OK -> dossier dist\RushCut.exe
pause
