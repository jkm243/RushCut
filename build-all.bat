@echo off
chcp 65001 >nul
echo ============================================
echo   RUSHCUT - Build complet (Windows)
echo ============================================
echo.

REM --- 1. Python et dependances ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python introuvable. Installez Python 3.10+ depuis python.org
    echo          cochez "Add Python to PATH" pendant l'installation.
    pause & exit /b 1
)
echo [1/4] Installation des dependances Python...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if errorlevel 1 (echo [ERREUR] pip a echoue. & pause & exit /b 1)

REM --- 2. ffmpeg telecharge automatiquement ---
if not exist "vendor\ffmpeg.exe" (
    echo [2/4] Telechargement de ffmpeg ^(~80 Mo, une seule fois^)...
    if not exist vendor mkdir vendor
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'vendor\ffmpeg.zip'"
    if errorlevel 1 (echo [ERREUR] Telechargement ffmpeg impossible. Verifiez internet. & pause & exit /b 1)
    powershell -Command "Expand-Archive -Path 'vendor\ffmpeg.zip' -DestinationPath 'vendor\tmp' -Force; Get-ChildItem -Path 'vendor\tmp' -Recurse -Filter ffmpeg.exe | Select-Object -First 1 | Copy-Item -Destination 'vendor\ffmpeg.exe'; Remove-Item -Recurse -Force 'vendor\tmp','vendor\ffmpeg.zip'"
) else (
    echo [2/4] ffmpeg deja present dans vendor\
)

REM --- 3. Build de l'exe ---
echo [3/4] Compilation de RushCut.exe...
python -m PyInstaller --onefile --windowed --name RushCut ^
    --add-binary "vendor\ffmpeg.exe;." ^
    app\main.py
if errorlevel 1 (echo [ERREUR] PyInstaller a echoue. & pause & exit /b 1)

REM --- 4. Installateur optionnel (Inno Setup) ---
echo [4/4] Creation de l'installateur...
where iscc >nul 2>&1
if not errorlevel 1 (
    iscc installer.iss
    echo.
    echo ============================================
    echo   TERMINE ! Dossier 'installer\RushCut-Setup.exe'
    echo   Fichier a distribuer a vos clients.
    echo ============================================
) else (
    echo Inno Setup non detecte - etape ignoree.
    echo Pour un vrai installateur : https://jrsoftware.org/isdl.php
    echo Puis relancez ce script.
    echo.
    echo ============================================
    echo   TERMINE ! Fichier : dist\RushCut.exe
    echo   (ffmpeg deja embarque dedans)
    echo ============================================
)
pause
