@echo off
setlocal
cd /d "%~dp0"

py -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

py -m PyInstaller --noconfirm --clean --onefile --windowed --name HEICtoPNG --collect-all pillow_heif app.py
if errorlevel 1 exit /b 1

echo.
echo Application creee : dist\HEICtoPNG.exe
echo Copiez ce fichier sur votre cle USB.
pause
